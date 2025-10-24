# Recommender Endpoint API Documentation

## Overview

The `/recommend` endpoint generates personalized skincare and haircare recommendations based on user analysis and profile data. It leverages the rule engine to apply YAML rules and returns tailored recommendations with product suggestions and escalation flags.

## Endpoints

### POST /api/v1/recommend

Generate personalized recommendations.

**Authentication:** Required (JWT token in Authorization header)

**Request Body:**

Two methods supported:

#### Method 1: Using Existing Analysis (recommended)

```json
{
  "method": "analysis_id",
  "analysis_id": 123,
  "include_diet": true,
  "include_products": true,
  "include_skincare": true,
  "include_lifestyle": false
}
```

**Parameters:**

- `method` (string, required): Must be `"analysis_id"`
- `analysis_id` (integer, required): ID of existing Analysis record from database
- `include_diet` (boolean, optional): Include dietary recommendations (default: true)
- `include_products` (boolean, optional): Include product recommendations (default: true)
- `include_skincare` (boolean, optional): Include skincare routine (default: true)
- `include_lifestyle` (boolean, optional): Include lifestyle tips (default: true)

**Advantages:**

- Uses real analysis from image processing
- Links to user history
- Can be reused for multiple recommendations

#### Method 2: Direct Analysis Data

```json
{
  "method": "direct_analysis",
  "skin_type": "oily",
  "hair_type": "straight",
  "conditions_detected": ["acne", "blackheads"],
  "confidence_scores": {
    "acne": 0.92,
    "blackheads": 0.87
  },
  "age": 25,
  "skin_sensitivity": "normal",
  "pregnancy_status": "not_pregnant",
  "allergies": ["benzoyl_peroxide"],
  "skin_tone": "medium",
  "gender": "F",
  "budget": "medium",
  "include_diet": true,
  "include_products": true
}
```

**Parameters:**

- `method` (string, required): Must be `"direct_analysis"`
- `skin_type` (string, required): One of: `oily`, `dry`, `combination`, `sensitive`, `normal`
- `hair_type` (string, optional): One of: `straight`, `wavy`, `curly`, `coily`
- `conditions_detected` (array, required): List of detected conditions
  - Examples: `acne`, `blackheads`, `eczema`, `rosacea`, `fine_lines`, `wrinkles`
- `confidence_scores` (object, optional): Confidence for each condition (0-1 or 0-100)
- `age` (integer, optional): User age
- `skin_sensitivity` (string, optional): One of: `normal`, `sensitive`, `very_sensitive`
- `pregnancy_status` (string, optional): One of: `pregnant`, `breastfeeding`, `not_pregnant`
- `allergies` (array, optional): List of allergies (e.g., `["benzoyl_peroxide"]`)
- `skin_tone` (string, optional): One of: `light`, `medium`, `dark`, `very_dark`
- `gender` (string, optional): `M`, `F`, or `O`
- `budget` (string, optional): One of: `low`, `medium`, `high`

**Advantages:**

- Ad-hoc recommendations
- No database lookup required
- Fast generation

---

### GET /api/v1/recommendations/{recommendation_id}

Retrieve a previously saved recommendation.

**Authentication:** Required

**Path Parameters:**

- `recommendation_id` (string): ID of recommendation to retrieve

**Example:**

```bash
GET /api/v1/recommendations/rec_20251024_143000
```

**Response:**

```json
{
  "recommendation_id": "rec_20251024_143000",
  "created_at": "2025-10-24T14:30:00",
  "content": {
    "routines": [...],
    "products": [...],
    "diet": [...],
    "warnings": [...],
    "escalation": {...}
  },
  "source": "rule_v1",
  "rules_applied": ["r001", "r007"]
}
```

---

### GET /api/v1/recommendations

List user's recent recommendations.

**Authentication:** Required

**Query Parameters:**

- `limit` (integer, optional): Number of recommendations to return (default: 10, max: 50)
- `offset` (integer, optional): Offset for pagination (default: 0)

**Example:**

```bash
GET /api/v1/recommendations?limit=20&offset=0
```

**Response:**

```json
{
  "total": 42,
  "limit": 20,
  "offset": 0,
  "recommendations": [
    {
      "recommendation_id": "rec_20251024_143000",
      "created_at": "2025-10-24T14:30:00",
      "source": "rule_v1",
      "rules_applied": ["r001", "r007"],
      "rules_count": 2
    },
    ...
  ]
}
```

---

## Response Format

### Success Response (201 Created)

