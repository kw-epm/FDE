# Decision Transparency Model

## Overview

This prototype implements a **Decision Explanation Layer** that makes every workflow decision explicit, traceable, and actionable.

## Purpose

Healthcare workflows require:
- **Explainability:** Staff must understand why decisions were made
- **Auditability:** Regulators need complete decision trails
- **Actionability:** Staff need clear guidance on what to do next
- **Trustworthiness:** No "black box" AI decisions

## Decision Explanation Structure

Every task decision includes a structured `DecisionExplanation` object:

```typescript
interface DecisionExplanation {
  decision: 'completed' | 'escalated' | 'blocked';
  reasonCode: string;              // Machine-readable code
  reasonText: string;              // Human-readable explanation
  ruleApplied: string;             // Explicit business rule
  confidence: 'deterministic';     // Always deterministic (no ML)
  nextAction: string;              // What should happen next
  owner?: Owner;                   // Who is responsible
  missingData?: string[];          // What data is missing (for blocked)
}
```

### Example: Completed Task

```json
{
  "decision": "completed",
  "reasonCode": "INS_VERIFIED",
  "reasonText": "Insurance successfully verified and policy is active",
  "ruleApplied": "RULE: If insurance.verified = true AND insurance.active = true → COMPLETE",
  "confidence": "deterministic",
  "nextAction": "Task completed, no further action needed"
}
```

### Example: Escalated Task

```json
{
  "decision": "escalated",
  "reasonCode": "PA_EXPIRED",
  "reasonText": "Prior authorization expired on 2026-01-15",
  "ruleApplied": "RULE: If priorAuth.required = true AND priorAuth.expirationDate < now → ESCALATE to front_desk",
  "confidence": "deterministic",
  "nextAction": "Request renewal of prior authorization from insurance provider",
  "owner": "front_desk"
}
```

### Example: Blocked Task

```json
{
  "decision": "blocked",
  "reasonCode": "INS_DATA_UNAVAILABLE",
  "reasonText": "Insurance verification data unavailable from external system",
  "ruleApplied": "RULE: If insurance data is missing → BLOCK task (external system issue)",
  "confidence": "deterministic",
  "nextAction": "Retry insurance verification system or manually verify coverage",
  "owner": "front_desk",
  "missingData": ["insurance verification status", "policy details"]
}
```

## Reason Codes

Reason codes provide machine-readable decision identifiers for reporting and analytics.

### Insurance Verification
- `INS_VERIFIED` - Insurance verified and active
- `INS_NOT_VERIFIED` - Verification failed
- `INS_NOT_ACTIVE` - Policy not active
- `INS_DATA_UNAVAILABLE` - External system unavailable

### Prior Authorization
- `PA_NOT_REQUIRED` - Prior auth not needed
- `PA_APPROVED` - Prior auth approved and valid
- `PA_NOT_APPROVED` - Prior auth not approved
- `PA_EXPIRED` - Prior auth expired
- `PA_DATA_UNAVAILABLE` - External system unavailable

### Questionnaire
- `QUEST_COMPLETE` - Questionnaire completed
- `QUEST_INCOMPLETE` - Questionnaire not finished
- `QUEST_MISSING` - No questionnaire data

### Visit Reason
- `VR_ROUTINE` - Routine visit reason
- `VR_ROUTING_TRIGGER` - Contains routing trigger keyword
- `VR_EMPTY` - Visit reason not provided
- `VR_MISSING` - No visit reason data

### Medication Review
- `MED_NO_CHANGE` - No changes reported
- `MED_CHANGE_REPORTED` - Changes require reconciliation
- `MED_DATA_MISSING` - No medication data

### Allergy Review
- `ALLERGY_NO_CHANGE` - No changes reported
- `ALLERGY_CHANGE_REPORTED` - Changes require review
- `ALLERGY_DATA_MISSING` - No allergy data

## Ownership and Next Actions

### Owner Assignment

