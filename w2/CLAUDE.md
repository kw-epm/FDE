# CLAUDE.md — MiniBase Community Moderation ATX Assessment
**Scenario 4 | Week 2 FDE Practice | Date: 2026-04-30**

## What this project is

ATX (Agentic Transformation) assessment of MiniBase's community moderation function. Goal: decompose the cognitive work done by 10 moderators (8 volunteers + 2 paid staff), identify what can be delegated to agents, and produce a buildable agent design.

This is a practice exercise. All stakeholder testimony is AI-simulated from brief artefacts. Nothing is confirmed by a real interview.

---

## File inventory

| File | Purpose | Status |
|---|---|---|
| `scenario4.md` | Source brief — MiniBase platform, 4 work streams, tooling sketch, 3 sample artefacts | Reference only; do not edit |
| `01_elicitation_log.md` | Pre-interview brief analysis — AI-proxy reconstruction of Tom (Q1–Q8), confidence rubric, gap register | Complete |
| `02_cognitive_load_map.md` | CLM: 4 work streams decomposed into micro-tasks, cognitive zones, breakpoints. 8-dimension ATX scoring. | Complete |
| `03_delegation_suitability_matrix.md` | DSM: 7 task clusters scored on 7-dimension delegation suitability set. Archetype assignments with rationale. | Complete |
| `04_agent_purpose_document.md` | APD: Agent 1 (WS1 Routine Moderation) full design; Agent 2 (Context Assembly) abbreviated; compounding roadmap. Revised post-build-loop. | Complete |
| `05_volume_value_analysis.md` | ATX scoring: suitability gate, volume × value scores, TCO estimate, sequencing rationale. | Complete |
| `06_discovery_questions.md` | Discovery questions for Main Stakeholder (10 Qs: 7 original + 3 build-design follow-ups). Extracted from 01. | Complete |
| `07_system_data_inventory.md` | System and Data Inventory (Wave 1 + Wave 2 systems, credentials, shared assets, P0 pre-launch checklist). Extracted from 04. | Complete |
| `CLAUDE.md` | This file. | — |
| `build_attempt_1/` | Closed build-loop output: 8 Python modules (`agent/`) + `BUILD_REPORT.md`. Diagnostic artifact, not a deliverable. | Complete |

**7 Gate-2 deliverables:** 02 (CLM), 03 (DSM), 04 (APD), 05 (V×V), 06 (Discovery), 07 (System Inventory), CLAUDE.md.

---

## Epistemic conventions

Every claim in this project is tagged with one of three labels:

| Tag | Meaning |
|---|---|
| `[Stated]` | Present in scenario4.md artefacts or brief |
| `[Inferred]` | Reasoned hypothesis from evidence; confidence level attached |
| `[Derived]` | Calculated value (not stakeholder-confirmed) |

`[Estimated]` is also used in 05 for cost figures with explicit assumption logging. `[Unconfirmed]` flags design choices that depend on stakeholder input not yet obtained.

**Do not add claims without one of these tags.** Unstated claims dressed as facts are the primary failure mode this discipline is designed to prevent.

Confidence levels (used with `[Inferred]`):
- **High** — corroborated by ≥2 independent artefacts; no plausible alternative interpretation
- **Medium** — single artefact; plausible mechanism; alternatives possible
- **Low** — inference only; no direct artefact support

---

## Key design decisions (non-obvious)

Preserve these when editing any artifact:

1. **VIP detection = controlled-list exact-match on Discourse `account_id` (integer)**, not a classifier and not username string. Sponsor-incident risk is existential; classifiers miss novel/aliased usernames.
2. **VIP lookup runs before classification** (APD), reversing the as-is CLM order. Closes breakpoint BP1.C.
3. **Latency is H for every cluster** — hoisted to header note in DSM; not repeated per cluster.
4. **CLM and DSM dimension sets differ in both directions.** CLM has Cognitive Load + Turn-Taking; DSM has Context Complexity. Don't cross-reference scores.
5. **Thin-log cascade:** WS2 log quality (Cluster 4 / task 2.7) drives WS3 appeals difficulty (Cluster 5a / task 3.2).
6. **Sub-forum norms are a structural gap** (11 of 14 undocumented). Tom + Senior Moderator must document; agent can't surface non-existent data.
7. **Discord deliberation is outside the agent's observation window.** Discourse-only integration misses the reasoning layer (CLM BP-X4).
8. **Re-eval-promoted cases get `reeval_promoted: true` log marker** — auditable separately. Without it, the lift-from-[0.6,0.8]-to-≥0.8 cohort is invisible to QA (Week 2 anti-pattern).
9. **VIP service unreachable → fail closed.** All cases escalate to volunteer queue; autonomous action halts until restored.
10. **VIP posts auto-hidden pending Tom's review** `[Unconfirmed: pending Q9 in 06]`. If Tom overrides, four APD locations update together (escalation triggers, 1.3E, action mapping, autonomy matrix).
11. **Policy RAG miss → Tom**, not volunteers. Systemic policy gaps need policy-team handling, not volunteer triage.
12. **`violation_type → action` defaults are schema-enforced**: `spam→remove`, `off_topic→warn|dismiss_flag`, `miscategorised→dismiss_flag`, `no_violation→dismiss_flag`. LLM cannot cross-map.
13. **Three Discourse artifacts required pre-launch:** `#mod-review-queue` category, `#mod-vip-escalation` category, moderation log topic (titles use `[mod-log] {processing_id}` for idempotency lookup). See 07.

