"""
SQLAlchemy models for Recommender System

Models:
- Product: Skincare/haircare products with ingredients and tags
- RuleLog: Log of rules applied during recommendation
- RecommendationRecord: Store generated recommendations with metadata
"""

from sqlalchemy import Column, Integer, String, Boolean, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from backend.app.db.base import Base


class Product(Base):
    """
    Skincare/Haircare Product Database
    
    Stores product information for recommendations including:
    - Product details (name, brand, price)
    - Chemical composition (ingredients)
    - Safety information (dermatologically tested, suitable for conditions)
    - Tagging system (safe for acne, dry skin, sensitive, etc.)
    """
    
    __tablename__ = "products"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Product Information
    name = Column(String(255), nullable=False, index=True)
    brand = Column(String(100), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)  # cleanser, moisturizer, treatment, etc.
    price_usd = Column(Integer, nullable=True)  # Price in cents (e.g., 899 = $8.99)
    url = Column(String(500), nullable=True)  # Purchase link
    
    # Product Composition
    ingredients = Column(JSON, nullable=True)  # Array of ingredient strings
    # Example: ["water", "glycerin", "salicylic acid", "hyaluronic acid"]
    
    # Tagging System
    tags = Column(JSON, nullable=True)  # Array of tags for categorization
    # Example: ["acne-prone", "gentle", "exfoliating", "hydrating", "non-comedogenic"]
    
    # Safety Information
    dermatologically_safe = Column(Boolean, default=True)  # Has dermatological testing
    
    recommended_for = Column(JSON, nullable=True)  # Array of conditions this product is good for
    # Example: ["acne", "blackheads", "oily_skin"]
    
    avoid_for = Column(JSON, nullable=True)  # Array of conditions to avoid this product for
    # Example: ["very_sensitive", "pregnancy"]
    
    # Ratings
    avg_rating = Column(Integer, nullable=True, default=0)  # Out of 500 (e.g., 450 = 4.5 stars)
    review_count = Column(Integer, nullable=True, default=0)
    
    # Product Source
    source = Column(String(50), nullable=True)  # 'sephora', 'amazon', 'yestoday', etc.
    external_id = Column(String(100), nullable=True)  # ID from external source
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    rule_logs = relationship("RuleLog")
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', brand='{self.brand}', price=${self.price_usd/100 if self.price_usd else 'N/A'})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "name": self.name,
            "brand": self.brand,
            "category": self.category,
            "price_usd": self.price_usd / 100 if self.price_usd else None,
            "url": self.url,
            "ingredients": self.ingredients or [],
            "tags": self.tags or [],
            "dermatologically_safe": self.dermatologically_safe,
            "recommended_for": self.recommended_for or [],
            "avoid_for": self.avoid_for or [],
            "rating": self.avg_rating / 100 if self.avg_rating else None,
            "review_count": self.review_count,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class RuleLog(Base):
    """
    Log of Rules Applied During Recommendation Generation
    
    Tracks which rules were used, whether they applied, and any details
    about their application. Used for:
    - Debugging recommendation logic
    - Analytics on which conditions are most common
    - Audit trail for recommendation decisions
    """
    
    __tablename__ = "rule_logs"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True, index=True)
    
    # Rule Information
    rule_id = Column(String(100), nullable=False, index=True)  # e.g., "acne_routine_step_1"
    rule_name = Column(String(255), nullable=True)  # Human-readable rule name
    rule_category = Column(String(50), nullable=True)  # "skincare", "diet", "product", "escalation"
    
    # Rule Execution
    applied = Column(Boolean, default=False, nullable=False)  # Was rule applied?
    reason_not_applied = Column(String(255), nullable=True)  # If not applied, why?
    
    # Rule Details
    details = Column(JSON, nullable=True)  # Additional information about rule application
    # Example: {
    #   "condition": "acne",
    #   "severity": "moderate",
    #   "step": 1,
    #   "action": "Gentle cleanser",
    #   "frequency": "2x daily",
    #   "reason": "Removes excess oil without stripping"
    # }
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    analysis = relationship("Analysis")
    product = relationship("Product")
    
    def __repr__(self):
        return f"<RuleLog(id={self.id}, rule_id='{self.rule_id}', applied={self.applied}, analysis_id={self.analysis_id})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "rule_category": self.rule_category,
            "applied": self.applied,
            "reason_not_applied": self.reason_not_applied,
            "details": self.details,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class RecommendationRecord(Base):
    """
    Store Generated Recommendations with Metadata
    
    Complete record of a recommendation including:
    - The recommendation content (routine, diet, products)
    - Metadata about how it was generated
    - Links to analysis and user for tracking
    - Used for analytics, user history, and feedback collection
    """
    
    __tablename__ = "recommendation_records"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False, index=True)
    
    # Recommendation Tracking
    recommendation_id = Column(String(100), nullable=False, unique=True, index=True)
    # Format: "rec_20251024_001"
    
    # Recommendation Content (Complete JSON object)
    content = Column(JSON, nullable=False)
    # Stores complete recommendation:
    # {
    #   "skincare_routine": [{step, action, frequency, ...}],
    #   "diet_recommendations": {tips, foods_to_add, foods_to_avoid},
    #   "products": {cleanser, treatment, moisturizer, ...},
    #   "safety_flags": {...},
    #   "timeline": {...}
    # }
    
    # Metadata
    source = Column(String(50), nullable=False, default="rule_v1")
    # e.g., "rule_v1", "rule_v2", "ml_v1" (for tracking which engine generated it)
    
    conditions_analyzed = Column(JSON, nullable=True)  # Array of conditions from analysis
    # Example: ["acne", "blackheads", "dry_skin"]
    
    rules_applied = Column(JSON, nullable=True)  # Array of rule IDs that were applied
    # Example: ["acne_routine_step_1", "acne_diet_tips", "dry_moisturizer"]
    
    # Generation Details
    generation_time_ms = Column(Integer, nullable=True)  # How long did generation take?
    
    # User Preferences (used for filtering)
    user_budget = Column(String(50), nullable=True)  # "low", "medium", "high"
    user_allergies = Column(JSON, nullable=True)  # Array of ingredient allergies
    
    # Validity
    expires_at = Column(DateTime, nullable=True)  # When does this recommendation expire? (e.g., 30 days)
    is_expired = Column(Boolean, default=False, nullable=False)  # Has it expired?
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User")
    analysis = relationship("Analysis")
    feedbacks = relationship("RecommendationFeedback")
    
    def __repr__(self):
        return f"<RecommendationRecord(id={self.id}, recommendation_id='{self.recommendation_id}', user_id={self.user_id}, analysis_id={self.analysis_id})>"
    
    def to_dict(self, include_content=True):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "recommendation_id": self.recommendation_id,
            "user_id": self.user_id,
            "analysis_id": self.analysis_id,
            "content": self.content if include_content else None,
            "source": self.source,
            "conditions_analyzed": self.conditions_analyzed,
            "rules_applied": self.rules_applied,
            "generation_time_ms": self.generation_time_ms,
            "user_budget": self.user_budget,
            "user_allergies": self.user_allergies,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_expired": self.is_expired,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class RecommendationFeedback(Base):
    """
    User Feedback on Recommendations
    
    Collects user ratings and feedback for:
    - Measuring recommendation quality
    - Training data for ML ranking model
    - Analytics on what works best
    - User satisfaction tracking
    """
    
    __tablename__ = "recommendation_feedbacks"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False, index=True)
    recommendation_id = Column(Integer, ForeignKey("recommendation_records.id"), nullable=False, index=True)
    
    # User Ratings (1-5 scale, stored as integers for precision)
    helpful_rating = Column(Integer, nullable=True)  # 1-5: not helpful to very helpful
    product_satisfaction = Column(Integer, nullable=True)  # 1-5: not satisfied to very satisfied
    routine_completion_pct = Column(Integer, nullable=True)  # 0-100: % of routine completed
    
    # Timeframe (when did they provide feedback?)
    timeframe = Column(String(50), nullable=True)  # "1_week", "2_weeks", "4_weeks", "8_weeks"
    
    # Text Feedback
    feedback_text = Column(Text, nullable=True)  # User comments
    improvement_suggestions = Column(Text, nullable=True)  # Suggestions for improvement
    adverse_reactions = Column(Text, nullable=True)  # Any negative reactions?
    
    # Behavior Tracking
    would_recommend = Column(Boolean, nullable=True)  # Would user recommend to friends?
    
    # Individual Product Ratings
    product_ratings = Column(JSON, nullable=True)  # {cleanser: 5, treatment: 4, moisturizer: 5}
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User")
    analysis = relationship("Analysis")
    recommendation = relationship("RecommendationRecord")
    
    def __repr__(self):
        return f"<RecommendationFeedback(id={self.id}, user_id={self.user_id}, helpful={self.helpful_rating}, satisfaction={self.product_satisfaction})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "analysis_id": self.analysis_id,
            "recommendation_id": self.recommendation_id,
            "helpful_rating": self.helpful_rating,
            "product_satisfaction": self.product_satisfaction,
            "routine_completion_pct": self.routine_completion_pct,
            "timeframe": self.timeframe,
            "feedback_text": self.feedback_text,
            "improvement_suggestions": self.improvement_suggestions,
            "adverse_reactions": self.adverse_reactions,
            "would_recommend": self.would_recommend,
            "product_ratings": self.product_ratings,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
