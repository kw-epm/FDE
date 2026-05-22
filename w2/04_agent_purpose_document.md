# Agent Purpose Document
**Scenario 4 — Community Content Moderation (MiniBase)**
**Date:** 2026-04-30
**Source:** DSM (03_delegation_suitability_matrix.md), CLM (02_cognitive_load_map.md)

> **Epistemic status:** Design choices that depend on data not in the brief are marked `[Unconfirmed: requires X]`. These are deployment blockers, not conservative assumptions. Inferences are tagged `[Inferred]` with confidence.

---

## Agent Selection Rationale

| Work stream | Daily volume | Agent-led clusters | Effort recoverable |
|---|---|---|---|
| WS1 — Routine spam | 1,080 cases | Cluster 1 (full WS1 flow) | ~9 hrs/day (19%) |
| WS2 — Grey-zone | 360 cases | Cluster 4 (documentation) | partial of 30 hrs/day |
| WS3 — Appeals | 60 cases | Cluster 5a (context assembly) | partial of 8 hrs/day |
| WS4 — IP claims | 3–5/wk | None | 0 |

**Primary agent (Wave 1):** WS1 Routine Moderation Agent. Highest volume, clearest delegation profile, best economics. The integrations it builds (Discourse client, VIP service, policy RAG) compound directly into Wave 2.

**Secondary agent (Wave 2):** Moderation Context Assembly Agent. Serves Clusters 2 (grey-zone context), 4 (grey-zone documentation), and 5a (appeals dossier). Blocked on sub-forum norm structuring; cannot precede that prerequisite.

---

## Agent 1 — Routine Moderation Agent

### Purpose Document

```
Agent Name: MiniBase Routine Moderation Agent
Job to be Done: Triage flagged content in the routine spam/clear-violation queue
                and execute the correct disposition (remove violation, warn user,
                or dismiss erroneous flag). Escalate to human review on VIP match,
                low confidence, multi-label classification, or policy gap.

Business context: Work Stream 1. ~1,080 cases/day at ~30 sec/case = ~9 hrs/day team effort.

Primary objectives:
  1. Process the WS1 queue with accuracy sufficient to sustain < 2% appeal rate
     on agent-handled dispositions.
  2. Guarantee no VIP account post (controlled list: @vortex_minis, @sculpturedragon,
     @vintage_kitbasher, plus any later additions) is acted on without human review.

KPIs (paired so they cannot conflict):
  - Accuracy: ≥ 98% correct dispositions (not reversed by reviewer; not upheld on appeal)
  - Coverage: ≥ 80% of WS1 queue handled autonomously (= HITL ≤ 20%)
  - HITL rate: target 10–20%; HITL > 20% triggers calibration alert
              (consistent with Coverage floor; no separate ceiling)
  - Throughput: ≥ 1,080 cases/day with headroom for growth
  - Cost per case: target < 10% of human-handling equivalent
                   [Unconfirmed: requires token cost modelling at expected case length]

Failure modes:
  - VIP miss → existential (founder brief). Prevented by task 1.3 account_id
    exact-match short-circuiting to 1.3E before classify. Recovery: Discourse `recover`.
  - False positive → reversible via `recover`. Prevented by 1.5H confidence gate.
  - False negative on routine spam → low risk (lacks viral potential).
    [Inferred: founder's asymmetric-error principle named VIP/high-profile FNs as
    existential but did not generalise to routine spam; confidence: Medium]
    Detected by 5% QA sampling of dismiss_flag items (task 1.7Q).
  - Borderline routed as clear → caught by appeals; ≤ 1 appeal-cycle cost.
    Prevented by multi-label trigger (top-2 violation classes within 0.15,
    excluding no_violation, both > 0.4 confidence).

Delegation archetype: Agent-led + Human Oversight
  Determinism (H) and volume (H) support autonomous action on clear violations.
  VIP detection gap and unconfirmed exception rate block promotion to Fully Agentic.

Escalation triggers (must match Autonomy Matrix exactly):
  - VIP account match (controlled-list exact-match on account_id at task 1.3)
    → Tom queue with pre-classification dossier;
    post is auto-hidden pending Tom's review (Discourse `hide` action, reversible)
    [Unconfirmed: hide-vs-leave-visible is a Tom decision; see interview Q9]
  - Confidence < 0.6 → volunteer mod queue with classification dossier
  - Confidence ∈ [0.6, 0.8] → fetch account history; re-evaluate once;
    if still in [0.6, 0.8] → volunteer mod queue
  - Multi-label classification (top-2 violation classes within 0.15 of each other,
    excluding `no_violation`, both above 0.4 confidence)
    → volunteer mod queue (annotated as borderline)
  - Policy RAG miss (no chunks above relevance threshold for given violation type)
    → Tom queue with "policy gap" annotation
    (policy gaps are systemic, not case-level grey-zone judgments)
  - VIP service unreachable → fail closed: every case escalates to volunteer mod
    queue with `vip_service_unavailable` annotation; alert Discord #ops; halt
    autonomous action until service restored
  - Discourse API write failure → dead-letter store; alert Discord #ops;
    retry up to 3 times with exponential backoff
```

