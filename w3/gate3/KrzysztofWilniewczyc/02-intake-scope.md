# D#2 Engagement intake & scope

## The business

MedFlex. Healthcare staffing agency. 200 employees, 5 US states. Connects travel nurses with hospitals that need shifts filled. Just closed Series B. CEO Marcus Reyes wants $14M → $200M in 24 months without 10x-ing the 8 coordinators.

Two prior AI projects failed:

- **Chatbot for hospitals.** They wouldn't use it. They prefer email.
- **Recommendation engine for matching.** "Too many mistakes" (Marcus). Coordinators stopped using it.

Whatever we build has to look clearly different from both.

## Stakeholders

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
| CFO | Year-1 dollar number for the board deck | Engaged Friday following Marcus's escalation on board-deck inputs; needs year-1 contribution estimate by Monday (handled in D#1 §Year-1 contribution + D#6) |

## Constraints

- Marcus wants ROI signal in 8 weeks.
- Email is sticky (hospitals rejected the chatbot).
- No layoff framing (Marcus said he'd grow the team if the business grows).
- Trust is low after two failures, output has to be explainable.
- Compliance stays separate, confirmed during discovery and in the post-discovery sync.

## Risks

Severity is **P × I** where P = probability and I = impact (both L / M / H). Critical = HH; High = HM or MH; Medium = MM or LH/HL; Low = LM or ML; Negligible = LL.

| Risk | P × I | Severity | Owner | Close by | Handling |
|---|---|---|---|---|---|
| Agent makes visible mistakes early, coordinators reject it | H × M | High | Engagement lead + coordinator-lead | Week 4 (override rate <40%) | Start in human-review. Earn the autonomy. Show reasoning on every decision. |
| Hospital acceptance rate drops | M × H | High | Engagement lead | Ongoing (weekly) | Baseline week 1, weekly tracking, rollback triggers in D#1. |
| Coordinators feel threatened, sabotage adoption | M × H | High | Head of Ops + engagement lead | Week 0 (change-comms) | Three moves: design partnership from week 1, override visibility on every offer, named "matching specialists" role. |
| Multi-submission race conditions at scale | H × H | Critical | FDE / architecture | D#4 spec (week 0) | Decision 3 in D#3 (four-state lock with partial-commitment handling). |
| Tacit knowledge isn't in any system | H × H | Critical | Engagement lead + Head of Ops | Week 1 (go/no-go gate) | Agent reads historical context, assumes data exists. See D#3 data assumptions and go/no-go gate. |
| CFO wants a year-1 dollar number for the board deck | H × M | High (active) | Engagement lead | Monday week 0 | Operational metrics + illustrative contribution model in D#1; replaced with real MedFlex inputs after Monday's Head-of-Ops conversation; revised number to CFO before board prep. |
| Email-only assumption wrong (portal volume significant) | M × M | Medium | FDE + Head of Ops | Week 0 | Confirm with Head of Ops before D#4. |
| 8-week target slips on instrumentation | L × H | Medium | FDE | Ongoing | Week 1 ships a thin live increment (intake parser on real ServiceNow records). Baselines captured by the running system, no separate measurement week. |
| ICU slice is the wrong slice | M × M | Medium | FDE + Head of Ops | Monday EOD week 0 | Five criteria + five questions for Head of Ops (see Slice section). Alternative slices ready. |
| Assumed workflow order is wrong | M × L | Low | FDE + Head of Ops | Week 0 | D#3 glossary flags this. State machine, lock point, KPI target all adapt. |
| HIPAA / patient data handling not confirmed | M × H | High (regulatory blocker) | Compliance + Legal + FDE | Week 0 (per D#7 §7.3) | Engagement pauses if unresolved by start of week 1. |

## v1, what we'll build

**One thing: matching, in two modes. Same engine.**

1. **Planned matching.** Hospital sends a shift request. Agent reads it, ranks eligible nurses with reasoning, surfaces shortlist to coordinator. Coordinators in the loop early; autonomy grows on the trust ramp (D#3). Main volume.

2. **Urgent re-matching.** Nurse no-shows or cancels late. Same engine. Less time, fewer choices, different oversight thresholds.

Plus: nurses say yes explicitly, conditional on confirming the no-reply finding (Decision 2 in D#3).

## The slice

**The slice is locked Monday EOD** after a 30-minute conversation with Head of Operations (offered by Marcus in his Friday pushback). The pre-discovery hypothesis was ICU + 2 hospitals (drawn from healthcare industry norms: high-volume, high-margin, uniform credentials), but that's a starting hypothesis, not a decision.

**Five criteria for the slice decision** (applied Monday after Head of Ops conversation):

1. **Volume**: at least ~15 fills/day on the slice, so mismatch and no-show baselines are statistically meaningful by week 4.
2. **Hospital partners**: 2 hospitals willing to participate AND with ≥12 months of MedFlex history (so the agent has historical acceptance patterns to reason over).
3. **Coordinator depth**: at least one experienced coordinator familiar with the slice, as the calibration signal for the trust ramp.
4. **Manageable credential complexity**: avoid specialties with high state-by-state credential variance in v1.
5. **Visible impact at week 6**: material enough that "the slice works" reads as business progress before Marcus's board update.

**Five questions for Head of Ops in 30 min:** fills/day by specialty; which 2 hospitals would participate with 12+ months of history; deepest-coordinator-by-specialty; historical acceptance/rejection data completeness; specialties or hospitals to avoid (politically, technically, contractually).

Candidate slices: **ICU** (industry-norm pick); **Med-Surg** (broader pool, simpler credentials, lower volatility); **Telemetry** (mid-complexity, steady volume); **single hospital + multiple specialties** (if cross-hospital signal is weaker than cross-specialty consistency). Final choice in writing by Monday EOD with the reasoning.

## Out of scope (in v1)

The list below is partly shaped by the two prior AI failures: no user-facing UI (the chatbot lesson) and no learned recommender at all in v1 (the recommendation-engine lesson). The omissions are pre-emptive, not accidental.

| Out | Why |
|---|---|
| Compliance automation | In engagement scope but Marcus and the operational team both signalled it stays a separate process; we honor that. Agent reads credential expiry as a precondition, doesn't verify. |
| Hospital portal or chatbot | Hospitals rejected the chatbot. Email is the channel. |
| Nurse-facing app | Out of v1 engagement scope. Not the bottleneck. |
| Pricing engine | Out of v1 engagement scope. |
| Cross-agency nurse dedup | Industry problem. Not soluble in 8 weeks. Guardrail: if no-show driver analysis shows this dominates past v1 baseline, response is operational (Decision 2's same-day re-check ping pattern), not architectural. Tracked in no-show driver diagnosis. |
| CE renewal automation | Out of v1 engagement scope. |
| Coordinator restructuring | HR question, not a build question. |
| Quality scoring rebuild | Bigger initiative on its own. |
| Sales-side contract optimisation | Owned by Legal/Sales. |

Open questions for Head of Ops are in D#1.

## Week 0: before kickoff (the 5 days that gate week 1)

Week 1 ships the parser live (per D#6). For that to be safe, five conversations have to happen before. Each has a named owner, an answer-needed-by date, and a downstream consequence if it doesn't land.

| Day | Conversation | Owner | Answer needed for |
|---|---|---|---|
| **Monday** | 30-min slot with Head of Operations: slice lock (5 criteria + 5 questions in §slice); review the 9 open Head-of-Ops questions in D#1. | FDE + Head of Ops | Slice locked in writing by Monday EOD; baseline endpoint pinned (open Q2) before week-1 instrumentation. |
| **Monday afternoon** | CFO clarification ahead of board prep: 5 questions in D#6 §3 (net vs. gross billings, net revenue per shift, slice volume, competitive-loss rate, no-show breakdown). | Engagement lead + CFO | Revised year-1 contribution number to board deck same day. |
| **Tuesday** | Data audit with IT + Compliance: confirm hospital accept/reject records and past nurse-hospital pairings are queryable; ServiceNow API rate-limit tier; nurse profile-notes structure. | FDE + IT lead + Compliance | D#3 go/no-go gate fires Friday; pause and rescope if both high-signal sources absent. |
| **Wednesday** | HIPAA / patient-data legal review escalation (D#7 §7.3): what data leaves MedFlex's environment for LLM calls, BAA in place, audit-trail storage compliant. | Compliance + Legal + FDE | Regulatory clearance before week 1 starts (hard blocker; engagement pauses if unresolved). |
| **Thursday** | Coordinator change-comms briefings (all 8 coordinators, 30 min each or one group session): "matching specialists" role naming, how reasoning citations work, how to override, why this is not a headcount play. | Head of Ops + FDE | Coordinator buy-in by week 1; mitigates the "feel threatened" risk row above. |
| **Friday** | Integration-design close (per A12 in D#4a): endpoint URLs, auth method, request/response JSON shapes for ServiceNow + nurse DB + comms layer, specific timeout values. | FDE + engineering | D#4 spec ready for the engineering team Monday week 1. |

If the Head of Ops slice conversation slips, week 1's parser ship may slip; if CFO inputs slip, only the revised board number slips. Marcus is told the same day in either case.

## What 8 weeks looks like

Working agent on the slice. Reads emails. Ranks nurses with explicit reasoning. Coordinators in the loop early, more autonomous over time per the D#3 ramp. Time-to-hospital-submission drops measurably from ~4h to **≤2h on the nurse-first path** (tighter, **≤1h**, where workflow order allows MedFlex to submit earlier). Marcus's <1h headline is the north star; week 8 is the first measurable step toward it, not the full mile. Marcus sees the ROI signal coming.

Everything else is later phases.
