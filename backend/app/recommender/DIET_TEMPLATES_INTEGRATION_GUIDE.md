# Diet Templates Integration Guide

## Overview

The diet templates system provides food recommendations based on skin conditions and nutritional deficiencies. This guide shows how to integrate it into the recommendation engine.

---

## Quick Start

### 1. Basic Usage

```python
from backend.app.recommender.diet_templates import (
    get_manager,
    get_diet_recommendation,
    get_foods_for,
    get_combined_recommendation
)

# Get recommendation for single condition
acne_rec = get_diet_recommendation('acne')
print(acne_rec['foods'])  # List of foods

# Get just foods
foods = get_foods_for('hair_loss')

# Get combined recommendation for multiple conditions
combined = get_combined_recommendation(['acne', 'dry_skin', 'hair_loss'])
print(combined['combined_foods'])  # Top recommended foods
```

### 2. Using the Manager

```python
from backend.app.recommender.diet_templates import DietTemplateManager

# Create manager
manager = DietTemplateManager()

# Query by condition
acne = manager.get_by_key('acne')

# Query by deficiency
omega3_foods = manager.get_by_deficiency('omega-3')

# Get multiple conditions
templates = manager.get_for_conditions(['acne', 'hair_loss'])

# Combine foods
combined = manager.combine_foods(['acne', 'dry_skin'], max_foods=10)
```

---

## Integration Points

### In Recommendation Engine

**File:** `backend/app/recommender/engine.py`

```python
from backend.app.recommender.diet_templates import get_combined_recommendation

class RuleEngine:
    def generate_recommendation(self, user_analysis):
        # ... existing recommendation logic ...
        
        # Add diet recommendations
        conditions_detected = self._detect_conditions(user_analysis)
        diet_rec = get_combined_recommendation(conditions_detected)
        
        recommendation['dietary_suggestions'] = diet_rec
        return recommendation
```

### In API Endpoints

**File:** `backend/app/api/v1/recommend.py`

```python
from backend.app.recommender.diet_templates import get_combined_recommendation

@router.post("/recommend")
def generate_recommendation(request: RecommendationRequest):
    # ... existing logic ...
    
    # Get diet recommendations
    diet_suggestions = get_combined_recommendation(
        conditions=request.detected_conditions
    )
    
    return {
        'products': products_recommendation,
        'routines': routine_recommendation,
        'diet': diet_suggestions
    }
```

### In Feedback System

**File:** `backend/app/api/v1/feedback.py`

```python
from backend.app.recommender.diet_templates import get_foods_for

@router.post("/feedback/{recommendation_id}")
def submit_feedback(recommendation_id: str, feedback: FeedbackRequest):
    # ... existing logic ...
    
    # Track diet feedback
    if feedback.followed_diet_suggestions:
        recommendation = db.query(RecommendationRecord).get(recommendation_id)
        for condition in recommendation.conditions:
            diet_foods = get_foods_for(condition)
            # Track adherence
    
    return feedback_response
```

---

## Condition Detection

### From User Analysis

```python
def detect_conditions(user_analysis):
    """Map user analysis to diet template conditions"""
    conditions = []
    
    # From skin analysis
    if user_analysis.skin_type == 'acne_prone':
        conditions.append('acne')
    elif user_analysis.skin_type == 'dry':
        conditions.append('dry_skin')
    
    # From hair analysis
    if user_analysis.hair_loss_severity > 0:
        conditions.append('hair_loss')
    if user_analysis.hair_type == 'dry':
        conditions.append('dry_hair')
    
    # From nutrient deficiencies
    if user_analysis.has_deficiency('iron'):
        conditions.append('iron_deficiency')
    
    return conditions
```

### From Survey Responses

```python
def map_survey_to_conditions(survey_responses):
    """Map user survey responses to conditions"""
    conditions = []
    
    # User-reported issues
    if 'acne' in survey_responses.get('main_concern', '').lower():
        conditions.append('acne')
    
    if 'hair loss' in survey_responses.get('hair_concerns', ''):
        conditions.append('hair_loss')
    
    # Deficiencies from history
    if survey_responses.get('takes_supplements') is False:
        conditions.extend(['vitamin_d_deficiency', 'omega_3_deficiency'])
    
    return conditions
```

---

## Response Format

### Single Condition Response

```json
{
  "key": "acne",
  "foods": [
    "leafy greens (spinach, kale)",
    "berries (blueberries, raspberries)",
    "omega-3 rich fish (salmon, sardines)",
    "probiotics (yogurt, kefir, sauerkraut)",
    "green tea"
  ],
  "description": "Anti-inflammatory foods that reduce sebum production...",
  "deficiency_type": "omega-3, zinc, vitamin A",
  "benefits": [
    "Reduces inflammation",
    "Lowers sebum production",
    "Supports skin barrier",
    "Fights acne-causing bacteria"
  ]
}
```

### Combined Conditions Response

```json
{
  "conditions": ["acne", "dry_skin", "hair_loss"],
  "combined_foods": [
    "leafy greens",
    "berries",
    "omega-3 fish",
    "nuts and seeds",
    "eggs",
    "avocado"
  ],
  "all_foods": [
    "leafy greens", 
    "berries",
    "omega-3 fish",
    "probiotics",
    "green tea",
    ...
  ],
  "food_frequency": {
    "leafy greens": 3,
    "berries": 3,
    "omega-3 fish": 3,
    "nuts and seeds": 2,
    "eggs": 2
  },
  "recommendations": [
    "acne: Anti-inflammatory foods...",
    "dry_skin: Rich foods that provide...",
    "hair_loss: Protein, iron, and biotin-rich..."
  ]
}
```

---

## API Response Example

### Recommendation Response with Diet

