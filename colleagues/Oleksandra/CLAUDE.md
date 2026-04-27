# CLAUDE.md - Pre-Visit Intake Orchestration Engine

## Project Overview

### Purpose

Build a pre-visit intake orchestration and escalation system for a small family medicine clinic.

The system improves intake reliability while preserving human control over clinically sensitive decisions.

### Core Capability

Pre-visit intake orchestration:
- Task creation and tracking (6 required task types per visit)
- Deterministic workflow rule execution
- Issue detection and escalation routing
- Decision transparency with structured explanations
- Explicit ownership and next-action guidance
- Complete audit trail

### Current Implementation State

**Prototype Status:**
- 58 unit tests (100% passing across 3 test suites)
- 5 demo scenarios covering all workflow paths
- Interactive HTML viewer with visual workflow stepper
- Decision transparency layer with 24 reason codes
- Ownership system with 5 owner types
- In-memory only (no persistence)
- Mock data only (no real integrations)

**What This IS:**
- Workflow logic demonstration
- Decision transparency model prototype
- Testable, maintainable TypeScript codebase
- Requirements validation tool for stakeholders

**What This IS NOT:**
- Production-ready system
- HIPAA-compliant application
- Clinical decision support tool
- Diagnostic or triage system
- Integration-ready platform

---

## Core Architecture

### Type System

**Location:** `src/types/enums.ts`, `src/types/interfaces.ts`

**5 Key Enums:**

1. **VisitState** (5 states)
   - NOT_STARTED, IN_PROGRESS, ESCALATED, READY_FOR_REVIEW, CLEARED

2. **TaskStatus** (4 statuses)
   - PENDING, COMPLETED, ESCALATED, BLOCKED

3. **TaskType** (6 required task types)
   - insurance_verification, prior_auth_check, questionnaire, visit_reason, medication_review, allergy_review

4. **Owner** (5 ownership types)
   - system, front_desk, nurse, manager, patient

5. **EscalationTarget** (2 targets)
   - front_desk (administrative), nurse (clinical)

**Critical Interface: DecisionExplanation**

Every workflow decision includes structured explanation:
```typescript
{
  decision: 'completed' | 'escalated' | 'blocked'
  reasonCode: string              // e.g., "INS_VERIFIED"
  reasonText: string              // Human-readable
  ruleApplied: string             // Explicit business rule
  confidence: 'deterministic'     // Always deterministic
  nextAction: string              // Specific guidance
  owner?: Owner                   // Responsibility
  missingData?: string[]          // Present only for BLOCKED
}
```

### Three Core Models

**Location:** `src/models/`

**1. Task (`Task.ts`)**

Represents one intake step with state management.

Key methods:
- `complete(explanation?)` - Marks task complete (throws if already completed)
- `escalate(target, reason, explanation?)` - Routes to human queue (front_desk or nurse)
- `block(reason, explanation?)` - Marks unavailable data (defaults owner to front_desk)

Guardrails:
- Completed tasks cannot be escalated or blocked (throws error)
- All state transitions are irreversible
- Every transition supports optional DecisionExplanation

**2. Visit (`Visit.ts`)**

Represents one patient visit moving through intake.

Key methods:
- `addTask(task)` - Adds task and triggers state update
- `getTask(type)` - Retrieves task by TaskType
- `getAllTasks()` - Returns array of all tasks
- `updateState()` - Computes visit state from task collection (idempotent)
- `completeReview(reviewerName)` - Human approval transition to CLEARED
- `logAuditEvent(type, details)` - Manual audit logging

State computation (stateless):
- 0 tasks → NOT_STARTED
- Any ESCALATED/BLOCKED task → ESCALATED visit
- Any PENDING task → IN_PROGRESS
- All COMPLETED → READY_FOR_REVIEW
- CLEARED only via explicit completeReview() call

**3. AuditEvent (`AuditEvent.ts`)**

Immutable event record with auto-generated ID (timestamp + random suffix).

Records: event type, timestamp, entity reference, details.

### WorkflowEngine

**Location:** `src/engine/WorkflowEngine.ts`

**Responsibilities:**
- Visit creation with automatic 6-task initialization
- Task processing with type-specific deterministic rules
- Human review coordination
- In-memory visit storage (Map<visitId, Visit>)

**Key Pattern:** Every task processing method creates DecisionExplanation before executing state transition.

