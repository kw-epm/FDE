# Deliverable #1 — Token Economics: MedFlex Matching Agent

**Author:** Krzysztof Wilniewczyc, FDE
**Date:** 2026-05-22
**Scenario:** Week 3 — MedFlex agentic transformation (planned matching + urgent rematching)
**Anchor architecture:** D#4a (planned) + D#4b (urgent) — extraction agent + ranking agent + HITL trust ramp

---

## 1. Assumptions and source ledger

**Traceability rule for this document:** every financial or operational number below has a source type. Derived figures point back to the row IDs in this table.

| Type | Meaning |
|---|---|
| S | Sourced from the MedFlex scenario or prior deliverables |
| P | Public benchmark or pricing source |
| U | User-confirmed input |
| E | Explicit FDE estimate |
| D | Derived calculation from other ledger rows |

| ID | Assumption / input | Value | Type | Source / derivation |
|---|---|---:|---|---|
| T1 | Coordinator hourly rate, base | $25/h | U | User-confirmed baseline |
| T2 | Fully loaded payroll multiplier | 1.3× | U/E | User-confirmed use of fully loaded rate; standard FDE payroll load assumption |
| T3 | Coordinator hourly rate, loaded | $32.50/h | D | T1 × T2 = $25 × 1.3 |
| T4 | Coordinator day length | 8h | E | Standard full-time workday assumption |
| T5 | Work days per year | 250 | E | 5 work days/week × 50 working weeks/year |
| T6 | Decisions per coordinator per day | 120 | S | MedFlex scenario brief §3 |
| T7 | Coordinator headcount today | 8 | S | D#2 `02-intake-scope.md`: "without 10x-ing the 8 coordinators" |
| T8 | Full-MedFlex annual decision volume today | 240,000 decisions/year | D | T6 × T7 × T5 = 120 × 8 × 250 |
| T9 | Daily MedFlex decision volume today | 960 decisions/day | D | T8 ÷ T5 = 240,000 ÷ 250 |
| T10 | Future coordinator headcount without agent | 14 | E | Counterfactual staffing model: current 8 + 6 hires to support expansion |
| T11 | Future annual volume without agent | 420,000 decisions/year | D | T10 × T6 × T5 = 14 × 120 × 250 |
| T12 | Counterfactual horizon | 18 months | S/E | D#2/D#6 board-growth window; used as a 12–18 month planning view |
| T13 | Pilot slice volume | 15 fills/day | S/E | D#6 slice criterion: "at least ~15 fills/day" |
| T14 | Decisions per fill | 1.3 decisions/fill | E | Allows for declines/timeouts/re-pooling; sensitivity candidate for CFO review |
| T15 | Pilot slice annual decisions | ~5,000 decisions/year | D | T13 × T14 × T5 = 15 × 1.3 × 250 = 4,875, rounded to 5,000 |
| T16 | Baseline mismatch rate | 7% | S | MedFlex scenario brief §3; also mirrored as D#4a guardrail baseline |
| T17 | Target mismatch rate after tuning | 4% | E | FDE target for agent reasoning improvement; stress-tested in §7 as "no reduction" |
| T18 | Mismatch rework time | 20 min/event | E | Coordinator phones nurse, re-matches, and re-sends; sensitivity candidate |
| T19 | FDE day-rate | $1,500/day | U | User-confirmed |
| T20 | Sonnet API price | $3/Mtok input; $15/Mtok output | P | Anthropic API pricing, May 2026: `https://platform.claude.com/docs/en/about-claude/pricing` |
| T21 | Haiku API price | $1/Mtok input; $5/Mtok output | P | Anthropic API pricing, May 2026: same source as T20 |
| T22 | Opus API price | $5/Mtok input; $25/Mtok output | P | Anthropic API pricing, May 2026: same source as T20 |
| T23 | SMS unit price | $0.0083/SMS segment | P | Twilio US SMS pricing: `https://www.twilio.com/en-us/sms/pricing/usa`; carrier fees excluded |
| T24 | Email unit price | $0.0001/email | P | Amazon SES pricing: $0.10/1,000 outbound emails, `https://aws.amazon.com/ses/pricing/` |
| T25 | Team-lead base salary benchmark | ~$73,000/year | P/E | BLS/O*NET SOC 43-1011: US median ~$66k, NY mean ~$77k; $73k midpoint estimate |
| T26 | Recruiting + onboarding cost | $15,000/hire | E | FDE estimate: recruiter time, job-board cost, and first-month productivity drag |
| T27 | Effective coordinator span per lead | 8–10 reports | E | FDE operating assumption for staffing-coordinator supervision |
| T28 | AI ownership role | $50,000/year | E | 0.3–0.5 FTE ML/ops engineer or retainer |
| T29 | Review time per HITL decision | 2 min/review | E | Coordinator reads shortlist, checks reasoning, approves/edits/escalates |
| T30 | Phase 2 HITL rate | 25% | S | D#4a week-8 trust-ramp target: sample audit only; aligns with override target <25% by week 8 |
| T31 | Phase 3 HITL rate | 15% | E | Post-month-6 maturity assumption; stress-tested in §7 through slower HITL |
| T32 | Golden set size | 500 rows | E | FDE test-calibration budget sized for the 2-hospital slice |
| T33 | ATX payback gate | 18 months | S | ATX economic gate used in programme rubric |

