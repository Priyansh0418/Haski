"""
Unit Tests for Product Ranking Module

Test Coverage:
- AllergySafetyFilter: Allergen detection and filtering
- DermatologicalRanker: Safety and quality scoring
- FeedbackScorer: Feedback-based scoring
- RankerEngine: Complete ranking pipeline
- rank_products: Main convenience function
- Edge cases: Empty lists, no allergies, perfect products, etc.

Run with: pytest test_ranker.py -v
"""

import pytest
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from unittest.mock import Mock, MagicMock, patch

# Import the ranker module
from backend.app.recommender.ranker import (
    UserProfile,
    RankedProduct,
    AllergySafetyFilter,
    DermatologicalRanker,
    FeedbackScorer,
    RankerEngine,
    rank_products,
)


# ===== MOCK PRODUCT CLASS =====

class MockProduct:
    """Mock Product for testing"""
    
    def __init__(
        self,
        id: int,
        name: str,
        brand: str,
        category: str = "moisturizer",
        price_usd: int = 2500,
        ingredients: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        dermatologically_safe: bool = True,
        recommended_for: Optional[List[str]] = None,
        avoid_for: Optional[List[str]] = None,
        avg_rating: int = 400,
        review_count: int = 100
    ):
        self.id = id
        self.name = name
        self.brand = brand
        self.category = category
        self.price_usd = price_usd
        self.ingredients = ingredients or []
        self.tags = tags or []
        self.dermatologically_safe = dermatologically_safe
        self.recommended_for = recommended_for or []
        self.avoid_for = avoid_for or []
        self.avg_rating = avg_rating
        self.review_count = review_count
        self.url = "https://example.com"
        self.external_id = f"test_{id}"
        self.created_at = None
        self.updated_at = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'brand': self.brand,
            'category': self.category,
            'price_usd': self.price_usd / 100,
            'ingredients': self.ingredients,
            'tags': self.tags,
            'dermatologically_safe': self.dermatologically_safe,
            'recommended_for': self.recommended_for,
            'avoid_for': self.avoid_for,
            'rating': self.avg_rating / 100 if self.avg_rating else None,
        }


# ===== TEST FIXTURES =====

@pytest.fixture
def sample_products():
    """Create sample products for testing"""
    return [
        MockProduct(
            id=1,
            name="CeraVe Moisturizing Cream",
            brand="CeraVe",
            ingredients=["water", "glycerin", "ceramides"],
            tags=["gentle", "hydrating", "hypoallergenic"],
            dermatologically_safe=True,
            recommended_for=["dry_skin", "sensitive"],
            avoid_for=[],
            avg_rating=450,
            review_count=500
        ),
        MockProduct(
            id=2,
            name="Neutrogena Acne Cleanser",
            brand="Neutrogena",
            ingredients=["water", "salicylic_acid", "benzoyl_peroxide"],
            tags=["acne-fighting", "exfoliating"],
            dermatologically_safe=True,
            recommended_for=["acne", "oily_skin"],
            avoid_for=["sensitive"],
            avg_rating=380,
            review_count=300
        ),
        MockProduct(
            id=3,
            name="The Ordinary Retinol",
            brand="The Ordinary",
            ingredients=["retinol", "squalane", "vitamin_e"],
            tags=["anti-aging", "powerful"],
            dermatologically_safe=False,
            recommended_for=["aging", "fine_lines"],
            avoid_for=["pregnancy", "sensitive"],
            avg_rating=420,
            review_count=200
        ),
        MockProduct(
            id=4,
            name="La Roche Posay Sunscreen",
            brand="La Roche Posay",
            ingredients=["zinc_oxide", "titanium_dioxide", "glycerin"],
            tags=["sun_protection", "mineral"],
            dermatologically_safe=True,
            recommended_for=["all_skin_types"],
            avoid_for=[],
            avg_rating=480,
            review_count=600
        ),
    ]


@pytest.fixture
def user_profile_basic():
    """Create basic user profile"""
    return UserProfile(
        user_id=1,
        allergies=None,
        age=25,
        skin_type="oily",
        conditions=["acne", "oily_skin"]
    )


@pytest.fixture
def user_profile_with_allergies():
    """Create user profile with allergies"""
    return UserProfile(
        user_id=2,
        allergies=["benzoyl_peroxide", "salicylic_acid"],
        age=30,
        skin_type="sensitive",
        conditions=["sensitive", "dry_skin"]
    )


# ===== TESTS: UserProfile =====

