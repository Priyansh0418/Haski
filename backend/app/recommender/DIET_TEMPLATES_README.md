# Diet Templates Documentation

## Overview

The `diet_templates.yml` file provides comprehensive mappings of skin conditions, hair issues, and nutritional deficiencies to food recommendations. This is used by the recommendation engine to suggest dietary changes that complement skincare/haircare routines.

**File Location:** `backend/app/recommender/diet_templates.yml`

**Format:** YAML with structured food suggestions and metadata

---

## Structure

Each diet template entry contains:

```yaml
- key: condition_name
  foods: [list of recommended foods]
  description: [explanation of benefits]
  deficiency_type: [what nutrient deficiency is addressed]
  benefits:
    - [benefit 1]
    - [benefit 2]
    - ...
```

### Fields

| Field | Type | Purpose |
|-------|------|---------|
| `key` | string | Unique identifier for the condition (e.g., "acne", "hair_loss") |
| `foods` | array | List of recommended foods with explanations |
| `description` | string | Why these foods help for this condition |
| `deficiency_type` | string | Nutrient deficiencies addressed |
| `benefits` | array | Expected benefits from following recommendations |

---

## Categories

### 1. Acne & Breakouts (4 entries)

**Keys:**
- `acne` - General acne treatment
- `oily_skin` - Sebum regulation
- `combination_skin` - Balanced nutrition
- (Plus many more...)

**Example Foods:**
- Leafy greens (spinach, kale)
- Berries (blueberries, raspberries)
- Omega-3 rich fish (salmon, sardines)
- Probiotics (yogurt, kefir)

**Key Nutrients:** Omega-3, zinc, vitamin A

---

### 2. Dry Skin & Dehydration (3 entries)

**Keys:**
- `dry_skin` - Comprehensive hydration
- `dehydration` - Fluid and electrolyte restoration
- `sensitive_skin` - Anti-inflammatory protection

**Example Foods:**
- Avocado
- Nuts and seeds
- Sweet potato
- Water-rich fruits

**Key Nutrients:** Omega-3, vitamin E, vitamin A

---

### 3. Aging & Wrinkles (3 entries)

**Keys:**
- `aging_skin` - General anti-aging
- `wrinkles` - Collagen support
- `fine_lines` - Fine line reduction

**Example Foods:**
- Berries (high in antioxidants)
- Leafy greens
- Fatty fish (omega-3)
- Red grapes

**Key Nutrients:** Antioxidants, vitamin C, omega-3

---

### 4. Dark Circles & Puffiness (2 entries)

**Keys:**
- `dark_circles` - Blood circulation and tone
- `puffy_eyes` - Fluid retention reduction

**Example Foods:**
- Iron-rich foods (spinach, red meat)
- Potassium sources (banana, coconut water)
- Anti-inflammatory (ginger, turmeric)

**Key Nutrients:** Iron, vitamin C, potassium

---

### 5. Pigmentation (2 entries)

**Keys:**
- `hyperpigmentation` - Melanin regulation
- `dark_spots` - Spot fading

**Example Foods:**
- Vitamin C rich foods
- Leafy greens
- Turmeric
- Green tea

**Key Nutrients:** Vitamin C, polyphenols

---

### 6. Hair Health (6 entries)

**Keys:**
- `hair_loss` - Hair follicle strengthening
- `dry_hair` - Hair hydration
- `oily_scalp` - Sebum regulation
- `dandruff` - Scalp health
- `brittle_hair` - Hair strengthening
- `hair_thinning` - Hair density

**Example Foods:**
- Eggs (biotin, protein)
- Spinach (iron)
- Fatty fish (omega-3)
- Nuts and seeds

**Key Nutrients:** Biotin, iron, zinc, protein, B vitamins

---

### 7. General Skin Health (3 entries)

**Keys:**
- `dull_skin` - Radiance restoration
- `uneven_skin_tone` - Tone evening
- `congested_skin` - Detoxification
- `inflamed_skin` - Inflammation reduction

**Example Foods:**
- Berries
- Leafy greens
- Green tea
- Turmeric

**Key Nutrients:** Antioxidants, vitamin C, omega-3

---

### 8. Deficiency-Based (9 entries)

**Keys:**
- `vitamin_a_deficiency`
- `vitamin_c_deficiency`
- `vitamin_d_deficiency`
- `vitamin_e_deficiency`
- `iron_deficiency`
- `zinc_deficiency`
- `biotin_deficiency`
- `omega_3_deficiency`
- `collagen_deficiency`

**Purpose:** Direct nutrition supplementation for identified deficiencies

---

### 9. Lifestyle & Hydration (2 entries)

**Keys:**
- `poor_hydration` - Hydration restoration
- `general_wellness` - Balanced nutrition

**Purpose:** Foundational nutrition for overall health

---

## Total Entries

**30+ Diet Templates** covering:

- ✅ Acne and breakouts
- ✅ Skin hydration and dryness
- ✅ Aging and wrinkles
- ✅ Dark circles and puffiness
- ✅ Pigmentation issues
- ✅ Hair health and growth
- ✅ Specific nutrient deficiencies
- ✅ General wellness

---

## Usage Examples

### In Recommendation Engine

```python
from backend.app.recommender.engine import RuleEngine

engine = RuleEngine()
diet_recommendations = engine.get_diet_recommendations(user_analysis)
```

### Expected Integration

1. **Analyze User Profile**
   - Identify conditions (acne, dry skin, hair loss, etc.)
   - Detect nutrient deficiencies

