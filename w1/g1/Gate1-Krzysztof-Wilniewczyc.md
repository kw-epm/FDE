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

---

# Artifact 2 — Delegation Analysis

## The Core Question

Which parts of FNOL processing should be fully agentic, which should be agent-led with human oversight, and which must remain human-led? This is not a question of what AI can do — it is a question of what should be delegated, given the regulatory environment, liability exposure, and specific risk profile of this insurer.

---

## Hard Constraints (Non-Negotiable for this spec draft)

The scenario does not explicitly provide these boundaries. They are design constraints used in this draft and must be validated with the client before build:

**C1 — Coverage denial requires human decision.**
The agent cannot deny coverage or communicate a denial to a claimant. If coverage is excluded or disputed, the agent flags and holds. A specialist confirms before any denial is communicated. Basis: conservative legal-control assumption pending legal sign-off.

**C2 — Bodily injury claims require human oversight before routing.**
Any claim where bodily injury is mentioned — regardless of estimated loss amount — requires supervisor review before adjuster assignment. Basis: conservative litigation-risk assumption pending operations/legal validation. The agent classifies and surfaces data; it does not route autonomously.

**C3 — High-value claims (≥ $50,000 estimated loss) require human confirmation of routing.**
The $50,000 threshold is a working default. At this threshold, a routing error has material financial and relationship consequences that justify the confirmation step [Assumption B1 — pending formal policy confirmation].

These three constraints define the floor. Every other boundary is a design choice.

---

## Delegation Framework

| Label | Meaning |
|---|---|
| **[Agent — Autonomous]** | Agent decides and acts; no human required before the action completes |
| **[Agent — Log & Monitor]** | Agent decides and acts; decision logged for human audit; human can override retroactively |
| **[Agent — Flag & Hold]** | Agent makes a recommendation and holds the claim; human confirms before action |
| **[Human — Decide]** | Agent gathers and presents data; human makes the call |

---

## Decision-by-Decision Analysis

### 1. Claim Intake and Field Extraction

**Decision:** Extract structured fields (policy number, claimant contact, claim type, incident date, estimated loss, bodily injury mention) from unstructured text.

**Sub-decision A — High-confidence extraction (all required fields, parse confidence ≥ 0.90):**
**Delegation:** **[Agent — Autonomous]**
**Justification:** NLP extraction on structured claim inputs (web form, standard email) achieves high accuracy for the primary fields. The risk of an autonomous extraction error is bounded: if the policy number is slightly wrong, the policy lookup fails and the error surfaces immediately. If the claim type is wrong, it is corrected at the coverage validation step. The agent is extracting, not deciding — the downstream modules catch extraction errors.

**Sub-decision B — Low-confidence extraction (parse confidence < 0.90 or required field missing):**
**Delegation:** **[Agent — Flag & Hold]**
**Justification:** A missing or uncertain policy number, claimant contact, or claim type cannot be safely inferred — the error would propagate through every downstream step. Better to surface the gap immediately and ask a specialist to complete the field than to continue with uncertain data.

**Why not require human review of all extractions?** The high-confidence path is the majority (~70–75% of claims). Requiring human review on every extraction eliminates the primary throughput gain of the agent. The confidence threshold is the control.

---

### 2. Policy Lookup

**Decision:** Query the legacy policy admin SOAP system with the extracted policy number.

**Sub-decision A — Policy found, status active:**
**Delegation:** **[Agent — Autonomous]**
**Justification:** This is a deterministic database lookup. The result is either a policy record or it is not. No judgment required. Automating this step alone eliminates a material portion of per-claim handling time across all successful lookups [Inferred — no step-level timing breakdown of the 22-minute average was provided in this engagement; the 2–4 minute estimate reflects typical manual legacy-SOAP lookup effort but must be validated against specialist time-tracking data].

**Sub-decision B — Policy not found:**
**Delegation:** **[Agent — Flag & Hold]**
**Justification:** A missing policy record can mean: wrong policy number extracted, billing number provided instead of policy number, or genuinely no policy (coverage question). The agent cannot determine which — this requires specialist verification.

**Sub-decision C — SOAP system failure after retries:**
**Delegation:** **[Human — Decide]** (IT + specialist)
**Justification:** A failed integration cannot be worked around by the agent. The claim is held and IT alerted. The specialist performs manual lookup while IT resolves the SOAP issue. Processing does not proceed on unverified coverage.

---

### 3. Coverage Validation

**Decision:** Does this claim type fall within the policy's covered perils? Are there applicable exclusions?

**Sub-decision A — Clear coverage match (claim type in covered perils, policy active, no exclusion match):**
**Delegation:** **[Agent — Log & Monitor]**
**Justification:** This is a structured rule application: claim_type ∈ coverage_types AND policy_status = ACTIVE AND incident_date ∈ [effective_date, expiration_date] AND no exclusion text similarity above threshold. The logic is fully encodable. A 10% random sample is reviewed by supervisors daily. False-clear events (the most dangerous failure mode — agent clears coverage when it should not) are tracked as the primary quality metric for this module.

**Sub-decision B — Possible exclusion match (NLP similarity ≥ 0.75 between exclusion clause text and incident description):**
**Delegation:** **[Agent — Flag & Hold]**
**Justification:** Exclusion clause interpretation is genuinely ambiguous at the margin. An exclusion clause that says "damage caused by flooding" applied to a claim that says "water came through the roof during a storm" requires a specialist to adjudicate. The agent can flag the similarity and present the clause text; it cannot make the call.

**Sub-decision C — Coverage type not in policy (clear exclusion):**
**Delegation:** **[Agent — Flag & Hold]** → **[Human — Decide]**
**Justification:** Confirmed hard constraint (C1). The agent sets coverage_status = EXCLUDED and surfaces it for specialist review. The specialist confirms and initiates the denial process. The agent never communicates a denial to the claimant directly.

**Sub-decision D — Policy lapsed or cancelled:**
**Delegation:** **[Agent — Flag & Hold]** → **[Human — Decide]**
**Justification:** Same constraint as C1. A lapsed policy does not automatically mean denial — there may be grace periods or reinstatement paths. A specialist must review.

**Sub-decision E — SOAP response returns policy with empty or malformed coverage_types_list:**
**Delegation:** **[Agent — Flag & Hold]**
**Justification:** An empty coverage list could mean: the policy genuinely has no covered perils (unusual — likely a data error), the SOAP response was truncated, or the coverage type mapping [Assumption A2] failed to resolve any codes. The agent cannot distinguish these cases. Treating an empty list as "no coverage" (EXCLUDED) risks wrongly denying a valid claimant; treating it as "coverage unknown" (DISPUTED) is the safer default. Agent sets coverage_status = DISPUTED, creates COVERAGE_REVIEW WorkItem with note "Policy returned empty coverage_types_list — possible SOAP data error or unmapped coverage codes", and holds for specialist review.

**Sub-decision F — CV-002 SOAP system failure (CheckExclusions unavailable):**
**Delegation:** **[Human — Decide]** (IT + specialist)
**Justification:** Same reasoning as PL-001 SOAP failure (Section 2, Sub-decision C). If the exclusion-check operation is unavailable, the claim cannot proceed with unverified exclusion status. Failing open — treating an unavailable exclusion check as "no exclusions found" and proceeding — would produce a coverage_status = CONFIRMED record that the assigned adjuster and downstream systems treat as authoritative, even though the exclusion check never ran. The claim halts; IT is alerted; a specialist performs manual exclusion review once IT resolves the SOAP issue.

**Why not require human review of all coverage validations?** Because the clear-coverage path (active policy, matching coverage type, no exclusion trigger) is the majority of claims, and the rule is fully encodable. The risk is a false clear — which is caught in the daily audit. The risk of requiring human review of all coverage validations is that the team bottleneck shifts from commodity processing to commodity review, with no SLA improvement.

---

### 4. Severity Classification

**Decision:** Assign a severity level (LOW / MEDIUM / HIGH / CRITICAL) to the claim.

**Sub-decision A — LOW or MEDIUM severity (no bodily injury, estimated loss < $50,000, no litigation flag):**
**Delegation:** **[Agent — Autonomous]**
**Justification:** Severity classification at LOW and MEDIUM is a structured scoring function based on claim type, estimated loss, and presence of bodily injury. The codifiability is high. The consequence of error at LOW/MEDIUM is a routing misassignment — which is caught by the routing validation step. Note: this means the severity classification and routing accuracy metrics must be tracked jointly.

**Sub-decision B — HIGH or CRITICAL severity (any of: bodily injury mentioned, estimated loss ≥ $50,000, liability involving multiple parties):**
**Delegation:** **[Agent — Flag & Hold]**
**Justification:** Two hard constraints apply here (C2 and C3). These are the claims where a severity mis-classification has the highest consequences: wrong adjuster type, potential litigation exposure, regulatory reporting obligation. The agent presents its scoring and the data it used; a supervisor confirms before routing.

**Why draw the boundary at HIGH?** Because below HIGH, severity classification is a structured data problem. At HIGH and above, the stakes of an error — litigation, regulator, large financial loss — justify the confirmation step. The cost of the confirmation (supervisor review, ~3–5 min) is negligible relative to the consequence of a mis-classified HIGH claim being routed autonomously to a general adjuster.

---

### 5. Adjuster Routing

**Decision:** Assign a specific adjuster to the claim.

**Sub-decision A — Standard routing (LOW/MEDIUM severity, clear coverage, adjuster available):**
**Delegation:** **[Agent — Autonomous]**
**Justification:** Adjuster assignment at LOW/MEDIUM is a matching function: claim_type × region × workload, with explicit rules for tie-breaking. This is the primary source of current routing errors (18%) because specialists manually shortcut the matching under queue pressure. An agent applying the rules consistently every time eliminates the shortcut failure mode.

**Sub-decision B — HIGH/CRITICAL severity or high-value (supervisor confirmed in prior step):**
**Delegation:** **[Agent — Flag & Hold]** (supervisor confirmed routing)
**Justification:** These claims require a specialist adjuster. The agent proposes the assignment (based on specialization and availability); the supervisor who reviewed severity confirms or adjusts the routing choice before the claim is sent.

**Sub-decision C — No eligible adjuster (all specialists at queue limit):**
**Delegation:** **[Human — Decide]**
**Justification:** Queue overflow requires a supervisor judgment call: extend a queue, reassign across teams, or escalate to the claims manager. The agent cannot make this call — it does not have the context on team priorities, adjuster capacity negotiations, or business relationships that inform overflow decisions.

---

### 6. Claimant Acknowledgment

**Decision:** Send acknowledgment to the claimant.

**Delegation:** **[Agent — Autonomous]** — always, for all claims
**Justification:** Acknowledgment is the claimant's primary SLA deliverable. It is templated — reference number, adjuster name (or "an adjuster will contact you" if not yet assigned), next-contact timeline by severity. No judgment is required in the acknowledgment itself. Any delay for human approval defeats the purpose.

**Critical design point:** Acknowledgment is decoupled from routing completion. If a claim is in human review (AWAITING_SEVERITY_REVIEW or AWAITING_ROUTING_OVERRIDE), the agent sends the acknowledgment anyway — using the template variant that acknowledges receipt and commits to adjuster contact within the severity-appropriate window, without naming an unconfirmed adjuster. The claimant is never left waiting for a human review to complete before they hear from the insurer.

---

### 7. Audit Logging

**Delegation:** **[Agent — Autonomous]** — always
**Justification:** Every state transition, human decision, and agent action must be logged immutably. This is a compliance requirement. No human review of logging is necessary; logging happens as a side effect of every operation.

---

## Summary: Autonomous vs. Human Workload

| Workload type | Estimated % of volume | Delegation |
|---|---|---|
| Clear text, active policy, confirmed coverage, LOW/MEDIUM severity | ~55–65% | Agent — Autonomous |
| Clear path, logged for daily audit | ~8–12% | Agent — Log & Monitor |
| Low-confidence parse or missing fields | ~8–12% | Agent — Flag & Hold → human completes |
| Coverage dispute / possible exclusion | ~5–8% | Agent — Flag & Hold → specialist reviews |
| HIGH/CRITICAL severity or high-value | ~8–12% | Agent — Flag & Hold → supervisor confirms |
| Bodily injury | ~3–5% | Agent — Flag & Hold (always, C2) |
| Coverage denial | ~2–3% | Human — Decide (C1) |
| SOAP failure / no adjuster available | ~1–2% | Human — Decide |

**Net autonomous rate: ~63–77%** — consistent with the scenario's implied 65–70% routine case estimate.

**Note on category overlap:** The rows above are not mutually exclusive. A bodily injury claim is also counted in HIGH/CRITICAL severity; a coverage dispute claim may also have had a low-confidence parse. The percentages are component estimates, not additive slices — summing them exceeds 100% because a single claim can fall into multiple categories. The net autonomous rate (~63–77%) is the fraction of claims that exit all modules without a human WorkItem, accounting for overlap. The categories are useful for estimating specialist workload by type, not for computing a coverage-exhaustive percentage breakdown.

---

## Why These Boundaries Are Drawn Here

**The coverage denial boundary** sits at human-always as a conservative legal-control assumption pending legal validation — this is not a "feels like a human decision" call. Any spec that allows the agent to deny coverage without legal sign-off is high risk.

**The bodily injury boundary** sits at human-always (pre-routing) because the litigation exposure of routing a bodily injury claim to the wrong adjuster — or to a general adjuster who mishandles the initial contact — outweighs the throughput cost of a supervisor confirmation. This is a conservative design constraint and should be validated with operations/legal owners. **It may be relaxed in V2:** if operations validates that self-reported minor injuries (no hospitalisation, no third party) can be auto-routed to a bodily-injury-qualified adjuster, the C2 constraint becomes a severity sub-threshold rather than a binary flag. The current spec treats it as binary pending that validation [Assumption B2].

**The $50,000 boundary** sits at flag-and-hold because at this financial level, a routing error has a material margin consequence and the cost of a 3–5 minute supervisor confirmation is negligible by comparison. This is a working assumption pending formal policy documentation.

**The acknowledgment boundary** is drawn at always-autonomous because decoupling acknowledgment from routing completion is the primary mechanism by which the 31% SLA breach rate gets resolved. Claimants cannot wait for human review to complete before they are acknowledged.

---

# Artifact 3 — Agent Specification

## Agent Identity

**Name:** FNOL Processing Agent (FPA)
**Version:** 1.0
**Purpose:** Automate the intake parsing, policy lookup, coverage validation, severity classification, adjuster routing, and claimant acknowledgment of First Notice of Loss reports. Reduce per-claim handling time for routine cases, eliminate manual routing errors, and guarantee claimant acknowledgment within the 2-hour SLA.

**Implementation scope note:** This spec defines behaviour — what the agent decides, when it escalates, what it writes to which systems, and what constitutes a correct vs. incorrect output. Technology choices (language, framework, NLP model, deployment platform) are the builder's decision and are intentionally not prescribed here.

**Scope (V1):**
- FNOL reports received via email, phone transcript (post-call upload), or web form
- Claims against personal and commercial lines policies in the legacy policy admin system
- Integration with: Salesforce CRM (REST), legacy policy admin system (SOAP), document management system (REST)
- Single operating environment (one claims centre)

**Out of scope (V1):**
- In-call real-time transcription and processing (phone transcripts are post-call uploads)
- Claims amendment or supplemental FNOL processing
- Coverage denial letter generation
- Adjuster-facing workflow management (downstream of routing)
- Multi-site deployment
- Claimant portal status updates

---

## Configuration Parameters

These values are set at deployment and adjustable by the claims operations team without code changes. **All defaults below are initial build estimates with no historical data basis; every threshold must be calibrated against Phase 0 shadow mode data before Phase 1 go/no-go [Assumption D5].**

