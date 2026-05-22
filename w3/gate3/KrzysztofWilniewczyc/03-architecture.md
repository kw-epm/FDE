# D#3 Architecture and ADRs

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

One agent. One job. Turn a free-text shift request into an auditable, hospital-ready submission, fast. Confirmed fill (both nurse yes and hospital yes) is tracked downstream as a secondary signal.

The agent reads the email and extracts structured intent. It reasons about which eligible nurses best fit, using hospital acceptance history and past pairings. It produces a ranked shortlist with reasoning a coordinator can audit. Depending on confidence and where v1 is on the trust ramp, it either offers the top candidate to a nurse on its own or hands the shortlist to a coordinator. Nurse accepts explicitly (Decision 2, conditional). MedFlex submits to the hospital. Compliance runs alongside as a human-owned guardrail.

### Why one agent, not many

The business problem (D#1) is matching speed: hospitals pick the fastest qualified offer; MedFlex loses ~30% of shifts to faster competitors today. Solving that means **one thing** has to get faster: the matching loop. Adding more agents for adjacent workflows doesn't move matching latency; it adds surface area to validate, debug, and explain to Marcus inside 8 weeks.

The candidates I considered for separate agents and rejected:

- **A compliance agent.** Compliance is human-owned by design (Decision 1 + edge-case reverse-direction handoff). The compliance team's audit posture is what's defensible to regulators. Agentifying it duplicates their work and breaks their audit posture.
- **A hospital intake agent.** Hospitals already submit by email; the chatbot failure showed they will not adopt a new channel. An intake agent would touch hospitals without changing matching latency. We parse the email instead.
- **A pricing agent.** Pricing is MedFlex's existing process. Out of v1 scope. An agent here adds stakeholder fights without moving the primary KPI.
- **A coordinator-augmentation agent.** This is what the matching agent already is. Adding a second one would compete for the coordinator's attention rather than help.
- **An orchestration agent** for multi-shift / priority queues. This is deterministic logic (Decision 3 four-state lock + scheduler). No contextual reasoning needed; not an agent decision.

What's left as the one agent: the matching loop, with two LLM moments inside it (extraction + ranking, see §"Where the AI actually thinks"). Everything else around the agent (eligibility filter, state machine transitions, integrations, audit trail) is deterministic plumbing.

This also passes the "agents are the mechanism, not a feature label" test. If we added agents for things that aren't agentic decisions, we'd be back to AI-as-a-feature drift. Two of Marcus's prior failures (chatbot + recommender) had a version of that problem: AI sprinkled on workflows it didn't redesign.

**The trade-off.** A multi-agent architecture has real appeal: parallelism, separation of concerns, the ability to scale specialists independently. The reason we don't take that path in v1 is the 8-week constraint and Marcus's tolerance after two prior failures. Adding agents for things that aren't bottlenecks adds risk without addressing the latency problem. Phase 2 (post-week-8, post-clean-labels per Decision 1) can split the ranker into specialty-aware sub-agents if a measured need emerges.

### Two modes, one engine

| Mode | When | Time horizon | Confidence tuning |
|---|---|---|---|
| Planned | Request arrives | Hours | Standard |
| Urgent re-matching | Nurse no-shows or cancels late | Minutes | More forgiving |

Autonomy is governed by the trust ramp below, not the mode table.

## Where the AI actually thinks (the AI-native decision points)

Two places. These are the AI-native moments: where contextual reasoning produces an outcome a rule-based system cannot reach. Everything else in the architecture is deterministic plumbing around these two steps.

**Reading the email.** Hospitals write in messy prose. A rules engine can't pull structured intent out of three paragraphs. An LLM can. That's the first agentic move.

**Reasoning about the match.** The agent reads hospital acceptance patterns, past hospital-nurse pairings, soft signals in the request, coordinator notes if they're there. It doesn't learn a model. It reasons over context as input and shows its reasoning. Coordinator can audit and override.

The previous recommender learned from noisy labels. Ours doesn't learn in v1 at all. That's the differentiator. Phase 2 adds a learned soft-signal layer, after Decision 2 produces clean labels.

### Worked example: the specific moment a rules engine can't reach

Hospital A sends: *"Need an ICU nurse for tomorrow's night shift. Prefer someone we've worked with before. The unit just admitted a pediatric patient with a rare medication allergy."*

A rules engine extracts: `specialty=ICU, date=tomorrow, time=night, certs=ICU+RN`. Done.

The agent reads further and picks up three context signals a rules engine can't:

1. *"someone we've worked with before"* is a soft preference, not a hard requirement. Hospital A's past acceptance history boosts Nurse N (3 prior shifts at Hospital A) over Nurse M (none, despite identical credentials).
2. *"pediatric"* + *"rare medication allergy"* implies the unit wants experience with allergic pediatric cases. The agent searches nurse profile notes for relevant prior shifts and weighs the result.
3. *"tomorrow night"* signals urgency. The agent leans toward known-reliable candidates over pure-credential-leaders, because at short lead time a no-show costs more than a marginal credential gain.

Result: top of the shortlist is Nurse N (Hospital A history + prior pediatric-allergy shift + acceptable credential profile), not Nurse M (slightly stronger credentials, no Hospital A history). A rules engine cannot make this distinction. The agent reasons over context, produces the shortlist, and shows its reasoning. The coordinator audits the *why* at the review step, not just the *who*.

That moment is the agent's actual job. "Matching" is just the label; the work is in the three signals above.

### From email to confirmed fill, step by step

```
Hospital A          Agent                Coordinator            Nurse N            MedFlex submission
   │                 │                       │                    │                       │
   │── email ──────▶ │                       │                    │                       │
   │                 │ extract intent (LLM) │                    │                       │
   │                 │ + citation spans      │                    │                       │
   │                 │                       │                    │                       │
   │                 │ eligibility filter    │                    │                       │
   │                 │ (rules)               │                    │                       │
   │                 │ credential precond.   │                    │                       │
   │                 │                       │                    │                       │
   │                 │ rank over context     │                    │                       │
   │                 │ (LLM): N > M because  │                    │                       │
   │                 │ Hospital A history +  │                    │                       │
   │                 │ pediatric allergy +  │                    │                       │
   │                 │ urgency tilt          │                    │                       │
   │                 │                       │                    │                       │
   │                 │── shortlist + ────▶  │                    │                       │
   │                 │   reasoning           │ approve top pick   │                       │
   │                 │   citations           │ (~30s, sees why)   │                       │
   │                 │                       │                    │                       │
   │                 │ soft-lock fires       │                    │                       │
   │                 │── nurse offer ────────────────────────────▶│                       │
   │                 │   (SMS + email)       │                    │ explicit yes (D2)     │
   │                 │◀───────────────────────────────────────────│                       │
   │                 │                       │                    │                       │
   │                 │ PartialCommitment     │                    │                       │
   │                 │                       │                    │                       │
   │                 │                       │  ────────────────────────────── submission ▶
   │                 │                                                                    │   ◀── primary KPI clock ends here
   │                 │                                                                    │
   │◀──── acceptance ────────────────────────────────────────────────────────────────────│
   │                 │                                                                    │
   │                 │ Confirmed (both yes)                                                │
```

The LLM-thinking moments are the two boxes inside the agent column. Everything else is deterministic plumbing.

### Coordinator perspective: week 1 vs week 8

Same hospital, same email arrives.

**Week 1.** Coordinator opens the dashboard. Sees the parsed structured intent (specialty, dates, credentials, soft preferences) sitting alongside the original email. Spends ~30 seconds confirming the parser got it right; clicks approve. Sees the ranked shortlist with reasoning citations; spends ~60 seconds reading why N is above M; clicks approve. Total touch: ~90 seconds. Used to sit inside a ~4h flow of reading, remembering, waiting, and submission work (endpoint unpinned, per D#1 open question 2).

**Week 8.** Same hospital, same email. The parser and ranker run autonomously for high-confidence cases (which this one is). The coordinator sees the decision in the audit dashboard as a sample audit, ~30 seconds total, only when picked. The 90 seconds at week 1 became zero on the happy path; the coordinator's time has moved to medium-confidence flagged cases, exception paths, and relationship work with hospital and nurses. Headcount stays at eight; decision volume goes from ~960/day to ~13,500/day at maturity.

The architecture is what makes that gradient possible. The trust ramp is what makes it safe.

## Data assumptions

The architecture depends on data we believe exists but haven't yet confirmed.

| Source | What it does | Confidence | Degraded path |
|---|---|---|---|
| Hospital accept/reject records | Reasons about hospital preferences | Medium-high | Eligibility-only ranking; build history from v1 |
| Past hospital-nurse pairings | "Nurse N worked Hospital A 3 times" | Medium-high | Same as above |
| Coordinator notes (free text) | "Don't put nurse X at Hospital B" | Low | Surfaced via coordinator override |
| Hospital preference profiles (formal) | Structured preferences | Very low | Inferred from acceptance history |
| Credential expiry dates | Compliance precondition | High | Without it, the agent can't enforce the eligibility precondition. Engagement stops until data is available, OR coordinators do manual eligibility filtering while we build the integration. |

**Go/no-go gate (week 1):** at least one of the two **high-signal** contextual sources must be usable: hospital accept/reject records OR past hospital-nurse pairings. Coordinator notes and formal preference profiles are softer signals; if those exist alone, we're still close to rules-only / recommender-trap territory. If both high-signal sources are absent, pause the engagement and rescope before building the ranker. We won't ship a v1 that's already in the recommender trap.

## Trust ramp

| Confidence | Ranker weeks 1–2 *(project weeks 2–3; parser ships week 1, ranker week 2)* | Ranker weeks 3–4 | Project week 8 (target) |
|---|---|---|---|
| High | Coordinator approves (~30s, sees reasoning) | Auto, logged | Auto, sample audits |
| Medium | Top 3 to coordinator | Coordinator approves | Coordinator approves |
| Low | Coordinator decides | Coordinator decides | Coordinator decides |

Ranker weeks 5–7 hold the week 3–4 state until metrics confirm the next step is safe. Week 8 is the earliest target, not a guarantee. (Note: the parser ships in project week 1 ahead of the ranker. The trust ramp above is for ranker decisions only. The parser doesn't have confidence levels.)

Mapping to ATX delegation archetypes: "Coordinator decides" = **Human–Decide**. "Coordinator approves" / "Top 3 to coordinator" = **Agent–Flag&Hold**. "Auto, logged" = **Agent–Log&Monitor**. "Auto, sample audits" = closest to **Agent–Autonomous** with periodic review.

### What "high / medium / low confidence" means

Confidence is agreement between signals, not a single score.

- **High:** strong eligibility match + strong historical signal + clear top pick.
- **Medium:** mixed signals or close top-two.
- **Low:** eligibility only, no strong historical signal, or unfamiliar request type.

D#4 names the confidence inputs and flags the production parameters that still need pinning (near-tie threshold, Top-N, weights; see D#4a A11). D#7 validates that high-confidence cases are actually the ones approved without override.

### Why urgent gets a different threshold

- Hospitals decide. Hospital review is the safety net in both modes.
- Reversibility before the shift starts is high.
- The alternative is an unfilled shift, a known-bad outcome.
- Operationally concrete: urgent re-matching has a defined SLA (D#4 spec; e.g., shift starting in <2h needs hospital re-submission in ≤30 min). For synchronous coordinator pre-review to be reliable, coordinator response median must be reliably under that SLA. Without a confirmed coordinator-availability SLA from Head of Ops, requiring synchronous pre-review on urgent paths bets the architecture on staffing patterns we haven't measured.

## Pause / roll back (mirrored from D#1)

| Signal | Pause | Roll back |
|---|---|---|
| Primary KPI | Worse than baseline at week 3 | Worse at week 4 |
| First-pick acceptance | <60% sustained 2 weeks (target at risk) | <50% sustained 2 weeks (Decision 1 quality failing) |
| Hospital accept rate | >10% drop WoW | >20% drop or below baseline 2 weeks |
| Override rate | >50% by week 4 | >70% sustained 2 weeks |
| Per-offer nurse response | Median >70 min planned / >22 min urgent | Median ≥90 min planned / ≥30 min urgent (response distribution saturating the window) |
| No-show (after explicit-yes is live, or after channel-improvement rollout if Decision 2 alternative path applies) | Worse than baseline at week 4 | 5+ points worse |
| Mismatch (guardrail) | >7% on slice 2 weeks | >10% on slice |
| Submission withdrawal rate | >5% on slice | >10% or rising 2 weeks |

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

## Decision 1. Reason over context, don't learn

**Problem.** The previous recommender failed. Marcus said "too many mistakes" and "not enough training." Our reading: it learned a ranking model from noisy historical data. Head of Ops can confirm or correct.

**Decision.** v1 agent doesn't learn. It reasons over historical context as input and shows its reasoning. Coordinator audits; override rate is the trust signal.

**Alternatives:**

1. Smarter ranking model (recommender pattern). Rejected: we've seen this fail.
2. Rules-only in v1, learned in Phase 2. Rejected: doesn't address the tacit-knowledge bottleneck. v1 would be too thin.
3. Force hospitals to submit structured forms. Rejected: they already rejected the chatbot.
4. End-to-end model doing both extraction and ranking. Rejected: lose explainability.

**Consequences:**

- Two-part agent: extraction + reasoning over context. Both genuinely agentic.
- Strength depends on the data. If the contextual sources are absent, v1 degrades toward rules-only, the recommender trap. Hence the go/no-go gate.
- Phase 2 adds a learned soft-signal layer, once Decision 2 produces clean labels.

**Revisit when** override rate is consistently low and clean labels exist for a learned model to demonstrably improve over the reasoning layer.

---

## Decision 2. Make nurses say yes (conditional)

**Problem.** Squad surfaced during discovery prep that today MedFlex may treat "nurse didn't reply" as a yes. Marcus didn't confirm or deny clearly. If true, it likely contributes to the 12% no-show rate and gives the agent fake training data.

**Status: conditional** on Head of Ops confirming (D#1 question 5). If wrong, this ADR shifts to confirmation channel improvements + same-day re-check.

**Decision (if finding holds).** Agent requires explicit nurse acceptance before counting the shift as filled. No reply within the window = move to next candidate.

**Windows (D#4 tunable):**

- Planned: ~90 min from nurse-offer-sent.
- Urgent: ~30 min.

These anchor the nurse-response targets in D#1 and the soft-lock windows in Decision 3.

**Alternatives:**

1. Reminder ping closer to the shift. Rejected: patches the symptom.
2. Phone confirmation by coordinator. Rejected: reintroduces the human-time cost.
3. Longer window for non-urgent. Acceptable as a D#4 parameter.

**Consequences (if finding holds):**

- No-show rate is expected to drop.
- Fill rate may look worse on paper at first. Shifts counted as "filled" but really no-shows now show as unfilled. Honest number.
- Comms layer (SMS / email / fallback) needs work in D#4.
- Phase 2 in Decision 1 unlocks once explicit-yes data accumulates.

**Revisit when** confirmation window length, channel, or no-reply fallback start limiting time-to-fill in production. Tune in production, not up front.

---

## Decision 3. Race conditions

**The problem, in one scene.** Today MedFlex sends the same nurse to several hospitals at the same time, then a coordinator pulls back the losing offers by hand once one hospital says yes. At ~960 decisions/day that just about works. At ~13,500/day (what v1 has to prove the architecture reaches) it stops working. Marcus admitted at the end of discovery he hadn't thought this through at the target volume. The architectural risk: two hospitals end up thinking they have the same nurse.

**The decision: a four-state lock.** Once a candidate is committed, the agent moves them through four states:

| State | What it means | Enters when | Exits when |
|---|---|---|---|
| **Soft-lock** | Offered; neither side has accepted yet. | Agent commits the candidate | First side accepts → Partial commitment. Decline or timeout on either side → Released. |
| **Partial commitment** | One side has accepted; the other has not. Candidate is **not** available for parallel offers. | First acceptance arrives | Second side accepts → Confirmed. Second side declines / times out → Released. Hard-cap timeout → Escalation. |
| **Confirmed** | Both sides have said yes. Shift is filled. | Both acceptances arrive | Shift starts (terminal). |
| **Released** | Available again. | Any decline, timeout, or withdraw | Terminal. |

**State diagram.**

```
                              first side accepts                       both sides accept
   ┌───────────┐  ─────────────────────────────────▶  ┌──────────────┐  ─────────────────▶  ┌───────────┐
   │ Soft-lock │                                       │    Partial   │                       │ Confirmed │ ──▶ shift starts
   └─────┬─────┘                                       │  commitment  │                       └───────────┘
         │                                             └──────┬───────┘
         │                                                    │
         │  decline or timeout                                │  decline, timeout, or hard-cap
         │  (any side, before any acceptance)                 │  (hard-cap path goes via escalation)
         │                                                    │
         ▼                                                    ▼
   ┌────────────────────────────────────────────────────────────────────┐
   │                          Released  (terminal)                       │
   └────────────────────────────────────────────────────────────────────┘
```

**What this prevents (without the lock):**

- **Two hospitals are told they have the same nurse.** One of them gets stood up. The hospital relationship takes the hit; the "no-show" on the books was actually MedFlex double-booking.
- **Manual pull-back stops working at scale.** Today it works because volume is ~960 decisions/day. At ~13,500/day (the v1 target volume) coordinators cannot chase down conflicts fast enough. Conflicts pile up; the agent loses the ground truth on who is actually free.
- **No-show statistics get polluted.** Part of the "12% no-show" becomes hidden internal double-booking rather than a real nurse-behaviour signal. Decision 2's whole improvement plan gets noisier.
- **Hospital trust burns.** Every double-booking is a contract-relationship cost MedFlex cannot pay at scale.

**Why Partial commitment is its own state.** Think of it as preventing a double-booking. The moment we offer a shift, we hold the nurse so no other shift can grab them (Soft-lock). When one side (nurse or hospital) says yes, we hold harder: one side has effectively booked, the other has not confirmed, and we cannot release the nurse to a competing shift until we know how the second side lands (Partial commitment). When both sides accept, the shift is filled (Confirmed). If anyone declines or times out, the nurse is released and the next candidate gets the offer. The "one yes, other pending" state has to be its own step: collapse it into Confirmed and we have lied to the second side; collapse it into Released and we have broken our commitment to the side that already said yes.

*(For the database-minded reader: this is the prepared state in a two-phase commit. Soft-lock = acquire phase; Confirmed = COMMIT; Released = ROLLBACK; hard cap = presumed-abort timeout.)*

**Soft-lock windows.** Same as Decision 2: ~90 min planned, ~30 min urgent (nurse-first workflow). If Head of Ops confirms a hospital-first or parallel workflow, windows track whichever side we are waiting on.

**When the lock fires.** Nurse-first (our assumption): on nurse-offer send. Hospital-first: on hospital submission. Parallel: on whichever event fires first. The state machine itself does not change; only the trigger event.

**What happens if a partial commitment gets stuck.**

- **Nurse accepted, hospital pending.** Re-ping hospital at ~1h planned / ~15m urgent. Coordinator alerted at ~2h / ~30m. Hard cap (24h planned / 2h urgent): withdraw from the nurse gracefully, candidate released.
- **Hospital accepted, nurse pending.** Decision 2's window applies. If the nurse declines or times out, the agent moves to the next candidate on the shortlist. Escalation only if the shortlist is exhausted.

**Alternatives we considered and rejected:**

1. **Today's parallel-and-pull-back.** Doesn't scale.
2. **Strict locking, no timeout.** One unresponsive party freezes the candidate forever.
3. **No locking, tolerate double-commitment.** Chaos.
4. **Sequential windows (no overlap).** Too slow.

**What this costs us.**

- Locking reduces raw parallelism. Today coordinators absorb that cost by hand-pulling pull-backs, which is exactly what doesn't scale.
- The architecture's worst case under normal latency is a stuck partial commitment with a non-responsive hospital. The hard cap bounds it.
- Two parameters live in D#4 and can be tuned: soft-lock window, escalation timeouts (including the hard cap).

**Two direct metrics tell us if the windows are right** (D#4 implements, D#7 validates):

- **Lock-timeout rate.** How often a soft-lock expires with no acceptance. Too high means windows too short.
- **Lock-release-then-immediate-reuse rate.** Whether locking just delayed an inevitable re-offer to the same candidate. Too high means locking is creating delay without preventing anything.

Primary KPI and hospital acceptance rate sit alongside as the broader picture. If either direct metric trips against the week-1 baseline, **tune the window, not the decision.**

**Revisit when** the lock-impact metrics say the windows are wrong in practice. Too many timeouts means windows are too short and we are missing fills. Too many stuck partial commitments means windows are too long and escalation paths are too slow.

---

The three decisions connect. Decision 1 differentiates from the recommender. Decision 2 produces the clean data Phase 2 of Decision 1 needs. Decision 3 lets Decision 1 scale beyond manual pull-back.

## Edge cases the architecture handles

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
- Hallucinated reasoning. Citations mandatory: every claim links to a data source. D#7 validates.
- Prompt injection in emails. Email body is data, not instructions. Output sanitisation. v1 risk is bounded by coordinator review in weeks 1–2.
- Auditability. Persist (input, intent, ranking context, reasoning, decision, timestamp) per shortlist + offer. D#7 covers audit trail validation.

**What the architecture cannot fix:**

- Coordinator override rate stays >50% past week 4 and doesn't drop. Response: narrow the deployment to the categories where overrides ARE low, ship those, iterate on the rest. v1 doesn't have to work for every shift. It has to work for some, well.
- Both high-signal contextual sources (hospital accept/reject records AND past hospital-nurse pairings) absent at the week-1 audit. Response: pause the engagement and rescope at the go/no-go gate. We don't ship a degraded v1 we already know is the recommender trap.
- Marcus pulls the plug at week 6. The slice deployment is stand-alone, can be turned off safely.
- A hospital moves to a structured portal. Coordinator-only routing for that hospital until portal integration in a later phase.
- Insider misuse (rogue coordinator overrides). Audit trail makes it visible after the fact.

## Economics (rough order of magnitude)

The agent makes two LLM calls per shift request: extraction (small input, structured output) and ranking (larger input with historical context, structured output). Token-cost order on rough current LLM pricing assumptions (provider-agnostic; tighten on real provider quote in engagement week 0–1):

| Step | Input tokens | Output tokens | Cost per call (rough) |
|---|---|---|---|
| Extraction (email → structured intent + citations) | ~500 | ~300 | ~$0.005 |
| Ranking (filtered pool + context + reasoning) | ~3,000 | ~600 | ~$0.025 |
| **Per shift request** | | | **~$0.03** |

At v1 slice volume (~15 fills/day): ~$0.45/day, ~$165/year. Negligible against the $260K year-1 contribution illustration.

At full MedFlex scale (~30 fills/day at gross-billings interpretation, ~184 fills/day at net-revenue interpretation, per D#1 §year-1 footnote): ~$2–$5.50/day; ~$700–$2,000/year. Still negligible.

At the ~13,500 decisions/day target (what v1 has to prove the architecture can reach): ~$405/day, ~$148,000/year. Material but not dominant against the gross revenue line.

**Operational implications:**
- **Caching:** historical context queries (hospital acceptance history, past pairings) are read-heavy and stable. Cache with short TTL to amortise cost on repeat requests from the same hospital.
- **Batching:** ranker calls within the same time window can share context (Hospital A's history doesn't change minute-to-minute). Group by hospital_id over 60-second windows.
- **Per-decision budget guard:** circuit-breaker if average per-request cost exceeds 2× the expected (e.g., model upgrade silently increases token use). Triggers ops alert; does not stop the system.
- **Slice scale check:** if the per-decision target is materially higher in production than this estimate, surface it in week 4 metrics and decide whether to invest in batching/caching before scale-up.

**Not yet pinned (flagged in D#4 A12 self-audit):** specific per-second rate-limit budgets per integration, ServiceNow API tier costs, comms-layer (SMS) per-message cost at scale. Closure: integration-design phase (week 0–1 of engagement).
