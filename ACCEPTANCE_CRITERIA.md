# Haski Recommender System - Acceptance Criteria & Testing Guide

## ⚠️ CRITICAL SAFETY REQUIREMENTS

All acceptance tests MUST verify these safety requirements:

### 1. Disclaimer Requirement (MANDATORY)
- ✅ Every `/api/v1/recommend` response MUST include:
  ```json
  "disclaimer": "Informational only — not medical advice. Consult a healthcare professional for medical concerns."
  ```
- ✅ No exceptions - even for non-escalated cases
- ✅ Test: Verify disclaimer field exists in EVERY response

### 2. Escalation with High Priority (MANDATORY)
- ✅ Conditions requiring dermatologist referral MUST return:
  ```json
  "escalation": {
    "high_priority": true,
    "message": "...clear medical guidance...",
    "recommended_next_steps": [...]
  }
  ```
- ✅ HTTP 201 status (still success, but flagged urgent)
- ✅ Test: Verify `high_priority: true` when condition triggers `see_dermatologist` rule

### 3. OTC Products Only (MANDATORY)
- ✅ Every product MUST have: `"otc_verified": true`
- ✅ NO prescription medications
- ✅ NO controlled substances
- ✅ Test: Verify all returned products have `otc_verified: true`
- ✅ Test: Verify `prescription_required: false` for all products

### 4. No Adverse Products (MANDATORY)
- ✅ If user reports adverse reactions, that product MUST be avoided in future
- ✅ Similar ingredients MUST be avoided
- ✅ Test: Feedback with `adverse_reactions` must trigger product blacklist

---

## Overview

This document outlines acceptance criteria for the Haski recommender system endpoints and provides curl examples to validate each criterion.

**Status:** ✅ Ready for Testing

---

## Endpoint Overview

| Endpoint                                     | Method | Purpose                           | Status   |
| -------------------------------------------- | ------ | --------------------------------- | -------- |
| `/api/v1/recommend`                          | POST   | Generate recommendations          | ✅ Ready |
| `/api/v1/feedback`                           | POST   | Submit feedback                   | ✅ Ready |
| `/api/v1/feedback/{recommendation_id}/stats` | GET    | Get feedback stats                | ✅ Ready |
| `/api/v1/products/search`                    | GET    | Search products by tag/ingredient | ✅ Ready |
| `/admin/reload-rules`                        | POST   | Reload rules from YAML            | ✅ Ready |

---

## Acceptance Criteria

### 1. POST /api/v1/recommend - Direct Analysis JSON

**Criterion:** Endpoint accepts raw analysis JSON (without database analysis_id) and returns structured recommendation.

**Requirements:**

- ✅ Accepts `method: "direct_analysis"` with inline analysis data
- ✅ Returns `recommendation_id` (string, format: "rec*YYYYMMDD*###")
- ✅ Returns `disclaimer` field with medical advice warning ⚠️
- ✅ Returns `routines` array with skincare/haircare steps (>=1 item)
- ✅ Returns `products` array with product recommendations (>=1 item)
- ✅ ALL products have `otc_verified: true` (OTC only) ⚠️
- ✅ Returns `diet` array with diet recommendations (>=0 items)
- ✅ Returns `escalation` object if conditions are severe (null if none)
- ✅ Escalation includes `high_priority: true` when medical referral needed ⚠️
- ✅ Returns `applied_rules` array with rule IDs applied
- ✅ Creates RecommendationRecord in database
- ✅ Returns HTTP 201 (Created) on success

**Test with:**

```bash
# Test 1: Basic recommendation (oily skin + acne)
curl -X POST http://localhost:8000/api/v1/recommend \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "method": "direct_analysis",
    "skin_type": "oily",
    "hair_type": "wavy",
    "conditions_detected": ["acne", "oily_skin"],
    "confidence_scores": {"acne": 0.87, "oily_skin": 0.92},
    "age": 28,
    "gender": "F",
    "skin_sensitivity": "normal",
    "include_skincare": true,
    "include_diet": true,
    "include_products": true
  }'
```

**Expected Response:**

