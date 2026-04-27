# Claude Build Notes

## Loop 1

### Build Goal
Validate whether the agent specification can be translated into a working workflow engine that:

- models intake tasks and visit states
- applies deterministic rules
- performs appropriate escalation
- enforces guardrails

### Prompt Used
Build a small prototype of a pre-visit intake orchestration and escalation engine for a family medicine clinic.

The goal is to model the workflow logic, not to build a full production application.

Use mocked data only. Do not integrate with real external systems yet.

Core requirements:

1. Model a Visit entity with these states:
- NOT_STARTED
- IN_PROGRESS
- READY_FOR_REVIEW
- ESCALATED
- CLEARED

2. Model intake tasks with these task types:
- insurance_verification
- prior_auth_check
- questionnaire
- visit_reason
- medication_review
- allergy_review

Each task should support these statuses:
- pending
- completed
- escalated
- blocked

3. When a visit is created, create all required intake tasks.

4. Implement deterministic workflow rules:
- if insurance verification succeeds, mark insurance task completed
- if insurance verification fails or is unknown, escalate to front desk
- if prior auth is required and missing or expired, escalate to front desk
- if questionnaire is incomplete, escalate to front desk
- if visit reason contains sensitive or ambiguous language, escalate to nurse
- if medication change is reported, escalate to nurse
- if allergy change is reported, escalate to nurse

5. Implement guardrails:
- do not perform clinical judgment
- do not interpret symptoms beyond conservative flagging
- do not auto-update medication or allergy records
- do not silently complete tasks when data is missing

6. Compute overall visit state:
- NOT_STARTED when no work has begun
- IN_PROGRESS when tasks exist and are being processed
- ESCALATED if any task is escalated or blocked
- READY_FOR_REVIEW when all tasks are completed or appropriately escalated for human review
- CLEARED only when the visit is fully processed with no unresolved blockers

7. Provide mock scenarios to demonstrate:
- successful intake flow
- prior auth missing
- sensitive visit reason
- medication change reported

8. Keep the code simple, readable, and modular.

9. Include basic tests for task state transitions and visit escalation logic.

10. Output:
- project structure
- source code
- sample test data
- instructions to run locally
- explanation of major design choices

Claude produced a working TypeScript prototype with:

- Visit and Task entities with explicit state management
- WorkflowEngine implementing deterministic intake rules
- Six intake task types:
  - insurance_verification
  - prior_auth_check
  - questionnaire
  - visit_reason
  - medication_review
  - allergy_review
- Escalation routing:
  - administrative → front desk
  - clinical/sensitive → nurse
- Four demo scenarios
- 39 unit tests covering logic and transitions

---

## What Worked

### 1. Workflow Orchestration
- Tasks are created correctly per visit
- Deterministic rules are applied consistently
- Task state transitions behave as expected

### 2. Escalation Logic
- Prior auth issues correctly escalate to front desk
- Sensitive visit reasons escalate to nurse
- Medication changes escalate correctly

### 3. Guardrails
- No clinical judgment implemented
- No autonomous record updates
- Conservative escalation applied

### 4. Code Quality
- Modular structure (models, engine, scenarios)
- Clear separation of concerns
- Strong test coverage

---

## What Didn’t Match Expectation

### 1. READY_FOR_REVIEW State Not Clearly Used
- Defined in spec but not meaningfully exercised in scenarios
- Most flows result in either CLEARED or ESCALATED

### 2. Visit Reason Logic Too Broad
- Keyword list includes terms like "depression", "anxiety", "abuse"
- Risk of being interpreted as clinical classification rather than routing

### 3. Auditability Overstated
- Prototype describes system as auditable
- But:
  - no persistence
  - no audit logs
  - no access tracking

### 4. Escalation Roles Assumed, Not Validated
- Nurse vs front desk split implemented
- Not validated against real workflow

---

## Diagnosis

### Spec Ambiguity
- Definition of "sensitive or ambiguous language"
- Intended use of READY_FOR_REVIEW state

### Design Gaps
- No audit logging model
- No handling of missing external data beyond escalation
- No explicit definition of "completion" vs "ready for review"
- No representation of human review step

### Not Builder Misread
- Implementation aligns well with provided spec
- No major violations of constraints observed

