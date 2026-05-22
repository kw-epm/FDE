# Gate 2 Submission — Apex Distribution Ltd

**Submitter:** Krzysztof Wilniewczyc
**Date:** 2026-05-06

## TL;DR

- **Primary agent:** **BDRA — Billing Dispute Resolution Assistant** (WS4 Billing Disputes, Wave 1, internal-facing)
- **Why:** largest contiguous Agent-led cluster surface; the audit-bypass fix becomes a feature; reads Aurum data but doesn't depend on Aurum's stability for writes (so the 2024 RPA failure pattern can't recur)
- **Scope:** ~35% of WS4 effort absorbed ≈ 2,700 hr/yr. **Scenario A** (HITL within current CO capacity): £30–67K saving. **Scenario B** (HITL adds 10–15% review overhead): £25–60K saving. Build £20–40K; median payback ~9 months in either scenario; worst-case-compounded ~20 months.
- **Roadmap:** Wave 2 = Aurum UI auto-write (G-12 gated); Wave 3 = cross-stream damage→billing watch (G-11 gated, *upstream prevention* — likely the highest-impact wave)
- **What's NOT here:** WS2 ETA (rules/RPA + ML, not agent value); WS3 driver coordination (relational, Human Only); WS1 dispatcher decision (Human Only in Wave 1 — see DSM C1A)
- **Honest implementation:** "Fully agentic" delegation does NOT mean "uses an LLM". 12 of 16 BDRA tasks are deterministic code (script/rule/API/RPA); only 2 pure LLM + 2 hybrid use the LLM. See APD activity catalog **Imp.** column.
- **Biggest risk to validate:** Sandra-class audit-bypass frequency (Discovery Q3). If widespread, Wave 1 ROI reframes around governance, not just hours.

**Reading order:** Deliverables 1–7 below per pack §5. Companion working artefact `00_elicitation_log.md` (cross-artefact evidence register, role decode, AM coverage map) is referenced from each deliverable but is NOT a Gate 2 deliverable — included alongside for audit traceability.

**File ↔ deliverable mapping:**
- `01_cognitive_load_map.md` → Deliverable #1
- `02_delegation_suitability_matrix.md` → Deliverable #2
- `03_volume_value_analysis.md` → Deliverable #3
- `04_agent_purpose_document.md` → Deliverable #4
- `05_system_data_inventory.md` → Deliverable #5
- `06_discovery_questions.md` → Deliverable #6
- `CLAUDE.md` → Deliverable #7
- `00_elicitation_log.md` → Supplementary working artefact (not a deliverable)

**Sources:** Gate 2 Participant Pack (brief + artefacts 1–4) + Gate 2 Artefacts folder (Aurum CSV samples for artefact 5).

---

# 1. Cognitive Load Map

**Gate 2 — Apex Distribution Ltd**
**Source:** Brief + 5 artefacts + 7 CSVs (paths in `00_elicitation_log.md` Source Index)

> Lived process narrative grounded in artefacts; dimension scores `[Derived]` from artefact + CSV evidence. Tags: `[Stated]` / `[Inferred]` / `[Derived]`.
>
> **Code legend (used throughout):** `WS1–4` = work streams (per brief §3); `BP1.A`/`BP-X1` = breakpoints defined below; `A-N` / `B-N` / `C-N` = cross-artefact evidence register (canonical: `00_elicitation_log.md`); `G-N` = open gaps (canonical: `CLAUDE.md` §Open gaps).

## Dimension scoring key (8-dim CLM set)

H = high delegation suitability / L = low.

| Dimension | H | L |
|---|---|---|
| **Cognitive Load** | Routine | Tacit knowledge / heavy reasoning |
| **Input Structure** | Structured | Unstructured / ambiguous |
| **Determinism** | Clear rules | Judgment-dependent |
| **Exception Rate** | Rare | Frequent |
| **Turn-Taking** | Minimal | Heavy multi-party |
| **Latency** | Async/batch | Real-time |
| **Risk** | Reversible / low | Irreversible / high |
| **Tool/API** | Available | Inaccessible / manual |

## Lived process narrative

Documented (SOP v2.3, Oct 2023 — see artefact 4): four streams handled per documented procedures via DispatchHub tablet (refusals §4.2), insurance-protocol-pending procedure (damaged §4.3), see-section-7 (unattended §4.4).

Lived (artefact-grounded):
1. **DispatchHub retired Oct 2024**, replaced by Driver App. SOP not updated. (`A-1`)
2. **§4.3 damaged-consignment is `[TBD]`** — no procedure exists. Driver phones dispatch; dispatch decides on the call. (`A-2`, artefact 1)
3. **Customer Ops bypasses APPROVER_ID** when applying credits — structural authority/work mismatch (CO has no APPROVER_ID role; only AMs do). (`A-4`, artefact 2)
4. **Disputes accumulate on `AWAITING_CUST` for extended periods** — no proactive chase logic; observed: D-337 7+ days untouched. (`B-3`)
5. **Aurum invoice modifications go via 48hr support ticket** OR **CO uses Aurum's UI directly** (faster path); the "no API" constraint is *programmatic*, not human-UI. (`B-1`)
6. **Cross-stream value chain**: damaged delivery (Mark/Cobham) → days-later billing dispute (Pete H./Hayes) → goodwill credit. Single cognitive thread spread across two streams + 9 days. (artefact 1 + artefact 2 + `C-1`)

---

## Work Stream 1 — Delivery Exceptions

**Volume:** 180/day | **Time:** 12 min/case | **Effort:** 36 hr/day (31% of tracked) `[Stated; Derived]`

**JtD:** Resolve a driver-reported delivery problem (refusal, damage, missed window, locked premises) in real-time, balancing customer SLA, route schedule, depot capacity, and vehicle utilisation.

### Micro-task table

| # | Micro-task | Type | Cog Load | Input | Det | Exc | Turn | Lat | Risk | Tool |
|---|---|---|---|---|---|---|---|---|---|---|
| 1.1 | Receive driver call/voicemail | Retrieval | H | L | H | H | M | L | M | M |
| 1.2 | Elicit narrative (extent of damage, customer reaction, route state) | Reasoning | M | L | M | M | L | L | M | L |
| 1.3 | Look up customer record + SLA tier + route impact | Retrieval | H | M | H | H | H | M | M | M |
| 1.4 | Apply judgment: return-to-depot / hold / re-attempt / PoD-with-photo / abandon | Decision | L | L | L | L | M | L | L | L |
| 1.5 | Communicate decision to driver | Action | H | M | H | H | L | L | M | M |
| 1.6 | Log decision (CRM + dispatch console) | Generation | H | M | H | H | H | M | H | M |
| 1.7 | Flag downstream billing follow-up if damage/dispute risk | Generation | M | M | M | M | H | M | M | L |

`[Derived: scores from artefact 1 narrative + brief tooling sketch + A-2/B-1 evidence]`

### Cognitive zones

| Zone | Tasks | Character |
|---|---|---|
| **Z1 INTAKE** | 1.1, 1.2 | Voice channel; unstructured driver narrative; Turn-Taking L (driver waits) |
| **Z2 CONTEXT** | 1.3 | Cross-system (CRM + dispatch console); the dispatcher is doing manual lookups under time pressure |
| **Z3 DECISION** | 1.4 | **Primary cognitive hotspot.** No SOP (§4.3 = TBD). Discretion under partial information. |
| **Z4 ACTION + LOG** | 1.5, 1.6 | Mechanical once decision made |
| **Z5 HANDOFF** | 1.7 | Cross-stream — and frequently dropped (see C-1, B-3) |

### Breakpoints

| BP | Trigger | Current path | Gap |
|---|---|---|---|
| **BP1.A** Driver → Dispatcher | Driver hits exception | Phone/voicemail | Voicemail = no synchronous handover; driver parks waiting (artefact 1: "I'm parked up till you tell me") |
| **BP1.B** Dispatcher → CRM/Console | Decision made | Manual entry | Two-system update; partial logging is observed (Z5 dropouts) |
| **BP1.C** Decision → Billing follow-up | Damage / dispute risk | Implicit / verbal | **Cross-stream handoff is the hotspot** — when missed, becomes a billing dispute days later (C-1) |

---

## Work Stream 2 — ETA Inquiries

**Volume:** 400/day | **Time:** 4 min/case | **Effort:** 26.7 hr/day (23%) `[Stated; Derived]`

**JtD:** Tell a customer where their delivery is and when to expect it.

### Micro-task table

| # | Micro-task | Type | Cog Load | Input | Det | Exc | Turn | Lat | Risk | Tool |
|---|---|---|---|---|---|---|---|---|---|---|
| 2.1 | Receive inquiry (phone / SMS / web / email) | Retrieval | H | M | H | H | M | L | H | M |
| 2.2 | Look up shipment + route + last GPS ping | Retrieval | H | H | H | H | H | M | H | H |
| 2.3 | Return scheduled window | Generation | H | H | H | H | M | M | H | H |
| 2.4 | If customer asks tighter: pull dispatcher for context | Coordination | M | L | L | M | L | L | M | L |
| 2.5 | Return best-guess narrower window OR "we don't know" | Generation | M | L | L | M | M | L | M | L |

`[Derived: scores from artefact 3 SMS evidence]`

### Cognitive zones

| Zone | Tasks | Character |
|---|---|---|
| **Z1 LOOKUP** | 2.1–2.3 | Mechanical, structured; rules/RPA candidate |
| **Z2 PREDICTION** | 2.4–2.5 | **Hotspot.** Tight ETA = ML problem (drops × dwell × traffic), not LLM. Pulls dispatcher attention from WS1/WS3. |

### Breakpoints

| BP | Trigger | Current path | Gap |
|---|---|---|---|
| **BP2.A** Lookup → Prediction | Customer rejects 4-hour window | Agent pings dispatcher | Dispatcher attention is a shared scarce resource pulled from WS1/WS3 |
| **BP2.B** Best-guess → Customer | Dispatcher gives narrower estimate | Agent passes verbatim | No accountability if narrower estimate misses |

---

## Work Stream 3 — Dispatch Adjustments

**Volume:** 90/day | **Time:** 18 min/case | **Effort:** 27 hr/day (23%) `[Stated; Derived]`

**JtD:** Modify a route mid-execution (additional pickup, diversion, driver swap) under tight time pressure.

> No artefact for this stream. Decomposition is `[Inferred]` from brief description; **confidence Medium (not Low)** because the brief gives stable constraints — volume, time-per-case, "tight time pressure", "additional pickups / diversions / driver swaps" — which are sufficient to scaffold micro-tasks without artefact validation. WS3 micro-task scoring carries this confidence ceiling.

### Micro-task table

| # | Micro-task | Type | Cog Load | Input | Det | Exc | Turn | Lat | Risk | Tool |
|---|---|---|---|---|---|---|---|---|---|---|
| 3.1 | Receive change request (customer / sales / ops) | Retrieval | H | M | H | M | L | L | M | M |
| 3.2 | Assess feasibility against current route state | Reasoning | M | M | M | L | L | L | L | L |
| 3.3 | Consult driver via Driver App / phone | Coordination | M | L | L | L | L | L | M | L |
| 3.4 | Update route plan (dispatch console) | Action | M | M | M | M | M | L | M | L |
| 3.5 | Notify all affected parties (driver, customer, depot) | Generation | H | M | H | M | L | L | M | M |

### Cognitive zones

| Zone | Tasks | Character |
|---|---|---|
| **Z1 INTAKE** | 3.1 | Multi-source change request; semi-structured |
| **Z2 FEASIBILITY** | 3.2 | Rule-checkable against route state if dispatch console exposes it |
| **Z3 NEGOTIATION** | 3.3 | **Hotspot.** Driver consult — relational, voice, real-time |
| **Z4 EXECUTION** | 3.4 | Route plan write; mechanical once decided |
| **Z5 NOTIFICATION** | 3.5 | Multi-party comms cascade (driver, customer, depot) |

### Breakpoints

| BP | Trigger | Current path | Gap |
|---|---|---|---|
| **BP3.A** Route consult | Mid-route change proposed | Phone call to driver | Sync with driver = real-time interruption; high turn-taking |
| **BP3.B** Feasibility uncertain | Route data ambiguous | Manual lookup across console + Driver App | Tool fragmentation; dispatcher juggles screens |
| **BP3.C** Notification cascade | Change confirmed | Sequential outbound (driver → customer → depot) | No atomic notification; partial-state visibility risk |

---

## Work Stream 4 — Billing Disputes

**Volume:** 60/day | **Time:** 28 min/case (handling) **but** elapsed = days–weeks per case | **Effort:** 28 hr/day handling (24%) `[Stated; Derived; B-2 — elapsed >> handling]`

**JtD:** Resolve a customer's disputed charge (fuel surcharge / redelivery / dim weight) by investigating root cause, deciding remedy, applying credit if warranted, and closing with proper audit trail.

### Micro-task table

| # | Micro-task | Type | Cog Load | Input | Det | Exc | Turn | Lat | Risk | Tool |
|---|---|---|---|---|---|---|---|---|---|---|
| 4.1 | Receive dispute (email / phone / billing forward) | Retrieval | H | M | H | H | M | H | H | M |
| 4.2 | Read invoice context: line items, fuel surcharge calc, route, customer history | Retrieval | M | M | H | M | H | H | H | M |
| 4.3 | Cross-reference upstream cause (delivery exception? known dim-weight dispute?) | Reasoning | L | L | L | L | M | H | H | L |
| 4.4 | Decide remedy: full credit / partial goodwill / FUEL_RECALC / reject | Decision | L | L | L | L | M | H | L | L |
| 4.5 | Route for approval if amount > authority (account manager) | Coordination | M | M | M | M | L | M | M | M |
| 4.6 | Apply credit via Aurum UI (with APPROVER_ID + AUDIT_REF) **or** open 48hr Aurum ticket for invoice modification | Action | M | M | M | M | L | M | M | L |
| 4.7 | Communicate to customer + close dispute in tracking system | Generation | H | M | H | H | M | M | M | M |

`[Derived: scores from artefact 2 email thread + APEX_CREDITS schema + A-4/A-6/B-1 evidence]`

### Cognitive zones

| Zone | Tasks | Character |
|---|---|---|
| **Z1 INTAKE** | 4.1 | Multi-channel; unstructured but extractable |
| **Z2 CONTEXT** | 4.2, 4.3 | **Primary cognitive hotspot.** Cross-source synthesis (CRM + Aurum CSVs + delivery history). High context-reload cost between touch-points (B-2). |
| **Z3 DECISION** | 4.4 | Remedy choice + amount; codifiable for repeat patterns (Hayes FUEL_SURCH_DAMAGE template, C-1) |
| **Z4 GOVERNANCE** | 4.5 | Authority routing — currently bypassed (A-4) |
| **Z5 ACTION** | 4.6 | Aurum UI keystrokes OR 48hr ticket — agent cannot bypass (B-1) |
| **Z6 CLOSE** | 4.7 | Customer comms + closure with audit trail filled in |

### Breakpoints

| BP | Trigger | Current path | Gap |
|---|---|---|---|
| **BP4.A** Intake → Investigation | Dispute lands | CO agent picks up | No SLA on agent pickup; multi-day stalls observed (B-3) |
| **BP4.B** Decision → Action | Remedy chosen | CO agent applies via Aurum UI | **Bypass risk: APPROVER_ID + AUDIT_REF dropped (A-4)** |
| **BP4.C** Action → Close | Credit applied | CO agent updates dispute record | **System state lags reality (A-3)** — disputes left open after resolution |
| **BP4.D** AWAITING_CUST → ? | Customer doesn't respond | Stalls until manual notice (observed: D-337 7+ days untouched) | No chase logic (B-3) |

---

## Cross-stream cognitive topology

### Shared zones

| Zone | Streams | Nature |
|---|---|---|
| **DISPATCHER ATTENTION** | WS1 (1.4 decision), WS2 (2.4 pull), WS3 (3.2–3.4 coordination) | Single scarce resource; pulled across three streams without queueing |
| **AURUM UI CREDIT WRITE** | WS4 (4.6); cross-relevant for any agent that compensates customers | Authority/work mismatch (A-4); UI-only path (B-1) |
| **CRM CUSTOMER RECORD** | All four | Salesforce; modern REST; the only consistently-reachable system |

### Cross-stream value chain (the big one)

```
WS1 (delivery exception, damaged) → BP1.C dropped handoff
                ↓
        days-later customer complaint
                ↓
WS4 (billing dispute, FUEL_SURCH_DAMAGE)
                ↓
WS4 4.6 goodwill credit (often without APPROVER_ID — A-4)
                ↓
APEX_DISPUTES_OPEN may lag closure (A-3)
                ↓
APEX_AGED_RECEIVABLES carries the open value (e.g. Hayes £8,420 in 0–30 bucket — C-1)
```

Three of the six open disputes (50%) follow this chain: D-342, D-318, D-328 are FUEL_SURCH_DAMAGE — i.e. damaged delivery → fuel-surcharge disputed.

### Cross-stream breakpoints

| BP | Streams | Description |
|---|---|---|
| **BP-X1** Exception → Dispute | WS1 → WS4 | Damaged delivery becomes a dispute days later; original context lost; agent reconstructs from scratch |
| **BP-X2** ETA pull | WS2 → WS1/WS3 | "Checking with dispatch" pulls dispatcher off whatever they're doing |
| **BP-X3** Adjustment cascade | WS3 → WS2 | Mid-route changes invalidate ETAs; downstream ETA inquiries spike |

---

## Cognitive hotspot summary

| Hotspot | Stream | Why it matters |
|---|---|---|
| **Cross-stream exception → dispute handoff (BP-X1)** | WS1→WS4 | Largest lived-vs-documented gap. 50% of open disputes follow this chain. Where the agent matters most. |
| **Aurum UI credit write (4.6)** | WS4 | Only governance-bypass mechanism in the lived process. Agent that enforces APPROVER_ID = governance upgrade. |
| **Dispatcher attention as shared resource** | WS1/2/3 | The dispatcher is the bottleneck. Any agent that reduces dispatcher pull (e.g. context pre-staging for WS1) compounds across WS2/WS3. |
| **WS4 Z2 cross-source synthesis (4.2–4.3)** | WS4 | Highest cognitive load on the highest-unit-value stream. Direct agent target. |
| **WS1 Z3 dispatcher discretion (1.4)** | WS1 | No SOP; pure judgment. Agent supports (context pre-stage), does not decide. |
| **Disputes stall on AWAITING_CUST (BP4.D)** | WS4 | Chase-logic gap. Easy agent win. |

---

# 2. Delegation Suitability Matrix

**Gate 2 — Apex Distribution Ltd**
**Source:** CLM (`01_cognitive_load_map.md`); brief + artefacts + CSVs

> Provisional archetypes. Each row carries explicit basis + open dependency that would change it.
>
> **Code legend:** `C1A`–`C4E` = task clusters defined below; `WS1–4` = work streams; `A-N` = cross-artefact evidence (canonical: `00_elicitation_log.md`); `G-N` = open gaps (canonical: `CLAUDE.md` §Open gaps).

## Suitability scoring key (7-dim DSM set; differs from CLM 8-dim — drops Cognitive Load + Turn-Taking, adds Context Complexity)

| Dim | H | L |
|---|---|---|
| Input Structure | Structured | Unstructured / ambiguous |
| Decision Determinism | Clear rules | Judgment-dependent |
| Tool Coverage | APIs available | Inaccessible / manual |
| Context Complexity | State explicit | Tacit / institutional knowledge |
| Exception Rate | Rare | Frequent |
| Latency | Async/batch | Real-time |
| Risk/Compliance | Reversible / low | Irreversible / regulated |

**Archetypes:** Fully Agentic / Agent-led + Human Oversight / Human-led + Agent Support / Human Only.

> **Latency varies by stream** (WS1/WS3 real-time, WS2 near-real-time, WS4 async) — scored per cluster.

---

## Task clusters (re-grouped from CLM micro-tasks)

| Cluster | CLM tasks | Description |
|---|---|---|
| **C1A** | WS1 1.1–1.4 | Delivery exception intake + dispatcher decision |
| **C1B** | WS1 1.5–1.6 | Decision execution + log |
| **C1C** | WS1 1.7 | Cross-stream handoff to billing (BP-X1 inverse: pre-emptive) |
| **C2A** | WS2 2.1–2.3 | ETA lookup |
| **C2B** | WS2 2.4–2.5 | Tight-window prediction |
| **C3A** | WS3 3.1–3.2 | Adjustment intake + feasibility |
| **C3B** | WS3 3.3–3.5 | Driver coordination + execute + notify |
| **C4A** | WS4 4.1–4.3 | Dispute intake + cross-source context assembly |
| **C4B** | WS4 4.4–4.5 | Remedy decision + authority routing |
| **C4C** | WS4 4.6 | Aurum UI credit write |
| **C4D** | WS4 4.7 | Close + customer comms |
| **C4E** | WS4 BP4.D | AWAITING_CUST chase logic |

---

## C1A — Delivery exception intake + dispatcher decision

| Dim | Score | Basis |
|---|---|---|
| Input | L | Voice narrative (artefact 1); unstructured |
| Determinism | L | No SOP for damages (A-2); discretion under partial info |
| Tool | L | Driver App API surface unconfirmed (G-10); dispatch console "limited API" (G-11) |
| Context | L | Driver-side reality (damage extent, site response) requires human eye |
| Exception | L | Frequent; each case unique |
| Latency | L | Real-time — driver parked waiting (artefact 1) |
| Risk | M | Wrong call = customer dispute downstream; reversible but costly |

**Profile:** L,L,L,L,L,L,M. **Archetype: Human Only in Wave 1; promotable to Human-led + Agent Support in Wave 3 (when G-10 / G-11 resolve).**
**Rationale:** Decision stays with dispatcher always. The agent's potential role is parallel context retrieval (CRM customer record + SLA tier + route state) so the dispatcher's call is informed, not faster — but Wave 1 has only CRM access (Driver App / dispatch console APIs gated by G-10 / G-11). Without route-state read, the agent cannot pre-stage in real-time, so Wave 1 is functionally Human Only on this cluster. Promote when API surfaces resolve.
**Open dependency:** G-10 + G-11 (both must resolve before promotion).

## C1B — Decision execution + log

| Dim | Score | Basis |
|---|---|---|
| Input | M | Decision output is a small enum + free-text reason |
| Determinism | H | Once decided, log writes are mechanical |
| Tool | L | Two systems (CRM + console); console limited API |
| Context | H | State is explicit at this point |
| Exception | H | Mechanical |
| Latency | M | Near-real-time |
| Risk | M | Partial logging is a known gap (Z5 dropouts, CLM) |

**Profile:** M,H,L,H,H,M,M. **Archetype: Agent-led + Human Oversight.**
**Rationale:** Agent enforces structured log schema (decision + reason + downstream-flag boolean). Oversight = sample audit.
**Open dependency:** Dispatch console API write capability (G-11).

## C1C — Cross-stream handoff to billing

| Dim | Score | Basis |
|---|---|---|
| Input | M | Damage flag + customer + invoice context |
| Determinism | M | Rule: damage → 72hr billing-watch entry |
| Tool | M | CRM REST + dispute system (TBD what system, G-9b) |
| Context | M | Cross-stream — needs upstream + downstream context |
| Exception | H | Once rule defined, mechanical |
| Latency | H | Async — handoff can be batched |
| Risk | M | Missed handoff = future dispute emerges blind (today's reality, BP1.C) |

**Profile:** M,M,M,M,H,H,M. **Archetype: Agent-led + Human Oversight.**
**Rationale:** **High-impact cluster.** Today this handoff fails (BP1.C → BP-X1 → 50% of open disputes are FUEL_SURCH_DAMAGE downstream of damaged deliveries). An agent that creates a "billing-watch" record on every damage flag closes the cross-stream loop.
**Open dependency:** What system stores disputes (CRM cases? dedicated disputes app? G-9b).

## C2A — ETA lookup

| Dim | Score | Basis |
|---|---|---|
| Input | H | Structured tracking ID |
| Determinism | H | Lookup → window |
| Tool | M | CRM REST; Driver App GPS via implicit API |
| Context | H | State explicit |
| Exception | H | Routine |
| Latency | L | Customer-facing real-time |
| Risk | H | Read-only — no real-world consequence |

**Profile:** H,H,M,H,H,L,H. **Archetype: Disqualified — rules/RPA territory, not agent value.**
**Rationale:** Disqualification driver is **deterministic lookup** (Determinism H + Input H), not latency. Lookup-then-respond is fully rule-expressible, so an agent (probabilistic) adds no value over a rules engine — only latency + token cost. (Latency L is a separate constraint any solution must meet — agent or rules.) **Recommend ETA lookup automation as a separate non-agent rules/RPA project.**
**Open dependency:** None — correctly classified as not an agent target.

## C2B — Tight-window prediction

| Dim | Score | Basis |
|---|---|---|
| Input | L | Last GPS ping + N pending drops + estimated dwell + traffic |
| Determinism | L | Probabilistic forecast |
| Tool | L | No route-state ML model exists at Apex (inferred from artefact 3 hedging) |
| Context | L | Domain-specific ML problem |
| Exception | M | Most cases need narrower estimate when customer asks |
| Latency | L | Real-time |
| Risk | M | Wrong estimate = customer trust damage; same customer-facing surface Sarah pulled the 2024 chatbot from (Q1) |

**Profile:** L,L,L,L,M,L,M. **Archetype: Human Only (with optional ML support — separate use case).**
**Rationale:** Tight ETA prediction is an ML problem (route-state model), not an LLM problem. Out of agent scope. Scaffolding an LLM on top of a missing ML model = chatbot rerun.
**Open dependency:** Route-state ML model is its own ~6-month project; not a Wave 1 candidate.

## C3A — Dispatch adjustment intake + feasibility

| Dim | Score | Basis |
|---|---|---|
| Input | M | Change request + current route state |
| Determinism | M | Rule-checkable feasibility (capacity, time-window) |
| Tool | L | Dispatch console limited API (G-11) |
| Context | M | Route geography + driver state |
| Exception | M | Some routine, some edge |
| Latency | L | Real-time |
| Risk | M | Wrong feasibility call = driver disruption |

**Profile:** M,M,L,M,M,L,M. **Archetype: Human-led + Agent Support.**
**Rationale:** Feasibility check is rule-checkable but tool gap (dispatch console) blocks Agent-led. Agent can pre-compute feasibility-likely from CRM/route data; human verifies.
**Open dependency:** G-11 (console API).

## C3B — Driver coordination + execute + notify

| Dim | Score | Basis |
|---|---|---|
| Input | L | Voice + relational context with driver |
| Determinism | L | Negotiation-shaped |
| Tool | L | Phone primary; Driver App messaging secondary |
| Context | L | Driver-relationship knowledge |
| Exception | L | Each case unique |
| Latency | L | Real-time |
| Risk | M | Mid-route disruption, fleet-wide ripple |

**Profile:** L,L,L,L,L,L,M. **Archetype: Human Only.**
**Rationale:** Deeply relational with drivers; voice channel; high real-time stakes. No defensible agent role.

## C4A — Dispute intake + cross-source context assembly

| Dim | Score | Basis |
|---|---|---|
| Input | M | Email/phone/forward; semi-structured |
| Determinism | M | Pattern match: dispute_type + invoice → context-set rule |
| Tool | M | Email + CRM REST + Aurum CSV reads (B-1: read path is fine) |
| Context | M | Cross-source synthesis (CRM + Aurum + delivery history) |
| Exception | M | Hayes-pattern (C-1) shows recurring templates exist |
| Latency | H | Async — multi-day acceptable |
| Risk | M | Read-only at this stage; risk emerges at decision (C4B) |

**Profile:** M,M,M,M,M,H,M. **Archetype: Agent-led + Human Oversight.**
**Rationale:** Cross-source synthesis is exactly what an LLM agent does well. Aurum CSV reads with schema-validation gate (per `00` elicitation Q2 design note) are stable enough. Context-reload cost (B-2) is the human pain agent removes.
**Open dependency:** Schema-validation contract per Aurum file (engineering).

## C4B — Remedy decision + authority routing

| Dim | Score | Basis |
|---|---|---|
| Input | M | Context dossier from C4A |
| Determinism | M | Repeating patterns codifiable (Hayes FUEL_SURCH_DAMAGE = goodwill ~50% of surcharge per artefact 2 precedent); novel cases require judgment |
| Tool | H | Decision is internal logic + routing |
| Context | M | Customer history + dispute type matrix |
| Exception | M | Routine vs novel split |
| Latency | H | Async |
| Risk | M | Wrong remedy = customer escalation OR lost margin |

**Profile:** M,M,H,M,M,H,M. **Archetype: Agent-led + Human Oversight (routine remedies); Human-led + Agent Support (novel).**
**Rationale:** Split by case profile. Routine = "dispute_type ∈ known patterns" (e.g. FUEL_SURCH_DAMAGE for Hayes-class customer = goodwill ≤ 50% of surcharge). Novel = unknown pattern, escalates with full context to human.
**Open dependency:** Threshold for "routine" definition (Discovery Q10 + Q15 + CO supervisor pattern-library seeding).

## C4C — Aurum UI credit write

| Dim | Score | Basis |
|---|---|---|
| Input | H | Decision + amount + APPROVER_ID + AUDIT_REF |
| Determinism | H | Mechanical UI keystrokes |
| Tool | L | **Aurum UI auth model unconfirmed (G-12)** — may require human keystroke; agent cannot bypass (B-1) |
| Context | H | All required fields explicit |
| Exception | M | Aurum schema-quarter-changes (Q7) |
| Latency | H | Async (UI step can be batched / queued) |
| Risk | M | Wrong credit application is reversible (Aurum support 48hr ticket) but customer-trust + audit cost moderate |

**Profile:** H,H,L,H,M,H,M. **Archetype: Human-led + Agent Support pending G-12; promotable to Agent-led if Aurum UI accepts service-account automation.**
**Rationale:** Tool gap is the only blocker. Agent prepares the credit packet (with proper APPROVER_ID assigned per AM coverage map); human applies via UI. Once G-12 is resolved as "service account works", promote.
**Open dependency:** G-12 (Aurum credits-UI auth model).

## C4D — Close + customer comms

| Dim | Score | Basis |
|---|---|---|
| Input | H | Decision outcome + customer record |
| Determinism | H | Templated comms |
| Tool | H | CRM REST + email |
| Context | H | State explicit at this point |
| Exception | H | Routine |
| Latency | H | Async |
| Risk | M | Customer-facing comms — tone matters |

**Profile:** H,H,H,H,H,H,M. **Archetype: Agent-led + Human Oversight (templated drafts) — NOT Fully Agentic.**
**Rationale:** Communications are customer-facing (Sarah wary of customer-facing — Q1). Agent drafts; CO agent confirms before send. Once trust calibrated, promotable.
**Open dependency:** First-month review cadence to validate tone before promotion.

## C4E — AWAITING_CUST chase

| Dim | Score | Basis |
|---|---|---|
| Input | H | Dispute record + days-since-last-update |
| Determinism | H | Rule: T+7 = nudge, T+14 = escalate, T+30 = auto-close |
| Tool | H | CRM REST + email |
| Context | H | Explicit |
| Exception | H | Routine |
| Latency | H | Daily batch |
| Risk | M | Reversible (customer can re-open) but cadence error = customer annoyance / brand impact |

**Profile:** H,H,H,H,H,H,M. **Archetype: Agent-led + Human Oversight.**
**Rationale:** Closes B-3 gap directly. Cadence chosen by Sarah; agent enforces. Why not Fully Agentic: customer-facing comms (per C4D); auto-close should be human-confirmed at first.
**Open dependency:** SLA thresholds (Q in #06).

---

## Summary

| Cluster | Archetype | Why | Promote-when |
|---|---|---|---|
| C1A intake/decision | Human Only (Wave 1) → Human-led + AS (Wave 3) | Discretion + Wave 1 tool gap | G-10 + G-11 |
| C1B execution/log | Agent-led + Oversight | Mechanical post-decision | — |
| **C1C cross-stream handoff** | **Agent-led + Oversight** | **Closes BP-X1 — 50% of disputes** | — |
| C2A ETA lookup | Disqualified — rules/RPA territory | Deterministic lookup; LLM adds latency + cost without value | n/a — not an agent target |
| C2B tight prediction | Human Only | Out of LLM scope | Separate ML project |
| C3A adjustment intake | Human-led + Agent Support | Tool gap | G-11 |
| C3B driver coord | Human Only | Relational | — |
| **C4A intake + context** | **Agent-led + Oversight** | **BDRA core** | — |
| **C4B remedy decision** | **Agent-led (routine) / Human-led (novel)** | **Split by pattern** | Threshold tuning |
| C4C Aurum UI write | Human-led + Agent Support | G-12 | G-12 resolution |
| C4D close + comms | Agent-led + Oversight | Customer-facing — Sarah's caution from 2024 chatbot | First-month review |
| C4E chase | Agent-led + Oversight | Closes B-3 gap | — |

---

## Notes on the matrix distribution

The 12 clusters split as: Fully Agentic 0 / Agent-led + Oversight 6 / Human-led + AS 3 / Human Only 2 / disqualified 1. Each archetype assignment is grounded in a positive evidence basis above — tool gaps (G-10 / G-11 / G-12), structural authority gaps (A-4), no codifiable rule (C1A / C2B), relational + voice channel (C3B), customer-facing surface Sarah won't go near after the 2024 chatbot (C4D / C4E), or not agent value at all (C2A — rules/RPA). C4B is split routine-vs-novel because the same dispute_type has a codifiable subset and a judgment-bound remainder.

---

# 3. Volume × Value Analysis

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

---

# 4. Agent Purpose Document

**Gate 2 — Apex Distribution Ltd**
**Source:** DSM (`02`), V×V (`03`); CLM (`01`); Source Index in `00`

> Design choices that depend on data not in brief are tagged `[Unconfirmed: requires X]` — these are deployment blockers, not assumptions.
>
> **Code legend:** `4.1`–`4.13Q` = activity-catalog tasks defined below; `C4A`–`C4E` = DSM task clusters; `WS1–4` = work streams; `A-N` / `B-N` / `C-N` = cross-artefact evidence (canonical: `00_elicitation_log.md`); `G-N` = open gaps (canonical: `CLAUDE.md` §Open gaps); `BP-X1` = cross-stream breakpoint (canonical: CLM).

## Agent selection

V×V committed **WS4 BDRA** as Wave 1. Largest contiguous Agent-led cluster surface; internal-facing (so no rerun of the 2024 chatbot); the audit-bypass fix becomes a feature; reads Aurum data but doesn't depend on Aurum's stability for writes. Wave 2 = C4C (Aurum auto-write, blocked on G-12). Wave 3 = C1C cross-stream handoff (blocked on G-11).

**Honest scope note:** Wave 1 BDRA does NOT touch dispatcher work in WS1. C1A (where dispatcher discretion lives) is **Human Only in Wave 1 per DSM**, becoming Human-led + AS only in Wave 3 when both Driver App (G-10) and dispatch console (G-11) APIs resolve and the agent can pre-stage context in real-time. So WS1 capacity is unchanged in Wave 1. WS1 enhancement waits for Wave 3.

---

## Agent 1 — Billing Dispute Resolution Assistant (BDRA)

### Purpose document

```
Agent Name: BDRA — Billing Dispute Resolution Assistant
Job to be Done: Investigate the root cause of a customer billing dispute,
                decide the remedy within authority bounds, prepare a credit
                packet with proper APPROVER_ID + AUDIT_REF, draft
                customer-closing comms, and chase stalled disputes on cadence.

Business context: WS4 — 60 disputes/day, 28 min handling/case, 28 hr/day
                  CO effort. Highest unit-value stream; sits downstream of
                  WS1 damages on the cross-stream value chain
                  (see CLM §Cross-stream value chain + register C-1 for
                  the 50%-of-disputes evidence).

Primary objectives:
  1. Eliminate the audit-bypass pattern (A-4) by emitting APPROVER_ID +
     AUDIT_REF on 100% of agent-prepared credits.
  2. Absorb routine disputes end-to-end; escalate novel patterns with
     full context for human decision.
  3. Close the chase-logic gap (B-3): no dispute stalls untouched
     beyond the cadence threshold on AWAITING_CUST.

KPIs (paired so they cannot conflict):
  - Audit completeness:  100% of agent-emitted credits carry APPROVER_ID +
                         AUDIT_REF (vs current bypass)
  - Packet acceptance:   ≥95% of agent-prepared packets accepted by
                         CO/AM without material modification
  - Routine coverage:    ≥60% of WS4 cases handled agent-led (routine
                         pattern); ≥35% total effort absorbed
                         (NOT 1:1 — routine cases keep C4C human-keystroke
                         step in Wave 1; "absorbed" is per-case-time-saved,
                         not per-case-count)
                         [Estimated — sensitivity ±10pp, see V×V §3]
  - Chase coverage:      100% of disputes ≥7d on AWAITING_CUST receive
                         a nudge per cadence (cadence set by stakeholder)
  - Cost per case:       <£0.10 (token + tool + infra)
                         [Estimated — see V×V §3 token assumptions]

Delegation archetype: Agent-led + Human Oversight (routine);
                      Human-led + Agent Support (novel patterns, C4C write).

Hard constraints (non-negotiable):
  - Never apply a credit without APPROVER_ID + AUDIT_REF in the packet
  - Never send customer comms without human confirmation in Wave 1
  - Never proceed past Aurum read on schema-validation failure (halt + alert)
  - Never auto-close a dispute with open customer comms <72h old
  - Never modify an Aurum invoice (UI write blocked Wave 1; ticket route
    only via human; service-account write conditional on G-12)

Escalation triggers (must match Autonomy Matrix exactly):
  - Novel pattern (no codified remedy template match)
       → CO agent queue with full dossier
  - Aurum schema-validation failure on any required file read
       → Halt + alert ops + flag dispute as "agent unavailable"
  - Dispute touches active delivery exception (cross-stream WS1)
       → Human pickup with cross-stream context surfaced
  - Customer escalates via channel other than reply (phone, manager-cc)
       → CO agent picks up; agent presents context dossier read-only
  - Confidence below threshold (provisional 0.8) on remedy classification
       → CO agent queue [calibrate in mock testing]

Authority routing (NOT escalation — routine):
  - Amount > CO authority threshold [Unconfirmed: threshold pending Sarah Q14]
       → AM (per AM coverage map) receives prepared packet for UI entry
```

### Activity catalog

> **Sequence note:** The agent intake-polls disputes from CRM (or dedicated dispute system, pending G-9b). Aurum CSV reads are *enrichment*, not the source-of-truth for dispute existence — that lives in the operational system.

> **Honest implementation note (per pack §8 anti-pattern check):** "Fully agentic" delegation does NOT mean "uses an LLM." Most BDRA tasks below are deterministic code (script / rule / API call / RPA) wrapped inside the agent's autonomous flow. Only the **Imp.** column flagged **LLM** uses the LLM; everything else is conventional IT (cheaper, faster, debuggable). This matches the ATX guidance: *"if a task could be solved with static rules, RPA, or a simple script — do not build an agent."* The LLM is the smallest moving part; the rest is plumbing. Per-case token cost in V×V §3 reflects only the LLM operations (4.5 partial + 4.6 + 4.11), not the full catalog.
>
> **Imp. legend:** **Script** = procedural code (poll, parse, format); **Rule** = deterministic logic / lookup table; **API** = system-integration call; **RPA** = UI automation; **LLM** = true agent reasoning (probabilistic, requires tokens); **Hybrid** = combination.

| # | Task | Type | Delegation | Imp. | Data | Tool | Risk |
|---|---|---|---|---|---|---|---|
| 4.1 | Poll dispute system for new + stalled records (5-min interval) | Retrieval | Fully agentic | **Script** | Dispute records | CRM/dispute REST | Low |
| 4.2 | Extract dispute fields + assign `processing_id` (idempotency from 4.6 onward) | Retrieval | Fully agentic | **Script** | Record | None | Low |
| 4.3 | Cross-source enrichment: pull invoice (APEX_BILL_DAILY), surcharge calc (APEX_FUEL_SURCH), prior credits (APEX_CREDITS), recon status (APEX_RECON), customer master (APEX_CUSTOMER_MASTER) — all behind schema-validation gate | Retrieval | Fully agentic (schema-gated) | **Script** | Aurum CSVs | Aurum file watch + schema validator | Medium — halt on schema fail |
| 4.4 | Cross-stream check: any open WS1 delivery exception linked to invoice? (CRM case query by invoice_no) | Retrieval | Fully agentic | **API** | CRM cases | CRM REST | Low |
| 4.5 | Compose context dossier (customer + dispute + invoice + cause-evidence + prior-pattern matches) | Generation | Fully agentic | **Hybrid** (script aggregation + LLM summary) | Aggregated context | Internal | Low |
| 4.6 | Pattern-match remedy template (e.g. FUEL_SURCH_DAMAGE → goodwill ≤ 50% of surcharge per Hayes/Pete precedent; DIM_WEIGHT → re-verify before crediting per Tom J.'s caseload pattern) | Reasoning | Agent-led (routine); Human-led + AS (novel) | **LLM + Rule** (LLM proposes, rule-table validates allowed remedies) | Dossier + remedy template library | LLM + rule lookup | Medium |
| 4.6E | If novel pattern OR confidence below threshold → escalate to CO queue with full dossier; STOP at 4.6 | Escalation | Human takes over | **Rule** | Dossier | CRM queue | Low |
| 4.7 | Authority routing: if amount within CO authority → assign self as preparer + AM as APPROVER_ID per coverage map; if above → AM-only path | Decision | Agent-led | **Rule** | Amount + AM coverage map | None (rule lookup) | Medium |
| 4.8 | Generate AUDIT_REF (deterministic format: `AUD-{YYYY}-BDRA-{processing_id}-{seq}`) | Generation | Fully agentic | **Script** | processing_id | None | Low |
| 4.9 | Prepare credit packet: REASON_CODE, amount, APPROVER_ID, AUDIT_REF, justification text | Generation | Fully agentic | **Script** (template fill) | All preceding | None | Low |
| 4.9E | If C4C blocked (G-12 unresolved) → packet to AM email queue for human Aurum UI entry; STOP at 4.9 | Escalation | Human-led + AS | **Script** (email send) | Packet | Email | Low |
| **— Wave 2 only (G-12-gated) below this line —** | | | | | | | |
| 4.10 | (Wave 2 only) Apply credit via Aurum UI service account; verify in next-day APEX_CREDITS export by AUDIT_REF lookup `[Inferred — Aurum may normalise AUDIT_REF on ingest; verify shape preservation in mock testing]` | Action | Agent-led + Oversight | **RPA** (Selenium/Playwright pattern) | Packet | Aurum UI client | Medium |
| **— Wave 1 (resumed) below this line —** | | | | | | | |
| 4.11 | Draft customer-closing comms; route to CO agent for confirm-and-send (Wave 1) | Generation | Agent-led + Oversight | **LLM** (template-guided) | Outcome | CRM email composer | Medium |
| 4.12 | Update dispute record: status, resolution code, link to APEX_CREDITS row (once visible) | Action | Fully agentic | **API** | Outcome | CRM REST | Low |
| 4.13 | Chase-cadence engine: scan AWAITING_CUST disputes daily; cadence `[Provisional — Sarah Q13]` T+7 = nudge draft (human send); T+14 = escalation flag; T+30 = auto-close proposal (CO confirms) | Generation + Action | Agent-led + Oversight | **Hybrid** (rule-driven timer + LLM-drafted nudge text) | Dispute records | CRM REST | Low |
| 4.13Q | QA: tag 5% of agent-led closed disputes (uniform random) for daily CO review | Generation | Fully agentic | **Script** | Disposition | CRM tag API | Low |

**Implementation summary across the catalog (16 tasks total):**
- **Pure LLM (2 tasks):** 4.6 (remedy classification), 4.11 (customer comms drafting)
- **Hybrid LLM + deterministic (2 tasks):** 4.5 (script aggregation + LLM summary), 4.13 (rule timer + LLM nudge text)
- **Pure deterministic (12 tasks):** 4.1, 4.2, 4.3, 4.4, 4.6E, 4.7, 4.8, 4.9, 4.9E, 4.10 (RPA, Wave 2), 4.12, 4.13Q
- **Engineering cost is mostly NOT in the LLM** — it's in the deterministic plumbing (Aurum schema validation, CRM client, AM router, idempotency, monitoring). LLM is the cheap part to swap if pricing changes; per-case token cost in V×V §3 reflects only the 2 pure + 2 partial LLM operations.

**Note on 4.6:** "Routine" = dispute matches a codified pattern (customer × dispute_type × known remedy precedent). Initial pattern library seeded from APEX_DISPUTES_OPEN history + artefact 2 precedent. Library expands via 4.13Q sample review. **Novel = always escalate.** (Cross-mapping enforcement detailed in Action Mapping Table + Hard Constraints.)

**Note on 4.7:** Authority routing uses the AM coverage map (`00` actor table). **Default = "any active AM"** — matches the lived practice (A-5: 2 of 4 sampled credits had APPROVER_ID ≠ customer's specific AM, so role-based authority is in use today). Customer-specific AM is the *configurable variant* to confirm with Sarah at Q7. Alert if no AM available.

**Note on 4.8:** AUDIT_REF format is BDRA-namespaced so audit can distinguish agent-emitted credits from human-emitted (current `AUD-YYYY-NNNNN` pattern stays intact for human credits).

### Action mapping table

**Default `dispute_type → remedy candidate set` (LLM constrained at 4.6 to choose from this set; cross-mapping is a schema error):**

| dispute_type | Remedy candidate set | Notes |
|---|---|---|
| `FUEL_SURCH_DAMAGE` | `GOODWILL` (≤ 50% of surcharge), `FUEL_RECALC` (if calc error verifiable), `REJECT` | Hayes-class precedent: goodwill default. FUEL_RECALC requires evidence of calc fault (A-6: criteria pending Q-A6). |
| `DIM_WEIGHT` | `INV_CORR` (if measurement re-verified), `GOODWILL` (≤ amount), `REJECT` | Tom J. handles current load; pattern: re-verify before crediting |
| `REDELIVERY_FEE` | `GOODWILL` (≤ amount), `REJECT` (if customer cause), escalate if amount > authority | |
| `OTHER` | Always escalate to CO/AM | Novel pattern by definition |

**REASON_CODE → APEX_CREDITS column** mapping is exact (must match Aurum's existing enum: `FUEL_RECALC`, `GOODWILL`, `INV_CORR`, plus any others in the schema we haven't seen — `[Unconfirmed: full enum from Aurum schema doc — engineering discovery]`).

### Autonomy matrix

```
AGENT DECIDES AND ACTS ALONE (routine pattern, all schema gates passed):
  - Polling, intake, processing_id assignment (4.1, 4.2)
  - Aurum CSV reads (schema-gated) (4.3)
  - Cross-stream WS1 check (4.4)
  - Context dossier composition (4.5)
  - AUDIT_REF generation (4.8)
  - Credit packet preparation (4.9) — but does NOT submit to Aurum in Wave 1
  - Dispute record updates (4.12)
  - Chase-cadence draft generation (4.13 — drafts only, send is human in Wave 1)
  - QA sample tagging (4.13Q)

AGENT ACTS, HUMAN NOTIFIED AFTER (audit/sample review, no blocking):
  - Routine remedy classification (4.6 routine path)
  - Authority routing (4.7) — AM sees the assignment
  - Dispute auto-close on T+30 stale (4.13) — CO confirms via daily review
  - QA sample (4.13Q) — daily CO review of 5% sampled closures

AGENT PROPOSES, HUMAN APPROVES BEFORE ACTION:
  - Credit packet → AM/CO for Aurum UI entry (4.9E in Wave 1)
  - Customer comms drafts → CO confirms before send (4.11)
  - Chase nudges → CO confirms before send (4.13)

HUMAN TAKES OVER (agent supports with dossier):
  - Novel remedy pattern (4.6E) — agent dossier, human decides
  - Confidence below threshold (4.6E) — agent dossier, human decides
  - Cross-stream WS1-active dispute (4.4 hit) — human pickup, agent context
  - Customer escalates off-channel — human pickup, agent context
  - Aurum schema-validation failure — agent halts, ops investigates
  - Amount above CO authority + AM coverage gap (rare) — escalate to ops
```

### System and data summary

**Extracted to `05_system_data_inventory.md`** for full inventory (Wave 1 + Wave 2 + 3, credentials, shared assets, P0 pre-launch checklist).

Key Wave 1 systems: Salesforce CRM (REST, OAuth), Aurum CSV file-watch + schema validator, AM email queue (for packet handoff in Wave 1), QA tag API (CRM).
Key Wave 1 P0 blockers: Dispute system identification (G-9b), Aurum CSV access path + service account credentials, schema validation contract per file, AM coverage map config.

### Context engineering design

**Memory architecture:**

| Type | Content | Storage | Lifecycle |
|---|---|---|---|
| **In-context** | Current dispute + dossier (invoice, customer, prior credits, cross-stream check) | Prompt window | Per case; cleared after 4.12 |
| **Episodic** | Customer dispute history (last N disputes, remedies, outcomes) | CRM query (cached 1hr) | **Fetched at 4.5** (always — it's small and load-bearing) |
| **Semantic** | Remedy template library; AM coverage map; authority thresholds; Aurum schema contracts | YAML config in repo | Versioned; deploy review on change |
| **Procedural** | Decision rules, escalation triggers, AUDIT_REF format, hard constraints | System prompt | Version-controlled |

**Retrieval strategy:**
- **Aurum CSVs (4.3):** file-watch latest snapshot per file; schema-validate before read; halt on mismatch. Joins by INVOICE_NO + CUSTOMER_ID.
- **CRM (4.4 + 4.12):** REST query by invoice_no for cross-stream WS1 check; case-write on close.
- **Cost control:** dossier composition is the single highest-token operation. Token ceiling per case: 3K input + 800 output. Episodic history truncated to last 5 disputes per customer.

**Prompt principles:**
1. **Role + scope first:** "You are BDRA. You investigate billing disputes and prepare credit packet with proper APPROVER_ID + AUDIT_REFs. You do not modify Aurum invoices. You do not send customer comms without human confirmation."
2. **Hard constraints as numbered rules** (matches "Hard constraints" section above).
3. **Structured output (JSON schema enforced):**
   ```
   { processing_id, dispute_id, classification (routine|novel|cross_stream),
     remedy: { type ∈ allowed candidate set per dispute_type, amount,
               justification, confidence },
     packet: { APPROVER_ID, AUDIT_REF, REASON_CODE, customer_id, invoice_no },
     escalation_reason | null,
     audit_trail (list of decision points + sources cited) }
   ```
   Invariants: (a) `remedy.type ∈ candidate_set[dispute_type]`; (b) `escalation_reason != null` ⟺ classification ∈ {novel, cross_stream, low_confidence}; (c) packet fields populated iff classification == routine AND amount ≤ authority.
4. **Chain-of-thought** required for routine classification (the audit_trail field) — every cited source explicit.
5. **Few-shot examples:** seed with artefact 2 (Pete H. case, FUEL_SURCH_DAMAGE → £170 goodwill ≈ 50% of £340 surcharge). Replace with stakeholder-validated examples in mock testing.
6. **Token discipline:** system prompt ~2K (role + scope + 5 hard constraints + 6 prompt principles + JSON schema); per-case dossier < 3K; episodic capped at last 5; no full-history retrieval.

### Operational constraints

- **Single-instance Wave 1.** Dispute polling has no claim semantics in CRM (assumed); horizontal scaling would race. Single-writer pattern.
- **Idempotency.** `processing_id` assigned at 4.2; lookup at 4.6/4.9/4.12 via CRM custom field. Duplicate retries are no-ops.
- **Polling.** 5-min interval on dispute system; 24hr cadence on chase scan (4.13). Webhook upgrade pending CRM/dispute-system capability discovery.
- **Schema validation.** Contract per Aurum file: column count + names + order + types + value ranges where known. Hard-fail = halt agent + alert ops Slack/email; don't downgrade to warning.
- **Aurum quarterly schema risk.** Pre-launch + monthly: diff actual schema against contract; alert if drift detected before agent next reads it.

### Monitoring

- **Per-case event:** processing_id, latency (4.1→4.12), dispute_type, classification, remedy.type, remedy.amount, escalation_reason, audit-trail-completeness boolean
- **Daily aggregation:** case count, routine/novel split, escalation count by reason, packet acceptance rate (when AM/CO confirms), avg time-to-close
- **Surface:** CRM dashboard or Google Sheet (whichever Sarah/CO supervisor prefers — choose at Wave 1 setup)
- **Alerts:**
  - Schema-validation failure (any) → ops + halt
  - Packet acceptance rate < 90% over rolling 7d → calibration alert to CO supervisor
  - Routine coverage < 50% over rolling 7d → calibration alert (under-confident classifier)
  - Chase nudges sent > expected daily volume → cadence calibration alert
  - 0 cases processed in any 6hr window during business hours → ops (silent failure check)

---

## Agent 2 — Cross-Stream Damage→Billing Watch (DECA-light, Wave 3)

```
Agent Name: DECA-light — Damage→Billing Watch
Job to be Done: When WS1 records a damage exception, generate a "billing-watch"
                record on the customer + invoice + delivery context — feeding
                BDRA's intake at 4.4 with the upstream cause already known.
                Reduces WS4 dispute volume at source.

Covers: CLM C1C cross-stream handoff (BP-X1 prevention).

Delegation archetype: Agent-led + Human Oversight.

Wave 3 prerequisites:
  - G-11 resolution (dispatch console) OR G-10 (Driver App) for damage-flag read
  - Wave 1 BDRA stable (so the billing-watch records have a consumer)
  - Dispatcher-side process change: structured damage flag emitted at WS1 task 1.6
    (otherwise the read-side has no signal to lift). This is a process
    prerequisite, not a downstream wave.
```

---

## Compounding roadmap

| Wave | Agent | Build | Reuses | Effort recovered (central) |
|---|---|---|---|---|
| 1 | BDRA core (C4A + C4B-routine + C4D + C4E) | Aurum schema validator; AM router; CRM dispute writer; chase engine; dossier composer; remedy template library | — | ~2,700 hr/yr (35% of WS4) |
| 2 | C4C Aurum auto-write | Aurum UI service-account client | Wave 1 schema validator + packet generator | +800–1,200 hr/yr |
| 3 | DECA-light (C1C) | Dispatch console / Driver App damage-flag read; billing-watch generator | Wave 1 CRM writer + dossier composer | +500–800 hr/yr (upstream prevention) |

### Integration reuse matrix

| Asset | Wave 1 | Wave 2 | Wave 3 |
|---|---|---|---|
| Salesforce CRM REST | Build | Reuse | Reuse |
| Aurum CSV file watch | Build | Reuse | Reuse |
| Aurum schema validator | Build | Reuse | Reuse |
| AM coverage map config | Build | Reuse | Reuse |
| Remedy template library | Build | Reuse + extend | Reuse |
| AUDIT_REF generator | Build | Reuse | Reuse |
| Dispute-state writer | Build | Reuse | Reuse |
| Aurum UI service-account client | — | Build | Reuse |
| Dispatch-console / Driver App reader | — | — | Build |
| Billing-watch generator | — | — | Build |

---

## Open deployment blockers

| Blocker | Wave | Priority | Owner |
|---|---|---|---|
| Dispute system identification (CRM cases? dedicated app?) | 1 | P0 launch | Engineering + Sarah |
| Aurum CSV access path + service account credentials | 1 | P0 launch | Engineering + Aurum support |
| Schema validation contract per Aurum file (BILL_DAILY, FUEL_SURCH, CREDITS, RECON, DISPUTES_OPEN, AGED_RECEIVABLES, CUSTOMER_MASTER) | 1 | P0 launch | Engineering |
| AM coverage map config (Q7 — also resolve A-5 routing fallback rule) | 1 | P0 launch | Sarah + AMs |
| CO authority threshold for self-prepared packets (£) | 1 | P0 launch | Sarah |
| Remedy template library seed (FUEL_SURCH_DAMAGE pattern + DIM_WEIGHT pattern + REDELIVERY_FEE pattern) | 1 | P1 — affects accuracy | Sarah + CO supervisor |
| Confidence thresholds (provisional: routine ≥ 0.8; mock-tested) | 1 | P1 — calibration | ML/ops + Sarah |
| Aurum UI service-account auth model | 2 | P0 Wave 2 | Engineering + Aurum support |
| Chase cadence (T+7, T+14, T+30 — provisional) | 1 | P1 — Sarah preference | Sarah |
| Customer comms tone calibration (first 100 cases human-confirmed) | 1 | P1 — trust build | CO supervisor |
| Dispatch console / Driver App damage-flag read API | 3 | P0 Wave 3 | Engineering |

---

# 5. System & Data Inventory

**Gate 2 — Apex Distribution Ltd**
**Source:** APD (`04`), brief tooling sketch, Aurum CSV catalogue (artefact 5), CSV samples

> Inventory for **Wave 1 BDRA** + **Wave 2 (C4C Aurum auto-write)** + **Wave 3 (DECA-light damage→billing watch)**. System boundaries match `04`.
>
> **Code legend:** `C4C` etc. = DSM task clusters; `4.10` etc. = APD activity-catalog tasks; `G-N` = open gaps (canonical: `CLAUDE.md` §Open gaps); `A-N` = cross-artefact evidence (canonical: `00_elicitation_log.md`).

## Wave 1 — BDRA

### Required systems

| System | Data needed | Access | Availability | Gap / Risk |
|---|---|---|---|---|
| **Salesforce CRM** | Dispute records, customer records, cases (cross-stream WS1 check), dispute-state writes, QA tags | Read + Write (REST, OAuth 2.0) | Modern SaaS; brief: "REST APIs available" | Confirm dispute object model (G-9b) — disputes may live as Cases, custom object, or in dedicated app |
| **Aurum CSV file-watch** | 7 daily/weekly/monthly files: BILL_DAILY, FUEL_SURCH, CREDITS, RECON, DISPUTES_OPEN, AGED_RECEIVABLES, CUSTOMER_MASTER | Read-only (file system / SFTP) | Brief: "Batch-file exports only … 02:00–04:00 GMT" | **P0:** access path (SFTP? shared mount? service account scope?). **P0:** schema validation contract per file. **P1:** quarterly Aurum schema-change risk (per `00` elicitation Q7) |
| **Aurum schema-validation contract store** | Per-file schema spec (column count, names, order, types, value ranges) | Read | Does not exist | **P0 build.** Generated from current CSV samples; versioned in repo |
| **AM email queue (Wave 1 only)** | Credit packet handoff for human Aurum UI entry (4.9E) | Write | Email exists | **P0:** AM coverage map config; routing rules for A-5 mismatch fallback |
| **Internal config store** | AM coverage map, remedy template library, authority thresholds, chase cadence, confidence thresholds | Read | YAML in repo | Versioned; deploy review on change |
| **Slack/email ops channel** | Schema validation failures, silent-failure alerts, calibration alerts | Write | Channel exists `[Inferred — standard ops practice; confidence Med]` | **P0:** Channel + webhook configured |

### Out-of-scope systems (Wave 1)

| System | Status | Reason |
|---|---|---|
| Aurum UI write | Wave 2 | Blocked on G-12 (service-account auth) |
| Aurum support ticket queue | Out of scope | 48hr SLA path is a fallback, not an agent integration |
| Driver App | Wave 3 | Blocked on G-10 (API surface); only needed for DECA-light |
| Dispatch console | Wave 3 | Blocked on G-11 (limited API surface unconfirmed) |
| Phone IVR | Out of scope | Not in BDRA's intake path; disputes arrive via CRM/email |
| Customer-facing UI | Out of scope | Sarah wary of customer-facing (Q1); BDRA is internal-facing |
| Stripe | Out of scope | Not in dispute resolution flow |

---

## Wave 2 — C4C Aurum auto-write

| System | Reuse / new | Notes |
|---|---|---|
| Salesforce CRM | Reuse | Same client |
| Aurum schema validator | Reuse + extend | Add validation for credits-write response (next-day APEX_CREDITS export AUDIT_REF lookup at 4.10) |
| **Aurum UI service-account client** | **New** | Blocked on G-12. Likely Selenium/Playwright pattern; needs Aurum login credentials with credit-write scope |
| AM email queue | Demoted | Used only as fallback if UI client fails |

---

## Wave 3 — DECA-light (damage→billing watch)

| System | Reuse / new | Notes |
|---|---|---|
| Salesforce CRM | Reuse | Write billing-watch records as CRM custom object or Case child |
| **Dispatch console / Driver App damage-flag read** | **New** | Blocked on G-11 (console) or G-10 (app). Either source works; pick whichever has better damage-flag fidelity |
| Aurum schema validator | Reuse | Same contract |
| Internal config store | Reuse + extend | Add damage-flag → billing-watch routing rules |

---

## Credentials

All API keys / secrets via environment variables; never committed.

| Variable | Purpose |
|---|---|
| `SF_CLIENT_ID` / `SF_CLIENT_SECRET` / `SF_PRIVATE_KEY` (or `SF_REFRESH_TOKEN`) | Salesforce OAuth — **JWT bearer flow preferred for unattended service** (no user interaction at refresh); refresh-token flow is a fallback if JWT not approved by SF admin. Engineering decides at provisioning. |
| `SF_API_VERSION` | Pinned Salesforce API version (avoid breaking on auto-upgrade) |
| `AURUM_FILE_PATH` | File watch root (`/exports/aurum/` per artefact 5) |
| `AURUM_FILE_AUTH` | SFTP credentials OR mount permissions, depending on access mode |
| `AM_ROUTING_CONFIG_PATH` | Path to AM coverage map YAML |
| `OPS_ALERT_WEBHOOK` | Slack/email webhook for ops alerts |
| `AGENT_VERSION` | Git SHA at deploy (written into per-case event log only — NOT into AUDIT_REF, which stays compact for Aurum-side ID matching) |
| `BDRA_AUTHORITY_THRESHOLDS_PATH` | Path to threshold YAML (CO max, AM tiers) |
| `AURUM_UI_SERVICE_ACCOUNT` (Wave 2) | Aurum login for service-account UI write |

---

## Shared Wave 1 → Wave 2/3 assets

Built in Wave 1, reused downstream:
- Salesforce CRM client + dispute-state writer
- Aurum CSV file watch + schema validator (the most-reused shared asset — Wave 2 reuses for write-back verification, Wave 3 reuses if billing-watch needs invoice context)
- Internal config store pattern (YAML + versioning + deploy review)
- AM coverage map (Wave 2 reuses for service-account approval routing)
- AUDIT_REF generator (Wave 2 reuses for service-account-emitted credits)
- Remedy template library + pattern matcher (Wave 2 reuses; Wave 3 reuses to predict downstream remedy)
- Per-case event log + ops alert pipeline

---

## Pre-launch P0 checklist (Wave 1)

- [ ] Dispute system identified (G-9b) — CRM cases vs custom object vs dedicated app
- [ ] Aurum CSV access path provisioned (SFTP/mount) + service account permissions verified
- [ ] Schema validation contract written for all 7 files; tested against current samples
- [ ] AM coverage map config loaded; A-5 mismatch fallback rule decided with Sarah
- [ ] CO authority threshold (£) defined with Sarah
- [ ] Remedy template library seeded for FUEL_SURCH_DAMAGE, DIM_WEIGHT, REDELIVERY_FEE
- [ ] Confidence thresholds set (provisional; mock-test calibrated)
- [ ] Chase cadence approved by Sarah (T+7 nudge, T+14 escalate, T+30 close-proposal)
- [ ] Salesforce OAuth app registered; refresh token issued
- [ ] Ops alert webhook live; tested with synthetic schema-failure event
- [ ] First 100 cases human-confirmed customer-comms send (tone calibration window)
- [ ] Idempotency tested: same dispute_id processed twice = no duplicate packets
- [ ] Schema-drift drill: deliberately corrupt a CSV; confirm agent halts cleanly
- [ ] Schema-failure alert latency test: confirm ops Slack/email webhook fires ≤15 min from agent halt; ops can disable BDRA Aurum reads within 1 hour of alert
- [ ] Partial-failure recovery test: simulate CRM write failure between tasks 4.9 (packet prepared) and 4.12 (state update); confirm agent re-reads dispute by `processing_id` on retry and any committed step is no-op (idempotency holds across the 4.9 → 4.12 sequence)

## Pre-launch P0 checklist (Wave 2)

- [ ] G-12 resolved: Aurum UI accepts service-account login with credit-write scope
- [ ] Service-account credentials issued + rotated to secrets manager
- [ ] UI automation client built + tested in Aurum sandbox (if available) or with throwaway test customer
- [ ] Verification loop: AUDIT_REF emitted by agent appears in next-day APEX_CREDITS export
- [ ] Rollback plan: how to reverse a wrongly-applied credit if UI write succeeds but logic was wrong (manual reverse via Aurum support 48hr ticket)

## Pre-launch P0 checklist (Wave 3)

- [ ] G-11 (dispatch console) OR G-10 (Driver App) damage-flag read API confirmed
- [ ] Damage-flag → billing-watch mapping rule defined
- [ ] BDRA Wave 1 stable (≥3 months production) before Wave 3 starts feeding it pre-emptive cases

---

# 6. Discovery Questions

**Gate 2 — Apex Distribution Ltd**
**Stakeholder:** Sarah Whitmore, COO

> Optimised for the 10-min live round (or ~3 min in small-group). **Q-numbering is stable — preserved from the discovery catalog so cross-references in CLAUDE.md, APD, DSM remain valid.** The Top-4 are flagged in priority order; everything else is reference.
>
> **Code legend:** `Q1–Q15` = questions defined below; `G-N` = open gaps (canonical: `CLAUDE.md` §Open gaps); `A-N` / `B-N` = cross-artefact evidence (canonical: `00_elicitation_log.md`); `BP-X1` = cross-stream breakpoint (canonical: CLM).

---

## Live-round priority order (the four to actually fire)

**Fire in this order:** **Q3** (highest chance to change the implementation) → **Q2** (lived-vs-documented anchor) → **Q5** (success criteria) → **Q4** (TCO baseline). **Backup: Q1** (only if you've burned through Top 4 with time left).

Each one carries the *spoken question* (plain English for Sarah), a *quantifier follow-up* (force a number when she hedges), and the *design fork* (what changes per answer — facilitator-only).

### Q3 — Sandra audit-bypass pattern (highest chance to change the implementation)

**Spoken:** *"Sandra applied £170 in goodwill credit on Pete's case without proper sign-off from a manager. How often is that happening across your team?"*

**Quantifier follow-up:** *"Out of 10 recent goodwill credits — how many would have the right manager's sign-off on them?"*

**Design fork:**
- "Most have it" → governance-upgrade is polish, not headline. BDRA's APPROVER_ID enforcement = nice-to-have
- "Maybe half" → governance-upgrade IS the primary metric; Wave 1 ROI reframes as compliance
- "Hardly any" → entire AM authority model needs Sarah to choose: (a) raise CO authority, (b) AM async approval, (c) CO supervisor counter-sign

### Q2 — Damaged-consignment actual workflow (lived-vs-doc anchor)

**Spoken:** *"Your SOP doesn't have a procedure for damaged pallets — it's left blank. When a damaged pallet is rejected, like in Mark's call, what does your dispatcher actually check before deciding what happens next?"*

**Quantifier follow-up:** *"Out of 10 recent damaged-pallet calls — how many came back to the depot, how many were left with the customer, how many were photographed and abandoned?"*

**Design fork:**
- Codifiable criteria → DECA-light Wave 3 unlocks earlier; agent can pre-stage and recommend
- "It varies, judgment call" → DECA-light stays context-only, dispatcher decides; honest Wave 3 scope

### Q5 — CEO success metric vs £1.2M anchor

**Spoken:** *"Your CEO heard about a competitor saving £1.2M. What result would HE consider a success in year one — in plain terms?"*

**Quantifier follow-up:** *"If you had to pick a number to put in front of the board — caveats fine — what would land?"*

**Design fork:**
- Hard target ≥ £500K → Wave 1 alone insufficient; need committed Wave 2/3 in the plan
- "A story he can tell, no number" → Wave 1 £25–67K (Scenario B–A range, V×V §3) + governance upgrade is enough
- "Match £1.2M" → Wave 1 BDRA insufficient; portfolio approach (BDRA + non-agent rules/RPA on ETA lookup)

### Q4 — 35-headcount split (cost baseline)

**Spoken:** *"Roughly how is your 35-person team split — dispatchers, customer-facing agents, account managers, supervisors?"*

**Quantifier follow-up:** *"To give your CFO a clean hours-saved-per-person figure, which group should I divide my numbers into?"*

**Design fork:**
- <15 are CO agents (the BDRA target sub-population) → all £-figures in V×V halve; FTE-equivalent drops
- 20+ CO agents → V×V baseline holds; cleaner ROI per agent

---

### Backup — Q1: 2024 chatbot failure mode

**Spoken:** *"The 2024 chatbot — what specifically went wrong that made you pull it?"* (let her describe; classify silently)

**Quantifier follow-up:** *"How long did it run before you killed it?"*

**Design fork:**
- Script-trap-shaped → BDRA's customer-comms drafts must be free-form
- Tone/voice → human-confirm window stays longer than 100 cases
- Misclassification → confidence-threshold floor 0.8 is non-negotiable

---

## Other P0 questions (catalog — for follow-up sessions, not live round)

| # | Spoken | Closes |
|---|---|---|
| Q6 | *"When a damaged delivery becomes a billing dispute weeks later — like Pete's case — who owns it through to resolution? Does the original dispatcher even know it became a dispute?"* | G-7, BP-X1 |
| Q7 | *"Looking at BlueSky's account, its named manager is one person but the credit was approved by another. Who's actually allowed to approve credits in practice — always the customer's own manager, or can any manager step in?"* | A-5 + AM authority routing gap (CLAUDE.md gap register) |
| Q8 | *"When your team applies a credit, what's the real process today? Could that step ever be done automatically by software, or must a person always do it?"* | G-12 (engineering) |

## Build-design questions (P1 — calibration / preference)

| # | Spoken | Closes |
|---|---|---|
| Q9 | *"I'm seeing a date mismatch in your dispute export — D-342 has an open-date that's later than the file's date. Which date should we trust as the 'as of' date when reading these files?"* | A-7 |
| Q10 | *"If the system handles about two-thirds of routine cases in month one and your team picks up the rest, is that acceptable while we tune it? Or do you want a higher floor from day one?"* | Calibration tolerance |
| Q11 | *"Where should action requests go so account managers actually see them quickly — email, Slack, a task in your CRM, somewhere else?"* | 4.9E channel |
| Q12 | *"Do you have sample 'good' customer-closing emails I can use as templates, or someone I can sit with for an hour to learn your team's voice?"* | Tone calibration |
| Q13 | *"For disputes waiting on the customer to respond — like D-337 which has been waiting since March — how often should we be following up?"* | Chase cadence |
| Q14 | *"At what credit amount must a manager approve, instead of customer ops handling it directly? Today, what's the most Sandra can do on her own?"* | CO authority threshold |
| Q15 | *"Sandra's email said fuel surcharge can't be adjusted on individual invoices — but I see a £45 fuel-recalculation credit was applied to Northstar. In which situations IS fuel recalculation actually allowed, and what proof is needed?"* | A-6 |

## Out-of-scope (do not ask — burns live time)

- Anything answerable from the brief or CSVs (volumes, vehicle count, system names)
- Open-ended process tours ("walk me through your operations" / "what are your pain points" / "tell me about your tooling")

---

## Interviewer cheat sheet (Appendix)

### Evasion / hedge handling

| Sarah says | Move |
|---|---|
| "It varies" / "it depends" | *"If you had to guess, what's the number — caveats fine?"* |
| "My team handles that" | *"Who specifically? Could I follow up with them after?"* |
| Long anecdote | Let her finish (don't cut off COO), then: *"What's the rule that comes out of that?"* |
| "We follow the SOP" | *"That's the SOP — what actually happens when [specific case]?"* |
| Specific number, no caveat | If contradicts CSV/artefact: *"I'm seeing X in the data — help me square that"* |

### Testimony-vs-artefact watch (where Sarah may give COO-frame answers that diverge from lived evidence)

- **Q3 (Sandra pattern):** if Sarah says "rare", probe — A-4 is structural (Sandra has no APPROVER_ID role), so it's the system, not the person. Push: *"It happened on the case in front of me — how would you measure 'rare'?"*
- **Q2 (damaged workflow):** Sarah is ex-dispatch — she'll likely give a confident, tidy answer. Cross-check against artefact 1 specifics (damage-extent + receiving-party posture + remaining-route-pressure). If her version omits any of those, that's a real-vs-self-image gap. Don't argue — note silently.
- **Q5 (CEO metric):** the £1.2M is an external anchor, not Sarah's. Listen for HER framing — what she thinks would land, not what she's been told.
- **Backup Q1 (chatbot):** if she gives a tone answer when context suggests script-trap, probe both. Failure narrative is often clean; lived failure is often messier.

### The "update live" move (rubric-rewarded)

When Sarah's answer overturns a design assumption:
> *"That changes my [X] — let me adjust. So if I'm hearing right, [paraphrase], which means [design implication]. Does that land?"*

One of these is worth more than two extra questions.

### Closing move (last 60s)

> *"Quick check — three things I'm taking away to update my design: [Q3 answer], [Q5 answer], [Q2 answer]. Did I miss anything you'd want me to weight differently?"*

Forces Sarah to confirm OR add the thing she didn't volunteer.

### Source pointer

AI-proxy reconstructions of Sarah's likely answers and the gap register are in `00_elicitation_log.md`. Do not cite them as Sarah-confirmed during the live round.

---

# 7. CLAUDE.md

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

