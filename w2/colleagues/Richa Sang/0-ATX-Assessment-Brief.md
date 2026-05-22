# ATX Assessment Brief — Westbridge Family Medicine

**Company**: Westbridge Family Medicine — 6-physician family practice, 180 patients/day  
**Stakeholder**: Dana Velazquez, Practice Manager  
**Assessment type**: Agentic Transformation (ATX) — Patient Intake  
**Date**: April 2026  
**Buildability Score**: 3.5 / 5

---

## What This Assessment Is

Westbridge Family Medicine asked whether AI agents could automate part of their patient intake process. This assessment worked through four intake work streams, scored each for agentic potential, selected the best target, and designed a concrete agent to build.

The result is a fully specified agent — the **MedRecon Agent** — ready for development with clearly defined behaviour, system connections, compliance controls, and human handoff points.

---

## The Problem

The front-desk intake team (4 staff) processes 180 patients per day across four work streams: insurance verification, prior-authorisation (PA) tracking, pre-visit questionnaire review, and medication reconciliation. Three specific failures surfaced in the scenario artefacts:

| Incident | Root Cause |
|----------|------------|
| Patient visit aborted mid-appointment | Pending PA not flagged at check-in |
| Billing miss | Insurance verification had gone stale after 6 months — no refresh for chronic patients |
| Medication error risk | Medication reconciliation missed a change — described as "the third time" by the physician |

These are not one-off mistakes. They reflect structural gaps: manual tracking in Google Sheets, tribal knowledge about insurer patterns not written down, and systems that don't talk to each other at check-in.

---

## The Four Work Streams — Scored

Each work stream was scored on **Volume** (how often it happens) and **Non-Determinism** (how much reasoning it requires beyond simple rules). The formula: `Agentic Value Score = Volume × Non-Determinism`.

| Work Stream | Daily Volume | Annual Hours | Value Score | Priority |
|-------------|-------------|-------------|-------------|----------|
| Medication Reconciliation | 180/day | 6,570 hrs | **22.5** | **Primary target** |
| Pre-Visit Questionnaire | 180/day | 4,380 hrs | 17.5 | Secondary |
| Insurance Verification | 180/day | 3,942 hrs | 8.0 | Rule-based automation |
| Prior-Authorisation Check | 25/day | 1,825 hrs | 6.0 | Deprioritise |

**Why Medication Reconciliation wins**: It has the highest volume *and* requires the most reasoning (comparing pharmacy history, allergy lists, and drug interactions across two systems). It's also the documented pain point. Insurance Verification, while high volume, is mostly deterministic — 70% of cases follow a straight path and need simple automation, not an agent.

---

## The Recommended Agent: MedRecon Agent

### What it does

During patient check-in, before the clinical encounter, the MedRecon Agent:

1. Retrieves the patient's current medication list from DoseSpot (pharmacy system)
2. Retrieves the prior medication list and allergy records from athenahealth (EHR)
3. Compares the two — identifying additions, removals, and dosage changes
4. Checks for drug interactions via DoseSpot's interaction API
5. Flags anything requiring human review
6. Writes a reconciliation summary back to the patient's chart

### What the agent decides on its own vs. what it escalates

| Decision | Who acts |
|----------|----------|
| Medication comparison, change detection, standard documentation | Agent alone |
| Non-critical discrepancies, routine self-reported changes | Agent acts, human notified after |
| Critical allergy alert, potential drug contraindication | Agent proposes — human must approve |
| Clinical interpretation, patient disputes, system outage | Human takes over |

This is an **Agent-led + Human Oversight** pattern. The agent handles the volume; humans handle the edge cases that require clinical judgment.

### Key performance targets

| Metric | Target |
|--------|--------|
| Reconciliation accuracy | > 95% |
| Cases handled without escalation | > 90% |
| Human-in-the-loop rate | < 10% |
| Cost per patient | < $0.10 |
| Critical alert recall | > 95% |

### What it will save

| | Current state | With agent |
|-|--------------|------------|
| Annual staff hours (Med Recon) | 6,570 hrs | ~657 hrs (HITL only) |
| Annual cost | $295,650 | ~$3,942 |
| Saving | — | **$291,708 (98.7%)** |

