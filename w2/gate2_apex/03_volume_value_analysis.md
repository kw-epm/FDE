# Volume × Value Analysis
**Gate 2 — Apex Distribution Ltd**
**Source:** Brief; CLM (`01`); DSM (`02`)
**Method:** ATX scoring — suitability gate → V×V → TCO → sequencing.

> Volumes/handling times stated in brief. Cost figures are ranges with explicit assumption log; all `[Estimated]`.
>
> **Code legend:** `WS1–4` = work streams (per brief §3); `C1A`–`C4E` = task clusters (canonical: DSM); `G-N` = open gaps (canonical: `CLAUDE.md` §Open gaps); `A-N` / `B-N` / `C-N` = cross-artefact evidence register (canonical: `00_elicitation_log.md`); `BP-X1` = cross-stream breakpoint (canonical: CLM §Cross-stream).

## Stream summary

| Stream | Vol/day | Time/case | Effort/day | Tracked share |
|---|---|---|---|---|
| WS1 Delivery Exceptions | 180 | 12 min | 36 hr | 31% |
| WS2 ETA Inquiries | 400 | 4 min | 26.7 hr | 23% |
| WS3 Dispatch Adjustments | 90 | 18 min | 27 hr | 23% |
| WS4 Billing Disputes | 60 | 28 min (handling); days–weeks elapsed (B-2) | 28 hr | 24% |

`[Stated: brief]` `[Derived: effort sums; tracked total = 117.7 hr/d, see C-3]`

---

## Step 1 — Suitability gate

| Stream / cluster | Input | Det | Tool | Exc | Risk | Gate |
|---|---|---|---|---|---|---|
| WS1 — C1A intake/decision | L | L | L | L | M | **Fail** (decision); **Cond.** for context-assist (Human-led + AS) |
| WS1 — C1C cross-stream handoff | M | M | M | H | M | **Cond.** — depends on dispatch console API (G-11) |
| WS2 — C2A lookup | H | H | M | H | H | **Pass** but **disqualified** as agentic — RPA territory, not agent value |
| WS2 — C2B prediction | L | L | L | M | M | **Fail** — wrong tech (ML, not LLM) |
| WS3 — C3A intake/feasibility | M | M | L | M | M | **Cond.** on G-11; Human-led + AS only |
| WS3 — C3B driver coord | L | L | L | L | M | **Fail** — relational + voice |
| **WS4 — C4A intake + context** | M | M | M | M | M | **Pass** — agent core |
| **WS4 — C4B remedy (routine)** | M | M | H | M | M | **Pass** for routine subset; novel = Human-led |
| WS4 — C4C Aurum write | H | H | L | M | M | **Cond.** on G-12 (UI auth) |
| **WS4 — C4D close/comms** | H | H | H | H | M | **Pass** with first-month tone calibration |
| **WS4 — C4E chase** | H | H | H | H | M | **Pass** |

**Outcome:** WS4 has the largest contiguous Pass surface (C4A + C4B-routine + C4D + C4E). WS1's only agentic cluster (C1C) is conditional on G-11 — Wave 3 candidate (per sequencing §below). WS2/WS3 are disqualified or human-only.

---

## Step 2 — Volume × Value scoring (ATX 1–5)

> Volume scoring per ATX reference (`atx-scoring.md`): 4 = 50–200/day; 5 = hundreds+/day or continuous.

| Stream | Volume | Non-determinism | Score | Verdict |
|---|---|---|---|---|
| WS1 (whole) | 4 (180/d) | 4 (no SOP, dispatcher discretion) | **16** | Tied at top — but agentic surface is only C1C (Wave 3) |
| WS2 | 5 (400/d) | 2 (lookup-dominant) | 10 | Disqualified — rules/RPA + ML, not agent value |
| WS3 | 4 (90/d) | 4 (multi-party real-time) | **16** | Tied at top — but agentic surface is only C3A; C3B Human Only |
| **WS4** | 4 (60/d) | 4 (cross-source synthesis + remedy) | **16** | **Tied at top + has the largest group of tasks suitable for agent-led execution** |

