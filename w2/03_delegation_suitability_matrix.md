# Delegation Suitability Matrix
**Scenario 4 — Community Content Moderation (MiniBase)**
**Date:** 2026-04-30
**Source:** CLM (02_cognitive_load_map.md), elicitation log (01_elicitation_log.md), brief artefacts 4.1–4.3

> **Epistemic status:** Archetype assignments are provisional. They depend on exception-rate data and escalation boundary confirmation not yet available from the brief. Each assignment is accompanied by its evidence basis and the open dependency that would change it.

---

## Suitability Scoring Key

Score each dimension H / M / L where H = high delegation suitability.

| Dimension | H | L |
|---|---|---|
| Input Structure | Structured, machine-readable | Unstructured, ambiguous |
| Decision Determinism | Clear rules, predictable | Judgment-dependent, contextual |
| Tool Coverage | APIs available | Inaccessible or manual |
| Context Complexity | State can be made explicit | Requires institutional knowledge |
| Exception Rate | Rare, predictable | Frequent, unpredictable |
| Latency | Async/batch acceptable | Real-time required |
| Risk/Compliance | Reversible, low consequence | Irreversible, high consequence |

**Archetype definitions:**

| Archetype | Meaning |
|---|---|
| **Fully Agentic** | Agent decides and acts autonomously within defined bounds |
| **Agent-led + Human Oversight** | Agent executes; human reviews or approves high-stakes outputs |
| **Human-led + Agent Support** | Human decides; agent provides synthesis, triage, or recommendation |
| **Human Only** | Agent has no role; tacit knowledge, ethics, or irreversibility rules it out |

> **Dimension note:** This matrix uses the 7-dimension ATX delegation suitability set, distinct from the 8-dimension CLM micro-task set in `02_cognitive_load_map.md` (which includes Cognitive Load and Turn-Taking). **Latency** scores H in every cluster — all four work streams accept async processing — and is omitted from per-cluster tables below.

---

## Task Cluster 1 — Routine Spam / Clear-Violation Removal

**CLM tasks:** 1.1–1.5 | **Volume:** ~1,080/day | **Effort:** 9 hrs/day (19%)

| Dimension | Score | Basis |
|---|---|---|
| Input Structure | H | Post + flag metadata are structured; Discourse API available `[Stated: tooling sketch]` |
| Decision Determinism | H | Clear violations are definitionally pattern-matchable; "obvious spam, off-topic, miscategorised" `[Stated: brief]` |
| Tool Coverage | M | Discourse API available for action and log; VIP lookup has no API (structural gap) `[Stated: artefact 4.3, tooling sketch]` |
| Context Complexity | M | Standard classification requires no institutional knowledge; VIP detection requires hidden tracker `[Stated: artefact 4.3]` |
| Exception Rate | M | Unknown empirically; assumed low for clear-violation stream but borderline reclassifications occur `[Inferred: plausible; not stated; confidence: Medium]` |
| Risk/Compliance | M | False positive (wrong removal) is reversible; false negative on VIP account content is potentially existential `[Stated: founder brief, artefact 4.3]` |

**Suitability profile:** H, H, M, M, M, M — strong on determinism and structure; moderated by VIP gap.

**Provisional archetype: Agent-led + Human Oversight**

**Rationale:** Strong agentic candidate on determinism and volume. Elevated to agent-led + oversight because: (1) VIP detection gap means the agent could act on a VIP account post without triggering the required human review; (2) exception rate is unconfirmed. Once VIP detection is solved at the system level (controlled-list lookup at intake) and exception rate is validated as low, this cluster is a **fully agentic** candidate.

**Open dependency:** Confirm exception rate empirically (what % of "clear" queue items are reclassified to grey-zone?). Confirm rollback mechanism for false positives. Resolve VIP lookup gap before any autonomous action is enabled.

---

## Task Cluster 2 — Grey-Zone Case Review: Context Assembly

