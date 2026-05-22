# Deliverable #3a — Peer Review: Pavel Klimasheuski

**Files reviewed:** `04a-capability-spec-intake.md`, `04b-capability-spec-matching.md`
**Reviewer:** Krzysztof Wilniewczyc
**Date:** 2026-05-19

## Verdict

Buildable with fixes. A builder can clone this and start today. A few bugs would break the system before the first real shift hits production.

## Triage

| Bucket | Count | What |
|---|---|---|
| Blocker | 2 | UTC date treatment; two different proximity formulas |
| Concern | 4 | Confidence formula has three versions; null-time request reaches Agent 2; `OTHER` enum value; shared cost limit has no shared counter |
| Acceptable difference | — | Two-agent split (parse vs. match); Haiku for parsing and Sonnet for matching |
| Missing | 1 | CRITICAL urgency has a longer coordinator deadline than normal urgency |

## Issues

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

## Strengths worth keeping

Build context with mock fallback (`SERVICENOW_BASE_URL=mock`, `MEDFLEX_API_BASE_URL=mock`) makes the spec runnable in 10 minutes without any external system — this is exactly what Deliverable #7 needs. The FM-2 fallback (algorithmic ranking when the LLM fails) is a real failure mode with a real recovery, not a sentence pretending to be one. The ADR-1 revisitation logging (`proposed_nurse_id`, `submitted_nurse_id`, `fill_outcome`, `submission_path`) is captured from day one — without those four fields, the four-week accuracy review cannot happen.
