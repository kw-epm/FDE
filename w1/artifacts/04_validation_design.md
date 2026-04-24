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
