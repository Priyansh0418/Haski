"""
FastAPI Router for Recommendation Feedback System

Handles:
- POST /feedback - Submit user feedback on recommendations
- GET /feedback/{recommendation_id}/stats - Get aggregated feedback stats
- Validates recommendation exists
- Saves feedback to RecommendationFeedback table
- Links to RuleLog entries for recommendation
- Returns updated aggregate stats (avg rating, helpful count)
"""

import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.db.session import get_db
from backend.app.core.security import get_current_user
from backend.app.models.db_models import User
from backend.app.recommender.models import (
    RecommendationRecord,
    RecommendationFeedback,
    RuleLog
)
from backend.app.recommender.schemas import FeedbackRequest, FeedbackResponse

logger = logging.getLogger(__name__)
router = APIRouter()


# ===== HELPER FUNCTIONS =====

def _validate_recommendation_exists(db: Session, recommendation_id: str) -> RecommendationRecord:
    """
    Validate that a recommendation exists.
    
    Args:
        db: Database session
        recommendation_id: Recommendation ID to validate
    
    Returns:
        RecommendationRecord if exists
    
    Raises:
        HTTPException: 404 if recommendation not found
    """
    recommendation = db.query(RecommendationRecord).filter(
        RecommendationRecord.recommendation_id == recommendation_id
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation '{recommendation_id}' not found"
        )
    
    return recommendation


def _save_feedback(
    db: Session,
    recommendation: RecommendationRecord,
    user_id: int,
    request: FeedbackRequest
) -> RecommendationFeedback:
    """
    Save feedback to database.
    
    Args:
        db: Database session
        recommendation: RecommendationRecord object
        user_id: User ID from JWT
        request: FeedbackRequest with feedback data
    
    Returns:
        Created RecommendationFeedback object
    """
    feedback = RecommendationFeedback(
        user_id=user_id,
        analysis_id=recommendation.analysis_id,
        recommendation_id=recommendation.id,
        helpful_rating=request.helpful_rating,
        product_satisfaction=request.product_satisfaction,
        routine_completion_pct=request.routine_completion_pct,
        timeframe=request.timeframe,
        feedback_text=request.feedback_text,
        improvement_suggestions=request.improvement_suggestions,
        adverse_reactions=request.adverse_reactions,
        would_recommend=request.would_recommend,
        product_ratings=request.product_ratings,
        created_at=datetime.utcnow()
    )
    
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    
    logger.info(
        f"Feedback saved: user_id={user_id}, recommendation_id={recommendation.recommendation_id}, "
        f"helpful_rating={request.helpful_rating}"
    )
    
    return feedback


