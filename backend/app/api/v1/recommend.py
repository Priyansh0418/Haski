"""
FastAPI Router for Recommender System Endpoint

Handles:
- POST /recommend - Generate personalized recommendations
- Loads rules from YAML and applies to user analysis + profile
- Creates RecommendationRecord in database
- Returns recommendation with product details and escalation flags
"""

import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...core.security import get_current_user, decode_access_token
from ...models.db_models import Analysis, Profile, User
from ...recommender.engine import RuleEngine, AnalysisValidator
from ...recommender.models import Product, RuleLog, RecommendationRecord
from ...recommender.schemas import RecommendationRequest

security = HTTPBearer(auto_error=False)

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[int]:
    """Optional authentication - returns user ID if token provided, None otherwise."""
    if credentials is None:
        return None
    try:
        payload = decode_access_token(credentials.credentials)
        user_id: str = payload.get("sub")
        return int(user_id) if user_id else None
    except Exception:
        return None

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize engine once at module load
try:
    ENGINE = RuleEngine()
    logger.info("Rule engine initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize rule engine: {e}")
    ENGINE = None


class RecommendationResponse:
    """Response model for recommendation endpoint"""
    pass


@router.post("/recommend", status_code=status.HTTP_201_CREATED)
def generate_recommendation(
    request: RecommendationRequest,
    db: Session = Depends(get_db),
    user_id: Optional[int] = Depends(get_optional_user)
):
    """
    Generate personalized skincare/haircare recommendations.
    
    Accepts either:
    1. analysis_id: Load existing Analysis and Profile from DB
    2. Direct data: Use provided analysis and profile data
    
    Returns:
    - Complete recommendation (routines, products, diet, warnings)
    - Recommended products with details
    - Escalation flag if medical consultation needed
    - Applied rules for transparency
    
    Args:
        request: RecommendationRequest with analysis and/or profile data
        db: Database session
        user_id: Current user ID from JWT token
    
    Returns:
        {
            "recommendation_id": "rec_20251024_001",
            "routines": [...],
            "products": [...],
            "diet": [...],
            "warnings": [...],
            "escalation": {
                "level": "urgent|caution|warning|none",
                "message": "...",
                "high_priority": true
            },
            "applied_rules": ["r001", "r007"],
            "metadata": {...}
        }
    
    Raises:
        HTTPException 400: Invalid input data
        HTTPException 404: Analysis not found (if using analysis_id)
        HTTPException 500: Engine or database error
    """
    
    if ENGINE is None:
        logger.error("Rule engine not initialized")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Recommender engine not available"
        )
    
    try:
        # Load analysis and profile data
        analysis_data, profile_data, analysis_id = _load_user_data(
            request, db, user_id
        )
        
        # Validate loaded data
        is_valid_analysis, error_msg = AnalysisValidator.validate_analysis(analysis_data)
        if not is_valid_analysis:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid analysis data: {error_msg}"
            )
        
        is_valid_profile, error_msg = AnalysisValidator.validate_profile(profile_data)
        if not is_valid_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid profile data: {error_msg}"
            )
        
        # Apply recommendation rules
        recommendation, applied_rules = ENGINE.apply_rules(analysis_data, profile_data)
        
        # Get product details for recommended products
        recommended_products = _get_product_details(
            recommendation, db
        )
        
        # Create RecommendationRecord in database
        recommendation_record = _save_recommendation(
            user_id=user_id,
            analysis_id=analysis_id,
            recommendation=recommendation,
            applied_rules=applied_rules,
            db=db
        )
        
        # Log applied rules
        _log_applied_rules(analysis_id, applied_rules, db)
        
        # Format response
        response = _format_response(
            recommendation_record=recommendation_record,
            recommendation=recommendation,
            recommended_products=recommended_products,
            applied_rules=applied_rules
        )
        
        logger.info(
            f"Generated recommendation for user {user_id}, "
            f"analysis {analysis_id}, rules {applied_rules}"
        )
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating recommendation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate recommendation"
        )


