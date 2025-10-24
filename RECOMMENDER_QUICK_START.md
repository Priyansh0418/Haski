# Recommender System Implementation Guide

## Quick Reference

### What It Does
- Maps analysis results (skin type, conditions) → personalized recommendations
- Provides skincare routines, diet tips, product suggestions
- Tracks user feedback for continuous improvement
- Escalates severe conditions to dermatologists

### MVP Architecture
- **Rule-based** (not ML-based yet)
- **YAML rules** for each condition
- **Database products** with safety tags
- **Feedback logging** for future ML

---

## Key Files Created

| File | Purpose |
|------|---------|
| `RECOMMENDER_DESIGN.md` | Full system design & architecture |
| `backend/app/recommender/rules.yml` | Recommendation rules (created next) |
| `backend/app/recommender/engine.py` | Core recommendation engine |
| `backend/app/recommender/safety.py` | Safety checks & escalation |
| `backend/app/api/v1/recommender.py` | API endpoints |

---

## Workflow: Analysis → Recommendations

```
1. User Analysis
   └─ skin_type: "dry"
   └─ conditions: ["acne", "blackheads"]
   └─ hair_type: "coily"

2. Load Rules & Profile
   └─ rules[acne] → skincare steps
   └─ rules[dry] → hydration routine
   └─ user.budget → filter expensive products

3. Generate Recommendations
   └─ 4-step skincare routine
   └─ 5 diet tips
   └─ 4 product suggestions

4. Add Safety Checks
   └─ Warnings: salicylic acid + moisturizer
   └─ No escalation needed (mild case)
   └─ Professional help not required

5. Return to User
   └─ Display routine + products
   └─ Enable feedback collection

6. Learn from Feedback
   └─ User rates: helpful? product satisfaction?
   └─ Store in recommendation_feedback table
   └─ Use for future ML ranking
```

---

## Three Key Endpoints

### 1. Generate Recommendations
```
POST /api/v1/recommender/recommend
Input: {analysis_id: 5} OR {analysis: {...}, profile: {...}}
Output: {routine, diet_tips, products, safety_flags}
Time: ~500ms
```

### 2. Submit Feedback
```
POST /api/v1/recommender/feedback
Input: {recommendation_id, helpful_rating, product_satisfaction, routine_completion_pct}
Output: {feedback_id, status}
Time: ~100ms
```

### 3. Get History
```
GET /api/v1/recommender/history
Input: {user_id, limit: 10}
Output: [past_recommendations with feedback]
Time: ~200ms
```

---

## Safety Guarantees

### ✅ SAFE (Recommended)
- OTC skincare: BHA, AHA, retinol, niacinamide
- Natural ingredients: tea tree oil, aloe (with disclaimers)
- Lifestyle: diet, sleep, hydration, stress
- Professional: dermatologist referral

### ❌ NOT SAFE (Never Recommend)
- Prescription meds: Accutane, tretinoin, antibiotics
- Steroids: topical, oral
- Medical procedures
- Anything requiring prescription

### 🚨 ESCALATION (Flag for Professional)
- Severe acne → dermatologist
- Skin infections → doctor immediately
- Allergic reactions → ER if severe
- Unknown conditions → professional assessment

---

## Database Tables

### products
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    category VARCHAR(50),        -- cleanser, treatment, moisturizer
    brand VARCHAR(100),
    price_usd DECIMAL(10, 2),
    url VARCHAR(500),
    
    ingredients TEXT,            -- JSON array
    safe_tags TEXT,              -- ["acne", "dry", "sensitive"]
    avoid_tags TEXT,             -- ["pregnancy", "breastfeeding"]
    
    avg_rating FLOAT,
    review_count INT,
    
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### recommendation_feedback
```sql
CREATE TABLE recommendation_feedback (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    analysis_id INT NOT NULL,
    recommendation_id VARCHAR(100),
    
    helpful_rating INT,          -- 1-5
    product_satisfaction INT,    -- 1-5
    routine_completion_pct INT,  -- 0-100
    feedback_text TEXT,
    
    created_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (analysis_id) REFERENCES analysis(id)
);
```

---

## Example: Acne Recommendation