### File Structure Reference

```
src/
├── types/
│   ├── enums.ts           # All enum types
│   └── interfaces.ts      # DecisionExplanation, PatientInfo, TaskInput
├── models/
│   ├── Task.ts            # Task entity with state transitions
│   ├── Visit.ts           # Visit entity with state computation
│   └── AuditEvent.ts      # Audit logging
├── engine/
│   └── WorkflowEngine.ts  # All workflow rules
└── scenarios/
    ├── mockData.ts        # Mock patient data
    └── runAll.ts          # 5 demo scenarios
```

---

## Decision Transparency Model

### DecisionExplanation Structure

Every task decision includes 7-8 fields providing complete transparency:

| Field | Type | Purpose | Present When |
|-------|------|---------|--------------|
| `decision` | DecisionType | Outcome: completed/escalated/blocked | Always |
| `reasonCode` | string | Machine-readable code (e.g., "INS_VERIFIED") | Always |
| `reasonText` | string | Human-readable explanation | Always |
| `ruleApplied` | string | Explicit business rule formula | Always |
| `confidence` | 'deterministic' | Always "deterministic" (no ML) | Always |
| `nextAction` | string | Specific guidance on what to do next | Always |
| `owner` | Owner | Who is responsible | Always |
| `missingData` | string[] | What data is unavailable | BLOCKED only |

### Reason Code Catalog (24 codes)

**Insurance Verification (4 codes):**
- `INS_VERIFIED` - Insurance verified and active
- `INS_NOT_VERIFIED` - Verification failed
- `INS_NOT_ACTIVE` - Policy not active
- `INS_DATA_UNAVAILABLE` - External system unavailable

**Prior Authorization (5 codes):**
- `PA_NOT_REQUIRED` - No prior auth needed
- `PA_APPROVED` - Prior auth approved and valid
- `PA_NOT_APPROVED` - Prior auth not approved
- `PA_EXPIRED` - Prior auth expired
- `PA_DATA_UNAVAILABLE` - External system unavailable

**Questionnaire (3 codes):**
- `QUEST_COMPLETE` - Questionnaire completed
- `QUEST_INCOMPLETE` - Questionnaire not finished
- `QUEST_MISSING` - No questionnaire data

**Visit Reason (4 codes):**
- `VR_ROUTINE` - Routine visit reason
- `VR_ROUTING_TRIGGER` - Contains routing trigger keyword
- `VR_EMPTY` - Visit reason not provided
- `VR_MISSING` - No visit reason data

**Medication Review (3 codes):**
- `MED_NO_CHANGE` - No changes reported
- `MED_CHANGE_REPORTED` - Changes require reconciliation
- `MED_DATA_MISSING` - No medication data

**Allergy Review (3 codes):**
- `ALLERGY_NO_CHANGE` - No changes reported
- `ALLERGY_CHANGE_REPORTED` - Changes require review
- `ALLERGY_DATA_MISSING` - No allergy data

### Confidence Model

**Always "deterministic":**
- No machine learning or probabilistic models
- No uncertainty ranges or confidence scores
- Same input always produces same output
- 100% explainable and auditable
- No training data required
- No model drift concerns

**Why deterministic?**
- Healthcare regulatory requirements for explainability
- Staff can verify logic themselves
- Complete audit trail to explicit rules
- Easy to maintain without retraining
- Behavior stable over time

### Next Action Pattern

Every non-completed state includes specific, actionable guidance.

**Good next actions:**
- ✅ "Retry insurance verification system or manually verify coverage"
- ✅ "Contact patient to complete pre-visit questionnaire"
- ✅ "Nurse to perform medication reconciliation and update EHR"
- ✅ "Submit prior authorization request to insurance"

**Bad next actions:**
- ❌ "Fix this"
- ❌ "Handle escalation"
- ❌ "Review"

---

## Workflow Rules

### Insurance Verification

**Decision Tree:**

1. **If** insurance data missing → **BLOCK** task
   - Reason code: `INS_DATA_UNAVAILABLE`
   - Next action: "Retry insurance verification system or manually verify coverage"
   - Owner: front_desk
   - Missing data: ["insurance verification status", "policy details"]

2. **Else if** insurance.verified = false → **ESCALATE** to front_desk
   - Reason code: `INS_NOT_VERIFIED`
   - Next action: "Verify insurance coverage manually or request updated information"

