# D#2 — Engagement intake & scope

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
| CFO (implied) | Year-1 numbers | Likely Marcus pushback |

## Constraints

- Marcus wants ROI signal in 8 weeks.
- Email is sticky (hospitals rejected the chatbot).
- No layoff framing (Marcus said he'd grow the team if the business grows).
- Trust is low after two failures — output has to be explainable.
- Compliance stays separate — the coach hammered this in the debrief.

## Risks

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

## v1 — what we'll build

**One thing — matching — in two modes. Same engine.**

1. **Planned matching.** Hospital sends a shift request. Agent reads it, ranks eligible nurses with reasoning, surfaces shortlist to coordinator. Coordinators in the loop early; autonomy grows on the trust ramp (D#3). Main volume.

2. **Urgent re-matching.** Nurse no-shows or cancels late. Same engine. Less time, fewer choices, different oversight thresholds.

Plus: nurses say yes explicitly — conditional on confirming the no-reply finding (Decision 2 in D#3).

## The slice

Working hypothesis: **ICU on 2 hospitals.** Reasons (from industry norms, not yet confirmed with MedFlex):

- High volume + high margin, so speed pressure is sharpest
- Credential complexity is uniform within ICU
- Two hospitals — enough to see hospital-specific reasoning vs one-hospital coincidence
- Small enough to tune and stay close

Our guess. Head of Ops may steer us. Alternatives ready: Med-Surg, Telemetry, or one hospital + multiple specialties.

## Out of scope (in v1)

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

## What 8 weeks looks like

Working agent on the slice. Reads emails. Ranks nurses with explicit reasoning. Coordinators in the loop early, more autonomous over time per the D#3 ramp. Time-to-hospital-submission drops measurably, trajectory toward Marcus's <1h target where workflow order makes that mechanically possible. Marcus sees the ROI signal coming.

Everything else is later phases.
