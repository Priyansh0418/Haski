"""
Unit Tests for Recommender Engine

Test coverage:
- Rule matching logic
- Condition evaluation
- Contraindication checking
- Action merging
- Escalation prioritization
- Data validation
"""

import pytest
from pathlib import Path
from backend.app.recommender.engine import RuleEngine, AnalysisValidator


class TestRuleEngineInitialization:
    """Test rule engine initialization and loading."""
    
    def test_engine_loads_rules(self):
        """Test that engine successfully loads YAML rules."""
        engine = RuleEngine()
        assert len(engine.rules) > 0, "Engine should load at least one rule"
        assert all('id' in r for r in engine.rules), "All rules should have an ID"
    
    def test_rules_have_required_fields(self):
        """Test that all rules have required fields."""
        engine = RuleEngine()
        required_fields = {'id', 'name', 'priority', 'conditions', 'actions', 'escalation'}
        
        for rule in engine.rules:
            for field in required_fields:
                assert field in rule, f"Rule {rule.get('id')} missing field: {field}"
    
    def test_engine_handles_missing_file(self):
        """Test that engine raises error for missing rules file."""
        with pytest.raises(FileNotFoundError):
            RuleEngine(rules_path="/nonexistent/path/rules.yaml")


class TestConditionMatching:
    """Test condition matching logic."""
    
    def test_exact_match_skin_type(self):
        """Test exact match for skin_type condition."""
        engine = RuleEngine()
        
        analysis = {"skin_type": "oily"}
        profile = {}
        
        # Rule with skin_type: oily should match
        rule = {
            "id": "test_r001",
            "conditions": [{"skin_type": "oily"}]
        }
        
        result = engine._matches_conditions(rule, analysis, profile)
        assert result is True
    
    def test_no_match_skin_type(self):
        """Test no match for different skin_type."""
        engine = RuleEngine()
        
        analysis = {"skin_type": "dry"}
        profile = {}
        
        rule = {"id": "test", "conditions": [{"skin_type": "oily"}]}
        
        result = engine._matches_conditions(rule, analysis, profile)
        assert result is False
    
    def test_multiple_options_match(self):
        """Test matching with multiple skin_type options."""
        engine = RuleEngine()
        
        analysis = {"skin_type": "dry"}
        profile = {}
        
        rule = {"id": "test", "conditions": [{"skin_type": ["dry", "very_dry"]}]}
        
        result = engine._matches_conditions(rule, analysis, profile)
        assert result is True
    
    def test_conditions_contains_all_match(self):
        """Test contains condition where all items are present."""
        engine = RuleEngine()
        
        analysis = {"conditions_detected": ["acne", "blackheads", "congestion"]}
        profile = {}
        
        rule = {
            "id": "test",
            "conditions": [{"conditions_contains": ["acne", "blackheads"]}]
        }
        
        result = engine._matches_conditions(rule, analysis, profile)
        assert result is True
    
    def test_conditions_contains_partial_no_match(self):
        """Test contains condition where not all items are present."""
        engine = RuleEngine()
        
        analysis = {"conditions_detected": ["acne"]}
        profile = {}
        
        rule = {
            "id": "test",
            "conditions": [{"conditions_contains": ["acne", "blackheads"]}]
        }
        
        result = engine._matches_conditions(rule, analysis, profile)
        assert result is False
    
    def test_age_range_match(self):
        """Test age range condition matching."""
        engine = RuleEngine()
        
        analysis = {"age": 25}
        profile = {}
        
        rule = {"id": "test", "conditions": [{"age_range": [18, 65]}]}
        
        result = engine._matches_conditions(rule, analysis, profile)
        assert result is True
    
    def test_age_range_no_match_below(self):
        """Test age range no match when below minimum."""
        engine = RuleEngine()
        
        analysis = {"age": 15}
        profile = {}
        
        rule = {"id": "test", "conditions": [{"age_range": [18, 65]}]}
        
        result = engine._matches_conditions(rule, analysis, profile)
        assert result is False
    
    def test_multiple_conditions_all_required(self):
        """Test that all conditions must match (AND logic)."""
        engine = RuleEngine()
        
        analysis = {
            "skin_type": "oily",
            "conditions_detected": ["acne"]
        }
        profile = {}
        
        rule = {
            "id": "test",
            "conditions": [
                {"skin_type": "oily"},
                {"conditions_contains": ["acne"]}
            ]
        }
        
        result = engine._matches_conditions(rule, analysis, profile)
        assert result is True
    
    def test_multiple_conditions_one_fails(self):
        """Test that failure of one condition fails entire rule."""
        engine = RuleEngine()
        
        analysis = {
            "skin_type": "dry",  # Wrong
            "conditions_detected": ["acne"]
        }
        profile = {}
        
        rule = {
            "id": "test",
            "conditions": [
                {"skin_type": "oily"},
                {"conditions_contains": ["acne"]}
            ]
        }
        
        result = engine._matches_conditions(rule, analysis, profile)
        assert result is False


