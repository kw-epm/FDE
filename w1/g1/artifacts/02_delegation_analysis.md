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
**Justification:** This is a deterministic database lookup. The result is either a policy record or it is not. No judgment required. Automating this step alone eliminates 2–4 minutes per claim on all successful lookups.

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

**The coverage denial boundary** sits at human-always because of explicit regulatory basis — this is not a "feels like a human decision" call. Any spec that allows the agent to deny coverage will fail legal review.

**The bodily injury boundary** sits at human-always (pre-routing) because the litigation exposure of routing a bodily injury claim to the wrong adjuster — or to a general adjuster who mishandles the initial contact — outweighs the throughput cost of a supervisor confirmation. This is a conservative design constraint and should be validated with operations/legal owners. **It may be relaxed in V2:** if operations validates that self-reported minor injuries (no hospitalisation, no third party) can be auto-routed to a bodily-injury-qualified adjuster, the C2 constraint becomes a severity sub-threshold rather than a binary flag. The current spec treats it as binary pending that validation [Assumption B2].

**The $50,000 boundary** sits at flag-and-hold because at this financial level, a routing error has a material margin consequence and the cost of a 3–5 minute supervisor confirmation is negligible by comparison. This is a working assumption pending formal policy documentation.

**The acknowledgment boundary** is drawn at always-autonomous because decoupling acknowledgment from routing completion is the primary mechanism by which the 31% SLA breach rate gets resolved. Claimants cannot wait for human review to complete before they are acknowledged.