**CLM tasks:** 2.1–2.4 | Sub-zone of WS2 | **Effort share:** `[Inferred]` majority of 5 min/case

| Dimension | Score | Basis |
|---|---|---|
| Input Structure | M | Post text is unstructured; flag metadata and thread structure are accessible via Discourse API `[Stated: tooling sketch]` |
| Decision Determinism | M | Sub-forum identification is deterministic; norm application is context-dependent `[Stated: artefacts 4.2, 4.3]` |
| Tool Coverage | L | Sub-forum norms not in any API-accessible system; VIP lookup not available to volunteers `[Stated: artefact 4.3]` |
| Context Complexity | L | Requires sub-forum-specific tacit knowledge; 11 of 14 sub-forum norms undocumented `[Stated: artefact 4.3; Derived: 14-3 coverage gap]` |
| Exception Rate | L | Grey-zone stream is defined by borderline edge cases `[Stated: brief — "genuine grey zones"]` |
| Risk/Compliance | M | Wrong context assembly leads to wrong decision; consequence depends on account type `[Inferred: causal chain; confidence: Medium]` |

**Suitability profile:** M, M, L, L, L, M — context and tool gaps dominate.

**Provisional archetype: Human-led + Agent Support**

**Rationale:** The agent cannot autonomously assemble complete context because two of three lookups (sub-forum norm, VIP status) are structurally inaccessible. The agent can support by: (a) retrieving readable thread context and account metadata via Discourse API; (b) flagging known sub-forum norms where documented; (c) surfacing VIP account matches if a structured lookup is built. This archetype holds until sub-forum norms are structured and VIP lookup is solved.

**Open dependency:** Sub-forum norm table must be built as structured data before agent support scope can expand. VIP lookup must be system-level (not volunteer-accessible document) before agent can flag it reliably.

---

## Task Cluster 3 — Grey-Zone Case Review: Decision

**CLM tasks:** 2.5–2.6 | Sub-zone of WS2

| Dimension | Score | Basis |
|---|---|---|
| Input Structure | L | All decision inputs are unstructured (post text, thread context, norm interpretation) `[Stated: artefacts 4.1, 4.2]` |
| Decision Determinism | L | Grey-zone is defined by the absence of deterministic rules; judgment is the product `[Stated: brief]` |
| Tool Coverage | M | Discourse action API available; decision reasoning has no tool support `[Stated: tooling sketch]` |
| Context Complexity | L | Requires sub-forum norms, account history, thread intent — all partially tacit `[Stated: artefacts 4.2, 4.3]` |
| Exception Rate | L | By definition: this is the exception stream `[Stated: brief]` |
| Risk/Compliance | M | Removals are reversible; incorrect decisions generate appeals; VIP account misstep is high-consequence `[Stated: founder brief, artefact 4.3]` |

**Suitability profile:** L, L, M, L, L, M — low determinism and context complexity dominate.

**Provisional archetype: Human-led + Agent Support**

**Rationale:** The decision itself is not delegatable with current evidence. Grey-zone is grey precisely because no rule resolves it. The agent's role here is recommendation and evidence synthesis — surfacing the relevant norm, flagging similar prior decisions, and presenting the assembled context — not making the call. Founder's asymmetric-error principle (false negative cost >> false positive cost) reinforces keeping human accountability on the final decision.

**Open dependency:** If exception rate and confidence threshold data become available from real decision logs, a subset of "high-confidence grey-zone" cases may be promotable to agent-led. Not assumable from brief alone.

---

## Task Cluster 4 — Grey-Zone Documentation

**CLM tasks:** 2.7