---

## Spec Updates Needed

### 1. Clarify Visit States
- Define exact difference:
  - READY_FOR_REVIEW = all tasks completed or escalated, awaiting human validation
  - CLEARED = human validation complete

### 2. Refine Visit Reason Handling
- Reframe as:
  - "conservative escalation triggers"
- Remove implication of clinical classification
- Move keyword list to configurable example

### 3. Adjust Audit Language
- Replace "auditable" with:
  - "designed for auditability"
- Explicitly state prototype limitations

### 4. Define Escalation Ownership as Assumption
- Move nurse vs front desk routing into assumption log

---

## Assumptions Updated from Build

- A7 — Prior authorization requirement varies by visit type
- A8 — Clinical escalation requires nursing involvement

---

## Next Prompt Changes

For next iteration:

1. Explicitly define READY_FOR_REVIEW behavior
2. Add requirement for:
   - audit event logging (even mock)
3. Add rule:
   - missing external data → BLOCKED or ESCALATED
4. Refine visit reason handling:
   - avoid clinical interpretation language
5. Ask Claude to:
   - simulate human review step
   - show transition from READY_FOR_REVIEW → CLEARED

---

## Key Learning from Loop 1

The spec is sufficiently precise to produce a working workflow engine.

However, the build revealed:
- unclear state semantics
- implicit assumptions about roles
- missing operational concepts (audit, review step)

These gaps must be resolved before treating the specification as production-ready.

# Loop 2

## Build Goal

Refine the workflow engine to:

- introduce meaningful READY_FOR_REVIEW state
- model human review explicitly
- distinguish BLOCKED vs ESCALATED
- introduce audit event tracking
- improve reviewer-facing clarity

---

## Prompt Used

Revise the existing prototype of the pre-visit intake orchestration engine.

Do not rebuild from scratch unless necessary. Evolve the current TypeScript prototype.

The purpose of this iteration is to improve state semantics, observability, and reviewer-facing clarity.

Please implement the following changes:

1. READY_FOR_REVIEW behavior
- Explicitly implement READY_FOR_REVIEW as a meaningful visit state.
- A visit should move to READY_FOR_REVIEW when:
  - no required task remains pending
  - all required tasks are either completed, escalated, or blocked with explicit ownership and reason
  - the automated workflow is finished and the visit is awaiting human review
- CLEARED should only happen after an explicit simulated human review step.
- Add at least one demo scenario that reaches READY_FOR_REVIEW before transitioning to CLEARED.

2. Mock audit event logging
- Add an AuditEvent model or equivalent structure.
- Log at least:
  - task created
  - task completed
  - task escalated
  - task blocked
  - visit state changed
  - review completed
- This can be in-memory only. No database required.
- Make audit events visible in demo output and sample JSON output.

3. Missing external data behavior
- Add explicit handling for missing or unavailable external data.
- Required rule:
  - missing external data must never be silently treated as complete
  - missing data must produce BLOCKED or ESCALATED according to the rule
  - the reason must be logged
- Add at least one scenario demonstrating missing external data.

4. Refine visit reason handling
- Avoid language that implies clinical interpretation.
- Reframe visit-reason logic as conservative routing / administrative escalation triggers only.
- Keep deterministic logic only.
- Use configurable example trigger phrases such as:
  - chest pain
  - shortness of breath
  - severe pain
  - bleeding
  - fainting
  - self-harm language
  - urgent
  - same day
  - getting worse
- Make clear in code comments and docs that these are routing triggers, not diagnosis or severity scoring.

5. Human review step
- Add a simulated human review action.
- This should allow a visit in READY_FOR_REVIEW to move to CLEARED.
- The review action should generate audit events.

6. Reviewer-facing visualization outputs
Please add:
- a markdown sequence diagram showing the happy path and one escalated path
- sample JSON/state output for at least one visit
- a tiny web page that shows one visit and its task statuses, escalation target, reason code, and overall visit state

7. Preserve prototype scope
Do NOT add:
- real EHR integration
- real insurance API integration
- authentication
- persistence
- HIPAA implementation
- advanced NLP/ML models

