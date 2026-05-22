# Delegation Suitability Matrix — Westbridge Family Medicine Patient Intake

**Scenario**: Scenario 5 — Small-Clinic Patient Intake  
**Company**: Westbridge Family Medicine  
**Function**: 4-person front-desk intake team  
**Stakeholder**: Dana Velazquez, Practice Manager

---

## Overview

This Delegation Suitability Matrix scores each major task cluster on seven delegation dimensions and assigns delegation archetypes with rationale. The analysis is grounded in the Cognitive Load Map and scenario artefacts.

---

## Scoring Legend

| Dimension | H (High suitability) | M (Medium suitability) | L (Low suitability) |
|-----------|---------------------|----------------------|---------------------|
| Input Structure | Structured, machine-readable | Semi-structured | Unstructured, ambiguous |
| Decision Determinism | Clear rules, predictable | Pattern-based with exceptions | Judgment-dependent, contextual |
| Tool Coverage | APIs available | Buildable with effort | Systems inaccessible |
| Context Complexity | State can be made explicit | Some tacit knowledge required | Requires institutional knowledge |
| Exception Frequency | Rare, predictable | Moderate (10-20%) | Frequent (>20%) |
| Latency Constraint | Batch acceptable | Hours acceptable | Real-time required |
| Risk/Compliance | Reversible, low consequence | Moderate | Irreversible, regulated |

---

## Work Stream 1: Insurance Verification

### Task Cluster 1.1: Automated Insurance Verification

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Input Structure | H | Structured: patient ID, procedure code, insurer code from athenahealth |
| Decision Determinism | H | Clear rules: active/inactive/partial based on Availity response codes |
| Tool Coverage | H | Availity REST API available; athenahealth REST API available |
| Context Complexity | M | Need to understand insurer-specific rules, but can be codified |
| Exception Frequency | M | ~30% fail auto-verify (moderate exception rate) |
| Latency Constraint | H | Batch acceptable; verification can run async |
| Risk/Compliance | M | Billing error consequence, but reversible with refiling |

**Delegation Archetype**: **Agent-led + Human Oversight**

**Rationale**: High-volume structured task with clear rules. Agent can handle the 70% success path autonomously; human reviews the 30% failures. Exception patterns (insurer-specific) can be codified into agent logic.

---

### Task Cluster 1.2: Verification Failure Resolution

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Input Structure | M | Semi-structured: failure code + patient contact info |
| Decision Determinism | M | Pattern-based: expired card vs. wrong info vs. system error |
| Tool Coverage | M | athenahealth available; patient contact requires human |
| Context Complexity | M | Need to understand patient's situation, but patterns exist |
| Exception Frequency | H | 30% of verifications fail; high exception rate |
| Latency Constraint | H | Can be batched; patient callback can be scheduled |
| Risk/Compliance | M | Billing error, but reversible |

**Delegation Archetype**: **Human-led + Agent Support**

**Rationale**: High exception rate (30%) requires human judgment for patient contact. Agent can gather failure information and prepare resolution options, but human must contact patient and make final decision on how to correct.

---

## Work Stream 2: Prior-Authorisation Check

### Task Cluster 2.1: PA Request Submission

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Input Structure | H | Structured: procedure code + insurer + clinical docs |
| Decision Determinism | H | Clear rules: which procedures require PA for which insurers |
| Tool Coverage | H | Availity API for PA submission; athenahealth for clinical docs |
| Context Complexity | M | Need to gather correct clinical documentation |
| Exception Frequency | L | Most submissions succeed; denial is exception |
| Latency Constraint | M | Hours to days; not real-time but can't be too slow |
| Risk/Compliance | M | Delayed procedure impacts patient care, but reversible |

**Delegation Archetype**: **Agent-led + Human Oversight**

**Rationale**: Structured task with clear rules. Agent can submit PA requests autonomously based on procedure+insurer rules. Human reviews denials.

---

### Task Cluster 2.2: PA Status Tracking & Chasing

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Input Structure | H | Structured: PA ID + insurer + submitted date from Availity |
| Decision Determinism | H | Clear patterns: insurer SLAs are predictable (UHC=6d, Humana=6d) |
| Tool Coverage | M | Availity provides status; Google Sheets is manual workaround |
| Context Complexity | M | Need to understand insurer-specific patterns |
| Exception Frequency | M | Moderate: some PAs pending, some denied |
| Latency Constraint | M | Daily check acceptable; SLA tracking |
| Risk/Compliance | M | Delayed PA impacts patient care |

**Delegation Archetype**: **Agent-led + Human Oversight**

**Rationale**: High-volume tracking with predictable patterns. Agent can monitor PA status, apply insurer-specific SLA rules, and flag overdue cases. Human handles chasing calls.

---