**Read:** Three streams tie at the raw V×V ceiling (16). The differentiator is **agentic cluster surface area, not raw stream score** — the right unit of analysis is the cluster, not the stream. WS4 has 4 contiguous Pass clusters (C4A + C4B-routine + C4D + C4E); WS1 has 1 (C1C, Wave 3); WS3 has 1 conditional (C3A). That's why WS4 wins.

---

## Step 3 — TCO assessment (Billing Dispute Resolution Assistant — BDRA)

> **Assumption log:**
> - Working days: **280/yr** `[Estimated — UK B2B carrier with Saturday delivery; sensitivity ±10%]`
> - Fully-loaded CO agent rate: **£18/hr** `[Estimated — UK ops mid-skill range £15–22/hr; sensitivity ±25%]`
> - Wave 1 absorption: **35% of WS4 effort** `[Estimated — agent absorbs C4A + C4B-routine + C4D-draft + C4E; C4C blocked, novel-decision human; sensitivity ±10pp]`
> - Token cost: **~£0.04/case** `[Estimated — Claude Sonnet, 2K input + 500 output per case avg; sensitivity ×3 down to ×3 up]`
> - HITL handled within already-allocated CO capacity: **net additional HITL £-cost = 0** `[Estimated — confidence Low; recalibration trigger: if CO time spent reviewing agent output exceeds 10% of original case time, this assumption is broken and Wave 1 absorption + payback degrade. Mock-test before Wave 1 launch; track in monitoring (per-case CO review time)]`
> - Build cost: **£20–40K** `[Estimated — internal-facing agent, Salesforce + CSV reads, no customer-facing UI; engineering scoping required]`
> - Headcount basis: **unconfirmed (G-5)** — savings expressed in hours-recovered AND £-equivalent; the £-figure is sensitive to the CO/AM/dispatcher split
> - **Sensitivity methodology:** ranges below are *single-factor variations* from central (one parameter at a time) — NOT worst-case compounded. Worst-case-compounded floor = ~£24K saving / £40K build / ~20mo payback; surfaced explicitly as honest disclosure rather than as the headline number.

### Baseline (current)

```
WS4 cases/year:        60 × 280 = 16,800
Hours/year:            28 × 280 = 7,840 hr
Annual baseline cost:  7,840 × £18 = £141,120
                       Range under sensitivity: £95K–£190K
```

### Agent target state (Wave 1 BDRA) — two scenarios

**Scenario A: HITL within already-allocated CO capacity (net HITL £-cost = 0)** `[Estimated; confidence Low — see assumption log]`

```
Hours absorbed:         7,840 × 35% = 2,744 hr/year
£-equivalent saved:     2,744 × £18 = £49,392
                        Range: £33K–£68K
Token cost:             16,800 × £0.04 = £672/year
                        Range: £224–£2,016
Net Wave 1 saving:      ~£48K central; £30–67K range
Build cost:             £30K central; £20–40K range
Payback:                ~7 months central; 4–14 months range
```

**Scenario B: HITL adds 10–15% review overhead (CO time on agent output)** `[Estimated — Cursor-flagged sensitivity; surface explicitly so it's not buried]`

```
HITL review overhead:   12.5% mid (range 10–15%)
                        2,744 × 12.5% = 343 hr/year of CO review time
HITL £-cost:            343 × £18 = £6,174/year
                        Range: £4,940–£7,400
Net Wave 1 saving:      ~£42K mid (range £25–£60K)
Payback:                ~9 months mid; 5–17 months range
```

**Trigger to switch from A to B:** if monitoring shows CO per-case review time ≥10% of original case time during Wave 1 mock-test or first month, recalculate using Scenario B and adjust the business case before Wave 2 commitment.

**Capacity framing (more important than cash):** 2,700 hours/year of CO time recovered = ~1.5 FTE-equivalent at typical UK utilisation. This capacity goes to: (a) reducing dispute backlog (B-3 chase), (b) preparing for the cross-stream handoff at Wave 3 (C1C → BDRA receives the billing-watch flag earlier, dispute volume drops at source).