3. **Else if** insurance.active = false → **ESCALATE** to front_desk
   - Reason code: `INS_NOT_ACTIVE`
   - Next action: "Contact patient about inactive insurance policy"

4. **Else** (verified = true AND active = true) → **COMPLETE**
   - Reason code: `INS_VERIFIED`
   - Next action: "Task completed, no further action needed"

### Prior Authorization Check

**Decision Tree:**

1. **If** priorAuth data missing → **BLOCK** task
   - Reason code: `PA_DATA_UNAVAILABLE`
   - Next action: "Retry prior authorization system or manually check status"
   - Owner: front_desk
   - Missing data: ["prior authorization status"]

2. **Else if** priorAuth.required = false → **COMPLETE**
   - Reason code: `PA_NOT_REQUIRED`
   - Next action: "Task completed, no further action needed"

3. **Else if** priorAuth.approved = false → **ESCALATE** to front_desk
   - Reason code: `PA_NOT_APPROVED`
   - Next action: "Submit prior authorization request to insurance"

4. **Else if** priorAuth.expirationDate < now → **ESCALATE** to front_desk
   - Reason code: `PA_EXPIRED`
   - Next action: "Request renewal of prior authorization from insurance provider"

5. **Else** (approved = true AND not expired) → **COMPLETE**
   - Reason code: `PA_APPROVED`
   - Next action: "Task completed, no further action needed"

### Questionnaire

**Decision Tree:**

1. **If** questionnaire data missing → **ESCALATE** to front_desk
   - Reason code: `QUEST_MISSING`
   - Next action: "Contact patient to complete pre-visit questionnaire"

2. **Else if** questionnaire.completed = false → **ESCALATE** to front_desk
   - Reason code: `QUEST_INCOMPLETE`
   - Next action: "Contact patient to complete pre-visit questionnaire"

3. **Else** (completed = true) → **COMPLETE**
   - Reason code: `QUEST_COMPLETE`
   - Next action: "Task completed, no further action needed"

### Visit Reason

**Decision Tree:**

1. **If** visitReason data missing → **ESCALATE** to nurse
   - Reason code: `VR_MISSING`
   - Next action: "Contact patient to obtain visit reason"

2. **Else if** visitReason.reason.trim().length = 0 → **ESCALATE** to nurse
   - Reason code: `VR_EMPTY`
   - Next action: "Contact patient to clarify visit reason"

3. **Else if** visitReason contains routing trigger → **ESCALATE** to nurse
   - Reason code: `VR_ROUTING_TRIGGER`
   - Next action: "Nurse to review visit reason and triage appropriately"
   - Matched trigger included in explanation

4. **Else** (reason provided AND no triggers) → **COMPLETE**
   - Reason code: `VR_ROUTINE`
   - Next action: "Task completed, no further action needed"

**Routing Triggers (27 keywords):**

*These are administrative routing triggers, NOT clinical diagnoses.*

**Emergency symptoms:**
- chest pain, shortness of breath, difficulty breathing, severe pain, bleeding, heavy bleeding

**Mental health concerns:**
- self-harm, suicide, suicidal

**Priority indicators:**
- urgent, same day, getting worse, worsening, emergency, severe

**Symptom keywords:**
- fever, high fever, dizzy, dizziness, confusion, confused, unresponsive

**Incident reports:**
- fainting, fainted

**Detection method:** Case-insensitive keyword matching using `includes()`. Not NLP, not clinical interpretation, not diagnosis.

### Medication Review

**Decision Tree:**

1. **If** medication data missing → **ESCALATE** to nurse
   - Reason code: `MED_DATA_MISSING`
   - Next action: "Obtain medication list from patient or EHR"

2. **Else if** medication.changeReported = true → **ESCALATE** to nurse
   - Reason code: `MED_CHANGE_REPORTED`
   - Next action: "Nurse to perform medication reconciliation and update EHR"

3. **Else** (changeReported = false) → **COMPLETE**
   - Reason code: `MED_NO_CHANGE`
   - Next action: "Task completed, no further action needed"

### Allergy Review

**Decision Tree:**

1. **If** allergy data missing → **ESCALATE** to nurse
   - Reason code: `ALLERGY_DATA_MISSING`
   - Next action: "Obtain allergy list from patient or EHR"

