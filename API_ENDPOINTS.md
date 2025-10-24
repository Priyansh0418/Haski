# Haski API Endpoints - Complete Reference

## ⚠️ CRITICAL SAFETY INFORMATION

> **DISCLAIMER:** All recommendations provided by this API are **informational only** and are **NOT medical advice**. Users must consult with a healthcare professional before making any medical decisions.

### Safety Requirements - All Endpoints MUST Follow:

1. **Disclaimer in All Responses:** Every recommendation response MUST include:
   ```
   "disclaimer": "Informational only — not medical advice. Consult a healthcare professional for medical concerns."
   ```

2. **Escalation Cases - Dermatologist Referral:**
   - When `escalation.condition` includes: `see_dermatologist`, severe skin infections, severe rashes, or severe hair loss
   - API MUST return: `"high_priority": true`
   - API MUST include clear instruction: "Seek immediate medical attention from a dermatologist"
   - Response HTTP status: 201 (still created, but flagged as urgent)

3. **Products Only - OTC Approved:**
   - Products returned MUST be over-the-counter (OTC) only
   - MUST NOT suggest prescription drugs or medications
   - MUST NOT suggest controlled substances
   - Each product MUST have `otc_verified: true` in response

---

## Quick Links

- [Base URL](#base-url)
- [Authentication](#authentication)
- [Safety Requirements](#-critical-safety-information)
- [Endpoints](#endpoints)
  - [Recommendations](#post-apiv1recommend)
  - [Feedback](#post-apiv1feedback)
  - [Statistics](#get-apiv1feedbackrecommendation_idstats)
  - [Products](#get-apiv1productssearch)
  - [Admin](#admin-endpoints)
- [Testing](#testing)
- [Curl Examples](#curl-examples)

---

## Base URL

```
http://localhost:8000
```

For production, replace with your deployed URL.

---

## Authentication

All endpoints (except health checks) require JWT authentication via `Authorization: Bearer <token>` header.

**Getting a Token:**

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "password"}'
```

Returns:

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

---

## Endpoints

### POST /api/v1/recommend

Generate personalized skincare/haircare recommendations.

**Authentication:** Required (user token)

**Request Method:** POST

**Request Headers:**

```
Content-Type: application/json
Authorization: Bearer <user_token>
```

**Request Body:**

```json
{
  "method": "direct_analysis",
  "skin_type": "oily|dry|combination|sensitive",
  "hair_type": "straight|wavy|curly",
  "conditions_detected": ["acne", "oily_skin", "dryness"],
  "confidence_scores": {
    "acne": 0.87,
    "oily_skin": 0.92
  },
  "age": 28,
  "gender": "M|F",
  "skin_sensitivity": "normal|sensitive|very_sensitive",
  "allergies": ["ingredient1", "ingredient2"],
  "budget": "low|medium|high",
  "include_skincare": true,
  "include_diet": true,
  "include_products": true,
  "include_lifestyle": true
}
```

**Response (HTTP 201 Created):**

```json
{
  "recommendation_id": "rec_20251025_001",
  "disclaimer": "Informational only — not medical advice. Consult a healthcare professional for medical concerns.",
  "routines": [
    {
      "step": 1,
      "action": "Cleanser",
      "frequency": "2x daily",
      "timing": "morning, evening",
      "duration_in_routine": 2,
      "why": "Remove oil and impurities",
      "expected_results": "Cleaner skin",
      "ingredients_to_look_for": ["salicylic acid"],
      "ingredients_to_avoid": ["alcohol"],
      "warning": null
    }
  ],
  "products": [
    {
      "id": 1,
      "name": "Gentle Cleanser",
      "category": "cleanser",
      "brand": "Brand",
      "price": 8.99,
      "rating": 4.5,
      "tags": ["acne", "oily_skin"],
      "otc_verified": true
    }
  ],
  "diet": [
    {
      "item": "Green tea",
      "frequency": "1-2 cups daily",
      "reason": "Antioxidants"
    }
  ],
  "escalation": null,
  "applied_rules": ["r001", "r002"],
  "metadata": {
    "generated_at": "2025-10-25T14:30:00Z",
    "processing_time_ms": 45,
    "analysis_method": "direct_analysis"
  }
}
```

**Error Responses:**

- **400 Bad Request:** Invalid input data

  ```json
  { "detail": "Invalid analysis data: skin_type must be one of..." }
  ```

- **401 Unauthorized:** Missing or invalid token

  ```json
  { "detail": "Not authenticated" }
  ```

- **500 Internal Server Error:** Engine or database error
  ```json
  { "detail": "Failed to generate recommendation" }
  ```

**⚠️ Escalation Response Example (High Priority):**

When a severe condition is detected that requires medical attention:

```json
{
  "recommendation_id": "rec_20251025_002",
  "disclaimer": "Informational only — not medical advice. URGENT: Seek immediate medical attention.",
  "routines": [],
  "products": [],
  "diet": [],
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

**Key Points for Escalation:**
- ✅ `high_priority: true` signals frontend to show urgent warning
- ✅ `escalation.message` MUST include clear medical guidance
- ✅ `medical_referral_required: true` in metadata
- ✅ Disclaimer updated to emphasize urgency
- ✅ HTTP 201 status (still a valid response, but flagged as critical)

**Curl Example:**

```bash
curl -X POST http://localhost:8000/api/v1/recommend \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "method": "direct_analysis",
    "skin_type": "oily",
    "hair_type": "wavy",
    "conditions_detected": ["acne"],
    "age": 28,
    "gender": "F"
  }' | jq '.'
```

---

### POST /api/v1/feedback

Submit user feedback on a recommendation.

**Authentication:** Required (user token)

**Request Method:** POST

**Request Headers:**

```
Content-Type: application/json
Authorization: Bearer <user_token>
```

**Request Body:**

```json
{
  "recommendation_id": "rec_20251025_001",
  "helpful_rating": 4,
  "product_satisfaction": 4,
  "routine_completion_pct": 80,
  "would_recommend": true,
  "timeframe": "1_week|2_weeks|1_month|3_months",
  "feedback_text": "Great recommendations!",
  "improvement_suggestions": "Could add more budget options",
  "adverse_reactions": null,
  "product_ratings": {
    "product_1": 5,
    "product_3": 4
  }
}
```

**Required Fields:**

- `recommendation_id`: string
- `helpful_rating`: integer (1-5)

**Optional Fields:**

- All other fields are optional

**Response (HTTP 201 Created):**

```json
{
  "feedback_id": 1,
  "recommendation_id": "rec_20251025_001",
  "helpful_rating": 4,
  "product_satisfaction": 4,
  "routine_completion_pct": 80,
  "would_recommend": true,
  "timeframe": "2_weeks",
  "feedback_text": "Great recommendations!",
  "improvement_suggestions": "Could add more budget options",
  "adverse_reactions": null,
  "product_ratings": { "product_1": 5, "product_3": 4 },
  "created_at": "2025-10-25T14:40:00Z",
  "message": "Feedback recorded successfully"
}
```

**⚠️ Important - Adverse Reactions:**

If a user reports adverse reactions in feedback (e.g., rash, itching, allergic reaction):
- The system SHOULD flag this for review
- The product SHOULD be marked for investigation
- Similar products SHOULD be avoided in future recommendations
- User SHOULD be advised to discontinue use and seek medical help if severe

**Example Adverse Reaction Feedback:**
```json
{
  "recommendation_id": "rec_20251025_001",
  "helpful_rating": 1,
  "adverse_reactions": ["severe_itching", "redness", "allergic_reaction"],
  "feedback_text": "I developed a severe allergic reaction to product #3. Please help me find alternatives.",
  "timeframe": "1_week"
}
```

**Error Responses:**

- **404 Not Found:** Recommendation not found

  ```json
  { "detail": "Recommendation 'invalid_id' not found" }
  ```

- **400 Bad Request:** Invalid rating (not 1-5)
  ```json
  { "detail": "helpful_rating must be between 1 and 5" }
  ```

**Curl Example:**

```bash
curl -X POST http://localhost:8000/api/v1/feedback \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "recommendation_id": "rec_20251025_001",
    "helpful_rating": 4,
    "product_satisfaction": 4,
    "would_recommend": true
  }' | jq '.'
```

---

### GET /api/v1/feedback/{recommendation_id}/stats

Get aggregated feedback statistics for a recommendation.

**Authentication:** Required (user token)

**Request Method:** GET

**Path Parameters:**

- `recommendation_id`: string (e.g., "rec_20251025_001")

**Request Headers:**

```
Authorization: Bearer <user_token>
```

**Response (HTTP 200 OK):**

```json
{
  "recommendation_id": "rec_20251025_001",
  "total_feedback_count": 5,
  "avg_helpful_rating": 4.2,
  "avg_product_satisfaction": 4.0,
  "avg_routine_completion_pct": 85.0,
  "recommend_percentage": 80.0,
  "rating_distribution": {
    "1_star": 0,
    "2_star": 0,
    "3_star": 1,
    "4_star": 3,
    "5_star": 1
  },
  "last_feedback_at": "2025-10-25T15:00:00Z"
}
```

**Error Responses:**

- **404 Not Found:** Recommendation not found
  ```json
  { "detail": "Recommendation 'invalid_id' not found" }
  ```

**Curl Example:**

```bash
curl -X GET http://localhost:8000/api/v1/feedback/rec_20251025_001/stats \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

---

### GET /api/v1/products/search

Search products by tag or ingredient.

**Authentication:** Required (user token)

**Request Method:** GET

**Query Parameters:**

- `tag`: string (optional) - Product tag (e.g., "acne", "oily_skin")
- `ingredient`: string (optional) - Ingredient name (partial match OK)
- `limit`: integer (optional, default: 50) - Max results
- `offset`: integer (optional, default: 0) - Pagination offset

**Request Headers:**

```
Authorization: Bearer <user_token>
```

**Response (HTTP 200 OK):**

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
      "tags": ["acne", "oily_skin"],
      "ingredients": ["salicylic acid 2%", "water", "cetyl alcohol"],
      "otc_verified": true,
      "prescription_required": false
    },
    {
      "id": 3,
      "name": "Niacinamide + Zinc Serum",
      "category": "treatment",
      "brand": "The Ordinary",
      "price": 5.99,
      "rating": 4.7,
      "tags": ["acne", "oil_control"],
      "ingredients": ["niacinamide 4%", "zinc pca"],
      "otc_verified": true,
      "prescription_required": false
    }
  ],
  "count": 2,
  "total": 15,
  "limit": 50,
  "offset": 0
}
```

**⚠️ OTC Verification Requirements:**

- ✅ `otc_verified: true` - ONLY products verified as OTC
- ✅ `prescription_required: false` - NO prescription medications
- ✅ NO controlled substances
- ✅ All products must be legally available without prescription
- ⚠️ DO NOT return:
  - Prescription retinoids (only OTC adapalene, retinol, or retinyl palmitate)
  - Prescription antibiotics
  - Corticosteroids (prescription strength)
  - Any controlled medications
```

**Notes:**

- Returns empty array if no matches (not 404)
- Ingredient search is partial (case-insensitive)
- Supports pagination with `limit` and `offset`

**Curl Examples:**

```bash
# Search by tag
curl -X GET "http://localhost:8000/api/v1/products/search?tag=acne" \
  -H "Authorization: Bearer $TOKEN" | jq '.'

# Search by ingredient
curl -X GET "http://localhost:8000/api/v1/products/search?ingredient=salicylic" \
  -H "Authorization: Bearer $TOKEN" | jq '.'

# Paginated search
curl -X GET "http://localhost:8000/api/v1/products/search?tag=acne&limit=10&offset=0" \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

---

## Admin Endpoints

### POST /admin/reload-rules

Reload recommendation rules from YAML configuration.

**Authentication:** Required (admin token)

**Request Method:** POST

**Request Headers:**

```
Content-Type: application/json
Authorization: Bearer <admin_token>
```

**Request Body:**

```json
{}
```

**Response (HTTP 200 OK):**

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

**Error Responses:**

- **403 Forbidden:** User is not admin

  ```json
  { "detail": "Admin access required" }
  ```

- **500 Internal Server Error:** Error reloading rules
  ```json
  { "detail": "Failed to reload rules: invalid YAML" }
  ```

**Curl Example:**

```bash
curl -X POST http://localhost:8000/admin/reload-rules \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{}' | jq '.'
```

---

### GET /admin/rule-logs

Get RuleLog entries (audit trail).

**Authentication:** Required (admin token)

**Request Method:** GET

**Query Parameters:**

- `recommendation_id`: string (optional) - Filter by recommendation
- `user_id`: integer (optional) - Filter by user
- `limit`: integer (optional, default: 50)
- `offset`: integer (optional, default: 0)

**Request Headers:**

```
Authorization: Bearer <admin_token>
```

**Response (HTTP 200 OK):**

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
    }
  ],
  "count": 2,
  "total": 47
}
```

**Curl Example:**

```bash
curl -X GET "http://localhost:8000/admin/rule-logs?recommendation_id=rec_20251025_001" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq '.'
```

---

## Testing

### Automated Testing Scripts

**Bash (Linux/Mac):**

```bash
chmod +x test_api.sh
./test_api.sh $TOKEN $ADMIN_TOKEN
```

**PowerShell (Windows):**

```powershell
.\test_api.ps1 -Token "YOUR_TOKEN" -AdminToken "ADMIN_TOKEN"
```

### Manual Testing with Postman

1. Import collection: `Haski-API.postman_collection.json` (if available)
2. Set variables:
   - `base_url`: http://localhost:8000
   - `token`: Your JWT token
   - `admin_token`: Admin JWT token
3. Run requests in order

---

## Curl Examples

### 1. Generate Recommendation (Oily + Acne)

```bash
curl -X POST http://localhost:8000/api/v1/recommend \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
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
  }' | jq '.'
```

### 2. Generate Recommendation (Dry + Eczema)

```bash
curl -X POST http://localhost:8000/api/v1/recommend \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "method": "direct_analysis",
    "skin_type": "dry",
    "hair_type": "straight",
    "conditions_detected": ["eczema", "dryness"],
    "confidence_scores": {"eczema": 0.75, "dryness": 0.88},
    "age": 35,
    "gender": "M",
    "allergies": ["fragrance"],
    "skin_sensitivity": "sensitive"
  }' | jq '.'
```

### 3. Generate Recommendation with Escalation (Sudden Hair Loss)

```bash
curl -X POST http://localhost:8000/api/v1/recommend \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "method": "direct_analysis",
    "skin_type": "normal",
    "hair_type": "straight",
    "conditions_detected": ["sudden_hair_loss"],
    "confidence_scores": {"sudden_hair_loss": 0.95},
    "age": 35,
    "gender": "F",
    "include_skincare": false,
    "include_products": false
  }' | jq '.'
```

### 4. Submit Feedback (Positive)

```bash
curl -X POST http://localhost:8000/api/v1/feedback \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "recommendation_id": "rec_20251025_001",
    "helpful_rating": 5,
    "product_satisfaction": 5,
    "routine_completion_pct": 95,
    "would_recommend": true,
    "timeframe": "1_week",
    "feedback_text": "Excellent recommendations! My skin improved significantly.",
    "product_ratings": {"product_1": 5, "product_3": 5}
  }' | jq '.'
```

### 5. Submit Feedback (Negative)

```bash
curl -X POST http://localhost:8000/api/v1/feedback \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "recommendation_id": "rec_20251025_001",
    "helpful_rating": 2,
    "product_satisfaction": 1,
    "routine_completion_pct": 20,
    "would_recommend": false,
    "timeframe": "3_months",
    "feedback_text": "Products caused allergic reaction.",
    "adverse_reactions": ["redness", "itching"]
  }' | jq '.'
```

### 6. Get Feedback Statistics

```bash
curl -X GET http://localhost:8000/api/v1/feedback/rec_20251025_001/stats \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

### 7. Search Products by Tag

```bash
# Search for acne products
curl -X GET "http://localhost:8000/api/v1/products/search?tag=acne" \
  -H "Authorization: Bearer $TOKEN" | jq '.'

# Search for oil control products
curl -X GET "http://localhost:8000/api/v1/products/search?tag=oil_control" \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

### 8. Search Products by Ingredient

```bash
# Search for salicylic acid products
curl -X GET "http://localhost:8000/api/v1/products/search?ingredient=salicylic" \
  -H "Authorization: Bearer $TOKEN" | jq '.'

# Search for niacinamide products
curl -X GET "http://localhost:8000/api/v1/products/search?ingredient=niacinamide" \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

### 9. Reload Rules (Admin)

```bash
curl -X POST http://localhost:8000/admin/reload-rules \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{}' | jq '.'
```

### 10. Get Rule Logs (Admin)

```bash
# Get all rule logs
curl -X GET "http://localhost:8000/admin/rule-logs" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq '.'

# Get rule logs for specific recommendation
curl -X GET "http://localhost:8000/admin/rule-logs?recommendation_id=rec_20251025_001" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq '.'

# Get rule logs for specific user
curl -X GET "http://localhost:8000/admin/rule-logs?user_id=5" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq '.'
```

---

## Status Codes Reference

| Code | Meaning                                     |
| ---- | ------------------------------------------- |
| 200  | OK - Request successful                     |
| 201  | Created - Resource created                  |
| 400  | Bad Request - Invalid input                 |
| 401  | Unauthorized - Missing/invalid token        |
| 403  | Forbidden - Insufficient permissions        |
| 404  | Not Found - Resource doesn't exist          |
| 422  | Validation Error - Schema validation failed |
| 500  | Server Error - Internal error               |

---

## Common Issues & Troubleshooting

### Issue: 401 Unauthorized

**Cause:** Missing or invalid JWT token

**Solution:**

```bash
# Get new token
curl -X POST http://localhost:8000/api/auth/login \
  -d '{"username": "user", "password": "password"}'

# Use token in Authorization header
export TOKEN="new_token_here"
```

### Issue: 404 Not Found (Recommendation)

**Cause:** Invalid or expired recommendation_id

**Solution:**

```bash
# Generate new recommendation first
curl -X POST http://localhost:8000/api/v1/recommend \
  -H "Authorization: Bearer $TOKEN" \
  -d '...' | jq '.recommendation_id'

# Use returned ID for feedback
```

### Issue: 422 Validation Error

**Cause:** Invalid request schema

**Solution:** Check request body matches schema. Common issues:

- `helpful_rating` not 1-5
- `conditions_detected` not an array
- Missing required fields

### Issue: Empty Products Array

**Cause:** Products not seeded in database

**Solution:**

```bash
# Load sample products
# Run: python manage.py seed_products
# Or use admin panel to add products
```

---

## ⚠️ Safety & Compliance

### Required Disclaimers

**Every API Response MUST include:**
```
"disclaimer": "Informational only — not medical advice. Consult a healthcare professional for medical concerns."
```

### Escalation Handling (High Priority Cases)

**Trigger Conditions:**
- Severe skin infections
- Severe rashes (coverage > 50% of body)
- Sudden hair loss (telogen effluvium symptoms)
- Severe acne (cystic, widespread)
- Recurring conditions (symptoms for >3 months)
- Any condition mentioning `see_dermatologist` rule

**Required Response Fields:**
```json
{
  "escalation": {
    "level": "urgent",
    "high_priority": true,
    "message": "..clearly advise seeking medical attention...",
    "condition": "specific_condition_name",
    "recommended_next_steps": [...]
  },
  "metadata": {
    "medical_referral_required": true,
    "escalation_triggered": true
  }
}
```

### OTC Product Verification

**ALLOWED Products:**
- ✅ Over-the-counter skincare (cleansers, moisturizers, serums)
- ✅ Non-prescription acne treatments (benzoyl peroxide, salicylic acid)
- ✅ Non-prescription hair care products
- ✅ OTC adapalene (Differin) - only OTC retinoid
- ✅ Dietary supplements (vitamins, minerals, plant extracts)
- ✅ Sunscreens (SPF protection)
- ✅ Face masks, peels (cosmetic use)

**PROHIBITED Products:**
- ❌ Prescription retinoids (tretinoin, tazarotene, isotretinoin)
- ❌ Prescription antibiotics (clindamycin, doxycycline, etc.)
- ❌ Prescription-strength corticosteroids
- ❌ Prescription hormonal treatments
- ❌ Any controlled medications
- ❌ Prescription-only medical devices
- ❌ Pharmaceutical injections or procedures

**Verification Requirements:**
- Every product in database MUST have: `otc_verified: true`
- Admin panel MUST require: OTC status verification before adding products
- Regular audits MUST verify all products maintain OTC status

### Adverse Reaction Handling

**If User Reports Adverse Reactions:**
1. STOP recommending that product/ingredient immediately
2. Flag product for admin review
3. Recommend discontinuing use
4. Advise seeking medical help if severe
5. Create alternative recommendation without similar ingredients
6. Log incident for compliance tracking

**Adverse Reaction Response Example:**
```json
{
  "status": "adverse_reaction_noted",
  "message": "Thank you for reporting this. We've marked this product for review and will avoid similar products in future recommendations.",
  "guidance": "If symptoms persist or worsen, please seek medical attention from a dermatologist.",
  "next_steps": "You will receive alternative recommendations without similar ingredients"
}
```

### Liability Protections

**Frontend MUST Display:**
1. Disclaimer on every recommendation view
2. "Consult Healthcare Provider" button/link
3. Warning banner for escalations (red background)
4. Instruction to discontinue if adverse reactions occur
5. Contact info for healthcare advice (NOT provided by app)

**Backend MUST Enforce:**
1. Disclaimer in every API response
2. `high_priority: true` flag for urgent cases
3. Separate escalation handling path
4. Audit logging for all recommendations
5. Error handling for missing/invalid data

### Compliance Checklist

- ✅ All responses include disclaimer
- ✅ Escalations have `high_priority: true`
- ✅ All products are OTC-verified
- ✅ No prescription medications suggested
- ✅ Adverse reactions logged and tracked
- ✅ Terms of Service available
- ✅ Privacy Policy available
- ✅ Medical advice disclaimers prominent
- ✅ Escalation paths clearly marked
- ✅ Audit trail maintained (RuleLog)

---

## Next Steps

1. **Authentication:** Setup login and get JWT token
2. **Testing:** Run test_api.sh or test_api.ps1
3. **Integration:** Integrate endpoints into frontend
4. **Monitoring:** Setup error tracking and analytics
5. **Deployment:** Deploy to staging then production
6. **Compliance:** Review with legal before production launch

---

**API Version:** 1.0
**Last Updated:** October 2025
**Status:** Production Ready ✅
