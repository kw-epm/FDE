"""PostgreSQL connection pool and persistence helpers for Agent 1."""
from __future__ import annotations

import json
import os
from contextlib import contextmanager
from typing import Iterator, List, Optional
from uuid import UUID

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool

from models import (
    AmbiguityFlag,
    CredentialRequirement,
    ShiftRequest,
    ShiftRequestStatus,
)


_pool: Optional[SimpleConnectionPool] = None


def init_pool(minconn: int = 1, maxconn: int = 5) -> None:
    global _pool
    if _pool is not None:
        return
    dsn = os.environ["DATABASE_URL"]
    _pool = SimpleConnectionPool(minconn, maxconn, dsn=dsn)


@contextmanager
def connection() -> Iterator[psycopg2.extensions.connection]:
    if _pool is None:
        init_pool()
    assert _pool is not None
    conn = _pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        _pool.putconn(conn)


# ---------------------------------------------------------------------------
# Idempotency / duplicate detection helpers
# ---------------------------------------------------------------------------


def ticket_sequence_already_persisted(ticket_id: str, sequence_num: int = 1) -> bool:
    """Return True if a ShiftRequest already exists for this (ticket_id, seq)."""
    with connection() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT 1 FROM shift_requests "
            "WHERE servicenow_ticket_id = %s AND ticket_sequence_num = %s LIMIT 1",
            (ticket_id, sequence_num),
        )
        return cur.fetchone() is not None


def find_duplicate_candidates(
    hospital_id: str,
    shift_date,
    shift_start_time,
    required_categories: List[str],
) -> List[dict]:
    """Return existing records that look like duplicates per spec rules.

    A duplicate is: same hospital_id, same shift_date, same shift_start_time, and at
    least one required_credential in common.
    """
    if shift_date is None or not required_categories:
        return []
    with connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT sr.id, sr.status, sr.servicenow_ticket_id
              FROM shift_requests sr
              JOIN credential_requirements cr ON cr.shift_request_id = sr.id
             WHERE sr.hospital_id = %s
               AND sr.shift_date = %s
               AND (sr.shift_start_time = %s OR (sr.shift_start_time IS NULL AND %s IS NULL))
               AND cr.is_required = TRUE
               AND cr.credential_category = ANY(%s)
            """,
            (hospital_id, shift_date, shift_start_time, shift_start_time, required_categories),
        )
        return list(cur.fetchall())


# ---------------------------------------------------------------------------
# ShiftRequest persistence
# ---------------------------------------------------------------------------


def insert_shift_request(sr: ShiftRequest) -> UUID:
    """Insert a ShiftRequest + its credential_requirements + ambiguity_flags atomically."""
    with connection() as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO shift_requests (
                id, servicenow_ticket_id, ticket_sequence_num, hospital_id,
                source_text, hospital_location, shift_date, shift_start_time,
                shift_end_time, unit_type, urgency, special_notes, status,
                confidence_score, parsed_by, coordinator_id, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                str(sr.id),
                sr.servicenow_ticket_id,
                sr.ticket_sequence_num,
                sr.hospital_id,
                sr.source_text,
                json.dumps(sr.hospital_location) if sr.hospital_location else None,
                sr.shift_date,
                sr.shift_start_time,
                sr.shift_end_time,
                sr.unit_type if isinstance(sr.unit_type, str) else sr.unit_type.value,
                sr.urgency if isinstance(sr.urgency, str) else sr.urgency.value,
                sr.special_notes,
                sr.status if isinstance(sr.status, str) else sr.status.value,
                sr.confidence_score,
                sr.parsed_by if isinstance(sr.parsed_by, str) else sr.parsed_by.value,
                sr.coordinator_id,
                sr.created_at,
                sr.updated_at,
            ),
        )

        for cred in sr.required_credentials:
            cur.execute(
                """
                INSERT INTO credential_requirements (
                    shift_request_id, credential_category, inference_confidence, is_required
                ) VALUES (%s, %s, %s, TRUE)
                """,
                (
                    str(sr.id),
                    cred.credential_category if isinstance(cred.credential_category, str) else cred.credential_category.value,
                    cred.inference_confidence,
                ),
            )
        for cred in sr.preferred_credentials:
            cur.execute(
                """
                INSERT INTO credential_requirements (
                    shift_request_id, credential_category, inference_confidence, is_required
                ) VALUES (%s, %s, %s, FALSE)
                """,
                (
                    str(sr.id),
                    cred.credential_category if isinstance(cred.credential_category, str) else cred.credential_category.value,
                    cred.inference_confidence,
                ),
            )

        for flag in sr.flagged_ambiguities:
            cur.execute(
                """
                INSERT INTO ambiguity_flags (
                    shift_request_id, type, description, source_excerpt
                ) VALUES (%s, %s, %s, %s)
                """,
                (
                    str(sr.id),
                    flag.type if isinstance(flag.type, str) else flag.type.value,
                    flag.description,
                    flag.source_excerpt,
                ),
            )

    return sr.id


# ---------------------------------------------------------------------------
# Audit log
# ---------------------------------------------------------------------------


def write_audit(
    entity_type: str,
    entity_id: UUID,
    action: str,
    *,
    from_status: Optional[str] = None,
    to_status: Optional[str] = None,
    agent_version: Optional[str] = None,
    confidence_score: Optional[float] = None,
    coordinator_id: Optional[str] = None,
    servicenow_ticket_id: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> None:
    with connection() as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO audit_log (
                entity_type, entity_id, action, from_status, to_status,
                agent_version, confidence_score, coordinator_id,
                servicenow_ticket_id, metadata
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                entity_type,
                str(entity_id),
                action,
                from_status,
                to_status,
                agent_version,
                confidence_score,
                coordinator_id,
                servicenow_ticket_id,
                json.dumps(metadata) if metadata else None,
            ),
        )
