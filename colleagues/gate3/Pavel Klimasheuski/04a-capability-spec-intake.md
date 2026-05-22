# Deliverable #4a — Capability Specification: Request Intake Agent
**Engagement:** MedFlex Healthcare Staffing
**Participant:** Pavel Klimasheuski
**Date:** 2026-05-13

> **Shared glossary note:** This document defines all shared entities (ShiftRequest, CredentialCategory, AmbiguityFlag, ConfidenceScore) used across both capability specs. Deliverable #4b references these definitions directly.

---

## Purpose & scope

The Request Intake Agent converts free-text hospital shift requests arriving in ServiceNow into structured `ShiftRequest` entities. It is the first stage in the matching pipeline. Its output is the sole input to Agent 2 (Nurse Matching).

**In scope:**
- Parsing free-text requests into structured ShiftRequest entities
- Credential category inference from natural-language descriptions
- Date/time resolution from relative and partial references
- Ambiguity detection and escalation to coordinator clarification queue
- Confidence scoring of parsed output

**Out of scope:**
- Nurse matching or candidate selection (Agent 2)
- Hospital submission or nurse notification (Agent 3)
- Credential verification against state regulatory databases (compliance team)

---

## Shared glossary

### CredentialCategory (enum)

Exhaustive list of credential categories the agent maps free-text descriptions to. All values are SCREAMING_SNAKE_CASE.

| Value | Description |
|---|---|
| `RN` | Registered Nurse (general) |
| `LPN` | Licensed Practical Nurse |
| `CNA` | Certified Nursing Assistant |
| `NP` | Nurse Practitioner |
| `CRNA` | Certified Registered Nurse Anesthetist |
| `ICU_CERTIFIED` | Intensive Care Unit specialisation |
| `ER_CERTIFIED` | Emergency Room specialisation |
| `OR_CERTIFIED` | Operating Room / perioperative specialisation |
| `PEDS_CERTIFIED` | Pediatric specialisation |
| `ONCOLOGY_CERTIFIED` | Oncology specialisation |
| `L_D_CERTIFIED` | Labor and Delivery specialisation |
| `PSYCH_CERTIFIED` | Psychiatric / behavioral health specialisation |
| `BLS` | Basic Life Support certification |
| `ACLS` | Advanced Cardiac Life Support certification |
| `PALS` | Pediatric Advanced Life Support certification |

> **[ASSUMED]** This taxonomy is based on common US travel-nursing credential categories. Must be validated with Kim (Head of Operations) and Linda (Compliance) before production deployment. If MedFlex uses a different internal taxonomy, this enum and all downstream credential-matching logic must be updated.

### UnitType (enum)

| Value | Description |
|---|---|
| `ICU` | Intensive Care Unit |
| `ER` | Emergency Room |
| `OR` | Operating Room |
| `MED_SURG` | Medical-Surgical floor |
| `PEDIATRIC` | Pediatric ward |
| `ONCOLOGY` | Oncology unit |
| `LABOR_DELIVERY` | Labor and Delivery |
| `PSYCH` | Psychiatric unit |
| `GENERAL` | General ward (non-specialised) |
| `UNKNOWN` | Could not be inferred from request text |

### Urgency (enum)

| Value | Trigger criteria |
|---|---|
| `STANDARD` | Default; shift date ≥ 48 hours from request receipt |
| `URGENT` | Shift date 24–48 hours from request receipt, OR request contains keyword: "urgent" |
| `CRITICAL` | Shift date < 24 hours from request receipt, OR request contains keywords: "ASAP", "immediately", "emergency cover" |

Urgency is computed from shift_date relative to request receipt timestamp, with keyword override. Keyword matching is case-insensitive.

### ConfidenceScore

A `decimal` value in the range `[0.0, 1.0]` representing the agent's certainty in its parsed output. Computed field — see Confidence Scoring Model below. Two decimal places.

- `≥ 0.85` — HIGH: agent output is sent directly to Agent 2
- `0.65–0.84` — MEDIUM: agent output is sent to Agent 2 but ambiguities are flagged for coordinator review before submission
- `< 0.65` — LOW: ShiftRequest is placed in coordinator clarification queue; Agent 2 does not run until coordinator reviews and approves the parse

Thresholds are configurable via `INTAKE_CONFIDENCE_HIGH_THRESHOLD` (default `0.85`) and `INTAKE_CONFIDENCE_LOW_THRESHOLD` (default `0.65`).

---

## Core entity: ShiftRequest

### Data model