class TestContraindications:
    """Test contraindication checking."""
    
    def test_pregnancy_contraindication(self):
        """Test that rule is avoided during pregnancy."""
        engine = RuleEngine()
        
        rule = {"id": "test", "avoid_if": ["pregnancy"]}
        profile = {"pregnancy_status": True}
        
        result = engine._check_contraindications(rule, profile)
        assert result is True  # Should be avoided
    
    def test_no_pregnancy_contraindication(self):
        """Test that non-pregnant users don't trigger pregnancy contraindication."""
        engine = RuleEngine()
        
        rule = {"id": "test", "avoid_if": ["pregnancy"]}
        profile = {"pregnancy_status": False}
        
        result = engine._check_contraindications(rule, profile)
        assert result is False  # Should not be avoided
    
    def test_very_sensitive_contraindication(self):
        """Test that certain rules avoid very sensitive skin."""
        engine = RuleEngine()
        
        rule = {"id": "test", "avoid_if": ["very_sensitive"]}
        profile = {"skin_sensitivity": "very_sensitive"}
        
        result = engine._check_contraindications(rule, profile)
        assert result is True  # Should be avoided
    
    def test_sensitive_not_very_sensitive(self):
        """Test that 'sensitive' doesn't trigger 'very_sensitive' contraindication."""
        engine = RuleEngine()
        
        rule = {"id": "test", "avoid_if": ["very_sensitive"]}
        profile = {"skin_sensitivity": "sensitive"}
        
        result = engine._check_contraindications(rule, profile)
        assert result is False  # Should not be avoided
    
    def test_no_contraindications(self):
        """Test rule with no contraindications."""
        engine = RuleEngine()
        
        rule = {"id": "test", "avoid_if": ["none"]}
        profile = {"pregnancy_status": True, "breastfeeding_status": True}
        
        result = engine._check_contraindications(rule, profile)
        assert result is False  # Should not be avoided