2. **Match with Diet Templates**
   - Find corresponding keys in `diet_templates.yml`
   - Retrieve food suggestions

3. **Generate Recommendations**
   - Include in skincare/haircare recommendations
   - Suggest dietary changes alongside product recommendations

4. **Deliver to Frontend**
   - Display food suggestions
   - Explain benefits
   - Show expected improvements

---

## Food Categories Reference

### Proteins
- Eggs, chicken, turkey, fish, beef, legumes, yogurt, Greek yogurt

### Healthy Fats
- Avocado, olive oil, nuts, seeds, fatty fish, coconut

### Vegetables
- Leafy greens (spinach, kale), bell peppers, carrots, sweet potato, broccoli, tomatoes, cucumber

### Fruits
- Berries, citrus fruits, watermelon, oranges, kiwi, pomegranate

### Other
- Whole grains, legumes, probiotics, green tea, water, herbal teas

---

## Nutrient Deficiency Mapping

| Deficiency | Foods | Benefits |
|------------|-------|----------|
| **Vitamin A** | Sweet potato, carrots, spinach | Cell renewal, eye health |
| **Vitamin C** | Citrus, kiwi, berries, peppers | Collagen, brightness |
| **Vitamin D** | Fatty fish, eggs, mushrooms | Immune function, skin health |
| **Vitamin E** | Almonds, seeds, spinach | Skin protection, antioxidant |
| **Iron** | Red meat, spinach, lentils | Blood circulation, complexion |
| **Zinc** | Oysters, beef, seeds, chocolate | Immune function, acne healing |
| **Biotin** | Eggs, almonds, sweet potato | Hair, skin, nails |
| **Omega-3** | Salmon, walnuts, flax seeds | Anti-inflammation, hydration |

---

## Common Food Recommendations

### Most Recommended Foods
1. **Leafy Greens** - 18+ conditions
2. **Berries** - 16+ conditions
3. **Fatty Fish** - 14+ conditions
4. **Nuts & Seeds** - 13+ conditions
5. **Avocado** - 8+ conditions

### Superfood Combinations
- **Anti-acne:** Berries + fish + greens + probiotics
- **Anti-aging:** Berries + nuts + citrus + greens
- **Hair growth:** Eggs + spinach + fish + seeds
- **General wellness:** Varied vegetables + proteins + whole grains

---

## Integration with Other Systems

### Recommender Engine
- Uses diet templates to suggest dietary changes
- Combines with product recommendations
- Provides holistic skincare routine

### Analysis System
- Identifies nutritional deficiencies
- Recommends food sources
- Tracks dietary improvements

### Feedback System
- Collects user feedback on diet recommendations
- Measures dietary compliance
- Assesses improvement from dietary changes

---

## Future Enhancements

### Possible Additions
- [ ] Meal plans based on diet templates
- [ ] Weekly food shopping lists
- [ ] Preparation instructions for foods
- [ ] Calorie and macro information
- [ ] Budget-friendly alternatives
- [ ] Seasonal food suggestions
- [ ] Cultural food variations
- [ ] Allergies and intolerances
- [ ] Recipe recommendations
- [ ] Restaurant menu suggestions

### Dietary Restrictions
- Vegan/vegetarian alternatives
- Gluten-free options
- Dairy-free options
- Nut allergies
- Shellfish alternatives

---

## Loading Diet Templates

### In Python Code

```python
import yaml

def load_diet_templates():
    """Load diet templates from YAML file"""
    with open('backend/app/recommender/diet_templates.yml', 'r') as f:
        templates = yaml.safe_load(f)
    return {item['key']: item for item in templates}

# Usage
diet_map = load_diet_templates()
acne_foods = diet_map['acne']['foods']
```

### Expected Output Format

```python
{
    'acne': {
        'key': 'acne',
        'foods': ['leafy greens (spinach, kale)', 'berries (blueberries, raspberries)', ...],
        'description': 'Anti-inflammatory foods...',
        'deficiency_type': 'omega-3, zinc, vitamin A',
        'benefits': ['Reduces inflammation', 'Lowers sebum production', ...]
    },
    'dry_skin': { ... },
    ...
}
```

---

## Best Practices

### When Using Diet Templates

1. **Combine Multiple Recommendations**
   - User with acne: Use `acne` + `omega_3_deficiency` + `zinc_deficiency`
   - User with hair loss: Use `hair_loss` + `iron_deficiency` + `biotin_deficiency`

2. **Prioritize Affordable Options**
   - Suggest common foods first
   - Provide budget alternatives
   - Note seasonal availability

3. **Consider Allergies/Restrictions**
   - Check user profile for restrictions
   - Suggest alternatives
   - Avoid problematic foods

4. **Gradual Implementation**
   - Don't suggest all foods at once
   - Prioritize 5-7 key foods
   - Build habit gradually

5. **Track Improvements**
   - Monitor user adherence
   - Collect feedback on effectiveness
   - Adjust recommendations as needed

---

## Troubleshooting

### Food Not In Templates
- Check for similar conditions
- Use generic wellness recommendations
- Consider deficiency-based templates

### Conflicting Recommendations
- Prioritize most specific condition
- Combine complementary foods
- Focus on most impactful nutrients

### User Not Seeing Results
- Ensure consistency
- Check for 4-6 week timeline
- Combine with skincare routine
- Monitor other factors

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-01 | Initial release with 30+ templates |

---

## Support

For questions or additions:
1. Check condition mapping in templates
2. Review food categories
3. Consult nutrient deficiency section
4. Review integration examples

---

**Status:** Ready for integration into recommendation engine