Every task and visit has an explicit owner:

| Owner | Role | Responsibility |
|-------|------|----------------|
| `system` | Automated system | Processing tasks automatically |
| `front_desk` | Front desk staff | Administrative tasks, insurance, scheduling |
| `nurse` | Clinical staff | Clinical tasks, medication/allergy review, triage |
| `manager` | Manager | Complex cases with multiple escalation types |
| `patient` | Patient | Providing missing information |

### Next Action Specification

Every non-completed state includes specific guidance:

**Good Next Actions:**
- ✅ "Retry insurance verification system or manually verify coverage"
- ✅ "Contact patient to complete pre-visit questionnaire"
- ✅ "Nurse to perform medication reconciliation and update EHR"
- ✅ "Submit prior authorization request to insurance"

**Bad Next Actions:**
- ❌ "Fix this"
- ❌ "Handle escalation"
- ❌ "Review"

## BLOCKED vs ESCALATED

Critical semantic distinction for operational clarity.

### BLOCKED Status

**Meaning:** External system or data unavailable (technical issue)

**Characteristics:**
- Missing external data
- System connectivity issues
- Temporary failures
- No policy/business decision needed

**Resolution Path:**
1. Retry external system
2. Manual workaround
3. Wait for system recovery

**Example:**
- Insurance verification API returns 503 error
- Prior auth database temporarily down
- Network timeout

### ESCALATED Status

**Meaning:** Business rule requires human review (policy issue)

**Characteristics:**
- Data present but requires decision
- Policy violation detected
- Clinical review needed
- Business rule triggered

**Resolution Path:**
1. Human reviews situation
2. Makes business/clinical decision
3. Takes appropriate action

**Example:**
- Insurance not active (needs patient contact)
- Prior auth expired (needs renewal request)
- Medication change (needs reconciliation)

### Visit State Impact

**Both BLOCKED and ESCALATED tasks set visit state to ESCALATED**

Why? Both require human intervention.

Difference: The `decisionExplanation` clarifies which type:
- Check `decision` field: "blocked" vs "escalated"
- Check `missingData` field: only present for blocked
- Check `nextAction`: describes specific resolution

## Confidence Level

All decisions have `confidence: "deterministic"`

**What This Means:**
- No machine learning
- No probabilistic models
- No uncertainty ranges
- Same input → same output (always)
- 100% explainable
- No black box

**Why Deterministic?**
1. **Regulatory Compliance:** Healthcare regulators require explainability
2. **Staff Trust:** Staff can verify logic themselves
3. **Auditability:** Every decision traceable to explicit rule
4. **Maintainability:** Rules easy to update without retraining
5. **No Drift:** System behavior stable over time

**What We DON'T Have:**
- ML confidence scores (0.85, 0.92, etc.)
- Neural network predictions
- Statistical classification
- Training data requirements
- Model retraining needs

## Workflow State Progression

### State Machine

```
NOT_STARTED → IN_PROGRESS → READY_FOR_REVIEW → CLEARED
                    ↓
                ESCALATED → (resolve) → READY_FOR_REVIEW → CLEARED
```

### State Definitions

**NOT_STARTED**
- Visit created, no tasks processed
- Owner: system
- Next Action: "Visit will begin automated intake processing"

**IN_PROGRESS**
- At least one task pending
- Owner: system
- Next Action: "Automated processing in progress"

**ESCALATED**
- One or more tasks escalated or blocked
- Owner: front_desk, nurse, or manager (depends on escalation types)
- Next Action: Specific to escalation type

**READY_FOR_REVIEW**
- All tasks completed or resolved
- Awaiting human approval
- Owner: front_desk
- Next Action: "Ready for human review and approval"

**CLEARED**
- Human review completed
- Visit approved for appointment
- Owner: system
- Next Action: "Visit cleared and ready for appointment"

### Key Rules