---

### Activity Catalog

> **Sequence note:** This catalog repositions VIP lookup (1.3) before classification (1.4), reversing the as-is CLM order. Intentional design change: VIP detection at intake closes CLM breakpoint BP1.C (the existential failure mode). The as-is order is a human process artifact, not a design constraint.

| # | Task | Type | Delegation level | Data required | Tool | Risk |
|---|---|---|---|---|---|---|
| 1.1 | Poll Discourse flag queue (60s interval) | Retrieval | Fully agentic | Discourse flag queue | Discourse REST API (read) | Low |
| 1.2 | Extract post text + flag metadata + account_id + sub_forum_id; **assign `processing_id`** (one per flagged item, used for idempotency from 1.6 onward) | Retrieval | Fully agentic | Post, flag, account, sub-forum | Discourse REST API (read) | Low |
| 1.3 | VIP account lookup (exact match on account_id) | Retrieval | Fully agentic (system call only) | VIP controlled list | VIP service (live query) | High — must not miss |
| 1.3E | If VIP match: auto-hide post pending Tom's review; package pre-classification dossier; route to Tom | Escalation | Human takes over | Post, flag, account_id, VIP rule key | Discourse `hide` + Discord webhook → Tom + mod-vip-escalation category | High |
| 1.4 | Classify violation type (LLM inference + policy RAG) | Reasoning | Agent-led | Post text, sub-forum norm (if structured) or global policy chunks | LLM, RAG retriever | Medium |
| 1.4E | If confidence < 0.6 OR multi-label: route to volunteer queue. If policy RAG miss: route to **Tom queue** (policy gaps are systemic, not case-level grey-zone). Package dossier per path. | Escalation | Human takes over | Classification output, confidence, reasoning chain | Discourse mod-review-queue category OR mod-vip-escalation category | Medium |
| 1.5 | Map (violation_type, confidence) → action via rule lookup | Decision | Agent-led | Classification output | None (rule lookup) | Medium |
| **1.5H** | HITL gate: if confidence ∈ [0.6, 0.8] AND no escalation already triggered, fetch account history and re-evaluate. If re-eval still in [0.6, 0.8], escalate to volunteer queue. If re-eval lifts confidence ≥ 0.8, pass through to 1.6 AND set `reeval_promoted=true` in the 1.7 log entry. | Decision | Conditional HITL | Confidence, account history | Discourse REST API (read user history) | Medium |
| 1.6 | Execute Discourse action (per action mapping table below) | Action | Fully agentic (post-1.5H) | Action decision, processing_id | Discourse REST API (write) | Medium |
| 1.7 | Write structured log entry as JSON code block in Discourse mod log | Generation | Fully agentic | All preceding outputs + processing_id + `reeval_promoted` flag | Discourse REST API (write) | Low |
| 1.7Q | QA sampling: tag 5% of `action == dismiss_flag` items (uniform random) with Discourse tag `qa-sample-{date}`. Reviewer (Tom or delegate) scans tagged items as part of existing daily review workflow. Stratification is a future calibration option. Focuses on false-negative detection. | Generation | Fully agentic (sampling); Human review (async via existing workflow) | Decision flag | Discourse tag API | Low |

**Note on 1.3:** Match exclusively on Discourse `account_id` (integer). Username strings can collide on case/aliases; account_id cannot. The VIP service must be a live runtime query, not a static config — additions take effect without agent restart.

