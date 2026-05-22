# D#3 — Architecture and ADRs

Notes from the call: `discovery_notes.md`.

## Shared glossary

| Term | Meaning |
|---|---|
| Shift request | Free-text hospital email asking for a nurse |
| Candidate shortlist | Agent's ranked top-N eligible nurses, with reasoning |
| Nurse offer | Agent contacts a nurse with a specific shift |
| Nurse acceptance | Nurse explicitly says yes within Decision 2's window |
| Hospital submission | MedFlex submits the accepted nurse to the hospital |
| Hospital acceptance | Hospital says yes |
| Confirmed fill | Both said yes |

Workflow order is our assumption. Marcus's multi-submission description hints it may not be strictly nurse-first. If the actual order is different (D#1 open question 9), the D#4 state machine, Decision 3's lock trigger, and the primary KPI target all adapt. The principles below hold either way.

## The architecture

One agent. One job. Turn a free-text shift request into a confirmed fill, fast.

The agent reads the email and extracts structured intent. It reasons about which eligible nurses best fit, using hospital acceptance history and past pairings. It produces a ranked shortlist with reasoning a coordinator can audit. Depending on confidence and where v1 is on the trust ramp, it either offers the top candidate to a nurse on its own or hands the shortlist to a coordinator. Nurse accepts explicitly (Decision 2, conditional). MedFlex submits to the hospital. Compliance runs alongside as a human-owned guardrail.

### Two modes, one engine

| Mode | When | Time | Confidence tuning |
|---|---|---|---|
| Planned | Request arrives | Hours | Standard |
| Urgent re-matching | Nurse no-shows or cancels late | Minutes | More forgiving |

Autonomy is governed by the trust ramp below, not the mode table.

## Where the AI actually thinks

Two places.

**Reading the email.** Hospitals write in messy prose. A rules engine can't pull structured intent out of three paragraphs. An LLM can. That's the first agentic move.

**Reasoning about the match.** The agent reads hospital acceptance patterns, past hospital-nurse pairings, soft signals in the request, coordinator notes if they're there. It doesn't learn a model. It reasons over context as input and shows its reasoning. Coordinator can audit and override.

The previous recommender learned from noisy labels. Ours doesn't learn in v1 at all. That's the differentiator. Phase 2 adds a learned soft-signal layer, after Decision 2 produces clean labels.

### Worked example: the specific moment a rules engine can't reach

Hospital A sends: *"Need an ICU nurse for tomorrow's night shift. Prefer someone we've worked with before — the unit just admitted a paediatric patient with a rare medication allergy."*

A rules engine extracts: `specialty=ICU, date=tomorrow, time=night, certs=ICU+RN`. Done.

The agent reads further and picks up three context signals a rules engine can't:

1. *"someone we've worked with before"* is a soft preference, not a hard requirement — Hospital A's past acceptance history boosts Nurse N (3 prior shifts at Hospital A) over Nurse M (none, despite identical credentials).
2. *"paediatric"* + *"rare medication allergy"* implies the unit wants experience with allergic paediatric cases — the agent searches nurse profile notes for relevant prior shifts and weighs the result.
3. *"tomorrow night"* signals urgency — the agent leans toward known-reliable candidates over pure-credential-leaders, because at short lead time a no-show costs more than a marginal credential gain.

Result: top of the shortlist is Nurse N (Hospital A history + prior paediatric-allergy shift + acceptable credential profile), not Nurse M (slightly stronger credentials, no Hospital A history). A rules engine cannot make this distinction. The agent reasons over context, produces the shortlist, and shows its reasoning — the coordinator audits the *why* at the review step, not just the *who*.

This is the agent decision point pack §7 asks about. Not "the agent does matching" generically. *This specific scene.*

## Data assumptions

The architecture depends on data we believe exists but haven't yet confirmed.

| Source | What it does | Confidence | Degraded path |
|---|---|---|---|
| Hospital accept/reject records | Reasons about hospital preferences | Medium-high | Eligibility-only ranking; build history from v1 |
| Past hospital-nurse pairings | "Nurse N worked Hospital A 3 times" | Medium-high | Same as above |
| Coordinator notes (free text) | "Don't put nurse X at Hospital B" | Low | Surfaced via coordinator override |
| Hospital preference profiles (formal) | Structured preferences | Very low | Inferred from acceptance history |
| Credential expiry dates | Compliance precondition | High | Without it, the agent can't enforce the eligibility precondition. Engagement stops until data is available, OR coordinators do manual eligibility filtering while we build the integration. |