| Parameter | Default | Description |
|---|---|---|
| `HIGH_VALUE_THRESHOLD` | $50,000 | Estimated loss above which is_high_value = true |
| `PARSE_CONFIDENCE_THRESHOLD` | 0.90 | Minimum field confidence for autonomous processing |
| `EXCLUSION_SIMILARITY_THRESHOLD` | 0.75 | NLP cosine similarity above which exclusion match is flagged |
| `MAX_ADJUSTER_QUEUE_SIZE` | 15 | Open claims count above which adjuster is excluded from assignment |
| `SLA_AT_RISK_BUFFER_MINUTES` | 30 | Minutes before sla_deadline at which AT_RISK alert fires |
| `SERIAL_CLAIMANT_WINDOW_DAYS` | 365 | Lookback window for prior claims count (fraud signal) |
| `SERIAL_CLAIMANT_THRESHOLD` | 5 | Prior claims count above which SERIAL_CLAIMANT signal fires |
| `DUPLICATE_WINDOW_MINUTES` | 10 | Time window for potential duplicate FNOL detection |

---

## Data Model

### Entity: Claim
```
Claim:
  id: UUID, primary key, immutable, generated on receipt
  received_at: ISO 8601 timestamp, UTC, immutable
    — SLA clock starts here; set at the moment the raw input enters the system,
      NOT at the start of parsing
  source_channel: enum [EMAIL, PHONE_TRANSCRIPT, WEB_FORM], required
  raw_input_document_id: string, FK to DMS document (stored in IN-001), nullable; required when DMS store succeeds, null only when DMS store fails and raw_input is held in ephemeral memory for retry
  source_message_id: string, max 500 chars, nullable; inbound deduplication key: EMAIL = MIME Message-ID, PHONE_TRANSCRIPT = upload session ID, WEB_FORM = form submission token; null for channels that provide no deduplication key
  processing_status: enum [
    RECEIVED,
    PARSING,
    AWAITING_FIELD_COMPLETION,
    AWAITING_DUPLICATE_REVIEW,
    POLICY_LOOKUP,
    COVERAGE_VALIDATION,
    AWAITING_COVERAGE_REVIEW,
    SEVERITY_SCORING,
    AWAITING_SEVERITY_REVIEW,
    ROUTING,
    AWAITING_ROUTING_OVERRIDE,
    ACKNOWLEDGED,
    COMPLETED,
    HALTED
  ], required, default RECEIVED
  
  State machine:
    RECEIVED → PARSING                       (immediately on receipt)
    PARSING → AWAITING_FIELD_COMPLETION      (parse_confidence < PARSE_CONFIDENCE_THRESHOLD
                                              or required field missing; IN-002)
    PARSING → AWAITING_DUPLICATE_REVIEW      (duplicate candidate detected by IN-003)
    PARSING → POLICY_LOOKUP                  (all required fields, confidence ≥ threshold, no duplicate; IN-002/IN-003)
    AWAITING_FIELD_COMPLETION → POLICY_LOOKUP (human resolves FIELD_COMPLETION WorkItem)
    AWAITING_DUPLICATE_REVIEW → POLICY_LOOKUP (specialist resolves DUPLICATE_REVIEW as DISTINCT or REPLACE)
    AWAITING_DUPLICATE_REVIEW → HALTED       (specialist resolves DUPLICATE_REVIEW as MERGE; this claim discarded)
    POLICY_LOOKUP → COVERAGE_VALIDATION      (policy found, PL-001 success)
    POLICY_LOOKUP → AWAITING_FIELD_COMPLETION (policy not found — human re-verifies policy number)
    COVERAGE_VALIDATION → AWAITING_COVERAGE_REVIEW (CV-001 or CV-002 triggers hold)
    COVERAGE_VALIDATION → SEVERITY_SCORING   (coverage_status = CONFIRMED; CV-001)
    AWAITING_COVERAGE_REVIEW → SEVERITY_SCORING (specialist confirms coverage)
    AWAITING_COVERAGE_REVIEW → HALTED        (coverage denied by human)
    SEVERITY_SCORING → AWAITING_SEVERITY_REVIEW (SV-002 triggers hold: HIGH/CRITICAL or is_high_value)
    SEVERITY_SCORING → ROUTING               (LOW/MEDIUM, not high-value, no bodily injury)
    AWAITING_SEVERITY_REVIEW → ROUTING       (supervisor confirms severity and approves routing)
    ROUTING → AWAITING_ROUTING_OVERRIDE      (no eligible adjuster; RT-001)
    ROUTING → ACKNOWLEDGED                   (adjuster assigned; RT-002 complete)
    AWAITING_ROUTING_OVERRIDE → ACKNOWLEDGED (supervisor manually assigns adjuster)
    ACKNOWLEDGED → COMPLETED                 (AC-001 send confirmed)
    Any → HALTED                             (PL-001 or CV-002 SOAP failure after all retries)
    HALTED → POLICY_LOOKUP                   (supervisor manually re-queues after IT resolves SOAP_FAILURE/PL-001)
    HALTED → COVERAGE_VALIDATION             (supervisor manually re-queues after IT resolves SOAP_FAILURE/CV-002)
    — Claims halted with halt_reason starting "DUPLICATE:" are permanently halted; the resume transition is not available. Resuming a DUPLICATE-merge claim would create exactly the duplicate processing the merge was designed to prevent.

  claimant_id: string, FK to CRM Contact (on CRM contact deletion: set null), nullable until IN-002 enrichment
  policy_number: string, max 20 chars (the regex [A-Z]{2,3}-\d{6,10} yields max 14 chars; 20 allows for namespace variations), extracted by IN-002, required after AWAITING_FIELD_COMPLETION resolves
  policy_id: string, FK to PolicyAdmin (returned by PL-001), nullable until PL-001
  policy_status: enum [ACTIVE, LAPSED, CANCELLED, SUSPENDED], nullable until PL-001
  policy_effective_date: ISO 8601 date, nullable until PL-001
  policy_expiration_date: ISO 8601 date, nullable until PL-001
  claim_type: enum [AUTO_COLLISION, AUTO_THEFT, PROPERTY_DAMAGE, PROPERTY_THEFT,
    BODILY_INJURY, LIABILITY], nullable until IN-002 or human confirmation
  incident_date: ISO 8601 date, nullable until IN-002 or human confirmation
  incident_location: string, max 500 chars, nullable
  incident_state: string, 2-char ISO 3166-2 state code, nullable (derived from incident_location or extracted)
  estimated_loss_amount: decimal(12,2), nullable (null if not stated in claim text)
  is_high_value: boolean, computed: true if estimated_loss_amount >= HIGH_VALUE_THRESHOLD; read-only
  bodily_injury_flag: boolean, default false; set to true by IN-002 if bodily injury phrase detected
    or claim_type = BODILY_INJURY
  multiple_parties_flag: boolean, default false; set by IN-002
  parse_confidence: decimal(4,3), range 0.000–1.000, nullable; minimum confidence across required extracted fields
  coverage_status: enum [CONFIRMED, EXCLUDED, LAPSED, DISPUTED, DENIED],
    nullable until CV-001
    — DENIED may only be written by human WorkItem resolution; the agent MUST NOT set this value
  coverage_denial_reason: string, max 1000 chars, nullable; populated only when specialist sets
    coverage_status = DENIED
  severity_score: integer, range ≥ 1 (maximum achievable: 13), nullable until SV-001
  severity_level: enum [LOW, MEDIUM, HIGH, CRITICAL], computed from severity_score; read-only
    (LOW: 1–3, MEDIUM: 4–5, HIGH: 6–7, CRITICAL: ≥ 8; maximum achievable score is 13)
  assigned_adjuster_id: string, FK to CRM User (on CRM user deactivation: set null), nullable until RT-001 or human override
  crm_claim_id: string, FK to CRM Claim record (returned by RT-002), nullable until RT-002
  interim_acknowledged_at: ISO 8601 timestamp, UTC, nullable; set when INTERIM acknowledgment is sent; remains null if FULL was sent as the first (and only) acknowledgment
  full_acknowledged_at: ISO 8601 timestamp, UTC, nullable; set when FULL acknowledgment is sent, regardless of whether INTERIM preceded it; null until FULL ack is sent
  acknowledged_at: ISO 8601 timestamp, UTC, nullable; computed = COALESCE(interim_acknowledged_at, full_acknowledged_at); set once the first acknowledgment fires (FULL or INTERIM); SLA computation uses this field; immutable once set
  sla_deadline: ISO 8601 timestamp, UTC, computed: received_at + 2 hours, immutable
  sla_status: enum [ON_TRACK, AT_RISK, BREACHED], computed; updated by AC-002 on schedule
  halt_reason: string, max 500 chars, nullable; set when processing_status = HALTED; describes failure type (e.g., "SOAP_FAILURE: policy admin system unresponsive after 3 retries")
  created_at: ISO 8601 timestamp, UTC, immutable
  updated_at: ISO 8601 timestamp, UTC
```

### Entity: ParsedField
```
ParsedField:
  id: UUID, primary key, immutable
  claim_id: UUID, foreign key to Claim (cascade delete), required
  field_name: string, max 100 chars, required
    (one of: policy_number, claimant_name, claimant_email, claimant_phone,
     claim_type, incident_date, incident_location, estimated_loss_amount,
     bodily_injury_mentioned, multiple_parties_mentioned)
  raw_span: string, format "{start_char}-{end_char}", required
    (character range in raw_input where extraction was sourced)
  extracted_value: string, max 2000 chars, required
  confidence: decimal(4,3), range 0.000–1.000, required
  human_verified: boolean, default false
  verified_value: string, max 2000 chars, nullable
    (human's correction; null if human confirmed extracted_value unchanged)
  verified_by: UUID, foreign key to User, nullable
  verified_at: ISO 8601 timestamp, UTC, nullable
```

### Entity: WorkItem
```
WorkItem:
  id: UUID, primary key, immutable
  type: enum [FIELD_COMPLETION, DUPLICATE_REVIEW, COVERAGE_REVIEW, SEVERITY_REVIEW,
    ROUTING_OVERRIDE, SOAP_FAILURE, SYSTEM_ERROR], required
  claim_id: UUID, foreign key to Claim (restrict delete — a Claim with open WorkItems cannot be deleted), required
  status: enum [OPEN, IN_PROGRESS, RESOLVED, ESCALATED], required, default OPEN
  assigned_role: enum [SPECIALIST, SUPERVISOR, CLAIMS_MANAGER, IT_ONCALL], required
  assigned_to: UUID, foreign key to User, nullable
  content: JSON object, required (type-specific payload defined in the module that creates it)
  agent_recommendation: string, max 500 chars, nullable
  resolution: string, max 1000 chars, nullable
  resolved_by: UUID, foreign key to User, nullable
  created_at: ISO 8601 timestamp, UTC, immutable
  updated_at: ISO 8601 timestamp, UTC
  sla_deadline: ISO 8601 timestamp, UTC, required
  escalated_at: ISO 8601 timestamp, UTC, nullable

  State machine:
    OPEN → IN_PROGRESS  (user opens WorkItem in UI)
    IN_PROGRESS → RESOLVED  (user submits resolution)
    OPEN or IN_PROGRESS → ESCALATED  (sla_deadline passes; re-assigned to next role)
    ESCALATED → RESOLVED  (escalation target resolves)
```

### Specialist WorkItem UI (Scope Note)

The WorkItem JSON schemas above define what data is carried. The actual UI that specialists and supervisors see when resolving WorkItems is out of scope for this spec but is a hard delivery dependency — without a usable UI, the WorkItem SLA times (20 min FIELD_COMPLETION, 30 min SEVERITY_REVIEW) are not achievable. The UI must support at minimum:
- Raw input text + extracted fields displayed side-by-side for FIELD_COMPLETION
- Inline edit of any extracted field (including claim_type and estimated_loss_amount, regardless of agent confidence)
- Explicit enforcement of the coverage_status = DENIED restriction: the DENIED value must not be available as a direct field edit; it is only settable via COVERAGE_REVIEW WorkItem resolution
- One-click WorkItem resolution with required resolution note field
- Queue view showing all OPEN WorkItems for the logged-in role, sorted by sla_deadline ascending

UI wireframes, resolution-time targets, and accessibility requirements must be specified jointly with the build team before UI development begins [Assumption B6].

### WorkItem Assignment Algorithm
When a WorkItem is created, assigned_to is set as follows:
1. Query active Users (is_active = true) with role matching WorkItem.assigned_role
2. Exclude users with any WorkItem currently IN_PROGRESS
3. Among remaining: select user with fewest OPEN WorkItems; tie-break by earliest last_resolved_at
4. If no eligible user: set assigned_to = null; retry every 60 seconds
5. If sla_deadline - now < 25% of original SLA duration and assigned_to still null: immediately escalate to next role

### Entity: User
```
User:
  id: UUID, primary key, immutable
  name: string, max 100 chars, required
  role: enum [SPECIALIST, SUPERVISOR, CLAIMS_MANAGER, IT_ONCALL], required
  specializations: array of enum [AUTO_COLLISION, AUTO_THEFT, PROPERTY_DAMAGE,
    PROPERTY_THEFT, BODILY_INJURY, LIABILITY], required for SPECIALIST role
  coverage_regions: array of string (2-char state codes), required for SPECIALIST role
  is_active: boolean, required, default true
  last_resolved_at: ISO 8601 timestamp, UTC, nullable
```

### Entity: AuditEvent
```
AuditEvent:
  id: UUID, primary key, immutable
  claim_id: UUID, foreign key to Claim (restrict delete — audit records must not be deleted with claim), required
  event_type: enum [
    CLAIM_RECEIVED,
    PARSING_STARTED, PARSING_COMPLETED, PARSING_LOW_CONFIDENCE,
    FIELD_COMPLETED_BY_HUMAN, FIELD_OVERRIDDEN_BY_HUMAN,
    POLICY_LOOKUP_SUCCESS, POLICY_LOOKUP_NOT_FOUND, POLICY_LOOKUP_FAILED,
    COVERAGE_VALIDATED, COVERAGE_EXCLUSION_FLAGGED, COVERAGE_CONFIRMED_BY_HUMAN,
    COVERAGE_DENIED_BY_HUMAN,
    SEVERITY_SCORED, SEVERITY_CONFIRMED_BY_HUMAN, SEVERITY_OVERRIDDEN_BY_HUMAN,
    ADJUSTER_ASSIGNED, ADJUSTER_OVERRIDE_BY_HUMAN,
    ACKNOWLEDGMENT_SENT,
    WORKITEM_CREATED, WORKITEM_ASSIGNED, WORKITEM_RESOLVED, WORKITEM_ESCALATED,
    SLA_AT_RISK_ALERT, SLA_BREACHED,
    DMS_STORE_FAILED, DUPLICATE_DETECTED, DUPLICATE_REVIEW_RESOLVED, CALLBACK_TASK_CREATED,
    CLAIM_COMPLETED, CLAIM_HALTED, CLAIM_RESUMED
  ], required
  actor_type: enum [AGENT, HUMAN], required
  actor_id: string, required (agent version string or User.id)
  from_value: string, nullable
  to_value: string, nullable
  timestamp: ISO 8601 timestamp, UTC, immutable
```

Logs are immutable. Retention: 7 years (regulatory compliance). Claimant PII in audit log is stored as salted SHA-256 hashed values: SHA-256(value + claim_id) for name, email, and phone. This is **pseudonymization for audit correlation** — not anonymization. An auditor with access to the claim record can still reverse-correlate via the claim_id salt. Do not cite audit log hashes as evidence of anonymization in compliance filings. Full PII is accessible only through WorkItem and CRM UIs for authorised users.

---

## Processing Modules

### End-to-End Processing Order

Run modules in this order so that inputs exist before they are consumed:

1. **IN-001** (receipt + DMS store) → **IN-002** (parse + enrich) → **IN-003** (duplicate detection)
2. **IN-003** complete (no duplicate or duplicate resolved as DISTINCT/REPLACE) → **PL-001** (policy lookup) — only if parse passes threshold; otherwise FIELD_COMPLETION or DUPLICATE_REVIEW WorkItem holds the claim
3. **PL-001** success → **CV-001** (coverage type check) → **CV-002** (exclusion check)
4. **CV-002** complete with CONFIRMED → **SV-001** (severity scoring) → **SV-002** (escalation check)
5. **SV-002** complete → **RT-001** (adjuster assignment) → **RT-002** (CRM update)
6. **AC-001** (acknowledgment) — triggered as soon as ACKNOWLEDGED status is reachable:
   - Standard path: after RT-002
   - Hold path: immediately when claim enters AWAITING_SEVERITY_REVIEW or AWAITING_ROUTING_OVERRIDE
     (sends INTERIM acknowledgment without adjuster name)

---

### Module IN — Intake & Parsing

**IN-001 — Claim Receipt**
- Trigger: inbound claim event from any channel (email webhook, transcript upload, web form submit)
- **Idempotency check (before creating a Claim record):** check for an existing Claim with the same source_message_id received within the last `DUPLICATE_WINDOW_MINUTES`. If found: discard the incoming event (webhook retry or double-submit); do not create a second Claim; return the existing Claim.id to the caller. Idempotency keys by channel: EMAIL = MIME Message-ID header; PHONE_TRANSCRIPT = upload session ID provided by the transcript system; WEB_FORM = form submission token. Store source_message_id on the Claim record (max 500 chars, nullable for channels that provide no deduplication key).
- Action:
  1. Set Claim.received_at = current UTC timestamp (immutable; SLA clock starts)
  2. Set Claim.processing_status = PARSING
  3. Store raw_input in DMS: POST /documents with document_type = FNOL_RAW (see Integration 3)
  4. Set Claim.raw_input_document_id from DMS response (or null when DMS store fails)
  5. Set Claim.source_channel from inbound channel identifier
  6. Log CLAIM_RECEIVED to AuditEvent
- This step must complete within 30 seconds of receipt; if DMS store fails, log warning and continue (DMS store is non-blocking — see Integration 3 fallback)

**IN-002 — Field Extraction and Enrichment**
- Trigger: immediately after IN-001
- Inputs: raw_input retrieved from DMS by raw_input_document_id when not null; otherwise from in-memory fallback buffer initialized in IN-001; source_channel

**Channel pre-processing before NLP extraction:**
- EMAIL: extract body text only; strip headers and footers; if attachments present (PDF or text), append attachment text after body; images in attachments are noted in a ParsedField with field_name = "attachment_images_present" and extracted_value = "true" (for adjuster review later — not processed by V1)
- PHONE_TRANSCRIPT: look for lines prefixed "Caller:" or "Customer:" (case-insensitive); extract only those lines as the claimant's text for NLP; agent/representative lines are preserved in raw_input but excluded from field extraction
- WEB_FORM: treat named form fields as pre-extracted with confidence = 0.95; treat the free-text "incident description" field as unstructured input for NLP extraction of claim_type, bodily_injury, and multiple_parties

**Required fields and extraction rules:**
| Field | Extraction method | Required? |
|---|---|---|
| policy_number | NLP + regex (pattern: [A-Z]{2,3}-\d{6,10} or as defined by Integration 2 WSDL [Assumption A1]) | Yes |
| claimant contact | NLP entity extraction: name + (email OR phone) — at least one of email/phone required | Yes |
| claim_type | NLP classification against 6-class enum (AUTO_COLLISION, AUTO_THEFT, PROPERTY_DAMAGE, PROPERTY_THEFT, BODILY_INJURY, LIABILITY); if web form, map from form dropdown | Yes |
| incident_date | NLP date extraction; relative dates ("yesterday", "last Tuesday") resolved to absolute date using received_at | Yes |
| incident_location | NLP location extraction; derive incident_state from location string | No (nullable) |
| estimated_loss_amount | NLP numeric extraction; currency normalised to USD | No (nullable) |
| bodily_injury_mentioned | Binary NLP classification: true if any of: injury, hurt, injured, hospital, ambulance, pain, medical treatment, fracture, broken bone, broken arm, broken leg, broken rib found in text. "broken" alone is NOT a trigger — must be followed by a body-part term. | No (but flags bodily_injury_flag) |
| multiple_parties_mentioned | Binary NLP: true if: other driver, third party, another vehicle, other person involved | No (but flags multiple_parties_flag) |

**Unknown label policy (no `OTHER` enum in V1):**
- If NLP classifier outputs a label outside the 6 allowed claim types, treat claim_type as missing data.
- Set parse_confidence to 0.00 for claim_type and route to FIELD_COMPLETION (AWAITING_FIELD_COMPLETION).
- Log PARSING_LOW_CONFIDENCE with `low_confidence_fields = [{"field":"claim_type","confidence":0.00}]`.
- The system MUST NOT invent new enum values at runtime.

**Confidence and thresholds:**
- parse_confidence = minimum confidence across the 4 required fields (policy_number, claimant contact, claim_type, incident_date)
- If parse_confidence ≥ PARSE_CONFIDENCE_THRESHOLD (0.90) AND all 4 required fields present:
  - Attempt CRM enrichment: GET /contacts?email={email}&phone={phone} (see Integration 1, Endpoint 1)
  - Set claimant_id from CRM response (or leave null if not found — not a blocking failure)
  - Set processing_status = POLICY_LOOKUP; proceed to PL-001
- If parse_confidence < PARSE_CONFIDENCE_THRESHOLD OR any required field missing:
  - Create WorkItem of type FIELD_COMPLETION (see content schema below)
  - Set processing_status = AWAITING_FIELD_COMPLETION
  - Trigger AC-001 (INTERIM acknowledgment — claim received, reference number, adjuster will contact)

**FIELD_COMPLETION WorkItem content:**
```json
{
  "claim_id": "<uuid>",
  "source_channel": "<channel>",
  "raw_input_preview": "<first 500 chars of raw_input>",
  "extracted_fields": [
    { "field_name": "<name>", "extracted_value": "<value>", "confidence": 0.00, "raw_span": "0-45" }
  ],
  "missing_or_low_confidence_fields": ["<field_name>", ...],
  "agent_note": "<reason for low confidence>"
}
```
SLA: WorkItem must be resolved within 20 minutes during operating hours; unresolved after 20 minutes → escalate to SUPERVISOR.

**IN-003 — Duplicate Detection**
- Trigger: immediately after IN-002 (only if IN-002 exits with processing_status = POLICY_LOOKUP; not triggered for claims already in AWAITING_FIELD_COMPLETION)
- Inputs: Claim.policy_number, Claim.incident_date, Claim.claimant_id (or claimant email/phone SHA-256 hash if claimant_id is null)
- Action: query the FPA claim store for claims received in the past `DUPLICATE_WINDOW_MINUTES` where ALL of the following match:
  - policy_number = this claim's policy_number, AND
  - incident_date = this claim's incident_date, AND
  - claimant_id = this claim's claimant_id (if both non-null), OR SHA-256(email) or SHA-256(phone) matches if claimant_id is null
- If no match: continue to PL-001 (no action)
- If match found:
  - Log DUPLICATE_DETECTED
  - Create DUPLICATE_REVIEW WorkItem (see content schema below); set assigned_role = SPECIALIST
  - Set processing_status = AWAITING_DUPLICATE_REVIEW
  - Do NOT proceed to PL-001 until WorkItem is resolved
  - INTERIM acknowledgment: if not already sent, trigger AC-001 (INTERIM) with note that the claim is under review

**DUPLICATE_REVIEW WorkItem content:**
```json
{
  "claim_id": "<uuid of this claim>",
  "duplicate_candidate_id": "<uuid of matching claim>",
  "duplicate_candidate_received_at": "<ISO 8601>",
  "match_basis": "<policy_number+incident_date+claimant_id | policy_number+incident_date+email_hash | ...>",
  "agent_note": "Potential duplicate FNOL. Review both claims and choose a resolution."
}
```
**Resolution options (specialist selects one):**
- `MERGE`: this claim is a true duplicate; discard this claim, continue processing the earlier duplicate_candidate_id; set this claim's processing_status = HALTED with halt_reason = "DUPLICATE: merged into {duplicate_candidate_id}"
- `DISTINCT`: claims are distinct (different incidents or different parties); resume this claim from POLICY_LOOKUP; log DUPLICATE_REVIEW_RESOLVED
- `REPLACE`: this claim supersedes the earlier one (claimant resubmitted with corrections); halt duplicate_candidate_id, resume this claim from POLICY_LOOKUP; log DUPLICATE_REVIEW_RESOLVED on both claims

WorkItem SLA: 20 minutes during operating hours; escalate to SUPERVISOR after 20 minutes.

---

### Module PL — Policy Lookup

**PL-001 — Policy Lookup via SOAP**
- Trigger: processing_status = POLICY_LOOKUP
- Input: Claim.policy_number
- Action: call GetPolicyByNumber SOAP operation (see Integration 2)
- On success (policy found):
  - Populate: policy_id, policy_status, policy_effective_date, policy_expiration_date, coverage_types_list, exclusions_list; also store deductible_amount and coverage_limits (reserved for V2 adjuster-facing use — not consumed by any V1 processing module)
  - Evaluate policy_status:
    - ACTIVE: proceed to CV-001
    - LAPSED or CANCELLED or SUSPENDED: set coverage_status = LAPSED; create COVERAGE_REVIEW WorkItem; set processing_status = AWAITING_COVERAGE_REVIEW; trigger AC-001 (INTERIM)
- On PolicyFault POLICY_NOT_FOUND:
  - Do NOT set any coverage fields
  - Create FIELD_COMPLETION WorkItem with note "Policy number {policy_number} not found in policy admin system. Please verify policy number with claimant."
  - Set processing_status = AWAITING_FIELD_COMPLETION
- On SOAP fault or timeout:
  - Retry per Integration 2 retry spec
  - If all retries fail: create SOAP_FAILURE WorkItem; set processing_status = HALTED; alert IT_ONCALL

---

### Module CV — Coverage Validation

**CV-001 — Coverage Type Check**
- Trigger: processing_status = COVERAGE_VALIDATION, policy_status = ACTIVE
- Hard constraint: the agent MUST NOT set coverage_status = DENIED. Only a human via WorkItem resolution may set DENIED. The agent sets EXCLUDED, DISPUTED, or LAPSED only.
- Action:
  1. Check: claim_type ∈ policy coverage_types_list
  2. Check: incident_date ∈ [policy_effective_date, policy_expiration_date] (inclusive)
  3. If both conditions true: proceed to CV-002
  4. If claim_type NOT in coverage_types_list: set coverage_status = EXCLUDED; create COVERAGE_REVIEW WorkItem (type: coverage exclusion confirmed); set processing_status = AWAITING_COVERAGE_REVIEW; trigger AC-001 (INTERIM)
  5. If incident_date outside policy period: set coverage_status = EXCLUDED; same as above with note "Incident date outside policy coverage period"

**CV-002 — Exclusion Check**
- Trigger: CV-001 passes (claim_type in coverage_types, incident_date in period)
- Action: call CheckExclusions SOAP operation with policy_id, incident description, claim_type (see Integration 2)
- If excluded = false (no exclusion match): set coverage_status = CONFIRMED; proceed to SV-001
- If excluded = true AND any matched exclusion has similarity ≥ EXCLUSION_SIMILARITY_THRESHOLD:
  - Set coverage_status = DISPUTED
  - Create COVERAGE_REVIEW WorkItem (content includes: exclusion clause text, matched phrases, similarity score, incident description)
  - Set processing_status = AWAITING_COVERAGE_REVIEW
  - Trigger AC-001 (INTERIM)
- If CheckExclusions SOAP fails (any fault after retries): log error; create SOAP_FAILURE WorkItem; set processing_status = HALTED; alert IT_ONCALL. Do NOT proceed to severity scoring with unverified exclusion status. This is the same halt behaviour as PL-001 SOAP failure — consistent with the Artifact 2 constraint that processing does not continue on unverified coverage.

**COVERAGE_REVIEW WorkItem content:**
```json
{
  "claim_id": "<uuid>",
  "coverage_status": "<EXCLUDED|DISPUTED|LAPSED>",
  "claim_type": "<type>",
  "policy_coverage_types": ["<type>", ...],
  "incident_date": "<date>",
  "policy_effective_date": "<date>",
  "policy_expiration_date": "<date>",
  "matched_exclusions": [
    { "code": "<code>", "text": "<clause text>", "similarity": 0.00 }
  ],
  "agent_recommendation": "<confirm exclusion / confirm coverage / review required>",
  "incident_description_preview": "<first 300 chars>"
}
```
Assigned to SUPERVISOR. SLA: 45 minutes during operating hours; escalate to CLAIMS_MANAGER after 45 minutes.
**Resolution requirement:** when the supervisor resolves this WorkItem with decision = DENIED, Claim.coverage_denial_reason (max 1000 chars) is a required field — the resolution must not be submittable without it. The WorkItem UI must enforce this: the DENIED resolution path shows a mandatory free-text reason field before submission. The agent must not set coverage_denial_reason; it is only written via WorkItem resolution.

---

### Module SV — Severity Classification

**SV-001 — Severity Scoring**
- Trigger: processing_status = SEVERITY_SCORING (coverage_status = CONFIRMED or human-confirmed)
- Inputs: claim_type, estimated_loss_amount, bodily_injury_flag, multiple_parties_flag, policy_status, coverage_status, claimant_id (for prior claims query)

**Scoring rules (additive):**
| Condition | Points |
|---|---|
| estimated_loss_amount is null (unknown) | +2 |
| estimated_loss_amount < $10,000 | +1 |
| $10,000 ≤ estimated_loss_amount < $50,000 | +2 |
| $50,000 ≤ estimated_loss_amount < $150,000 | +4 |
| estimated_loss_amount ≥ $150,000 | +6 |
| bodily_injury_flag = true | +3 |
| claim_type = LIABILITY | +2 |
| multiple_parties_flag = true | +1 |
| Prior FNOL claims by this claimant_id in past SERIAL_CLAIMANT_WINDOW_DAYS ≥ SERIAL_CLAIMANT_THRESHOLD | +1 (flag for adjuster note; does not change severity level alone). **Data source:** use `prior_claims_count` from CRM Endpoint 1 (returned during IN-002 enrichment) as the authoritative value — it covers claims predating FPA deployment. The FPA's own claim store supplements this after 12 months of operation. If CRM contact not found (claimant_id = null): score 0 for this component and log absence in SEVERITY_SCORED AuditEvent. |

**Scoring note:** The null estimated_loss row scores +2 — higher than the known-small (<$10K) row at +1. Absent loss information is itself a risk signal: the claimant either has not yet assessed the damage or has chosen not to state it. Both cases warrant more cautious adjuster attention than a confidently stated small loss.

**Severity level derivation:**
- Score 1–3: LOW
- Score 4–5: MEDIUM
- Score 6–7: HIGH
- Score ≥ 8: CRITICAL

**Threshold rationale:** CRITICAL (≥ 8) requires at least two compounding risk factors, or one extreme factor combined with a secondary signal. For example: high financial loss ($150K+, +6 points) alone reaches HIGH (6); it requires bodily injury (+3) to reach CRITICAL (9). LIABILITY + bodily injury + loss ≥ $50K (+2+3+4 = 9) also reaches CRITICAL. A claim with only financial risk ($150K+, no injury, no liability) scores HIGH — which still receives human review via is_high_value = true. The boundary reflects the design assumption that compound risk is categorically more dangerous than any single factor in isolation. Pending calibration against historical outcome data [Assumption D3].

Set Claim.severity_score and Claim.severity_level. Log SEVERITY_SCORED.

**SV-002 — Escalation Check**
- If severity_level = HIGH or CRITICAL OR is_high_value = true OR bodily_injury_flag = true:
  - Create SEVERITY_REVIEW WorkItem
  - Set processing_status = AWAITING_SEVERITY_REVIEW
  - Trigger AC-001 (INTERIM) if not already triggered
