# Deliverable 4 — Shared Entity Glossary (referenced by 04a and 04b)

**Author:** Tamas Kiss
**Engagement:** MedFlex agentic transformation  
**Date:** 2026-05-13
**Gate:** Gate 3 — Final submission

---

This glossary is **shared by both capability specifications** (`04a-capability-spec-parallel-submit.md` and `04b-capability-spec-classification.md`). Both specs use exactly these entity definitions — no parallel divergence. If a term is referenced in either spec, its canonical meaning is here.

## Core entities

### `ticket`
A hospital's incoming shift request, received via one of three channels: `email`, `portal`, or `phone_transcribed`. The ticket payload is `ticket.body` (free text) plus channel-specific metadata. Tickets land in ServiceNow; the agent reads them there.

| Field | Type | Notes |
|---|---|---|
| `ticket.id` | UUID | ServiceNow ticket identifier |
| `ticket.body` | TEXT | Free-text shift request (the input to classification) |
| `ticket.submission_channel` | ENUM[`email`, `portal`, `phone_transcribed`] | |
| `ticket.hospital_id` | FK → hospital | Sender |
| `ticket.received_at` | TIMESTAMP | |
| `previous_shift_request_id` | UUID? | Set if ticket modifies an earlier request |

### `classification`
The structured representation of a ticket after Capability 1 has parsed it. Six required structured fields plus confidence per field plus aggregate confidence.

| Field | Type | Notes |
|---|---|---|
| `shift_type` | controlled vocab (credential taxonomy) | e.g. "RN" |
| `unit` | controlled vocab (credential taxonomy) | e.g. "ICU" |
| `required_certifications` | TEXT[] (each from cert taxonomy) | e.g. ["CCRN", "RN"] |
| `start_at` | ISO 8601 UTC TIMESTAMP | |
| `end_at` | ISO 8601 UTC TIMESTAMP | |
| `count` | positive INTEGER | Nurses requested |
| `per_field_confidence` | FLOAT[6] | One per structured field |
| `classification_confidence` | FLOAT | Arithmetic mean of per_field_confidence |
| `hospital_preferences_referenced` | TEXT[] | Signals D1.2 lookup (Capability 2 territory) |

### `candidate` (nurse)
A nurse in MedFlex's roster. The candidate has credentials, availability, and per-hospital history.

| Field | Type | Notes |
|---|---|---|
| `candidate.id` | UUID | |
| `candidate.full_name` | TEXT | Authoritative source = credentialing_db |
| `candidate.certs` | TEXT[] | Credentials currently held |
| `candidate.licensed_states` | TEXT[] | States with active license |
| `candidate.license_expires_at_for_state` | MAP<state,DATE> | Per-state expiry |
| `candidate.compliance_status` | ENUM[`verified`, `pending`, `expired`] | |
| `candidate.availability` | object | window-typed; last_self_update_at |
| `candidate.block_list_for_nurse` | hospital_id[] | Hospitals nurse declines |
| `candidate.preferred_channel` | ENUM[`sms`, `email`, `phone`] | For holding signals |

### `shift_request` (open request)
An unfilled hospital request, derived from a classification. May map 1:N to submissions (parallel mode) or 1:1 (sequential mode).

| Field | Type | Notes |
|---|---|---|
| `shift_request.id` | UUID | |
| `shift_request.hospital_id` | FK → hospital | |
| `shift_request.window` | TIMESTAMP_RANGE | `start_at`..`end_at` |
| `shift_request.classification_id` | FK → classification | |
| `shift_request.state` | ENUM[`OPEN`, `MATCHED`, `FILLED`, `EXPIRED`] | |

### `submission`
An agent-sent submission of a candidate to a hospital for a specific shift_request. The submission state machine is the cross-capability spine.

| Field | Type | Notes |
|---|---|---|
| `submission.id` | UUID | |
| `submission.nurse_id` | FK → candidate | |
| `submission.shift_request_id` | FK → shift_request | |
| `submission.state` | ENUM (see below) | 11-state machine |
| `submission.confirm_evidence_strength` | FLOAT | LLM-classified inbound event strength |
| `submission.confirmed_at` | TIMESTAMP? | Set on confirm |
| `submission.acked_at` | TIMESTAMP? | Channel-level receipt |
| `submission.packet` | JSONB | The composed submission payload |