| Dimension | Score | Basis |
|---|---|---|
| Input Structure | M | Structured action + free-text rationale field `[Stated: artefact 4.2 log format]` |
| Decision Determinism | H | Logging what was decided is deterministic `[Derived]` |
| Tool Coverage | H | Discourse API supports log writes `[Stated: tooling sketch]` |
| Context Complexity | L | Rationale must reflect reasoning that happened in Discord — context the agent may not have seen `[Stated: artefact 4.2; Inferred: context-loss implication]` |
| Exception Rate | H | Rare exceptions in the logging step itself `[Derived]` |
| Risk/Compliance | M | Thin logs degrade WS3 appeal quality; minimum quality standard does not currently exist `[Stated: artefact 4.2; Inferred: downstream impact]` |

**Suitability profile:** M, H, H, L, H, M — strong except for context gap.

**Provisional archetype: Agent-led + Human Oversight**

**Rationale:** The mechanical logging action is highly delegatable. The agent can write a structured log entry from the decision output. The context-complexity gap (Discord reasoning not captured) means the agent's log will be based on the decision alone, not the reasoning — which is exactly the thin-log problem already present in the human process.

**Open dependency:** Define minimum log quality standard (required fields). Confirm whether agent has access to the context assembled in Cluster 2 at logging time.

---

## Task Cluster 5a — User Dispute Appeals: Context Assembly

**CLM tasks:** 3.1–3.2 | **Volume:** ~60/day | **Effort:** share of 8 hrs/day (17%)

| Dimension | Score | Basis |
|---|---|---|
| Input Structure | M | Appeal text is unstructured; original Discourse log is semi-structured `[Stated: artefact 4.2 log format]` |
| Decision Determinism | M | Retrieval of original decision is deterministic; quality of what is retrieved varies `[Stated: artefact 4.2; Inferred: quality-variance mechanism]` |
| Tool Coverage | M | Discourse API supports retrieval; Discord reasoning not captured in any API `[Stated: tooling sketch, artefact 4.2]` |
| Context Complexity | M | Reconstruction is mostly document-based; fails when original log is thin `[Stated: artefact 4.2; Inferred: failure mode]` |
| Exception Rate | M | Reconstruction fails when log quality is low — a known failure mode; frequency unknown from brief `[Inferred: confidence: Medium]` |
| Risk/Compliance | M | Context errors propagate into wrong re-evaluation; correctable if caught `[Inferred: confidence: Medium]` |

**Suitability profile:** M, M, M, M, M, M — uniformly moderate; no hard blockers.

**Provisional archetype: Agent-led + Human Oversight**

**Rationale:** Context assembly is primarily retrieval and formatting — structured enough for agent-led execution. The agent retrieves the original decision, surfaces the sub-forum norm (if structured), flags VIP account status, and presents the dossier. Human oversight is needed because log quality is variable and thin logs produce incomplete dossiers. Agent-led is defensible here in a way it is not for the decision itself.

**Open dependency:** Quality depends on WS2 log quality. If logs are thin (current state), agent dossiers will be thin. Improving WS2 documentation (Cluster 4) directly improves this cluster.

---

## Task Cluster 5b — User Dispute Appeals: Final Ruling

**CLM tasks:** 3.3–3.5 | **Volume:** ~60/day | **Effort:** share of 8 hrs/day (17%)

| Dimension | Score | Basis |
|---|---|---|
| Input Structure | L | All ruling inputs are unstructured; norm re-application requires tacit knowledge `[Stated: artefact 4.3]` |
| Decision Determinism | L | Re-evaluation requires same judgment as original decision, plus appellant's claim assessment `[Inferred: causal; confidence: High]` |
| Tool Coverage | M | Discourse action API available; reasoning has no tool support `[Stated: tooling sketch]` |
| Context Complexity | L | Sub-forum norm, account history, appellant intent — all partly tacit `[Stated: artefacts 4.2, 4.3]` |
| Exception Rate | L | Appeals are by definition exception cases `[Stated: brief]` |
| Risk/Compliance | M | Reversals set precedent; VIP account appeals are high-consequence `[Inferred: precedent mechanism; confidence: Medium]` |

**Suitability profile:** L, L, M, L, L, M — same profile as grey-zone decision.