- If severity_level = LOW or MEDIUM AND is_high_value = false AND bodily_injury_flag = false:
  - Proceed directly to RT-001

**SEVERITY_REVIEW WorkItem content:**
```json
{
  "claim_id": "<uuid>",
  "agent_severity_score": 0,
  "agent_severity_level": "<level>",
  "scoring_components": [
    { "condition": "<condition>", "points": 0 }
  ],
  "is_high_value": false,
  "bodily_injury_flag": false,
  "estimated_loss_amount": 0.00,
  "claim_type": "<type>",
  "agent_recommended_adjuster_specialization": "<type>",
  "agent_note": "<free text>"
}
```
Assigned to SUPERVISOR. SLA: 30 minutes during operating hours; escalate to CLAIMS_MANAGER after 30 minutes.
After supervisor resolves: supervisor may confirm severity_level or override it; agent proceeds to RT-001 with the confirmed/overridden severity_level.

---

### Module RT — Routing

**RT-001 — Adjuster Assignment**
- Trigger: processing_status = ROUTING
- Inputs: claim_type, severity_level, incident_state, bodily_injury_flag

**Assignment algorithm:**
1. Query CRM Endpoint 2: GET /users with role=adjuster, specialization includes claim_type, is_active=true (see Integration 1)
   **Bodily injury exception:** when bodily_injury_flag = true, additionally require that the adjuster's specializations array includes BODILY_INJURY. This selects only adjusters dual-qualified for both the primary claim_type and bodily injury handling. A LIABILITY adjuster without BODILY_INJURY in their specializations must not receive a bodily-injury-flagged claim. If no dual-qualified adjuster is available after step 5, fall through to the ROUTING_OVERRIDE WorkItem path — do NOT relax the dual-qualification requirement.
2. Filter by: incident_state ∈ user.coverage_regions
3. Filter out: users with open_claims_count ≥ MAX_ADJUSTER_QUEUE_SIZE
4. From remaining: rank by open_high_severity_claims_count ascending, then by open_claims_count ascending; select top rank (first eligible)
5. If no eligible adjuster after filters:
   - Create ROUTING_OVERRIDE WorkItem (assigned to SUPERVISOR)
   - Set processing_status = AWAITING_ROUTING_OVERRIDE
   - If INTERIM acknowledgment not yet sent: trigger AC-001 (INTERIM)
   - Do NOT assign a wrong-specialty adjuster as fallback
6. If eligible adjuster found: set Claim.assigned_adjuster_id; proceed to RT-002

**ROUTING_OVERRIDE WorkItem content:**
```json
{
  "claim_id": "<uuid>",
  "claim_type": "<type>",
  "severity_level": "<level>",
  "incident_state": "<state>",
  "available_adjusters_checked": 0,
  "filter_result": "<reason no adjuster found: queue full / no coverage region / no specialization>",
  "agent_note": "All eligible adjusters for this claim type and region are at queue capacity."
}
```
Assigned to SUPERVISOR. SLA: 15 minutes; escalate to CLAIMS_MANAGER after 15 minutes.

**RT-002 — CRM Claim Record Create/Update**
- Trigger: after RT-001 (or after ROUTING_OVERRIDE is resolved by human)
- Action: POST /claims to Salesforce CRM (see Integration 1, Endpoint 3)
- Request body:
```json
{
  "fnol_id": "<Claim.id>",
  "claimant_id": "<claimant_id>",
  "policy_number": "<policy_number>",
  "claim_type": "<claim_type>",
  "severity_level": "<severity_level>",
  "coverage_status": "<coverage_status>",
  "assigned_adjuster_id": "<adjuster_id>",
  "received_at": "<ISO 8601>",
  "sla_deadline": "<ISO 8601>",
  "incident_date": "<ISO 8601>",
  "incident_location": "<string>",
  "estimated_loss_amount": 0.00,
  "bodily_injury_flag": false,
  "source_channel": "<channel>"
}
```
- On success: set Claim.crm_claim_id from response; set processing_status = ACKNOWLEDGED; proceed to AC-001
- On CRM failure: retry per Integration 1 retry spec; if all retries fail: create SYSTEM_ERROR WorkItem; alert IT_ONCALL

---

### Module AC — Acknowledgment

**AC-001 — Claimant Acknowledgment**
- Trigger: processing_status reaches ACKNOWLEDGED — OR — claim enters any AWAITING_* state AND this is the first time that status is reached (sends INTERIM acknowledgment)
- Acknowledgment types:
  - **FULL**: sent when adjuster is already assigned. Contains: claim reference, adjuster name + direct phone/email, next-contact commitment by severity (LOW/MEDIUM: within 24h; HIGH: within 4h; CRITICAL: within 2h)
  - **INTERIM**: sent when claim is in human review (adjuster not yet assigned). Contains: claim reference, "An adjuster will contact you within 24 hours (or sooner for urgent claims)". Does NOT name an unconfirmed adjuster.

- Delivery by channel:
  - EMAIL source: send via CRM Endpoint 4 to claimant email
  - WEB_FORM source: trigger CRM Endpoint 4 (email); also set portal status to "Received and Processing"
  - PHONE_TRANSCRIPT source: if claimant email available in CRM, send via CRM Endpoint 4; also create an adjuster callback task in CRM and log `CALLBACK_TASK_CREATED`
    If no email available: create callback task only; log warning that email acknowledgment was not possible

- If sending INTERIM: set Claim.interim_acknowledged_at = current UTC timestamp
- If sending FULL: set Claim.full_acknowledged_at = current UTC timestamp
- (Claim.acknowledged_at = computed COALESCE; set automatically)
- Log ACKNOWLEDGMENT_SENT (to_value = "FULL" or "INTERIM")

**If INTERIM was sent and routing completes later:**
- When processing_status transitions to COMPLETED: send a follow-up FULL acknowledgment (with adjuster name) to claimant via same channel. Set Claim.full_acknowledged_at = current UTC timestamp. Log ACKNOWLEDGMENT_SENT with to_value = "FULL".

**AC-002 — SLA Monitoring**
- **Operating hours note:** Claim SLA (received_at + 2 hours) counts on calendar time, 24/7. WorkItem SLAs count only during operating hours [Assumption C1: assumed M–F 08:00–18:00 local time]. Claims received outside operating hours that enter an AWAITING_* state will breach the Claim SLA if an INTERIM acknowledgment has not already been sent. The autonomous INTERIM acknowledgment path has no operating-hours dependency — it fires at any time.
- Runs on two triggers:
  1. On every processing_status change for any Claim
  2. On a background timer: every 5 minutes, evaluate all Claims with processing_status ≠ COMPLETED and processing_status ≠ HALTED
- SLA computation:
  - time_remaining = Claim.sla_deadline - now
  - If acknowledged_at is not null: sla_status remains as set at acknowledgment time (do not retroactively change)
  - Else if now > Claim.sla_deadline:
    - Set sla_status = BREACHED
    - Log SLA_BREACHED
    - Notify CLAIMS_MANAGER
  - Else if time_remaining ≤ SLA_AT_RISK_BUFFER_MINUTES:
    - Set sla_status = AT_RISK
    - Log SLA_AT_RISK_ALERT
    - Notify assigned SUPERVISOR via CRM notification (push to supervisor dashboard)
    - If any OPEN WorkItem exists for this claim: escalate WorkItem immediately (do not wait for WorkItem SLA timer)
  - Else:
    - sla_status = ON_TRACK

---

## Integration Contracts

### Integration 1 — Salesforce CRM (REST API)

**Purpose:** Claimant lookup, adjuster query, claim record creation, acknowledgment delivery
**Authentication:** OAuth 2.0 client credentials; credentials and token endpoint URL are deployment configuration items provided by IT [Assumption A3]
**Base URL:** `[CRM_BASE_URL]` — to be provided by client IT team [Assumption A3]
**Timeout:** 5 seconds per request
**Retry:** HTTP 5xx → 3 retries, exponential backoff; intervals are deployment configuration items. HTTP 4xx → no retry; log error.
**Rate limits:** Must be confirmed with client IT before build [Assumption A3]; implement configurable rate limits (`CRM_RATE_LIMIT_SUSTAINED_RPM`, `CRM_RATE_LIMIT_BURST_RPM` deployment config). 429 handling: honor `Retry-After` header if present; otherwise exponential backoff; on final failure create SYSTEM_ERROR WorkItem.
**Authentication failure:** If token refresh fails after retries: create SYSTEM_ERROR WorkItem; set sla_status = AT_RISK for all claims currently in processing; alert IT_ONCALL. Do not proceed with CRM calls during token failure.

**Endpoint 1 — Claimant lookup:**
```
GET /contacts?email={email}&phone={phone}
(at least one of email or phone required; both preferred)
Response 200:
{
  "contact_id": string,
  "name": string,
  "email": string (nullable),
  "phone": string (nullable),
  "prior_claims_count": integer,   ← for SERIAL_CLAIMANT scoring in SV-001; window must match SERIAL_CLAIMANT_WINDOW_DAYS (default 365 days) — confirm with CRM admin whether this field is a rolling 365-day count or a lifetime count; if lifetime, the SERIAL_CLAIMANT signal will be miscalibrated [See Assumption A6 — Additional validation required (claimant contact records)]
  "policy_numbers": [string]
}
Response 404: no matching contact (non-blocking; claimant_id remains null)
```

**Endpoint 2 — Adjuster query:**
```
GET /users?role=adjuster&specialization={claim_type}&region={incident_state}&active=true
Response 200:
{
  "adjusters": [
    {
      "id": string,
      "name": string,
      "direct_phone": string,
      "direct_email": string,
      "specializations": [string],
      "coverage_regions": [string],
      "open_claims_count": integer,
      "open_high_severity_claims_count": integer
    }
  ]
}
```

**Endpoint 3 — Create claim record:**
```
POST /claims
Request body: (see RT-002 above)
Response 200:
{
  "crm_claim_id": string,
  "created_at": ISO 8601 timestamp
}
Response 422: validation error (e.g., invalid adjuster_id) → create SYSTEM_ERROR WorkItem; do not retry
```

**Endpoint 4 — Send acknowledgment:**
```
POST /communications
Request:
{
  "contact_id": string,
  "channel": "EMAIL",
  "template_id": "FNOL_ACK_FULL_V1" | "FNOL_ACK_INTERIM_V1",
  "variables": {
    "claim_reference": string,           ← formatted as "FNOL-{YYYY}-{claim_id_short}"
    "adjuster_name": string,             ← omitted in INTERIM template
    "adjuster_phone": string,            ← omitted in INTERIM template
    "adjuster_email": string,            ← omitted in INTERIM template
    "next_contact_by": ISO 8601 timestamp  ← omitted in INTERIM; "within 24h" is baked into INTERIM template
  }
}
Response 200: { "communication_id": string, "sent_at": ISO 8601 timestamp }
Response 404: contact_id not found → log error; create SYSTEM_ERROR WorkItem; a specialist must manually send the acknowledgment. Direct SMTP is out of scope for V1 — no SMTP integration contract exists in this spec.
```

---

### Integration 2 — Legacy Policy Administration System (SOAP)

**Purpose:** Policy lookup and exclusion check
**Authentication:** WS-Security token; credentials provided by IT [Assumption A3]
**WSDL:** `[POLICY_ADMIN_BASE_URL]/PolicyService?wsdl` — to be provided by client IT [Assumption A1]
**Base URL:** `[POLICY_ADMIN_BASE_URL]` — to be provided by client IT [Assumption A3]

**Timeout:** 10 seconds (legacy system; allow generous timeout)
**Retry:** SOAP fault → 3 retries, exponential backoff; connection timeout → 3 retries, exponential backoff. HTTP 4xx (proxy errors) → no retry; create SOAP_FAILURE WorkItem immediately. Retry intervals are deployment configuration items.
**Rate limits:** Must be confirmed with client IT before build [Assumption A3]; implement configurable rate limits (`SOAP_RATE_LIMIT_SUSTAINED_RPM`, `SOAP_RATE_LIMIT_BURST_RPM` deployment config).
**Concurrency:** Limit concurrent SOAP calls via the `MAX_SOAP_CONCURRENT_CALLS` configuration parameter (see Configuration Parameters table). If all connections occupied, incoming requests queue (do not fail fast). Pool size must be confirmed with IT before load testing.

**Operation 1 — GetPolicyByNumber:**
- **Input:** policyNumber (string, max 20 chars)
- **Returns — success:** policyId, status (ACTIVE|LAPSED|CANCELLED|SUSPENDED), effectiveDate (YYYY-MM-DD), expirationDate (YYYY-MM-DD), deductibleAmount (decimal), coverageTypes (list of strings), coverageLimits (list of {coverageType, amount}), exclusions (list of {code, text})
- **Returns — fault (POLICY_NOT_FOUND):** fault code POLICY_NOT_FOUND with message string

Note: exact SOAP element names and namespace are defined in the WSDL from IT [Assumption A1]. Coverage type codes in the response require mapping to the FPA's internal claim_type enum [Assumption A2]; the mapping table is a deployment configuration item.

**Operation 2 — CheckExclusions:**
- **Input:** policyId (string), incidentDescription (text extracted from claim), claimType (string)
- **Returns — success:** excluded (boolean), matchedExclusions (list of {code, text, similarity: decimal 0.00–1.00})
- **Returns — fault:** INVALID_POLICY_ID or SERVICE_UNAVAILABLE

On INVALID_POLICY_ID fault: log error; create SOAP_FAILURE WorkItem; set processing_status = HALTED; alert IT_ONCALL (policy record inconsistency — cannot verify exclusion status without a valid policy ID).
On SERVICE_UNAVAILABLE fault (after retries): create SOAP_FAILURE WorkItem; set processing_status = HALTED; alert IT_ONCALL.

Note: exact SOAP element names and namespace are defined in the WSDL from IT [Assumption A1].

**Fallback if SOAP unavailable:** Do NOT proceed with unverified coverage. Create SOAP_FAILURE WorkItem; halt claim processing; alert IT_ONCALL. This is the hardest failure mode — no workaround in V1.

---

### Integration 3 — Document Management System (REST)

**Purpose:** Store raw claim input; retrieve for processing
**Authentication:** API key; mechanism and credentials provided by IT [Assumption A3, A4]
**Base URL:** `[DMS_BASE_URL]` — to be provided by client IT [Assumption A3]
**Timeout:** 5 seconds
**Retry:** HTTP 5xx → 2 retries, exponential backoff; intervals are deployment configuration items
**Rate limits:** Must be confirmed with client IT before build [Assumption A4]; implement configurable rate limits (`DMS_RATE_LIMIT_SUSTAINED_RPM`, `DMS_RATE_LIMIT_BURST_RPM` deployment config).

**Endpoint 1 — Store document:**
```
POST /documents
Request:
{
  "claim_id": string,
  "document_type": "FNOL_RAW" | "PARSED_CLAIM",
  "content_base64": string (base64-encoded UTF-8 text),
  "content_type": "text/plain" | "application/pdf",
  "source_channel": string
}
Response 200: { "document_id": string, "stored_at": ISO 8601 timestamp }
Response 413: content too large (>10MB) → log warning; proceed without storing; alert IT
```

**Fallback:** DMS is non-blocking for intake. If DMS unavailable at IN-001: log warning, proceed with processing (raw_input held in memory for duration of claim processing session), retry DMS store every 60 seconds for up to 30 minutes. If still failing after 30 minutes: alert IT_ONCALL; document processing continues in-memory but compliance gap exists.

---

## Escalation Summary

