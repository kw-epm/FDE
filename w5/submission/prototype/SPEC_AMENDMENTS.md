# Spec amendments & build notes — Deliverable #12

**Read this against the Tuesday design alone — it is self-contained.** The design package
(#1–#11) was submitted end of Virtual Tuesday and is the spec of record. This note ships with
the prototype (#12) and records *every* way the build diverges from that submission and why, so
no other file is required to follow it. Per the Gate 5a pack: *"known gaps beat hidden gaps… a
spec amendment note alongside the prototype is honoured."* The pristine Tuesday originals are in
`../design-backup-pre-multiagent/`. None of these changes alter the agent's **scope** or its
**safety guarantees**; they change decomposition, presentation, and prompt calibration.

---

## 1. Single agent → multi-agent (Coordinator + workers) — the largest change

**Tuesday design:** one "ResolveOne Triage & Disposition Agent" (`04`) with two capability specs —
**Spec A** (triage/disposition) and **Spec B** (entitlement pre-fill + human gate) (`06`).

**Build (adopted on the Wednesday coach-checkpoint steer):** the *same capabilities*, re-expressed
as the **orchestrator-workers** pattern — a **Coordinator** orchestrating four specialist workers.
Purpose, scope, autonomy matrix, escalation triggers, and hard constraints are unchanged; only the
decomposition changed. Spec A's flow is split across Coordinator/Triage/Resolution/Escalation; Spec B
is the Entitlement worker.

| Agent | Model | Responsibility |
|---|---|---|
| **Coordinator** | Sonnet (residual decision only) | Owns the disposition decision + delegation: idempotency, phone short-circuit, fail-loud customer lookup, runs the deterministic guardrail gate, decides the residual tier, routes to one worker, writes the audit line |
| **Triage** | Haiku | Classify `issue_type` + surface signals; decides/routes nothing |
| **Resolution** | Sonnet | Compose the Tier-1 KB-grounded reply |
| **Entitlement** | Sonnet | Spec B — eligibility + pre-fill + holding message; **never approves** (`approved=False`) |
| **Escalation** | Sonnet | Tier-3 internal briefing for the named human |

**How the agents communicate:** hub-and-spoke, **in-process typed messages** (function calls passing
typed objects). The Coordinator is the only caller; **workers never call each other**. Not a wire protocol.

```
Coordinator → Triage:        Ticket             → classification {issue_type, confidence, signals}
Coordinator → guardrail gate: classification+record → {forced_tier, flags, route}  (deterministic, synchronous)
Coordinator → Resolution:    Ticket+class+KB    → {draft, kb_articles}
Coordinator → Entitlement:   Ticket+record      → EntitlementRequest(approved=False)
Coordinator → Escalation:    Ticket+class+flags → briefing
Coordinator → audit:         Disposition(+handled_by) → one immutable JSON line
```

The deterministic **guardrail gate** (the Tuesday ADR-1 layer — entitlement/identity/legal/abuse/
enterprise/phone/low-confidence) still sits between Coordinator and workers and can only *downgrade*
autonomy. It remains the binding safety layer. Every disposition is tagged `handled_by`, and the live
UI labels each step **AI** (model call) vs **deterministic** (code).

**Alternatives considered and rejected (this is the full ADR-6, inlined so it stands alone):**
- *Keep the single-agent pipeline (Tuesday design).* Simpler and ~1 fewer model call/ticket, but
  presents the disposition as one monolithic step and doesn't make the decision/execution boundary
  legible — the exact thing the checkpoint asked to see.
- *Peer-to-peer agent mesh (workers negotiate directly).* Rejected: adds coordination cost and makes the
  compliance gate far harder to guarantee, for a flow that is fundamentally one routed decision per
  ticket. There is no negotiation to have.
- *Distributed agents over a protocol — A2A / a message bus / MCP-as-agent-transport.* Rejected for
  Phase 1: the workers are one team's code in one deployable service; in-process typed messages are
  lower-latency, keep a single audit trail, and let the guardrail gate run synchronously. **MCP** is
  reserved for the external *tool/data* surface (KB, billing, ticketing — see `07`); **A2A / a queue** is
  the production-scale option *if* workers ever become independently deployed. Phase 1 needs neither.

**Trade-off / economics delta (against `08`):** separating *decide* from *compose* adds **+1 Sonnet
call on the Tier-1 path** (classify + decide + compose = **3** vs 2); the new Escalation briefing adds
**+1 Sonnet call on Tier-3** (**2** vs 1). Entitlement unchanged (2); phone unchanged (**0**). The
Coordinator only spends a *decide* call on the residual (when no guardrail has already decided), so cost
is concentrated where judgment is genuinely needed. Net ≈ **+$360/yr** ($2,160 → $2,520, ~1% of the
labour saving) — the business case in `08` is unchanged. Bought for a more legible, more extensible
architecture and a clean decision/execution separation.

---

## 2. The decision is separated from the composition

`06` Spec A specifies the residual Tier-1/2/3 decision as a bounded **Sonnet** call (P2). Under the
multi-agent topology this is split: the **Coordinator** makes the tier **decision** (P2-decide) and the
**Resolution worker** does the **composition** (P2-compose). Either way the deterministic layer then
**enforces the Tier-1 envelope** (allow-list ∧ confidence ≥ τ ∧ retrieval_ok ∧ no guardrail flag ∧ KB
cited) and downgrades anything that fails it. The offline mock reproduces both steps deterministically so
the tests pass with no API key.

---

## 3. Structural & presentation deltas (no behavioural change)

| `CLAUDE.md` / design said | Prototype ships | Why |
|---|---|---|
| `core/classify.py` | `core/llm.py` | classify (Haiku P1) + decide/compose (Sonnet P2) + holding (P3) + briefing (P4) share the provider, key handling, retry, and the live/mock swap — one boundary is cleaner than several files. Prompt contracts unchanged. |
| customer lookup as plumbing | `core/stores.py` `CustomerStore` | sibling deterministic reader to `core/retrieve.py` (KBIndex). |
| `app.py` — **Gradio** UI | `demo.py` (CLI) + `server.py` (FastAPI) + `ui/` (React/Vite) | The graded requirement is a **live demo of running code**. `server.py` is a thin FastAPI wrapper over `core.disposition.triage` (it also streams a live per-agent trace via SSE); `ui/` is the React frontend; `demo.py` is the zero-dependency CLI fallback. **UI-tech divergence only** — no behavioural/scope change. |

**Deployment (beyond the #12 spec, noted for completeness):** the prototype is packaged as a **single
Docker image** (FastAPI serves the API *and* the built React UI on one port) and deployed to Kubernetes
(`k8s/`). In deployment the app is mounted under base path **`/2905/`** (`/` 307-redirects there) and the
`Server`/`Date` response headers are dropped at uvicorn. These are hosting choices; the agent is identical.

---

## 4. Build-phase LLM calibration (the live model over/under-triggered on real phrasings)

The Tuesday `06` prompt templates (P1/P2) were tightened during the build after the **live** Haiku/Sonnet
calls mis-fired on real wording. The deterministic gate and the mock are unchanged; these align the live
model with the intended semantics. Each was a one-line prompt refinement, logged here for faithfulness:

- **`distress_signal`:** a deadline/urgency alone (e.g. "meeting in 30 min") is **not** distress — distress
  requires anger, repeat contact, threats to leave, or demanding a human. (Also: the distress/complaint
  escalation now records a **`DISTRESS` guardrail flag** so the trace/audit explains it, instead of empty
  `flags=[]`.)
- **`multi_intent`:** one problem phrased as several questions ("can't log in — is it my password? how do I
  proceed?") is a **single** intent, not multi-intent.
- **`entitlement_signal`:** a declined or informational mention ("I'll keep it", "never mind", "just FYI")
  is **not** an active request and must not trip the entitlement gate.
- **KB anchor is a strong prior (extends spike finding #1):** an allow-list issue type now **grounds on its
  canonical article** (`PASSWORD_RESET → password-reset.md`, etc.) directly — keyword retrieval was brittle
  on synonyms ("credentials" vs "password"). The Tier-1 confidence gate (τ) + the guardrails still guard
  misclassification; keyword retrieval is the fallback only for issues with no anchor (`HOW_TO_QUESTION`).
- **Resolution worker:** composes from the (canonical) article and returns `draft=null` **only** on a true
  *topic* mismatch — never because the request is terse — so a confidently-classified read-only ticket
  resolves consistently regardless of phrasing.

These tune *classification precision*, not the safety model: a misfire still degrades toward a human, never
toward an unsafe action.

---

## 5. Validation results & known-safe misses

Offline eval against `validation/ground-truth-labels.csv` (48 labelled tickets): **V1** (entitlement-gate
precision — 0 auto-resolved) **PASS**; **V2** (phone leakage — 0) **PASS**; **V3** tier accuracy **91%**
(31/34 certain rows). All 3 misses are the **safe** direction — the agent routes to a human where the
oracle would have done more (two `technical_issue` → Tier 2 not Tier-3 specialist; one `how_to_question` →
Tier 2). None auto-resolves something that needed a human. Automated tests cover the three required paths +
safety negatives (guardrail independence, forbidden-phrase filter, legal override, `approved` never True,
the AUTO_RESOLVE-requires-citation invariant, enterprise-cancellation-not-filed, and missing-customer
fail-loud).

---

## Closing — every divergence fails toward a human

The agent fails **closed**: unsure → human, can't-approve → human, source unreachable → human, classifier
misfire → human. So these amendments cost throughput and tuning effort in production, never a compliance
breach. That asymmetry — model judges within bounds, deterministic code guarantees the bounds — is the
design's load-bearing property, and it is preserved by every change above.
