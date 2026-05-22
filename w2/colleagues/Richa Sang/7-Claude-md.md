# CLAUDE.md — Westbridge Family Medicine ATX Assessment

**Project**: ATX (Agentic Transformation) Assessment for Westbridge Family Medicine  
**Scenario**: Scenario 5 — Small-Clinic Patient Intake  
**Date**: April 2026  
**Author**: FDE (Functional Design Engineer)

---

## Project Overview

This document captures the workflow discipline for the ATX assessment of Westbridge Family Medicine's patient intake process. The assessment follows the ATX methodology to decompose cognitive work, score delegation suitability, and produce an agent design.

---

## Workflow Summary

### Phase 1: Discovery & Context Building

| Activity | Input | Output | Tool |
|----------|-------|--------|------|
| Read scenario brief | enriched_scenarios.md | Company, function, work streams, tooling, stakeholder | read_file |
| Read ATX reference docs | atx-concepts.md, atx-assessment.md, atx-scoring.md, atx-agent-mapping.md | Framework understanding | read_file |
| Identify artefacts | enriched_scenarios.md | 3 artefacts per scenario | grep_search |

**Time Budget**: ~45 minutes

---

### Phase 2: Cognitive Load Mapping

| Activity | Input | Output | Tool |
|----------|-------|--------|------|
| Decompose work streams | Scenario brief, artefacts | Jobs to be Done (JtDs) | Manual analysis |
| Identify micro-tasks | JtDs | Task inventory | Table format |
| Map Cognitive Zones | Micro-tasks | Zone clusters | Manual analysis |
| Identify Breakpoints | Process flow | Control handoff points | Manual analysis |

**Time Budget**: ~60 minutes

**Key Insight**: Artefact 5.3 shows verification refresh issue — lived work differs from documented process

---

### Phase 3: Delegation Suitability Scoring

| Activity | Input | Output | Tool |
|----------|-------|--------|------|
| Score each task cluster | Cognitive Load Map | 7-dimension scores (H/M/L) | Manual analysis |
| Assign archetypes | Dimension scores | Delegation archetype per task | Matrix format |
| Check anti-patterns | Matrix | "Everything is fully agentic" detection | Manual review |

**Time Budget**: ~45 minutes

**Key Anti-Pattern Caught**: 
- Task Cluster 2.4 (Visit Flagging) has low Tool Coverage — system integration gap
- High Exception Frequency tasks (1.2, 2.3) require human judgment, not full automation

---

### Phase 4: Volume × Value Analysis

| Activity | Input | Output | Tool |
|----------|-------|--------|------|
| Calculate volumes | Scenario brief | Annual cases per work stream | Manual calculation |
| Score non-determinism | Cognitive Load Map | 1-5 scale per work stream | Manual scoring |
| Calculate agentic value | Volume × Non-Determinism | Score 1-25 | Formula |
| Plot on grid | Scores | 2x2 priority grid | Manual plotting |

**Time Budget**: ~30 minutes

**Primary Target**: Medication Reconciliation (Score 22.5)
**Secondary Target**: Pre-Visit Questionnaire (Score 17.5)

---

### Phase 5: Agent Purpose Document

| Activity | Input | Output | Tool |
|----------|-------|--------|------|
| Define purpose | Volume × Value analysis | Agent name, JtD | Manual |
| Set KPIs | Business context | Targets and ceilings | Manual |
| Build autonomy matrix | Delegation matrix | Decision authority levels | Table format |
| Define escalation triggers | Risk analysis | Conditions and actions | List format |
| Document failure modes | Risk analysis | Failure scenarios and recovery | Table format |

**Time Budget**: ~60 minutes

---

### Phase 6: System/Data Inventory

| Activity | Input | Output | Tool |
|----------|-------|--------|------|
| Map systems | Scenario brief | System list with API availability | Table format |
| Identify data gaps | Artefacts | Missing data areas | List format |
| Classify risks | Data types | Risk classification per system | Table format |
| Address legacy system | Scenario mention | Discovery questions | List format |

**Time Budget**: ~30 minutes

**Key Gap Identified**: Legacy billing system not named — must elicit

---

### Phase 7: Discovery Questions

| Activity | Input | Output | Tool |
|----------|-------|--------|------|
| Generate questions | Artefacts, gaps | Questions tied to tensions | Manual |
| Categorise | Question purpose | By design impact | Table format |
| Validate | Generic question check | Remove generic questions | Manual review |

**Time Budget**: ~30 minutes

---

### Phase 8: Closed Build Loop

| Activity | Input | Output | Tool |
|----------|-------|--------|------|
| Feed to Claude Code | Agent Purpose Document | Build output | Claude Code |
| Diagnose gaps | Build output | Specification, ambiguity, delegation gaps | Analysis |
| Revise | Gap diagnosis | Updated Agent Purpose Document | edit |

**Time Budget**: ~60 minutes (iterative)

---

## Total Time Budget

| Phase | Time |
|-------|------|
| Discovery & Context | 45 min |
| Cognitive Load Map | 60 min |
| Delegation Suitability | 45 min |
| Volume × Value | 30 min |
| Agent Purpose Document | 60 min |
| System/Data Inventory | 30 min |
| Discovery Questions | 30 min |
| Closed Build Loop | 60 min |
| **Total** | **~6 hours** |

*Note: Gate 2 allows 3 hours — this is the ideal workflow; time-boxing required*

---