2. **Else if** allergy.changeReported = true → **ESCALATE** to nurse
   - Reason code: `ALLERGY_CHANGE_REPORTED`
   - Next action: "Nurse to review allergy changes and update EHR"

3. **Else** (changeReported = false) → **COMPLETE**
   - Reason code: `ALLERGY_NO_CHANGE`
   - Next action: "Task completed, no further action needed"

### BLOCKED vs ESCALATED Distinction

**BLOCKED:**
- **Meaning:** External system or data unavailable (technical/infrastructure issue)
- **Cause:** Missing external data, system timeout, API failure
- **Resolution:** Retry system, manual workaround, wait for recovery
- **Includes:** `missingData` array in DecisionExplanation
- **Examples:** Insurance API returns 503, prior auth database down, network timeout

**ESCALATED:**
- **Meaning:** Business rule requires human review (policy/clinical issue)
- **Cause:** Data present but requires decision, policy violation, clinical need
- **Resolution:** Human evaluates situation and takes action
- **Includes:** No `missingData` array
- **Examples:** Insurance inactive, prior auth expired, medication change, routing trigger

**Both result in:** Visit state = ESCALATED (human intervention needed)

**Key distinction:** DecisionExplanation clarifies which type through `decision` field and presence/absence of `missingData`.

---

## Ownership System

### 5 Owner Types

| Owner | Role | Responsibility |
|-------|------|----------------|
| `system` | Automated | Processing tasks automatically |
| `front_desk` | Administrative | Insurance, prior auth, questionnaires, scheduling |
| `nurse` | Clinical | Visit reason triage, medication/allergy reconciliation |
| `manager` | Coordination | Complex cases with multiple escalation types |
| `patient` | Self-service | Providing missing information (future use) |

### Task Owner Assignment Rules

**By Task Status:**
- PENDING → system (awaiting automated processing)
- COMPLETED → system (no action needed)
- ESCALATED to front_desk → front_desk
- ESCALATED to nurse → nurse
- BLOCKED → front_desk (default, system issue resolution)

**Automatic Assignment:**
- Task.complete() sets owner to system
- Task.escalate(FRONT_DESK, ...) sets owner to front_desk
- Task.escalate(NURSE, ...) sets owner to nurse
- Task.block(...) sets owner to front_desk

### Visit Owner Determination

**Logic in Visit.updateState():**

1. **If** visit has no escalated/blocked tasks:
   - NOT_STARTED → owner = system
   - IN_PROGRESS → owner = system
   - READY_FOR_REVIEW → owner = front_desk
   - CLEARED → owner = system

2. **Else if** visit has escalated/blocked tasks (ESCALATED state):
   - Collect escalation types from all escalated/blocked tasks
   - **If** both nurse + front_desk escalations → owner = **manager** (coordination required)
   - **Else if** only nurse escalations → owner = **nurse**
   - **Else** (only admin escalations or blocked tasks) → owner = **front_desk**

**Manager Coordination Scenario:**

When a visit has both administrative escalations (insurance, prior auth, questionnaire) AND clinical escalations (visit reason, medication, allergy), the manager coordinates resolution across both teams.

Example:
- Task 1: Prior auth expired (front_desk escalation)
- Task 2: Visit reason "chest pain" (nurse escalation)
- Visit owner → manager
- Next action: "Manager review required: visit has both administrative and clinical escalations"

---

## State Management

### Visit States (5 states)

**NOT_STARTED**
- Visit created, no tasks processed yet
- Owner: system
- Next action: "Visit will begin automated intake processing"

**IN_PROGRESS**
- At least one task still pending
- Owner: system
- Next action: "Automated processing in progress"

**ESCALATED**
- One or more tasks escalated or blocked
- Owner: front_desk, nurse, or manager (depends on escalation types)
- Next action: Specific to escalation type

**READY_FOR_REVIEW**
- All tasks completed or resolved
- Awaiting human approval
- Owner: front_desk
- Next action: "Ready for human review and approval"

**CLEARED**
- Human review completed
- Visit approved for appointment
- Owner: system
- Next action: "Visit cleared and ready for appointment"

### Allowed Visit State Transitions

**Forward progression:**
- NOT_STARTED → IN_PROGRESS (tasks added)
- IN_PROGRESS → ESCALATED (any task escalated/blocked)
- IN_PROGRESS → READY_FOR_REVIEW (all tasks completed)
- ESCALATED → READY_FOR_REVIEW (escalations resolved)
- READY_FOR_REVIEW → CLEARED (completeReview called)

