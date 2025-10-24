"""
Escalation Handler Module

Loads and manages escalation conditions that require medical attention.
Integrates with RuleEngine to flag recommendations requiring professional care.
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Optional, List, Any
from functools import lru_cache

logger = logging.getLogger(__name__)


class EscalationHandler:
    """
    Manages escalation conditions and checks.
    
    Usage:
        handler = EscalationHandler()
        escalation = handler.check_recommendation(recommendation)
        
        if escalation:
            print(f"ESCALATION: {escalation['medical_advice']}")
    """
    
    def __init__(self, escalation_file: Optional[str] = None):
        """
        Initialize escalation handler.
        
        Args:
            escalation_file: Path to escalation.yml. Defaults to backend/app/recommender/escalation.yml
        """
        if escalation_file is None:
            escalation_file = Path(__file__).parent / "escalation.yml"
        
        self.escalation_file = escalation_file
        self._escalations = None
        self._conditions = None
    
    @property
    def escalations(self) -> Dict[str, Any]:
        """Load escalations lazily (cached)."""
        if self._escalations is None:
            self._escalations = self._load_escalations()
        return self._escalations
    
    @property
    def conditions(self) -> Dict[str, Any]:
        """Get all escalation conditions."""
        if self._conditions is None:
            self._conditions = self.escalations.get('escalations', {})
        return self._conditions
    
    def _load_escalations(self) -> Dict[str, Any]:
        """Load escalation.yml file."""
        try:
            with open(self.escalation_file, 'r') as f:
                data = yaml.safe_load(f)
                logger.info(f"Loaded escalations from {self.escalation_file}")
                return data
        except FileNotFoundError:
            logger.error(f"Escalation file not found: {self.escalation_file}")
            return {'escalations': {}}
        except yaml.YAMLError as e:
            logger.error(f"Error parsing escalation YAML: {e}")
            return {'escalations': {}}
    
    def check_recommendation(self, recommendation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Check if recommendation contains escalation conditions.
        
        Args:
            recommendation: Recommendation dict with conditions_detected field
        
        Returns:
            Escalation data if found, None otherwise
        """
        conditions = recommendation.get('conditions_detected', [])
        
        for condition in conditions:
            if condition in self.conditions:
                escalation_data = self.conditions[condition]
                
                logger.warning(
                    f"ESCALATION DETECTED: {condition} - {escalation_data.get('medical_advice')}"
                )
                
                return escalation_data
        
        return None
    
    def check_condition(self, condition: str) -> Optional[Dict[str, Any]]:
        """
        Check if specific condition is an escalation.
        
        Args:
            condition: Condition name (e.g., 'infection', 'sudden_hair_loss')
        
        Returns:
            Escalation data if found, None otherwise
        """
        if condition in self.conditions:
            return self.conditions[condition]
        return None
    
    def get_escalation_message(self, condition: str) -> Optional[str]:
        """Get medical advice message for condition."""
        escalation = self.check_condition(condition)
        return escalation.get('medical_advice') if escalation else None
    
    def is_emergency(self, condition: str) -> bool:
        """Check if condition is a medical emergency (immediate action needed)."""
        escalation = self.check_condition(condition)
        return escalation.get('urgency') == 'immediate' if escalation else False
    
    def get_next_steps(self, condition: str) -> Optional[List[str]]:
        """Get recommended next steps for condition."""
        escalation = self.check_condition(condition)
        return escalation.get('recommended_next_steps') if escalation else None
    
    def get_severity(self, condition: str) -> Optional[str]:
        """Get severity level for condition."""
        escalation = self.check_condition(condition)
        return escalation.get('severity') if escalation else None
    
    def get_condition_type(self, condition: str) -> Optional[str]:
        """Get condition type (skin, hair, systemic, etc.)."""
        escalation = self.check_condition(condition)
        return escalation.get('condition_type') if escalation else None
    
    def get_triggers(self, condition: str) -> Optional[List[str]]:
        """Get trigger symptoms for condition."""
        escalation = self.check_condition(condition)
        return escalation.get('triggers') if escalation else None
    
    def format_escalation_response(self, condition: str) -> Optional[Dict[str, Any]]:
        """
        Format escalation data for API response.
        
        Returns dict with keys: condition, severity, message, urgency, next_steps, why_escalated
        """
        escalation = self.check_condition(condition)
        
        if not escalation:
            return None
        
        return {
            'condition': condition,
            'severity': escalation.get('severity'),
            'message': escalation.get('medical_advice'),
            'urgency': escalation.get('urgency'),
            'action': escalation.get('action'),
            'next_steps': escalation.get('recommended_next_steps'),
            'why_escalated': escalation.get('why_escalated'),
            'condition_type': escalation.get('condition_type'),
        }
    
    def get_all_escalation_conditions(self) -> List[str]:
        """Get list of all escalation condition names."""
        return list(self.conditions.keys())
    
    def get_escalations_by_severity(self, severity: str) -> List[str]:
        """Get escalation conditions by severity level."""
        return [
            cond for cond, data in self.conditions.items()
            if data.get('severity') == severity
        ]
    
    def get_escalations_by_type(self, condition_type: str) -> List[str]:
        """Get escalation conditions by type (skin, hair, systemic)."""
        return [
            cond for cond, data in self.conditions.items()
            if data.get('condition_type') == condition_type
        ]
    
    def get_emergencies(self) -> List[str]:
        """Get all emergency escalation conditions (urgency='immediate')."""
        return [
            cond for cond, data in self.conditions.items()
            if data.get('urgency') == 'immediate'
        ]


