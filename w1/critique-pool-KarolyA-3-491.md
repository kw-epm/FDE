# Artifact 1 — Problem Statement & Success Metrics

## The Business Problem

A mid-sized apparel retailer ($280M revenue, 60 stores + online) processes ~234,000 returned items per year through a 12-person manual team at a central returns facility. The process — reason-code classification, condition inspection, and disposition routing — is executed entirely by human judgment, from memory, with no supporting tooling. The result is a compounding failure across three dimensions:

1. **Accuracy failure**: Reason codes are wrong 22% of the time (~51,000 mis-classifications/year), degrading return analytics, corrupting inventory decisions, and creating a false baseline for fraud detection.

2. **Fraud failure**: Only 40% of fraudulent returns are detected at intake. The remaining 60% surface 30–60 days later in chargeback reports, after the merchandise has been processed and the refund issued. Estimated annual undetected fraud loss: $84K–$281K.

3. **Capacity failure**: The team runs near-capacity at current volume (900 items/day, ~6.5 min/item). Any volume spike — seasonal, promotional, or channel growth — creates backlogs without headcount increase.

Combined, return-related losses total approximately **$2.1M/year** (merchandise recovery losses, fraud losses, processing cost), per Finance.

---

## The User Perspective

**Who is affected:**

| Stakeholder | Current pain |
|---|---|
| Returns processors (12 FTEs) | ~75 items/day with no system support; all judgment, no consistency tools; new hires take 6–8 weeks to reach full accuracy |
| Loss Prevention (2 investigators) | Reviewing 15–20 manual fraud flags/week while 50–60 additional fraud cases only surface in chargeback reports — no time for retrospective review at scale |
| VP of Operations (Sandra K.) | Q4 backlogs, inconsistent quality, vulnerable to CFO scrutiny on fraud chargebacks, no capacity buffer |
| CFO (Maria C.) | Mandate: $400K year-one margin improvement with 18-month payback |

**What users actually need (not what they asked for):**

- Processors need a system that tells them what to do for the obvious cases so they can focus attention on the genuinely hard ones
- Loss Prevention needs fraud signals surfaced before disposition, with enough explainability to act on
- Operations leadership needs a real-time accuracy dashboard so they can trust the data they're making decisions with

---

## The Business Perspective

**Mandate:** Deliver $400K in margin improvement in year one, on a $2.1M loss base (19% improvement), with 18-month payback.

**Three value levers:**

### Lever 1 — Merchandise Recovery (~$225K potential year-one)
Finance confirmed **15% of restockable items** are misrouted to outlet or donate when they should have been full-price restock. That is a **subset** of the 234,000 annual items (the rest of the mix is already in acceptable lanes for those SKUs).  
**Opportunity (order of magnitude):** 234,000 × 15% = **35,100** items/year in the wrong recovery lane. At **$30** average margin left on the table per misrouted item (Finance estimate: full recovery vs. discount/donate) → 35,100 × $30 ≈ **$1.05M/year** total addressable.  
A **~50%** cut in that misrouting path once the agent and routing table are in use would recover on the order of **~$525K** at steady state; the business case uses a **conservative $225K in year one** to reflect ramp, partial category coverage, and execution risk.

### Lever 2 — Fraud Chargeback Reduction (~$70K–$140K potential year-one)
Current undetected fraud loss: $84K–$281K/year (at 1–2% fraud rate).  
If agent improves detection from 40% to 70% of detectable fraud cases: 30-percentage-point improvement on the detectable portion.  
Conservative year-one target (ramp): **$70K–$140K**.

### Lever 3 — Labor Redeployment (~$135K–$180K value year-one)
If agent handles 65% of volume autonomously, 12 processors handling 900 items/day could theoretically reduce to 5–6 processors handling exceptions + oversight.  
Redeployment of 5–6 FTEs to higher-value roles (customer experience, quality assurance) = $45K × 3–4 FTEs redeployed (not eliminated) = **$135K–$180K**.

**Combined year-one estimate: $430K–$545K** — above the $400K mandate, with headroom for implementation costs.

---

## Why an AI Agent Is the Right Solution

**Not traditional automation (scripted/RPA for *judgment*):** The classification logic involves natural language (customer return reason text), condition assessment from structured input, and fraud detection from pattern-matching across multiple data sources. A fixed script cannot maintain accuracy across the variance in how customers write reasons, how processors grade, and how multiple systems disagree. A rules-plus-model agent (as specified) is the right abstraction for that stack.

**Not a process redesign alone:** The root problem is not that the process is poorly designed — it's that the process requires consistent judgment at scale that 12 humans cannot reliably provide. Adding a rubric without a system to enforce it doesn't solve the accuracy problem.

**Not a hire:** Hiring more processors scales the cost linearly with volume and does not improve accuracy, fraud detection, or the CFO's payback story.

**An AI agent is right because:**
- The majority of cases (estimated 65–70%) are routine and follow predictable patterns that can be encoded as rules + ML classification
- The minority of hard cases (fraud, high-value, escalations) are where human judgment is irreplaceable — and the agent's job is to route them there reliably, not to replace that judgment
- The data the agent needs (customer return text, order history, SKU data, condition codes) is already in systems the retailer owns

---

## Measurable Success Criteria

### Accuracy Metrics (tracked in agent dashboard)
| Metric | Baseline | Year-1 Target | Measurement Method |
|---|---|---|---|
| Reason-code classification accuracy | 78% | ≥ 92% | Monthly random sample audit (n=200/month) compared to gold-standard reclassification |
| Restock-optimality / disposition routing (restockable pool) | ~85% optimal (implied by 15% misroute of that pool) | ≥ 95% | Monthly audit: agent + expert re-review of lane vs. model optimal lane for restockable items |
| Autonomous handling rate (no *review* escalation) | 0% | ≥ 65% | System log: % of items that complete the RDA path without `HOLD_REVIEW` / `HOLD_FRAUD` or other supervisor/exception WorkItem. Station tasks (scan, pick condition from rubric, high-value or DESTROY confirm clicks) are **in scope** and do not count against this metric. |

### Fraud Metrics (Loss Prevention dashboard)
| Metric | Baseline | Year-1 Target | Measurement Method |
|---|---|---|---|
| Fraud detection rate (items flagged at intake / total fraud attempts) | 40% | ≥ 70% | Quarterly reconciliation against chargeback reports |
| False positive rate (legitimate returns flagged as fraud) | Unknown | ≤ 5% | Monthly audit of escalated cases |
| Loss Prevention SLA compliance (review within defined SLA) | N/A | ≥ 95% | System log |

### Financial Metrics (Finance dashboard)
| Metric | Baseline | Year-1 Target | Measurement Method |
|---|---|---|---|
| Merchandise recovery rate (actual vs. optimal recovery) | ~85% | ≥ 94% | Finance: compare disposition mix to optimal routing model |
| Fraud chargeback losses | $84K–$281K/year | Reduction ≥ 50% | Finance: chargeback report vs. prior year |
| Processing cost per return | ~$2.31 (current team cost / volume) | ≤ $1.20 | Finance: fully loaded team cost / annual volume post-redeployment |

### Operational Metrics
| Metric | Baseline | Year-1 Target | Measurement Method |
|---|---|---|---|
| Average processing time per item | ~6.5 min | ≤ 2.5 min (agent-handled); ≤ 8 min (escalations) | System timestamp on item lifecycle |
| Peak capacity (items/day without backlog) | ~900 | ≥ 1,500 | Stress test during Q4 planning |
| Processor ramp-up time to full productivity | 6–8 weeks | ≤ 2 weeks | HR onboarding records |
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
# Artifact 3 — Agent Specification

## Agent Identity

**Name:** Returns Disposition Agent (RDA)  
**Version:** 1.0  
**Purpose:** Automate the classification, fraud assessment, condition validation, and disposition routing of returned merchandise items at the central returns facility. Reduce per-item processing time for routine cases, improve classification accuracy above the 78% human baseline, and surface fraud signals to Loss Prevention before disposition.

**Implementation scope note:** This spec defines *behavior* — what the agent decides, when it escalates,
what it writes to which systems, and what constitutes correct vs. incorrect output. Technology choices
(language, framework, database engine, deployment platform, UI framework) are the builder's decision
and are intentionally not prescribed here. The spec is implementation-agnostic.

**Scope (V1):**
- Inbound returns at the central facility only (not store-level returns)
- Items with a readable barcode that resolves to an OMS record
- The 5 defined reason codes and 5 condition grades
- Integration with Manhattan WMS, Salesforce Commerce Cloud OMS, Narvar returns portal

**Out of scope (V1):**
- Image-based condition assessment (no camera at station)
- In-store return processing
- Chargeback feedback loop (Phase 2)
- Refurbish workflow management (downstream of disposition routing)
- Returns from B2B / wholesale accounts

---

## Data Model