---

## What the agent must never do

These are hard constraints, not calibration targets:

- Act on a post from a VIP account without human review
- Process VIP-flagged content without auto-hiding pending Tom's review (current default; subject to change per Q9)
- Apply a confidence below 0.6 and proceed to autonomous action
- Promote a re-eval-cleared case (was [0.6, 0.8], now ≥ 0.8) without setting `reeval_promoted: true` in the log
- Continue autonomous action when the VIP service is unreachable (fail-closed required)
- Cross-map violation_type to action (e.g. emit `remove` for `no_violation`) — schema-enforced
- Process the same `processing_id` twice without idempotency check
- Infer IP triage criteria (WS4 is Human Only; no triage rules documented)
- Route grey-zone *decisions* autonomously (agent assembles context; human decides)
- Log a WS1 action without writing a structured log entry (thin logs degrade WS3)

---

## Open gaps that affect design

| Gap | Affects | Status |
|---|---|---|
| VIP controlled-list service does not exist | Agent 1 launch | P0 blocker |
| Discourse write API auth scope unconfirmed | Agent 1 launch | P0 blocker |
| Gallery posts intake path | Agent 1 task 1.1 | P0 blocker |
| Discord webhook to Tom not configured | Agent 1 VIP escalation path | P0 blocker (no destination = silent failure) |
| Three Discourse setup tasks (categories + log topic) | Agent 1 launch | P0 setup |
| Confidence thresholds uncalibrated (0.6/0.8 action gate; 0.15 multi-label delta; 0.4 multi-label class floor; 0.35 RAG relevance) | Agent 1 accuracy | P1 — mock testing |
| Sub-forum norm table: 11/14 undocumented | Agent 2 launch | P0 (Wave 2) |
| WS2 minimum log quality standard undefined | Agent 2 / WS3 | P1 (Wave 2) |
| IP triage criteria for non-named claimants | WS4 scope | P0 — no delegation until documented |
| 2024 sponsor incident specifics | Risk model calibration | Stakeholder gap (interview Q1) |
| VIP list completeness beyond 3 named | VIP service data | Stakeholder gap (interview Q4); treat 3 as minimum |
| VIP post visibility (auto-hide vs leave-visible vs remove) | Task 1.3E behaviour | Stakeholder gap (interview Q9b) |

---

## What not to fabricate

- IP triage criteria beyond what artefact 4.3 states (only `@sculpturedragon` and `@vintage_kitbasher` routing)
- VIP accounts beyond the 3 named in artefact 4.3 (treat as minimum, not closed list)
- Sub-forum norms for any of the 11 undocumented sub-forums
- Details of the 2024 sponsor incident (not in brief)
- Handling-time breakdowns within a work stream (e.g. context-assembly fraction of 5 min/case is `[Inferred]`)
- Stakeholder confirmations on any of the `[Unconfirmed]`-flagged design choices in the APD

---

## Reviewer orientation

If you are reviewing this submission:
- The CLM covers all 4 work streams with full micro-task tables, cognitive zones, breakpoints
- The DSM splits WS2 into 3 sub-clusters and WS3 into 2 sub-clusters (7 clusters total); no cluster is Fully Agentic
- The primary agent (WS1) is Agent-led + Human Oversight, not Fully Agentic — VIP detection gap is the key blocker
- IP claims are Human Only on evidence (no triage criteria, legal risk, no audit infrastructure), not conservatism
- All cost figures in 05 are estimates; the primary value argument is capacity recovery, not cash savings
- The build loop has been run; `build_attempt_1/BUILD_REPORT.md` is the diagnostic record. The APD has been revised based on its findings (look for `reeval_promoted`, fail-closed VIP service, policy_gap → Tom, multi-label refinement, default action mapping table).
- Discovery questions (06) include 3 build-loop-surfaced questions (Q8–Q10) on top of the 7 original Tom-interview questions.
