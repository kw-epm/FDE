# Cognitive Load Map
**Scenario 4 — Community Content Moderation (MiniBase)**
**Date:** 2026-04-30
**Source:** Brief artefacts 4.1–4.3, founder brief, tooling sketch, elicitation log (01_elicitation_log.md)

> **Epistemic status:** All claims grounded in brief or labeled [Inferred]. Dimension scores marked [Derived] where calculated, not confirmed by stakeholder.

---

## Dimension Scoring Key

H = high delegation suitability / L = low delegation suitability

Traceability convention used throughout this file:
- `[Stated]` = directly present in scenario artefacts/brief
- `[Inferred]` = reasoned hypothesis from evidence
- `[Derived]` = computed/analytical value (not stakeholder-confirmed)

| Dimension | H (high suitability) | L (low suitability) |
|---|---|---|
| **Cognitive Load** | Low effort; routine | High reasoning; tacit knowledge |
| **Input Structure** | Structured, machine-readable | Unstructured, ambiguous |
| **Determinism** | Clear rules, predictable output | Judgment-dependent, contextual |
| **Exception Rate** | Rare, predictable | Frequent, unpredictable |
| **Turn-Taking** | Minimal back-and-forth | Heavy multi-party interaction |
| **Latency** | Async/batch acceptable | Real-time required |
| **Risk** | Reversible, low consequence | Irreversible, high consequence |
| **Tool/API** | Available and accessible | Unavailable, manual, or inaccessible |

---

## Lived Process Narrative (Traceable)

**Documented process:** Volunteers receive flagged content, apply the 14-page global policy, log decisions in Discourse.

**What actually happens:**

1. **Sub-forum norms override global policy** in at least 3 of 14 sub-forums (painters, historical, Japanese painters). Volunteers rely on memory/prior guidance, not an accessible system source. `[Stated: artefact 4.3]`

2. **Deliberation happens in Discord before Discourse.** Discourse is post-hoc logging; decision reasoning is primarily external to system-of-record. `[Stated: artefact 4.2]`

3. **VIP account rules are not volunteer-visible.** Tom's tracker for @vortex_minis, @sculpturedragon, @vintage_kitbasher is shared only with the Senior Moderator. `[Stated: artefact 4.3]`

4. **Norm propagation appears verbal, not formalized.** Tom's prior guidance influences behavior without corresponding policy updates in artefacts. `[Stated: artefact 4.2; Inferred: propagation mechanism]`

5. **IP claims are off-system.** Intake is email-based with no explicit ticket/case-management flow. `[Stated: tooling sketch]`

---

## Work Stream 1 — Routine Spam / Clear-Violation Removal

**Volume:** ~1,080/day | **Handling time:** ~30 sec/case | **Team effort:** ~9 hrs/day (19%)
[Stated: brief]

**Job to be Done:** Identify and remove content that clearly violates platform rules without requiring policy judgment.

### Micro-task Table

| # | Micro-task | Type | Cog Load | Input Struct | Determinism | Exception Rate | Turn-Taking | Latency | Risk | Tool/API |
|---|---|---|---|---|---|---|---|---|---|---|
| 1.1 | Receive queue item (flag / auto-detect / sample) | Retrieval | H | H | H | H | H | H | H | H |
| 1.2 | Read post; classify violation type (spam / off-topic / miscategorised) | Reasoning | H | M | H | M | H | H | H | H |
| 1.3 | Check VIP account status | Retrieval | H | M | H | H | H | H | L | L |
| 1.4 | Apply action (remove / warn / dismiss flag) | Action | H | H | H | H | H | H | M | H |
| 1.5 | Log decision in Discourse | Generation | H | H | H | H | H | H | H | H |

[Derived: dimension scores from brief content, artefact 4.3, tooling sketch]

**Critical note on 1.3:** Tool/API = L and Risk = L because VIP list lookup is not available to volunteers. This is a structural control gap, not a training gap. `[Stated: artefact 4.3; Inferred: control-gap classification]`

### Cognitive Zones