### Entity: ReturnItem
```
ReturnItem:
  id: UUID, primary key, immutable, generated on intake scan
  barcode: string, max 64 chars, required
  processing_status: enum [SCANNING, AWAITING_CONDITION, CLASSIFYING, AWAITING_REVIEW,
    AWAITING_LP_REVIEW, COMPLETED, HALTED], required, default SCANNING
    State machine:
      SCANNING → AWAITING_CONDITION  (RC-001 + RC-002 complete)
      AWAITING_CONDITION → CLASSIFYING  (CC-001 complete)
      CLASSIFYING → AWAITING_REVIEW  (RC-004 triggered)
      CLASSIFYING → AWAITING_LP_REVIEW  (FR-003 triggered)
      CLASSIFYING → COMPLETED  (all modules pass, autonomous path)
      AWAITING_REVIEW → CLASSIFYING  (processor resolves WorkItem, re-enters CC-002)
      AWAITING_LP_REVIEW → COMPLETED  (LP decision APPROVE or REJECT recorded)
      Any → HALTED  (RC-001 fails after all retries; item requires manual processing)
  sku_id: string, foreign key to ProductCatalog, required after barcode lookup
  order_id: string, foreign key to OMS Order, required after barcode lookup
  customer_id: string, foreign key to OMS Customer, required after barcode lookup
  original_retail_price: decimal(10,2), in USD, required after RC-001, populated from OMS barcode
    lookup response (not ProductCatalog — OMS is the authoritative price source)
  is_high_value: boolean, computed: true if original_retail_price >= 100.00, read-only
  reason_code: enum [DEFECTIVE, DIDNT_FIT, CHANGED_MIND, WRONG_ITEM, SUSPECTED_FRAUD, AMBIGUOUS] or null; null only when the flow is halted at RC-001 and no return record exists; otherwise required after classification
  reason_code_source: enum [CUSTOMER_PROVIDED, AGENT_CLASSIFIED, HUMAN_OVERRIDE], required
  reason_code_confidence: decimal(4,3), range 0.000–1.000, required when source = AGENT_CLASSIFIED
  customer_reason_text: string, max 2000 chars, optional (null if customer provided no text)
  condition_grade: enum [LIKE_NEW, GOOD, FAIR, POOR, UNSELLABLE], required after CC-001
    (nullable at creation; NOT NULL constraint enforced only after processing_status leaves AWAITING_CONDITION)
  condition_grade_assigned_by: reference to User (processor who entered grade), required after CC-001
  fraud_signals: array of FraudSignal, min 0 items
  fraud_signal_count: integer, computed: len(fraud_signals), read-only
  is_fraud_escalated: boolean, computed: true if fraud_signal_count >= 2, read-only
  is_customer_escalated: boolean, populated from OMS CRM flag, required
  disposition: enum [RESTOCK_AS_NEW, OUTLET, REFURBISH, DONATE, DESTROY, HOLD_FRAUD, HOLD_REVIEW], required
  disposition_source: enum [AGENT_AUTONOMOUS, AGENT_RECOMMENDED_HUMAN_CONFIRMED, HUMAN_OVERRIDE], required
  processor_id: reference to User, required (processor who handled the item)
  created_at: ISO 8601 timestamp, UTC, immutable
  updated_at: ISO 8601 timestamp, UTC
  completed_at: ISO 8601 timestamp, UTC, null until item fully dispositioned
```

**Note on `SUSPECTED_FRAUD`:** The RC-003 classifier only outputs `DEFECTIVE`, `DIDNT_FIT`, `CHANGED_MIND`, `WRONG_ITEM`, or `AMBIGUOUS`. The scenario’s “suspected fraud” path is implemented with **fraud signals** and `HOLD_FRAUD` / Loss Prevention, not with an agent-assigned `SUSPECTED_FRAUD` reason code. Humans may set `SUSPECTED_FRAUD` via override where the WMS still uses that code.

### Entity: FraudSignal
```
FraudSignal:
  id: UUID, primary key, immutable
  return_item_id: UUID, foreign key to ReturnItem, required
  signal_type: enum [SERIAL_RETURNER, HIGH_VALUE_NO_PACKAGING, SKU_HIGH_FRAUD_RATE,
    REASON_CONDITION_MISMATCH, CUSTOMER_RETURN_VELOCITY], required
  signal_detail: string, max 500 chars, required (human-readable explanation)
  signal_data: JSON object, required (structured evidence supporting the signal)
  confidence: decimal(4,3), range 0.000–1.000, required
  created_at: ISO 8601 timestamp, UTC, immutable
```

### Entity: WorkItem
```
WorkItem:
  id: UUID, primary key, immutable
  type: enum [MANUAL_IDENTIFICATION, REASON_CODE_REVIEW, HOLD_REVIEW, HOLD_FRAUD,
    DESTROY_CONFIRM, WMS_ROUTING_ERROR, SYSTEM_ERROR], required
  return_item_id: UUID, foreign key to ReturnItem, required
  status: enum [OPEN, IN_PROGRESS, RESOLVED, ESCALATED], required, default OPEN
  assigned_role: enum [PROCESSOR, SUPERVISOR, LOSS_PREVENTION, LP_MANAGER, IT_ONCALL],
    required (controls which users can claim/be assigned this item)
  assigned_to: UUID, foreign key to User, nullable (null = unassigned)
  content: JSON object, required (type-specific payload defined in the requirement that creates it)
  agent_recommendation: string, max 500 chars, optional
  resolution: string, max 1000 chars, optional (human free-text note on resolution)
  resolved_by: UUID, foreign key to User, null until resolved
  created_at: ISO 8601 timestamp, UTC, immutable
  updated_at: ISO 8601 timestamp, UTC
  sla_deadline: ISO 8601 timestamp, UTC, required
    (set at creation: sla_deadline = created_at + SLA duration from §Escalation Summary,
    counting only facility operating hours — see Assumption C3)
  escalated_at: ISO 8601 timestamp, UTC, null until escalated

  State machine:
    OPEN → IN_PROGRESS  (assigned user opens the item in UI)
    IN_PROGRESS → RESOLVED  (user submits resolution)
    OPEN or IN_PROGRESS → ESCALATED  (sla_deadline passes; system escalates; assigned_to
      updated to next-level role per §Escalation Summary)
    ESCALATED → RESOLVED  (escalation target resolves)
```

Note: `LossPreventionWorkItem` referenced elsewhere in this spec is a `WorkItem` with
`type = HOLD_FRAUD` and `assigned_role = LOSS_PREVENTION`. No separate entity.

### WorkItem Assignment Algorithm
When a WorkItem is created, `assigned_to` is set as follows:
1. Query active Users (`is_active = true`) with `role` matching `WorkItem.assigned_role`
2. Exclude users who have any WorkItem in status IN_PROGRESS at this moment
3. Among remaining eligible users, select the user with the fewest OPEN WorkItems (tie-break: user with the earliest `last_resolved_at` timestamp)
4. If no eligible user exists, set `assigned_to = null`; the system retries assignment every 60 seconds
5. If `sla_deadline - now < 25%` of original SLA duration and `assigned_to` is still null, escalate immediately (set status = ESCALATED, re-run assignment targeting the escalation role)

### Entity: User
```
User:
  id: UUID, primary key, immutable
  name: string, max 100 chars, required
  role: enum [PROCESSOR, SUPERVISOR, LOSS_PREVENTION, LP_MANAGER, IT_ONCALL], required
  station_id: string, max 50 chars, optional (physical station ID; null for off-floor roles)
  is_active: boolean, required, default true
  last_resolved_at: ISO 8601 timestamp, UTC, null until first WorkItem resolved
  created_at: ISO 8601 timestamp, UTC, immutable
```

### Entity: MonitoringRecord
```
MonitoringRecord:
  id: UUID, primary key, immutable
  return_item_id: UUID, foreign key to ReturnItem, required
  snapshot_disposition: enum (copy of ReturnItem.disposition at creation), required
  snapshot_reason_code: enum (copy of ReturnItem.reason_code at creation), required
  snapshot_condition_grade: enum (copy of ReturnItem.condition_grade at creation), required
  processor_id: UUID, foreign key to User, required
  created_at: ISO 8601 timestamp, UTC, immutable
  reviewed_at: ISO 8601 timestamp, UTC, null until reviewed
  reviewed_by: UUID, foreign key to User (Supervisor), nullable
  override_triggered: boolean, default false
    (set to true if supervisor changes the agent disposition during review;
    feeds into the daily accuracy metric)
```
MonitoringRecords are aggregated in a supervisor dashboard, filtered by `created_at >= shift_start`.
Supervisor reviews a sample by end of shift and marks `reviewed_at`. Target: 10% random sample daily.

---

## Requirements

### End-to-end processing order (V1)

On each item, run modules in this order so inputs exist before they are read:

1. **RC-001** (barcode / OMS lookup) → **RC-002** (Narvar text via `narvar_return_id` from OMS)  
2. **CC-001** (processor enters `condition_grade`) — must complete before RC-003, which may reference `condition_grade` for null-reason and consistency paths  
3. **RC-003** (agent reason classification) — **skipped** if RC-002 found a valid Narvar mapping
   (`reason_code_source = CUSTOMER_PROVIDED`); otherwise runs → **RC-004** (human review) when triggered  
4. **CC-002** (reason vs. condition consistency)  
5. **CC-003** (high-value grade confirmation) when `is_high_value = true`  
6. If CC-003 changes `condition_grade`, re-run **CC-002**; then re-run **FR-001** from that point (reason and final condition may affect signals)  
7. **FR-001** (fraud signals) through **DR** (disposition) as below  

---

### Module RC — Return identification and reason classification

**RC-001 — Barcode Lookup**
- Input: scanned barcode string
- Action: query Salesforce Commerce Cloud OMS `GET /returns?barcode={barcode}` (see §Integration Contracts; path must match Integration 1 exactly)
- If OMS returns exactly 1 matching record: populate `sku_id`, `order_id`, `customer_id`, `original_retail_price`, and `narvar_return_id` from response; proceed to RC-002
- If OMS returns 0 records: set `reason_code = null`, create WorkItem of type MANUAL_IDENTIFICATION, assign to available processor; halt automated flow for this item
- If OMS returns 2+ records (duplicate barcode): set `reason_code = null`, create WorkItem of type MANUAL_IDENTIFICATION with note "Duplicate barcode — manual disambiguation required"; halt automated flow
- If OMS call fails (timeout or HTTP 5xx): retry up to 3 times with 2-second exponential backoff; if all retries fail, create WorkItem of type SYSTEM_ERROR; halt automated flow

