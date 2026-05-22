# Delegation Suitability Matrix
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