**Disallowed:**
- Direct NOT_STARTED → CLEARED
- Direct IN_PROGRESS → CLEARED
- Automatic ESCALATED → CLEARED without review
- Any backward transitions (no "undo")

### Task Statuses (4 statuses)

**PENDING**
- Task exists but not yet processed
- Owner: system

**COMPLETED**
- Task completed successfully with deterministic logic
- Owner: system

**ESCALATED**
- Task requires human review/decision
- Owner: front_desk or nurse (based on escalation target)

**BLOCKED**
- Task cannot proceed due to missing external data
- Owner: front_desk (default)

### Allowed Task Status Transitions

**Forward progression:**
- pending → completed
- pending → escalated
- pending → blocked
- blocked → escalated (after resolution attempt)
- escalated → completed (via human review simulation)

**Disallowed:**
- completed → any other status (immutable)
- Any transition from completed (throws error)

### Human-in-the-Loop Requirement

**CLEARED state is ONLY reachable via completeReview():**
- Prevents automatic visit approval
- Requires explicit human review
- Creates audit trail of reviewer name and timestamp
- Can be called from READY_FOR_REVIEW or ESCALATED states

**completeReview(reviewerName) method:**
```typescript
visit.completeReview("Jane Doe (Front Desk)")
```
- Validates current state (READY_FOR_REVIEW or ESCALATED)
- Sets state to CLEARED
- Records reviewedBy and reviewedAt
- Sets owner to system
- Logs review_completed audit event

---

## Critical Guardrails

### 1. No Clinical Judgment

**Principle:** The system NEVER diagnoses, interprets symptoms, or makes clinical decisions.

**Implementation:**
- Visit reason uses keyword matching only (27 predefined keywords)
- No NLP, no ML models, no medical knowledge base
- Routing triggers are administrative flags, not clinical assessments
- Medication/allergy changes are reported to nurse, not interpreted

**Example of what system DOES NOT do:**
- ❌ "Chest pain indicates cardiac event" → WRONG
- ✅ "Chest pain contains routing trigger → escalate to nurse" → CORRECT

### 2. No Autonomous Triage

**Principle:** The system NEVER determines urgency or priority of care.

**Implementation:**
- No "urgent" vs "routine" classification
- No same-day scheduling decisions
- No appointment priority assignment
- Routing triggers flag for nurse review, not urgency determination

### 3. No Medication/Allergy Record Updates

**Principle:** The system NEVER modifies clinical records autonomously.

**Implementation:**
- Medication changes are escalated to nurse, not applied
- Allergy changes are escalated to nurse, not applied
- System reports changes, nurse reconciles and updates EHR
- No write access to medication/allergy data structures

### 4. Completed Tasks Cannot Be Modified

**Principle:** Once a task is completed, it is immutable.

**Implementation:**
```typescript
task.complete()
// Later attempts throw error:
task.escalate() // throws: "Cannot escalate completed task"
task.block()    // throws: "Cannot block completed task"
```

**Rationale:** Ensures audit trail integrity, prevents data corruption.

### 5. Missing Data Must Be Escalated or Blocked

**Principle:** The system NEVER infers or assumes missing data.

**Implementation:**
- Missing insurance data → BLOCK (external system issue)
- Missing questionnaire → ESCALATE (patient action needed)
- Missing visit reason → ESCALATE (patient action needed)
- No default values, no assumptions, no guessing

**Conservative approach:** When uncertain, escalate rather than complete.

### 6. Routing Triggers Are Administrative Only

**Principle:** Keyword matches are for routing, not clinical interpretation.

**Implementation:**
- "Chest pain" triggers nurse review (not cardiac diagnosis)
- "Fever" triggers nurse review (not infection diagnosis)
- "Dizzy" triggers nurse review (not neurological assessment)
- Purpose: Ensure appropriate staff member reviews visit reason

**Critical distinction:** Administrative routing ≠ Clinical triage

---

## Operational Constraints

### Prototype Limitations

**In-Memory Only:**
- No database persistence
- Visits stored in Map<string, Visit>
- Data lost on process restart
- Suitable for prototype/demo only

**Mock Data Only:**
- No real external system integration
- Insurance, EHR, prior auth systems stubbed
- TaskInput provided directly (no API calls)
- All scenarios use mock patient data