### Input
```json
{
  "skin_type": "dry",
  "conditions": ["acne", "blackheads"],
  "confidence": 0.87,
  "user_budget": "medium",
  "user_allergies": ["sulfates"]
}
```

### Processing
1. Look up `rules[acne]` → 4-step routine
2. Look up `rules[dry]` → additional hydration
3. Merge routines (prioritize acne)
4. Find products:
   - Clean with gentle cleanser (no sulfates)
   - Treat with salicylic acid
   - Moisturize (for dry skin)
   - Protect with SPF
5. Check budget → filter <$50 total
6. Check allergies → remove sulfates
7. Check safety → warn about dryness

### Output
```json
{
  "routine": [
    {
      "step": 1,
      "action": "Gentle cleanser",
      "frequency": "2x daily",
      "reason": "Removes excess oil without stripping"
    },
    {
      "step": 2,
      "action": "Salicylic acid 2%",
      "frequency": "1x nightly",
      "reason": "Unclogs pores, reduces acne"
    },
    {
      "step": 3,
      "action": "Rich moisturizer",
      "frequency": "2x daily",
      "reason": "Restores hydration (dry skin)"
    },
    {
      "step": 4,
      "action": "SPF 30+",
      "frequency": "Daily AM",
      "reason": "Prevents post-inflammatory hyperpigmentation"
    }
  ],
  
  "products": {
    "cleanser": {"name": "CeraVe", "price": 8.99},
    "treatment": {"name": "The Ordinary SA 2%", "price": 5.90},
    "moisturizer": {"name": "Vanicream", "price": 7.99},
    "sunscreen": {"name": "La Roche-Posay", "price": 34.00}
  },
  
  "diet_tips": [
    "Increase water: 2-3L daily",
    "Reduce dairy: linked to acne",
    "Add omega-3s: salmon, walnuts",
    "Avoid high-glycemic: white bread, sugar"
  ],
  
  "safety": {
    "severe": false,
    "escalation": null,
    "warnings": [
      "Salicylic acid may cause initial dryness - use moisturizer"
    ]
  }
}
```

---

## Implementation Checklist

- [ ] Create `backend/app/recommender/` directory
- [ ] Write `engine.py` (RecommendationEngine class)
- [ ] Write `safety.py` (SafetyChecker class)
- [ ] Write `products.py` (database queries)
- [ ] Write `schemas.py` (Pydantic models)
- [ ] Create `rules.yml` (recommendation rules)
- [ ] Add SQLAlchemy models (Product, Feedback)
- [ ] Create API endpoints in `api/v1/recommender.py`
- [ ] Test with `test_recommender.py`
- [ ] Integration with `/api/v1/analyze/photo` endpoint
- [ ] Load sample products to database
- [ ] Frontend integration to display recommendations
- [ ] User feedback form in frontend
- [ ] Analytics dashboard

---

## What's Next?

1. **Write engine.py** → Core recommendation logic
2. **Create rules.yml** → Condition-based rules
3. **Add API endpoints** → FastAPI integration
4. **Test thoroughly** → Unit + integration tests
5. **Frontend UI** → Display recommendations
6. **Collect feedback** → Record user ratings
7. **Analyze trends** → Improve recommendations
8. **Deploy MVP** → Launch to users
9. **ML optimization** → Use feedback data for ranking
10. **Iterate** → Continuous improvement

---

## Files to Create

**Next Priority:**
```
backend/app/recommender/
├── __init__.py
├── engine.py                # ← Start here
├── safety.py
├── products.py
├── schemas.py
├── models.py
├── rules.yml
└── load_products.py         # Script to populate DB
```

**API Integration:**
```
backend/app/api/v1/
└── recommender.py          # ← Then here
```

**Testing:**
```
tests/
└── test_recommender.py
```

---

## Success = Recommendations Users Actually Use

✅ Helpful recommendations (4+/5 rating)
✅ Products users are satisfied with (4+/5)
✅ Users following 60%+ of the routine
✅ Users returning for more recommendations
✅ Zero safety incidents
✅ All severe cases escalated properly

---

**Status**: 🎯 Design locked, ready for implementation