| WorkItem Type | Trigger | Assigned Role | SLA | Timeout Action |
|---|---|---|---|---|
| FIELD_COMPLETION | Parse confidence < PARSE_CONFIDENCE_THRESHOLD or required field missing | SPECIALIST | 20 min | Escalate to SUPERVISOR |
| DUPLICATE_REVIEW | Duplicate candidate found in DUPLICATE_WINDOW_MINUTES; sets AWAITING_DUPLICATE_REVIEW | SPECIALIST | 20 min | Escalate to SUPERVISOR |
| COVERAGE_REVIEW | Exclusion match, lapsed policy, or claim type mismatch | SUPERVISOR | 45 min | Escalate to CLAIMS_MANAGER |
| SEVERITY_REVIEW | HIGH/CRITICAL severity, is_high_value, or bodily_injury_flag | SUPERVISOR | 30 min | Escalate to CLAIMS_MANAGER |
| ROUTING_OVERRIDE | No eligible adjuster available | SUPERVISOR | 15 min | Escalate to CLAIMS_MANAGER |
| SOAP_FAILURE | Policy admin SOAP failure (PL-001 or CV-002) after all retries | IT_ONCALL | 30 min | Manual policy lookup or exclusion check by specialist |
| SYSTEM_ERROR | Any other integration failure after retries | IT_ONCALL | 1 hour | Manual processing |

---

## Deployment Strategy

**Phase 0 — Shadow mode (weeks 1–4 of pilot):** The FPA runs against live inbound claims but makes no autonomous decisions. All outputs (extracted fields, coverage recommendations, severity scores, routing proposals) are logged and compared against specialist decisions. Shadow metrics establish baseline accuracy before any autonomous action is taken.

**Phase 1 — Partial rollout (weeks 5–8):** EMAIL channel claims only; low-complexity filter: claim_type ∈ {AUTO_COLLISION, AUTO_THEFT, PROPERTY_DAMAGE, PROPERTY_THEFT} AND estimated_loss_amount < $10,000 AND bodily_injury_flag = false. Autonomous processing enabled for this subset. All other claims follow shadow-mode path. Pilot accuracy metrics reviewed weekly.
Note: the bodily_injury_flag = false condition is the materially restrictive element — hard constraint C2 would already hold any bodily-injury-flagged claim for SEVERITY_REVIEW regardless of claim_type. Making it explicit in the Phase 1 filter ensures the rollout boundary is transparent and does not depend implicitly on a downstream hard constraint to enforce it. LIABILITY is excluded despite potentially scoring LOW/MEDIUM because its +2 severity weight reflects third-party exposure and latent litigation risk that does not always manifest in the initial estimated loss figure — a $8,000 LIABILITY claim can escalate in ways a $8,000 AUTO_COLLISION claim typically does not. Relaxing this exclusion is a candidate Phase 2 decision once pilot data establishes autonomous handling quality for the included claim types. Note: the fraction of total volume this filter admits depends on channel distribution and loss-amount distribution — both unknown at spec time. Builder must estimate from historical intake data before Phase 1 rollout begins.

**Phase 2 — Full autonomous path (week 9+):** All claim types enabled once Phase 1 accuracy thresholds are met (per Artifact 4 production readiness table). Human shadow review shifts from full-sample to 10% random audit.

**Kill switch:** A deployment configuration flag (`AUTONOMOUS_PROCESSING_ENABLED`, default false) must be present before go-live. Setting it to false reverts all claims to AWAITING_FIELD_COMPLETION WorkItems (full human review) without code changes. Operations team must have documented procedure for activating the kill switch in under 5 minutes.

**Operating cost note:** Agent operates 24/7 per the SLA requirements. Cost estimate: ~5–8% of 300 claims/day × 365 calendar days = ~5,500–8,800 complex reasoning calls/year × $1–$2/call = ~$5,500–$17,600/year. Materially below the $115K–$135K/year rework elimination value quantified in Artifact 1, and well below any realistic estimate of conditional capacity redeployment value. Builder must validate against chosen model provider's actual per-call pricing before go/no-go.

---

## Audit & Logging

Every Claim state transition and every human action must produce an AuditEvent (see entity definition above). Logs are immutable, append-only. 7-year retention.

**Required to_value content for key events (to_value is mandatory for these; nullable only for events listed below):**
- `PARSING_COMPLETED`: to_value = `{"claim_type": "<value>", "confidence": 0.00, "parse_confidence": 0.00}` — required; this is the record that enables retrospective classification accuracy audits
- `PARSING_LOW_CONFIDENCE`: to_value = `{"missing_fields": ["<field>"], "low_confidence_fields": [{"field": "<name>", "confidence": 0.00}]}`
- `SEVERITY_SCORED`: to_value = `{"severity_score": 0, "severity_level": "<level>", "components": [{"condition": "<text>", "points": 0}]}`
- All `*_BY_HUMAN` events: from_value = old value, to_value = new value (both required; nullable only if no prior value existed)

**Applicable regulatory context:** NAIC Unfair Claims Settlement Practices Act (model law; confirm which operating states have adopted it); state DOI acknowledgment timing requirements (see Assumption B4); NAIC Insurance Data Security Model Law (for PII handling and audit log controls). Builder must confirm applicable state-level adoptions with legal before deployment. The 7-year retention period is a conservative default pending legal confirmation of the shortest applicable state requirement.

The supervisor dashboard aggregates:
- Claims in each processing_status, by hour
- SLA_AT_RISK and SLA_BREACHED counts for current shift
- WorkItem open/resolved counts by type
- Autonomous handling rate (claims reaching COMPLETED with no WorkItem created) for current shift

The claims manager dashboard adds:
- Routing accuracy rate (audit sample: adjuster confirmed correct / total sample)
- Coverage review outcome distribution (confirmed / denied / disputed resolved)
- SOAP_FAILURE and SYSTEM_ERROR counts (IT health signal)

---

## Definition Of Done (Spec Handoff)

This specification is ready for implementation handoff only when all items below are true:

- All Priority 1 assumptions in Artifact 5 are validated with named stakeholders and documented outcomes.
- Integration credentials, base URLs, and numeric rate limits are confirmed in environment configuration.
- Claim acknowledgment templates (`FNOL_ACK_FULL_V1`, `FNOL_ACK_INTERIM_V1`) are created and approved in CRM.
- WorkItem UI requirements (Artifact 3 scope note) are agreed with builder and product owner.
- Pilot gates in Artifact 4 are acknowledged by operations and compliance owners.
- Any unresolved assumption is explicitly marked as out-of-scope for V1 with rollback or contingency behavior documented.

---

# Artifact 4 — Validation Design

## Purpose

This document defines how to verify that the FNOL Processing Agent (FPA) is working correctly. It covers: what to test, how to test it, what failure looks like — including the *quiet* failure modes where the agent is wrong and no one notices — and what thresholds must be met before the agent is trusted for production.

---

## Validation Principles

1. **Test the delegation boundary, not just the happy path.** The most consequential tests are the ones that probe where the agent hands off to a human. An agent that passes happy-path tests but fails at the boundary causes systematic harm before anyone notices.

2. **Define quiet failure explicitly.** Quiet failure is worse than loud failure. An agent that routes a bodily injury claim to a property adjuster (wrong specialization) fails loudly when the adjuster calls back confused. An agent that misidentifies a claim type and routes to the right specialty by accident passes audit reviews until a coverage dispute surfaces weeks later. Test for both.

3. **The SLA clock is not the agent's SLA clock.** The 2-hour SLA starts at receipt, not at processing start. Tests must verify that received_at is set before any parsing, and that AC-001 fires correctly in both FULL and INTERIM paths.

---

## Test Suite Structure

| Suite | Focus | Minimum test count |
|---|---|---|
| V1 — Happy Path | End-to-end autonomous claim processing | 3 |
| V2 — Parsing Edge Cases | Field extraction accuracy and confidence thresholds | 7 |
| V3 — Coverage Validation | Coverage match, exclusion, lapsed policy | 5 |
| V4 — Severity & Delegation Boundary | Severity scoring, escalation triggers, hard constraints | 7 |
| V5 — SLA Monitoring | SLA clock, AT_RISK alerting, INTERIM acknowledgment | 4 |
| V6 — Integration Failure Modes | SOAP timeout, CRM failure, DMS unavailable | 5 |
| V7 — Concurrency | Duplicate claim receipt, simultaneous field edit | 2 |
| V8 — Post-Launch Monitoring | Continuous production drift signals (not pre-launch tests) | 4 |

---

## V1 — Happy Path

### V1-01 — Standard Auto Collision, Low Value (Fully Autonomous)
**Given:**
- Email received: "Hi, I was in a rear-end collision on the highway. My policy number is AA-123456. The other driver hit me from behind. No injuries. My car has significant bumper damage. It happened yesterday around 3pm on I-95 in Georgia. My contact is jane.doe@email.com"
- Policy AA-123456: ACTIVE, covers AUTO_COLLISION, effective dates encompass incident_date, no matching exclusions
- Estimated loss: not stated in text
- Claimant has 1 prior claim in the last 12 months
- Adjuster available: AUTO_COLLISION specialist, Georgia coverage, open_claims_count = 8

**When:** Agent processes claim end-to-end

**Then:**
- received_at set at email receipt time (before IN-002 begins)
- claim_type = AUTO_COLLISION, parse_confidence ≥ 0.90
- bodily_injury_flag = false (no injury language detected)
- coverage_status = CONFIRMED
- severity_score: estimated_loss null (+2) = 2 → severity_level = LOW
- **Verify:** prior claims count (1) < SERIAL_CLAIMANT_THRESHOLD (5) → SERIAL_CLAIMANT signal does NOT fire; severity_score remains 2 (not 3)
- No SV-002 escalation (LOW, not high-value, no bodily injury)
- Adjuster assigned: AUTO_COLLISION specialist, Georgia coverage, not at queue limit
- CRM claim record created (crm_claim_id populated)
- Acknowledgment: FULL, sent to jane.doe@email.com, contains claim reference + adjuster name + "within 24 hours" commitment
- acknowledged_at set; sla_status = ON_TRACK at acknowledgment
- Total agent processing time (received_at → acknowledged_at): ≤ 5 minutes
- No WorkItem created
- processing_status = COMPLETED

---

### V1-02 — Web Form Claim, GOOD Coverage Match (Fully Autonomous)
**Given:**
- Web form submitted with: policy_number = PR-789012, claim_type = PROPERTY_DAMAGE (dropdown), incident_date = 2026-04-20, incident_location = "Miami, FL", estimated_loss_amount = $8,500, description = "Storm damage to roof and windows"
- Policy PR-789012: ACTIVE, covers PROPERTY_DAMAGE, no exclusions matching storm/roof
- Adjuster available: PROPERTY_DAMAGE specialist, FL coverage, open_claims_count = 10

**When:** Agent processes claim end-to-end

**Then:**
- Web form fields extracted with confidence = 0.95 (pre-structured)
- parse_confidence ≥ 0.90, all required fields present
- coverage_status = CONFIRMED (no exclusion match for storm/roof)
- severity_score: $8,500 < $10K (+1) = 1 → LOW
- Autonomous routing
- Acknowledgment: FULL, via email (if available in CRM) + web portal status updated
- No WorkItem created

---

### V1-03 — Phone Transcript, Bodily Injury — INTERIM Ack Then FULL
**Given:**
- Phone transcript uploaded: "Caller: I need to report an accident. I was hit by another driver, I'm in the hospital. My policy is LI-456789. It happened this morning in Austin, Texas. I think the damages might be around $30,000 to my car."
- Policy LI-456789: ACTIVE, covers LIABILITY
- bodily_injury_flag = true ("I'm in the hospital")
- multiple_parties_flag = true ("another driver" matches IN-002 trigger phrase "other driver")
- Adjuster assigned after supervisor severity review (dual-qualified adjuster: specializations = [LIABILITY, BODILY_INJURY], TX coverage; required by RT-001 bodily injury exception)

**When:** Agent processes

**Then:**
- Caller lines extracted; representative lines excluded from NLP
- bodily_injury_flag = true; multiple_parties_flag = true; claim_type = LIABILITY; severity scoring: bodily_injury (+3) + LIABILITY (+2) + $30K loss (+2) + multiple_parties (+1) = 8 → severity_level = CRITICAL; SEVERITY_REVIEW WorkItem triggered (CRITICAL severity + bodily_injury_flag = true)
- SV-002 creates SEVERITY_REVIEW WorkItem → processing_status = AWAITING_SEVERITY_REVIEW
- INTERIM acknowledgment sent immediately on AWAITING_SEVERITY_REVIEW entry: claim reference, "An adjuster will contact you within 24 hours"
- acknowledged_at set at INTERIM send time (SLA met)
- After supervisor confirms severity and routing: FULL acknowledgment sent with adjuster name
- No autonomous adjuster assignment without supervisor confirmation

---

## V2 — Parsing Edge Cases

### V2-01 — Policy Number Ambiguity: Billing Number Provided
**Given:** Email contains "account number 4420-001" but no policy number in expected format

**When:** IN-002 extracts fields

**Then:**
- policy_number field extracted with confidence < 0.90 (or not extracted)
- FIELD_COMPLETION WorkItem created within 10 seconds
- WorkItem content shows: extracted value = "4420-001", confidence = low, note "Value does not match expected policy number format"
- processing_status = AWAITING_FIELD_COMPLETION
- INTERIM acknowledgment sent

---

### V2-02 — Relative Date Resolution
**Given:** Email states "the accident happened last Tuesday"; received_at = 2026-04-27 (Monday)

**When:** IN-002 extracts incident_date

**Then:**
- incident_date resolved to 2026-04-21 (the Tuesday prior to received_at)
- Confidence ≥ 0.85 (relative dates carry slightly lower confidence than absolute)
- AuditEvent records: extracted_value = "last Tuesday", resolved_to = "2026-04-21"
- **Verify:** resolution uses received_at as the reference point, not the current processing time

---

### V2-03 — Bodily Injury in Phone Transcript Not Misidentified
**Given:** Phone transcript contains representative line "Agent: Are you injured?" followed by "Caller: No, I'm fine, just the car is damaged"

**When:** IN-002 processes

**Then:**
- Only Caller: lines processed by NLP
- bodily_injury_flag = false (claimant explicitly denies injury; agent question is excluded)
- **Verify:** representative lines containing injury words do NOT set bodily_injury_flag

---

### V2-04 — All Required Fields Missing (Minimal Web Form Submission)
**Given:** Web form submitted with only incident_description = "My stuff was damaged"

**When:** IN-002 runs

**Then:**
- policy_number: not extracted
- claimant contact: not extracted
- claim_type: ambiguous (for example PROPERTY_DAMAGE vs LIABILITY; low confidence)
- incident_date: not extracted
- parse_confidence = 0.00 (no required fields)
- FIELD_COMPLETION WorkItem created with all 4 required fields in missing_or_low_confidence_fields list
- INTERIM acknowledgment still sent (claim reference created and sent before field completion)
- **Verify:** INTERIM ack is sent even when claim has zero parseable fields

---

### V2-05 — Web Form Double-Submit Blocked by IN-001 Idempotency Check
**Given:** Claimant clicks "Submit" twice in quick succession; both submissions carry the same form submission token (source_message_id = "FORM-TOKEN-abc123"); second submission arrives 3 seconds after the first

**When:** Both submissions are received by IN-001

**Then:**
- First submission (token FORM-TOKEN-abc123): IN-001 finds no existing Claim with this source_message_id → creates Claim, stores source_message_id, processing begins normally
- Second submission (same token FORM-TOKEN-abc123): IN-001 idempotency check finds existing Claim with source_message_id = FORM-TOKEN-abc123 received within DUPLICATE_WINDOW_MINUTES → incoming event discarded; no second Claim record created; existing Claim.id returned to caller
- No DUPLICATE_DETECTED AuditEvent logged (this is a pre-creation technical guard, not a business logic duplicate — IN-003 is never reached)
- Claimant receives one acknowledgment only
- **Verify:** IN-001 idempotency operates on source_message_id (the form submission token), not on claim content fields (policy_number + incident_date + claimant_id); content-based deduplication is IN-003's responsibility (tested in V7-01)

---

### V2-06 — Estimated Loss Exceeds HIGH_VALUE_THRESHOLD During Parsing
**Given:** Email states "I estimate damage around $75,000 to my property"

