# Recommender Rules - Quick Reference

## Rule Lookup Table

| ID | Name | Triggers | Products | Escalation |
|----|------|----------|----------|-----------|
| **r001** | Oily Skin + Acne | oily + acne/blackheads | Salicylic acid, Niacinamide, SPF | None |
| **r002** | Dry Skin + Eczema | dry + eczema/dermatitis | Hydrating cleanser, Cream, Toner, Mask | If worsens |
| **r003** | Sensitive + Rosacea | sensitive + rosacea/redness | Gentle cleanser, Niacinamide, Cream, SPF | If spreads/eyes |
| **r004** | Combination + Anti-Aging | combination + fine_lines/wrinkles | Hydrating cleanser, Retinol, Toner, SPF | None |
| **r005** | Curly + Dry Hair | curly + dry_hair/damaged | Sulfate-free shampoo | None |
| **r006** | Dehydrated Oily | oily + dehydration | Toner, Niacinamide, Gel moisturizer | None |
| **r007** | Blackheads + Pores | blackheads/enlarged_pores | Salicylic acid, Niacinamide | None |
| **r008** | Severe Acne ⚠️ | severe_acne/cystic/infection | NONE - Escalate | **URGENT DERMATOLOGIST** |
| **r009** | Post-Treatment | post_treatment/barrier_damaged | Gentle cleanser, Cream, SPF | If severe swelling/infection |

## Condition Matching Reference

### Skin Types Supported
- `oily` - Excess sebum, shiny
- `dry` - Tight feeling, flaky
- `combination` - Oily T-zone, dry cheeks
- `sensitive` - Easily irritated
- `normal` - Balanced

### Conditions Detected
```
Acne-Related:
  - acne, blackheads, acne_prone, acne_scars, congestion

Sensitivity/Inflammation:
  - sensitive, rosacea, flushing, facial_redness, dermatitis

Dryness/Hydration:
  - dry_patches, dehydration, eczema

Aging:
  - fine_lines, wrinkles, age_spots, loss_of_elasticity

Hair-Specific:
  - frizz, breakage, color_treated, damaged_hair

Other:
  - enlarged_pores, hyperpigmentation, post_treatment
  - severe_acne, cystic_acne, infection
```

### Sensitivity Levels
- `normal` - Standard care
- `sensitive` - Gentle products, minimal actives
- `very_sensitive` - Avoids most actives, hypoallergenic only

## Product External IDs

| ID | Product | Category |
|----|---------|----------|
| `cerave_cleanser_001` | Hydrating Facial Cleanser | Cleanser |
| `ordinary_sa_001` | Salicylic Acid 2% Solution | Treatment |
| `vanicream_moisturizer_001` | Moisturizing Cream | Moisturizer |
| `lrp_sunscreen_001` | Anthelios Fluid SPF 60 | Sunscreen |
| `hadalabo_toner_001` | Hydrating Toner | Toner |
| `ordinary_niacinamide_001` | Niacinamide 10% + Zinc 1% | Serum |
| `neutrogena_cleanser_001` | Gentle Exfoliating Cleanser | Cleanser |
| `mac_mask_001` | Deep Hydrating Sheet Mask | Mask |
| `ordinary_retinol_001` | Retinol 0.2% in Squalane | Serum |
| `sheamoisture_shampoo_001` | Sulfate-Free Hydrating Shampoo | Hair Shampoo |

## Product Tags Reference

### By Category
**Cleansing**: gentle, exfoliating, hydrating, foaming  
**Treatment**: exfoliating, BHA, AHA, acne-fighting, anti-aging  
**Moisturizing**: hydrating, rich, barrier-repair, lightweight  
**Sun Protection**: broad-spectrum, mineral, non-comedogenic  
**Hair**: sulfate-free, hydrating, curly-hair-friendly, natural

### By Benefit
**Oil Control**: oil-control, pore-cleansing, pore-minimizing  
**Hydration**: hydrating, essence-like, layer-able  
**Anti-Aging**: retinol, anti-aging, brightening, collagen_support  
**Safety**: hypoallergenic, fragrance-free, dermatologist-recommended

## Common Routines

### Morning Routine (Oily/Acne)
```
Gentle Cleanser (Neutrogena) → Niacinamide Serum → Sunscreen SPF 60
```

