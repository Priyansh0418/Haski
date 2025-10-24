# Escalation System - Quick Reference

## ⚡ Quick Start

### What is Escalation?

Conditions requiring immediate medical attention that cannot be handled with skincare recommendations.

### Escalation Conditions (11 Total)

| Condition                | Severity  | Type     | Urgency   | Action                              |
| ------------------------ | --------- | -------- | --------- | ----------------------------------- |
| **Infection**            | High      | Skin     | Immediate | ER if fever/cellulitis; derm 24-48h |
| **Severe Rash**          | High      | Skin     | High      | Derm 24-48h                         |
| **Severe Acne**          | High      | Skin     | High      | Derm for Accutane/antibiotics       |
| **Severe Eczema**        | High      | Skin     | High      | Derm for prescription treatment     |
| **Severe Psoriasis**     | High      | Skin     | High      | Derm urgently                       |
| **Sudden Hair Loss**     | High      | Hair     | High      | Derm 1-2 weeks                      |
| **Scalp Infection**      | High      | Hair     | High      | Derm 48-72h                         |
| **Severe Urticaria**     | Immediate | Skin     | Immediate | 🚨 **CALL 911**                     |
| **Suspicious Mole**      | High      | Skin     | High      | Derm 1-2 weeks (biopsy possible)    |
| **Autoimmune Suspected** | High      | Systemic | High      | Derm → Rheumatology                 |

---

## 🔧 Integration Code

### Load Escalation Rules

```python
import yaml

def load_escalations():
    with open('backend/app/recommender/escalation.yml', 'r') as f:
        return yaml.safe_load(f)

escalations = load_escalations()
```

### Check for Escalation

```python
def check_for_escalation(analysis):
    escalations = load_escalations()

    for condition in analysis.conditions_detected:
        if condition in escalations['escalations']:
            return escalations['escalations'][condition]

    return None
```

### Return Escalation Response

```python
from backend.app.recommender.audit_logger import get_audit_logger

logger = get_audit_logger()

@app.post("/api/v1/recommend")
def get_recommendation(request: RecommendationRequest):
    recommendation, applied_rules = engine.apply_rules(analysis)

    # Check for escalation
    escalation_data = check_for_escalation(recommendation)

    if escalation_data:
        # Log escalation
        logger.log_analysis_error(
            user_id=request.user_id,
            analysis_id=analysis.id,
            error_message=f"Escalation: {escalation_data['medical_advice']}"
        )

        # Add to response
        recommendation['escalation'] = {
            'condition': condition,
            'severity': escalation_data['severity'],
            'message': escalation_data['medical_advice'],
            'urgency': escalation_data['urgency'],
            'next_steps': escalation_data['recommended_next_steps']
        }

    return recommendation
```

---

## 🎨 Frontend Display

### React Component Template

```typescript
interface Escalation {
  condition: string;
  severity: "high" | "immediate";
  message: string;
  urgency: string;
  next_steps: string[];
}

export function EscalationAlert({ escalation }: { escalation: Escalation }) {
  const isEmergency = escalation.severity === "immediate";

  return (
    <div
      className={`
      p-6 rounded-lg border-2 mb-6
      ${
        isEmergency
          ? "border-red-600 bg-red-50"
          : "border-orange-500 bg-orange-50"
      }
    `}
    >
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        {isEmergency ? (
          <AlertTriangle className="text-red-600 w-6 h-6" />
        ) : (
          <AlertCircle className="text-orange-600 w-6 h-6" />
        )}
        <h2
          className={`
          text-xl font-bold
          ${isEmergency ? "text-red-700" : "text-orange-700"}
        `}
        >
          ⚠️ Medical Attention Required
        </h2>
      </div>

      {/* Main Message */}
      <p className="text-lg font-semibold mb-2">{escalation.message}</p>

      {/* Condition Info */}
      <p className="text-sm text-gray-600 mb-4">
        Condition:{" "}
        <span className="font-semibold text-gray-800">
          {escalation.condition.replace(/_/g, " ")}
        </span>
      </p>

      {/* Next Steps */}
      <div className="mb-6">
        <h3 className="font-semibold mb-3">📋 Recommended Next Steps:</h3>
        <ul className="space-y-2">
          {escalation.next_steps.map((step, idx) => (
            <li key={idx} className="flex gap-2">
              <span className="text-blue-600 font-bold">{idx + 1}.</span>
              <span>{step}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Emergency Banner */}
      {isEmergency && (
        <div className="bg-red-100 border-l-4 border-red-600 p-4 mb-4">
          <p className="font-bold text-red-800">🚨 MEDICAL EMERGENCY</p>
          <p className="text-red-700">
            Call 911 or go to the nearest Emergency Room immediately
          </p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-3 flex-wrap">
        <a
          href="https://dermatologist-finder-url.com"
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          target="_blank"
        >
          🔗 Find Dermatologist
        </a>

        {isEmergency && (
          <a
            href="tel:911"
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 font-bold"
          >
            📞 Call 911
          </a>
        )}
      </div>
    </div>
  );
}
```

### Display in Recommendation Screen

```typescript
export function RecommendationScreen() {
  const [recommendation, setRecommendation] = useState(null);

  return (
    <div className="container mx-auto p-6">
      {/* Show escalation alert if present */}
      {recommendation?.escalation && (
        <EscalationAlert escalation={recommendation.escalation} />
      )}

      {/* Regular recommendation content below */}
      {!recommendation?.escalation && (
        <NormalRecommendationCard recommendation={recommendation} />
      )}
    </div>
  );
}
```

---

## 📊 API Examples

### Request

```bash
POST /api/v1/recommend
Content-Type: application/json

{
  "user_id": 5,
  "analysis_id": 10
}
```

