# Build Report — Routine Moderation Agent (Wave 1)

**Language chosen:** Python 3.13. Stdlib only. No vector store, no live Discourse, no LLM call. Stubs preserve the integration contracts the APD mandates.

**Time spent:** ~25 minutes (within budget). Three intended modules (`idempotency.py`, `dead_letter.py`, `orchestrator.py`) and this report were blocked by a harness permission issue during the build agent's session. **This report was saved manually after the agent finished. The three runtime modules remain unwritten** — their behavior is documented in §3 below as the diagnostic record. The deliverable is the build-loop diagnosis (which fed APD revisions), not the runnable code.

## 1. Built confidently

All under `/mnt/c/xyh/fde/w2/build_attempt_1/agent/`:

| File | One-liner | APD section |
|---|---|---|
| `__init__.py` | Package marker + scope statement | — |
| `types.py` | `ViolationType`, `Action`, `EscalationReason`, `EscalationQueue` enums; `FlagItem`, `Classification` (with `action == "escalate"` iff `escalation_reason != null` invariant enforced in `__post_init__`), `EscalationDossier`, `LogEntry` with the exact 1.7 schema | Prompt principle 3, Activity Catalog note 1.7 |
| `vip_service.py` | `VipService` Protocol + `StubVipService` with `add()` for hot-reload simulation; lookup keyed on `account_id: int` (not username); placeholder ids called out in comments as not real | 1.3 + 1.3 note, System Inventory P0, Operational Constraints "VIP list hot-reload" |
| `discourse_client.py` | Stub recording every call. All four action-mapping write endpoints, plus `recover`, account-history read, escalation/log topic write, idempotency lookup, QA tag write. `DiscourseApiError` on injected paths for retry tests | Action Mapping table; 1.1, 1.2, 1.5H, 1.6, 1.7, 1.7Q |
| `policy_rag.py` | RAG retriever stub. `STRUCTURED_SUB_FORUMS = {painters, historical, painters-japan}` (3 of 14, per APD). `is_policy_gap()` based on `RELEVANCE_THRESHOLD=0.35` | Memory architecture, Retrieval strategy, "policy RAG miss" trigger |
| `llm_classifier.py` | Real `SYSTEM_PROMPT` translating Prompt principles 1–6 verbatim: VIP rule, JSON-only output, escalate-iff-reason invariant, multi-label rule, low-confidence rule, soft-warn-Japanese-painters rule, artefact 4.1 few-shot tagged `[Unconfirmed: requires Tom-validated examples]`. JSON schema embedded as `CLASSIFICATION_JSON_SCHEMA`. `default_mock_llm` deterministic; tests inject their own. Strict parse via `Classification.__post_init__` | Prompt principles 1–6, Output schema |
| `action_mapping.py` | Pure rule lookup. `map_to_action()`, `needs_hitl_reeval()`, `derive_escalation_reason()`. Thresholds named (0.6, 0.8, 0.15) and `[Unconfirmed]` per APD. Defaults to ESCALATE rather than guessing | 1.5 + 1.5H, Escalation triggers |
| `escalation.py` | Total `route(reason)` mapping each `EscalationReason` to its `EscalationQueue` (Tom / volunteer / ops). Raises on unknown reason — no silent default | Autonomy Matrix routing |

Tests not written — they would exercise the orchestrator/runtime.

## 2. Clarifying questions

1. **`warn` vs `remove` mapping at the rule layer is unspecified.** Spec ambiguity. Three interpretations: classifier picks (a), violation_type defaults (b), or first-time-offender warn-then-remove (c). Picked (a) — the APD's Memory architecture explicitly excludes account history from the high-confidence path, which is the only signal that would distinguish (b) and (c). Category: **Spec Ambiguity** with Design Gap dimension.

2. **HITL re-eval that *lifts* confidence into ≥ 0.8.** Spec says "pass through to 1.6". (a) autonomous after re-eval, (b) marked for async human review, (c) cool-down. Picked (a). Category: **Delegation Boundary Gap** — canonical Week 2 anti-pattern.

3. **What counts as "agent-dismissed" for the 5% QA sample (1.7Q)?** (a) only `DISMISS_FLAG`, (b) every action where the post wasn't removed, (c) any agent-handled disposition. Picked (a). Category: **Spec Ambiguity**.

4. **Policy RAG threshold value undefined.** Used 0.35 placeholder. Category: **Test Problem** — calibration data needed; bundle with the existing P1 confidence-threshold-tuning blocker.

5. **Idempotency lookup data source unspecified.** (a) query the moderation log topic, (b) side-table SQLite, (c) custom field. Picked (a) at the interface boundary. Category: **Design Gap**.

6. **VIP escalation post-visibility expectation.** No SLA, no instruction on whether the post is hidden pending Tom's review. (a) stays visible (Discourse default), (b) hidden pending review, (c) auto-remove + recover on disagreement. Picked (a) by silence — but the founder calls VIP misses existential. Category: **Spec Ambiguity** with **Risk** dimension.

7. **Multi-label trigger semantics for `top2_score_delta`.** (a) absolute delta < 0.15 across top-2, (b) relative ratio, (c) only when both top-2 are violation classes (not `no_violation`). Picked (a). (c) is more useful — a `no_violation`-vs-`spam` 0.5/0.5 tie is low-confidence not multi-label. Category: **Spec Ambiguity**.

## 3. Couldn't build

