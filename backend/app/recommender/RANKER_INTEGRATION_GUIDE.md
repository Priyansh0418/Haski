# Ranker Integration Guide

## Integration Overview

The ranker module integrates into the recommendation pipeline between the recommendation engine and API response:

```
User Analysis
    ↓
RuleEngine (engine.py)
    ↓
Product IDs + Metadata
    ↓
Database Query → Products
    ↓
RankerEngine (ranker.py) ← NEW STEP
    ↓
Ranked Products (with scores & reasons)
    ↓
API Response (recommend.py)
    ↓
Client (Frontend)
```

---

## Step 1: Basic Integration with Recommend Endpoint

### Current Endpoint (Without Ranker)

```python
# In backend/app/api/v1/recommend.py

@router.post("/analyze-and-recommend")
async def analyze_and_recommend(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze user and generate recommendations.
    """
    engine = RuleEngine()
    recommendation, applied_rules = engine.apply_rules(
        analysis=request.analysis,
        profile=request.profile
    )

    # Get products
    product_ids = recommendation.get('products', [])
    products = db.query(Product).filter(
        Product.id.in_(product_ids)
    ).all()

    return {
        "recommendations": [p.to_dict() for p in products],
        "applied_rules": applied_rules
    }
```

### Enhanced Endpoint (With Ranker)

```python
# In backend/app/api/v1/recommend.py

from backend.app.recommender.ranker import rank_products, UserProfile

@router.post("/analyze-and-recommend")
async def analyze_and_recommend(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze user, generate recommendations, and rank them.
    """
    engine = RuleEngine()
    recommendation, applied_rules = engine.apply_rules(
        analysis=request.analysis,
        profile=request.profile
    )

    # Get products
    product_ids = recommendation.get('products', [])
    products = db.query(Product).filter(
        Product.id.in_(product_ids)
    ).all()

    # NEW: Rank products
    user_profile = UserProfile(
        user_id=current_user.id,
        allergies=request.profile.get('allergies'),
        age=request.profile.get('age'),
        skin_type=request.profile.get('skin_type'),
        hair_type=request.profile.get('hair_type'),
        conditions=request.analysis.get('conditions_detected')
    )

    ranked_products = rank_products(
        products_list=products,
        user_profile=user_profile,
        db=db,
        k=5  # Return top 5 ranked products
    )

    return {
        "recommendations": [r.to_dict() for r in ranked_products],
        "applied_rules": applied_rules,
        "ranking_method": "rule-based"
    }
```

---

## Step 2: Pydantic Schema Updates

### Add Ranking Response Schema

```python
# In backend/app/recommender/schemas.py

from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class RankingReasonResponse(BaseModel):
    """Why a product was ranked at this position"""
    reasons: List[str]
    safety_issues: Optional[List[str]] = None

class RankedProductResponse(BaseModel):
    """Product with ranking information"""
    id: int
    name: str
    brand: str
    category: str
    price_usd: Optional[float]
    tags: List[str]
    dermatologically_safe: bool
    recommended_for: List[str]
    rating: Optional[float]
    review_count: int

    # Ranking fields
    rank: int
    ranking_score: float
    ranking_reasons: List[str]
    safety_issues: Optional[List[str]] = None

class RecommendationResponseWithRanking(BaseModel):
    """Full recommendation response with ranked products"""
    recommendations: List[RankedProductResponse]
    applied_rules: List[str]
    ranking_method: str = "rule-based"
    total_products: int
    top_k: int

    model_config = {"from_attributes": True}
```

---

## Step 3: Integration Points

### Integration Point 1: In Recommend Endpoint

**File:** `backend/app/api/v1/recommend.py`

**Pseudo-code:**

```python
@router.post("/recommendations")
async def get_recommendations(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Get analysis from database
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == current_user.id
    ).first()

    # 2. Get user profile
    profile_data = {
        'allergies': current_user.profile.allergies,
        'skin_type': current_user.profile.skin_type,
        'conditions': analysis.conditions
    }

    # 3. Run recommendation engine
    engine = RuleEngine()
    recommendation, rules = engine.apply_rules(
        analysis=analysis.to_dict(),
        profile=profile_data
    )

    # 4. Get products
    products = db.query(Product).filter(
        Product.id.in_(recommendation['products'])
    ).all()

    # 5. RANK PRODUCTS ← NEW
    user_profile = UserProfile(
        user_id=current_user.id,
        allergies=profile_data['allergies'],
        conditions=profile_data['conditions'],
        skin_type=profile_data['skin_type']
    )

    ranked = rank_products(
        products_list=products,
        user_profile=user_profile,
        db=db,
        k=5
    )

    # 6. Return ranked products
    return {
        "recommendations": [r.to_dict() for r in ranked],
        "applied_rules": rules
    }
```

