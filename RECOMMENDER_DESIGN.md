# 🎯 SkinHairAI Recommender System

## Overview

The SkinHairAI Recommender System is an intelligent engine that transforms skin/hair analysis results into **personalized skincare routines, dietary recommendations, and product suggestions**. It combines rule-based logic with machine learning-ready feedback collection for continuous improvement.

### Purpose

Map analysis data + user profile → **personalized recommendations** that are:

- ✅ **Safe** - No prescription medications, evidence-based
- ✅ **Scalable** - Rule-based MVP, ML-powered optimization later
- ✅ **Adaptive** - Learns from user feedback
- ✅ **Compliant** - Clear warnings for severe conditions

---

## 📋 System Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────┐
│ User Analysis Result                                        │
│ {skin_type: "dry", conditions: ["acne"], hair_type: "coily"} │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ User Profile Context                                        │
│ {age, gender, budget, allergies, skin_tone}               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ Rule-Based Recommendation Engine                            │
│ Load: rules.yml + product DB                               │
│ Match: skin_type, conditions, hair_type                    │
│ Filter: budget, allergies, skin_tone compatibility        │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   ┌────────┐    ┌───────────┐  ┌──────────┐
   │Skincare│    │Diet Tips  │  │Products  │
   │Routine │    │& Hydration│  │Suggestions
   └────────┘    └───────────┘  └──────────┘
        │              │              │
        └──────────────┼──────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ Response with Safety Flags                                  │
│ ✓ Routine steps, diet advice, product links                │
│ ✓ Severity escalation flags (→ dermatologist)              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ Feedback Collection                                         │
│ User rates: helpfulness, product satisfaction              │
│ Stores: recommendation_feedback table                       │
│ Used: For future ML-based ranking                           │
└─────────────────────────────────────────────────────────────┘
```

### Components

| Component            | Purpose                                       | Location                                 |
| -------------------- | --------------------------------------------- | ---------------------------------------- |
| **Rule Engine**      | Matches conditions to recommendations         | `backend/app/recommender/engine.py`      |
| **Rules Repository** | YAML/JSON rules for each condition            | `backend/app/recommender/rules.yml`      |
| **Product Database** | Products with tags, ingredients, safety flags | Database table `products`                |
| **Feedback Logger**  | Records user responses                        | Database table `recommendation_feedback` |
| **Safety Module**    | Checks severity, escalations                  | `backend/app/recommender/safety.py`      |
| **API Endpoints**    | HTTP interface                                | `backend/app/api/v1/recommender.py`      |

---

## 🏗️ Directory Structure

```
backend/app/recommender/
├── __init__.py
├── engine.py                    # Core recommendation engine
├── safety.py                    # Safety & escalation checks
├── rules.yml                    # Rule definitions (YAML)
├── products.py                  # Product queries from DB
├── README.md                    # This file
└── schemas.py                   # Pydantic schemas for I/O
```

---

## 📝 Rule-Based Engine (MVP)

### How It Works

**Step 1: Load Rules**

```python
rules = load_rules("backend/app/recommender/rules.yml")
# rules[condition] = {
#   "skincare_routine": [...],
#   "diet_tips": [...],
#   "products": {...},
#   "severity": "mild|moderate|severe",
#   "escalation": {...}
# }
```

**Step 2: Match Analysis to Rules**

```python
for condition in analysis.conditions:
    if condition in rules:
        recommendations.append(rules[condition])
```

**Step 3: Filter by User Profile**

```python
filtered = filter_by_profile(
    recommendations,
    budget=user.budget,
    allergies=user.allergies,
    skin_tone=user.skin_tone,
    age=user.age
)
```

**Step 4: Prioritize & Return**

```python
ranked = rank_recommendations(filtered)
response = format_response(ranked, safety_flags)
```

### Example Rule Structure (rules.yml)

```yaml
# backend/app/recommender/rules.yml