| Field | Type | Required | Constraints | Notes |
|---|---|---|---|---|
| `id` | UUID | Yes | Immutable, generated on creation | Primary key |
| `servicenow_ticket_id` | string | Yes | Immutable, max 64 chars | Foreign key to ServiceNow ticket |
| `hospital_id` | string | Yes | Immutable, foreign key to Hospital | Must exist in hospital registry |
| `source_text` | string | Yes | Immutable, max 5000 chars | Raw text from ServiceNow; preserved for audit |
| `shift_date` | date (ISO 8601 YYYY-MM-DD) | Yes | Must be ≥ today's date at parse time | UTC date |
| `shift_start_time` | time (ISO 8601 HH:MM) | No | 24-hour format; null if not specified | UTC; inferred if not explicit; null triggers TIME_UNCLEAR flag |
| `shift_end_time` | time (ISO 8601 HH:MM) | No | Must be > shift_start_time; OR if shift crosses midnight (e.g. start 19:00, end 07:00), end may be < start — Agent 2 handles via `shift_date + 1 day + shift_end_time`; null if shift_start_time is null | UTC; inferred if not explicit |
| `shift_duration_hours` | decimal | Yes | Computed: (shift_end_time - shift_start_time) in hours; read-only | Range 1.0–24.0 |
| `unit_type` | UnitType enum | Yes | — | `UNKNOWN` triggers ambiguity flag |
| `urgency` | Urgency enum | Yes | Default `STANDARD` | See Urgency enum rules above |
| `required_credentials` | list[CredentialRequirement] | Yes | Min 1 item | At least one hard-required credential must be present |
| `preferred_credentials` | list[CredentialRequirement] | No | — | Soft preferences (nice to have) |
| `special_notes` | string | No | Max 2000 chars | Any additional requirements not captured in structured fields |
| `status` | ShiftRequestStatus enum | Yes | Default `PENDING_MATCH` | See state machine below |
| `confidence_score` | ConfidenceScore | Yes | 0.0–1.0, 2 decimal places | Set by Agent 1 on creation |
| `flagged_ambiguities` | list[AmbiguityFlag] | No | — | Empty list if no ambiguities |
| `created_at` | ISO 8601 timestamp (UTC) | Yes | Immutable, set on creation | — |
| `updated_at` | ISO 8601 timestamp (UTC) | Yes | Updated on any modification | — |
| `parsed_by` | enum [`AGENT_1`, `COORDINATOR`] | Yes | Immutable | `COORDINATOR` if coordinator manually created or corrected |
| `coordinator_id` | string | No | Required if `parsed_by = COORDINATOR` | FK to coordinator who created or corrected the record |

### CredentialRequirement (sub-entity)

| Field | Type | Required | Constraints |
|---|---|---|---|
| `credential_category` | CredentialCategory enum | Yes | Must be a valid enum value |
| `inference_confidence` | ConfidenceScore | Yes | Confidence of this specific inference (0.0–1.0) |

### AmbiguityFlag (sub-entity)

| Field | Type | Required | Constraints |
|---|---|---|---|
| `type` | AmbiguityType enum | Yes | See AmbiguityType below |
| `description` | string | Yes | Max 500 chars; human-readable explanation |
| `source_excerpt` | string | Yes | Max 300 chars; the specific text that triggered the flag |

**AmbiguityType (enum):** `CREDENTIAL_UNCLEAR`, `DATE_UNCLEAR`, `TIME_UNCLEAR`, `UNIT_TYPE_UNCLEAR`, `CONFLICTING_REQUIREMENTS`, `INSUFFICIENT_INFORMATION`, `DUPLICATE_SUSPECTED`

### ShiftRequestStatus state machine

```
PENDING_MATCH       → MATCHED (Agent 3 submits a candidate to the hospital; MatchingResult.status = SUBMITTED)
PENDING_MATCH       → CLARIFICATION_NEEDED (confidence < LOW threshold)
CLARIFICATION_NEEDED → PENDING_MATCH (coordinator reviews and approves parse)
CLARIFICATION_NEEDED → CANCELLED (coordinator determines request is invalid)
MATCHED             → FILLED (Agent 3 confirms hospital acceptance)
MATCHED             → CANCELLED (no suitable candidate found; coordinator decides)
FILLED              → [terminal]
CANCELLED           → [terminal]
```

No backwards transitions except `CLARIFICATION_NEEDED → PENDING_MATCH` (after coordinator review).

---

## Decision logic

### Credential category inference

The agent maps free-text descriptions to `CredentialCategory` values using LLM reasoning. Rules:

1. If the text contains an explicit, unambiguous credential name (e.g., "RN", "Registered Nurse", "ICU nurse") → infer with `inference_confidence ≥ 0.90`
2. If the text implies a credential by unit type (e.g., "needs someone for the ICU" without stating nurse type) → infer both `RN` and `ICU_CERTIFIED` as required, `inference_confidence 0.70–0.85`; flag ambiguity if nurse type is not stated
3. If the text uses non-standard shorthand (e.g., "critical care RN", "step-down nurse") → map to closest standard category; set `inference_confidence 0.70–0.85`; add `CREDENTIAL_UNCLEAR` flag
4. If credential cannot be inferred at all → add `INSUFFICIENT_INFORMATION` flag; set overall `confidence_score < 0.65`; route to clarification queue

**Credential inference must not assume** a credential category that is not at least implied by the text. When uncertain between two categories (e.g., `ICU_CERTIFIED` vs `ER_CERTIFIED`), include both as required and set `inference_confidence 0.70` for each, plus an `AMBIGUITY_FLAG` of type `CREDENTIAL_UNCLEAR`.

### Date/time resolution

Rules applied in priority order:

1. **Explicit date + time:** parse directly. Example: "January 15th, 7am–7pm" → `shift_date: 2026-01-15`, `shift_start_time: 07:00`, `shift_end_time: 19:00`
2. **Relative date reference:** resolve against request receipt timestamp (UTC). "Tomorrow" = receipt date + 1 day. "This Friday" = the next Friday on or after receipt date. "Next week Monday" = Monday of the following calendar week. If ambiguous (e.g., "Friday" when today is Friday) → flag `DATE_UNCLEAR`
3. **Partial time reference:** "nights" = 19:00–07:00 (next day). "days" = 07:00–19:00. "evenings" = 15:00–23:00. These are defaults; if hospital profile specifies different standard shift times, use those.
4. **No time specified:** infer `shift_start_time` and `shift_end_time` as `NULL`; add `TIME_UNCLEAR` ambiguity flag; do not default silently
5. **"ASAP" or no date:** set `urgency = CRITICAL`, do not set `shift_date`; add `DATE_UNCLEAR` flag; route to clarification queue immediately

> **[ASSUMED]** Standard shift time mappings (nights/days/evenings) default to common US hospital patterns. Must be overridable per hospital profile. If hospital profile contains custom shift time mappings, those take precedence.

### Confidence scoring model

Overall `confidence_score` is the weighted minimum of component scores:

| Component | Weight | Score = 1.0 if | Score = 0.0 if |
|---|---|---|---|
| Credential inference | 0.40 | All credentials inferred with `inference_confidence ≥ 0.90` | Any credential cannot be inferred |
| Date resolution | 0.30 | Explicit date and time in source text | Date cannot be resolved |
| Unit type identification | 0.20 | Unit type unambiguous | Unit type is `UNKNOWN` |
| Completeness | 0.10 | All required fields populated | Any required field missing |

`confidence_score = sum(component_score × weight)` for all components. Rounded to 2 decimal places.

If any component scores 0.0, the overall confidence_score is capped at 0.64 (routes to clarification queue regardless of other component scores).

### Duplicate detection

Before creating a new ShiftRequest, query existing records for the same `hospital_id` where `shift_date`, `shift_start_time`, and at least one `required_credential` match. If a match exists:
- If existing record status is `PENDING_MATCH` or `MATCHED`: add `DUPLICATE_SUSPECTED` flag; do not auto-cancel; route to coordinator review
- If existing record status is `FILLED` or `CANCELLED`: proceed with new record (replacement shift)

---

## Delegation boundaries

| Decision | Owner | Condition | Action |
|---|---|---|---|
| Parse free text → ShiftRequest | Agent [Agent + Log] | Always | Parse and log with source text |
| Route to matching | Agent [Agent + Log] | `confidence_score ≥ 0.65` | Set status `PENDING_MATCH`; pass to Agent 2 |
| Route to clarification | Agent [Agent + Log] | `confidence_score < 0.65` | Set status `CLARIFICATION_NEEDED`; add to coordinator queue |
| Flag ambiguity (MEDIUM confidence) | Agent [Agent + Log] | `0.65 ≤ confidence_score < 0.85` | Pass to Agent 2 with flags visible to coordinator in review interface |
| Resolve ambiguity | Coordinator [Human] | Any `CLARIFICATION_NEEDED` status | Coordinator edits ShiftRequest fields; sets `parsed_by = COORDINATOR`; status → `PENDING_MATCH` |
| Cancel invalid request | Coordinator [Human] | `CLARIFICATION_NEEDED` where request is determined invalid | Set status `CANCELLED`; log reason |

**Escalation timeout:** If a `CLARIFICATION_NEEDED` record has not been resolved by a coordinator within 60 minutes, a notification is sent to the coordinator queue supervisor. Configurable via `CLARIFICATION_TIMEOUT_MINUTES` (default 60).

---

## Integration contracts

### ServiceNow — read

> **[ASSUMED]** The following contract is based on standard ServiceNow REST API patterns. Exact table name, field names, and auth method must be confirmed with Aaron (IT) before build.

**Purpose:** Poll ServiceNow for new shift request tickets.

**Trigger:** Polling every 2 minutes. Configurable via `SERVICENOW_POLL_INTERVAL_SECONDS` (default 120). [ASSUMED — confirm with Aaron whether webhook push is available; if so, prefer webhook over polling]

**Endpoint:** `GET ${SERVICENOW_BASE_URL}/api/now/table/${SHIFT_REQUEST_TABLE_NAME}`

**Authentication:** OAuth 2.0 Bearer token. Token sourced from `SERVICENOW_OAUTH_TOKEN` environment variable. Never hardcoded. [ASSUMED — confirm auth method with Aaron]

**Query parameters:**
```
sysparm_query=state=open^sys_created_on>javascript:gs.minutesAgoStart(${POLL_INTERVAL_MINUTES})
sysparm_fields=sys_id,description,u_hospital_id,sys_created_on
sysparm_limit=100
```

**Expected response (HTTP 200):**
```json
{
  "result": [
    {
      "sys_id": "string",
      "description": "string",
      "u_hospital_id": "string",
      "sys_created_on": "ISO 8601 timestamp"
    }
  ]
}
```

**Error handling:**