### Integration Point 2: In Feedback System

**File:** `backend/app/api/v1/feedback.py`

**Use Case:** Re-rank products based on feedback

```python
@router.post("/feedback/{recommendation_id}")
async def submit_feedback(
    recommendation_id: str,
    feedback: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    User rates a product from recommendation.

    After storing feedback, re-rank remaining products
    to boost alternatives if user disliked recommendation.
    """
    # Store feedback
    recommendation = db.query(RecommendationRecord).filter_by(
        recommendation_id=recommendation_id
    ).first()

    # ... store feedback logic ...

    # NEW: Re-rank if user rated low
    if feedback.rating and feedback.rating <= 2:
        # Get remaining products from same recommendation
        remaining_products = get_remaining_products(
            recommendation,
            excluded_product_id=feedback.product_id
        )

        # Re-rank with emphasis on alternatives
        user_profile = UserProfile(
            user_id=current_user.id,
            allergies=current_user.profile.allergies,
            conditions=recommendation.conditions_detected
        )

        reranked = rank_products(
            remaining_products,
            user_profile,
            db=db,
            k=3
        )

        return {
            "feedback_saved": True,
            "alternatives": [r.to_dict() for r in reranked]
        }
```

### Integration Point 3: In Product Browse Endpoint

**File:** `backend/app/api/v1/products.py`

**Use Case:** Rank filtered products for user

```python
@router.get("/products/browse")
async def browse_products(
    category: Optional[str] = None,
    min_rating: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Browse products with personalized ranking.
    """
    # Query products
    query = db.query(Product)
    if category:
        query = query.filter(Product.category == category)
    if min_rating:
        query = query.filter(Product.avg_rating >= min_rating * 100)

    products = query.all()

    # Rank for current user
    user_profile = UserProfile(
        user_id=current_user.id,
        allergies=current_user.profile.allergies,
        skin_type=current_user.profile.skin_type
    )

    ranked = rank_products(
        products_list=products,
        user_profile=user_profile,
        db=db,
        k=20
    )

    return {
        "products": [r.to_dict() for r in ranked],
        "total": len(ranked)
    }
```

---

## Step 4: Complete Request/Response Example

### Request Example

```bash
curl -X POST http://localhost:8000/api/v1/analyze-and-recommend \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "analysis": {
      "skin_type": "oily",
      "hair_type": "fine",
      "conditions_detected": ["acne", "blackheads"],
      "confidence_scores": {"acne": 0.92}
    },
    "profile": {
      "age": 25,
      "gender": "M",
      "allergies": "benzoyl_peroxide,salicylic_acid",
      "skin_type": "oily"
    }
  }'
```

### Response Example (With Ranking)

