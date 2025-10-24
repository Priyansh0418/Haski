"""
Tests for Diet Templates module

Tests the DietTemplateManager and convenience functions.
"""

import pytest
from pathlib import Path
from backend.app.recommender.diet_templates import (
    DietTemplateManager,
    get_manager,
    get_diet_recommendation,
    get_foods_for,
    get_combined_recommendation
)


class TestDietTemplateLoading:
    """Test loading and initialization of diet templates"""
    
    def test_manager_initialization(self):
        """Test manager initializes without error"""
        manager = DietTemplateManager()
        assert manager is not None
        assert len(manager.templates) > 0
    
    def test_templates_loaded(self):
        """Test templates are actually loaded"""
        manager = DietTemplateManager()
        templates = manager.get_all_keys()
        assert len(templates) >= 30
        assert 'acne' in templates
        assert 'hair_loss' in templates
        assert 'dry_skin' in templates
    
    def test_template_structure(self):
        """Test each template has required fields"""
        manager = DietTemplateManager()
        for key, template in manager.templates.items():
            assert 'key' in template, f"Template {key} missing 'key'"
            assert 'foods' in template, f"Template {key} missing 'foods'"
            assert isinstance(template['foods'], list), f"Template {key} foods not a list"
            assert len(template['foods']) > 0, f"Template {key} has no foods"
    
    def test_global_manager(self):
        """Test global manager singleton"""
        manager1 = get_manager()
        manager2 = get_manager()
        assert manager1 is manager2


class TestDietTemplateQueries:
    """Test querying diet templates"""
    
    @pytest.fixture
    def manager(self):
        """Get manager instance"""
        return DietTemplateManager()
    
    def test_get_by_key_acne(self, manager):
        """Test getting acne template"""
        acne = manager.get_by_key('acne')
        assert acne is not None
        assert acne['key'] == 'acne'
        assert 'leafy greens' in str(acne['foods']).lower()
        assert 'berries' in str(acne['foods']).lower()
    
    def test_get_by_key_hair_loss(self, manager):
        """Test getting hair_loss template"""
        hair = manager.get_by_key('hair_loss')
        assert hair is not None
        assert 'eggs' in str(hair['foods']).lower()
        assert 'protein' in hair.get('deficiency_type', '').lower()
    
    def test_get_by_key_nonexistent(self, manager):
        """Test getting nonexistent template"""
        result = manager.get_by_key('nonexistent_condition')
        assert result is None
    
    def test_get_foods(self, manager):
        """Test getting foods for condition"""
        foods = manager.get_foods('acne')
        assert len(foods) > 0
        assert isinstance(foods[0], str)
    
    def test_get_foods_nonexistent(self, manager):
        """Test getting foods for nonexistent condition"""
        foods = manager.get_foods('nonexistent')
        assert foods == []
    
    def test_get_description(self, manager):
        """Test getting description"""
        desc = manager.get_description('acne')
        assert desc is not None
        assert len(desc) > 0
        assert 'anti-inflammatory' in desc.lower()
    
    def test_get_benefits(self, manager):
        """Test getting benefits"""
        benefits = manager.get_benefits('acne')
        assert len(benefits) > 0
        assert isinstance(benefits[0], str)
    
    def test_get_deficiency_type(self, manager):
        """Test getting deficiency type"""
        deficiency = manager.get_deficiency_type('acne')
        assert deficiency is not None
        assert 'omega' in deficiency.lower() or 'zinc' in deficiency.lower()


class TestDeficiencyQueries:
    """Test querying by deficiency type"""
    
    @pytest.fixture
    def manager(self):
        return DietTemplateManager()
    
    def test_get_by_deficiency_omega3(self, manager):
        """Test getting templates for omega-3 deficiency"""
        templates = manager.get_by_deficiency('omega-3')
        assert len(templates) > 0
        keys = [t['key'] for t in templates]
        assert 'omega_3_deficiency' in keys
    
    def test_get_by_deficiency_vitamin_c(self, manager):
        """Test getting templates for vitamin C"""
        templates = manager.get_by_deficiency('vitamin c')
        assert len(templates) > 0
    
    def test_get_by_deficiency_iron(self, manager):
        """Test getting templates for iron"""
        templates = manager.get_by_deficiency('iron')
        assert len(templates) > 0
    
    def test_get_by_deficiency_nonexistent(self, manager):
        """Test getting templates for nonexistent deficiency"""
        templates = manager.get_by_deficiency('nonexistent_nutrient')
        assert len(templates) == 0


