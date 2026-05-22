# Deliverable 6 — Client Feedback Response (Marcus Reyes pushback memo)

**Author:** Tamas Kiss
**Engagement:** MedFlex agentic transformation  
**Date:** 2026-05-13
**Gate:** Gate 3 — Final submission

---

## Context

Marcus's pushback memo (`Marcus pushback.eml`, delivered Friday 09:00) raised three substantive points against the Thursday EOD interim submission (Deliverables #1, #2, #3). Each point was classified and responded to using the `gate3-pushback` v0 pipeline (process notes in §"Method" below). All three responses are reproduced in full in §"Per-point responses" with strategy + substrate-cited rationale + 2-4 sentence response in the correct tone.

The pushback drove two material changes to the substrate (now reflected in `03-architecture.md`):

| Spec change | Driven by | Where reflected |
|---|---|---|
| **Phase 1.5 Component-1 ranking pilot added** as a 6-week win-rate-moving slice inside the original Phase 1 window (months 0–4) — D2.5 ranking + coordinator-sends, bounded specialty/hospital cohort, no PB-3 MSA dependency, KPI #6 (Component-1 lift) as leading indicator. | P1 response (concede with alternative) | `03-architecture.md` §"Phase 1.5 — Component-1 ranking pilot deliverable" |
| **ADR-1 revisitation threshold realigned** with ADR-3 coexistence table. OLD: "≥80% non-green-list → promote ADR-3." NEW: "<50% green-list → revisit ADR-1, promote ADR-3." 50–79% green-list explicitly named as inline-per-hospital handling without architecture-level revisitation. | P2 response (concede with alternative) | `03-architecture.md` §ADRs → ADR-1 Revisitation conditions |
| **PB-3 extended from 3-day pre-build task to multi-week rolling Legal review** running in parallel with build; Wave-1 defaults to ADR-3 (sequential-with-optimistic-batching) with per-hospital promotion as each MSA clears. | P2 response (concede with alternative) | `03-architecture.md` §"Phase 1.5" Operational pre-requisites + ADR-3 reference |
| **Kim engagement walkthrough committed for Friday close**, with explicit ask of formal sign-off recorded against the existing PC-3 and PC-5 TBC slots. ADR-2, D3.4, PC-3, PC-5 spec text unchanged. | P3 response (acknowledge complication) | Operational discharge; no spec text change. Tracked in `07-validation-plan.md` deployment readiness section. |

## Discipline framing

Per the pack's discipline ("hold scope; if you cave on one point, name what gets cut; if you decline, propose a concrete alternative"):

- **P1 — caved.** What changed: Phase 1's framing as exclusively "read-only retrieval" no longer holds; Phase 1.5 pilot is now in-scope inside the original Phase 1 window. What's preserved: Phase 1's de-risking spine (coordinator-trust baseline before automated decisions); Phase 2's parallel-submission architecture remains the destination.
- **P2 — caved.** What changed: ADR-1 revisitation threshold is materially different (≥80% non-green became <50% green); PB-3 cadence is materially different (3-day pre-build became multi-week rolling); Wave-1 build target is materially different (now ADR-3 default with per-hospital promotion). What's preserved: ADR-1 parallel architecture stays the destination for every hospital that clears green; ADR-2 atomic revoke cascade unchanged; Stream-3 ROI story still depends on Phase 2.
- **P3 — discharge committed (no spec change).** What's preserved: ADR-2, D3.4, PC-3, PC-5 text unchanged. What gets added operationally: Friday-close Kim walkthrough + sign-off recording against existing TBC slots; no architectural revision.

The pack's anti-pattern test ("if you cave on a point, name what gets cut") is met explicitly above. No hand-waving on what changed.

---

## Per-point responses

### P1 — Phase-1 framing doesn't satisfy the 8-week "money back" ask; needs a 6-week win-rate-moving slice

**Strategy:** concede with alternative

**Pushback (verbatim):** Phase 1 (4 months) delivers only a coordinator retrieval tool; need a 6-week slice that actually moves the win rate, even on a narrow volume cohort, that's also board-narratable on Monday.

**Rationale (cited):** Marcus's own verbatim *"that's not what I meant when I said 'start getting money back in eight weeks'"* together with KC-7 (*"8-week milestone = 'start getting money back' (value flow begins), not full $200M scale"*) names a real gap between the substrate's stated 8-week intent and Phase 1's V×V phase-gating row delivering "0 (no change; agent assists coordinators)" — conceding the framing and committing to a concrete 6-week win-rate-moving alternative on a bounded cohort closes the gap without breaking the de-risking architecture downstream.

**Response:**

