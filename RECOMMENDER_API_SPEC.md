# Recommender System API Specifications

## Overview

The Recommender API translates skin/hair analysis + user profile → actionable recommendations.

---

## Endpoints

### 1. Generate Recommendations

**Route**: `POST /api/v1/recommender/recommend`

**Authentication**: Required (Bearer token)

**Request Schema**:

```json
{
  "method": "analysis_id", // or "direct_analysis"
  "analysis_id": 5, // if using analysis_id method

  // OR provide direct analysis:
  "analysis": {
    "skin_type": "dry",
    "hair_type": "coily",
    "conditions_detected": ["acne", "blackheads"],
    "confidence_scores": {
      "dry": 0.87,
      "acne": 0.72,
      "blackheads": 0.65
    }
  },

  // User profile (optional if analysis_id provided):
  "user_profile": {
    "age": 28,
    "gender": "F",
    "budget": "medium", // "low", "medium", "high"
    "allergies": ["sulfates", "fragrance"],
    "skin_tone": "medium", // "light", "medium", "dark"
    "skin_sensitivity": "normal",
    "pregnancy_status": "not_pregnant"
  },

  // Options:
  "include_skincare": true,
  "include_diet": true,
  "include_products": true,
  "include_lifestyle": true
}
```

**Response Schema** (201 Created):

