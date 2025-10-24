"""
Product Ranking Module for Recommendation System

Lightweight ranking module that orders products based on:
- Dermatological safety
- Profile allergy filters
- Feedback history
- Product ratings and reviews
- User preferences

Key Components:
- RankerEngine: Main ranking class
- rank_products(): Main ranking function
- AllergySafetyFilter: Filters products by user allergies
- DermatologicalRanker: Prioritizes dermatologically safe products
- FeedbackScorer: Scores products based on historical feedback

Usage:
    from backend.app.recommender.ranker import rank_products
    from sqlalchemy.orm import Session
    
    ranked = rank_products(
        products_list=product_objects,
        user_profile=user_profile,
        db=db_session,
        k=5
    )

TODO: Replace rule-based ranking with ML model (contextual bandit approach):
    - Track user interactions (click, view, add-to-cart, purchase)
    - Train contextual bandit model on user features + product features
    - Use epsilon-greedy strategy for exploration/exploitation
    - Implement Thompson sampling for posterior sampling
    - A/B test model performance vs rule-based baseline
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from sqlalchemy.orm import Session
from sqlalchemy import func

logger = logging.getLogger(__name__)


@dataclass
class UserProfile:
    """User profile for ranking context"""
    user_id: int
    allergies: Optional[List[str]] = None
    age: Optional[int] = None
    skin_type: Optional[str] = None
    hair_type: Optional[str] = None
    conditions: Optional[List[str]] = None
    
    def get_allergies_set(self) -> set:
        """Get allergies as lowercase set for matching"""
        if not self.allergies:
            return set()
        
        # Handle both comma-separated strings and lists
        if isinstance(self.allergies, str):
            return set(a.strip().lower() for a in self.allergies.split(',') if a.strip())
        elif isinstance(self.allergies, list):
            return set(a.lower() for a in self.allergies if a)
        return set()


@dataclass
class RankedProduct:
    """Product with ranking score and metadata"""
    product: Any  # SQLAlchemy Product model
    score: float
    rank: int
    reasons: List[str]  # Why this product was ranked here
    safety_issues: List[str] = None  # Any allergy/safety warnings
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        product_dict = self.product.to_dict() if hasattr(self.product, 'to_dict') else {
            'id': self.product.id,
            'name': self.product.name,
            'brand': self.product.brand
        }
        return {
            **product_dict,
            'ranking_score': round(self.score, 3),
            'rank': self.rank,
            'ranking_reasons': self.reasons,
            'safety_issues': self.safety_issues or []
        }


class AllergySafetyFilter:
    """Filter products by user allergies"""
    
    @staticmethod
    def filter_safe_products(
        products: List[Any],
        user_allergies: set,
        strict_mode: bool = False
    ) -> Tuple[List[Any], Dict[int, List[str]]]:
        """
        Filter products by allergen content.
        
        Args:
            products: List of product objects
            user_allergies: Set of allergens user is allergic to (lowercase)
            strict_mode: If True, exclude products with any potential allergen cross-contact
        
        Returns:
            (safe_products, products_with_issues) where products_with_issues maps
            product_id -> list of allergen concerns
        """
        safe_products = []
        products_with_issues = {}
        
        for product in products:
            allergies_found = []
            
            # Check main ingredients
            ingredients = product.ingredients or []
            for ingredient in ingredients:
                ingredient_lower = ingredient.lower()
                for allergen in user_allergies:
                    if allergen in ingredient_lower or ingredient_lower in allergen:
                        allergies_found.append(f"Ingredient: {ingredient}")
            
            # Check tags for allergen warnings
            tags = product.tags or []
            tag_str = ' '.join(tags).lower()
            for allergen in user_allergies:
                if allergen in tag_str:
                    allergies_found.append(f"Tagged: {allergen}")
            
            # Check avoid_for conditions
            avoid_for = product.avoid_for or []
            avoid_str = ' '.join(avoid_for).lower()
            for allergen in user_allergies:
                if allergen in avoid_str:
                    allergies_found.append(f"Avoid recommendation: {allergen}")
            
            if allergies_found:
                products_with_issues[product.id] = allergies_found
                if not strict_mode:
                    safe_products.append(product)
            else:
                safe_products.append(product)
        
        return safe_products, products_with_issues
    
    @staticmethod
    def has_allergen_concern(product: Any, user_allergies: set) -> bool:
        """Check if product has any allergen concerns for user"""
        allergies = AllergySafetyFilter.filter_safe_products([product], user_allergies)[1]
        return product.id in allergies


class DermatologicalRanker:
    """Score products based on dermatological credentials"""
    
    DERMATOLOGICAL_WEIGHT = 0.25  # 25% of ranking score
    RATING_WEIGHT = 0.20  # 20% of ranking score
    REVIEW_COUNT_WEIGHT = 0.10  # 10% of ranking score
    
    @staticmethod
    def score_dermatological_safety(product: Any) -> float:
        """
        Score product's dermatological credentials.
        
        Args:
            product: Product object
        
        Returns:
            Score 0-100 based on safety credentials
        """
        score = 0
        
        # Base: dermatologically tested
        if product.dermatologically_safe:
            score += 100
        else:
            score += 40
        
        # Boost: recommended for conditions (suggests testing)
        recommended_for = product.recommended_for or []
        if len(recommended_for) >= 3:
            score = min(100, score + 20)
        elif len(recommended_for) > 0:
            score = min(100, score + 10)
        
        # Penalty: avoid_for many conditions (suggests limitations)
        avoid_for = product.avoid_for or []
        if len(avoid_for) > 5:
            score = max(0, score - 20)
        
        return score
    
    @staticmethod
    def score_product_quality(product: Any) -> float:
        """
        Score product quality based on ratings and reviews.
        
        Args:
            product: Product object with avg_rating and review_count
        
        Returns:
            Score 0-100
        """
        score = 0
        
        # Convert rating (0-500 scale, e.g., 450 = 4.5 stars)
        rating = (product.avg_rating or 0) / 5.0 if product.avg_rating else 0
        
        # Review count factor (diminishing returns after 100 reviews)
        review_count = min(product.review_count or 0, 100)
        review_factor = min(1.0, review_count / 50.0)  # Plateau at 50 reviews
        
        # Combined score
        if rating > 0:
            score = rating * 20 * (0.5 + 0.5 * review_factor)
        
        return min(100, score)
    
    @staticmethod
    def calculate_total_safety_score(product: Any) -> float:
        """Calculate combined safety and quality score 0-100"""
        derma_score = DermatologicalRanker.score_dermatological_safety(product)
        quality_score = DermatologicalRanker.score_product_quality(product)
        
        return (
            derma_score * DermatologicalRanker.DERMATOLOGICAL_WEIGHT +
            quality_score * (
                DermatologicalRanker.RATING_WEIGHT +
                DermatologicalRanker.REVIEW_COUNT_WEIGHT
            )
        )


class FeedbackScorer:
    """Score products based on feedback history"""
    
    @staticmethod
    def get_product_feedback_stats(
        db: Session,
        product_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Get feedback statistics for a product from user's feedback history.
        
        Args:
            db: Database session
            product_id: Product ID
            user_id: User ID
        
        Returns:
            Dictionary with feedback statistics:
            {
                'avg_rating': float,
                'helpful_count': int,
                'total_feedback': int,
                'user_rated_before': bool,
                'user_rating': Optional[int]
            }
        """
        try:
            from backend.app.recommender.models import RecommendationFeedback
            
            # Get feedback for this product
            feedback = db.query(RecommendationFeedback).filter(
                RecommendationFeedback.product_id == product_id
            ).all()
            
            if not feedback:
                return {
                    'avg_rating': 0,
                    'helpful_count': 0,
                    'total_feedback': 0,
                    'user_rated_before': False,
                    'user_rating': None
                }
            
            ratings = [f.rating for f in feedback if f.rating is not None]
            helpful_count = sum(1 for f in feedback if f.was_helpful)
            
            # Check if current user rated this product
            user_feedback = next(
                (f for f in feedback if hasattr(f, 'user_id') and f.user_id == user_id),
                None
            )
            
            return {
                'avg_rating': sum(ratings) / len(ratings) if ratings else 0,
                'helpful_count': helpful_count,
                'total_feedback': len(feedback),
                'user_rated_before': user_feedback is not None,
                'user_rating': user_feedback.rating if user_feedback else None
            }
        except Exception as e:
            logger.warning(f"Failed to get feedback stats for product {product_id}: {e}")
            return {
                'avg_rating': 0,
                'helpful_count': 0,
                'total_feedback': 0,
                'user_rated_before': False,
                'user_rating': None
            }
    
    @staticmethod
    def score_from_feedback(feedback_stats: Dict[str, Any]) -> float:
        """
        Calculate score 0-100 from feedback statistics.
        
        Args:
            feedback_stats: Output from get_product_feedback_stats
        
        Returns:
            Score 0-100
        """
        if feedback_stats['total_feedback'] == 0:
            return 50  # Neutral for unrated products
        
        # Rating component (0-5 scale -> 0-100)
        rating_score = feedback_stats['avg_rating'] * 20
        
        # Helpful component
        helpful_ratio = (
            feedback_stats['helpful_count'] / feedback_stats['total_feedback']
            if feedback_stats['total_feedback'] > 0
            else 0
        )
        helpful_score = helpful_ratio * 30
        
        return min(100, rating_score + helpful_score)