8. Tests
Add or update tests for:
- READY_FOR_REVIEW transition
- READY_FOR_REVIEW -> CLEARED transition after simulated review
- audit event creation
- missing external data behavior
- visit-reason routing trigger behavior

9. Documentation
Update the prototype docs to:
- avoid overstating compliance or auditability
- clearly distinguish prototype behavior from production requirements
- explain the difference between READY_FOR_REVIEW and CLEARED

Output requested:
- updated project structure
- updated code
- updated tests
- markdown sequence diagram
- sample JSON/state output
- tiny web page
- short explanation of design changes and tradeoffs

---

## What Was Built

The prototype was extended with:

- Fully implemented `READY_FOR_REVIEW` state
- Explicit human review step enabling transition to `CLEARED`
- AuditEvent model with event tracking:
  - task_created
  - task_completed
  - task_escalated
  - task_blocked
  - visit_state_changed
  - review_completed
- Missing external data scenario using `BLOCKED`
- Five demo scenarios
- Updated test suite (≈58 tests)
- Lightweight web UI showing:
  - visit state
  - task statuses
  - audit trail

---

## What Worked

### State Model
- READY_FOR_REVIEW now acts as a real boundary between automation and human review
- CLEARED requires explicit review action
- State transitions align with intended workflow

### Missing Data Handling
- BLOCKED introduced and used correctly
- No silent completion when data unavailable

### Audit Visibility
- Event log shows clear sequence of system actions
- Supports reasoning about workflow execution

### Human-in-the-loop Model
- Review step makes system behavior realistic and compliant with constraints

### Code Quality
- Maintained modular structure
- Tests extended and passing

---

## What Didn’t Match Expectation

### Workflow Communication in UI
- UI shows current state but not progression clearly
- No explicit indication of:
  - previous states
  - next step
  - overall workflow stage

### Documentation Consistency
- Some existing docs likely still reflect Loop 1:
  - "no UI"
  - "no audit logging"
  - 4 scenarios instead of 5
- Creates inconsistency risk for reviewer

### Visit Reason Handling Still Assumption-Heavy
- Routing trigger logic works technically
- But:
  - trigger set is arbitrary
  - not validated with real workflow
  - still needs explicit positioning as assumption

### Escalation Ownership Not Validated
- Nurse vs front desk split implemented
- Still an assumption about clinic operations

### BLOCKED Semantics Not Fully Mature
- Correctly introduced
- But still unclear:
  - whether BLOCKED always implies escalation
  - whether BLOCKED must be resolved before READY_FOR_REVIEW

---

## Diagnosis

### Spec Ambiguity
- Exact semantics of BLOCKED vs ESCALATED
- Boundaries of visit-reason routing triggers
- Definition of “ready” vs “cleared”

### Design Gaps
- UI does not clearly communicate workflow progression
- Documentation not aligned across repo
- Operational ownership (roles) still assumed
- No explicit definition of completion criteria after escalation

### Not Builder Misread
- Implementation aligns well with refined spec
- No major constraint violations observed

---

## Spec Updates Needed

### 1. Clarify BLOCKED Behavior
- Define whether BLOCKED:
  - must be escalated
  - blocks READY_FOR_REVIEW
  - requires explicit ownership

### 2. Strengthen Workflow Visibility
- Add visual workflow stepper:
  - NOT_STARTED → IN_PROGRESS → READY_FOR_REVIEW → CLEARED
- Highlight current stage clearly

### 3. Tighten Language
- Replace:
  - "production-ready"
- With:
  - "prototype ready for review"
- Clarify audit = mock, not compliance-grade

### 4. Explicitly Mark Assumptions
- Visit reason triggers
- Escalation ownership (nurse vs front desk)

### 5. Align Documentation
- Update README and prototype docs to reflect:
  - UI exists
  - audit events exist
  - 5 scenarios exist

---

## What Is Now Validated

- Workflow engine can be built from spec
- State machine can be implemented cleanly
- Escalation logic is enforceable
- Guardrails can be respected in implementation
- Human review integration is feasible

---

## What Is NOT Yet Validated

- Real clinic workflow alignment
- Correct ownership of escalation roles
- Acceptability of routing triggers
- Business impact (effort reduction)
- Production compliance (HIPAA, audit, access control)

---