**Note on 1.5H:** Closes the delegation boundary that would otherwise let 1.5 → 1.6 silently auto-promote borderline cases. The `reeval_promoted` log marker keeps the lifted-cohort auditable separately from first-pass-high-confidence cases (the canonical Week 2 anti-pattern, surfaced by the build loop).

**Note on 1.7:** Log entry = Discourse post in the dedicated **moderation log topic**. Title: `[mod-log] {processing_id}` (idempotency lookup is search-by-title). Body: fenced JSON:
```
{ processing_id, item_id, account_type ("vip"|"standard"), violation_type, confidence,
  action, escalation_reason | null, sub_forum_id, reporter_count, reeval_promoted: bool,
  agent_version (git SHA from env), timestamp (ISO8601) }
```
Wave 2 extends this schema with `norm_applied`, `decision_rationale`, `human_moderator_id` for WS2 decision logs (superset, not strict reuse).

---

### Action Mapping Table

**Default violation_type → action mapping** (applied at task 1.5; the LLM emits a recommended `action` directly in the structured output and the rule layer accepts it on the `≥ 0.8` path. The LLM is constrained by prompt principle 3 to choose only from the mapped set per violation_type — e.g. `spam` may map to `remove`; `off_topic` may map to `warn` or `dismiss_flag`; never cross-map):

| violation_type | Default action | Notes |
|---|---|---|
| `spam` | `remove` | No first-offence carveout in Wave 1 (account history not on the high-confidence path) |
| `off_topic` | `warn` | LLM may pick `dismiss_flag` if context (e.g. invited tangent) supports it |
| `miscategorised` | `dismiss_flag` | Wrong category; post itself is not violating |
| `no_violation` | `dismiss_flag` | Flag was erroneous |

**Discourse API endpoint mapping:**

| Action | Discourse API endpoint | Notes |
|---|---|---|
| `remove` | `DELETE /posts/{id}` (soft delete) | Reversible via `PUT /posts/{id}/recover` (admin only) |
| `warn` | `POST /private_messages` to OP + flag entry on user record | One-way; subsequent flag reviews see warning history |
| `dismiss_flag` | `POST /flags/{id}` with `disagree=true` | Marks flag as invalid; post stays |
| `escalate` | Write to volunteer or Tom queue category (no action on post) | Post remains visible until human reviews; exception: VIP escalation auto-hides the post per task 1.3E |
| `hide` (VIP escalation only, internal) | `POST /posts/{id}/hide` | Reversible; only invoked at 1.3E, never as a final disposition |

`[Unconfirmed: exact endpoint paths require Discourse write API auth scope confirmation — P0 blocker]`

---

### Autonomy Matrix

```
AGENT DECIDES AND ACTS ALONE (confidence ≥ 0.8, non-VIP, single-label, policy hit):
  - Queue intake (1.1, 1.2)
  - VIP lookup (1.3) — system call only, no inference
  - Classification (1.4)
  - Action selection + execution (1.5, 1.6)
  - Log write (1.7)
  - QA sample tag (1.7Q)

AGENT ACTS; HUMAN NOTIFIED AFTER (high-confidence dispositions, async review):
  - First-pass high-confidence (confidence ≥ 0.8 directly from 1.4): standard log entry
  - Re-eval-promoted (confidence lifted from [0.6, 0.8] into ≥ 0.8 at 1.5H): same log
    schema but with `reeval_promoted: true` — auditable as a separate cohort
  - Reviewers see structured log entries in Discourse moderation log topic
  - Daily QA review of 5% sampled `dismiss_flag` outcomes (uniform random)
  - No push notification in Wave 1; existing daily moderation review workflow covers it

AGENT PROPOSES; HUMAN APPROVES BEFORE ACTION (confidence ∈ [0.6, 0.8] after re-eval):
  - Volunteer mod queue (Discourse mod-review-queue category)
  - Dossier includes: post, classification, confidence, reasoning chain, account history

HUMAN TAKES OVER (agent supports with dossier):
  - VIP match → Tom (post auto-hidden + Discord webhook + Discourse mod-vip-escalation category)
  - Confidence < 0.6 → volunteer mod queue
  - Multi-label (top-2 violation classes within 0.15, excluding no_violation, both > 0.4) → volunteer mod queue
  - Policy RAG miss → Tom queue (systemic policy gap, not case-level judgment)
  - VIP service unreachable → fail closed (all cases to volunteer queue + halt) → on-call
  - Discourse API write failure → on-call (Discord #ops); item dead-lettered
```

