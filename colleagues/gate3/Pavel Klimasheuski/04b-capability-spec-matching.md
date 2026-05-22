# Deliverable #4b — Capability Specification: Nurse Matching Agent
**Engagement:** MedFlex Healthcare Staffing
**Participant:** Pavel Klimasheuski
**Date:** 2026-05-13

> **Shared glossary:** All shared entities — `ShiftRequest`, `ShiftRequestStatus`, `CredentialCategory`, `UnitType`, `Urgency`, `ConfidenceScore`, `AmbiguityFlag` — are defined in Deliverable #4a. This document references them without redefining. Any term not defined here is defined in #4a.

---

## Purpose & scope

The Nurse Matching Agent receives a structured `ShiftRequest` from Agent 1, queries the nurse database and hospital preference data, and produces a ranked list of eligible candidates with confidence scores and reasoning. It is the second stage in the matching pipeline. Its output determines the routing path: auto-submit to Agent 3, coordinator review, or escalation when no viable candidate exists.

**In scope:**
- Hard-constraint filtering of ineligible nurses (credentials, availability, active status, exclusion lists)
- Multi-factor soft ranking of eligible candidates
- Matching confidence scoring for the top candidate
- Routing decision: auto-submit, coordinator review, or escalate (no viable candidates)
- Reasoning generation for coordinator review interface
- Credential expiry proximity warnings and compliance flagging

**Out of scope:**
- Parsing free-text requests (Agent 1)
- Hospital submission or nurse notification (Agent 3)
- Credential verification against state regulatory databases (compliance team)
- Nurse recruitment or roster management

---

## Core entities

### NurseProfile

Read from the nurse database. Agent 2 does not write to this entity.

| Field | Type | Required | Constraints | Notes |
|---|---|---|---|---|
| `nurse_id` | UUID | Yes | Immutable | Primary key |
| `active` | boolean | Yes | — | `false` excludes nurse from all matching; check first |
| `credentials` | list[NurseCredential] | Yes | Min 1 item | See NurseCredential sub-entity |
| `confirmed_schedule` | list[ScheduledShift] | Yes | — | Confirmed future shifts; used for hard availability check |
| `availability_preferences` | list[AvailabilityPreference] | No | — | Self-reported soft preferences; used for soft ranking only |
| `home_location` | object `{lat: decimal, lng: decimal}` | Yes | lat: −90.0 to 90.0; lng: −180.0 to 180.0 | Used for proximity calculation |
| `preferred_hospitals` | list[string] | No | Each is a valid `hospital_id` | Nurse-stated hospital preferences |
| `preferred_unit_types` | list[UnitType] | No | — | Nurse-stated unit type preferences |
| `performance_summary` | NursePerformanceSummary | Yes | — | See NursePerformanceSummary sub-entity |
| `hospital_history` | list[HospitalHistoryEntry] | No | — | Past placements per hospital; used for soft ranking |
| `do_not_send` | list[string] | No | Each is a valid `hospital_id` | Hard exclusion per hospital; cannot be overridden by agent |
| `updated_at` | ISO 8601 timestamp (UTC) | Yes | — | Data freshness indicator; logged per matching run |

> **[ASSUMED]** The NurseProfile schema reflects what Agent 2 requires. Actual database schema must be confirmed with Aaron (IT) before build. If field names differ, the integration contract maps external names to internal names. All field names in this schema are tagged [ASSUMED] pending Aaron confirmation.

### NurseCredential (sub-entity)

| Field | Type | Required | Constraints |
|---|---|---|---|
| `credential_category` | CredentialCategory enum | Yes | Must match shared glossary |
| `expiry_date` | date (ISO 8601 YYYY-MM-DD) | Yes | — |
| `verification_status` | enum [`VERIFIED`, `PENDING_RENEWAL`, `LAPSED`] | Yes | — |

A credential is eligible for hard-constraint matching if and only if `verification_status = VERIFIED` AND `expiry_date > shift_date`.

### ScheduledShift (sub-entity)

Confirmed future shifts that block the nurse's availability.

| Field | Type | Required | Constraints |
|---|---|---|---|
| `shift_id` | UUID | Yes | FK to a filled ShiftRequest |
| `shift_date` | date (ISO 8601 YYYY-MM-DD) | Yes | — |
| `start_time` | time (ISO 8601 HH:MM) | Yes | 24-hour, UTC |
| `end_time` | time (ISO 8601 HH:MM) | Yes | UTC; may be on the following calendar day if shift crosses midnight |

### AvailabilityPreference (sub-entity)

Nurse-stated soft preferences. Used for soft ranking only — does not block matching.

| Field | Type | Required | Constraints |
|---|---|---|---|
| `day_of_week` | enum [`MON`, `TUE`, `WED`, `THU`, `FRI`, `SAT`, `SUN`] | No | Null means any day |
| `preferred_time` | enum [`DAYS`, `NIGHTS`, `EVENINGS`, `ANY`] | Yes | Default `ANY` |

### NursePerformanceSummary (sub-entity)

Pre-computed summary fields. Must be stored in or derivable from the nurse database. [ASSUMED — confirm with Aaron whether these are pre-computed fields or must be derived from raw records at query time. If derived on read, confirm query latency is acceptable at 960 requests/day.]

| Field | Type | Constraints | Derivation |
|---|---|---|---|
| `no_show_rate_12m` | decimal (0.0–1.0) | 2 decimal places | No-shows ÷ total notified shifts in last 12 months |
| `mismatch_rate_12m` | decimal (0.0–1.0) | 2 decimal places | Hospital-flagged mismatches ÷ total filled shifts in last 12 months |
| `total_shifts_12m` | integer | ≥ 0 | Total shifts for which nurse was notified in last 12 months |
| `performance_score` | decimal (0.0–1.0) | Computed, read-only | See formula below |

**Performance score formula:**

`performance_score = (1.0 − no_show_rate_12m) × 0.60 + (1.0 − mismatch_rate_12m) × 0.40`

If `total_shifts_12m < 5`: set `performance_score = 0.50` (insufficient history; neutral score applied). [ASSUMED — minimum sample threshold of 5; configurable via `PERFORMANCE_MIN_SAMPLE`]

### HospitalHistoryEntry (sub-entity)

| Field | Type | Required | Constraints |
|---|---|---|---|
| `hospital_id` | string | Yes | FK to Hospital |
| `shifts_completed` | integer | Yes | ≥ 0 |
| `no_shows_at_hospital` | integer | Yes | ≥ 0 |
| `repeat_requested` | boolean | Yes | `true` if this hospital has explicitly requested this nurse by name for future shifts |
| `last_shift_date` | date (ISO 8601 YYYY-MM-DD) | Yes | Date of most recent completed shift at this hospital |

---

### CandidateRecommendation

Produced by Agent 2. One per ranked nurse in a MatchingResult.

| Field | Type | Required | Constraints | Notes |
|---|---|---|---|---|
| `nurse_id` | UUID | Yes | FK to NurseProfile | — |
| `rank` | integer | Yes | 1-based; unique within a MatchingResult; no gaps | 1 = top candidate |
| `matching_confidence` | decimal (0.0–1.0) or null | Conditional | 2 decimal places; required for `rank = 1`; must be `null` for `rank ≥ 2` | See Confidence Scoring Model |
| `soft_factor_scores` | SoftFactorScores | Yes | See SoftFactorScores sub-entity | — |
| `composite_score` | decimal (0.0–1.0) | Yes | Computed, read-only; weighted sum of soft_factor_scores; 2 decimal places | See formula in SoftFactorScores |
| `adjusted_composite_score` | decimal (0.0–1.0) | Yes | LLM-adjusted score; see LLM output constraints | May differ from composite_score by at most ±0.15 |
| `reasoning_summary` | string | Yes | Max 500 chars | Human-readable for coordinator review interface |
| `warnings` | list[string] | No | Each max 200 chars | E.g., "ICU_CERTIFIED expires 2026-02-15, 12 days after shift" |
| `credential_expiry_alert` | boolean | Yes | Default `false` | `true` if any required credential expires within 30 days of shift_date |

### SoftFactorScores (sub-entity of CandidateRecommendation)