**No Authentication:**
- No user identity verification
- No role-based access control
- Reviewer name stored as plain string
- No session management

**No HIPAA Compliance:**
- No PHI encryption (at rest or in transit)
- No access audit logging for security
- No data retention policies
- No business associate agreements
- Not suitable for real patient data

**Single-Threaded Processing:**
- No concurrent visit handling
- No locking or transaction support
- Sequential task processing only
- No async/await patterns

**6 Required Tasks:**
- Every visit requires all 6 task types
- No task type customization
- Fixed workflow structure
- Cannot skip or add task types

**2 Escalation Targets:**
- Only front_desk and nurse
- Manager assigned by engine logic (not explicit escalation)
- No specialist or physician escalations
- No custom escalation targets

### NOT Implemented

**Infrastructure:**
- ❌ Database persistence (PostgreSQL, MongoDB, etc.)
- ❌ External API integrations (real insurance, EHR, prior auth)
- ❌ Message queues or event buses
- ❌ Caching layer
- ❌ Load balancing or high availability

**Security:**
- ❌ Authentication (OAuth, SAML, etc.)
- ❌ Authorization (RBAC, permissions)
- ❌ Encryption (at rest or in transit)
- ❌ Security audit logging
- ❌ PHI handling procedures

**Compliance:**
- ❌ HIPAA technical safeguards
- ❌ Data retention and destruction
- ❌ Patient consent tracking
- ❌ Breach notification
- ❌ Business associate agreements

**Advanced Features:**
- ❌ Advanced NLP for visit reason classification
- ❌ ML models for risk prediction
- ❌ Notification system (email, SMS, push)
- ❌ Analytics dashboard
- ❌ Customizable workflow rules (UI-based configuration)

---

## Testing and Validation

### Test Coverage

**Statistics:**
- 3 test suites (Task, Visit, WorkflowEngine)
- 58 tests total
- 100% passing
- No skipped or pending tests

**Task.test.ts (13 tests):**
- Constructor initialization
- complete() validation and error handling
- escalate() validation with both targets
- block() validation
- Preventing modification of completed tasks
- JSON serialization

**Visit.test.ts (14 tests):**
- Constructor and initial state
- State transitions for all 5 states
- Task management (add, retrieve, getAllTasks)
- Owner assignment for all scenarios
- completeReview() validation
- Audit event logging
- JSON serialization

**WorkflowEngine.test.ts (31 tests):**
- Visit creation and 6-task initialization
- All 6 task type decision rules
- Insurance verification (all 4 outcomes)
- Prior authorization (all 5 outcomes)
- Questionnaire (all 3 outcomes)
- Visit reason (all 4 outcomes including routing triggers)
- Medication review (all 3 outcomes)
- Allergy review (all 3 outcomes)
- BLOCKED vs ESCALATED distinction
- Visit state progression through all states
- Audit event generation

### What Tests Validate

**Deterministic Rule Execution:**
- Same input produces same output every time
- All 24 reason codes triggered correctly
- Decision explanations structure complete

**State Transition Correctness:**
- Allowed transitions work
- Disallowed transitions throw errors
- State computation matches rules

**Owner Assignment Logic:**
- Task owners match status and target
- Visit owners match escalation types
- Manager assigned for mixed escalations

**Decision Explanation Structure:**
- All required fields present
- Reason codes match outcomes
- Next actions are specific
- Missing data included for BLOCKED

**Audit Trail Completeness:**
- Events logged for all state changes
- Event details include explanations
- Timestamps recorded correctly

**Edge Cases:**
- Empty strings handled
- Expired dates detected
- Missing data caught
- Null/undefined inputs handled

### Demo Scenarios

**5 scenarios in src/scenarios/runAll.ts:**

1. **Successful Intake**
   - All 6 tasks complete successfully
   - Visit progresses: NOT_STARTED → IN_PROGRESS → READY_FOR_REVIEW → CLEARED
   - Shows human review step
   - Demonstrates complete workflow

2. **Prior Auth Expired**
   - Prior authorization check finds expired auth
   - Task escalated to front_desk
   - Visit state: ESCALATED
   - Demonstrates administrative escalation

3. **Routing Trigger Detected**
   - Visit reason contains "chest pain"
   - Task escalated to nurse
   - Visit state: ESCALATED
   - Demonstrates clinical escalation

