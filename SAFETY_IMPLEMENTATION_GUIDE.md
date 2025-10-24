# Safety Implementation Guide for Backend Developers

## Overview

This guide shows how to implement the required safety features in the Haski backend. All requirements are **mandatory** and must be tested before deployment.

---

## 1. Disclaimer Implementation

### 1.1 Add Disclaimer to Response Schema

Update `backend/app/schemas/pydantic_schemas.py`:

```python
from pydantic import BaseModel
from typing import Optional, List

class RecommendationResponse(BaseModel):
    """Recommendation response with required safety disclaimer."""

    # Add this disclaimer field at the top
    disclaimer: str = "Informational only — not medical advice. Consult a healthcare professional for medical concerns."

    recommendation_id: str
    routines: List[dict]
    products: List[dict]
    diet: List[dict]
    escalation: Optional[dict] = None
    applied_rules: List[str]
    metadata: dict

    class Config:
        schema_extra = {
            "example": {
                "disclaimer": "Informational only — not medical advice. Consult a healthcare professional for medical concerns.",
                "recommendation_id": "rec_20251025_001",
                "routines": [...],
                "products": [...],
                "diet": [...],
                "escalation": None,
                "applied_rules": ["r001", "r002"],
                "metadata": {...}
            }
        }
```

### 1.2 Update Endpoint to Include Disclaimer

Update `backend/app/api/v1/recommend.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from backend.app.schemas.pydantic_schemas import RecommendationResponse

router = APIRouter()

@router.post("/recommend", response_model=RecommendationResponse, status_code=201)
async def generate_recommendation(
    request: RecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> RecommendationResponse:
    """
    Generate skincare/haircare recommendations.

    ⚠️ IMPORTANT: All responses include a disclaimer that this is not medical advice.
    """
    try:
        # Generate recommendation logic...
        recommendation = engine.generate(request)

        # Build response with REQUIRED disclaimer field
        response = RecommendationResponse(
            disclaimer="Informational only — not medical advice. Consult a healthcare professional for medical concerns.",  # MANDATORY
            recommendation_id=recommendation.id,
            routines=recommendation.routines,
            products=recommendation.products,
            diet=recommendation.diet,
            escalation=recommendation.escalation,
            applied_rules=recommendation.applied_rules,
            metadata={
                "generated_at": datetime.utcnow().isoformat(),
                "processing_time_ms": processing_time,
                "analysis_method": request.method
            }
        )

        return response

    except Exception as e:
        logger.error(f"Recommendation generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate recommendation")
```

### 1.3 Test Disclaimer

```bash
# Test 1: Verify disclaimer in basic recommendation
curl -X POST http://localhost:8000/api/v1/recommend \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"method":"direct_analysis","skin_type":"oily","conditions_detected":["acne"],"age":25,"gender":"F"}' \
  | jq '.disclaimer'

# Expected output:
# "Informational only — not medical advice. Consult a healthcare professional for medical concerns."

# Test 2: Verify disclaimer is present (not null/empty)
curl ... | jq '.disclaimer | length > 0'
# Expected: true
```

---

## 2. Escalation with High Priority Flag

### 2.1 Update Escalation Schema

Update `backend/app/schemas/pydantic_schemas.py`:

```python
class EscalationResponse(BaseModel):
    """Escalation response for severe conditions requiring medical attention."""

    level: str  # "urgent", "caution", "warning"
    condition: str  # e.g., "sudden_hair_loss", "severe_infection"
    high_priority: bool  # ⚠️ MANDATORY: Set to True for medical referrals
    message: str  # Clear guidance for user
    recommended_next_steps: List[str]  # List of actions user should take

    class Config:
        schema_extra = {
            "example": {
                "level": "urgent",
                "condition": "sudden_hair_loss",
                "high_priority": True,
                "message": "Sudden hair loss can indicate underlying health issues. PLEASE SEEK IMMEDIATE MEDICAL ATTENTION FROM A DERMATOLOGIST.",
                "recommended_next_steps": [
                    "Contact a dermatologist or physician immediately",
                    "Prepare documentation of symptoms and timeline",
                    "Do not delay seeking professional medical advice"
                ]
            }
        }
```

### 2.2 Update Escalation Detection Logic

Update `backend/app/services/escalation_handler.py` (or your equivalent):