| Zone | Tasks | Character |
|---|---|---|
| **Z1-INTAKE** | 1.1 | Automated → human handoff; deterministic |
| **Z2-CLASSIFY** | 1.2 | Low-effort pattern recognition for clear violations |
| **Z3-ACCOUNT CHECK** | 1.3 | Conceptually simple; structurally broken (VIP lookup unavailable) |
| **Z4-ACTION** | 1.4 | Deterministic once classification confirmed |
| **Z5-LOG** | 1.5 | Routine documentation |

### Breakpoints

| Breakpoint | Trigger | Current path | Gap |
|---|---|---|---|
| **BP1.A** Queue → Volunteer | Automated flag or moderator sample fires | Item enters volunteer queue | No VIP pre-filter before volunteer sees it |
| **BP1.B** Clear → Borderline | Post reads as borderline during 1.2 | Re-routes to WS2 (grey-zone) | No formal re-route mechanism; relies on volunteer judgment |
| **BP1.C** VIP miss | Post is from VIP account; volunteer unaware | Action applied without Tom review | Missing: VIP lookup at intake |

---

## Work Stream 2 — Grey-Zone Case Review

**Volume:** ~360/day | **Handling time:** ~5 min/case | **Team effort:** ~30 hrs/day (64%)
[Stated: brief]

**Job to be Done:** Evaluate reported content at the edge of policy, applying sub-forum context and community norms to reach a defensible moderation decision.

### Micro-task Table

| # | Micro-task | Type | Cog Load | Input Struct | Determinism | Exception Rate | Turn-Taking | Latency | Risk | Tool/API |
|---|---|---|---|---|---|---|---|---|---|---|
| 2.1 | Receive flagged post; read content and flag metadata | Retrieval + Reasoning | M | M | L | L | H | H | M | H |
| 2.2 | Identify sub-forum; retrieve applicable norm | Retrieval | M | M | M | M | H | H | M | L |
| 2.3 | Assemble thread context (thread type, OP intent, prior replies) | Reasoning | M | M | M | M | H | H | M | M |
| 2.4 | Check VIP account status | Retrieval | H | M | H | H | H | H | L | L |
| 2.5 | Colleague consultation via Discord (optional; triggered by borderline confidence) | Reasoning | M | L | L | L | L | M | M | M |
| 2.6 | Make moderation decision (action / no action / escalate) | Decision | L | L | L | L | M | H | M | H |
| 2.7 | Log decision with rationale in Discourse | Generation | M | M | H | H | H | H | M | H |

[Derived: dimension scores from brief, artefacts 4.1–4.3]

**Notes (traceable):**
- **2.2:** Tool/API = L; norms are not in an accessible system source for volunteers. `[Stated: artefact 4.3]`
- **2.4:** Same control gap as 1.3; VIP lookup unavailable at volunteer level. `[Stated: artefact 4.3]`
- **2.5:** Turn-Taking = L and Input Struct = L due to unstructured multi-turn Discord deliberation. `[Stated: artefact 4.2]`
- **2.7:** Thin rationale logs increase downstream appeal reconstruction cost. `[Stated: artefact 4.2; Inferred: downstream cost mechanism]`

### Cognitive Zones

| Zone | Tasks | Character |
|---|---|---|
| **Z1-INTAKE** | 2.1 | Reading and initial framing; semi-structured |
| **Z2-CONTEXT ASSEMBLY** | 2.2, 2.3, 2.4 | **Primary cognitive hotspot.** Three parallel lookups: norm (tacit/inaccessible), thread (readable), VIP status (inaccessible). Quality of 2.6 depends entirely on completeness of this zone. |
| **Z3-DELIBERATION** | 2.5, 2.6 | Judgment zone. Consultation is the norm-transmission mechanism, not an exception path. |
| **Z4-DOCUMENTATION** | 2.7 | Log quality determines WS3 appeal complexity downstream. |

### Breakpoints

| Breakpoint | Trigger | Current path | Gap |
|---|---|---|---|
| **BP2.A** Flag → Queue | User flags (threshold unknown; artefact 4.1 example: 4 reports), automated detection, or moderator sampling `[Inferred: queue-entry threshold not stated in brief]` | Item enters grey-zone review queue | No confidence score or pre-classification before volunteer sees it |
| **BP2.B** Solo → Consultation | Volunteer uncertain after context assembly | Volunteer posts to #mod-decisions Discord | No formal escalation criteria; relies on volunteer self-assessment |
| **BP2.C** Discord → Discourse | Decision reached in Discord | One volunteer logs decision in Discourse | Reasoning in Discord is lost; Discourse log is post-hoc summary only |
| **BP2.D** Volunteer → Tom | VIP account or high-sensitivity case | Implicit; no defined trigger for volunteers | No systematic mechanism; VIP detection gap makes this path invisible |