**RC-002 — Customer Reason Retrieval**
- Input: `narvar_return_id` from RC-001 (not `order_id` — Narvar keys reasons by return)
- Action: query Narvar `GET /returns/{narvar_return_id}/reason` (see §Integration Contracts)
- Populate `customer_reason_text` from response
- If Narvar returns no text (null or empty): set `customer_reason_text = null`; do not halt flow
- If Narvar returns `reason_code_customer` (non-null, non-empty), map it to an internal reason code
  using the following table and set `reason_code_source = CUSTOMER_PROVIDED`, `reason_code_confidence = 0.92`;
  if a valid mapping is found, skip RC-003 entirely for this item (and do **not** open **RC-004** solely for low
  score — 0.92 is above the review threshold; the shopper attested a structured category in the portal, analogous
  to a high-confidence text rule match):

  | Narvar `reason_code_customer` value | Internal `reason_code` |
  |---|---|
  | "Doesn't Fit", "Wrong Size", "Too Small", "Too Large" | DIDNT_FIT |
  | "Changed My Mind", "No Longer Needed", "Ordered by Mistake" | CHANGED_MIND |
  | "Defective", "Damaged", "Damaged on Arrival", "Product Defect" | DEFECTIVE |
  | "Wrong Item", "Wrong Item Received", "Wrong Color", "Wrong Style" | WRONG_ITEM |
  | "Other", any value not in the table above, or null | null → proceed to RC-003 |

  If mapping produces null (unrecognised Narvar code): set `customer_reason_text` from `reason_text`
  field as usual and proceed to RC-003.
- If Narvar call fails: set `customer_reason_text = null`; log error; proceed (text is optional input)

**RC-003 — Agent Classification**  
- Inputs: `customer_reason_text` (may be null), `condition_grade` from CC-001, `shipped_sku_id` and returned `sku_id` from RC-001, item category from `sku_id` ProductCatalog lookup  
- Action: classify into reason code. Apply **one** rule from the list below, **first match wins**.

  **Defect / fit keyword lists (non-exhaustive, case-insensitive):**
  - *Defect:* `broken`, `torn`, `split`, `snapped`, `fell apart`, `stopped working`, `zipper broken`, `button missing`, `seam split`, `defective`, `damaged on arrival`, `arrived damaged`, `stitching`, `stitch` (match `stitching` and `came loose` together in QA tests)
  - *Fit:* `too small`, `too large`, `too tight`, `too loose`, `wrong size`, `doesn't fit`, `didn't fit`, `runs small`, `runs large`, `fit issue`, `size issue`, `sizing`
    Note: bare word `size` is intentionally excluded — too broad (e.g., "bought in size M" would false-match).
  - *Changed mind:* `changed my mind`, `don't want`, `no longer need`, `found better`, `bought by mistake`, `gift duplicate`, `impulse buy`
  - *Self-blame (customer damage):* `my fault`, `I dropped`, `I washed`, `I altered`, `I damaged`, `I ruined`

  **Rule set (priority order):**
  1. If OMS / RC-001 shows `shipped_sku_id` ≠ scanned `sku_id` → `WRONG_ITEM`, confidence = 0.97 (system-verified; not overridden by text)
  2. If `customer_reason_text` contains at least one *fit* phrase and at least one *defect* phrase → `AMBIGUOUS`, confidence = 0.00 (escalate per RC-004) — *competing customer narratives*
  3. If `customer_reason_text` contains any *defect* phrase and any *self-blame* phrase → `AMBIGUOUS`, confidence = 0.00; attach note "Possible customer damage — manual review required" (escalate per RC-004)
  4. If `customer_reason_text` contains any *defect* phrase (and rules 1–3 did not match) → `DEFECTIVE`, confidence = 0.90
  5. If `customer_reason_text` contains any *fit* phrase → `DIDNT_FIT`, confidence = 0.95
  6. If `customer_reason_text` contains any *changed-mind* phrase → `CHANGED_MIND`, confidence = 0.92
  7. If `customer_reason_text` is null AND shipped SKU = returned `sku_id` AND `condition_grade` is LIKE_NEW or GOOD → `CHANGED_MIND`, confidence = 0.70
  8. All other cases → `AMBIGUOUS`, confidence = 0.00 → escalate per RC-004

  Set `reason_code_source = AGENT_CLASSIFIED` for all automated assignments from this module.

**RC-004 — Human Confirmation for Ambiguous or Low-Confidence Classification**
- Trigger: any of the following:
  1. `reason_code = AMBIGUOUS`, or
  2. `reason_code_source = AGENT_CLASSIFIED` AND `reason_code_confidence < 0.90`  
  When `reason_code_source = CUSTOMER_PROVIDED` (Narvar table mapping in **RC-002**), this WorkItem is **not**
  created on confidence alone; confidence is 0.92 and the path skipped RC-003 for that reason.
- Action: create WorkItem of type REASON_CODE_REVIEW; assign per §WorkItem Assignment Algorithm
  with `assigned_role = PROCESSOR`
- WorkItem content:
  - ReturnItem ID, SKU description, original retail price
  - Customer-provided reason text (verbatim), or "(no reason text provided)" if null
  - Agent's primary classification and confidence score (or "Ambiguous — no primary match")
  - **Top-2 alternative classifications**, computed as follows:
    - Score each of the 4 non-selected reason codes (DEFECTIVE, DIDNT_FIT, CHANGED_MIND,
      WRONG_ITEM) by counting how many of that code's keyword phrases appear in
      `customer_reason_text`; rank by count descending; show top 2 with their keyword match counts
    - If `customer_reason_text` is null: show only the agent's note (e.g., "No text — possible
      CHANGED_MIND based on condition") and the remaining codes sorted alphabetically
  - Link to the classification rubric for this item category
- Processor **must** select one of the 5 definitive codes: DEFECTIVE, DIDNT_FIT, CHANGED_MIND,
  WRONG_ITEM, SUSPECTED_FRAUD. `AMBIGUOUS` is not a valid selection in this UI — the processor
  must choose the best-fit code or escalate to supervisor.
- After selection: set `reason_code_source = HUMAN_OVERRIDE` if different from the pre-filled suggestion
  (from agent or Narvar mapping); if processor confirms the existing code unchanged, set
  `reason_code_source` to `AGENT_CLASSIFIED` (agent) or keep `CUSTOMER_PROVIDED` (Narvar) as appropriate
- SLA: WorkItem must be resolved within 30 minutes during facility operating hours;
  unresolved items after 30 minutes escalate to supervisor (WorkItem.status → ESCALATED)

---

### Module CC — Condition classification and validation

**CC-001 — Rubric Presentation**
- Trigger: after RC-002 completes for this item; processor is at the grading step
- Action: display condition grading rubric for this item's category (derived from `sku_id`
  ProductCatalog lookup — see §Integration 5; field: `category`, e.g., TOPS, BOTTOMS, OUTERWEAR,
  FOOTWEAR, ACCESSORIES)