**When:** IN-002 extracts

**Then:**
- estimated_loss_amount = 75000.00 (USD normalised)
- is_high_value = true (75000 ≥ 50000)
- SV-001 scoring: $50K–$150K range (+4); SV-002 triggers SEVERITY_REVIEW because is_high_value = true
- **Verify:** is_high_value flag is computed at parse time and flows through to SV-002 trigger correctly

---

### V2-07 — Ambiguous Claim Type: "Water Damage"
**Given:** Email states "there was water damage to my basement after the storm"

**When:** IN-002 classifies claim_type

**Then:**
- NLP classification: PROPERTY_DAMAGE (most likely) with confidence ~0.82 (below threshold; storm vs. flood ambiguity)
- FIELD_COMPLETION WorkItem created with claim_type in low-confidence list
- WorkItem shows: agent's top classification = PROPERTY_DAMAGE (0.82), note "Storm vs. flood coverage distinction may apply — verify claim type with specialist"
- **Verify:** agent does NOT autonomously classify flood-related claims as PROPERTY_DAMAGE if confidence is below threshold

---

## V3 — Coverage Validation

### V3-01 — Clear Coverage Match
**Given:** claim_type = AUTO_COLLISION; policy covers AUTO_COLLISION; no exclusions return from CheckExclusions

**When:** CV-001 and CV-002 run

**Then:**
- coverage_status = CONFIRMED
- No COVERAGE_REVIEW WorkItem created
- Processing continues to SV-001

---

### V3-02 — Claim Type Not in Policy (Clear Exclusion)
**Given:** claim_type = AUTO_COLLISION; policy coverage_types = [LIABILITY] only (liability-only policy)

**When:** CV-001 runs

**Then:**
- claim_type NOT in coverage_types_list
- coverage_status = EXCLUDED
- COVERAGE_REVIEW WorkItem created: content shows claim_type = AUTO_COLLISION, policy_coverage_types = [LIABILITY]
- INTERIM acknowledgment sent if not already sent
- processing_status = AWAITING_COVERAGE_REVIEW
- **Verify:** agent does NOT proceed to severity scoring with coverage_status = EXCLUDED

---

### V3-03 — Lapsed Policy
**Given:** policy_status = LAPSED (returned by PL-001)

**When:** PL-001 returns policy record

**Then:**
- coverage_status = LAPSED
- COVERAGE_REVIEW WorkItem created with note "Policy is in LAPSED status — specialist must determine if grace period applies"
- Agent does NOT deny coverage; specialist reviews
- **Verify:** processing does not continue to coverage type check while policy is lapsed

---

### V3-04 — Exclusion Similarity Threshold: Below
**Given:** Exclusion clause text: "damage arising from intentional acts by the insured"
Incident description: "my roof collapsed due to heavy snowfall"
Similarity score returned by CheckExclusions: 0.42

**When:** CV-002 evaluates

**Then:**
- 0.42 < EXCLUSION_SIMILARITY_THRESHOLD (0.75)
- excluded = false → coverage_status = CONFIRMED
- No COVERAGE_REVIEW WorkItem
- **Verify:** low similarity scores do NOT trigger a hold

---

### V3-05 — Exclusion Similarity Threshold: Above
**Given:** Exclusion clause text: "damage arising from flood or surface water intrusion"
Incident description: "water came into my basement during the rainstorm"
Similarity score: 0.81

**When:** CV-002 evaluates

**Then:**
- 0.81 ≥ EXCLUSION_SIMILARITY_THRESHOLD (0.75)
- coverage_status = DISPUTED
- COVERAGE_REVIEW WorkItem includes: exclusion clause text, similarity = 0.81, incident description preview
- processing_status = AWAITING_COVERAGE_REVIEW
- **Verify:** boundary is enforced at exactly 0.75 — a score of 0.74 does NOT trigger the hold

---

## V4 — Severity & Delegation Boundary

### V4-01 — LOW Severity Routes Autonomously
**Given:** claim_type = AUTO_THEFT, estimated_loss_amount = $5,000, bodily_injury_flag = false, no prior claims

**When:** SV-001 and SV-002 run

**Then:**
- severity_score: $5K < $10K (+1) = 1 → severity_level = LOW
- SV-002: no escalation (LOW, not high-value, no bodily injury)
- No SEVERITY_REVIEW WorkItem
- Proceeds directly to RT-001

---

### V4-02 — Bodily Injury Always Escalates (Hard Constraint C2)
**Given:** claim_type = AUTO_COLLISION, estimated_loss_amount = $3,000, bodily_injury_flag = true

**When:** SV-002 runs

**Then:**
- severity_score: $3K < $10K (+1) + bodily_injury (+3) = 4 → MEDIUM; BUT bodily_injury_flag = true
- SEVERITY_REVIEW WorkItem created regardless of severity_level (bodily_injury_flag = true is a hard trigger)
- processing_status = AWAITING_SEVERITY_REVIEW
- INTERIM acknowledgment sent
- **Verify:** bodily_injury_flag = true ALWAYS triggers SEVERITY_REVIEW, even at MEDIUM severity and low financial value

---

### V4-03 — HIGH_VALUE_THRESHOLD Boundary Precision
**Given:** Two claims — Claim A: estimated_loss_amount = $49,999.99; Claim B: estimated_loss_amount = $50,000.00
Both: AUTO_COLLISION, no bodily injury, coverage CONFIRMED

**When:** Both processed

**Then:**
- Claim A: is_high_value = false; if severity otherwise LOW/MEDIUM → no SEVERITY_REVIEW → autonomous routing
- Claim B: is_high_value = true → SEVERITY_REVIEW WorkItem created regardless of severity_level
- **Verify:** threshold is inclusive at exactly $50,000.00; the ≥ comparison uses decimal(12,2) arithmetic — no floating-point ambiguity
- **Verify:** estimated_loss_amount is stored and compared as decimal(12,2) per the schema; test rejects any implementation using floating-point types (float/double) for this field
- **How to verify the type constraint:** runtime logic tests alone cannot prove decimal storage. Use both: (a) Phase 0 code review checklist item — "Confirm estimated_loss_amount column is declared DECIMAL/NUMERIC in database schema, not FLOAT or DOUBLE; verify ORM model definition"; and (b) storage-layer precision assertion — insert $49999.99 and $50000.00, read back both values, assert they are exactly equal to the inserted values to 2 decimal places. A float64 implementation rounds $49999.999... to $50000.00, which would erroneously trigger is_high_value = true for a claim just below threshold.

---

### V4-04 — Coverage Denial Requires Human (Hard Constraint C1)
**Given:** Specialist resolves COVERAGE_REVIEW WorkItem with decision = DENIED

**When:** Human decision recorded

**Then:**
- coverage_status = DENIED (only set by human; never by agent)
- Claim.coverage_denial_reason is populated by the specialist (required for DENIED resolution; WorkItem UI enforces this field as mandatory on the DENIED resolution path — resolution cannot be submitted without it)
- processing_status = HALTED
- AuditEvent: actor_type = HUMAN, event_type = COVERAGE_DENIED_BY_HUMAN, to_value = coverage_denial_reason text
- No adjuster assignment occurs
- No FULL acknowledgment with adjuster name is sent
- **Verify:** the agent cannot set coverage_status = DENIED at any point in any module
- **Verify:** coverage_denial_reason is non-null when coverage_status = DENIED; the schema permits null only until a human sets DENIED

---

### V4-05 — SERIAL_CLAIMANT Flag: Score Contribution Only
**Given:** claimant_id has 7 prior claims in last 365 days (≥ SERIAL_CLAIMANT_THRESHOLD of 5)
Claim: AUTO_COLLISION, estimated_loss_amount = $4,000, bodily_injury_flag = false

**When:** SV-001 runs

**Then:**
- severity_score: $4K (+1) + SERIAL_CLAIMANT (+1) = 2 → LOW
- No SEVERITY_REVIEW escalation on SERIAL_CLAIMANT signal alone (score is 2, still LOW)
- Flag is noted in adjuster WorkItem content as "claimant has elevated prior claim frequency"
- **Verify:** SERIAL_CLAIMANT adds +1 to score but does NOT independently trigger a hold if total score remains LOW/MEDIUM

---

### V4-06 — No Eligible Adjuster: Routing Override
**Given:** claim_type = PROPERTY_DAMAGE, incident_state = HI (Hawaii); no active PROPERTY_DAMAGE adjusters with coverage_regions including HI

**When:** RT-001 runs

**Then:**
- No eligible adjuster found after all filters
- ROUTING_OVERRIDE WorkItem created: "No PROPERTY_DAMAGE adjuster with Hawaii coverage available"
- processing_status = AWAITING_ROUTING_OVERRIDE
- INTERIM acknowledgment sent if not already sent
- Agent does NOT assign a wrong-specialization adjuster as a fallback
- **Verify:** queue overflow triggers human WorkItem, not a compromise routing

---

### V4-07 — Semantic Classification Error Produces Auditable Signal
**Given:** Email describes an AUTO_THEFT incident ("my car was stolen from the parking lot"), but NLP classifies claim_type = AUTO_COLLISION at confidence 0.91 (above threshold — extraction proceeds autonomously)

**When:** Claim is routed and completed

**Then:**
- Claim routes to an AUTO_COLLISION adjuster (wrong specialty — the routing algorithm uses the extracted claim_type)
- The routing is wrong, but no WorkItem is created (confidence was above threshold)
- **Verify:** AuditEvent PARSING_COMPLETED event contains to_value = `{"claim_type": "AUTO_COLLISION", "confidence": 0.91, "parse_confidence": 0.91}` per the required schema (Artifact 3 Audit & Logging section) — this is the record that makes the monthly accuracy audit possible
- **Verify:** the monthly labeled-test accuracy measurement (Artifact 1: ≥ 93% claim type classification accuracy) would catch this failure in sample review
- **Verify:** when the adjuster identifies the error and the WorkItem is updated with corrected claim_type = AUTO_THEFT, AuditEvent records FIELD_OVERRIDDEN_BY_HUMAN with from_value = AUTO_COLLISION, to_value = AUTO_THEFT

**Purpose:** This test verifies that high-confidence misclassifications are auditable (not silently wrong). The system cannot prevent all semantic errors at runtime, but it must produce the signals that allow humans to detect them in audit.

---

## V5 — SLA Monitoring

### V5-01 — SLA Clock Starts at Receipt, Not at Parsing Start
**Given:** Email arrives at 10:00:00 UTC; parsing begins at 10:00:05 UTC (5-second DMS store delay)

**When:** received_at is set

**Then:**
- Claim.received_at = 10:00:00 UTC (not 10:00:05)
- sla_deadline = 12:00:00 UTC (not 12:00:05)
- **Verify:** received_at is immutable and set before IN-002 begins

---

### V5-02 — AT_RISK Alert Fires at Correct Time
**Given:** Claim received at 09:00:00 UTC; SLA_AT_RISK_BUFFER_MINUTES = 30; sla_deadline = 11:00:00 UTC; claim is in AWAITING_SEVERITY_REVIEW at 10:31:00 UTC

**When:** AC-002 runs on its 5-minute timer at 10:35:00 UTC

