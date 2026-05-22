# Cognitive Load Map
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