- `agent/idempotency.py`, `agent/dead_letter.py`, `agent/orchestrator.py`, and this report — every Write call to those filenames was repeatedly denied by the harness during the build agent's session. Modules are pure stdlib Python with no external deps. **Blocker: harness permission, not design.** (Resolved post-session.)
- **Orchestrator behaviour** (preserved here for diagnosis): `_extract` (1.2; assigns processing_id), `_vip_check` (1.3/1.3E short-circuit before classify), `_classify` (1.4 = `policy_rag.retrieve` then `llm_classifier.classify`), honour `Classification.action == ESCALATE` → volunteer queue dossier (1.4E), `needs_hitl_reeval` → fetch account history → re-prompt once → still borderline → escalate (1.5H), `map_to_action` → final action, `_execute` performs Discourse write under `with_retry`; on 3-attempt failure → dead-letter + Discord #ops; `_log_entry` writes 1.7 always, including escalation paths; QA-sample tag at 5% of `DISMISS_FLAG`. Mirrors the Autonomy Matrix; no silent defaults.
- **VIP service real implementation.** APD blocker (P0).
- **Discourse write API auth scope.** APD blocker (P0).
- **Gallery intake path.** APD blocker (P0, promoted from gap).
- **Policy RAG real index.** Per build instructions, no vector DB stand-up.

## 4. Assumptions made

| # | Assumption | Location | Linked CQ |
|---|---|---|---|
| A1 | Classifier picks warn vs remove; rule layer trusts on confidence ≥ 0.8 | `action_mapping.map_to_action` | CQ1 |
| A2 | After HITL re-eval, confidence ≥ 0.8 → autonomous, no further HITL | (orchestrator) | CQ2, §5 |
| A3 | QA sampling on `DISMISS_FLAG` only, not `WARN` | (orchestrator `_log_entry`) | CQ3 |
| A4 | Policy RAG threshold = 0.35 | `policy_rag.RELEVANCE_THRESHOLD` | CQ4 |
| A5 | Idempotency = Discourse single source of truth, no side-table | `discourse_client.has_action_for_processing_id` | CQ5 |
| A6 | VIP placeholder ids `{1001, 1002, 1003}` are explicitly non-real | `vip_service.StubVipService._SEED` | — |
| A7 | Retry: 3 attempts, exp backoff base 0.5s | (runtime) | — |
| A8 | Multi-label trigger uses absolute delta regardless of class | `action_mapping` | CQ7 |
| A9 | `recover` is admin-only, not invoked by the agent | `discourse_client.recover_post` exposed but unused | — |
| A10 | Soft-warn rule for Japanese painters lives in the LLM prompt (Rule 8), not in action mapping | `llm_classifier.SYSTEM_PROMPT` | — |

## 5. Delegation boundary observations

1. **HITL re-eval that lifts confidence ≥ 0.8 has no audit marker.** A case that originated in the HITL band can end up fully-agentic by re-eval, with the human never seeing it unless QA sampling picks it. Exact Week 2 anti-pattern. Fix: post-re-eval autonomous path emits a distinct log marker (e.g. `account_type="standard:reeval-promoted"`) so the cohort is auditable.

2. **Policy RAG miss is routed to volunteers.** Spec routes `policy_gap` to volunteer queue, but policy gaps are *systematic policy missingness*, not case-level grey-zone judgement. Right routing is arguably Tom for policy review.

3. **VIP service unavailable is not addressed.** APD covers a VIP-list miss but not a VIP-service outage. Naive orchestrator lets the lookup raise and the case falls through to classification — wrong default given "never get this wrong". Conservative behaviour: fail-closed — VIP service unreachable → escalate every case to volunteer queue, alert Discord #ops, until recovery.

4. **QA sample distribution silent.** APD specifies 5% rate but not whether selection is uniform random or stratified. Stratified is a calibration multiplier; uniform is easy. Lower-stakes than (1) but same shape.

---

**Files on disk:** `agent/__init__.py`, `agent/types.py`, `agent/vip_service.py`, `agent/discourse_client.py`, `agent/policy_rag.py`, `agent/llm_classifier.py`, `agent/action_mapping.py`, `agent/escalation.py` — all under `/mnt/c/xyh/fde/w2/build_attempt_1/`.

**Diagnosis triage** (input to APD revision):

| Finding | Category | APD revision |
|---|---|---|
| CQ2 / DB1 — HITL re-eval audit marker | Delegation Boundary Gap | **YES — add log marker for re-eval-promoted cases** |
| DB3 — VIP service outage handling | Design Gap | **YES — add fail-closed behaviour to escalation triggers** |
| CQ6 — VIP escalation post-visibility | Spec Ambiguity (high risk) | **YES — specify behaviour at task 1.3E; add to interview Q9** |
| CQ7 — Multi-label semantics with no_violation | Spec Ambiguity | **YES — refine multi-label rule to exclude no_violation** |
| CQ1 — warn vs remove mapping | Spec Ambiguity / Design Gap | **YES — add explicit default mapping table to prompt principles** |
| DB2 — policy_gap routing | Delegation Boundary | **YES — route policy_gap to Tom not volunteers** |
| CQ3 — QA sample scope | Spec Ambiguity | Minor wording fix |
| CQ4 — Policy RAG threshold | Test Problem | Bundle into existing calibration blocker |
| CQ5 — Idempotency source | Design Gap | Minor — specify Discourse as source of truth |
| DB4 — QA distribution | Spec Ambiguity | Minor — specify uniform random in Wave 1 |