1. **CLEARED only via human review:** Automated processing cannot set CLEARED
2. **Multiple escalations → manager:** If both administrative and clinical escalations, manager coordinates
3. **Any block/escalation → ESCALATED visit:** Visit state immediately shows intervention needed
4. **Explicit progression:** No automatic state transitions without explicit action

## Operational Usability

### For Front Desk Staff

**Dashboard View:**
```
Visit #123 - John Smith
State: ESCALATED
Owner: front_desk
Next Action: Retry insurance verification system or manually verify coverage

Blocked Task: insurance_verification
- Reason: Insurance verification data unavailable from external system
- Missing Data: insurance verification status, policy details
- What to do: Check if system is back online, then retry OR call insurance directly
```

### For Nurses

**Dashboard View:**
```
Visit #456 - Sarah Johnson
State: ESCALATED
Owner: nurse
Next Action: Nurse to perform medication reconciliation and update EHR

Escalated Task: medication_review
- Reason: Patient reported medication changes: Metformin 500mg
- What to do: Review changes with patient, update EHR, check for interactions
```

### For Managers

**Dashboard View:**
```
Visit #789 - Michael Chen
State: ESCALATED
Owner: manager
Next Action: Manager review required: visit has both administrative and clinical escalations

Issues:
1. Prior authorization expired (front_desk)
2. Visit reason contains routing trigger: "chest pain" (nurse)

What to do: Coordinate with front desk for auth renewal AND nurse for triage
```

## Audit Trail Integration

Every decision is logged in audit events:

```json
{
  "type": "task_completed",
  "timestamp": "2026-04-22T17:30:00Z",
  "taskId": "task-1",
  "taskType": "insurance_verification",
  "explanation": {
    "decision": "completed",
    "reasonCode": "INS_VERIFIED",
    "reasonText": "Insurance successfully verified and policy is active",
    "ruleApplied": "RULE: If insurance.verified = true AND insurance.active = true → COMPLETE",
    "confidence": "deterministic",
    "nextAction": "Task completed, no further action needed"
  }
}
```

This provides:
- Complete decision trail
- Rule verification capability
- Performance analytics (which rules fire most)
- Compliance documentation

## Limitations (Prototype)

**What This System IS:**
- ✅ Deterministic business rule engine
- ✅ Decision explanation framework
- ✅ Workflow orchestration prototype
- ✅ Explainable automation

**What This System IS NOT:**
- ❌ Production-ready application
- ❌ HIPAA-compliant system
- ❌ Real-time integration platform
- ❌ Machine learning system
- ❌ Clinical decision support tool
- ❌ Diagnostic system
- ❌ Persistent data store

**Not Implemented:**
- Database persistence
- Authentication/authorization
- External system integration
- Encryption
- Access controls
- Backup/recovery
- High availability
- Load balancing
- Monitoring/alerting
- Compliance reporting

## Future Enhancements

Potential improvements for production:

1. **Rule Configuration UI:** Allow non-developers to modify rules
2. **Analytics Dashboard:** Track escalation rates, bottlenecks
3. **Notification System:** Alert staff when action needed
4. **Batch Operations:** Process multiple visits at once
5. **Rule Testing Sandbox:** Test rule changes before deployment
6. **Integration Adapters:** Plug-and-play external system connectors
7. **Mobile App:** Allow staff to resolve escalations on mobile
8. **Reporting:** Generate compliance and performance reports

## Summary

The Decision Transparency Model provides:

✅ **Explainability:** Every decision has a clear explanation  
✅ **Traceability:** Complete audit trail with reasoning  
✅ **Actionability:** Specific next steps for staff  
✅ **Determinism:** No black box ML  
✅ **Ownership Clarity:** Explicit responsibility assignment  
✅ **Semantic Precision:** BLOCKED vs ESCALATED distinction  
✅ **Operational Clarity:** Staff know exactly what to do  

This makes the system trustworthy, maintainable, and compliant with healthcare requirements for explainable automation.