## AI Usage Patterns

### Where AI Accelerated the Work

1. **Context summarisation**: Claude Code helped summarise the scenario brief into digestible chunks
2. **Template generation**: Used Claude Code to generate table formats for deliverables
3. **Elicitation proxy**: Used Claude Code to role-play as Dana Velazquez for practice questions

### Where AI Couldn't Help

1. **Artefact interpretation**: Required human judgment to identify lived work vs. documented process
2. **Delegation archetype assignment**: Required FDE expertise to justify, not just score
3. **Stakeholder nuance**: AI couldn't capture Dana's personal stake without direct elicitation

---

## Iteration Trail

### Iteration 1: Initial Cognitive Load Map

- Decomposed Insurance Verification and Prior-Authorisation work streams
- Identified 2 JtDs and 9 micro-tasks for Insurance Verification
- Identified 3 JtDs and 13 micro-tasks for Prior-Authorisation
- **Gap**: Didn't include Pre-Visit Questionnaire or Medication Reconciliation

### Iteration 2: Delegation Matrix

- Scored all task clusters on 7 dimensions
- Assigned archetypes with rationale
- **Correction**: Initially considered "Fully Agentic" for automated verification — corrected to "Agent-led + Human Oversight" due to 30% exception rate

### Iteration 3: Volume × Value

- Calculated agentic value scores
- **Finding**: Medication Reconciliation (22.5) > Pre-Visit (17.5) > Insurance (8.0) > Prior-Auth (6.0)
- **Decision**: Primary target is Medication Reconciliation

### Iteration 4: Agent Purpose Document

- Created MedRecon Agent with full specification
- Defined autonomy matrix with 4 levels
- Defined escalation triggers
- **Refinement**: Added "No clinical judgment" boundary explicitly

### Iteration 5: System/Data Inventory

- Mapped 5 systems
- Identified legacy billing system gap
- **Discovery Question**: Must ask Dana for legacy system name

### Iteration 6: Discovery Questions

- Generated 11 questions across 4 categories
- Added Question 4.3: Previous automation attempts (not in brief — must elicit)
- **Validation**: All questions tied to specific tensions in artefacts or brief
- **Removed**: Generic questions like "walk me through your process"

### Iteration 7: Buildability Assessment & Gap Resolution

- Fed Agent Purpose Document to Claude Code closed build loop
- **Finding**: Initial buildability score 2.3/5 — major gaps in API auth, error handling, HIPAA implementation
- **Resolutions added**: Sections 11–16 of Agent Purpose Document (OAuth, rate limits, drug interaction logic, alert thresholds, error handling, HIPAA, system integration)
- **Updated score**: 3.5/5
- **Remaining gaps**: Legacy billing system name, real API credentials, testing plan, stakeholder validation

---

## Key Decisions & Rationale

### Decision 1: Primary Target = Medication Reconciliation

**Rationale**: 
- Highest agentic value score (22.5)
- High volume (180/day) justifies investment
- High non-determinism (4.5) — requires reasoning beyond rules
- Pain point from Artefact 5.3

### Decision 2: Delegation Archetype = Agent-led + Human Oversight

**Rationale**:
- High volume structured task
- Clear rules for 70% of cases
- Human reviews 30% failures and all critical alerts
- Hard constraint: "No clinical judgment" requires human for clinical interpretation

### Decision 3: Not Everything is Fully Agentic

**Anti-Pattern Avoided**:
- Insurance Verification failure resolution → Human-led + Agent Support
- PA Denial Handling → Human-led + Agent Support
- Visit Flagging → Human-led + Agent Support

---

## Assumptions Log

| Assumption | Confidence | Evidence |
|------------|------------|----------|
| Availity API is reliable for eligibility queries | High | Scenario brief: "REST-API tool" |
| ~30% of verifications fail auto-verify | Medium | Scenario brief: "~30% that fail auto-verify" |
| athenahealth ticker exists but isn't used | Medium | Artefact 5.2 |
| Legacy billing system exists but not named | High | Scenario brief mentions it |
| Fully loaded hourly cost = $45/hr | Medium | Industry standard |

---

## Files Produced

| File | Description |
|------|-------------|
| `1-Cognitive-Load-Map.md` | JtDs, micro-tasks, Cognitive Zones, Breakpoints across all 4 work streams |
| `2-Delegation-Suitability-Matrix.md` | 7-dimension scores, archetypes, rationale for 11 task clusters |
| `3-Volume-Value-Analysis.md` | Volume × Non-Determinism scores, priority grid, economic justification |
| `4-Agent-Purpose-Document.md` | Full agent specification (18 sections including API auth, HIPAA, error handling) |
| `5-System-Data-Inventory.md` | System map, data gaps, risk classification, compliance notes |
| `6-Discovery-Questions.md` | 11 questions tied to design tensions (4 categories) |
| `7-Claude-md.md` | This file — workflow discipline, iteration trail, key decisions |
| `8-Buildability-Assessment.md` | Gap analysis: what Claude Code can and cannot build |
| `9-ATX-Terminology-Explained.md` | Educational reference for ATX concepts with Westbridge examples |

---

## Next Steps

1. **Run closed build loop**: Feed Agent Purpose Document to Claude Code
2. **Validate with artefacts**: Ensure lived work is captured, not just documented
3. **Elicit from stakeholder**: Use Discovery Questions in coach role-play
4. **Refine**: Incorporate feedback from build loop and elicitation