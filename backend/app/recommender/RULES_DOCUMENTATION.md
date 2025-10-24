# Recommender Rules System Documentation

## Overview

The recommender rules system is a YAML-based configuration that matches user skin/hair conditions to personalized skincare and haircare recommendations. Each rule combines:

- **Condition Matching**: Triggers based on skin type, conditions detected, and sensitivity level
- **Product Recommendations**: Specific products from the database or by product tags
- **Routine Guidance**: Step-by-step morning/evening routines and special treatments
- **Dietary Advice**: Foods to increase/limit for skin and hair health
- **Safety Warnings**: Important cautions about product interactions and side effects
- **Medical Escalation**: Flags for when professional dermatologist consultation is needed

## File Location

```
backend/app/recommender/rules.yaml
```

## Rule Schema

Each rule follows this structure:

```yaml
- id: r001                          # Unique rule identifier
  name: "Rule Name"                 # Human-readable name
  description: "What triggers this" # Trigger description
  priority: 1                       # Execution order (1=highest)
  conditions:
    - skin_type: oily               # OR: [oily, combination]
    - conditions_contains:          # Must match all items
        - acne
        - blackheads
    - skin_sensitivity: sensitive   # Optional
    - hair_type: curly              # Optional (for hair rules)
  actions:
    recommend_products_external_ids:  # Specific products
      - cerave_cleanser_001
    recommend_products_tags:          # Product tag filters
      - exfoliating
      - oil-control
    routine:
      - morning: "Step-by-step morning routine"
      - evening: "Step-by-step evening routine"
      - weekly: "Special treatments"
    diet_recommendations:
      - increase:
          - "food or nutrient"
      - limit:
          - "food to avoid"
    warnings:
      - "Important safety warning"
  escalation: "Medical escalation trigger or 'none'"
  avoid_if:                         # Contraindications
    - pregnancy
    - very_sensitive
```

## Rules Included

### Rule 1: Oily Skin + Acne (r001)
**Trigger**: Oily skin type + acne/blackheads/congestion  
**Products**: Salicylic acid, Niacinamide, Non-comedogenic sunscreen  
**Focus**: Oil control, pore cleansing, exfoliation  
**Escalation**: None (OTC management)  
**Cautions**: Pregnancy (salicylic acid risks)

**Key Points**:
- Exfoliate 2-3x per week with salicylic acid (BHA)
- Layer niacinamide for oil control and anti-inflammatory benefits
- SPF 60+ non-comedogenic sunscreen mandatory
- Results visible in 4-6 weeks

---

### Rule 2: Dry Skin + Eczema (r002)
**Trigger**: Dry/very dry skin + eczema/dermatitis/dry patches  
**Products**: Hydrating cleanser, Rich moisturizer, Hydrating toner, Sheet mask  
**Focus**: Barrier repair, deep hydration, soothing  
**Escalation**: If rash worsens → dermatologist  
**Cautions**: None (all products hypoallergenic)

**Key Points**:
- Use ONLY lukewarm/cool water (hot water damages barrier)
- Pat dry gently, apply moisturizer to damp skin
- Deep hydrate 2-3x per week with sheet masks
- All products fragrance-free, hypoallergenic

---

### Rule 3: Sensitive Skin + Rosacea (r003)
**Trigger**: Sensitive skin + rosacea/flushing/facial redness  
**Products**: Gentle cleanser, Niacinamide, Rich moisturizer, SPF 60+  
**Focus**: Calming, anti-inflammatory, barrier support  
**Escalation**: If worsens or affects eyes → dermatologist  
**Cautions**: None (all gentle)

**Key Points**:
- Niacinamide is anti-inflammatory and critical
- SPF 60+ MANDATORY daily (UV triggers flare-ups)
- Avoid ALL exfoliants (physical + chemical)
- Identify and avoid personal triggers (spicy food, heat, alcohol)

---

### Rule 4: Combination Skin + Anti-Aging (r004)
**Trigger**: Combination skin + fine lines/wrinkles/age spots  
**Products**: Hydrating cleanser, Retinol 0.2%, Hydrating toner, SPF 60+  
**Focus**: Anti-aging, hydration, collagen support  
**Escalation**: None  
**Cautions**: CONTRAINDICATED in pregnancy/breastfeeding

**Key Points**:
- Retinol 0.2% is beginner-friendly concentration
- Start 1-2x per week, expect retinization (dryness 1-2 weeks)
- SPF 60+ MANDATORY (retinol increases sun sensitivity)
- Do NOT combine with vitamin C or AHAs on same night

