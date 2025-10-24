"""
Admin Recommender Engine Management Router

Provides endpoints to manage the recommendation engine, including:
- Reloading rules from YAML file
- Checking engine status
- Viewing loaded rule count

Protected with ADMIN_SECRET environment variable token.
"""

import os
import logging
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, Header
from typing import Optional

from ...recommender.engine import RuleEngine

logger = logging.getLogger(__name__)

router = APIRouter()


def verify_admin_token(authorization: Optional[str] = Header(None)) -> str:
    """
    Verify admin token from Authorization header.
    
    Expected format: "Bearer <token>"
    
    Args:
        authorization: Authorization header value
        
    Returns:
        Token if valid
        
    Raises:
        HTTPException: If token is missing or invalid
    """
    admin_secret = os.getenv("ADMIN_SECRET", "")
    
    if not admin_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ADMIN_SECRET not configured"
        )
    
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header"
        )
    
    # Parse "Bearer <token>" format
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Use: Bearer <token>"
        )
    
    token = parts[1]
    
    if token != admin_secret:
        logger.warning(f"Invalid admin token attempt from authorization header")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin token"
        )
    
    return token


# Global rule engine instance
_rule_engine_instance: Optional[RuleEngine] = None


def get_rule_engine() -> RuleEngine:
    """Get or initialize the global rule engine instance."""
    global _rule_engine_instance
    
    if _rule_engine_instance is None:
        try:
            _rule_engine_instance = RuleEngine()
            logger.info(f"Initialized RuleEngine with {len(_rule_engine_instance.rules)} rules")
        except Exception as e:
            logger.error(f"Failed to initialize RuleEngine: {e}")
            raise
    
    return _rule_engine_instance


@router.post("/reload-rules")
def reload_rules(token: str = Depends(verify_admin_token)) -> dict:
    """
    Force reload recommendation rules from YAML file.
    
    This endpoint re-reads the rules.yaml file and reinitializes the rule engine.
    Useful for hot-reloading rules during development or after rule updates.
    
    Security:
        Requires valid ADMIN_SECRET token in Authorization header.
        Format: "Bearer <your-admin-secret>"
    
    Returns:
        {
            "status": "success",
            "rules_loaded": <count>,
            "rules_path": "<path to rules file>",
            "timestamp": "<ISO timestamp>"
        }
    
    Raises:
        HTTPException 401: Missing or invalid Authorization header
        HTTPException 403: Invalid admin token
        HTTPException 500: Failed to load rules
    """
    global _rule_engine_instance
    
    try:
        logger.info("Admin request: Reloading recommendation rules")
        
        # Determine rules file path
        rules_path = Path(__file__).parent.parent.parent / "recommender" / "rules.yaml"
        
        if not rules_path.exists():
            logger.error(f"Rules file not found: {rules_path}")
            raise FileNotFoundError(f"Rules file not found at: {rules_path}")
        
        # Create new engine instance (forces reload)
        new_engine = RuleEngine(str(rules_path))
        _rule_engine_instance = new_engine
        
        rules_count = len(new_engine.rules)
        logger.info(f"Successfully reloaded {rules_count} rules from {rules_path}")
        
        return {
            "status": "success",
            "rules_loaded": rules_count,
            "rules_path": str(rules_path),
            "timestamp": __import__("datetime").datetime.utcnow().isoformat()
        }
    
    except FileNotFoundError as e:
        logger.error(f"Rules file error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Rules file error: {str(e)}"
        )
    
    except Exception as e:
        logger.error(f"Failed to reload rules: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reload rules: {str(e)}"
        )


@router.get("/status")
def engine_status(token: str = Depends(verify_admin_token)) -> dict:
    """
    Get current status of recommendation engine.
    
    Security:
        Requires valid ADMIN_SECRET token in Authorization header.
        Format: "Bearer <your-admin-secret>"
    
    Returns:
        {
            "status": "ready",
            "rules_loaded": <count>,
            "rules_path": "<path to rules file>",
            "engine_initialized": true
        }
    
    Raises:
        HTTPException 401: Missing or invalid Authorization header
        HTTPException 403: Invalid admin token
    """
    try:
        engine = get_rule_engine()
        rules_count = len(engine.rules)
        
        rules_path = Path(__file__).parent.parent.parent / "recommender" / "rules.yaml"
        
        return {
            "status": "ready",
            "rules_loaded": rules_count,
            "rules_path": str(rules_path),
            "engine_initialized": True
        }
    
    except Exception as e:
        logger.error(f"Error getting engine status: {e}")
        return {
            "status": "error",
            "rules_loaded": 0,
            "rules_path": str(Path(__file__).parent.parent.parent / "recommender" / "rules.yaml"),
            "engine_initialized": False,
            "error": str(e)
        }


__all__ = ["router", "verify_admin_token", "get_rule_engine"]