### Response with Escalation

```json
{
  "recommendation": {
    "routines": [],
    "products": [],
    "diet": [],
    "escalation": {
      "condition": "infection",
      "severity": "high",
      "message": "Seek immediate dermatologic care",
      "urgency": "immediate",
      "next_steps": [
        "Do not self-treat with over-the-counter products",
        "Avoid squeezing or picking at lesions",
        "Schedule dermatology appointment within 24-48 hours"
      ]
    }
  }
}
```

### Response without Escalation

```json
{
  "recommendation": {
    "routines": [
      {
        "name": "Morning Skincare",
        "steps": [...]
      }
    ],
    "products": [
      {
        "name": "Gentle Cleanser",
        "why": "..."
      }
    ],
    "diet": [...]
  }
}
```

---

## ⚠️ Trigger Keywords

### Quick Escalation Check

```python
# Map common terms to escalation conditions
ESCALATION_TRIGGERS = {
    "infection": ["pus", "infection", "infected", "abscess", "cellulitis"],
    "severe_rash": ["rash", "hives", "urticaria", "itchy", "widespread"],
    "severe_acne": ["cystic", "nodular", "severe acne", "scarring"],
    "severe_eczema": ["eczema", "dermatitis", "itching"],
    "sudden_hair_loss": ["hair loss", "alopecia", "bald patches", "thinning"],
    "scalp_infection": ["scalp", "fungal", "ringworm", "folliculitis"],
    "suspicious_mole": ["mole", "spot", "melanoma", "changing"],
    "urticaria_severe": ["hives", "swelling", "anaphylaxis"],
    "autoimmune_suspected": ["lupus", "autoimmune", "joint pain"]
}

def find_escalation(symptoms: str):
    symptoms_lower = symptoms.lower()
    for condition, keywords in ESCALATION_TRIGGERS.items():
        if any(keyword in symptoms_lower for keyword in keywords):
            return condition
    return None
```

---

## 🗂️ Database Schema

```sql
CREATE TABLE escalations (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    analysis_id INTEGER NOT NULL,
    condition VARCHAR(100) NOT NULL,
    severity ENUM('high', 'immediate'),
    message VARCHAR(500),
    action_taken VARCHAR(100),
    appointment_date DATETIME,
    notes VARCHAR(1000),
    created_at DATETIME DEFAULT NOW(),
    updated_at DATETIME DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (analysis_id) REFERENCES analyses(id)
);
```

---

## 🧪 Testing

```python
def test_escalation_detection():
    analysis = Analysis(
        user_id=1,
        skin_conditions=["infection"]
    )

    recommendation, _ = engine.apply_rules(analysis)
    assert recommendation.get('escalation') is not None
    assert recommendation['escalation']['severity'] == 'high'

def test_escalation_urgency():
    analysis = Analysis(user_id=1, skin_conditions=["urticaria_severe"])
    recommendation, _ = engine.apply_rules(analysis)
    assert recommendation['escalation']['urgency'] == 'immediate'
```

---

## 📱 Mobile Considerations

### Responsive Alert

```typescript
export function EscalationAlert({ escalation }: Props) {
  return (
    <div className="w-full md:max-w-2xl mx-auto p-4 md:p-6">
      {/* Alert content - scales on mobile */}
    </div>
  );
}
```

### Mobile Action Buttons

```typescript
<div className="flex flex-col gap-2 sm:flex-row">
  <a
    href="tel:911"
    className="flex-1 px-3 py-2 bg-red-600 text-white rounded text-center"
  >
    Call 911
  </a>
  <a
    href="https://dermatologist-finder"
    className="flex-1 px-3 py-2 bg-blue-600 text-white rounded text-center"
  >
    Find Derm
  </a>
</div>
```

---

## 🔐 Compliance

### Required Disclaimer

> ⚠️ **Medical Disclaimer**  
> This analysis is for informational purposes only and does not constitute medical advice. Always consult with a licensed dermatologist or healthcare provider for professional diagnosis and treatment. In case of medical emergency, call 911 or visit your nearest emergency room immediately.

### Required User Acknowledgment

```typescript
const [acknowledged, setAcknowledged] = useState(false);

<div className="my-4">
  <label className="flex items-center gap-2">
    <input
      type="checkbox"
      checked={acknowledged}
      onChange={(e) => setAcknowledged(e.target.checked)}
    />
    <span>I understand this is not medical advice and will seek professional care</span>
  </label>
</div>

<button
  disabled={!acknowledged}
  onClick={handleDismiss}
>
  I Understand
</button>
```

---

## 📞 Emergency Contacts

Include in UI:

- **911**: Life-threatening emergency
- **Poison Control**: 1-800-222-1222 (US)
- **Dermatology Hotline**: (varies by location)
- **Telemedicine Derm**: Available 24/7

---

## 📚 Related Documentation

- **Full Reference**: `ESCALATION_DOCUMENTATION.md`
- **Rules**: `rules.yml`
- **Audit Logger**: `audit_logger.py`
- **Engine**: `engine.py`

---

## ✅ Implementation Checklist

- [ ] Load escalation.yml in RuleEngine
- [ ] Check for escalations in recommendation flow
- [ ] Add escalation field to API response schema
- [ ] Create EscalationAlert React component
- [ ] Display escalation on recommendation screen
- [ ] Add emergency action buttons
- [ ] Log escalations to audit trail
- [ ] Add medical disclaimer to UI
- [ ] Require user acknowledgment
- [ ] Test all escalation conditions
- [ ] Add mobile responsiveness
- [ ] Deploy and monitor

---

**Last Updated**: 2025-10-25  
**Version**: 1.0