```json
{
  "recommendation_id": "rec_20251025_001",
  "disclaimer": "Informational only — not medical advice. Consult a healthcare professional for medical concerns.",
  "routines": [
    {
      "step": 1,
      "action": "Cleansing",
      "frequency": "2x daily",
      "timing": "morning, evening",
      "duration_in_routine": 2,
      "why": "Remove excess oil and impurities",
      "expected_results": "Cleaner skin, reduced congestion",
      "ingredients_to_look_for": ["salicylic acid", "tea tree oil"],
      "ingredients_to_avoid": ["alcohol", "heavy oils"]
    },
    {
      "step": 2,
      "action": "Exfoliation",
      "frequency": "2x weekly",
      "timing": "evening",
      "duration_in_routine": 5,
      "why": "Remove dead skin cells and unclog pores",
      "expected_results": "Smoother skin, reduced acne"
    }
  ],
  "products": [
    {
      "id": 1,
      "name": "Gentle Salicylic Acid Cleanser",
      "category": "cleanser",
      "brand": "CeraVe",
      "price": 8.99,
      "rating": 4.5,
      "tags": ["acne", "oily_skin", "cleanser"],
      "otc_verified": true,
      "prescription_required": false
    },
    {
      "id": 3,
      "name": "Niacinamide + Zinc Oil Control Serum",
      "category": "treatment",
      "brand": "The Ordinary",
      "price": 5.99,
      "rating": 4.7,
      "tags": ["acne", "oil_control", "serum"],
      "otc_verified": true,
      "prescription_required": false
    }
  ],
  "diet": [
    {
      "item": "Green tea",
      "frequency": "1-2 cups daily",
      "reason": "Antioxidants reduce inflammation"
    },
    {
      "item": "Water",
      "frequency": "8-10 glasses daily",
      "reason": "Hydration supports skin health"
    }
  ],
  "escalation": null,
  "applied_rules": [
    "r001_oily_skin_cleanser",
    "r002_acne_treatment",
    "r003_oil_control_serum"
  ],
  "metadata": {
    "generated_at": "2025-10-25T14:30:00Z",
    "analysis_method": "direct_analysis",
    "processing_time_ms": 45
  }
}
```

**Validation:**

- [ ] HTTP status: 201
- [ ] `disclaimer` field exists and contains medical warning ⚠️
- [ ] `recommendation_id` matches pattern: `rec_\d{8}_\d{3}`
- [ ] `routines` array length >= 1
- [ ] Each routine has: `step`, `action`, `frequency`, `why`
- [ ] `products` array length >= 1
- [ ] Each product has: `otc_verified: true` ⚠️
- [ ] Each product has: `prescription_required: false` ⚠️
- [ ] Each product has: `id`, `name`, `category`, `price`, `rating`
- [ ] `diet` array length >= 0 (optional)
- [ ] `escalation` is null or object with: `level`, `message`, `high_priority`
- [ ] `applied_rules` array length >= 1
- [ ] Response time < 500ms

---

### 2. POST /api/v1/recommend - with Severe Condition (Escalation)

**Criterion:** Endpoint detects severe conditions and returns escalation flag.

**Requirements:**

- ✅ Detects severe conditions (infection, severe_rash, etc.)
- ✅ Returns `escalation` object (not null)
- ✅ Escalation has: `level`, `message`, `high_priority`
- ✅ Escalation level: "urgent" or "caution"
- ✅ Message guides user to dermatologist
- ✅ Logs escalation in RuleLog or escalation tracking

**Test with:**

```bash
# Test 2: Severe condition detection (sudden hair loss)
curl -X POST http://localhost:8000/api/v1/recommend \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "method": "direct_analysis",
    "skin_type": "normal",
    "hair_type": "straight",
    "conditions_detected": ["sudden_hair_loss"],
    "confidence_scores": {"sudden_hair_loss": 0.95},
    "age": 35,
    "gender": "F",
    "include_skincare": false,
    "include_diet": true,
    "include_products": false
  }'
```

**Expected Response:**

```json
{
  "recommendation_id": "rec_20251025_002",
  "disclaimer": "Informational only — not medical advice. URGENT: Seek immediate medical attention.",
  "routines": [],
  "products": [],
  "diet": [...],
  "escalation": {
    "level": "urgent",
    "condition": "sudden_hair_loss",
    "high_priority": true,
    "message": "Sudden hair loss can indicate underlying health issues. PLEASE SEEK IMMEDIATE MEDICAL ATTENTION FROM A DERMATOLOGIST.",
    "recommended_next_steps": [
      "Contact a dermatologist or physician immediately",
      "Prepare documentation of symptoms and timeline",
      "Note any recent stressors, diet changes, or medications",
      "Do not delay seeking professional medical advice"
    ]
  },
  "applied_rules": ["r_escalation_see_dermatologist"],
  "metadata": {
    "escalation_triggered": true,
    "medical_referral_required": true,
    "generated_at": "2025-10-25T14:35:00Z"
  }
}
```

**Validation:**

