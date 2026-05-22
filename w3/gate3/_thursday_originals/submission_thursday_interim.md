# Gate 3 Interim Submission — D#1, D#2, D#3

**Participant:** Krzysztof Wilniewczyc
**Submitted:** Thursday, Week 3 (EOD)
**Status:** Interim draft for the squad lead — input to the Marcus Reyes pushback memo

---

## Marcus, the short version

**What we're building.** An AI agent that reads hospital shift-request emails, reasons about which eligible nurses best fit using historical data, and surfaces a ranked shortlist with explicit reasoning. Coordinators review every decision early; agent autonomy grows as it earns trust by being right. One job. One engine. Two modes — planned matching, and urgent re-matching when a nurse no-shows.

**Why it isn't the chatbot or the recommender.** The chatbot tried to change how hospitals submit. They wouldn't use it. We absorb the email channel — no behaviour change for them. The recommender learned from noisy data and made too many mistakes. We don't learn in v1; we reason transparently. Every coordinator sees why a nurse was picked and can override. Trust is built through audit, not marketing.

**What you'll see in 8 weeks.** On a defined slice — ICU nursing across 2 hospitals — time-to-hospital-submission drops measurably from ~4h to **≤2h** on the nurse-first path, tighter (**≤1h**) where the workflow shape lets us submit earlier. Your <1h headline is the north star; week 8 is the first measurable step, not the full mile. Hospital acceptance rate holds. Coordinators override agent decisions less and less. Concrete numbers below; you mark us against them.

**How this gets to $200M.** Today's 8 coordinators do ~960 matching decisions a day, supporting $14M revenue. At $200M, the system has to absorb ~13,500 decisions a day with the same coordinator headcount. v1 proves the architecture can. The alternative is hiring 100+ more coordinators.

**What could pause us.** Three real risks, each with a tracked metric and a defined response. (1) Data we assume exists isn't usable → we audit in week 1 and rescope before building. (2) Coordinator override rate stays high → we narrow to categories that work, ship those, iterate on the rest. (3) The no-reply-as-yes finding doesn't hold → we shift to confirmation-channel improvements.

---

## D#1 — Problem framing & success metrics

### The problem

MedFlex takes too long to put a nurse in front of a hospital. Marcus said it himself: *"if someone submits quicker than I do, the hospital picks them."* In this market, slow means lost.

Marcus gave us roughly 4 hours per fill today, target under 1 hour. Endpoint isn't pinned (offer / submission / confirmed fill — open question 2). He also hedged on the 4h ("never beyond" then "sometimes longer than 4 hours"), so we treat it as a working figure pending Head of Ops.

The 3-hour gap isn't laziness. It's what coordinators have to do:

- Read messy email shift requests and figure out what's actually needed
- Match against tacit knowledge that lives in their heads, not any system
- Multi-offer the same nurse to several hospitals at once, then pull back

The 7% mismatch could be time pressure pushing "close enough" over "right" — but Marcus said the 7% is hospital-flagged, not internally categorised. Could be ranking, eligibility, or compliance data. We don't have the breakdown. Open question for Head of Ops.

### What "10x without 10x-ing" means in numbers

Marcus gave the headline: $14M today → $200M in 24 months.

The math: 8 coordinators × ~120 decisions/day = ~960/day. If shift volume tracks revenue, ~13,500/day at maturity. The same 8 people can't do that. Either hire 100+ more, or the system takes the load. That's the architectural requirement v1 has to prove the design can reach. v1 doesn't have to deliver 13,500/day in 8 weeks.

The 8-week target Marcus asked for is "money back signal." We'll define it in D#7. For now: a measurable drop in time-to-hospital-submission on the slice.

### Success metrics

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
| Guardrail | Mismatch rate (wrong credentials for facility type) | 7% system-wide; slice trend by week 4–6 | hold or improve |
| Guardrail — KPI honesty | Submission withdrawal rate (submissions later retracted before hospital acceptance — catches KPI-gaming via provisional packets) | new metric | <5% on slice |

Two caveats on the table:

1. **Baseline endpoint is unpinned.** Marcus's ~4h is the only existing number, but the endpoint isn't clear (offer / submission / confirmed fill — open question 2). Week 1 instrumentation has to establish a request→submission baseline specifically; the improvement claim only stands when we compare like to like.
2. **Decision 2 dependency.** Several targets are conditional on Decision 2 holding (Head of Ops confirming the no-reply finding). If it doesn't hold, the no-show ≤8% target shifts to a confirmation-channel improvement target (Decision 2 alternative path in D#3), and per-offer nurse response time becomes a diagnostic rather than a primary metric. The primary KPI itself doesn't change.

The math works at these targets: with ≥75% first-pick + <30 min to offer + <60 min nurse response, median lands ~90–110 min, well inside the ≤2h target. Below ~60% first-pick the target is at risk; below ~50% the simplified nurse-first median likely misses ≤2h. The 60% trigger below is conservative on purpose.

Why primary KPI ends at hospital submission, not at confirmed fill: hospital response time is downstream of our action. Measuring only up to our action keeps us honest about what we control. Hospital response latency belongs to confirmed-fill analysis; hospital acceptance rate separately tracks whether our submissions are good enough.

### Pause / roll back

Pause = hold autonomy at current level. Roll back = drop one level on the D#3 trust ramp.

| Metric | Pause | Roll back |
|---|---|---|
| Primary KPI | Worse than baseline at week 3 | Worse at week 4 |
| First-pick acceptance | <60% sustained 2 weeks (target at risk) | <50% sustained 2 weeks (Decision 1 quality failing) |
| Hospital accept rate | >10% drop WoW | >20% drop or below baseline 2 weeks |
| Override rate | >50% by week 4 | >70% sustained 2 weeks |
| Per-offer nurse response | Median >70 min planned / >22 min urgent | Median ≥90 min planned / ≥30 min urgent (response distribution saturating the window) |
| No-show | Worse than baseline 4 weeks after explicit-yes (or after channel-improvement rollout, if Decision 2 alternative path applies) | 5+ points worse |
| Mismatch | >7% on slice 2 weeks | >10% |
| Submission withdrawal rate | >5% on slice | >10% or rising 2 weeks |

Numbers tighten or loosen after week 1 baselines come in. First-pick acceptance only becomes meaningful from week 2 onward (week 1 is baseline + instrumentation) — early-week noise does not trigger the pause.

### What we're not measuring (and why)

- Money saved per shift — Marcus said it's not relevant.
- Coordinator headcount — Marcus said he'd grow the team if business grows.
- The 7% mismatch — tracked as a guardrail, not optimised against.

### Open questions for Head of Operations

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

---

## D#2 — Engagement intake & scope

### The business

MedFlex. Healthcare staffing agency. 200 employees, 5 US states. Connects travel nurses with hospitals that need shifts filled. Just closed Series B. CEO Marcus Reyes wants $14M → $200M in 24 months without 10x-ing the 8 coordinators.

Two prior AI projects failed:

- **Chatbot for hospitals.** They wouldn't use it. They prefer email.
- **Recommendation engine for matching.** "Too many mistakes" (Marcus). Coordinators stopped using it.

Whatever we build has to look clearly different from both.

### Stakeholders

| Who | Owns | Engaged |
|---|---|---|
| Marcus Reyes (CEO) | Growth, board, 8-week ROI | Yes (discovery) |
| Head of Operations | Coordinator workflow | Not yet. Primary follow-up. |
| Coordinators (8) | The matching today | Not yet. Change management. |
| Compliance team | Credentialing | In architecture, out of v1 automation |
| Legal/sales | Hospital contracts | Not yet |
| Marketing | Nurse recruitment | Not v1 |
| Hospitals | Submit requests, accept/reject | External; their signal is critical |
| Nurses | Accept or refuse offers | External; their behaviour drives no-shows |
| CFO (implied) | Year-1 numbers | Likely Marcus pushback |

### Constraints