- The category-specific rubric text (e.g., "OUTERWEAR GOOD: insulation intact, no visible tears,
  lining undamaged") is stored in the ProductCatalog reference table per category × grade combination.
  Initial rubric content must be provided by the Operations team before deployment — this is a
  deployment configuration item, not a builder decision [see Assumption A8]
- Rubric is a 5-grade scale with category-specific descriptors:

  | Grade | General Description |
  |---|---|
  | LIKE_NEW | Unworn/unused, original tags attached, no signs of handling |
  | GOOD | Worn or tried on; no visible defects; full resale value |
  | FAIR | Minor visible defects (loose thread, slight mark); sellable at discount |
  | POOR | Significant defects; requires repair or cleaning before resale |
  | UNSELLABLE | Damaged beyond resale (tears, stains, structural failure, missing components) |

- Processor selects one of 5 grades; system records `condition_grade` and `condition_grade_assigned_by`

**CC-002 — Consistency Validation**
- Trigger: after RC-003 / RC-004 have produced a final `reason_code` for routing (if RC-004 ran, use human-selected code)
- Validate reason vs. `condition_grade`:
  - If `reason_code = DIDNT_FIT` AND `condition_grade` is POOR or UNSELLABLE → flag as inconsistent, display warning: "Condition grade POOR/UNSELLABLE is unusual for a fit return. Please confirm or change the reason code." Processor must explicitly confirm to proceed
  - If `reason_code = DEFECTIVE` AND `condition_grade = LIKE_NEW` → flag as inconsistent, display warning: "Customer claims defective but item is graded LIKE_NEW. Please confirm or change the reason or grade." Processor must explicitly confirm; this situation also feeds `REASON_CONDITION_MISMATCH` in FR-001
  - All other combinations: no warning

**CC-003 — High-Value Confirmation Gate**
- Trigger: `is_high_value = true` (original retail price ≥ $100.00)
- Action: after processor enters condition grade, require a second confirmation:
  - Display: "High-value item ($[price]). Confirm condition grade: [GRADE]."
  - Processor confirms or adjusts grade
  - If processor adjusts: log both original and adjusted grade, with processor ID and timestamp
  - Item cannot proceed to FR-001 or disposition routing until high-value confirmation is recorded

---

### Module FR — Fraud signal assessment

**FR-001 — Signal Evaluation**
- Trigger: after **CC-002** has completed, and after **CC-003** has completed if `is_high_value = true`
  (CC-003 does not run for non-high-value items; do not wait for it). `sku_id`, `order_id`, and
  `customer_id` are populated from RC-001. If CC-003 changes the grade, re-run FR-001.  
- Action: evaluate the following **five** signals; each is independent (may all fire in one run):

  **Signal: SERIAL_RETURNER**
  - Query OMS customer return history: count of returns by this `customer_id` in the past 90 days
  - If count ≥ 5 returns in 90 days: fire signal
  - Signal detail: "Customer has made {N} returns in the past 90 days"
  - Signal data: `{customer_id, return_count_90d: N, return_dates: [...]}`

  **Signal: HIGH_VALUE_NO_PACKAGING**
  - Only evaluate if `is_high_value = true` AND `customer_reason_text` is **not null**
    (null text provides no evidence either way — do not fire on absence of text)
  - If both conditions met AND `customer_reason_text` does NOT contain any of:
    `original packaging`, `with tags`, `with box`, `unopened`, `tags attached`, `in box`:
  - Fire signal with confidence 0.60
  - Signal detail: "High-value item returned without mention of original packaging"
  - Signal data: `{sku_id, retail_price, customer_reason_text}`

  **Signal: SKU_HIGH_FRAUD_RATE**
  - Query FraudReferenceData (Loss Prevention spreadsheet import, see §Integration Contracts) for `sku_id`
  - If SKU is in the top-20 fraud-targeted SKU list AND item retail price ≥ $50: fire signal
  - Signal detail: "SKU {sku_id} has elevated historical fraud rate ({rate}%)"
  - Signal data: `{sku_id, fraud_rate_pct, source: "LP_reference_data"}`

  **Signal: REASON_CONDITION_MISMATCH**
  - Requires final `reason_code` and `condition_grade` after CC-002 (see FR-001 trigger)
  - If `reason_code = DEFECTIVE` AND `condition_grade = LIKE_NEW`: fire signal
  - Signal detail: "Customer claims defective but item is graded LIKE_NEW"
  - Signal data: `{reason_code, condition_grade}`

  **Signal: CUSTOMER_RETURN_VELOCITY**
  - Query OMS: count of returns by this `customer_id` at this ship-to address in the past 30 days
  - If count ≥ 3 at same address: fire signal
  - Signal detail: "3+ returns to same address in 30 days"
  - Signal data: `{customer_id, ship_to_address_hash, return_count_30d}`

**FR-002 — Single Signal: Log and Continue**
- If `fraud_signal_count = 1`:
  - Log signal to ReturnItem.fraud_signals
  - Set `is_fraud_escalated = false`
  - Continue normal processing
  - Signal visible to Loss Prevention in their monitoring dashboard (not a hold)

**FR-003 — Multiple Signals: Hold and Escalate**
- If `fraud_signal_count >= 2`:
  - Set `disposition = HOLD_FRAUD`
  - Set `is_fraud_escalated = true`
  - Create LossPreventionWorkItem with:
    - All fraud signals with detail and data
    - Customer return history (last 12 months): query OMS Endpoint 2 with `days=365`;
      include all returns, dates, SKUs, dispositions
    - Original order details: purchase date, channel, payment method
    - Current return details: condition grade, reason code, customer text
  - Assign to Loss Prevention queue
  - SLA: Loss Prevention must action within 4 hours during operating hours; unactioned items escalate to Loss Prevention Manager after 4 hours
  - Item physically held in HOLD lane; no disposition action until Loss Prevention decision

**FR-004 — Loss Prevention Decision**
- Loss Prevention agent reviews LossPreventionWorkItem and records decision:
  - `APPROVE`: return is legitimate; clear the hold and proceed with normal disposition routing (re-evaluate **DR-001** with current reason, condition, and fraud state)
  - `REJECT`: return is treated as fraud; `disposition` remains `HOLD_FRAUD` until the refund/chargeback workflow in OMS is complete; do **not** auto-route the item to a sellable lane; record decision and hand off to fraud reporting (implementation detail out of scope V1)
  - `NEEDS_MORE_INFO`: hold continues; Loss Prevention adds a note; SLA extends 2 hours
- All decisions logged with LP agent ID, timestamp, decision, and free-text notes

---

### Module DR — Disposition Routing

**DR-001 — Routing Table**
- Trigger: after reason code confirmed, condition grade confirmed, fraud signals evaluated, all gates passed
- Rules applied in priority order (first matching rule wins):

  | Priority | Condition | Reason Code | Fraud Signals | High Value | Escalated | Disposition | Delegation |
  |---|---|---|---|---|---|---|---|
  | 1 | Any | Any | ≥ 2 | Any | Any | HOLD_FRAUD | Human (FR-003) |
  | 2 | Any | Any | Any | Any | true | HOLD_REVIEW | Agent — Flag & Hold |
  | 3 | LIKE_NEW | DEFECTIVE | 0–1 | false | false | HOLD_REVIEW | Agent — Flag & Hold |
  | 4 | LIKE_NEW | non-DEFECTIVE non-AMBIGUOUS non-fraud | 0–1 | false | false | RESTOCK_AS_NEW | Agent — Autonomous |
  | 5 | GOOD | DIDNT_FIT or CHANGED_MIND | 0–1 | false | false | RESTOCK_AS_NEW | Agent — Autonomous |
  | 6 | GOOD | WRONG_ITEM | 0–1 | false | false | RESTOCK_AS_NEW | Agent — Autonomous |
  | 7 | GOOD | DEFECTIVE | 0–1 | false | false | REFURBISH | Agent — Log & Monitor |
  | 8 | LIKE_NEW or GOOD | Any non-fraud | 0–1 | true | false | HOLD_REVIEW | Agent — Flag & Hold |
  | 9 | FAIR | Any non-fraud | 0–1 | false | false | OUTLET | Agent — Log & Monitor |
  | 10 | FAIR | Any non-fraud | 0–1 | true | false | HOLD_REVIEW | Agent — Flag & Hold |
  | 11 | POOR | Any | 0–1 | false | false | REFURBISH | Agent — Flag & Hold |
  | 12 | UNSELLABLE | Any | 0–1 | Any | false | DESTROY | Agent — Flag & Hold |
  | 13 | Any | Any | 0–1 | Any | false | HOLD_REVIEW | Agent — Flag & Hold |

  Row 3 note: LIKE_NEW + DEFECTIVE is an inherently contradictory combination (CC-002 will have
  flagged it; processor confirmed). Agent cannot resolve it — requires human decision on whether
  to restock or refurbish.
  Row 13 is a catch-all: any combination that reaches this point without matching rows 1–12 is
  routed to HOLD_REVIEW with agent note "No routing rule matched — manual disposition required."
  This should not occur in normal operation; if it does, it signals a spec gap to investigate.

**DR-002 — Autonomous Routing (rows 4, 5, 6)**
- Agent writes `disposition` and `disposition_source = AGENT_AUTONOMOUS` to ReturnItem
- Sends WMS routing instruction to Manhattan WMS (see §Integration Contracts)
- Logs to audit trail

**DR-003 — Log & Monitor Routing (rows 7, 9)**
- Agent writes `disposition` and `disposition_source = AGENT_AUTONOMOUS` to ReturnItem
- Sends WMS routing instruction
- Creates MonitoringRecord for daily audit review by supervisor

**DR-004 — Flag & Hold Routing (rows 2, 3, 8, 10, 11, 12, 13)**
- Agent sets `disposition = HOLD_REVIEW`
- Creates ReviewWorkItem with:
  - Agent-recommended disposition from the routing table
  - Reason for hold (high-value / escalation / poor condition / DESTROY)
  - Item summary: SKU, condition, reason code, retail price
- Processor/supervisor reviews and confirms or overrides
- After human confirmation: agent writes final disposition and sends WMS instruction
- `disposition_source = AGENT_RECOMMENDED_HUMAN_CONFIRMED`

**DR-005 — DESTROY Confirmation**
- Applies when recommended disposition = DESTROY (row 12)
- Hold type: DESTROY_CONFIRM
- Reviewer sees: item details, condition grade, photo slot (for future use), explicit warning: "Destruction is irreversible. Confirm to proceed."
- Requires explicit confirmation — cannot be auto-approved by timeout

---

## Integration Contracts

### Integration 1 — Salesforce Commerce Cloud OMS

**Purpose:** Order/return lookup, customer history, customer escalation flag  
**Authentication:** OAuth 2.0 client credentials; credentials in environment variable `SFCC_CLIENT_ID` and `SFCC_CLIENT_SECRET`; token endpoint: `[SFCC_BASE_URL]/oauth2/tokens`  
**Base URL:** `[SFCC_BASE_URL]` — to be provided by client IT team [Assumption A3]

**Endpoint 1 — Barcode lookup:**
```
GET /returns?barcode={barcode}
Response 200:
{
  "return_id": string,
  "order_id": string,
  "customer_id": string,
  "sku_id": string,
  "original_retail_price": number (USD, 2 decimal places),
  "shipped_sku_id": string,
  "customer_escalation_flag": boolean,
  "narvar_return_id": string,
  "ship_to_address_hash": string   ← required for CUSTOMER_RETURN_VELOCITY fraud signal
}
Response 404: no matching return
Response 409: multiple matches (duplicate barcode)
```

**Endpoint 2 — Customer return history:**
```
GET /customers/{customer_id}/returns?days={days}
  days: integer, required — caller specifies lookback window.
  SERIAL_RETURNER uses days=90; CUSTOMER_RETURN_VELOCITY uses days=30.
  Make two separate calls if both signals need to be evaluated in one pass,
  OR cache the 90-day response and filter client-side for the 30-day window.
Response 200:
{
  "returns": [
    {
      "return_id": string,
      "order_id": string,
      "return_date": ISO 8601 date,
      "sku_id": string,
      "ship_to_address_hash": string,
      "disposition": string
    }
  ]
}
```

**Timeout:** 5 seconds  
**Retry:** HTTP 5xx → 3 retries, exponential backoff (2s, 4s, 8s). HTTP 4xx → no retry, log error.  
**Rate limit:** to be confirmed with client IT [Assumption A4]

---

### Integration 2 — Narvar Returns Portal

**Purpose:** Retrieve customer-provided return reason text  
**Authentication:** API key in header `X-Narvar-Key`; key in environment variable `NARVAR_API_KEY`  
**Base URL:** `[NARVAR_BASE_URL]` — to be provided by client [Assumption A3]

**Endpoint:**
```
GET /returns/{narvar_return_id}/reason
Response 200:
{
  "reason_text": string (may be null or empty),
  "reason_code_customer": string (customer-selected category, if applicable),
  "submitted_at": ISO 8601 timestamp
}
Response 404: no reason found (treat as null reason_text)
```

**Timeout:** 3 seconds  
**Retry:** HTTP 5xx → 2 retries, 2s backoff. HTTP 404 → no retry, set `customer_reason_text = null`.  
**Fallback:** If unavailable, proceed with `customer_reason_text = null` — do not halt processing.

---

### Integration 3 — Manhattan WMS

**Purpose:** Routing instructions for physical disposition lanes  
**Authentication:** Basic Auth; credentials in environment variables `WMS_USERNAME`, `WMS_PASSWORD`  
**Base URL:** `[MANHATTAN_WMS_URL]` — to be provided by client [Assumption A3]

**Endpoint:**
```
POST /routing-instructions
Request body:
{
  "item_id": string (ReturnItem.id),
  "sku_id": string,
  "disposition_lane": string (one of: RESTOCK_AS_NEW, OUTLET, REFURBISH, DONATE, DESTROY, HOLD_FRAUD, HOLD_REVIEW),
  "priority": string enum [NORMAL, HIGH, URGENT],
  "notes": string (max 500 chars, optional)
}
Response 200:
{
  "instruction_id": string,
  "lane_location": string (physical bin identifier),
  "acknowledged_at": ISO 8601 timestamp
}
Response 422: invalid lane or SKU not in WMS
```

**Timeout:** 5 seconds  
**Retry:** HTTP 5xx → 3 retries, exponential backoff. HTTP 422 → no retry; create WorkItem of type WMS_ROUTING_ERROR; alert supervisor.

---

### Integration 4 — Loss Prevention Fraud Reference Data

**Purpose:** SKU-level fraud rate lookup  
**Source:** Loss Prevention Manager's spreadsheet (CSV export), imported to a local reference table  
**Refresh cadence:** Monthly manual re-import [Assumption A7]  
**Format:**
```
sku_id: string
fraud_rate_pct: decimal (0.0–100.0)
last_updated: ISO 8601 date
```
**Fallback:** If SKU not in table, treat as `fraud_rate_pct = 0.0`; do not fire SKU_HIGH_FRAUD_RATE signal.

---

### Integration 5 — ProductCatalog (local reference table)

**Purpose:** SKU → category mapping and condition rubric content for CC-001  
**Source:** Local database table populated and maintained by Operations team  
**Not an external API call** — read from local DB at runtime  
**Schema:**
```
ProductCatalog:
  sku_id: string, primary key
  category: enum [TOPS, BOTTOMS, OUTERWEAR, FOOTWEAR, ACCESSORIES, OTHER], required
  description: string, max 200 chars
  brand: string, max 100 chars, optional

ConditionRubric:
  category: enum [TOPS, BOTTOMS, OUTERWEAR, FOOTWEAR, ACCESSORIES, OTHER], required
  grade: enum [LIKE_NEW, GOOD, FAIR, POOR, UNSELLABLE], required
  description: string, max 500 chars, required (category-specific rubric text shown to processor)
  primary key: (category, grade)
```
**Fallback:** If `sku_id` not found in ProductCatalog, use `category = OTHER`; display the generic
(non-category-specific) rubric.  
**Assumption A8:** Initial rubric content (25 rows: 5 categories × 5 grades) must be authored by
Operations team before go-live. Builder scaffolds the table; content is a deployment dependency.

---

## Escalation Summary

| Escalation Type | Trigger | Assigned To | SLA | Timeout Action |
|---|---|---|---|---|
| MANUAL_IDENTIFICATION | Unreadable barcode or no OMS match | Available processor | 15 min | Escalate to supervisor |
| REASON_CODE_REVIEW | Ambiguous classification | Available processor | 30 min | Escalate to supervisor |
| HOLD_FRAUD | 2+ fraud signals | Loss Prevention queue | 4 hours | Escalate to LP Manager |
| HOLD_REVIEW | High-value / escalated / POOR / DESTROY | Processor / supervisor | 1 hour | Escalate to supervisor |
| DESTROY_CONFIRM | UNSELLABLE condition | Supervisor | 2 hours | Escalate to facility manager |
| WMS_ROUTING_ERROR | WMS rejects routing instruction | Supervisor | 30 min | Manual routing |
| SYSTEM_ERROR | OMS call fails after retries | IT on-call | 1 hour | Manual processing |

---

## Audit & Logging Requirements

Every state change on a ReturnItem must be logged to the audit table with:
- `event_type`: enum — exhaustive list:
  ```
  BARCODE_SCANNED, OMS_LOOKUP_SUCCESS, OMS_LOOKUP_FAILED, OMS_LOOKUP_NO_MATCH,
  NARVAR_REASON_RETRIEVED, NARVAR_REASON_NULL, NARVAR_LOOKUP_FAILED,
  CUSTOMER_CODE_MAPPED,
  CONDITION_GRADE_ENTERED, CONDITION_GRADE_CONFIRMED_HIGH_VALUE, CONDITION_GRADE_ADJUSTED,
  REASON_CODE_CLASSIFIED, REASON_CODE_AMBIGUOUS, REASON_CODE_HUMAN_CONFIRMED,
  REASON_CODE_HUMAN_OVERRIDDEN,
  CONSISTENCY_WARNING_SHOWN, CONSISTENCY_WARNING_CONFIRMED,
  FRAUD_SIGNAL_FIRED, FRAUD_HOLD_CREATED, LP_DECISION_RECORDED,
  DISPOSITION_SET_AUTONOMOUS, DISPOSITION_SET_AFTER_REVIEW, DISPOSITION_HUMAN_OVERRIDDEN,
  WMS_INSTRUCTION_SENT, WMS_INSTRUCTION_FAILED,
  WORKITEM_CREATED, WORKITEM_ASSIGNED, WORKITEM_RESOLVED, WORKITEM_ESCALATED,
  PROCESSING_HALTED, PROCESSING_COMPLETED
  ```
- `return_item_id`
- `actor_type`: enum [AGENT, HUMAN]
- `actor_id`: agent version string or User ID
- `from_value` and `to_value`: previous and new values for the changed field
- `timestamp`: ISO 8601, UTC
- `session_id`: processor session ID (for human actions)

Logs are immutable. Retention: 7 years (financial compliance requirement per Finance).  
The audit stream stores `customer_id` in hashed form; `WorkItem` and Loss Prevention review UIs may display the customer narrative and evidence **for investigation** per corporate PII policy (those screens are not the same as the 7-year audit table).
# Artifact 4 — Validation Design

## Purpose

This document defines how to verify that the Returns Disposition Agent (RDA) is working correctly. It covers: what to test, how to test it, what failure looks like, and what success thresholds must be met before the agent is trusted for production.

---

## Validation Principles

1. **Test the delegation boundary, not just the happy path.** The most important tests are the ones that probe where the agent hands off to a human — these are where errors have the greatest consequence.
2. **Test for acceptable failure, not just success.** A well-designed failure (escalate to human) is better than a wrong autonomous decision. Tests must verify that the agent fails gracefully.
3. **Test signal coverage for fraud.** The fraud signal module is the most high-stakes component — false negatives have direct financial cost, false positives have operational cost.

---

## Test Suite Structure

| Suite | Focus | Minimum test count |
|---|---|---|
| V1 — Happy Path | End-to-end clean returns | 3 |
| V2 — Reason Code Classification | All classification rules + edge cases | 8 |
| V3 — Fraud Signal Detection | All 5 fraud signals, threshold behavior | 7 |
| V4 — Delegation Boundary | High-value gate, escalation flag, DESTROY gate | 5 |
| V5 — Integration Failure Modes | OMS down, WMS reject, Narvar timeout | 4 |
| V6 — Concurrent Processing | Race conditions, duplicate scans | 2 |

---

## V1 — Happy Path Scenarios

### V1-01 — Standard Fit Return (Fully Autonomous)
**Given:**
- Item scanned: SKU `APP-BLOUSE-S-BLU`, retail price $45.00
- OMS returns valid order, `customer_escalation_flag = false`
- Customer reason text: "didn't fit, too small"
- No prior returns in 90 days for this customer
- SKU not in fraud reference list
- Processor grades condition: LIKE_NEW

**When:** Agent processes the item end-to-end

**Then:**
- `reason_code = DIDNT_FIT`, `reason_code_confidence ≥ 0.95`
- `is_high_value = false`
- `fraud_signal_count = 0`
- `disposition = RESTOCK_AS_NEW`
- `disposition_source = AGENT_AUTONOMOUS`
- WMS receives routing instruction: `disposition_lane = RESTOCK_AS_NEW`
- Audit log contains: barcode lookup event, Narvar query event, FR-001 evaluation event, disposition event
- Total agent processing time (scan to WMS instruction): ≤ 8 seconds

---

### V1-02 — Wrong Item Shipped (Fully Autonomous)
**Given:**
- Item scanned: SKU `APP-JACKET-M-RED`, retail price $75.00
- OMS shows original order had `shipped_sku_id = APP-JACKET-M-BLK` (different SKU)
- Customer reason text: "wrong color sent"
- No fraud signals
- Processor grades condition: GOOD

**When:** Agent processes the item

**Then:**
- `reason_code = WRONG_ITEM`, `reason_code_confidence = 0.97`
- `disposition = RESTOCK_AS_NEW`
- `disposition_source = AGENT_AUTONOMOUS`
- WMS routing: `RESTOCK_AS_NEW` with `priority = NORMAL`
- No WorkItem created

---

### V1-03 — Fair Condition, Low-Value (Log & Monitor)
**Given:**
- Item scanned: SKU `APP-TSHIRT-L-WHT`, retail price $22.00
- Customer reason text: "changed my mind"
- No fraud signals
- Processor grades condition: FAIR (minor pilling visible)

**When:** Agent processes the item

**Then:**
- `reason_code = CHANGED_MIND`
- `condition_grade = FAIR`
- `disposition = OUTLET`
- `disposition_source = AGENT_AUTONOMOUS`
- MonitoringRecord created for daily audit
- WMS routing: `OUTLET`

---

## V2 — Reason Code Classification

### V2-01 — Null Customer Reason Text
**Given:** Customer returned item through a store drop-off with no reason text; Narvar returns null

**When:** Agent attempts classification

**Then:**
- `customer_reason_text = null`
- If `condition_grade = GOOD` or `LIKE_NEW` AND shipped SKU = returned `sku_id` (no OMS mismatch) → `reason_code = CHANGED_MIND`, `confidence = 0.70` (RC-003 rule 7)
- Because `0.70 < 0.90`, **RC-004** creates a `REASON_CODE_REVIEW` WorkItem; processor must confirm the suggested code (or override)

---

### V2-02 — Ambiguous Text: "Quality Issue"
**Given:** Customer reason text: "the quality wasn't what I expected"

**When:** Agent classifies

**Then:**
- No specific rule matches
- `reason_code = AMBIGUOUS`, `confidence = 0.00`
- WorkItem of type REASON_CODE_REVIEW created within 2 seconds
- WorkItem includes agent's two most plausible alternatives with confidence breakdown
- SLA timer starts (30 min)

---

### V2-03 — DEFECTIVE Claim, LIKE_NEW Condition — Fraud Signal Trigger
**Given:** Customer text: "arrived damaged, zipper broken"  
**Condition grade (processor):** LIKE_NEW  
**No other fraud signals**

**When:** Agent evaluates

**Then:**
- `reason_code = DEFECTIVE` from RC-003 (defect phrase list matches; rule 4, after CC-001 has run)
- After CC-002: `reason_code = DEFECTIVE` + `condition_grade = LIKE_NEW` → inconsistency flag raised; processor receives warning: "Customer claims defective but item is graded LIKE_NEW. Please confirm or change the reason or grade."
- FR-001 (after CC-002/CC-003): fires `REASON_CONDITION_MISMATCH` (confidence 0.85 in signal payload)
- `fraud_signal_count = 1` → FR-002 (log and continue, not hold)
- **Note:** A `REASON_CODE_REVIEW` WorkItem is **not** required solely because confidence = 0.90 for DEFECTIVE; the **CC-002** inconsistency flow handles human confirmation for the mismatch.

---

### V2-04 — Possible Customer Damage (DEFECTIVE Override)
**Given:** Customer text: "the seam split after I washed it at high temperature"

**When:** Agent classifies

**Then:**
- RC-003 **rule 3** applies (defect phrase + self-blame phrase) before the pure-defect rule
- `reason_code = AMBIGUOUS`, `confidence = 0.00`, with note "Possible customer damage — manual review required"
- `REASON_CODE_REVIEW` WorkItem created; agent does **not** assign `DEFECTIVE` autonomously for this text

---

### V2-05 — Multiple Reason Signals in One Text
**Given:** Customer text: "it didn't fit and also the stitching came loose"

**When:** Agent classifies

**Then:**
- Text matches both a *fit* phrase and a *defect* phrase
- RC-003 **rule 2** (competing fit + defect narratives) applies before single-category rules
- Expected: `reason_code = AMBIGUOUS`, `confidence = 0.00`, and `REASON_CODE_REVIEW` WorkItem created

---

### V2-06 — WRONG_ITEM Verified by System (No Customer Text Needed)
**Given:** OMS `shipped_sku_id = APP-PANTS-32-GRY`; scanned barcode resolves to `APP-PANTS-32-BLK`  
**Customer text:** "I just wanted to return this"

**When:** Agent classifies

**Then:**
- `reason_code = WRONG_ITEM`, `confidence = 0.97` (system-verified; RC-003 rule 1 fires before text rules)
- Text content irrelevant to final classification
- No WorkItem created

---

### V2-07 — High-Volume Serial Returner, Legitimate Classification
**Given:** Customer has 4 returns in 90 days (below SERIAL_RETURNER threshold of 5)  
**Return text:** "too small"  
**Condition:** GOOD  
**Retail price:** $55

**When:** Agent processes

**Then:**
- `reason_code = DIDNT_FIT`
- No SERIAL_RETURNER signal fires (count = 4, threshold = 5)
- No fraud signals
- `disposition = RESTOCK_AS_NEW`, autonomous
- **Verify:** agent does NOT fire fraud signal below threshold

---

### V2-08 — Empty String vs. Null Reason Text
**Given:** Narvar returns `"reason_text": ""` (empty string, not null)

**When:** Agent reads reason text

**Then:**
- Agent treats `""` as equivalent to null
- `customer_reason_text` set to null
- Processing proceeds as per V2-01
- **Verify:** empty string is not passed to classification rules (would cause unexpected matches)

---

## V3 — Fraud Signal Detection

### V3-01 — Single Signal: Does Not Hold
**Given:** Customer has 6 returns in 90 days (SERIAL_RETURNER fires)  
**Retail price:** $40  
**No other signals**

**When:** Agent evaluates fraud

**Then:**
- `fraud_signal_count = 1`
- `is_fraud_escalated = false`
- Item NOT placed on hold
- Signal logged to ReturnItem.fraud_signals
- Signal visible in Loss Prevention monitoring dashboard
- Processing continues normally

---

### V3-02 — Two Signals: Hold Fires
**Given:** Customer has 6 returns in 90 days (SERIAL_RETURNER) + item is on high-fraud SKU list (SKU_HIGH_FRAUD_RATE)  
**Retail price:** $120

**When:** Agent evaluates fraud

**Then:**
- `fraud_signal_count = 2`
- `is_fraud_escalated = true`
- `disposition = HOLD_FRAUD`
- LossPreventionWorkItem created within 5 seconds
- WorkItem contains: both signals with detail, customer return history (last 12 months), original order details
- Loss Prevention queue receives item
- SLA timer starts: 4 hours

---

### V3-03 — Loss Prevention: Approve Decision
**Given:** LossPreventionWorkItem exists (from V3-02 scenario)  
**Action:** LP investigator reviews and selects APPROVE

**When:** LP decision recorded

**Then:**
- `is_fraud_escalated` remains true (log only — cannot un-flag)
- Item disposition proceeds via normal routing table (DR-001) based on condition and reason code
- LP decision logged: `actor_id = LP investigator ID`, `decision = APPROVE`, `timestamp`, `notes`
- Item removed from HOLD_FRAUD status

---

### V3-04 — Loss Prevention SLA Breach
**Given:** LossPreventionWorkItem created; no LP action taken within 4 hours

**When:** 4-hour SLA timer expires

**Then:**
- Escalation notification sent to Loss Prevention Manager
- WorkItem priority changes to URGENT
- Item remains on HOLD_FRAUD (does NOT auto-approve)
- **Verify:** item cannot be released without explicit LP or LP Manager decision

---

### V3-05 — REASON_CONDITION_MISMATCH as the Only Signal
**Given:** `reason_code = DEFECTIVE`, `condition_grade = LIKE_NEW`  
**No other fraud signals present**

**When:** Agent evaluates fraud

**Then:**
- `fraud_signal_count = 1` (REASON_CONDITION_MISMATCH)
- No hold
- Where this pair arises in an end-to-end path, **CC-002** already surfaces the mismatch to the processor (see V2-03); this test isolates **FR-001** behavior given the pair
- Fraud signal is logged and visible, not actionable on its own

---

### V3-06 — All Five Signals Fire Simultaneously
**Given:** A crafted test case with all 5 fraud signals present

**When:** Agent evaluates

**Then:**
- `fraud_signal_count = 5`
- Item placed on HOLD_FRAUD
- LossPreventionWorkItem contains all 5 signals
- **Verify:** system handles `fraud_signal_count > 2` correctly (does not fail or cap at 2)

---

### V3-07 — Fraud Reference Data: SKU Not in List
**Given:** `sku_id = APP-NEW-SKU-XYZ` (not in Loss Prevention fraud reference table)

**When:** Agent evaluates SKU_HIGH_FRAUD_RATE signal

**Then:**
- Signal does NOT fire
- `fraud_rate_pct` treated as 0.0
- No error or exception thrown
- Processing continues normally

---

## V4 — Delegation Boundary Tests

### V4-01 — High-Value Gate Prevents Autonomous Disposition
**Given:** Item retail price = $150.00 (`is_high_value = true`)  
**Condition:** LIKE_NEW, `reason_code = DIDNT_FIT`, no fraud signals

**When:** Agent determines disposition

**Then:**
- Routing table row 7 applies: HOLD_REVIEW (not RESTOCK_AS_NEW from row 4)
- ReviewWorkItem created: "High-value item ($150.00). Confirm condition grade and disposition."
- `disposition = HOLD_REVIEW` (not RESTOCK_AS_NEW)
- Processor must confirm before WMS instruction is sent
- **Verify:** the $100 threshold is exact — $99.99 does NOT trigger high-value gate; $100.00 DOES

---

### V4-02 — Customer Escalation Gate
**Given:** OMS returns `customer_escalation_flag = true`  
**Item:** Any condition, any reason code, no fraud signals, retail price $30

**When:** Agent processes

**Then:**
- Routing table row 2 applies: HOLD_REVIEW
- ReviewWorkItem created: "Customer has open escalation with Contact Centre. Supervisor review required."
- `disposition = HOLD_REVIEW`
- **Verify:** escalation flag overrides routing table — even a LIKE_NEW, low-value item is held if escalated

---

### V4-03 — DESTROY Gate Requires Explicit Confirmation (Not Timeout)
**Given:** Condition = UNSELLABLE  
**Retail price:** $20  
**No fraud signals, no escalation**

**When:** Agent routes to DESTROY

**Then:**
- `disposition = HOLD_REVIEW` (DESTROY_CONFIRM type)
- ReviewWorkItem displayed to supervisor with explicit destruction warning
- Timeout of 2 hours elapses WITHOUT supervisor action

**Then (after timeout):**
- Item does NOT auto-proceed to DESTROY
- Escalation to facility manager
- **Verify:** DESTROY is the only disposition that does not have an auto-proceed timeout path

---

### V4-04 — Boundary Precision: $99.99 vs. $100.00
**Given:** Two items — Item A: retail price $99.99; Item B: retail price $100.00  
**Both:** LIKE_NEW, DIDNT_FIT, no fraud signals

**When:** Both are processed

**Then:**
- Item A: `is_high_value = false` → disposition = RESTOCK_AS_NEW, autonomous
- Item B: `is_high_value = true` → disposition = HOLD_REVIEW
- **Verify:** the threshold is inclusive at exactly $100.00

---

### V4-05 — Fraud Hard Constraint Overrides All Routing
**Given:** 2+ fraud signals, item condition = LIKE_NEW, retail price = $20

**When:** Agent routes

**Then:**
- Routing table row 1 fires (highest priority): HOLD_FRAUD
- Despite LIKE_NEW condition and low value, no autonomous disposition occurs
- **Verify:** fraud constraint is the highest-priority rule and cannot be overridden by any condition/price combination

---

## V5 — Integration Failure Modes

### V5-01 — OMS Unavailable After All Retries
**Given:** OMS returns HTTP 503 for 3 consecutive attempts (barcode lookup)

**When:** All retries exhausted

**Then:**
- WorkItem of type SYSTEM_ERROR created with item barcode and error details
- IT on-call alerted
- Item placed in MANUAL_PROCESSING queue
- No `reason_code`, `sku_id`, or `order_id` populated (no guessing from partial data)
- Agent does NOT proceed with incomplete data

---

### V5-02 — Narvar Timeout: Processing Continues
**Given:** Narvar call times out (exceeds 3 seconds)

**When:** Timeout occurs

**Then:**
- `customer_reason_text = null`
- Error logged (not a WorkItem — non-blocking)
- Processing continues with null reason text (RC-003 rule 7 if like-new/good and same SKU; otherwise AMBIGUOUS)
- **Verify:** Narvar failure does not halt the entire item flow

---

### V5-03 — WMS Rejects Routing Instruction (422)
**Given:** Manhattan WMS returns HTTP 422: "Invalid disposition lane for this SKU category"

**When:** WMS rejects instruction

**Then:**
- No retry (422 = client error, not server error)
- WorkItem of type WMS_ROUTING_ERROR created: includes ReturnItem ID, attempted lane, WMS error message
- Supervisor alerted
- Item disposition NOT recorded in ReturnItem until manual WMS routing confirmed
- **Verify:** `disposition_source` is not set to AGENT_AUTONOMOUS if WMS rejected the instruction

---

### V5-04 — Partial OMS Response (Missing Fields)
**Given:** OMS returns 200 but response is missing `customer_escalation_flag`

**When:** Agent parses response

**Then:**
- `is_customer_escalated` defaults to `false` — missing flag treated as "no escalation" (safe default)
- Warning logged: "OMS response missing customer_escalation_flag for return {id} — defaulting to false"
- **Verify:** missing optional field does not cause exception; agent documents the assumption

---

## V6 — Concurrent Processing

### V6-01 — Same Item Scanned Twice Simultaneously
**Given:** Two processors at adjacent stations scan the same item barcode within 500ms of each other (physical error — item near two scanners)

**When:** Both scan events processed

**Then:**
- First scan creates ReturnItem with status = PROCESSING
- Second scan: OMS lookup returns same `return_id` → system detects duplicate in-flight ReturnItem for this `return_id`
- Second scan rejected: error displayed to processor: "This return is already being processed at another station."
- Only one ReturnItem record created
- **Verify:** idempotency check on `return_id` prevents duplicate records

---

### V6-02 — Processor Modifies Reason Code While Agent Is Evaluating Fraud
**Given:** Processor selects condition grade; agent begins FR-001 (fraud evaluation). Simultaneously, processor modifies reason code (late correction).

**When:** Both operations in flight

**Then:**
- Fraud evaluation uses the reason code value that was current when FR-001 started
- If reason code changes during fraud evaluation: FR-001 result is invalidated; fraud evaluation re-runs with new reason code
- ReturnItem `updated_at` timestamp updated on reason code change; audit log records both original and corrected value
- **Verify:** no stale-read condition produces a fraud evaluation against an already-corrected reason code

---

## Production Readiness Thresholds

Before going live, all of the following must be true:

| Criterion | Threshold | Test |
|---|---|---|
| Reason code accuracy (on labeled test set of 500 items) | ≥ 90% | V2 suite + labeled historical data |
| Fraud signal false positive rate | ≤ 5% (of all fraud escalations) | V3 suite + Loss Prevention review of pilot period |
| Autonomous routing accuracy (on test set of 200 items) | ≥ 96% correct disposition | V1 + V4 suite + expert re-review |
| V5-01: graceful handling of OMS failure | 100% (no unhandled exceptions) | V5 suite |
| V6-01: no duplicate records from concurrent scans | 100% | V6 suite |
| DESTROY gate: no auto-proceed on timeout | 100% | V4-03 |
| Fraud hold cannot be released without LP decision | 100% | V3-04 |

All thresholds must be met in a controlled pre-production pilot (minimum 200 items from historical data before live processing begins).
# Artifact 5 — Assumptions & Unknowns

## How to Read This Document

Every assumption in this document represents a bet. If the assumption is wrong, something in the spec breaks. The **Impact if Wrong** column tells you how badly it breaks. The **Status** column tells you what we know:

- `[Known]` — confirmed by a stakeholder in discovery
- `[Assumed]` — reasonable inference from context; not yet validated
- `[Flagged for Validation]` — must be confirmed before building this component; building on this assumption risks rework

---

## A — System & Integration Assumptions

### A1 — Manhattan WMS Has a Routing API
**Statement:** The Manhattan Associates WMS deployment at this retailer exposes an HTTP API for routing instructions that the agent can call programmatically.  
**Why it matters:** The entire disposition routing module (Module DR) depends on being able to send routing instructions to the WMS. Without an API, routing instructions would have to be entered manually.  
**Impact if wrong:** The DR module cannot be built as specified. Agent would need to surface instructions on a processor screen for manual WMS entry — significantly degrading automation.  
**Status:** `[Flagged for Validation]`  
**Validation owner:** IT / Systems team  
**Validation question:** "Does your Manhattan WMS instance expose a REST or SOAP API for routing instructions? If yes, please share the endpoint documentation and auth method."

---

### A2 — Salesforce Commerce Cloud OMS Has Customer Return History API
**Statement:** The SFCC OMS supports querying a customer's full return history by `customer_id` with a date-range filter (used in FR-001 for SERIAL_RETURNER and CUSTOMER_RETURN_VELOCITY signals).  
**Why it matters:** Two of the five fraud signals require querying return history. Without this, those signals cannot fire.  
**Impact if wrong:** SERIAL_RETURNER and CUSTOMER_RETURN_VELOCITY signals are unbuildable. Fraud detection rate target (70%) becomes harder to achieve.  
**Status:** `[Flagged for Validation]`  
**Validation question:** "Can we query SFCC for all returns by a customer_id within a date range? What is the API endpoint and response format?"

---

### A3 — API Base URLs and Authentication Credentials Are Available
**Statement:** The client IT team will provide base URLs and credentials for SFCC OMS, Manhattan WMS, and Narvar portal before development begins.  
**Why it matters:** All integration contracts in the spec use `[BASE_URL]` placeholders. Without real URLs, integration tests cannot run.  
**Impact if wrong:** Development can proceed with mocks, but integration testing is blocked. Increases delivery risk.  
**Status:** `[Flagged for Validation]`  
**Validation question:** "Who is the IT contact who can provide API credentials and base URLs for SFCC, Manhattan, and Narvar?"

---

### A4 — API Rate Limits Are Sufficient for Processing Volume
**Statement:** OMS and WMS APIs can handle the call volume generated by processing 900 items/day (peak ~1,500 items/day during seasonal spikes) without throttling.  
**Why it matters:** Each item triggers 2 OMS calls + 1 Narvar call + 1 WMS call = 4 API calls per item. At 900 items/day: ~3,600 calls/day = ~7.5 calls/minute average, with bursts up to ~30 calls/minute at peak.  
**Impact if wrong:** Processing will be throttled; items will queue; backlog will form. The peak capacity target (1,500 items/day) may be unachievable.  
**Status:** `[Flagged for Validation]`  
**Validation question:** "What are the rate limits for SFCC OMS, Manhattan WMS, and Narvar API? Are burst limits higher than sustained rate limits?"

---

### A5 — Narvar Return Portal Stores Customer Reason Text Per Return
**Statement:** The Narvar returns portal stores the customer's free-text return reason and exposes it via API at the `return_id` level.  
**Why it matters:** The reason code classification module (RC-003) depends on customer-provided text for high-confidence classification. Without Narvar text, the agent falls back to the lower-confidence null-text rules, increasing human review workload.  
**Impact if wrong:** Classification accuracy declines for online returns (which go through Narvar). More items hit the AMBIGUOUS path.  
**Status:** `[Assumed]`

---

### A6 — Real-Time Inventory Sync Between OMS and Manhattan WMS
**Statement:** The Manhattan WMS inventory is updated in real-time (or near real-time, ≤ 5 minutes) when items are sold in stores or online, so the agent can route RESTOCK_AS_NEW items with confidence that the inventory position is current.  
**Why it matters:** If WMS inventory is stale, RESTOCK_AS_NEW items may be routed to a bin that is at capacity, or items may be double-counted.  
**Impact if wrong:** WMS routing errors increase; disposition accuracy degrades. Operational confusion at the facility.  
**Status:** `[Flagged for Validation]`  
**Validation question:** "What is the inventory sync frequency between your online/store sales channels and Manhattan WMS?"

---

### A7 — Loss Prevention Fraud Reference Data Can Be Exported and Imported Monthly
**Statement:** The Loss Prevention Manager's spreadsheet of high-fraud SKUs can be exported as a CSV and imported to the agent's reference table on a monthly refresh schedule.  
**Why it matters:** The SKU_HIGH_FRAUD_RATE fraud signal depends on this data. If data is never refreshed, it goes stale as fraud patterns shift.  
**Impact if wrong (stale data):** SKU_HIGH_FRAUD_RATE signal misses new fraud targets; fires on discontinued fraud targets. Signal becomes noise.  
**Status:** `[Assumed]`  
**Desired state:** Loss Prevention should ideally maintain this data in a system (not a spreadsheet) that the agent can query directly. This is a Phase 2 recommendation.

---

### A8 — Condition Rubric Content Authored by Operations Before Go-Live
**Statement:** The category-specific condition grading rubric (25 rows: 5 categories × 5 grades) will
be authored by the Operations/Returns team and loaded into the ProductCatalog.ConditionRubric table
before the system goes live. The builder scaffolds the table structure; content is a client delivery.  
**Why it matters:** CC-001 displays category-specific rubric text to processors. Without this content,
the grading step shows no guidance — defeating the purpose of the feature.  
**Impact if wrong:** Processors see blank rubric descriptions; grading consistency does not improve;
the accuracy improvement target is at risk.  
**Status:** `[Flagged for Validation]`  
**Validation question:** "Who on the Operations team will author the 25 rubric descriptions, and by
what date before go-live? Do you have any existing written grading guidelines we can use as a
starting point?"

---

## B — Business Rule Assumptions

### B1 — High-Value Threshold is $100.00 Retail Price
**Statement:** An item is classified as "high-value" (requiring human confirmation at condition grading and disposition) if its original retail price is ≥ $100.00 USD.  
**Why it matters:** This threshold directly controls how many items go through the HOLD_REVIEW path. At $100, approximately 10–12% of returns are high-value. At $150, it drops to ~6%. At $75, it rises to ~18%.  
**Impact if wrong:** Either too many items in human review queue (threshold too low → operational overhead) or high-value items getting autonomous disposition (threshold too high → margin risk).  
**Source:** VP of Operations indicated "over about $100" in discovery conversation. Not a formal policy document.  
**Status:** `[Flagged for Validation]`  
**Validation question:** "What is the formal definition of 'high-value' for returns processing? Is $100 retail price the right threshold, or is it category-specific (e.g., $75 for footwear, $150 for outerwear)?"

---

### B2 — "Defective" Means Manufacturer Defect, Not Customer Damage
**Statement:** The DEFECTIVE reason code applies only to items that arrived defective or failed due to a manufacturing fault. Items damaged by the customer should be coded differently (CUSTOMER_DAMAGE — currently not a code in the 5-code system).  
**Why it matters:** This distinction drives warranty/vendor chargebacks vs. normal inventory recovery. Mis-classification costs the retailer money in both directions.  
**Impact if wrong:** Either warranty claims are submitted for customer-damaged items (fraud toward vendors) or genuine defects are absorbed as returns cost.  
**Status:** `[Assumed]`  
**Validation question:** "Is DEFECTIVE vs. CUSTOMER_DAMAGE a distinction your current process makes? Should CUSTOMER_DAMAGE be a 6th reason code? What disposition does customer-damaged merchandise receive?"

---

### B3 — 1–2% of Returns Involve Fraud Attempts
**Statement:** Approximately 1–2% of all returns (2,340–4,680 per year) involve attempted fraud, based on apparel industry averages.  
**Why it matters:** This underpins the fraud ROI calculation in Artifact 1. If the actual fraud rate is lower (e.g., 0.3%), the fraud chargeback reduction benefit shrinks. If higher (e.g., 4%), the benefit is larger.  
**Impact if wrong:** CFO's payback model shifts. Could undermine the business case if actual fraud rate is significantly lower.  
**Status:** `[Assumed — industry estimate]`  
**Validation question:** "What is your actual annual fraud rate as a percentage of returns, based on historical chargeback records from Loss Prevention?"

---

### B4 — OUTLET and REFURBISH Disposition Lanes Are Distinct Physical Locations
**Statement:** The RESTOCK_AS_NEW, OUTLET, REFURBISH, DONATE, and DESTROY lanes correspond to physically separate destinations in the returns facility that can be addressed by WMS routing instructions.  
**Why it matters:** The routing instructions sent to Manhattan WMS assume a lane identifier that maps to a physical bin/location. If lanes don't exist as discrete physical locations, WMS routing as specified is not valid.  
**Impact if wrong:** WMS integration must be redesigned around actual physical facility layout.  
**Status:** `[Assumed — standard returns facility layout]`

---

### B5 — The 5 Reason Codes Are Exhaustive for V1
**Statement:** DEFECTIVE, DIDNT_FIT, CHANGED_MIND, WRONG_ITEM, SUSPECTED_FRAUD cover all return scenarios the **business** records in WMS/OMS for V1. The **autonomous classifier** in the spec outputs the first four plus `AMBIGUOUS`; `SUSPECTED_FRAUD` is reserved for human/LP assignment where legacy systems still require that code (fraud **handling** is via signals and `HOLD_FRAUD`).  
**Why it matters:** The classification module (RC-003) is designed around automated labels plus `AMBIGUOUS`. If there are additional codes used in practice that are not in this list, the agent will classify them as AMBIGUOUS.  
**Impact if wrong:** Higher-than-expected AMBIGUOUS rate; human review queue is larger than projected.  
**Status:** `[Flagged for Validation]`  
**Validation question:** "Are there any return reason codes used in your current WMS or OMS beyond these five? For example: NOT_AS_DESCRIBED, LATE_DELIVERY, GIFT_RETURN, WARRANTY_CLAIM?"

---

## C — Operational Assumptions

### C1 — Processing Happens in a Single Central Facility
**Statement:** All returns are processed at one central facility, not at stores or regional hubs. The agent is deployed to this facility only.  
**Why it matters:** The spec assumes a single deployment point with consistent station hardware and network access to the same systems.  
**Impact if wrong:** Multi-site deployment requires infrastructure replication and potentially different WMS configurations per site.  
**Status:** `[Known — stated in scenario]`

---

### C2 — Barcode Scan is the Entry Point for Every Item
**Statement:** Every item that enters the agent's processing flow has been scanned by a barcode reader at the intake station. There is no path where an item receives agent processing without a barcode scan event.  
**Why it matters:** RC-001 (barcode lookup) is the first step in the entire flow. If some items enter the flow without a scan (e.g., batch imports from store-originated returns), the agent's flow breaks.  
**Impact if wrong:** Need to add a manual entry path or batch import capability.  
**Status:** `[Assumed]`

---

### C3 — Facility Operates 5 Days a Week, 8-Hour Shifts
**Statement:** SLAs in the escalation table (30 min, 4 hours, etc.) are calibrated to a 5-day, 8-hour operating schedule. "During operating hours" means Mon–Fri, 06:00–14:00 local time (or shift equivalent).  
**Why it matters:** If the facility operates 6 or 7 days, or runs double shifts, SLA timers that reference "during operating hours" must account for this.  
**Impact if wrong:** SLA timers expire during non-operating hours when no one can action them. WorkItems pile up.  
**Status:** `[Assumed]`  
**Validation question:** "What are the facility's operating hours and days? Does Loss Prevention work the same shift?"

---

### C4 — Processors Have Individual User Accounts in the System
**Statement:** Each processor logs into the RDA station with a unique user ID, enabling `processor_id` and `condition_grade_assigned_by` to be populated per-person (not per-station).  
**Why it matters:** Per-processor accuracy tracking (for the accuracy dashboard and for training feedback) requires individual identification. Station-level IDs would prevent this.  
**Impact if wrong:** Cannot track per-processor accuracy. Loses a key value lever: identifying and coaching low-accuracy processors.  
**Status:** `[Assumed]`

---

## D — Scope & Design Assumptions

### D1 — No Image Capture at Intake Station (V1)
**Statement:** The intake station does not have a camera or image capture device. Condition grading is entirely processor-driven via rubric + drop-down selection. The agent cannot assess physical condition independently.  
**Why it matters:** A significant portion of the automation opportunity (autonomous condition grading) is blocked by this constraint. It is a hard V1 constraint.  
**Impact if wrong (upside):** If cameras are added or already exist, autonomous condition grading becomes feasible for clear-cut cases, significantly increasing the autonomous handling rate.  
**Status:** `[Known — confirmed by VP of Operations]`  
**Phase 2 recommendation:** Camera installation at intake stations to enable computer vision-based condition grading.

---

### D2 — Customer Return History Lookback Window is 90 Days for SERIAL_RETURNER, 30 Days for VELOCITY
**Statement:** The SERIAL_RETURNER signal uses a 90-day window (≥5 returns); the CUSTOMER_RETURN_VELOCITY signal uses a 30-day same-address window (≥3 returns).  
**Why it matters:** These thresholds determine the signal sensitivity. Shorter windows = more sensitive but more false positives. These specific values are engineering choices, not confirmed business rules.  
**Impact if wrong:** Signal false-positive rate may be higher or lower than the **≤5%** threshold in validation design.  
**Status:** `[Assumed — starting parameters subject to tuning during pilot]`  
**Tuning plan:** Measure false-positive rate during pre-production pilot; adjust thresholds before live deployment.

---

## Summary: What Must Be Validated Before Building

Priority 1 (blocks building):
- A1 — WMS API exists and is accessible
- A3 — API credentials and base URLs available
- B1 — High-value threshold formally confirmed
- B5 — Reason code list is exhaustive

Priority 2 (blocks accurate fraud detection):
- A2 — SFCC customer return history API available
- A4 — API rate limits sufficient
- A7 — Fraud reference data export process confirmed

Priority 3 (affects ROI model):
- B3 — Actual fraud rate from historical chargebacks
- C3 — Operating hours for SLA calibration
