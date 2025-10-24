"""
Diet Templates Loader and Manager

Handles loading and managing diet recommendation templates from YAML.
Provides utilities for querying diet recommendations by condition or deficiency.
"""

import yaml
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

# Get the directory where this file is located
DIET_TEMPLATES_PATH = Path(__file__).parent / "diet_templates.yml"


class DietTemplateManager:
    """
    Manager for diet template loading and querying.
    
    Provides methods to:
    - Load diet templates from YAML
    - Query by condition key
    - Filter by deficiency type
    - Get foods for multiple conditions
    """
    
    def __init__(self, template_path: Optional[Path] = None):
        """
        Initialize diet template manager.
        
        Args:
            template_path: Optional path to diet_templates.yml file.
                          Defaults to diet_templates.yml in same directory.
        """
        self.template_path = template_path or DIET_TEMPLATES_PATH
        self.templates: Dict[str, Dict[str, Any]] = {}
        self._load_templates()
    
    def _load_templates(self) -> None:
        """
        Load diet templates from YAML file.
        
        Raises:
            FileNotFoundError: If template file doesn't exist
            yaml.YAMLError: If YAML is malformed
        """
        try:
            if not self.template_path.exists():
                logger.warning(f"Template file not found: {self.template_path}")
                self.templates = {}
                return
            
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template_list = yaml.safe_load(f)
            
            # Convert list to dict keyed by 'key' field
            self.templates = {}
            if template_list:
                for item in template_list:
                    if 'key' in item:
                        self.templates[item['key']] = item
            
            logger.info(f"Loaded {len(self.templates)} diet templates from {self.template_path}")
        
        except FileNotFoundError as e:
            logger.error(f"Diet templates file not found: {e}")
            self.templates = {}
        except yaml.YAMLError as e:
            logger.error(f"Error parsing diet templates YAML: {e}")
            self.templates = {}
        except Exception as e:
            logger.error(f"Unexpected error loading diet templates: {e}")
            self.templates = {}
    
    def get_by_key(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get diet template by condition key.
        
        Args:
            key: Condition key (e.g., 'acne', 'dry_skin', 'hair_loss')
        
        Returns:
            Template dict if found, None otherwise
        
        Example:
            >>> manager = DietTemplateManager()
            >>> acne_template = manager.get_by_key('acne')
            >>> print(acne_template['foods'])
        """
        return self.templates.get(key)
    
    def get_foods(self, key: str) -> List[str]:
        """
        Get food recommendations for a condition.
        
        Args:
            key: Condition key
        
        Returns:
            List of food recommendations, empty list if not found
        
        Example:
            >>> manager = DietTemplateManager()
            >>> foods = manager.get_foods('acne')
            >>> print(foods)  # ['leafy greens (spinach, kale)', ...]
        """
        template = self.get_by_key(key)
        if template and 'foods' in template:
            return template['foods']
        return []
    
    def get_description(self, key: str) -> Optional[str]:
        """
        Get description for a condition.
        
        Args:
            key: Condition key
        
        Returns:
            Description string if found, None otherwise
        """
        template = self.get_by_key(key)
        if template:
            return template.get('description')
        return None
    
    def get_deficiency_type(self, key: str) -> Optional[str]:
        """
        Get deficiency type for a condition.
        
        Args:
            key: Condition key
        
        Returns:
            Deficiency type string if found, None otherwise
        """
        template = self.get_by_key(key)
        if template:
            return template.get('deficiency_type')
        return None
    
    def get_benefits(self, key: str) -> List[str]:
        """
        Get benefits list for a condition.
        
        Args:
            key: Condition key
        
        Returns:
            List of benefits, empty list if not found
        """
        template = self.get_by_key(key)
        if template and 'benefits' in template:
            return template['benefits']
        return []
    
    def get_by_deficiency(self, deficiency: str) -> List[Dict[str, Any]]:
        """
        Get all templates that address a specific deficiency.
        
        Args:
            deficiency: Nutrient deficiency (e.g., 'omega-3', 'vitamin_c')
        
        Returns:
            List of matching templates
        
        Example:
            >>> manager = DietTemplateManager()
            >>> omega3_templates = manager.get_by_deficiency('omega-3')
            >>> for template in omega3_templates:
            ...     print(template['key'], template['foods'])
        """
        matching = []
        for template in self.templates.values():
            deficiency_types = template.get('deficiency_type', '')
            if deficiency.lower() in deficiency_types.lower():
                matching.append(template)
        return matching
    
    def get_for_conditions(self, conditions: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get templates for multiple conditions.
        
        Useful for combining recommendations for user with multiple conditions.
        
        Args:
            conditions: List of condition keys
        
        Returns:
            Dict mapping condition key to template
        
        Example:
            >>> manager = DietTemplateManager()
            >>> templates = manager.get_for_conditions(['acne', 'hair_loss', 'dry_skin'])
            >>> for key, template in templates.items():
            ...     print(f"{key}: {template['foods']}")
        """
        result = {}
        for condition in conditions:
            template = self.get_by_key(condition)
            if template:
                result[condition] = template
        return result
    
    def combine_foods(self, conditions: List[str], max_foods: int = 15) -> Dict[str, Any]:
        """
        Combine food recommendations for multiple conditions.
        
        Removes duplicates and prioritizes frequently suggested foods.
        
        Args:
            conditions: List of condition keys
            max_foods: Maximum number of foods to return
        
        Returns:
            Dict with combined foods, all foods, and frequencies
        
        Example:
            >>> manager = DietTemplateManager()
            >>> combined = manager.combine_foods(['acne', 'oily_skin'])
            >>> print(combined['combined_foods'])  # Top 15 foods
            >>> print(combined['food_frequency'])  # How often each food appears
        """
        food_frequency = {}
        all_foods = []
        
        for condition in conditions:
            foods = self.get_foods(condition)
            for food in foods:
                all_foods.append(food)
                # Count base food name (before parenthesis)
                base_food = food.split('(')[0].strip()
                food_frequency[base_food] = food_frequency.get(base_food, 0) + 1
        
        # Sort by frequency, then alphabetically
        sorted_foods = sorted(
            food_frequency.items(),
            key=lambda x: (-x[1], x[0])
        )
        
        # Get top foods
        top_foods = [food for food, _ in sorted_foods[:max_foods]]
        
        return {
            'combined_foods': top_foods,
            'all_foods': list(set(all_foods)),
            'food_frequency': dict(sorted_foods),
            'conditions': conditions,
            'total_unique_foods': len(set(all_foods))
        }
    
    def get_all_keys(self) -> List[str]:
        """
        Get all available condition keys.
        
        Returns:
            Sorted list of all condition keys
        
        Example:
            >>> manager = DietTemplateManager()
            >>> all_conditions = manager.get_all_keys()
            >>> print(f"Available conditions: {len(all_conditions)}")
        """
        return sorted(self.templates.keys())
    
    def get_all_deficiency_types(self) -> List[str]:
        """
        Get all unique deficiency types from templates.
        
        Returns:
            Sorted list of unique deficiency types
        """
        deficiency_set = set()
        for template in self.templates.values():
            deficiency_type = template.get('deficiency_type', '')
            # Parse comma-separated deficiencies
            for item in deficiency_type.split(','):
                item = item.strip()
                if item:
                    deficiency_set.add(item)
        return sorted(deficiency_set)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about loaded templates.
        
        Returns:
            Dict with template statistics
        
        Example:
            >>> manager = DietTemplateManager()
            >>> stats = manager.get_stats()
            >>> print(f"Total templates: {stats['total_templates']}")
            >>> print(f"Food categories: {stats['categories']}")
        """
        all_foods = set()
        all_deficiencies = set()
        categories = {}
        
        for key, template in self.templates.items():
            # Count foods
            foods = template.get('foods', [])
            all_foods.update(foods)
            
            # Collect deficiencies
            deficiency_type = template.get('deficiency_type', '')
            for item in deficiency_type.split(','):
                all_deficiencies.add(item.strip())
            
            # Categorize by key prefix
            prefix = key.split('_')[0] if '_' in key else key
            categories[prefix] = categories.get(prefix, 0) + 1
        
        return {
            'total_templates': len(self.templates),
            'total_unique_foods': len(all_foods),
            'total_deficiency_types': len(all_deficiencies),
            'categories': categories,
            'template_keys': sorted(self.templates.keys())
        }
    
    def validate(self) -> Dict[str, Any]:
        """
        Validate template structure and content.
        
        Returns:
            Dict with validation results and any issues found
        """
        issues = []
        warnings = []
        
        for key, template in self.templates.items():
            # Check required fields
            if 'foods' not in template:
                issues.append(f"Template '{key}': missing 'foods' field")
            elif not template['foods']:
                warnings.append(f"Template '{key}': empty foods list")
            
            if 'description' not in template:
                warnings.append(f"Template '{key}': missing 'description'")
            
            if 'benefits' not in template:
                warnings.append(f"Template '{key}': missing 'benefits'")
            
            if 'deficiency_type' not in template:
                warnings.append(f"Template '{key}': missing 'deficiency_type'")
            
            # Check data types
            if 'foods' in template and not isinstance(template['foods'], list):
                issues.append(f"Template '{key}': 'foods' must be a list")
            
            if 'benefits' in template and not isinstance(template['benefits'], list):
                issues.append(f"Template '{key}': 'benefits' must be a list")
        
        return {
            'is_valid': len(issues) == 0,
            'total_templates': len(self.templates),
            'issues': issues,
            'warnings': warnings
        }


# Global instance for convenience
_manager: Optional[DietTemplateManager] = None


def get_manager() -> DietTemplateManager:
    """
    Get or create global diet template manager instance.
    
    Returns:
        DietTemplateManager instance
    """
    global _manager
    if _manager is None:
        _manager = DietTemplateManager()
    return _manager


# ===== CONVENIENCE FUNCTIONS =====

def get_diet_recommendation(condition_key: str) -> Optional[Dict[str, Any]]:
    """
    Get diet recommendation for a single condition.
    
    Args:
        condition_key: Condition key (e.g., 'acne')
    
    Returns:
        Complete template dict or None
    """
    return get_manager().get_by_key(condition_key)


def get_foods_for(condition_key: str) -> List[str]:
    """
    Get foods for a single condition.
    
    Args:
        condition_key: Condition key
    
    Returns:
        List of food recommendations
    """
    return get_manager().get_foods(condition_key)


def get_combined_recommendation(conditions: List[str]) -> Dict[str, Any]:
    """
    Get combined diet recommendation for multiple conditions.
    
    Args:
        conditions: List of condition keys
    
    Returns:
        Combined recommendation with merged foods and insights
    """
    manager = get_manager()
    templates = manager.get_for_conditions(conditions)
    combined = manager.combine_foods(conditions)
    
    return {
        'conditions': conditions,
        'templates': templates,
        'combined_foods': combined['combined_foods'],
        'all_foods': combined['all_foods'],
        'food_frequency': combined['food_frequency'],
        'recommendations': [
            f"{condition}: {manager.get_description(condition)}"
            for condition in conditions
            if manager.get_by_key(condition)
        ]
    }