conditions:
  acne:
    severity: moderate
    skincare_routine:
      - step: 1
        action: "Gentle cleanser"
        frequency: "2x daily"
        duration_weeks: 4
        reason: "Removes excess sebum without irritation"
      - step: 2
        action: "Salicylic acid (0.5-2%)"
        frequency: "1x daily at night"
        duration_weeks: 4
        reason: "Chemical exfoliation, unclogs pores"
      - step: 3
        action: "Lightweight moisturizer"
        frequency: "2x daily"
        duration_weeks: 4
        reason: "Maintains barrier, prevents over-drying"
      - step: 4
        action: "SPF 30+ sunscreen"
        frequency: "Daily morning"
        duration_weeks: 0
        reason: "Prevents PIH (post-inflammatory hyperpigmentation)"

    diet_tips:
      - "Increase water intake: 2-3L daily"
      - "Reduce dairy: linked to acne in 20% of population"
      - "Limit high-glycemic foods (white bread, sugar)"
      - "Include omega-3s: salmon, flax, walnuts"
      - "Avoid excess iodine: seaweed, iodized salt"

    products:
      cleanser:
        tags: ["gentle", "acne-prone"]
        ingredients_to_avoid: ["alcohol", "fragrance"]
        recommended_ingredients: ["salicylic acid", "glycerin"]

      treatment:
        tags: ["acne-fighting", "non-comedogenic"]
        ingredients_to_avoid: ["silicone", "heavy oils"]
        recommended_ingredients: ["niacinamide", "zinc"]

      moisturizer:
        tags: ["lightweight", "oil-free"]
        ingredients_to_avoid: ["heavy oils", "lanolin"]
        recommended_ingredients: ["hyaluronic acid", "glycerin"]

    escalation:
      severe_signs: ["cystic acne", "widespread", "resistant"]
      action: "See dermatologist for isotretinoin evaluation"
      urgent: false

  dry_skin:
    severity: mild
    skincare_routine:
      - step: 1
        action: "Creamy cleanser (non-stripping)"
        frequency: "2x daily"
        duration_weeks: 0
        reason: "Preserves natural oils"
      - step: 2
        action: "Hydrating toner or essence"
        frequency: "2x daily"
        duration_weeks: 0
        reason: "Adds moisture layer before moisturizer"
      - step: 3
        action: "Rich moisturizer with ceramides"
        frequency: "2x daily"
        duration_weeks: 0
        reason: "Seals in hydration, repairs barrier"
      - step: 4
        action: "Weekly hydrating mask"
        frequency: "1x weekly"
        duration_weeks: 0
        reason: "Intensive moisture boost"

    diet_tips:
      - "Hydrate: 3-4L water daily"
      - "Include healthy fats: avocado, nuts, seeds"
      - "Increase collagen: bone broth, citrus"
      - "Add electrolytes: coconut water, mineral water"
      - "Limit caffeine: dehydrating effect"

    products:
      cleanser:
        tags: ["hydrating", "gentle"]
        ingredients_to_avoid: ["sulfates", "alcohol"]
        recommended_ingredients: ["glycerin", "hyaluronic acid"]

      moisturizer:
        tags: ["rich", "barrier-repair"]
        ingredients_to_avoid: ["fragrance", "alcohol"]
        recommended_ingredients: ["ceramides", "peptides", "hyaluronic acid"]

  blackheads:
    severity: mild
    skincare_routine:
      - step: 1
        action: "Gentle exfoliating cleanser"
        frequency: "1x daily (evening)"
        duration_weeks: 0
      - step: 2
        action: "BHA (salicylic acid) toner"
        frequency: "3-4x weekly"
        duration_weeks: 4
      - step: 3
        action: "Clay mask"
        frequency: "1x weekly"
        duration_weeks: 0

    products:
      treatment:
        tags: ["exfoliating", "pore-cleansing"]
        recommended_ingredients: ["salicylic acid", "lactic acid"]

  # Add more conditions as needed...
```

---

## 💾 Database Schema

### Products Table

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(50),  -- cleanser, moisturizer, treatment, etc.
    brand VARCHAR(100),
    price_usd DECIMAL(10, 2),
    url VARCHAR(500),

    -- Safety & Ingredients
    ingredients TEXT,  -- JSON array
    safe_tags TEXT,    -- JSON array: ["acne-prone", "sensitive", "dry", ...]
    avoid_tags TEXT,   -- JSON array: conditions to avoid for

    -- Ratings & Feedback
    avg_rating FLOAT DEFAULT 0.0,
    review_count INT DEFAULT 0,

    -- Admin
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Example rows:
-- | id | name | category | brand | price | ingredients | safe_tags | avoid_tags |
-- | 1 | Salicylic Acid Cleanser | cleanser | CeraVe | 8.99 | ["water", "salicylic acid", "glycerin"] | ["acne", "oily"] | ["sensitive"] |
-- | 2 | Gentle Hydrating Cleanser | cleanser | Vanicream | 7.99 | ["water", "glycerin"] | ["dry", "sensitive"] | [] |
```

### Recommendation Feedback Table

