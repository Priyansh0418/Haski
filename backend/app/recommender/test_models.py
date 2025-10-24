"""
Unit tests for Recommender System Models

Tests for:
- Product model
- RuleLog model
- RecommendationRecord model
- RecommendationFeedback model
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.db.session import Base
from backend.app.recommender.models import (
    Product,
    RuleLog,
    RecommendationRecord,
    RecommendationFeedback
)


# ===== FIXTURES =====

@pytest.fixture
def db_session():
    """Create in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def sample_product(db_session):
    """Create sample product for testing"""
    product = Product(
        name="CeraVe Hydrating Cleanser",
        brand="CeraVe",
        category="cleanser",
        price_usd=899,  # $8.99
        url="https://example.com/product",
        ingredients=["water", "glycerin", "hyaluronic acid", "ceramides"],
        tags=["gentle", "hydrating", "non-comedogenic"],
        dermatologically_safe=True,
        recommended_for=["dry_skin", "sensitive", "eczema"],
        avoid_for=[],
        avg_rating=450,  # 4.5 stars
        review_count=2340,
        source="sephora",
        external_id="cerave_123"
    )
    db_session.add(product)
    db_session.commit()
    return product


@pytest.fixture
def sample_rule_log(db_session, sample_product):
    """Create sample rule log for testing"""
    rule_log = RuleLog(
        analysis_id=1,
        product_id=sample_product.id,
        rule_id="acne_routine_step_1",
        rule_name="Gentle Cleanser for Acne",
        rule_category="skincare",
        applied=True,
        details={
            "condition": "acne",
            "severity": "moderate",
            "step": 1,
            "action": "Gentle cleanser",
            "frequency": "2x daily",
            "reason": "Removes excess oil without stripping"
        }
    )
    db_session.add(rule_log)
    db_session.commit()
    return rule_log