**`submission.state` ENUM (11 states):** `DRAFT`, `FACTUALITY_CHECK_PENDING`, `SUBMITTED`, `ACKED_BY_HOSPITAL`, `CONFIRMED`, `COMMITTED`, `COMMITTED_ELSEWHERE`, `REVOKE_PENDING`, `REVOKED`, `REVOKE_STUCK`, `INCONSISTENT_FROZEN`.

### `assignment`
The committed (nurse, hospital, shift) triple. Created on `submission.state = COMMITTED` after the revoke cascade passes the ledger-consistency check.

| Field | Type | Notes |
|---|---|---|
| `assignment.id` | UUID | |
| `assignment.nurse_id` | FK → candidate | |
| `assignment.hospital_id` | FK → hospital | |
| `assignment.shift_request_id` | FK → shift_request | |
| `assignment.state` | ENUM[`PENDING_COMMIT`, `COMMITTED`, `INCONSISTENT_FROZEN`] | |
| `assignment.committed_at` | TIMESTAMP | |

### `hospital`
Hospital entity with MSA review state (per ADR-1).

| Field | Type | Notes |
|---|---|---|
| `hospital.id` | UUID | |
| `hospital.msa_state` | ENUM[`green`, `yellow`, `red`, `unreviewed`] | Defaulted to `unreviewed`; agent treats `unreviewed` ≡ `yellow` until Legal sign-off |
| `hospital.exclusivity_window_minutes` | INTEGER | Defaulted to BLOCK; per-MSA Legal review sets the value |
| `hospital.preferred_channel` | ENUM[`email`, `portal`] | For submission delivery |
| `hospital.state` | TEXT | US state (for licensure check) |

### `credential_taxonomy`
Internal MedFlex artefact (snapshot pulled by Bootstrap Day 3 per PB-2 / DG-2). Single source of truth for `shift_type`, `unit`, and `required_certifications` controlled vocabularies.

### `submission_factuality_ledger`
Per-slot audit row written **before** any submission is sent (per Phase 10 R1 / Hartwood B-1 mitigation). Each row records the slot, its claimed value in the packet, the source-of-record value, and `exact_match` boolean.

| Field | Type | Notes |
|---|---|---|
| `ledger_row.submission_id` | FK → submission | |
| `ledger_row.slot` | TEXT | e.g. `nurse.full_name`, `start_at` |
| `ledger_row.claimed_value` | TEXT | What the packet says |
| `ledger_row.source_value` | TEXT | What source-of-record says |
| `ledger_row.exact_match` | BOOLEAN | TRUE iff identical |

## The 4 stores

The agent reads/writes against these 4 named stores:
- **`credentialing_db`** — source-of-record for nurse identity, credentials, licensed_states. Authoritative on `credential_present=true` per row.
- **`availability_db`** — nurse availability windows; `last_self_update_at` per nurse.
- **`request_db`** — historical hospital-shift-request data; supports `last_30d_fill_rate_per_hospital`, `recent_hospital_feedback` enrichments.
- **`hospital_preference_db`** — Wave-1-build store for hospital-specific preference records (preference_key, preference_value, confidence, state, authored_by).

## Channels

The agent operates over four channels with hospitals/nurses; no chatbot interface:
- **Email** — both directions (inbound: hospital responses; outbound: submissions, revokes, clarifications).
- **Hospital portal** — outbound submission; inbound portal events.
- **SMS** — outbound holding signals to nurses (per Phase 10 C-CA1).
- **ServiceNow** — inbound ticket payloads.

## Confidence-tag glossary

Used throughout both specs (carried verbatim from gate2 assumption-log convention):
- **HIGH** — substantively grounded in primary substrate (DG/PB/discovery confirmation); revisitation requires substrate-level change.
- **MED** — derived from substrate by reasonable inference; revisitation triggered by Pilot Week-1 calibration.
- **LOW** — placeholder / PENDING_CALIBRATION; revisitation expected during Phase 1.

## Cross-spec consistency

Both `04a-capability-spec-parallel-submit.md` and `04b-capability-spec-classification.md` reference this glossary **as their single source of entity truth.** If a term appears in either spec that is not defined here, it is either:
1. A within-spec local term (e.g. a variable in a code block), or
2. A defect — flag it.

The shared glossary discipline matches the pack's "**one glossary, not two**" requirement.