---

### Rule 5: Dry Curly Hair (r005)
**Trigger**: Curly hair + dry/damaged hair/frizz  
**Products**: Sulfate-free hydrating shampoo  
**Focus**: Deep moisturization, curl definition, damage prevention  
**Escalation**: None  
**Cautions**: None

**Key Points**:
- Use sulfate-free products ONLY (sulfates strip natural oils)
- Reduce wash frequency to 1-2x per week
- Co-wash (conditioner-only wash) on non-wash days
- Deep condition 2x per month

---

### Rule 6: Dehydrated Oily Skin (r006)
**Trigger**: Oily skin + dehydration/tight feeling/oily T-zone  
**Products**: Hydrating toner, Niacinamide, Light gel moisturizer  
**Focus**: Hydration without heaviness, oil control  
**Escalation**: None  
**Cautions**: None

**Key Points**:
- Dehydration ≠ Dryness (oily skin can be dehydrated)
- Layer lightweight hydrating products (toner, essences)
- Increase water intake 2-3L daily
- Use gel moisturizer not heavy cream

---

### Rule 7: Blackheads & Enlarged Pores (r007)
**Trigger**: Blackheads/enlarged pores/sebaceous filaments  
**Products**: Salicylic acid 2%, Niacinamide serum  
**Focus**: Deep cleansing, pore appearance minimization  
**Escalation**: None  
**Cautions**: Pregnancy (salicylic acid risks)

**Key Points**:
- Blackheads take 6-8 weeks to improve (consistency key)
- Never squeeze or pick (scarring risk)
- Pores can't be permanently shrunk but appear minimized
- Initial breakout possible (1-2 weeks) as pores purge

---

### Rule 8: Severe Acne/Infection (r008) ⚠️ **ESCALATION RULE**
**Trigger**: Severe acne, cystic acne, signs of infection  
**Products**: None (OTC insufficient)  
**Focus**: MEDICAL ESCALATION  
**Escalation**: **URGENT - See dermatologist immediately**  
**Cautions**: All

**Key Points**:
- ⚠️ Do NOT attempt self-treatment
- ⚠️ Risk of permanent scarring if untreated
- ⚠️ Likely needs prescription oral antibiotics or isotretinoin
- Temporarily use only gentle cleanser + moisturizer until consultation

---

### Rule 9: Post-Treatment Sensitivity (r009)
**Trigger**: Post-professional treatment (laser, peel, microneedling)  
**Products**: Gentle cleanser, Barrier repair cream, SPF 60+  
**Focus**: Recovery, barrier repair, sun protection  
**Escalation**: If severe blistering/swelling/infection → dermatologist  
**Cautions**: None (all gentle)

**Key Points**:
- SPF 60+ MANDATORY for 4 weeks post-treatment
- NO active ingredients (retinol, AHA/BHA) for 2 weeks minimum
- Minimal routine: cleanser → moisturizer → SPF only
- Some redness/flaking normal - do NOT strip skin

---

## Engine Integration

The recommender engine will:

1. **Parse YAML** rules from `rules.yaml`
2. **Match conditions**: Compare user analysis data against rule conditions
3. **Filter by priority**: Execute highest priority matching rules first
4. **Check contraindications**: Verify avoid_if conditions
5. **Build recommendation**: Compile products + routine + warnings
6. **Apply escalation**: Flag for medical referral if needed
7. **Log execution**: Record which rules were applied in RuleLog table

## Condition Matching Logic

### Skin Type Conditions
```yaml
skin_type:
  - oily          # Excess sebum, shiny appearance
  - dry           # Tight feeling, flaky
  - combination   # Oily T-zone, dry cheeks
  - sensitive     # Easily irritated, reactive
  - normal        # Balanced, minimal concerns
```

### Condition Detection
```yaml
conditions_contains:  # All listed must be detected
  - acne            # Pimples, clogged pores
  - blackheads      # Open comedones
  - rosacea         # Facial redness, flushing
  - eczema          # Patches, itching, scaling
  - fine_lines      # Wrinkles, age-related
  - hyperpigmentation # Dark spots, uneven tone
  - dehydration     # Tight, dull, needs hydration
  - infection       # Pustules, spreading, warmth
```

### Hair Types
```yaml
hair_type:
  - straight
  - wavy
  - curly
  - coily

hair_condition:
  - dry_hair
  - oily_hair
  - damaged_hair
  - frizz
  - color_treated
```

## Product Recommendation Methods