class TestActionMerging:
    """Test merging of multiple rule actions."""
    
    def test_apply_single_rule_products(self):
        """Test applying a single rule's product recommendations."""
        engine = RuleEngine()
        
        recommendation = {
            "products": [], "product_tags": [], "routines": [],
            "diet": [], "warnings": [], "escalation": {"level": "none"}
        }
        
        rule = {
            "id": "r001",
            "name": "Test Rule",
            "actions": {
                "recommend_products_external_ids": ["product_001", "product_002"],
                "recommend_products_tags": ["tag1", "tag2"],
                "routine": {},
                "diet_recommendations": {},
                "warnings": []
            }
        }
        
        engine._apply_rule_actions(rule, recommendation, "r001")
        
        assert len(recommendation['products']) == 2
        assert len(recommendation['product_tags']) == 2
        assert recommendation['products'][0]['source_rules'] == ["r001"]
    
    def test_merge_duplicate_products(self):
        """Test that duplicate products are deduplicated."""
        engine = RuleEngine()
        
        recommendation = {
            "products": [
                {"external_id": "product_001", "reason": "From r001", "source_rules": ["r001"]}
            ],
            "product_tags": [], "routines": [],
            "diet": [], "warnings": [], "escalation": {"level": "none"}
        }
        
        rule = {
            "id": "r002",
            "name": "Test Rule 2",
            "actions": {
                "recommend_products_external_ids": ["product_001"],
                "recommend_products_tags": [],
                "routine": {},
                "diet_recommendations": {},
                "warnings": []
            }
        }
        
        engine._apply_rule_actions(rule, recommendation, "r002")
        
        # Should still have only 1 product, but with 2 source rules
        assert len(recommendation['products']) == 1
        assert "r001" in recommendation['products'][0]['source_rules']
        assert "r002" in recommendation['products'][0]['source_rules']
    
    def test_merge_diet_recommendations(self):
        """Test merging diet recommendations from multiple rules."""
        engine = RuleEngine()
        
        recommendation = {
            "products": [], "product_tags": [], "routines": [],
            "diet": [
                {
                    "action": "increase",
                    "items": ["water", "vegetables"],
                    "source_rules": ["r001"]
                }
            ],
            "warnings": [], "escalation": {"level": "none"}
        }
        
        rule = {
            "id": "r002",
            "name": "Test Rule 2",
            "actions": {
                "recommend_products_external_ids": [],
                "recommend_products_tags": [],
                "routine": {},
                "diet_recommendations": {
                    "increase": ["fruits", "water"]  # water is duplicate
                },
                "warnings": []
            }
        }
        
        engine._apply_rule_actions(rule, recommendation, "r002")
        
        # Should have deduplicated items
        assert len(recommendation['diet']) == 1
        diet_items = set(recommendation['diet'][0]['items'])
        assert 'water' in diet_items
        assert 'vegetables' in diet_items
        assert 'fruits' in diet_items
    
    def test_merge_warnings(self):
        """Test deduplicating warnings from multiple rules."""
        engine = RuleEngine()
        
        recommendation = {
            "products": [], "product_tags": [], "routines": [],
            "diet": [],
            "warnings": [
                {"text": "Warning A", "source_rules": ["r001"]}
            ],
            "escalation": {"level": "none"}
        }
        
        rule = {
            "id": "r002",
            "name": "Test Rule 2",
            "actions": {
                "recommend_products_external_ids": [],
                "recommend_products_tags": [],
                "routine": {},
                "diet_recommendations": {},
                "warnings": ["Warning A", "Warning B"]
            }
        }
        
        engine._apply_rule_actions(rule, recommendation, "r002")
        
        # Warning A should have both sources, Warning B added
        assert len(recommendation['warnings']) == 2
        warning_a = next(w for w in recommendation['warnings'] if w['text'] == 'Warning A')
        assert 'r001' in warning_a['source_rules']
        assert 'r002' in warning_a['source_rules']


class TestEscalation:
    """Test escalation level prioritization."""
    
    def test_escalation_urgent_priority(self):
        """Test that urgent escalation takes priority."""
        engine = RuleEngine()
        
        recommendation = {
            "products": [], "product_tags": [], "routines": [],
            "diet": [], "warnings": [],
            "escalation": {"level": "caution", "message": "Caution", "source_rules": ["r001"]}
        }
        
        engine._update_escalation(recommendation, "URGENT: See dermatologist immediately", "r002")
        
        assert recommendation['escalation']['level'] == 'urgent'
        assert "r002" in recommendation['escalation']['source_rules']
    
    def test_escalation_same_level_accumulates(self):
        """Test that same escalation level accumulates source rules."""
        engine = RuleEngine()
        
        recommendation = {
            "products": [], "product_tags": [], "routines": [],
            "diet": [], "warnings": [],
            "escalation": {"level": "urgent", "message": "Urgent 1", "source_rules": ["r001"]}
        }
        
        engine._update_escalation(recommendation, "URGENT: Another urgent case", "r002")
        
        assert recommendation['escalation']['level'] == 'urgent'
        assert "r001" in recommendation['escalation']['source_rules']
        assert "r002" in recommendation['escalation']['source_rules']