| Field | Type | Weight | Score = 1.0 if | Score = 0.0 if |
|---|---|---|---|---|
| `proximity_score` | decimal (0.0–1.0) | 0.25 | Distance ≤ 10 miles | Distance ≥ 100 miles |
| `hospital_preference_score` | decimal (0.0–1.0) | 0.35 | Hospital has `repeat_requested = true` for this nurse | No prior history at this hospital |
| `nurse_preference_score` | decimal (0.0–1.0) | 0.25 | Hospital in `preferred_hospitals` AND `unit_type` in `preferred_unit_types` | Neither matches AND preferences list is non-empty |
| `performance_score` | decimal (0.0–1.0) | 0.15 | Equals NursePerformanceSummary.performance_score | Equals NursePerformanceSummary.performance_score |

**Composite score formula:**

`composite_score = (proximity × 0.25) + (hospital_preference × 0.35) + (nurse_preference × 0.25) + (performance × 0.15)`

Rounded to 2 decimal places.

All four weights configurable via environment variables: `MATCHING_WEIGHT_PROXIMITY` (default `0.25`), `MATCHING_WEIGHT_HOSPITAL_PREF` (default `0.35`), `MATCHING_WEIGHT_NURSE_PREF` (default `0.25`), `MATCHING_WEIGHT_PERFORMANCE` (default `0.15`). Weights must sum to 1.0; reject configuration that does not.

> **[ASSUMED]** All soft factor weights are initial estimates calibrated against senior coordinator judgment. Must be tuned against ground truth data after the Phase 1 advisory period (see ADR-1 in D3).

**Intermediate score formulas:**

*Proximity score* — linear interpolation:
- `distance ≤ 10 miles`: `proximity_score = 1.0`
- `10 < distance ≤ 100 miles`: `proximity_score = 1.0 − ((distance − 10) / 90)`
- `distance > 100 miles`: `proximity_score = 0.0`
- Distance = straight-line miles between `nurse.home_location` and hospital coordinates. [ASSUMED — hospital coordinates must be stored in hospital profile; confirm with Aaron]

*Hospital preference score*:
- `repeat_requested = true`: score = `1.0`
- `shifts_completed ≥ 3` AND `no_shows_at_hospital = 0`: score = `0.80`
- `shifts_completed ≥ 1` AND `no_shows_at_hospital = 0`: score = `0.60`
- `shifts_completed ≥ 1` AND `no_shows_at_hospital > 0`: score = `0.30`
- No history at this hospital: score = `0.50` (neutral; not penalised for being new)

*Nurse preference score*:
- Hospital in `preferred_hospitals` AND `unit_type` in `preferred_unit_types`: score = `1.0`
- Hospital in `preferred_hospitals` only: score = `0.70`
- `unit_type` in `preferred_unit_types` only: score = `0.50`
- Neither matches (both lists non-empty): score = `0.30`
- Both lists empty (no stated preferences): score = `0.50` (neutral)

---

### MatchingResult

Top-level output produced by Agent 2. Consumed by Agent 3.

| Field | Type | Required | Constraints | Notes |
|---|---|---|---|---|
| `id` | UUID | Yes | Immutable, generated on creation | Primary key |
| `shift_request_id` | UUID | Yes | Immutable; FK to ShiftRequest; unique (one MatchingResult per ShiftRequest) | — |
| `candidates` | list[CandidateRecommendation] | Yes | 0–5 items, ordered by rank ascending | Empty list if `routing_decision = ESCALATE_NO_CANDIDATES` |
| `eligible_candidate_count` | integer | Yes | ≥ 0; count of nurses that passed Phase 1 hard filtering | Logged for audit and thin pool detection |
| `routing_decision` | RoutingDecision enum | Yes | See Routing Decision section | Computed by agent; not set by LLM |
| `override_window_expires_at` | ISO 8601 timestamp (UTC) | Conditional | Required if `routing_decision = AUTO_SUBMIT`; null otherwise | `created_at + OVERRIDE_WINDOW_MINUTES` |
| `status` | MatchingResultStatus enum | Yes | Default `PENDING_ROUTING` | See state machine below |
| `coordinator_id` | string | No | Required if human action triggered status change | FK to coordinator |
| `override_reason_category` | OverrideReasonCategory enum | No | Required if `coordinator_id` is set; cannot be null when coordinator acts | — |
| `selected_candidate_nurse_id` | UUID | No | Required when status transitions to `SUBMITTED` | The nurse actually passed to Agent 3 |
| `routing_rationale` | string | Yes | Max 300 chars; generated by LLM | Surfaced to coordinator in escalation notifications |
| `agent_version` | string | Yes | Semver | Model quality tracking |
| `llm_call_id` | string | Yes | — | Trace ID for LLM call; enables log correlation |
| `created_at` | ISO 8601 timestamp (UTC) | Yes | Immutable | — |
| `updated_at` | ISO 8601 timestamp (UTC) | Yes | Updated on any modification | — |

**RoutingDecision (enum):** `AUTO_SUBMIT`, `COORDINATOR_REVIEW`, `ESCALATE_NO_CANDIDATES`

**MatchingResultStatus state machine:**

```
PENDING_ROUTING      → AWAITING_SUBMISSION   (routing_decision = AUTO_SUBMIT; override window starts)
PENDING_ROUTING      → AWAITING_COORDINATOR  (routing_decision = COORDINATOR_REVIEW)
PENDING_ROUTING      → ESCALATED             (routing_decision = ESCALATE_NO_CANDIDATES)

AWAITING_SUBMISSION  → SUBMITTED             (override window expired; no coordinator action)
AWAITING_SUBMISSION  → OVERRIDDEN            (coordinator acts within override window)

AWAITING_COORDINATOR → SUBMITTED             (coordinator approves top candidate)
AWAITING_COORDINATOR → OVERRIDDEN            (coordinator selects alternative candidate)
AWAITING_COORDINATOR → ESCALATED             (coordinator escalates; no candidate acceptable)

OVERRIDDEN           → SUBMITTED             (after coordinator selects candidate; passed to Agent 3)

SUBMITTED            → [terminal; Agent 3 takes over]
ESCALATED            → [terminal for Agent 2; coordinator handles manually]
```

No backwards transitions. `SUBMITTED` and `ESCALATED` are terminal states for Agent 2.

**OverrideReasonCategory (enum):** `CANDIDATE_UNAVAILABLE`, `BETTER_CANDIDATE_KNOWN`, `HOSPITAL_PREFERENCE_CONFLICT`, `COMPLIANCE_CONCERN`, `COORDINATOR_JUDGMENT`, `OTHER`

---

## Decision logic

### Phase 1 — Hard constraint filtering

Hard constraints are evaluated as boolean pass/fail. A nurse failing any single check is excluded from candidates. Applied in the order listed; excluded nurses are logged with exclusion reason.

| Constraint | Check | Exclusion reason logged |
|---|---|---|
| Active status | `nurse.active == true` | `INACTIVE` |
| Required credentials | For each credential in `ShiftRequest.required_credentials`: nurse must have a `NurseCredential` where `credential_category` matches AND `verification_status = VERIFIED` AND `expiry_date > shift_date` | `CREDENTIAL_MISSING`, `CREDENTIAL_LAPSED`, or `CREDENTIAL_EXPIRED` |
| Confirmed availability | No `ScheduledShift` overlaps the requested shift window (see overlap rule) | `AVAILABILITY_CONFLICT` |
| Do-not-send exclusion | `ShiftRequest.hospital_id` is not in `nurse.do_not_send` | `DO_NOT_SEND` |

**Shift overlap rule:**

Two time windows overlap if: `window_A_start < window_B_end AND window_A_end > window_B_start`

For the availability check:
- `requested_start = shift_date + shift_start_time` (UTC datetime)
- `requested_end = shift_date + shift_end_time` (UTC datetime); if `shift_end_time < shift_start_time` (shift crosses midnight), `requested_end = shift_date + 1 day + shift_end_time`
- Compare against each `ScheduledShift`: `scheduled_start = scheduled.shift_date + scheduled.start_time`; `scheduled_end = scheduled.shift_date + scheduled.end_time` (apply same midnight-crossing rule)

**Credential expiry proximity check (separate from hard filter):**

After Phase 1, for each nurse that passed: if any required credential has `expiry_date ≤ shift_date + 30 days`: set `CandidateRecommendation.credential_expiry_alert = true`; add warning: `"[credential_category] expires [expiry_date], [N] days after shift."`  The nurse remains eligible; the alert is surfaced in the coordinator review interface.

**Compliance flagging (fire-and-forget):**

