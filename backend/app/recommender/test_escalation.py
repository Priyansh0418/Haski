"""
Unit Tests for Escalation System

Tests cover:
- Escalation detection
- Severity levels
- Emergency conditions
- Formatted responses
- Integration with recommendations
"""

import pytest
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock

from backend.app.recommender.escalation_handler import (
    EscalationHandler,
    get_escalation_handler,
    check_escalation,
    is_emergency_condition,
    get_escalation_advice,
)


# ===== FIXTURES =====

@pytest.fixture
def escalation_handler():
    """Create fresh escalation handler for each test."""
    return EscalationHandler()


@pytest.fixture
def sample_escalations():
    """Sample escalation data."""
    return {
        'escalations': {
            'infection': {
                'severity': 'high',
                'condition_type': 'skin',
                'medical_advice': 'Seek immediate dermatologic care',
                'action': 'escalate',
                'urgency': 'immediate',
                'triggers': ['pus-filled pustules', 'spreading rash'],
                'recommended_next_steps': [
                    'Do not self-treat',
                    'Schedule dermatology appointment'
                ],
                'why_escalated': 'Requires prescription treatment'
            },
            'urticaria_severe': {
                'severity': 'high',
                'condition_type': 'skin',
                'medical_advice': 'Go to ER immediately',
                'action': 'escalate',
                'urgency': 'immediate',
                'triggers': ['swelling of face', 'breathing difficulty'],
                'recommended_next_steps': ['Call 911', 'Go to ER'],
                'why_escalated': 'Can progress to anaphylaxis'
            },
            'severe_rash': {
                'severity': 'high',
                'condition_type': 'skin',
                'medical_advice': 'Seek dermatologic consultation',
                'action': 'escalate',
                'urgency': 'high',
                'triggers': ['widespread rash', 'blistering'],
                'recommended_next_steps': ['Stop using products', 'See dermatologist'],
                'why_escalated': 'Indicates allergies or dermatitis'
            }
        }
    }


@pytest.fixture
def sample_recommendation():
    """Sample recommendation data."""
    return {
        'routines': [
            {'name': 'Morning Routine', 'steps': ['Cleanser', 'Moisturizer']}
        ],
        'products': [
            {'name': 'Gentle Cleanser', 'why': 'Non-stripping'}
        ],
        'diet': ['Increase water intake'],
        'conditions_detected': []
    }


# ===== ESCALATION DETECTION TESTS =====

class TestEscalationDetection:
    """Test escalation detection in recommendations."""
    
    def test_detect_single_escalation(self, escalation_handler, sample_recommendation):
        """Test detecting a single escalation condition."""
        sample_recommendation['conditions_detected'] = ['infection']
        
        escalation = escalation_handler.check_recommendation(sample_recommendation)
        
        assert escalation is not None
        assert escalation['severity'] == 'high'
        assert 'medical_advice' in escalation
    
    def test_detect_multiple_conditions_with_escalation(self, escalation_handler, sample_recommendation):
        """Test detecting escalation when multiple conditions present."""
        sample_recommendation['conditions_detected'] = ['acne', 'infection', 'dry_skin']
        
        escalation = escalation_handler.check_recommendation(sample_recommendation)
        
        # Should detect first escalation (infection)
        assert escalation is not None
        assert escalation['severity'] == 'high'
    
    def test_no_escalation_detected(self, escalation_handler, sample_recommendation):
        """Test when no escalation condition is present."""
        sample_recommendation['conditions_detected'] = ['acne', 'oily_skin']
        
        escalation = escalation_handler.check_recommendation(sample_recommendation)
        
        assert escalation is None
    
    def test_empty_conditions_list(self, escalation_handler, sample_recommendation):
        """Test with empty conditions list."""
        sample_recommendation['conditions_detected'] = []
        
        escalation = escalation_handler.check_recommendation(sample_recommendation)
        
        assert escalation is None


# ===== CONDITION LOOKUP TESTS =====

class TestConditionLookup:
    """Test individual condition lookup methods."""
    
    def test_check_specific_condition_exists(self, escalation_handler):
        """Test checking for existing escalation condition."""
        escalation = escalation_handler.check_condition('infection')
        
        assert escalation is not None
        assert escalation['severity'] == 'high'
    
    def test_check_specific_condition_not_exists(self, escalation_handler):
        """Test checking for non-existent condition."""
        escalation = escalation_handler.check_condition('non_existent')
        
        assert escalation is None
    
    def test_get_escalation_message(self, escalation_handler):
        """Test retrieving medical advice message."""
        message = escalation_handler.get_escalation_message('infection')
        
        assert message is not None
        assert isinstance(message, str)
        assert len(message) > 0
    
    def test_get_severity(self, escalation_handler):
        """Test retrieving severity level."""
        severity = escalation_handler.get_severity('infection')
        
        assert severity == 'high'
    
    def test_get_condition_type(self, escalation_handler):
        """Test retrieving condition type."""
        cond_type = escalation_handler.get_condition_type('infection')
        
        assert cond_type == 'skin'
    
    def test_get_triggers(self, escalation_handler):
        """Test retrieving trigger symptoms."""
        triggers = escalation_handler.get_triggers('infection')
        
        assert triggers is not None
        assert isinstance(triggers, list)
        assert len(triggers) > 0
    
    def test_get_next_steps(self, escalation_handler):
        """Test retrieving recommended next steps."""
        steps = escalation_handler.get_next_steps('infection')
        
        assert steps is not None
        assert isinstance(steps, list)
        assert len(steps) > 0


