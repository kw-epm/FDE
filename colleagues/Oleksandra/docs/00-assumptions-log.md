# Assumption Log

## A1 — The primary problem is workflow reliability

- Assumption  
The main issue is inconsistent completion of intake tasks rather than purely staff capacity.

- Hypothesis  
If intake tasks are explicitly tracked and enforced, visit-time intake defects will decrease.

- Validation Approach  
Clarify current workflow:
- how intake completeness is verified
- whether missed steps are due to time pressure or lack of tracking

- Confidence  
High

---

## A2 — A significant portion of intake work is repeatable

- Assumption  
Insurance checks, prior auth checks, and questionnaire follow-ups are largely deterministic.

- Hypothesis  
Automating these steps reduces manual effort without reducing control.

- Validation Approach  
Identify:
- which steps follow fixed rules
- which require judgment

- Confidence  
Medium

---

## A3 — Prior auth and medication issues are high-impact failures

- Assumption  
The most common issues mentioned are also the most costly.

- Hypothesis  
Improving these areas first will yield measurable benefit.

- Validation Approach  
Validate:
- which intake failures create the most disruption
- frequency vs impact

- Confidence  
Medium

---

## A4 — Visit reason handling must remain conservative

- Assumption  
The system can create value without interpreting symptoms.

- Hypothesis  
Capture + escalation is sufficient without performing triage.

- Validation Approach  
Confirm:
- acceptable level of automation in patient interaction
- tolerance for false positives in escalation

- Evidence from Build Loop  
The prototype successfully implemented routing triggers without performing clinical interpretation.  
However, trigger definitions remain arbitrary and not validated against real workflows.

- Confidence  
Medium (reduced from High due to unvalidated trigger definitions)

---
## A5 — Escalation queues are operationally viable

- Assumption  
Staff roles can be mapped to structured queues.

- Hypothesis  
Clear ownership enables agent-human collaboration.

- Validation Approach  
Clarify:
- who handles unresolved intake issues today
- how handoffs are performed

- Evidence from Build Loop  
Prototype successfully routes:
- administrative issues → front desk
- clinical-adjacent issues → nurse  

However, this mapping is assumed and not validated with real clinic operations.

- Confidence  
Low
---

## A6 — Automation will reduce downstream disruption

- Assumption  
Earlier detection of issues reduces physician interruption.

- Hypothesis  
Moving issue detection before the visit improves flow and efficiency.

- Validation Approach  
Compare:
- current detection timing
- downstream impact of late discovery

- Confidence  
Medium

## A7 — Prior authorization requirement varies by visit type

- Assumption  
Not all visits require prior authorization; requirement depends on procedure or visit type.

- Hypothesis  
The system must correctly distinguish between:
- visits where prior auth is required
- visits where it is not

Incorrect handling would create false escalations or missed risks.

- Validation Approach  
Clarify:
- which visit types require prior auth
- how this is currently determined (EHR? manual?)

- Confidence  
Medium

## A8 — Clinical escalation requires nursing involvement

- Assumption  
Cases involving symptoms, medication changes, or clinical ambiguity should be escalated to nursing staff rather than front desk.

- Hypothesis  
Separating administrative and clinical escalation improves safety and aligns with typical clinic workflows.

- Validation Approach  
Clarify:
- who currently handles symptom-related intake issues
- whether front desk performs any triage
- acceptable boundaries for non-clinical staff

- Confidence  
Low-Medium

## A9 — BLOCKED vs ESCALATED distinction reflects real-world workflow differences

- Assumption  
System failures (missing data) should be treated differently from business-rule escalations.

- Hypothesis  
Separating BLOCKED from ESCALATED improves clarity and operational handling.

- Validation Approach  
Clarify:
- how clinics currently handle missing system data vs business issues
- whether different ownership or urgency applies

- Evidence from Build Loop  
Prototype successfully distinguishes:
- BLOCKED → system/data issue
- ESCALATED → business or clinical routing issue  

However, downstream handling of BLOCKED cases remains undefined.

- Confidence  
Medium
## A10 — Human review is required before a visit is considered operationally ready

- Assumption  
Even when all automated checks are complete, a human review step is required before final clearance.

- Hypothesis  
Separating READY_FOR_REVIEW and CLEARED improves safety and control.

- Validation Approach  
Clarify:
- whether clinics require explicit approval before visit readiness
- who performs this review

- Evidence from Build Loop  
Prototype introduced:
- READY_FOR_REVIEW state
- explicit human review step  

This improved workflow clarity and prevented automatic finalization.

- Confidence  
Medium-High

## A11 — Workflow must be clearly understandable to end users

- Assumption  
Users need clear visibility of:
- current state
- previous steps
- next actions

- Hypothesis  
Without explicit workflow visualization, usability and adoption will suffer.

- Validation Approach  
Evaluate:
- whether users can understand process from UI
- whether state progression is clear

- Evidence from Build Loop  
Prototype UI shows current state and tasks but does not clearly communicate:
- workflow progression
- position in process  

This indicates a usability gap.

- Confidence  
High

## A12 — Audit visibility is required, but does not equal compliance

- Assumption  
Users and stakeholders require visibility into system actions.

- Hypothesis  
Basic audit event logging improves trust and traceability.

- Validation Approach  
Clarify:
- required audit depth
- regulatory expectations

- Evidence from Build Loop  
Prototype includes audit event stream showing:
- task transitions
- state changes
- review actions  

However, this is not compliance-grade logging.

- Confidence  
High

---

## A13 — Intake error rates align with industry benchmarks

- Assumption  
The clinic's current intake error rate is consistent with industry ranges for manual administrative workflows.

- Hypothesis  
Baseline defect rate is approximately 8–10% of visits.

- Validation Approach  
- Compare with clinic data (audit sample of visits)
- Validate frequency of prior auth / medication issues

- Evidence from Build Loop  
Used as baseline to define success metrics and targets.

- Confidence  
Medium