```json
{
  "recommendation_id": "rec_20251024_001",
  "analysis_id": 5,
  "user_id": 3,
  "created_at": "2025-10-24T20:55:00Z",
  "expires_at": "2025-11-24T20:55:00Z",

  "analysis_summary": {
    "skin_type": "dry",
    "hair_type": "coily",
    "conditions": ["acne", "blackheads"],
    "severity_overall": "moderate"
  },

  "skincare_routine": {
    "duration_weeks": 4,
    "difficulty": "easy",
    "expected_cost": "low",
    "steps": [
      {
        "step": 1,
        "action": "Gentle facial cleanser",
        "frequency": "2x daily",
        "timing": "morning and night",
        "duration_in_routine": 1,
        "why": "Removes excess oil without stripping dry skin",
        "expected_results": "Reduced oiliness within 1 week",
        "ingredients_to_look_for": ["glycerin", "hyaluronic acid"],
        "ingredients_to_avoid": ["sulfates", "alcohol"],
        "warning": null
      },
      {
        "step": 2,
        "action": "Salicylic acid (BHA) treatment",
        "frequency": "1-3x weekly",
        "timing": "evening",
        "duration_in_routine": 2,
        "why": "Unclogs pores and prevents blackheads",
        "expected_results": "Visible improvement in 2-3 weeks",
        "ingredients_to_look_for": ["salicylic acid", "glycerin"],
        "ingredients_to_avoid": ["essential oils"],
        "warning": "May cause initial dryness or 'purging' of congestion"
      },
      {
        "step": 3,
        "action": "Rich, non-comedogenic moisturizer",
        "frequency": "2x daily",
        "timing": "after cleanser and treatment",
        "duration_in_routine": 1,
        "why": "Maintains skin barrier and prevents over-drying",
        "expected_results": "Less irritation, better tolerance",
        "ingredients_to_look_for": ["ceramides", "hyaluronic acid", "peptides"],
        "ingredients_to_avoid": ["heavy oils", "lanolin"],
        "warning": null
      },
      {
        "step": 4,
        "action": "Broad-spectrum SPF 30+ sunscreen",
        "frequency": "daily",
        "timing": "morning, reapply every 2 hours if outdoors",
        "duration_in_routine": 0,
        "why": "Prevents dark marks and hyperpigmentation",
        "expected_results": "Even skin tone, no new marks",
        "ingredients_to_look_for": ["zinc oxide", "titanium dioxide"],
        "ingredients_to_avoid": ["oxybenzone"],
        "warning": null
      }
    ]
  },

  "diet_recommendations": {
    "hydration": {
      "target": "2.5-3L water daily",
      "why": "Skin hydration starts from inside"
    },
    "foods_to_add": [
      {
        "food": "Salmon",
        "why": "Omega-3 fatty acids reduce inflammation",
        "frequency": "2-3x per week",
        "serving": "150g (palm-sized piece)"
      },
      {
        "food": "Spinach & leafy greens",
        "why": "Antioxidants, vitamins A and C",
        "frequency": "Daily",
        "serving": "1-2 cups raw or half cooked"
      },
      {
        "food": "Berries",
        "why": "Antioxidants, low glycemic index",
        "frequency": "Daily",
        "serving": "1 cup mixed berries"
      },
      {
        "food": "Bone broth",
        "why": "Collagen and amino acids for skin repair",
        "frequency": "3-4x per week",
        "serving": "1-2 cups"
      },
      {
        "food": "Almonds & walnuts",
        "why": "Omega-3s and vitamin E",
        "frequency": "Daily",
        "serving": "Handful (28g)"
      }
    ],
    "foods_to_limit": [
      {
        "food": "Dairy (milk, cheese)",
        "why": "Casein and whey can trigger acne in some",
        "limit_to": "1-2x per week or avoid"
      },
      {
        "food": "High-glycemic carbs (white bread, sugar)",
        "why": "Can trigger inflammation and acne",
        "limit_to": "Occasional"
      },
      {
        "food": "Excess iodine (seaweed, iodized salt)",
        "why": "Can trigger or worsen acne",
        "limit_to": "Minimal"
      }
    ]
  },

  "product_recommendations": {
    "cleanser": {
      "product_id": 42,
      "name": "CeraVe Hydrating Facial Cleanser",
      "brand": "CeraVe",
      "category": "facial cleanser",
      "price_usd": 8.99,
      "url": "https://www.cerave.com/skincare/hydrating-cleanser",
      "why_recommended": "Sulfate-free, contains glycerin and hyaluronic acid, perfect for dry + acne-prone skin",
      "ingredients": ["water", "glycerin", "hyaluronic acid", "ceramides"],
      "safe_for_allergies": true,
      "rating": 4.5,
      "review_count": 2340,
      "in_stock": true,
      "alternatives": [
        {
          "name": "Vanicream Gentle Facial Cleanser",
          "price_usd": 7.5,
          "reason": "Even gentler, more budget-friendly"
        }
      ]
    },

    "treatment": {
      "product_id": 156,
      "name": "The Ordinary Salicylic Acid 2%",
      "brand": "Deciem",
      "category": "acne treatment",
      "price_usd": 5.9,
      "url": "https://theordinary.deciem.com/product/rbn-salicylic-acid-2pct-solution-30ml",
      "why_recommended": "Affordable, effective BHA for blackheads and acne. No fragrance or essential oils.",
      "ingredients": ["salicylic acid", "glycerin"],
      "safe_for_allergies": true,
      "rating": 4.3,
      "review_count": 5890,
      "in_stock": true,
      "usage_notes": "Start 1-2x per week, can increase to 3-4x per week",
      "alternatives": [
        {
          "name": "Paula's Choice 2% BHA Liquid",
          "price_usd": 44.0,
          "reason": "Premium option, slower acting but gentler"
        }
      ]
    },

    "moisturizer": {
      "product_id": 89,
      "name": "Vanicream Moisturizing Cream",
      "brand": "Vanicream",
      "category": "moisturizer",
      "price_usd": 7.99,
      "url": "https://www.vanicream.com/moisturizing-cream",
      "why_recommended": "Rich but non-comedogenic, free of fragrance and dyes, ideal for dry skin with acne",
      "ingredients": ["ceramides", "hyaluronic acid", "petrolatum"],
      "safe_for_allergies": true,
      "rating": 4.6,
      "review_count": 1230,
      "in_stock": true,
      "alternatives": [
        {
          "name": "CeraVe Moisturizing Cream",
          "price_usd": 14.99,
          "reason": "Slightly lighter texture, similar benefits"
        }
      ]
    },

    "sunscreen": {
      "product_id": 203,
      "name": "La Roche-Posay Anthelios Fluid SPF 60",
      "brand": "La Roche-Posay",
      "category": "sunscreen",
      "price_usd": 34.0,
      "url": "https://www.laroche-posay.com/products/sun-care/anthelios",
      "why_recommended": "Lightweight, non-comedogenic, mineral + chemical hybrid, prevents PIH (dark marks)",
      "ingredients": ["zinc oxide", "avobenzone", "niacinamide"],
      "safe_for_allergies": true,
      "rating": 4.4,
      "review_count": 890,
      "in_stock": true,
      "note": "Sunscreen is CRITICAL when using acne treatments"
    }
  },

  "total_estimated_cost": {
    "initial_setup": 56.88, // All products
    "monthly_replacement": 18.5,
    "currency": "USD"
  },

  "lifestyle_recommendations": [
    {
      "category": "sleep",
      "tip": "Aim for 7-9 hours nightly",
      "why": "Sleep deprivation increases cortisol, triggering acne"
    },
    {
      "category": "stress",
      "tip": "Practice stress-relief: meditation, exercise, yoga",
      "why": "Stress hormones can worsen acne"
    },
    {
      "category": "exercise",
      "tip": "Wash face immediately after sweating",
      "why": "Sweat can mix with bacteria and clog pores"
    },
    {
      "category": "hygiene",
      "tip": "Change pillowcase 2-3x per week",
      "why": "Prevents bacteria transfer to face"
    }
  ],

  "safety_flags": {
    "severe_condition": false,
    "requires_professional": false,
    "escalation_needed": false,

    "warnings": [
      "Salicylic acid may cause initial dryness or 'purging' - this is normal",
      "Always wear sunscreen when using acne treatments to prevent dark marks",
      "Avoid combining multiple exfoliants - use only salicylic acid"
    ],

    "escalation": null, // null if no escalation needed

    "disclaimer": "These recommendations are NOT medical advice. If conditions worsen or persist after 8 weeks, consult a dermatologist. For severe reactions, seek immediate medical attention."
  },

  "timeline": {
    "week_1": "Skin adjusts, may see increased oiliness as barrier stabilizes",
    "week_2": "Possible 'purging' as salicylic acid brings congestion to surface",
    "week_3": "Improvement in blackheads and congestion becomes visible",
    "week_4": "Significant improvement in acne, skin tone more even"
  },

  "what_to_expect": "Follow this routine for 4 weeks before assessing results. Some people see improvement earlier, others take full 4-6 weeks.",

  "next_steps": [
    "Start routine immediately",
    "Take 'before' photo for comparison",
    "Rate feedback after 2 weeks and again at 4 weeks",
    "Provide product satisfaction feedback",
    "Share any adverse reactions in comments"
  ]
}
```