class TestUserProfile:
    """Test UserProfile class"""
    
    def test_allergies_as_string(self):
        """Test allergies parsed from comma-separated string"""
        profile = UserProfile(
            user_id=1,
            allergies="benzoyl_peroxide, salicylic_acid, fragrance"
        )
        allergies = profile.get_allergies_set()
        
        assert "benzoyl_peroxide" in allergies
        assert "salicylic_acid" in allergies
        assert "fragrance" in allergies
        assert len(allergies) == 3
    
    def test_allergies_as_list(self):
        """Test allergies as list"""
        profile = UserProfile(
            user_id=1,
            allergies=["benzoyl_peroxide", "salicylic_acid"]
        )
        allergies = profile.get_allergies_set()
        
        assert "benzoyl_peroxide" in allergies
        assert "salicylic_acid" in allergies
    
    def test_no_allergies(self):
        """Test profile with no allergies"""
        profile = UserProfile(user_id=1)
        allergies = profile.get_allergies_set()
        
        assert len(allergies) == 0
        assert isinstance(allergies, set)
    
    def test_allergies_case_insensitive(self):
        """Test that allergies are normalized to lowercase"""
        profile = UserProfile(
            user_id=1,
            allergies="Benzoyl_Peroxide, SALICYLIC_ACID"
        )
        allergies = profile.get_allergies_set()
        
        assert "benzoyl_peroxide" in allergies
        assert "salicylic_acid" in allergies


# ===== TESTS: AllergySafetyFilter =====

class TestAllergySafetyFilter:
    """Test allergen filtering"""
    
    def test_filter_no_allergies(self, sample_products):
        """Test filtering with no allergies"""
        allergies = set()
        safe, issues = AllergySafetyFilter.filter_safe_products(
            sample_products,
            allergies
        )
        
        assert len(safe) == len(sample_products)
        assert len(issues) == 0
    
    def test_filter_by_ingredient(self, sample_products):
        """Test filtering by ingredient allergen"""
        allergies = {"benzoyl_peroxide"}
        safe, issues = AllergySafetyFilter.filter_safe_products(
            sample_products,
            allergies
        )
        
        # Product 2 has benzoyl_peroxide
        assert sample_products[1].id in issues
        assert len(issues) == 1
    
    def test_filter_by_tag(self, sample_products):
        """Test filtering by tag allergen"""
        allergies = {"acne-fighting"}
        safe, issues = AllergySafetyFilter.filter_safe_products(
            sample_products,
            allergies
        )
        
        # Product 2 is tagged acne-fighting
        assert sample_products[1].id in issues
    
    def test_filter_by_avoid_for(self, sample_products):
        """Test filtering by avoid_for recommendation"""
        allergies = {"sensitive"}
        safe, issues = AllergySafetyFilter.filter_safe_products(
            sample_products,
            allergies
        )
        
        # Product 2 should be avoided for sensitive
        assert sample_products[1].id in issues
    
    def test_filter_strict_mode(self, sample_products):
        """Test strict mode removes all allergen products"""
        allergies = {"benzoyl_peroxide"}
        safe, issues = AllergySafetyFilter.filter_safe_products(
            sample_products,
            allergies,
            strict_mode=True
        )
        
        # Strict mode excludes products with issues
        assert sample_products[1].id not in [p.id for p in safe]
        assert len(safe) == len(sample_products) - 1


# ===== TESTS: DermatologicalRanker =====

class TestDermatologicalRanker:
    """Test dermatological safety scoring"""
    
    def test_score_dermatological_safe(self):
        """Test scoring dermatologically safe products"""
        product = MockProduct(
            id=1,
            name="Safe Product",
            brand="Brand",
            dermatologically_safe=True,
            recommended_for=["acne", "oily_skin", "sensitive"]
        )
        
        score = DermatologicalRanker.score_dermatological_safety(product)
        
        assert score >= 100  # Should be maxed out
        assert score <= 120  # With bonuses
    
    def test_score_dermatological_unsafe(self):
        """Test scoring non-dermatologically tested products"""
        product = MockProduct(
            id=1,
            name="Untested Product",
            brand="Brand",
            dermatologically_safe=False,
            recommended_for=[]
        )
        
        score = DermatologicalRanker.score_dermatological_safety(product)
        
        assert score < 100
        assert score >= 0
    
    def test_score_product_quality_high_rating(self):
        """Test quality scoring for highly rated products"""
        product = MockProduct(
            id=1,
            name="Great Product",
            brand="Brand",
            avg_rating=480,  # 4.8 stars
            review_count=200
        )
        
        score = DermatologicalRanker.score_product_quality(product)
        
        assert score > 50
        assert score <= 100
    
    def test_score_product_quality_low_rating(self):
        """Test quality scoring for low-rated products"""
        product = MockProduct(
            id=1,
            name="Poor Product",
            brand="Brand",
            avg_rating=200,  # 2.0 stars
            review_count=50
        )
        
        score = DermatologicalRanker.score_product_quality(product)
        
        assert score >= 0
        assert score < 50
    
    def test_score_product_quality_no_reviews(self):
        """Test quality scoring for unreviewed products"""
        product = MockProduct(
            id=1,
            name="Unreviewed Product",
            brand="Brand",
            avg_rating=0,
            review_count=0
        )
        
        score = DermatologicalRanker.score_product_quality(product)
        
        assert score == 0


