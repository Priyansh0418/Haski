# Rule Engine Integration Guide

## Overview

The `engine.py` module provides a rule-based recommendation engine that loads YAML rules and applies them to user analysis + profile data to generate personalized skincare/haircare recommendations.

## Quick Start

### Installation

The engine requires PyYAML:

```bash
pip install pyyaml
```

### Basic Usage

```python
from backend.app.recommender.engine import RuleEngine

# Initialize engine (loads rules.yaml)
engine = RuleEngine()

# User data
analysis = {
    "skin_type": "oily",
    "conditions_detected": ["acne", "blackheads"],
    "skin_sensitivity": "normal"
}

profile = {
    "age": 25,
    "pregnancy_status": False,
    "allergies": []
}

# Apply rules
recommendation, applied_rules = engine.apply_rules(analysis, profile)

# Results
print(f"Applied rules: {applied_rules}")
print(f"Products: {recommendation['products']}")
print(f"Escalation: {recommendation['escalation']}")
```

## Core Components

### 1. RuleEngine Class

Main class that manages rule loading and application.

**Methods:**

#### `__init__(rules_path: Optional[str] = None)`

Initialize and load YAML rules.

```python
# Use default path (backend/app/recommender/rules.yaml)
engine = RuleEngine()

# Or specify custom path
engine = RuleEngine(rules_path="/custom/path/rules.yaml")
```

**Raises:**

- `FileNotFoundError`: If rules.yaml not found
- `yaml.YAMLError`: If YAML parsing fails

#### `apply_rules(analysis: Dict, profile: Dict) -> Tuple[Dict, List[str]]`

Apply all matching rules to user data.

**Args:**

`analysis`: User skin/hair analysis

```python
{
    "skin_type": "oily|dry|combination|sensitive|normal",
    "conditions_detected": ["acne", "blackheads", ...],
    "skin_sensitivity": "normal|sensitive|very_sensitive",
    "hair_type": "straight|curly|wavy|coily",  # Optional
    "hair_condition": ["dry_hair", "damaged_hair", ...],  # Optional
    "age": 25  # Optional
}
```

`profile`: User profile with medical/lifestyle flags

```python
{
    "age": 25,
    "pregnancy_status": False,
    "breastfeeding_status": False,
    "active_infection": False,
    "allergies": ["benzoyl_peroxide"],
    "lifestyle_flags": ["high_sun_exposure"],
    "budget_level": "medium"
}
```

**Returns:**

`Tuple[recommendation_dict, applied_rules_list]`

**recommendation_dict structure:**

```python
{
    "routines": [
        {
            "step": "morning|evening|weekly|intensive",
            "routine_text": "Cleanser → Toner → Serum → SPF",
            "source_rules": ["r001", "r003"]
        }
    ],
    "products": [
        {
            "external_id": "cerave_cleanser_001",
            "reason": "For hydration and barrier repair",
            "source_rules": ["r002"]
        }
    ],
    "product_tags": [
        {
            "tag": "hydrating",
            "reason": "For barrier repair",
            "source_rules": ["r002"]
        }
    ],
    "diet": [
        {
            "action": "increase",
            "items": ["omega-3 fatty acids", "water intake"],
            "source_rules": ["r001"]
        },
        {
            "action": "limit",
            "items": ["dairy products"],
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
        "message": "See dermatologist for severe acne",
        "source_rules": ["r008"]
    },
    "metadata": {
        "total_rules_checked": 9,
        "rules_matched": 2,
        "generated_at": "2025-10-24T14:30:00"
    }
}
```

**applied_rules_list:** List of rule IDs that matched

```python
["r001", "r007"]
```

#### `get_rules_summary() -> List[Dict]`

Get summary of all loaded rules (for documentation).

```python
summaries = engine.get_rules_summary()
# Returns: [
#     {"id": "r001", "name": "Oily Skin + Acne", "priority": 1},
#     ...
# ]
```

### 2. AnalysisValidator Class

Validates user input data before passing to engine.

**Static Methods:**

#### `validate_analysis(analysis: Dict) -> Tuple[bool, Optional[str]]`

Validate analysis data structure.

