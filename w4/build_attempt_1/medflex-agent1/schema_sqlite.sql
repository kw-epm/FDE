-- SQLite adaptation of schema.sql. Postgres is unavailable in this build env.
-- Differences from the spec schema:
--   * UUIDs are stored as TEXT (caller generates with uuid.uuid4()).
--   * JSONB -> TEXT (caller JSON-encodes).
--   * No CHECK on char_length; enforced in application layer via pydantic.
--   * TIMESTAMPTZ -> TEXT with ISO-8601 UTC strings.

CREATE TABLE IF NOT EXISTS shift_requests (
    id                   TEXT    PRIMARY KEY,
    servicenow_ticket_id TEXT    NOT NULL,
    ticket_sequence_num  INTEGER NOT NULL DEFAULT 1,
    hospital_id          TEXT    NOT NULL,
    source_text          TEXT    NOT NULL,
    hospital_location    TEXT,
    shift_date           TEXT,
    shift_start_time     TEXT,
    shift_end_time       TEXT,
    unit_type            TEXT    NOT NULL DEFAULT 'UNKNOWN',
    urgency              TEXT    NOT NULL DEFAULT 'STANDARD',
    special_notes        TEXT,
    status               TEXT    NOT NULL DEFAULT 'PENDING_MATCH',
    confidence_score     REAL    NOT NULL,
    parsed_by            TEXT    NOT NULL DEFAULT 'AGENT_1',
    coordinator_id       TEXT,
    created_at           TEXT    NOT NULL,
    updated_at           TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS credential_requirements (
    id                   TEXT    PRIMARY KEY,
    shift_request_id     TEXT    NOT NULL REFERENCES shift_requests(id) ON DELETE CASCADE,
    credential_category  TEXT    NOT NULL,
    inference_confidence REAL    NOT NULL,
    is_required          INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS ambiguity_flags (
    id               TEXT NOT NULL PRIMARY KEY,
    shift_request_id TEXT NOT NULL REFERENCES shift_requests(id) ON DELETE CASCADE,
    type             TEXT NOT NULL,
    description      TEXT NOT NULL,
    source_excerpt   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_log (
    id                   TEXT NOT NULL PRIMARY KEY,
    entity_type          TEXT NOT NULL,
    entity_id            TEXT NOT NULL,
    timestamp            TEXT NOT NULL,
    action               TEXT NOT NULL,
    from_status          TEXT,
    to_status            TEXT,
    agent_version        TEXT,
    confidence_score     REAL,
    coordinator_id       TEXT,
    servicenow_ticket_id TEXT,
    metadata             TEXT
);

CREATE INDEX IF NOT EXISTS idx_sr_ticket_seq ON shift_requests(servicenow_ticket_id, ticket_sequence_num);
CREATE INDEX IF NOT EXISTS idx_sr_hospital_date ON shift_requests(hospital_id, shift_date);