# ===== TESTS: RankerEngine =====

class TestRankerEngine:
    """Test main ranking engine"""
    
    def test_rank_empty_list(self):
        """Test ranking empty product list"""
        engine = RankerEngine()
        profile = UserProfile(user_id=1)
        
        ranked = engine.rank_products([], profile, k=5)
        
        assert len(ranked) == 0
    
    def test_rank_k_parameter(self, sample_products):
        """Test that k parameter limits results"""
        engine = RankerEngine()
        profile = UserProfile(user_id=1)
        
        ranked = engine.rank_products(sample_products, profile, k=2)
        
        assert len(ranked) == 2
    
    def test_rank_k_exceeds_products(self, sample_products):
        """Test k > number of products"""
        engine = RankerEngine()
        profile = UserProfile(user_id=1)
        
        ranked = engine.rank_products(sample_products, profile, k=100)
        
        assert len(ranked) == len(sample_products)
    
    def test_ranked_product_structure(self, sample_products):
        """Test RankedProduct has required fields"""
        engine = RankerEngine()
        profile = UserProfile(user_id=1)
        
        ranked = engine.rank_products(sample_products, profile, k=1)
        
        assert len(ranked) == 1
        ranked_product = ranked[0]
        assert isinstance(ranked_product, RankedProduct)
        assert hasattr(ranked_product, 'product')
        assert hasattr(ranked_product, 'score')
        assert hasattr(ranked_product, 'rank')
        assert hasattr(ranked_product, 'reasons')
        assert ranked_product.rank == 1
    
    def test_ranked_product_ordering(self, sample_products):
        """Test products are ranked in descending order by score"""
        engine = RankerEngine()
        profile = UserProfile(user_id=1)
        
        ranked = engine.rank_products(sample_products, profile, k=len(sample_products))
        
        # Verify ranks are sequential
        for i, ranked_product in enumerate(ranked, 1):
            assert ranked_product.rank == i
        
        # Verify scores are descending
        scores = [r.score for r in ranked]
        assert scores == sorted(scores, reverse=True)
    
    def test_filter_by_allergies(self, sample_products, user_profile_with_allergies):
        """Test that products with allergies are penalized"""
        engine = RankerEngine()
        
        ranked = engine.rank_products(sample_products, user_profile_with_allergies, k=4)
        
        # Product 2 (benzoyl_peroxide) should have warnings
        product_2_ranked = next((r for r in ranked if r.product.id == 2), None)
        if product_2_ranked:
            assert product_2_ranked.safety_issues is not None
            assert len(product_2_ranked.safety_issues) > 0
    
    def test_condition_match_scoring(self):
        """Test scoring based on condition match"""
        product = MockProduct(
            id=1,
            name="Acne Product",
            recommended_for=["acne", "oily_skin"]
        )
        profile = UserProfile(
            user_id=1,
            conditions=["acne", "blackheads"]
        )
        
        engine = RankerEngine()
        score = engine._score_condition_match(product, profile)
        
        assert score > 50  # Should have some match
    
    def test_condition_no_match(self):
        """Test scoring with no condition match"""
        product = MockProduct(
            id=1,
            name="Aging Product",
            recommended_for=["fine_lines", "wrinkles"]
        )
        profile = UserProfile(
            user_id=1,
            conditions=["acne", "oily_skin"]
        )
        
        engine = RankerEngine()
        score = engine._score_condition_match(product, profile)
        
        assert score < 50  # Should be low with no match


# ===== TESTS: FeedbackScorer =====

class TestFeedbackScorer:
    """Test feedback-based scoring"""
    
    def test_score_from_no_feedback(self):
        """Test scoring when no feedback exists"""
        feedback_stats = {
            'avg_rating': 0,
            'helpful_count': 0,
            'total_feedback': 0,
            'user_rated_before': False,
            'user_rating': None
        }
        
        score = FeedbackScorer.score_from_feedback(feedback_stats)
        
        assert score == 50  # Neutral score
    
    def test_score_from_high_feedback(self):
        """Test scoring with high feedback"""
        feedback_stats = {
            'avg_rating': 4.5,
            'helpful_count': 8,
            'total_feedback': 10,
            'user_rated_before': True,
            'user_rating': 5
        }
        
        score = FeedbackScorer.score_from_feedback(feedback_stats)
        
        assert score > 50
    
    def test_score_from_low_feedback(self):
        """Test scoring with low feedback"""
        feedback_stats = {
            'avg_rating': 1.5,
            'helpful_count': 1,
            'total_feedback': 10,
            'user_rated_before': False,
            'user_rating': None
        }
        
        score = FeedbackScorer.score_from_feedback(feedback_stats)
        
        assert score < 50