```python
is_valid, error = AnalysisValidator.validate_analysis({
    "skin_type": "oily",
    "conditions_detected": ["acne"]
})

if not is_valid:
    print(f"Validation error: {error}")
```

#### `validate_profile(profile: Dict) -> Tuple[bool, Optional[str]]`

Validate profile data structure.

```python
is_valid, error = AnalysisValidator.validate_profile({
    "age": 25,
    "pregnancy_status": False
})

if not is_valid:
    print(f"Validation error: {error}")
```

## Integration with FastAPI

### Example API Endpoint

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.recommender.engine import RuleEngine, AnalysisValidator
from backend.app.recommender.schemas import RecommendationRequest, RecommendationResponse

router = APIRouter()
engine = RuleEngine()  # Initialized once at module load

@router.post("/api/v1/recommend", response_model=RecommendationResponse)
async def get_recommendation(
    request: RecommendationRequest,
    db: Session = Depends(get_db)
):
    """Generate personalized recommendation based on analysis and profile."""

    # Validate input
    is_valid_analysis, error_analysis = AnalysisValidator.validate_analysis(request.analysis)
    if not is_valid_analysis:
        raise HTTPException(status_code=400, detail=error_analysis)

    is_valid_profile, error_profile = AnalysisValidator.validate_profile(request.profile)
    if not is_valid_profile:
        raise HTTPException(status_code=400, detail=error_profile)

    try:
        # Apply rules
        recommendation, applied_rules = engine.apply_rules(
            analysis=request.analysis,
            profile=request.profile
        )

        # Log applied rules to database
        for rule_id in applied_rules:
            rule_log = RuleLog(
                analysis_id=request.analysis_id,
                rule_id=rule_id,
                applied=True,
                details={"matched": True}
            )
            db.add(rule_log)

        db.commit()

        # Format response
        return RecommendationResponse(
            recommendation_id=f"rec_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            recommendation=recommendation,
            applied_rules=applied_rules,
            generated_at=datetime.utcnow()
        )

    except Exception as e:
        logger.error(f"Error generating recommendation: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate recommendation")
```

## Condition Matching Reference

### Exact Match Conditions

```yaml
conditions:
  - skin_type: oily # Matches if user.skin_type == "oily"
  - hair_type: curly # Matches if user.hair_type == "curly"
```

### Multiple Options (OR Logic)

```yaml
conditions:
  - skin_type: [oily, combination] # Matches if either oily OR combination
  - hair_type: [curly, wavy]
```

### Contains Condition (ALL Must Be Present)

```yaml
conditions:
  - conditions_contains: [acne, blackheads] # Matches if user has BOTH acne AND blackheads
```

### Range Condition

```yaml
conditions:
  - age_range: [18, 65] # Matches if 18 <= user.age <= 65
```

### Multiple Conditions (AND Logic)

```yaml
conditions:
  - skin_type: oily # AND
  - conditions_contains: [acne] # AND
  - age_range: [15, 50]
```

ALL conditions must pass for rule to match.

## Contraindication Reference

### Supported Contraindications

```yaml
avoid_if:
  - pregnancy # Skip if user.pregnancy_status == True
  - breastfeeding # Skip if user.breastfeeding_status == True
  - very_sensitive # Skip if user.skin_sensitivity == "very_sensitive"
  - active_infection # Skip if user.active_infection == True
  - allergies # Skip if user allergies overlap with rule ingredients
  - none # No contraindications
```

### Example: Rule Contraindicated by Pregnancy

```yaml
- id: r004
  name: "Retinol Anti-Aging"
  avoid_if:
    - pregnancy # Retinol not safe during pregnancy
    - breastfeeding # Not safe during breastfeeding
```

User profile:

```python
profile = {"pregnancy_status": True, ...}
```

Result: Rule r004 will NOT be applied.

## Escalation Levels

Escalation severity (highest to lowest):

1. **emergency** - Immediate 911 or ER referral
2. **urgent** - See dermatologist immediately
3. **caution** - Recommend professional consultation
4. **warning** - Note for awareness
5. **none** - No escalation needed

### Escalation Examples

**Urgent (r008 - Severe Acne):**

```yaml
escalation: "URGENT - See dermatologist immediately. Likely requires prescription..."
```

→ Engine extracts as `level: "urgent"`

**Caution (r002 - Eczema):**

```yaml
escalation: "If rash worsens, consult dermatologist"
```

→ Engine extracts as `level: "caution"`

**None:**

```yaml
escalation: none
```

→ Engine sets `level: "none"` (no escalation returned)

## Testing

Run engine tests:

```bash
# Test specific test class
pytest backend/app/recommender/test_engine.py::TestRuleEngineInitialization -v

