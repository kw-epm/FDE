# Pre-Interview Brief Analysis & Cross-Artefact Evidence Register
**Gate 2 — Apex Distribution Ltd**
**Subject:** Sarah Whitmore, COO (primary)
**Date:** 2026-05-06

> Proxy answers are AI-reconstructions bounded to source. Where source is silent, proxy is silent and `OPEN` records the gap. Confidence rubric: **High** = ≥2 independent supports. **Medium** = 1 support + plausible mechanism. **Low** = inference only.

## Source index

| Source | Reference |
|---|---|
| Brief (§3) + Artefacts 1–4 (§4) | Gate 2 Participant Pack |
| Artefact 5 (Aurum CSV catalogue) | Gate 2 Participant Pack §4 |
| CSV exports (APEX_*.csv) | Gate 2 Artefacts folder accompanying the pack |
| Methodology references | ATX reference set (`atx-concepts.md`, `atx-assessment.md`, `atx-scoring.md`, `atx-agent-mapping.md`, `atx-economics.md`); plus `discovery-questioning-patterns.md` and `spec-ambiguity-vs-builder-mistakes.md` |

---

## Role / actor map

| Actor | Role | Evidence |
|---|---|---|
| Sarah Whitmore | COO; ex-dispatch (5y); 18mo in role | brief |
| Sandra W. | Customer Ops; ASSIGNED_TO on 4 of 6 open disputes (D-342, D-337, D-328, D-318); applied £170 manual override | artefact 2, APEX_DISPUTES_OPEN |
| Tom J. | Customer Ops; ASSIGNED_TO on 2 of 6 open disputes (D-339, D-301), both DIM_WEIGHT | APEX_DISPUTES_OPEN |
| Mark Petrov | Driver, route 042 | artefact 1 |
| Pete H. | Customer contact, Hayes & Sons (C-04451) | artefact 2 |
| U-0042 | Account manager → Aldgate, Northstar | APEX_CUSTOMER_MASTER |
| U-0089 | Account manager → Hayes, Travis & Mason, Severn | APEX_CUSTOMER_MASTER |
| U-0011 | Account manager → BlueSky (smallest, opened 2025-09-30, £5K limit) | APEX_CUSTOMER_MASTER |
| Aurum support | External; 48hr SLA on invoice modification tickets | brief |
| `SYS_BATCH` | Service account running overnight Aurum batch (CALC_USER on fuel surcharges) | APEX_FUEL_SURCH |
| Customer Ops (35) | Composition unstated — discovery gap | brief |

**No Customer Ops agent ID appears in any CSV column** (APPROVER_ID, ACCT_MGR, CALC_USER are all U-00xx AMs or SYS_BATCH). Sandra/Tom J. surface only in DISPUTES_OPEN.ASSIGNED_TO. Structural finding.

---

## AI-proxy elicitation

### Q1: 2024 chatbot — what did customers hate?

SARAH: We deployed a customer-facing chatbot. Customers hated it. We pulled it.

`[Stated: brief]`
`OPEN: failure mode + surface — discovery Q`
`DESIGN NOTE: anything customer-facing is the surface Sarah is most wary of, given the 2024 chatbot history. Bias to internal-facing agent.`
`[Inferred: customer-facing AI carries strong veto-risk with Sarah; confidence High — brief confirms chatbot was pulled + Sarah explicitly sceptical]`

### Q2: RPA on Aurum — what broke?

SARAH: An RPA that did billing reconciliation. It broke when Aurum's schema changed.

`[Stated: brief]`
`OPEN: which file, failure mode, detection lag — discovery Q`
`DESIGN NOTE: any agent ingesting Aurum CSVs needs schema-validation contract per file with hard-fail on mismatch. Silent re-mapping is not acceptable.`
`[Inferred: Aurum-fragile designs carry strong veto-risk with Sarah; confidence High — brief confirms RPA broke + Sarah explicitly sceptical]`

### Q3: SOP §4.3 "Damaged consignments" is TBD — what is the real workflow?

SARAH: SOP's silent because we never agreed insurance protocol. In practice: driver calls dispatch; dispatch decides on the call.

`[Stated: artefact 4 (TBD), artefact 1 (Mark calls dispatch for damaged-pallet decision)]`
`[Inferred: dispatcher discretion = de facto procedure; confidence High — two independent supports: artefact 4 (no documented procedure exists) + artefact 1 (lived behaviour shows dispatcher making the call)]`
`OPEN: dispatcher decision criteria — discovery Q`
`OPEN: handoff exception → billing follow-up — discovery Q`
`DESIGN NOTE: damaged-consignment is the cross-stream value chain (exception → dispute). Agent must address the handoff, not either stream in isolation.`