```json
{
  "recommendation_id": "rec_20251024_143000",
  "created_at": "2025-10-24T14:30:00.123456",

  "routines": [
    {
      "step": "morning",
      "routine_text": "Gentle exfoliating cleanser (Neutrogena) → Niacinamide serum → Non-comedogenic sunscreen SPF 60",
      "source_rules": ["r001"]
    },
    {
      "step": "evening",
      "routine_text": "Gentle exfoliating cleanser → Salicylic acid 2% (2-3x per week) → Light moisturizer",
      "source_rules": ["r001"]
    },
    {
      "step": "weekly",
      "routine_text": "Clay mask or BHA to manage pore congestion",
      "source_rules": ["r001", "r007"]
    }
  ],

  "diet_recommendations": [
    {
      "action": "increase",
      "items": [
        "omega-3 fatty acids (salmon, walnuts, flax seeds)",
        "water intake (2-3 liters daily)",
        "zinc-rich foods (oysters, beef, pumpkin seeds)",
        "antioxidants (berries, green tea)"
      ],
      "source_rules": ["r001"]
    },
    {
      "action": "limit",
      "items": [
        "dairy products (can trigger acne)",
        "high-glycemic foods (refined sugars)",
        "excess oils and fried foods"
      ],
      "source_rules": ["r001"]
    }
  ],

  "recommended_products": [
    {
      "id": 2,
      "name": "Salicylic Acid 2% Solution",
      "brand": "The Ordinary",
      "external_id": "ordinary_sa_001",
      "category": "treatment",
      "price": 5.9,
      "url": "https://theordinary.deciem.com/...",
      "tags": ["exfoliating", "BHA", "acne-fighting"],
      "rating": 4.3,
      "review_count": 5890,
      "dermatologically_safe": true,
      "reason": "For acne control and exfoliation",
      "source_rules": ["r001"]
    },
    {
      "id": 6,
      "name": "Niacinamide 10% + Zinc 1%",
      "brand": "The Ordinary",
      "external_id": "ordinary_niacinamide_001",
      "category": "serum",
      "price": 5.9,
      "url": "https://theordinary.deciem.com/...",
      "tags": ["pore-minimizing", "oil-control"],
      "rating": 4.4,
      "review_count": 8920,
      "dermatologically_safe": true,
      "reason": "For oil control and pore minimization",
      "source_rules": ["r001", "r007"]
    },
    {
      "id": 4,
      "name": "Anthelios Fluid SPF 60",
      "brand": "La Roche-Posay",
      "external_id": "lrp_sunscreen_001",
      "category": "sunscreen",
      "price": 34.0,
      "url": "https://www.laroche-posay.com/...",
      "tags": ["broad-spectrum", "non-comedogenic"],
      "rating": 4.4,
      "review_count": 890,
      "dermatologically_safe": true,
      "reason": "Non-comedogenic UV protection for acne-prone skin",
      "source_rules": ["r001"]
    }
  ],

  "product_count": 3,

  "escalation": null, // or escalation object if present

  "applied_rules": ["r001", "r007"],
  "rules_count": 2,

  "metadata": {
    "total_rules_checked": 9,
    "rules_matched": 2,
    "generated_at": "2025-10-24T14:30:00.123456",
    "product_tags_searched": [
      "exfoliating",
      "oil-control",
      "pore-cleansing",
      "acne-fighting"
    ],
    "tags_count": 4
  }
}
```

### Escalation Response (with medical escalation)

When escalation is present, the response includes:

```json
{
  "recommendation_id": "rec_...",
  "created_at": "...",

  "routines": [...],
  "diet_recommendations": [...],
  "recommended_products": [...],

  "escalation": {
    "level": "urgent",
    "message": "URGENT - See dermatologist immediately. Likely requires prescription oral antibiotics or isotretinoin.",
    "see_dermatologist": true,
    "high_priority": true
  },

  "applied_rules": ["r008"],
  "metadata": {...}
}
```

**Escalation Levels:**

- `urgent`: Immediate dermatologist consultation needed
- `caution`: Recommend professional consultation
- `warning`: Note for awareness
- `none`: No escalation

**`see_dermatologist` flag:** `true` if level is `urgent` or `emergency`

**`high_priority` flag:** `true` if any escalation present