# ===== TESTS: Main rank_products Function =====

class TestRankProductsFunction:
    """Test main convenience function"""
    
    def test_rank_products_basic(self, sample_products, user_profile_basic):
        """Test basic ranking"""
        ranked = rank_products(sample_products, user_profile_basic, k=3)
        
        assert len(ranked) == 3
        assert all(isinstance(r, RankedProduct) for r in ranked)
    
    def test_rank_products_with_allergies(self, sample_products, user_profile_with_allergies):
        """Test ranking with allergy filtering"""
        ranked = rank_products(sample_products, user_profile_with_allergies, k=4)
        
        assert len(ranked) <= 4
        # Should not have benzoyl_peroxide products at top
        top_product = ranked[0]
        assert "benzoyl_peroxide" not in [i.lower() for i in top_product.product.ingredients]
    
    def test_ranked_to_dict(self, sample_products, user_profile_basic):
        """Test RankedProduct.to_dict() conversion"""
        ranked = rank_products(sample_products, user_profile_basic, k=1)
        
        product_dict = ranked[0].to_dict()
        
        assert 'id' in product_dict
        assert 'name' in product_dict
        assert 'ranking_score' in product_dict
        assert 'rank' in product_dict
        assert 'ranking_reasons' in product_dict


# ===== INTEGRATION TESTS =====

class TestRankingIntegration:
    """Integration tests for complete ranking pipeline"""
    
    def test_end_to_end_ranking(self, sample_products):
        """Test complete ranking workflow"""
        profile = UserProfile(
            user_id=1,
            allergies="salicylic_acid, retinol",
            age=25,
            skin_type="oily",
            conditions=["acne", "oily_skin"]
        )
        
        ranked = rank_products(sample_products, profile, k=5)
        
        assert len(ranked) > 0
        assert all(r.rank > 0 for r in ranked)
        assert all(len(r.reasons) > 0 for r in ranked)
    
    def test_ranking_with_extreme_allergies(self, sample_products):
        """Test ranking with user having many allergies"""
        profile = UserProfile(
            user_id=1,
            allergies="benzoyl_peroxide, salicylic_acid, retinol, fragrance",
            skin_type="sensitive"
        )
        
        ranked = rank_products(sample_products, profile, k=len(sample_products))
        
        # Should still rank all products but with warnings
        assert len(ranked) > 0
    
    def test_ranking_deterministic(self, sample_products, user_profile_basic):
        """Test that ranking is deterministic"""
        ranked1 = rank_products(sample_products, user_profile_basic, k=5)
        ranked2 = rank_products(sample_products, user_profile_basic, k=5)
        
        # Same order and scores
        for r1, r2 in zip(ranked1, ranked2):
            assert r1.product.id == r2.product.id
            assert r1.score == r2.score


# ===== EDGE CASE TESTS =====

class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_single_product(self):
        """Test ranking single product"""
        product = MockProduct(id=1, name="Only Product", brand="Brand")
        profile = UserProfile(user_id=1)
        
        ranked = rank_products([product], profile, k=5)
        
        assert len(ranked) == 1
        assert ranked[0].rank == 1
    
    def test_products_with_missing_fields(self):
        """Test ranking products with missing optional fields"""
        product = MockProduct(
            id=1,
            name="Minimal Product",
            brand="Brand",
            ingredients=None,
            tags=None,
            recommended_for=None,
            avg_rating=0,
            review_count=0
        )
        profile = UserProfile(user_id=1)
        
        ranked = rank_products([product], profile, k=1)
        
        assert len(ranked) == 1
        assert isinstance(ranked[0].score, (int, float))
    
    def test_k_zero(self, sample_products):
        """Test k=0 returns empty list"""
        profile = UserProfile(user_id=1)
        
        ranked = rank_products(sample_products, profile, k=0)
        
        assert len(ranked) == 0
    
    def test_all_products_allergen_issue(self):
        """Test when all products have allergen concerns"""
        products = [
            MockProduct(
                id=1,
                name="P1",
                brand="B",
                ingredients=["allergen1"]
            ),
            MockProduct(
                id=2,
                name="P2",
                brand="B",
                ingredients=["allergen1"]
            ),
        ]
        profile = UserProfile(
            user_id=1,
            allergies="allergen1"
        )
        
        ranked = rank_products(products, profile, k=2)
        
        # Should still rank all products but with penalties/warnings
        assert len(ranked) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