class TestMultiConditionRecommendations:
    """Test combining recommendations for multiple conditions"""
    
    @pytest.fixture
    def manager(self):
        return DietTemplateManager()
    
    def test_get_for_conditions(self, manager):
        """Test getting templates for multiple conditions"""
        conditions = ['acne', 'hair_loss', 'dry_skin']
        templates = manager.get_for_conditions(conditions)
        assert len(templates) == 3
        assert 'acne' in templates
        assert 'hair_loss' in templates
        assert 'dry_skin' in templates
    
    def test_get_for_conditions_partial_match(self, manager):
        """Test with some nonexistent conditions"""
        conditions = ['acne', 'nonexistent', 'dry_skin']
        templates = manager.get_for_conditions(conditions)
        assert len(templates) == 2
        assert 'acne' in templates
        assert 'dry_skin' in templates
    
    def test_combine_foods(self, manager):
        """Test combining foods from multiple conditions"""
        conditions = ['acne', 'oily_skin']
        combined = manager.combine_foods(conditions)
        
        assert 'combined_foods' in combined
        assert 'all_foods' in combined
        assert 'food_frequency' in combined
        assert len(combined['combined_foods']) > 0
        assert len(combined['all_foods']) >= len(combined['combined_foods'])
    
    def test_combine_foods_max_foods(self, manager):
        """Test combine_foods respects max_foods parameter"""
        conditions = ['acne', 'hair_loss', 'dry_skin']
        combined = manager.combine_foods(conditions, max_foods=10)
        assert len(combined['combined_foods']) <= 10
    
    def test_food_frequency(self, manager):
        """Test food frequency calculation"""
        conditions = ['acne', 'oily_skin']
        combined = manager.combine_foods(conditions)
        
        # Check frequency dict is correct type
        assert isinstance(combined['food_frequency'], dict)
        # Higher frequency items should appear first
        freq_list = list(combined['food_frequency'].values())
        assert freq_list == sorted(freq_list, reverse=True)


class TestConvenienceFunctions:
    """Test convenience wrapper functions"""
    
    def test_get_diet_recommendation(self):
        """Test getting single recommendation"""
        rec = get_diet_recommendation('acne')
        assert rec is not None
        assert 'foods' in rec
    
    def test_get_foods_for(self):
        """Test getting foods convenience function"""
        foods = get_foods_for('hair_loss')
        assert len(foods) > 0
        assert 'eggs' in str(foods).lower()
    
    def test_get_combined_recommendation(self):
        """Test combined recommendation convenience function"""
        combined = get_combined_recommendation(['acne', 'hair_loss'])
        assert 'conditions' in combined
        assert 'combined_foods' in combined
        assert 'recommendations' in combined
        assert len(combined['recommendations']) > 0


class TestStatisticsAndValidation:
    """Test statistics and validation methods"""
    
    @pytest.fixture
    def manager(self):
        return DietTemplateManager()
    
    def test_get_all_keys(self, manager):
        """Test getting all template keys"""
        keys = manager.get_all_keys()
        assert len(keys) >= 30
        assert isinstance(keys, list)
        assert all(isinstance(k, str) for k in keys)
        # Should be sorted
        assert keys == sorted(keys)
    
    def test_get_all_deficiency_types(self, manager):
        """Test getting all deficiency types"""
        deficiencies = manager.get_all_deficiency_types()
        assert len(deficiencies) > 0
        assert 'omega-3' in deficiencies
        assert 'vitamin C' in deficiencies or 'vitamin c' in deficiencies
        assert 'iron' in deficiencies
    
    def test_get_stats(self, manager):
        """Test getting statistics"""
        stats = manager.get_stats()
        
        assert 'total_templates' in stats
        assert stats['total_templates'] >= 30
        assert 'total_unique_foods' in stats
        assert stats['total_unique_foods'] > 0
        assert 'total_deficiency_types' in stats
        assert 'categories' in stats
        assert isinstance(stats['categories'], dict)
    
    def test_validate(self, manager):
        """Test template validation"""
        result = manager.validate()
        
        assert 'is_valid' in result
        assert 'total_templates' in result
        assert 'issues' in result
        assert 'warnings' in result
        
        # Should have at least some templates
        assert result['total_templates'] >= 30
        
        # Should have no critical issues
        assert len(result['issues']) == 0