| HTTP status | Action |
|---|---|
| 200 | Process results |
| 204 | No new tickets; log poll with 0 results; no action |
| 401 / 403 | Log error; alert ops; pause polling; do not retry until token refreshed |
| 429 | Honour `Retry-After` header; backoff and retry |
| 5xx | Retry once after 30 seconds; if retry fails, log error and skip poll cycle; alert if 3 consecutive poll cycles fail |
| Timeout (> 10 seconds) | Treat as 5xx |

**Rate limit:** [ASSUMED — confirm with Aaron. Default assumption: 60 requests/minute. Agent makes at most 1 poll request per poll cycle.]

### Hospital profile — read

**Purpose:** Retrieve hospital context to assist credential inference and date resolution.

**Endpoint:** `GET ${MEDFLEX_API_BASE_URL}/hospitals/${hospital_id}/profile`

**Authentication:** Internal API key. Sourced from `MEDFLEX_API_KEY` environment variable.

**Expected response fields used:**
- `standard_shift_times`: object with keys `days`, `nights`, `evenings` mapping to `{start: HH:MM, end: HH:MM}`
- `preferred_credential_categories`: list[CredentialCategory]
- `common_unit_types`: list[UnitType]
- `coordinates`: object `{lat: decimal, lng: decimal}` — used by Agent 2 for proximity calculation; must be present in hospital profile

**Fallback:** If hospital profile is unavailable, proceed with parse using default shift time mappings. Log warning. Do not block ShiftRequest creation.

### LLM — parse

**Model:** `claude-haiku-4-5-20251001` (default). Configurable via `INTAKE_LLM_MODEL` environment variable. Use `claude-sonnet-4-6` for requests flagged as `CRITICAL` urgency or where hospital profile indicates high complexity.

**System prompt:** Loaded from `prompts/intake_parse_system.txt` at runtime (not build time). Changes to the prompt require review before deployment.

**Required input context per call:**
- Source text (max 5000 chars)
- Hospital profile summary (shift times, common credentials)
- Current date and time (UTC) for relative date resolution
- CredentialCategory enum values (embedded in system prompt)

**Max input tokens:** 4000 (source text ~1000 + hospital profile ~500 + system prompt ~2500)

**Required LLM output schema** — enforce via JSON mode or tool use. Do not parse free text:

```json
{
  "shift_date": "YYYY-MM-DD or null",
  "shift_start_time": "HH:MM or null",
  "shift_end_time": "HH:MM or null",
  "unit_type": "UnitType enum value",
  "urgency": "Urgency enum value",
  "required_credentials": [
    {
      "credential_category": "CredentialCategory enum value",
      "inference_confidence": 0.0
    }
  ],
  "preferred_credentials": [],
  "special_notes": "string or null",
  "overall_confidence_score": 0.0,
  "flagged_ambiguities": [
    {
      "type": "AmbiguityType enum value",
      "description": "string",
      "source_excerpt": "string"
    }
  ]
}
```

If LLM output fails JSON schema validation or is missing required fields: do not create ShiftRequest; log failure with `servicenow_ticket_id` and raw LLM response; route ticket to coordinator manual queue.

**LLM call timeout:** 15 seconds. On timeout: retry once after 5 seconds. If retry fails: route to coordinator manual queue; log incident.

---

## Validation design

### Happy path

**Scenario:** Standard ICU shift request, explicit date and time, single credential.

**Input (ServiceNow description):** `"Need ICU-trained RN for nights January 20th, 7pm to 7am. St. Mary's downtown."`

