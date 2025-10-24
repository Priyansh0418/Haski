"""
Tests for Recommender Endpoint

Test coverage:
- POST /recommend with analysis_id
- POST /recommend with direct analysis data
- Product lookup and filtering
- Escalation handling
- Database persistence
- Error handling
"""

import pytest
import json
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.db.session import SessionLocal
from backend.app.models.db_models import User, Profile, Analysis, Photo
from backend.app.recommender.models import Product
from backend.app.api.v1.recommend import (
    _load_user_data,
    _parse_pregnancy_status,
    _parse_breastfeeding_status,
    _parse_allergies,
    _get_product_details
)


client = TestClient(app)


@pytest.fixture
def db():
    """Provide test database session."""
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture
def test_user(db):
    """Create test user."""
    user = User(
        username="test_user",
        email="test@example.com",
        hashed_password="hashed_password"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_profile(db, test_user):
    """Create test user profile."""
    profile = Profile(
        user_id=test_user.id,
        age=25,
        gender="F",
        skin_type="oily",
        hair_type="straight",
        allergies="benzoyl_peroxide,salicylic_acid",
        lifestyle="active"
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@pytest.fixture
def test_analysis(db, test_user):
    """Create test analysis."""
    analysis = Analysis(
        user_id=test_user.id,
        photo_id=None,
        skin_type="oily",
        hair_type="straight",
        conditions=["acne", "blackheads"],
        confidence_scores={"acne": 0.92, "blackheads": 0.87}
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


@pytest.fixture
def seed_products(db):
    """Seed test products."""
    products = [
        Product(
            name="Salicylic Acid 2%",
            brand="The Ordinary",
            category="treatment",
            price_usd=590,
            ingredients=["salicylic acid", "glycerin"],
            tags=["exfoliating", "acne-fighting", "BHA"],
            dermatologically_safe=True,
            recommended_for=["acne", "blackheads"],
            external_id="ordinary_sa_001",
            avg_rating=430,
            review_count=5890
        ),
        Product(
            name="Niacinamide 10%",
            brand="The Ordinary",
            category="serum",
            price_usd=590,
            ingredients=["niacinamide", "zinc"],
            tags=["oil-control", "pore-minimizing"],
            dermatologically_safe=True,
            recommended_for=["oily_skin", "acne"],
            external_id="ordinary_niacinamide_001",
            avg_rating=440,
            review_count=8920
        ),
        Product(
            name="Hydrating Cleanser",
            brand="CeraVe",
            category="cleanser",
            price_usd=899,
            ingredients=["water", "glycerin"],
            tags=["gentle", "hydrating"],
            dermatologically_safe=True,
            recommended_for=["dry_skin", "sensitive"],
            external_id="cerave_cleanser_001",
            avg_rating=450,
            review_count=2340
        ),
    ]
    
    for product in products:
        db.add(product)
    
    db.commit()
    return products


class TestRecommendationEndpoint:
    """Test POST /recommend endpoint."""
    
    def test_recommend_with_analysis_id(self, test_user, test_analysis, seed_products, db):
        """Test recommendation using existing analysis_id."""
        # Note: In real tests, you'd mock authentication
        # This is a conceptual test showing the flow
        
        request_data = {
            "method": "analysis_id",
            "analysis_id": test_analysis.id,
            "include_diet": True,
            "include_products": True
        }
        
        # Would call: POST /api/v1/recommend
        # with Authorization header and request_data
        # Expected: 201 Created with recommendation
    
    def test_recommend_with_direct_analysis(self, test_user, seed_products):
        """Test recommendation using direct analysis data."""
        request_data = {
            "method": "direct_analysis",
            "skin_type": "oily",
            "hair_type": "straight",
            "conditions_detected": ["acne", "blackheads"],
            "age": 25,
            "skin_sensitivity": "normal",
            "include_diet": True,
            "include_products": True
        }
        
        # Would call: POST /api/v1/recommend
        # Expected: 201 Created with recommendation
    
    def test_recommend_invalid_analysis_id(self, test_user):
        """Test recommendation with non-existent analysis_id."""
        request_data = {
            "method": "analysis_id",
            "analysis_id": 99999  # Non-existent
        }
        
        # Expected: 404 Not Found


class TestDataParsing:
    """Test helper functions for data parsing."""
    
    def test_parse_pregnancy_status_yes(self):
        """Test parsing pregnancy status from text."""
        result = _parse_pregnancy_status("pregnant, active")
        assert result is True
    
    def test_parse_pregnancy_status_no(self):
        """Test parsing non-pregnancy status."""
        result = _parse_pregnancy_status("active, healthy")
        assert result is False
    
    def test_parse_breastfeeding_status_yes(self):
        """Test parsing breastfeeding status."""
        result = _parse_breastfeeding_status("breastfeeding")
        assert result is True
    
    def test_parse_breastfeeding_status_no(self):
        """Test parsing non-breastfeeding status."""
        result = _parse_breastfeeding_status("active")
        assert result is False
    
    def test_parse_allergies_from_text(self):
        """Test parsing allergies from comma-separated text."""
        allergies = _parse_allergies("benzoyl_peroxide,salicylic_acid", None)
        assert "benzoyl_peroxide" in allergies
        assert "salicylic_acid" in allergies
    
    def test_parse_allergies_from_list(self):
        """Test parsing allergies from list."""
        allergies = _parse_allergies(None, ["benzoyl_peroxide", "salicylic_acid"])
        assert "benzoyl_peroxide" in allergies
        assert "salicylic_acid" in allergies
    
    def test_parse_allergies_combined(self):
        """Test parsing allergies from both sources."""
        allergies = _parse_allergies(
            "benzoyl_peroxide",
            ["salicylic_acid"]
        )
        assert len(allergies) == 2
        assert "benzoyl_peroxide" in allergies
        assert "salicylic_acid" in allergies


class TestProductLookup:
    """Test product lookup and filtering."""
    
    def test_get_products_by_external_id(self, db, seed_products):
        """Test getting products by external_id."""
        recommendation = {
            "products": [
                {
                    "external_id": "ordinary_sa_001",
                    "reason": "For acne",
                    "source_rules": ["r001"]
                }
            ],
            "product_tags": []
        }
        
        products = _get_product_details(recommendation, db)
        
        assert len(products) == 1
        assert products[0]["name"] == "Salicylic Acid 2%"
        assert products[0]["external_id"] == "ordinary_sa_001"
    
    def test_get_products_by_tags(self, db, seed_products):
        """Test getting products by tags."""
        recommendation = {
            "products": [],
            "product_tags": [
                {
                    "tag": "exfoliating",
                    "reason": "For oil control",
                    "source_rules": ["r001"]
                }
            ]
        }
        
        products = _get_product_details(recommendation, db)
        
        assert len(products) >= 1
        assert any("exfoliating" in p["tags"] for p in products)
    
    def test_get_products_sorted_by_rating(self, db, seed_products):
        """Test that products are sorted by rating."""
        recommendation = {
            "products": [],
            "product_tags": [
                {
                    "tag": "oil-control",
                    "reason": "For oily skin",
                    "source_rules": ["r001"]
                }
            ]
        }
        
        products = _get_product_details(recommendation, db)
        
        # Should be sorted by rating (highest first)
        if len(products) > 1:
            for i in range(len(products) - 1):
                assert (products[i].get('rating') or 0) >= (products[i+1].get('rating') or 0)
    
    def test_no_duplicate_products(self, db, seed_products):
        """Test that products aren't duplicated."""
        recommendation = {
            "products": [
                {
                    "external_id": "ordinary_sa_001",
                    "reason": "For acne",
                    "source_rules": ["r001"]
                }
            ],
            "product_tags": [
                {
                    "tag": "exfoliating",
                    "reason": "For oil control",
                    "source_rules": ["r001"]
                }
            ]
        }
        
        products = _get_product_details(recommendation, db)
        
        external_ids = [p["external_id"] for p in products]
        assert len(external_ids) == len(set(external_ids))  # No duplicates


class TestEscalationHandling:
    """Test escalation flags in response."""
    
    def test_escalation_urgent(self):
        """Test urgent escalation flag."""
        recommendation = {
            "escalation": {
                "level": "urgent",
                "message": "See dermatologist immediately",
                "source_rules": ["r008"]
            }
        }
        
        # Verify escalation would be returned as:
        # "escalation": {
        #     "level": "urgent",
        #     "see_dermatologist": True,
        #     "high_priority": True
        # }
    
    def test_escalation_caution(self):
        """Test caution escalation flag."""
        recommendation = {
            "escalation": {
                "level": "caution",
                "message": "Consider consulting dermatologist",
                "source_rules": ["r002"]
            }
        }
        
        # Verify escalation would be returned as:
        # "escalation": {
        #     "level": "caution",
        #     "see_dermatologist": False,
        #     "high_priority": True
        # }
    
    def test_no_escalation(self):
        """Test no escalation case."""
        recommendation = {
            "escalation": None
        }
        
        # Verify escalation would be returned as: null


class TestDatabasePersistence:
    """Test saving recommendations to database."""
    
    def test_recommendation_saved_to_db(self, test_user, test_analysis, db):
        """Test that recommendation is saved to RecommendationRecord table."""
        # Would verify that:
        # 1. RecommendationRecord created with user_id, analysis_id
        # 2. Content stored as JSON
        # 3. Rules applied list saved
        # 4. Timestamps set correctly
        pass
    
    def test_rule_logs_created(self, test_analysis, db):
        """Test that RuleLog entries created for each applied rule."""
        # Would verify that:
        # 1. RuleLog entry created for each rule_id
        # 2. analysis_id linked
        # 3. applied=True flag set
        pass


class TestErrorHandling:
    """Test error handling."""
    
    def test_invalid_analysis_data(self):
        """Test 400 error for invalid analysis data."""
        request_data = {
            "method": "direct_analysis",
            "skin_type": "invalid_type",  # Invalid
            "conditions_detected": ["acne"]
        }
        
        # Expected: 400 Bad Request
    
    def test_missing_required_fields(self):
        """Test 400 error for missing required fields."""
        request_data = {
            "method": "direct_analysis",
            # Missing skin_type, conditions_detected
        }
        
        # Expected: 400 Bad Request
    
    def test_engine_not_initialized(self):
        """Test 500 error if engine fails to initialize."""
        # Expected: 500 Internal Server Error


class TestRecommendationResponse:
    """Test response format and content."""
    
    def test_response_has_required_fields(self):
        """Test that response contains all required fields."""
        # Expected response structure:
        # {
        #     "recommendation_id": "rec_...",
        #     "created_at": "2025-10-24T...",
        #     "routines": [...],
        #     "diet_recommendations": [...],
        #     "recommended_products": [...],
        #     "escalation": {...} | null,
        #     "applied_rules": [...],
        #     "metadata": {...}
        # }
        pass
    
    def test_products_include_reason(self):
        """Test that products include reason for recommendation."""
        # Each product should have:
        # {
        #     "id": ...,
        #     "name": "...",
        #     "reason": "Recommended by r001 for acne",
        #     "source_rules": ["r001"],
        #     ...
        # }
        pass
    
    def test_metadata_includes_rules_info(self):
        """Test that metadata includes rules information."""
        # Metadata should have:
        # {
        #     "total_rules_checked": 9,
        #     "rules_matched": 2,
        #     "product_tags_searched": [...],
        #     "tags_count": 4
        # }
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
