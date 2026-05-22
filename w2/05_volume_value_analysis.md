# Volume × Value Analysis
**Scenario 4 — Community Content Moderation (MiniBase)**
**Date:** 2026-04-30
**Source:** Brief (scenario4.md), CLM (02_cognitive_load_map.md), DSM (03_delegation_suitability_matrix.md)
**Method:** ATX Use Case Scoring (suitability gate → volume × value → TCO → sequencing)

> **Epistemic status:** Volumes and handling times are stated in the brief. Cost figures are estimates with assumptions logged below; all marked `[Estimated]`. Token costs use approximate Claude Sonnet pricing; actuals require mock testing.

---

## Stream Summary

| Work stream | Volume/day | Time/case | Effort/day | Team share |
|---|---|---|---|---|
| WS1 — Routine spam / clear violation | 1,080 | 30 sec | 9 hrs | 19% |
| WS2 — Grey-zone case review | 360 | 5 min | 30 hrs | 64% |
| WS3 — User dispute appeals | 60 | 8 min | 8 hrs | 17% |
| WS4 — IP-claim resolution | ~0.6 | 30 min+ | <0.3 hrs | <1% |

`[Stated: brief]` `[Derived: effort totals; denominator = 10-person team at capacity]`

---

## Step 1 — Suitability Gate

| Stream / sub-cluster | Input | Det. | Tool | Exc. | Risk | Gate |
|---|---|---|---|---|---|---|
| WS1 — Routine spam | H | H | M | M | M | **Conditional** — VIP service required |
| WS2 — Decision cluster | M | L | L | L | M | **Fail** — judgment-bound |
| WS2 — Context assembly | M | M | L | L | M | **Conditional** — sub-forum norms blocker |
| WS3 — Context assembly (5a) | M | M | M | M | M | **Conditional** — depends on WS2 log quality |
| WS3 — Final ruling (5b) | L | L | M | L | M | **Fail** — same as WS2 decision |
| WS4 — IP-claim resolution | M | L | L | L | L | **Fail** — legal risk; no triage criteria |

**Outcome:** WS1 and WS3-5a pass conditionally. WS2 context assembly passes conditionally but is blocked on a hard prerequisite (sub-forum norm structuring). WS2 decision, WS3 final ruling, and WS4 fail outright.

---

## Step 2 — Volume × Value Scoring

ATX 1–5 scales. Gate-passing streams scored for build prioritisation; gate-failing streams scored for completeness only.

| Stream / cluster | Volume | Non-determinism | Score | Verdict |
|---|---|---|---|---|
| WS1 — Routine spam | 5 (1,080/day) | 3 (rule-based core, NL classification, borderline detection) | **15** | Strong — gate PASS |
| WS2 — Context assembly | 5 (360/day) | 3 (multi-source synthesis) | 15 | Strong — but BLOCKED |
| WS2 — Decision | 5 | 5 (policy + tacit norms) | 25 | Highest score — gate FAIL |
| WS3 — Context assembly (5a) | 4 (60/day) | 3 (retrieval + dossier) | 12 | Consider — gate PASS |
| WS4 — IP-claim resolution | 1 (~0.6/day) | 5 (legal judgment) | 5 | Below threshold — gate FAIL |

**Read of the table:** WS1 is the highest-scoring stream that *also* passes the gate. The two "higher value" possibilities (WS2 decision, WS2 context) are blocked by structural gaps (judgment indelegability, missing sub-forum norms). WS3-5a is a downstream candidate that benefits directly from WS1 infrastructure.

---

## Step 3 — TCO Assessment (Preliminary)

> **Assumption log:**
> - Volunteer time valued at £12/hr opportunity equivalent `[Estimated; not stated in brief]`
> - 365 working days/yr (no seasonality data)
> - Token cost (WS1, classification): ~400 tokens/case (300 in + 100 out) at ~$0.003/case ≈ **£0.0024/case** at 1.27 USD/GBP, rounded to **£0.003/case** including infra `[Estimated]`
> - Token cost (WS3, dossier assembly): ~700 tokens/case (longer context retrieval + synthesis), rounded to **£0.005/case** `[Estimated]`
> - HITL cases handled by volunteers within already-allocated capacity → **net additional HITL £-cost = 0**
> - Build cost: £15K–25K Wave 1, £5K–8K Wave 2 `[Estimated; requires engineering scoping]`

### WS1 — Routine Moderation Agent

```
Human baseline (current state):
  Cases per year:           1,080 × 365 = 394,200
  Time per case:            30 sec (0.00833 hr)
  Volunteer hours/yr:       394,200 × 0.00833 = 3,283 hrs
  Annual baseline cost:     3,283 × £12 = £39,394 [Estimated]

Agent target state (80% autonomous coverage):
  Autonomous cases:         80% × 394,200 = 315,360 cases/yr
  HITL cases:               20% × 394,200 = 78,840 cases/yr
  Token cost (all cases):   394,200 × £0.003 = £1,183/yr
  HITL human cost:          0 (already-allocated volunteer capacity)
  Annual agent cost:        ~£1,183/yr [Estimated]

Economics (corrected — saves only the 80% the agent absorbs):
  Volunteer hours freed:    315,360 × 0.00833 = 2,627 hrs/yr
  Volunteer cost freed:     2,627 × £12 = £31,524 [Estimated]
  Net saving:               £31,524 - £1,183 = £30,341/yr [Estimated]
  Build cost:               £15,000–25,000
  Payback period:           6–10 months
  Year 1 ROI:               21–102%
  3-year ROI:               264–507%
  Economic gate:            PASS
```