---

### 2. Submit Feedback

**Route**: `POST /api/v1/recommender/feedback`

**Authentication**: Required (Bearer token)

**Request Schema**:

```json
{
  "recommendation_id": "rec_20251024_001",
  "helpful_rating": 4, // 1-5: not helpful to very helpful
  "product_satisfaction": 4, // 1-5: not satisfied to very satisfied
  "routine_completion_pct": 75, // 0-100: % of routine followed
  "timeframe": "2_weeks", // "1_week", "2_weeks", "4_weeks", "8_weeks"
  "feedback_text": "Great recommendations! The cleanser worked well for my dry skin. Will update after full 4 weeks.",
  "improvement_suggestions": "Could suggest more budget-friendly alternatives",
  "adverse_reactions": null, // Any negative reactions
  "would_recommend": true,
  "product_ratings": {
    "cleanser": 5,
    "treatment": 4,
    "moisturizer": 5,
    "sunscreen": 4
  }
}
```

**Response Schema** (201 Created):

```json
{
  "feedback_id": "fb_20251024_001",
  "recommendation_id": "rec_20251024_001",
  "user_id": 3,
  "status": "recorded",
  "message": "Thank you! Your feedback helps us improve recommendations for all users.",
  "insights": {
    "your_rating": 4,
    "average_rating": 3.8,
    "helpful_vs_unhelpful": "87% found similar recommendations helpful"
  },
  "created_at": "2025-10-24T21:00:00Z"
}
```

