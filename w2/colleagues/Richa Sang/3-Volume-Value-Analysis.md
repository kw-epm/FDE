# Volume × Value Analysis — Westbridge Family Medicine Patient Intake

**Scenario**: Scenario 5 — Small-Clinic Patient Intake  
**Company**: Westbridge Family Medicine  
**Function**: 4-person front-desk intake team  
**Stakeholder**: Dana Velazquez, Practice Manager

---

## Overview

This Volume × Value Analysis plots the four work streams on a volume vs. non-determinism grid to identify the primary agentic target. The analysis uses volumes and handling times from the scenario brief.

---

## Work Stream Data

| Work Stream | Daily Volume | Annual Volume | Time per Case (min) | Total Annual Hours | Primary Activity |
|-------------|--------------|---------------|--------------------|--------------------|-------------------|
| Insurance Verification | 180/day | ~65,700/yr | ~5 min (30% fail) + ~3 min (70% pass) = ~3.6 avg | ~3,942 hrs | Verification + failure resolution |
| Prior-Authorisation Check | 25/day | ~9,125/yr | ~12 min | ~1,825 hrs | PA submission + tracking + chasing |
| Pre-Visit Questionnaire & Triage | 180/day | ~65,700/yr | ~4 min | ~4,380 hrs | Questionnaire review + classification |
| Medication Reconciliation & Allergy | 180/day | ~65,700/yr | ~6 min | ~6,570 hrs | Pharmacy history + allergy review |

---

## Non-Determinism Scoring

| Score | Description | Applied to Work Streams |
|-------|-------------|------------------------|
| 1 | Fully deterministic: pure rules/logic | Insurance Verification (70% pass) |
| 2 | Mostly deterministic: small reasoning component | Prior-Authorisation (submission) |
| 3 | Mixed: core path rule-based, exceptions require reasoning | Prior-Authorisation (chasing, denial) |
| 4 | Significant reasoning: contextual adaptation required | Pre-Visit Triage |
| 5 | High reasoning: synthesis of multiple sources, policy interpretation | Medication Reconciliation |

### Scoring Rationale

**Insurance Verification**: 
- 70% auto-verify = deterministic (Score 1)
- 30% failure = requires diagnosis (Score 3)
- Weighted average: ~1.6

**Prior-Authorisation Check**:
- Submission = deterministic (Score 1)
- Tracking = pattern-based (Score 2)
- Denial handling = requires interpretation (Score 3)
- Weighted average: ~2.0

**Pre-Visit Questionnaire & Triage**:
- Routine vs. urgent vs. same-day classification requires context (Score 3)
- Some judgment on urgency (Score 4)
- Weighted average: ~3.5

**Medication Reconciliation**:
- Requires synthesis of pharmacy history + allergy alerts + change flagging (Score 4)
- Drug interaction checking requires clinical context (Score 5)
- Weighted average: ~4.5

---

## Agentic Value Score Calculation

**Formula**: Agentic Value Score = Volume × Non-Determinism

| Work Stream | Volume Score (1-5) | Non-Determinism Score (1-5) | Agentic Value Score | Priority Zone |
|-------------|-------------------|----------------------------|---------------------|---------------|
| Insurance Verification | 5 | 1.6 | 8.0 | Top-left (high vol, low non-determinism) |
| Prior-Authorisation Check | 3 | 2.0 | 6.0 | Bottom-left (moderate vol, low non-determinism) |
| Pre-Visit Questionnaire | 5 | 3.5 | 17.5 | Top-right (high vol, high non-determinism) |
| Medication Reconciliation | 5 | 4.5 | 22.5 | **Top-right (primary target)** |

---

## Volume × Value Grid