```sql
CREATE TABLE recommendation_feedback (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    analysis_id INT NOT NULL,
    recommendation_id VARCHAR(100),  -- ID of recommendation set

    -- Feedback
    helpful_rating INT,              -- 1-5: not helpful to very helpful
    product_satisfaction INT,        -- 1-5: not satisfied to very satisfied
    routine_completion_pct INT,      -- 0-100: % of routine they followed
    feedback_text TEXT,              -- User comments

    -- Tracking
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (analysis_id) REFERENCES analysis(id)
);
```

---

## 🔌 API Endpoints

### 1. Generate Recommendations

**Endpoint**: `POST /api/v1/recommender/recommend`

**Request** (Option A: Using Analysis ID):

```json
{
  "analysis_id": 5,
  "include_diet": true,
  "include_products": true
}
```

**Request** (Option B: Direct Analysis JSON):

```json
{
  "analysis": {
    "skin_type": "dry",
    "hair_type": "coily",
    "conditions_detected": ["acne", "blackheads"],
    "confidence_scores": {
      "dry": 0.87,
      "acne": 0.72
    }
  },
  "user_profile": {
    "age": 28,
    "gender": "F",
    "budget": "medium",
    "allergies": ["sulfates"],
    "skin_tone": "medium"
  },
  "include_diet": true,
  "include_products": true
}
```

**Response** (201 Created):

```json
{
  "recommendation_id": "rec_20251024_001",
  "analysis_id": 5,
  "user_id": 3,

  "skincare_routine": {
    "duration_weeks": 4,
    "steps": [
      {
        "step": 1,
        "action": "Gentle cleanser",
        "frequency": "2x daily",
        "reason": "Removes excess sebum without irritation",
        "expected_results": "Reduced oil production in 1 week"
      },
      {
        "step": 2,
        "action": "Salicylic acid treatment",
        "frequency": "1x nightly",
        "reason": "Chemical exfoliation",
        "expected_results": "Visible improvement in 2-3 weeks"
      },
      {
        "step": 3,
        "action": "Rich moisturizer",
        "frequency": "2x daily",
        "reason": "Maintains barrier",
        "expected_results": "Less irritation"
      },
      {
        "step": 4,
        "action": "SPF 30+ sunscreen",
        "frequency": "Daily AM",
        "reason": "UV protection",
        "expected_results": "Prevents PIH"
      }
    ]
  },

  "diet_recommendations": {
    "tips": [
      "Increase water: 2-3L daily",
      "Reduce dairy: linked to acne",
      "Include omega-3s: salmon, flax",
      "Avoid high-glycemic foods",
      "Limit iodine: seaweed, salt"
    ],
    "foods_to_add": [
      "Salmon (omega-3s)",
      "Spinach (antioxidants)",
      "Berries (vitamins)",
      "Green tea (EGCG)"
    ],
    "foods_to_avoid": [
      "Dairy (casein, whey)",
      "High-glycemic: white bread, sugar",
      "High-iodine: seaweed"
    ]
  },

  "product_recommendations": {
    "cleanser": {
      "name": "CeraVe Hydrating Cleanser",
      "brand": "CeraVe",
      "price_usd": 8.99,
      "url": "https://...",
      "why_recommended": "Gentle, sulfate-free, suitable for dry + acne-prone",
      "ingredients": ["glycerin", "ceramides"],
      "rating": 4.5,
      "reviews": 2340
    },
    "treatment": {
      "name": "The Ordinary Salicylic Acid 2%",
      "brand": "Deciem",
      "price_usd": 5.9,
      "url": "https://...",
      "why_recommended": "Affordable, effective BHA for acne",
      "ingredients": ["salicylic acid", "glycerin"],
      "rating": 4.3,
      "reviews": 5890
    },
    "moisturizer": {
      "name": "Vanicream Moisturizing Cream",
      "brand": "Vanicream",
      "price_usd": 7.99,
      "url": "https://...",
      "why_recommended": "Free of common irritants, ceramides for barrier repair",
      "ingredients": ["ceramides", "glycerin"],
      "rating": 4.6,
      "reviews": 1230
    },
    "sunscreen": {
      "name": "La Roche-Posay Anthelios Fluid",
      "brand": "La Roche-Posay",
      "price_usd": 34.0,
      "url": "https://...",
      "why_recommended": "Lightweight, non-comedogenic",
      "rating": 4.4,
      "reviews": 890
    }
  },

  "safety_flags": {
    "severe": false,
    "requires_professional": false,
    "warnings": [
      "Salicylic acid may cause dryness initially - use moisturizer"
    ],
    "escalation": null
  },

  "created_at": "2025-10-24T20:55:00Z",
  "expires_at": "2025-11-24T20:55:00Z" // 30-day validity
}
```

### 2. Record Feedback

