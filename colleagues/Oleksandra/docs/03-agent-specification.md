# Agent Specification

## Purpose

Build a pre-visit intake orchestration and escalation engine for a small family medicine clinic.

The system’s job is to improve intake reliability before the visit by:
- creating and tracking required intake tasks
- applying deterministic administrative workflow rules
- routing unresolved or sensitive cases to the correct human queue
- maintaining explicit state transitions and audit events

The system is not a clinical agent. It must not diagnose, triage, or make care decisions.

---

## Scope

### In Scope
- Visit intake task creation
- Task state management
- Administrative rule execution
- Conservative visit-reason flagging for human review
- Medication/allergy change reporting and escalation
- Missing-data handling
- Audit event generation
- Human review step simulation

### Out of Scope
- Clinical judgment
- Diagnosis
- Autonomous urgency determination
- Autonomous medication/allergy record updates
- Real EHR or insurance API integration in prototype form
- Authentication, HIPAA controls, persistence, or production infrastructure

---

## Core Entities

### Visit

Represents one patient visit moving through intake.

#### Attributes
- `visit_id`: string, immutable
- `patient_id`: string, immutable
- `location_id`: string
- `visit_date`: ISO date string
- `visit_reason_text`: string, optional
- `state`: enum
  - `NOT_STARTED`
  - `IN_PROGRESS`
  - `READY_FOR_REVIEW`
  - `ESCALATED`
  - `CLEARED`
- `tasks`: array of `Task`
- `created_at`: timestamp
- `updated_at`: timestamp

#### State Semantics
- `NOT_STARTED`  
  Visit exists, but intake tasks have not yet been created or processed.

- `IN_PROGRESS`  
  Intake tasks exist and at least one required task is still pending.

- `ESCALATED`  
  At least one required task is escalated or blocked and requires human intervention before the visit can be considered operationally ready.

- `READY_FOR_REVIEW`  
  All required tasks are either:
  - completed, or
  - escalated to the correct human queue with a recorded reason,
  
  and there are no unassigned blockers.  
  This state means the workflow has finished its automated processing and is awaiting human review or acknowledgement.

- `CLEARED`  
  Human review is complete and the visit is operationally ready.  
  In the prototype, this may be simulated through an explicit review action.

#### Allowed State Transitions
- `NOT_STARTED -> IN_PROGRESS`
- `IN_PROGRESS -> ESCALATED`
- `IN_PROGRESS -> READY_FOR_REVIEW`
- `ESCALATED -> READY_FOR_REVIEW`
- `READY_FOR_REVIEW -> CLEARED`

Disallowed:
- direct `NOT_STARTED -> CLEARED`
- direct `IN_PROGRESS -> CLEARED`
- automatic `ESCALATED -> CLEARED` without review step

---

### Task

Represents one intake step.

#### Task Types
- `insurance_verification`
- `prior_auth_check`
- `questionnaire`
- `visit_reason`
- `medication_review`
- `allergy_review`

#### Attributes
- `task_id`: string, immutable
- `visit_id`: string, immutable
- `task_type`: enum
- `status`: enum
  - `pending`
  - `completed`
  - `escalated`
  - `blocked`
- `escalation_target`: enum or null
  - `front_desk`
  - `nurse`
  - `manager`
- `reason_code`: string or null
- `reason_text`: string or null
- `created_at`: timestamp
- `updated_at`: timestamp

#### Task Status Semantics
- `pending`  
  Task exists but has not yet been resolved.

- `completed`  
  Task completed successfully using deterministic logic and sufficient input data.

- `escalated`  
  Task cannot be completed automatically and has been routed to a human queue with an explicit reason.

- `blocked`  
  Task cannot proceed because required source data is missing or unavailable.  
  A blocked task must not be auto-completed.

#### Allowed Task Transitions
- `pending -> completed`
- `pending -> escalated`
- `pending -> blocked`
- `blocked -> escalated`
- `escalated -> completed` only through explicit human review simulation

Disallowed:
- `completed -> pending`
- `completed -> escalated`
- silent status changes without a reason

---

### AuditEvent

Represents a mock audit log entry for prototype visibility.

#### Attributes
- `event_id`: string
- `entity_type`: enum
  - `visit`
  - `task`
- `entity_id`: string
- `event_type`: string
- `previous_state`: string or null
- `new_state`: string or null
- `actor_type`: enum
  - `system`
  - `human`
- `actor_id`: string or null
- `timestamp`: timestamp
- `details`: object or string

#### Required Audit Events
The prototype should log at least:
- task created
- task completed
- task escalated
- task blocked
- visit state changed
- review completed

The prototype does not need production-grade persistence, but it must model audit events explicitly.

---

## Workflow

### 1. Visit Intake Initialization
When a visit enters the intake workflow:
- create all required tasks
- set visit state to `IN_PROGRESS`
- create audit events for task creation and visit state transition

### 2. Deterministic Administrative Checks
The engine evaluates each task according to documented rules.

### 3. Patient Input Handling
The engine processes provided mock inputs for:
- questionnaire completion
- visit reason text
- medication change reported
- allergy change reported

### 4. Escalation Handling
If a task cannot be safely completed, escalate to the correct human queue with:
- escalation target
- reason code
- reason text
- audit event

