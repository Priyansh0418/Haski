# Safety Requirements - Quick Reference (1-Page)

## 🚨 4 Mandatory Safety Requirements

### 1️⃣ Disclaimer in ALL Responses
```python
# EVERY recommendation response MUST have:
"disclaimer": "Informational only — not medical advice. Consult a healthcare professional for medical concerns."
```
**Test:** `curl ... | jq '.disclaimer'`

---

### 2️⃣ High Priority Flag for Escalations
```python
# When medical referral needed (see_dermatologist rule):
"escalation": {
  "high_priority": True,  # ← REQUIRED
  "message": "PLEASE SEEK IMMEDIATE MEDICAL ATTENTION FROM A DERMATOLOGIST",
  "recommended_next_steps": [...]
}
```
**Test:** `curl ... | jq '.escalation.high_priority'` → must be `true`

**Conditions that escalate:**
- sudden_hair_loss
- severe_skin_infection
- severe_rash (>50% coverage)
- severe_acne_cystic

---

### 3️⃣ OTC Products Only
```python
# ALL products returned MUST have:
{
  "otc_verified": True,          # ← REQUIRED
  "prescription_required": False  # ← REQUIRED
}
```

**Allowed:**
- ✅ Cleansers, moisturizers, serums
- ✅ Benzoyl peroxide, salicylic acid
- ✅ OTC adapalene (Differin)
- ✅ Supplements, sunscreens

**Prohibited:**
- ❌ Tretinoin, tazarotene, isotretinoin
- ❌ Prescription antibiotics
- ❌ Corticosteroids
- ❌ Any Rx medications

**Test:** `curl ... | jq '.products | map(.otc_verified) | all'` → must be all `true`

---

### 4️⃣ Adverse Reactions Tracking
```python
# Accept and store:
{
  "adverse_reactions": ["redness", "itching", "allergic_reaction"]
}

# Actions on report:
# 1. Store in database ✅
# 2. Flag product for review ✅
# 3. Alert admin ✅
# 4. Avoid product in future ✅
```

**Test:** `curl -X POST /feedback -d '{"adverse_reactions":["redness"]}'`

---

## 📋 Implementation Checklist

### Backend Code
```python
# 1. Schema
class RecommendationResponse(BaseModel):
    disclaimer: str = "Informational only — not medical advice..."
    escalation: Optional[dict] = None
    # escalation.high_priority: bool when medical referral

# 2. Product Query
products = db.query(Product).filter(
    Product.otc_verified == True,       # ← MANDATORY
    Product.prescription_required == False  # ← MANDATORY
).all()

# 3. Feedback
class FeedbackRequest(BaseModel):
    adverse_reactions: Optional[List[str]] = None
    
# 4. Handle
if request.adverse_reactions:
    flag_product_for_review()
    alert_admin()
```

### Frontend Display
- [ ] Show disclaimer prominently (before recommendations)
- [ ] Show red warning banner for escalations
- [ ] "Seek Medical Help" button with dermatologist info
- [ ] Adverse reactions checkboxes in feedback form

### Testing
```bash
# 1. Disclaimer
curl ... | jq '.disclaimer | length > 0'

# 2. Escalation
curl ... | jq '.escalation.high_priority'

# 3. OTC Products
curl ... | jq '.products | map(.otc_verified == true) | all'

# 4. Adverse Reactions
curl ... | jq '.adverse_reactions'
```

---

## 🎯 Before Deployment

**Run these 4 checks:**

1. ✅ **Disclaimer Test**
   ```bash
   curl -X POST /api/v1/recommend ... | grep -q "not medical advice" && echo "PASS" || echo "FAIL"
   ```

2. ✅ **Escalation Test**
   ```bash
   curl -X POST /api/v1/recommend ... | jq '.escalation.high_priority' | grep -q "true" && echo "PASS" || echo "FAIL"
   ```

3. ✅ **OTC Test**
   ```bash
   curl ... | jq '.products | map(select(.otc_verified == false)) | length' | grep -q "0" && echo "PASS" || echo "FAIL"
   ```

4. ✅ **Legal Review**
   ```
   [ ] Terms of Service approved
   [ ] Privacy Policy approved
   [ ] Medical disclaimers approved
   ```

---

## ⚠️ Common Mistakes

| ❌ WRONG | ✅ CORRECT |
|---------|-----------|
| Disclaimer only on escalations | Disclaimer in ALL responses |
| `high_priority: "true"` (string) | `high_priority: true` (boolean) |
| Mix OTC + Rx products | OTC only, filter `otc_verified == true` |
| Ignore adverse reactions | Store, flag, alert, avoid in future |
| Generic error messages | "Informational only — not medical advice..." |
| No medical guidance in escalation | "PLEASE SEEK IMMEDIATE MEDICAL ATTENTION FROM A DERMATOLOGIST" |

---

## 📞 Quick Links

| Document | Purpose |
|----------|---------|
| `API_ENDPOINTS.md` | Complete API reference with examples |
| `ACCEPTANCE_CRITERIA.md` | 6 safety tests to pass |
| `SAFETY_COMPLIANCE_CHECKLIST.md` | Pre-deployment sign-off |
| `SAFETY_IMPLEMENTATION_GUIDE.md` | Code examples & implementation |
| `SAFETY_REMINDERS_SUMMARY.md` | Comprehensive guide |

---

## 🔴 CRITICAL

**These 4 requirements are MANDATORY.**

**No exceptions. No delays.**

**All 6 tests must pass before production.**

**Get legal approval before launch.**

---

**Saved:** October 25, 2025

**Print this page. Post it. Reference it daily.**