**Expected output:**
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
  "overall_confidence_score": 0.95,
  "flagged_ambiguities": []
}
```

Status: `PENDING_MATCH`. Passed to Agent 2.

---

### Edge cases

**EC-1: Relative date — "ASAP"**
- Input: `"Need RN ASAP, med-surg floor"`
- Expected: `shift_date = null`, `urgency = CRITICAL`, ambiguity flag `DATE_UNCLEAR`, `confidence_score < 0.65`, status `CLARIFICATION_NEEDED`

**EC-2: Credential not in taxonomy — non-standard shorthand**
- Input: `"Step-down unit nurse, 12-hour day shift next Monday"`
- Expected: `unit_type = GENERAL`, `required_credentials = [{RN, 0.75}]`, ambiguity flag `CREDENTIAL_UNCLEAR` with `source_excerpt = "Step-down unit nurse"`, `confidence_score 0.65–0.75`, status `PENDING_MATCH` with flags visible to coordinator

**EC-3: Conflicting requirements**
- Input: `"Need ICU nurse for general ward, evening shift tomorrow"`
- Expected: ambiguity flag `CONFLICTING_REQUIREMENTS` with description noting ICU credential + general ward mismatch; `confidence_score < 0.65`; status `CLARIFICATION_NEEDED`

**EC-4: Duplicate detection**
- Input: New ticket for same hospital, same date, same credential as existing `PENDING_MATCH` record
- Expected: `DUPLICATE_SUSPECTED` flag added; new ShiftRequest created with status `CLARIFICATION_NEEDED`; coordinator notified; existing record not modified

**EC-5: No time specified**
- Input: `"RN needed for pediatric ward on February 3rd"`
- Expected: `shift_start_time = null`, `shift_end_time = null`, ambiguity flag `TIME_UNCLEAR`; `confidence_score 0.65–0.84` (date and credential are clear); status `PENDING_MATCH` with `TIME_UNCLEAR` flag visible to coordinator

**EC-6: Unknown hospital ID**
- Input: ServiceNow ticket with `u_hospital_id` not in hospital registry
- Expected: ShiftRequest creation blocked; log error with `servicenow_ticket_id`; ticket routed to coordinator manual queue; do not proceed to Agent 2

**EC-7: Multiple shifts in one request**
- Input: `"Need 3 ICU RNs for nights the 20th, 21st, and 22nd"`
- Expected: three separate ShiftRequest entities created (one per shift date); each has status `PENDING_MATCH`; each references the same `servicenow_ticket_id` with `ticket_sequence_num` = 1, 2, 3 respectively; `special_notes` on each records "Part of 3-shift block request"; idempotency check uses `(servicenow_ticket_id, ticket_sequence_num)` combination, not `servicenow_ticket_id` alone

---

### Failure modes

**FM-1: ServiceNow API unavailable**
- Trigger: 3 consecutive poll cycles return 5xx or timeout
- Expected: ops alert sent via `OPS_ALERT_CHANNEL` (configurable); polling pauses for `SERVICENOW_OUTAGE_PAUSE_MINUTES` (default 15); coordinator team notified to monitor ServiceNow manually; automatic resume after pause

**FM-2: LLM parse failure (invalid JSON output)**
- Trigger: LLM returns non-JSON or schema-invalid output after one retry
- Expected: ShiftRequest not created; `servicenow_ticket_id` logged with raw LLM response and error type; ticket routed to coordinator manual queue; incident logged for model quality monitoring

**FM-3: Hospital profile unavailable**
- Trigger: hospital profile API returns 4xx or 5xx
- Expected: proceed with parse using default shift time mappings; log warning with `hospital_id`; no blocking; coordinator will see the warning in the review interface

---

## Assumptions register

| ID | Assumption | Why it matters | If wrong | Status |
|---|---|---|---|---|
| A1 | CredentialCategory taxonomy matches MedFlex's internal credential categories | Drives all credential inference logic | Inference maps to wrong categories; matching produces wrong nurses | [FLAGGED] — validate with Kim + Linda before build |
| A2 | ServiceNow is accessible via REST API with sufficient field exposure | Agent reads from ServiceNow programmatically | Agent cannot read requests; entire pipeline blocked | [FLAGGED] — confirm with Aaron; is build blocker |
| A3 | Hospital profiles are accessible via internal API and include shift time preferences | Improves date/time inference accuracy | Agent uses default shift times; slightly lower confidence scores | [ASSUMED] — confirm with Aaron |
| A4 | Standard shift time defaults (days: 07:00–19:00, nights: 19:00–07:00) are a reasonable fallback | Used when hospital profile is missing or shift time not stated | Minor inference errors for hospitals with non-standard shifts | [ASSUMED] |
| A5 | ServiceNow ticket field `u_hospital_id` reliably identifies the requesting hospital | Required for hospital profile lookup | Hospital profile cannot be retrieved; credential inference is less accurate | [FLAGGED] — confirm field name with Aaron |
| A6 | LLM model `claude-haiku-4-5-20251001` achieves acceptable parsing accuracy on healthcare staffing requests | Drives build cost model | Needs upgrade to Sonnet; inference cost increases | [ASSUMED] — validate with sample parse tests before production |

---

## Economics

| Operation | Type | Estimated cost | Frequency | Notes |
|---|---|---|---|---|
| LLM parse call (Haiku) | Generate | ~$0.001 per request | ~960/day | Low cost per call; high volume |
| ServiceNow poll | Coordinate | Negligible API cost | 720/day (every 2 min) | Confirm rate limits with Aaron |
| Hospital profile read | Coordinate | Negligible | ~960/day | Cache per hospital per session; invalidate after 1 hour |

**Caching:** Hospital profiles must be cached in memory with a 1-hour TTL. Do not call hospital profile API per ticket — call once per hospital per poll cycle. At most 8–10 distinct hospitals expected in a given hour.

**Circuit breaker:** If LLM API costs exceed `DAILY_LLM_COST_LIMIT_USD` (default $50), halt automatic processing and alert ops. All incoming tickets route to coordinator manual queue until limit is reset.

---

## Governance & audit

**Audit trail:** Every ShiftRequest creation and status transition must be logged with:
- `timestamp` (UTC, ISO 8601)
- `servicenow_ticket_id`
- `action` (enum: `CREATED`, `STATUS_CHANGED`, `COORDINATOR_CORRECTED`, `AMBIGUITY_FLAGGED`, `ESCALATED`)
- `from_status` / `to_status` (on status changes)
- `agent_version` (for model quality tracking)
- `confidence_score` at time of creation
- `coordinator_id` (if human action)

**Retention:** Audit logs retained for 3 years minimum. ShiftRequest records and `source_text` retained for 1 year after shift date. [ASSUMED — confirm retention requirements with Linda (Compliance)]

**HITL checkpoints:**
- Any record with `confidence_score < 0.65` must not proceed to Agent 2 without coordinator review
- Any record with `DUPLICATE_SUSPECTED` flag must be reviewed by coordinator before matching proceeds
- Coordinator corrections are logged with `coordinator_id`; corrected records are marked `parsed_by = COORDINATOR`

**Data handling:** `source_text` contains free-text from hospitals and may include patient-identifiable information (e.g., patient room numbers, diagnosis hints). Treat `source_text` as potentially containing PHI. Do not log `source_text` in plain-text application logs — log only the `servicenow_ticket_id` reference. [FLAGGED — confirm HIPAA data handling requirements with Linda]

---

## Build context

> This section provides all implementation decisions a builder needs to start without asking clarifying questions. It resolves every [ASSUMED] infrastructure gap in this spec.

### Stack

- **Language:** Python 3.11
- **Dependencies** (`requirements.txt`):

```
anthropic>=0.40.0
psycopg2-binary>=2.9.9
pydantic>=2.5.0
python-dotenv>=1.0.0
httpx>=0.27.0
```

### Project structure

```
medflex-agent1/
├── .env                           # environment variables (copy from table below)
├── requirements.txt
├── schema.sql                     # run once to create tables
├── prompts/
│   └── intake_parse_system.txt    # system prompt — full content defined below
├── fixtures/
│   ├── servicenow_fixture.json    # mock ServiceNow tickets for local testing
│   └── hospital_profiles.json     # mock hospital profiles for local testing
├── agent1_intake.py               # main polling loop
├── models.py                      # Pydantic models matching entity definitions above
├── db.py                          # PostgreSQL connection pool
├── servicenow_client.py           # ServiceNow polling (real or stub)
└── hospital_api.py                # hospital profile fetch with 1-hour cache
```

### Environment variables — full list with defaults

| Variable | Default | Required | Notes |
|---|---|---|---|
| `DATABASE_URL` | — | Yes | e.g. `postgresql://user:pass@localhost:5432/medflex` |
| `ANTHROPIC_API_KEY` | — | Yes | Anthropic API key |
| `SERVICENOW_BASE_URL` | — | Yes | Set to `mock` to use fixture file instead of real ServiceNow |
| `SERVICENOW_OAUTH_TOKEN` | — | Yes if not mock | ServiceNow OAuth Bearer token |
| `SHIFT_REQUEST_TABLE_NAME` | `u_shift_requests` | No | ServiceNow table name |
| `SERVICENOW_POLL_INTERVAL_SECONDS` | `120` | No | How often to poll for new tickets |
| `MEDFLEX_API_BASE_URL` | — | Yes | Set to `mock` to use fixture file instead of real API |
| `MEDFLEX_API_KEY` | — | Yes if not mock | Internal MedFlex API key |
| `INTAKE_LLM_MODEL` | `claude-haiku-4-5-20251001` | No | LLM model for parsing |
| `INTAKE_CONFIDENCE_HIGH_THRESHOLD` | `0.85` | No | — |
| `INTAKE_CONFIDENCE_LOW_THRESHOLD` | `0.65` | No | — |
| `CLARIFICATION_TIMEOUT_MINUTES` | `60` | No | Escalation timeout for unresolved CLARIFICATION_NEEDED |
| `OPS_ALERT_WEBHOOK_URL` | — | Yes | Webhook URL for ops alerts; see format below |
| `DAILY_LLM_COST_LIMIT_USD` | `50` | No | Circuit breaker threshold |
| `AGENT_VERSION` | `0.1.0` | No | Logged in audit trail |