### Morning Routine (Dry/Eczema)
```
Hydrating Cleanser (CeraVe) → Hydrating Toner → Moisturizer → SPF 30+
```

### Evening Routine (Oily/Acne)
```
Gentle Cleanser → Salicylic Acid 2% (2-3x/week) → Light Moisturizer
```

### Evening Routine (Dry/Eczema)
```
Hydrating Cleanser → Toner → Rich Moisturizer (apply to damp skin)
```

### Anti-Aging Routine
```
Morning: Cleanser → Toner → Retinol (1-2x/week) → SPF 60
Evening: Cleanser → Toner → Retinol (alternate nights) → Night Cream
```

## Key Warnings by Rule

| Rule | Critical Warning |
|------|------------------|
| r001 (Acne) | Start salicylic acid at 1x/week, increase gradually |
| r002 (Eczema) | Use lukewarm water ONLY, never hot water |
| r003 (Rosacea) | SPF 60+ MANDATORY daily - UV triggers flare-ups |
| r004 (Anti-Aging) | CONTRAINDICATED in pregnancy/breastfeeding |
| r005 (Hair) | Avoid sulfate shampoos - they strip natural oils |
| r006 (Dehydrated) | Dehydration ≠ Dryness - layer light products |
| r007 (Pores) | Never squeeze blackheads - risk of scarring |
| r008 (Severe) | ⚠️ DO NOT self-treat - see dermatologist URGENT |
| r009 (Post-Treat) | SPF 60+ MANDATORY 4 weeks, no actives 2 weeks |

## Contraindications

| Condition | Affected Rules |
|-----------|----------------|
| Pregnancy | r001, r004, r007, r008 |
| Breastfeeding | r004, r008 |
| Very Sensitive | r001, r004, r008 |
| Active Infection | r008 (escalate immediately) |
| Open Wounds | r001, r007 |

## Implementation Notes for Engine

1. **Parse YAML** on startup into rule objects
2. **Match conditions**: Check if all conditions_contains items are detected
3. **Check priority**: Execute highest priority first
4. **Verify avoid_if**: Skip rule if contraindicated
5. **Collect products**: Get external_ids + tag-based matches
6. **Build routine**: Combine all matched rules' routines
7. **Merge warnings**: Deduplicate warnings from all rules
8. **Check escalation**: If any rule has escalation, flag it
9. **Return response**: Complete recommendation or escalation notice

## Example Usage

**API Call:**
```bash
POST /api/v1/recommend
{
  "analysis_id": 123,
  "skin_type": "oily",
  "conditions_detected": ["acne", "blackheads"],
  "skin_sensitivity": "normal"
}
```

**Engine Process:**
1. Loads rules.yaml
2. Matches r001 (oily + acne) ✓
3. Matches r007 (blackheads) ✓
4. Skips all others (no match)
5. Returns products: [sa, niacinamide, spf]
6. Returns combined routine
7. Returns merged warnings
8. No escalation (returns null)

**Response:**
```json
{
  "rules_applied": ["r001", "r007"],
  "products": [...],
  "routine": {...},
  "warnings": [...],
  "escalation": null
}
```

## Adding New Rules

Template:
```yaml
- id: rXXX
  name: "Condition 1 + Condition 2"
  description: "Trigger description"
  priority: 2
  conditions:
    - skin_type: type_here
    - conditions_contains:
        - condition1
        - condition2
  actions:
    recommend_products_external_ids:
      - product_id_1
    recommend_products_tags:
      - tag1
    routine:
      - morning: "..."
      - evening: "..."
    diet_recommendations:
      - increase: ["food1", "food2"]
      - limit: ["bad1", "bad2"]
    warnings:
      - "Warning 1"
      - "Warning 2"
  escalation: "none"
  avoid_if: []
```

Then:
1. Add to `rules.yaml`
2. Test with engine.py
3. Update this quick reference
4. Commit and push

## File Locations

- **Rules**: `backend/app/recommender/rules.yaml`
- **Documentation**: `backend/app/recommender/RULES_DOCUMENTATION.md`
- **Quick Reference**: This file (you are here)
- **Seed Products**: `backend/app/recommender/seed_products.json`
- **Engine**: `backend/app/recommender/engine.py` (to be created)