class RankerEngine:
    """
    Main ranking engine for products.
    
    Combines multiple ranking factors:
    1. Allergy/Safety Filtering (strict filter)
    2. Dermatological Safety (25% weight)
    3. Product Quality/Ratings (30% weight)
    4. Feedback History (20% weight)
    5. Condition Match (25% weight)
    """
    
    def __init__(self, db: Session = None):
        """
        Initialize ranker.
        
        Args:
            db: Database session for feedback queries
        """
        self.db = db
        self.allergy_filter = AllergySafetyFilter()
        self.derma_ranker = DermatologicalRanker()
        self.feedback_scorer = FeedbackScorer()
    
    def rank_products(
        self,
        products_list: List[Any],
        user_profile: UserProfile,
        k: int = 5,
        include_allergen_warnings: bool = True
    ) -> List[RankedProduct]:
        """
        Main ranking function - orders products by relevance and safety.
        
        Ranking Algorithm:
        1. Filter out products with user allergies (strict)
        2. Calculate composite score for each product:
           - Dermatological safety (25%)
           - Product quality/ratings (30%)
           - Feedback history (20%)
           - Condition match (25%)
        3. Sort by score and return top k
        
        Args:
            products_list: List of Product objects to rank
            user_profile: UserProfile with allergies, conditions, etc.
            k: Number of top products to return (default: 5)
            include_allergen_warnings: If True, include warnings for products
                                      with allergen concerns but still rank them
        
        Returns:
            List of RankedProduct objects (top k, sorted by score descending)
        """
        if not products_list:
            logger.info("No products to rank")
            return []
        
        logger.info(f"Ranking {len(products_list)} products for user {user_profile.user_id}")
        
        # Step 1: Filter by allergies
        user_allergies = user_profile.get_allergies_set()
        safe_products, products_with_issues = self.allergy_filter.filter_safe_products(
            products_list,
            user_allergies,
            strict_mode=False  # Keep products with issues but warn
        )
        
        if not safe_products:
            logger.warning(f"All {len(products_list)} products have allergen concerns")
            safe_products = products_list  # Fallback: rank all but with warnings
        
        logger.info(f"After allergy filter: {len(safe_products)} safe products")
        
        # Step 2: Calculate scores for each product
        scored_products = []
        for product in safe_products:
            score = self._calculate_product_score(
                product,
                user_profile,
                user_allergies
            )
            
            # Get allergen warnings if applicable
            warnings = products_with_issues.get(product.id, []) if include_allergen_warnings else []
            
            scored_products.append((product, score, warnings))
        
        # Step 3: Sort by score (descending)
        scored_products.sort(key=lambda x: x[1], reverse=True)
        
        # Step 4: Create RankedProduct objects with rank and reasons
        ranked_results = []
        for rank, (product, score, warnings) in enumerate(scored_products[:k], 1):
            reasons = self._get_ranking_reasons(product, user_profile, score)
            
            ranked = RankedProduct(
                product=product,
                score=score,
                rank=rank,
                reasons=reasons,
                safety_issues=warnings if warnings else None
            )
            ranked_results.append(ranked)
        
        logger.info(f"Ranked top {len(ranked_results)} products for user {user_profile.user_id}")
        
        return ranked_results
    
    def _calculate_product_score(
        self,
        product: Any,
        user_profile: UserProfile,
        user_allergies: set
    ) -> float:
        """
        Calculate composite ranking score for a product.
        
        Score Components (total 100):
        - Dermatological safety: 25 points
        - Product quality (ratings/reviews): 30 points
        - Feedback history: 20 points
        - Condition match: 25 points
        
        Args:
            product: Product object
            user_profile: User profile with conditions
            user_allergies: Set of user allergies
        
        Returns:
            Score 0-100
        """
        score = 0
        
        # Component 1: Dermatological Safety (25%)
        derma_score = self.derma_ranker.calculate_total_safety_score(product)
        score += derma_score * 0.25
        
        # Component 2: Product Quality (30%)
        quality_score = self.derma_ranker.score_product_quality(product)
        score += quality_score * 0.30
        
        # Component 3: Feedback History (20%)
        if self.db:
            feedback_stats = self.feedback_scorer.get_product_feedback_stats(
                self.db,
                product.id,
                user_profile.user_id
            )
            feedback_score = self.feedback_scorer.score_from_feedback(feedback_stats)
            score += feedback_score * 0.20
        else:
            score += 50 * 0.20  # Neutral score if no DB
        
        # Component 4: Condition Match (25%)
        condition_score = self._score_condition_match(product, user_profile)
        score += condition_score * 0.25
        
        # Penalize products with allergen concerns
        allergies_found, _ = self.allergy_filter.filter_safe_products(
            [product], user_allergies
        )
        if not allergies_found:
            score *= 0.9  # 10% penalty for allergen concerns
        
        return min(100, max(0, score))
    
    def _score_condition_match(
        self,
        product: Any,
        user_profile: UserProfile
    ) -> float:
        """
        Score how well product matches user's detected conditions.
        
        Args:
            product: Product object
            user_profile: User profile with conditions
        
        Returns:
            Score 0-100
        """
        if not user_profile.conditions:
            return 50  # Neutral if no conditions detected
        
        recommended_for = set((product.recommended_for or []))
        if not recommended_for:
            return 40  # Slight penalty if no recommendations
        
        user_conditions = set(c.lower() for c in user_profile.conditions)
        matching_conditions = user_conditions.intersection(recommended_for)
        
        if not matching_conditions:
            return 30  # Lower score if no condition match
        
        # Score based on overlap
        match_ratio = len(matching_conditions) / len(user_conditions)
        
        return min(100, 60 + (match_ratio * 40))
    
    def _get_ranking_reasons(
        self,
        product: Any,
        user_profile: UserProfile,
        score: float
    ) -> List[str]:
        """Generate human-readable reasons for ranking"""
        reasons = []
        
        # Dermatological safety
        if product.dermatologically_safe:
            reasons.append("Dermatologically tested and approved")
        
        # Recommended for conditions
        recommended_for = product.recommended_for or []
        if user_profile.conditions:
            matching = [c for c in user_profile.conditions if c in recommended_for]
            if matching:
                reasons.append(f"Recommended for: {', '.join(matching)}")
        
        # High rating
        if product.avg_rating and product.avg_rating >= 400:  # 4.0+ stars
            stars = product.avg_rating / 100
            reasons.append(f"Highly rated ({stars:.1f} ⭐)")
        
        # Popular with positive feedback
        if product.review_count and product.review_count >= 50:
            reasons.append(f"Popular choice ({product.review_count}+ reviews)")
        
        # Safety for skin type
        if user_profile.skin_type and product.tags:
            tags_lower = [t.lower() for t in product.tags]
            if user_profile.skin_type.lower() in tags_lower:
                reasons.append(f"Suitable for {user_profile.skin_type} skin")
        
        # Generic quality message
        if not reasons:
            reasons.append("Recommended by recommendation engine")
        
        return reasons