### OPS_ALERT_CHANNEL — implementation

Send `POST` to `OPS_ALERT_WEBHOOK_URL` with `Content-Type: application/json`:

```json
{
  "alert_type": "SERVICENOW_OUTAGE | LLM_PARSE_FAILURE | COST_LIMIT_EXCEEDED",
  "message": "human-readable description",
  "timestamp": "ISO 8601 UTC",
  "details": {}
}
```

If the POST fails (any error), log the error and continue — ops alerting must never block the main processing loop. If `OPS_ALERT_WEBHOOK_URL` is not set, write the alert to stderr only.

### Coordinator clarification queue — implementation

Not a separate table. The coordinator queue is this query:

```sql
SELECT * FROM shift_requests
WHERE status = 'CLARIFICATION_NEEDED'
ORDER BY created_at ASC;
```

Agent 1 only sets `status = 'CLARIFICATION_NEEDED'` and inserts rows into `ambiguity_flags`. No additional notification mechanism is required beyond the database state for the initial build.

### Database schema — run `schema.sql` once before starting

```sql
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE shift_requests (
    id                   UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    servicenow_ticket_id VARCHAR(64)  NOT NULL,  -- NOT UNIQUE: one ticket can produce multiple records (see EC-7)
    ticket_sequence_num  SMALLINT     NOT NULL DEFAULT 1,  -- 1-based index within a multi-shift ticket; 1 for single-shift tickets
    hospital_id          VARCHAR(255) NOT NULL,
    source_text          TEXT         NOT NULL CHECK (char_length(source_text) <= 5000),
    hospital_location    JSONB,                  -- {lat: decimal, lng: decimal}; copied from hospital profile at parse time; used by Agent 2 for proximity scoring
    shift_date           DATE,
    shift_start_time     TIME,
    shift_end_time       TIME,
    unit_type            VARCHAR(50)  NOT NULL DEFAULT 'UNKNOWN',
    urgency              VARCHAR(20)  NOT NULL DEFAULT 'STANDARD',
    special_notes        TEXT         CHECK (char_length(special_notes) <= 2000),
    status               VARCHAR(50)  NOT NULL DEFAULT 'PENDING_MATCH',
    confidence_score     NUMERIC(3,2) NOT NULL CHECK (confidence_score BETWEEN 0.0 AND 1.0),
    parsed_by            VARCHAR(20)  NOT NULL DEFAULT 'AGENT_1',
    coordinator_id       VARCHAR(255),
    created_at           TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE credential_requirements (
    id                   UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    shift_request_id     UUID         NOT NULL REFERENCES shift_requests(id) ON DELETE CASCADE,
    credential_category  VARCHAR(50)  NOT NULL,
    inference_confidence NUMERIC(3,2) NOT NULL CHECK (inference_confidence BETWEEN 0.0 AND 1.0),
    is_required          BOOLEAN      NOT NULL DEFAULT TRUE
);

CREATE TABLE ambiguity_flags (
    id               UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    shift_request_id UUID         NOT NULL REFERENCES shift_requests(id) ON DELETE CASCADE,
    type             VARCHAR(50)  NOT NULL,
    description      VARCHAR(500) NOT NULL,
    source_excerpt   VARCHAR(300) NOT NULL
);

CREATE TABLE audit_log (
    id                   UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type          VARCHAR(50)  NOT NULL,
    entity_id            UUID         NOT NULL,
    timestamp            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    action               VARCHAR(50)  NOT NULL,
    from_status          VARCHAR(50),
    to_status            VARCHAR(50),
    agent_version        VARCHAR(20),
    confidence_score     NUMERIC(3,2),
    coordinator_id       VARCHAR(255),
    servicenow_ticket_id VARCHAR(64),
    metadata             JSONB
);
```