For any nurse excluded with reason `CREDENTIAL_LAPSED` or `CREDENTIAL_EXPIRED`: if the credential had `verification_status = VERIFIED` within the prior 90 days (detectable if a timestamp-of-last-verification field exists [ASSUMED]): log a compliance event with `nurse_id`, `credential_category`, `expiry_date` to `COMPLIANCE_ALERT_CHANNEL` (configurable env var). This does not block the matching run and does not require a response before proceeding.

---

### Phase 2 — Soft ranking

Applied to all nurses that passed Phase 1.

**Step 1:** Fetch soft ranking data for each eligible nurse. Required: hospital history for `ShiftRequest.hospital_id`, availability preferences, home location, preferred hospitals/unit types, performance summary.

**Step 2:** Compute `composite_score` per nurse using the SoftFactorScores formula. This is a deterministic calculation — no LLM involved at this step.

**Step 3:** If eligible candidate pool exceeds `MAX_LLM_CANDIDATE_INPUT` (default 50): pre-rank by `composite_score` descending; pass top 50 to LLM. Log warning if pool was truncated.

**Step 4:** Pass structured data to LLM. LLM inputs: ShiftRequest fields, list of eligible candidates (nurse_id + pre-computed composite_score + soft_factor_scores + performance_summary + credential_expiry_alert), hospital preferences summary. LLM returns: ranked candidate list (max 5), `adjusted_composite_score` and `matching_confidence` for rank-1, `reasoning_summary` per candidate, `routing_rationale`.

**Step 5:** Validate LLM output schema (see LLM contract). If validation fails: apply FM-2 fallback. Otherwise: set `CandidateRecommendation` fields from LLM output; apply `adjusted_composite_score` constraints (see LLM output constraints).

**Step 6:** Compute `routing_decision` from `matching_confidence` and `eligible_candidate_count` (agent logic, not LLM).

**The LLM does not re-evaluate hard constraints and does not invent nurses.** It receives only nurses that passed Phase 1. Its job is contextual interpretation of soft factors and generation of human-readable reasoning.

---

### Confidence scoring model

`matching_confidence` represents the agent's certainty that the rank-1 candidate is the right match for this shift. It is set by the LLM for rank-1 only, subject to the rules below.

**Confidence rules (agent applies after receiving LLM output):**

| Condition | matching_confidence |
|---|---|
| `eligible_candidate_count == 0` | `0.0` (routing decision forced to `ESCALATE_NO_CANDIDATES`) |
| `eligible_candidate_count == 1` | `LLM-returned value × 0.80` (thin pool penalty applies) |
| LLM fallback active (FM-2) | `composite_score × 0.85` for rank-1 (fallback discount) |
| Normal path | LLM-returned value (within schema constraints) |

Thresholds configurable:
- `MATCH_HIGH_THRESHOLD` (default `0.80`) — boundary for `AUTO_SUBMIT`
- `MATCH_LOW_THRESHOLD` (default `0.60`) — boundary between `COORDINATOR_REVIEW` and `ESCALATE_NO_CANDIDATES`

---

### Routing decision

Computed by the agent (not LLM) after confidence scoring. Applied in order; first matching rule wins.

| Priority | Condition | routing_decision | Action |
|---|---|---|---|
| 1 | `eligible_candidate_count == 0` | `ESCALATE_NO_CANDIDATES` | Empty candidates list; notify coordinator immediately |
| 2 | `eligible_candidate_count == 1` | `COORDINATOR_REVIEW` | Thin pool; coordinator judgment required regardless of score |
| 3 | `matching_confidence ≥ MATCH_HIGH_THRESHOLD` AND `eligible_candidate_count ≥ 2` | `AUTO_SUBMIT` | Set `override_window_expires_at = now() + OVERRIDE_WINDOW_MINUTES`; notify coordinator of pending auto-submission |
| 4 | `matching_confidence ≥ MATCH_LOW_THRESHOLD` | `COORDINATOR_REVIEW` | Add to coordinator review queue |
| 5 | `matching_confidence < MATCH_LOW_THRESHOLD` | `ESCALATE_NO_CANDIDATES` | No viable match despite eligible candidates; notify coordinator with score explanation |

**Override window (AUTO_SUBMIT path):**

- MatchingResult status → `AWAITING_SUBMISSION`
- Coordinator is notified on dashboard and via `COORDINATOR_NOTIFICATION_CHANNEL` (configurable): shift details, top candidate, confidence score, override deadline
- Coordinator can: approve (no action required), select alternative candidate, or block submission within `OVERRIDE_WINDOW_MINUTES` (default `10`; configurable)
- If no coordinator action before `override_window_expires_at`: status → `SUBMITTED`; `selected_candidate_nurse_id = candidates[0].nurse_id`; Agent 3 receives the MatchingResult
- If coordinator acts within window: status → `OVERRIDDEN`; `coordinator_id`, `override_reason_category`, `selected_candidate_nurse_id` logged; status → `SUBMITTED` with coordinator's selection; Agent 3 receives updated MatchingResult

**Coordinator review queue (COORDINATOR_REVIEW path):**

- MatchingResult status → `AWAITING_COORDINATOR`
- Coordinator sees in review interface: parsed ShiftRequest (editable if incorrect), top 5 ranked candidates with composite scores, adjusted scores, reasoning summaries, and any warnings or credential expiry alerts; action buttons: approve top candidate / select alternative / escalate
- If `ShiftRequest.urgency = CRITICAL` and no coordinator action within `CRITICAL_REVIEW_TIMEOUT_MINUTES` (default `15`; configurable): send escalation notification to queue supervisor; MatchingResult remains `AWAITING_COORDINATOR` until acted on
- All coordinator actions log: `coordinator_id`, `override_reason_category`, `selected_candidate_nurse_id`, timestamp

**Escalation path (ESCALATE_NO_CANDIDATES):**

- MatchingResult status → `ESCALATED`
- Coordinator is notified immediately with: ShiftRequest summary, `eligible_candidate_count`, `routing_rationale` from LLM (or "Nurse database unavailable" if FM-1)
- Coordinator decides how to proceed: manual outreach, defer shift, cancel; Agent 2's role ends here

**Multi-submission (coordinator review path only):**

Agent 2 produces a ranked list of up to 5 candidates. When `routing_decision = COORDINATOR_REVIEW`, the coordinator may approve up to `MAX_MULTI_SUBMIT_CANDIDATES` (default `3`) candidates from the list for simultaneous submission to the same hospital. Coordinator selects candidates in the review interface; the `candidates` list in the approved MatchingResult reflects the selection. Agent 3 handles simultaneous submissions and race condition resolution. Agent 2 does not autonomously trigger multi-submission.

**Race condition scope boundary:**

Agent 2 does not prevent the same nurse from appearing as rank-1 candidate in multiple simultaneous MatchingResults for different hospitals. Submitting the same nurse to multiple hospitals simultaneously is an intentional competitive practice at MedFlex. Agent 3 resolves conflicts after hospital confirmation (see architecture document, Agent 3 section).

---

## Delegation boundaries

| Decision | Owner | Condition | Action |
|---|---|---|---|
| Hard constraint filtering | Agent [Agent + Log] | Always | Deterministic; log each excluded nurse with exclusion reason |
| Soft factor score computation | Agent [Agent + Log] | Always | Deterministic formula; all scores logged |
| Contextual ranking and reasoning | Agent (LLM) [Agent + Log] | Applied to Phase 1 eligible candidates | LLM ranks candidates and generates reasoning summaries |
| Routing decision computation | Agent [Agent + Log] | Always; after LLM output | Deterministic from matching_confidence + eligible_candidate_count; not delegated to LLM |
| Auto-submit (high confidence) | Agent [Agent + Human Oversight] | `matching_confidence ≥ MATCH_HIGH_THRESHOLD` AND `eligible_candidate_count ≥ 2` | Agent decides; coordinator can override within `OVERRIDE_WINDOW_MINUTES` |
| Final candidate selection (coordinator review) | Coordinator [Human-led + Agent Support] | `routing_decision = COORDINATOR_REVIEW` | Agent surfaces ranked list with reasoning; coordinator selects |
| Override within window | Coordinator [Human] | `routing_decision = AUTO_SUBMIT`; action within window | Coordinator selects alternative; `override_reason_category` required |
| No-match escalation | Agent escalates → Coordinator [Human] | `routing_decision = ESCALATE_NO_CANDIDATES` | Agent notifies with summary; coordinator decides how to proceed |
| Compliance flagging (credential expiry) | Agent [Agent + Log] | Recently-lapsed credential detected | Fire-and-forget compliance alert; does not block matching |