---

### 3. Get Recommendation History

**Route**: `GET /api/v1/recommender/history?user_id=3&limit=10`

**Authentication**: Required (Bearer token)

**Response Schema** (200 OK):

```json
{
  "user_id": 3,
  "total_recommendations": 5,
  "recommendations": [
    {
      "recommendation_id": "rec_20251024_001",
      "analysis_id": 5,
      "created_at": "2025-10-24T20:55:00Z",
      "conditions": ["acne", "blackheads"],
      "helpful_rating": 4,
      "product_satisfaction": 4,
      "routine_completion_pct": 75,
      "feedback_recorded": true,
      "has_feedback": true
    },
    {
      "recommendation_id": "rec_20251010_042",
      "analysis_id": 3,
      "created_at": "2025-10-10T15:30:00Z",
      "conditions": ["dry_skin"],
      "helpful_rating": 3,
      "product_satisfaction": 3,
      "routine_completion_pct": 50,
      "feedback_recorded": true,
      "has_feedback": true
    }
  ]
}
```

---

### 4. Get Recommendation by ID

**Route**: `GET /api/v1/recommender/{recommendation_id}`

**Authentication**: Required (Bearer token)

**Response**: Full recommendation object (same as generate endpoint)

---

## Error Handling

### 400 Bad Request

```json
{
  "error": "Invalid request",
  "detail": "analysis_id or analysis must be provided"
}
```

### 404 Not Found

```json
{
  "error": "Not found",
  "detail": "Recommendation rec_20251024_001 not found"
}
```

### 422 Unprocessable Entity

```json
{
  "error": "Validation error",
  "detail": "helpful_rating must be between 1 and 5"
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal server error",
  "detail": "Failed to generate recommendations"
}
```

---

## Rate Limiting

- **Recommended Requests**: Max 10 per minute per user
- **Feedback Requests**: Max 20 per minute per user
- **History Requests**: Max 30 per minute per user

---

## Data Flow

```
1. User takes photo
2. Analysis generated: {skin_type, conditions, ...}
3. Frontend calls POST /recommender/recommend with analysis_id
4. Backend:
   - Loads user profile
   - Loads analysis
   - Applies rules for each condition
   - Filters by budget/allergies
   - Checks safety
   - Formats response
5. Frontend displays recommendation
6. User follows routine for 2-4 weeks
7. User submits feedback via POST /recommender/feedback
8. Backend stores feedback in recommendation_feedback table
9. Feedback used to improve future recommendations
```

---

## Testing

### Test with cURL

```bash
# Generate recommendation
curl -X POST "http://localhost:8000/api/v1/recommender/recommend" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_id": 5,
    "include_diet": true,
    "include_products": true
  }'

# Submit feedback
curl -X POST "http://localhost:8000/api/v1/recommender/feedback" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recommendation_id": "rec_20251024_001",
    "helpful_rating": 4,
    "product_satisfaction": 4,
    "routine_completion_pct": 75,
    "feedback_text": "Great recommendations!"
  }'

# Get history
curl "http://localhost:8000/api/v1/recommender/history?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Integration with Frontend

```typescript
// TypeScript example
const generateRecommendations = async (analysisId: number) => {
  const response = await fetch("/api/v1/recommender/recommend", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      analysis_id: analysisId,
      include_diet: true,
      include_products: true,
    }),
  });

  const data = await response.json();
  return data; // Full recommendation object
};

const submitFeedback = async (recommendationId: string, rating: number) => {
  const response = await fetch("/api/v1/recommender/feedback", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      recommendation_id: recommendationId,
      helpful_rating: rating,
      product_satisfaction: rating,
      routine_completion_pct: 75,
      feedback_text: "Helpful recommendations!",
    }),
  });

  return await response.json();
};
```

---

**API Version**: v1  
**Last Updated**: 2025-10-24  
**Status**: Specification Complete, Ready for Implementation