```
High Non-Determinism (5)
        │
        │   Prior-Auth    │   Medication
        │   (6.0)         │   Reconciliation
        │                 │   (22.5) ★ PRIMARY
        │─────────────────┼─────────────────────
        │   Insurance     │   Pre-Visit
        │   Verification  │   Questionnaire
        │   (8.0)         │   (17.5) ◎ SECONDARY
        │                 │
Low Non-Determinism (1)
Low Volume (1) ──────────┴──────────── High Volume (5)
```

**How to read**: Top-right quadrant = high volume + high reasoning requirement = best agentic targets. Bottom-left = low volume + deterministic = rule-based automation or deprioritise.

---

## Primary Agentic Target: Medication Reconciliation & Allergy-Flag Review

### Why This Wins

| Factor | Analysis |
|--------|----------|
| **Highest Agentic Value** | Score 22.5 — significantly above threshold (≥15) |
| **High Volume** | 180 patients/day, 65,700/year — justifies investment |
| **High Non-Determinism** | Requires synthesis of pharmacy history, allergy alerts, change flagging — beyond simple rules |
| **Pain Point** | Artefact 5.3 shows medication reconciliation misses: "Patient verification refresh window > 6 months caused billing miss. We don't refresh for chronic patients on stable insurance — Dana said this is the third time." |

### Why Not Others

**Insurance Verification** (Score 8.0):
- High volume but low non-determinism (mostly deterministic)
- 70% auto-pass; only 30% requires human judgment
- Rule-based automation more appropriate than agent

**Prior-Authorisation Check** (Score 6.0):
- Moderate volume, low non-determinism
- Submission is deterministic; chasing requires human but is low-volume
- Score below threshold — not strong agentic candidate

**Pre-Visit Questionnaire** (Score 17.5):
- High volume, moderate non-determinism
- Close to threshold but secondary to Medication Reconciliation
- Hard constraint: "Any contact with stated visit reason must preserve clear human escalation path" — limits agentic potential

---

## Economic Justification

### Baseline Cost (Current State)

| Work Stream | Annual Hours | Fully Loaded Hourly Cost | Annual Cost |
|-------------|--------------|------------------------|-------------|
| Insurance Verification | 3,942 hrs | $45/hr | $177,390 |
| Prior-Authorisation Check | 1,825 hrs | $45/hr | $82,125 |
| Pre-Visit Questionnaire | 4,380 hrs | $45/hr | $197,100 |
| Medication Reconciliation | 6,570 hrs | $45/hr | $295,650 |
| **Total** | **16,717 hrs** | | **$752,265** |

### Agent Cost Model (Medication Reconciliation only)

| Component | Estimate |
|-----------|----------|
| Token cost per case | $0.02 (avg 500 tokens × $0.04/1K) |
| Tool call cost | $0.01 (2 API calls) |
| HITL cost | $0.03 (10% require human review) |
| **Cost per case** | **$0.06** |
| **Annual cost (65,700 cases)** | **$3,942** |

### Projected Savings

| Metric | Value |
|--------|-------|
| Current annual cost (Med Recon) | $295,650 |
| Agent annual cost | $3,942 |
| Savings | $291,708 |
| Reduction | 98.7% |

*Note: This assumes 90% automation with 10% human review. Actual savings depend on HITL rate and accuracy.*

---

## Assumptions

| Assumption | Confidence | Evidence |
|------------|------------|----------|
| Fully loaded hourly cost = $45/hr | Medium | Industry standard for administrative healthcare staff |
| Agent can handle 90% of medication reconciliation cases | Low | Requires validation; hard constraint limits clinical judgment |
| HITL rate = 10% | Low | Estimate based on exception frequency in similar domains |
| Token cost = $0.04/1K tokens | High | Current market rates for LLM API calls |

---

## Recommendation

**Primary Agentic Target**: Medication Reconciliation & Allergy-Flag Review

**Secondary Target**: Pre-Visit Questionnaire & Visit-Reason Triage (Score 17.5, close to threshold)

**Do Not Agenticize**: Insurance Verification and Prior-Authorisation Check — these are better suited for rule-based automation given low non-determinism scores.