---

## Integration contracts

### ShiftRequest — read

**Purpose:** Retrieve the ShiftRequest created by Agent 1 to trigger a matching run.

**Trigger:** Agent 2 polls the `shift_requests` table every `MATCHING_POLL_INTERVAL_SECONDS` (default `30`) for records with `status = 'PENDING_MATCH'` that have no corresponding `MatchingResult`. Query:

```sql
SELECT sr.*
FROM shift_requests sr
LEFT JOIN matching_results mr ON sr.id = mr.shift_request_id
WHERE sr.status = 'PENDING_MATCH'
  AND mr.id IS NULL
ORDER BY sr.created_at ASC
LIMIT 10;
```

Process each result sequentially. After creating the MatchingResult, the ShiftRequest status is not changed by Agent 2 — Agent 3 advances it to `MATCHED` once a candidate is submitted (aligns with D4a state machine: `PENDING_MATCH → MATCHED` is owned by Agent 3 on `MatchingResult.status = SUBMITTED`).

**Source:** The same PostgreSQL database written to by Agent 1 (shared `shift_requests` table).

**Required fields consumed:**

| Field | Used for |
|---|---|
| `id` | Link `MatchingResult.shift_request_id` |
| `shift_date`, `shift_start_time`, `shift_end_time` | Hard availability check |
| `hospital_id` | Hospital preference lookup; do-not-send check |
| `hospital_location` | Hospital coordinates `{lat, lng}` for proximity scoring; written by Agent 1 from hospital profile |
| `required_credentials` | Hard credential check |
| `preferred_credentials` | Soft ranking input to LLM (nice-to-have signal) |
| `unit_type` | Nurse unit type preference match |
| `urgency` | `CRITICAL` urgency sets `CRITICAL_REVIEW_TIMEOUT_MINUTES` for coordinator review |
| `confidence_score` | Passed to LLM as context (lower parse confidence = more caution in matching) |

---

### Nurse database — read

> **[ASSUMED]** The following contract defines what Agent 2 requires. Actual endpoint, query parameters, field names, and auth must be confirmed with Aaron (IT) before build.

**Purpose:** Retrieve nurse profiles including credentials, confirmed schedules, soft preferences, home location, hospital history, and performance data.

**Endpoint:** `GET ${MEDFLEX_API_BASE_URL}/nurses/search`

**Authentication:** Internal API key. Sourced from `MEDFLEX_API_KEY` environment variable. Never hardcoded.

**Request parameters:**

```
credential_categories: list[CredentialCategory]   // required credentials from ShiftRequest
                                                   // server-side pre-filter if supported [ASSUMED]
shift_date:            YYYY-MM-DD                  // for server-side credential expiry check [ASSUMED]
shift_start_datetime:  ISO 8601 timestamp          // for server-side availability check [ASSUMED]
shift_end_datetime:    ISO 8601 timestamp          // for server-side availability check [ASSUMED]
hospital_id:           string                      // for server-side do-not-send check [ASSUMED]
active_only:           true                        // always true
include_fields:        credentials,confirmed_schedule,availability_preferences,
                       home_location,preferred_hospitals,preferred_unit_types,
                       performance_summary,hospital_history,do_not_send
```

> **[ASSUMED — fallback]** If the nurse database API does not support server-side credential or availability filtering: Agent 2 fetches all active nurses and applies all Phase 1 hard constraint checks client-side. The request simplifies to `GET ${MEDFLEX_API_BASE_URL}/nurses?active=true` with the same `include_fields`. Performance implication: acceptable if active nurse database is ≤ 10,000 records at 960 requests/day; confirm nurse roster size with Aaron.

**Expected response (HTTP 200):**

```json
{
  "results": [
    {
      "nurse_id": "string (UUID)",
      "active": true,
      "credentials": [
        {
          "credential_category": "CredentialCategory enum value",
          "expiry_date": "YYYY-MM-DD",
          "verification_status": "VERIFIED | PENDING_RENEWAL | LAPSED"
        }
      ],
      "confirmed_schedule": [
        {
          "shift_id": "string (UUID)",
          "shift_date": "YYYY-MM-DD",
          "start_time": "HH:MM",
          "end_time": "HH:MM"
        }
      ],
      "availability_preferences": [
        {
          "day_of_week": "MON | TUE | WED | THU | FRI | SAT | SUN",
          "preferred_time": "DAYS | NIGHTS | EVENINGS | ANY"
        }
      ],
      "home_location": {"lat": 0.0, "lng": 0.0},
      "preferred_hospitals": ["string"],
      "preferred_unit_types": ["UnitType enum value"],
      "performance_summary": {
        "no_show_rate_12m": 0.0,
        "mismatch_rate_12m": 0.0,
        "total_shifts_12m": 0,
        "performance_score": 0.0
      },
      "hospital_history": [
        {
          "hospital_id": "string",
          "shifts_completed": 0,
          "no_shows_at_hospital": 0,
          "repeat_requested": false,
          "last_shift_date": "YYYY-MM-DD"
        }
      ],
      "do_not_send": ["string"],
      "updated_at": "ISO 8601 timestamp"
    }
  ],
  "total_count": 0
}
```

**Error handling:**

| HTTP status | Action |
|---|---|
| 200 | Process results; apply Phase 1 filtering |
| 204 | No nurses returned; `eligible_candidate_count = 0`; `routing_decision = ESCALATE_NO_CANDIDATES` |
| 401 / 403 | Log error; alert ops via `OPS_ALERT_CHANNEL`; create MatchingResult with `routing_decision = ESCALATE_NO_CANDIDATES`; coordinator notified with message: "Matching blocked — nurse database access error" |
| 429 | Honour `Retry-After` header; backoff and retry |
| 5xx | Retry once after 30 seconds; if retry fails: apply FM-1 failure mode |
| Timeout (> 15 seconds) | Treat as 5xx |

**Rate limit:** [ASSUMED — internal API; no rate limiting expected. If rate limits apply, implement request queue with configurable `NURSE_DB_REQUEST_QUEUE_SIZE`.]

---

### Hospital preference data — read

**Purpose:** Retrieve hospital-specific nurse preferences to inform `hospital_preference_score`.

**Endpoint:** `GET ${MEDFLEX_API_BASE_URL}/hospitals/${hospital_id}/preferences`

**Authentication:** Internal API key. Sourced from `MEDFLEX_API_KEY` environment variable.

**Expected response fields used:**

```json
{
  "preferred_nurse_ids": ["string (UUID)"],
  "blocked_nurse_ids": ["string (UUID)"],
  "unit_type_preferences": ["UnitType enum value"]
}
```

`preferred_nurse_ids` used to set `repeat_requested = true` override in hospital_preference_score computation if not already set from `HospitalHistoryEntry`. [ASSUMED — confirm whether hospital preferences are stored in the hospital record or derived from history; if both exist, history takes precedence]

`blocked_nurse_ids` are treated as an additional do-not-send source. [ASSUMED — confirm whether this is already reflected in `nurse.do_not_send` or is a separate hospital-side list]

**Timeout:** 10 seconds.

**Fallback:** If hospital preference API returns 4xx, 5xx, or times out: proceed with matching using `hospital_preference_score = 0.50` (neutral) for all candidates; `repeat_requested` sourced from `HospitalHistoryEntry.repeat_requested` only; log warning with `hospital_id`. Do not block matching.

**Caching:** Cache per `hospital_id` with 30-minute TTL (`HOSPITAL_PREF_CACHE_TTL_MINUTES`). Invalidate on any write to hospital preferences. At most ~20 distinct hospitals expected per hour.

---

### LLM — rank and reason

**Model:** `claude-sonnet-4-6` (default). Nurse matching requires multi-factor contextual reasoning across heterogeneous soft signals; Haiku is not sufficient for this task. Configurable via `MATCHING_LLM_MODEL` environment variable.

**System prompt:** Loaded from `prompts/matching_rank_system.txt` at runtime (not build time). Changes to the prompt require review before deployment. Prompt contains: role framing (senior coordinator analog), soft factor interpretation guidance, reasoning summary format instructions, instruction not to invent nurse IDs.

