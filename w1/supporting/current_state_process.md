# Current State Process — Retail Returns Disposition
## Purpose

This document maps the **as-is process** at the returns facility before any agentic solution is introduced. It exists so that the delegation analysis and agent spec are grounded in what the work actually is — not a generic description of "returns processing."

Sources: scenario description + reasonable retail-industry inference. All inferred details are flagged `[Inferred]` and should be validated with the client. Confirmed details are flagged `[Stated]`.

---

## Facility Overview

| Attribute | Value | Source |
|---|---|---|
| Annual revenue | ~$280M | [Stated] |
| Store count | 60 stores + online channel | [Stated] |
| Return volume | ~4,500 items/week | [Stated] |
| Annual return volume | ~234,000 items/year | [Calculated: 4,500 × 52] |
| Processing team | 12 returns processors | [Stated] |
| Current reason-code accuracy | ~78% | [Stated] |
| Current fraud detection rate | ~40% | [Stated] |

---

## Volume Math

**Daily volume:**
- Assuming 5-day operating week: ~900 items/day
- Per processor per day: ~75 items (900 ÷ 12)
- Per processor per hour (8-hour shift): ~9.4 items/hour
- Average time per item: ~6–7 minutes [Inferred]

**Weekly reason-code errors (based on 78% accuracy):**
- 4,500 × 22% = ~990 mis-classified items per week
- ~51,480 mis-classified items per year

**Annual fraud exposure (based on 40% catch rate):**
- Assumption: 1–2% of returns involve attempted fraud [Inferred — industry average for apparel is 1–3%]
- At 1%: 2,340 fraud attempts/year → 1,404 undetected (60%)
- At 2%: 4,680 fraud attempts/year → 2,808 undetected (60%)
- Average loss per undetected fraudulent return (item value + processing + chargeback fee): ~$60–$100 [Inferred]
- Estimated annual undetected fraud loss: **$84K–$281K** [Calculated range]

---

## Step-by-Step Current Process

### Step 0 — Return Arrival
- Customer or store ships item to central returns facility
- Item arrives with a return merchandise authorization (RMA) number or packing slip [Inferred — standard retail]
- Some returns arrive without documentation (lost packing slip, store-originated returns) [Inferred]
- Item is placed in an intake queue

### Step 1 — Item Identification
**Who:** Returns processor  
**How:** Scan barcode/SKU label if present; manual lookup if label is missing or damaged [Inferred]  
**Output:** Item matched to original order in OMS (Order Management System) [Inferred]  
**Failure mode:** ~5–10% of items arrive with missing or unreadable labels; processor must identify by visual inspection or customer note [Inferred]  
**Time:** ~30–60 seconds per item [Inferred]

### Step 2 — Reason Code Classification
**Who:** Returns processor  
**How:** Processor reads customer-provided return reason (written on packing slip or submitted via online return portal) and assigns one of 5 reason codes [Inferred]:

| Code | Label | Description |
|---|---|---|
| RC-01 | DEFECTIVE | Item arrived damaged or failed in normal use |
| RC-02 | DIDNT_FIT | Size/fit issue, item otherwise in good condition |
| RC-03 | CHANGED_MIND | Customer changed mind, impulse return |
| RC-04 | WRONG_ITEM | Retailer shipped wrong SKU or color |
| RC-05 | SUSPECTED_FRAUD | Return deemed suspicious by processor |

**Current accuracy:** 78% [Stated]  
**Why accuracy is low:** [Inferred]
- No written rubric — each processor applies personal interpretation
- Customer-provided reasons are often inaccurate (e.g., "defective" claimed to avoid restocking fee when item is actually in perfect condition)
- Processors vary in experience; new hires take 6–8 weeks to reach full accuracy
- Fatigue: ~75 items/day with no system support leads to pattern fatigue

**Time:** ~1–2 minutes per item [Inferred]

### Step 3 — Physical Condition Inspection
**Who:** Returns processor  
**How:** Visual inspection only — no standardized scoring rubric [Stated: "visually and by memory"]

Likely condition categories applied informally [Inferred]:
| Grade | Description |
|---|---|
| LIKE_NEW | Unworn, tags attached, original packaging |
| GOOD | Worn or tried on, no visible defects, sellable |
| FAIR | Minor defects (loose thread, slight mark), sellable at discount |
| POOR | Significant defects, not sellable as-is |
| UNSELLABLE | Damaged beyond resale (stains, tears, structural failure) |

**Current failure modes:**
- No consistent grading rubric → same item graded differently by different processors [Inferred]
- "FAIR" vs "POOR" boundary is especially inconsistent [Inferred]
- Condition grade directly affects disposition lane → inconsistency cascades downstream