# Run all engine tests
pytest backend/app/recommender/test_engine.py -v

# Run with coverage
pytest backend/app/recommender/test_engine.py --cov=backend.app.recommender.engine
```

## Performance Considerations

### Rule Matching Speed

- Typically **< 50ms** for full rule evaluation (9 rules)
- Linear with number of rules
- Constant time per condition check

### Memory Usage

- Rules YAML loaded once at initialization
- ~20KB for 9 rules
- Recommendation dict ~5-10KB per user

### Optimization Tips

1. **Cache engine instance** - Initialize once, reuse for all requests
2. **Validate input early** - Fail fast on invalid data
3. **Log matched rules** - Asynchronously for analytics

## Adding New Rules

To add a new rule to the system:

1. **Edit rules.yaml** and add new rule object
2. **Assign unique ID** (r010, r011, etc.)
3. **Set priority** (1-10, where 1 is highest)
4. **Define conditions** using supported syntax
5. **Add actions** (products, routines, diet, warnings)
6. **Specify escalation** (urgent, caution, warning, none)
7. **Mark contraindications** in avoid_if
8. **Test with test_engine.py**

Example:

```yaml
- id: r010
  name: "New Condition - Specific Recommendation"
  description: "..."
  priority: 4
  conditions:
    - skin_type: oily
    - conditions_contains: [acne]
  actions:
    recommend_products_external_ids: [...]
    recommend_products_tags: [...]
    routine: { ... }
    diet_recommendations: { ... }
    warnings: [...]
  escalation: none
  avoid_if: [pregnancy]
```

## Debugging

### Enable Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("backend.app.recommender.engine")

# Now engine logs condition matches, rule applications, etc.
engine = RuleEngine()
recommendation, rules = engine.apply_rules(analysis, profile)
```

**Sample output:**

```
INFO:Loaded 9 rules from /path/to/rules.yaml
INFO:Rule r001 matched
INFO:Rule r007 matched
INFO:Applied 2 rules: ['r001', 'r007']
```

### Inspect Rules

```python
engine = RuleEngine()
summaries = engine.get_rules_summary()

for summary in summaries:
    print(f"{summary['id']}: {summary['name']} (priority {summary['priority']})")
```

### Test Rule Matching

```python
engine = RuleEngine()

# Try different analysis/profile combinations
test_cases = [
    ({"skin_type": "oily", "conditions_detected": ["acne"]}, {}),
    ({"skin_type": "dry", "conditions_detected": ["eczema"]}, {}),
    ({"conditions_detected": ["severe_acne"]}, {}),
]

for analysis, profile in test_cases:
    rec, rules = engine.apply_rules(analysis, profile)
    print(f"Analysis: {analysis} → Rules: {rules}")
```

## Troubleshooting

### "Rules file not found"

**Solution:** Verify `rules.yaml` exists in `backend/app/recommender/`

```python
from pathlib import Path
p = Path(__file__).parent / "rules.yaml"
print(f"Expected path: {p}")
print(f"Exists: {p.exists()}")
```

### "Failed to parse YAML"

**Solution:** Check YAML syntax (indentation, colons, etc.)

```bash
# Validate YAML
python -m yaml backend/app/recommender/rules.yaml
```

### "No rules matched"

**Solution:** Verify conditions are correctly formatted

```python
engine = RuleEngine()
rule = engine.rules[0]  # Get first rule
print(f"Rule conditions: {rule['conditions']}")

# Try to match manually
result = engine._matches_conditions(rule, analysis, profile)
print(f"Matches: {result}")
```

## Next Steps

1. ✅ Engine.py created and tested
2. → Create API endpoint integration (api/v1/recommender.py)
3. → Add database logging for analytics
4. → Implement user feedback loop
5. → Add ML optimization phase