4. **Medication Change Reported**
   - Patient reports medication change
   - Task escalated to nurse for reconciliation
   - Visit state: ESCALATED
   - Demonstrates clinical escalation

5. **Missing External Data (BLOCKED)**
   - Insurance verification data unavailable
   - Task BLOCKED (not escalated)
   - Visit state: ESCALATED
   - Demonstrates system issue vs business rule distinction

### Output Formats

**Console Output:**
- Visit summary with state and owner
- Task list with statuses and owners
- Decision explanations with reason codes
- Next actions for escalated/blocked tasks
- Audit trail (last 10 events)

**JSON Output:**
- Complete visit state
- All task details with decision explanations
- Full audit event history
- Timestamps and owner tracking
- See `output/sample-visit-state.json`

**HTML Viewer:**
- Interactive visual workflow stepper
- Color-coded task status cards
- Decision explanation display
- Next action guidance
- Formatted audit trail
- See `output/visit-viewer.html`

---

## Extension Guidance

### For Production Deployment

**1. Persistence Layer:**
- Choose database: PostgreSQL (relational) or MongoDB (document)
- Design schema: visits table, tasks table, audit_events table
- Implement repository pattern for data access
- Add transaction support for state changes

**2. External System Integration:**
- Insurance verification API adapter (eligibility checks)
- EHR system connector (HL7 FHIR, Epic API, Cerner API)
- Prior authorization system integration
- Implement retry logic with exponential backoff
- Add circuit breakers for fault tolerance

**3. Authentication & Authorization:**
- Implement OAuth 2.0 or SAML for SSO
- Role-based access control (RBAC)
- Permission checks before state transitions
- Audit logging for all access

**4. HIPAA Compliance:**
- Encrypt PHI at rest (AES-256)
- Encrypt PHI in transit (TLS 1.3)
- Implement access audit logging
- Add data retention and destruction policies
- Create incident response plan
- Execute business associate agreements

**5. Notification System:**
- Email notifications for escalations
- SMS alerts for urgent issues
- Push notifications for mobile app
- Slack/Teams integration for staff alerts

**6. Analytics & Monitoring:**
- Track escalation rates by task type
- Identify bottlenecks in workflow
- Monitor completion times
- Alert on high failure rates
- Dashboard for managers

**7. Advanced Features:**
- ML-based visit reason classification (with human review)
- Predictive analytics for no-show risk
- Customizable workflow rules (UI-based configuration)
- Multi-tenancy for multiple clinics
- Scheduling system integration

### Modifying Workflow Rules

**Location:** `src/engine/WorkflowEngine.ts`

**To modify existing task rules:**
1. Find the appropriate process method (e.g., `processInsuranceVerification`)
2. Update decision logic while preserving DecisionExplanation creation
3. Update reason codes if needed (add to catalog)
4. Update tests in `WorkflowEngine.test.ts`
5. Run `npm test` to validate

**Example - Adding new insurance verification check:**
```typescript
// In processInsuranceVerification method:
if (insurance.copayAmount > 100) {
  const explanation: DecisionExplanation = {
    decision: DecisionType.ESCALATED,
    reasonCode: 'INS_HIGH_COPAY',
    reasonText: `High copay amount: $${insurance.copayAmount} requires patient notification`,
    ruleApplied: 'RULE: If copay > $100 → ESCALATE to front_desk',
    confidence: 'deterministic',
    nextAction: 'Contact patient to confirm willingness to pay copay',
    owner: Owner.FRONT_DESK
  };
  task.escalate(EscalationTarget.FRONT_DESK, explanation.reasonText, explanation);
  return;
}
```

### Adding New Task Types

**Steps:**

1. **Add to TaskType enum** (`src/types/enums.ts`):
   ```typescript
   export enum TaskType {
     // existing...
     IDENTITY_VERIFICATION = 'identity_verification'
   }
   ```

2. **Add reason codes** for the new task type (document in DECISION_TRANSPARENCY.md)

3. **Create processing method** in WorkflowEngine:
   ```typescript
   private processIdentityVerification(task: Task, input: TaskInput): void {
     // Decision logic with DecisionExplanation
   }
   ```

4. **Update visit creation** to include new task in initialization

5. **Add tests** in WorkflowEngine.test.ts:
   ```typescript
   describe('Identity Verification', () => {
     test('completes when verified', () => { /* ... */ });
     test('escalates when not verified', () => { /* ... */ });
   });
   ```

