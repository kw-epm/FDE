# D#1 — Problem framing & success metrics

Notes from the Thursday discovery call: `discovery_notes.md`.

## The problem

MedFlex takes too long to put a nurse in front of a hospital. Marcus said it himself: *"if someone submits quicker than I do, the hospital picks them."* In this market, slow means lost.

Marcus gave us roughly 4 hours per fill today, target under 1 hour. Endpoint isn't pinned (offer / submission / confirmed fill — open question 2). He also hedged on the 4h ("never beyond" then "sometimes longer than 4 hours"), so we treat it as a working figure pending Head of Ops.

The 3-hour gap isn't laziness. It's what coordinators have to do:

- Read messy email shift requests and figure out what's actually needed
- Match against tacit knowledge that lives in their heads, not any system
- Multi-offer the same nurse to several hospitals at once, then pull back

The 7% mismatch could be time pressure pushing "close enough" over "right" — but Marcus said the 7% is hospital-flagged, not internally categorised. Could be ranking, eligibility, or compliance data. We don't have the breakdown. Open question for Head of Ops.

## What "10x without 10x-ing" means in numbers

Marcus gave the headline: $14M today → $200M in 24 months.

The math: 8 coordinators × ~120 decisions/day = ~960/day. If shift volume tracks revenue, ~13,500/day at maturity. The same 8 people can't do that. Either hire 100+ more, or the system takes the load. That's the architectural requirement v1 has to prove the design can reach. v1 doesn't have to deliver 13,500/day in 8 weeks.

The 8-week target Marcus asked for is "money back signal." We'll define it in D#7. For now: a measurable drop in time-to-hospital-submission on the slice.

## Success metrics

Marcus said cost-per-shift isn't relevant. Fine — we measure throughput. All on the v1 slice (ICU + 2 hospitals — see D#2). Provisional numbers, recalibrated after week-1 baselines.

| For whom | Metric | Today | Week-8 target |
|---|---|---|---|
| MedFlex (primary) | Time from request to hospital submission | ~4h (Marcus, endpoint unpinned; week-1 request→submission baseline required) | ≤2h nurse-first / ≤1h parallel or hospital-first |
| MedFlex (diagnostic) | Time from request to nurse-offer-sent | not measured | <30 min |
| MedFlex (Decision 1 quality) | First-pick acceptance rate (measured against the agent's pre-override top rank, so it's a Decision 1 quality signal — not the production offer flow during early trust ramp) | new metric | ≥75% |
| Hospitals | Hospital acceptance rate of submissions | not measured; baseline week 1 | no more than 5pp below baseline |
| Nurses | Per-offer nurse response time (median) | new (conditional on Decision 2) | <60 min planned / <15 min urgent (within 90 / 30 min windows) |
| MedFlex / trust | Coordinator override rate | new | <40% by week 4; <25% by week 8 |
| Hospitals + nurses | No-show rate | 12% system-wide; meaningful slice baseline by week 4 | ≤8% on slice (conditional on Decision 2) |
| Guardrail | Mismatch rate | 7% system-wide; slice trend by week 4–6 | hold or improve |

Two caveats on the table:

1. **Baseline endpoint is unpinned.** Marcus's ~4h is the only existing number, but the endpoint isn't clear (offer / submission / confirmed fill — open question 2). Week 1 instrumentation has to establish a request→submission baseline specifically; the improvement claim only stands when we compare like to like.
2. **Decision 2 dependency.** Several targets are conditional on Decision 2 holding (Head of Ops confirming the no-reply finding). If it doesn't hold, the no-show ≤8% target shifts to a confirmation-channel improvement target (Decision 2 alternative path in D#3), and per-offer nurse response time becomes a diagnostic rather than a primary metric. The primary KPI itself doesn't change.

The math works at these targets: with ≥75% first-pick + <30 min to offer + <60 min nurse response, median lands ~90–110 min, well inside the ≤2h target. Below ~60% first-pick the target is at risk; below ~50% the simplified nurse-first median likely misses ≤2h. The 60% trigger below is conservative on purpose.

Why primary KPI ends at hospital submission, not at confirmed fill: hospital response time is downstream of our action. Measuring only up to our action keeps us honest about what we control. Hospital response latency belongs to confirmed-fill analysis; hospital acceptance rate separately tracks whether our submissions are good enough.

## Pause / roll back

Pause = hold autonomy at current level. Roll back = drop one level on the D#3 trust ramp.

| Metric | Pause | Roll back |
|---|---|---|
| Primary KPI | Worse than baseline at week 3 | Worse at week 4 |
| First-pick acceptance | <60% sustained 2 weeks (target at risk) | <50% sustained 2 weeks (Decision 1 quality failing) |
| Hospital accept rate | >10% drop WoW | >20% drop or below baseline 2 weeks |
| Override rate | >50% by week 4 | >70% sustained 2 weeks |
| Per-offer nurse response | Median >70 min planned / >22 min urgent | At/above Decision 2 window |
| No-show | Worse than baseline 4 weeks after explicit-yes | 5+ points worse |
| Mismatch | >7% on slice 2 weeks | >10% |

Numbers tighten or loosen after week 1 baselines come in.

## What we're not measuring (and why)

- Money saved per shift — Marcus said it's not relevant.
- Coordinator headcount — Marcus said he'd grow the team if business grows.
- The 7% mismatch — tracked as a guardrail, not optimised against.

## Open questions for Head of Operations

1. Where do the 4 hours actually go — working or waiting?
2. Is 4h an average or a median? What's the tail? Measured to nurse-offer, submission, or confirmed fill?
3. What do 10-year coordinators do that newcomers don't?
4. When hospitals reject submissions, why? Breakdown of the 7%?
5. Is "no reply = yes" really how it works today? (Decision 2 conditionality)
6. Does shift volume scale with revenue?
7. Email/portal/phone share of incoming requests?
8. What hospital-side and nurse-side records actually exist, and in what form? (D#3 data assumptions)
9. Workflow order — nurse first, hospital first, or parallel? (D#3 state machine, Decision 3 lock trigger, primary KPI target)

All answerable in writing within 48 hours.