### ServiceNow stub — `fixtures/servicenow_fixture.json`

When `SERVICENOW_BASE_URL=mock`, skip HTTP calls entirely. Read this file on each poll cycle and process any ticket whose `sys_id` is not already in `shift_requests.servicenow_ticket_id`.

```json
[
  {
    "sys_id": "ticket_001",
    "description": "Need ICU-trained RN for nights January 20th, 7pm to 7am. St. Mary's downtown.",
    "u_hospital_id": "hospital_stmarys_01",
    "sys_created_on": "2026-01-19T10:00:00Z"
  },
  {
    "sys_id": "ticket_002",
    "description": "RN needed ASAP for med-surg floor",
    "u_hospital_id": "hospital_metro_02",
    "sys_created_on": "2026-01-19T11:30:00Z"
  },
  {
    "sys_id": "ticket_003",
    "description": "Pediatric RN, day shift, February 3rd",
    "u_hospital_id": "hospital_stmarys_01",
    "sys_created_on": "2026-01-19T12:00:00Z"
  }
]
```

### Hospital profile stub — `fixtures/hospital_profiles.json`

When `MEDFLEX_API_BASE_URL=mock`, return the matching entry from this file keyed by `hospital_id`. If the hospital is not found, use the `_default` entry.

```json
{
  "_default": {
    "standard_shift_times": {
      "days":    {"start": "07:00", "end": "19:00"},
      "nights":  {"start": "19:00", "end": "07:00"},
      "evenings":{"start": "15:00", "end": "23:00"}
    },
    "preferred_credential_categories": ["RN"],
    "common_unit_types": ["MED_SURG", "GENERAL"],
    "coordinates": {"lat": 40.7128, "lng": -74.0060}
  },
  "hospital_stmarys_01": {
    "standard_shift_times": {
      "days":    {"start": "07:00", "end": "19:00"},
      "nights":  {"start": "19:00", "end": "07:00"},
      "evenings":{"start": "15:00", "end": "23:00"}
    },
    "preferred_credential_categories": ["RN", "ICU_CERTIFIED", "ACLS"],
    "common_unit_types": ["ICU", "ER", "MED_SURG"],
    "coordinates": {"lat": 40.7549, "lng": -73.9840}
  },
  "hospital_metro_02": {
    "standard_shift_times": {
      "days":    {"start": "07:00", "end": "19:00"},
      "nights":  {"start": "19:00", "end": "07:00"},
      "evenings":{"start": "15:00", "end": "23:00"}
    },
    "preferred_credential_categories": ["RN", "LPN"],
    "common_unit_types": ["MED_SURG", "GENERAL", "PSYCH"],
    "coordinates": {"lat": 40.6892, "lng": -74.0445}
  }
}
```

### System prompt — write verbatim to `prompts/intake_parse_system.txt`

