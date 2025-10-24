"""
Unit Tests for Feedback Processor

Tests cover:
- Feedback data export
- Deduplication logic
- Anonymization (hashing, age bucketing)
- CSV generation
- Data integrity
- Edge cases
"""

import pytest
import csv
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from backend.app.db.base import Base
from backend.app.models.db_models import User, Profile, Analysis
from backend.app.recommender.models import RecommendationRecord, RecommendationFeedback
from backend.app.recommender.feedback_processor import (
    FeedbackProcessor,
    FeedbackTrainingPair,
    FeedbackProcessingStats,
    run_daily_feedback_export,
    run_bulk_feedback_export
)


# ===== FIXTURES =====

@pytest.fixture
def test_db():
    """Create in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create temporary output directory."""
    output_dir = tmp_path / "feedback_training"
    output_dir.mkdir(parents=True, exist_ok=True)
    return str(output_dir)


@pytest.fixture
def sample_user(test_db):
    """Create sample user."""
    user = User(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed"
    )
    profile = Profile(
        id=1,
        user_id=1,
        age=28,
        gender="F",
        location="San Francisco",
        skin_type="combination"
    )
    test_db.add(user)
    test_db.add(profile)
    test_db.commit()
    return user


@pytest.fixture
def sample_analysis(test_db, sample_user):
    """Create sample analysis."""
    analysis = Analysis(
        id=1,
        user_id=sample_user.id,
        photo_id=None,
        skin_type="combination",
        hair_type="wavy",
        conditions={"detected": ["acne", "oily_skin"]},
        confidence_scores={"acne": 0.87, "oily_skin": 0.92}
    )
    test_db.add(analysis)
    test_db.commit()
    return analysis


@pytest.fixture
def sample_recommendation(test_db, sample_user, sample_analysis):
    """Create sample recommendation record."""
    rec = RecommendationRecord(
        id=1,
        user_id=sample_user.id,
        analysis_id=sample_analysis.id,
        recommendation_id="rec_20251025_001",
        content={
            "skincare_routine": [
                {"step": 1, "action": "Cleanser", "frequency": "2x daily"}
            ]
        },
        source="rule_v1",
        conditions_analyzed=["acne", "oily_skin"],
        rules_applied=["r001_cleanser", "r002_treatment"],
        generation_time_ms=45
    )
    test_db.add(rec)
    test_db.commit()
    return rec


@pytest.fixture
def sample_feedback(test_db, sample_user, sample_analysis, sample_recommendation):
    """Create sample feedback record."""
    feedback = RecommendationFeedback(
        id=1,
        user_id=sample_user.id,
        analysis_id=sample_analysis.id,
        recommendation_id=sample_recommendation.id,
        helpful_rating=5,
        product_satisfaction=4,
        routine_completion_pct=80,
        timeframe="2_weeks",
        would_recommend=True,
        feedback_text="Great recommendations!",
        created_at=datetime.utcnow()
    )
    test_db.add(feedback)
    test_db.commit()
    return feedback


@pytest.fixture
def feedback_processor(test_db, temp_output_dir):
    """Create feedback processor instance."""
    return FeedbackProcessor(db_session=test_db, output_dir=temp_output_dir)


# ===== DATA CLASS TESTS =====

class TestFeedbackTrainingPair:
    """Test FeedbackTrainingPair data class."""
    
    def test_create_training_pair(self):
        """Test creating a training pair."""
        pair = FeedbackTrainingPair(
            analysis_hash="abc123def456",
            recommendation_id="rec_001",
            helpful_rating=5,
            product_satisfaction=4,
            routine_completion_pct=80,
            would_recommend=True,
            conditions_detected="acne,oily_skin",
            rules_applied="r001,r002",
            timeframe="2_weeks",
            age_range="25-35",
            feedback_timestamp="2025-10-25T10:00:00",
            export_date="2025-10-25T12:00:00"
        )
        
        assert pair.analysis_hash == "abc123def456"
        assert pair.helpful_rating == 5
    
    def test_to_dict(self):
        """Test converting training pair to dictionary."""
        pair = FeedbackTrainingPair(
            analysis_hash="abc123",
            recommendation_id="rec_001",
            helpful_rating=5,
            product_satisfaction=4,
            routine_completion_pct=80,
            would_recommend=True,
            conditions_detected="acne",
            rules_applied="r001",
            timeframe="2_weeks",
            age_range="25-35",
            feedback_timestamp="2025-10-25T10:00:00",
            export_date="2025-10-25T12:00:00"
        )
        
        d = pair.to_dict()
        
        assert isinstance(d, dict)
        assert "analysis_hash" in d
        assert d["helpful_rating"] == 5


# ===== ANONYMIZATION TESTS =====

