# Artifact 1 — Problem Statement & Success Metrics

## The Business Problem

A mid-size insurance company's 12-person claims team processes 300 First Notice of Loss (FNOL) reports per day across three unstructured channels — email, phone transcript, and web form. Each report must be triaged by severity, validated against policy coverage, routed to an adjuster, and acknowledged to the claimant within 2 hours of receipt.

The process is failing on all three operational dimensions:

**1. Speed failure — 31% SLA breach rate**
93 claims per day (~23,250/year) miss the 2-hour acknowledgment window. The root cause is capacity: the team's **maximum theoretical processing capacity** at 22 min/claim across 8-hour shifts is ~262 claims/day (12 × 480 ÷ 22 = 261.8). This is a ceiling figure: it assumes 100% productive utilization — no breaks, no administrative overhead, no meeting time, no handling-time variance. At 300 claims/day, the team runs at 114.5% of this theoretical ceiling, with no buffer for volume spikes. Real operational capacity is lower than 262/day [Inferred — actual utilization rate not measured in this engagement]; the 114.5% figure is therefore a lower bound on overload severity, not an accurate measure of day-to-day strain. The real utilization rate is worse than it appears. Any surge — a weather event, a product recall — causes immediate queue collapse.

**Why the breach rate (31% = 93/day) is higher than the capacity overflow (300 − 262 = 38/day):** The 38-claim overflow represents the absolute floor — claims that cannot be processed within the shift regardless of effort. The additional 55 daily breaches arise from three compounding factors: (a) *arrival bunching* — claims do not arrive uniformly distributed; when 20 arrive in the first 45 minutes, the queue backs up even though the daily total would be manageable; (b) *handling time variance* — the 22-minute average likely masks a bimodal distribution [Inferred — not measured in this engagement; consistent with typical mixed-complexity claims work patterns]: routine claims may take 12–15 min, complex claims (bodily injury, coverage dispute) 35–45 min; a single complex claim in a full queue can delay the next 2–3 routine claims past their SLA windows [Inferred — modelled from queue-saturation dynamics; specific number depends on queue depth at the moment of the delay]; (c) *channel-switching overhead* — specialists manually monitor three separate inbound channels, adding 3–5 min of context-switching per transition that is not captured in per-claim time estimates. The 31% breach rate is not a quality problem; it is a structural capacity problem wearing a quality mask.

**2. Accuracy failure — 18% routing error rate**
54 claims per day (~13,500/year) arrive at the wrong adjuster. Each mis-route generates rework: the receiving adjuster identifies the error, returns the claim to the pool, a correct adjuster is reassigned, and the claimant must be re-contacted. Estimated rework cost: 25 min of specialist time per mis-routed claim plus one claimant re-contact. Root cause: routing is a manual workload-balancing step that specialists shortcut under queue pressure, and there is no system enforcement of specialization or geography rules.

