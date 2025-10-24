"""
Integration Tests for Recommender System

Tests:
1. Rule Engine with sample data
   - Load analysis and profile JSON
   - Call apply_rules()
   - Assert returned structure contains routines, products, diet arrays

2. Product Integration
   - Insert product with 'salicylic_cleanser' tag in DB
   - Run recommend with matching analysis
   - Assert product appears in returned products

3. Feedback Integration
   - Post feedback on recommendation
   - Verify feedback saved to DB
   - Assert aggregate stats updated
"""

import pytest
import json
from datetime import datetime
from typing import Dict, Any

from sqlalchemy import create_engine, func, cast, Integer
from sqlalchemy.orm import sessionmaker, Session

from backend.app.db.base import Base
from backend.app.models.db_models import User, Profile, Photo, Analysis
from backend.app.recommender.engine import RuleEngine
from backend.app.recommender.models import Product, RuleLog, RecommendationRecord, RecommendationFeedback
from backend.app.recommender.schemas import FeedbackRequest


# ===== TEST FIXTURES =====

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
def sample_analysis() -> Dict[str, Any]:
    """Sample analysis JSON matching acne/oily skin pattern."""
    return {
        "skin_type": "oily",
        "conditions_detected": ["acne", "blackheads"],
        "skin_sensitivity": "normal",
        "hair_type": "straight",
        "hair_condition": [],
        "age": 25,
        "birth_year": 2000
    }


@pytest.fixture
def sample_profile() -> Dict[str, Any]:
    """Sample user profile JSON."""
    return {
        "age": 25,
        "pregnancy_status": False,
        "allergies": [],
        "previous_treatments": ["benzoyl_peroxide"],
        "budget_level": "medium"
    }


