# Safety Reminders - Action Checklist

**Date:** October 25, 2025

**Status:** ⚠️ CRITICAL - ACTION REQUIRED BEFORE DEPLOYMENT

---

## 📌 Your Safety Requirements (TL;DR)

### 1. Disclaimer
Every recommendation must include:
```
"Informational only — not medical advice. Consult a healthcare professional."
```

### 2. Escalation Flag
For medical cases:
```
"high_priority": true  // + clear "SEEK MEDICAL ATTENTION" message
```

### 3. OTC Products Only
All products must have:
```
"otc_verified": true, "prescription_required": false
```

### 4. Adverse Reactions
Track and handle:
```
"adverse_reactions": ["redness", "itching", ...]
```

---

## ✅ Your Action Checklist

### Week 1: Understand

- [ ] **Day 1:** Read SAFETY_QUICK_REFERENCE.md (5 min)
- [ ] **Day 1:** Read SAFETY_REMINDERS_SUMMARY.md (15 min)
- [ ] **Day 2:** Backend dev? Read SAFETY_IMPLEMENTATION_GUIDE.md (30 min)
- [ ] **Day 2:** QA? Read ACCEPTANCE_CRITERIA.md (45 min)
- [ ] **Day 3:** Team sync - discuss all 4 requirements
- [ ] **Day 3:** Assign implementation tasks
- [ ] **Day 3:** Set deadline: _________________ (date)

### Week 2: Implement

**Backend Developer:**
- [ ] Add `disclaimer` field to response schema (1-2 hours)
- [ ] Include disclaimer in all recommendation responses (1-2 hours)
- [ ] Add `high_priority` flag to escalations (2-3 hours)
- [ ] Add `otc_verified` and `prescription_required` to products (2-3 hours)
- [ ] Filter products: OTC only (1-2 hours)
- [ ] Add adverse reactions handling (2-3 hours)
- [ ] Write unit tests (2-3 hours)
- [ ] Test with test_api.sh or test_api.ps1 (1 hour)

**Frontend Developer:**
- [ ] Design disclaimer display (1-2 hours)
- [ ] Add escalation warning banner (2-3 hours)
- [ ] Add "Seek Medical Help" button (1 hour)
- [ ] Add adverse reactions form (2-3 hours)
- [ ] Test with actual responses (1-2 hours)

**QA Engineer:**
- [ ] Setup test environment (1-2 hours)
- [ ] Run test_api.sh or test_api.ps1 (30 min)
- [ ] Execute 6 safety tests (1-2 hours)
- [ ] Verify response formats (1-2 hours)
- [ ] Manual UI testing (2-3 hours)

### Week 3: Verify & Sign Off

- [ ] All code complete and committed
- [ ] All unit tests passing
- [ ] All acceptance tests passing
- [ ] Frontend displays correctly
- [ ] QA lead: Complete SAFETY_COMPLIANCE_CHECKLIST.md (2 hours)
- [ ] Dev lead: Review & sign § 1, 2, 3, 4
- [ ] QA lead: Review & sign § 8
- [ ] Product lead: Review & sign § 6, 7
- [ ] Legal/Compliance: Review & sign § 9
- [ ] Security lead: Review & sign § 10 (if applicable)

### Week 4: Deploy

- [ ] All sign-offs obtained
- [ ] Deploy to staging environment
- [ ] Run full test suite against staging
- [ ] Final QA verification
- [ ] Deploy to production
- [ ] Monitor for issues
- [ ] Update documentation

---

## 🧪 Testing Checklist

### Before Deployment - Run These 4 Tests

**Test 1: Disclaimer Present**
```bash
curl -X POST http://localhost:8000/api/v1/recommend \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"method":"direct_analysis","skin_type":"oily","conditions_detected":["acne"],"age":25,"gender":"F"}' \
  | jq '.disclaimer | length > 0'

# ✅ PASS if: true
# ❌ FAIL if: false or field missing
```
- [ ] Pass

**Test 2: High Priority Flag**
```bash
curl -X POST http://localhost:8000/api/v1/recommend \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"method":"direct_analysis","conditions_detected":["sudden_hair_loss"],"confidence_scores":{"sudden_hair_loss":0.95},"age":35,"gender":"F"}' \
  | jq '.escalation.high_priority'

# ✅ PASS if: true
# ❌ FAIL if: false or field missing
```
- [ ] Pass

**Test 3: OTC Products Only**
```bash
curl -X POST http://localhost:8000/api/v1/recommend \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"method":"direct_analysis","skin_type":"oily","conditions_detected":["acne"],"age":25,"gender":"F"}' \
  | jq '.products | map(select(.otc_verified == false or .prescription_required == true)) | length'

# ✅ PASS if: 0
# ❌ FAIL if: > 0
```
- [ ] Pass

**Test 4: Adverse Reactions**
```bash
curl -X POST http://localhost:8000/api/v1/feedback \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"recommendation_id":"rec_001","helpful_rating":1,"adverse_reactions":["redness","itching"],"feedback_text":"Allergic reaction"}' \
  | jq '.adverse_reactions | length > 0'

# ✅ PASS if: true
# ❌ FAIL if: false or field missing
```
- [ ] Pass

### Run Full Test Suite

**Bash (Linux/Mac):**
```bash
chmod +x test_api.sh
./test_api.sh $TOKEN $ADMIN_TOKEN

# All tests should show: ✅ PASS
```
- [ ] Pass

**PowerShell (Windows):**
```powershell
.\test_api.ps1 -Token "YOUR_TOKEN" -AdminToken "ADMIN_TOKEN"

# All tests should show: ✅ PASS
```
- [ ] Pass

---

## 📋 Sign-Off Checklist