# ===== SEVERITY & URGENCY TESTS =====

class TestSeverityAndUrgency:
    """Test severity and urgency classification."""
    
    def test_is_emergency_true(self, escalation_handler):
        """Test emergency condition detection (true case)."""
        is_emergency = escalation_handler.is_emergency('urticaria_severe')
        
        assert is_emergency is True
    
    def test_is_emergency_false(self, escalation_handler):
        """Test emergency condition detection (false case)."""
        is_emergency = escalation_handler.is_emergency('severe_rash')
        
        assert is_emergency is False
    
    def test_is_emergency_nonexistent(self, escalation_handler):
        """Test emergency check for non-existent condition."""
        is_emergency = escalation_handler.is_emergency('nonexistent')
        
        assert is_emergency is False
    
    def test_get_all_emergencies(self, escalation_handler):
        """Test retrieving all emergency conditions."""
        emergencies = escalation_handler.get_emergencies()
        
        assert emergencies is not None
        assert isinstance(emergencies, list)
        assert 'urticaria_severe' in emergencies
        assert 'infection' in emergencies
        assert 'severe_rash' not in emergencies


# ===== CATEGORIZATION TESTS =====

class TestCategorization:
    """Test escalation categorization methods."""
    
    def test_get_escalations_by_severity(self, escalation_handler):
        """Test retrieving escalations by severity."""
        high_severity = escalation_handler.get_escalations_by_severity('high')
        
        assert high_severity is not None
        assert len(high_severity) > 0
        assert 'infection' in high_severity
    
    def test_get_escalations_by_type_skin(self, escalation_handler):
        """Test retrieving skin escalations."""
        skin_conditions = escalation_handler.get_escalations_by_type('skin')
        
        assert skin_conditions is not None
        assert len(skin_conditions) > 0
        assert 'infection' in skin_conditions
    
    def test_get_escalations_by_type_hair(self, escalation_handler):
        """Test retrieving hair escalations."""
        hair_conditions = escalation_handler.get_escalations_by_type('hair')
        
        assert hair_conditions is not None
        assert 'sudden_hair_loss' in hair_conditions
        assert 'scalp_infection' in hair_conditions
    
    def test_get_escalations_by_type_systemic(self, escalation_handler):
        """Test retrieving systemic escalations."""
        systemic_conditions = escalation_handler.get_escalations_by_type('systemic')
        
        assert systemic_conditions is not None
        assert 'autoimmune_suspected' in systemic_conditions


# ===== RESPONSE FORMATTING TESTS =====

class TestResponseFormatting:
    """Test API response formatting."""
    
    def test_format_escalation_response(self, escalation_handler):
        """Test formatting escalation for API response."""
        response = escalation_handler.format_escalation_response('infection')
        
        assert response is not None
        assert 'condition' in response
        assert 'severity' in response
        assert 'message' in response
        assert 'urgency' in response
        assert 'next_steps' in response
        assert 'why_escalated' in response
        
        assert response['condition'] == 'infection'
        assert response['severity'] == 'high'
        assert response['urgency'] == 'immediate'
    
    def test_format_response_nonexistent_condition(self, escalation_handler):
        """Test formatting response for non-existent condition."""
        response = escalation_handler.format_escalation_response('nonexistent')
        
        assert response is None
    
    def test_response_contains_all_fields(self, escalation_handler):
        """Test that formatted response contains all required fields."""
        response = escalation_handler.format_escalation_response('severe_rash')
        
        required_fields = [
            'condition', 'severity', 'message', 'urgency',
            'action', 'next_steps', 'why_escalated', 'condition_type'
        ]
        
        for field in required_fields:
            assert field in response


# ===== GLOBAL HANDLER TESTS =====

