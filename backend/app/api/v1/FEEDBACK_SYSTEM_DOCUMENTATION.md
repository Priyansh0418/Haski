# Feedback System API Documentation

## Overview

The feedback system collects user ratings, comments, and behavioral data on recommendations. It provides:

- **Feedback Submission** - Users rate recommendations and provide detailed feedback
- **Aggregate Statistics** - Track recommendation quality metrics
- **User Insights** - Calculate satisfaction, adherence, and product quality trends
- **Rule Analytics** - Link feedback to specific rules that generated recommendations
- **Data-Driven Improvements** - Identify which recommendations work best

---

## Endpoints

### POST /api/v1/feedback/feedback

Submit feedback on a recommendation.

**Authentication:** Required (JWT token)

**Request Body:**

```json
{
  "recommendation_id": "rec_20251024_001",
  "helpful_rating": 4,
  "product_satisfaction": 4,
  "routine_completion_pct": 75,
  "timeframe": "2_weeks",
  "feedback_text": "Great recommendations, easy to follow!",
  "improvement_suggestions": "Could include more budget options",
  "adverse_reactions": null,
  "would_recommend": true,
  "product_ratings": {
    "cleanser": 5,
    "treatment": 4,
    "moisturizer": 3
  }
}
```

**Field Descriptions:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `recommendation_id` | string | Yes | ID of recommendation being reviewed |
| `helpful_rating` | integer | No | 1-5: How helpful was the recommendation? |
| `product_satisfaction` | integer | No | 1-5: How satisfied with recommended products? |
| `routine_completion_pct` | integer | No | 0-100: What % of routine did you complete? |
| `timeframe` | string | No | When providing feedback: `1_week`, `2_weeks`, `4_weeks`, `8_weeks` |
| `feedback_text` | string | No | User comments on the recommendation |
| `improvement_suggestions` | string | No | Suggestions for improving recommendations |
| `adverse_reactions` | string | No | Any negative reactions experienced |
| `would_recommend` | boolean | No | Would you recommend to friends? |
| `product_ratings` | object | No | Individual product ratings (1-5) |

**Response (201 Created):**

```json
{
  "feedback_id": 42,
  "recommendation_id": "rec_20251024_001",
  "user_id": 5,
  "status": "success",
  "message": "Feedback recorded successfully",
  "feedback_data": {
    "helpful_rating": 4,
    "product_satisfaction": 4,
    "routine_completion_pct": 75,
    "would_recommend": true,
    "has_adverse_reactions": false,
    "timeframe": "2_weeks"
  },
  "stats": {
    "recommendation_id": "rec_20251024_001",
    "total_feedbacks": 5,
    "avg_helpful_rating": 4.2,
    "avg_product_satisfaction": 4.0,
    "avg_routine_completion_pct": 82,
    "would_recommend_count": 4,
    "would_not_recommend_count": 1,
    "adverse_reactions": 0,
    "helpful_feedbacks": 5,
    "not_helpful_feedbacks": 0,
    "ratings_distribution": {
      "1": 0,
      "2": 0,
      "3": 1,
      "4": 2,
      "5": 2
    }
  },
  "insights": {
    "user_satisfaction_level": "high",
    "routine_adherence": "good",
    "product_quality_assessment": "high_quality",
    "recommendations_for_improvement": [],
    "escalations": []
  },
  "rules_applied": [
    {
      "rule_id": "r001",
      "rule_name": "Oily + Acne",
      "rule_category": "skincare",
      "details": {
        "condition": "acne",
        "severity": "moderate",
        "step": 1,
        "action": "Gentle cleanser"
      }
    },
    {
      "rule_id": "r007",
      "rule_name": "Blackheads + Pores",
      "rule_category": "skincare",
      "details": {
        "condition": "blackheads",
        "severity": "mild",
        "action": "Pore cleanser"
      }
    }
  ],
  "created_at": "2025-10-24T14:30:00"
}
```

**Response Fields:**

- `feedback_id` - Unique ID of saved feedback
- `stats` - Aggregated stats for this recommendation (see stats endpoint)
- `insights` - Calculated insights based on feedback (see insights section)
- `rules_applied` - Rules that generated the recommendation (linked from RuleLog)

**Error Responses:**

```json
// 404: Recommendation not found
{
  "detail": "Recommendation 'rec_invalid' not found"
}

// 403: User can't submit feedback for another user's recommendation
{
  "detail": "User can only submit feedback for their own recommendations"
}

// 422: Validation error
{
  "detail": "helpful_rating must be between 1 and 5"
}
```

---

### GET /api/v1/feedback/feedback/{recommendation_id}/stats

Get aggregated feedback statistics for a recommendation.

**Authentication:** Required (JWT token)

**Path Parameters:**

