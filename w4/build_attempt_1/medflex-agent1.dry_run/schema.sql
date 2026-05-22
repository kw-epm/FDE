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

-- Unique index on (servicenow_ticket_id, ticket_sequence_num) for idempotency (per EC-7).
CREATE UNIQUE INDEX shift_requests_ticket_seq_idx
    ON shift_requests (servicenow_ticket_id, ticket_sequence_num);

CREATE INDEX shift_requests_status_idx ON shift_requests (status);
CREATE INDEX shift_requests_hospital_date_idx ON shift_requests (hospital_id, shift_date);

CREATE TABLE credential_requirements (
    id                   UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    shift_request_id     UUID         NOT NULL REFERENCES shift_requests(id) ON DELETE CASCADE,
    credential_category  VARCHAR(50)  NOT NULL,
    inference_confidence NUMERIC(3,2) NOT NULL CHECK (inference_confidence BETWEEN 0.0 AND 1.0),
    is_required          BOOLEAN      NOT NULL DEFAULT TRUE
);

CREATE INDEX credential_requirements_shift_idx
    ON credential_requirements (shift_request_id);

CREATE TABLE ambiguity_flags (
    id               UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    shift_request_id UUID         NOT NULL REFERENCES shift_requests(id) ON DELETE CASCADE,
    type             VARCHAR(50)  NOT NULL,
    description      VARCHAR(500) NOT NULL,
    source_excerpt   VARCHAR(300) NOT NULL
);

CREATE INDEX ambiguity_flags_shift_idx
    ON ambiguity_flags (shift_request_id);

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

CREATE INDEX audit_log_entity_idx ON audit_log (entity_type, entity_id);
CREATE INDEX audit_log_ticket_idx ON audit_log (servicenow_ticket_id);
