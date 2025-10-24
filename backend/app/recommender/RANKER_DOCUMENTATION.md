# Product Ranking Module Documentation

## Overview

The **ranker.py** module provides a lightweight, rule-based product ranking system that orders skincare/haircare products based on dermatological safety, user allergies, product quality, feedback history, and condition match.

**Location:** `backend/app/recommender/ranker.py`

**Purpose:**

- Accept recommended products from the recommendation engine
- Rank them by relevance and safety for the specific user
- Return top-k products with explanations for each ranking

## Architecture

### Core Components

```
RankerEngine (main orchestrator)
├── AllergySafetyFilter (allergen detection & filtering)
├── DermatologicalRanker (safety & quality scoring)
└── FeedbackScorer (historical feedback scoring)
```

### Ranking Algorithm

The ranking combines four independent scoring components:

```
Final Score = (
    Dermatological Safety (25%) +
    Product Quality/Ratings (30%) +
    Feedback History (20%) +
    Condition Match (25%)
) × Safety Multiplier
```

**Safety Multiplier:** Products with allergen concerns receive a 0.9× penalty.

## Classes and Functions

### UserProfile

Represents user context for ranking decisions.

```python
@dataclass
class UserProfile:
    user_id: int
    allergies: Optional[List[str]] = None
    age: Optional[int] = None
    skin_type: Optional[str] = None
    hair_type: Optional[str] = None
    conditions: Optional[List[str]] = None

    def get_allergies_set(self) -> set:
        """Convert allergies to lowercase set for matching"""
```

**Usage:**

```python
profile = UserProfile(
    user_id=123,
    allergies=["benzoyl_peroxide", "salicylic_acid"],
    skin_type="oily",
    conditions=["acne", "blackheads"]
)
```

### RankedProduct

Result of ranking - a product with score and metadata.

```python
@dataclass
class RankedProduct:
    product: Any              # SQLAlchemy Product object
    score: float              # 0-100
    rank: int                 # 1, 2, 3, ...
    reasons: List[str]        # Why ranked here
    safety_issues: List[str]  # Allergen warnings

    def to_dict(self):        # Convert to API response
```

### AllergySafetyFilter

Static utility class for allergen detection.

```python
class AllergySafetyFilter:

    @staticmethod
    def filter_safe_products(
        products: List[Any],
        user_allergies: set,
        strict_mode: bool = False
    ) -> Tuple[List[Any], Dict[int, List[str]]]:
        """
        Filter products by allergen content.

        Returns:
            (safe_products, products_with_issues)

        In strict_mode=False (default):
            - Keeps products with allergen concerns
            - Records the concerns for warnings

        In strict_mode=True:
            - Excludes products with allergen concerns
        """

    @staticmethod
    def has_allergen_concern(
        product: Any,
        user_allergies: set
    ) -> bool:
        """Quick check if product has allergen concerns"""
```

**Detection Methods:**

1. **Ingredient matching** - Check if allergen appears in ingredients list
2. **Tag matching** - Check if allergen appears in product tags
3. **Avoid-for matching** - Check if allergen is in avoid_for recommendations

### DermatologicalRanker

Static utility class for safety and quality scoring.

```python
class DermatologicalRanker:

    DERMATOLOGICAL_WEIGHT = 0.25
    RATING_WEIGHT = 0.20
    REVIEW_COUNT_WEIGHT = 0.10

    @staticmethod
    def score_dermatological_safety(product: Any) -> float:
        """
        Score product safety (0-100) based on:
        - Dermatological testing status (+100)
        - Recommended_for conditions (+10-20)
        - Avoid_for conditions (-20)
        """

    @staticmethod
    def score_product_quality(product: Any) -> float:
        """
        Score product quality (0-100) based on:
        - Average rating (0-500 scale, e.g., 450 = 4.5 stars)
        - Review count (diminishing returns after 50 reviews)
        """

    @staticmethod
    def calculate_total_safety_score(product: Any) -> float:
        """Combined safety + quality score (0-100)"""
```

**Scoring Breakdown:**