**Provisional archetype: Human-led + Agent Support**

**Rationale:** Decision accountability must remain human. The final ruling involves the same judgment demands as the original grey-zone decision — low determinism, tacit norms, contextual risk. Agent supports by surfacing the assembled dossier from Cluster 5a; human makes the call.

**Open dependency:** Same as Cluster 3 (grey-zone decision) — if high-confidence sub-cases can be identified empirically, a subset may be promotable. Not assumable from brief.

---

## Task Cluster 6 — IP-Claim Resolution

**CLM tasks:** 4.1–4.5 | **Volume:** 3–5/wk | **Effort:** <1%

| Dimension | Score | Basis |
|---|---|---|
| Input Structure | M | Email intake; claim content varies; no structured intake form `[Stated: tooling sketch]` |
| Decision Determinism | L | Legal judgment required; triage criteria for non-named claimants undocumented (P0 gap) `[Stated: elicitation log]` |
| Tool Coverage | L | Email only; no case management; VIP routing depends on inaccessible tracker `[Stated: tooling sketch, artefact 4.3]` |
| Context Complexity | L | Rights-holder verification, infringement assessment, legal record — all require specialist judgment `[Inferred: domain standard; confidence: High]` |
| Exception Rate | L | Every claim is materially different; 2 IP-specific named-account routing rules (@sculpturedragon, @vintage_kitbasher) of unknown total claimant population `[Stated: artefact 4.3]` |
| Risk/Compliance | L | Legal liability; irreversible if wrongly acted on; no audit trail system `[Stated: tooling sketch; Inferred: legal risk implication]` |

**Suitability profile:** M, L, L, L, L, L — fails on five dimensions; high legal risk.

**Provisional archetype: Human Only**

**Rationale:** Three hard blockers: (1) triage criteria for non-named claimants are undocumented — no rule set exists to delegate against; (2) legal liability makes wrong decisions irreversible and consequential; (3) tool coverage is email-only with no audit infrastructure. Volume (3–5/wk) is too low to justify building the infrastructure for any agent role here. No agent in Wave 1 or 2. If intake-routing automation becomes attractive later (e.g., as part of a broader email triage system), treat it as a separate use case requiring its own scoring.

**Open dependency:** Triage criteria must be documented before any delegation is considered. Infrastructure (case management, audit trail) must be built. These are prerequisites, not just improvements.

---

## Delegation Archetype Summary

| Task Cluster | Archetype (Provisional) | Primary Blocker to Promotion |
|---|---|---|
| Routine spam / clear-violation | Agent-led + Human Oversight | VIP detection gap; exception rate unconfirmed |
| Grey-zone context assembly | Human-led + Agent Support | Sub-forum norms not structured; VIP lookup missing |
| Grey-zone decision | Human-led + Agent Support | Low determinism; founder asymmetric-error policy |
| Grey-zone documentation | Agent-led + Human Oversight | Minimum log quality standard undefined |
| Appeals: context assembly | Agent-led + Human Oversight | Depends on WS2 log quality; thin logs = thin dossiers |
| Appeals: final ruling | Human-led + Agent Support | Same judgment demands as grey-zone decision |
| IP-claim resolution | Human Only | Triage criteria undocumented; legal risk; no audit infrastructure |

---

## Anti-Pattern Check

> *"If every box in your matrix is agentic, you haven't done the real thinking yet."*

- No cluster is assigned Fully Agentic. Routine spam is the closest candidate but is blocked by the VIP detection gap and unconfirmed exception rate.
- IP claims are Human Only on evidence, not conservatism.
- Grey-zone decision is Human-led not because judgment is hard in principle, but because the specific context (tacit norms, VIP risk, founder policy) makes autonomous action indefensible with current evidence.
- The pattern: agent support is strongest where the task is structured retrieval or mechanical action; human accountability is preserved where the task involves norm interpretation, precedent, or legal consequence.