def _load_user_data(
    request: RecommendationRequest,
    db: Session,
    user_id: int
) -> tuple:
    """
    Load analysis and profile data from request.
    
    Returns:
        (analysis_data_dict, profile_data_dict, analysis_id)
    """
    
    # Method 1: Load from existing analysis
    if request.method == "analysis_id" and request.analysis_id:
        analysis = db.query(Analysis).filter(
            Analysis.id == request.analysis_id,
            Analysis.user_id == user_id
        ).first()
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis {request.analysis_id} not found"
            )
        
        # Build analysis data from Analysis object
        analysis_data = {
            "skin_type": analysis.skin_type,
            "conditions_detected": analysis.conditions or [],
            "confidence_scores": analysis.confidence_scores or {}
        }
        
        if analysis.hair_type:
            analysis_data["hair_type"] = analysis.hair_type
    
    # Method 2: Use direct analysis data
    else:
        analysis_data = {
            "skin_type": request.skin_type,
            "conditions_detected": request.conditions_detected or [],
        }
        
        if request.hair_type:
            analysis_data["hair_type"] = request.hair_type
        if request.confidence_scores:
            analysis_data["confidence_scores"] = request.confidence_scores
        
        # If no analysis_id provided, we'll create a placeholder
        # (In real usage, this would be linked to a Photo/Analysis)
        analysis_id = None
    
    # Load profile data
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    
    profile_data = {
        "age": profile.age if profile else request.age,
        "pregnancy_status": _parse_pregnancy_status(
            profile.lifestyle if profile else request.pregnancy_status
        ),
        "breastfeeding_status": _parse_breastfeeding_status(
            profile.lifestyle if profile else request.pregnancy_status
        ),
        "allergies": _parse_allergies(
            profile.allergies if profile else None,
            request.allergies
        ),
        "skin_sensitivity": request.skin_sensitivity or "normal",
    }
    
    # Use analysis_id from request or from loaded analysis
    if hasattr(request, 'analysis_id') and request.analysis_id:
        analysis_id = request.analysis_id
    else:
        analysis_id = analysis.id if 'analysis' in locals() else None
    
    return analysis_data, profile_data, analysis_id


def _parse_pregnancy_status(lifestyle_text: Optional[str]) -> bool:
    """Extract pregnancy status from profile lifestyle field."""
    if not lifestyle_text:
        return False
    return "pregnant" in lifestyle_text.lower()


def _parse_breastfeeding_status(lifestyle_text: Optional[str]) -> bool:
    """Extract breastfeeding status from profile lifestyle field."""
    if not lifestyle_text:
        return False
    return "breastfeed" in lifestyle_text.lower()


def _parse_allergies(profile_allergies: Optional[str], request_allergies: Optional[List[str]]) -> List[str]:
    """Parse allergies from profile and request."""
    allergies = []
    
    if profile_allergies:
        # Profile allergies might be comma-separated or JSON
        if profile_allergies.startswith('['):
            try:
                allergies = json.loads(profile_allergies)
            except:
                allergies = [a.strip() for a in profile_allergies.split(',')]
        else:
            allergies = [a.strip() for a in profile_allergies.split(',')]
    
    if request_allergies:
        allergies.extend(request_allergies)
    
    return list(set(allergies))  # Deduplicate


def _get_product_details(
    recommendation: Dict[str, Any],
    db: Session
) -> List[Dict[str, Any]]:
    """
    Query database for product details based on recommendation.
    
    Gets products matching:
    1. External IDs from recommendation['products']
    2. Tags from recommendation['product_tags']
    
    Returns products sorted by rating.
    """
    
    recommended_products = []
    queried_ids = set()
    
    # Get products by external_id
    for product_ref in recommendation.get('products', []):
        external_id = product_ref.get('external_id')
        if external_id and external_id not in queried_ids:
            product = db.query(Product).filter(
                Product.external_id == external_id
            ).first()
            
            if product:
                recommended_products.append({
                    "id": product.id,
                    "name": product.name,
                    "brand": product.brand,
                    "external_id": external_id,
                    "category": product.category,
                    "price": product.price_usd / 100 if product.price_usd else None,
                    "url": product.url,
                    "tags": product.tags or [],
                    "rating": product.avg_rating / 100 if product.avg_rating else None,
                    "review_count": product.review_count,
                    "dermatologically_safe": product.dermatologically_safe,
                    "reason": product_ref.get('reason', 'Recommended'),
                    "source_rules": product_ref.get('source_rules', [])
                })
                queried_ids.add(external_id)
    
    # Get products by tags (limit to top matches)
    tags_to_search = [t['tag'] for t in recommendation.get('product_tags', [])]
    
    if tags_to_search:
        # Query products with matching tags
        products = db.query(Product).filter(
            Product.external_id.notin_(queried_ids)  # Avoid duplicates
        ).all()
        
        for product in products:
            product_tags = set(product.tags or [])
            matching_tags = product_tags & set(tags_to_search)
            
            if matching_tags:
                recommended_products.append({
                    "id": product.id,
                    "name": product.name,
                    "brand": product.brand,
                    "external_id": product.external_id,
                    "category": product.category,
                    "price": product.price_usd / 100 if product.price_usd else None,
                    "url": product.url,
                    "tags": product.tags or [],
                    "rating": product.avg_rating / 100 if product.avg_rating else None,
                    "review_count": product.review_count,
                    "dermatologically_safe": product.dermatologically_safe,
                    "reason": f"Matches tags: {', '.join(matching_tags)}",
                    "source_rules": next(
                        (t['source_rules'] for t in recommendation['product_tags'] if t['tag'] in matching_tags),
                        []
                    )
                })
                queried_ids.add(product.external_id)
    
    # Sort by rating (highest first)
    recommended_products.sort(
        key=lambda p: (p.get('rating') or 0, p.get('review_count') or 0),
        reverse=True
    )
    
    return recommended_products