- **Dermatological Safe + Well Recommended:** 100-120
- **Dermatological Safe + Few Recommendations:** 80-100
- **Not Tested + Some Recommendations:** 40-60
- **Not Tested + No Data:** 0-40

### FeedbackScorer

Utility class for feedback-based scoring.

```python
class FeedbackScorer:

    @staticmethod
    def get_product_feedback_stats(
        db: Session,
        product_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Query feedback history for a product.

        Returns:
            {
                'avg_rating': float (0-5),
                'helpful_count': int,
                'total_feedback': int,
                'user_rated_before': bool,
                'user_rating': Optional[int]
            }
        """

    @staticmethod
    def score_from_feedback(feedback_stats: Dict) -> float:
        """
        Convert feedback stats to score (0-100).

        Scoring:
            - Rating: (avg_rating / 5) × 20 (max 100)
            - Helpful: (helpful_count / total) × 30 (max 30)
            - Neutral: 50 if no feedback
        """
```

### RankerEngine

Main orchestrating class that combines all components.

```python
class RankerEngine:

    def __init__(self, db: Session = None):
        """Initialize with optional database session for feedback queries"""

    def rank_products(
        self,
        products_list: List[Any],
        user_profile: UserProfile,
        k: int = 5,
        include_allergen_warnings: bool = True
    ) -> List[RankedProduct]:
        """
        Rank products and return top k.

        Algorithm:
        1. Filter by allergies (strict)
        2. Score each product (composite score)
        3. Sort by score (descending)
        4. Return top k with explanations
        """
```

**Processing Steps:**

```
Input: products_list, user_profile, k
│
├─ Step 1: Allergy Filtering
│  └─ Identify products with allergen concerns
│     └─ Option 1: Exclude (strict_mode=True)
│     └─ Option 2: Keep with warnings (strict_mode=False)
│
├─ Step 2: Score Each Product
│  ├─ Component 1: Dermatological Safety (25%)
│  │  └─ Safety score × 0.25
│  │
│  ├─ Component 2: Product Quality (30%)
│  │  └─ Quality score × 0.30
│  │
│  ├─ Component 3: Feedback History (20%)
│  │  └─ Feedback score × 0.20
│  │
│  └─ Component 4: Condition Match (25%)
│     └─ Condition score × 0.25
│
├─ Step 3: Apply Safety Multiplier
│  └─ If allergen concerns: score × 0.9
│
├─ Step 4: Sort by Score
│  └─ Descending order
│
└─ Output: RankedProduct[] (top k with explanations)
```

### Main Function: rank_products

Convenience function for typical usage.

```python
def rank_products(
    products_list: List[Any],
    user_profile: UserProfile,
    db: Session = None,
    k: int = 5
) -> List[RankedProduct]:
    """
    Main ranking function.

    Typical usage:
        ranked = rank_products(
            products_list=products,
            user_profile=profile,
            db=db_session,
            k=5
        )
    """
```

## Usage Examples

### Basic Ranking

```python
from backend.app.recommender.ranker import rank_products, UserProfile
from sqlalchemy.orm import Session

# Create user profile
profile = UserProfile(
    user_id=123,
    allergies=["benzoyl_peroxide"],
    skin_type="oily",
    conditions=["acne"]
)

# Rank products (from recommendation engine)
ranked_products = rank_products(
    products_list=recommended_products,
    user_profile=profile,
    db=db_session,
    k=5
)

# Display results
for ranked in ranked_products:
    print(f"{ranked.rank}. {ranked.product.name}")
    print(f"   Score: {ranked.score:.1f}/100")
    print(f"   Reasons: {', '.join(ranked.reasons)}")
    if ranked.safety_issues:
        print(f"   ⚠️  Safety concerns: {ranked.safety_issues}")
```

### Advanced: Filter Specific Allergies

```python
# User with multiple allergies
profile = UserProfile(
    user_id=456,
    allergies=["salicylic_acid", "benzoyl_peroxide", "fragrance"],
    skin_type="sensitive",
    conditions=["sensitive", "dry_skin"]
)

ranked = rank_products(
    products_list=products,
    user_profile=profile,
    db=db_session,
    k=10
)

# Filter to only safe products
safe_ranked = [r for r in ranked if not r.safety_issues]
```