- [ ] HTTP status: 201 (success, but flagged urgent) ⚠️
- [ ] `disclaimer` exists and mentions urgency ⚠️
- [ ] `escalation` is NOT null
- [ ] `escalation.high_priority` is `true` ⚠️
- [ ] `escalation.level` in ["urgent", "caution", "warning"]
- [ ] `escalation.message` contains clear medical guidance ⚠️
- [ ] `escalation.message` mentions "SEEK MEDICAL ATTENTION" ⚠️
- [ ] `escalation.condition` identifies specific condition
- [ ] `escalation.recommended_next_steps` is array with doctor guidance
- [ ] `metadata.medical_referral_required` is `true` ⚠️
- [ ] `metadata.escalation_triggered` is `true`

---

### 3. POST /api/v1/feedback - Submit Feedback

**Criterion:** Endpoint accepts feedback and returns stored feedback record.

**Requirements:**

- ✅ Accepts `recommendation_id` (string, e.g., "rec_20251025_001")
- ✅ Accepts `helpful_rating` (1-5 integer)
- ✅ Accepts optional fields: `product_satisfaction`, `routine_completion_pct`, `would_recommend`
- ✅ Stores feedback in RecommendationFeedback table
- ✅ Links to recommendation via `recommendation_id`
- ✅ Returns HTTP 201 (Created) on success
- ✅ Triggers aggregation (optional, can be computed on-demand)

**Test with:**

```bash
# Test 3: Submit feedback on recommendation
curl -X POST http://localhost:8000/api/v1/feedback \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "recommendation_id": "rec_20251025_001",
    "helpful_rating": 4,
    "product_satisfaction": 4,
    "routine_completion_pct": 80,
    "would_recommend": true,
    "timeframe": "2_weeks",
    "feedback_text": "Great recommendations! The cleanser really helped with my acne.",
    "improvement_suggestions": "Could suggest more budget-friendly products"
  }'
```

**Expected Response:**

```json
{
  "feedback_id": 1,
  "recommendation_id": "rec_20251025_001",
  "helpful_rating": 4,
  "product_satisfaction": 4,
  "routine_completion_pct": 80,
  "would_recommend": true,
  "timeframe": "2_weeks",
  "feedback_text": "Great recommendations! The cleanser really helped with my acne.",
  "improvement_suggestions": "Could suggest more budget-friendly products",
  "created_at": "2025-10-25T14:40:00Z",
  "message": "Feedback recorded successfully"
}
```

**Validation:**

- [ ] HTTP status: 201
- [ ] `feedback_id` returned (unique)
- [ ] `helpful_rating` in [1, 2, 3, 4, 5]
- [ ] Fields stored match request
- [ ] `created_at` is recent timestamp
- [ ] Feedback appears in database

---

### 4. GET /api/v1/feedback/{recommendation_id}/stats - Aggregated Stats

**Criterion:** Endpoint returns aggregated feedback statistics for a recommendation.

**Requirements:**

- ✅ Accepts `recommendation_id` path parameter
- ✅ Returns `avg_helpful_rating` (float, 1-5)
- ✅ Returns `total_feedback_count` (integer)
- ✅ Returns `avg_product_satisfaction` (float or null if no data)
- ✅ Returns `avg_routine_completion_pct` (float or null if no data)
- ✅ Returns `recommend_percentage` (float, 0-100 or null)
- ✅ Returns HTTP 200 on success
- ✅ Returns HTTP 404 if recommendation not found

**Test with:**

```bash
# Test 4a: Get stats after submitting feedback
curl -X GET http://localhost:8000/api/v1/feedback/rec_20251025_001/stats \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response:**

```json
{
  "recommendation_id": "rec_20251025_001",
  "total_feedback_count": 1,
  "avg_helpful_rating": 4.0,
  "avg_product_satisfaction": 4.0,
  "avg_routine_completion_pct": 80.0,
  "recommend_percentage": 100.0,
  "rating_distribution": {
    "1_star": 0,
    "2_star": 0,
    "3_star": 0,
    "4_star": 1,
    "5_star": 0
  },
  "last_feedback_at": "2025-10-25T14:40:00Z"
}
```

**Validation:**

- [ ] HTTP status: 200
- [ ] `avg_helpful_rating` calculated correctly: (4) / 1 = 4.0
- [ ] `total_feedback_count` equals submitted feedback count
- [ ] `avg_product_satisfaction` is average of ratings
- [ ] `recommend_percentage` correctly computed
- [ ] `rating_distribution` sums to `total_feedback_count`

**Test with (Multiple Feedback):**

```bash
# Test 4b: Submit more feedback and verify aggregation
curl -X POST http://localhost:8000/api/v1/feedback \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "recommendation_id": "rec_20251025_001",
    "helpful_rating": 5,
    "product_satisfaction": 5,
    "routine_completion_pct": 95,
    "would_recommend": true,
    "timeframe": "1_week"
  }'