```python
class EscalationHandler:
    """Detect and handle severe conditions requiring medical attention."""

    # Conditions that trigger high_priority = true
    URGENT_CONDITIONS = {
        "sudden_hair_loss",
        "severe_skin_infection",
        "severe_rash",
        "severe_acne_cystic",
        "severe_eczema_flare",
    }

    def detect_escalation(self, analysis: dict) -> Optional[EscalationResponse]:
        """
        Detect if conditions warrant escalation.

        ⚠️ MANDATORY: Return high_priority=True for urgent conditions.
        """
        conditions = analysis.get("conditions_detected", [])

        for condition in conditions:
            if condition in self.URGENT_CONDITIONS:
                return EscalationResponse(
                    level="urgent",
                    condition=condition,
                    high_priority=True,  # ⚠️ MANDATORY FLAG
                    message=self._get_urgent_message(condition),
                    recommended_next_steps=self._get_next_steps(condition)
                )

        # Check for severe confidence scores
        confidence = analysis.get("confidence_scores", {})
        if any(score > 0.9 for score in confidence.values()):
            # Could be escalated - check with dermatologist rule
            if self._check_dermatologist_rule(conditions):
                return EscalationResponse(
                    level="urgent",
                    condition="see_dermatologist",
                    high_priority=True,  # ⚠️ MANDATORY
                    message="A healthcare professional should evaluate this condition.",
                    recommended_next_steps=[
                        "Consult with a dermatologist or physician",
                        "Prepare list of symptoms"
                    ]
                )

        return None

    def _get_urgent_message(self, condition: str) -> str:
        """Get urgent medical guidance message."""
        messages = {
            "sudden_hair_loss": "Sudden hair loss can indicate underlying health issues. PLEASE SEEK IMMEDIATE MEDICAL ATTENTION FROM A DERMATOLOGIST.",
            "severe_skin_infection": "Severe skin infections can worsen quickly. PLEASE SEEK IMMEDIATE MEDICAL ATTENTION.",
            "severe_rash": "Severe rashes require professional evaluation. PLEASE CONTACT A DERMATOLOGIST OR PHYSICIAN IMMEDIATELY.",
        }
        return messages.get(condition, "This condition requires professional medical evaluation.")

    def _get_next_steps(self, condition: str) -> List[str]:
        """Get recommended next steps."""
        return [
            "Contact a dermatologist or physician immediately",
            "Prepare documentation of symptoms and timeline",
            "Note any recent stressors or changes",
            "Do not delay seeking professional medical advice"
        ]
```

### 2.3 Update Response with High Priority

Update `backend/app/api/v1/recommend.py`:

```python
@router.post("/recommend", response_model=RecommendationResponse, status_code=201)
async def generate_recommendation(request: RecommendationRequest, ...):
    # ... existing code ...

    # Check for escalation
    escalation = escalation_handler.detect_escalation(analysis)

    # Build escalation response if needed
    escalation_response = None
    if escalation:
        escalation_response = {
            "level": escalation.level,
            "condition": escalation.condition,
            "high_priority": escalation.high_priority,  # ⚠️ KEY FIELD
            "message": escalation.message,
            "recommended_next_steps": escalation.recommended_next_steps
        }

    # Update metadata for escalations
    metadata = {
        "generated_at": datetime.utcnow().isoformat(),
        "processing_time_ms": processing_time,
        "analysis_method": request.method,
    }

    if escalation:
        metadata["escalation_triggered"] = True
        metadata["medical_referral_required"] = escalation.high_priority

    return RecommendationResponse(
        disclaimer="Informational only — not medical advice. URGENT: Seek immediate medical attention." if escalation else "Informational only — not medical advice. Consult a healthcare professional for medical concerns.",
        recommendation_id=recommendation.id,
        routines=recommendation.routines if not escalation else [],  # Empty for urgent cases
        products=recommendation.products if not escalation else [],
        diet=recommendation.diet,
        escalation=escalation_response,
        applied_rules=recommendation.applied_rules,
        metadata=metadata
    )
```

### 2.4 Test High Priority Flag