### Integration with Recommendation Engine

```python
from backend.app.recommender.engine import RuleEngine
from backend.app.recommender.ranker import rank_products, UserProfile

# Get recommendations from rule engine
engine = RuleEngine()
recommendation, rules = engine.apply_rules(
    analysis=user_analysis,
    profile=user_profile_dict
)

# Get recommended products (product IDs from engine)
recommended_product_ids = recommendation.get('products', [])
products = db.query(Product).filter(
    Product.id.in_(recommended_product_ids)
).all()

# Rank for user
user_profile = UserProfile(
    user_id=user_id,
    allergies=user_profile_dict.get('allergies'),
    skin_type=user_profile_dict.get('skin_type'),
    conditions=user_analysis.get('conditions_detected')
)

ranked = rank_products(products, user_profile, db=db, k=5)
```

## Ranking Factors Explained

### 1. Dermatological Safety (25%)

**What it measures:** Whether the product is clinically tested and suitable.

**Scoring:**

- ✅ Dermatologically tested: +100 points
- ❌ Not tested: +40 points
- +10-20 points per recommended condition
- -20 points if avoid_for many conditions

**Examples:**

- CeraVe (dermatologist brand, safe for sensitive): 100+
- The Ordinary Retinol (not dermatologically tested, powerful): 60-80

### 2. Product Quality/Ratings (30%)

**What it measures:** Product popularity and user satisfaction.

**Scoring:**

- Average rating (0-500 scale, e.g., 450 = 4.5 stars): weighted by review count
- Review count: diminishing returns after 50 reviews
- Products with 4.5+ stars and 100+ reviews: 80-100
- Products with 3.0 stars and 20 reviews: 20-40
- Unreviewed products: 0-10

**Why it matters:** Popular, well-reviewed products are usually effective.

### 3. Feedback History (20%)

**What it measures:** How users in the community rated this product.

**Scoring:**

- **No feedback:** Neutral (50)
- **High feedback (4+ stars, 50%+ helpful):** 70-100
- **Low feedback (2- stars, 20% helpful):** 10-40
- **Mixed feedback:** 40-60

**Why it matters:** Community feedback reveals real-world effectiveness.

### 4. Condition Match (25%)

**What it measures:** How well the product targets the user's detected conditions.

**Scoring:**

- **Perfect match (all conditions covered):** 100
- **Partial match (some conditions):** 60-90
- **No specific recommendation:** 40
- **No match:** 30

**Why it matters:** Targeted products are more effective than generic ones.

## Safety Filtering Details

### Allergen Detection

The system detects allergies through three mechanisms:

**1. Ingredient Matching**

```python
User allergy: "benzoyl_peroxide"
Product ingredients: ["water", "benzoyl_peroxide", "glycerin"]
Result: ⚠️ Match found
```

**2. Tag Matching**

```python
User allergy: "acne-fighting"
Product tags: ["gentle", "acne-fighting", "moisturizing"]
Result: ⚠️ Match found
```

**3. Avoid-For Matching**

```python
User allergy: "sensitive"
Product avoid_for: ["very_sensitive", "pregnancy"]
Result: ⚠️ Partial match
```

### Strict vs. Non-Strict Mode

**Default (strict_mode=False):**

- Keeps products with allergen concerns
- Adds allergen warnings to RankedProduct.safety_issues
- Products ranked lower (0.9× score multiplier)
- Useful for: Giving user full visibility and choice

**Strict Mode (strict_mode=True):**

- Excludes products with allergen concerns entirely
- Returns only completely safe products
- Useful for: Users with severe allergies

## Performance Considerations

### Time Complexity

- **rank_products():** O(n log n) where n = number of products
  - Filtering: O(n × m) where m = number of allergens
  - Scoring: O(n) or O(n × k) if feedback queries enabled
  - Sorting: O(n log n)

### Optimization Strategies

1. **Caching Feedback Stats**

   ```python
   # Cache feedback for products queried recently
   feedback_cache = {}
   for product in products:
       if product.id not in feedback_cache:
           feedback_cache[product.id] = get_feedback_stats(...)
   ```