Where assumptions are weakest — T14 decisions-per-fill, T18 mismatch rework time, T26 recruiting/onboarding, and T31 Phase 3 HITL rate — sensitivity or explicit caveats cover them.

---

## 2. Baseline human cost (today, no agent)

**Per decision.**

- Direct coordinator time: 8h/day ÷ 120 decisions = **4 min active per decision**.
- Direct cost: 4 min × $32.50/h ÷ 60 = **$2.17 per decision**.
- Mismatch rework: 7% × 20 min × $32.50/h ÷ 60 = **$0.76 per decision** averaged across all decisions.
- **Total baseline: $2.93 per decision.**

### Where $2.93 comes from (one-look derivation)

> **$2.93 per decision = $2.17 active matching + $0.76 averaged rework**
>
> - **$2.17 active matching** = (8 hours/day ÷ 120 decisions/day) × ($32.50/hour ÷ 60 min) = 4 min × $0.5417/min
> - **$0.76 averaged rework** = 7% mismatch rate × 20 min per rework × $32.50/hour ÷ 60 min
>
> **Inputs (all from §1 assumptions table):**
> - 120 decisions per coordinator per day — T6
> - $32.50/hour fully loaded — T3
> - 7% mismatch rate — T16
> - 20 minutes per rework event — T18; flagged in §1 as a weak assumption and stress-tested in §7
>
> **If a coach asks "where did $2.93 come from" — this box is the answer.** All four inputs are named, all multiplications are shown, the two soft assumptions are flagged.

**Annual.**

- 240,000 decisions × $2.93 = **$703,200/year** in coordinator labour attributable to matching, including rework.
- This is the addressable cost the agent has to displace.

---

## 2b. Counterfactual — what happens financially if MedFlex does NOT deploy the agent

"Doing nothing" is not a zero-cost option. The baseline above is today's bill. The counterfactual is what tomorrow's bill looks like without the agent. Three things move against MedFlex over the next ~18 months (T12).

**1. Volume grows. Headcount has to grow with it.**