### Q4: Sandra's £170 manual override — pattern or one-off?

SARAH: Likely structural, not one-off. Customer Ops have no APPROVER_ID role; account managers do. Agents handle the customer call but lack credit authority — so they bypass.

`[Stated: artefact 2 internal note ("no entry in audit log"); APEX_CREDITS.APPROVER_IDs all match AM IDs in CUSTOMER_MASTER; Sandra/Tom J. only appear as DISPUTES_OPEN.ASSIGNED_TO]`
`[Inferred: structural authority/work mismatch is the mechanism; confidence High — three corroborating evidence points cited above]`
`OPEN: frequency, supervisor awareness, written/unwritten policy — discovery Q`
`DESIGN NOTE: agent-applied credits MUST emit APPROVER_ID + AUDIT_REF. Three policy options to test with Sarah: (1) raise agent authority, (2) agent proposes → AM approves async, (3) agent prepares → CO supervisor counter-signs.`

### Q5: 35-person Customer Ops — composition?

SARAH: [unstated in brief]

`[Stated: 35 total only]`
`OPEN: split (dispatchers / agents / AMs / supervisors); shift / depot structure — discovery Q (P0 — TCO baseline)`
`DESIGN NOTE: no £-saving claim without headcount basis. Carry "headcount basis unconfirmed" through V×V.`

### Q6: ETA inquiries — reality of 4-hour window?

SARAH: [grounded only on artefact 3]

`[Stated: artefact 3 — agent gives 13:00–17:00; customer asks tighter; agent gives 14:00–15:00 best-guess from "Driver's last GPS ping was 10:48 in Watford"; "We don't have a tighter ETA than that — sorry"]`
`[Inferred: tight-window prediction needs route-state ML model (drops × dwell × traffic), not LLM reasoning; confidence Medium-High — 1 artefact + uncontested domain reasoning, not 2 independent artefacts]`
`OPEN: customer-satisfaction signal on windows; % of ETA inquiries that pull dispatch — discovery Q`
`DESIGN NOTE: ETA looks like the obvious "high-volume easy" target but is structurally an ML problem (lookup is RPA; tight prediction is ML + customer-facing risk Sarah is wary of). Carry as deprioritised primary candidate pending discovery.`

### Q7: Aurum schema changes — frequency, notice?

SARAH: ~Quarterly. No prior notice.

`[Stated: brief]`
`OPEN: change type history; today's detection mechanism — engineering discovery`
`DESIGN NOTE: see Q2. Treat Aurum as untrusted external interface.`

### Q8: CEO's £1.2M ask — actual success metric?

SARAH: [unstated in brief]

`[Stated: brief — CEO heard competitor figure, asked Sarah to "look into it"; Sarah is "open to something that actually works"]`
`OPEN: CEO hard target vs anchor; failure threshold; board-reporting cadence — discovery Q (P0)`
`[Inferred: gap between CEO anchor and Sarah's risk tolerance; confidence Medium — 1 brief reference + Sarah's two prior failures; no CEO testimony]`
`DESIGN NOTE: design for credibility (no chatbot rerun, governance upgrade visible, audit trail enforced) over max £-saving on paper. Specific £-thresholds undefined pending Q8 discovery.`

---

## Cross-artefact evidence register

Three categories. Each row verified manually against source files.

### A — Confirmed contradictions (direct evidence conflict)

| # | Finding | Sources |
|---|---|---|
| **A-1** | SOP §4.2 references "DispatchHub tablet"; DispatchHub retired Oct 2024, replaced by Driver App. SOP stale ≥18mo. CLM-citing §4.2 as current = lived-vs-documented failure. | Artefact 4 + footnote |
| **A-2** | SOP §4.3 "Damaged consignments" = `[TBD pending review of insurance protocol]`. Most painful workstream has no documented procedure. | Artefact 4 |
| **A-3** | Pete's £170 applied ~day 6 of email thread; APEX_DISPUTES_OPEN snapshot still shows D-342 as PENDING_CLAIM. **System-of-record state ≠ real-world state.** Material for any "agent triages from disputes table" design. | Artefact 2 + APEX_DISPUTES_OPEN |
| **A-4** | Sandra's £170 has no audit entry; APEX_CREDITS schema requires APPROVER_ID + AUDIT_REF; APPROVER_IDs are all AM IDs; Sandra is CO not AM. Workaround is structural, not individual misconduct. | Artefact 2 + APEX_CREDITS + APEX_CUSTOMER_MASTER |
| **A-5** | APPROVER_ID does not consistently match the customer's specific AM: CR-815 (BlueSky AM=U-0011) approved by U-0042; CR-816 (Aldgate AM=U-0042) approved by U-0089. Approval is a *role*, not customer-specific. | APEX_CREDITS + APEX_CUSTOMER_MASTER |
| **A-6** | Sandra (artefact 2 msg 4): "fuel surcharge can't be adjusted on individual invoices"; APEX_CREDITS shows REASON_CODE=`FUEL_RECALC` for £45 (Northstar). FUEL_RECALC IS valid. Sandra either doesn't know, lacks authority, or it's policy-restricted. | Artefact 2 + APEX_CREDITS |
| **A-7** | APEX_DISPUTES_OPEN_20260414 contains D-342 with `OPEN_DT=2026-04-15` — date AFTER file's nominal date. Either filename ≠ data date, or forward-dated row. **Temporal trust in disputes file is questionable.** | APEX_DISPUTES_OPEN + catalogue |

