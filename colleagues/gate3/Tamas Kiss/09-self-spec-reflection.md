# Deliverable 9 — Self-spec Build-loop Reflection (1 page)

**Author:** Tamas Kiss
**Engagement:** MedFlex agentic transformation  
**Date:** 2026-05-13
**Spec under build:** `04b-capability-spec-classification.md` (Capability 1 — Free-text intake classification, D1.1 + D1.3)
**Build environment:** Claude Code subagent simulating exam-conditions build; scaffold-only output; design walkthrough proceeded. Per pack: "Graded on diagnosis quality, not code correctness."

---



## (a) What was built vs intent

A Python scaffold with `Ticket`/`Classification` dataclasses read from the shared glossary, an `extract_fields` LLM-boundary stub, arithmetic-mean confidence aggregator, channel-penalty handling, and tier-assignment for T2/T3/T4. The `classify_ticket(t, taxonomy, prompt) -> Classification` signature matched the §4 invariant. 

**What did not match my intent:** the build added five fields to `Classification` (`tier`, `language_detected`, `unmatched_tokens`, `clarification_draft`, `sent_by`) that §4/§7/§10 functionally require but the shared glossary does not declare — flagging back to me my own under-specification of the glossary.

## (b) Questions surfaced and refusals

The build surfaced 13 spec-ambiguity questions with quoted citations and 6 hard blockers. The four most consequential:

1. **§4 "AND no boundary violation"** — term not defined in §4, §5, or glossary; build defaulted to a blank predicate, which means §4's invariant makes not too much sence.
2. **Per-field confidence for non-categorical fields** — glossary types `FLOAT[6]`, but spec does not control how an LLM emits confidence for timestamps (`start_at`/`end_at`) or integer (`count`).
3. **EC-1.4 PHONE_MULTIPLIER PENDING_CALIBRATION** — Phase 1 is the build phase; no starting value means EC-1.4 does not compile..
4. **§3 vs §4 Tier T1** — §3 enumerates T1, §4's algorithm never produces it; build silently dropped T1 from `assign_tier`, flagged as unjustified.

## (c) Per-gap diagnosis (5 most build-impactful)

| Gap | Category | Diagnosis |
|---|---|---|
| §4 "boundary violation" undefined | **Spec ambiguity** | §4 invariant has an undefined conjunct; build defaulted to vacuous truth, so §4's safety guarantee is unenforceable. |
| Per-field confidence semantics | **Spec ambiguity** | No contract for LLM confidence on non-categorical fields; `classification_confidence` not reproducible across prompt revisions. |
| EC-1.4 PHONE_MULTIPLIER PENDING_CALIBRATION | **Spec ambiguity** (deferred-calibration anti-pattern) | Spec defers to Phase 1, but Phase 1 IS the build. Same critique Marcus levelled at Phase 1 framing applies at capability level. |
| 500-row eval set schema/location undefined | **Test-environment issue** | Spec mandates accuracy-regression gate, but eval set isn't stood up: row schema, file path, validation procedure all unspecified. |
| `Classification` schema gaps (`tier`, `language_detected`, etc.) | **Unjustified addition** (by me, not builder) | §4/§7/§10 require these fields functionally; glossary doesn't declare them; builder caught itself adding them — diagnosis is mine. |

**Pattern across the diagnosis:** the dominant gap class is the **deferred-calibration anti-pattern** — I wrote PENDING_CALIBRATION, "TBD at deploy time," and "calibrated against eval set at deploy" in three places. Each individually looks reasonable; the pattern is structural. I keep deferring values to a build phase that needs the values to start.

## (d) 30-min spec edits (4 highest-impact)

1. **Define "boundary violation" as a list of machine-checkable predicates in §5** — makes §4's invariant enforceable instead of vacuous.
2. **Add a confidence contract for non-categorical fields to the glossary** — one sentence per field type (LLM self-reported for categorical; parse-success × range-plausibility for timestamps; bounded-range plausibility for integers).
3. **Provide a starting `PHONE_MULTIPLIER` value** confidence-tagged LOW — Phase 1 instrumentation overwrites it. No starting value = no deterministic build.
4. **Pin eval-set row schema and storage path** in §2 — one sentence: `{ticket_body, expected_classification, validated_by, validated_at}` at `eval/v1/intake-classification-500.jsonl`. Without this the §10 accuracy gate is unimplementable.

---

## Honest assessment

The build's "code is not graded — diagnosis is" framing matches my read of the pack. The highest-leverage edit isn't any single spec fix — it's the **deferred-calibration anti-pattern**: I keep using `PENDING_CALIBRATION` as a future commitment, but the build phase IS deploy time. Same critique Marcus made of Phase 1 architecturally (P1 pushback: "not a revisitation condition") applies to my own spec at the capability level. One discipline would have prevented most of these gaps: every value the spec defers carries a starting value, not just a calibration plan.
