"""
Test Suite for Feedback Endpoint

Tests for:
- Feedback submission (POST /feedback)
- Feedback statistics retrieval (GET /feedback/{id}/stats)
- User feedback summary (GET /feedbacks/user/{id}/summary)
- Validation and error handling
- Aggregate statistics calculation
- Rule log integration
"""

import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from backend.app.db.base import Base
from backend.app.db.session import get_db, engine
from backend.app.main import app
from backend.app.models.db_models import User, Analysis, Profile
from backend.app.recommender.models import (
    Product,
    RecommendationRecord,
    RecommendationFeedback,
    RuleLog
)


# ===== FIXTURES =====

@pytest.fixture
def db_session():
    """Create test database session"""
    Base.metadata.create_all(bind=engine)
    session = Session(engine)
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """Create test client with database dependency override"""
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def test_user(db_session):
    """Create test user"""
    user = User(
        id=1,
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_analysis(db_session, test_user):
    """Create test analysis"""
    analysis = Analysis(
        id=1,
        user_id=test_user.id,
        image_path="/path/to/image.jpg",
        skin_type="oily",
        conditions_detected=["acne", "blackheads"],
        confidence_scores={"acne": 0.92, "blackheads": 0.87},
        created_at=datetime.utcnow()
    )
    db_session.add(analysis)
    db_session.commit()
    db_session.refresh(analysis)
    return analysis


@pytest.fixture
def test_profile(db_session, test_user):
    """Create test profile"""
    profile = Profile(
        user_id=test_user.id,
        age=25,
        gender="F",
        skin_tone="medium",
        skin_sensitivity="normal",
        allergies=[]
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    return profile


@pytest.fixture
def test_recommendation(db_session, test_user, test_analysis):
    """Create test recommendation"""
    recommendation = RecommendationRecord(
        id=1,
        user_id=test_user.id,
        analysis_id=test_analysis.id,
        recommendation_id="rec_20251024_001",
        content={
            "routines": [
                {
                    "step": "morning",
                    "routine_text": "Gentle cleanser → Toner → Moisturizer",
                    "source_rules": ["r001"]
                }
            ],
            "products": [
                {
                    "external_id": "ordinary_sa_001",
                    "reason": "For acne control",
                    "source_rules": ["r001"]
                }
            ]
        },
        source="rule_v1",
        rules_applied=["r001", "r007"],
        conditions_analyzed=["acne", "blackheads"],
        generation_time_ms=150,
        created_at=datetime.utcnow()
    )
    db_session.add(recommendation)
    db_session.commit()
    db_session.refresh(recommendation)
    return recommendation


@pytest.fixture
def test_rule_logs(db_session, test_analysis):
    """Create test rule logs"""
    logs = [
        RuleLog(
            analysis_id=test_analysis.id,
            rule_id="r001",
            rule_name="Oily + Acne",
            rule_category="skincare",
            applied=True,
            details={
                "condition": "acne",
                "severity": "moderate",
                "step": 1,
                "action": "Gentle cleanser"
            },
            created_at=datetime.utcnow()
        ),
        RuleLog(
            analysis_id=test_analysis.id,
            rule_id="r007",
            rule_name="Blackheads + Pores",
            rule_category="skincare",
            applied=True,
            details={
                "condition": "blackheads",
                "severity": "mild",
                "action": "Pore cleanser"
            },
            created_at=datetime.utcnow()
        )
    ]
    for log in logs:
        db_session.add(log)
    db_session.commit()
    return logs


# ===== TESTS =====

class TestFeedbackSubmission:
    """Test feedback submission endpoint"""
    
    def test_submit_feedback_success(self, client, db_session, test_user, test_recommendation, test_rule_logs):
        """Test successful feedback submission"""
        # Mock JWT auth
        client.headers = {"Authorization": f"Bearer mock_token"}
        
        response = client.post(
            "/api/v1/feedback",
            json={
                "recommendation_id": "rec_20251024_001",
                "helpful_rating": 4,
                "product_satisfaction": 4,
                "routine_completion_pct": 75,
                "timeframe": "2_weeks",
                "feedback_text": "Great recommendations!",
                "would_recommend": True
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert data["feedback_id"] is not None
        assert data["recommendation_id"] == "rec_20251024_001"
        assert data["feedback_data"]["helpful_rating"] == 4
    
    def test_submit_feedback_with_adverse_reactions(self, client, db_session, test_user, test_recommendation):
        """Test feedback submission with adverse reactions"""
        response = client.post(
            "/api/v1/feedback",
            json={
                "recommendation_id": "rec_20251024_001",
                "helpful_rating": 2,
                "adverse_reactions": "Skin irritation from salicylic acid"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["feedback_data"]["has_adverse_reactions"] is True
        assert any(e["type"] == "adverse_reaction" for e in data["insights"]["escalations"])
    
    def test_submit_feedback_recommendation_not_found(self, client):
        """Test feedback submission for non-existent recommendation"""
        response = client.post(
            "/api/v1/feedback",
            json={
                "recommendation_id": "rec_nonexistent",
                "helpful_rating": 4
            }
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_submit_feedback_partial_data(self, client, test_recommendation):
        """Test feedback submission with only required field"""
        response = client.post(
            "/api/v1/feedback",
            json={
                "recommendation_id": "rec_20251024_001"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert data["feedback_data"]["helpful_rating"] is None
    
    def test_feedback_includes_rules_applied(self, client, db_session, test_user, test_recommendation, test_rule_logs):
        """Test that feedback response includes rules applied"""
        response = client.post(
            "/api/v1/feedback",
            json={
                "recommendation_id": "rec_20251024_001",
                "helpful_rating": 5
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert len(data["rules_applied"]) == 2
        assert data["rules_applied"][0]["rule_id"] == "r001"
        assert data["rules_applied"][0]["rule_name"] == "Oily + Acne"


class TestFeedbackStatistics:
    """Test feedback statistics aggregation"""
    
    def test_get_feedback_stats_empty(self, client, test_recommendation):
        """Test stats with no feedback"""
        response = client.get(
            f"/api/v1/feedback/rec_20251024_001/stats"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_feedbacks"] == 0
        assert data["avg_helpful_rating"] is None
    
    def test_get_feedback_stats_with_feedbacks(self, client, db_session, test_user, test_recommendation):
        """Test stats calculation with multiple feedbacks"""
        # Add multiple feedbacks
        feedbacks_data = [
            {"helpful_rating": 5, "product_satisfaction": 5},
            {"helpful_rating": 4, "product_satisfaction": 4},
            {"helpful_rating": 3, "product_satisfaction": 3}
        ]
        
        for fb_data in feedbacks_data:
            feedback = RecommendationFeedback(
                user_id=test_user.id,
                analysis_id=test_recommendation.analysis_id,
                recommendation_id=test_recommendation.id,
                helpful_rating=fb_data["helpful_rating"],
                product_satisfaction=fb_data["product_satisfaction"],
                created_at=datetime.utcnow()
            )
            db_session.add(feedback)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/feedback/rec_20251024_001/stats"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_feedbacks"] == 3
        assert data["avg_helpful_rating"] == 4.0
        assert data["avg_product_satisfaction"] == 4.0
    
    def test_feedback_stats_rating_distribution(self, client, db_session, test_user, test_recommendation):
        """Test rating distribution calculation"""
        # Add feedbacks with different ratings
        for rating in [1, 2, 3, 4, 5, 5]:
            feedback = RecommendationFeedback(
                user_id=test_user.id,
                analysis_id=test_recommendation.analysis_id,
                recommendation_id=test_recommendation.id,
                helpful_rating=rating,
                created_at=datetime.utcnow()
            )
            db_session.add(feedback)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/feedback/rec_20251024_001/stats"
        )
        
        assert response.status_code == 200
        data = response.json()
        distribution = data["ratings_distribution"]
        assert distribution[1] == 1
        assert distribution[2] == 1
        assert distribution[3] == 1
        assert distribution[4] == 1
        assert distribution[5] == 2
    
    def test_feedback_stats_recommendation_metrics(self, client, db_session, test_user, test_recommendation):
        """Test recommendation metrics (would_recommend, adverse reactions)"""
        feedbacks_data = [
            {"would_recommend": True},
            {"would_recommend": True},
            {"would_recommend": False},
            {"adverse_reactions": "Some irritation"}
        ]
        
        for fb_data in feedbacks_data:
            feedback = RecommendationFeedback(
                user_id=test_user.id,
                analysis_id=test_recommendation.analysis_id,
                recommendation_id=test_recommendation.id,
                would_recommend=fb_data.get("would_recommend"),
                adverse_reactions=fb_data.get("adverse_reactions"),
                created_at=datetime.utcnow()
            )
            db_session.add(feedback)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/feedback/rec_20251024_001/stats"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["would_recommend_count"] == 2
        assert data["would_not_recommend_count"] == 1
        assert data["adverse_reactions"] == 1
    
    def test_feedback_stats_not_found(self, client):
        """Test stats for non-existent recommendation"""
        response = client.get(
            f"/api/v1/feedback/rec_nonexistent/stats"
        )
        
        assert response.status_code == 404


class TestUserFeedbackSummary:
    """Test user feedback summary endpoint"""
    
    def test_get_user_summary_empty(self, client, test_user):
        """Test summary with no recommendations"""
        response = client.get(
            f"/api/v1/feedbacks/user/{test_user.id}/summary"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == test_user.id
        assert data["total_recommendations"] == 0
        assert data["total_feedbacks_given"] == 0
    
    def test_get_user_summary_with_feedbacks(self, client, db_session, test_user, test_recommendation):
        """Test summary with multiple feedbacks"""
        # Add multiple feedbacks
        feedbacks_data = [
            {"helpful_rating": 5, "would_recommend": True},
            {"helpful_rating": 4, "would_recommend": True},
            {"helpful_rating": 3, "would_recommend": False}
        ]
        
        for fb_data in feedbacks_data:
            feedback = RecommendationFeedback(
                user_id=test_user.id,
                analysis_id=test_recommendation.analysis_id,
                recommendation_id=test_recommendation.id,
                helpful_rating=fb_data["helpful_rating"],
                would_recommend=fb_data["would_recommend"],
                created_at=datetime.utcnow()
            )
            db_session.add(feedback)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/feedbacks/user/{test_user.id}/summary"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == test_user.id
        assert data["total_recommendations"] == 1
        assert data["total_feedbacks_given"] == 3
        assert data["overall_avg_helpful_rating"] == 4.0
        assert data["would_recommend_rate"] == round(2/3, 2)
    
    def test_user_summary_permission_denied(self, client, test_user):
        """Test that users can only view their own summary"""
        # Trying to view another user's summary should fail
        other_user_id = test_user.id + 999
        
        response = client.get(
            f"/api/v1/feedbacks/user/{other_user_id}/summary"
        )
        
        assert response.status_code == 403


class TestInsightCalculation:
    """Test insight calculation from feedback"""
    
    def test_low_satisfaction_insight(self, client, db_session, test_user, test_recommendation):
        """Test insights for low satisfaction"""
        response = client.post(
            "/api/v1/feedback",
            json={
                "recommendation_id": "rec_20251024_001",
                "helpful_rating": 2,
                "routine_completion_pct": 30
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        insights = data["insights"]
        assert insights["user_satisfaction_level"] == "low"
        assert insights["routine_adherence"] == "poor"
        assert any("complex" in rec for rec in insights["recommendations_for_improvement"])
    
    def test_high_satisfaction_insight(self, client):
        """Test insights for high satisfaction"""
        response = client.post(
            "/api/v1/feedback",
            json={
                "recommendation_id": "rec_20251024_001",
                "helpful_rating": 5,
                "routine_completion_pct": 95
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        insights = data["insights"]
        assert insights["user_satisfaction_level"] == "high"
        assert insights["routine_adherence"] == "excellent"
    
    def test_adverse_reactions_escalation(self, client):
        """Test escalation for adverse reactions"""
        response = client.post(
            "/api/v1/feedback",
            json={
                "recommendation_id": "rec_20251024_001",
                "adverse_reactions": "Severe allergic reaction"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        insights = data["insights"]
        assert len(insights["escalations"]) > 0
        assert insights["escalations"][0]["type"] == "adverse_reaction"
        assert insights["escalations"][0]["severity"] == "high"


class TestValidation:
    """Test input validation"""
    
    def test_rating_validation_too_high(self, client):
        """Test that rating >5 is rejected"""
        response = client.post(
            "/api/v1/feedback",
            json={
                "recommendation_id": "rec_20251024_001",
                "helpful_rating": 10
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_rating_validation_too_low(self, client):
        """Test that rating <1 is rejected"""
        response = client.post(
            "/api/v1/feedback",
            json={
                "recommendation_id": "rec_20251024_001",
                "helpful_rating": 0
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_completion_percentage_validation(self, client):
        """Test that completion percentage is 0-100"""
        response = client.post(
            "/api/v1/feedback",
            json={
                "recommendation_id": "rec_20251024_001",
                "routine_completion_pct": 150
            }
        )
        
        assert response.status_code == 422  # Validation error


class TestRuleLogIntegration:
    """Test integration with RuleLog"""
    
    def test_feedback_response_includes_all_applied_rules(self, client, db_session, test_user, test_recommendation):
        """Test that feedback response includes all applied rules"""
        # Create multiple rule logs
        for i, (rule_id, rule_name) in enumerate([("r001", "Rule 1"), ("r002", "Rule 2"), ("r003", "Rule 3")]):
            log = RuleLog(
                analysis_id=test_recommendation.analysis_id,
                rule_id=rule_id,
                rule_name=rule_name,
                rule_category="skincare",
                applied=True,
                details={"step": i+1}
            )
            db_session.add(log)
        db_session.commit()
        
        response = client.post(
            "/api/v1/feedback",
            json={
                "recommendation_id": "rec_20251024_001",
                "helpful_rating": 4
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert len(data["rules_applied"]) == 3
    
    def test_stats_includes_rules_metadata(self, client, db_session, test_user, test_recommendation):
        """Test that stats include rule metadata"""
        log = RuleLog(
            analysis_id=test_recommendation.analysis_id,
            rule_id="r001",
            rule_name="Test Rule",
            rule_category="skincare",
            applied=True,
            details={"reason": "condition_matched"}
        )
        db_session.add(log)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/feedback/rec_20251024_001/stats"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "rules_applied" in data
        assert data["rules_applied"][0]["rule_id"] == "r001"
