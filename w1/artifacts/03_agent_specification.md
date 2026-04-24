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