**Required input context per call:**
- `ShiftRequest` fields: `shift_date`, `unit_type`, `required_credentials`, `preferred_credentials`, `urgency`, `hospital_id`, `confidence_score` (from Agent 1)
- Eligible candidate list (each entry: `nurse_id`, `composite_score`, `soft_factor_scores` object, `performance_summary.performance_score`, `performance_summary.total_shifts_12m`, `credential_expiry_alert`)
- Hospital preferences summary: `preferred_nurse_ids`, `blocked_nurse_ids`, `unit_type_preferences`

**Max input tokens:** 6000 (ShiftRequest ~500 + up to 50 candidate summaries × 80 tokens + hospital preferences ~200 + system prompt ~2500). [ASSUMED — validate against actual candidate pool sizes in Phase 1]

**Required LLM output schema** — enforce via JSON mode or tool use. Do not parse free text:

```json
{
  "ranked_candidates": [
    {
      "nurse_id": "string (UUID)",
      "rank": 1,
      "matching_confidence": 0.0,
      "adjusted_composite_score": 0.0,
      "reasoning_summary": "string",
      "warnings": ["string"]
    }
  ],
  "routing_rationale": "string"
}
```

**Constraints on LLM output:**

- `ranked_candidates` must contain only `nurse_id` values from the eligible candidates provided as input. If LLM returns an unrecognised `nurse_id`: reject the entire output; apply FM-2 fallback; log incident.
- `rank` must be 1-based with no gaps and no duplicates (1, 2, 3, 4, 5). Any gap or duplicate: reject output; apply FM-2 fallback.
- `matching_confidence` must be populated for `rank = 1` only; any other value triggers schema rejection.
- `adjusted_composite_score` may differ from the pre-computed `composite_score` by at most ±0.15. If deviation exceeds ±0.15 for any candidate: use pre-computed `composite_score` for that candidate; log the deviation with `nurse_id` and `llm_call_id`; `matching_confidence` for rank-1 is set to `composite_score × 0.85` (treated as partial fallback).
- `reasoning_summary` max 500 chars; truncate silently if exceeded.
- `routing_rationale` max 300 chars; truncate silently if exceeded.
- `ranked_candidates` max 5 entries. If more than 5 returned: use first 5 by `rank` order; log warning.

If LLM output fails JSON schema validation: apply FM-2 fallback (see Failure Modes).

**LLM call timeout:** 20 seconds. Retry once after 5 seconds. If retry fails: apply FM-2 fallback; log incident.

---

## Validation design

### Happy path

**Scenario:** Standard ICU RN shift request; 8 eligible nurses after hard filtering; clear top candidate with strong hospital and proximity signals.

**Input (ShiftRequest):**
```json
{
  "shift_date": "2026-01-20",
  "shift_start_time": "19:00",
  "shift_end_time": "07:00",
  "unit_type": "ICU",
  "urgency": "STANDARD",
  "required_credentials": [
    {"credential_category": "RN", "inference_confidence": 0.95},
    {"credential_category": "ICU_CERTIFIED", "inference_confidence": 0.95}
  ],
  "preferred_credentials": [],
  "hospital_id": "hospital_stmarys_01",
  "confidence_score": 0.95
}
```

**Expected output (MatchingResult):**
- `eligible_candidate_count`: 8
- `candidates`: 5 ranked CandidateRecommendations with composite scores, adjusted scores, and reasoning summaries
- `routing_decision`: `AUTO_SUBMIT` (top candidate `matching_confidence ≥ 0.80` and `eligible_candidate_count ≥ 2`)
- `matching_confidence` for rank-1: ≥ 0.80
- `override_window_expires_at`: `created_at + 10 minutes`
- `status`: `AWAITING_SUBMISSION`

Coordinator receives notification: shift summary, top candidate name+score, override deadline. If no action in 10 minutes: status → `SUBMITTED`; Agent 3 receives `(shift_request_id, selected_candidate_nurse_id)`.

---

### Edge cases

**EC-1: No eligible nurses after hard filtering**
- Input: ICU RN shift for a hospital where all ICU-certified nurses have scheduling conflicts or lapsed credentials
- Expected: `eligible_candidate_count = 0`; `routing_decision = ESCALATE_NO_CANDIDATES`; `candidates = []`; status `ESCALATED`; coordinator notified immediately with `routing_rationale` summarising reason (e.g., "No nurses with valid ICU_CERTIFIED credentials available on 2026-01-20")

**EC-2: Single eligible nurse — thin pool**
- Input: CRNA specialty shift; only 1 nurse in database holds CRNA and is available
- Expected: `eligible_candidate_count = 1`; `routing_decision = COORDINATOR_REVIEW` regardless of composite_score; `matching_confidence = LLM-returned value × 0.80`; status `AWAITING_COORDINATOR`; `routing_rationale` notes thin pool

**EC-3: Credential expires before shift date**
- Input: Nurse_A has `ICU_CERTIFIED` with `expiry_date = 2026-01-18`; `shift_date = 2026-01-20`; expiry is 2 days before shift
- Expected: Nurse_A excluded in Phase 1 with reason `CREDENTIAL_EXPIRED`; compliance flag logged if credential was VERIFIED within last 90 days; Nurse_A does not appear in `candidates`

**EC-4: Credential expires within 30 days of shift date**
- Input: Nurse_B has `ICU_CERTIFIED` with `expiry_date = 2026-02-05`; `shift_date = 2026-01-20`; expiry is 16 days after shift
- Expected: Nurse_B passes Phase 1 (`expiry_date > shift_date`); `credential_expiry_alert = true`; `warnings` contains: `"ICU_CERTIFIED expires 2026-02-05, 16 days after shift"`; Nurse_B included in ranked candidates; coordinator sees alert in review interface

**EC-5: Nurse on do-not-send list for requesting hospital**
- Input: Nurse_C has `hospital_stmarys_01` in `do_not_send`; shift request is from `hospital_stmarys_01`
- Expected: Nurse_C excluded in Phase 1 with reason `DO_NOT_SEND`; no compliance alert; Nurse_C does not appear in `candidates`

**EC-6: Preferred credential (not required) present — soft ranking signal**
- Input: `ShiftRequest.preferred_credentials = [{BLS, 0.90}]`; Nurse_D holds BLS; Nurse_E does not; all other soft factors equal
- Expected: Both pass Phase 1 (BLS is preferred, not required); LLM receives `preferred_credentials` in input; `reasoning_summary` for Nurse_D references BLS as positive signal; Nurse_D ranked above Nurse_E in LLM output if composite scores are otherwise equivalent

**EC-7: LLM returns adjusted_composite_score deviation > 0.15**
- Input: Nurse_F has pre-computed `composite_score = 0.75`; LLM returns `adjusted_composite_score = 0.45` (deviation = 0.30)
- Expected: deviation exceeds ±0.15 limit; `composite_score = 0.75` used for Nurse_F; incident logged with `nurse_id` and `llm_call_id`; `matching_confidence` for rank-1 set to `0.75 × 0.85 = 0.64` if Nurse_F is rank-1 (partial fallback); `routing_decision = COORDINATOR_REVIEW`; LLM `reasoning_summary` kept for coordinator display

**EC-8: Shift crosses midnight — availability overlap**
- Input: `shift_date = 2026-01-20`, `shift_start_time = 19:00`, `shift_end_time = 07:00`; Nurse_G has `ScheduledShift` on `2026-01-21` from `06:00` to `14:00`
- Expected: `requested_end_datetime = 2026-01-21T07:00:00Z`; `scheduled_start = 2026-01-21T06:00:00Z`; overlap check: `06:00 < 07:00 AND 14:00 > 19:00 (prev day)` — overlap confirmed; Nurse_G excluded with reason `AVAILABILITY_CONFLICT`

---

### Failure modes

**FM-1: Nurse database API unavailable**
- Trigger: nurse database API returns 5xx or timeout on initial call and one retry
- Expected: MatchingResult created with `routing_decision = ESCALATE_NO_CANDIDATES`; `candidates = []`; `routing_rationale = "Matching could not complete — nurse database unavailable"`; status `ESCALATED`; coordinator notified; ops alert sent via `OPS_ALERT_CHANNEL`; `ShiftRequest.status` remains `PENDING_MATCH` (not advanced) so the run can be retried when database recovers; incident logged

