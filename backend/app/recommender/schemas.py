"""
Pydantic schemas for Recommender System API

Request/Response schemas for:
- Recommendation generation
- Feedback submission
- History queries
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


# ===== REQUEST SCHEMAS =====

class RecommendationRequest(BaseModel):
    """Request to generate recommendations"""
    
    # Method selection
    method: str = Field(default="analysis_id", description="'analysis_id' or 'direct_analysis'")
    
    # Option 1: Using existing analysis
    analysis_id: Optional[int] = Field(None, description="ID of existing analysis")
    
    # Option 2: Direct analysis data
    skin_type: Optional[str] = Field(None, description="e.g., 'dry', 'oily', 'combination'")
    hair_type: Optional[str] = Field(None, description="e.g., 'straight', 'wavy', 'curly'")
    conditions_detected: Optional[List[str]] = Field(None, description="e.g., ['acne', 'blackheads']")
    confidence_scores: Optional[Dict[str, float]] = Field(None, description="Confidence for each condition")
    
    # User profile
    age: Optional[int] = Field(None, description="User age")
    gender: Optional[str] = Field(None, description="'M' or 'F'")
    budget: Optional[str] = Field(None, description="'low', 'medium', 'high'")
    allergies: Optional[List[str]] = Field(None, description="Ingredient allergies")
    skin_tone: Optional[str] = Field(None, description="'light', 'medium', 'dark'")
    skin_sensitivity: Optional[str] = Field(None, description="'normal', 'sensitive', 'very_sensitive'")
    pregnancy_status: Optional[str] = Field(None, description="'pregnant', 'breastfeeding', 'not_pregnant'")
    
    # Options
    include_skincare: bool = Field(default=True, description="Include skincare routine?")
    include_diet: bool = Field(default=True, description="Include diet recommendations?")
    include_products: bool = Field(default=True, description="Include product recommendations?")
    include_lifestyle: bool = Field(default=True, description="Include lifestyle tips?")
    
    class Config:
        example = {
            "method": "analysis_id",
            "analysis_id": 5,
            "include_diet": True,
            "include_products": True
        }


class DirectAnalysisData(BaseModel):
    """Direct analysis data for recommendation"""
    
    skin_type: str = Field(..., description="Skin type")
    hair_type: str = Field(..., description="Hair type")
    conditions_detected: List[str] = Field(..., description="Detected conditions")
    confidence_scores: Dict[str, float] = Field(..., description="Confidence scores")


class UserProfileData(BaseModel):
    """User profile for personalization"""
    
    age: Optional[int] = None
    gender: Optional[str] = None
    budget: Optional[str] = None
    allergies: Optional[List[str]] = None
    skin_tone: Optional[str] = None
    skin_sensitivity: Optional[str] = None
    pregnancy_status: Optional[str] = None


# ===== RECOMMENDATION RESPONSE SCHEMAS =====

class RoutineStep(BaseModel):
    """Single step in skincare routine"""
    
    step: int
    action: str
    frequency: str
    timing: Optional[str] = None
    duration_in_routine: int
    why: str
    expected_results: Optional[str] = None
    ingredients_to_look_for: Optional[List[str]] = None
    ingredients_to_avoid: Optional[List[str]] = None
    warning: Optional[str] = None


class SkincareRoutine(BaseModel):
    """Complete skincare routine"""
    
    duration_weeks: int
    difficulty: str
    expected_cost: str
    steps: List[RoutineStep]


class DietRecommendation(BaseModel):
    """Diet recommendations"""
    
    hydration: Optional[Dict[str, Any]] = None
    foods_to_add: Optional[List[Dict[str, Any]]] = None
    foods_to_limit: Optional[List[Dict[str, Any]]] = None


class ProductRecommendation(BaseModel):
    """Single product recommendation"""
    
    product_id: int
    name: str
    brand: str
    category: str
    price_usd: Optional[float] = None
    url: Optional[str] = None
    why_recommended: str
    ingredients: Optional[List[str]] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None


class SafetyFlags(BaseModel):
    """Safety information in recommendation"""
    
    severe_condition: bool
    requires_professional: bool
    escalation_needed: bool
    warnings: Optional[List[str]] = None
    escalation: Optional[Dict[str, Any]] = None
    no_prescription_meds: bool = True
    disclaimer: Optional[str] = None


class RecommendationResponse(BaseModel):
    """Complete recommendation response"""
    
    recommendation_id: str
    analysis_id: int
    user_id: Optional[int] = None
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    analysis_summary: Optional[Dict[str, Any]] = None
    skincare_routine: Optional[SkincareRoutine] = None
    diet_recommendations: Optional[DietRecommendation] = None
    product_recommendations: Optional[Dict[str, ProductRecommendation]] = None
    lifestyle_recommendations: Optional[List[Dict[str, Any]]] = None
    
    total_estimated_cost: Optional[Dict[str, Any]] = None
    safety_flags: SafetyFlags
    timeline: Optional[Dict[str, str]] = None
    what_to_expect: Optional[str] = None
    next_steps: Optional[List[str]] = None


# ===== FEEDBACK SCHEMAS =====

class FeedbackRequest(BaseModel):
    """Request to submit recommendation feedback"""
    
    recommendation_id: str = Field(..., description="ID of recommendation")
    helpful_rating: Optional[int] = Field(None, ge=1, le=5, description="1-5: not helpful to very helpful")
    product_satisfaction: Optional[int] = Field(None, ge=1, le=5, description="1-5 satisfaction")
    routine_completion_pct: Optional[int] = Field(None, ge=0, le=100, description="0-100% of routine completed")
    
    timeframe: Optional[str] = Field(None, description="'1_week', '2_weeks', '4_weeks', '8_weeks'")
    feedback_text: Optional[str] = Field(None, description="User comments")
    improvement_suggestions: Optional[str] = Field(None, description="Suggestions for improvement")
    adverse_reactions: Optional[str] = Field(None, description="Any negative reactions?")
    
    would_recommend: Optional[bool] = Field(None, description="Would recommend to friends?")
    product_ratings: Optional[Dict[str, int]] = Field(None, description="Individual product ratings")
    
    class Config:
        example = {
            "recommendation_id": "rec_20251024_001",
            "helpful_rating": 4,
            "product_satisfaction": 4,
            "routine_completion_pct": 75,
            "feedback_text": "Great recommendations!"
        }


class FeedbackResponse(BaseModel):
    """Response to feedback submission"""
    
    feedback_id: int
    recommendation_id: str
    user_id: int
    status: str
    message: str
    insights: Optional[Dict[str, Any]] = None
    created_at: datetime


# ===== HISTORY SCHEMAS =====

class RecommendationHistoryItem(BaseModel):
    """Single recommendation in history"""
    
    recommendation_id: str
    analysis_id: int
    created_at: datetime
    conditions: List[str]
    helpful_rating: Optional[int] = None
    product_satisfaction: Optional[int] = None
    routine_completion_pct: Optional[int] = None
    feedback_recorded: bool
    has_feedback: bool


class HistoryResponse(BaseModel):
    """History query response"""
    
    user_id: int
    total_recommendations: int
    recommendations: List[RecommendationHistoryItem]


# ===== PRODUCT SCHEMAS =====

class ProductCreate(BaseModel):
    """Schema to create a new product"""
    
    name: str
    brand: str
    category: str
    price_usd: Optional[int] = None
    url: Optional[str] = None
    
    ingredients: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    dermatologically_safe: bool = True
    recommended_for: Optional[List[str]] = None
    avoid_for: Optional[List[str]] = None
    
    avg_rating: Optional[int] = None
    review_count: Optional[int] = None
    source: Optional[str] = None
    external_id: Optional[str] = None


class ProductResponse(BaseModel):
    """Schema for product response"""
    
    id: int
    name: str
    brand: str
    category: str
    price_usd: Optional[float] = None
    url: Optional[str] = None
    
    ingredients: List[str]
    tags: List[str]
    dermatologically_safe: bool
    recommended_for: List[str]
    avoid_for: List[str]
    
    rating: Optional[float] = None
    review_count: int
    
    created_at: datetime
    
    class Config:
        from_attributes = True


# ===== ERROR SCHEMAS =====

class ErrorResponse(BaseModel):
    """Error response schema"""
    
    error: str
    detail: str
    status_code: int


# ===== ANALYSIS SCHEMAS (for reference) =====

class AnalysisSummary(BaseModel):
    """Summary of analysis results"""
    
    skin_type: str
    hair_type: str
    conditions_detected: List[str]
    confidence_scores: Dict[str, float]
    severity_overall: Optional[str] = None


# ===== VALIDATORS =====

class RecommendationRequestValidator:
    """Validators for recommendation requests"""
    
    @staticmethod
    def validate_budget(budget: Optional[str]) -> bool:
        """Validate budget value"""
        if budget is None:
            return True
        return budget.lower() in ['low', 'medium', 'high']
    
    @staticmethod
    def validate_gender(gender: Optional[str]) -> bool:
        """Validate gender value"""
        if gender is None:
            return True
        return gender.upper() in ['M', 'F', 'O', 'N']  # M, F, Other, Not specified
    
    @staticmethod
    def validate_skin_tone(skin_tone: Optional[str]) -> bool:
        """Validate skin tone value"""
        if skin_tone is None:
            return True
        return skin_tone.lower() in ['light', 'medium', 'dark', 'very_dark']
    
    @staticmethod
    def validate_skin_sensitivity(sensitivity: Optional[str]) -> bool:
        """Validate sensitivity value"""
        if sensitivity is None:
            return True
        return sensitivity.lower() in ['normal', 'sensitive', 'very_sensitive']
    
    @staticmethod
    def validate_pregnancy_status(status: Optional[str]) -> bool:
        """Validate pregnancy status"""
        if status is None:
            return True
        return status.lower() in ['pregnant', 'breastfeeding', 'not_pregnant', 'unknown']


# ===== TYPE DEFINITIONS =====

RuleEngineResponse = Dict[str, Any]  # Generic rule engine output
ProductDict = Dict[str, Any]  # Product as dictionary
RoutineDict = Dict[str, Any]  # Routine as dictionary
DietDict = Dict[str, Any]  # Diet recommendations as dictionary
