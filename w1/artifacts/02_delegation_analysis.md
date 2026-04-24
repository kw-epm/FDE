# Artifact 2 — Delegation Analysis

## The Core Question

Which parts of the returns processing workflow should become fully agentic, which should be agent-led with human oversight, and which must remain human-led? This is not a question of what AI *can* do — it's a question of what *should* be delegated, given the specific risk profile, compliance constraints, and business context of this retailer.

---

## The Hard Constraints (Non-Negotiable)

These constraints were confirmed in stakeholder discovery and cannot be softened in the spec:

**C1 — No autonomous fraud disposition.**
> Any return with 2+ fraud signals must be held and routed to Loss Prevention for human decision. The agent cannot approve, reject, or disposition a fraud-flagged return. (Source: VP of Operations, hard rule confirmed by prior incident.)

**C2 — High-value items require human review.**
> Items with original retail price ≥ $100 require human confirmation of condition grade and disposition before processing. (Source: VP of Operations, $100 threshold indicated — pending formal confirmation.)

**C3 — Escalated returns require human oversight.**
> Any return associated with a customer service escalation (contact centre flag in OMS) must be reviewed by a returns supervisor before disposition. (Source: VP of Operations — "there's a relationship risk.")

These three constraints define the floor. Everything above the floor is a design choice.

---

## Delegation Framework

Every decision point in the returns workflow is categorized as one of:

| Label | Meaning |
|---|---|
| **[Agent — Autonomous]** | Agent decides and acts; no human needed before disposition |
| **[Agent — Log & Monitor]** | Agent decides and acts; decision is logged for human audit; human can override retroactively |
| **[Agent — Flag & Hold]** | Agent makes a recommendation and holds the item; human confirms before action |
| **[Human — Decide]** | Agent gathers and presents; human makes the call |

---

## Decision-by-Decision Analysis

### 1. Item Identification (barcode scan → SKU lookup)

**Decision:** Match scanned barcode to SKU in OMS.  
**Delegation:** **[Agent — Autonomous]**  
**Justification:** This is a deterministic lookup — either the barcode matches a record or it doesn't. There is no judgment involved. Error rate is near-zero when barcodes are intact.  
**Exception:** If barcode is unreadable or returns no OMS match → escalate to processor for manual identification. **[Human — Decide]**  
**Why not human?** Automating this step alone eliminates ~45 seconds per item on 65% of volume = significant throughput gain at zero risk.

---

### 2. Reason Code Classification

**Decision:** Assign one of 5 reason codes (DEFECTIVE, DIDNT_FIT, CHANGED_MIND, WRONG_ITEM, SUSPECTED_FRAUD) based on customer return text + order data.

**Sub-decision A — High-confidence classification (confidence ≥ 90%, no fraud signals):**
**Delegation:** **[Agent — Log & Monitor]**  
**Justification:** The majority of returns have unambiguous customer language and clear signal ("too small," "wrong color sent," "zipper broke day one"). Agent classifies and logs. Human audits a random sample (see Validation Design). Current human accuracy baseline is 78% — a well-designed classifier will exceed this on the high-confidence subset.

**Sub-decision B — Low-confidence classification (confidence < 90%, no fraud signals):**
**Delegation:** **[Agent — Flag & Hold]**  
**Justification:** Ambiguous customer language ("it just wasn't what I expected," "quality issue") is genuinely hard to classify. Better to surface it for human review than to log a guess. The 22% of current mis-classifications likely concentrate here.

**Sub-decision C — DEFECTIVE vs. CUSTOMER_DAMAGE:**
**Delegation:** **[Agent — Flag & Hold]** (always)  
**Justification:** This boundary is explicitly contested (confirmed by Returns Team Lead). There is no reliable way to distinguish manufacturer defect from customer-induced damage from text alone without physical inspection, and the financial and warranty implications differ. Default to human review until a formal policy is defined and encoded.  
**Dependency:** Requires client to define and provide a DEFECTIVE vs. CUSTOMER_DAMAGE decision rubric.

---

### 3. Fraud Signal Assessment

**Decision:** Evaluate whether the return shows fraud indicators.

**Sub-decision A — Fraud signal scoring (2+ signals):**
**Delegation:** **[Agent — Flag & Hold]** → **[Human — Decide]**  
**Justification:** Confirmed hard constraint (C1). The agent's role is to surface signals with evidence, not to render a verdict. Loss Prevention holds the decision.  
**Agent produces:** fraud signal list + confidence score + customer return history + SKU fraud rate (if available). Loss Prevention receives this in their review queue with all data consolidated in one view.

**Sub-decision B — Single fraud signal (1 signal):**
**Delegation:** **[Agent — Log & Monitor]**  
**Justification:** Single signals have high false-positive rate (confirmed by Loss Prevention Manager: "one signal is noise"). Agent logs the signal against the return record for potential retroactive review, but does not hold the item. This creates the chargeback feedback loop that Loss Prevention requested.

**Sub-decision C — No fraud signals:**
**Delegation:** **[Agent — Autonomous]** (continues normal processing)

---

### 4. Physical Condition Grading

**Decision:** Assign a condition grade (LIKE_NEW, GOOD, FAIR, POOR, UNSELLABLE) to the returned item.

**Context:** The intake station has **no camera** (confirmed by VP). The agent cannot visually inspect the item. The agent receives: item SKU, customer-provided reason text, and — if implemented — a structured condition input that the processor selects from a drop-down at the scan station.