class TestSpecificConditions:
    """Test specific condition templates"""
    
    @pytest.fixture
    def manager(self):
        return DietTemplateManager()
    
    def test_acne_template(self, manager):
        """Test acne template completeness"""
        acne = manager.get_by_key('acne')
        assert acne is not None
        assert len(acne['foods']) >= 5
        assert len(acne['benefits']) >= 3
        assert 'omega-3' in acne['deficiency_type'] or 'zinc' in acne['deficiency_type']
    
    def test_dry_skin_template(self, manager):
        """Test dry skin template"""
        dry = manager.get_by_key('dry_skin')
        assert dry is not None
        assert 'avocado' in str(dry['foods']).lower()
        assert 'omega' in dry['deficiency_type'].lower()
    
    def test_hair_loss_template(self, manager):
        """Test hair loss template"""
        hair = manager.get_by_key('hair_loss')
        assert hair is not None
        assert 'eggs' in str(hair['foods']).lower()
        assert 'biotin' in hair['deficiency_type'].lower()
    
    def test_vitamin_c_deficiency(self, manager):
        """Test vitamin C deficiency template"""
        vc = manager.get_by_key('vitamin_c_deficiency')
        assert vc is not None
        assert 'citrus' in str(vc['foods']).lower()
    
    def test_iron_deficiency(self, manager):
        """Test iron deficiency template"""
        iron = manager.get_by_key('iron_deficiency')
        assert iron is not None
        assert 'spinach' in str(iron['foods']).lower() or 'meat' in str(iron['foods']).lower()


class TestFoodRecommendationPatterns:
    """Test common food recommendation patterns"""
    
    @pytest.fixture
    def manager(self):
        return DietTemplateManager()
    
    def test_leafy_greens_prevalence(self, manager):
        """Test leafy greens appear in many templates"""
        leafy_count = 0
        for template in manager.templates.values():
            if any('green' in food.lower() for food in template['foods']):
                leafy_count += 1
        # Should be in many templates (at least 50% of templates)
        assert leafy_count >= len(manager.templates) / 2
    
    def test_berries_prevalence(self, manager):
        """Test berries appear in many templates"""
        berry_count = 0
        for template in manager.templates.values():
            if any('berr' in food.lower() for food in template['foods']):
                berry_count += 1
        # Should be in many templates
        assert berry_count >= 10
    
    def test_fish_for_hair(self, manager):
        """Test fish appears in hair condition templates"""
        hair_loss = manager.get_by_key('hair_loss')
        has_fish = any('fish' in food.lower() for food in hair_loss['foods'])
        assert has_fish
    
    def test_water_in_hydration(self, manager):
        """Test water appears in hydration template"""
        hydration = manager.get_by_key('poor_hydration')
        has_water = any('water' in food.lower() for food in hydration['foods'])
        assert has_water


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.fixture
    def manager(self):
        return DietTemplateManager()
    
    def test_empty_conditions_list(self, manager):
        """Test combining empty conditions list"""
        result = manager.get_for_conditions([])
        assert result == {}
    
    def test_duplicate_conditions(self, manager):
        """Test combining duplicate conditions"""
        combined1 = manager.combine_foods(['acne', 'acne'])
        combined2 = manager.combine_foods(['acne'])
        # Should have same foods
        assert set(combined1['all_foods']) == set(combined2['all_foods'])
    
    def test_case_sensitivity(self, manager):
        """Test case handling in queries"""
        # Exact case
        acne1 = manager.get_by_key('acne')
        # Different case (should not match due to exact key matching)
        acne2 = manager.get_by_key('ACNE')
        assert acne1 is not None
        assert acne2 is None
    
    def test_special_characters_in_foods(self, manager):
        """Test foods with special characters are preserved"""
        for template in manager.templates.values():
            for food in template['foods']:
                # Should handle parentheses, commas, etc.
                assert isinstance(food, str)
                assert len(food) > 0


class TestIntegration:
    """Integration tests"""
    
    def test_complete_workflow_single_condition(self):
        """Test complete workflow for single condition"""
        # Step 1: Get recommendation
        rec = get_diet_recommendation('acne')
        assert rec is not None
        
        # Step 2: Get foods
        foods = rec['foods']
        assert len(foods) > 0
        
        # Step 3: Check benefits
        benefits = rec['benefits']
        assert len(benefits) > 0
    
    def test_complete_workflow_multiple_conditions(self):
        """Test complete workflow for multiple conditions"""
        conditions = ['acne', 'hair_loss', 'dry_skin']
        
        # Get combined recommendation
        combined = get_combined_recommendation(conditions)
        
        assert len(combined['combined_foods']) > 0
        assert len(combined['recommendations']) == 3
        
        # Check each condition has foods
        for condition in conditions:
            foods = get_foods_for(condition)
            assert len(foods) > 0
    
    def test_consistency_across_queries(self):
        """Test results are consistent across different query methods"""
        manager = get_manager()
        
        # Query same condition different ways
        method1 = manager.get_by_key('acne')['foods']
        method2 = manager.get_foods('acne')
        
        assert method1 == method2