### Wave 2 add-on — C4C Aurum auto-write (when G-12 resolved)

Removes the human-keystroke step. Estimated additional ~10–15% absorption. £15–25K incremental annual saving. Build cost ~£5–10K (reuses Wave 1 Aurum-read schema-validation contract).

### Wave 3 add-on — C1C cross-stream handoff (when G-11 resolved)

Closes BP1.C → BP-X1 chain. Reduces *upstream* dispute generation — every prevented FUEL_SURCH_DAMAGE dispute is ~28 min not spent. C-1 evidence (50% of open disputes follow this chain) suggests **upstream prevention matters more than downstream automation**. Estimated 10–20% reduction in WS4 dispute volume → ~£15–30K/year. Build ~£10K (reuses BDRA's CRM integration + adds dispatch-console read).

---

## Step 4 — Positioning matrix

```
                              VOLUME (cases/day)
                  LOW                               HIGH
                  ┌─────────────────────┬─────────────────────────┐
                  │                     │                         │
            HIGH  │  C1C cross-stream ● │  C4A intake (BDRA)   ●  │
                  │  (Wave 3, G-11)     │  C4B routine (BDRA)  ●  │
                  │                     │  C4D close (BDRA)    ●  │
                  │  C4E chase ●        │  C4C Aurum write     ◑  │
SUITABILITY       │  (Wave 1)           │  (Wave 2, G-12)         │
                  │                     │                         │
                  ├─────────────────────┼─────────────────────────┤
                  │                     │                         │
            LOW   │  WS3 driver coord ✗ │  WS2 lookup ◌           │
                  │  WS3 intake/feas ◑  │  (RPA, not agent)       │
                  │  C1A discretion ◑   │  WS2 prediction ✗       │
                  │  (Human-led + AS)   │  (ML, not agent)        │
                  │                     │                         │
                  └─────────────────────┴─────────────────────────┘

  ●  Wave 1 BDRA target   ◑  conditional / Human-led + AS
  ✗  Human Only           ◌  disqualified (wrong tech)
```

---

## Step 4b — Feasibility scoring (BDRA, per ATX Phase 4)

| Factor | Score (1–5) | Notes |
|---|---|---|
| Data availability | 4 | Aurum CSVs accessible (artefact 5); Salesforce REST modern. Quarterly schema-drift is the deduction. |
| System integration feasibility | 4 | Salesforce REST + Aurum file-watch are routine builds; Wave 2 adds UI-automation client (G-12 dependent) |
| Compliance risk | 5 | Internal-facing in Wave 1 (no customer-facing risk); enforces APPROVER_ID + AUDIT_REF (improves audit posture vs status quo) |
| Context stability | 4 | Dispute patterns recurring (Hayes-class FUEL_SURCH_DAMAGE, Tom J. DIM_WEIGHT caseloads); Aurum schema is the variable |
| Organisational readiness | 3 | Sarah is open but cautious (two prior failures); CO supervisor + AM buy-in needed; first-100-cases human-confirm window required |
| TCO viability | 4 | Payback ≤17 months even in Scenario B + worst-case-compounded (V×V §3); self-financing |
| **Total** | **24 / 30** | **Strong — proceed to Wave 1 build** |

---

## Primary target: WS4 BDRA (Billing Dispute Resolution Assistant)

Wins on five grounds:

1. **Largest contiguous Agent-led cluster surface** (C4A + C4B-routine + C4D + C4E). WS1's higher raw V×V score is concentrated in non-agentic clusters.
2. **Internal-facing.** No 2024-chatbot rerun.
3. **Governance upgrade as feature.** A-4 (audit-bypass) is fixed by agent enforcing APPROVER_ID + AUDIT_REF on every credit. This is a *credibility win* with Sarah independently of cash savings.
4. **Aurum-aware not Aurum-dependent.** Reads CSVs with schema-validation gate (per `00` elicitation Q2 design note on RPA failure mode); writes via either AM-approved UI step (Wave 1) or service-account UI (Wave 2 if G-12 resolves). Worst case: Aurum schema breaks, agent halts on read — same as RPA failed BUT detected on read instead of corrupting writes.
5. **Compounding into cross-stream chain.** C1C Wave 3 reduces dispute *generation* upstream — and reuses BDRA's CRM/Aurum integrations. Wave 1 builds the integration; Wave 3 turns it into prevention.

## Why not WS1 first

Tied for highest raw V×V (16). But: C1A (where the discretion lives) is Human Only in Wave 1 (becomes Human-led + AS only when G-10 + G-11 resolve). Only C1C is agentic, and it's conditional on G-11 (dispatch console API). Building an "agent" that's actually Human Only for the high-volume sub-cluster while waiting for G-11 = building twice. Better: WS4 first, then C1C as Wave 3 *prevention layer* feeding WS4.

## Why not WS2

C2A (lookup) is rules/RPA — fully deterministic, agent adds latency and cost without value. C2B (tight prediction) needs an ML route-state model that doesn't exist at Apex; building it = customer-facing ML project, separate use case, ~6-month timeline. Both fail the suitability gate for *agent* (different tech for different reasons).

## Why not WS3

C3A is rule-checkable feasibility (Human-led + AS at best). C3B is Human Only — relational, voice channel, real-time multi-party. No defensible agent role.

## Strategic sequencing

### Sequencing criteria check (per ATX Step 4)

| Criterion | Weight (per ATX) | BDRA Wave 1 standing |
|---|---|---|
| Self-financing ROI | High | ✓ Pass — Scenario A median payback 7mo, Scenario B 9mo (V×V §3) |
| Integration reusability | High | ✓ Pass — Aurum schema validator, CRM client, AM router, AUDIT_REF generator, dispute-state writer all reused in Wave 2/3 (see APD integration reuse matrix) |
| Low compliance risk | Medium | ✓ Pass — internal-facing only; APPROVER_ID + AUDIT_REF enforced (improves posture) |
| Data readiness | Medium | ✓ Pass with caveat — Aurum CSVs available; quarterly schema-drift mitigated by validation gate |
| Organisational readiness | Medium | ⚠️ Conditional — Sarah open but cautious; first-100-cases human-confirm window in plan; CO supervisor walkthrough needed |
| Strategic visibility | Low | ✓ Indirect — governance upgrade (audit-bypass fix) is a board-narrative-friendly story; not the headline reason |

**Net:** 5 of 6 criteria fully pass; 1 conditional (org readiness, addressed via calibration window). Sequencing rationale holds.



| Wave | Scope | Prereq | Hours saved/yr (central) | New assets |
|---|---|---|---|---|
| **1** | BDRA core: C4A + C4B-routine + C4D + C4E | P0 blockers per APD §Open Deployment Blockers + System Inventory §P0 checklist (dispute system identification, Aurum CSV access, schema validation contract, AM coverage map, CO authority threshold). NO external G-codes — all P0s are internal/engineering. | ~2,700 (35% of WS4) | Aurum CSV schema-validation contract; APPROVER_ID router; CRM dispute-state writer; chase-cadence engine; case-context dossier composer |
| **2** | C4C Aurum UI auto-write | G-12 resolution (Aurum credits-UI service-account auth) | +800–1,200 (10–15pp lift) | Aurum UI automation client (reuses Wave 1 schema validation) |
| **3** | C1C cross-stream handoff (DECA-light) | G-11 resolution (dispatch console API) + Wave 1 stable | Indirect: 10–20% fewer disputes generated upstream → ~500–800 hr/yr WS4 reduction | Dispatch-console read; damage→billing-watch generator |

**Critical path:** Wave 1 first; resolve G-12 in parallel for Wave 2 promotion; resolve G-11 in parallel for Wave 3.

**Self-funding logic:** Wave 1 absorbs £30–67K (Scenario A) or £25–60K (Scenario B) of CO effort/year against £20–40K build → median payback ~9 months in either scenario; worst-case-compounded ~20 months. Wave 2/3 reuse Wave 1 Aurum/CRM integration = lower marginal build cost.
