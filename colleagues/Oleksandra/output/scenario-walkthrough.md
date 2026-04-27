# Complete Intake Workflow - Step-by-Step Decision Explanation

This document walks through a complete intake workflow showing every decision with full transparency.

## Scenario: Blocked Visit Due to Missing Insurance Data

**Patient:** David Williams (P005)  
**Visit Type:** Annual checkup  
**Issue:** Insurance verification system unavailable  

---

## Step-by-Step Workflow

### Step 1: Visit Creation
```
TIME: 2026-04-22 17:30:00
ACTION: Create visit for patient David Williams
SYSTEM STATE: Visit created with 6 pending tasks
OWNER: system
NEXT ACTION: Visit will begin automated intake processing
```

**Tasks Created:**
1. insurance_verification (pending)
2. prior_auth_check (pending)
3. questionnaire (pending)
4. visit_reason (pending)
5. medication_review (pending)
6. allergy_review (pending)

---

### Step 2: Insurance Verification (BLOCKED)

```
TASK: insurance_verification
INPUT: No insurance data (external system unavailable)
```

**Decision Process:**
```javascript
if (!input.insurance) {
  // Missing external data detected
  decision = BLOCKED  // NOT escalated - this is a system issue
}
```

**Decision Explanation:**
- **Decision:** BLOCKED
- **Reason Code:** `INS_DATA_UNAVAILABLE`
- **Reason Text:** "Insurance verification data unavailable from external system"
- **Rule Applied:** "RULE: If insurance data is missing → BLOCK task (external system issue)"
- **Confidence:** deterministic
- **Next Action:** "Retry insurance verification system or manually verify coverage"
- **Owner:** front_desk
- **Missing Data:** ["insurance verification status", "policy details"]

**Result:**
- Task status: **BLOCKED**
- Task owner: **front_desk**
- Visit state: **IN_PROGRESS** → **ESCALATED** (blocked task triggers escalation)

**Why BLOCKED and not ESCALATED?**
- BLOCKED = External system/data unavailability (technical issue)
- ESCALATED = Business rule requires human review (policy issue)
- Both result in visit state = ESCALATED (human intervention needed)
- But the resolution paths differ:
  - BLOCKED → Retry system or manual workaround
  - ESCALATED → Human decision required

---

### Step 3: Prior Authorization Check (COMPLETED)

```
TASK: prior_auth_check
INPUT: {required: false}
```

**Decision Process:**
```javascript
if (!priorAuth.required) {
  decision = COMPLETED
}
```

**Decision Explanation:**
- **Decision:** COMPLETED
- **Reason Code:** `PA_NOT_REQUIRED`
- **Reason Text:** "Prior authorization not required for this visit"
- **Rule Applied:** "RULE: If priorAuth.required = false → COMPLETE"
- **Confidence:** deterministic
- **Next Action:** "Task completed, no further action needed"

**Result:**
- Task status: **COMPLETED**
- Task owner: **system**
- No change to visit state (already ESCALATED due to blocked task)

---

### Step 4: Questionnaire (COMPLETED)

```
TASK: questionnaire
INPUT: {completed: true, responses: {...}}
```

**Decision Explanation:**
- **Decision:** COMPLETED
- **Reason Code:** `QUEST_COMPLETE`
- **Reason Text:** "Pre-visit questionnaire completed by patient"
- **Rule Applied:** "RULE: If questionnaire.completed = true → COMPLETE"
- **Confidence:** deterministic
- **Next Action:** "Task completed, no further action needed"

---

### Step 5: Visit Reason (COMPLETED)

```
TASK: visit_reason
INPUT: {reason: "Annual checkup", urgency: "routine"}
```

**Decision Process:**
```javascript
if (reason && !containsRoutingTrigger(reason)) {
  decision = COMPLETED
}
```

**Decision Explanation:**
- **Decision:** COMPLETED
- **Reason Code:** `VR_ROUTINE`
- **Reason Text:** "Visit reason provided and appears routine"
- **Rule Applied:** "RULE: If visitReason provided AND no routing triggers detected → COMPLETE"
- **Confidence:** deterministic
- **Next Action:** "Task completed, no further action needed"

**Note:** The routing trigger check found no matches for:
- "chest pain", "shortness of breath", "severe pain", "bleeding", etc.
- This is purely keyword matching, NOT clinical assessment
- Purpose: Administrative routing only

---

### Step 6: Medication Review (COMPLETED)

```
TASK: medication_review
INPUT: {changeReported: false, medications: ["Aspirin 81mg"]}
```

**Decision Explanation:**
- **Decision:** COMPLETED
- **Reason Code:** `MED_NO_CHANGE`
- **Reason Text:** "No medication changes reported"
- **Rule Applied:** "RULE: If medication.changeReported = false → COMPLETE"
- **Confidence:** deterministic
- **Next Action:** "Task completed, no further action needed"