---

### System and Data Inventory

**Extracted to standalone deliverable: see `07_system_data_inventory.md`** for the full inventory (Wave 1 + Wave 2 systems, credentials, shared assets, pre-launch checklist).

Summary: 11 systems referenced. **P0 launch blockers:** VIP controlled-list service (does not exist), Discourse write auth scope (unconfirmed), gallery posts intake path (unresolved), Discord webhook to Tom (must be configured), 3 Discourse setup tasks (moderation log topic, `#mod-review-queue` category, `#mod-vip-escalation` category).

---

### Context Engineering Design

#### Memory architecture

| Type | Content | Storage | Lifecycle |
|---|---|---|---|
| **In-context** | Current post + flag metadata + sub-forum ID + classification + confidence | Prompt window | Per case; cleared after log write |
| **Episodic** | Account disposition history (prior flags, actions, warnings) | Discourse API query | **Fetched conditionally only when confidence ∈ [0.6, 0.8]** (cost control). Not at intake. |
| **Semantic** | Global policy chunks; structured sub-forum norms (3 of 14 in Wave 1) | Vector index | Re-indexed on policy update (build trigger required) |
| **Procedural** | Decision rules, confidence thresholds, VIP routing, log schema, action mapping | System prompt | Version-controlled; deploy review on change |

#### Retrieval strategy

- **VIP lookup (task 1.3):** unconditional at intake. Exact-match on account_id. Match short-circuits to 1.3E.
- **Policy retrieval (task 1.4):** sub-forum ID routes to sub-forum-specific norm if structured (3 of 14 in Wave 1); else fall back to global policy. Top-3 chunks by cosine similarity. Violation-type label included as query context.
- **Account history (task 1.5H):** triggered only when confidence ∈ [0.6, 0.8]. Used to re-evaluate once before escalating.
  - Trade-off acknowledged: skipping account history for high-confidence cases means action selection in those cases is based on violation type only, not account history. Repeat-offender escalation rules cannot be applied to the high-confidence path. If repeat-offender rules become required, add account history to the unconditional path and accept the cost.

#### Prompt principles

1. **Role and scope first:** "You are the MiniBase Routine Moderation Agent. Classify and action clear violations from WS1. You do not decide grey-zone cases."
2. **Hard constraints as numbered rules:** "Rule 1: If account_id is in VIP list, stop. Do not classify. Route to escalation."
3. **Structured output:** classification must be JSON: `{ violation_type: enum[spam, off_topic, miscategorised, no_violation], confidence: float[0..1], action: enum[remove, warn, dismiss_flag, escalate], escalation_reason: enum[vip, low_confidence, multi_label, policy_gap] | null, top2_score_delta: float, top2_excludes_no_violation: bool }`. Invariants: (a) `action == "escalate"` iff `escalation_reason != null`; (b) `action` ∈ allowed defaults for the chosen `violation_type` (per Action Mapping table) — cross-mapping is an error; (c) `top2_score_delta` is computed over the top-2 *violation classes only*; if `top2_excludes_no_violation` is true, the multi-label trigger applies. Schema is enforced; deviation = error.
4. **Chain of thought for confidence ∈ [0.6, 0.8]:** reasoning chain attached to escalation dossier.
5. **Language handling:** detect post language. For Japanese-language posts in painters-Japan sub, default to soft-warning before removal action `[Stated: artefact 4.3]`.
6. **Few-shot examples:** Wave 1 launch uses brief artefacts as initial examples (artefact 4.1 = "no action — invited critique within sub norms"). Replace with annotated cases from Tom before production. `[Unconfirmed: requires Tom-validated examples]`

---

### Operational Constraints

- **Single-instance Wave 1.** Discourse flag queue has no claim semantics; horizontal scaling would race.
- **Idempotency.** `processing_id` assigned at 1.2; looked up at 1.6 via Discourse search by post title (`[mod-log] {processing_id}`). Duplicate retries are no-ops.
- **Polling.** 60s interval; webhooks deferred (Discourse self-hosted webhook config unconfirmed).
- **Rate limits.** Discourse default 60 RPM authenticated; load ~5 RPM avg, ~30 peak.
- **VIP hot-reload.** Live query at 1.3, no cache; additions take effect immediately.

---

### Monitoring