6. **Update mock data** with new task input structure

7. **Run tests**: `npm test` (should have 60+ tests now)

### Adding New Owner Types or Escalation Targets

**To add new escalation target** (e.g., "physician"):

1. **Add to EscalationTarget enum** (`src/types/enums.ts`):
   ```typescript
   export enum EscalationTarget {
     FRONT_DESK = 'front_desk',
     NURSE = 'nurse',
     PHYSICIAN = 'physician'  // NEW
   }
   ```

2. **Add to Owner enum**:
   ```typescript
   export enum Owner {
     // existing...
     PHYSICIAN = 'physician'  // NEW
   }
   ```

3. **Update Task.escalate()** to map new target to owner

4. **Update Visit owner logic** if needed (coordination scenarios)

5. **Update HTML viewer** with new owner badge styling

6. **Update tests** to cover new escalation path

### Testing Requirements

**For any code change:**
- All 58 existing tests must pass
- Add tests for new behavior (decision rules, state transitions, owner logic)
- Test error handling and edge cases
- Verify decision explanation structure
- Validate reason codes are correct

**Test command:**
```bash
npm test              # Run all tests
npm run test:watch    # Watch mode for development
```

---

## Key Files Reference

### To Understand...

| Topic | See File |
|-------|----------|
| **Type system** | `src/types/enums.ts`, `src/types/interfaces.ts` |
| **Decision transparency model** | `src/types/interfaces.ts` (DecisionExplanation) |
| **Task behavior** | `src/models/Task.ts` |
| **Visit state computation** | `src/models/Visit.ts` (updateState method) |
| **Workflow rules** | `src/engine/WorkflowEngine.ts` |
| **All 6 task type rules** | `src/engine/WorkflowEngine.ts` (process* methods) |
| **Routing trigger list** | `src/engine/WorkflowEngine.ts` (detectRoutingTrigger) |
| **Owner assignment logic** | `src/models/Task.ts`, `src/models/Visit.ts` (updateState) |
| **Test examples** | `src/models/Task.test.ts`, `src/models/Visit.test.ts`, `src/engine/WorkflowEngine.test.ts` |
| **Demo scenarios** | `src/scenarios/runAll.ts` |
| **Mock patient data** | `src/scenarios/mockData.ts` |
| **Interactive visualization** | `output/visit-viewer.html` |

### Critical Files for Deep Dive

**Architecture:**
- `src/types/enums.ts` - All enum types (30 lines, easy to scan)
- `src/types/interfaces.ts` - All interfaces including DecisionExplanation

**Core Logic:**
- `src/models/Task.ts` - Task entity (80 lines)
- `src/models/Visit.ts` - Visit entity (150 lines, focus on updateState)
- `src/engine/WorkflowEngine.ts` - All workflow rules (500+ lines)

**Examples:**
- `src/scenarios/mockData.ts` - Patient and scenario data structures
- `output/scenario-walkthrough.md` - Step-by-step example with explanations
- `output/sample-visit-state.json` - Example JSON output

**Validation:**
- `src/engine/WorkflowEngine.test.ts` - 31 tests covering all rules
- Run `npm test` to see all tests pass

---

## Summary

This comprehensive CLAUDE.md reflects the Loop 3 implementation state with:

✅ **Decision transparency layer** with 24 reason codes and structured explanations
✅ **Ownership system** with 5 owner types and automatic assignment
✅ **6 task types** with explicit decision trees
✅ **5 visit states** with clear transition rules
✅ **27 routing triggers** for administrative routing (not clinical diagnosis)
✅ **BLOCKED vs ESCALATED** semantic distinction
✅ **Human-in-the-loop** requirement (CLEARED only via completeReview)
✅ **58 passing tests** validating all behavior
✅ **5 demo scenarios** covering all workflow paths
✅ **Interactive HTML viewer** with visual workflow stepper

**Key Principles:**
- No clinical judgment (keyword matching only)
- Conservative escalation (when uncertain, escalate)
- Deterministic rules (no ML, 100% explainable)
- Immutable completed tasks (audit trail integrity)
- Explicit ownership (clear responsibility)

**Use this file as:**
- Authoritative reference for contributors
- Quick lookup for workflow rules and reason codes
- Extension guide for production planning
- Orientation guide for new developers

**For more details:** See referenced files and test suites for examples.