### Required Signatures (Before Production)

**Development Lead**
- Reviewed: SAFETY_IMPLEMENTATION_GUIDE.md
- Verified: Code follows all requirements
- Status: [ ] Sign-off  Date: _______ 
- Signature: _________________________

**QA Lead**
- Reviewed: ACCEPTANCE_CRITERIA.md
- Verified: All 6 tests passing
- Verified: Response formats correct
- Status: [ ] Sign-off  Date: _______
- Signature: _________________________

**Product Manager**
- Reviewed: SAFETY_REMINDERS_SUMMARY.md
- Verified: Requirements understood
- Verified: Timeline acceptable
- Status: [ ] Sign-off  Date: _______
- Signature: _________________________

**Legal/Compliance**
- Reviewed: SAFETY_COMPLIANCE_CHECKLIST.md § 9
- Verified: Terms of Service adequate
- Verified: Privacy Policy compliant
- Verified: Medical disclaimers prominent
- Status: [ ] Sign-off  Date: _______
- Signature: _________________________

**Security Lead** (if applicable)
- Reviewed: Security considerations
- Verified: No vulnerabilities introduced
- Status: [ ] Sign-off  Date: _______
- Signature: _________________________

---

## 📱 Deployment Checklist (Final)

### Before Going Live

- [ ] All 4 requirements implemented
- [ ] All 6 acceptance tests passing
- [ ] Code reviewed & merged
- [ ] Database migrations completed
- [ ] Frontend displays correctly
- [ ] All sign-offs obtained
- [ ] Monitoring alerts configured
- [ ] Rollback plan documented
- [ ] Team trained on procedures
- [ ] Communications plan ready

### Post-Deployment (24 hours)

- [ ] Monitor error rates
- [ ] Monitor escalation frequency
- [ ] Monitor adverse reaction reports
- [ ] Check frontend rendering
- [ ] Verify database entries
- [ ] No unexpected errors
- [ ] All systems green ✅

---

## 🚨 If Something Goes Wrong

### Issue: Disclaimer missing from response

**Immediate Action:**
1. Rollback deployment
2. Fix schema: add `disclaimer` field
3. Retest before redeployment

**Responsible:** Development Lead

### Issue: High priority flag not working

**Immediate Action:**
1. Rollback deployment
2. Check escalation detection logic
3. Verify `URGENT_CONDITIONS` list populated
4. Retest with known escalation cases

**Responsible:** Development Lead

### Issue: Non-OTC products appearing

**Immediate Action:**
1. Rollback deployment
2. Audit product database
3. Run query: `SELECT * FROM products WHERE otc_verified = false`
4. Remove non-OTC products
5. Retest before redeployment

**Responsible:** QA Lead + Development Lead

### Issue: Adverse reactions not storing

**Immediate Action:**
1. Check database schema: `adverse_reactions` field present?
2. Check endpoint code: storing in correct field?
3. Verify admin alerts working
4. Retest before redeployment

**Responsible:** Development Lead

---

## 📞 Support & Contact

### Questions About Requirements?
→ Read: SAFETY_QUICK_REFERENCE.md

### How to Implement?
→ Read: SAFETY_IMPLEMENTATION_GUIDE.md

### How to Test?
→ Read: ACCEPTANCE_CRITERIA.md

### Pre-Deployment Checklist?
→ Complete: SAFETY_COMPLIANCE_CHECKLIST.md

### API Reference?
→ See: API_ENDPOINTS.md

---

## 📊 Progress Tracking

```
WEEK 1: Understanding
████░░░░░░░░░░░░░░░░  20%
↳ Read documentation
↳ Team sync
↳ Plan implementation

WEEK 2: Implementation
░░░░░░░░░░░░░░░░░░░░  0%
↳ Backend development
↳ Frontend development
↳ Unit testing

WEEK 3: Verification
░░░░░░░░░░░░░░░░░░░░  0%
↳ Acceptance testing
↳ Manual testing
↳ Sign-offs

WEEK 4: Deployment
░░░░░░░░░░░░░░░░░░░░  0%
↳ Staging
↳ Production
↳ Monitoring
```

---

## ⏰ Timeline

| Phase | Duration | Deadline |
|-------|----------|----------|
| Understanding | 1 week | ________________ |
| Implementation | 1 week | ________________ |
| Verification | 1 week | ________________ |
| Deployment | 1 week | ________________ |
| **Total** | **4 weeks** | **________________** |

---

## 🎯 Success Criteria

✅ **All 4 requirements implemented**
- Disclaimer present
- High priority flag working
- OTC products only
- Adverse reactions tracked

✅ **All 6 acceptance tests passing**
- Test 1: Disclaimer ✅
- Test 2: High Priority ✅
- Test 3: OTC Products ✅
- Test 4: Product Search ✅
- Test 5: Adverse Reactions ✅
- Test 6: Error Handling ✅

✅ **All sign-offs obtained**
- Development ✅
- QA ✅
- Product ✅
- Legal ✅
- Security ✅

✅ **Legal review complete**
- Terms of Service ✅
- Privacy Policy ✅
- Medical disclaimers ✅

✅ **Ready for production**
- All tests passing ✅
- Monitoring configured ✅
- Team trained ✅
- Rollback plan ready ✅

---

## 🎓 Remember

> **All 4 requirements are MANDATORY.**
>
> **No exceptions. No waiving. No delays.**
>
> **All 6 tests must pass before production.**
>
> **Get legal approval before launch.**

---

**Printed Date:** _________________

**By:** _________________

**Team:** _________________

**Next Review:** _________________

---

**Questions?** Contact: safety-team@haski.com

**Keep this checklist posted in your workspace.**