## Key Learning from Loop 2

The system is now a **credible prototype**:

- It demonstrates workflow feasibility
- It models human-in-the-loop interaction
- It exposes key assumptions and design gaps

However:

- usability and communication remain weaker than logic
- documentation consistency is critical for reviewer trust
- several operational assumptions remain unvalidated

---

## Next Steps (if continued)

- improve UI workflow clarity
- clean and align documentation
- refine BLOCKED semantics
- validate escalation ownership assumptions

# Loop 3

## Build Goal

Improve decision transparency, workflow clarity, and operational usability without adding new functional scope.

This iteration focused on making the system easier to understand and explain by:
- exposing structured decision explanations
- making ownership and next actions explicit
- improving workflow progression visibility in the UI
- clarifying the distinction between BLOCKED and ESCALATED tasks

---

## Prompt Used

Refine the existing intake orchestration prototype to improve decision transparency, workflow clarity, and operational usability.

Do not add new functional scope. Focus on making the system explainable and unambiguous.

Implement the following improvements:

1. Decision Explanation Layer

For every task decision (completed, escalated, blocked), include structured explanation data:

- decision (completed / escalated / blocked)
- reason_code
- reason_text
- rule_applied (explicit condition that triggered decision)
- confidence (deterministic)
- next_action (what should happen next)

Expose this in:
- JSON output
- UI
- audit trail (where appropriate)

---

2. Next-Step and Ownership Clarity

For each task and visit, explicitly show:

- current owner (system / front desk / nurse / manager)
- next required action
- whether the system is waiting or completed

---

3. Workflow Stepper Visualization

Add a clear workflow progression indicator:

States:
NOT_STARTED → IN_PROGRESS → ESCALATED → READY_FOR_REVIEW → CLEARED

Requirements:
- highlight current state
- show completed vs pending steps
- visually distinguish ESCALATED paths

This should be visible in the UI.

---

4. BLOCKED vs ESCALATED Clarification

Enhance both logic and display:

- clearly differentiate:
  - BLOCKED = system/data issue
  - ESCALATED = business or clinical routing issue
- display required action for each
- ensure BLOCKED tasks show:
  - what data is missing
  - who is responsible for resolution

---

5. Visit Completion Logic (Explicit)

Display and enforce:

- READY_FOR_REVIEW:
  all tasks resolved (completed or escalated), awaiting human review

- CLEARED:
  human review completed and all issues acknowledged/resolved

Make this visible in UI and JSON output.

---

6. Improved UI Clarity (Minimal, Not Polished)

Update the existing web page to:

- include workflow stepper at top
- show:
  - visit state
  - next step
  - responsible owner
- display decision explanation for each task
- make escalation reasons clearly visible

Do NOT focus on styling. Focus on clarity.

---

7. Enhanced Sample Output

Provide:

- sample JSON for:
  - successful visit
  - escalated visit
  - blocked visit
- markdown explanation of one full scenario:
  step-by-step with decisions

---

8. Documentation Update

Update prototype documentation to:

- explain decision explanation model
- explain BLOCKED vs ESCALATED
- clarify workflow states in plain language
- remove any claims implying production readiness or compliance

---

9. Tests

Add or update tests to validate:

- decision explanation is always present
- next_action is defined for all non-completed states
- correct ownership assignment
- correct workflow progression

---

Constraints:

- Do not add real integrations
- Do not add authentication or persistence
- Do not add ML/NLP models
- Keep system deterministic and explainable

---

Output:

- updated code
- updated UI
- updated JSON examples
- updated documentation
- explanation of design changes

---

## What Was Built

The prototype was refined with:

- Structured `decisionExplanation` objects for task decisions, including:
  - decision
  - reasonCode
  - reasonText
  - ruleApplied
  - confidence
  - nextAction
- Explicit ownership and next action fields at both task and visit level
- Improved distinction between:
  - `BLOCKED` = external system or data issue
  - `ESCALATED` = business-rule or clinical-adjacent routing issue
- Updated UI with:
  - workflow stepper
  - current owner
  - next action
  - decision explanation visible on task cards
- Improved audit trail formatting showing decision context
- Additional documentation artifacts for decision transparency and scenario walkthroughs
- Existing tests remained passing

