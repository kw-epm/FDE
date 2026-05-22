# D#1 — Problem framing & success metrics

Notes from the Thursday discovery call: `discovery_notes.md`.

## The stated request vs. the actual problem

**Marcus framed the engagement as:** *"10x the business without 10x-ing the coordinators."* In 8 weeks.

**The real diagnosis:** the binding constraint isn't coordinator capacity — it's **response latency in a winner-takes-first market.** Hospitals submit shift requests to multiple agencies; the fastest qualified offer wins the placement. At 4 hours average time-to-offer against a sub-1-hour competitive bar, MedFlex loses placements before its nurse is even submitted. Revenue grows when speed wins; speed wins when the matching loop stops being human-bounded. The "10x without 10x-ing" framing is correct in direction but incomplete in diagnosis — the architectural ask isn't "more decisions per coordinator," it's "decisions made fast enough to win, at a volume the team can't reach manually."

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

Marcus said cost-per-shift wasn't relevant at discovery; his CFO has since asked for a year-1 dollar number for the board deck (see Year-1 section below). We measure both: operational metrics (throughput) for the architecture, and a back-of-envelope dollar figure for the CFO. All metrics on the v1 slice (slice locked Monday EOD after Head of Ops — see D#2). Provisional numbers, recalibrated after week-1 baselines from the live system.

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

## Year-1 contribution impact, on the slice (illustrative, not committed)

The Thursday framing said cost-per-shift wasn't where the value sits. Marcus's CFO disagreed and asked for a defensible year-1 number for the board deck. What follows is *illustrative contribution impact*, not committed revenue. **The math depends on what "$14M revenue" actually represents in MedFlex's accounts** — net agency revenue (the cut after paying the nurse) vs. gross billings (what hospitals pay before MedFlex pays the nurse). CFO can confirm which figure is meant; that single clarification shifts the math materially.

**Working assumptions (placeholders, to be replaced Monday):**

- **MedFlex's net revenue per filled shift:** ~$300 (industry norm — agency typically keeps 15–25% of a ~$1,500–$2,000 hospital bill rate; using mid-range $300 as the agency's net per fill). If $14M is gross billings instead, per-shift revenue is closer to $1,800 and volume is roughly 6× lower than the back-solve below.
- **Total fills/day at $14M net revenue:** $14M ÷ $300 ÷ 250 working days ≈ **~184 fills/day** *(if $14M = net agency revenue; ~30 fills/day if gross billings)*.
- **Placeholder slice volume:** ~10–20 fills/day across 2 hospitals — illustrative only. The slice is ICU at 2 specific hospitals, not ICU across all MedFlex; actual slice volume is a slice-selection question for Monday's Head of Ops conversation.

**Three improvement levers, illustrative math at 15 fills/day on the slice:**

| Lever | Math | Year-1 contribution on slice |
|---|---|---|
| Speed recovery (shifts lost to faster competitors today) | 15 × 30% lost × 50% recoverable × $300 × 250 | ~$170K |
| Mismatch reduction (7% → ~3%) | 4pp × 15 × $300 × 250 | ~$45K |
| No-show reduction (12% → ~8%, conditional on Decision 2) | 4pp × 15 × $300 × 250 | ~$45K |
| **Year-1 contribution on the slice (illustrative)** | | **~$260K** |

Plausible range with placeholder volume (10–20 fills/day) and the speed-recovery assumption: **~$150K–$400K**.

**Scaled across MedFlex** (when architecture extends beyond the slice): same three levers extrapolate to roughly **~$2M–$5M/year addressable contribution** at current scale — directionally large, but the precise figure depends on the revenue/billings clarification and the slice-extension rate. Foundation of the $200M path; the architecture must absorb ~14× decision volume to get there.

**Five clarifications from Head of Ops Monday would turn this from illustration into a real number:**
1. Whether "$14M revenue" is net agency revenue or gross billings (single biggest math input)
2. Actual MedFlex net revenue per filled shift
3. Volume on the chosen 2-hospital slice (replaces 10–20 fills/day placeholder)
4. Actual competitive-loss rate (replaces 30% industry estimate)
5. Whether the no-show breakdown (~2pp structural multi-agency vs. ~10pp addressable) is roughly right

Until those land, this section is back-of-envelope, not board-defensible.

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