def _get_feedback_stats(db: Session, recommendation: RecommendationRecord) -> Dict[str, Any]:
    """
    Calculate aggregated feedback statistics for a recommendation.
    
    Args:
        db: Database session
        recommendation: RecommendationRecord object
    
    Returns:
        Dictionary with aggregated stats:
        {
            "recommendation_id": "rec_...",
            "total_feedbacks": 5,
            "avg_helpful_rating": 4.2,
            "avg_product_satisfaction": 4.0,
            "avg_routine_completion_pct": 82,
            "would_recommend_count": 4,
            "would_not_recommend_count": 1,
            "adverse_reactions": 0,
            "helpful_feedbacks": 5,
            "not_helpful_feedbacks": 0,
            "ratings_distribution": {1: 0, 2: 0, 3: 1, 4: 2, 5: 2}
        }
    """
    feedbacks = db.query(RecommendationFeedback).filter(
        RecommendationFeedback.recommendation_id == recommendation.id
    ).all()
    
    total = len(feedbacks)
    
    if total == 0:
        return {
            "recommendation_id": recommendation.recommendation_id,
            "total_feedbacks": 0,
            "avg_helpful_rating": None,
            "avg_product_satisfaction": None,
            "avg_routine_completion_pct": None,
            "would_recommend_count": 0,
            "would_not_recommend_count": 0,
            "adverse_reactions": 0,
            "helpful_feedbacks": 0,
            "not_helpful_feedbacks": 0,
            "ratings_distribution": {}
        }
    
    # Calculate averages
    helpful_ratings = [f.helpful_rating for f in feedbacks if f.helpful_rating]
    satisfaction_ratings = [f.product_satisfaction for f in feedbacks if f.product_satisfaction]
    completion_pcts = [f.routine_completion_pct for f in feedbacks if f.routine_completion_pct is not None]
    
    avg_helpful = sum(helpful_ratings) / len(helpful_ratings) if helpful_ratings else None
    avg_satisfaction = sum(satisfaction_ratings) / len(satisfaction_ratings) if satisfaction_ratings else None
    avg_completion = sum(completion_pcts) / len(completion_pcts) if completion_pcts else None
    
    # Count recommendations
    would_recommend = sum(1 for f in feedbacks if f.would_recommend is True)
    would_not_recommend = sum(1 for f in feedbacks if f.would_recommend is False)
    
    # Count adverse reactions
    adverse_count = sum(1 for f in feedbacks if f.adverse_reactions and f.adverse_reactions.strip())
    
    # Count helpful/not helpful
    helpful_count = sum(1 for f in feedbacks if f.helpful_rating and f.helpful_rating >= 4)
    not_helpful_count = sum(1 for f in feedbacks if f.helpful_rating and f.helpful_rating <= 2)
    
    # Rating distribution
    rating_dist = {}
    for rating in range(1, 6):
        rating_dist[rating] = sum(1 for f in feedbacks if f.helpful_rating == rating)
    
    return {
        "recommendation_id": recommendation.recommendation_id,
        "total_feedbacks": total,
        "avg_helpful_rating": round(avg_helpful, 2) if avg_helpful else None,
        "avg_product_satisfaction": round(avg_satisfaction, 2) if avg_satisfaction else None,
        "avg_routine_completion_pct": round(avg_completion, 1) if avg_completion else None,
        "would_recommend_count": would_recommend,
        "would_not_recommend_count": would_not_recommend,
        "adverse_reactions": adverse_count,
        "helpful_feedbacks": helpful_count,
        "not_helpful_feedbacks": not_helpful_count,
        "ratings_distribution": rating_dist
    }


def _get_rule_logs_for_recommendation(db: Session, recommendation: RecommendationRecord) -> List[Dict[str, Any]]:
    """
    Get all rule logs associated with a recommendation's analysis.
    
    Args:
        db: Database session
        recommendation: RecommendationRecord object
    
    Returns:
        List of rule log dictionaries with details
    """
    rule_logs = db.query(RuleLog).filter(
        RuleLog.analysis_id == recommendation.analysis_id,
        RuleLog.applied == True  # Only applied rules
    ).all()
    
    rules_applied = []
    for log in rule_logs:
        rules_applied.append({
            "rule_id": log.rule_id,
            "rule_name": log.rule_name,
            "rule_category": log.rule_category,
            "details": log.details
        })
    
    return rules_applied