2. **Batch Database Queries**

   ```python
   # Query all feedback at once, not per-product
   feedback = db.query(RecommendationFeedback).filter(
       RecommendationFeedback.product_id.in_(product_ids)
   ).all()
   ```

3. **Pre-filtering by Allergies**
   ```python
   # Filter dangerous products first to reduce scoring work
   safe_products = filter_safe_products(products, allergies)
   ```

## Testing

Run the comprehensive test suite:

```bash
pytest backend/app/recommender/test_ranker.py -v
```

**Test Coverage:**

- ✅ UserProfile (allergies parsing, case sensitivity)
- ✅ AllergySafetyFilter (ingredient, tag, avoid_for detection)
- ✅ DermatologicalRanker (safety and quality scoring)
- ✅ FeedbackScorer (feedback statistics and scoring)
- ✅ RankerEngine (complete ranking pipeline)
- ✅ Edge cases (empty lists, missing fields, extreme allergies)
- ✅ Integration tests (end-to-end workflows)

**Example Test:**

```python
def test_rank_by_allergies():
    profile = UserProfile(
        user_id=1,
        allergies=["benzoyl_peroxide"]
    )
    ranked = rank_products(sample_products, profile, k=5)

    # Product with benzoyl_peroxide should have warning
    assert any(r.safety_issues for r in ranked if "benzoyl_peroxide" in r.product.ingredients)
```

## Future Enhancements

### TODO: ML-Based Ranking (Contextual Bandit)

Replace rule-based ranking with machine learning:

```python
# Future implementation using contextual bandit approach

class ContextualBanditRanker:
    """
    ML-based ranking using Thompson sampling or UCB.

    Features:
    - User context: age, skin_type, conditions, allergies
    - Product context: ingredients, tags, price, rating
    - Action: rank position (1-10)
    - Reward: user feedback (click, view, add-to-cart, purchase)

    Learning:
    - Train on user interactions
    - Posterior sampling for exploration/exploitation
    - A/B test vs. rule-based baseline

    Implementation steps:
    1. Track user interactions in database
    2. Create feature vectors (product + user)
    3. Train Thompson sampling model
    4. Evaluate on held-out test set
    5. Deploy with feature flagging
    6. Monitor performance metrics
    """
```

**ML Ranking Advantages:**

- Personalized ranking per user type
- Automatically learns patterns from user feedback
- A/B testing capability
- Continuous improvement

**Implementation Roadmap:**

1. **Phase 1:** Track user interactions (clicks, purchases)
2. **Phase 2:** Create feature engineering pipeline
3. **Phase 3:** Train contextual bandit model
4. **Phase 4:** A/B test vs. rule-based baseline
5. **Phase 5:** Deploy with feature flags

## API Response Format

When integrated with FastAPI endpoints, ranked products appear as:

```json
{
  "recommendations": [
    {
      "rank": 1,
      "product": {
        "id": 42,
        "name": "CeraVe Moisturizing Cream",
        "brand": "CeraVe",
        "price_usd": 24.99,
        "category": "moisturizer",
        "tags": ["gentle", "hydrating"],
        "dermatologically_safe": true
      },
      "ranking_score": 87.5,
      "ranking_reasons": [
        "Dermatologically tested and approved",
        "Recommended for: dry_skin, sensitive",
        "Highly rated (4.5 ⭐)",
        "Popular choice (500+ reviews)"
      ],
      "safety_issues": []
    },
    {
      "rank": 2,
      "product": { ... },
      "ranking_score": 82.3,
      "ranking_reasons": [ ... ],
      "safety_issues": ["Ingredient: salicylic_acid"]
    }
  ]
}
```

## Files

- **Source:** `backend/app/recommender/ranker.py` (600+ lines)
- **Tests:** `backend/app/recommender/test_ranker.py` (500+ lines, 40+ tests)
- **Documentation:** This file

## Related Modules

- **engine.py:** Generates initial product recommendations
- **models.py:** Product database schema
- **feedback.py:** User feedback system
- **API integration:** `backend/app/api/v1/recommend.py`