- `recommendation_id` - String ID of recommendation (e.g., `rec_20251024_001`)

**Example:**

```bash
GET /api/v1/feedback/feedback/rec_20251024_001/stats
Authorization: Bearer <JWT_TOKEN>
```

**Response (200 OK):**

```json
{
  "recommendation_id": "rec_20251024_001",
  "total_feedbacks": 5,
  "avg_helpful_rating": 4.2,
  "avg_product_satisfaction": 4.0,
  "avg_routine_completion_pct": 82.0,
  "would_recommend_count": 4,
  "would_not_recommend_count": 1,
  "adverse_reactions": 0,
  "helpful_feedbacks": 5,
  "not_helpful_feedbacks": 0,
  "ratings_distribution": {
    "1": 0,
    "2": 0,
    "3": 1,
    "4": 2,
    "5": 2
  },
  "rules_applied": [
    {
      "rule_id": "r001",
      "rule_name": "Oily + Acne",
      "rule_category": "skincare",
      "details": {
        "condition": "acne",
        "severity": "moderate",
        "step": 1,
        "action": "Gentle cleanser"
      }
    }
  ],
  "recommendation_metadata": {
    "recommendation_id": "rec_20251024_001",
    "created_at": "2025-10-24T12:30:00",
    "conditions_analyzed": ["acne", "blackheads"],
    "rules_applied_ids": ["r001", "r007"]
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `total_feedbacks` | integer | Number of feedback submissions |
| `avg_helpful_rating` | float | Average helpful rating (1-5) |
| `avg_product_satisfaction` | float | Average product satisfaction (1-5) |
| `avg_routine_completion_pct` | float | Average routine completion percentage |
| `would_recommend_count` | integer | Number who would recommend |
| `would_not_recommend_count` | integer | Number who would not recommend |
| `adverse_reactions` | integer | Count of adverse reactions reported |
| `helpful_feedbacks` | integer | Count of ratings 4-5 (helpful) |
| `not_helpful_feedbacks` | integer | Count of ratings 1-2 (not helpful) |
| `ratings_distribution` | object | Breakdown of 1-5 ratings |
| `rules_applied` | array | Rules that generated recommendation (with details) |
| `recommendation_metadata` | object | Original recommendation info |

---

### GET /api/v1/feedback/feedbacks/user/{user_id}/summary

Get summary of all feedback submitted by a user.

**Authentication:** Required (JWT token)

**Path Parameters:**

- `user_id` - Integer ID of user (must be current user)

**Example:**

```bash
GET /api/v1/feedback/feedbacks/user/5/summary
Authorization: Bearer <JWT_TOKEN>
```

**Response (200 OK):**

```json
{
  "user_id": 5,
  "total_recommendations": 10,
  "total_feedbacks_given": 7,
  "overall_avg_helpful_rating": 4.1,
  "overall_avg_product_satisfaction": 4.0,
  "overall_avg_routine_completion_pct": 78.0,
  "would_recommend_rate": 0.86,
  "adverse_reactions_count": 1,
  "recommendations": [
    {
      "recommendation_id": "rec_20251024_001",
      "created_at": "2025-10-24T12:30:00",
      "feedback_recorded": true,
      "helpful_rating": 4,
      "product_satisfaction": 4,
      "routine_completion_pct": 75
    },
    {
      "recommendation_id": "rec_20251024_002",
      "created_at": "2025-10-23T10:15:00",
      "feedback_recorded": false,
      "helpful_rating": null,
      "product_satisfaction": null,
      "routine_completion_pct": null
    }
  ]
}
```

---

## Insights System

The feedback system automatically calculates insights based on submitted data.

### Satisfaction Levels

**High Satisfaction**
- Trigger: `helpful_rating >= 4`
- Action: Recommendation is working well

**Medium Satisfaction**
- Trigger: `helpful_rating == 3`
- Action: Recommendation acceptable but could improve

**Low Satisfaction**
- Trigger: `helpful_rating <= 2`
- Action: Flag for review, adjust rules

### Routine Adherence

**Excellent**
- Trigger: `routine_completion_pct >= 80`
- Meaning: User completing most of routine

**Good**
- Trigger: `routine_completion_pct >= 60`
- Meaning: User completing majority

**Fair**
- Trigger: `routine_completion_pct >= 40`
- Meaning: User completing half

**Poor**
- Trigger: `routine_completion_pct < 40`
- Meaning: Routine too complex or not applicable

### Product Quality Assessment

**High Quality**
- Trigger: `product_satisfaction >= 4`
- Meaning: Products are well-matched

**Acceptable**
- Trigger: `product_satisfaction == 3`
- Meaning: Products are okay

**Needs Improvement**
- Trigger: `product_satisfaction <= 2`
- Meaning: Different products should be recommended

### Automatic Recommendations

The system suggests improvements when:

1. **Low Adherence** - "Routine may be too complex - consider simplifying steps"
2. **Low Satisfaction** - "Recommendation quality appears low - review rule set"
3. **Adverse Reactions** - "Review product ingredients for potential allergens"
4. **Won't Recommend** - "User would not recommend - investigate dissatisfaction"

### Escalations

Automatic escalations triggered by:

1. **Adverse Reactions** (HIGH)
   - Message: "User reported adverse reactions: [details]"
   - Action: Flag for manual review

---

## Data Models

### RecommendationFeedback Table

```sql
CREATE TABLE recommendation_feedbacks (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  analysis_id INTEGER NOT NULL,
  recommendation_id INTEGER NOT NULL,
  
  -- Ratings (1-5 scale)
  helpful_rating INTEGER,                -- 1-5: not helpful to very helpful
  product_satisfaction INTEGER,          -- 1-5: not satisfied to very satisfied
  routine_completion_pct INTEGER,        -- 0-100: % of routine completed
  
  -- Feedback
  timeframe VARCHAR(50),                 -- 1_week, 2_weeks, 4_weeks, 8_weeks
  feedback_text TEXT,                    -- User comments
  improvement_suggestions TEXT,          -- Suggestions
  adverse_reactions TEXT,                -- Any negative reactions
  
  -- Behavior
  would_recommend BOOLEAN,               -- Would recommend to friends?
  product_ratings JSON,                  -- {cleanser: 5, treatment: 4, ...}
  
  -- Timestamps
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL
);
```

### RuleLog Integration

The feedback system links to `RuleLog` entries to show which rules were applied:

```python
# Query applied rules for a recommendation
rules = db.query(RuleLog).filter(
    RuleLog.analysis_id == recommendation.analysis_id,
    RuleLog.applied == True
).all()