*Based on $45/hr fully loaded staff cost and 90% automation rate.*

---

## Systems the Agent Needs

| System | What it provides | API | Risk |
|--------|-----------------|-----|------|
| **athenahealth** | Patient demographics, visit history, allergy list, chart write-back | REST (OAuth 2.0) | High — PHI |
| **DoseSpot** | Current medications, pharmacy history, drug interactions | Integrated with athenahealth | High — PHI |
| Availity | Insurance eligibility, PA status | REST (API key) | Medium |
| Google Sheets | PA chase list | REST (service account) | Low |
| Legacy billing | Unknown | Batch file only | Unknown — must elicit |

The agent's core path (medication reconciliation) only needs athenahealth and DoseSpot. Availity and Google Sheets are relevant to insurance and PA flows if those are built later.

---

## Hard Constraints

These are non-negotiable and built into the agent design:

1. **No clinical judgment by the agent** — the agent flags, humans interpret
2. **Clear escalation path always preserved** — no action blocks human review
3. **HIPAA compliance** — full audit logging, encrypted PHI, 7-year retention, breach response protocol

---

## What We Still Need to Find Out

Eleven discovery questions were developed for the stakeholder conversation. The ones with highest design impact:

| Question | Why it matters |
|----------|----------------|
| What is the legacy billing system and what data does it hold? | Determines if it's relevant to the agent at all |
| Why isn't the athenahealth ticker being used at check-in? | May be a training gap (easy fix) or a system gap (integration work) |
| Does medication history go stale like insurance verification does? | Would change how aggressively the agent refreshes data |
| What specific HIPAA or malpractice constraints govern AI use here? | May restrict what data the agent can process or store |
| What were the exact root causes of the three intake misses? | Defines the primary failure modes the agent must prevent |
| What has been tried before, and what failed? | Avoids repeating previous mistakes |

---

## What Still Needs to Be Built

The current specification is detailed enough for a developer to start. Remaining gaps before production:

| Gap | Impact | Resolution |
|-----|--------|------------|
| No testing plan | Medium — no acceptance criteria defined | Add test strategy document |
| Legacy billing system unnamed | Low — likely not relevant to Med Recon | Elicit from Dana |
| Real API credentials | Low — expected at deployment | Provide at build time |
| Stakeholder validation | Medium — design may not match practice reality | Run discovery questions with Dana |

**Buildability score: 3.5/5.** To reach 4.5/5, add a testing plan and complete stakeholder validation.

---

## How the Assessment Was Done

Nine deliverable documents were produced following the ATX methodology:

| # | Document | Purpose |
|---|----------|---------|
| 1 | Cognitive Load Map | Broke down each work stream into the cognitive steps staff actually perform |
| 2 | Delegation Suitability Matrix | Scored each task on 7 dimensions — which parts should agents handle vs. humans |
| 3 | Volume × Value Analysis | Identified the highest-priority agentic target using volume and reasoning load |
| 4 | Agent Purpose Document | Full specification: KPIs, autonomy levels, escalation triggers, API details, HIPAA controls |
| 5 | System/Data Inventory | Mapped all systems, data availability, integration gaps, and compliance requirements |
| 6 | Discovery Questions | 11 questions for the stakeholder that would materially change the design |
| 7 | CLAUDE.md | Workflow log — decisions made, iterations, assumptions, rationale |
| 8 | Buildability Assessment | Honest evaluation of what Claude Code can and cannot build from these specs |
| 9 | ATX Terminology | Plain-English explanation of the framework terms used throughout |

---

## Recommended Next Steps

1. **Run discovery questions with Dana** — confirm legacy billing system, clinical judgment boundary, and previous automation attempts
2. **Add a testing plan** — define unit test scenarios, integration test cases, and UAT acceptance criteria
3. **Start Phase 1 build** — agent core (medication reconciliation, allergy review, drug interaction check) using athenahealth + DoseSpot
4. **Validate with first 100 cases** — review alert precision and false positive rate; calibrate thresholds with Dana's feedback before full rollout