---

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Invalid analysis data: Invalid skin_type: invalid_type"
}
```

**Common causes:**

- Invalid `skin_type` value
- Missing required fields
- Invalid `conditions_detected` format

---

### 401 Unauthorized

```json
{
  "detail": "Not authenticated"
}
```

**Solution:** Include valid JWT token in Authorization header

```
Authorization: Bearer <token>
```

---

### 404 Not Found

```json
{
  "detail": "Analysis 99999 not found"
}
```

**Cause:** `analysis_id` doesn't exist or doesn't belong to user

---

### 500 Internal Server Error

```json
{
  "detail": "Failed to generate recommendation"
}
```

**Causes:**

- Rule engine initialization failed
- Database connection error
- Unhandled exception in recommendation generation

---

## Usage Examples

### Example 1: Oily Skin with Acne (Using Analysis ID)

```bash
curl -X POST http://localhost:8000/api/v1/recommend \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "analysis_id",
    "analysis_id": 123,
    "include_diet": true,
    "include_products": true
  }'
```

**Flow:**

1. Load Analysis #123 from database
2. Load user's Profile
3. Apply rules (r001 - Oily + Acne, r007 - Blackheads + Pores)
4. Query Products table for recommended tags
5. Save RecommendationRecord
6. Return recommendation with 3+ products

---

### Example 2: Direct Analysis (Dry Skin with Eczema)

```bash
curl -X POST http://localhost:8000/api/v1/recommend \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "direct_analysis",
    "skin_type": "dry",
    "conditions_detected": ["eczema", "dry_patches"],
    "age": 30,
    "skin_sensitivity": "normal",
    "allergies": ["fragrance"],
    "include_diet": true,
    "include_products": true
  }'
```

**Flow:**

1. Validate provided analysis data
2. Load user's Profile for allergies/pregnancy status
3. Apply rules (r002 - Dry + Eczema)
4. Query Products for hydrating/barrier-repair tags
5. Return recommendation without database storage (optional)

---

### Example 3: Retrieve Saved Recommendation

```bash
curl -X GET http://localhost:8000/api/v1/recommendations/rec_20251024_143000 \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

---

### Example 4: List User's Recommendations

```bash
curl -X GET "http://localhost:8000/api/v1/recommendations?limit=20&offset=0" \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

---

## Integration with Frontend

### JavaScript/TypeScript Example

```typescript
// Generate recommendation
async function generateRecommendation(analysisId: number) {
  const response = await fetch("/api/v1/recommend", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      method: "analysis_id",
      analysis_id: analysisId,
      include_diet: true,
      include_products: true,
    }),
  });

  if (!response.ok) {
    throw new Error(await response.text());
  }

  const recommendation = await response.json();

  // Check for escalation
  if (recommendation.escalation?.high_priority) {
    showUrgentAlert(recommendation.escalation.message);
  }

  // Display recommendation
  displayRoutines(recommendation.routines);
  displayProducts(recommendation.recommended_products);
  displayDiet(recommendation.diet_recommendations);
}

// Retrieve saved recommendation
async function getRecommendation(recommendationId: string) {
  const response = await fetch(`/api/v1/recommendations/${recommendationId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error("Failed to retrieve recommendation");
  }

  return response.json();
}

// List recommendations
async function listRecommendations(limit = 10) {
  const response = await fetch(`/api/v1/recommendations?limit=${limit}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error("Failed to list recommendations");
  }

  return response.json();
}
```

---

## Database Schema

### RecommendationRecord Table

```sql
CREATE TABLE recommendation_records (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  analysis_id INTEGER,
  recommendation_id VARCHAR(100) UNIQUE,
  content TEXT,  -- JSON stored as string
  source VARCHAR(50),  -- "rule_v1", "ml_v1", etc.
  conditions_analyzed JSON,
  rules_applied JSON,  -- ["r001", "r007"]
  generation_time_ms INTEGER,
  created_at DATETIME,
  updated_at DATETIME
);
```

### RuleLog Table

```sql
CREATE TABLE rule_logs (
  id INTEGER PRIMARY KEY,
  analysis_id INTEGER,
  rule_id VARCHAR(100),
  applied BOOLEAN,
  details JSON,
  created_at DATETIME
);
```

---

## Performance Considerations

- **Rule Engine Initialization:** ~100-200ms (first load)
- **Rule Evaluation:** ~30-50ms for 9 rules
- **Database Queries:** ~20-50ms (product lookup, save)
- **Total Response Time:** Typically 100-300ms

**Optimization:**

1. Engine initialized once at module load
2. Use `analysis_id` method to avoid re-processing
3. Product queries indexed by tags and external_id

---

## Next Steps

1. ✅ Endpoint created
2. ✅ Database models integrated
3. → Add to main.py router
4. → Test with real JWT tokens
5. → Frontend integration
6. → Analytics and logging
7. → ML feedback loop
