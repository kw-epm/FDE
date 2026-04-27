# Current State Process — FNOL Claims Processing

## Purpose

This document maps the as-is process at the insurance company's claims operations centre before any agentic solution is introduced. It grounds the delegation analysis and agent spec in what the work actually is.

Sources: scenario description + insurance industry inference. All inferred details are flagged `[Inferred]`. Confirmed details are flagged `[Stated]`.

---

## Operations Overview

| Attribute | Value | Source |
|---|---|---|
| Daily FNOL volume | ~300 reports/day | [Stated] |
| Annual FNOL volume | ~75,000 reports/year | [Calculated: 300 × 250 working days] |
| Processing team | 12 specialists | [Stated] |
| Average handling time | 22 min/claim | [Stated] |
| Routing error rate | 18% | [Stated] |
| SLA breach rate | 31% | [Stated] |
| SLA target | 2 hours from receipt to acknowledgment | [Stated] |
| Inbound channels | Email, phone transcript, web form | [Stated] |
| Systems | Modern CRM (APIs), legacy policy admin (SOAP), DMS | [Stated] |
| AI infrastructure | None | [Stated] |

---

## Volume Math

**Daily workload:**
- 300 claims/day ÷ 12 specialists = 25 claims per specialist per day [Calculated]
- 25 claims × 22 min = 550 min of active work per specialist per day [Calculated]
- At an 8-hour shift (480 min): team has capacity for ~262 claims/day [Calculated]
- Current volume (300/day) exceeds 8-hour capacity by ~14.5% [Calculated]
- This explains both the overtime and the SLA breach rate: the queue builds faster than it drains

**SLA breach math:**
- 31% × 300 = ~93 claims/day miss the 2-hour window [Calculated]
- ~23,250 SLA breaches/year [Calculated]

**Routing error math:**
- 18% × 300 = ~54 mis-routed claims/day [Calculated]
- ~13,500 mis-routed claims/year [Calculated]

**Channel distribution (estimated):** [Inferred]
- Email: ~40% (~120/day)
- Web form: ~35% (~105/day)
- Phone transcript: ~25% (~75/day)

**Claim type distribution (estimated):** [Inferred]
- Auto (collision + theft): ~40%
- Property (damage + theft): ~35%
- Liability: ~15%
- Bodily injury and other: ~10%

---

## Step-by-Step Current Process (per claim)

All steps performed by a single specialist without any decision-support tooling. [Inferred except where noted]

| Step | Description | Estimated Time |
|---|---|---|
| 1. Queue pickup | Specialist selects next claim from shared inbox/queue | 1–3 min (includes queue wait during busy periods) |
| 2. Read & orient | Read full unstructured text; identify claim type and urgency | 3–5 min |
| 3. Policy lookup | Search legacy policy admin system by policy number (manual SOAP UI or internal portal) | 2–4 min |
| 4. Coverage check | Verify claim type against covered perils; check policy status, effective dates | 2–4 min |
| 5. Severity assessment | Assess severity based on experience; consult routing guidelines if uncertain | 2–3 min |
| 6. Adjuster selection | Check adjuster roster (CRM), match by claim type and geography, check availability | 3–5 min |
| 7. Acknowledgment | Draft and send email to claimant (or create callback task if phone-only) | 2–3 min |
| 8. CRM logging | Enter claim details, assigned adjuster, and processing notes into CRM | 2–3 min |
| **Total** | | **17–30 min, avg 22 min** |

---

## Known Failure Points

### Routing errors (18%)
Primary causes [Inferred]:
- Claim type mis-identification from ambiguous unstructured text (e.g., "my car was damaged" — collision or theft?)
- Adjuster specialization mismatch (liability specialist assigned to auto collision)
- Geography mismatch (adjuster covering wrong region for incident location)
- Adjuster queue overload not checked at time of assignment

### SLA breaches (31%)
Primary causes [Inferred]:
- Queue backup during peak intake periods (morning); claims arriving faster than specialists can process
- Complex claims requiring additional research (e.g., policy verification takes longer due to legacy system slowness)
- Email acknowledgments deprioritised when specialist is occupied with routing decisions
- No automated SLA alerting — specialists do not always know when a claim is approaching the 2-hour window

### Consistency gaps [Inferred]
- Severity assessment relies entirely on specialist experience — no rubric enforced
- Routing table is a shared document, updated informally
- No check that the same claim is not picked up by two specialists simultaneously

---

## What the Current Team is Good At

- Complex coverage disputes: experienced specialists can interpret exclusion clauses and identify edge cases
- Relationship continuity: when a claimant calls back, a specialist can pull history quickly
- Bodily injury escalation: team generally recognises these and prioritises them [Inferred]

These are the areas where human judgment remains irreplaceable and where the agentic solution should not attempt to replace specialist decision-making.
