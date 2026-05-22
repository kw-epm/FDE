"""Tests for EC-1 .. EC-7 from spec.md."""
import datetime as _dt

import pytest

import db
from agent1_intake import process_ticket
from llm_client import FakeLLMClient
from models import (
    AmbiguityType,
    CredentialCategory,
    ShiftRequestStatus,
    UnitType,
    Urgency,
)


REF_NOW = _dt.datetime(2026, 1, 19, 10, 0, 0, tzinfo=_dt.timezone.utc)


def _row(conn, sr_id):
    cur = conn.execute("SELECT * FROM shift_requests WHERE id=?", (sr_id,))
    r = cur.fetchone()
    assert r is not None, "ShiftRequest not found"
    return dict(r)


def _flags(conn, sr_id):
    cur = conn.execute("SELECT * FROM ambiguity_flags WHERE shift_request_id=?", (sr_id,))
    return [dict(r) for r in cur.fetchall()]


def _creds(conn, sr_id):
    cur = conn.execute("SELECT * FROM credential_requirements WHERE shift_request_id=?", (sr_id,))
    return [dict(r) for r in cur.fetchall()]


# ---------------- EC-1 ----------------

def test_ec1_asap(conn, hospital_client, fake_llm):
    ticket = {
        "sys_id": "ec1_ticket",
        "description": "Need RN ASAP, med-surg floor",
        "u_hospital_id": "hospital_metro_02",
        "sys_created_on": "2026-01-19T10:00:00Z",
    }
    out = process_ticket(conn, ticket, llm_client=fake_llm, hospital_client=hospital_client, current_datetime_utc=REF_NOW)
    assert out.created_shift_request_ids, "expected a ShiftRequest"
    row = _row(conn, out.created_shift_request_ids[0])
    assert row["shift_date"] is None
    assert row["urgency"] == "CRITICAL"
    assert row["confidence_score"] < 0.65
    assert row["status"] == "CLARIFICATION_NEEDED"
    flags = _flags(conn, out.created_shift_request_ids[0])
    assert any(f["type"] == "DATE_UNCLEAR" for f in flags)


# ---------------- EC-2 ----------------

def test_ec2_step_down_shorthand(conn, hospital_client, fake_llm):
    ticket = {
        "sys_id": "ec2_ticket",
        "description": "Step-down unit nurse, 12-hour day shift next Monday",
        "u_hospital_id": "hospital_metro_02",
        "sys_created_on": "2026-05-20T10:00:00Z",
    }
    out = process_ticket(conn, ticket, llm_client=fake_llm, hospital_client=hospital_client, current_datetime_utc=REF_NOW)
    assert out.created_shift_request_ids
    sr_id = out.created_shift_request_ids[0]
    row = _row(conn, sr_id)
    assert row["unit_type"] == "GENERAL"
    creds = _creds(conn, sr_id)
    assert any(c["credential_category"] == "RN" for c in creds)
    flags = _flags(conn, sr_id)
    assert any(f["type"] == "CREDENTIAL_UNCLEAR" for f in flags)
    assert 0.65 <= row["confidence_score"] <= 0.84
    assert row["status"] == "PENDING_MATCH"


# ---------------- EC-3 ----------------

def test_ec3_conflicting_requirements(conn, hospital_client, fake_llm):
    ticket = {
        "sys_id": "ec3_ticket",
        "description": "Need ICU nurse for general ward, evening shift tomorrow",
        "u_hospital_id": "hospital_metro_02",
        "sys_created_on": "2026-05-22T10:00:00Z",
    }
    out = process_ticket(conn, ticket, llm_client=fake_llm, hospital_client=hospital_client, current_datetime_utc=REF_NOW)
    assert out.created_shift_request_ids
    sr_id = out.created_shift_request_ids[0]
    row = _row(conn, sr_id)
    flags = _flags(conn, sr_id)
    assert any(f["type"] == "CONFLICTING_REQUIREMENTS" for f in flags)
    assert row["confidence_score"] < 0.65
    assert row["status"] == "CLARIFICATION_NEEDED"


# ---------------- EC-4 ----------------