**Endpoint**: `POST /api/v1/recommender/feedback`

**Request**:

```json
{
  "recommendation_id": "rec_20251024_001",
  "helpful_rating": 4,
  "product_satisfaction": 4,
  "routine_completion_pct": 75,
  "feedback_text": "Great recommendations! The cleanser worked well. Will update after full 4 weeks.",
  "improvement_suggestions": "Could suggest more budget-friendly alternatives"
}
```

**Response** (201 Created):

```json
{
  "feedback_id": "fb_20251024_001",
  "recommendation_id": "rec_20251024_001",
  "status": "recorded",
  "message": "Thank you! Your feedback helps us improve recommendations.",
  "created_at": "2025-10-24T21:00:00Z"
}
```

### 3. Get Recommendation History

**Endpoint**: `GET /api/v1/recommender/history?user_id=3&limit=10`

**Response** (200 OK):

```json
{
  "user_id": 3,
  "recommendations": [
    {
      "recommendation_id": "rec_20251024_001",
      "analysis_id": 5,
      "conditions": ["acne", "blackheads"],
      "helpful_rating": 4,
      "created_at": "2025-10-24T20:55:00Z",
      "feedback_recorded": true
    }
  ],
  "total": 5
}
```

---

## 🛡️ Safety & Escalation

### Safety Module (`backend/app/recommender/safety.py`)

```python
class SafetyChecker:
    def check_conditions(self, analysis):
        """Identify conditions requiring professional help"""

        severe_conditions = {
            "severe_acne": {
                "signs": ["cystic", "widespread", "resistant"],
                "action": "See dermatologist for isotretinoin",
                "urgent": False
            },
            "skin_infection": {
                "signs": ["spreading", "painful", "pus"],
                "action": "Seek medical attention immediately",
                "urgent": True
            },
            "severe_rash": {
                "signs": ["severe itching", "blistering"],
                "action": "Consult doctor within 24 hours",
                "urgent": True
            }
        }

        flags = []
        for condition, details in severe_conditions.items():
            if any(sign in analysis.conditions for sign in details["signs"]):
                flags.append({
                    "condition": condition,
                    "action": details["action"],
                    "urgent": details["urgent"]
                })

        return flags
```

### Safety Checks in Recommendations

```python
response = {
    "safety_flags": {
        "severe": bool(severe_conditions),
        "requires_professional": bool(escalation_needed),

        "warnings": [
            "Salicylic acid may cause dryness - use moisturizer",
            "Niacinamide can cause flushing temporarily",
            "Sunscreen is CRITICAL with acne treatments"
        ],

        "escalation": {
            "condition": "Severe cystic acne",
            "action": "Consult dermatologist for isotretinoin",
            "urgent": False,
            "dermatologist_referral_link": "https://..."
        } if severe else None,

        "no_prescription_meds": True,  # Always true
        "disclaimer": "These recommendations are not medical advice..."
    }
}
```

### Prohibited Items

❌ **NEVER recommend:**

- Prescription medications (Accutane, tretinoin, antibiotics)
- Steroids (topical, oral)
- Prescription treatments
- Anything requiring medical supervision

✅ **CAN recommend:**

- OTC skincare (BHA, AHA, retinol)
- Natural ingredients (neem, tea tree with caveats)
- Lifestyle changes (diet, sleep, stress)
- Professional consultation (dermatologist referral)

---

## 🤖 Future ML Integration

### Phase 1: MVP (Current)

- ✅ Rule-based engine
- ✅ Fixed recommendation logic
- ✅ Feedback collection

### Phase 2: ML Ranking (Next)

- 📊 Use feedback data to train ranking model
- 🎯 Learn which products work best for each user
- 📈 Personalize routine recommendations
- 💡 Predict product satisfaction before recommending

### Phase 3: Advanced (Future)

- 🧬 Genetic factors (skin microbiome, genetic predisposition)
- ⏰ Seasonal recommendations (summer vs winter)
- 👥 Community-based collaborative filtering
- 🔄 Dynamic routine adjustments based on progress

---

## 📊 Feedback Analytics

### Stored Queries

```python
# Top-rated products for each condition
SELECT product_id, AVG(satisfaction) as avg_satisfaction
FROM recommendation_feedback
WHERE condition = 'acne'
GROUP BY product_id
ORDER BY avg_satisfaction DESC;

# Routine completion analysis
SELECT AVG(routine_completion_pct) as avg_completion
FROM recommendation_feedback
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY condition;

# Most helpful recommendations
SELECT recommendation_id, helpful_rating, COUNT(*) as feedback_count
FROM recommendation_feedback
GROUP BY recommendation_id
ORDER BY helpful_rating DESC;
```