def _calculate_feedback_insights(
    feedback: RecommendationFeedback,
    stats: Dict[str, Any],
    recommendation: RecommendationRecord
) -> Dict[str, Any]:
    """
    Calculate insights based on feedback data.
    
    Args:
        feedback: RecommendationFeedback object just created
        stats: Aggregated stats dictionary
        recommendation: RecommendationRecord object
    
    Returns:
        Dictionary with insights and actionable data
    """
    insights = {
        "user_satisfaction_level": None,
        "routine_adherence": None,
        "product_quality_assessment": None,
        "recommendations_for_improvement": [],
        "escalations": []
    }
    
    # Satisfaction level
    if feedback.helpful_rating:
        if feedback.helpful_rating >= 4:
            insights["user_satisfaction_level"] = "high"
        elif feedback.helpful_rating == 3:
            insights["user_satisfaction_level"] = "medium"
        else:
            insights["user_satisfaction_level"] = "low"
    
    # Routine adherence
    if feedback.routine_completion_pct is not None:
        if feedback.routine_completion_pct >= 80:
            insights["routine_adherence"] = "excellent"
        elif feedback.routine_completion_pct >= 60:
            insights["routine_adherence"] = "good"
        elif feedback.routine_completion_pct >= 40:
            insights["routine_adherence"] = "fair"
        else:
            insights["routine_adherence"] = "poor"
    
    # Product quality
    if feedback.product_satisfaction:
        if feedback.product_satisfaction >= 4:
            insights["product_quality_assessment"] = "high_quality"
        elif feedback.product_satisfaction == 3:
            insights["product_quality_assessment"] = "acceptable"
        else:
            insights["product_quality_assessment"] = "needs_improvement"
    
    # Recommendations for improvement
    if feedback.routine_completion_pct and feedback.routine_completion_pct < 60:
        insights["recommendations_for_improvement"].append(
            "Routine may be too complex - consider simplifying steps"
        )
    
    if feedback.helpful_rating and feedback.helpful_rating <= 2:
        insights["recommendations_for_improvement"].append(
            "Recommendation quality appears low - review rule set and conditions"
        )
    
    if feedback.adverse_reactions:
        insights["escalations"].append({
            "type": "adverse_reaction",
            "severity": "high",
            "message": f"User reported adverse reactions: {feedback.adverse_reactions}"
        })
        insights["recommendations_for_improvement"].append(
            "Review product ingredients for potential allergens"
        )
    
    if feedback.would_recommend is False:
        insights["recommendations_for_improvement"].append(
            "User would not recommend - investigate dissatisfaction factors"
        )
    
    return insights


# ===== ENDPOINTS =====