### Method 1: Specific External IDs
```yaml
recommend_products_external_ids:
  - cerave_cleanser_001
  - ordinary_sa_001
```
Direct product recommendation by database ID.

### Method 2: Tag-Based Filtering
```yaml
recommend_products_tags:
  - exfoliating
  - oil-control
  - pore-cleansing
```
Search for products with these tags from database.

### Method 3: Both (Recommended)
Combine both for specificity + flexibility:
```yaml
recommend_products_external_ids:
  - ordinary_sa_001  # Specific trusted product
recommend_products_tags:
  - barrier-repair   # Additional complementary products
```

## Escalation Levels

| Level | Trigger | Action |
|-------|---------|--------|
| `none` | No escalation | Continue with OTC recommendations |
| `warning` | Minor concern | Include warning in response |
| `caution` | Moderate concern | Suggest professional consultation |
| `urgent` | Severe issue | Direct to dermatologist immediately |
| `emergency` | Medical emergency | Call 911 or emergency services |

## Contraindications (avoid_if)

Conditions that prevent rule application:

```yaml
avoid_if:
  - pregnancy           # Retinol, salicylic acid risks
  - breastfeeding       # Medication transfer to infant
  - very_sensitive      # Too strong for ultra-sensitive skin
  - active_infection    # Need antibiotics first
  - open_wounds         # Risk of irritation/infection
```

## Dietary Recommendations Structure

Each rule includes food guidance:

```yaml
diet_recommendations:
  - increase:
      - "omega-3 fatty acids (salmon, walnuts)"
      - "zinc-rich foods (oysters, pumpkin seeds)"
  - limit:
      - "dairy products"
      - "high-glycemic foods"
```

These target internal health to support skin/hair.

## Routine Format

Routines are ordered by time and frequency:

```yaml
routine:
  - morning: "Cleanser → Toner → Serum → Moisturizer → SPF"
  - evening: "Cleanser → Toner → Active Treatment → Moisturizer"
  - weekly: "Exfoliating mask 2-3x per week"
  - intensive: "Deep treatment 1x per week"
```

## Safety Warnings

Each rule includes critical safety information:

- **Contraindications**: When NOT to use
- **Starting protocol**: How to introduce (gradual or immediate)
- **Expected timeline**: When to expect results
- **Possible side effects**: What's normal vs concerning
- **Interaction warnings**: What NOT to combine
- **Sun sensitivity**: SPF requirements

## Priority Ordering

Lower `priority` number = higher execution priority:

```yaml
priority: 0   # HIGHEST - Medical escalations
priority: 1   # HIGH - Severe conditions (severe acne, eczema)
priority: 2   # MEDIUM - Common conditions (oily+acne, sensitive+rosacea)
priority: 3   # LOWER - Combination/maintenance (anti-aging, pore minimization)
```

Multiple rules can apply - all matching rules are executed in priority order.

## Example: Full Rule Execution

**User Input:**
```json
{
  "skin_type": "oily",
  "conditions_detected": ["acne", "blackheads"],
  "skin_sensitivity": "normal",
  "budget": "medium"
}
```

**Matching Rules:**
1. r001 (Oily Skin + Acne) - MATCH ✓
2. r007 (Blackheads & Pores) - MATCH ✓

**Engine Output:**
```json
{
  "rules_applied": ["r001", "r007"],
  "products": [
    "ordinary_sa_001",
    "ordinary_niacinamide_001",
    "lrp_sunscreen_001"
  ],
  "routine": {
    "morning": "Gentle exfoliating cleanser → Niacinamide serum → Non-comedogenic sunscreen SPF 60",
    "evening": "Gentle exfoliating cleanser → Salicylic acid 2% (2-3x per week) → Light moisturizer",
    "weekly": "Clay mask or BHA to manage pore congestion"
  },
  "warnings": [
    "Salicylic acid may cause initial dryness - start 1x per week",
    "Blackheads take 6-8 weeks to improve - consistency is key"
  ],
  "escalation": null
}
```

## Updating Rules

To add or modify rules:

1. **Edit `rules.yaml`** with new/updated rule
2. **Test with engine.py** to verify YAML parsing
3. **Run integration tests** with sample user data
4. **Commit and push** to GitHub

Rules are hot-reloaded on each API call (no restart needed).

## Notes

- **All rules are dermatologically vetted** - based on established guidelines
- **Product recommendations are prioritized** by rating and review count
- **Warnings are non-blocking** - user sees them but continues
- **Escalations are blocking** - user directed to professional
- **Rules can overlap** - multiple matching rules are combined
- **Priority ensures** medical escalations are always checked first
