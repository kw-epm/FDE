"""SQLite-backed persistence layer.

Spec calls for psycopg2/Postgres. Postgres is not available in this build
environment, so we use SQLite (stdlib). All public functions take a
sqlite3.Connection as the first arg so tests can use in-memory databases.
"""
from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

from models import (
    AmbiguityFlag,
    CredentialRequirement,
    ShiftRequest,
    ShiftRequestStatus,
)

SCHEMA_PATH = Path(__file__).with_name("schema_sqlite.sql")


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Open a SQLite connection and ensure schema exists.

    db_path = None or ":memory:" opens an in-memory DB.
    """
    if db_path is None:
        db_path = os.environ.get("DATABASE_URL", ":memory:")
        # accept "sqlite:///path" form
        if db_path.startswith("sqlite:///"):
            db_path = db_path[len("sqlite:///") :]
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    init_schema(conn)
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    sql = SCHEMA_PATH.read_text()
    conn.executescript(sql)
    conn.commit()


def insert_shift_request(conn: sqlite3.Connection, sr: ShiftRequest) -> str:
    """Insert a ShiftRequest with its credentials and ambiguity flags.

    Returns the generated id (UUID string).
    """
    sr_id = str(uuid.uuid4())
    now = _utcnow_iso()
    conn.execute(
        """
        INSERT INTO shift_requests (
            id, servicenow_ticket_id, ticket_sequence_num, hospital_id, source_text,
            hospital_location, shift_date, shift_start_time, shift_end_time,
            unit_type, urgency, special_notes, status, confidence_score,
            parsed_by, coordinator_id, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            sr_id,
            sr.servicenow_ticket_id,
            sr.ticket_sequence_num,
            sr.hospital_id,
            sr.source_text,
            json.dumps(sr.hospital_location) if sr.hospital_location else None,
            sr.shift_date.isoformat() if sr.shift_date else None,
            sr.shift_start_time.isoformat() if sr.shift_start_time else None,
            sr.shift_end_time.isoformat() if sr.shift_end_time else None,
            sr.unit_type.value,
            sr.urgency.value,
            sr.special_notes,
            sr.status.value,
            float(sr.confidence_score),
            sr.parsed_by.value,
            sr.coordinator_id,
            now,
            now,
        ),
    )
    for cr in sr.required_credentials:
        conn.execute(
            """
            INSERT INTO credential_requirements (
                id, shift_request_id, credential_category, inference_confidence, is_required
            ) VALUES (?, ?, ?, ?, 1)
            """,
            (str(uuid.uuid4()), sr_id, cr.credential_category.value, float(cr.inference_confidence)),
        )
    for cr in sr.preferred_credentials:
        conn.execute(
            """
            INSERT INTO credential_requirements (
                id, shift_request_id, credential_category, inference_confidence, is_required
            ) VALUES (?, ?, ?, ?, 0)
            """,
            (str(uuid.uuid4()), sr_id, cr.credential_category.value, float(cr.inference_confidence)),
        )
    for af in sr.flagged_ambiguities:
        conn.execute(
            """
            INSERT INTO ambiguity_flags (id, shift_request_id, type, description, source_excerpt)
            VALUES (?, ?, ?, ?, ?)
            """,
            (str(uuid.uuid4()), sr_id, af.type.value, af.description, af.source_excerpt),
        )
    conn.commit()
    return sr_id


def already_processed(
    conn: sqlite3.Connection, servicenow_ticket_id: str, ticket_sequence_num: int = 1
) -> bool:
    """Idempotency check — keyed on (ticket_id, sequence_num) per EC-7."""
    cur = conn.execute(
        "SELECT 1 FROM shift_requests WHERE servicenow_ticket_id = ? AND ticket_sequence_num = ?",
        (servicenow_ticket_id, ticket_sequence_num),
    )
    return cur.fetchone() is not None


def find_duplicate(
    conn: sqlite3.Connection,
    hospital_id: str,
    shift_date,
    shift_start_time,
    credential_categories: Iterable[str],
) -> Optional[str]:
    """Return the id of an existing PENDING_MATCH/MATCHED ShiftRequest that matches on
    hospital, date, start_time, and at least one required credential. None otherwise.
    """
    if shift_date is None:
        return None
    cats = list(credential_categories)
    if not cats:
        return None
    placeholders = ",".join("?" * len(cats))
    sql = f"""
        SELECT sr.id
        FROM shift_requests sr
        JOIN credential_requirements cr ON cr.shift_request_id = sr.id
        WHERE sr.hospital_id = ?
          AND sr.shift_date = ?
          AND COALESCE(sr.shift_start_time,'') = COALESCE(?, '')
          AND sr.status IN ('PENDING_MATCH','MATCHED')
          AND cr.is_required = 1
          AND cr.credential_category IN ({placeholders})
        LIMIT 1
    """
    params = [
        hospital_id,
        shift_date.isoformat() if hasattr(shift_date, "isoformat") else shift_date,
        shift_start_time.isoformat() if shift_start_time and hasattr(shift_start_time, "isoformat") else (shift_start_time or ""),
        *cats,
    ]
    cur = conn.execute(sql, params)
    row = cur.fetchone()
    return row["id"] if row else None


def write_audit(
    conn: sqlite3.Connection,
    *,
    entity_type: str,
    entity_id: str,
    action: str,
    servicenow_ticket_id: Optional[str] = None,
    from_status: Optional[str] = None,
    to_status: Optional[str] = None,
    agent_version: Optional[str] = None,
    confidence_score: Optional[float] = None,
    coordinator_id: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> None:
    conn.execute(
        """
        INSERT INTO audit_log (
            id, entity_type, entity_id, timestamp, action,
            from_status, to_status, agent_version, confidence_score,
            coordinator_id, servicenow_ticket_id, metadata
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            str(uuid.uuid4()),
            entity_type,
            entity_id,
            _utcnow_iso(),
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
    conn.commit()


def count_shift_requests(conn: sqlite3.Connection) -> int:
    cur = conn.execute("SELECT COUNT(*) AS n FROM shift_requests")
    return cur.fetchone()["n"]


def fetch_clarification_queue(conn: sqlite3.Connection):
    cur = conn.execute(
        "SELECT * FROM shift_requests WHERE status = 'CLARIFICATION_NEEDED' ORDER BY created_at ASC"
    )
    return [dict(r) for r in cur.fetchall()]