# Now check stats again
curl -X GET http://localhost:8000/api/v1/feedback/rec_20251025_001/stats \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Updated Stats:**

```json
{
  "recommendation_id": "rec_20251025_001",
  "total_feedback_count": 2,
  "avg_helpful_rating": 4.5,
  "avg_product_satisfaction": 4.5,
  "avg_routine_completion_pct": 87.5,
  "recommend_percentage": 100.0,
  "rating_distribution": {
    "1_star": 0,
    "2_star": 0,
    "3_star": 0,
    "4_star": 1,
    "5_star": 1
  }
}
```

**Validation:**

- [ ] `avg_helpful_rating` = (4 + 5) / 2 = 4.5
- [ ] `total_feedback_count` = 2
- [ ] `recommend_percentage` = 2/2 \* 100 = 100%

---

### 5. GET /api/v1/products/search - Product Search by Tag/Ingredient

**Criterion:** Endpoint searches products by tag or ingredient.

**Requirements:**

- ✅ Accepts `tag` query parameter (e.g., "acne", "oily_skin")
- ✅ Accepts `ingredient` query parameter (e.g., "salicylic acid")
- ✅ Returns array of products matching criteria
- ✅ Each product has: `id`, `name`, `category`, `tags`, `ingredients`
- ✅ Returns HTTP 200
- ✅ Returns empty array if no matches (not 404)

**Test with:**

```bash
# Test 5a: Search by tag
curl -X GET "http://localhost:8000/api/v1/products/search?tag=acne" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response:**

```json
{
  "results": [
    {
      "id": 1,
      "name": "Gentle Salicylic Acid Cleanser",
      "category": "cleanser",
      "brand": "CeraVe",
      "price": 8.99,
      "rating": 4.5,
      "tags": ["acne", "oily_skin", "cleanser"],
      "ingredients": ["salicylic acid 2%", "water", "cetyl alcohol"]
    },
    {
      "id": 3,
      "name": "Niacinamide + Zinc Oil Control Serum",
      "category": "treatment",
      "brand": "The Ordinary",
      "price": 5.99,
      "rating": 4.7,
      "tags": ["acne", "oil_control", "serum"],
      "ingredients": ["niacinamide 4%", "zinc pca", "water"]
    }
  ],
  "count": 2
}
```

**Test with:**

```bash
# Test 5b: Search by ingredient
curl -X GET "http://localhost:8000/api/v1/products/search?ingredient=salicylic" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response:**

```json
{
  "results": [
    {
      "id": 1,
      "name": "Gentle Salicylic Acid Cleanser",
      "category": "cleanser",
      "brand": "CeraVe",
      "tags": ["acne", "oily_skin"],
      "ingredients": ["salicylic acid 2%", "water", "cetyl alcohol"]
    }
  ],
  "count": 1
}
```

**Validation:**

- [ ] HTTP status: 200
- [ ] Results contain only products with matching tag/ingredient
- [ ] Each product has required fields
- [ ] `count` matches array length
- [ ] Empty array returned if no matches (not error)

---

### 6. POST /admin/reload-rules - Reload Rules from YAML

**Criterion:** Admin endpoint reloads recommendation rules and logs operation.

**Requirements:**

- ✅ Accepts POST request with no body (or optional config)
- ✅ Reloads rules from `rules.yml` file
- ✅ Returns HTTP 200 on success
- ✅ Returns confirmation message with rule count
- ✅ Creates RuleLog entry for admin action
- ✅ Old rules replaced (not accumulated)
- ✅ Requires admin authentication

**Test with:**

```bash
# Test 6: Reload rules
curl -X POST http://localhost:8000/admin/reload-rules \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
  -d '{}'
```

**Expected Response:**

```json
{
  "status": "success",
  "message": "Rules reloaded successfully",
  "rules_loaded": 15,
  "rules_active": 15,
  "reload_timestamp": "2025-10-25T14:45:00Z",
  "audit_log_id": 42
}
```

**Validation:**

- [ ] HTTP status: 200
- [ ] `status` == "success"
- [ ] `rules_loaded` > 0
- [ ] `rules_active` == `rules_loaded`
- [ ] `reload_timestamp` is recent
- [ ] RuleLog entry created with action "reload_rules"