**Time:** ~2–3 minutes per item [Inferred]

### Step 4 — Fraud Assessment
**Who:** Returns processor  
**How:** Gut-check based on experience — "does something feel off?" [Stated: "by memory"]

Known fraud signals in apparel returns [Industry standard — Inferred as applicable]:
- Item returned is different from item that was shipped (switched item — e.g., counterfeit returned in place of genuine item)
- Serial returner: same customer address, >3 returns in 30 days
- Receipt of delivery with return claim "never received"
- Damage appears staged (deliberate tear, not wear-and-tear)
- High-value item, return without original packaging or tags
- Return window exceeded but claimed within window

**Current detection rate:** 40% [Stated]  
**Why 60% escapes:** [Inferred]
- Processors are not trained on fraud signal patterns consistently
- No system-level data on customer return history available at the workstation
- Fraud signals require cross-referencing multiple data points (customer history, item condition, claim vs. actual) — hard to do manually at 75 items/day
- "Suspected fraud" triggers additional paperwork; processors may subconsciously avoid the flag to maintain throughput

**Time:** 0–5 minutes depending on suspicion level [Inferred]

### Step 5 — Disposition Routing
**Who:** Returns processor  
**How:** Combination of reason code + condition grade determines lane, applied from memory [Stated: "by memory"]

Current routing logic (inferred from industry standard):
| Condition | Reason Code | Typical Disposition |
|---|---|---|
| LIKE_NEW | Any non-fraud | RESTOCK_AS_NEW |
| GOOD | DIDNT_FIT / CHANGED_MIND | RESTOCK_AS_NEW or OUTLET depending on policy |
| GOOD | DEFECTIVE | REFURBISH (quality check first) |
| GOOD | WRONG_ITEM | RESTOCK_AS_NEW (retailer error) |
| FAIR | Any non-fraud | OUTLET (discount lane) |
| POOR | Any | REFURBISH or DONATE depending on brand policy |
| UNSELLABLE | Any | DESTROY |
| Any condition | SUSPECTED_FRAUD | HOLD for Loss Prevention review |

**Current failure modes:**
- No written routing table — each processor applies their own mental model
- Inconsistent application leads to value leakage: items that could be restocked at full price going to outlet, or outlet items being destroyed
- High-value items with GOOD condition going to outlet instead of restock = direct margin loss

**Time:** ~30 seconds per item [Inferred]

### Step 6 — Physical Routing & Documentation
**Who:** Returns processor  
**How:** Item placed in physical lane bin; reason code and disposition recorded in a system [Inferred — likely a basic WMS or spreadsheet]  
**Time:** ~30 seconds [Inferred]

---

## Total Per-Item Time Estimate

| Step | Time |
|---|---|
| Identification | 45 sec |
| Reason code | 90 sec |
| Condition inspection | 150 sec |
| Fraud assessment | 60 sec (average) |
| Disposition routing | 30 sec |
| Documentation | 30 sec |
| **Total** | **~6.5 minutes** |

At 12 processors × 8 hours × 60 min = 5,760 processor-minutes/day.  
At 6.5 min/item = 885 items/day capacity. Matches the ~900/day volume. The team is running near-capacity.

---

## Current System Landscape (Inferred — Must Validate)

| System | Probable Use | Confidence |
|---|---|---|
| OMS (Order Management) | Customer order history, return requests, original order data | High — standard retail |
| WMS (Warehouse Management) | Inventory tracking, physical bin locations, disposition lanes | High — standard at this scale |
| Returns portal | Customer-facing return initiation, reason submission | High — online channel present |
| Loss Prevention system | Fraud flags, chargeback records | Medium — may be manual/spreadsheet |
| Image capture at intake | [Virtual discovery: **none**; VP confirmed no camera at the station. Treat as not available for V1; validate with client.] | Confirmed in `stakeholder_discovery.md` for this practice pack |

---

## Key Pain Points Summary

| Pain Point | Root Cause | Business Impact |
|---|---|---|
| 78% reason-code accuracy | No rubric, processor experience variance | Bad analytics, wrong chargebacks, wrong fraud detection |
| 40% fraud detection | No system support for pattern recognition, processor fatigue | $84K–$281K estimated annual undetected fraud |
| Near-capacity throughput | Manual process at 6.5 min/item × 12 people | No buffer for volume spikes |
| Inconsistent condition grading | No rubric, "by memory" | Value leakage: full-price items going to outlet |
| High-value item mis-routing | No system flag for value threshold | Direct margin loss |
| Processor ramp-up time | 6–8 weeks to reach full accuracy | Seasonal hiring is expensive and slow |
