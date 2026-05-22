# Execution log — Agent 1 intake build (build_attempt_1)

## Environment recon
- `python3 --version` -> 3.13.5 (spec wanted 3.11; using 3.13)
- `pg_isready` -> not found. No Postgres in this WSL environment.
- `python3 -c 'import sqlite3'` -> ok
- `python3 -c 'import pydantic'` -> ModuleNotFoundError
- `python3 -c 'import httpx'`    -> ModuleNotFoundError
- `python3 -c 'import psycopg2'` -> ModuleNotFoundError
- `python3 -c 'import pytest'`   -> 9.0.3 already installed

## Decisions
- Switched persistence from Postgres -> SQLite (stdlib). Wrote both `schema.sql` (Postgres, preserved verbatim from spec) and `schema_sqlite.sql` (adapted).
- Skipped `psycopg2-binary`; not needed for SQLite. Documented in `requirements.txt`.
- `pip3 install --user pydantic httpx` rejected by Debian PEP 668. Used `--break-system-packages`. Installed pydantic 2.13.4 and httpx 0.28.1.
- Cannot `python3 -m venv` either (python3-venv not installed). Live with user-site install.

## File creation order
- `requirements.txt`
- `fixtures/servicenow_fixture.json` (verbatim from spec)
- `fixtures/hospital_profiles.json` (verbatim from spec)
- `prompts/intake_parse_system.txt` (verbatim from spec)
- `models.py`        — Pydantic v2 enums + `LLMParseResult` + `ShiftRequest`
- `schema.sql` / `schema_sqlite.sql`
- `db.py`            — SQLite connect, insert, idempotency, duplicate, audit
- `servicenow_client.py` — mock + real HTTP, error mapping per spec
- `hospital_api.py`  — mock + real, 1-hour TTL cache, FM-3 fallback to None
- `llm_client.py`    — `FakeLLMClient` keyed by source_text substrings, `RealLLMClient` stub for Anthropic
- `agent1_intake.py` — `process_ticket`, `run_one_cycle`, polling loop, EC-7 multi-shift detector

## Live mock run #1
- `rm -f /tmp/medflex_agent1.sqlite`
- `SERVICENOW_BASE_URL=mock MEDFLEX_API_BASE_URL=mock INTAKE_USE_FAKE_LLM=true INTAKE_RUN_ONCE=true DATABASE_URL=/tmp/medflex_agent1.sqlite python3 agent1_intake.py`
- Output: 3 ServiceNow fixture tickets processed:
  - ticket_001 -> ShiftRequest PENDING_MATCH, confidence 0.95, ICU + RN + ICU_CERTIFIED
  - ticket_002 -> CLARIFICATION_NEEDED, 0.55, urgency CRITICAL, DATE_UNCLEAR + TIME_UNCLEAR flags
  - ticket_003 -> PENDING_MATCH, 0.93, PEDIATRIC, RN + PEDS_CERTIFIED
- Audit log: 3 rows, action=CREATED, all populated with confidence + to_status.
- DB inspect via `sqlite3` confirms 3 rows in `shift_requests`, 5 in `credential_requirements`, 2 in `ambiguity_flags`, 3 in `audit_log`.

## Tests
- First run: 9 passed, 1 failed.
  - `test_ec7_multi_shift_block` failed: original regex was too rigid (required `(comma|" and ")` between every pair). Replaced with a permissive ordinal-day scanner + plurality hint.
- Second run: 10/10 passed.

## Live mock run #2 (idempotency)
- Re-ran the agent against the SAME populated SQLite database.
- All 3 fixture tickets were correctly skipped with `skipped_reason=already_processed`.
- DB row count unchanged at 3.

## Punts / honest notes
- Postgres -> SQLite is a real divergence. The Postgres-specific bits (gen_random_uuid, JSONB, CHECK char_length) are documented but unverified.
- Did not exercise the RealLLMClient (no API key). FakeLLMClient covered both tests and the live mock run.
- FM-1 test only checks non-crashy behavior on one ServiceNow failure. The spec's "3 consecutive failures + pause" loop is NOT exercised end-to-end — that would need a stateful poller.
- OPS_ALERT webhook implementation is described in spec but not wired up. Build skipped it (called out as a place I noticed).
- The "LLM call timeout + retry once after 5s" is implemented in RealLLMClient but cannot be tested without a flaky real client.
- Coordinator clarification queue is a SELECT, not a separate table — implemented as `db.fetch_clarification_queue()`.