class TestAnonymization:
    """Test anonymization functions."""
    
    def test_hash_id_deterministic(self, feedback_processor):
        """Test that ID hashing is deterministic."""
        hash1 = feedback_processor._hash_id(42)
        hash2 = feedback_processor._hash_id(42)
        
        assert hash1 == hash2
        assert len(hash1) == 16
    
    def test_hash_id_different_for_different_ids(self, feedback_processor):
        """Test that different IDs produce different hashes."""
        hash1 = feedback_processor._hash_id(42)
        hash2 = feedback_processor._hash_id(43)
        
        assert hash1 != hash2
    
    def test_bucket_age_18_to_25(self, feedback_processor):
        """Test age bucketing for 18-25 range."""
        assert feedback_processor._bucket_age(18) == "18-25"
        assert feedback_processor._bucket_age(20) == "18-25"
        assert feedback_processor._bucket_age(24) == "18-25"
    
    def test_bucket_age_25_to_35(self, feedback_processor):
        """Test age bucketing for 25-35 range."""
        assert feedback_processor._bucket_age(25) == "25-35"
        assert feedback_processor._bucket_age(28) == "25-35"
        assert feedback_processor._bucket_age(34) == "25-35"
    
    def test_bucket_age_35_to_50(self, feedback_processor):
        """Test age bucketing for 35-50 range."""
        assert feedback_processor._bucket_age(35) == "35-50"
        assert feedback_processor._bucket_age(40) == "35-50"
        assert feedback_processor._bucket_age(49) == "35-50"
    
    def test_bucket_age_50_plus(self, feedback_processor):
        """Test age bucketing for 50+ range."""
        assert feedback_processor._bucket_age(50) == "50+"
        assert feedback_processor._bucket_age(65) == "50+"
    
    def test_bucket_age_under_18(self, feedback_processor):
        """Test age bucketing for under 18."""
        assert feedback_processor._bucket_age(16) == "<18"
    
    def test_bucket_age_none(self, feedback_processor):
        """Test age bucketing with None."""
        assert feedback_processor._bucket_age(None) is None


# ===== FEEDBACK PROCESSING TESTS =====

class TestFeedbackProcessing:
    """Test feedback record processing."""
    
    def test_process_complete_feedback(
        self,
        feedback_processor,
        sample_feedback,
        sample_recommendation,
        sample_analysis,
        sample_user
    ):
        """Test processing complete feedback record."""
        pair = feedback_processor._process_feedback_record(
            sample_feedback,
            sample_recommendation,
            sample_analysis,
            sample_user
        )
        
        assert pair is not None
        assert pair.helpful_rating == 5
        assert pair.product_satisfaction == 4
        assert pair.routine_completion_pct == 80
        assert pair.would_recommend is True
        assert pair.age_range == "25-35"
        assert "acne" in pair.conditions_detected
    
    def test_process_partial_feedback(
        self,
        feedback_processor,
        sample_recommendation,
        sample_analysis,
        sample_user,
        test_db
    ):
        """Test processing feedback with partial ratings."""
        feedback = RecommendationFeedback(
            id=2,
            user_id=sample_user.id,
            analysis_id=sample_analysis.id,
            recommendation_id=sample_recommendation.id,
            helpful_rating=4,
            product_satisfaction=None,
            routine_completion_pct=None,
            would_recommend=None,
            created_at=datetime.utcnow()
        )
        test_db.add(feedback)
        test_db.commit()
        
        pair = feedback_processor._process_feedback_record(
            feedback,
            sample_recommendation,
            sample_analysis,
            sample_user
        )
        
        assert pair is not None
        assert pair.helpful_rating == 4
        assert pair.product_satisfaction is None
    
    def test_skip_empty_feedback(
        self,
        feedback_processor,
        sample_recommendation,
        sample_analysis,
        sample_user,
        test_db
    ):
        """Test skipping feedback with no ratings."""
        feedback = RecommendationFeedback(
            id=3,
            user_id=sample_user.id,
            analysis_id=sample_analysis.id,
            recommendation_id=sample_recommendation.id,
            helpful_rating=None,
            product_satisfaction=None,
            routine_completion_pct=None,
            would_recommend=None,
            created_at=datetime.utcnow()
        )
        test_db.add(feedback)
        test_db.commit()
        
        pair = feedback_processor._process_feedback_record(
            feedback,
            sample_recommendation,
            sample_analysis,
            sample_user
        )
        
        assert pair is None


# ===== DEDUPLICATION TESTS =====

