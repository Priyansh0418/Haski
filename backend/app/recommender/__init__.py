"""
Recommender System Package

Transforms skin/hair analysis + user profile into personalized recommendations.

Modules:
- models: SQLAlchemy database models
- schemas: Pydantic request/response schemas
- engine: Core recommendation logic
- safety: Safety checks and escalations
- products: Product database queries
- rules: YAML-based recommendation rules

Usage:
    from .models import Product, RuleLog, RecommendationRecord, RecommendationFeedback
    from .schemas import RecommendationRequest, RecommendationResponse
    from .engine import RecommendationEngine
    
    engine = RecommendationEngine()
    recommendation = engine.generate(analysis_id=5, user_id=3)
"""

from .models import (
    Product,
    RuleLog,
    RecommendationRecord,
    RecommendationFeedback
)

from .schemas import (
    RecommendationRequest,
    RecommendationResponse,
    FeedbackRequest,
    FeedbackResponse,
    ProductResponse,
    SkincareRoutine,
    DietRecommendation,
    SafetyFlags
)

__all__ = [
    # Models
    "Product",
    "RuleLog",
    "RecommendationRecord",
    "RecommendationFeedback",
    # Schemas
    "RecommendationRequest",
    "RecommendationResponse",
    "FeedbackRequest",
    "FeedbackResponse",
    "ProductResponse",
    "SkincareRoutine",
    "DietRecommendation",
    "SafetyFlags",
]

__version__ = "1.0.0"
__author__ = "SkinHairAI Team"