---

## Work Stream 3 — User Dispute Appeals

**Volume:** ~60/day | **Handling time:** ~8 min/case | **Team effort:** ~8 hrs/day (17%)
[Stated: brief]

**Job to be Done:** Evaluate a user's challenge to a prior moderation action; determine whether the original decision was correct, should be reversed, or requires escalation.

### Micro-task Table

| # | Micro-task | Type | Cog Load | Input Struct | Determinism | Exception Rate | Turn-Taking | Latency | Risk | Tool/API |
|---|---|---|---|---|---|---|---|---|---|---|
| 3.1 | Receive appeal; read appellant's claim | Retrieval | M | M | H | H | H | H | H | H |
| 3.2 | Retrieve original decision and rationale from Discourse | Retrieval | M | M | M | M | H | H | M | M |
| 3.3 | Re-evaluate original content against policy and sub-forum norm | Reasoning | L | L | L | L | M | H | M | M |
| 3.4 | Decide: uphold / reverse / escalate to Tom | Decision | L | L | L | L | M | H | M | H |
| 3.5 | Communicate decision to appellant; log outcome | Generation | M | M | H | H | M | H | M | H |

[Derived: dimension scores from brief and artefact 4.2 log quality observation]

**Notes (traceable):**
- **3.2:** Variable Discourse rationale quality drives context reconstruction effort in appeals. `[Stated: artefact 4.2; Inferred: time-driver mechanism]`
- **3.3:** Same norm-lookup limitation as WS2 due to tacit/non-systematized sub-forum norms. `[Stated: artefact 4.3]`

### Cognitive Zones

| Zone | Tasks | Character |
|---|---|---|
| **Z1-INTAKE** | 3.1 | Low effort; claim receipt |
| **Z2-CONTEXT RECONSTRUCTION** | 3.2 | **Hotspot when original log is thin.** Time cost scales inversely with WS2 log quality. |
| **Z3-RE-EVALUATION** | 3.3, 3.4 | Full policy + norm re-application; same cognitive demands as original WS2 decision |
| **Z4-RESOLUTION** | 3.5 | Communication + documentation |

### Breakpoints

| Breakpoint | Trigger | Current path | Gap |
|---|---|---|---|
| **BP3.A** Original log thin | Rationale field incomplete or absent | Appeals handler must reconstruct from memory or find original moderator | No minimum log quality standard enforced |
| **BP3.B** VIP account appeal | Appeal involves @vortex_minis, @sculpturedragon, or @vintage_kitbasher | Implicit escalation to Tom | Trigger not defined; volunteer may not detect VIP status |
| **BP3.C** Reversal decision | Handler decides to reverse prior action | Action executed; logged | Reversals set precedent; no review step before execution |

---

## Work Stream 4 — IP-Claim Resolution

**Volume:** ~3–5/wk | **Handling time:** ~30 min/case + escalation | **Team effort:** <1% of total
[Stated: brief]

**Job to be Done:** Evaluate an intellectual property claim against user-uploaded content; determine validity and appropriate action, maintaining legal records.

### Micro-task Table

| # | Micro-task | Type | Cog Load | Input Struct | Determinism | Exception Rate | Turn-Taking | Latency | Risk | Tool/API |
|---|---|---|---|---|---|---|---|---|---|---|
| 4.1 | Receive claim via email; read claimant identity and claim | Retrieval | M | M | H | H | H | H | H | M |
| 4.2 | Identify claimant; route to Tom (@sculpturedragon) or standard path | Decision | M | M | H | M | H | H | M | L |
| 4.3 | Locate allegedly infringing content on platform | Retrieval | M | M | H | M | H | H | M | M |
| 4.4 | Assess claim validity (rights-holder, scope of infringement) | Reasoning | L | L | L | L | M | H | L | L |
| 4.5 | Decide action; communicate; maintain legal record | Decision + Action | L | L | L | L | M | H | L | L |

