"""
Audit Logging Module for Recommender System

Logs recommendation engine activity to:
1. Database (RuleLog table) for queryable audit trail
2. Rotating file logs for backup and compliance

Features:
- Automatic RuleLog database entries
- Rotating file handler (daily rotation)
- Structured logging with user, analysis, rules, and recommendations
- Easy integration with RuleEngine
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from backend.app.db.session import SessionLocal
from backend.app.models.db_models import Analysis
from backend.app.recommender.models import RuleLog


class RecommendationAuditLogger:
    """
    Logs recommendation engine operations to database and rotating files.
    
    Usage:
        logger = RecommendationAuditLogger()
        logger.log_recommendation(
            user_id=5,
            analysis_id=10,
            applied_rules=["r001_acne_routine", "r002_diet"],
            recommendation={"products": [...], "routines": [...]},
            confidence_score=0.85
        )
    """
    
    def __init__(self, log_dir: Optional[str] = None):
        """
        Initialize audit logger with file and database handlers.
        
        Args:
            log_dir: Directory for log files. Defaults to backend/logs/
        """
        self.logger = logging.getLogger("recommender_audit")
        self.logger.setLevel(logging.INFO)
        
        # Avoid duplicate handlers
        if self.logger.handlers:
            return
        
        # Set up log directory
        if log_dir is None:
            log_dir = Path(__file__).parent.parent.parent / "logs"
        else:
            log_dir = Path(log_dir)
        
        log_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir = log_dir
        
        # Create rotating file handler (daily rotation, keep 30 days)
        log_file = log_dir / "recommendations_audit.log"
        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=str(log_file),
            when="midnight",
            interval=1,
            backupCount=30,
            encoding="utf-8"
        )
        
        # Format: ISO timestamp | user_id | analysis_id | applied_rules | summary
        formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        
        # Also add console handler for development
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def log_recommendation(
        self,
        user_id: int,
        analysis_id: int,
        applied_rules: List[str],
        recommendation: Dict[str, Any],
        confidence_score: float = 0.0,
        product_ids: Optional[List[int]] = None
    ) -> None:
        """
        Log recommendation to database (RuleLog) and rotating file.
        
        Args:
            user_id: User ID
            analysis_id: Analysis ID
            applied_rules: List of rule IDs applied (e.g., ["r001_acne_routine"])
            recommendation: Complete recommendation dict with routines, products, diet
            confidence_score: Overall confidence of recommendation (0-1)
            product_ids: List of product IDs recommended (optional)
        
        Returns:
            None
        """
        try:
            # 1. Generate summary for file log
            summary = self._generate_summary(recommendation)
            
            # 2. Log to rotating file
            file_log_msg = (
                f"user_id={user_id} | analysis_id={analysis_id} | "
                f"rules={len(applied_rules)} | score={confidence_score:.2f} | "
                f"{summary}"
            )
            self.logger.info(file_log_msg)
            
            # 3. Log each rule to database
            db = SessionLocal()
            try:
                for rule_id in applied_rules:
                    rule_log = RuleLog(
                        analysis_id=analysis_id,
                        product_id=product_ids[0] if product_ids else None,
                        rule_id=rule_id,
                        rule_name=self._get_rule_name(rule_id),
                        rule_category=self._get_rule_category(rule_id),
                        applied=True,
                        details={
                            "user_id": user_id,
                            "confidence_score": confidence_score,
                            "recommendation_summary": summary,
                            "total_rules_applied": len(applied_rules),
                            "generated_at": datetime.utcnow().isoformat()
                        }
                    )
                    db.add(rule_log)
                
                db.commit()
            except Exception as db_error:
                db.rollback()
                self.logger.error(f"Database logging failed: {db_error}")
            finally:
                db.close()
        
        except Exception as e:
            self.logger.error(f"Recommendation logging failed: {e}")
    
    def log_rule_not_applied(
        self,
        user_id: int,
        analysis_id: int,
        rule_id: str,
        reason: str
    ) -> None:
        """
        Log when a rule was evaluated but not applied.
        
        Args:
            user_id: User ID
            analysis_id: Analysis ID
            rule_id: Rule ID that didn't apply
            reason: Why the rule wasn't applied
        """
        try:
            # File log
            self.logger.info(
                f"user_id={user_id} | analysis_id={analysis_id} | "
                f"rule_not_applied={rule_id} | reason={reason}"
            )
            
            # Database log
            db = SessionLocal()
            try:
                rule_log = RuleLog(
                    analysis_id=analysis_id,
                    rule_id=rule_id,
                    rule_name=self._get_rule_name(rule_id),
                    rule_category=self._get_rule_category(rule_id),
                    applied=False,
                    reason_not_applied=reason,
                    details={
                        "user_id": user_id,
                        "evaluated_at": datetime.utcnow().isoformat()
                    }
                )
                db.add(rule_log)
                db.commit()
            except Exception as db_error:
                db.rollback()
                self.logger.error(f"Database logging failed: {db_error}")
            finally:
                db.close()
        
        except Exception as e:
            self.logger.error(f"Rule not applied logging failed: {e}")
    
    def log_analysis_error(
        self,
        user_id: int,
        analysis_id: int,
        error_message: str
    ) -> None:
        """
        Log when recommendation generation failed.
        
        Args:
            user_id: User ID
            analysis_id: Analysis ID
            error_message: Error description
        """
        try:
            self.logger.error(
                f"user_id={user_id} | analysis_id={analysis_id} | "
                f"recommendation_error={error_message}"
            )
        except Exception as e:
            self.logger.error(f"Error logging failed: {e}")
    
    @staticmethod
    def _generate_summary(recommendation: Dict[str, Any]) -> str:
        """
        Generate brief summary of recommendation for logs.
        
        Example: "routines=3, products=5, diet=2"
        """
        parts = []
        
        if "routines" in recommendation:
            parts.append(f"routines={len(recommendation['routines'])}")
        
        if "products" in recommendation:
            parts.append(f"products={len(recommendation['products'])}")
        
        if "diet" in recommendation:
            parts.append(f"diet={len(recommendation['diet'])}")
        
        if "escalation" in recommendation and recommendation["escalation"]:
            parts.append(f"escalation={recommendation['escalation'].get('level', 'unknown')}")
        
        return ", ".join(parts) if parts else "no_recommendations"
    
    @staticmethod
    def _get_rule_name(rule_id: str) -> str:
        """Convert rule ID to human-readable name."""
        mapping = {
            "r001_acne_routine": "Acne Skincare Routine",
            "r002_acne_diet": "Acne-Friendly Diet",
            "r003_hydration": "Hydration Tips",
            "r004_dry_skin_treatment": "Dry Skin Treatment",
            "r005_oily_skin_management": "Oily Skin Management",
            "r006_sensitive_care": "Sensitive Skin Care",
            "r007_anti_aging": "Anti-Aging Routine",
            "r008_sun_protection": "Sun Protection",
            "r009_hair_care": "Hair Care Routine",
        }
        return mapping.get(rule_id, rule_id)
    
    @staticmethod
    def _get_rule_category(rule_id: str) -> str:
        """Determine rule category from rule ID."""
        if "diet" in rule_id or "hydration" in rule_id:
            return "diet"
        elif "hair" in rule_id:
            return "hair"
        elif "escalation" in rule_id or "urgent" in rule_id:
            return "escalation"
        else:
            return "skincare"


# Global logger instance
_audit_logger: Optional[RecommendationAuditLogger] = None


def get_audit_logger() -> RecommendationAuditLogger:
    """Get or create global audit logger instance."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = RecommendationAuditLogger()
    return _audit_logger