**FM-2: LLM failure — fallback to algorithmic ranking**
- Trigger: LLM returns invalid JSON, schema-invalid output, or unrecognised nurse IDs after one retry
- Expected: eligible candidates sorted by pre-computed `composite_score` descending; top 5 placed in `candidates`; `matching_confidence = composite_score × 0.85` for rank-1; `routing_decision = COORDINATOR_REVIEW` regardless of score; `reasoning_summary` for each candidate set to `"Automated ranking — LLM reasoning unavailable"`; incident logged with `llm_call_id`; model quality monitoring flag set; matching run completes without blocking

**FM-3: Hospital preference data unavailable**
- Trigger: hospital preference API returns 4xx, 5xx, or times out
- Expected: matching proceeds with `hospital_preference_score = 0.50` (neutral) for all candidates; `repeat_requested` sourced from `HospitalHistoryEntry` only; warning logged with `hospital_id`; coordinator sees warning in review interface: `"Hospital preference data unavailable — hospital preference score defaulted to 0.50"`; routing decision proceeds normally on remaining soft factors

---

## Assumptions register

| ID | Assumption | Why it matters | If wrong | Status |
|---|---|---|---|---|
| A1 | Nurse database has a queryable API returning profiles with credentials (including expiry dates), confirmed schedules, availability preferences, home location, hospital history, and performance data | Entire Phase 1 filtering and Phase 2 ranking depend on this | Agent cannot match; matching falls back to manual-only | [FLAGGED] — confirm with Aaron; is build blocker |
| A2 | Credential expiry dates are stored as structured date fields, not free-text or manual lookup | Required for programmatic hard constraint check | Agent cannot enforce credential expiry; compliance risk | [FLAGGED] — confirm with Aaron before build |
| A3 | Nurse home location is stored as geocodable coordinates or a US zip code | Required for proximity score computation | Proximity score disabled; weight redistributed: `MATCHING_WEIGHT_HOSPITAL_PREF += 0.15`, `MATCHING_WEIGHT_NURSE_PREF += 0.10`; agent logs notice of redistribution | [ASSUMED] — if coordinates unavailable, fallback redistribution applies automatically |
| A4 | Hospital preference data (preferred nurses, blocked nurses) exists as a structured API response | Enables `hospital_preference_score` computation | Defaults to 0.50 (neutral) for all candidates; soft ranking quality degrades | [ASSUMED] — confirm structure and completeness with Aaron |
| A5 | Performance data (no-show rate, mismatch rate) is available per nurse as pre-computed fields or derivable in < 2 seconds | Performance score is a differentiator in soft ranking | Defaults to 0.50 for all nurses; soft ranking quality degrades | [ASSUMED] — confirm whether pre-computed or requires aggregation query |
| A6 | Nurse confirmed schedule in the database reflects near-real-time state (< 15-minute lag) | Hard availability constraint accuracy depends on freshness | Agent may match a nurse with an unrecorded conflict; no-show risk | [ASSUMED] — confirm data freshness model with Aaron |
| A7 | `do_not_send` per hospital is a structured list in the nurse record, not an informal note | Required for programmatic exclusion in Phase 1 | Do-not-send exclusions not enforced automatically; relationship and compliance risk | [FLAGGED] — confirm with Aaron |
| A8 | `claude-sonnet-4-6` achieves acceptable contextual ranking quality on healthcare staffing matching tasks | Drives cost model and model selection | May require `claude-opus-4-6` for complex specialist cases; cost increases | [ASSUMED] — validate with sample ranking tests before production |

---

## Economics

| Operation | Type | Estimated cost | Frequency | Notes |
|---|---|---|---|---|
| LLM ranking call (Sonnet) | Generate | $0.015–0.050 per request | ~960/day | Cost varies with eligible candidate pool size; Sonnet required for multi-factor reasoning |
| Nurse database query | Coordinate | Negligible internal API cost | ~960/day | No caching — availability data must be fresh per request |
| Hospital preference read | Coordinate | Negligible | ~960/day | Cache per hospital, 30-minute TTL; at most ~20 distinct hospitals per hour |

**Total estimated LLM cost (Agent 2):** $14–$48/day at 960 requests/day. Combined with Agent 1 (~$1/day for Haiku), total pipeline LLM cost estimate: **$15–$50/day**.

**Candidate pool pre-filtering:** If nurse database API supports server-side filtering by credential and availability, use it. Goal: pass ≤ 50 eligible candidates to LLM per call. If post-Phase-1 pool exceeds 50: pre-rank by `composite_score`; pass top 50 to LLM; log truncation warning with pool size and shift_request_id.

**Circuit breaker:** If LLM API costs exceed `DAILY_LLM_COST_LIMIT_USD` (default `$50`; shared limit with Agent 1): halt LLM calls; apply FM-2 algorithmic fallback for all requests; route all MatchingResults to `COORDINATOR_REVIEW` regardless of score; alert ops; limit resets at `00:00 UTC` daily. Configurable via `DAILY_LLM_COST_LIMIT_USD`.

---

## Governance & audit

**Audit trail:** Every MatchingResult creation and status transition must be logged with:
- `timestamp` (UTC, ISO 8601)
- `shift_request_id`
- `action` (enum: `CREATED`, `STATUS_CHANGED`, `COORDINATOR_APPROVED`, `COORDINATOR_OVERRIDDEN`, `AUTO_SUBMITTED`, `ESCALATED`)
- `from_status` / `to_status` (on status changes)
- `agent_version`
- `routing_decision` at creation
- `matching_confidence` at creation
- `eligible_candidate_count` at creation
- `coordinator_id` and `override_reason_category` (if human action; both required when coordinator acts)
- `llm_call_id` (for model quality tracking and incident correlation)

**ADR-1 revisitation data — required from day one:**

Per MatchingResult, also log for the accuracy comparison required in ADR-1:
- `proposed_nurse_id` = `candidates[0].nurse_id` at time of creation
- `submitted_nurse_id` = `selected_candidate_nurse_id` after submission
- `submission_path` = `AUTO_SUBMIT` or `COORDINATOR_REVIEW` (derived from routing_decision)
- `fill_outcome`: backfilled by Agent 3 after hospital confirmation as `FILLED`, `UNFILLED`, or `NO_SHOW`

Without `fill_outcome` and `submission_path` logged from day one, the ADR-1 revisitation condition ("auto-submission accuracy ≥ coordinator average") cannot be evaluated. These fields are mandatory, not optional.

**Retention:** Audit logs and MatchingResult records retained for 3 years minimum. [ASSUMED — confirm with Linda (Compliance)]

**HITL checkpoints:**
- Any MatchingResult with `routing_decision = COORDINATOR_REVIEW` must not transition to `SUBMITTED` without explicit coordinator action (`coordinator_id` set)
- Any MatchingResult with `routing_decision = ESCALATE_NO_CANDIDATES` must not proceed to Agent 3; coordinator handles manually
- Override window expiry (auto-submit without coordinator action) is a valid and logged path (`action = AUTO_SUBMITTED`, `coordinator_id = null`)
- `override_reason_category` is required whenever `coordinator_id` is set; schema must reject null `override_reason_category` with non-null `coordinator_id`

**Data handling:** MatchingResult contains `nurse_id` and `coordinator_id` references (PII). Do not log nurse names, coordinator names, or contact details in audit logs — log only UUID references. [FLAGGED — confirm PHI handling requirements for nurse records with Linda (Compliance)]

---

## Build context

This section provides all implementation details required to build Agent 2 without making infrastructure assumptions. Read this section before starting.

### Stack

- **Language:** Python 3.11
- **Dependencies** (`requirements.txt`):

```
anthropic>=0.25.0
psycopg2-binary>=2.9.9
pydantic>=2.0.0
httpx>=0.27.0
python-dotenv>=1.0.0
```

No other packages. Haversine distance calculation uses the Python standard library (`math` module) only — do not add a geopy or haversine package.

### Project structure

```
medflex-agent2/
├── main.py                          # polling loop entry point
├── agent.py                         # orchestrates one matching run end-to-end
├── hard_filter.py                   # Phase 1 hard constraint checks
├── soft_rank.py                     # composite_score computation
├── llm_client.py                    # LLM call, output validation, FM-2 fallback
├── routing.py                       # routing_decision logic
├── db.py                            # PostgreSQL read/write functions
├── nurse_db.py                      # mock nurse database queries (see below)
├── models.py                        # Pydantic models for all entities
├── haversine.py                     # proximity calculation (stdlib only)
├── prompts/
│   └── matching_rank_system.txt     # system prompt, loaded at runtime
├── fixtures/
│   └── nurses.sql                   # mock nurse data (see below)
├── .env                             # environment variables (not committed)
└── requirements.txt
```