**Capacity framing.** The team is at capacity. The £30K/yr cash figure understates the value: the binding constraint is volunteer hours, not cash. 2,600 hours/yr returned to the team allows WS2 capacity growth without adding headcount and reduces volunteer burnout.

### WS3-5a — Context Assembly (preliminary, Wave 2)

```
Human baseline:
  Cases per year:           60 × 365 = 21,900
  Context-assembly time:    ~4 min/case [Estimated split of 8 min total]
  Volunteer hours/yr:       21,900 × 0.0667 = 1,461 hrs
  Annual baseline cost:     1,461 × £12 = £17,532 [Estimated]

Agent target state (70% dossier-completeness; remaining 30% need human top-up):
  Token cost (all cases):   21,900 × £0.005 = £110/yr (longer assembly)
  Annual agent cost:        ~£110/yr [Estimated]

Economics:
  Hours freed:              70% × 1,461 = 1,023 hrs/yr
  Cost freed:               1,023 × £12 = £12,272 [Estimated]
  Net saving:               £12,272 - £110 = £12,162/yr [Estimated]
  Build cost:               £5,000–8,000 (reuses Wave 1 assets)
  Payback period:           5–8 months
  Economic gate:            PASS — but quality depends on WS2 log quality (currently thin)
```

---

## Step 4 — Positioning Matrix

```
                         VOLUME
                LOW                       HIGH
              ┌─────────────────┬─────────────────────┐
              │                 │                     │
         HIGH │  WS3-5a ●       │  WS1 ●              │
              │  60/day         │  1,080/day          │
SUITABILITY   │  Score 12       │  Score 15  ←PRIMARY │
              │  gate PASS      │  gate PASS          │
              │                 │                     │
              │                 │  WS2-context ○      │
              │                 │  360/day · Score 15 │
              │                 │  PASS but BLOCKED   │
              ├─────────────────┼─────────────────────┤
              │                 │                     │
         LOW  │  WS4 ✗          │  WS2-decision ○     │
              │  ~0.6/day       │  360/day            │
              │  Score 5        │  Score 25           │
              │  gate FAIL      │  gate FAIL          │
              │                 │                     │
              └─────────────────┴─────────────────────┘

● = buildable in Wave 1 or 2
○ = blocked or gate-fail (informational)
✗ = gate-fail, not pursued
```

**Read of the matrix:** WS1 sits in the top-right (high volume, high suitability) — the primary target. WS2-context shares the same quadrant on score and suitability but is BLOCKED on sub-forum norm prerequisites. WS2-decision in the bottom-right is the trap that pure volume × value would mislead toward (highest raw score, ungated). WS3-5a is the secondary candidate.

---

## Primary Target: WS1 — Routine Moderation Agent

WS1 wins on five grounds:

1. **Passes the suitability gate.** Only stream with H determinism and H input structure. The VIP gap is buildable infrastructure, not a missing decision framework.
2. **Highest gate-passing value score (15).** Tied with WS2 context assembly, which is blocked on undocumented sub-forum norms with no committed timeline.
3. **Best economics.** Payback 6–10 months, Year 1 ROI 21–102%, Year 3 ROI 264–507% [Estimated].
4. **Self-funding foundation.** The integrations Wave 1 builds (Discourse client, VIP service, policy RAG, log schema, mod-review-queue) are exactly what Wave 2 reuses. Wave 1 build cost is largely Wave 2's avoided integration cost.
5. **Structural risk reduction.** The VIP controlled-list service mitigates the existential failure mode named in the founder brief, across WS1, WS2, and WS4. Its absence is a current live risk; building it has value independent of the agent.

**Why not WS2 decision (score 25):** Gate fails on determinism and tool coverage. The 64% of effort is dominated by judgment that no rule resolves. Attacking it first means building everything from scratch and failing on the tacit-norms gap.

**Why not WS3-5a first (score 12):** Output quality is downstream of WS2 log quality, which is currently thin. WS1's structured log schema (task 1.7) is the prerequisite that makes WS3-5a defensible. Order matters.

---

## Strategic Sequencing

| Wave | Agent | Prerequisite | Effort recovery | Assets created |
|---|---|---|---|---|
| 1 | Routine Moderation (WS1) | VIP service built; Discourse write auth confirmed; gallery intake path resolved | ~7.2 hrs/day (80% of WS1) | Discourse client, VIP service, policy RAG, log schema, mod-review-queue, dead-letter store |
| 2 | Context Assembly (WS2 + WS3-5a) | Sub-forum norm table complete (14/14); WS2 minimum log standard | Partial WS2 + WS3-5a effort | Sub-forum norm data store |
| 3 | Multi-agent workflow | Wave 1 + 2 stable; decision log corpus indexed | Reduced grey-zone handling time | Decision log vector index, intake router |

**Critical path:** VIP service → Wave 1 launch → sub-forum norm table → Wave 2 launch. Both gates are infrastructure prerequisites, not preferences.