**Then:**
- time_remaining = 11:00:00 - 10:35:00 = 25 min (< 30 min buffer)
- sla_status set to AT_RISK
- SLA_AT_RISK_ALERT logged
- Supervisor notified via dashboard
- If SEVERITY_REVIEW WorkItem is OPEN: WorkItem immediately escalated (does not wait for WorkItem's 30-min timer)

---

### V5-03 — INTERIM Ack Sent on AWAITING State Entry
**Given:** Claim enters AWAITING_SEVERITY_REVIEW at 10:15 UTC (received_at = 10:00 UTC; 1:45 remaining)

**When:** processing_status = AWAITING_SEVERITY_REVIEW is set

**Then:**
- AC-001 fires immediately (not after SEVERITY_REVIEW is resolved)
- INTERIM acknowledgment sent; acknowledged_at set
- sla_status = ON_TRACK (1:45 remaining; acknowledged within window)
- **Verify:** INTERIM ack fires on AWAITING state entry, not on COMPLETED

---

### V5-04 — SLA Boundary: Email Ingestion Delay
**Given:** Email was sent at 08:00 UTC but not ingested until 10:05 UTC (email server delay); received_at = 10:05 UTC; sla_deadline = 12:05 UTC

**When:** Claim is processed and acknowledged at 10:08 UTC

**Then:**
- sla_status = ON_TRACK (acknowledged_at 10:08 < sla_deadline 12:05)
- **Verify:** sla_deadline = received_at + 2h; sent timestamps from email metadata are NOT used as the SLA start

**Design rationale and known limitation:** The FPA measures SLA from system receipt (received_at), not from claimant send time. This is necessary because email infrastructure delays are outside the insurer's control. However, a claimant who sent at 08:00 and was not acknowledged until 10:08 experienced a 2h8min wait — technically "on-track" by system measure but potentially unsatisfactory. **V1 mitigation (partial):** If the email Date header is present, not in the future, and within 15 minutes before system ingestion time, use the Date header as received_at. Date header must be rejected (fall back to ingestion time) if: (a) header is absent; (b) header timestamp is in the future (sender clock misconfiguration or timezone error); (c) header predates ingestion by more than 15 minutes (infrastructure or relay delay). This guards against backdated headers — either malicious or from misconfigured sender mail servers — being used to artificially advance the SLA clock. Document the system-receipt convention in claimant-facing operational procedures.

---

## V6 — Integration Failure Modes

### V6-01 — SOAP System Unavailable After All Retries
**Given:** Policy admin SOAP returns connection timeout on all retry attempts (PL-001 exhausts retry policy)

**When:** PL-001 exhausts retries

**Then:**
- SOAP_FAILURE WorkItem created with claim ID, policy_number attempted, error detail
- processing_status = HALTED
- IT_ONCALL alerted
- SLA risk notification sent to supervisor (halted claim with time remaining)
- No coverage_status set; no fields from policy admin populated
- Agent does NOT attempt to infer coverage from claim text

---

### V6-02 — CRM Adjuster Query Returns Empty (All at Capacity)
**Given:** All PROPERTY_DAMAGE adjusters in FL have open_claims_count ≥ 15

**When:** RT-001 runs

**Then:**
- Distinct from V4-06 (different cause: queue full, not specialization mismatch)
- ROUTING_OVERRIDE WorkItem created: filter_result = "All PROPERTY_DAMAGE adjusters in FL are at queue capacity (≥ 15 open claims)"
- **Verify:** system clearly distinguishes "no adjuster with this specialization" from "all eligible adjusters are full"

---

### V6-03 — CRM Acknowledgment Email Send Fails (404 Contact Not Found)
**Given:** claimant_id was not enriched (CRM contact not found in IN-002); CRM Endpoint 4 returns 404 for contact_id

**When:** AC-001 attempts to send acknowledgment

**Then:**
- No SMTP fallback (SMTP is out of scope for V1 — no SMTP integration contract exists)
- SYSTEM_ERROR WorkItem created; log acknowledgment as FAILED; specialist must manually contact claimant
- **Verify:** acknowledgment failure does NOT silently pass — SYSTEM_ERROR WorkItem is created so a human knows a claimant was not reached
- **Verify:** agent does NOT attempt any out-of-spec channel (no SMTP, no direct API) — failure is surfaced via WorkItem only

---

### V6-04 — DMS Store Fails at Intake (IN-001)

**Given:** DMS returns HTTP 503 at IN-001

**When:** IN-001 attempts to store raw_input

**Then:**
- IN-001 proceeds (DMS is non-blocking); raw_input_document_id = null; raw_input cached in-memory for current processing session; AuditEvent log: DMS_STORE_FAILED
- Parsing continues in-memory; WorkItem NOT created for DMS failure alone
- Background retry: every 60 seconds for 30 minutes
- After 30 minutes still failing: SYSTEM_ERROR WorkItem created for IT_ONCALL; supervisor dashboard flag
- **Verify:** DMS failure does NOT halt claim processing; it is a compliance and record-keeping risk, not a processing blocker

---

### V6-05 — CV-002 CheckExclusions SOAP Failure
**Given:** Claim has passed PL-001 (policy found, ACTIVE) and CV-001 (claim_type in coverage_types, incident_date in period). CheckExclusions SOAP call returns SERVICE_UNAVAILABLE on all retry attempts.

**When:** CV-002 exhausts retries

**Then:**
- SOAP_FAILURE WorkItem created; processing_status = HALTED; IT_ONCALL alerted
- No severity scoring begins; no routing proceeds
- coverage_status is NOT set (remains null — exclusion status unverified)
- INTERIM acknowledgment sent if not already sent (claim is halted, no adjuster assigned)
- **Verify:** CheckExclusions SOAP failure does NOT set coverage_status = CONFIRMED or treat excluded = false — coverage cannot be cleared when verification is unavailable
- **Verify:** When IT resolves the SOAP issue and supervisor re-queues the claim, processing resumes from COVERAGE_VALIDATION (CV-002 re-runs), not from the beginning of the pipeline

---

## V7 — Concurrency

### V7-01 — Same Claim Received via Two Channels Simultaneously
**Given:** Claimant submits web form at 10:00:00 AND calls at 10:00:30, transcript uploaded at 10:02:00; same policy_number, same incident_date, both processed simultaneously

**When:** Both are processed

**Then:**
- First receipt (web form, 10:00:00): creates Claim with unique ID; processing begins
- Second receipt (transcript, 10:02:00): IN-002 completes parsing successfully; IN-003 then runs and detects matching policy_number + incident_date + claimant contact within 10-minute window; flags as potential duplicate
- DUPLICATE_DETECTED event logged; specialist notified; second claim held for manual deduplication
- Only one claim proceeds to full processing
- **Verify:** deduplication check uses policy_number + incident_date + claimant_id (not source_channel) as the key — this is IN-003 (business-logic deduplication). The two submissions arrive on different channels and have different source_message_ids (web form submission token vs. phone transcript upload session ID), so IN-001's source_message_id idempotency check does not trigger. IN-003's content-based matching is the correct deduplication mechanism for this cross-channel scenario.

---

### V7-02 — Two Specialists Edit the Same WorkItem Simultaneously
**Given:** FIELD_COMPLETION WorkItem assigned to Specialist A; Specialist B opens and begins editing the same WorkItem 30 seconds later (after A but before A submits)

**When:** Both submit their resolutions

**Then:**
- First submit (A, at 10:05:30): resolution recorded; WorkItem status = RESOLVED
- Second submit (B, at 10:05:45): system detects WorkItem already in RESOLVED state; B's submission rejected with error "This WorkItem has already been resolved"
- AuditEvent records both submission attempts; only A's is recorded as the resolution
- **Verify:** optimistic locking or status check prevents double-resolution of a WorkItem

---

## V8 — Post-Launch Monitoring (Drift Detection)

These checks run continuously in production; they are not one-time tests.

### V8-01 — NLP Extraction Accuracy Drift
**Signal:** Monthly labeled-set accuracy for claim_type classification drops ≥ 3 percentage points below the baseline established in Phase 0 shadow mode; OR falls below 90% absolute (floor regardless of baseline).
**Trigger threshold:** Any single month triggering either condition above.
**Baseline establishment:** Baseline is set at the end of Phase 0 shadow mode (first 4 weeks). If baseline comes in below 93% (the year-1 target), the Phase 1 go/no-go decision must be reviewed — do not proceed to autonomous processing if shadow-mode accuracy is already below target.
**Response:** Retrain or fine-tune NLP model on recent claims data. Lower PARSE_CONFIDENCE_THRESHOLD temporarily to route more claims to FIELD_COMPLETION while retraining completes.
**Why this matters:** If the company expands into new lines of business (commercial trucking, marine) or new terminology enters claim descriptions, the pre-trained model's vocabulary distribution shifts. Drift is invisible until accuracy metrics drop.

### V8-02 — Routing Error Rate Monitoring
**Signal:** Monthly routing accuracy audit (n=200 sample) shows adjuster confirmed wrong > 2% (the ≤ 2% year-1 target).
**Trigger threshold:** Any month above 2%; two consecutive months above 1.5% (early warning).
**Response:** Review recent WorkItem FIELD_OVERRIDDEN_BY_HUMAN events for systematic claim_type misclassification patterns; recalibrate scoring weights if needed.

### V8-03 — Coverage False-Clear Rate
**Signal:** Quarterly reconciliation: claims autonomously cleared (coverage_status = CONFIRMED by agent, no human review) that subsequently raised a coverage dispute.
**Trigger threshold:** Rate exceeds 1% in any quarterly reconciliation.
**Response:** Immediate reduction of EXCLUSION_SIMILARITY_THRESHOLD (lower it to flag more claims for COVERAGE_REVIEW) while root cause is identified.

### V8-04 — SLA Breach Pattern
**Signal:** Weekly SLA compliance rate drops below 92% (below the 95% target, with 3-point buffer for early warning).
**Trigger threshold:** Two consecutive weeks below 92%.
**Response:** Review AWAITING_* queue depths and WorkItem resolution times; check if specialist team has been reduced or redeployed.

---

## Production Readiness Thresholds

All of the following must be true before go-live:

| Criterion | Threshold | Test |
|---|---|---|
| Field extraction accuracy (labeled set, n=500) | ≥ 95% correct on required fields | V2 suite + labeled historical claims data |
| SLA compliance in controlled pilot (n=200 claims) | ≥ 95% acknowledged within 2 hours | V1 + V5 suite |
| Routing accuracy (specialist review of n=200 autonomous routes) | ≥ 98% correct adjuster specialization and region | V1 + V4 suite |
| Bodily injury flag never autonomously routed (0 exceptions) | 100% | V4-02 |
| Coverage denial never set by agent (0 exceptions) | 100% | V4-04 |
| SOAP failure handled gracefully (no unhandled exceptions) | 100% | V6-01 |
| Duplicate claim detection (no duplicate Claim records) | 100% | V7-01 |
| INTERIM ack fires on AWAITING state entry | 100% | V5-03 |
All thresholds above must be met in a pre-production pilot of minimum 200 live claims with human shadow review before autonomous processing begins (Phase 0 → Phase 1 gate).

**Phase 1 → Phase 2 exit criterion (coverage false-clear rate):** Coverage false-clear rate cannot be statistically measured at n=200. Instead: after Phase 1 processes ≥ 1,000 autonomous claims, perform a reconciliation check (claims agent-cleared that subsequently raised a coverage dispute). If false-clear rate ≤ 1% at that point, proceed to Phase 2 full rollout. If > 1%: hold Phase 2; investigate root cause; lower EXCLUSION_SIMILARITY_THRESHOLD and re-run Phase 1.

**Statistical power note for coverage false-clear rate:** At n=200, a 1% false-clear rate corresponds to 2 expected events. The probability of observing 0 events from a true 1% rate is ~13% (Poisson approximation) — meaning the pilot could pass this threshold by chance even if the true rate is 1%. For a statistically valid measurement of a ≤ 1% rate, n ≥ 1,000 claims is required (95% confidence interval width ≈ ±0.6%). The coverage false-clear threshold must therefore be validated on a 30-day production sample of ≥ 1,000 autonomously processed claims, not solely on the initial pilot. Pilot evaluation uses the test suite (V3); production evaluation uses reconciliation data.

**Statistical power note for routing accuracy threshold:** At n=200, a 2% error rate corresponds to ~4 expected errors. The 95% binomial confidence interval for an observed 98% accuracy at n=200 spans approximately 95.3%–99.4% — meaning the pilot cannot reliably distinguish 98.0% from 96.0%. The go-live gate at ≥ 98% on n=200 confirms there is no catastrophic routing failure, not that the year-1 target is precisely achieved. Sustained measurement is provided by V8-02 (monthly n=200 audit); that rolling signal — not the one-time pilot — is the meaningful accuracy monitor over time. If a higher-confidence go-live gate is required, increase pilot sample to n=500 (95% CI ≈ ±1.2pp at 98% accuracy).

---

# Artifact 5 — Assumptions & Unknowns

## How to Read This Document

Every assumption is a bet. If the assumption is wrong, something in the spec breaks. The **Impact if Wrong** column tells you how badly. The **Status** column tells you what is known:

- `[Stated]` — explicitly confirmed in the scenario text
- `[Inferred]` — reasonable inference from context or industry knowledge; not yet validated
- `[Flagged for Validation]` — must be confirmed before building this component; proceeding without validation risks rework

---

## A — System & Integration Assumptions

### A1 — Legacy Policy Admin System Has Documented SOAP Operations
**Statement:** The policy administration system exposes GetPolicyByNumber and CheckExclusions SOAP operations (or functionally equivalent operations) with a WSDL available from the IT team. The coverage type codes in the policy admin system can be mapped to the FPA's internal claim_type enum.
**Why it matters:** The entire PL and CV modules depend on these SOAP calls. If the SOAP API has different operation names, different response schema, or no exclusion-check capability, the spec must be rewritten for those modules.
**Impact if wrong (no exclusion check operation):** CV-002 cannot be built as specified. Exclusion flagging must be implemented differently — possibly as a local rules table populated from the policy admin system's data export. This is a significant rework risk.
**Status:** `[Flagged for Validation]`
**Validation question:** "Can you share the WSDL and any existing API documentation for the policy admin system? Does it have an exclusion-check operation, or are exclusions returned as a list in the policy record itself?"

---

### A2 — Policy Admin Coverage Type Codes Map Cleanly to Claim Types
**Statement:** The coverage type codes in the legacy policy admin system can be deterministically mapped to the FPA's six internal claim_type values (AUTO_COLLISION, AUTO_THEFT, PROPERTY_DAMAGE, PROPERTY_THEFT, BODILY_INJURY, LIABILITY). This mapping is a deployment configuration item, not a runtime decision.
**Why it matters:** CV-001's coverage match logic is "claim_type ∈ policy coverage_types_list." If the legacy system uses codes like "HO3" or "PAP" that don't map cleanly, the FPA would need to implement a more complex coverage interpretation layer.
**Impact if wrong:** The mapping table must be jointly authored with the IT team and legal/underwriting before deployment. This is a documentation dependency, not a code dependency — but it blocks go-live.
**Status:** `[Flagged for Validation]`
**Validation question:** "What are the coverage type codes your policy admin system uses? Can you provide a list of all active coverage codes and their plain-language descriptions?"

---

### A3 — Base URLs and Credentials Available Before Development
**Statement:** IT will provide base URLs and authentication credentials for all three integrations (CRM, policy admin SOAP, DMS) before development begins. SOAP namespace strings are also included.
**Why it matters:** All integration contracts use placeholder URLs. Without real values, integration tests cannot run.
**Impact if wrong:** Development can proceed with mocks, but integration testing is blocked. Each unresolved URL is a delivery risk item.
**Status:** `[Flagged for Validation]`
**Validation question:** "Who is the IT contact who can provide API credentials and base URLs for Salesforce CRM, the policy admin SOAP service, and the DMS?"

---

### A4 — DMS Has a REST API for Document Storage
**Statement:** The document management system exposes an HTTP API for storing and retrieving claim documents. The scenario mentions a DMS but provides no API details.
**Why it matters:** IN-001 stores the raw claim input to DMS immediately on receipt. If the DMS has no API (e.g., it is a file-share system), the storage mechanism must be redesigned.
**Impact if wrong (DMS is file-share only):** Raw input storage becomes a file write operation. This is a simpler integration but changes the Integration 3 spec significantly. Non-blocking for core claim processing but affects audit record completeness.
**Status:** `[Flagged for Validation]`
**Validation question:** "Does the DMS have a REST API for programmatic document storage? If not, how is document storage currently automated (if at all)?"

---

### A5 — CRM Handles Outbound Email Acknowledgments
**Statement:** Salesforce CRM's Endpoint 4 (POST /communications) can send templated emails to claimants. If not, the FPA needs a separate SMTP integration or email service API for acknowledgments.
**Why it matters:** AC-001 sends the claimant acknowledgment via CRM. If CRM cannot send outbound email, an additional integration is required — and the 2-hour SLA delivery depends on that integration working reliably.
**Impact if wrong:** An additional integration contract (email service provider) must be added to the spec and the integration budget. Not a spec-breaking change but a scope addition.
**Status:** `[Inferred]` — Salesforce CRM typically has outbound email capability. Confirm with IT.

---

### A6 — CRM Adjuster Records Include Specialization, Region, and Queue Depth
**Statement:** CRM User records for adjusters include: (1) specialization (list of claim types they handle), (2) coverage_regions (list of state codes), (3) open_claims_count (maintained in real-time or near-real-time). RT-001's assignment algorithm depends on all three attributes being queryable via the CRM API.
**Why it matters:** RT-001 is the primary mechanism for eliminating the 18% routing error rate. If CRM adjuster records lack specialization or region data, the routing logic degrades to queue-depth-only matching — better than the current manual approach but less accurate.
**Impact if wrong (no specialization data):** Routing quality is reduced. A data enrichment project is required before go-live to populate adjuster attributes in CRM. This is a deployment dependency.
**Status:** `[Flagged for Validation]`
**Validation question:** "Do adjuster records in Salesforce CRM include specialization by claim type and geographic coverage regions? Is open claims count a maintained field? If not, can these attributes be added before go-live?"

**Additional validation required (claimant contact records):** The `prior_claims_count` field returned by CRM Endpoint 1 (claimant lookup) must cover a rolling 365-day window to match SERIAL_CLAIMANT_WINDOW_DAYS. If the field is a lifetime count, the SERIAL_CLAIMANT fraud signal will be systematically over-triggered for long-standing customers. Confirm with CRM admin before build.

---

### A7 — Inbound Event Deduplication Keys Are Available per Channel
**Statement:** Each inbound channel provides a stable, unique identifier that the FPA can use to detect webhook retries and double-submissions: EMAIL channels provide a MIME Message-ID header; the phone transcript upload system provides a session ID with each upload; and the web form system generates a unique submission token per submission.
**Why it matters:** Without idempotency keys, a webhook retry (common in event-driven architectures under transient failure) creates two Claim records for the same FNOL. IN-003 (duplicate detection) operates on business-logic duplicates (same claimant, same incident), not on technical duplicates (same webhook fired twice). A technical duplicate would pass IN-003's check because the second Claim would be created before IN-003 runs.
**Impact if wrong (no unique IDs available):** The FPA must implement a client-side deduplication strategy based on hash of raw_input content + received_at window. This is less reliable than server-side idempotency keys and adds implementation complexity.
**Status:** `[Flagged for Validation]`
**Validation question:** "Does the email webhook include a Message-ID or equivalent unique event identifier? Does the transcript upload API include a session or upload ID? Does the web form system generate unique submission tokens?"

---

## B — Business Rule Assumptions

### B1 — High-Value Threshold is $50,000 Estimated Loss
**Statement:** A claim is classified as "high-value" (requiring supervisor review before routing) if the estimated loss amount stated in the claim is ≥ $50,000.
**Why it matters:** The HIGH_VALUE_THRESHOLD directly controls how many claims go through the AWAITING_SEVERITY_REVIEW path. At $50K, approximately 10–15% of claims would trigger the threshold [Inferred — no historical claim-value distribution was provided in this engagement; this estimate is indicative only]. Lowering the threshold to $25K would increase that share materially; raising it to $100K would reduce it [Inferred].
**Source:** Working threshold selected in this draft for buildability. Not confirmed in a formal policy document.
**Impact if wrong:** Either too many claims in human review queue (threshold too low → throughput degraded) or high-value claims being autonomously routed (threshold too high → financial exposure).
**Status:** `[Flagged for Validation]`
**Validation question:** "Is $50,000 estimated loss the formal threshold for 'high-value' claim review? Is the threshold uniform across claim types, or does it differ (e.g., lower for liability, higher for property)?"

---

### B2 — Bodily Injury Always Requires Human Review, Regardless of Financial Value
**Statement:** Any claim where bodily injury is mentioned — regardless of estimated loss amount — is held for supervisor review before adjuster routing. This applies even for seemingly minor injuries (e.g., "I have a small bruise").
**Why it matters:** This is the C2 hard constraint in this draft. If the business later decides that minor injury claims can be auto-routed, the SV-002 escalation logic must be updated. The current spec treats this as binary (bodily_injury_flag = true → always escalate).
**Impact if wrong (if there is a severity threshold for bodily injury):** A graduated approach would be needed: e.g., self-reported minor injury at LOW severity could be auto-routed to a combined auto/injury adjuster. This would increase autonomous handling rate but requires a more nuanced escalation rule.
**Status:** `[Inferred — draft boundary choice pending stakeholder validation]`
**Validation question:** "Is any bodily injury claim a hard escalation regardless of apparent severity, or is there a threshold (e.g., hospitalisation required) below which bodily injury claims can be auto-routed?"

---

### B3 — Coverage Denial is a Human-Only Decision with Regulatory Basis
**Statement:** No AI agent can autonomously deny coverage on a claim. The agent can identify a clear coverage exclusion (coverage_status = EXCLUDED), but a human specialist must review and confirm the denial before any communication is sent to the claimant. This has a regulatory basis under state insurance regulations.
**Why it matters:** This is the C1 hard constraint. If this is wrong — e.g., if for certain clear-cut exclusions the regulatory framework permits automated denial — then coverage_status = DENIED could potentially be set autonomously for some claim types. The current spec treats this as absolute.
**Impact if wrong (upside):** For very clear exclusions (e.g., policy explicitly cancelled before incident date), autonomous denial processing would increase throughput and reduce the AWAITING_COVERAGE_REVIEW queue. But this is a significant legal risk to take on without explicit regulatory sign-off.
**Status:** `[Inferred — conservative legal-control choice; regulatory basis not specifically cited in scenario]`
**Validation question:** "Is coverage denial automation prohibited by regulation in your operating states, or is it an internal policy choice? Has legal reviewed this constraint?"

---

### B4 — Regulatory Exposure from SLA Non-Compliance
**Statement:** The 2-hour acknowledgment SLA may be tighter than many state DOI regulatory floors (which vary by state and line of business). Financial exposure should be treated primarily as audit/remediation risk unless legal confirms direct per-breach penalties for specific jurisdictions.
**Why it matters:** This underpins the regulatory compliance value lever in the business case. If any operating states have a 2-hour acknowledgment requirement in regulation, the per-breach financial exposure could be significant. If no states have this requirement, the regulatory risk is audit risk, not direct fine risk.
**Impact if wrong (if fines apply):** Financial exposure is higher, strengthening the business case. If fines do NOT apply, the regulatory lever is reframed as "audit risk reduction" rather than direct financial exposure.
**Status:** `[Inferred — requires legal and compliance validation with state-level citations]`
**Validation question:** "In which states does the company operate? Do any operating states have regulations requiring FNOL acknowledgment within 2 hours or faster? What were the specific findings in the last DOI audit?"

---

### B5 — Phone Transcripts Are Post-Call, Not Real-Time
**Statement:** When a claimant calls to report a loss, the call is handled by a call centre agent (not the FPA). After the call, a transcript is uploaded to the intake system, at which point the FPA begins processing. The FPA does not process calls in real-time.
**Why it matters:** If phone transcripts are available in real-time (i.e., from a live transcription feed), the FPA could begin processing during the call — potentially acknowledging the claimant before they hang up. This would significantly change the SLA profile for the phone channel.
**Impact if wrong (real-time transcription available):** A real-time processing path could be added as a Phase 2 enhancement. V1 is designed for post-call uploads, which is the simpler and more reliable integration pattern.
**Status:** `[Inferred — standard call centre practice; not stated in scenario]`
**Validation question:** "Does the call centre use real-time transcription? Is the transcript available immediately on call completion, or is there a processing delay before upload? Who uploads the transcript — the agent, or is it automated?"

---

### B6 — Human Override Authority Boundaries
**Statement:** When a specialist resolves a FIELD_COMPLETION WorkItem, they may correct any extracted field including claim_type, incident_date, and estimated_loss_amount — even if the agent's confidence was above the parse threshold. When a supervisor resolves a SEVERITY_REVIEW WorkItem, they may override the agent's severity_level and modify the routing recommendation. These overrides are the full extent of human authority within the FPA; no role may change coverage_status to DENIED without going through a COVERAGE_REVIEW WorkItem.
**Why it matters:** If override authority is ambiguous, specialists may feel uncertain about whether they are allowed to change a high-confidence extraction, and may leave errors uncorrected rather than risk "overriding the system." Alternatively, if override authority is too broad, a supervisor could bypass the coverage denial constraint by changing coverage_status directly.
**Impact if wrong:** The WorkItem resolution UI must be designed to permit the authorized overrides and block the prohibited ones. This is a UI requirement that must be specified before the human-in-the-loop interface is built.
**Status:** `[Inferred — pending stakeholder confirmation of override scope]`
**Validation question:** "Can a specialist change a claim_type that the agent extracted at high confidence? Can a supervisor downgrade a CRITICAL severity to HIGH during SEVERITY_REVIEW? Are there any fields on the Claim record that no human role may edit directly?"

---

## C — Operational Assumptions

### C1 — Operating Hours and SLA Calibration
**Statement:** The claims operations centre operates during business hours (assumed Monday–Friday, 08:00–18:00 local time). WorkItem SLAs (e.g., 20 min for FIELD_COMPLETION, 30 min for SEVERITY_REVIEW) count only during operating hours. The 2-hour FNOL SLA applies 24/7 (claims arrive at any time and must be acknowledged within 2 hours regardless of whether it is business hours).
**Why it matters:** If claims arrive outside business hours and no specialist is available, the 2-hour SLA cannot be met for claims requiring human WorkItem resolution (AWAITING_* states). An INTERIM acknowledgment is always sent autonomously, but if specialist review is required, the SLA may breach overnight.
**Impact if wrong (24/7 operations):** WorkItem SLA calibration is straightforward for 24/7. If the centre is business-hours-only, the spec must define a "business hours SLA" vs. a "calendar SLA" and clarify what happens to claims received overnight (next-day queue vs. after-hours on-call).
**Status:** `[Flagged for Validation]`
**Validation question:** "What are the claims centre's operating hours? Is there an after-hours on-call team for urgent claims? How are overnight claims currently handled?"

---

### C2 — Specialists Have Individual User Accounts in the CRM
**Statement:** Each specialist logs in with a unique CRM user ID. WorkItem assignment (assigned_to) is per-person, not per-station or per-team. This enables per-specialist quality tracking (field completion accuracy, coverage review outcomes) over time.
**Why it matters:** The WorkItem assignment algorithm selects by least-loaded individual. If specialists share login accounts, assignment cannot be personalised and quality tracking is lost.
**Impact if wrong:** WorkItem assignment must fall back to role-level (assign to SPECIALIST team, first available). Quality tracking by individual is lost. This is a configuration issue, not a spec-breaking change.
**Status:** `[Inferred]`

---

### C3 — Claim Reference Number Format and Acknowledgment Templates
**Statement:** The claim reference number format used in acknowledgments is "FNOL-{YYYY}-{UUID_SHORT}" (first 8 chars of UUID). The acknowledgment email templates (FNOL_ACK_FULL_V1 and FNOL_ACK_INTERIM_V1) must be authored in the CRM before go-live. The 24/7 emergency line number referenced in acknowledgments must be confirmed with operations.
**Why it matters:** AC-001 sends acknowledgments using these templates. If templates are not loaded in CRM, acknowledgments cannot be sent. The emergency line number is a hardcoded configuration item.
**Impact if wrong (templates not ready):** Go-live is blocked until templates are configured. This is a deployment dependency, not a builder dependency.
**Status:** `[Flagged for Validation — deployment dependency]`
**Validation question:** "Who will author the FNOL acknowledgment email templates in Salesforce CRM before go-live? What is the correct 24/7 claims emergency line number to include?"

---

## D — Scope & Design Assumptions

### D1 — NLP Extraction Accuracy is Sufficient Without Custom Training
**Statement:** An off-the-shelf NLP model (or a pre-trained insurance-domain model) can extract the required fields (policy number, claim type, incident date, estimated loss, bodily injury flag) from FNOL claim text with sufficient accuracy to achieve the ≥ 95% extraction accuracy threshold. Custom model training on the company's historical FNOL data is a Phase 2 option if V1 accuracy is insufficient.
**Why it matters:** The parse_confidence threshold (0.90) determines how many claims fall into the AWAITING_FIELD_COMPLETION path. If extraction accuracy is lower than expected, more claims require human field completion, reducing the autonomous handling rate.
**Impact if wrong:** The FIELD_COMPLETION WorkItem queue grows, specialists spend more time on field completion than routing — a different bottleneck from today, but still a bottleneck. Phase 2 custom model training would resolve this.
**Status:** `[Inferred — off-the-shelf NLP performance on insurance text is well-documented; custom training improves but may not be necessary for V1]`

---

### D2 — Volume Distribution is Relatively Uniform During Operating Hours
**Statement:** 300 claims/day arrive with some variation but without extreme concentration at specific times. Peak arrival rate is estimated at no more than 1.5× the average rate for any sustained 30-minute window [Inferred — no arrival distribution data was provided in this engagement; this multiplier reflects typical web and email submission patterns and is used to calibrate the SLA monitoring frequency and queue handling design].
**Why it matters:** The SLA monitoring (AC-002) fires every 5 minutes and the autonomous processing path is designed for near-real-time throughput. If claims arrive in large batches (e.g., 150 claims in the first 30 minutes of the operating day), queue depth and SLA performance may differ significantly from the steady-state model.
**Impact if wrong (extreme batching):** The architecture may need queue-depth-based scaling to handle peak arrival. This is an infrastructure decision for the builder.
**Status:** `[Inferred — email and web form submissions typically distribute through the day; phone transcripts depend on call centre hours]`

---

### D3 — Severity Score Calibration Thresholds Have No Historical Basis
**Statement:** The severity scoring thresholds (LOW: 1–3, MEDIUM: 4–5, HIGH: 6–7, CRITICAL: ≥ 8) and the scoring weights (e.g., bodily_injury = +3, estimated_loss ≥ $150K = +6) were selected for internal consistency and buildability, not calibrated against historical claims data.
**Why it matters:** A threshold of CRITICAL ≥ 8 means that a $150K property-damage claim with no injury scores exactly HIGH (6 points), while the same claim combined with bodily injury scores CRITICAL (9 points). Whether this boundary is correct depends on historical outcome data — does the HIGH/CRITICAL distinction predict adjuster assignment errors or litigation exposure? If not, the scoring weights should be recalibrated.
**Impact if wrong:** Miscalibrated thresholds would send too many or too few claims to SEVERITY_REVIEW, affecting both specialist workload and claims quality. A threshold set too low overloads the review queue; too high lets high-risk claims route autonomously.
**Status:** `[Flagged for Validation — requires calibration against historical claims data before or during pilot]`
**Validation question:** "Do you have historical FNOL data that includes final outcome (litigation / coverage dispute / adjuster reassignment) that could be used to validate whether HIGH/CRITICAL severity claims actually had worse outcomes? Can the scoring weights be compared against the specialist team's intuitive routing rules?"
See also Assumption D5 for the broader configuration parameter calibration dependency.

---

### D4 — CRM Adjuster Queue Depth Is Maintained in Near-Real-Time
**Statement:** The `open_claims_count` field returned by CRM Endpoint 2 (adjuster query) reflects the adjuster's current workload accurately enough for the assignment algorithm to rely on. Specifically: a claim assigned to an adjuster in the last 30 seconds is reflected in that adjuster's open_claims_count before the next routing decision is made.
**Why it matters:** RT-001's filter `open_claims_count < MAX_ADJUSTER_QUEUE_SIZE` is the primary mechanism preventing adjuster overload. If open_claims_count is eventually consistent with a lag of several minutes, the FPA might assign a 16th claim to an adjuster it believes has 14 — exceeding the configured limit. Under high volume (claims arriving faster than CRM cache updates), multiple claims could be simultaneously routed to the same adjuster.
**Impact if wrong (significant lag):** The FPA must implement optimistic concurrency control: after assigning a claim, increment a local counter and use it for subsequent routing decisions until CRM confirms. Or: accept that queue limits are approximate and set MAX_ADJUSTER_QUEUE_SIZE conservatively (e.g., 12 instead of 15).
**Status:** `[Flagged for Validation]`
**Validation question:** "When the FPA creates a CRM claim record (RT-002) and assigns an adjuster, how quickly does the adjuster's open_claims_count update in CRM? Is it real-time, or is there a sync delay? Does Salesforce CRM expose a real-time event for assignment updates?"

---

### D5 — Configuration Parameter Defaults Are Uncalibrated
**Statement:** All numeric thresholds in the Configuration Parameters table (Artifact 3) — PARSE_CONFIDENCE_THRESHOLD (0.90), EXCLUSION_SIMILARITY_THRESHOLD (0.75), MAX_ADJUSTER_QUEUE_SIZE (15), SLA_AT_RISK_BUFFER_MINUTES (30), SERIAL_CLAIMANT_WINDOW_DAYS (365), SERIAL_CLAIMANT_THRESHOLD (5), DUPLICATE_WINDOW_MINUTES (10) — are initial build estimates. None was derived from this company's historical claims data. The HIGH_VALUE_THRESHOLD ($50,000) is treated separately under Assumption B1.
**Why it matters:** Each threshold directly controls operational behaviour. PARSE_CONFIDENCE_THRESHOLD determines how many claims fall to FIELD_COMPLETION specialist workload; EXCLUSION_SIMILARITY_THRESHOLD determines false-clear rate; SERIAL_CLAIMANT_THRESHOLD calibrates fraud-signal sensitivity. A threshold calibrated for a generic insurer may systematically over-route or under-route for this company's claim profile.
**Impact if wrong:** Miscalibrated thresholds produce the wrong mix of autonomous vs. human-reviewed claims — either overloading the specialist queue (threshold too sensitive) or routing claims that should be reviewed (threshold too permissive). The primary calibration mechanism is Phase 0 shadow mode: run the agent against the 4-week pilot, compare autonomous outputs to specialist decisions, then adjust thresholds before Phase 1 go/no-go.
**Status:** `[Flagged for Calibration — required before Phase 1 go/no-go]`
**Validation question:** "Can you provide 3–6 months of historical FNOL data with specialist routing outcomes (claim type assigned, adjuster assigned, final coverage decision) for threshold calibration before build begins?"

---

## Summary: What Must Be Validated Before Building

**Priority 1 (blocks building):**
- A1 — SOAP operations exist and are documented (required for PL and CV modules)
- A3 — Base URLs and credentials available
- A6 — CRM adjuster attributes (specialization, region, queue depth) are populated
- A7 — Inbound event deduplication keys available per channel
- B1 — High-value threshold formally confirmed

**Priority 2 (blocks accurate operations):**
- A2 — Coverage type code mapping confirmed with IT and underwriting
- A4 — DMS API confirmed
- B5 — Phone transcript upload mechanism confirmed
- C1 — Operating hours and after-hours handling defined
- D3 — Severity score calibration validated against historical claims data
- D4 — CRM adjuster queue depth refresh latency confirmed
- D5 — All configuration thresholds calibrated against Phase 0 shadow data before Phase 1 go/no-go

**Priority 3 (affects go-live readiness but not build):**
- A5 — CRM outbound email confirmed
- B6 — Human override authority boundaries confirmed and reflected in UI design
- C3 — Acknowledgment templates authored; emergency line confirmed
- B3 — Regulatory basis for coverage denial constraint confirmed with legal
