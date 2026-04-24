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
