# CLAUDE.md — Apex Distribution Gate 2 ATX Assessment
**Gate 2 | Apex Distribution Ltd | Date: 2026-05-06**

## TL;DR (for the 30-second scan)

- **Primary agent:** **BDRA — Billing Dispute Resolution Assistant** (WS4 Wave 1; internal-facing)
- **Why:** largest contiguous Agent-led cluster surface (C4A + C4B-routine + C4D + C4E); the audit-bypass fix (A-4) becomes a feature; reads Aurum data but doesn't depend on Aurum's stability for writes (mitigates the 2024 RPA failure pattern)
- **Scope:** ~35% of WS4 effort absorbed = ~2,700 hr/yr. **Scenario A** (HITL within current CO capacity): £30–67K saving. **Scenario B** (HITL adds 10–15% review overhead): £25–60K saving. Build £20–40K. Median payback ~9 months in either scenario; worst-case-compounded ~20 months.
- **Roadmap:** Wave 2 = C4C Aurum UI auto-write (G-12 gated); Wave 3 = C1C cross-stream damage→billing watch (G-11 gated). Wave 3 is *upstream prevention* — likely the highest-impact wave.
- **Hard line:** never apply a credit without `APPROVER_ID + AUDIT_REF`; never customer-facing in Wave 1 (Sarah's 2024 chatbot scar); halt on Aurum schema-drift.
- **What's NOT here:** WS2 ETA (rules/RPA + ML, not agent value); WS3 driver coordination (relational, Human Only); WS1 dispatcher decision (Human Only Wave 1 — see DSM C1A).
- **Single biggest risk:** Sandra-class audit-bypass frequency (Q3 to Sarah). If widespread, Wave 1 ROI reframes around governance, not just hours.

---

## What this project is

ATX assessment of Apex's Customer Operations function. Goal: decompose the 4-stream cognitive work (delivery exceptions, ETA inquiries, dispatch adjustments, billing disputes), identify what to delegate to agents, design BDRA — the Wave 1 internal-facing Billing Dispute Resolution Assistant — and sequence Wave 2/3.

This is a Gate 2 timed exercise. All stakeholder testimony (Sarah Whitmore, COO) is AI-proxy reconstruction from brief artefacts and CSV exports. Nothing is confirmed by a real interview; the live clarification round produces the first stakeholder evidence.

---

## File inventory

| File | Purpose | Status |
|---|---|---|
| `00_elicitation_log.md` | AI-proxy elicitation, role/actor map, cross-artefact evidence register (3 categories), provisional design hypothesis | Working artefact — NOT a Gate 2 deliverable |
| `01_cognitive_load_map.md` | CLM: 4 work streams decomposed into JtDs, micro-tasks, zones, breakpoints; cross-stream topology; hotspot summary | Deliverable #1 |
| `02_delegation_suitability_matrix.md` | DSM: 12 task clusters scored on 7-dim ATX delegation suitability; archetype + rationale + open dependency per cluster; anti-pattern check | Deliverable #2 |
| `03_volume_value_analysis.md` | V×V: suitability gate, scoring, TCO with explicit assumption log + sensitivity, positioning matrix, primary-target rationale, why-not, sequencing | Deliverable #3 |
| `04_agent_purpose_document.md` | APD: BDRA full design — purpose, KPIs, autonomy matrix, escalation triggers, activity catalog, action mapping, context engineering, monitoring; Wave 2/3 abbreviated; compounding roadmap | Deliverable #4 |
| `05_system_data_inventory.md` | System & Data Inventory: Wave 1/2/3 systems, credentials, shared assets, P0 pre-launch checklists | Deliverable #5 |
| `06_discovery_questions.md` | Discovery: 9 P0 + 6 P1 questions for Sarah; testimony-vs-artefact watch annotations; question→artifact mapping | Deliverable #6 |
| `CLAUDE.md` | This file | Deliverable #7 |
| `Gate2-Krzysztof-Wilniewczyc.md` | Concatenated submission per pack §9 | Final |
| `_internal_methodology_coverage.md` | Submitter's own methodology-coverage map + maintenance note | Internal — NOT a deliverable; NOT in concatenated submission |

**Note:** Filename numbering matches deliverable order (00 = supplementary working artefact; 01–06 = deliverables #1–#6; CLAUDE.md = deliverable #7).

---

## Epistemic conventions

Every claim is tagged:

| Tag | Meaning |
|---|---|
| `[Stated]` | Present in brief, artefacts 1–5, or APEX_*.csv |
| `[Inferred]` | Reasoned hypothesis from evidence; confidence level attached |
| `[Derived]` | Calculated value (not stakeholder-confirmed) |
| `[Estimated]` | Cost/parameter assumption with explicit basis logged |
| `[Unconfirmed]` | Design choice depending on stakeholder/engineering input not yet available |

**Confidence rubric (`[Inferred]`):** High = ≥2 independent supports. Medium = 1 support + plausible mechanism. Low = inference only.

**Sources:** Gate 2 Participant Pack (brief + artefacts 1–4) + Gate 2 Artefacts folder (Aurum CSV samples for artefact 5).

**Discipline applied:** AI-proxy answers in `00` invent no narrative texture. Where source is silent, proxy is silent and `OPEN` records the gap.

---

## Key design decisions (non-obvious — preserve when editing)

1. **Primary agent = WS4 BDRA (billing disputes), not WS1 (delivery exceptions).** WS1 has higher raw V×V (16) but its agentic surface is a single cluster (C1C). WS4 has the largest contiguous Agent-led cluster mass (C4A + C4B-routine + C4D + C4E). The right unit of analysis is the *cluster*, not the *stream*.

2. **Internal-facing only in Wave 1.** Sarah's 2024 chatbot scar rules out customer-facing surfaces. BDRA assists CO agents and AMs; customers never talk to it directly.

3. **Audit-bypass (A-4) is fixed as a feature, not just an automation.** Every agent-emitted credit carries `APPROVER_ID + AUDIT_REF`. This is the credibility win with Sarah independent of cash savings.

4. **Aurum is read-stable, write-blocked in Wave 1.** Schema-validation contract per CSV; halt on drift (mitigates the RPA failure scar). Writes go via human-keystroke UI step (4.9E). Wave 2 promotes to service-account UI write only after G-12 resolves.

5. **Cross-stream value chain (BP-X1) is the structural insight.** Evidence + percentage in register C-1 + CLM §Cross-stream value chain. Wave 3 (DECA-light) closes this loop *upstream* — preventing disputes matters more than handling them faster.

6. **Routine vs novel split at C4B.** Routine = pattern matches a codified remedy template (Hayes-class FUEL_SURCH_DAMAGE → goodwill ≤ 50% of surcharge). Novel = always escalates with full dossier. Cross-mapping `dispute_type → remedy.type` is schema-enforced.

7. **AUDIT_REF format is BDRA-namespaced** (canonical: APD task 4.8) so audit can distinguish agent-emitted credits from human-emitted (`AUD-YYYY-NNNNN` stays for human credits).

8. **AM coverage map handles A-5 mismatches** (BlueSky/Aldgate cases where APPROVER_ID ≠ customer's specific AM). Configurable: prefer customer's AM, fall back to any active AM, alert if both unavailable.

9. **Customer comms are agent-drafted, human-confirmed in Wave 1.** First 100 cases tone-calibrate. Promotable to fully agent-led only after CO supervisor signs off.

10. **Chase logic at C4E closes B-3** (D-337 stalled 7+ days on AWAITING_CUST). Cadence T+7/T+14/T+30 provisional, pending Sarah Q13.

11. **Idempotency via `processing_id` written to CRM custom field** at task 4.2. Lookup at 4.6/4.9/4.12 makes duplicate retries no-ops.

12. **The agent does not compute tight ETA windows** (artefact 3 problem). That's an ML route-state model project, separate use case, customer-facing risk Sarah is wary of. WS2 prediction is Human Only.

13. **No dispatcher-replacement.** WS1 C1A and WS3 C3B are Human-led + Agent Support / Human Only. The dispatcher exercises real-time discretion under partial information; the agent does not enter that loop in Wave 1.

14. **Testimony-vs-artefact governance.** When Sarah's testimony in the live round conflicts with artefact / CSV evidence in the brief, **artefact evidence governs the design** unless Sarah provides contemporaneous documentation supporting her account. The pattern is "I think the answer is X" → check artefact → if mismatch, flag the divergence as a discovery sub-question, not a design overturn. (See Discovery #06 testimony-vs-artefact watch annotations on Q1, Q2, Q3, Q5, Q8.)

15. **Partial-failure recovery.** Tasks 4.9 (packet prepared) → 4.12 (state update) are not transactional in CRM; if a write fails mid-sequence, agent re-reads dispute state by `processing_id` on retry. Any step that succeeded is no-op on retry (idempotency via `processing_id` lookup at 4.6/4.9/4.12). Task 4.9E (AM email handoff) is NOT idempotent by default — confirm with engineering whether AM email queue dedupes by `AUDIT_REF`; if not, agent dedupes by checking CRM dispute state before re-emitting.

16. **"Fully agentic" ≠ "uses an LLM."** Of 16 BDRA activity-catalog tasks (APD §Activity Catalog), only 2 are pure LLM (4.6, 4.11) plus 2 partial / Hybrid (4.5, 4.13). The other 12 are **deterministic code** — script / rule / API call / RPA — wrapped inside the agent's autonomous flow. This matches the ATX guidance (per `atx-assessment.md`): *"if a task could be solved with static rules, RPA, or a simple script — do not build an agent."* The LLM is the smallest moving part; engineering effort lives in the deterministic plumbing (schema validation, CRM client, idempotency, monitoring). See APD activity catalog **Imp.** column for per-task taxonomy.

---

## What the agent must never do (hard constraints)

- Apply a credit without `APPROVER_ID + AUDIT_REF` in the packet
- Send customer comms without human confirmation in Wave 1
- Proceed past Aurum read on schema-validation failure
- Auto-close a dispute with open customer comms < 72h old
- Modify an Aurum invoice (only credit application, never invoice edit; UI-write blocked Wave 1)
- Cross-map `dispute_type` to a remedy outside the schema-defined candidate set
- Process the same `processing_id` twice without idempotency check
- Make tight ETA predictions (out of scope; ML project)
- Enter the dispatcher's real-time decision loop in WS1 / WS3
- Apply pattern-matched routine remedy without confidence ≥ provisional 0.8 threshold (calibrate in mock testing)

---

## Open gaps that affect design

> **G-N** identifiers are referenced from DSM / APD / Discovery / V×V — this table is the canonical glossary.

| G-N | Gap | Affects | Status |
|---|---|---|---|
| G-1 | 2024 chatbot specific failure mode | Wave 1 customer-comms design (4.11) | P0 — Sarah Q1 |
| G-2 | RPA-2 failure detail (which Aurum file, what change, detection) | Schema validation focus areas | P1 — Sarah Q (engineering) |
| G-3 | Damaged-consignment actual decision criteria (SOP §4.3 = TBD) | DECA Wave 3 viability | P0 — Sarah Q2 |
| G-4 | Sandra-pattern frequency + supervisor awareness | Governance KPI weighting | P0 — Sarah Q3 |
| G-5 | 35-headcount split (CO agents / dispatchers / AMs / supervisors) | TCO baseline | P0 — Sarah Q4 |
| G-6 | CEO success metric vs £1.2M anchor + failure threshold | Success criteria | P0 — Sarah Q5 |
| G-7 | Cross-stream RACI (exception → dispute owner) | Wave 3 DECA scope | P0 — Sarah Q6 |
| G-8 | FUEL_RECALC eligibility criteria (A-6) | Remedy candidate set for FUEL_SURCH_DAMAGE | P1 — Sarah Q15 |
| G-9 | Disputes file timestamp semantics (A-7) | Polling source choice | P1 — discovery + test |
| G-9b | Dispute system identification (CRM cases? custom object? dedicated app?) | BDRA Wave 1 launch (intake source) | P0 — discovery + engineering |
| G-10 | Driver App API surface | Wave 3 DECA-light source choice | P1 (Wave 3) — engineering |
| G-11 | Dispatch console "limited API" actual scope | C1A/C3A agent role; Wave 3 DECA-light | P1 — engineering (P0 if Wave 3 sequenced earlier) |
| G-12 | Aurum credits-UI service-account auth | Wave 2 entire scope (C4C); also affects Wave 1 routing | P0 (Wave 2) — engineering Q8 |
| (no G) | Aurum CSV access path + service account scope | Wave 1 launch | P0 — engineering + Aurum support |
| (no G) | Schema validation contract per Aurum file (7 files) | Wave 1 launch | P0 — engineering |
| (no G) | AM coverage map + A-5 fallback rule | Authority routing at 4.7 | P0 — Sarah Q7 |
| (no G) | CO authority threshold (£) for self-prepared packets | Routing split at 4.7 | P0 — Sarah Q14 |
| (no G) | Confidence thresholds (provisional 0.8 routine gate) | Wave 1 calibration | P1 — mock testing |
| (no G) | Customer comms tone style guide | Few-shot examples for prompt | P1 — CO supervisor sit-down |
| (no G) | Chase cadence (T+7/14/30 provisional) | C4E behaviour | P1 — Sarah Q13 |

---

## What not to fabricate

- AM authorities/customer routing beyond what APEX_CREDITS shows (CR-813 to CR-816 only; broader tier rules are a discovery gap)
- £-thresholds for CO authority — none stated; pure stakeholder input
- Aurum schema for files not shown (only 7 sampled in artefact 5; real Aurum has more)
- 2024 chatbot specifics beyond "customer-facing" and "pulled" (everything else is invented)
- RPA-2 failure mechanism beyond "schema change" (specific file, change type, detection mechanism all unstated)
- Pattern frequency for Sandra-class overrides (one observed case; cannot generalise)
- Customer comms tone (no sample provided)
- Token cost / cost-per-case precision beyond order-of-magnitude (estimates in V×V are explicit)
- ETA window customer satisfaction data
- Dispatcher discretion criteria beyond what artefact 1 narrative shows (extent / receiving party / route pressure)
- Apex-internal naming (no system-of-record names invented; "dispute system" stays generic pending G-9b)