```
You are a healthcare staffing intake agent for MedFlex, a US healthcare staffing agency.

Your task: parse a free-text hospital shift request into a structured JSON object.

You will receive a JSON input with three fields:
- "source_text": raw text of the shift request
- "hospital_profile": object with "standard_shift_times" (keys: "days", "nights", "evenings",
  each with "start" and "end" in HH:MM 24-hour format) and "common_unit_types" (list of strings)
- "current_datetime_utc": current UTC datetime in ISO 8601 format

Return ONLY the JSON object specified in OUTPUT SCHEMA below.
No explanation, no markdown code fences, no text outside the JSON.

VALID CREDENTIAL_CATEGORY VALUES (use only these exact strings):
RN, LPN, CNA, NP, CRNA, ICU_CERTIFIED, ER_CERTIFIED, OR_CERTIFIED, PEDS_CERTIFIED,
ONCOLOGY_CERTIFIED, L_D_CERTIFIED, PSYCH_CERTIFIED, BLS, ACLS, PALS

VALID UNIT_TYPE VALUES (use only these exact strings):
ICU, ER, OR, MED_SURG, PEDIATRIC, ONCOLOGY, LABOR_DELIVERY, PSYCH, GENERAL, UNKNOWN

VALID URGENCY VALUES: STANDARD, URGENT, CRITICAL

VALID AMBIGUITY TYPE VALUES:
CREDENTIAL_UNCLEAR, DATE_UNCLEAR, TIME_UNCLEAR, UNIT_TYPE_UNCLEAR,
CONFLICTING_REQUIREMENTS, INSUFFICIENT_INFORMATION, DUPLICATE_SUSPECTED

PARSING RULES:

1. DATE RESOLUTION: Resolve all relative dates against current_datetime_utc.
   "Tomorrow" = current date + 1 day.
   "This Friday" = next Friday on or after today.
   "Next week Monday" = Monday of the following calendar week.
   If the date reference is ambiguous, set shift_date to null and add a DATE_UNCLEAR flag.

2. TIME RESOLUTION: Use hospital_profile.standard_shift_times if provided.
   Otherwise: "nights" = 19:00-07:00, "days" = 07:00-19:00, "evenings" = 15:00-23:00.
   If no time stated, set both to null and add TIME_UNCLEAR. Never default silently.

3. CREDENTIAL INFERENCE: Map free text to the closest valid CredentialCategory.
   Set inference_confidence >= 0.90 for explicit names ("RN", "Registered Nurse").
   Set 0.70-0.85 for implied ("need someone for the ICU" implies RN + ICU_CERTIFIED)
   or non-standard shorthand ("critical care RN", "step-down nurse").
   When uncertain between two categories, include both with inference_confidence 0.70 each
   and add CREDENTIAL_UNCLEAR flag.
   If no credential can be inferred at all, add INSUFFICIENT_INFORMATION and set
   overall_confidence_score below 0.65.

4. URGENCY: Set CRITICAL if shift_date is null or text contains (case-insensitive):
   "ASAP", "immediately", "emergency cover".
   Set URGENT if shift is 24-48 hours from current_datetime_utc or text contains "urgent".
   Otherwise STANDARD.

5. CONFLICTING REQUIREMENTS: If requirements contradict each other (e.g., ICU-trained nurse
   for a general ward), add CONFLICTING_REQUIREMENTS and set overall_confidence_score < 0.65.

6. CONFIDENCE SCORING:
   Compute components:
   - credential_component: 1.0 if all >= 0.90; 0.5 if any between 0.70-0.89; 0.0 if any unresolvable
   - date_component: 1.0 if explicit; 0.5 if resolved from relative reference; 0.0 if null
   - unit_type_component: 1.0 if unambiguous; 0.5 if inferred; 0.0 if UNKNOWN
   - completeness_component: 1.0 if all required fields populated; 0.5 if minor fields missing;
     0.0 if critical fields (shift_date or required_credentials) missing
   overall = (credential * 0.40) + (date * 0.30) + (unit_type * 0.20) + (completeness * 0.10)
   If any component is 0.0, cap overall at 0.64 regardless.
   Round to 2 decimal places.

7. NULL FIELDS: Use JSON null (not empty string) for missing shift_date, shift_start_time,
   shift_end_time, and special_notes.

OUTPUT SCHEMA (return exactly this structure, no extra fields):
{
  "shift_date": "YYYY-MM-DD or null",
  "shift_start_time": "HH:MM or null",
  "shift_end_time": "HH:MM or null",
  "unit_type": "UnitType value",
  "urgency": "Urgency value",
  "required_credentials": [
    {"credential_category": "CredentialCategory value", "inference_confidence": 0.0}
  ],
  "preferred_credentials": [],
  "special_notes": "string or null",
  "overall_confidence_score": 0.0,
  "flagged_ambiguities": [
    {"type": "AmbiguityType value", "description": "string", "source_excerpt": "string"}
  ]
}
```

### How to run

```bash
# 1. Create and activate virtualenv
python3.11 -m venv venv && source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create database tables
psql $DATABASE_URL -f schema.sql

# 4. Copy and fill in environment variables
cp .env.example .env
# Set DATABASE_URL, ANTHROPIC_API_KEY
# Set SERVICENOW_BASE_URL=mock and MEDFLEX_API_BASE_URL=mock for local testing

# 5. Run the agent
python agent1_intake.py
```

The agent runs as a long-lived polling loop. It polls every `SERVICENOW_POLL_INTERVAL_SECONDS`, processes any new tickets, and logs results to stdout. Stop with Ctrl+C.
