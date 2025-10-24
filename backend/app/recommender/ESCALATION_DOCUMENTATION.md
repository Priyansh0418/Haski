# Escalation System Documentation

## Overview

The `escalation.yml` file defines conditions that require immediate medical attention and cannot be managed with over-the-counter skincare recommendations. These conditions should trigger professional dermatologic consultation or emergency care.

## Structure

```yaml
escalations:
  condition_name:
    severity: high | immediate
    condition_type: "skin" | "hair" | "systemic"
    description: "..."
    triggers: [list of symptoms/signs that trigger escalation]
    medical_advice: "recommended action"
    action: "escalate" | "emergency"
    urgency: "immediate" | "high"
    recommended_next_steps: [list of actions for user]
    why_escalated: "reasoning"
```

## Escalation Conditions (11 Total)

### 1. **Infection** (IMMEDIATE)

**Severity**: High  
**Type**: Skin

**Triggers**:

- Pus-filled pustules with surrounding redness
- Spreading rash with warmth or heat
- Yellow/green discharge from lesions
- Fever accompanying skin symptoms
- Cellulitis (rapidly spreading redness)

**Action**: Escalate to ER if fever/cellulitis; dermatology within 24-48h

**Why**: Requires prescription antibiotics, antivirals, or antifungals

---

### 2. **Severe Rash** (HIGH)

**Severity**: High  
**Type**: Skin

**Triggers**:

- Rash covering >25% of body surface
- Sudden unexplained rash
- Swelling (especially face/lips)
- Blistering or oozing
- Accompanied by fever/systemic symptoms

**Action**: Dermatology within 24-48 hours

**Why**: Indicates allergies, dermatitis, or systemic conditions

---

### 3. **Severe Acne** (HIGH)

**Severity**: High  
**Type**: Skin

**Triggers**:

- Painful deep cystic acne (>5mm)
- Nodular acne (hard, inflamed bumps)
- Multi-site acne (face, chest, back)
- Post-inflammatory scarring
- Resistant to 3+ months of skincare
- Sudden severe flare

**Action**: Dermatology for possible Accutane, antibiotics, or hormonal therapy

**Why**: Risk of permanent scarring; requires prescription treatment

---

### 4. **Severe Eczema** (HIGH)

**Severity**: High  
**Type**: Skin

**Triggers**:

- Covering >40% of body
- Severe itching disrupting sleep/function
- Secondary bacterial infection
- Resistant to moisturizing
- Sudden onset/worsening
- Face/hands extensively affected

**Action**: Dermatology for prescription corticosteroids, biologics, or immunosuppressants

**Why**: Requires professional treatment beyond skincare; possible systemic involvement

---

### 5. **Severe Psoriasis** (HIGH)

**Severity**: High  
**Type**: Skin

**Triggers**:

- Covering >10% of body (BSA)
- Erythrodermic psoriasis (nearly complete coverage)
- Pustular psoriasis with systemic symptoms
- Psoriatic arthritis pain
- Resistant to topical treatments after 4+ weeks
- Sudden severe onset

**Action**: Dermatology urgently for systemic treatment

**Why**: Requires biologics or systemic immunomodulatory therapy

---

### 6. **Sudden Hair Loss** (HIGH)

**Severity**: High  
**Type**: Hair

**Triggers**:

- Losing >100 hairs daily
- Circular bald patches (alopecia areata)
- Diffuse thinning over weeks
- Hair loss after stress/illness/surgery
- Nail pitting accompanying hair loss
- Scalp pain/itching with loss

**Action**: Dermatology within 1-2 weeks

**Why**: Requires diagnosis (hormonal, autoimmune, nutritional) and treatment

---

### 7. **Scalp Infection** (HIGH)

**Severity**: High  
**Type**: Hair

**Triggers**:

- Pus-filled bumps on scalp with pain
- Scaling with pustules and redness
- Circular scaly patches (possible ringworm)
- Drainage or crusting
- Painful lymph nodes
- Foul-smelling discharge

**Action**: Dermatology within 48-72 hours

**Why**: Requires prescription antifungal or antibiotic treatment

---

### 8. **Severe Urticaria with Angioedema** (IMMEDIATE)

**Severity**: Immediate  
**Type**: Skin

**Triggers**:

- Widespread hives (>50% body coverage)
- Swelling of face, lips, or throat
- Breathing difficulty or throat closure
- Fever or systemic symptoms
- Unresponsive to antihistamines

**Action**: CALL 911 OR GO TO ER IMMEDIATELY

**Why**: Can progress to anaphylaxis - life-threatening emergency

---

### 9. **Suspicious Mole** (HIGH)

**Severity**: High  
**Type**: Skin

**Triggers** (ABCDE criteria):

- **A**symmetry: sides don't match
- **B**order: irregular or scalloped
- **C**olor: multiple colors (brown, black, red, white)
- **D**iameter: >6mm (pencil eraser size)
- **E**volution: recent change in size/shape/color
- Itching, bleeding, or oozing
- Unusual texture or raised appearance

**Action**: Dermatology within 1-2 weeks for possible biopsy

**Why**: Possible melanoma - requires professional evaluation and possible biopsy

---

### 10. **Autoimmune Suspected** (HIGH)

**Severity**: High  
**Type**: Systemic

**Triggers**:

- Hair loss + joint pain + fatigue
- Rash with photosensitivity
- Discoid lupus pattern (face/ears)
- Skin symptoms + oral ulcers + eye inflammation
- Multiple joint pain + skin changes + fever

**Action**: Dermatology first, then rheumatology referral

**Why**: Requires multidisciplinary evaluation and systematic diagnosis

---

## Integration with RuleEngine

### How to Use in Backend

```python
from backend.app.recommender.engine import RuleEngine
from backend.app.recommender.escalation import load_escalations

# Load escalation rules
escalations = load_escalations()

# In recommendation flow:
def generate_recommendation(analysis):
    engine = RuleEngine()
    recommendation, applied_rules = engine.apply_rules(analysis)

    # Check for escalation conditions
    for condition in recommendation.get('conditions_detected', []):
        if condition in escalations['escalations']:
            escalation_data = escalations['escalations'][condition]

            # Flag this recommendation
            recommendation['escalation'] = {
                'condition': condition,
                'severity': escalation_data['severity'],
                'message': escalation_data['medical_advice'],
                'urgency': escalation_data['urgency'],
                'action': escalation_data['action'],
                'next_steps': escalation_data['recommended_next_steps']
            }

            # Log for audit trail
            logger.log_analysis_error(
                user_id=user.id,
                analysis_id=analysis.id,
                error_message=f"Escalation: {condition} - {escalation_data['medical_advice']}"
            )

            break  # Only one escalation per analysis

    return recommendation
```

### Frontend Display

```typescript
// React component example
interface EscalationMessage {
  condition: string;
  severity: "high" | "immediate";
  message: string;
  urgency: string;
  next_steps: string[];
}

export function RecommendationCard({ recommendation }: Props) {
  if (recommendation.escalation) {
    const esc = recommendation.escalation as EscalationMessage;

    return (
      <div
        className={`
        p-6 rounded-lg border-2
        ${
          esc.severity === "immediate"
            ? "border-red-600 bg-red-50"
            : "border-orange-500 bg-orange-50"
        }
      `}
      >
        <div className="flex items-center gap-2 mb-4">
          <AlertTriangle
            className={`
            ${esc.severity === "immediate" ? "text-red-600" : "text-orange-600"}
          `}
          />
          <h2 className="font-bold text-lg">⚠️ Medical Attention Required</h2>
        </div>

        <p className="text-lg font-semibold mb-2">{esc.message}</p>

        <p className="text-sm text-gray-700 mb-4">
          Condition: <span className="font-semibold">{esc.condition}</span>
        </p>

        <div className="mb-4">
          <h3 className="font-semibold mb-2">Recommended Next Steps:</h3>
          <ul className="list-disc pl-5 space-y-1">
            {esc.next_steps.map((step, idx) => (
              <li key={idx} className="text-sm">
                {step}
              </li>
            ))}
          </ul>
        </div>

        {esc.urgency === "immediate" && (
          <div className="bg-red-100 border border-red-400 rounded p-3 mt-4">
            <p className="font-bold text-red-800">🚨 EMERGENCY</p>
            <p className="text-red-700">
              Call 911 or go to nearest ER immediately
            </p>
          </div>
        )}
      </div>
    );
  }

  // Regular recommendation display...
}
```

## Database Schema

Add to your database models:

```python
from sqlalchemy import Column, String, Enum, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

class Escalation(Base):
    __tablename__ = "escalations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)

    condition = Column(String(100), nullable=False)  # e.g., "infection", "sudden_hair_loss"
    severity = Column(Enum("high", "immediate"), nullable=False)
    message = Column(String(500), nullable=False)

    # Action taken by user
    action_taken = Column(String(100), nullable=True)  # "ignored", "scheduled_appointment", "went_to_er"
    appointment_date = Column(DateTime, nullable=True)
    notes = Column(String(1000), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="escalations")
    analysis = relationship("Analysis", back_populates="escalations")
```

## API Response Format

When an escalation is detected, return:

```json
{
  "user_id": 5,
  "analysis_id": 10,
  "recommendation": {
    "routines": [],
    "products": [],
    "diet": [],
    "escalation": {
      "condition": "infection",
      "severity": "high",
      "message": "Seek immediate dermatologic care",
      "urgency": "immediate",
      "action": "escalate",
      "next_steps": [
        "Do not self-treat with over-the-counter products",
        "Avoid squeezing or picking at lesions",
        "Schedule dermatology appointment within 24-48 hours",
        "If fever or signs of cellulitis: visit urgent care/ER immediately"
      ],
      "why_escalated": "Infections require professional diagnosis and prescription treatment"
    }
  }
}
```

## Compliance & Safety

### Legal Considerations

1. **Disclaimer Required**: Always include:

   > "This analysis is for informational purposes only and does not constitute medical advice. Always consult with a licensed dermatologist or healthcare provider for professional diagnosis and treatment."

2. **Escalation Logging**: Log all escalations for:

   - Compliance tracking
   - Liability documentation
   - Audit trails
   - Quality improvement

3. **User Acknowledgment**: Require users to acknowledge they understand escalation messages

### Implementation Requirements

- [ ] Display escalation messages prominently (red/orange alert styling)
- [ ] Include "Contact Dermatologist" CTA button
- [ ] Log escalation to audit trail
- [ ] Provide dermatologist finder/referral links
- [ ] Include emergency numbers (911, poison control, etc.)
- [ ] Require user acknowledgment before dismissing

## Testing

```python
def test_escalation_detection():
    """Test that escalation conditions are properly detected."""
    analysis = Analysis(
        user_id=1,
        skin_conditions=["infection"],
        images=["infected_skin.jpg"]
    )

    recommendation, applied_rules = engine.apply_rules(analysis)

    assert recommendation.get('escalation') is not None
    assert recommendation['escalation']['condition'] == 'infection'
    assert recommendation['escalation']['severity'] == 'high'
    assert recommendation['escalation']['action'] == 'escalate'


def test_escalation_logging():
    """Test that escalations are logged to audit trail."""
    analysis = Analysis(user_id=1, skin_conditions=["severe_rash"])
    recommendation = engine.apply_rules(analysis)[0]

    # Log to database
    escalation_log = Escalation(
        user_id=1,
        analysis_id=analysis.id,
        condition=recommendation['escalation']['condition'],
        severity=recommendation['escalation']['severity'],
        message=recommendation['escalation']['message']
    )

    db.add(escalation_log)
    db.commit()

    # Verify logged
    logged = db.query(Escalation).filter_by(user_id=1).first()
    assert logged is not None
```

## Metrics & Analytics

Track escalations for insights:

```python
# Most common escalations
escalation_counts = db.query(Escalation.condition, func.count()).group_by(Escalation.condition)

# Escalation severity distribution
severity_dist = db.query(Escalation.severity, func.count()).group_by(Escalation.severity)

# User actions after escalation
action_breakdown = db.query(
    Escalation.action_taken,
    func.count()
).group_by(Escalation.action_taken)
```

## Related Files

- `escalation.yml` - Escalation condition definitions
- `rules.yml` - Recommendation rules
- `engine.py` - RuleEngine integration point
- `audit_logger.py` - Escalation logging
- `schemas.py` - Pydantic response schemas

## Version History

| Version | Date       | Changes                                       |
| ------- | ---------- | --------------------------------------------- |
| 1.0     | 2025-10-25 | Initial release with 11 escalation conditions |

## Support & Questions

For questions about escalation conditions, see:

1. Medical references in `why_escalated` field
2. Integration guide in this document
3. Test examples in test files