### Environment variables

All configuration is read from environment variables. Load with `python-dotenv`. Never hardcode values.

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | (required) | PostgreSQL connection string, e.g. `postgresql://user:pass@localhost:5432/medflex` |
| `MEDFLEX_API_BASE_URL` | (required) | Nurse DB and hospital API base URL. Set to `mock` to use mock nurse DB (see below). |
| `MEDFLEX_API_KEY` | (required) | Internal API key for MedFlex APIs. Ignored when `MEDFLEX_API_BASE_URL=mock`. |
| `ANTHROPIC_API_KEY` | (required) | Anthropic API key. |
| `MATCHING_LLM_MODEL` | `claude-sonnet-4-6` | LLM model for ranking calls. |
| `MATCHING_POLL_INTERVAL_SECONDS` | `30` | Seconds between polling cycles. |
| `MATCH_HIGH_THRESHOLD` | `0.80` | Confidence threshold for AUTO_SUBMIT routing. |
| `MATCH_LOW_THRESHOLD` | `0.60` | Confidence threshold below which ESCALATE_NO_CANDIDATES is triggered. |
| `OVERRIDE_WINDOW_MINUTES` | `10` | Minutes coordinator has to override before auto-submission. |
| `CRITICAL_REVIEW_TIMEOUT_MINUTES` | `15` | Minutes before escalation notification for CRITICAL urgency coordinator reviews. |
| `MAX_LLM_CANDIDATE_INPUT` | `50` | Max candidates passed to LLM; pre-rank by composite_score if pool exceeds this. |
| `MAX_MULTI_SUBMIT_CANDIDATES` | `3` | Max candidates coordinator may approve for multi-submission. |
| `DAILY_LLM_COST_LIMIT_USD` | `50` | Circuit breaker: halt LLM calls if daily cost exceeds this. Resets at 00:00 UTC. |
| `OPS_ALERT_WEBHOOK_URL` | (optional) | Webhook URL for ops alerts. If unset, ops alerts are logged to stderr only. |
| `COORDINATOR_NOTIFICATION_CHANNEL` | `log` | `log` (log to stdout) or a webhook URL for coordinator notifications. |
| `COMPLIANCE_ALERT_CHANNEL` | `log` | `log` or webhook URL for compliance alerts (credential expiry). |
| `HOSPITAL_PREF_CACHE_TTL_MINUTES` | `30` | Cache TTL for hospital preference API responses. |
| `MATCHING_WEIGHT_PROXIMITY` | `0.25` | Soft ranking weight for proximity score. |
| `MATCHING_WEIGHT_HOSPITAL_PREF` | `0.35` | Soft ranking weight for hospital preference score. |
| `MATCHING_WEIGHT_NURSE_PREF` | `0.25` | Soft ranking weight for nurse preference score. |
| `MATCHING_WEIGHT_PERFORMANCE` | `0.15` | Soft ranking weight for performance score. |
| `PERFORMANCE_MIN_SAMPLE` | `5` | Minimum number of shifts in last 12 months required to use computed performance_score; below this threshold, performance_score defaults to 0.50 (neutral). |

Weights must sum to 1.0. Validate on startup; raise `ValueError` if sum ≠ 1.0.

### PostgreSQL schema

Run this DDL before starting the agent. Assumes `shift_requests` and `credential_requirements` tables from Agent 1 already exist.

```sql
-- MatchingResult (one per ShiftRequest)
CREATE TABLE IF NOT EXISTS matching_results (
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shift_request_id            UUID NOT NULL REFERENCES shift_requests(id),
    status                      TEXT NOT NULL DEFAULT 'PENDING_ROUTING',
    routing_decision            TEXT,
    matching_confidence         NUMERIC(4,3),
    eligible_candidate_count    INTEGER,
    candidates_json             JSONB,          -- serialised list of CandidateRecommendation
    routing_rationale           TEXT,
    proposed_nurse_id           UUID,           -- ADR-1: rank-1 nurse at creation
    selected_candidate_nurse_id UUID,           -- set after coordinator action or auto-submit
    submitted_nurse_id          UUID,           -- ADR-1: backfilled by Agent 3 on confirmation
    submission_path             TEXT,           -- ADR-1: 'AUTO_SUBMIT' or 'COORDINATOR_REVIEW'
    fill_outcome                TEXT,           -- ADR-1: 'FILLED', 'UNFILLED', 'NO_SHOW'; backfilled by Agent 3
    coordinator_id              UUID,
    override_reason_category    TEXT,
    override_window_expires_at  TIMESTAMPTZ,
    llm_call_id                 TEXT,
    agent_version               TEXT,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Matching audit log
CREATE TABLE IF NOT EXISTS matching_audit_log (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    matching_result_id  UUID NOT NULL REFERENCES matching_results(id),
    timestamp           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    action              TEXT NOT NULL,
    from_status         TEXT,
    to_status           TEXT,
    coordinator_id      UUID,
    override_reason     TEXT,
    agent_version       TEXT,
    notes               TEXT
);

-- Mock nurse tables (used when MEDFLEX_API_BASE_URL=mock)
-- In production these would be queried via the MedFlex API, not directly.
CREATE TABLE IF NOT EXISTS nurses (
    nurse_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    active          BOOLEAN NOT NULL DEFAULT TRUE,
    home_lat        NUMERIC(9,6),
    home_lng        NUMERIC(9,6),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS nurse_credentials (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nurse_id            UUID NOT NULL REFERENCES nurses(nurse_id),
    credential_category TEXT NOT NULL,
    expiry_date         DATE NOT NULL,
    verification_status TEXT NOT NULL DEFAULT 'VERIFIED'
);

CREATE TABLE IF NOT EXISTS nurse_scheduled_shifts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nurse_id        UUID NOT NULL REFERENCES nurses(nurse_id),
    shift_date      DATE NOT NULL,
    start_time      TIME NOT NULL,
    end_time        TIME NOT NULL
);

CREATE TABLE IF NOT EXISTS nurse_preferences (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nurse_id            UUID NOT NULL REFERENCES nurses(nurse_id),
    day_of_week         TEXT,                   -- MON|TUE|WED|THU|FRI|SAT|SUN
    preferred_time      TEXT,                   -- DAYS|NIGHTS|EVENINGS|ANY
    preferred_hospital  TEXT,
    preferred_unit_type TEXT,
    do_not_send         TEXT                    -- hospital_id to exclude
);

CREATE TABLE IF NOT EXISTS nurse_hospital_history (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nurse_id            UUID NOT NULL REFERENCES nurses(nurse_id),
    hospital_id         TEXT NOT NULL,
    shifts_completed    INTEGER DEFAULT 0,
    no_shows_at_hospital INTEGER DEFAULT 0,
    repeat_requested    BOOLEAN DEFAULT FALSE,
    last_shift_date     DATE
);

CREATE TABLE IF NOT EXISTS nurse_performance_summary (
    nurse_id            UUID PRIMARY KEY REFERENCES nurses(nurse_id),
    no_show_rate_12m    NUMERIC(4,3) DEFAULT 0.0,
    mismatch_rate_12m   NUMERIC(4,3) DEFAULT 0.0,
    total_shifts_12m    INTEGER DEFAULT 0,
    performance_score   NUMERIC(4,3) DEFAULT 0.5
);
```

### Mock nurse database

When `MEDFLEX_API_BASE_URL=mock`, Agent 2 must query the PostgreSQL mock tables above directly via `psycopg2` instead of making HTTP calls to the nurse database API. The `nurse_db.py` module implements this mock path.

Load this fixture data once before running in mock mode:

```sql
-- fixtures/nurses.sql
-- 4 mock nurses for local development and testing

INSERT INTO nurses VALUES
  ('aaaaaaaa-0001-0001-0001-000000000001', TRUE, 40.7128, -74.0060, NOW()),  -- NYC
  ('aaaaaaaa-0001-0001-0001-000000000002', TRUE, 40.7580, -73.9855, NOW()),  -- Midtown
  ('aaaaaaaa-0001-0001-0001-000000000003', TRUE, 40.6892, -74.0445, NOW()),  -- Brooklyn
  ('aaaaaaaa-0001-0001-0001-000000000004', TRUE, 40.7282, -73.7949, NOW()); -- Queens

INSERT INTO nurse_credentials VALUES
  (gen_random_uuid(), 'aaaaaaaa-0001-0001-0001-000000000001', 'RN',           '2027-06-01', 'VERIFIED'),
  (gen_random_uuid(), 'aaaaaaaa-0001-0001-0001-000000000001', 'ICU_CERTIFIED','2027-06-01', 'VERIFIED'),
  (gen_random_uuid(), 'aaaaaaaa-0001-0001-0001-000000000002', 'RN',           '2026-12-31', 'VERIFIED'),
  (gen_random_uuid(), 'aaaaaaaa-0001-0001-0001-000000000002', 'ICU_CERTIFIED','2026-12-31', 'VERIFIED'),
  (gen_random_uuid(), 'aaaaaaaa-0001-0001-0001-000000000003', 'RN',           '2027-03-15', 'VERIFIED'),
  (gen_random_uuid(), 'aaaaaaaa-0001-0001-0001-000000000003', 'ICU_CERTIFIED','2026-02-01', 'VERIFIED'),  -- expires soon
  (gen_random_uuid(), 'aaaaaaaa-0001-0001-0001-000000000004', 'RN',           '2027-09-30', 'VERIFIED'),
  (gen_random_uuid(), 'aaaaaaaa-0001-0001-0001-000000000004', 'MED_SURG',     '2027-09-30', 'VERIFIED');

INSERT INTO nurse_preferences VALUES
  (gen_random_uuid(), 'aaaaaaaa-0001-0001-0001-000000000001', 'MON', 'NIGHTS', 'hospital_stmarys_01', 'ICU',      NULL),
  (gen_random_uuid(), 'aaaaaaaa-0001-0001-0001-000000000001', 'TUE', 'NIGHTS', NULL,                  NULL,       NULL),
  (gen_random_uuid(), 'aaaaaaaa-0001-0001-0001-000000000002', 'MON', 'ANY',    'hospital_stmarys_01', 'ICU',      NULL),
  (gen_random_uuid(), 'aaaaaaaa-0001-0001-0001-000000000003', 'WED', 'NIGHTS', NULL,                  'ICU',      NULL),
  (gen_random_uuid(), 'aaaaaaaa-0001-0001-0001-000000000004', 'MON', 'DAYS',   NULL,                  'MED_SURG', NULL);

INSERT INTO nurse_hospital_history VALUES
  (gen_random_uuid(), 'aaaaaaaa-0001-0001-0001-000000000001', 'hospital_stmarys_01', 12, 0, TRUE,  '2026-01-10'),
  (gen_random_uuid(), 'aaaaaaaa-0001-0001-0001-000000000002', 'hospital_stmarys_01',  4, 0, FALSE, '2025-12-15'),
  (gen_random_uuid(), 'aaaaaaaa-0001-0001-0001-000000000003', 'hospital_stmarys_01',  1, 1, FALSE, '2025-11-20');

INSERT INTO nurse_performance_summary VALUES
  ('aaaaaaaa-0001-0001-0001-000000000001', 0.02, 0.01, 48, 0.92),
  ('aaaaaaaa-0001-0001-0001-000000000002', 0.05, 0.03, 20, 0.80),
  ('aaaaaaaa-0001-0001-0001-000000000003', 0.10, 0.05,  8, 0.65),
  ('aaaaaaaa-0001-0001-0001-000000000004', 0.03, 0.02, 32, 0.88);
```

### Haversine implementation

`haversine.py` — compute distance in km between two lat/lng points. Standard library only.

```python
import math

def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
```

Proximity score formula: `1.0 / (1.0 + distance_km / 20.0)` — gives 1.0 at 0 km, ~0.5 at 20 km, ~0.25 at 60 km. If nurse `home_lat` or `home_lng` is NULL: `proximity_score = 0.50` (neutral).

Hospital coordinates for proximity calculation come from the hospital profile in the `shift_requests` table (the `hospital_location` JSON column written by Agent 1, containing `lat` and `lng`).

### OPS_ALERT_CHANNEL implementation

When `OPS_ALERT_WEBHOOK_URL` is set: POST JSON to that URL with fields `{"level": "ERROR", "agent": "agent2-matching", "message": "...", "timestamp": "ISO8601"}`. Use `httpx` with a 5-second timeout. Never let a failed ops alert block the main loop — catch all exceptions from the webhook call and log to stderr.

When `OPS_ALERT_WEBHOOK_URL` is not set: log to stderr with prefix `[OPS_ALERT]`.

### System prompt — `prompts/matching_rank_system.txt`

```
You are a senior healthcare staffing coordinator with 15 years of experience matching registered nurses to hospital shift requests. You have deep knowledge of healthcare credential requirements, hospital unit culture, and nurse reliability patterns.

Your role in this system: you receive a structured shift request and a list of pre-screened eligible nurses (all hard constraints already verified). Your job is to rank the eligible nurses for this specific shift and explain your reasoning clearly enough that a coordinator can approve or override your recommendation confidently.

## Your inputs

You will receive:
1. The shift request: date, time, unit type, required credentials, preferred credentials, urgency, hospital ID, and Agent 1's parse confidence score
2. A list of eligible nurses: each with a pre-computed composite score, soft factor scores (proximity, hospital preference, nurse preference, performance), performance summary, and credential expiry alerts
3. Hospital preferences: which nurses the hospital has worked with before, any blocked nurses, and unit type preferences

## Your ranking task

Return a ranked list of up to 5 nurses for this shift. For each nurse:
- Assign a rank (1 = best match)
- Set an adjusted_composite_score (within ±0.15 of the pre-computed composite_score — do not invent scores)
- Write a reasoning_summary (max 500 characters): explain specifically why this nurse is a good or weaker fit for this particular shift. Reference the soft factors that matter most for this shift type. Be concrete — "strong ICU history at this hospital, available nights" not "good candidate"
- List any warnings (credential expiry alerts, performance flags, thin pool signals)

For rank 1 only: set matching_confidence between 0.0 and 1.0 representing your certainty that this is the right nurse for this shift.

## Confidence calibration

- 0.90+: Strong match across all soft factors; hospital has worked with this nurse before; no warnings
- 0.80–0.89: Good match; minor soft factor gaps or one warning; still clearly best available
- 0.60–0.79: Acceptable match; notable gaps or thin pool; coordinator review appropriate
- Below 0.60: Weak match; significant gaps or no strong candidate; escalation likely appropriate

When Agent 1's parse confidence is below 0.75, apply a conservative bias — reduce your confidence by 0.05 to account for potential shift requirement ambiguity.

## routing_rationale

After your ranked list, provide a routing_rationale (max 300 characters) summarising the key signal driving your top recommendation. Example: "Nurse A has 12 prior shifts at St Mary's ICU with zero no-shows and is available nights on the requested date." This is shown to the coordinator as context for the routing decision.

## Critical constraints

- Only use nurse_id values from the eligible candidates list provided. Never invent nurse IDs.
- Do not re-evaluate hard constraints. Every nurse in your input has already passed credential verification and availability checks.
- Do not rank nurses not in your input.
- If all candidates have similar scores and no strong differentiator exists, say so in routing_rationale and set confidence accordingly — do not manufacture false confidence.

## Output format

Return valid JSON only. No preamble. No explanation outside the JSON structure. Schema:
{
  "ranked_candidates": [
    {
      "nurse_id": "UUID string",
      "rank": integer (1-based, no gaps),
      "matching_confidence": float (rank 1 only; omit for rank 2+),
      "adjusted_composite_score": float,
      "reasoning_summary": "string max 500 chars",
      "warnings": ["string"]
    }
  ],
  "routing_rationale": "string max 300 chars"
}
```

### How to run Agent 2

1. Copy `.env.example` to `.env` and fill in values. For local development set `MEDFLEX_API_BASE_URL=mock` and provide a local PostgreSQL `DATABASE_URL`.
2. Create the PostgreSQL schema: `psql $DATABASE_URL -f schema.sql` (run Agent 1's schema first, then Agent 2's DDL above).
3. Load mock nurse data: `psql $DATABASE_URL -f fixtures/nurses.sql`
4. Start the polling loop: `python main.py`
5. To test: insert a row into `shift_requests` with `status = 'PENDING_MATCH'` and credentials matching the mock nurses. Agent 2 will pick it up within `MATCHING_POLL_INTERVAL_SECONDS` seconds, run the matching pipeline, and write a `MatchingResult` to the database.