### 5. Human Review Simulation
If all tasks are either completed or correctly escalated, the visit may enter `READY_FOR_REVIEW`.

A separate simulated human review action may then:
- review escalated tasks
- mark them acknowledged or resolved
- transition visit to `CLEARED`
- write review audit events

---

## Deterministic Decision Rules

### Insurance Verification
Complete when:
- insurance data is present
- insurance status is active

Escalate to `front_desk` when:
- insurance is inactive
- insurance verification fails
- insurance status is unknown

Block when:
- insurance data is missing entirely and no verification result is available

Reason codes:
- `insurance_inactive`
- `insurance_unknown`
- `insurance_data_missing`

---

### Prior Authorization Check
Complete when:
- prior auth is not required, or
- prior auth is required and approved and not expired

Escalate to `front_desk` when:
- prior auth is required and missing
- prior auth is required and expired
- prior auth is required and pending/unknown

Block when:
- required prior auth data cannot be retrieved

Reason codes:
- `prior_auth_missing`
- `prior_auth_expired`
- `prior_auth_unknown`
- `prior_auth_data_missing`

Important:
Not every visit requires prior authorization. Requirement depends on visit/procedure context. This remains an assumption to validate outside the prototype.

---

### Questionnaire
Complete when:
- questionnaire is marked complete

Escalate to `front_desk` when:
- questionnaire is incomplete by the workflow decision point

Block when:
- questionnaire status cannot be determined

Reason codes:
- `questionnaire_incomplete`
- `questionnaire_status_missing`

---

### Visit Reason Handling
The system must not perform clinical interpretation.

The system may only:
- capture the patient’s original text
- apply conservative routing flags
- escalate to human review when configured administrative safety triggers are present

Complete when:
- visit reason is present
- no conservative escalation trigger is detected

Escalate to `nurse` when:
- visit reason is missing or empty
- visit reason contains configured escalation triggers
- input is ambiguous enough that the system cannot safely classify it as routine administrative intake

Block when:
- visit reason input is unavailable

Reason codes:
- `visit_reason_missing`
- `visit_reason_flagged`
- `visit_reason_unavailable`

### Conservative Escalation Triggers
These are not diagnostic categories. They are routing examples only.

Examples:
- chest pain
- shortness of breath
- severe pain
- bleeding
- fainting
- self-harm language
- “urgent”
- “same day”
- “getting worse”

These examples should be treated as configurable prototype inputs, not clinical logic.

---

### Medication Review
Complete when:
- no medication change is reported

Escalate to `nurse` when:
- medication change is reported

Block when:
- medication review input is unavailable

Reason codes:
- `medication_change_reported`
- `medication_input_missing`

The system must not modify the medication record autonomously.

---

### Allergy Review
Complete when:
- no allergy change is reported

Escalate to `nurse` when:
- allergy change is reported

Block when:
- allergy review input is unavailable

Reason codes:
- `allergy_change_reported`
- `allergy_input_missing`

The system must not modify the allergy record autonomously.

---

## Missing External Data Rule

If required external data is missing, unavailable, or cannot be retrieved:
- do not infer the value
- do not silently complete the task
- mark the task as `blocked` or `escalated` based on the defined rule
- create an audit event with the missing-data reason

This rule exists because the prototype must fail safely rather than fabricate completeness.

---

## Escalation Ownership

### Front Desk
Owns:
- insurance issues
- prior authorization issues
- incomplete questionnaires
- administrative follow-up

### Nurse
Owns:
- flagged visit reasons
- medication changes
- allergy changes
- clinically adjacent intake review

### Manager
Owns:
- repeated system failures
- unresolved blocked tasks beyond normal workflow
- operational overrides in future iterations

Note:
The exact nurse vs front-desk boundary is still an assumption and should be validated.

---

## Review Logic

A visit may move to `READY_FOR_REVIEW` only when:
- no tasks remain `pending`
- every required task is either `completed`, `escalated`, or `blocked` with explicit ownership
- no task is left without a reason code
- all state transitions have corresponding audit events

A visit may move to `CLEARED` only when:
- human review simulation has occurred
- any escalated or blocked tasks have been acknowledged or resolved
- a review audit event is written

---

## Guardrails

The system must not:
- diagnose
- triage clinically
- decide treatment urgency
- auto-update medication records
- auto-update allergy records
- infer missing external data
- silently close unresolved tasks
- bypass review for escalated or blocked tasks

---

## Output Requirements for Prototype

The prototype should produce:
- runnable workflow logic
- explicit task and visit states
- mock audit log entries
- one markdown sequence diagram
- sample JSON showing visit state and task state output
- a tiny web page that displays one visit and its tasks, including:
  - task type
  - task status
  - escalation target
  - reason code
  - visit state

---

## Known Assumptions Carried by This Spec

- prior authorization requirement varies by visit type
- nursing review is the correct owner for flagged visit reasons and med/allergy changes
- conservative escalation is preferable to false completion
- the prototype is validating workflow feasibility, not production viability

---

## Risks This Spec Is Pressure-Testing

- **Feasibility risk**: can a coding agent build the workflow engine cleanly?
- **Usability risk**: are states and escalations understandable to human operators?
- **Viability risk**: are boundaries between automation and human review explicit enough?