**3. Capacity failure — zero headroom for volume growth**
At 300 claims/day and 22 min average handling, the team already works beyond 8-hour shift capacity. Any channel growth, line-of-business expansion, or seasonal claim spike (catastrophic weather) cannot be absorbed without either SLA degradation or headcount addition. Processing cost per claim (~$10.50 fully loaded [Calculated: $720K–$840K annual labor ÷ ~75,000 annual claims at 300/day × 250 working days — assumes operating-day-only intake; Inferred — scenario does not confirm whether 300/day is a calendar-day or operating-day figure. Calendar-day intake (300 × 365 = 109,500/year) would give ~$6.60–$7.70/claim and higher utilisation in the capacity model. This spec uses operating-day throughout the labor analysis; the agent's 24/7 LLM cost in Artifact 3 correctly uses 365 days. Client must confirm intake distribution before finalising the business case]) is unsustainable for the commodity cases that represent the majority of volume.

**Combined annual impact (estimated):**
- Current fully-loaded labor cost: $720K–$840K/year (12 specialists, $60K–$70K fully loaded) [Inferred] — this is the cost being inefficiently allocated, not a cost that disappears; specialists are retained and redeployed
- Rework from routing errors: ~$115K–$135K/year [Calculated: 13,500 × 25 min × specialist cost/min]
- Regulatory exposure from sustained SLA non-compliance: heightened DOI scrutiny, corrective action overhead, and remediation program cost; direct per-breach fines are jurisdiction-dependent and must be validated with legal [Assumption B4]

---

## The Claimant Perspective

Filing a First Notice of Loss is not a routine transaction. The claimant has just experienced an accident, property loss, or injury. The filing moment is a moment of stress. What the claimant needs from that first interaction is not claim resolution — it is **acknowledgment**: confirmation that the claim was received, a reference number, and a named contact.

**What claimants currently experience:**
- **31% chance of no acknowledgment within 2 hours** — they do not know if their submission was received or lost. Many call the main line to check, adding inbound volume and further straining the team.
- **18% chance of wrong adjuster contact** — they are contacted by an adjuster unfamiliar with their claim type, cannot get answers, and must re-explain the situation when transferred. Being forced to re-explain a stressful incident to a second unfamiliar adjuster is a trust-destroying experience that is plausibly linked to non-renewal based on general service-quality literature [Inferred — no company-specific retention data was provided in this engagement].
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

**Lever 1 — Capacity redeployment (conditional value; not a cash saving)**
If the agent handles 65–70% of volume autonomously, 7–8 FTE-equivalents of specialist time are freed from commodity processing (65–70% × 12 = 7.8–8.4, rounded conservatively). That freed capacity is real. Whether it converts to financial value depends entirely on what the organisation does with it — the capacity itself is worth nothing until it is applied.

Value materialises only if one or more of the following is true:

- **Hiring is avoided:** the company was about to add headcount to handle volume growth. Freed capacity absorbs that growth instead. Value = avoided salary + overhead per hire [Inferred — no planned headcount data provided; must be confirmed with operations].
- **Overtime is eliminated:** specialists are currently working paid overtime to clear the daily backlog. Freed capacity removes the overtime requirement. Value = current annual overtime cost [Inferred — not stated in scenario; requires payroll data].
- **Complex claim outcomes improve measurably:** specialist time redirected from commodity to complex claims reduces coverage disputes, adjuster reassignments, or litigation rates. Value = avoided downstream cost [Inferred — no outcome data provided; requires historical claims analysis].
- **Volume growth is absorbed:** business growth of 20–30% in claim volume is absorbed without additional headcount. Value = hiring cost avoidance on future growth [Inferred — no growth forecast provided].

**No single cash value is assigned to Lever 1 in this document.** A number would require at least one of the above conditions to be confirmed with supporting data. Presenting a dollar figure without that confirmation is consultant math, not financial analysis.

**Lever 2 — Rework elimination (~$115K–$135K/year in time-cost avoided)**
Routing accuracy improvement from 82% to ≥ 98% eliminates ~50 mis-routed claims/day (~13,500/year). Each avoided rework event frees 25 min of specialist time plus one claimant re-contact [Calculated: 13,500 × 25 min × specialist cost/min, at $60K–$70K fully loaded (~$0.48–$0.56/min) = $115K–$135K/year].

This is opportunity-cost arithmetic, not direct cash outflow — the salary is paid regardless. The cash value is real only if the freed time enables productive output that would otherwise require additional cost (more claims processed, backlog cleared, overtime avoided). However, unlike Lever 1, the direction is unambiguous: time currently wasted on avoidable rework disappears. That is the most defensible element of the business case.

**Lever 3 — Regulatory compliance risk reduction (directional; not quantifiable here)**
Achieving ≥ 95% SLA compliance substantially reduces the DOI audit exposure that sustained non-compliance creates and eliminates any active corrective action plan overhead [Inferred — must be validated with legal/compliance; see Assumption B4]. Financial value is jurisdiction-dependent and cannot be responsibly estimated without state-level regulatory analysis.

**Honest summary of the business case:**

| Value type | Amount | Confidence |
|---|---|---|
| Rework elimination (time-cost proxy) | $115K–$135K/year | Calculable from stated inputs; cash realisation conditional on productive redeployment |
| Capacity redeployment | Not quantified | Real capacity freed; dollar value requires confirmation of hiring avoidance, overtime, or growth data |
| Regulatory risk reduction | Not quantified | Directionally strong; jurisdiction-dependent |

The business case is strong without a padded combined total. The rework elimination alone — $115K–$135K/year in avoidable specialist time — is a concrete, defensible number. The capacity value is the upside that makes this a compelling investment, but it must be validated against actual operational data before appearing in a financial approval document.

**Why an AI agent is a strong candidate solution — and what must still be validated:**
The work distribution is a necessary condition for considering an AI agent, not a sufficient one. 65–70% of FNOL claims reportedly follow predictable patterns: the text is clear, the policy is active and matched, the severity is evident, the adjuster assignment is deterministic [Inferred — not measured; this estimate is the premise of the business case, not a validated finding]. Claims in this category require consistent rule application rather than specialist judgment — which an agent can do faster and more consistently than a specialist under queue pressure.

The remaining 30–35% — bodily injury, coverage disputes, high-value claims, ambiguous text — are precisely where specialist judgment is irreplaceable. The agent's proposed role is to clear the commodity volume and route complex claims to a specialist with the data already assembled.

**However, the distribution of work alone does not establish that this solution is viable.** Before committing to the agent approach, the following feasibility questions must be answered — each represents a risk that could invalidate or significantly constrain the design:

- **Data quality:** Are historical FNOL inputs clean enough for NLP extraction to reach the 0.90 confidence threshold? If the actual low-confidence parse rate is 40% rather than 25%, the FIELD_COMPLETION queue dominates and throughput gains disappear.
- **Integration feasibility:** Do the legacy policy admin SOAP operations (GetPolicyByNumber, CheckExclusions) actually exist and perform within 10-second timeout tolerances? An undocumented legacy system is the single most common source of AI project delay [Assumptions A1, A2, A3].
- **Claims language complexity:** Are claimants' self-reported incident descriptions sufficiently structured for classification? Regional dialects, multi-language submissions, dictated transcripts, and non-native speakers can all degrade NLP accuracy significantly — not modelled here.
- **Policy rules codification:** Can the legacy coverage type codes be deterministically mapped to the six-class claim_type enum? If coverage logic requires underwriting judgment rather than a lookup table, CV-001 cannot be automated [Assumption A2].
- **Compliance constraints:** Does any operating state's insurance regulation prohibit or restrict automated acknowledgment, automated routing, or NLP-based coverage assessment beyond the coverage-denial constraint already identified? [Assumption B4].
- **Hallucination and extraction error risk:** The NLP extraction model can confidently produce a wrong answer. The 0.90 confidence threshold is a calibration assumption, not a validated floor — it must be tested against actual historical FNOL data before go-live.
- **Customer communication controls:** Templated acknowledgments must be reviewed by legal and compliance before use. The template content (including what can and cannot be promised in an INTERIM acknowledgment) is a deployment dependency, not a builder decision [Assumption C3].
- **Exception rate reality:** If the true rate of LOW/MEDIUM, non-bodily-injury, clear-coverage claims is closer to 45% than 65%, the autonomous handling rate misses its target and the business case weakens materially.

The agent approach is the right hypothesis given the problem profile. It is not yet a confirmed answer. The spec that follows is written to make these feasibility questions answerable — not to assume they are already resolved.

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
| Peak capacity (claims/day without SLA degradation) | ~262 (theoretical max; real operational capacity lower) | ≥ 500 | Load test during simulated volume spike |
| Specialist capacity freed for complex claims | 0% | ≥ 60% of specialist time | Time-tracking audit |

### Claimant Experience Metrics
| Metric | Baseline | Year-1 Target | Measurement |
|---|---|---|---|
| Post-FNOL CSAT score (survey, 1–5) | [Baseline to be established pre-launch] | ≥ baseline + 0.5 points (e.g., if baseline is 3.4, target is ≥ 3.9) | Post-FNOL survey, 30-day window |
| Claimant inbound calls to check claim status (per 100 FNOL) | [Baseline to be established] | ≤ 5 calls per 100 FNOL | CRM inbound call log |