```json
{
  "recommendation_id": "rec_12345",
  "user_id": 1,
  "analysis_id": 5,
  "status": "success",
  "created_at": "2024-01-15T10:30:00",
  
  "skincare_routine": [
    {
      "step": 1,
      "product_id": 1,
      "product_name": "Cleanser",
      "frequency": "2x daily",
      "reason": "Removes excess oil without stripping"
    }
  ],
  
  "diet_suggestions": {
    "conditions": ["acne", "oily_skin"],
    "combined_foods": [
      "leafy greens (spinach, kale)",
      "berries (blueberries, raspberries)",
      "omega-3 fish (salmon, sardines)",
      "green tea",
      "citrus fruits",
      "lean proteins",
      "whole grains"
    ],
    "food_frequency": {
      "leafy greens": 2,
      "berries": 2,
      "omega-3 fish": 2,
      "green tea": 1,
      "citrus fruits": 1
    },
    "key_recommendations": [
      "Reduce saturated fats - switch to lean proteins",
      "Increase antioxidants - add berries to breakfast",
      "Boost omega-3s - eat salmon 2-3x per week",
      "Stay hydrated - drink 8-10 glasses water daily"
    ]
  },
  
  "hair_care_routine": [
    {
      "step": 1,
      "product_id": 10,
      "product_name": "Hair Oil",
      "frequency": "2x weekly"
    }
  ]
}
```

---

## Frontend Integration

### Display Diet Recommendations

**React Component Example:**

```tsx
interface DietSuggestions {
  conditions: string[];
  combined_foods: string[];
  food_frequency: Record<string, number>;
  key_recommendations: string[];
}

export function DietRecommendations({ diet }: { diet: DietSuggestions }) {
  return (
    <div className="diet-suggestions">
      <h2>Nutritional Recommendations</h2>
      
      <div className="conditions">
        <p>Addresses: {diet.conditions.join(', ')}</p>
      </div>
      
      <div className="foods">
        <h3>Recommended Foods</h3>
        <ul>
          {diet.combined_foods.map(food => (
            <li key={food}>{food}</li>
          ))}
        </ul>
      </div>
      
      <div className="tips">
        <h3>Key Tips</h3>
        <ul>
          {diet.key_recommendations.map((tip, i) => (
            <li key={i}>{tip}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
```

### Food Frequency Visualization

```tsx
export function FoodFrequencyChart({ frequency }: { frequency: Record<string, number> }) {
  return (
    <div className="frequency-chart">
      {Object.entries(frequency).map(([food, count]) => (
        <div key={food} className="frequency-item">
          <span>{food}</span>
          <span className="count">{count} recommendations</span>
          <div className="bar" style={{ width: `${(count / 3) * 100}%` }}></div>
        </div>
      ))}
    </div>
  );
}
```

---

## Testing Integration

### Unit Tests

```python
def test_diet_recommendation_in_engine():
    """Test diet recommendation in rule engine"""
    engine = RuleEngine()
    analysis = UserAnalysis(skin_type='acne', hair_condition='dry')
    
    recommendation = engine.generate_recommendation(analysis)
    
    assert 'dietary_suggestions' in recommendation
    assert len(recommendation['dietary_suggestions']['combined_foods']) > 0
```

### Integration Tests

```python
def test_recommendation_with_diet_and_products():
    """Test recommendation combining products and diet"""
    recommendation = generate_recommendation(
        user_id=1,
        include_diet=True
    )
    
    assert 'products' in recommendation
    assert 'diet_suggestions' in recommendation
    
    # Diet should complement products
    assert recommendation['diet_suggestions']['conditions']
```

---

## Data Flow

```
User Analysis
      ↓
Detect Conditions (acne, dry_skin, etc.)
      ↓
Query Diet Templates
      ↓
Combine Recommendations
      ↓
Generate Response
      ↓
Frontend Displays Foods & Tips
      ↓
User Provides Feedback
      ↓
Track Adherence & Results
```

---

## Performance Considerations

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_diet_recommendation_cached(condition_key: str):
    """Cached diet recommendation"""
    return get_diet_recommendation(condition_key)
```

### Lazy Loading

```python
# Manager loads templates once on first use
manager = get_manager()  # Templates loaded
rec = manager.get_by_key('acne')  # No I/O needed
```

---

## Error Handling

```python
def get_diet_with_fallback(conditions: List[str]) -> Dict:
    """Get diet recommendation with fallback"""
    try:
        return get_combined_recommendation(conditions)
    except Exception as e:
        logger.error(f"Error getting diet recommendation: {e}")
        # Return generic wellness recommendation
        return get_diet_recommendation('general_wellness')
```

---

## Troubleshooting

### Templates Not Loading

```python
manager = DietTemplateManager()
validation = manager.validate()

if not validation['is_valid']:
    print(validation['issues'])
    print(validation['warnings'])
```

### Missing Condition

```python
manager = get_manager()
all_keys = manager.get_all_keys()

if 'desired_condition' not in all_keys:
    # Try similar condition
    similar = [k for k in all_keys if 'keyword' in k]
```

---

## Next Steps

1. **Integrate** into recommendation engine
2. **Test** with sample user data
3. **Deploy** with products endpoint
4. **Collect** user feedback on diet recommendations
5. **Enhance** with user-specific preferences (allergies, restrictions)
6. **Expand** with meal plans and recipes

---

## Files Reference

| File | Purpose |
|------|---------|
| `diet_templates.yml` | Template data (30+ entries) |
| `diet_templates.py` | Manager and utilities |
| `test_diet_templates.py` | Comprehensive tests |
| `DIET_TEMPLATES_README.md` | Documentation |
| `DIET_TEMPLATES_INTEGRATION_GUIDE.md` | This file |

---

**Status:** Ready for integration