**Go/no-go gate (week 1):** if the audit shows none of the four contextual sources usable, pause the engagement and rescope. The fallback (rules-only ranking) is what Decision 1 explicitly rejects. We won't ship a v1 that's already in the recommender trap.

## Trust ramp

| Confidence | Ranker weeks 1–2 *(project weeks 2–3 — parser ships week 1, ranker week 2)* | Ranker weeks 3–4 | Project week 8 (target) |
|---|---|---|---|
| High | Coordinator approves (~30s, sees reasoning) | Auto, logged | Auto, sample audits |
| Medium | Top 3 to coordinator | Coordinator approves | Coordinator approves |
| Low | Coordinator decides | Coordinator decides | Coordinator decides |

Ranker weeks 5–7 hold the week 3–4 state until metrics confirm the next step is safe. Week 8 is the earliest target, not a guarantee. (Note: the parser ships in project week 1 ahead of the ranker. The trust ramp above is for ranker decisions only — the parser doesn't have confidence levels.)

Mapping to ATX delegation archetypes: "Coordinator decides" = **Human–Decide**. "Coordinator approves" / "Top 3 to coordinator" = **Agent–Flag&Hold**. "Auto, logged" = **Agent–Log&Monitor**. "Auto, sample audits" = closest to **Agent–Autonomous** with periodic review.

### What "high / medium / low confidence" means

Confidence is agreement between signals, not a single score.

- **High:** strong eligibility match + strong historical signal + clear top pick.
- **Medium:** mixed signals or close top-two.
- **Low:** eligibility only, no strong historical signal, or unfamiliar request type.

D#4 makes the formula precise. D#7 validates that high-confidence cases are actually the ones approved without override.

### Why urgent gets a different threshold

- Hospitals decide. Hospital review is the safety net in both modes.
- Reversibility before the shift starts is high.
- The alternative is an unfilled shift — a known-bad outcome.
- Operationally concrete: urgent re-matching has a defined SLA (D#4 spec — e.g., shift starting in <2h needs candidate resolution in <30 min). For synchronous coordinator pre-review to be reliable, coordinator response median must be reliably under that SLA. Without a confirmed coordinator-availability SLA from Head of Ops, requiring synchronous pre-review on urgent paths bets the architecture on staffing patterns we haven't measured.

## Pause / roll back (mirrored from D#1)

| Signal | Pause | Roll back |
|---|---|---|
| Primary KPI | Worse than baseline at week 3 | Worse at week 4 |
| First-pick acceptance | <60% sustained 2 weeks (target at risk) | <50% sustained 2 weeks (Decision 1 quality failing) |
| Hospital accept rate | >10% drop WoW | >20% drop or below baseline 2 weeks |
| Override rate | >50% by week 4 | >70% sustained 2 weeks |
| Per-offer nurse response | Median >70 min planned / >22 min urgent | At/above Decision 2 window |
| No-show | Worse than baseline 4 weeks after explicit-yes | 5+ points worse |
| Mismatch | >7% on slice 2 weeks | >10% |

Numbers tighten or loosen after week 1 baselines.

## Data flow

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

Compliance subsystem runs alongside, human-owned. Agent reads expiry as a precondition. Verification stays with the team. Credential gap → handoff to compliance team.

This is not a chatbot, not the previous recommender, not a coordinator replacement, not a compliance system, not a learning system in v1, and not full autonomy in 8 weeks.

---

## Decision 1 — Reason over context, don't learn

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

## Decision 2 — Make nurses say yes (conditional)

**Problem.** Pavel surfaced that today MedFlex may treat "nurse didn't reply" as a yes. Marcus didn't confirm or deny clearly. If true, it likely contributes to the 12% no-show rate and gives the agent fake training data.

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

## Decision 3 — Race conditions

**Problem.** Today MedFlex multi-submits the same nurse and pulls back when one accepts. Marcus admitted at session end he hadn't fully thought through this at the target volume. Contention explodes at 14×.

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

## Edge cases — what the architecture handles

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

- Override rate stays high indefinitely. Narrow deployment to categories that work; iterate on the rest.
- All four contextual data sources unusable. Pause and rescope at the go/no-go gate.
- Marcus pulls the plug at week 6. The slice deployment is stand-alone — can be turned off safely.
- A hospital moves to a structured portal. Coordinator-only routing for that hospital until portal integration in a later phase.
- Insider misuse (rogue coordinator overrides). Audit trail makes it visible after the fact.