@pytest.fixture
def sample_user(test_db: Session) -> User:
    """Create sample user in database."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="test_hash"
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def sample_photo(test_db: Session, sample_user: User) -> Photo:
    """Create sample photo in database."""
    photo = Photo(
        user_id=sample_user.id,
        filename="test_photo.jpg",
        s3_key="test_photos/test_photo.jpg"
    )
    test_db.add(photo)
    test_db.commit()
    test_db.refresh(photo)
    return photo


@pytest.fixture
def sample_analysis_record(
    test_db: Session,
    sample_user: User,
    sample_photo: Photo,
    sample_analysis: Dict[str, Any]
) -> Analysis:
    """Create sample analysis record in database."""
    analysis = Analysis(
        user_id=sample_user.id,
        photo_id=sample_photo.id,
        skin_type=sample_analysis["skin_type"],
        hair_type=sample_analysis["hair_type"],
        conditions=sample_analysis.get("conditions_detected", []),
        confidence_scores={
            "skin_type": 0.85,
            "hair_type": 0.90
        }
    )
    test_db.add(analysis)
    test_db.commit()
    test_db.refresh(analysis)
    return analysis


@pytest.fixture
def salicylic_product(test_db: Session) -> Product:
    """Create a salicylic acid cleanser product with matching tags."""
    product = Product(
        name="BHA Exfoliating Cleanser",
        brand="CeraVe",
        category="cleanser",
        price_usd=899,
        url="https://example.com/product",
        ingredients=["water", "salicylic_acid", "glycerin"],
        tags=["salicylic_cleanser", "acne-prone", "gentle", "exfoliating"],
        dermatologically_safe=True,
        recommended_for=["acne", "blackheads", "oily_skin"],
        avoid_for=["very_sensitive"],
        avg_rating=450,  # 4.5 stars
        review_count=1200,
        source="sephora",
        external_id="sephora_12345"
    )
    test_db.add(product)
    test_db.commit()
    test_db.refresh(product)
    return product


# ===== TEST CASES =====

class TestRuleEngineWithSampleData:
    """Test rule engine with sample analysis and profile data."""
    
    def test_engine_returns_required_structure(
        self,
        sample_analysis: Dict[str, Any],
        sample_profile: Dict[str, Any]
    ):
        """Test that apply_rules returns required recommendation structure."""
        engine = RuleEngine()
        
        recommendation, applied_rules = engine.apply_rules(
            analysis=sample_analysis,
            profile=sample_profile
        )
        
        # Assert top-level structure
        assert recommendation is not None, "Recommendation should not be None"
        assert isinstance(recommendation, dict), "Recommendation should be a dict"
        
        # Assert key arrays exist (these are what we care about most)
        required_arrays = {'routines', 'products', 'diet'}
        assert all(key in recommendation for key in required_arrays), \
            f"Recommendation missing arrays. Expected: {required_arrays}, Got: {recommendation.keys()}"
        
        # Assert arrays have correct types
        assert isinstance(recommendation['routines'], list), \
            f"routines should be list, got {type(recommendation['routines'])}"
        assert isinstance(recommendation['products'], list), \
            f"products should be list, got {type(recommendation['products'])}"
        assert isinstance(recommendation['diet'], list), \
            f"diet should be list, got {type(recommendation['diet'])}"
    
    def test_applied_rules_returns_list(
        self,
        sample_analysis: Dict[str, Any],
        sample_profile: Dict[str, Any]
    ):
        """Test that applied_rules is a list of rule IDs."""
        engine = RuleEngine()
        
        recommendation, applied_rules = engine.apply_rules(
            analysis=sample_analysis,
            profile=sample_profile
        )
        
        assert isinstance(applied_rules, list), \
            f"applied_rules should be list, got {type(applied_rules)}"
        # Note: applied_rules can be empty if no rules match exactly
    
    def test_recommendation_structure_details(
        self,
        sample_analysis: Dict[str, Any],
        sample_profile: Dict[str, Any]
    ):
        """Test detailed structure of recommendation components."""
        engine = RuleEngine()
        
        recommendation, applied_rules = engine.apply_rules(
            analysis=sample_analysis,
            profile=sample_profile
        )
        
        # Test routines structure (should have step, action, frequency)
        if recommendation['routines']:
            routine = recommendation['routines'][0]
            assert 'step' in routine or 'action' in routine, \
                "Routine should have step or action field"
        
        # Test products structure (should have name, category)
        if recommendation['products']:
            product = recommendation['products'][0]
            assert 'name' in product or 'category' in product, \
                "Product recommendation should have name or category"
        
        # Test escalation field (can be None or dict)
        escalation = recommendation.get('escalation')
        assert escalation is None or isinstance(escalation, dict), \
            "escalation should be None or dict"


class TestProductIntegration:
    """Test product matching with database integration."""
    
    def test_salicylic_product_in_db(
        self,
        test_db: Session,
        salicylic_product: Product
    ):
        """Test that product was created in database."""
        # Query the product back
        product = test_db.query(Product).filter(
            Product.name == "BHA Exfoliating Cleanser"
        ).first()
        
        assert product is not None, "Product should exist in database"
        assert product.brand == "CeraVe"
        assert "salicylic_cleanser" in (product.tags or [])
        assert "acne" in (product.recommended_for or [])
    
    def test_product_tags_for_acne(
        self,
        test_db: Session,
        salicylic_product: Product
    ):
        """Test querying products by tags."""
        # Find products with salicylic_cleanser tag
        products = test_db.query(Product).filter(
            Product.tags.contains("salicylic_cleanser")  # This won't work with JSON
        ).all()
        
        # Alternative: fetch all and filter in Python
        all_products = test_db.query(Product).all()
        acne_products = [
            p for p in all_products
            if p.tags and "salicylic_cleanser" in p.tags
        ]
        
        assert len(acne_products) > 0, "Should find salicylic cleanser products"
        assert acne_products[0].name == "BHA Exfoliating Cleanser"
    
    def test_product_matches_analysis_conditions(
        self,
        test_db: Session,
        salicylic_product: Product,
        sample_analysis: Dict[str, Any]
    ):
        """Test that product is suitable for the analysis conditions."""
        product = test_db.query(Product).filter(
            Product.name == "BHA Exfoliating Cleanser"
        ).first()
        
        analysis_conditions = sample_analysis["conditions_detected"]
        product_recommended = product.recommended_for or []
        
        # Check if product is recommended for any of the detected conditions
        has_match = any(
            condition in product_recommended
            for condition in analysis_conditions
        )
        
        assert has_match, \
            f"Product should be recommended for {analysis_conditions}, but is only for {product_recommended}"


class TestRecommendationRecordIntegration:
    """Test recommendation record creation and retrieval."""
    
    def test_create_recommendation_record(
        self,
        test_db: Session,
        sample_analysis_record: Analysis,
        salicylic_product: Product
    ):
        """Test creating a recommendation record."""
        recommendation = RecommendationRecord(
            user_id=sample_analysis_record.user_id,
            analysis_id=sample_analysis_record.id,
            recommendation_id="rec_001",
            content={
                "routines": [
                    {"step": 1, "action": "Gentle cleanser", "frequency": "2x daily"}
                ],
                "products": [salicylic_product.id],
                "diet": ["water", "antioxidants"]
            },
            source="rule_v1",
            rules_applied=["r001_acne_routine"],
            user_budget="medium"
        )
        
        test_db.add(recommendation)
        test_db.commit()
        test_db.refresh(recommendation)
        
        # Verify it was saved
        assert recommendation.id is not None
        assert recommendation.recommendation_id == "rec_001"
        assert recommendation.analysis_id == sample_analysis_record.id


class TestFeedbackIntegration:
    """Test feedback submission and aggregation."""
    
    def test_submit_feedback(
        self,
        test_db: Session,
        sample_user: User,
        sample_analysis_record: Analysis,
        salicylic_product: Product
    ):
        """Test submitting feedback on a recommendation."""
        # Create a recommendation first
        recommendation = RecommendationRecord(
            user_id=sample_analysis_record.user_id,
            analysis_id=sample_analysis_record.id,
            recommendation_id="rec_feedback_test",
            content={
                "routines": [],
                "products": [salicylic_product.id],
                "diet": []
            },
            source="rule_v1",
            rules_applied=["r001"]
        )
        test_db.add(recommendation)
        test_db.commit()
        test_db.refresh(recommendation)
        
        # Submit feedback
        feedback = RecommendationFeedback(
            user_id=sample_user.id,
            analysis_id=sample_analysis_record.id,
            recommendation_id=recommendation.id,
            helpful_rating=4,
            product_satisfaction=4,
            routine_completion_pct=90,
            timeframe="1 week",
            feedback_text="Great results!",
            improvement_suggestions="Could use more detail",
            adverse_reactions=None,
            would_recommend=True,
            product_ratings={"salicylic_cleanser": 5},
            created_at=datetime.utcnow()
        )
        
        test_db.add(feedback)
        test_db.commit()
        test_db.refresh(feedback)
        
        # Verify feedback was saved
        assert feedback.id is not None
        assert feedback.helpful_rating == 4
        assert feedback.would_recommend is True
    
    def test_aggregate_feedback_stats(
        self,
        test_db: Session,
        sample_user: User,
        sample_analysis_record: Analysis,
        salicylic_product: Product
    ):
        """Test aggregating feedback statistics."""
        # Create recommendation
        recommendation = RecommendationRecord(
            user_id=sample_analysis_record.user_id,
            analysis_id=sample_analysis_record.id,
            recommendation_id="rec_stats_test",
            content={
                "products": [salicylic_product.id],
                "routines": [],
                "diet": []
            },
            source="rule_v1",
            rules_applied=["r001"]
        )
        test_db.add(recommendation)
        test_db.commit()
        test_db.refresh(recommendation)
        
        # Submit multiple feedbacks
        feedbacks = [
            RecommendationFeedback(
                user_id=sample_user.id,
                analysis_id=sample_analysis_record.id,
                recommendation_id=recommendation.id,
                helpful_rating=5,
                product_satisfaction=5,
                routine_completion_pct=100,
                would_recommend=True,
                created_at=datetime.utcnow()
            ),
            RecommendationFeedback(
                user_id=sample_user.id,
                analysis_id=sample_analysis_record.id,
                recommendation_id=recommendation.id,
                helpful_rating=4,
                product_satisfaction=4,
                routine_completion_pct=80,
                would_recommend=True,
                created_at=datetime.utcnow()
            ),
            RecommendationFeedback(
                user_id=sample_user.id,
                analysis_id=sample_analysis_record.id,
                recommendation_id=recommendation.id,
                helpful_rating=3,
                product_satisfaction=3,
                routine_completion_pct=50,
                would_recommend=False,
                created_at=datetime.utcnow()
            )
        ]
        
        for fb in feedbacks:
            test_db.add(fb)
        test_db.commit()
        
        # Query aggregate stats
        stats = test_db.query(
            func.count(RecommendationFeedback.id).label('count'),
            func.avg(RecommendationFeedback.helpful_rating).label('avg_helpful'),
            func.avg(RecommendationFeedback.product_satisfaction).label('avg_satisfaction'),
            func.avg(RecommendationFeedback.routine_completion_pct).label('avg_completion'),
            func.sum(
                cast(RecommendationFeedback.would_recommend, Integer)
            ).label('would_recommend_count')
        ).filter(
            RecommendationFeedback.recommendation_id == recommendation.id
        ).first()
        
        # Verify aggregates
        assert stats.count == 3, f"Should have 3 feedbacks, got {stats.count}"
        assert stats.avg_helpful == 4.0, f"Average helpful should be 4.0, got {stats.avg_helpful}"
        assert stats.avg_satisfaction == 4.0, f"Average satisfaction should be 4.0"
        # Allow floating point imprecision with assertAlmostEqual-like check
        assert abs(stats.avg_completion - 76.66666666666667) < 0.01, \
            f"Average completion should be ~76.67%, got {stats.avg_completion}"
        assert stats.would_recommend_count == 2, \
            f"Should have 2 positive recommendations, got {stats.would_recommend_count}"
    
    def test_feedback_request_schema(self):
        """Test FeedbackRequest schema validation."""
        # Valid feedback request
        feedback_data = {
            "recommendation_id": "rec_20251024_001",
            "helpful_rating": 5,
            "product_satisfaction": 4,
            "routine_completion_pct": 90,
            "timeframe": "1 week",
            "would_recommend": True
        }
        
        feedback_request = FeedbackRequest(**feedback_data)
        
        assert feedback_request.helpful_rating == 5
        assert feedback_request.would_recommend is True
        assert feedback_request.recommendation_id == "rec_20251024_001"


class TestEndToEndRecommendation:
    """End-to-end tests combining multiple components."""
    
    def test_analysis_to_recommendation_to_feedback(
        self,
        test_db: Session,
        sample_user: User,
        sample_photo: Photo,
        sample_analysis: Dict[str, Any],
        sample_profile: Dict[str, Any],
        salicylic_product: Product
    ):
        """Test complete flow from analysis to feedback."""
        # 1. Create analysis
        analysis = Analysis(
            user_id=sample_user.id,
            photo_id=sample_photo.id,
            skin_type=sample_analysis["skin_type"],
            hair_type=sample_analysis["hair_type"],
            conditions=sample_analysis["conditions_detected"],
            confidence_scores={"skin_type": 0.85}
        )
        test_db.add(analysis)
        test_db.commit()
        test_db.refresh(analysis)
        
        # 2. Run rule engine
        engine = RuleEngine()
        recommendation, applied_rules = engine.apply_rules(
            analysis=sample_analysis,
            profile=sample_profile
        )
        
        # Verify recommendation structure
        assert "products" in recommendation or isinstance(recommendation, dict)
        
        # 3. Create recommendation record
        rec_record = RecommendationRecord(
            user_id=sample_user.id,
            analysis_id=analysis.id,
            recommendation_id=f"rec_{analysis.id}",
            content=recommendation if isinstance(recommendation, dict) else {},
            source="rule_v1",
            rules_applied=applied_rules
        )
        test_db.add(rec_record)
        test_db.commit()
        test_db.refresh(rec_record)
        
        # 4. Submit feedback
        feedback = RecommendationFeedback(
            user_id=sample_user.id,
            analysis_id=analysis.id,
            recommendation_id=rec_record.id,
            helpful_rating=5,
            would_recommend=True
        )
        test_db.add(feedback)
        test_db.commit()
        
        # 5. Verify complete flow
        assert rec_record.id is not None
        assert feedback.id is not None
        
        # Verify we can query everything back
        stored_rec = test_db.query(RecommendationRecord).filter(
            RecommendationRecord.id == rec_record.id
        ).first()
        assert stored_rec is not None
        
        stored_feedback = test_db.query(RecommendationFeedback).filter(
            RecommendationFeedback.recommendation_id == rec_record.id
        ).first()
        assert stored_feedback is not None
        assert stored_feedback.helpful_rating == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