# Each rule includes:
# - rule_id: "r001"
# - rule_name: "Oily + Acne"
# - rule_category: "skincare"
# - details: {...}
```

---

## Usage Examples

### Example 1: Submit Feedback with Full Details

```bash
curl -X POST http://localhost:8000/api/v1/feedback/feedback \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recommendation_id": "rec_20251024_001",
    "helpful_rating": 5,
    "product_satisfaction": 5,
    "routine_completion_pct": 95,
    "timeframe": "4_weeks",
    "feedback_text": "Excellent recommendations! Clear routine and products work great.",
    "would_recommend": true,
    "product_ratings": {
      "cleanser": 5,
      "treatment": 5,
      "moisturizer": 5,
      "sunscreen": 5
    }
  }'
```

**Response includes:**
- Feedback confirmation with ID
- Updated aggregate statistics
- Insights (high satisfaction, excellent adherence, etc.)
- Rules that generated the recommendation

### Example 2: Report Adverse Reactions

```bash
curl -X POST http://localhost:8000/api/v1/feedback/feedback \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recommendation_id": "rec_20251024_001",
    "helpful_rating": 1,
    "adverse_reactions": "Severe skin irritation and redness after using recommended treatment",
    "would_recommend": false
  }'
```

**Response includes:**
- Adverse reaction escalation (HIGH priority)
- Recommendation to review ingredients
- Flag for manual review

### Example 3: Get Recommendation Stats

```bash
curl -X GET http://localhost:8000/api/v1/feedback/feedback/rec_20251024_001/stats \
  -H "Authorization: Bearer $TOKEN"
```

**Shows:**
- 10 total feedbacks
- 4.2 average helpful rating
- 82% average routine completion
- 9 would recommend, 1 would not
- Rating distribution (helpful vs not)
- Rules that generated recommendation

### Example 4: Get User Summary

```bash
curl -X GET http://localhost:8000/api/v1/feedback/feedbacks/user/5/summary \
  -H "Authorization: Bearer $TOKEN"
```

**Shows:**
- 42 total recommendations
- 35 feedbacks given
- 4.1 overall average rating
- 86% would recommend rate
- List of all recommendations with feedback status

---

## Frontend Integration

### React Component Example

```typescript
import React, { useState } from 'react';

interface FeedbackFormProps {
  recommendationId: string;
  token: string;
  onSuccess?: (data: any) => void;
}