class TestGlobalHandler:
    """Test global handler singleton."""
    
    def test_get_escalation_handler_singleton(self):
        """Test that get_escalation_handler returns singleton."""
        handler1 = get_escalation_handler()
        handler2 = get_escalation_handler()
        
        assert handler1 is handler2
    
    def test_check_escalation_helper(self):
        """Test check_escalation helper function."""
        recommendation = {
            'conditions_detected': ['infection'],
            'routines': [],
            'products': []
        }
        
        escalation = check_escalation(recommendation)
        
        assert escalation is not None
        assert escalation['condition'] == 'infection'
    
    def test_is_emergency_condition_helper(self):
        """Test is_emergency_condition helper function."""
        is_emerg = is_emergency_condition('urticaria_severe')
        
        assert is_emerg is True
    
    def test_get_escalation_advice_helper(self):
        """Test get_escalation_advice helper function."""
        advice = get_escalation_advice('infection')
        
        assert advice is not None
        assert isinstance(advice, str)


# ===== INTEGRATION TESTS =====

class TestEscalationIntegration:
    """Test escalation integration with recommendations."""
    
    def test_full_escalation_flow(self, escalation_handler):
        """Test complete escalation detection and response formatting."""
        recommendation = {
            'conditions_detected': ['severe_rash'],
            'routines': [],
            'products': [],
            'diet': []
        }
        
        # Step 1: Detect escalation
        escalation_data = escalation_handler.check_recommendation(recommendation)
        assert escalation_data is not None
        
        # Step 2: Find condition name
        condition_name = None
        for cond in escalation_handler.get_all_escalation_conditions():
            if escalation_handler.conditions[cond] == escalation_data:
                condition_name = cond
                break
        
        assert condition_name == 'severe_rash'
        
        # Step 3: Format response
        response = escalation_handler.format_escalation_response(condition_name)
        
        assert response is not None
        assert response['condition'] == 'severe_rash'
        assert response['severity'] == 'high'
    
    def test_escalation_with_audit_logging(self, escalation_handler):
        """Test escalation detection with logging."""
        recommendation = {
            'conditions_detected': ['infection'],
            'routines': [],
            'products': []
        }
        
        # Should log warning
        with patch('backend.app.recommender.escalation_handler.logger') as mock_logger:
            escalation_handler.check_recommendation(recommendation)
            
            # Verify warning was logged
            mock_logger.warning.assert_called_once()
    
    def test_multiple_recommendations_no_escalation_then_escalation(self, escalation_handler):
        """Test processing multiple recommendations, one with escalation."""
        rec1 = {'conditions_detected': ['acne'], 'routines': []}
        rec2 = {'conditions_detected': ['infection'], 'routines': []}
        
        # First recommendation - no escalation
        escalation1 = escalation_handler.check_recommendation(rec1)
        assert escalation1 is None
        
        # Second recommendation - escalation
        escalation2 = escalation_handler.check_recommendation(rec2)
        assert escalation2 is not None


# ===== EDGE CASES =====

class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_missing_conditions_detected_field(self, escalation_handler):
        """Test recommendation missing conditions_detected field."""
        recommendation = {'routines': [], 'products': []}
        
        escalation = escalation_handler.check_recommendation(recommendation)
        
        assert escalation is None
    
    def test_none_conditions_list(self, escalation_handler):
        """Test recommendation with None conditions_detected."""
        recommendation = {
            'conditions_detected': None,
            'routines': []
        }
        
        # Will raise TypeError when iterating None, which is expected behavior
        # The calling code should ensure conditions_detected is always a list
        with pytest.raises(TypeError):
            escalation_handler.check_recommendation(recommendation)
    
    def test_get_all_conditions(self, escalation_handler):
        """Test retrieving all escalation conditions."""
        conditions = escalation_handler.get_all_escalation_conditions()
        
        assert conditions is not None
        assert isinstance(conditions, list)
        assert len(conditions) > 0
        assert 'infection' in conditions
    
    def test_escalation_file_not_found(self):
        """Test handler with missing escalation file."""
        handler = EscalationHandler(escalation_file="/nonexistent/path/escalation.yml")
        
        # Should handle gracefully
        conditions = handler.get_all_escalation_conditions()
        
        assert conditions == []


# ===== COUNT & STATISTICS TESTS =====

class TestStatistics:
    """Test escalation statistics and counts."""
    
    def test_escalation_count(self, escalation_handler):
        """Test total count of escalation conditions."""
        conditions = escalation_handler.get_all_escalation_conditions()
        
        # Should have at least the documented conditions (currently 10)
        assert len(conditions) >= 10
    
    def test_emergency_count(self, escalation_handler):
        """Test count of emergency conditions."""
        emergencies = escalation_handler.get_emergencies()
        
        # Should have multiple emergencies
        assert len(emergencies) >= 2  # infection, urticaria_severe
    
    def test_condition_type_distribution(self, escalation_handler):
        """Test distribution of condition types."""
        skin = escalation_handler.get_escalations_by_type('skin')
        hair = escalation_handler.get_escalations_by_type('hair')
        systemic = escalation_handler.get_escalations_by_type('systemic')
        
        total = len(skin) + len(hair) + len(systemic)
        
        assert total == len(escalation_handler.get_all_escalation_conditions())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