**This is the most constrained decision in the entire workflow.**

**Approach:** The agent does not independently grade condition. Instead, it:
1. Presents the processor with the standardized condition rubric for this specific SKU category (e.g., outerwear grading guide vs. footwear grading guide)
2. The processor selects a condition grade from the rubric
3. The agent validates the grade against the customer's return reason for consistency (e.g., LIKE_NEW + DEFECTIVE is inconsistent → flag for review)
4. For high-value items (≥ $100 retail), an additional confirmation step is required (C2 constraint)

**Delegation:** **[Agent — Flag & Hold]** (agent assists, human confirms grade)  
**Justification:** Without image capture, the agent cannot be autonomous on condition. Attempting to predict condition from text alone would introduce new errors. The agent's value here is: presenting the rubric (reducing inter-processor variance), validating consistency (catching grade/reason conflicts), and enforcing the high-value confirmation gate.

**Future state (not in V1 scope):** Image capture at intake station would enable autonomous condition grading for clear-cut cases. This should be raised as a Phase 2 recommendation.

---

### 5. Disposition Routing

**Decision:** Route item to one of 5 disposition lanes: RESTOCK_AS_NEW, OUTLET, REFURBISH, DONATE, DESTROY.

**Delegation matrix:**

| Condition + Reason | Disposition | Delegation |
|---|---|---|
| LIKE_NEW + any non-fraud, retail price < $100 | RESTOCK_AS_NEW | **[Agent — Autonomous]** |
| GOOD + DIDNT_FIT or CHANGED_MIND, retail price < $100 | RESTOCK_AS_NEW or OUTLET per routing table | **[Agent — Autonomous]** |
| GOOD + DEFECTIVE | REFURBISH (quality check) | **[Agent — Log & Monitor]** |
| GOOD + WRONG_ITEM | RESTOCK_AS_NEW | **[Agent — Autonomous]** |
| FAIR + any non-fraud | OUTLET | **[Agent — Log & Monitor]** |
| POOR + any | REFURBISH or DONATE | **[Agent — Flag & Hold]** (REFURBISH vs. DONATE is policy-dependent) |
| UNSELLABLE + any | DESTROY | **[Agent — Flag & Hold]** (destruction is irreversible) |
| Any condition + retail price ≥ $100 | Any | **[Agent — Flag & Hold]** (C2 constraint) |
| Any condition + 2+ fraud signals | HOLD | **[Human — Decide]** (C1 constraint) |
| Any condition + customer escalation flag | Any | **[Agent — Flag & Hold]** (C3 constraint) |

**Justification for DESTROY requiring human confirmation:**  
Destruction is irreversible. An agent error on a DESTROY routing cannot be undone. Even if the condition clearly warrants destruction, a human confirmation step adds minimal friction (one click) against an irreversible consequence.

---

### 6. Documentation & Audit Logging

**Decision:** Record the classification, condition, disposition, and any flags to the WMS and OMS.

**Delegation:** **[Agent — Autonomous]** (always)  
**Justification:** Logging is mandatory, deterministic, and should never require human judgment. Every agent action and every human confirmation is logged with: timestamp, action type, agent/user ID, item ID, and any override reason. This is a governance requirement, not a feature.

---

## Summary: Autonomous vs. Human Workload

| Workload type | Estimated % of volume | Delegation |
|---|---|---|
| Clear classification, low-value, no fraud | ~55–60% | Agent — Autonomous |
| Clear classification, log + monitor | ~10–12% | Agent — Log & Monitor |
| Ambiguous classification, needs human confirm | ~8–10% | Agent — Flag & Hold |
| High-value items (≥ $100) | ~10–12% | Agent — Flag & Hold |
| Fraud flags (2+ signals) | ~1–2% | Human — Decide (Loss Prevention) |
| Customer escalations | ~1–2% | Agent — Flag & Hold (supervisor) |
| DESTROY routing | ~2–3% | Agent — Flag & Hold (single confirmation) |
| Unreadable barcode / no OMS match | ~2–3% | Human — Decide |

**Net autonomous rate: ~65–72%** — consistent with VP estimate of "70% are easy cases."  
**Human touchpoint rate: ~28–35%** — concentrated in high-value, fraud, ambiguous, and irreversible decisions.

**How this maps to Artifact 1’s “autonomous handling rate”:** That KPI means **no `HOLD_REVIEW` / `HOLD_FRAUD` / exception queue** for the item — not “no human at the station.” Scans, rubric-based grading, and required confirm clicks still happen; they are expected.

---

## Why These Boundaries Are Drawn Here

**The fraud boundary** sits at the fraud signal threshold (2+ signals) because: below this, the signal-to-noise ratio doesn't justify holding items; above this, the VP's hard constraint (C1) applies. The single-signal log-and-monitor approach is a deliberate middle path that preserves Loss Prevention's data without creating false-positive queue overload.

**The high-value boundary** sits at $100 because: the VP indicated this threshold; at this price point, a routing error has material margin impact (a $150 jacket routed to OUTLET loses ~$60 in recovery); and the cost of the human confirmation step (30 seconds) is negligible against the risk.

**The DESTROY boundary** sits at human confirmation because: destruction is the only irreversible disposition; all others (outlet, refurbish, donate) can be corrected post-facto if an error is discovered; destruction cannot.

**The condition boundary** sits at human-always because: no camera, no image data, no autonomous vision — the agent cannot assess physical condition independently. Any spec that claims otherwise would be undeliverable.