- Marcus wants ROI signal in 8 weeks.
- Email is sticky (hospitals rejected the chatbot).
- No layoff framing (Marcus said he'd grow the team if the business grows).
- Trust is low after two failures — output has to be explainable.
- Compliance stays separate — the coach hammered this in the debrief.

### Risks

| Risk | Likelihood | Handling |
|---|---|---|
| Agent makes visible mistakes early, coordinators reject it | High | Start in human-review. Earn the autonomy. Show reasoning on every decision. |
| Hospital acceptance rate drops | Medium | Baseline week 1, weekly tracking, rollback triggers in D#1 |
| Coordinators feel threatened, sabotage adoption | Medium | Three moves: design from week 1, override visibility on every offer, named "matching specialists" role |
| Multi-submission race conditions at scale | High at scale | Decision 3 in D#3 (four-state lock with partial-commitment handling) |
| Tacit knowledge isn't in any system | High | Agent reads historical context — assumes data exists. See D#3 data assumptions and the go/no-go gate. |
| CFO wants a dollar number | Medium | Operational metrics with stated reason for not anchoring on dollars |
| Email-only assumption wrong (portal volume significant) | Medium | Confirm with Head of Ops before D#4 |
| 8-week target slips on instrumentation | Medium | Week 1 reserved for baselines. Improvement clock starts week 2. |
| ICU slice is the wrong slice | Medium | Alternative slices ready |
| Assumed workflow order is wrong | Medium | D#3 glossary flags this. State machine, lock point, KPI target all adapt. |

### v1 — what we'll build

**One thing — matching — in two modes. Same engine.**

1. **Planned matching.** Hospital sends a shift request. Agent reads it, ranks eligible nurses with reasoning, surfaces shortlist to coordinator. Coordinators in the loop early; autonomy grows on the trust ramp (D#3). Main volume.

2. **Urgent re-matching.** Nurse no-shows or cancels late. Same engine. Less time, fewer choices, different oversight thresholds.

Plus: nurses say yes explicitly — conditional on confirming the no-reply finding (Decision 2 in D#3).

### The slice

Working hypothesis: **ICU on 2 hospitals.** Reasons (from industry norms, not yet confirmed with MedFlex):

- High volume + high margin, so speed pressure is sharpest
- Credential complexity is uniform within ICU
- Two hospitals — enough to see hospital-specific reasoning vs one-hospital coincidence
- Small enough to tune and stay close

Our guess. Head of Ops may steer us. Alternatives ready: Med-Surg, Telemetry, or one hospital + multiple specialties.

### Out of scope (in v1)

| Out | Why |
|---|---|
| Compliance automation | Pack says it's in engagement scope. Marcus and the coach both said separate process. We honor both: agent reads credential expiry as a precondition, doesn't verify. |
| Hospital portal or chatbot | Hospitals rejected the chatbot. Email is the channel. |
| Nurse-facing app | Out of pack scope. Not the bottleneck. |
| Pricing engine | Out of pack scope. |
| Cross-agency nurse dedup | Industry problem. Not soluble in 8 weeks. Guardrail: if no-show driver analysis shows this dominates past v1 baseline, response is operational (Decision 2's same-day re-check ping pattern), not architectural — tracked in no-show driver diagnosis. |
| CE renewal automation | Out of pack scope. |
| Coordinator restructuring | HR question, not a build question. |
| Quality scoring rebuild | Bigger initiative on its own. |
| Sales-side contract optimisation | Owned by Legal/Sales. |

Open questions for Head of Ops are in D#1.

### What 8 weeks looks like

Working agent on the slice. Reads emails. Ranks nurses with explicit reasoning. Coordinators in the loop early, more autonomous over time per the D#3 ramp. Time-to-hospital-submission drops measurably, trajectory toward Marcus's <1h target where workflow order makes that mechanically possible. Marcus sees the ROI signal coming.

Everything else is later phases.

---

## D#3 — Architecture and ADRs

### Shared glossary

| Term | Meaning |
|---|---|
| Shift request | Free-text hospital email asking for a nurse |
| Candidate shortlist | Agent's ranked top-N eligible nurses, with reasoning |
| Nurse offer | Agent contacts a nurse with a specific shift |
| Nurse acceptance | Nurse explicitly says yes within Decision 2's window |
| Hospital submission | MedFlex submits the accepted nurse to the hospital |
| Hospital acceptance | Hospital says yes |
| Confirmed fill | Both said yes |

Glossary uses nurse-first naming. In hospital-first or parallel workflows, the milestone names stay but their order shifts; D#4 will rename / re-sequence as needed once Head of Ops confirms.

Workflow order is our assumption. Marcus's multi-submission description hints it may not be strictly nurse-first. If the actual order is different (D#1 open question 9), the D#4 state machine, Decision 3's lock trigger, and the primary KPI target all adapt. The principles below hold either way.

### The architecture

One agent. One job. Turn a free-text shift request into an auditable, hospital-ready submission, fast. Confirmed fill — both nurse yes and hospital yes — is tracked downstream as a secondary signal.

The agent reads the email and extracts structured intent. It reasons about which eligible nurses best fit, using hospital acceptance history, past pairings, and nurse preferences (location, hours, hospital affinity) where available. It produces a ranked shortlist with reasoning a coordinator can audit. Depending on confidence and where v1 is on the trust ramp, it either offers the top candidate to a nurse on its own or hands the shortlist to a coordinator. Nurse accepts explicitly (Decision 2, conditional). MedFlex submits to the hospital. Compliance runs alongside as a human-owned guardrail.

#### Two modes, one engine

| Mode | When | Time | Confidence tuning |
|---|---|---|---|
| Planned | Request arrives | Hours | Standard |
| Urgent re-matching | Nurse no-shows or cancels late | Minutes | More forgiving |

Autonomy is governed by the trust ramp below, not the mode table.

### Where the AI actually thinks

Two places.

**Reading the email.** Hospitals write in messy prose. A rules engine can't pull structured intent out of three paragraphs. An LLM can. That's the first agentic move.

**Reasoning about the match.** The agent reads hospital acceptance patterns, past hospital-nurse pairings, soft signals in the request, coordinator notes if they're there. It doesn't learn a model. It reasons over context as input and shows its reasoning. Coordinator can audit and override.

The previous recommender learned from noisy labels. Ours doesn't learn in v1 at all. That's the differentiator. Phase 2 adds a learned soft-signal layer, after Decision 2 produces clean labels.

### Data assumptions

The architecture depends on data we believe exists but haven't yet confirmed.

| Source | What it does | Confidence | Degraded path |
|---|---|---|---|
| Hospital accept/reject records | Reasons about hospital preferences | Medium-high | Eligibility-only ranking; build history from v1 |
| Past hospital-nurse pairings | "Nurse N worked Hospital A 3 times" | Medium-high | Same as above |
| Coordinator notes (free text) | "Don't put nurse X at Hospital B" | Low | Surfaced via coordinator override |
| Hospital preference profiles (formal) | Structured preferences | Very low | Inferred from acceptance history |
| Credential expiry dates | Compliance precondition | High | Without it, the agent can't enforce the eligibility precondition. Engagement stops until data is available, OR coordinators do manual eligibility filtering while we build the integration. |

**Go/no-go gate (week 1):** the four contextual sources are the top four rows (acceptance records, past pairings, coordinator notes, preference profiles). Credential expiry is a separate hard eligibility blocker, not a contextual source. Within the four, **at least one of the two high-signal sources must be usable** — hospital accept/reject records OR past hospital–nurse pairings. Coordinator notes and formal preference profiles are softer signals; if those exist alone, we're still close to rules-only / recommender-trap territory. If both high-signal sources are absent, pause the engagement and rescope before building. We won't ship a v1 that's already in the recommender trap.

### Trust ramp

| Confidence | Week 1–2 | Week 3–4 | Week 8 (target) |
|---|---|---|---|
| High | Coordinator approves (~30s, sees reasoning) | Auto, logged | Auto, sample audits |
| Medium | Top 3 to coordinator | Coordinator approves | Coordinator approves |
| Low | Coordinator decides | Coordinator decides | Coordinator decides |

Weeks 5–7 hold the week 3–4 state until metrics confirm the next step is safe. Week 8 is the earliest target, not a guarantee.

Medium-confidence transition (weeks 1–2 → 3–4): coordinator goes from "pick one of the agent's top 3" to "approve the agent's single top pick." This is trust growing, not transparency shrinking — the agent's reasoning is visible at every step.

Mapping to ATX delegation archetypes: "Coordinator decides" = **Human–Decide**. "Coordinator approves" / "Top 3 to coordinator" = **Agent–Flag&Hold**. "Auto, logged" = **Agent–Log&Monitor**. "Auto, sample audits" = closest to **Agent–Autonomous** with periodic review.

#### What "high / medium / low confidence" means

Confidence is agreement between signals, not a single score.

- **High:** strong eligibility match + strong historical signal + clear top pick.
- **Medium:** mixed signals or close top-two.
- **Low:** eligibility only, no strong historical signal, or unfamiliar request type.

D#4 makes the formula precise. D#7 validates that high-confidence cases are actually the ones approved without override.

#### Why urgent gets a different threshold

- Hospitals decide. Hospital review is the safety net in both modes.
- Reversibility before the shift starts is high.
- The alternative is an unfilled shift — a known-bad outcome.
- Operationally concrete: urgent re-matching has a defined SLA (D#4 spec — e.g., shift starting in <2h needs candidate resolution in <30 min). For synchronous coordinator pre-review to be reliable, coordinator response median must be reliably under that SLA. Without a confirmed coordinator-availability SLA from Head of Ops, requiring synchronous pre-review on urgent paths bets the architecture on staffing patterns we haven't measured.

### Pause / roll back (mirrored from D#1)

| Signal | Pause | Roll back |
|---|---|---|
| Primary KPI | Worse than baseline at week 3 | Worse at week 4 |
| First-pick acceptance | <60% sustained 2 weeks (target at risk) | <50% sustained 2 weeks (Decision 1 quality failing) |
| Hospital accept rate | >10% drop WoW | >20% drop or below baseline 2 weeks |
| Override rate | >50% by week 4 | >70% sustained 2 weeks |
| Per-offer nurse response | Median >70 min planned / >22 min urgent | Median ≥90 min planned / ≥30 min urgent (response distribution saturating the window) |
| No-show | Worse than baseline 4 weeks after explicit-yes (or after channel-improvement rollout, if Decision 2 alternative path applies) | 5+ points worse |
| Mismatch | >7% on slice 2 weeks | >10% |
| Submission withdrawal rate | >5% on slice | >10% or rising 2 weeks |

Numbers tighten or loosen after week 1 baselines. First-pick acceptance only becomes meaningful from week 2 onward — early-week noise does not trigger the pause (mirrored from D#1).

### Data flow

```
Hospital shift request (email)
     │
     ▼
Agent extracts structured intent
     │
     ▼
Eligibility filter (credentials, availability, location)
     │     └─── Compliance precondition: credentials current?
     │             No → filter out + handoff to compliance team
     │
     ▼
Agent reasons over historical context
     │
     ▼
Ranked candidate shortlist + reasoning
     │
     ▼
Confidence gate × trust ramp → auto / flag / human
     │
     ▼
Nurse offer
     │
     ▼
Nurse explicit acceptance (Decision 2, conditional)
     │
     ▼
Hospital submission ← primary KPI ends here
     │
     ▼
Hospital acceptance → Confirmed fill
```

This is the nurse-first happy path. In hospital-first or parallel workflows, hospital submission can happen earlier in the sequence (before nurse acceptance), which is why the primary KPI target is more aggressive in those modes (≤1h vs ≤2h). In those variants, early submission is provisional — subject to nurse acceptance per Decision 2 — until both sides confirm (no commitment to the hospital becomes binding without nurse acceptance). D#4 encodes the actual variant once Head of Ops confirms workflow order.

Compliance subsystem runs alongside, human-owned. Agent reads expiry as a precondition. Verification stays with the team. Credential gap → handoff to compliance team.

This is not a chatbot, not the previous recommender, not a coordinator replacement, not a compliance system, not a learning system in v1, and not full autonomy in 8 weeks.

---

### Decision 1 — Reason over context, don't learn

**Problem.** The previous recommender failed. Marcus said "too many mistakes" and "not enough training." Our reading: it learned a ranking model from noisy historical data. Head of Ops can confirm or correct.

**Decision.** v1 agent doesn't learn. It reasons over historical context as input and shows its reasoning. Coordinator audits; override rate is the trust signal.

**Alternatives:**

1. Smarter ranking model (recommender pattern). Rejected — we've seen this fail.
2. Rules-only in v1, learned in Phase 2. Rejected — doesn't address the tacit-knowledge bottleneck. v1 would be too thin.
3. Force hospitals to submit structured forms. Rejected — they already rejected the chatbot.
4. End-to-end model doing both extraction and ranking. Rejected — lose explainability.

**Consequences:**

- Two-part agent: extraction + reasoning over context. Both genuinely agentic.
- Strength depends on the data. If the contextual sources are absent, v1 degrades toward rules-only — the recommender trap. Hence the go/no-go gate.
- Phase 2 adds a learned soft-signal layer, once Decision 2 produces clean labels.

**Revisit when** override rate is consistently low and clean labels exist for a learned model to demonstrably improve over the reasoning layer.

---

### Decision 2 — Make nurses say yes (conditional)

**Problem.** Squad surfaced during discovery prep that today MedFlex may treat "nurse didn't reply" as a yes. Marcus didn't confirm or deny clearly. If true, it likely contributes to the 12% no-show rate and gives the agent fake training data.

**Status: conditional** on Head of Ops confirming (D#1 question 5). If wrong, this ADR shifts to confirmation channel improvements + same-day re-check.

**Decision (if finding holds).** Agent requires explicit nurse acceptance before counting the shift as filled. No reply within the window = move to next candidate.

**Windows (D#4 tunable):**

- Planned: ~90 min from nurse-offer-sent.
- Urgent: ~30 min.

These anchor the nurse-response targets in D#1 and the soft-lock windows in Decision 3.

**Alternatives:**

1. Reminder ping closer to the shift. Rejected — patches the symptom.
2. Phone confirmation by coordinator. Rejected — reintroduces the human-time cost.
3. Longer window for non-urgent. Acceptable — D#4 parameter.

**Consequences (if finding holds):**

- No-show rate is expected to drop.
- Fill rate may look worse on paper at first — shifts counted as "filled" but really no-shows now show as unfilled. Honest number.
- Comms layer (SMS / email / fallback) needs work in D#4.
- Phase 2 in Decision 1 unlocks once explicit-yes data accumulates.

**Revisit when** confirmation window length, channel, or no-reply fallback start limiting time-to-fill in production. Tune in production, not up front.

---

### Decision 3 — Race conditions

**Problem.** Today MedFlex multi-submits the same nurse and pulls back when one accepts. Marcus admitted at session end he hadn't fully thought through this at the target volume. At ~14× decision volume (per the architectural decode), contention scales superlinearly with parallel submissions — manual pull-back stops working.

**Decision.** Four-state lock with explicit handling of partial commitments.

| State | Means | Enter | Leave |
|---|---|---|---|
| Soft-lock | Committed; neither side accepted | Agent commits the candidate | Side accepts → partial commitment; both accept → confirmed; decline → released; timeout → released |
| Partial commitment | One side accepted, other pending. Candidate not available for parallel offers. | First acceptance | Other accepts → confirmed; declines → released, re-pool; times out → escalation |
| Confirmed | Both accepted | Both accepts | Shift starts |
| Released | Available again | Any release condition | (terminal) |

**Soft-lock windows match Decision 2 in nurse-first workflow:** ~90 min planned, ~30 min urgent. For hospital-first or parallel, windows match whichever party we're waiting on — open question for Head of Ops on typical hospital response times.

**Why partial commitment is its own state.** If the lock just timed out after one side accepted, the candidate could be re-offered while the other side was still pending. Exact double-commitment chaos we're preventing.

**Escalation for stuck partial commitments:**

- Nurse accepted, hospital pending: re-ping hospital at ~1h planned / ~15m urgent. Coordinator alerted at ~2h / ~30m. Hard cap (e.g. 24h non-urgent / 2h urgent): withdraw from nurse gracefully, candidate released.
- Hospital accepted, nurse pending: Decision 2's window applies. If nurse declines or times out, agent submits the next candidate. No escalation unless shortlist is exhausted.

**Lock trigger depends on workflow order.** In nurse-first (our assumption), the lock fires on nurse offer. In hospital-first, on hospital submission. In parallel, on whichever event fires first. State machine doesn't change. D#4 wires the actual trigger once Head of Ops confirms order.

**Alternatives:**

1. Today's parallel multi-submission, manual pull-back. Rejected — doesn't scale.
2. Strict locking, no timeout. Rejected — single unresponsive party freezes the candidate.
3. No locking, tolerate double-commitment. Rejected — chaos.
4. Sequential offer windows (no overlap). Rejected — too slow.

**Consequences:**

- Lock-state data store needed (D#4 spec).
- Coordinator dashboard shows locked candidates.
- Soft-lock window, escalation timeouts, and hard caps are D#4 parameters.
- Stuck partial commitment with a non-responsive hospital is the architecture's worst case under normal latency. Hard cap bounds it.
- Tradeoff: locking reduces raw parallelism. Today coordinators absorb that cost manually by chasing pull-backs (which doesn't scale).
- Direct locking-impact metrics (D#4 implements, D#7 validates): **lock-timeout rate** (soft-lock expires with no acceptance — measures wasted lock-time) and **lock-release-then-immediate-reuse rate** (measures whether locking just delayed an inevitable re-offer to the same candidate). These are direct, not downstream-only. Primary KPI and hospital acceptance rate sit alongside as the broader signals. If either direct metric exceeds thresholds set against week-1 data, tune the soft-lock window, not the decision.

**Revisit when** soft-lock or escalation timeouts prove wrong in practice — too many timeouts (windows too short, missing fills) or too many stuck partial commitments (windows too long, escalation paths too slow).

---

The three decisions connect. Decision 1 differentiates from the recommender. Decision 2 produces the clean data Phase 2 of Decision 1 needs. Decision 3 lets Decision 1 scale beyond manual pull-back.

### Edge cases — what the architecture handles

**Race conditions inside the lock:**

- Late acceptance at window boundary. Acceptance received before timeout signal counts. Last-writer-wins is acceptance.
- Acceptance then withdrawal. State returns to released, treated as decline.
- Credential or availability changes between shortlist and offer. Re-check at offer time.
- Hospital cancels mid-flow. New state transition: any state → release.

**Cross-system / external failures:**

- Cross-agency double-booking. Our lock is internal. Bounded by Decision 2 no-show tracking, not architecture.
- Agent crash mid-flow. Lock state must be durable, not in-memory. Resume from last state. D#4 spec.
- Volume spike (5× overnight). Queue, raise review thresholds, alert ops. Don't drop requests.
- Hospital response time degrades for reasons unrelated to us. Affects time-to-confirmed-fill, not the primary KPI (which ends at submission). Hospital acceptance rate is tracked separately as a submission-quality signal (yes/no rate, not latency).
- ServiceNow outage. Buffer locally, retry, alert ops.
- LLM provider outage. Fall back to coordinator-only routing. Don't fail open or closed.

**LLM-specific failure modes:**

- Hallucinated extraction. Two-stage extraction with cross-check against source text. Suspicious cases flagged low confidence.
- Hallucinated reasoning. Citations mandatory — every claim links to a data source. D#7 validates.
- Prompt injection in emails. Email body is data, not instructions. Output sanitisation. v1 risk is bounded by coordinator review in weeks 1–2.
- Auditability. Persist (input, intent, ranking context, reasoning, decision, timestamp) per shortlist + offer. D#7 covers audit trail validation.

**What the architecture cannot fix:**

| Issue | Result / response |
|---|---|
| Coordinators keep overriding the agent | The agent is not saving enough work. Narrow v1 to shift categories where overrides are low; keep the rest coordinator-led. |
| All four contextual data sources are unusable | Pause and rescope at the go/no-go gate. |
| Marcus pulls the plug at week 6 | Slice deployment is stand-alone: only ICU shift requests from the two selected pilot hospitals use the agent. Turning it off routes those requests back to the existing coordinator workflow without breaking the rest of MedFlex operations. |
| A hospital moves to a structured portal | Route that hospital to coordinators until portal integration is added later. |
| Coordinator misuses overrides to favour or block specific nurses | Audit trail cannot prevent every misuse, but it makes suspicious override patterns visible. |