### B — Inferential contradictions (derived, not directly stated)

| # | Finding | Sources |
|---|---|---|
| **B-1** | Brief: Aurum has "no real-time API" + "modifications require 48hr ticket"; Sandra applied £170 faster than 48hr. Inferred mechanism: credits enter Aurum via a UI used by Customer Ops, NOT via API and NOT via the support ticket. **The "no API" constraint is programmatic only — human UI exists.** Critical for agent design. (Not directly stated in source — derived from timing contradiction.) | Brief + artefact 2 |
| **B-2** | Brief: billing disputes = 28 min/case; Pete's case spans 9 days, 4 messages, multi-party. "28 min" = handling time, not elapsed. Multi-day disputes have N touch-points × context-reload cost. **Cognitive load > 28-min figure suggests.** | Brief + artefact 2 |
| **B-3** | D-337 (Hayes, REDELIVERY_FEE) status `AWAITING_CUST` since 2026-03-28, last update 2026-04-08 — 7+ days untouched. Inferred: Apex doesn't proactively chase customer responses on disputes. Agent opportunity: chase logic with timer. | APEX_DISPUTES_OPEN |

### C — Patterns and confirmations (cross-file findings, not contradictions)

| # | Finding | Sources |
|---|---|---|
| **C-1** | Hayes (C-04451) has 3 of 6 open disputes; 2 are FUEL_SURCH_DAMAGE; all 3 assigned to Sandra; £8,420 of £10,272 open A/R is in 0–30 bucket. Pattern: recurring customer + recurring failure mode + single handler + fast-accumulating fresh disputes. | APEX_DISPUTES_OPEN + APEX_AGED_RECEIVABLES |
| **C-2** | £170 absent from APEX_CREDITS_20260414. Consistent with timeline (credit applied ~5 days after file's data window). **However:** if applied "via manual override" without AUDIT_REF, may *never* appear in any future CREDITS file. Cannot verify without later snapshot. | Artefact 2 + APEX_CREDITS_20260414 |
| **C-3** | CO effort math: (180×12)+(400×4)+(90×18)+(60×28) = 7,060 min/day = 117.7 hrs/day. 35 ppl × 7.5hr × 80% util `[Estimated: typical UK knowledge-worker]` ≈ 210 hr/day capacity. Tracked = 56%. Not inconsistent — but means 44% non-stream (meetings/admin/untracked). **£-savings claim must flag headcount basis or it overstates.** | Brief math |
| **C-4** | APEX_RECON REC-2026-08842 (INV-04201, VAR=-£88, DISPUTE_OPEN) cross-references cleanly with D-339 (INV-04201, £88, DIM_WEIGHT, Tom J., AWAITING_CUST since 2026-04-12). **Cross-file linkage CAN work.** Counter-evidence to A-3/A-7 worry: disputes file may be reliable for older items, lag on freshly opened ones. | APEX_RECON + APEX_DISPUTES_OPEN |

---

## Provisional design hypothesis

Two candidates carried forward. CLM/DSM commits one (or both as Wave 1+2). Hard elimination requires discovery closure.

- **H1 — Billing Dispute Resolution Assistant.** Internal-facing. Highest unit value (28 min × 60/d). The audit-bypass fix becomes a feature (agent enforces APPROVER_ID + AUDIT_REF). Reads Aurum data but doesn't depend on Aurum's stability for writes.
- **H2 — Delivery Exception Context Assembler.** Internal-facing. Highest total effort (36 hrs/d). Pre-stages context for dispatcher's call with driver. Pure context-automation, not decision-automation.

**Deprioritised pending discovery:** ETA (chatbot scar surface + ML-not-LLM, per Q6); Dispatch Adjustments (no artefact, deeply relational with drivers).
