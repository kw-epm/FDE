# ATX Assessment Summary — Westbridge Family Medicine (Scenario 5)

**Scenario**: Small-Clinic Patient Intake  
**Company**: Westbridge Family Medicine — 6-physician family practice, 180 patients/day  
**Stakeholder**: Dana Velazquez, Practice Manager  
**Date**: April 2026

---

## Executive Summary

This ATX assessment evaluates whether AI agents can automate parts of the patient intake process at Westbridge Family Medicine. The assessment identified **Medication Reconciliation & Allergy-Flag Review** as the primary agentic target with an agentic value score of 22.5 (threshold: ≥15).

**Buildability Score**: 3.5/5 (improved from 2.3/5 after gap resolution)

---

## The Four Work Streams

| Work Stream | Daily Volume | Annual Hours | Agentic Value Score |
|-------------|--------------|-------------|---------------------|
| **Medication Reconciliation** | 180/day | 6,570 hrs | **22.5** (Primary) |
| Pre-Visit Questionnaire | 180/day | 4,380 hrs | 17.5 (Secondary) |
| Insurance Verification | 180/day | 3,942 hrs | 8.0 |
| Prior-Authorisation Check | 25/day | 1,825 hrs | 6.0 |

---

## Deliverable 1: Cognitive Load Map

**What it is**: Decomposition of cognitive work into Jobs to be Done (JtDs), micro-tasks, Cognitive Zones, and Breakpoints.

**Key findings**:
- Decomposed **all 4 work streams** (not just 2)
- **Work Stream 3**: Pre-Visit Questionnaire — 2 JtDs, 9 micro-tasks
- **Work Stream 4**: Medication Reconciliation — 3 JtDs, 14 micro-tasks
- Identified 5 Cognitive Zones: Data Retrieval, Diagnosis, Resolution, Monitoring, Coordination
- Found Breakpoints where control shifts: verification failure, PA denial, visit at risk

**Lived Work vs. Documented**:
- Artefact 5.3: Insurance verification goes stale after 6 months → billing miss
- Artefact 5.1: Wellpath always denies first time → tribal knowledge not in SOP

---

## Deliverable 2: Delegation Suitability Matrix

**What it is**: Scores each task cluster on 7 dimensions and assigns delegation archetypes.

**Scoring dimensions**: Input Structure, Decision Determinism, Tool Coverage, Context Complexity, Exception Frequency, Latency Constraint, Risk/Compliance

**Archetype assignments**:

| Task Cluster | Archetype | Rationale |
|-------------|-----------|------------|
| Automated Verification | Agent-led + Oversight | High volume, structured, 70% pass rate |
| Verification Failure Resolution | Human-led + Agent Support | 30% exception rate requires human |
| PA Submission | Agent-led + Oversight | Clear rules, deterministic |
| PA Tracking | Agent-led + Oversight | Predictable insurer patterns |
| Denial Handling | Human-led + Agent Support | Tribal knowledge required |
| Visit Flagging | Human-led + Agent Support | High risk + weak integration |
| **Questionnaire Processing** | Agent-led + Oversight | Agent processes, human reviews low confidence |
| **Discrepancy Handling** | Human-led + Agent Support | Hard constraint: human escalation path required |
| **Medication Reconciliation** | Agent-led + Oversight | Primary target — agent reconciles, human reviews |
| **Allergy Review** | Agent-led + Oversight | Agent compares, critical escalates |
| **Drug Interaction Check** | Agent-led + Oversight | Agent queries, critical escalates |

**Anti-Pattern avoided**: Not everything is "Fully Agentic"

---

## Deliverable 3: Volume × Value Analysis

**What it is**: Plots work streams on volume vs. non-determinism grid to identify primary agentic target.

**Formula**: Agentic Value Score = Volume (1-5) × Non-Determinism (1-5)

**Primary Target**: Medication Reconciliation (22.5)
- Highest volume + highest reasoning requirement
- Pain point from artefacts: "third time" medication issue (Artefact 5.3)

**Economic justification**:
- Current annual cost: $295,650
- Projected agent cost: $3,942
- Potential savings: 98.7%

---

## Deliverable 4: Agent Purpose Document

**What it is**: Full specification for the MedRecon Agent.

**Agent Name**: MedRecon Agent

**Job to be Done**: Automate review of patient medication histories and allergy alerts during intake, flagging changes, interactions, and discrepancies.

**Key KPIs**:
- Accuracy: >95%
- Coverage: >90% without human escalation
- HITL rate: <10%
- Cost per case: <$0.10

**Autonomy Matrix**:
- Agent decides alone: medication reconciliation, allergy flagging, change detection
- Agent proposes, human approves: critical allergy alerts, potential contraindications
- Human takes over: clinical interpretation, patient disputes

**Escalation triggers**:
- New severe allergy → immediate phone notification
- System unavailable >15 min → manual fallback
- Patient safety near-miss → incident report

---

## Deliverable 5: System/Data Inventory

**What it is**: Maps systems the agent needs to access, data availability, gaps, and risks.

**Systems mapped**:

| System | API | Data | Risk |
|--------|-----|------|------|
| athenahealth | REST | Patient data, visits, chart | High (PHI) |
| DoseSpot | Integrated | Medications, allergies | High (PHI) |
| Availity | REST | Eligibility, PA status | Medium |
| Google Sheets | REST | Internal tracking | Low |
| Legacy Billing | **Unknown** | **Unknown** | **Unknown** |

**Key gap**: Legacy billing system not named in scenario — must elicit from stakeholder

---

## Deliverable 6: Discovery Questions

**What it is**: Questions whose answers would materially change the agent design.

**11 questions across 4 categories**:

1. **System & Data Gaps** (2 questions)
   - Legacy billing system name and data
   - athenahealth ticker integration

2. **Process & Practice** (3 questions)
   - Medication reconciliation refresh patterns
   - Insurer-specific tribal knowledge
   - Non-digital patient populations

3. **Risk & Compliance** (3 questions)
   - HIPAA constraints on AI
   - Clinical judgment boundary
   - Root causes of previous intake misses

4. **Stakeholder Concerns** (3 questions)
   - Dana's personal stake beyond this project
   - Fears about AI-driven approach
   - Previous automation attempts and lessons learned

---

## Deliverable 7: CLAUDE.md (Workflow Discipline)

**What it is**: Workflow discipline documentation.

**Workflow phases**:
1. Discovery & Context (~45 min)
2. Cognitive Load Map (~60 min)
3. Delegation Suitability (~45 min)
4. Volume × Value (~30 min)
5. Agent Purpose Document (~60 min)
6. System/Data Inventory (~30 min)
7. Discovery Questions (~30 min)
8. Closed Build Loop (~60 min)

**Total**: ~6 hours (Gate 2 allows 3 hours — time-boxing required)

---

## Deliverable 8: Buildability Assessment

**What it is**: Gap analysis evaluating whether Claude Code can build from the deliverables.

**Key findings**:
- Buildability improved from **2.3/5 → 3.5/5** after addressing major specification gaps
- High confidence on: API client wrappers, medication logic, alert flagging, audit logging, error handling, system integration
- Remaining gaps: legacy billing system name (low impact), real API credentials (deployment concern), testing plan (medium impact), stakeholder validation (medium impact)

---

## Deliverable 9: ATX Terminology Explained

**What it is**: Educational reference explaining the four core ATX concepts with concrete examples from Westbridge Family Medicine.

**Terms defined**:

| Term | Definition | Example |
|------|------------|---------|
| **Job to be Done (JtD)** | The cognitive contract — the outcome the actor is trying to achieve | "Verify patient insurance eligibility" |
| **Micro-task** | Individual atomic steps to complete a JtD | "Query Availity for eligibility" |
| **Cognitive Zone** | Cluster of similar cognitive activity | "Data Retrieval" — all API-fetching tasks |
| **Breakpoint** | Point where control transfers between actors | System → Human when verification fails |

---

## Hard Constraints

1. **No clinical judgment by the agent** — clinical interpretation stays with human
2. **Clear human escalation path** — any contact with visit reason must preserve escalation
3. **HIPAA compliance** — non-negotiable

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| Primary target = Medication Reconciliation | Highest agentic value (22.5), high volume, pain point |
| Archetype = Agent-led + Human Oversight | High volume structured task + hard constraint |
| Not everything Fully Agentic | Exception-heavy tasks need human judgment |

---

## Files

| # | File | Description |
|---|------|-------------|
| 1 | `deliverables/1-Cognitive-Load-Map.md` | JtDs, micro-tasks, Cognitive Zones, Breakpoints across all 4 work streams |
| 2 | `deliverables/2-Delegation-Suitability-Matrix.md` | 7-dimension scores and delegation archetypes for 11 task clusters |
| 3 | `deliverables/3-Volume-Value-Analysis.md` | Volume × Non-Determinism scoring, priority grid, economic justification |
| 4 | `deliverables/4-Agent-Purpose-Document.md` | Full MedRecon Agent specification (18 sections) |
| 5 | `deliverables/5-System-Data-Inventory.md` | System map, data gaps, risk classification, compliance notes |
| 6 | `deliverables/6-Discovery-Questions.md` | 11 targeted questions tied to design tensions |
| 7 | `deliverables/7-Claude-md.md` | Workflow discipline, iteration trail, key decisions |
| 8 | `deliverables/8-Buildability-Assessment.md` | Gap analysis: what Claude Code can and cannot build |
| 9 | `deliverables/9-ATX-Terminology-Explained.md` | Educational reference for ATX concepts with Westbridge examples |

---

## Buildability Improvements

The deliverables have been updated to address the major gaps identified in the initial buildability assessment:

| Gap | Resolution |
|-----|------------|
| API Authentication | ✅ Added Section 11: OAuth 2.0 / Service Account |
| Rate Limits | ✅ Added estimated limits with handling strategy |
| Drug Interaction Logic | ✅ Added JSON format and severity classification |
| Alert Thresholds | ✅ Added critical criteria and priority levels |
| Error Handling | ✅ Added timeout, retry, circuit breaker, fallback |
| HIPAA Implementation | ✅ Added audit log schema, access control, breach response |
| System Integration | ✅ Added data flow, source of truth, sync frequency |

**Updated Buildability Score**: 3.5/5 (from 2.3/5)