def _save_recommendation(
    user_id: int,
    analysis_id: Optional[int],
    recommendation: Dict[str, Any],
    applied_rules: List[str],
    db: Session
) -> RecommendationRecord:
    """
    Save recommendation to database.
    
    Returns:
        RecommendationRecord instance
    """
    
    rec_record = RecommendationRecord(
        user_id=user_id,
        analysis_id=analysis_id,
        recommendation_id=f"rec_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        content=json.dumps(recommendation),
        source="rule_v1",
        conditions_analyzed=recommendation.get('metadata', {}).get('conditions_analyzed'),
        rules_applied=applied_rules,
        generation_time_ms=0,  # TODO: Track actual generation time
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(rec_record)
    db.commit()
    db.refresh(rec_record)
    
    return rec_record


def _log_applied_rules(
    analysis_id: Optional[int],
    applied_rules: List[str],
    db: Session
) -> None:
    """
    Log applied rules to RuleLog table for analytics/debugging.
    """
    
    if not analysis_id:
        return
    
    for rule_id in applied_rules:
        rule_log = RuleLog(
            analysis_id=analysis_id,
            rule_id=rule_id,
            applied=True,
            details={"matched": True, "timestamp": datetime.utcnow().isoformat()},
            created_at=datetime.utcnow()
        )
        db.add(rule_log)
    
    db.commit()


def _format_response(
    recommendation_record: RecommendationRecord,
    recommendation: Dict[str, Any],
    recommended_products: List[Dict[str, Any]],
    applied_rules: List[str]
) -> Dict[str, Any]:
    """
    Format final response for API.
    
    Includes:
    - Recommendation content
    - Product details
    - Escalation flags
    - Applied rules for transparency
    """
    
    escalation = recommendation.get('escalation')
    has_escalation = escalation is not None and escalation.get('level') != 'none'
    
    return {
        "recommendation_id": recommendation_record.recommendation_id,
        "created_at": recommendation_record.created_at.isoformat(),
        
        # Core recommendation
        "routines": recommendation.get('routines', []),
        "diet_recommendations": recommendation.get('diet', []),
        "warnings": recommendation.get('warnings', []),
        
        # Recommended products
        "recommended_products": recommended_products,
        "product_count": len(recommended_products),
        
        # Escalation (if applicable)
        "escalation": {
            "level": escalation.get('level', 'none') if escalation else 'none',
            "message": escalation.get('message') if escalation else None,
            "see_dermatologist": escalation and escalation.get('level') in ['urgent', 'emergency'],
            "high_priority": has_escalation
        } if has_escalation or escalation else None,
        
        # Transparency
        "applied_rules": applied_rules,
        "rules_count": len(applied_rules),
        
        # Metadata
        "metadata": {
            "total_rules_checked": recommendation.get('metadata', {}).get('total_rules_checked'),
            "rules_matched": recommendation.get('metadata', {}).get('rules_matched'),
            "generated_at": recommendation.get('metadata', {}).get('generated_at'),
            "product_tags_searched": [t['tag'] for t in recommendation.get('product_tags', [])],
            "tags_count": len(recommendation.get('product_tags', []))
        }
    }


# Optional: GET endpoint to retrieve saved recommendations
@router.get("/recommendations/{recommendation_id}")
def get_recommendation(
    recommendation_id: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    Retrieve a previously saved recommendation.
    
    Args:
        recommendation_id: ID of recommendation to retrieve
        db: Database session
        user_id: Current user ID from JWT token
    
    Returns:
        Full recommendation record with products
    
    Raises:
        HTTPException 404: Recommendation not found
    """
    
    try:
        rec = db.query(RecommendationRecord).filter(
            RecommendationRecord.recommendation_id == recommendation_id,
            RecommendationRecord.user_id == user_id
        ).first()
        
        if not rec:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recommendation {recommendation_id} not found"
            )
        
        content = json.loads(rec.content) if isinstance(rec.content, str) else rec.content
        
        return {
            "recommendation_id": rec.recommendation_id,
            "created_at": rec.created_at.isoformat(),
            "content": content,
            "source": rec.source,
            "rules_applied": rec.rules_applied or []
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving recommendation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recommendation"
        )


# Optional: GET list of user recommendations
@router.get("/recommendations")
def list_recommendations(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    List user's recent recommendations.
    
    Args:
        limit: Number of recommendations to return
        offset: Offset for pagination
        db: Database session
        user_id: Current user ID from JWT token
    
    Returns:
        List of recommendations with metadata
    """
    
    try:
        recommendations = db.query(RecommendationRecord).filter(
            RecommendationRecord.user_id == user_id
        ).order_by(
            RecommendationRecord.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        total = db.query(RecommendationRecord).filter(
            RecommendationRecord.user_id == user_id
        ).count()
        
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "recommendations": [
                {
                    "recommendation_id": r.recommendation_id,
                    "created_at": r.created_at.isoformat(),
                    "source": r.source,
                    "rules_applied": r.rules_applied or [],
                    "rules_count": len(r.rules_applied or [])
                }
                for r in recommendations
            ]
        }
    
    except Exception as e:
        logger.error(f"Error listing recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list recommendations"
        )