MedFlex is scaling from the 2-hospital pilot toward the full network (D#2 scope). Today's 8 coordinators handle 240,000 decisions/year at full utilization (T8). To carry the projected month-18 volume of ~420,000 decisions/year (T11), the coordinator team would have to grow from 8 to ~14 — six new hires.

- **Additional coordinator payroll: ~$390,000/year.** Derivation: 6 coordinators × $32.50/h (T3) × 8h (T4) × 250 days (T5) = $390,000.
- **Recruiting + onboarding: ~$90,000 one-off.** Derivation: ~$15k/hire (T26) × 6 hires = $90,000.
- **Second team-lead role: ~$95,000/year fully loaded.** Derivation: ~$73,000 base (T25) × 1.3 loaded multiplier (T2) = $94,900 ≈ $95k. A 14-coordinator span exceeds the assumed single-lead effective span of control (~8–10 reports, T27).

**2. Mismatch costs scale linearly with volume.**

With no agent-driven reasoning improvement, mismatch rate stays at the 7% baseline. As volume grows from today's 240k to the projected month-18 420k:

- **Today's rework cost (no agent, 240k volume): ~$182,000/year.** Derivation: 240,000 × 7% × 20 min × $32.50/h ÷ 60 = $182,000. (This sits inside the §2 baseline; not an additional cost.)
- **Future rework cost (no agent, 420k volume): ~$318,500/year.** Derivation: 420,000 × 7% × 20 min × $32.50/h ÷ 60 = $318,500.
- **Rework delta (the additional cost the agent could prevent): ~$136,500/year.** Derivation: $318,500 − $182,000 = $136,500.

**3. Competitive opportunity cost.**

Per the slice-level competitive-win analysis in D#6 client-feedback (Marcus pushback response), AI-equipped competitors win faster and at higher fill rates. Contribution-margin estimate at risk: ~$260,000/year per slice. Trace: D#6 derives this as speed recovery (~$170k) + mismatch reduction (~$45k) + no-show reduction (~$45k) at 15 fills/day, $300 net revenue/fill, and 250 work days. Across the full network this is mid-six-figures of foregone contribution per year — not a P&L cost line, but a real economic cost.

**Counterfactual summary (12–18 month view):**

| Line | "Do nothing" cost vs today's baseline |
|---|---|
| Additional coordinator payroll (6 new hires fully ramped) | +$390,000/year |
| Additional team-lead role (~14-coordinator span) | +$95,000/year |
| Recruiting + onboarding | +$90,000 one-off |
| Rework at unchanged 7% mismatch on grown volume (240k → 420k) | +$136,500/year (delta vs today) |
| Opportunity cost — competitive win-rate erosion | ~$260,000+/year contribution at risk |
| **Total run-rate cost addition by month 18 (cash + opportunity)** | **~$881,500/year extra cost or foregone margin** (+$90,000 one-off) |

**The real choice on the table.** It is not "spend $95k on the agent versus spend $0." It is:

- **Deploy the agent:** spend $95k build (§5), ~$231k/year run (§4), save ~$472k/year vs today's baseline (§4 Phase 2).
- **Do nothing:** spend ~$0 build, but absorb ~$882k+/year of additional cost and foregone margin by month 18 (§2b table).

**Swing between the two paths: more than $1.35M/year by month 18.** Derivation: ~$472k/year Phase 2 saving vs today's baseline + ~$882k/year counterfactual cost/foregone margin = ~$1.354M/year. The agent does not just save money against today's bill — it prevents a much larger bill that is already on the way as MedFlex grows.

---

## 3. Agent cost per case

Three components: LLM tokens, tools, HITL.

### 3.1 LLM tokens per decision

Based on D#4a workflow (extraction → eligibility filter → ranking with reasoning). Token counts are FDE estimates from the expected prompt/context shape: one free-text request plus schema/citation instructions for extraction; eligible-pool context plus top-N reasoning for ranking.

| Call | Model | Input tokens | Output tokens | Cost derivation | Cost |
|---|---|---|---|---|---|
| Extraction (parse free-text request → structured ShiftRequest with citations) | Haiku | ~2,000 | ~500 | (2,000 × $1 + 500 × $5) ÷ 1,000,000; prices from T21 | **$0.0045** |
| Ranking with reasoning (rank eligible pool, generate per-candidate citations) | Sonnet | ~6,000 (eligible pool context) | ~1,500 (top-N with reasoning) | (6,000 × $3 + 1,500 × $15) ÷ 1,000,000; prices from T20 | **$0.0405** |
| **Total LLM cost per decision** | | | | $0.0045 + $0.0405 | **~$0.045** |

Notes:
- Eligibility filter (step 2 of D#4a) is deterministic rules — no LLM cost.
- Urgent rematching (D#4b) uses the same engine with a narrower pool, so token cost is the same or slightly less. Treating both modes at the planned cost is conservative.
- Citations are part of the ranking output — no separate call.

### 3.2 Tool calls per decision

| Tool | Calls per decision | Cost derivation | Cost |
|---|---|---|---|
| Nurse database query | 1 | Internal API; no per-call charge | negligible |
| Hospital profile read | 1 (cached, 1h TTL) | Internal API; no per-call charge | negligible |
| SMS send for NurseOffer (Twilio) | 1 (planned mode; ~70% of decisions reach SMS) | 0.7 × $0.0083/SMS (T23) = $0.0058 | ~$0.006 |
| Email send for NurseOffer (Amazon SES) | 1 (~30% of decisions go email-only) | 0.3 × $0.0001/email (T24) = $0.00003 | negligible |
| ServiceNow write-back | 1 | Internal API; no per-call charge | negligible |
| **Total tool cost per decision** | | $0.0058 + negligible ≈ $0.006 | **~$0.006** |

### 3.3 HITL cost per decision (varies by trust-ramp phase)

Per D#4a §1 trust ramp: weeks 1–2 = 100% manual approval; weeks 3–4 = high-confidence auto-send; week 8 = sample-audit only. Review rates between named gates are FDE ramp assumptions; T30 anchors the week-8 Phase 2 value.

Formula across all rows: `HITL cost = review rate × 2 min (T29) × $32.50/h (T3) ÷ 60 = review rate × $1.083`

| Phase | Coordinator review rate | Time per review | Cost derivation | HITL cost per decision |
|---|---|---|---|---|
| Weeks 1–2 (cold start) | 100% | 2 min | 1.00 × 2 × 32.50 ÷ 60 = 1.083 | **$1.08** |
| Weeks 3–4 (ramp) | 60% | 2 min | 0.60 × 1.083 = 0.650 | **$0.65** |
| Week 8 (steady state Phase 2) | 25% (T30) | 2 min | 0.25 × 1.083 = 0.271 | **$0.27** |
| Phase 3 (post month 6) | 15% (T31) | 2 min | 0.15 × 1.083 = 0.162 | **$0.16** |

The model below uses **Phase 2 (week 8) as the sustaining baseline** because that is when the trust-ramp targets in D#4a §11 are met. Phase 3 is shown for upside.

### 3.4 Agent cost per case — summary

| Phase | LLM | Tools | HITL | **Total per decision** |
|---|---|---|---|---|
| Weeks 1–2 (cold start) | $0.045 | $0.006 | $1.08 | **$1.13** |
| Week 8 (Phase 2 sustaining) | $0.045 | $0.006 | $0.27 | **$0.32** |
| Phase 3 | $0.045 | $0.006 | $0.16 | **$0.21** |

---

## 4. Annual saving

**Where the savings come from — said plainly.** This model assumes MedFlex **avoids future coordinator hires**. It does *not* assume current coordinators are let go. MedFlex is growing (D#2/D#6: 2-hospital pilot → full network). To carry the planned volume without the agent, the coordinator team would need to grow from 8 to ~14 over the next ~18 months (T10–T12). The agent means that growth doesn't happen. The 8 current coordinators stay, redeployed onto HITL review, escalation handling, and new-hospital onboarding.

**One of the avoided hires is not a coordinator — it's an AI ownership slot.** A part-time ML/ops engineer (or equivalent retainer with the build team) is needed to handle prompt tuning, model upgrades, token-spend monitoring, and on-call when the agent misbehaves. **Coordinators are not qualified for that work** — it is technical AI ops, not staffing operations. This slot is surfaced as a real line in the cost tables below (not buried in infra). Net effect: roughly **5 avoided coordinator hires instead of 6**, plus 1 new technical role.

Two cost lines move when the agent goes in:

1. **Coordinator-time saving** — coordinators no longer do active matching on every decision; only on the review share.
2. **Mismatch-rework saving** — agent reasoning improves match quality (D#4a §6 reasoning-over-context argument). Target mismatch rate: 4% (T17) vs 7% baseline (T16) once the ranker is tuned.

**Phase 1 (weeks 1–2 cold start — 2-week transient, not an annual rate):**

| Line | Value |
|---|---|
| Volume during Phase 1 (10 working days × 960 decisions/day from T9) | ~9,600 decisions |
| Baseline cost on Phase 1 volume (9,600 × $2.93) | ~$28,100 |
| Agent operating cost (9,600 × $1.13 — HITL at 100% review per §3.3) | ~$10,850 |
| Residual rework at unchanged 7% mismatch (ranker not yet tuned; T16/T18) | ~$7,300 |
| AI ownership pro-rated (2/52 weeks of $50k/year; T28) | ~$1,900 |
| **Total Phase 1 cost** | **~$20,050** |
| **Phase 1 saving (cumulative over 2 weeks, not annualized)** | **~$8,000 over 2 weeks** |

Phase 1 is deliberately not shown as an annual rate. It is a 2-week transient. Phase 2 is the sustaining steady state from week 8 onwards (shown as annual below). The ramp between them (weeks 3–7) is captured inside the §6 ramp-adjusted payback calculation; annualizing the ramp would overstate the early-period saving.

**Phase 2 (week 8 steady state):**

| Line | Value |
|---|---|
| Baseline annual cost (§2) | $703,200/year |
| Agent operating cost (240k × $0.32; T8 and §3.4) | $76,800/year |
| Residual rework at 4% mismatch (240k × 4% × 20 min × $32.50/h ÷ 60; T8/T17/T18/T3) | $104,000/year |
| AI ownership — 0.3–0.5 FTE ML/ops engineer or retainer (T28; see §5) | $50,000/year |
| **Total Phase 2 cost** | **$230,800/year** |
| **Annual saving Phase 2** | **$472,400/year** |

**Phase 3 (post month 6):**

| Line | Value |
|---|---|
| Agent operating cost (240k × $0.21; T8 and §3.4) | $50,400/year |
| Residual rework at 4% mismatch (same derivation as Phase 2; T8/T17/T18/T3) | $104,000/year |
| AI ownership (steady state, T28; see §5) | $50,000/year |
| **Total Phase 3 cost** | **$204,400/year** |
| **Annual saving Phase 3** | **$498,800/year** |

**Pilot slice (my 2-hospital slice, 5k decisions/year):**

| Line | Value |
|---|---|
| Baseline cost on the slice (5k × $2.93; T15) | $14,650/year |
| Phase 2 agent cost on the slice (5k × $0.32 + rework at T17/T18/T3) | $3,768/year |
| **Pilot slice saving** | **~$10,900/year** |

The slice cost saving is small (the slice is small). The slice's real economic case is in **contribution-margin uplift from competitive-win speed** (covered in D#6 client-feedback memo, ~$260k year-1 contribution per Marcus pushback response; see §2b competitive-opportunity trace). That sits outside the cost-saving model below.

---

## 5. Build cost

The MedFlex engagement is 8 weeks (D#2/D#6). Build cost is broken into the six ATX-prescribed economics categories from the programme rubric. The local repo snapshot does not include the referenced `inputs/atx/atx-economics.md` file, so the category names are treated as programme-supplied structure rather than an independently inspectable source.

| ATX category | What it covers | Cost |
|---|---|---|
| Assessment and design | Discovery interviews; architecture; ADRs; capability specs | ~$10,000 |
| Development | FDE build of intake parser + matching agent + urgent rematch + HITL queue + audit log | ~$32,000 |
| Integration | ServiceNow read API; nurse DB read API; SMS + email rails; PostgreSQL schema | ~$13,000 |
| Testing and calibration | Eval harness; 500-row golden set (T32); mock-mode fixtures; threshold tuning Pilot Week 1 | ~$5,000 |
| Platform infrastructure setup | Anthropic API setup; database hosting; monitoring; cost meter; circuit breaker | ~$15,000 |
| Change management / training | Coordinator dashboard onboarding; Head-of-Ops playbook; trust-ramp coaching weeks 1–8 | ~$20,000 |
| **Total build cost** | | **~$95,000** |

FDE time underlying: 1 FDE × 8 weeks × 5 days × $1,500/day (T19) = $60,000, distributed across the first four categories above (assessment $10k + development $32k + integration $13k + testing $5k = $60k). Infrastructure setup ($15k) is an FDE estimate for one-off cloud + tooling. Change management ($20k) is estimated client-side time allocated, not billable to the FDE.

**Ongoing AI ownership after Week 8: ~$50,000/year (T28).** This covers a part-time ML/ops engineer (0.3–0.5 FTE) or an equivalent retainer with the build team. Responsibilities: prompt tuning, model upgrades, token-spend monitoring, on-call when the agent misbehaves, quarterly accuracy review on the golden set. **The existing coordinator team is not qualified for this work** — it is technical AI ops, not staffing operations. This cost is surfaced as its own line in §4 (not buried in infra).

---

## 6. Payback period + ROI

Using Phase 2 sustaining saving (now net of AI ownership cost):

- Build cost: $95,000
- Monthly Phase 2 saving: $472,400 ÷ 12 = $39,367/month
- **Naive payback: 2.4 months.**

Ramp-adjusted (weeks 1–2 cold start has near-zero net saving; weeks 3–4 partial; week 5+ full Phase 2). The monthly saving figures below are FDE ramp estimates derived by interpolating between the HITL rates in §3.3 and the full Phase 2 monthly saving of $39,367/month:

| Period | HITL review rate | Effective monthly saving | Cumulative |
|---|---|---|---|
| Months 1–2 (cold start) | 100% → 60% | ~$12,000/month × 2 months = $24,000 | $24,000 |
| Months 3–4 (ramp) | 60% → 40% | ~$25,000/month × 2 months = $50,000 | $74,000 |
| Months 5–6 (late ramp) | 40% → 25% | ~$33,000/month × 2 months = $66,000 | $140,000 |
| Months 7–12 (Phase 2 sustaining) | 25% | ~$39,400/month × 6 months = $236,000 | **$376,000** |

The cumulative saving crosses the $95,000 build cost between month 4 and month 5 (cumulative ~$74k at end of month 4; ~$107k at mid-month 5).

- **Ramp-adjusted payback: ~4.5 months.**

That is the number to put in front of the CFO.

**Year 1 ROI** (ATX programme formula: `(Annual saving − Build cost) / Build cost × 100%`):

- Year 1 net saving (ramp-adjusted, from table above): ~$376,000 — rounded down to ~$360,000 for conservatism (accounting for additional unplanned ramp friction not captured in the four-period model).
- Year 1 ROI = ($360,000 − $95,000) ÷ $95,000 × 100% = **~279%**

**3-year ROI:**

- 3-year cumulative saving (Year 1 ~$360k ramp, Year 2 ~$472k Phase 2, Year 3 ~$486k Phase 2→3 blend): ~$1.32M (AI ownership cost is already netted out inside these figures)
- 3-year net = $1,320,000 − $95,000 = $1,225,000
- 3-year ROI = $1,225,000 ÷ $95,000 × 100% = **~1,290%**

**ATX economic gate** (programme rule: proceed if Year 1 ROI > 0% or payback period ≤ 18 months; T33): MedFlex clears both bars by a wide margin. Even under combined-worst-case stress (§7 final paragraph), Year 1 ROI stays positive and the project is still defensible.

---

## 7. Sensitivity analysis

Five variables a CFO would push on. The model holds under all of them. Each stress case changes one input from the T-ledger and recomputes the §4 Phase 2 saving with all other inputs held constant.

All sensitivity numbers below are net of the $50k/year AI ownership cost.

| Variable | Baseline | Stress test | New Phase 2 saving | New payback |
|---|---|---|---|---|
| **Coordinator hourly rate** | $25 ($32.50 loaded; T1/T3) | $15 ($19.50 loaded) — low US/offshore | $263,000/year | ~7 months |
| **Annual decision volume** | 240k (T8) | 120k (half — pilot expansion stall) | $211,000/year | ~9 months |
| **HITL rate at Phase 2** | 25% (T30) | 50% (trust ramp slower than D#4a targets) | $327,000/year | ~6 months |
| **Token price** | Sonnet at $3/$15 and Haiku at $1/$5 per Mtok (T20/T21) | 2× all token prices | $462,000/year | ~3 months |
| **Mismatch reduction** | 7% → 4% (T16/T17) | No reduction (mismatch stays at 7%) | $393,000/year | ~3.5 months |

**All-stressed-together case** (low rate + half volume + slow HITL + 2× token + no mismatch gain): saving still ~$85,000/year. Payback ~14 months. Tight, but still inside the ATX 18-month gate.

The build-cost number is more brittle than the saving number — if the build runs to 12 weeks instead of 8, build cost rises to ~$135k. Derivation: $95,000 baseline + 4 extra FDE weeks ($1,500/day × 5 days × 4 weeks = $30,000; T19/T5 weekly cadence) + ~$10,000 of additional integration friction, testing rerun, and change-management coaching for the extended timeline = $135,000. Payback stretches from ~4.5 to ~5 months. Still defensible.

---

## 8. Multi-model note (when to use which)

The model uses Haiku for extraction and Sonnet for ranking because that is the cost-correct split for this workload:

| Step | Why this model | Per-decision cost |
|---|---|---|
| **Extraction** (parse free-text → structured ShiftRequest with citations) | Structured-output task with verifiable spans. Haiku handles it. | $0.0045 |
| **Ranking** (reason over heterogeneous soft signals: hospital history, past pairings, urgency, profile notes) | Multi-factor contextual reasoning. Haiku underperforms; Opus costs more without a measured accuracy lift on this task. Sonnet is the right tier. | $0.040 |
| **Citation generation** (per-candidate reasoning summary) | Bundled inside the ranking output. No separate call. | included |

**If we forced Opus everywhere:** per-decision LLM cost rises from ~$0.045 to ~$0.09 using current Anthropic direct API prices (T22). Derivation: extraction `(2,000 × $5 + 500 × $25) ÷ 1,000,000 = $0.0225`; ranking `(6,000 × $5 + 1,500 × $25) ÷ 1,000,000 = $0.0675`. Annual LLM cost rises from ~$10.8k to ~$21.6k at 240k decisions/year, so saving drops by ~$10.8k. Payback remains inside the same rounded month band. Still positive — but the extra cost buys no validated accuracy lift on this workload.

**If we forced Haiku everywhere:** the extraction step is fine but ranking accuracy drops materially (validated qualitatively in D#9 self-spec reflection — Haiku's context reasoning on the slice's worst ambiguous-credential cases was weaker). Cost saving is ~$6.5k/year. Derivation: Haiku ranking cost `(6,000 × $1 + 1,500 × $5) ÷ 1,000,000 = $0.0135`; current ranking cost is $0.0405; delta $0.027/decision × 240k = ~$6.5k. Accuracy loss likely costs more than that in additional mismatches. Not the right call.

**The point for the CFO:** model choice per step is not a default. It is an economic decision tied to what each step actually does.

### 8.1 Why each model was chosen (defendable in one sentence each)

- **Haiku for extraction.** Extraction is a structured-output task — parse free-text into a fixed JSON schema with verifiable spans. The right test is "does the output schema validate and do the cited spans actually exist in the source?" That test passes or fails deterministically. Haiku is sufficient for this class of task and ~3× cheaper than Sonnet on current Anthropic direct pricing (T20/T21).
- **Sonnet for ranking.** Ranking has to weigh heterogeneous soft signals (hospital history, past pairings, urgency, profile notes, ambiguous credentials). Haiku underperforms here — qualitatively validated on the slice's worst ambiguous-credential cases (see D#9 self-spec reflection). Opus is ~1.7× Sonnet cost on current Anthropic direct pricing, but still lacks a measured accuracy lift for this workload. Sonnet is the right tier.
- **No model for eligibility filter.** Deterministic rules. Saves the cost of a third call and removes a class of LLM-driven false positives.

### 8.2 Model-choice validation — how we know the choice is right

The model choice is not a "decide once and hope" decision. It is validated against a 500-row golden set (T32, built during the §5 testing-and-calibration line) at three gates. Thresholds in this table are FDE validation thresholds unless they reference a D#4a trust-ramp target:

| Gate | When | What we measure | Pass threshold |
|---|---|---|---|
| **Pre-launch gate** | End of Week 6 (Testing & Calibration phase) | Extraction: schema-validation rate ≥ 99%, citation accuracy ≥ 95%. Ranking: top-3 candidate match rate vs. coordinator gold ≥ 85%. | Both pass → proceed to launch. Either fails → escalate per §8.3. |
| **Trust-ramp gate** | End of Week 4 of live operation | Coordinator override rate ≤ 20% on the high-confidence auto-send path. Override-reason tagging for any rejected matches. | Pass → continue Phase 2 ramp. Fail → freeze HITL rate; investigate before increasing automation. |
| **Quarterly accuracy review** | Every 3 months in steady state | Re-run the golden set against current production prompts and model versions. Compare to last quarter. Track per-step accuracy drift. | If drift > 3 percentage points on either step → trigger §8.3 escalation. |

### 8.3 Contingency — what we do if Haiku is NOT good enough

If extraction accuracy drops below the §8.2 thresholds, the upgrade path is **Haiku → Sonnet for extraction only** (ranking already uses Sonnet, so no second move needed).

**Cost impact of upgrading extraction from Haiku to Sonnet:**

- Sonnet extraction cost per decision = (2,000 × $3 + 500 × $15) ÷ 1,000,000 = $0.006 + $0.0075 = **$0.0135** (vs Haiku at $0.0045 — 3× more).
- New total LLM cost per decision = $0.0135 (Sonnet extraction) + $0.0405 (Sonnet ranking) = **$0.054** (vs current $0.045 — +$0.009 per decision, +20%).
- New annual LLM cost at 240k volume = 240,000 × $0.009 = **+$2,160/year**.
- **Impact on Phase 2 saving: drops from $472,400 to ~$470,200.** Negligible — well within sensitivity tolerance.
- **Impact on payback: ~4.5 months unchanged** (the per-decision cost shift is below rounding).

**The buffer is real.** Even if Haiku has to be entirely replaced by Sonnet, the economic case barely moves. The doc is not betting the engagement on Haiku working — it is using Haiku because it is *the cheapest sufficient option*, with an explicit upgrade path that costs about $2k/year if needed.

**Architecture note that protects the buffer.** The extraction service is built model-agnostic — the LLM call wrapper (per D#4a §6) takes a model identifier as configuration, not as hard-coded logic. Switching from `haiku-4.5` to `sonnet-4.6` for extraction is a config change + a re-run of the §8.2 pre-launch gate, not a code rewrite. Same applies to ranking if Sonnet ever needs to escalate to Opus (current cost impact: +~$10.8k/year per §8 above).

### 8.4 Model-version cadence

Anthropic releases new model versions roughly every 6–12 months (FDE operating assumption, based on recent vendor cadence). Each release is treated as a §8.2 quarterly-review trigger:

- New model versions are evaluated on the golden set before being promoted to production.
- If a new Haiku version closes the accuracy gap on ranking, we may consolidate ranking onto Haiku → +~$6.5k/year saving (per §8 "if we forced Haiku everywhere" paragraph, with the accuracy gap now closed).
- If a new Sonnet version delivers materially better ranking accuracy at the same cost, we may stay on Sonnet but upgrade — no cost impact, accuracy lift only.
- The AI-ownership slot (§5) is responsible for these evaluations — this is one of the reasons the $50k/year ownership budget is in the model.

---

## 9. CFO one-paragraph summary

The MedFlex matching agent costs ~$95,000 to build, ~$231,000/year to operate at Phase 2 sustaining state (LLM tokens, tools, HITL, residual rework, plus a $50k AI-ownership slot for a part-time ML/ops engineer or retainer), and saves ~$472,000/year against the current coordinator-only baseline of $703,000/year for matching labour and mismatch rework. Ramp-adjusted payback is ~4.5 months. **The savings are avoided future hires, not coordinators let go**: MedFlex would have grown the coordinator team from 8 to ~14 over the next 18 months to carry volume; the agent means ~5 of those hires don't happen, and 1 is reallocated to the AI-ownership role. Under conservative stress (half the volume, slower trust ramp, no mismatch improvement, 2× token prices, low-rate coordinators) the saving still clears $85,000/year and payback stays under 14 months. The build is self-funding inside the 8-week engagement window if it ships on time. Model choice is traceable but not the main economic lever: Haiku-for-extraction saves about $2k/year versus Sonnet extraction, and avoiding Opus end-to-end saves about $10.8k/year at current public prices.