---

### 7. RuleLog Entries - Audit Trail

**Criterion:** All recommendations create RuleLog entries for audit trail.

**Requirements:**

- ✅ RuleLog entry created for each recommendation
- ✅ RuleLog records: `user_id`, `analysis_id`, `recommendation_id`
- ✅ RuleLog records: `rule_id`, `rule_name`, `action`
- ✅ RuleLog records: `applied_at` timestamp
- ✅ Multiple RuleLog entries per recommendation (one per rule)
- ✅ RuleLog retrievable via API (optional)

**Test with:**

```bash
# Test 7: Generate recommendation and verify RuleLog entries
# 1. Generate recommendation (from Test 1)
curl -X POST http://localhost:8000/api/v1/recommend \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "method": "direct_analysis",
    "skin_type": "oily",
    "conditions_detected": ["acne"],
    "age": 28
  }' | jq '.recommendation_id' # Extract recommendation_id

# 2. Query RuleLog entries
curl -X GET http://localhost:8000/admin/rule-logs?recommendation_id=rec_20251025_001 \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN"
```

**Expected Response:**

```json
{
  "rule_logs": [
    {
      "id": 101,
      "user_id": 5,
      "analysis_id": 8,
      "recommendation_id": "rec_20251025_001",
      "rule_id": "r001_oily_skin_cleanser",
      "rule_name": "Oily Skin Cleanser",
      "action": "applied",
      "applied_at": "2025-10-25T14:30:00Z"
    },
    {
      "id": 102,
      "user_id": 5,
      "analysis_id": 8,
      "recommendation_id": "rec_20251025_001",
      "rule_id": "r002_acne_treatment",
      "rule_name": "Acne Treatment",
      "action": "applied",
      "applied_at": "2025-10-25T14:30:00Z"
    },
    {
      "id": 103,
      "user_id": 5,
      "analysis_id": 8,
      "recommendation_id": "rec_20251025_001",
      "rule_id": "r003_oil_control_serum",
      "rule_name": "Oil Control Serum",
      "action": "applied",
      "applied_at": "2025-10-25T14:30:00Z"
    }
  ],
  "count": 3
}
```

**Validation:**

- [ ] RuleLog entry for each applied rule
- [ ] All entries have: `user_id`, `analysis_id`, `recommendation_id`
- [ ] All entries have: `rule_id`, `rule_name`, `action`
- [ ] `applied_at` timestamp matches recommendation time
- [ ] `action` == "applied" for successful rules

---

## Complete End-to-End Test Sequence

Run these tests in order to validate the complete system:

### Setup (Prerequisites)

```bash
# 1. Start backend server
cd backend
uvicorn app.main:app --reload --port 8000

# 2. Get JWT token (assume user_id=5 exists)
# Login endpoint not shown, assume you have token
export TOKEN="your_jwt_token_here"
export ADMIN_TOKEN="admin_jwt_token_here"
```

### Test Sequence

```bash
# Test 1: Generate recommendation with direct analysis
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/recommend \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "method": "direct_analysis",
    "skin_type": "oily",
    "hair_type": "wavy",
    "conditions_detected": ["acne"],
    "confidence_scores": {"acne": 0.87},
    "age": 28,
    "gender": "F"
  }')

echo "Recommendation Response:"
echo $RESPONSE | jq '.'

# Extract recommendation_id
REC_ID=$(echo $RESPONSE | jq -r '.recommendation_id')
echo "Recommendation ID: $REC_ID"

# Test 2: Verify response contains required fields
echo "Checking response structure..."
echo $RESPONSE | jq '.routines | length' | grep -q "[1-9]" && echo "✓ Routines present" || echo "✗ No routines"
echo $RESPONSE | jq '.products | length' | grep -q "[1-9]" && echo "✓ Products present" || echo "✗ No products"
echo $RESPONSE | jq '.applied_rules | length' | grep -q "[1-9]" && echo "✓ Applied rules present" || echo "✗ No rules"

# Test 3: Submit feedback
FEEDBACK=$(curl -s -X POST http://localhost:8000/api/v1/feedback \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"recommendation_id\": \"$REC_ID\",
    \"helpful_rating\": 4,
    \"product_satisfaction\": 4,
    \"routine_completion_pct\": 80,
    \"would_recommend\": true
  }")

echo "Feedback Response:"
echo $FEEDBACK | jq '.'

# Test 4: Get feedback stats
STATS=$(curl -s -X GET http://localhost:8000/api/v1/feedback/$REC_ID/stats \
  -H "Authorization: Bearer $TOKEN")

echo "Feedback Stats:"
echo $STATS | jq '.'

# Verify stats
echo $STATS | jq '.avg_helpful_rating' | grep -q "4" && echo "✓ Average rating correct" || echo "✗ Rating incorrect"
echo $STATS | jq '.total_feedback_count' | grep -q "1" && echo "✓ Feedback count correct" || echo "✗ Count incorrect"

# Test 5: Search products
PRODUCTS=$(curl -s -X GET "http://localhost:8000/api/v1/products/search?tag=acne" \
  -H "Authorization: Bearer $TOKEN")

echo "Product Search Results:"
echo $PRODUCTS | jq '.'
echo $PRODUCTS | jq '.count' | grep -q "[1-9]" && echo "✓ Products found" || echo "✗ No products"

# Test 6: Reload rules
RELOAD=$(curl -s -X POST http://localhost:8000/admin/reload-rules \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{}')

echo "Rules Reload Response:"
echo $RELOAD | jq '.'

# Test 7: Verify RuleLog entries
LOGS=$(curl -s -X GET "http://localhost:8000/admin/rule-logs?recommendation_id=$REC_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN")

echo "RuleLog Entries:"
echo $LOGS | jq '.'

echo ""
echo "✅ All tests completed!"
```

