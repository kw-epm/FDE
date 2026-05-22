# Deliverable #3 — Peer Review Portfolio

**Reviewer:** Krzysztof Wilniewczyc, FDE
**Date:** 2026-05-19
**Peers reviewed:** Pavel Klimasheuski (MedFlex intake + matching specs); Tamas Kiss (shared glossary + parallel-submit + classification specs)

This portfolio bundles both peer reviews completed Tuesday Week 4. Each review is preserved verbatim as authored on 2026-05-19; per the principle of frozen evidence, neither has been patched after the build-loop reflection (Deliverable #7) was authored. Any findings I missed at peer-review time, or any false-positive findings I raised, are surfaced honestly in D#7 — not back-edited into this portfolio.

The original per-reviewer files (`03a-peer-review-Pavel-Klimasheuski.md` and `03b-peer-review-Tamas-Kiss.md`) are kept alongside as timestamped working copies. This file is the canonical submission portfolio.

---

## Review 1 — Pavel Klimasheuski

**Files reviewed:** `04a-capability-spec-intake.md`, `04b-capability-spec-matching.md`
**Reviewer:** Krzysztof Wilniewczyc
**Date:** 2026-05-19

### Verdict

Buildable with fixes. A builder can clone this and start today. A few bugs would break the system before the first real shift hits production.

### Triage

| Bucket | Count | What |
|---|---|---|
| Blocker | 2 | UTC date treatment; two different proximity formulas |
| Concern | 4 | Confidence formula has three versions; null-time request reaches Agent 2; `OTHER` enum value; shared cost limit has no shared counter |
| Acceptable difference | — | Two-agent split (parse vs. match); Haiku for parsing and Sonnet for matching |
| Missing | 1 | CRITICAL urgency has a longer coordinator deadline than normal urgency |

### Issues

**1. `shift_date` is "UTC date" but MedFlex covers 5 US states. [Blocker]**
04a §"Core entity: ShiftRequest" — *"shift_date | date (ISO 8601 YYYY-MM-DD) | UTC date"*. A night shift on January 20 means different absolute hours in New York and Los Angeles. Agent 2's overlap check in 04b will compare windows in the wrong frame.
*Fix:* Store `shift_date_local` together with `hospital_timezone`. Convert to UTC inside Agent 2, only when comparing windows.

**2. Two different proximity formulas. [Blocker]**
04b §"SoftFactorScores" says linear interpolation from 10 to 100 **miles**. 04b §"Haversine implementation" says `1.0 / (1.0 + distance_km / 20.0)`. One uses miles, the other uses kilometres. The curves are not the same shape either.
*Fix:* Pick one formula, one unit. Remove the other.

**3. Confidence formula appears in three versions. [Concern]**
04a §"Confidence scoring model" body says *"weighted minimum of component scores"*. The line below it is `confidence_score = sum(component_score × weight)`. The system prompt at the end of 04a uses a third version with 1.0 / 0.5 / 0.0 buckets per component. All three live in the same file.
*Fix:* Keep the weighted sum. Delete the "minimum" wording. Rewrite the prompt so the bucket logic matches the body formula.

**4. EC-5 routes a null-time request to Agent 2. [Concern]**
04a edge case EC-5 sets `shift_start_time = null`, `shift_end_time = null`, confidence 0.65–0.84, status `PENDING_MATCH`. Agent 2's hard availability check in 04b needs both times to compute the overlap window. The spec is silent on what Agent 2 does with nulls. The likely result is silent zero-eligible, which looks the same as a real no-match.
*Fix:* Either route null-time requests to `CLARIFICATION_NEEDED` in 04a, or add an explicit Agent 2 rule for null times.

**5. `OverrideReasonCategory` enum contains `OTHER`. [Concern]**
04b §"MatchingResult" lists `OTHER` as a valid enum value. The production-spec checklist requires enums to be exhaustive with no "other" category.
*Fix:* Replace `OTHER` with one or two specific reasons, e.g. `RELATIONSHIP_RISK`, `DATA_QUALITY_ISSUE`.

**6. Shared `$50` cost limit, no shared counter. [Concern]**
Both Agent 1 and Agent 2 read `DAILY_LLM_COST_LIMIT_USD = 50` and call it "shared limit with Agent 1". Two separate processes cannot enforce one shared limit without a shared store. The spec does not name the store.
*Fix:* Name the storage. A single `daily_cost_counter` row in PostgreSQL with `UPDATE ... RETURNING` for atomic increments is enough.

**7. CRITICAL urgency has the longer coordinator deadline. [Missing]**
04b sets `OVERRIDE_WINDOW_MINUTES = 10` (auto-submit path) and `CRITICAL_REVIEW_TIMEOUT_MINUTES = 15` (coordinator review path for CRITICAL urgency). A CRITICAL shift starts within 24 hours. The longer wait belongs on the calmer path.
*Fix:* Swap the defaults. CRITICAL review timeout = 5 min. Standard = 15 min.

### Strengths worth keeping

Build context with mock fallback (`SERVICENOW_BASE_URL=mock`, `MEDFLEX_API_BASE_URL=mock`) makes the spec runnable in 10 minutes without any external system — this is exactly what Deliverable #7 needs. The FM-2 fallback (algorithmic ranking when the LLM fails) is a real failure mode with a real recovery, not a sentence pretending to be one. The ADR-1 revisitation logging (`proposed_nurse_id`, `submitted_nurse_id`, `fill_outcome`, `submission_path`) is captured from day one — without those four fields, the four-week accuracy review cannot happen.

---

## Review 2 — Tamas Kiss

**Files reviewed:** `04-shared-glossary.md`, `04a-capability-spec-parallel-submit.md`, `04b-capability-spec-classification.md`
**Reviewer:** Krzysztof Wilniewczyc
**Date:** 2026-05-19

### Verdict

Not buildable from this package alone. The thinking behind the design is strong. A builder who has only these three files cannot start without inventing too many missing pieces.

### Triage

| Bucket | Count | What |
|---|---|---|
| Blocker | 3 | Spec depends on files not in the package; 04b has no LLM contract; submission engine has no integration contracts |
| Concern | 2 | Confidence is a plain arithmetic mean of six fields; T2 tier behaviour contradicts the ALHO archetype |
| Acceptable difference | — | Shared glossary as a separate file; 11-state machine covers ADR-1 and ADR-3 via one boolean |
| Missing | 1 | SMS holding signal has no failure mode |

### Issues

**1. Spec depends on files not in the submission. [Blocker]**
04a and 04b repeatedly cite `output/submit/05-agent-purpose.md` §3b, `03-delegation-matrix.md` §3, `output/submit/adr.md`, `assumptions-log.md`, `06-client-feedback.md`, `07-validation-plan.md`. Many short codes ride on top of those references: GR-13, PB-3, PB-6, C-CA1, C-CA5, R3, R7.18, Phase 10 R1, Hartwood B-1, A4-F1. A reader who only has the Gate-3 folder cannot resolve the rule that each code carries.
*Fix:* Inline the rule itself wherever a citation appears. Where a citation is unavoidable, add an "External references" appendix and copy the rule body into it.

**2. 04b has no LLM contract. [Blocker]**
04b describes the classifier as `extract_fields(text, schema=credential_taxonomy)` and the inbound-event classifier as `LLM_classify(event, prompt="Classify as confirm | ack | reject; return confidence")`. There is no output schema, no model choice, no token budget, no timeout, no retry policy, and no rule for what to do when the LLM returns invalid output.
*Fix:* Add an "LLM contract" section. Name a model. Define the JSON output as a fixed schema. Specify timeout (e.g. 15s), retry (one retry), and the fallback path when the output fails schema validation.

**3. The submission engine has no integration contracts. [Blocker]**
04a calls verbs like `send via request.hospital.preferred_channel`, `send_holding_signal_sms(...)`, and `wait_for_revoke_acks(timeout=60s, retries=2)`. No SMTP server, no portal endpoint, no SMS provider, no authentication, no payload format, no rate limit.
*Fix:* Add one integration contract per channel (Email, Hospital Portal, SMS). Each must include endpoint, authentication source, request body, success and error responses, timeout, and retry rule.

**4. Confidence aggregation is a plain mean of six fields. [Concern]**
04b §"Behaviour rules" sets `classification_confidence = mean(per_field_confidences)`. Six fields, six equal weights. A wrong `count` field (say 0.20) gets washed out by five strong fields and the ticket still passes T2. Assumption A1.2 flags the risk; the design ships the unweighted mean anyway.
*Fix:* Either weight the fields (e.g. `count` and `start_at` heavier than `unit`) or cap the aggregate at the lowest per-field confidence.

**5. T2 tier bypasses the ALHO archetype. [Concern]**
04b §3 describes T2 as *"agent finalises classification; 1-click coordinator ack queued"*, and the flow in §4 calls `downstream_dispatch(classification_record)` immediately. ALHO is supposed to mean the coordinator approves before downstream use. T2 sends downstream without waiting for the ack. The label and the behaviour disagree.
*Fix:* Either change T2 to "wait for coordinator ack, then `downstream_dispatch`", or relabel T2 as Fully Agentic with coordinator visibility (no ack required).

**6. SMS holding signal has no failure mode. [Missing]**
04a §4.1 calls `send_holding_signal_sms(...)` right after the submission is sent. The spec does not say what happens if the SMS gateway is down. Does the submission stand? Is it rolled back? Is the nurse marked as un-notified?
*Fix:* Add an explicit failure rule. Suggested: the submission proceeds; the SMS failure is logged with a retry job; the coordinator dashboard shows a "missing holding signal" flag for that nurse.

### Strengths worth keeping

The shared glossary as its own file is the cleanest example I have seen in the squad — entities defined once, both specs referencing the same source, no parallel divergence. The submission factuality ledger (every claim slot-by-slot exact-matched against the source-of-record before any send) is a strong governance idea — it would catch the hallucinated-field bug that other specs leave to luck. ADR-3 (sequential-with-optimistic-batching) shows real engagement with the legal/MSA risk that Pavel's pair under-weights.