@pytest.fixture
def sample_recommendation(db_session):
    """Create sample recommendation record for testing"""
    recommendation = RecommendationRecord(
        user_id=1,
        analysis_id=1,
        recommendation_id="rec_20251024_001",
        content={
            "skincare_routine": [
                {
                    "step": 1,
                    "action": "Gentle cleanser",
                    "frequency": "2x daily",
                    "why": "Removes excess oil"
                }
            ],
            "products": {
                "cleanser": {
                    "name": "CeraVe",
                    "price": 8.99
                }
            }
        },
        source="rule_v1",
        conditions_analyzed=["acne", "blackheads"],
        rules_applied=["acne_routine_step_1", "acne_routine_step_2"],
        generation_time_ms=450,
        user_budget="medium",
        user_allergies=["fragrance"],
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    db_session.add(recommendation)
    db_session.commit()
    return recommendation


# ===== PRODUCT MODEL TESTS =====

class TestProductModel:
    """Test Product model"""
    
    def test_create_product(self, db_session):
        """Test creating a product"""
        product = Product(
            name="Test Cleanser",
            brand="TestBrand",
            category="cleanser",
            price_usd=999,
            ingredients=["water", "glycerin"],
            tags=["gentle"],
            dermatologically_safe=True,
            recommended_for=["dry_skin"]
        )
        db_session.add(product)
        db_session.commit()
        
        assert product.id is not None
        assert product.name == "Test Cleanser"
        assert product.created_at is not None
    
    def test_product_to_dict(self, sample_product):
        """Test product to_dict conversion"""
        product_dict = sample_product.to_dict()
        
        assert product_dict["name"] == "CeraVe Hydrating Cleanser"
        assert product_dict["price_usd"] == 8.99
        assert product_dict["rating"] == 4.5
        assert "water" in product_dict["ingredients"]
        assert "gentle" in product_dict["tags"]
    
    def test_product_repr(self, sample_product):
        """Test product string representation"""
        assert "CeraVe" in repr(sample_product)
        assert "8.99" in repr(sample_product)
    
    def test_product_price_conversion(self, db_session):
        """Test price is stored and converted correctly"""
        product = Product(
            name="Test",
            brand="Test",
            category="cleanser",
            price_usd=1050  # $10.50
        )
        db_session.add(product)
        db_session.commit()
        
        retrieved = db_session.query(Product).first()
        assert retrieved.to_dict()["price_usd"] == 10.50


# ===== RULE LOG MODEL TESTS =====

class TestRuleLogModel:
    """Test RuleLog model"""
    
    def test_create_rule_log(self, db_session, sample_product):
        """Test creating a rule log"""
        rule_log = RuleLog(
            analysis_id=1,
            product_id=sample_product.id,
            rule_id="acne_routine_step_1",
            applied=True,
            details={"condition": "acne"}
        )
        db_session.add(rule_log)
        db_session.commit()
        
        assert rule_log.id is not None
        assert rule_log.applied == True
        assert rule_log.created_at is not None
    
    def test_rule_log_not_applied(self, db_session):
        """Test rule log with applied=False"""
        rule_log = RuleLog(
            analysis_id=1,
            rule_id="severe_acne_escalation",
            applied=False,
            reason_not_applied="Condition severity is mild"
        )
        db_session.add(rule_log)
        db_session.commit()
        
        retrieved = db_session.query(RuleLog).first()
        assert retrieved.applied == False
        assert "mild" in retrieved.reason_not_applied
    
    def test_rule_log_to_dict(self, sample_rule_log):
        """Test rule log to_dict conversion"""
        rule_dict = sample_rule_log.to_dict()
        
        assert rule_dict["rule_id"] == "acne_routine_step_1"
        assert rule_dict["applied"] == True
        assert rule_dict["details"]["condition"] == "acne"
    
    def test_rule_log_repr(self, sample_rule_log):
        """Test rule log string representation"""
        assert "acne_routine_step_1" in repr(sample_rule_log)
        assert "applied=True" in repr(sample_rule_log)


# ===== RECOMMENDATION RECORD MODEL TESTS =====

class TestRecommendationRecordModel:
    """Test RecommendationRecord model"""
    
    def test_create_recommendation(self, db_session):
        """Test creating a recommendation record"""
        recommendation = RecommendationRecord(
            user_id=1,
            analysis_id=1,
            recommendation_id="rec_20251024_001",
            content={"routine": [{"step": 1, "action": "Cleanse"}]},
            source="rule_v1"
        )
        db_session.add(recommendation)
        db_session.commit()
        
        assert recommendation.id is not None
        assert recommendation.recommendation_id == "rec_20251024_001"
        assert recommendation.created_at is not None
    
    def test_recommendation_expiration(self, db_session):
        """Test recommendation expiration date"""
        future_date = datetime.utcnow() + timedelta(days=30)
        recommendation = RecommendationRecord(
            user_id=1,
            analysis_id=1,
            recommendation_id="rec_test",
            content={},
            expires_at=future_date
        )
        db_session.add(recommendation)
        db_session.commit()
        
        assert recommendation.expires_at > datetime.utcnow()
    
    def test_recommendation_to_dict(self, sample_recommendation):
        """Test recommendation to_dict conversion"""
        rec_dict = sample_recommendation.to_dict(include_content=True)
        
        assert rec_dict["recommendation_id"] == "rec_20251024_001"
        assert rec_dict["user_budget"] == "medium"
        assert "acne" in rec_dict["conditions_analyzed"]
        assert rec_dict["content"] is not None
    
    def test_recommendation_to_dict_without_content(self, sample_recommendation):
        """Test recommendation to_dict without content"""
        rec_dict = sample_recommendation.to_dict(include_content=False)
        
        assert rec_dict["recommendation_id"] == "rec_20251024_001"
        assert rec_dict["content"] is None
    
    def test_recommendation_repr(self, sample_recommendation):
        """Test recommendation string representation"""
        assert "rec_20251024_001" in repr(sample_recommendation)
        assert "user_id=1" in repr(sample_recommendation)


# ===== RECOMMENDATION FEEDBACK MODEL TESTS =====

class TestRecommendationFeedbackModel:
    """Test RecommendationFeedback model"""
    
    def test_create_feedback(self, db_session, sample_recommendation):
        """Test creating feedback record"""
        feedback = RecommendationFeedback(
            user_id=1,
            analysis_id=1,
            recommendation_id=sample_recommendation.id,
            helpful_rating=4,
            product_satisfaction=4,
            routine_completion_pct=75,
            feedback_text="Great recommendations!"
        )
        db_session.add(feedback)
        db_session.commit()
        
        assert feedback.id is not None
        assert feedback.helpful_rating == 4
        assert feedback.created_at is not None
    
    def test_feedback_ratings_validation(self, db_session, sample_recommendation):
        """Test feedback with various ratings"""
        for rating in [1, 2, 3, 4, 5]:
            feedback = RecommendationFeedback(
                user_id=1,
                analysis_id=1,
                recommendation_id=sample_recommendation.id,
                helpful_rating=rating
            )
            db_session.add(feedback)
        
        db_session.commit()
        feedbacks = db_session.query(RecommendationFeedback).all()
        assert len(feedbacks) == 5
    
    def test_feedback_product_ratings(self, db_session, sample_recommendation):
        """Test feedback with individual product ratings"""
        product_ratings = {
            "cleanser": 5,
            "treatment": 4,
            "moisturizer": 5
        }
        feedback = RecommendationFeedback(
            user_id=1,
            analysis_id=1,
            recommendation_id=sample_recommendation.id,
            product_ratings=product_ratings
        )
        db_session.add(feedback)
        db_session.commit()
        
        retrieved = db_session.query(RecommendationFeedback).first()
        assert retrieved.product_ratings["cleanser"] == 5
    
    def test_feedback_to_dict(self, db_session, sample_recommendation):
        """Test feedback to_dict conversion"""
        feedback = RecommendationFeedback(
            user_id=1,
            analysis_id=1,
            recommendation_id=sample_recommendation.id,
            helpful_rating=4,
            product_satisfaction=4,
            routine_completion_pct=75,
            would_recommend=True,
            feedback_text="Excellent!"
        )
        db_session.add(feedback)
        db_session.commit()
        
        feedback_dict = feedback.to_dict()
        assert feedback_dict["helpful_rating"] == 4
        assert feedback_dict["would_recommend"] == True
        assert "Excellent" in feedback_dict["feedback_text"]
    
    def test_feedback_repr(self, db_session, sample_recommendation):
        """Test feedback string representation"""
        feedback = RecommendationFeedback(
            user_id=1,
            analysis_id=1,
            recommendation_id=sample_recommendation.id,
            helpful_rating=4,
            product_satisfaction=4
        )
        db_session.add(feedback)
        db_session.commit()
        
        assert "helpful=4" in repr(feedback)
        assert "satisfaction=4" in repr(feedback)


# ===== INTEGRATION TESTS =====

class TestModelIntegration:
    """Integration tests for recommender models"""
    
    def test_product_rule_log_relationship(self, db_session, sample_product, sample_rule_log):
        """Test relationship between Product and RuleLog"""
        assert len(sample_product.rule_logs) == 1
        assert sample_product.rule_logs[0].rule_id == "acne_routine_step_1"
    
    def test_recommendation_feedback_relationship(self, db_session, sample_recommendation):
        """Test relationship between Recommendation and Feedback"""
        feedback = RecommendationFeedback(
            user_id=1,
            analysis_id=1,
            recommendation_id=sample_recommendation.id,
            helpful_rating=5
        )
        db_session.add(feedback)
        db_session.commit()
        
        assert len(sample_recommendation.feedbacks) == 1
        assert sample_recommendation.feedbacks[0].helpful_rating == 5
    
    def test_multiple_feedbacks_for_recommendation(self, db_session, sample_recommendation):
        """Test multiple feedbacks for single recommendation"""
        for i in range(3):
            feedback = RecommendationFeedback(
                user_id=i+1,
                analysis_id=i+1,
                recommendation_id=sample_recommendation.id,
                helpful_rating=4+i
            )
            db_session.add(feedback)
        
        db_session.commit()
        
        assert len(sample_recommendation.feedbacks) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