@router.post("/feedback", status_code=status.HTTP_201_CREATED)
def submit_feedback(
    request: FeedbackRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Submit feedback on a recommendation.
    
    Accepts user ratings and comments on:
    - Overall helpfulness (1-5 scale)
    - Product satisfaction (1-5 scale)
    - Routine completion percentage (0-100)
    - Individual product ratings
    - Text feedback and improvement suggestions
    - Adverse reactions (if any)
    - Willingness to recommend
    
    Validates that recommendation exists, saves feedback, and returns:
    - Feedback submission confirmation
    - Updated aggregate statistics for the recommendation
    - Insights and actionable recommendations
    - Applied rules that generated the recommendation
    
    Args:
        request: FeedbackRequest with feedback data
        db: Database session
        user_id: Current user ID from JWT token
    
    Returns:
        {
            "feedback_id": 42,
            "recommendation_id": "rec_20251024_001",
            "user_id": 5,
            "status": "success",
            "message": "Feedback recorded successfully",
            "feedback_data": {
                "helpful_rating": 4,
                "product_satisfaction": 4,
                "routine_completion_pct": 75
            },
            "stats": {
                "recommendation_id": "rec_20251024_001",
                "total_feedbacks": 3,
                "avg_helpful_rating": 4.0,
                "avg_product_satisfaction": 3.7,
                "avg_routine_completion_pct": 76,
                "would_recommend_count": 2,
                "ratings_distribution": {1: 0, 2: 0, 3: 1, 4: 1, 5: 1}
            },
            "insights": {
                "user_satisfaction_level": "high",
                "routine_adherence": "good",
                "product_quality_assessment": "high_quality",
                "recommendations_for_improvement": [],
                "escalations": []
            },
            "rules_applied": [
                {
                    "rule_id": "r001",
                    "rule_name": "Oily + Acne",
                    "rule_category": "skincare"
                },
                {
                    "rule_id": "r007",
                    "rule_name": "Blackheads + Pores",
                    "rule_category": "skincare"
                }
            ],
            "created_at": "2025-10-24T14:30:00"
        }
    
    Raises:
        HTTPException: 404 if recommendation not found
        HTTPException: 400 if validation fails
    """
    try:
        # 1. Validate recommendation exists
        recommendation = _validate_recommendation_exists(db, request.recommendation_id)
        
        # 2. Validate user owns this recommendation or has permission
        if recommendation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User can only submit feedback for their own recommendations"
            )
        
        # 3. Save feedback to database
        feedback = _save_feedback(db, recommendation, user_id, request)
        
        # 4. Get aggregated statistics
        stats = _get_feedback_stats(db, recommendation)
        
        # 5. Calculate insights
        insights = _calculate_feedback_insights(feedback, stats, recommendation)
        
        # 6. Get rules applied for this recommendation
        rules_applied = _get_rule_logs_for_recommendation(db, recommendation)
        
        # 7. Format response
        response = {
            "feedback_id": feedback.id,
            "recommendation_id": recommendation.recommendation_id,
            "user_id": user_id,
            "status": "success",
            "message": "Feedback recorded successfully",
            "feedback_data": {
                "helpful_rating": feedback.helpful_rating,
                "product_satisfaction": feedback.product_satisfaction,
                "routine_completion_pct": feedback.routine_completion_pct,
                "would_recommend": feedback.would_recommend,
                "has_adverse_reactions": bool(feedback.adverse_reactions),
                "timeframe": feedback.timeframe
            },
            "stats": stats,
            "insights": insights,
            "rules_applied": rules_applied,
            "created_at": feedback.created_at.isoformat()
        }
        
        logger.info(
            f"Feedback submitted successfully: feedback_id={feedback.id}, "
            f"recommendation_id={recommendation.recommendation_id}, user_id={user_id}"
        )
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit feedback"
        )


@router.get("/feedback/{recommendation_id}/stats")
def get_feedback_stats(
    recommendation_id: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get aggregated feedback statistics for a recommendation.
    
    Returns comprehensive statistics including:
    - Total feedback count
    - Average ratings (helpful, satisfaction, completion)
    - Recommendation metrics (would recommend, adverse reactions)
    - Rating distribution (1-5 scale breakdown)
    - Rules applied for the recommendation
    
    Args:
        recommendation_id: ID of recommendation to get stats for
        db: Database session
        user_id: Current user ID from JWT token
    
    Returns:
        {
            "recommendation_id": "rec_20251024_001",
            "total_feedbacks": 5,
            "avg_helpful_rating": 4.2,
            "avg_product_satisfaction": 4.0,
            "avg_routine_completion_pct": 82,
            "would_recommend_count": 4,
            "would_not_recommend_count": 1,
            "adverse_reactions": 0,
            "helpful_feedbacks": 5,
            "not_helpful_feedbacks": 0,
            "ratings_distribution": {
                "1": 0,
                "2": 0,
                "3": 1,
                "4": 2,
                "5": 2
            },
            "rules_applied": [
                {
                    "rule_id": "r001",
                    "rule_name": "Oily + Acne",
                    "rule_category": "skincare",
                    "details": {...}
                }
            ],
            "recommendation_metadata": {
                "recommendation_id": "rec_20251024_001",
                "created_at": "2025-10-24T12:30:00",
                "conditions_analyzed": ["acne", "blackheads"],
                "rules_applied_ids": ["r001", "r007"]
            }
        }
    
    Raises:
        HTTPException: 404 if recommendation not found
    """
    try:
        # Validate recommendation exists
        recommendation = _validate_recommendation_exists(db, recommendation_id)
        
        # Verify user has permission (can view own recommendations)
        if recommendation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User can only view stats for their own recommendations"
            )
        
        # Get feedback stats
        stats = _get_feedback_stats(db, recommendation)
        
        # Get rules applied
        rules_applied = _get_rule_logs_for_recommendation(db, recommendation)
        
        # Add metadata
        response = {
            **stats,
            "rules_applied": rules_applied,
            "recommendation_metadata": {
                "recommendation_id": recommendation.recommendation_id,
                "created_at": recommendation.created_at.isoformat(),
                "conditions_analyzed": recommendation.conditions_analyzed,
                "rules_applied_ids": recommendation.rules_applied
            }
        }
        
        logger.info(
            f"Feedback stats retrieved: recommendation_id={recommendation_id}, "
            f"user_id={user_id}, total_feedbacks={stats['total_feedbacks']}"
        )
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving feedback stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve feedback statistics"
        )