```json
{
  "recommendations": [
    {
      "rank": 1,
      "product": {
        "id": 1,
        "name": "CeraVe Foaming Facial Cleanser",
        "brand": "CeraVe",
        "category": "cleanser",
        "price_usd": 8.99,
        "tags": ["gentle", "fragrance-free", "hypoallergenic"],
        "dermatologically_safe": true,
        "recommended_for": ["oily_skin", "acne", "sensitive"],
        "rating": 4.5,
        "review_count": 1250
      },
      "ranking_score": 88.5,
      "ranking_reasons": [
        "Dermatologically tested and approved",
        "Recommended for: acne, oily_skin",
        "Highly rated (4.5 ⭐)",
        "Popular choice (1250+ reviews)"
      ],
      "safety_issues": null
    },
    {
      "rank": 2,
      "product": {
        "id": 5,
        "name": "La Roche-Posay Effaclar",
        "brand": "La Roche-Posay",
        "category": "treatment",
        "price_usd": 12.99,
        "tags": ["oil-control", "balancing"],
        "dermatologically_safe": true,
        "recommended_for": ["acne", "oily_skin"],
        "rating": 4.3,
        "review_count": 890
      },
      "ranking_score": 84.2,
      "ranking_reasons": [
        "Dermatologically tested and approved",
        "Recommended for: acne, oily_skin",
        "Highly rated (4.3 ⭐)"
      ],
      "safety_issues": null
    },
    {
      "rank": 3,
      "product": {
        "id": 12,
        "name": "Neutrogena Ultra Gentle Cleanser",
        "brand": "Neutrogena",
        "category": "cleanser",
        "price_usd": 5.99,
        "tags": ["gentle", "fragrance-free"],
        "dermatologically_safe": true,
        "recommended_for": ["sensitive", "all_skin_types"],
        "rating": 4.4,
        "review_count": 2100
      },
      "ranking_score": 81.7,
      "ranking_reasons": [
        "Dermatologically tested and approved",
        "Popular choice (2100+ reviews)",
        "Highly rated (4.4 ⭐)"
      ],
      "safety_issues": null
    },
    {
      "rank": 4,
      "product": {
        "id": 8,
        "name": "The Ordinary Niacinamide",
        "brand": "The Ordinary",
        "category": "serum",
        "price_usd": 5.9,
        "tags": ["powerful", "budget-friendly"],
        "dermatologically_safe": false,
        "recommended_for": ["oily_skin", "large_pores"],
        "rating": 4.1,
        "review_count": 450
      },
      "ranking_score": 76.3,
      "ranking_reasons": [
        "Recommended for: oily_skin",
        "Budget-friendly option ($5.90)"
      ],
      "safety_issues": null
    },
    {
      "rank": 5,
      "product": {
        "id": 15,
        "name": "Neutrogena Acne Cleanser",
        "brand": "Neutrogena",
        "category": "cleanser",
        "price_usd": 6.99,
        "tags": ["acne-fighting", "exfoliating"],
        "dermatologically_safe": true,
        "recommended_for": ["acne"],
        "rating": 3.8,
        "review_count": 320
      },
      "ranking_score": 68.5,
      "ranking_reasons": ["Recommended for: acne"],
      "safety_issues": [
        "Ingredient: salicylic_acid",
        "Ingredient: benzoyl_peroxide"
      ]
    }
  ],
  "applied_rules": ["rule_oily_skin_basic", "rule_acne_treatment"],
  "ranking_method": "rule-based",
  "total_products": 5,
  "top_k": 5
}
```

---

## Step 5: Error Handling

```python
from backend.app.recommender.ranker import rank_products, UserProfile
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

async def safe_rank_products(
    products_list,
    user_profile: UserProfile,
    db: Session = None,
    k: int = 5,
    fallback_to_unsorted: bool = True
):
    """
    Rank products with error handling.
    """
    try:
        ranked = rank_products(
            products_list=products_list,
            user_profile=user_profile,
            db=db,
            k=k
        )
        logger.info(f"Successfully ranked {len(ranked)} products")
        return ranked

    except Exception as e:
        logger.error(f"Ranking failed: {e}")

        if fallback_to_unsorted:
            # Fallback: return unsorted products
            from backend.app.recommender.ranker import RankedProduct
            fallback = [
                RankedProduct(
                    product=p,
                    score=50.0,
                    rank=i+1,
                    reasons=["Ranking unavailable - using default order"],
                    safety_issues=None
                )
                for i, p in enumerate(products_list[:k])
            ]
            return fallback
        else:
            raise
```

---

## Step 6: Testing Integration

```python
# In test_recommend.py

def test_recommend_with_ranking(client, db, current_user):
    """Test recommendation endpoint with ranking"""
    response = client.post(
        "/api/v1/analyze-and-recommend",
        json={
            "analysis": {
                "skin_type": "oily",
                "conditions_detected": ["acne"]
            },
            "profile": {
                "allergies": "benzoyl_peroxide"
            }
        },
        headers={"Authorization": f"Bearer {get_token(current_user)}"}
    )

    assert response.status_code == 200
    data = response.json()

    # Verify ranking
    assert "recommendations" in data
    recs = data["recommendations"]
    assert len(recs) > 0

    # Verify each recommendation has ranking fields
    for rec in recs:
        assert "rank" in rec
        assert "ranking_score" in rec
        assert "ranking_reasons" in rec
        assert rec["rank"] > 0
        assert 0 <= rec["ranking_score"] <= 100

    # Verify ranked in descending score order
    scores = [r["ranking_score"] for r in recs]
    assert scores == sorted(scores, reverse=True)
```