def test_ec4_duplicate_detected(conn, hospital_client, fake_llm):
    ticket_a = {
        "sys_id": "ec4_ticket_a",
        "description": "Need ICU-trained RN for nights January 20th, 7pm to 7am. St. Mary's downtown.",
        "u_hospital_id": "hospital_stmarys_01",
        "sys_created_on": "2026-01-19T10:00:00Z",
    }
    ticket_b = {
        "sys_id": "ec4_ticket_b",
        "description": "Need ICU-trained RN for nights January 20th, 7pm to 7am. St. Mary's downtown.",
        "u_hospital_id": "hospital_stmarys_01",
        "sys_created_on": "2026-01-19T10:10:00Z",
    }
    a = process_ticket(conn, ticket_a, llm_client=fake_llm, hospital_client=hospital_client, current_datetime_utc=REF_NOW)
    b = process_ticket(conn, ticket_b, llm_client=fake_llm, hospital_client=hospital_client, current_datetime_utc=REF_NOW)
    assert a.created_shift_request_ids and b.created_shift_request_ids
    sr_b = b.created_shift_request_ids[0]
    flags_b = _flags(conn, sr_b)
    assert any(f["type"] == "DUPLICATE_SUSPECTED" for f in flags_b)
    row_b = _row(conn, sr_b)
    assert row_b["status"] == "CLARIFICATION_NEEDED"


# ---------------- EC-5 ----------------

def test_ec5_no_time_specified(conn, hospital_client, fake_llm):
    ticket = {
        "sys_id": "ec5_ticket",
        "description": "RN needed for pediatric ward on February 3rd",
        "u_hospital_id": "hospital_stmarys_01",
        "sys_created_on": "2026-01-19T10:00:00Z",
    }
    out = process_ticket(conn, ticket, llm_client=fake_llm, hospital_client=hospital_client, current_datetime_utc=REF_NOW)
    assert out.created_shift_request_ids
    sr_id = out.created_shift_request_ids[0]
    row = _row(conn, sr_id)
    assert row["shift_start_time"] is None
    assert row["shift_end_time"] is None
    flags = _flags(conn, sr_id)
    assert any(f["type"] == "TIME_UNCLEAR" for f in flags)
    assert 0.65 <= row["confidence_score"] <= 0.84
    assert row["status"] == "PENDING_MATCH"


# ---------------- EC-6 ----------------

def test_ec6_unknown_hospital(conn, hospital_client, fake_llm):
    ticket = {
        "sys_id": "ec6_ticket",
        "description": "Need ICU-trained RN for nights January 20th, 7pm to 7am.",
        "u_hospital_id": "hospital_does_not_exist_99",
        "sys_created_on": "2026-01-19T10:00:00Z",
    }
    out = process_ticket(conn, ticket, llm_client=fake_llm, hospital_client=hospital_client, current_datetime_utc=REF_NOW)
    assert out.routed_to_manual_queue is True
    assert not out.created_shift_request_ids
    assert db.count_shift_requests(conn) == 0


# ---------------- EC-7 ----------------

def test_ec7_multi_shift_block(conn, hospital_client, fake_llm):
    ticket = {
        "sys_id": "ec7_ticket",
        "description": "Need 3 ICU RNs for nights the 20th, 21st, and 22nd",
        "u_hospital_id": "hospital_stmarys_01",
        "sys_created_on": "2026-01-19T10:00:00Z",
    }
    out = process_ticket(conn, ticket, llm_client=fake_llm, hospital_client=hospital_client, current_datetime_utc=REF_NOW)
    assert len(out.created_shift_request_ids) == 3, f"expected 3, got {len(out.created_shift_request_ids)}"
    dates = []
    for sr_id in out.created_shift_request_ids:
        r = _row(conn, sr_id)
        dates.append(r["shift_date"])
        assert r["status"] == "PENDING_MATCH"
        assert "3-shift block" in (r["special_notes"] or "")
    assert sorted(dates) == ["2026-01-20", "2026-01-21", "2026-01-22"]
    # sequence numbers must be 1, 2, 3
    cur = conn.execute(
        "SELECT ticket_sequence_num FROM shift_requests WHERE servicenow_ticket_id=? ORDER BY ticket_sequence_num",
        ("ec7_ticket",),
    )
    seqs = [r["ticket_sequence_num"] for r in cur.fetchall()]
    assert seqs == [1, 2, 3]