# Global singleton instance
_escalation_handler: Optional[EscalationHandler] = None


def get_escalation_handler() -> EscalationHandler:
    """Get global escalation handler instance."""
    global _escalation_handler
    if _escalation_handler is None:
        _escalation_handler = EscalationHandler()
    return _escalation_handler


# ===== HELPER FUNCTIONS =====

def check_escalation(recommendation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Check recommendation for escalation conditions.
    
    Args:
        recommendation: Recommendation dict
    
    Returns:
        Formatted escalation response if found
    """
    handler = get_escalation_handler()
    escalation = handler.check_recommendation(recommendation)
    
    if escalation:
        # Extract condition name from the escalation dict
        # Find which condition this escalation belongs to
        for cond_name in handler.get_all_escalation_conditions():
            if handler.conditions[cond_name] == escalation:
                return handler.format_escalation_response(cond_name)
    
    return None


def is_emergency_condition(condition: str) -> bool:
    """Check if condition requires immediate emergency care."""
    handler = get_escalation_handler()
    return handler.is_emergency(condition)


def get_escalation_advice(condition: str) -> Optional[str]:
    """Get medical advice for escalation condition."""
    handler = get_escalation_handler()
    return handler.get_escalation_message(condition)


# ===== EXAMPLE USAGE =====

if __name__ == "__main__":
    # Initialize handler
    handler = EscalationHandler()
    
    # List all escalation conditions
    print("Escalation Conditions:")
    for cond in handler.get_all_escalation_conditions():
        severity = handler.get_severity(cond)
        print(f"  - {cond} ({severity})")
    
    print("\n" + "="*60 + "\n")
    
    # Check specific condition
    print("Checking 'infection' condition:")
    escalation = handler.format_escalation_response('infection')
    print(f"  Severity: {escalation['severity']}")
    print(f"  Message: {escalation['message']}")
    print(f"  Urgency: {escalation['urgency']}")
    print(f"  Is Emergency: {handler.is_emergency('infection')}")
    
    print("\n" + "="*60 + "\n")
    
    # Get all emergencies
    print("Emergency Conditions (urgency=immediate):")
    for cond in handler.get_emergencies():
        print(f"  - {cond}")
    
    print("\n" + "="*60 + "\n")
    
    # Check recommendation
    recommendation = {
        'conditions_detected': ['severe_rash'],
        'routines': [],
        'products': []
    }
    
    print("Checking recommendation for escalations:")
    escalation = check_escalation(recommendation)
    if escalation:
        print(f"  ✓ Escalation detected!")
        print(f"    Condition: {escalation['condition']}")
        print(f"    Message: {escalation['message']}")
    else:
        print(f"  ✓ No escalation detected")