---

### Step 7: Allergy Review (COMPLETED)

```
TASK: allergy_review
INPUT: {changeReported: false, allergies: []}
```

**Decision Explanation:**
- **Decision:** COMPLETED
- **Reason Code:** `ALLERGY_NO_CHANGE`
- **Reason Text:** "No allergy changes reported"
- **Rule Applied:** "RULE: If allergy.changeReported = false → COMPLETE"
- **Confidence:** deterministic
- **Next Action:** "Task completed, no further action needed"

---

## Final Visit State

### Task Summary
| Task | Status | Owner | Next Action |
|------|--------|-------|-------------|
| insurance_verification | **BLOCKED** | front_desk | Retry insurance verification system or manually verify coverage |
| prior_auth_check | completed | system | - |
| questionnaire | completed | system | - |
| visit_reason | completed | system | - |
| medication_review | completed | system | - |
| allergy_review | completed | system | - |

### Visit State
```
STATE: ESCALATED
OWNER: front_desk
NEXT ACTION: Front desk review required: resolve escalated administrative tasks or blocked items
REASON: One task is BLOCKED (insurance verification unavailable)
```

### Resolution Path

**Front Desk Actions:**
1. Check insurance verification system status
2. If system recovered: Retry verification
3. If system down: Manually verify insurance via phone/web portal
4. Update task with verification result
5. If verified: Task completes, visit moves to READY_FOR_REVIEW
6. Human review and clear visit

**Key Points:**
- Visit cannot proceed to READY_FOR_REVIEW until blocked task resolved
- BLOCKED status clearly indicates system/data issue, not policy issue
- Front desk knows exactly what action to take (retry or manual verify)
- Decision explanation provides full context for troubleshooting

---

## Decision Transparency Benefits

### For Staff
- **Clear Ownership:** Each task shows who is responsible
- **Actionable Next Steps:** No guessing what to do
- **Reason Codes:** Structured codes for reporting and tracking
- **Rule Visibility:** Can verify system followed correct logic

### For Auditors
- **Full Trail:** Every decision logged with explanation
- **Deterministic:** Same input always produces same output
- **Explainable:** No black-box ML, pure business rules
- **Traceable:** Can replay any decision

### For System Designers
- **Rule Documentation:** Rules are self-documenting in code
- **Easy Updates:** Can modify rules without rewriting system
- **Testable:** Each rule can be unit tested
- **Observable:** Can track which rules fire most often

---

## BLOCKED vs ESCALATED - Clear Distinction

### BLOCKED Task Example
```json
{
  "decision": "blocked",
  "reasonCode": "INS_DATA_UNAVAILABLE",
  "reasonText": "Insurance verification data unavailable from external system",
  "ruleApplied": "RULE: If insurance data is missing → BLOCK task",
  "nextAction": "Retry insurance verification system or manually verify coverage",
  "owner": "front_desk",
  "missingData": ["insurance verification status", "policy details"]
}
```

**Resolution:** Technical/system fix or workaround

### ESCALATED Task Example
```json
{
  "decision": "escalated",
  "reasonCode": "PA_NOT_APPROVED",
  "reasonText": "Prior authorization is required but has not been approved",
  "ruleApplied": "RULE: If priorAuth.required = true AND priorAuth.approved = false → ESCALATE",
  "nextAction": "Submit prior authorization request to insurance",
  "owner": "front_desk"
}
```

**Resolution:** Business process/human decision

---

## Confidence Level

All decisions show **confidence: "deterministic"**

This means:
- Same input ALWAYS produces same output
- No probabilistic models
- No ML-based classification
- Pure business rule logic
- 100% explainable
- No training data required
- No model drift concerns

**Why Deterministic?**
- Healthcare demands explainability
- Regulatory compliance easier
- Staff can verify correctness
- Easier to maintain and update
- No false confidence from statistical models

---

## Next Action Guidance

Every non-completed task provides specific next action:

**Good Examples:**
- "Retry insurance verification system or manually verify coverage"
- "Contact patient to complete pre-visit questionnaire"
- "Submit prior authorization request to insurance"
- "Nurse to perform medication reconciliation and update EHR"

**Not:**
- "Fix this"
- "Handle escalation"
- "Review task"

The specificity helps staff know exactly what to do without additional context.

---

## Summary

This workflow demonstrates:
✅ Full decision transparency with structured explanations  
✅ Clear distinction between BLOCKED (system) vs ESCALATED (business)  
✅ Explicit ownership assignment  
✅ Actionable next steps  
✅ Complete audit trail  
✅ Deterministic, explainable logic  
✅ No hidden AI/ML complexity  

The system makes every decision explicit, traceable, and actionable.