- **Per-case event:** processing_id, latency (1.1 → 1.7), violation_type, confidence, action, escalation_reason
- **Daily aggregation:** case count, autonomous count, escalation count by reason, avg confidence by violation_type, p50 / p95 latency
- **Surface:** Discourse admin page or Google Sheet (whichever Tom prefers — choose at Wave 1 setup)
- **Alerts:** HITL rate > 20% over rolling 24h → Discord webhook to Tom (calibration signal). Discourse API failures (any) → Discord #ops.

---

## Agent 2 — Moderation Context Assembly Agent (Wave 2)

```
Agent Name: MiniBase Context Assembly Agent
Job to be Done: Assemble structured case dossiers for grey-zone review (WS2)
                and appeal review (WS3); write WS2 decision logs in the
                shared schema (Cluster 4 / task 2.7).

Covers: CLM tasks 2.1–2.4 (Cluster 2), 2.7 (Cluster 4), 3.1–3.2 (Cluster 5a).

Delegation archetype: Agent-led + Human Oversight (assembly + logging);
                      Human-led + Agent Support (decision and ruling — out of scope).

Dossier output (per case):
  - Post text + flag metadata
  - Sub-forum norm applicable (if structured; flagged "missing" if not)
  - VIP account status (Wave 1 service, reused)
  - Thread context: OP intent, prior replies, thread type
  - Account history: prior flags, prior dispositions
  - For appeals (WS3): original decision log, rationale, moderator ID

Wave 2 prerequisites:
  - Sub-forum norm table structured for all 14 sub-forums (currently 3) [P0]
  - WS2 minimum log quality standard defined [P1]
  - DSM Cluster 4 dependency ("agent has access to Cluster 2 context at logging
    time") is structurally satisfied: Agent 2 covers both clusters in one
    execution path; in-context state carries from assembly to logging.
```

---

## Compounding Roadmap

| Wave | Agent | New build | Reuses from prior wave | Effort recovered |
|---|---|---|---|---|
| 1 — Foundation (self-funding) | Routine Moderation | Discourse client, VIP service, policy RAG, log schema, mod-review-queue, dead-letter store | — | ~7.2 hrs/day (80% of WS1) |
| 2 — Compounding | Context Assembly | Sub-forum norm data store; addresses thin-log cascade by writing WS2 logs to shared schema | All Wave 1 assets | Partial WS2 + WS3-5a effort |
| 3 — Multi-agent workflow | Routine + Context Assembly composed via intake router | Decision log vector index (cross-case precedent retrieval) | All Wave 1 + 2 assets | Reduced grey-zone handling time |

### Integration reuse matrix

| Asset | Agent 1 (Wave 1) | Agent 2 (Wave 2) | Wave 3 |
|---|---|---|---|
| Discourse read API | Build | Reuse | Reuse |
| Discourse write API | Build | Reuse | Reuse |
| VIP controlled-list service | Build | Reuse | Reuse |
| Policy RAG pipeline | Build (global only) | Reuse + extend (sub-forum norms) | Reuse |
| Structured log schema | Build (write) | Reuse (read + write — Agent 2 also logs WS2 decisions) | Reuse |
| Sub-forum norm data store | — | Build | Reuse |
| Mod review queue | Build | Reuse | Reuse |
| Decision log vector index | — | — | Build |

---

## Open Deployment Blockers

| Blocker | Agent | Priority | Owner |
|---|---|---|---|
| VIP controlled-list service does not exist | Agent 1 | P0 launch | Engineering + Tom |
| Discourse write API auth scope unconfirmed | Agent 1 | P0 launch | Engineering |
| Gallery posts intake path: Discourse queue or separate? | Agent 1 | P0 — promoted from gap | Engineering + Tom |
| Confidence thresholds uncalibrated (provisional: 0.6 / 0.8 action gate; 0.15 multi-label delta; 0.4 multi-label class confidence floor; 0.35 policy RAG relevance) | Agent 1 | P1 — tune in mock testing | ML/ops + Tom |
| Tom-validated few-shot examples | Agent 1 | P1 — affects accuracy | Tom + Senior Moderator |
| Sub-forum norm table: 11 of 14 undocumented | Agent 2 | P0 — Wave 2 launch | Tom + Senior Moderator |
| WS2 minimum log quality standard | Agent 2 | P1 — Wave 2 quality | Tom |