class TestDeduplication:
    """Test deduplication logic."""
    
    def test_get_pair_hash(self, feedback_processor):
        """Test pair hash generation."""
        pair = FeedbackTrainingPair(
            analysis_hash="abc123",
            recommendation_id="rec_001",
            helpful_rating=5,
            product_satisfaction=4,
            routine_completion_pct=80,
            would_recommend=True,
            conditions_detected="acne",
            rules_applied="r001",
            timeframe="2_weeks",
            age_range="25-35",
            feedback_timestamp="2025-10-25T10:00:00",
            export_date="2025-10-25T12:00:00"
        )
        
        hash1 = feedback_processor._get_pair_hash(pair)
        hash2 = feedback_processor._get_pair_hash(pair)
        
        assert hash1 == hash2
        assert isinstance(hash1, str)
    
    def test_duplicate_detection(self, feedback_processor):
        """Test detecting duplicate pairs."""
        pair1 = FeedbackTrainingPair(
            analysis_hash="abc123",
            recommendation_id="rec_001",
            helpful_rating=5,
            product_satisfaction=4,
            routine_completion_pct=80,
            would_recommend=True,
            conditions_detected="acne",
            rules_applied="r001",
            timeframe="2_weeks",
            age_range="25-35",
            feedback_timestamp="2025-10-25T10:00:00",
            export_date="2025-10-25T12:00:00"
        )
        
        pair2 = FeedbackTrainingPair(
            analysis_hash="abc123",
            recommendation_id="rec_001",
            helpful_rating=5,
            product_satisfaction=4,
            routine_completion_pct=80,
            would_recommend=True,
            conditions_detected="acne",
            rules_applied="r001",
            timeframe="2_weeks",
            age_range="25-35",
            feedback_timestamp="2025-10-25T10:00:00",
            export_date="2025-10-25T12:00:00"
        )
        
        hash1 = feedback_processor._get_pair_hash(pair1)
        hash2 = feedback_processor._get_pair_hash(pair2)
        
        assert hash1 == hash2


# ===== CSV EXPORT TESTS =====

class TestCSVExport:
    """Test CSV export functionality."""
    
    def test_export_to_csv(self, feedback_processor, temp_output_dir):
        """Test exporting training pairs to CSV."""
        pairs = [
            FeedbackTrainingPair(
                analysis_hash="abc123",
                recommendation_id="rec_001",
                helpful_rating=5,
                product_satisfaction=4,
                routine_completion_pct=80,
                would_recommend=True,
                conditions_detected="acne",
                rules_applied="r001",
                timeframe="2_weeks",
                age_range="25-35",
                feedback_timestamp="2025-10-25T10:00:00",
                export_date="2025-10-25T12:00:00"
            )
        ]
        
        filename = feedback_processor._export_to_csv(pairs)
        
        assert filename
        assert Path(filename).exists()
    
    def test_csv_format(self, feedback_processor, temp_output_dir):
        """Test CSV file format."""
        pairs = [
            FeedbackTrainingPair(
                analysis_hash="abc123",
                recommendation_id="rec_001",
                helpful_rating=5,
                product_satisfaction=4,
                routine_completion_pct=80,
                would_recommend=True,
                conditions_detected="acne",
                rules_applied="r001",
                timeframe="2_weeks",
                age_range="25-35",
                feedback_timestamp="2025-10-25T10:00:00",
                export_date="2025-10-25T12:00:00"
            )
        ]
        
        filename = feedback_processor._export_to_csv(pairs)
        
        # Read and verify CSV
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) == 1
        assert rows[0]['analysis_hash'] == 'abc123'
        assert rows[0]['helpful_rating'] == '5'
    
    def test_csv_contains_no_user_ids(self, feedback_processor, temp_output_dir):
        """Test that CSV does not contain user IDs."""
        pairs = [
            FeedbackTrainingPair(
                analysis_hash="abc123",
                recommendation_id="rec_001",
                helpful_rating=5,
                product_satisfaction=4,
                routine_completion_pct=80,
                would_recommend=True,
                conditions_detected="acne",
                rules_applied="r001",
                timeframe="2_weeks",
                age_range="25-35",
                feedback_timestamp="2025-10-25T10:00:00",
                export_date="2025-10-25T12:00:00"
            )
        ]
        
        filename = feedback_processor._export_to_csv(pairs)
        
        with open(filename, 'r') as f:
            content = f.read()
        
        assert 'user_id' not in content
    
    def test_export_empty_list(self, feedback_processor):
        """Test exporting empty training pairs list."""
        filename = feedback_processor._export_to_csv([])
        
        assert filename == ""


# ===== INTEGRATION TESTS =====

class TestProcessAndExport:
    """Test full process_and_export workflow."""
    
    def test_process_and_export_complete(
        self,
        feedback_processor,
        sample_feedback,
        sample_recommendation,
        sample_analysis,
        sample_user
    ):
        """Test complete process and export workflow."""
        stats = feedback_processor.process_and_export(
            days_back=1,
            min_feedback_fields=1
        )
        
        assert stats.total_feedback_records >= 1
        assert stats.exported_records >= 1
        assert stats.export_filename
        assert Path(stats.export_filename).exists()
    
    def test_statistics_calculation(
        self,
        feedback_processor,
        sample_feedback,
        sample_recommendation,
        sample_analysis,
        sample_user
    ):
        """Test statistics are calculated correctly."""
        stats = feedback_processor.process_and_export(days_back=1)
        
        assert stats.execution_time_seconds > 0
        assert stats.exported_records > 0
        assert stats.anonymized_records >= stats.exported_records - stats.deduplicated_records


# ===== STATS TESTS =====

class TestProcessingStats:
    """Test FeedbackProcessingStats."""
    
    def test_stats_initialization(self):
        """Test stats object initialization."""
        stats = FeedbackProcessingStats()
        
        assert stats.total_feedback_records == 0
        assert stats.exported_records == 0
        assert stats.deduplicated_records == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