export const FeedbackForm: React.FC<FeedbackFormProps> = ({
  recommendationId,
  token,
  onSuccess
}) => {
  const [rating, setRating] = useState<number>(5);
  const [satisfaction, setSatisfaction] = useState<number>(5);
  const [completion, setCompletion] = useState<number>(80);
  const [feedback, setFeedback] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/feedback/feedback', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          recommendation_id: recommendationId,
          helpful_rating: rating,
          product_satisfaction: satisfaction,
          routine_completion_pct: completion,
          feedback_text: feedback,
          would_recommend: rating >= 4
        })
      });

      if (!response.ok) {
        throw new Error('Failed to submit feedback');
      }

      const data = await response.json();
      
      if (data.insights?.escalations?.length > 0) {
        alert('⚠️ Adverse reaction reported - our team will review');
      }
      
      if (onSuccess) {
        onSuccess(data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="feedback-form">
      <h2>How helpful was this recommendation?</h2>
      
      <div className="rating-group">
        <label>Helpfulness (1-5)</label>
        <select value={rating} onChange={(e) => setRating(Number(e.target.value))}>
          <option value={1}>1 - Not helpful</option>
          <option value={2}>2 - Somewhat unhelpful</option>
          <option value={3}>3 - Neutral</option>
          <option value={4}>4 - Helpful</option>
          <option value={5}>5 - Very helpful</option>
        </select>
      </div>

      <div className="rating-group">
        <label>Product Satisfaction (1-5)</label>
        <select value={satisfaction} onChange={(e) => setSatisfaction(Number(e.target.value))}>
          <option value={1}>1 - Not satisfied</option>
          <option value={2}>2 - Somewhat satisfied</option>
          <option value={3}>3 - Neutral</option>
          <option value={4}>4 - Satisfied</option>
          <option value={5}>5 - Very satisfied</option>
        </select>
      </div>

      <div className="completion-group">
        <label>Routine Completion: {completion}%</label>
        <input
          type="range"
          min="0"
          max="100"
          value={completion}
          onChange={(e) => setCompletion(Number(e.target.value))}
        />
      </div>

      <div className="textarea-group">
        <label>Additional Feedback</label>
        <textarea
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
          placeholder="Share any comments or suggestions..."
        />
      </div>

      <button type="submit" disabled={loading}>
        {loading ? 'Submitting...' : 'Submit Feedback'}
      </button>

      {error && <div className="error">{error}</div>}
    </form>
  );
};
```

---

## Analytics & Metrics

### Key Metrics to Track

1. **Recommendation Quality**
   - Average helpful rating
   - % of recommendations rated 4-5 stars

2. **User Engagement**
   - % of recommendations with feedback
   - Feedback submission rate over time

3. **Product Performance**
   - Which products get highest satisfaction
   - Adverse reaction frequency

4. **Rule Effectiveness**
   - Average rating by applied rule
   - Which rule combinations work best

5. **User Behavior**
   - Average routine completion
   - Completion by user segment
   - Recommendation conversion to purchase

### Dashboards

Suggested dashboards to build:

1. **Admin Dashboard**
   - Overall recommendation quality
   - High/low performing rules
   - Adverse reactions (alerts)

2. **User Dashboard**
   - My recommendations history
   - My feedback trends
   - Products I've tried

3. **Analyst Dashboard**
   - Rule performance metrics
   - User cohort analysis
   - Trend analysis (improving/declining)

---

## Best Practices

### Collecting Feedback

1. **Timing** - Request feedback 2-4 weeks after recommendation
2. **Incentives** - Consider rewarding feedback submission
3. **UX** - Make feedback form easy and quick to complete
4. **Reminders** - Send reminders for high-value feedback
5. **Escalation** - Immediately flag adverse reactions

### Using Feedback

1. **Monitor** - Track recommendation quality metrics daily
2. **Alert** - Set up alerts for adverse reactions
3. **Improve** - Adjust rules based on feedback patterns
4. **Communicate** - Tell users how feedback improved system

### Privacy

1. **Anonymize** - Remove PII from public analytics
2. **Consent** - Get explicit consent for data usage
3. **Retention** - Archive old feedback appropriately
4. **Security** - Encrypt sensitive health data

---

## Troubleshooting

**Q: Why is my feedback not showing stats?**
A: Stats are calculated from all submitted feedbacks. Your first feedback will show single-entry averages.

**Q: Can I edit feedback?**
A: Currently no - submit new feedback to update ratings. Feedback is immutable for audit trail.

**Q: What does "poor" routine adherence mean?**
A: User only completed <40% of the recommended routine - consider simplifying.

**Q: How are adverse reactions handled?**
A: Automatically flagged with HIGH escalation for immediate review and user follow-up.

---

## Summary

The feedback system provides complete user feedback collection, analysis, and insights for:

✅ Measuring recommendation quality
✅ Tracking user satisfaction trends
✅ Identifying problematic products/rules
✅ Detecting adverse reactions (escalation)
✅ Data-driven rule improvements
✅ User engagement metrics

**Total Implementation:** 500+ lines (endpoint + tests)
**Database Integration:** Full RecommendationFeedback + RuleLog link
**Production Ready:** Yes