if __name__ == "__main__":
    # Test the logger
    logger = RecommendationAuditLogger()
    
    # Test successful recommendation
    logger.log_recommendation(
        user_id=1,
        analysis_id=5,
        applied_rules=["r001_acne_routine", "r002_acne_diet", "r003_hydration"],
        recommendation={
            "routines": [
                {"step": 1, "action": "Gentle cleanser", "frequency": "2x daily"},
                {"step": 2, "action": "Salicylic acid treatment", "frequency": "1x daily"},
                {"step": 3, "action": "Moisturizer", "frequency": "2x daily"}
            ],
            "products": [
                {"id": 12, "name": "CeraVe Cleanser"},
                {"id": 15, "name": "Paula's Choice BHA"},
                {"id": 18, "name": "CeraVe Moisturizer"}
            ],
            "diet": [
                "Increase water intake",
                "Avoid dairy",
                "Add omega-3s"
            ],
            "escalation": None
        },
        confidence_score=0.87,
        product_ids=[12, 15, 18]
    )
    
    # Test rule not applied
    logger.log_rule_not_applied(
        user_id=1,
        analysis_id=5,
        rule_id="r007_anti_aging",
        reason="User age 25 - anti-aging not applicable"
    )
    
    # Test error
    logger.log_analysis_error(
        user_id=2,
        analysis_id=6,
        error_message="Invalid skin type in analysis data"
    )
    
    print("\n✅ Audit logging test complete. Check backend/logs/recommendations_audit.log")