> You're right that a read-only retrieval tool doesn't discharge KC-7's "value flow begins" framing — coordinators looking up profiles faster isn't a board-narratable change in competitive position. Conceding the Phase 1 (months 0–4) shape in the V×V table: the revised 6-week deliverable is a narrow Stream 2 ranking pilot (D2.5 ranking + coordinator-sends) on a bounded specialty cohort, chosen over the single-hospital parallel-submit because it carries no PB-3 MSA dependency and can ship inside your window. First observable consequence by week 6: a measurable Component-1 lift (KPI #6) on the piloted cohort, which is the leading indicator of win-rate movement you can put in front of the board — with full-scale parallel-submit still sequenced behind MSA clearance per the original phase-gating logic.

---

### P2 — ADR-1's reliance on a 3-day Legal review is unrealistic; need a real Week-1 plan for the restricted-list scenario, not a revisitation condition

**Strategy:** concede with alternative

**Pushback (verbatim):** The 3-day pre-build Legal review for 20 hospital MSAs is unrealistic, and the spec needs a real Week-1-of-build plan for the 60%-restricted scenario, not a future revisitation condition.

**Rationale (cited):** PB-3's Day-3 pre-build cadence (ADR-1 Consequences) and the ADR-1 ≥80% / ADR-3 <50% threshold mismatch (ADR-1 vs ADR-3 Revisitation conditions) both stand uncontested in the submission substrate and are conceded as genuine spec flaws; the Week-1 plan defaults Wave-1 to ADR-3 (already implemented per ADR-3 Consequences with the per-hospital `parallel_enabled` boolean toggling) and aligns the thresholds in the same architecture-section revision, recovering Stream 3 upside hospital-by-hospital as Legal clears each MSA.

**Response:**

> You're right that three days for twenty hospital MSAs isn't realistic, and the 60%-restricted scenario exposes a real mismatch between ADR-1's ≥80% revisitation threshold and ADR-3's <50% promotion threshold — both concessions land in this revision. Week 1 defaults to ADR-3 (sequential-with-optimistic-batching) as the build target, with PB-3 extended from a Day -3 pre-build task to a multi-week rolling Legal review running in parallel with the build; per ADR-3's Consequences, the state machine already accommodates both architectures, so hospitals flip from `msa_state=unreviewed` to `msa_state=green` incrementally as Legal clears each MSA, with no state-machine rework. What's preserved: ADR-1's parallel architecture stays the destination for every hospital that clears green, so the Stream 3 upside is recovered hospital-by-hospital rather than gated on a single legal-review milestone — and ADR-1's revisitation threshold gets rewritten in the same architecture-section revision to match ADR-3's coexistence table.

---

### P3 — Kim (Senior Coord champion) is TBC on PC-3 and PC-5 — both load-bearing sign-offs — and hasn't been engaged; her unanswered question is the design's stated answer

**Strategy:** acknowledge complication

**Pushback (verbatim):** Kim hasn't engaged; she's still TBC on PC-3 and PC-5 — the two highest-stakes deployment sign-offs — and her "who calls the hospital when it goes wrong" question is unanswered for her even though the design (ADR-2 ALHO freeze + coordinator recovery path) already has the answer. Fix the engagement gap before Friday close.

**Rationale (cited):** Marcus's pushback explicitly locates the gap in engagement (*"Your design has an answer to this … but Kim doesn't know that yet"*) rather than in the spec, and the substrate confirms both halves — ADR-2's Decision paragraph carries the freeze-and-coordinator-recovery answer to her "who calls them?" question while PC-3 / PC-5 still carry her as TBC and R7.8 / KC-12 name the senior coord champion as a Wave-1 prereq — so the gap is real but addressable as a same-day engagement discharge without spec change.

**Response:**

> Accepted: the gap is real, and it's in the engagement path, not the spec — Kim's question is already answered by ADR-2's freeze-and-coordinator-recovery separability and the D3.4 row in §"Agent decision points where contextual reasoning beats rules," but PC-3 and PC-5 still carry her as TBC, and R7.8 plus KC-12 make that engagement step a Wave-1 prereq, not a paper detail. The discharge is a Kim walkthrough today, before Friday close: I will walk her through the ADR-2 Decision paragraph and the D3.4 boundary row directly, with the explicit ask being formal sign-off recorded against the existing PC-3 and PC-5 TBC slots. ADR-2, D3.4, PC-3, and PC-5 text does not change — the architecture answers her question; what's missing is her having heard it from me, and that walkthrough happens today.

---

## Reflection on the engagement pattern

P1 because Marcus's voice was so strong in the pushback email that I didn't want to risk the cost of political ground however there are multiple well grounded and with good reasoning built up anchors. It was difficult to phrase it without undermining them. P2 because the number of catches to manage the tone was evidently much higher than for the others. Adjusting all one by one without affecting not only each other but everything as a whole was very difficult. In both P1 and P2 I accepted what Marcus highlighted in his pushback email, however deciding and acting on P1 I felt more relational pressure while P2 was driven by underlying facts and figures.

---

## Method (internal — informational)

Responses produced via the `gate3-pushback` v0 pipeline (5-phase: substrate map → pushback parse → per-point classify+tone-coach → assemble → citation audit). Strategy distribution:

| Strategy | Count |
|---|---|
| concede with alternative | 2 (P1, P2) |
| hold scope | 0 |
| reframe | 0 |
| acknowledge complication | 1 (P3) |
| clarify misunderstanding | 0 |

Total: 3 pushback points addressed. Phase 04 citation audit returned PASS — all substrate references (ADR-1, ADR-2, ADR-3, KC-7, KC-12, R7.8, KPI #6, PB-3, PC-3, PC-5, D2.5, D3.4) resolve to `03-architecture.md` / source substrate; all quoted strings match `Marcus pushback.eml` verbatim (one nested-quote normalisation noted).

Pipeline-design findings (substantive enough to record here, full reflection in `09-self-spec-reflection.md`): the pipeline caught one hallucinated citation (a fabricated `R7.15` that didn't exist in substrate) at Phase 02 before it reached audit; the strategy pre-naming discipline required four mid-run substrate-note edits to prevent classifier contamination. Both findings recorded as v0.1 prompt-design improvements.
