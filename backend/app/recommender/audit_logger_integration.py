"""
Integration Guide: Using Audit Logger with Recommendation Engine

This module shows how to integrate the audit logger into your API endpoints
and recommendation engine calls.
"""

from typing import Dict, Any, Optional
from backend.app.recommender.engine import RuleEngine
from backend.app.recommender.audit_logger import get_audit_logger
from backend.app.models.db_models import Analysis
from backend.app.db.session import SessionLocal


def get_recommendation_with_audit(
    user_id: int,
    analysis_id: int,
    analysis_data: Dict[str, Any],
    profile_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Generate recommendation with automatic audit logging.
    
    Usage in API endpoint:
        @router.post("/recommendations")
        def create_recommendation(req: RecommendationRequest, db: Session):
            result = get_recommendation_with_audit(
                user_id=req.user_id,
                analysis_id=req.analysis_id,
                analysis_data={...},
                profile_data={...}
            )
            return result
    
    Args:
        user_id: User ID from JWT or session
        analysis_id: Analysis record ID from database
        analysis_data: Skin/hair analysis results
        profile_data: User profile data
    
    Returns:
        Recommendation dict or None if generation failed
    """
    logger = get_audit_logger()
    
    try:
        # Generate recommendation
        engine = RuleEngine()
        recommendation, applied_rules = engine.apply_rules(
            analysis=analysis_data,
            profile=profile_data
        )
        
        # Extract product IDs if available
        product_ids = None
        if isinstance(recommendation.get("products"), list):
            product_ids = [
                p.get("id") for p in recommendation["products"]
                if isinstance(p, dict) and "id" in p
            ]
        
        # Log to database and file
        logger.log_recommendation(
            user_id=user_id,
            analysis_id=analysis_id,
            applied_rules=applied_rules,
            recommendation=recommendation,
            confidence_score=recommendation.get("confidence", 0.0),
            product_ids=product_ids
        )
        
        return recommendation
    
    except Exception as e:
        logger.log_analysis_error(
            user_id=user_id,
            analysis_id=analysis_id,
            error_message=str(e)
        )
        raise


def example_api_integration():
    """Example of how to integrate into FastAPI endpoint."""
    
    example_code = '''
    from fastapi import APIRouter, Depends, HTTPException
    from backend.app.db.session import SessionLocal, get_db
    from backend.app.recommender.audit_logger import get_audit_logger
    from backend.app.recommender.schemas import RecommendationRequest, RecommendationResponse
    
    router = APIRouter(prefix="/api/v1/recommendations", tags=["recommendations"])
    
    @router.post("/generate", response_model=RecommendationResponse)
    async def generate_recommendation(
        req: RecommendationRequest,
        db: Session = Depends(get_db),
        user_id: int = Depends(get_current_user)
    ):
        """Generate recommendation with audit logging."""
        logger = get_audit_logger()
        
        try:
            # Get analysis from database
            analysis = db.query(Analysis).filter(
                Analysis.id == req.analysis_id,
                Analysis.user_id == user_id
            ).first()
            
            if not analysis:
                raise HTTPException(status_code=404, detail="Analysis not found")
            
            # Generate recommendation with audit
            engine = RuleEngine()
            recommendation, applied_rules = engine.apply_rules(
                analysis={
                    "skin_type": analysis.skin_type,
                    "conditions_detected": analysis.conditions,
                    "age": user.age
                },
                profile={"allergies": user.profile.allergies}
            )
            
            # Log the recommendation
            logger.log_recommendation(
                user_id=user_id,
                analysis_id=req.analysis_id,
                applied_rules=applied_rules,
                recommendation=recommendation,
                confidence_score=recommendation.get("confidence", 0.0)
            )
            
            # Save to database
            rec_record = RecommendationRecord(
                user_id=user_id,
                analysis_id=req.analysis_id,
                recommendation_id=f"rec_{analysis.id}",
                content=recommendation,
                rules_applied=applied_rules
            )
            db.add(rec_record)
            db.commit()
            
            return recommendation
        
        except Exception as e:
            logger.log_analysis_error(
                user_id=user_id,
                analysis_id=req.analysis_id,
                error_message=str(e)
            )
            raise HTTPException(status_code=500, detail="Recommendation generation failed")
    '''
    
    print(example_code)


if __name__ == "__main__":
    print("✅ Integration guide created. See docstrings for usage examples.")