```bash
# Test with escalation condition (sudden hair loss)
curl -X POST http://localhost:8000/api/v1/recommend \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "method":"direct_analysis",
    "conditions_detected":["sudden_hair_loss"],
    "confidence_scores":{"sudden_hair_loss":0.95},
    "age":35,"gender":"F"
  }' \
  | jq '.escalation.high_priority'

# Expected output: true

# Verify in metadata
curl ... | jq '.metadata.medical_referral_required'
# Expected output: true
```

---

## 3. OTC Products Only Verification

### 3.1 Add OTC Fields to Product Schema

Update `backend/app/models/db_models.py`:

```python
class Product(Base):
    """Product model with OTC verification."""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float)
    rating = Column(Float)
    ingredients = Column(JSON)
    tags = Column(JSON)

    # ⚠️ MANDATORY OTC VERIFICATION FIELDS
    otc_verified: bool = Column(Boolean, default=False, nullable=False)  # MUST be True
    prescription_required: bool = Column(Boolean, default=False, nullable=False)  # MUST be False
    verified_by: str = Column(String)  # Admin who verified
    verified_at: datetime = Column(DateTime, default=datetime.utcnow)

    # Prohibited substances check
    is_prohibited: bool = Column(Boolean, default=False)  # Flag if suspicious

    class Config:
        orm_mode = True
```

### 3.2 Add OTC Fields to Response Schema

Update `backend/app/schemas/pydantic_schemas.py`:

```python
class ProductResponse(BaseModel):
    """Product response with OTC verification."""

    id: int
    name: str
    brand: str
    category: str
    price: float
    rating: float
    tags: List[str]
    ingredients: List[str]

    # ⚠️ MANDATORY OTC FIELDS
    otc_verified: bool  # Must be True
    prescription_required: bool  # Must be False

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Gentle Salicylic Acid Cleanser",
                "brand": "CeraVe",
                "category": "cleanser",
                "price": 8.99,
                "rating": 4.5,
                "tags": ["acne", "oily_skin"],
                "ingredients": ["salicylic acid 2%", "water"],
                "otc_verified": True,  # MANDATORY
                "prescription_required": False  # MANDATORY
            }
        }
```

### 3.3 Update Recommendation Endpoint

Update `backend/app/api/v1/recommend.py`:

```python
def _get_products_for_recommendation(
    analysis: dict,
    db: Session,
    engine
) -> List[ProductResponse]:
    """
    Get products for recommendation.

    ⚠️ MANDATORY: ONLY return OTC products.
    """
    # Get recommended products from engine
    product_ids = engine.get_product_ids(analysis)

    # Filter ONLY OTC products
    products = db.query(Product).filter(
        Product.id.in_(product_ids),
        Product.otc_verified == True,  # ⚠️ MANDATORY FILTER
        Product.prescription_required == False,  # ⚠️ MANDATORY FILTER
        Product.is_prohibited == False  # ⚠️ SAFETY CHECK
    ).all()

    if not products:
        logger.warning(f"No OTC products found for conditions: {analysis.get('conditions_detected')}")

    # Convert to response schema (automatically includes otc_verified and prescription_required)
    return [ProductResponse.from_orm(p) for p in products]
```

### 3.4 Test OTC Products

```bash
# Test 1: Verify all products in recommendation are OTC
curl -X POST http://localhost:8000/api/v1/recommend \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"method":"direct_analysis","skin_type":"oily","conditions_detected":["acne"],"age":25,"gender":"F"}' \
  | jq '.products[] | {name, otc_verified, prescription_required}'

# Expected output:
# {
#   "name": "Product Name",
#   "otc_verified": true,
#   "prescription_required": false
# }

# Test 2: Verify no products with prescription_required=true
curl ... | jq '.products | map(select(.prescription_required == true)) | length'
# Expected: 0

# Test 3: Product search
curl "http://localhost:8000/api/v1/products/search?tag=acne" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.results | map(select(.otc_verified == false)) | length'
# Expected: 0
```

---

## 4. Adverse Reactions Handling

### 4.1 Add Adverse Reactions to Feedback Schema

Update `backend/app/schemas/pydantic_schemas.py`:

```python
class FeedbackRequest(BaseModel):
    """Feedback request including adverse reactions."""

    recommendation_id: str
    helpful_rating: int  # 1-5
    product_satisfaction: Optional[int] = None
    routine_completion_pct: Optional[int] = None
    would_recommend: Optional[bool] = None
    timeframe: Optional[str] = None
    feedback_text: Optional[str] = None

    # ⚠️ MANDATORY: Adverse reactions tracking
    adverse_reactions: Optional[List[str]] = None  # e.g., ["redness", "itching", "allergic_reaction"]
    product_ratings: Optional[dict] = None

    @validator('helpful_rating')
    def validate_rating(cls, v):
        if not 1 <= v <= 5:
            raise ValueError('helpful_rating must be between 1 and 5')
        return v
```

### 4.2 Handle Adverse Reactions in Endpoint

Update `backend/app/api/v1/feedback.py`:

```python
@router.post("/feedback", response_model=FeedbackResponse, status_code=201)
async def submit_feedback(
    request: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit feedback on recommendation.

    ⚠️ MANDATORY: Handle adverse reactions.
    """
    # Validate recommendation exists
    recommendation = db.query(RecommendationRecord).filter(
        RecommendationRecord.id == request.recommendation_id
    ).first()

    if not recommendation:
        raise HTTPException(status_code=404, detail=f"Recommendation '{request.recommendation_id}' not found")

    # Store feedback
    feedback = RecommendationFeedback(
        recommendation_id=request.recommendation_id,
        user_id=current_user.id,
        helpful_rating=request.helpful_rating,
        product_satisfaction=request.product_satisfaction,
        routine_completion_pct=request.routine_completion_pct,
        would_recommend=request.would_recommend,
        timeframe=request.timeframe,
        feedback_text=request.feedback_text,
        adverse_reactions=request.adverse_reactions,  # ⚠️ STORE REACTIONS
        product_ratings=request.product_ratings,
        created_at=datetime.utcnow()
    )

    db.add(feedback)
    db.commit()

    # ⚠️ CRITICAL: Handle adverse reactions
    if request.adverse_reactions and len(request.adverse_reactions) > 0:
        await _handle_adverse_reactions(
            recommendation,
            request,
            current_user,
            db
        )

    return FeedbackResponse.from_orm(feedback)


async def _handle_adverse_reactions(recommendation, feedback_request, user, db):
    """
    Handle adverse reactions reported by user.

    ⚠️ MANDATORY: Flag product, create incident, alert admin.
    """
    logger.warning(f"ADVERSE REACTION reported by user {user.id}: {feedback_request.adverse_reactions}")

    # 1. Flag products in recommendation for review
    for product_id in recommendation.product_ids:
        product = db.query(Product).filter(Product.id == product_id).first()
        if product:
            product.is_prohibited = True
            product.verified_by = "ADVERSE_REACTION_FLAG"
            product.verified_at = datetime.utcnow()

    # 2. Create incident for admin review
    incident = AdverseReactionIncident(
        user_id=user.id,
        recommendation_id=recommendation.id,
        reactions=feedback_request.adverse_reactions,
        product_ids=recommendation.product_ids,
        feedback_text=feedback_request.feedback_text,
        severity="high" if any(r in ["severe_allergic_reaction", "anaphylaxis"] for r in feedback_request.adverse_reactions) else "medium",
        created_at=datetime.utcnow(),
        status="new"
    )

    db.add(incident)

    # 3. Send admin alert
    await _send_admin_alert(incident, user)

    # 4. Log to audit
    audit_logger.log_adverse_reaction(incident)

    db.commit()


async def _send_admin_alert(incident: AdverseReactionIncident, user: User):
    """Send alert to admin team."""
    message = f"""
    ⚠️ ADVERSE REACTION REPORTED

    User: {user.email} (ID: {user.id})
    Reactions: {', '.join(incident.reactions)}
    Products: {incident.product_ids}
    Severity: {incident.severity}
    Time: {incident.created_at}

    Incident ID: {incident.id}
    Action Required: Review products and user recommendations
    """

    # Send to admin email/Slack
    await send_admin_notification(message)
```

### 4.3 Test Adverse Reactions

```bash
# Test: Submit feedback with adverse reactions
curl -X POST http://localhost:8000/api/v1/feedback \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "recommendation_id":"rec_20251025_001",
    "helpful_rating":1,
    "adverse_reactions":["redness","itching","allergic_reaction"],
    "feedback_text":"I developed a severe allergic reaction to product"
  }' | jq '.'

# Expected:
# - HTTP 201 Created
# - adverse_reactions stored
# - Product flagged (visible in admin)
# - Admin alert sent
```