### Task Cluster 2.3: PA Denial Handling

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Input Structure | M | Semi-structured: denial reason + patient history |
| Decision Determinism | M | Pattern-based: Wellpath always denies first time (Artefact 5.1) |
| Tool Coverage | M | Denial reason from Availity; resubmit via API |
| Context Complexity | M | Need to understand denial reason and required fix |
| Exception Frequency | H | Insurer-specific patterns (Wellpath denies first) |
| Latency Constraint | H | Can be batched; resubmit cycle is days |
| Risk/Compliance | M | Patient care delayed; reversible with resubmit |

**Delegation Archetype**: **Human-led + Agent Support**

**Rationale**: Denial handling requires understanding of insurer-specific patterns (tribal knowledge). Agent can surface denial reason and prepare resubmit options, but human must make decision on additional documentation.

---

### Task Cluster 2.4: Visit Impact Flagging

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Input Structure | M | Semi-structured: PA status + visit date from two systems |
| Decision Determinism | M | Pattern-based: if PA pending and visit approaching, flag |
| Tool Coverage | L | athenahealth has ticker but not integrated to flagging (Artefact 5.2) |
| Context Complexity | H | Need to understand clinical urgency; tacit knowledge |
| Exception Frequency | M | Moderate: some visits at risk |
| Latency Constraint | H | Real-time not required; flag at check-in is sufficient |
| Risk/Compliance | H | Patient visit aborted (Artefact 5.2); high impact |

**Delegation Archetype**: **Human-led + Agent Support**

**Rationale**: High risk (patient visit aborted) but system integration is weak. Agent can identify at-risk visits by correlating PA status with visit calendar, but human must make flagging decision at check-in due to clinical context.

---

## Work Stream 3: Pre-Visit Questionnaire & Visit-Reason Triage

### Task Cluster 3.1: Questionnaire Processing

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Input Structure | M | Semi-structured: questionnaire responses + free-text |
| Decision Determinism | M | Classification rules exist but free-text requires interpretation |
| Tool Coverage | H | athenahealth patient portal API available |
| Context Complexity | M | Need to understand patient's stated reason, but patterns exist |
| Exception Frequency | M | Moderate: some responses need clarification |
| Latency Constraint | H | Batch acceptable; not real-time |
| Risk/Compliance | M | Misclassification could affect visit priority |

**Delegation Archetype**: **Agent-led + Human Oversight**

**Rationale**: Agent can process questionnaire and classify visit type. Human reviews when NLP confidence is low or when discrepancies exist between stated and scheduled reason.

### Task Cluster 3.2: Visit-Reason Discrepancy Handling

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Input Structure | M | Semi-structured: stated reason vs. scheduled reason |
| Decision Determinism | L | Requires clinical context to determine if discrepancy is significant |
| Tool Coverage | H | athenahealth provides both data points |
| Context Complexity | H | Need to understand clinical implications |
| Exception Frequency | M | Moderate: some discrepancies found |
| Latency Constraint | H | Can be batched |
| Risk/Compliance | H | Wrong classification could affect patient care |

**Delegation Archetype**: **Human-led + Agent Support**

**Rationale**: Hard constraint: "Any contact with stated visit reason must preserve a clear human escalation path." Agent flags discrepancies, human makes final classification.

---

## Work Stream 4: Medication Reconciliation & Allergy-Flag Review

### Task Cluster 4.1: Medication Reconciliation

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Input Structure | H | Structured: medication lists from DoseSpot and athenahealth |
| Decision Determinism | M | Clear rules for comparison but changes require interpretation |
| Tool Coverage | H | DoseSpot API and athenahealth API available |
| Context Complexity | M | Need to understand medication changes, but patterns can be codified |
| Exception Frequency | M | Moderate: some patients have changes |
| Latency Constraint | H | Batch acceptable; reconciliation before visit |
| Risk/Compliance | M | Medication error could affect patient care but reversible |

**Delegation Archetype**: **Agent-led + Human Oversight**

**Rationale**: Agent can reconcile medications autonomously. Human reviews flagged changes. This is the primary agentic target.

### Task Cluster 4.2: Allergy Review

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Input Structure | H | Structured: allergy lists from DoseSpot and athenahealth |
| Decision Determinism | M | Clear rules for comparison but new allergies require interpretation |
| Tool Coverage | H | DoseSpot API and athenahealth API available |
| Context Complexity | M | Need to understand clinical significance of allergy changes |
| Exception Frequency | L | Low: most patients have stable allergy lists |
| Latency Constraint | H | Batch acceptable |
| Risk/Compliance | H | Missed severe allergy could be life-threatening |

**Delegation Archetype**: **Agent-led + Human Oversight**

**Rationale**: Agent can compare allergy lists and flag changes. Critical new allergies escalate immediately. Human reviews all flagged changes.

