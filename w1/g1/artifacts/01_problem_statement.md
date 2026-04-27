# Artifact 1 — Problem Statement & Success Metrics

## The Business Problem

A mid-size insurance company's 12-person claims team processes 300 First Notice of Loss (FNOL) reports per day across three unstructured channels — email, phone transcript, and web form. Each report must be triaged by severity, validated against policy coverage, routed to an adjuster, and acknowledged to the claimant within 2 hours of receipt.

The process is failing on all three operational dimensions:

**1. Speed failure — 31% SLA breach rate**
93 claims per day (~23,250/year) miss the 2-hour acknowledgment window. The root cause is capacity: the team's theoretical throughput at 22 min/claim across 8-hour shifts is ~262 claims/day. At 300 claims/day, the team runs at 114.5% of capacity, with no buffer for volume spikes. Any surge — a weather event, a product recall — causes immediate queue collapse. The 31% SLA breach rate is not a quality problem; it is a structural capacity problem wearing a quality mask.

**2. Accuracy failure — 18% routing error rate**
54 claims per day (~13,500/year) arrive at the wrong adjuster. Each mis-route generates rework: the receiving adjuster identifies the error, returns the claim to the pool, a correct adjuster is reassigned, and the claimant must be re-contacted. Estimated rework cost: 25 min of specialist time per mis-routed claim plus one claimant re-contact. Root cause: routing is a manual workload-balancing step that specialists shortcut under queue pressure, and there is no system enforcement of specialization or geography rules.

**3. Capacity failure — zero headroom for volume growth**
At 300 claims/day and 22 min average handling, the team already works beyond 8-hour shift capacity. Any channel growth, line-of-business expansion, or seasonal claim spike (catastrophic weather) cannot be absorbed without either SLA degradation or headcount addition. Processing cost per claim (~$10.50 fully loaded) is unsustainable for the commodity cases that represent the majority of volume.

**Combined annual impact (estimated):**
- Labor cost: $720K–$840K/year (12 specialists, $60K–$70K fully loaded) [Inferred]
- Rework from routing errors: ~$115K–$135K/year [Calculated: 13,500 × 25 min × specialist cost/min]
- Regulatory exposure from sustained SLA non-compliance: heightened DOI scrutiny, corrective action overhead, and remediation program cost; direct per-breach fines are jurisdiction-dependent and must be validated with legal [Assumption B4]

---

## The Claimant Perspective

Filing a First Notice of Loss is not a routine transaction. The claimant has just experienced an accident, property loss, or injury. The filing moment is a moment of stress. What the claimant needs from that first interaction is not claim resolution — it is **acknowledgment**: confirmation that the claim was received, a reference number, and a named contact.

**What claimants currently experience:**
- **31% chance of no acknowledgment within 2 hours** — they do not know if their submission was received or lost. Many call the main line to check, adding inbound volume and further straining the team.
- **18% chance of wrong adjuster contact** — they are contacted by an adjuster unfamiliar with their claim type, cannot get answers, and must re-explain the situation when transferred. Retention data shows a measurable non-renewal uplift for claimants who experienced a routing error.
- **No self-service status visibility** — they cannot check where their claim is in the process without calling.

The 2-hour SLA is not primarily an internal efficiency target. It is the claimant's first signal that the insurer is responsive. Missing it at a 31% rate is a trust failure that compounds over the life of the claim relationship.

---

## The Business Perspective

**Investment mandate:**
- Achieve ≥ 95% SLA compliance (from 69%) within 12 months
- Reduce routing error rate to ≤ 2% (from 18%)
- Achieve 18-month payback on implementation cost
- Retain all 12 specialists and redeploy to complex/high-value claims only

**Three value levers:**

**Lever 1 — Labor redeployment (~$350K–$420K value, year one)**
If the agent handles 65–70% of volume autonomously (the routine, clear-coverage, low-severity claims), 12 specialists shift from commodity processing to complex-claim-only handling. At current headcount, that means each specialist's day changes from 25 mixed claims to 7–8 complex claims handled well — no net reduction in headcount, but material improvement in quality for the hard cases, and significant buffer for volume growth. 7–8 redeployed FTE-equivalents at $50K–$60K redeployment value = $350K–$420K/year.

**Lever 2 — Rework elimination (~$115K–$135K/year)**
Routing accuracy improvement from 82% to ≥ 98% eliminates ~50 mis-routed claims/day. Each eliminated rework event saves ~25 min of specialist time plus claimant re-contact.

**Lever 3 — Regulatory compliance risk reduction (material but jurisdiction-dependent)**
Achieving ≥ 95% SLA compliance removes the company from the regulatory watchlist, eliminates corrective action plan overhead, and reduces audit exposure. Financial value is jurisdiction-dependent [Assumption B4] but the directional case is unambiguous.

**Combined year-one estimate: $465K–$555K** — above any realistic implementation cost for a well-scoped V1.

**Why an AI agent is the right solution:**
The distribution of the work tells you the answer. 65–70% of FNOL claims follow predictable patterns: the text is clear, the policy is active and matched, the severity is evident, the adjuster assignment is deterministic. These claims do not require 22 minutes of specialist judgment. They require consistent rule application — which an agent does faster and more consistently than a specialist under queue pressure.

The remaining 30–35% — bodily injury, coverage disputes, high-value claims, ambiguous text — are precisely where specialist judgment is irreplaceable and where the current team is under-resourced because commodity claims consume their capacity. The agent's job is to clear the commodity volume and route complex claims to a specialist with the data already assembled.

---

## Measurable Success Criteria

### SLA Compliance
| Metric | Baseline | Year-1 Target | Measurement |
|---|---|---|---|
| Claims acknowledged within 2 hours | 69% | ≥ 95% | System timestamp: received_at → acknowledged_at |
| Agent processing time (autonomous path) | N/A | ≤ 5 min | System log: RECEIVED → ACKNOWLEDGED for autonomous claims |
| Human review handling time (complex path) | 22 min | ≤ 15 min | System log: WorkItem created → resolved |

### Accuracy Metrics
| Metric | Baseline | Year-1 Target | Measurement |
|---|---|---|---|
| Routing accuracy (correct adjuster on first assignment) | 82% | ≥ 98% | Monthly sample audit (n=200): adjuster confirmed correct by supervisor |
| Claim type classification accuracy | Unknown | ≥ 93% | Monthly labeled test set review |
| Coverage validation accuracy (false clear rate) | Unknown | ≤ 1% | Quarterly reconciliation: claims cleared by agent that subsequently raised coverage dispute |

### Operational Metrics
| Metric | Baseline | Year-1 Target | Measurement |
|---|---|---|---|
| Autonomous handling rate | 0% | ≥ 65% | System log: % of claims reaching ACKNOWLEDGED with no open WorkItem |
| Peak capacity (claims/day without SLA degradation) | ~262 | ≥ 500 | Load test during simulated volume spike |
| Specialist capacity freed for complex claims | 0% | ≥ 60% of specialist time | Time-tracking audit |

### Claimant Experience Metrics
| Metric | Baseline | Year-1 Target | Measurement |
|---|---|---|---|
| Post-FNOL CSAT score (survey, 1–5) | [Baseline to be established pre-launch] | ≥ 4.2 / 5 | Post-FNOL survey, 30-day window |
| Claimant inbound calls to check claim status (per 100 FNOL) | [Baseline to be established] | ≤ 5 calls per 100 FNOL | CRM inbound call log |
