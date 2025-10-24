"""
Recommender Engine Module

Core business logic for applying recommendation rules to user analysis and profiles.

Key Components:
- RuleEngine: Main class that loads YAML rules and applies them
- Condition Matching: Evaluates user data against rule conditions
- Action Merging: Combines multiple matched rules' recommendations
- Escalation Handling: Prioritizes medical escalations

Usage:
    from backend.app.recommender.engine import RuleEngine
    
    engine = RuleEngine()  # Loads rules on initialization
    recommendation, applied_rules = engine.apply_rules(
        analysis={
            "skin_type": "oily",
            "conditions_detected": ["acne", "blackheads"],
            "skin_sensitivity": "normal"
        },
        profile={
            "age": 25,
            "pregnancy_status": False,
            "allergies": ["benzoyl_peroxide"]
        }
    )
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class RuleEngine:
    """
    Rule-based recommendation engine for skincare and haircare.
    
    Loads YAML rules and applies them to user analysis + profile data.
    Handles condition matching, action merging, and escalation prioritization.
    """
    
    # Escalation severity levels (higher number = more severe)
    ESCALATION_LEVELS = {
        "none": 0,
        "warning": 1,
        "caution": 2,
        "urgent": 3,
        "emergency": 4,
    }
    
    def __init__(self, rules_path: Optional[str] = None):
        """
        Initialize the rule engine by loading YAML rules.
        
        Args:
            rules_path: Path to rules.yaml file. If None, uses default location.
        
        Raises:
            FileNotFoundError: If rules.yaml not found
            yaml.YAMLError: If YAML parsing fails
        """
        if rules_path is None:
            rules_path = Path(__file__).parent / "rules.yaml"
        else:
            rules_path = Path(rules_path)
        
        if not rules_path.exists():
            raise FileNotFoundError(f"Rules file not found: {rules_path}")
        
        try:
            with open(rules_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                self.rules = config.get('rules', [])
                logger.info(f"Loaded {len(self.rules)} rules from {rules_path}")
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML rules: {e}")
            raise
    
    def apply_rules(
        self,
        analysis: Dict[str, Any],
        profile: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], List[str]]:
        """
        Apply all matching rules to user analysis and profile data.
        
        Args:
            analysis: User skin/hair analysis data
                {
                    "skin_type": "oily|dry|combination|sensitive|normal",
                    "conditions_detected": ["acne", "blackheads", ...],
                    "skin_sensitivity": "normal|sensitive|very_sensitive",
                    "hair_type": "straight|curly|wavy|coily",
                    "hair_condition": ["dry_hair", "damaged_hair", ...],
                    "age": 25,
                    "birth_year": 1999
                }
            
            profile: User profile data with lifestyle/medical flags
                {
                    "age": 25,
                    "pregnancy_status": False,
                    "breastfeeding_status": False,
                    "allergies": ["benzoyl_peroxide", "salicylic_acid"],
                    "lifestyle_flags": ["high_sun_exposure", "high_stress"],
                    "budget_level": "medium"
                }
        
        Returns:
            Tuple[recommendation_dict, applied_rules_list]
            
            recommendation_dict: {
                "routines": [
                    {
                        "step": "morning|evening|weekly|intensive",
                        "routine_text": "Step 1 → Step 2 → ...",
                        "source_rules": ["r001", "r003"]
                    }
                ],
                "products": [
                    {
                        "external_id": "product_id_001",
                        "name": "Product Name",
                        "reason": "Recommended by r001 for acne control",
                        "source_rules": ["r001"]
                    }
                ],
                "product_tags": [
                    {
                        "tag": "exfoliating",
                        "reason": "For oil control",
                        "source_rules": ["r001"]
                    }
                ],
                "diet": [
                    {
                        "action": "increase",
                        "items": ["omega-3 fatty acids", "water intake"],
                        "source_rules": ["r001"]
                    }
                ],
                "warnings": [
                    {
                        "text": "Salicylic acid may cause initial dryness",
                        "source_rules": ["r001"]
                    }
                ],
                "escalation": {
                    "level": "urgent|caution|warning|none",
                    "message": "See dermatologist for X",
                    "source_rules": ["r008"]
                }
            }
            
            applied_rules_list: List of rule IDs that matched ["r001", "r003"]
        """
        matched_rules = []
        recommendation = {
            "routines": [],
            "products": [],
            "product_tags": [],
            "diet": [],
            "warnings": [],
            "escalation": {
                "level": "none",
                "message": None,
                "source_rules": []
            },
            "metadata": {
                "total_rules_checked": len(self.rules),
                "rules_matched": 0,
                "generated_at": datetime.utcnow().isoformat()
            }
        }
        
        # Sort rules by priority (1 = highest)
        sorted_rules = sorted(self.rules, key=lambda r: r.get('priority', 10))
        
        # Evaluate each rule
        for rule in sorted_rules:
            rule_id = rule.get('id')
            
            # Check if rule matches conditions
            if self._matches_conditions(rule, analysis, profile):
                # Check contraindications
                if self._check_contraindications(rule, profile):
                    logger.info(f"Rule {rule_id} skipped due to contraindications")
                    continue
                
                logger.info(f"Rule {rule_id} matched")
                matched_rules.append(rule_id)
                
                # Apply rule's actions
                self._apply_rule_actions(rule, recommendation, rule_id)
        
        # Update metadata
        recommendation["metadata"]["rules_matched"] = len(matched_rules)
        
        # Finalize escalation level
        self._finalize_escalation(recommendation)
        
        logger.info(f"Applied {len(matched_rules)} rules: {matched_rules}")
        
        return recommendation, matched_rules
    
    def _matches_conditions(
        self,
        rule: Dict[str, Any],
        analysis: Dict[str, Any],
        profile: Dict[str, Any]
    ) -> bool:
        """
        Check if a rule's conditions match the user data.
        
        Supports:
        - Exact matches: skin_type: "oily"
        - Multiple options: skin_type: [oily, combination]
        - Contains (all must be present): conditions_contains: [acne, blackheads]
        - Numeric ranges: age_range: [18, 65]
        
        Args:
            rule: Rule dictionary with conditions
            analysis: User analysis data
            profile: User profile data
        
        Returns:
            True if all conditions match, False otherwise
        """
        conditions = rule.get('conditions', [])
        
        for condition in conditions:
            # Each condition is a dict with key=field, value=criterion
            for field, criterion in condition.items():
                if not self._evaluate_condition(field, criterion, analysis, profile):
                    return False
        
        return True
    
    def _evaluate_condition(
        self,
        field: str,
        criterion: Any,
        analysis: Dict[str, Any],
        profile: Dict[str, Any]
    ) -> bool:
        """
        Evaluate a single condition.
        
        Args:
            field: Field name (e.g., "skin_type", "conditions_contains", "age_range")
            criterion: Expected value (string, list, dict, etc.)
            analysis: User analysis data
            profile: User profile data
        
        Returns:
            True if condition matches, False otherwise
        """
        # Combine analysis + profile for lookup (profile takes precedence)
        user_data = {**analysis, **profile}
        
        # Handle "contains" conditions (all items must be in user's list)
        if field.endswith('_contains'):
            base_field = field.replace('_contains', '')
            user_value = user_data.get(base_field, [])
            
            if not isinstance(user_value, list):
                user_value = [user_value]
            if not isinstance(criterion, list):
                criterion = [criterion]
            
            # All criterion items must be in user_value
            for item in criterion:
                if item not in user_value:
                    return False
            return True
        
        # Handle range conditions
        if field.endswith('_range'):
            base_field = field.replace('_range', '')
            user_value = user_data.get(base_field)
            
            if user_value is None:
                return False
            
            if not isinstance(criterion, (list, tuple)) or len(criterion) != 2:
                return False
            
            min_val, max_val = criterion
            return min_val <= user_value <= max_val
        
        # Handle exact match conditions
        user_value = user_data.get(field)
        
        if user_value is None:
            return False
        
        # Single value criterion
        if isinstance(criterion, str):
            return user_value == criterion
        
        # Multiple options criterion (OR logic)
        if isinstance(criterion, list):
            return user_value in criterion
        
        # Direct comparison
        return user_value == criterion
    
    def _check_contraindications(
        self,
        rule: Dict[str, Any],
        profile: Dict[str, Any]
    ) -> bool:
        """
        Check if user profile contradicts the rule's avoid_if conditions.
        
        Args:
            rule: Rule dictionary with avoid_if list
            profile: User profile data
        
        Returns:
            True if rule should be avoided (contraindicated), False otherwise
        """
        avoid_if = rule.get('avoid_if', [])
        
        # Handle "none" as string
        if avoid_if == 'none' or avoid_if == ['none']:
            return False
        
        if not avoid_if or avoid_if is None:
            return False
        
        # Check each contraindication
        for condition in avoid_if:
            # Pregnancy contraindication
            if condition == 'pregnancy' and profile.get('pregnancy_status', False):
                logger.info(f"Rule contraindicated: pregnancy")
                return True
            
            # Breastfeeding contraindication
            if condition == 'breastfeeding' and profile.get('breastfeeding_status', False):
                logger.info(f"Rule contraindicated: breastfeeding")
                return True
            
            # Very sensitive skin contraindication
            if condition == 'very_sensitive':
                if profile.get('skin_sensitivity') == 'very_sensitive':
                    logger.info(f"Rule contraindicated: very_sensitive skin")
                    return True
            
            # Active infection contraindication
            if condition == 'active_infection' and profile.get('active_infection', False):
                logger.info(f"Rule contraindicated: active_infection")
                return True
            
            # Allergies contraindication
            if condition == 'allergies':
                user_allergies = set(profile.get('allergies', []))
                rule_ingredients = set(rule.get('actions', {}).get('ingredients_to_avoid', []))
                if user_allergies & rule_ingredients:
                    logger.info(f"Rule contraindicated: allergy conflict")
                    return True
        
        return False
    
    def _apply_rule_actions(
        self,
        rule: Dict[str, Any],
        recommendation: Dict[str, Any],
        rule_id: str
    ) -> None:
        """
        Extract and merge rule's actions into the recommendation.
        
        Args:
            rule: Rule dictionary with actions
            recommendation: Accumulated recommendation dict (modified in-place)
            rule_id: ID of this rule for tracking
        """
        actions = rule.get('actions', {})
        
        # Extract products by external ID
        product_ids = actions.get('recommend_products_external_ids', [])
        for product_id in product_ids:
            # Check if already added
            existing = [p for p in recommendation['products'] if p['external_id'] == product_id]
            if not existing:
                recommendation['products'].append({
                    'external_id': product_id,
                    'reason': f"Recommended for {rule.get('name')}",
                    'source_rules': [rule_id]
                })
            else:
                existing[0]['source_rules'].append(rule_id)
        
        # Extract product tags
        tags = actions.get('recommend_products_tags', [])
        for tag in tags:
            existing = [t for t in recommendation['product_tags'] if t['tag'] == tag]
            if not existing:
                recommendation['product_tags'].append({
                    'tag': tag,
                    'reason': f"For {rule.get('name')}",
                    'source_rules': [rule_id]
                })
            else:
                existing[0]['source_rules'].append(rule_id)
        
        # Extract routines
        routine_dict = actions.get('routine', {})
        for step_key, routine_text in routine_dict.items():
            # Check if step already exists
            existing = [r for r in recommendation['routines'] if r['step'] == step_key]
            if not existing:
                recommendation['routines'].append({
                    'step': step_key,
                    'routine_text': routine_text,
                    'source_rules': [rule_id]
                })
            else:
                # Merge routine text (append with separator)
                existing[0]['routine_text'] += f" | {routine_text}"
                existing[0]['source_rules'].append(rule_id)
        
        # Extract diet recommendations
        diet_rec = actions.get('diet_recommendations', {})
        for action_type in ['increase', 'limit']:
            items = diet_rec.get(action_type, [])
            if items:
                existing = [d for d in recommendation['diet'] if d['action'] == action_type]
                if not existing:
                    recommendation['diet'].append({
                        'action': action_type,
                        'items': items,
                        'source_rules': [rule_id]
                    })
                else:
                    # Merge items (deduplicate)
                    existing_items = set(existing[0]['items'])
                    new_items = set(items)
                    existing[0]['items'] = list(existing_items | new_items)
                    existing[0]['source_rules'].append(rule_id)
        
        # Extract warnings
        warnings = actions.get('warnings', [])
        for warning_text in warnings:
            # Check for duplicates
            existing = [w for w in recommendation['warnings'] if w['text'] == warning_text]
            if not existing:
                recommendation['warnings'].append({
                    'text': warning_text,
                    'source_rules': [rule_id]
                })
            else:
                existing[0]['source_rules'].append(rule_id)
        
        # Extract escalation (accumulate highest severity)
        escalation = rule.get('escalation', 'none')
        if escalation and escalation != 'none':
            self._update_escalation(recommendation, escalation, rule_id)
    
    def _update_escalation(
        self,
        recommendation: Dict[str, Any],
        escalation_text: str,
        rule_id: str
    ) -> None:
        """
        Update recommendation's escalation to highest severity.
        
        Args:
            recommendation: Recommendation dict to update
            escalation_text: Escalation message from rule
            rule_id: ID of rule with escalation
        """
        # Determine severity level from escalation text
        level = "caution"  # Default
        if "urgent" in escalation_text.lower() or "immediately" in escalation_text.lower():
            level = "urgent"
        elif "emergency" in escalation_text.lower() or "911" in escalation_text.lower():
            level = "emergency"
        elif "warn" in escalation_text.lower():
            level = "warning"
        
        # Keep highest severity
        current_level = self.ESCALATION_LEVELS.get(recommendation['escalation']['level'], 0)
        new_level = self.ESCALATION_LEVELS.get(level, 0)
        
        if new_level > current_level:
            recommendation['escalation']['level'] = level
            recommendation['escalation']['message'] = escalation_text
            recommendation['escalation']['source_rules'] = [rule_id]
        elif new_level == current_level:
            # Same level: append rule ID
            if rule_id not in recommendation['escalation']['source_rules']:
                recommendation['escalation']['source_rules'].append(rule_id)
    
    def _finalize_escalation(self, recommendation: Dict[str, Any]) -> None:
        """
        Clean up escalation data (remove empty/none values).
        
        Args:
            recommendation: Recommendation dict to finalize
        """
        if recommendation['escalation']['level'] == 'none':
            recommendation['escalation'] = None
        elif not recommendation['escalation']['message']:
            # If no message but there's a level, set default message
            recommendation['escalation']['message'] = f"Please consult a dermatologist"
    
    def get_rules_summary(self) -> List[Dict[str, Any]]:
        """
        Get summary of all loaded rules for documentation/debugging.
        
        Returns:
            List of rule summaries with id, name, priority
        """
        return [
            {
                'id': r.get('id'),
                'name': r.get('name'),
                'priority': r.get('priority'),
                'description': r.get('description')
            }
            for r in self.rules
        ]


class AnalysisValidator:
    """
    Validates user analysis data before passing to rule engine.
    
    Ensures required fields are present and have valid values.
    """
    
    VALID_SKIN_TYPES = {'oily', 'dry', 'combination', 'sensitive', 'normal', 'very_dry'}
    VALID_SENSITIVITIES = {'normal', 'sensitive', 'very_sensitive'}
    VALID_HAIR_TYPES = {'straight', 'wavy', 'curly', 'coily'}
    
    @staticmethod
    def validate_analysis(analysis: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate analysis data structure and values.
        
        Args:
            analysis: User analysis data
        
        Returns:
            Tuple[is_valid, error_message]
        """
        if not isinstance(analysis, dict):
            return False, "Analysis must be a dictionary"
        
        # Validate skin_type if present
        if 'skin_type' in analysis:
            if analysis['skin_type'] not in AnalysisValidator.VALID_SKIN_TYPES:
                return False, f"Invalid skin_type: {analysis['skin_type']}"
        
        # Validate skin_sensitivity if present
        if 'skin_sensitivity' in analysis:
            if analysis['skin_sensitivity'] not in AnalysisValidator.VALID_SENSITIVITIES:
                return False, f"Invalid skin_sensitivity: {analysis['skin_sensitivity']}"
        
        # Validate hair_type if present
        if 'hair_type' in analysis:
            if analysis['hair_type'] not in AnalysisValidator.VALID_HAIR_TYPES:
                return False, f"Invalid hair_type: {analysis['hair_type']}"
        
        # Validate conditions_detected is a list
        if 'conditions_detected' in analysis:
            if not isinstance(analysis['conditions_detected'], list):
                return False, "conditions_detected must be a list"
        
        # Validate age if present
        if 'age' in analysis:
            if not isinstance(analysis['age'], (int, float)) or analysis['age'] < 0:
                return False, "age must be a non-negative number"
        
        return True, None
    
    @staticmethod
    def validate_profile(profile: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate profile data structure and values.
        
        Args:
            profile: User profile data
        
        Returns:
            Tuple[is_valid, error_message]
        """
        if not isinstance(profile, dict):
            return False, "Profile must be a dictionary"
        
        # Validate boolean flags
        bool_fields = ['pregnancy_status', 'breastfeeding_status', 'active_infection']
        for field in bool_fields:
            if field in profile:
                if not isinstance(profile[field], bool):
                    return False, f"{field} must be a boolean"
        
        # Validate allergies is a list
        if 'allergies' in profile:
            if not isinstance(profile['allergies'], list):
                return False, "allergies must be a list"
        
        # Validate age if present
        if 'age' in profile:
            if not isinstance(profile['age'], (int, float)) or profile['age'] < 0:
                return False, "age must be a non-negative number"
        
        return True, None


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    engine = RuleEngine()
    
    # Test case 1: Oily skin with acne
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
    
    print("\n" + "="*60)
    print("RECOMMENDATION RESULT")
    print("="*60)
    print(f"Applied Rules: {applied_rules}")
    print(f"\nRoutines ({len(recommendation['routines'])}):")
    for routine in recommendation['routines']:
        print(f"  - {routine['step']}: {routine['routine_text'][:80]}...")
    
    print(f"\nProducts ({len(recommendation['products'])}):")
    for product in recommendation['products']:
        print(f"  - {product['external_id']}: {product['reason']}")
    
    print(f"\nProduct Tags ({len(recommendation['product_tags'])}):")
    for tag in recommendation['product_tags']:
        print(f"  - {tag['tag']}: {tag['reason']}")
    
    print(f"\nDiet Recommendations ({len(recommendation['diet'])}):")
    for diet in recommendation['diet']:
        print(f"  - {diet['action']}: {', '.join(diet['items'][:3])}...")
    
    print(f"\nEscalation: {recommendation['escalation']}")
    print("="*60)