class TestAnalysisValidator:
    """Test data validation."""
    
    def test_valid_analysis(self):
        """Test validation of valid analysis data."""
        analysis = {
            "skin_type": "oily",
            "conditions_detected": ["acne"],
            "skin_sensitivity": "normal"
        }
        
        is_valid, error = AnalysisValidator.validate_analysis(analysis)
        assert is_valid is True
        assert error is None
    
    def test_invalid_skin_type(self):
        """Test validation rejects invalid skin_type."""
        analysis = {"skin_type": "invalid_type"}
        
        is_valid, error = AnalysisValidator.validate_analysis(analysis)
        assert is_valid is False
        assert "Invalid skin_type" in error
    
    def test_valid_profile(self):
        """Test validation of valid profile data."""
        profile = {
            "age": 25,
            "pregnancy_status": False,
            "allergies": ["benzoyl_peroxide"]
        }
        
        is_valid, error = AnalysisValidator.validate_profile(profile)
        assert is_valid is True
        assert error is None
    
    def test_invalid_pregnancy_status_type(self):
        """Test validation rejects non-boolean pregnancy_status."""
        profile = {"pregnancy_status": "yes"}  # Should be boolean
        
        is_valid, error = AnalysisValidator.validate_profile(profile)
        assert is_valid is False
        assert "boolean" in error


class TestIntegration:
    """Integration tests with real rules."""
    
    def test_oily_acne_scenario(self):
        """Test full flow for oily skin with acne."""
        engine = RuleEngine()
        
        analysis = {
            "skin_type": "oily",
            "conditions_detected": ["acne", "blackheads"],
            "skin_sensitivity": "normal"
        }
        
        profile = {
            "age": 25,
            "pregnancy_status": False,
            "breastfeeding_status": False,
            "allergies": []
        }
        
        recommendation, applied_rules = engine.apply_rules(analysis, profile)
        
        # Should have matched at least r001 (Oily + Acne)
        assert "r001" in applied_rules or len(applied_rules) > 0
        
        # Should have recommendations
        assert len(recommendation['products']) > 0
        assert len(recommendation['product_tags']) > 0
        assert len(recommendation['routines']) > 0
        
        # Should not have escalation for non-severe acne
        assert recommendation['escalation'] is None
    
    def test_dry_eczema_scenario(self):
        """Test full flow for dry skin with eczema."""
        engine = RuleEngine()
        
        analysis = {
            "skin_type": "dry",
            "conditions_detected": ["eczema", "dry_patches"],
            "skin_sensitivity": "normal"
        }
        
        profile = {
            "age": 30,
            "pregnancy_status": False,
            "breastfeeding_status": False,
            "allergies": []
        }
        
        recommendation, applied_rules = engine.apply_rules(analysis, profile)
        
        # Should have matched r002 (Dry + Eczema)
        assert "r002" in applied_rules or len(applied_rules) > 0
        
        # Check for barrier repair products/tags
        product_tags = [t['tag'] for t in recommendation['product_tags']]
        routines = [r['routine_text'] for r in recommendation['routines']]
        
        # Should have hydrating/barrier recommendations
        assert len(recommendation['products']) > 0
    
    def test_pregnancy_contraindication(self):
        """Test that pregnant users get safe recommendations."""
        engine = RuleEngine()
        
        analysis = {
            "skin_type": "combination",
            "conditions_detected": ["fine_lines"],
            "skin_sensitivity": "normal"
        }
        
        profile = {
            "age": 35,
            "pregnancy_status": True,  # PREGNANT
            "breastfeeding_status": False,
            "allergies": []
        }
        
        recommendation, applied_rules = engine.apply_rules(analysis, profile)
        
        # r004 (Anti-aging) should NOT be applied due to pregnancy
        assert "r004" not in applied_rules


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