@router.get("/feedbacks/user/{user_id}/summary")
def get_user_feedback_summary(
    user_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get summary of all feedback submitted by a user.
    
    Returns:
    - Total recommendations received
    - Average helpfulness across all recommendations
    - Product satisfaction trend
    - Routine completion trend
    - List of recommendations with feedback
    
    Args:
        user_id: User ID to get summary for
        db: Database session
        current_user_id: Current user ID from JWT
    
    Returns:
        {
            "user_id": 5,
            "total_recommendations": 10,
            "total_feedbacks_given": 7,
            "overall_avg_helpful_rating": 4.1,
            "overall_avg_product_satisfaction": 4.0,
            "overall_avg_routine_completion_pct": 78,
            "would_recommend_rate": 0.86,
            "adverse_reactions_count": 1,
            "recommendations": [
                {
                    "recommendation_id": "rec_20251024_001",
                    "created_at": "2025-10-24T12:30:00",
                    "feedback_recorded": true,
                    "helpful_rating": 4,
                    "product_satisfaction": 4,
                    "routine_completion_pct": 75
                }
            ]
        }
    
    Raises:
        HTTPException: 403 if user can't view another user's summary
    """
    # Only allow users to view their own summary
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User can only view their own feedback summary"
        )
    
    try:
        # Get all recommendations for user
        recommendations = db.query(RecommendationRecord).filter(
            RecommendationRecord.user_id == user_id
        ).all()
        
        total_recs = len(recommendations)
        
        # Get all feedbacks for user
        feedbacks = db.query(RecommendationFeedback).filter(
            RecommendationFeedback.user_id == user_id
        ).all()
        
        total_feedbacks = len(feedbacks)
        
        if total_feedbacks == 0:
            return {
                "user_id": user_id,
                "total_recommendations": total_recs,
                "total_feedbacks_given": 0,
                "overall_avg_helpful_rating": None,
                "overall_avg_product_satisfaction": None,
                "overall_avg_routine_completion_pct": None,
                "would_recommend_rate": 0,
                "adverse_reactions_count": 0,
                "recommendations": []
            }
        
        # Calculate averages
        helpful_ratings = [f.helpful_rating for f in feedbacks if f.helpful_rating]
        satisfaction_ratings = [f.product_satisfaction for f in feedbacks if f.product_satisfaction]
        completion_pcts = [f.routine_completion_pct for f in feedbacks if f.routine_completion_pct is not None]
        would_recommend = [f.would_recommend for f in feedbacks if f.would_recommend is not None]
        
        avg_helpful = sum(helpful_ratings) / len(helpful_ratings) if helpful_ratings else None
        avg_satisfaction = sum(satisfaction_ratings) / len(satisfaction_ratings) if satisfaction_ratings else None
        avg_completion = sum(completion_pcts) / len(completion_pcts) if completion_pcts else None
        recommend_rate = sum(1 for x in would_recommend if x) / len(would_recommend) if would_recommend else 0
        
        adverse_count = sum(1 for f in feedbacks if f.adverse_reactions and f.adverse_reactions.strip())
        
        # Build recommendation list
        recs_list = []
        for rec in recommendations:
            feedback = next((f for f in feedbacks if f.recommendation_id == rec.id), None)
            recs_list.append({
                "recommendation_id": rec.recommendation_id,
                "created_at": rec.created_at.isoformat(),
                "feedback_recorded": feedback is not None,
                "helpful_rating": feedback.helpful_rating if feedback else None,
                "product_satisfaction": feedback.product_satisfaction if feedback else None,
                "routine_completion_pct": feedback.routine_completion_pct if feedback else None
            })
        
        response = {
            "user_id": user_id,
            "total_recommendations": total_recs,
            "total_feedbacks_given": total_feedbacks,
            "overall_avg_helpful_rating": round(avg_helpful, 2) if avg_helpful else None,
            "overall_avg_product_satisfaction": round(avg_satisfaction, 2) if avg_satisfaction else None,
            "overall_avg_routine_completion_pct": round(avg_completion, 1) if avg_completion else None,
            "would_recommend_rate": round(recommend_rate, 2),
            "adverse_reactions_count": adverse_count,
            "recommendations": recs_list
        }
        
        logger.info(f"User feedback summary retrieved: user_id={user_id}, total_feedbacks={total_feedbacks}")
        
        return response
    
    except Exception as e:
        logger.error(f"Error retrieving user feedback summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve feedback summary"
        )