[Derived: dimension scores from brief, artefact 4.3, tooling sketch]

**Notes (traceable):**
- **4.2:** Tool/API = L; routing depends on tracker visibility at intake point. `[Stated: artefact 4.3 + tooling sketch]`
- **4.4/4.5:** Risk = L and Tool/API = L due to legal stakes + email-only handling with no case-management system. `[Stated: tooling sketch; Inferred: suitability implication]`
- Non-named-claimant triage remains P0 gap; 4.4/4.5 scores are conservative pending criteria evidence. `[Stated: elicitation log open gap]`

### Cognitive Zones

| Zone | Tasks | Character |
|---|---|---|
| **Z1-INTAKE + ROUTING** | 4.1, 4.2 | Low effort but routing error risk is high (VIP detection gap) |
| **Z2-CONTENT LOCATION** | 4.3 | Mechanical but cross-system (email claim → platform content) |
| **Z3-VALIDITY ASSESSMENT** | 4.4 | Highest-complexity zone; legal judgment; no tool support |
| **Z4-RESOLUTION + RECORD** | 4.5 | Legal obligation; email-only; no audit trail system |

### Breakpoints

| Breakpoint | Trigger | Current path | Gap |
|---|---|---|---|
| **BP4.A** Email intake → routing | Claim arrives; handler checks identity | Manual check against Tom's tracker (if accessible) | No systematic VIP check at email intake |
| **BP4.B** Standard → Tom (@sculpturedragon) | Claim from @sculpturedragon identified | Routed to Tom personally | Routing depends on handler knowing the rule |
| **BP4.C** Uncertain claim | Validity assessment is inconclusive | Tom holds and gathers more [Inferred: plausible; not stated] | No defined hold state or evidence-request workflow |

---

## Cross-Stream Cognitive Topology

### Shared Zones

| Zone | Appears in | Nature |
|---|---|---|
| **VIP ACCOUNT CHECK** | WS1 (1.3), WS2 (2.4), WS4 (4.2) | Structurally broken in all three streams — same root cause |
| **SUB-FORUM NORM RETRIEVAL** | WS2 (2.2), WS3 (3.3) | Tacit knowledge, no API, no accessible document |
| **DISCORD DELIBERATION** | WS2 (2.5) | Exists only in WS2; absent from WS1, WS3, WS4 |
| **DISCOURSE LOG** | WS1 (1.5), WS2 (2.7), WS3 (3.2, 3.5) | Output quality in WS1/WS2 determines WS3 input quality |

### Cross-Stream Breakpoints

| Breakpoint | Streams | Description |
|---|---|---|
| **BP-X1** WS1 → WS2 | 1→2 | Clear-violation read reclassifies as borderline during 1.2; re-routes to grey-zone queue |
| **BP-X2** WS2 → WS3 | 2→3 | Grey-zone decision generates an appeal; WS2 log quality determines WS3 difficulty |
| **BP-X3** Any → Tom | 1,2,3,4→Tom | Escalation to Tom has no systematic trigger in any stream; all paths are informal |
| **BP-X4** Discord deliberation / Discourse log gap | 2 | Deliberation happens in Discord; only the conclusion enters Discourse — reasoning context is not captured in system of record |

---

## Cognitive Hotspot Summary (Straight to the Point)

| Hotspot | Stream | Why it matters |
|---|---|---|
| **VIP account detection** | WS1, WS2, WS4 | Single structural gap affecting 3 streams; no tool available to volunteers; consequence is existential per founder brief |
| **Sub-forum norm retrieval** | WS2, WS3 | Tacit knowledge with no accessible structured form; 11 of 14 sub-forums undocumented |
| **Discord → Discourse boundary** | WS2 | Reasoning is lost at this boundary; Discourse log is post-hoc; WS3 appeal quality degrades as a result |
| **WS2 context assembly (Z2)** | WS2 | Three parallel lookups (norm, thread, VIP), two of which are structurally broken; this zone determines decision quality for 64% of team effort |
| **WS4 validity assessment** | WS4 | Highest legal risk; lowest tool support; criteria undocumented (P0 gap) |