### Task Cluster 4.3: Drug Interaction Checking

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Input Structure | H | Structured: medication list sent to DoseSpot |
| Decision Determinism | H | Clear severity levels from DoseSpot (critical/moderate/minor) |
| Tool Coverage | H | DoseSpot provides interaction data via API |
| Context Complexity | L | DoseSpot provides severity and recommendation |
| Exception Frequency | L | Low: most patients don't have interactions |
| Latency Constraint | H | Batch acceptable |
| Risk/Compliance | H | Critical interaction missed could be life-threatening |

**Delegation Archetype**: **Agent-led + Human Oversight**

**Rationale**: Agent queries DoseSpot for interactions and classifies severity. Critical interactions escalate immediately. Human reviews all flagged interactions.

---

## Summary Matrix

| Task Cluster | Input | Decision | Tool | Context | Exception | Latency | Risk | Archetype |
|-------------|-------|----------|------|---------|-----------|---------|------|-----------|
| 1.1 Automated Verification | H | H | H | M | M | H | M | Agent-led + Oversight |
| 1.2 Failure Resolution | M | M | M | M | H | H | M | Human-led + Agent Support |
| 2.1 PA Submission | H | H | H | M | L | M | M | Agent-led + Oversight |
| 2.2 PA Tracking | H | H | M | M | M | M | M | Agent-led + Oversight |
| 2.3 Denial Handling | M | M | M | M | H | H | M | Human-led + Agent Support |
| 2.4 Visit Flagging | M | M | L | H | M | H | H | Human-led + Agent Support |
| 3.1 Questionnaire Processing | M | M | H | M | M | H | M | Agent-led + Oversight |
| 3.2 Discrepancy Handling | M | L | H | H | M | H | H | Human-led + Agent Support |
| 4.1 Medication Reconciliation | H | M | H | M | M | H | M | Agent-led + Oversight |
| 4.2 Allergy Review | H | M | H | M | L | H | H | Agent-led + Oversight |
| 4.3 Drug Interaction Check | H | H | H | L | L | H | H | Agent-led + Oversight |

---

## Anti-Pattern Check

**Task Cluster 2.4 (Visit Flagging)** has low Tool Coverage because athenahealth's built-in ticker doesn't integrate with check-in workflow. This is a system gap, not a delegation gap. The agent would need to query two systems and correlate data — feasible but requires integration work.

**Task Cluster 1.2 and 2.3** have high Exception Frequency — these are not suitable for full automation because the patterns require human judgment to interpret (e.g., "Wellpath always denies first time" is tribal knowledge).

---

## Build Sequence Recommendation

Based on the matrix, the recommended build order for the MedRecon Agent:

| Phase | Task Clusters | Why First |
|-------|--------------|-----------|
| **Phase 1 — Core Agent** | 4.1 Medication Reconciliation, 4.2 Allergy Review, 4.3 Drug Interaction Check | Primary target; all H/H/H on Input, Tool, Latency — fastest path to value |
| **Phase 2 — Secondary Automation** | 3.1 Questionnaire Processing, 2.1 PA Submission, 2.2 PA Tracking | High Input Structure, clear Tool Coverage — automatable with moderate effort |
| **Phase 3 — Assisted Flows** | 1.1 Automated Verification | High volume but moderate exception rate — build HITL queue before full deployment |
| **Phase 4 — Human-Augmented** | 1.2 Failure Resolution, 2.3 Denial Handling, 3.2 Discrepancy Handling, 2.4 Visit Flagging | Human-led — build agent support tooling, not autonomous agents |

---

## Assumptions

| Assumption | Confidence | Evidence |
|------------|------------|----------|
| Availity API provides status updates for PA tracking | High | Scenario brief: "Availity (insurance eligibility, separate REST-API tool)" |
| athenahealth ticker exists but isn't used effectively | Medium | Artefact 5.2: "see athenahealth ticker" but front desk didn't flag |
| Insurer SLA patterns are consistent enough to codify | Medium | Artefact 5.1 shows patterns but limited data points |
| No clinical judgment allowed per hard constraint | High | Scenario brief hard constraint: "No clinical judgment by the agent" |

---

## Notes on Delegation Boundary Drift

If every task were marked "Fully Agentic," we would have missed:

1. **Exception handling** (1.2, 2.3): 30% failure rate and insurer-specific patterns require human interpretation
2. **Visit flagging** (2.4): High risk + weak system integration = human must verify
3. **Patient contact** (1.2): Requires human for sensitive communication about insurance issues

The matrix correctly assigns **Agent-led + Human Oversight** for high-volume structured tasks (1.1, 2.1, 2.2) and **Human-led + Agent Support** for exception-heavy or high-risk tasks (1.2, 2.3, 2.4).