---

## 🚀 Deployment

### Prerequisites

```bash
# Install dependencies
pip install pyyaml pydantic sqlalchemy

# Set up database
python -m backend.app.db.init_db
```

### Load Initial Rules

```bash
# Copy rules.yml to backend/app/recommender/
cp rules.yml backend/app/recommender/

# Load sample products to DB
python backend/app/recommender/load_products.py
```

### Test Endpoints

```bash
# Test recommendation generation
curl -X POST "http://localhost:8000/api/v1/recommender/recommend" \
  -H "Content-Type: application/json" \
  -d '{"analysis_id": 5}'

# Test feedback submission
curl -X POST "http://localhost:8000/api/v1/recommender/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "recommendation_id": "rec_20251024_001",
    "helpful_rating": 4,
    "product_satisfaction": 4,
    "routine_completion_pct": 75
  }'
```

---

## 📁 File Structure

```
backend/app/recommender/
├── __init__.py
├── README.md (this file)
├── rules.yml                    # All recommendation rules
├── engine.py                    # Core logic
│   ├── RecommendationEngine class
│   ├── generate_recommendations()
│   ├── filter_by_profile()
│   ├── rank_recommendations()
│   └── format_response()
├── safety.py                    # Safety checks
│   ├── SafetyChecker class
│   ├── check_conditions()
│   ├── validate_recommendations()
│   └── get_escalation_flags()
├── products.py                  # DB queries
│   ├── get_product_by_category()
│   ├── filter_by_budget()
│   ├── filter_by_allergies()
│   └── get_top_rated_products()
├── schemas.py                   # Pydantic models
│   ├── RecommendationRequest
│   ├── RecommendationResponse
│   ├── FeedbackRequest
│   └── FeedbackResponse
└── models.py                    # SQLAlchemy models
    ├── Product
    └── RecommendationFeedback
```

---

## 🔍 Example: Full Workflow

### User Flow

1. **User takes photo** → API analyzes → Result: acne + dry skin

2. **Frontend calls recommend endpoint**:

```bash
POST /api/v1/recommender/recommend
{
  "analysis_id": 5,
  "include_diet": true,
  "include_products": true
}
```

3. **Backend processes**:

   - Loads user profile
   - Loads analysis results
   - Applies rules for: acne + dry skin
   - Checks safety (moderate severity, no escalation)
   - Filters products by budget + allergies
   - Ranks by rating + relevance

4. **Frontend displays**:

   - ✅ 4-week skincare routine (with timing, reasons)
   - ✅ 5 diet tips (backed by science)
   - ✅ 4 product recommendations (with prices, links)
   - ✅ Safety disclaimer + warnings

5. **User follows routine** → After 2 weeks, submits feedback:

```bash
POST /api/v1/recommender/feedback
{
  "recommendation_id": "rec_20251024_001",
  "helpful_rating": 4,
  "product_satisfaction": 4,
  "routine_completion_pct": 75,
  "feedback_text": "Great results! Skin clearer already."
}
```

6. **System learns**:
   - Records feedback in DB
   - Updates product ratings
   - Analyzes routine completion
   - Improves future recommendations

---

## 🎯 Success Metrics

Track these metrics to measure recommender effectiveness:

```
✓ Feedback collection rate (target: >40% of users)
✓ Recommendation helpfulness (target: 4+ / 5)
✓ Product satisfaction (target: 4+ / 5)
✓ Routine completion (target: >60% on average)
✓ User retention (target: 70%+ repeat visits)
✓ Safety incidents (target: 0)
✓ Escalation accuracy (target: 100% coverage)
```

---

## 📚 References

- [Rule-based Recommendation Systems](https://en.wikipedia.org/wiki/Recommendation_system)
- [Dermatology Best Practices](https://www.aad.org/)
- [YAML Specification](https://yaml.org/)
- [Skincare Ingredients Database](https://www.incidecoder.com/)

---

## ✅ Next Steps

1. **Define comprehensive rules** → Dermatologist review
2. **Build product database** → Populate with top 500 products
3. **Implement engine** → Write Python code
4. **Add API endpoints** → FastAPI integration
5. **Frontend integration** → Display recommendations
6. **User testing** → Collect feedback
7. **Optimize with ML** → Use feedback for ranking

---

**Status**: 📋 Design Complete | 🏗️ Ready for Implementation

**Current Version**: MVP (Rule-based)  
**Next Version**: ML-Enhanced Ranking  
**Long-term**: Genetic + Predictive Models