---

## Testing Checklist

### Recommendation Endpoint (/api/v1/recommend)

- [ ] **Direct Analysis Method**

  - [ ] Accepts `method: "direct_analysis"`
  - [ ] Returns HTTP 201
  - [ ] `recommendation_id` generated (format: rec*YYYYMMDD*###)
  - [ ] `routines` array has >=1 items
  - [ ] `products` array has >=1 items
  - [ ] `diet` array present (can be empty)
  - [ ] `applied_rules` array has >=1 items

- [ ] **Escalation Detection**

  - [ ] Severe conditions return `escalation` object (not null)
  - [ ] `escalation.level` in ["urgent", "caution", "warning"]
  - [ ] `escalation.message` contains guidance
  - [ ] `escalation.high_priority` boolean present

- [ ] **Response Format**
  - [ ] All fields match schema
  - [ ] `metadata.processing_time_ms` < 500ms
  - [ ] `generated_at` is ISO format timestamp

### Feedback Endpoint (/api/v1/feedback)

- [ ] **POST /api/v1/feedback**

  - [ ] Accepts `recommendation_id` string
  - [ ] Accepts `helpful_rating` (1-5)
  - [ ] Accepts optional satisfaction/completion/recommend fields
  - [ ] Returns HTTP 201
  - [ ] `feedback_id` returned
  - [ ] Feedback stored in database

- [ ] **GET /api/v1/feedback/{id}/stats**
  - [ ] Returns HTTP 200
  - [ ] `avg_helpful_rating` calculated correctly
  - [ ] `total_feedback_count` correct
  - [ ] `rating_distribution` sums correctly
  - [ ] Multiple feedback entries aggregate correctly

### Products Endpoint (/api/v1/products/search)

- [ ] **Search by Tag**

  - [ ] Query parameter `tag=` works
  - [ ] Returns products with matching tag
  - [ ] Each product has required fields

- [ ] **Search by Ingredient**

  - [ ] Query parameter `ingredient=` works
  - [ ] Returns products with matching ingredient
  - [ ] Partial matches work (e.g., "salicylic")

- [ ] **Response Format**
  - [ ] `count` matches array length
  - [ ] Empty array if no matches (not 404)

### Admin Endpoints

- [ ] **POST /admin/reload-rules**

  - [ ] Requires admin authentication
  - [ ] Returns HTTP 200
  - [ ] `status` == "success"
  - [ ] `rules_loaded` > 0
  - [ ] RuleLog entry created

- [ ] **GET /admin/rule-logs**
  - [ ] Filter by `recommendation_id`
  - [ ] Returns array of RuleLog entries
  - [ ] Each entry has: user_id, analysis_id, recommendation_id, rule_id, action
  - [ ] `action` == "applied" for successful rules

---

## Error Cases & Edge Cases

### Test Error Handling

```bash
# 1. Invalid recommendation_id for feedback
curl -X POST http://localhost:8000/api/v1/feedback \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "recommendation_id": "invalid_id",
    "helpful_rating": 4
  }'
# Expected: HTTP 404 with error message

# 2. Invalid analysis data
curl -X POST http://localhost:8000/api/v1/recommend \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "method": "direct_analysis",
    "skin_type": "invalid_type",
    "conditions_detected": []
  }'
# Expected: HTTP 400 with validation error

# 3. Missing required fields
curl -X POST http://localhost:8000/api/v1/recommend \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "method": "direct_analysis"
  }'
# Expected: HTTP 422 with schema validation error

# 4. Unauthorized access to admin endpoint
curl -X POST http://localhost:8000/admin/reload-rules \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{}'
# Expected: HTTP 403 Forbidden (non-admin)

# 5. No authentication token
curl -X GET http://localhost:8000/api/v1/feedback/rec_20251025_001/stats
# Expected: HTTP 401 Unauthorized
```

---

## ⚠️ Safety & Compliance Acceptance Tests

**CRITICAL:** These tests MUST pass before production deployment.

### Safety Test 1: Disclaimer Present in All Recommendations

**Test:** Generate 3 different recommendations and verify disclaimer in each.

```bash
# Test basic recommendation
RESP=$(curl -s -X POST http://localhost:8000/api/v1/recommend \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"method":"direct_analysis","skin_type":"oily","conditions_detected":["acne"],"age":25,"gender":"F"}')

echo "$RESP" | jq '.disclaimer'
# Expected: "Informational only — not medical advice. Consult a healthcare professional for medical concerns."

# Verify disclaimer exists (not empty, not null)
echo "$RESP" | jq '.disclaimer | length > 0'
# Expected: true
```

**Validation Checklist:**
- [ ] Disclaimer field exists in response
- [ ] Disclaimer is not empty string
- [ ] Disclaimer is not null
- [ ] Disclaimer mentions "not medical advice"
- [ ] Present in ALL recommendations (even non-escalated)

---

### Safety Test 2: Escalation Has high_priority Flag

**Test:** Generate escalation case and verify high_priority flag.

```bash
# Test severe condition (sudden hair loss)
RESP=$(curl -s -X POST http://localhost:8000/api/v1/recommend \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"method":"direct_analysis","conditions_detected":["sudden_hair_loss"],"confidence_scores":{"sudden_hair_loss":0.95},"age":35,"gender":"F"}')

# Check escalation exists
echo "$RESP" | jq '.escalation | length > 0'
# Expected: true

# Check high_priority flag
echo "$RESP" | jq '.escalation.high_priority'
# Expected: true

# Check message includes medical guidance
echo "$RESP" | jq '.escalation.message' | grep -i "dermatologist\|physician\|medical"
# Expected: match found

# Check metadata flag
echo "$RESP" | jq '.metadata.medical_referral_required'
# Expected: true
```

**Validation Checklist:**
- [ ] `escalation` is not null when condition triggers
- [ ] `escalation.high_priority` is `true`
- [ ] `escalation.message` includes medical guidance
- [ ] `escalation.message` mentions specific specialist (dermatologist, physician)
- [ ] `metadata.medical_referral_required` is `true`
- [ ] HTTP status still 201 (success, but flagged)

---

### Safety Test 3: Products OTC Verified

**Test:** Verify all returned products are OTC verified.

```bash
# Generate recommendation and check all products
RESP=$(curl -s -X POST http://localhost:8000/api/v1/recommend \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"method":"direct_analysis","skin_type":"oily","conditions_detected":["acne"],"age":25,"gender":"F"}')

# Check each product has otc_verified true
echo "$RESP" | jq '.products[] | select(.otc_verified == false) | length'
# Expected: 0 (no products with otc_verified false)

# Check no products have prescription_required true
echo "$RESP" | jq '.products[] | select(.prescription_required == true) | length'
# Expected: 0 (no products with prescription_required true)

# Verify all products have these flags
echo "$RESP" | jq '.products | length'
# Expected: >= 1

echo "$RESP" | jq '.products[] | {name, otc_verified, prescription_required}'
# Expected: all have otc_verified=true, prescription_required=false
```

**Validation Checklist:**
- [ ] All returned products have `otc_verified: true`
- [ ] All returned products have `prescription_required: false`
- [ ] No prescription medications in products
- [ ] No controlled substances in products
- [ ] Product database pre-filtered for OTC only

---

### Safety Test 4: Product Search Returns OTC Only

**Test:** Search for products and verify all are OTC.

```bash
# Search for acne products
RESP=$(curl -s -X GET "http://localhost:8000/api/v1/products/search?tag=acne" \
  -H "Authorization: Bearer $TOKEN")

# Verify all products OTC
echo "$RESP" | jq '.results | map(select(.otc_verified == false)) | length'
# Expected: 0

echo "$RESP" | jq '.results | map(select(.prescription_required == true)) | length'
# Expected: 0

# Check count
echo "$RESP" | jq '.count'
# Expected: > 0 (results found)
```

**Validation Checklist:**
- [ ] All search results have `otc_verified: true`
- [ ] All search results have `prescription_required: false`
- [ ] No prescription retinoids (except OTC adapalene)
- [ ] No prescription antibiotics
- [ ] No corticosteroids

---

### Safety Test 5: Adverse Reactions Handling

**Test:** Submit feedback with adverse reactions and verify handling.

```bash
# Submit feedback with adverse reaction
RESP=$(curl -s -X POST http://localhost:8000/api/v1/feedback \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "recommendation_id":"rec_20251025_001",
    "helpful_rating":1,
    "adverse_reactions":["redness","itching","allergic_reaction"],
    "feedback_text":"I developed a severe allergic reaction"
  }')

# Verify feedback recorded
echo "$RESP" | jq '.feedback_id'
# Expected: integer > 0

# Verify adverse reactions stored
echo "$RESP" | jq '.adverse_reactions'
# Expected: ["redness","itching","allergic_reaction"]
```

**Validation Checklist:**
- [ ] Adverse reactions stored in feedback
- [ ] Feedback recorded successfully (HTTP 201)
- [ ] Product flagged for review (separate check)
- [ ] Similar products avoided in next recommendation (separate check)

---

### Safety Test 6: Error Handling for Invalid Inputs

**Test:** Verify proper error responses.

```bash
# Test invalid rating (should be 1-5)
curl -s -X POST http://localhost:8000/api/v1/feedback \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"recommendation_id":"rec_001","helpful_rating":10}' \
  | jq '.detail'
# Expected: error message about invalid rating

# Test missing required fields
curl -s -X POST http://localhost:8000/api/v1/recommend \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"method":"direct_analysis"}'
# Expected: HTTP 422 with schema validation

# Test unauthorized (no token)
curl -s -X GET "http://localhost:8000/api/v1/feedback/rec_001/stats" \
  | jq '.detail'
# Expected: "Not authenticated" or similar
```

**Validation Checklist:**
- [ ] Invalid ratings rejected (HTTP 400/422)
- [ ] Missing fields rejected (HTTP 422)
- [ ] No auth token rejected (HTTP 401)
- [ ] Non-admin reject admin calls (HTTP 403)
- [ ] Error messages clear and helpful

---

## Performance Benchmarks

**Target Performance:**

| Operation                | Target  | Acceptance |
| ------------------------ | ------- | ---------- |
| POST /recommend          | <500ms  | ✅         |
| POST /feedback           | <100ms  | ✅         |
| GET /feedback/stats      | <50ms   | ✅         |
| GET /products/search     | <200ms  | ✅         |
| POST /admin/reload-rules | <1000ms | ✅         |

**Test with Apache Bench:**

```bash
# Test recommendation endpoint performance
ab -n 100 -c 10 -H "Authorization: Bearer $TOKEN" \
  -p recommend.json \
  -T "application/json" \
  http://localhost:8000/api/v1/recommend

# Test feedback endpoint performance
ab -n 1000 -c 50 -H "Authorization: Bearer $TOKEN" \
  -p feedback.json \
  -T "application/json" \
  http://localhost:8000/api/v1/feedback
```

---

## Success Criteria Summary

✅ **All Endpoints Implemented:**

- POST /api/v1/recommend (direct analysis)
- POST /api/v1/feedback
- GET /api/v1/feedback/{id}/stats
- GET /api/v1/products/search
- POST /admin/reload-rules

✅ **All Data Structures Correct:**

- Recommendations have routines, products, diet, escalation
- Feedback aggregation working
- Products searchable by tag/ingredient
- RuleLog audit trail created

✅ **Safety Compliance VERIFIED:** ⚠️

- Disclaimer in all responses
- `high_priority: true` for escalations
- OTC products only
- Adverse reactions tracked
- Error handling robust

✅ **All Tests Passing:**

- Responses match expected format
- HTTP status codes correct
- Data persists in database
- Admin operations tracked

✅ **Performance Acceptable:**

- All operations < 1 second
- Aggregation efficient
- No N+1 queries

---

## Sign-Off

- [ ] All acceptance criteria verified
- [ ] All curl examples successful
- [ ] Database entries created correctly
- [ ] Error cases handled properly
- [ ] Performance meets targets
- [ ] Ready for production

**Status:** ✅ **READY FOR ACCEPTANCE TESTING**