def rank_products(
    products_list: List[Any],
    user_profile: UserProfile,
    db: Session = None,
    k: int = 5
) -> List[RankedProduct]:
    """
    Convenience function to rank products.
    
    Typical Usage:
        from backend.app.recommender.ranker import rank_products, UserProfile
        from sqlalchemy.orm import Session
        
        profile = UserProfile(
            user_id=123,
            allergies=['benzoyl_peroxide', 'salicylic_acid'],
            skin_type='oily',
            conditions=['acne', 'blackheads']
        )
        
        ranked = rank_products(
            products_list=products,
            user_profile=profile,
            db=db_session,
            k=5
        )
        
        for ranked_product in ranked:
            print(f"{ranked_product.rank}. {ranked_product.product.name}")
            print(f"   Score: {ranked_product.score}")
            print(f"   Reasons: {ranked_product.reasons}")
    
    Args:
        products_list: List of Product objects to rank
        user_profile: UserProfile instance
        db: Database session for feedback queries (optional)
        k: Number of top products to return
    
    Returns:
        List of RankedProduct objects (top k)
    """
    engine = RankerEngine(db=db)
    return engine.rank_products(products_list, user_profile, k=k)


def rank_products_by_id(
    product_ids: List[int],
    user_profile: UserProfile,
    db: Session = None,
    k: int = 5
) -> List[RankedProduct]:
    """
    Rank products given product IDs (fetch from DB first).
    
    Args:
        product_ids: List of product IDs
        user_profile: UserProfile instance
        db: Database session (required for fetching products)
        k: Number of top products to return
    
    Returns:
        List of RankedProduct objects
    """
    if not db:
        raise ValueError("Database session required for rank_products_by_id")
    
    try:
        from backend.app.recommender.models import Product
        
        products = db.query(Product).filter(Product.id.in_(product_ids)).all()
        return rank_products(products, user_profile, db=db, k=k)
    except Exception as e:
        logger.error(f"Failed to rank products by ID: {e}")
        raise
