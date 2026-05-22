"""Tests for FM-1..FM-3 from spec.md."""
import datetime as _dt
from unittest.mock import patch

import pytest

import db
from agent1_intake import process_ticket, run_one_cycle
from hospital_api import HospitalAPIClient
from llm_client import FakeLLMClient, LLMError, LLMSchemaError
from servicenow_client import ServiceNowClient, ServiceNowError

REF_NOW = _dt.datetime(2026, 1, 19, 10, 0, 0, tzinfo=_dt.timezone.utc)


# ---------------- FM-1 ----------------

def test_fm1_servicenow_unavailable_does_not_crash(conn, hospital_client, fake_llm):
    """If ServiceNow raises (3 consecutive 5xx in spec), one poll cycle
    must return an empty outcome list and the agent must not crash. The
    operational alert is fire-and-forget — we only check the non-crashy
    path here. FAILS if the loop bubbles ServiceNowError.
    """
    class Boomer:
        def __init__(self):
            self.calls = 0
        def fetch_tickets(self):
            self.calls += 1
            raise ServiceNowError("server_error:500")

    sn = Boomer()
    outcomes = run_one_cycle(conn, sn_client=sn, hospital_client=hospital_client, llm_client=fake_llm, current_datetime_utc=REF_NOW)
    assert outcomes == []
    assert sn.calls == 1


# ---------------- FM-2 ----------------

def test_fm2_llm_invalid_json_routes_to_manual_queue(conn, hospital_client):
    """LLM returns garbage. After one internal retry the orchestrator must
    NOT create a ShiftRequest. The ticket must be flagged for the manual
    coordinator queue. Audit log row must exist for LLM_PARSE_FAILURE.
    """
    class BrokenLLM:
        def parse(self, source_text, hospital_profile, current_datetime_utc):
            raise LLMSchemaError("not JSON")
    ticket = {
        "sys_id": "fm2_ticket",
        "description": "Need ICU-trained RN for nights January 20th, 7pm to 7am.",
        "u_hospital_id": "hospital_stmarys_01",
        "sys_created_on": "2026-01-19T10:00:00Z",
    }
    out = process_ticket(conn, ticket, llm_client=BrokenLLM(), hospital_client=hospital_client, current_datetime_utc=REF_NOW)
    assert out.routed_to_manual_queue is True
    assert not out.created_shift_request_ids
    assert db.count_shift_requests(conn) == 0
    cur = conn.execute("SELECT * FROM audit_log WHERE action='LLM_PARSE_FAILURE'")
    assert cur.fetchone() is not None


# ---------------- FM-3 ----------------

def test_fm3_hospital_profile_unavailable_proceeds_with_defaults(conn, fake_llm):
    """Hospital exists but the profile fetch fails — the agent should still
    parse the ticket using default shift time mappings, log a warning, and
    NOT block ShiftRequest creation.
    """
    class FlakyHosp(HospitalAPIClient):
        def hospital_exists(self, hospital_id):
            return True  # hospital is known to the registry...
        def get_profile(self, hospital_id):
            return None  # ...but profile fetch fails (FM-3)

    hosp = FlakyHosp(base_url="mock")
    ticket = {
        "sys_id": "fm3_ticket",
        "description": "Need ICU-trained RN for nights January 20th, 7pm to 7am.",
        "u_hospital_id": "hospital_stmarys_01",
        "sys_created_on": "2026-01-19T10:00:00Z",
    }
    out = process_ticket(conn, ticket, llm_client=fake_llm, hospital_client=hosp, current_datetime_utc=REF_NOW)
    assert out.created_shift_request_ids, "ShiftRequest should still be created"
    cur = conn.execute("SELECT status FROM shift_requests WHERE id=?", (out.created_shift_request_ids[0],))
    assert cur.fetchone()["status"] in ("PENDING_MATCH", "CLARIFICATION_NEEDED")