---

## Step 7: Performance Optimization

### Caching Strategy

```python
from functools import lru_cache
import hashlib
from datetime import datetime, timedelta

class RankerCache:
    """Cache ranking results for common queries"""

    def __init__(self, ttl_minutes=5):
        self.cache = {}
        self.ttl = timedelta(minutes=ttl_minutes)

    def _make_key(self, user_id, product_ids, allergies):
        """Create cache key from parameters"""
        key_str = f"{user_id}:{sorted(product_ids)}:{sorted(allergies or [])}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, user_id, product_ids, allergies):
        """Get cached ranking if available and fresh"""
        key = self._make_key(user_id, product_ids, allergies)
        if key in self.cache:
            result, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                return result
            else:
                del self.cache[key]
        return None

    def set(self, user_id, product_ids, allergies, result):
        """Cache ranking result"""
        key = self._make_key(user_id, product_ids, allergies)
        self.cache[key] = (result, datetime.now())

# Usage
ranker_cache = RankerCache(ttl_minutes=5)

ranked = ranker_cache.get(user_id, product_ids, allergies)
if ranked is None:
    ranked = rank_products(products, profile, db=db, k=5)
    ranker_cache.set(user_id, product_ids, allergies, ranked)
```

### Batch Ranking

```python
# Rank products in batches for multiple users
from concurrent.futures import ThreadPoolExecutor

def rank_products_for_users(users, products, db):
    """Rank same products for multiple users in parallel"""
    results = {}

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {}
        for user in users:
            profile = UserProfile(
                user_id=user.id,
                allergies=user.profile.allergies,
                conditions=user.analysis.conditions
            )
            future = executor.submit(
                rank_products,
                products,
                profile,
                db=db
            )
            futures[user.id] = future

        for user_id, future in futures.items():
            results[user_id] = future.result()

    return results
```

---

## Step 8: Monitoring & Metrics

```python
from dataclasses import dataclass
from typing import Dict
import time

@dataclass
class RankingMetrics:
    """Track ranking performance"""
    avg_score: float
    min_score: float
    max_score: float
    processing_time_ms: float
    products_ranked: int
    allergen_filtered_count: int

def rank_with_metrics(products, profile, db=None, k=5) -> tuple:
    """Rank products and collect metrics"""
    start = time.time()

    ranked = rank_products(
        products_list=products,
        user_profile=profile,
        db=db,
        k=k
    )

    elapsed_ms = (time.time() - start) * 1000

    scores = [r.score for r in ranked]
    allergen_filtered = sum(1 for r in ranked if r.safety_issues)

    metrics = RankingMetrics(
        avg_score=sum(scores) / len(scores) if scores else 0,
        min_score=min(scores) if scores else 0,
        max_score=max(scores) if scores else 0,
        processing_time_ms=elapsed_ms,
        products_ranked=len(ranked),
        allergen_filtered_count=allergen_filtered
    )

    return ranked, metrics

# Usage
ranked, metrics = rank_with_metrics(products, profile, db=db)
logger.info(f"Ranked {metrics.products_ranked} in {metrics.processing_time_ms:.1f}ms")
logger.info(f"Avg score: {metrics.avg_score:.1f}, Allergen issues: {metrics.allergen_filtered_count}")
```

---

## Summary

**Integration Checklist:**

- [ ] Import ranker module in recommend.py
- [ ] Create UserProfile from user data
- [ ] Call rank_products() after recommendation engine
- [ ] Update response schema to include ranking fields
- [ ] Add error handling for ranking failures
- [ ] Test with sample user data
- [ ] Benchmark performance (target: <100ms for 50 products)
- [ ] Deploy and monitor metrics
- [ ] Collect user feedback on rankings

**Files to modify:**

1. `backend/app/api/v1/recommend.py` - Add ranking call
2. `backend/app/recommender/schemas.py` - Add ranking response schemas
3. `tests/test_recommend.py` - Add ranking tests

**Expected outcome:**

- Recommendations now ranked by relevance for user
- Safety concerns flagged with explanations
- Top-5 products returned with confidence

See RANKER_DOCUMENTATION.md for detailed API reference.