---

## What Worked

### 1. Decision Transparency
- The system now explains why each task reached its current state
- Decision reasoning is visible in both structured JSON and the UI
- Reason codes and applied rules make the behavior easier to inspect and defend

### 2. Workflow Clarity
- The workflow stepper makes visit progression easier to understand
- Current state is now visually anchored in the UI rather than implied

### 3. Ownership and Next Action
- Tasks and visits now show:
  - current owner
  - next required action
- This makes the prototype more operationally realistic

### 4. BLOCKED vs ESCALATED Differentiation
- The prototype now communicates the difference between technical/system issues and workflow/business issues more clearly
- The distinction is visible in both the decision explanation and the UI

### 5. Reviewer-Facing Communication
- The HTML viewer is now substantially better aligned with the backend logic
- The prototype is easier to explain without forcing the reviewer to inspect raw JSON

---

## What Didn’t Fully Match Expectation

### 1. UI Still Uses Demo Data Structure Inline
- The HTML viewer now reflects the improved logic
- But it still embeds sample data directly in the page rather than loading generated output artifacts
- This is acceptable for prototype review, but not ideal architecture

### 2. Some Documentation Proliferation Remains
- New explanation artifacts were added
- However, the repo may now have too many narrative markdown files at the top level
- This creates reviewer scanability risk

### 3. BLOCKED Semantics Still Need Final Wording Discipline
- The prototype behavior is clearer
- But documentation must still state very carefully whether:
  - blocked tasks always require named ownership
  - blocked tasks prevent READY_FOR_REVIEW
  - blocked tasks are operationally resolved the same way as escalations

### 4. Operational Assumptions Still Unvalidated
- Nurse vs front desk routing remains an assumption
- Visit-reason routing triggers remain prototype examples rather than validated clinic policy

---

## Diagnosis

### Spec Ambiguity Reduced
Compared with Loop 2, ambiguity is lower in:
- visit progression
- task explanation
- ownership and next action display

### Remaining Spec Ambiguity
- final semantics of `BLOCKED`
- exact clinic ownership model for escalations
- validated routing-trigger policy for visit reasons

### Design Gaps Reduced
Compared with Loop 2, the system now better addresses:
- explainability
- workflow visibility
- operator guidance

### Remaining Design Gaps
- repository/documentation sprawl
- separation of demo data from viewer
- final consistency pass across docs

### Not Builder Misread
- Implementation appears aligned with the Loop 3 prompt
- No major prompt violation is evident from the prototype output

---

## Spec Updates Needed

### 1. Finalize BLOCKED Semantics
Explicitly state:
- whether blocked tasks prevent READY_FOR_REVIEW
- whether blocked tasks always require explicit ownership
- whether blocked tasks are resolved through retry, workaround, or human override

### 2. Keep Routing Triggers Framed as Assumptions
Continue to document visit-reason triggers as:
- conservative prototype routing examples
- not validated clinic policy
- not clinical classification logic

### 3. Align All Docs to Loop 3 State
Update repo-facing docs so they consistently describe:
- decision transparency
- workflow stepper / viewer
- owner and next-action fields
- prototype limitations

---

## What Is Now Validated

- Workflow engine remains buildable from the spec
- State machine is understandable and demonstrable
- Decision logic can be made transparent and inspectable
- Ownership and next actions can be surfaced clearly
- Reviewer-facing UI can reflect backend workflow meaningfully

---

## What Is NOT Yet Validated

- Real clinic workflow alignment
- Correct escalation ownership by role
- Acceptability of visit-reason routing trigger set
- Real business impact
- Production compliance / security / integration viability

---

## Key Learning from Loop 3

The prototype now explains itself much better.

Loop 1 proved the spec was buildable.  
Loop 2 produced a credible workflow prototype.  
Loop 3 improved the system’s explainability and operational clarity.

At this point, the main remaining work is no longer core functionality. It is:
- documentation consistency
- repo cleanliness
- tighter communication of assumptions and limits

This makes housekeeping the correct next step rather than another feature iteration.

---

## Next Steps

- run housekeeping/refactor pass for docs and repo structure
- consolidate redundant markdown files
- make README the single entry point
- align all documentation with Loop 3 behavior