---

## 5. Testing & Validation

### 5.1 Unit Test Template

Create `backend/tests/test_safety_requirements.py`:

```python
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

class TestSafetyRequirements:
    """Test all mandatory safety requirements."""

    def test_recommendation_includes_disclaimer(self, user_token):
        """Test 1: Every recommendation includes disclaimer."""
        response = client.post(
            "/api/v1/recommend",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "method": "direct_analysis",
                "skin_type": "oily",
                "conditions_detected": ["acne"],
                "age": 25,
                "gender": "F"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert "disclaimer" in data
        assert "not medical advice" in data["disclaimer"]
        assert len(data["disclaimer"]) > 0

    def test_escalation_has_high_priority_flag(self, user_token):
        """Test 2: Escalations include high_priority flag."""
        response = client.post(
            "/api/v1/recommend",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "method": "direct_analysis",
                "conditions_detected": ["sudden_hair_loss"],
                "confidence_scores": {"sudden_hair_loss": 0.95},
                "age": 35,
                "gender": "F"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["escalation"] is not None
        assert data["escalation"]["high_priority"] == True
        assert "SEEK MEDICAL ATTENTION" in data["escalation"]["message"]

    def test_products_otc_verified(self, user_token):
        """Test 3: All products are OTC verified."""
        response = client.post(
            "/api/v1/recommend",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "method": "direct_analysis",
                "skin_type": "oily",
                "conditions_detected": ["acne"],
                "age": 25,
                "gender": "F"
            }
        )

        assert response.status_code == 201
        data = response.json()

        for product in data["products"]:
            assert product["otc_verified"] == True
            assert product["prescription_required"] == False

    def test_adverse_reactions_stored(self, user_token, recommendation_id):
        """Test 4: Adverse reactions are stored."""
        response = client.post(
            "/api/v1/feedback",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "recommendation_id": recommendation_id,
                "helpful_rating": 1,
                "adverse_reactions": ["redness", "itching"],
                "feedback_text": "Allergic reaction"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["adverse_reactions"] == ["redness", "itching"]

if __name__ == "__main__":
    pytest.main([__file__])
```

### 5.2 Run Safety Tests

```bash
# Run all safety tests
pytest backend/tests/test_safety_requirements.py -v

# Run specific test
pytest backend/tests/test_safety_requirements.py::TestSafetyRequirements::test_recommendation_includes_disclaimer -v
```

---

## 6. Deployment Checklist

Before deploying to production:

- [ ] Disclaimer in all responses ✅
- [ ] High priority flag for escalations ✅
- [ ] OTC products only ✅
- [ ] Adverse reactions tracked ✅
- [ ] All unit tests passing ✅
- [ ] Integration tests passing ✅
- [ ] Safety tests passing ✅
- [ ] Frontend displays disclaimer ✅
- [ ] Frontend displays escalation warnings ✅
- [ ] Legal review completed ✅
- [ ] Terms of Service in place ✅
- [ ] Privacy Policy in place ✅

---

## 7. Support & Troubleshooting

### Issue: Disclaimer not appearing

**Solution:** Verify:

1. Schema includes `disclaimer` field
2. Endpoint returns `disclaimer` in response
3. Response model is `RecommendationResponse`
4. Database doesn't have stale cache

```python
# Force disclaimer in all responses
response_dict = {
    "disclaimer": "Informational only — not medical advice. Consult a healthcare professional for medical concerns.",
    # ... rest of response
}
```

### Issue: High priority flag not set

**Solution:**

1. Check escalation detection logic
2. Verify condition is in `URGENT_CONDITIONS` list
3. Test with conditions that should escalate:
   - sudden_hair_loss
   - severe_skin_infection
   - severe_rash

### Issue: Non-OTC products appearing

**Solution:**

1. Database query must include:
   - `otc_verified == True`
   - `prescription_required == False`
2. Add audit query to find non-OTC products:
   ```sql
   SELECT * FROM products WHERE otc_verified = false OR prescription_required = true;
   ```
3. Review product database entries

---

**Last Updated:** 2025-10-25

**Questions?** Contact: [safety-team@haski.com]

**Critical:** All safety requirements are mandatory. Do not skip.
