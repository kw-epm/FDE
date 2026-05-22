"""Agent 1 — Request Intake. Main orchestration + polling loop.

Run with `python agent1_intake.py`. Honours environment variables (see spec
build context table). With SERVICENOW_BASE_URL=mock and
MEDFLEX_API_BASE_URL=mock the agent will read fixture files and process a
single poll cycle of tickets (or loop, depending on the runtime flag).

The orchestration is exposed as `process_ticket(...)` so tests can drive
each EC/FM scenario without standing up the polling loop.
"""
from __future__ import annotations

import datetime as _dt
import json
import logging
import os
import re
import sqlite3
import sys
import time as _time
from dataclasses import dataclass, field
from typing import Optional

import db
from hospital_api import HospitalAPIClient
from llm_client import FakeLLMClient, LLMError, LLMSchemaError, RealLLMClient, build_default_fake
from models import (
    AmbiguityFlag,
    AmbiguityType,
    CredentialRequirement,
    LLMParseResult,
    ShiftRequest,
    ShiftRequestStatus,
    Urgency,
)
from servicenow_client import ServiceNowClient, ServiceNowError

log = logging.getLogger("agent1")

AGENT_VERSION = os.environ.get("AGENT_VERSION", "0.1.0")


def _high_threshold() -> float:
    return float(os.environ.get("INTAKE_CONFIDENCE_HIGH_THRESHOLD", "0.85"))


def _low_threshold() -> float:
    return float(os.environ.get("INTAKE_CONFIDENCE_LOW_THRESHOLD", "0.65"))


# ---------------- Result objects ----------------

@dataclass
class ProcessOutcome:
    """Outcome of attempting to process one ServiceNow ticket."""
    ticket_id: str
    created_shift_request_ids: list[str] = field(default_factory=list)
    skipped: bool = False
    skipped_reason: Optional[str] = None
    routed_to_manual_queue: bool = False  # FM-2 / EC-6
    error: Optional[str] = None


# ---------------- Multi-shift heuristic for EC-7 ----------------

_DAY_TOKEN_RE = re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)\b", re.IGNORECASE)


def _detect_multi_shift_block(source_text: str, base_shift_date: Optional[_dt.date]) -> list[_dt.date]:
    """Detect 'the 20th, 21st, and 22nd' style multi-shift blocks.

    Heuristic: find all ordinal day tokens (20th, 21st, etc.) in the source.
    If there are >= 2 such tokens AND the source contains the keyword
    'block', 'shifts' (plural) or a leading count like '3 ICU' / '2 ICU',
    treat them as separate shifts in the same month/year as the LLM's
    inferred shift_date. Returns [] if no block detected.
    """
    if base_shift_date is None:
        return []
    days = [int(m.group(1)) for m in _DAY_TOKEN_RE.finditer(source_text)]
    if len(days) < 2:
        return []
    # require a plurality / count hint
    pl_hint = bool(re.search(r"\b(?:\d+\s+\w+|shifts|block|multiple)\b", source_text, re.IGNORECASE))
    if not pl_hint:
        return []
    base = base_shift_date
    out = []
    for d in days:
        try:
            out.append(base.replace(day=d))
        except ValueError:
            return []
    return out


# ---------------- Core processing ----------------

def process_ticket(
    conn: sqlite3.Connection,
    ticket: dict,
    *,
    llm_client,
    hospital_client: HospitalAPIClient,
    current_datetime_utc: Optional[_dt.datetime] = None,
) -> ProcessOutcome:
    """Process a single ServiceNow ticket end-to-end."""
    ticket_id = ticket["sys_id"]
    source_text = ticket.get("description", "") or ""
    hospital_id = ticket.get("u_hospital_id", "")
    now = current_datetime_utc or _dt.datetime.now(_dt.timezone.utc)
    outcome = ProcessOutcome(ticket_id=ticket_id)

    # Idempotency
    if db.already_processed(conn, ticket_id, ticket_sequence_num=1):
        outcome.skipped = True
        outcome.skipped_reason = "already_processed"
        return outcome

    # EC-6: unknown hospital — block creation
    if not hospital_client.hospital_exists(hospital_id):
        log.error("unknown_hospital ticket_id=%s hospital_id=%s", ticket_id, hospital_id)
        db.write_audit(
            conn,
            entity_type="servicenow_ticket",
            entity_id=ticket_id,
            action="ROUTED_TO_MANUAL_QUEUE",
            servicenow_ticket_id=ticket_id,
            agent_version=AGENT_VERSION,
            metadata={"reason": "unknown_hospital", "hospital_id": hospital_id},
        )
        outcome.routed_to_manual_queue = True
        outcome.skipped_reason = "unknown_hospital"
        return outcome

    # FM-3: hospital profile fetch — fallback to default mappings if missing
    profile = hospital_client.get_profile(hospital_id)
    profile_was_missing = False
    if profile is None:
        profile_was_missing = True
        log.warning("hospital_profile_missing using_defaults ticket_id=%s", ticket_id)
        profile = {
            "standard_shift_times": {
                "days":     {"start": "07:00", "end": "19:00"},
                "nights":   {"start": "19:00", "end": "07:00"},
                "evenings": {"start": "15:00", "end": "23:00"},
            },
            "preferred_credential_categories": [],
            "common_unit_types": [],
            "coordinates": None,
        }

    # LLM parse — FM-2 handled here
    try:
        result: LLMParseResult = llm_client.parse(
            source_text=source_text,
            hospital_profile=profile,
            current_datetime_utc=now.isoformat(),
        )
    except LLMSchemaError as e:
        log.error("llm_parse_failure ticket_id=%s err=%s", ticket_id, e)
        db.write_audit(
            conn,
            entity_type="servicenow_ticket",
            entity_id=ticket_id,
            action="LLM_PARSE_FAILURE",
            servicenow_ticket_id=ticket_id,
            agent_version=AGENT_VERSION,
            metadata={"error": str(e)[:500]},
        )
        outcome.routed_to_manual_queue = True
        outcome.error = f"llm_schema:{e}"
        return outcome
    except LLMError as e:
        log.error("llm_unavailable ticket_id=%s err=%s", ticket_id, e)
        db.write_audit(
            conn,
            entity_type="servicenow_ticket",
            entity_id=ticket_id,
            action="LLM_PARSE_FAILURE",
            servicenow_ticket_id=ticket_id,
            agent_version=AGENT_VERSION,
            metadata={"error": str(e)[:500]},
        )
        outcome.routed_to_manual_queue = True
        outcome.error = f"llm:{e}"
        return outcome

    # Multi-shift detection — EC-7
    multi_dates = _detect_multi_shift_block(source_text, result.shift_date)
    if multi_dates and len(multi_dates) > 1:
        shifts = multi_dates
    else:
        shifts = [result.shift_date]

    for seq, shift_date in enumerate(shifts, start=1):
        if db.already_processed(conn, ticket_id, ticket_sequence_num=seq):
            continue
        sr = _build_shift_request(
            ticket_id=ticket_id,
            ticket_sequence_num=seq,
            hospital_id=hospital_id,
            source_text=source_text,
            hospital_profile=profile,
            result=result,
            shift_date_override=shift_date,
            multi_shift_total=len(shifts) if len(shifts) > 1 else None,
        )

        # Duplicate detection — only for status PENDING_MATCH parses
        cred_cats = [c.credential_category.value for c in sr.required_credentials]
        existing = db.find_duplicate(
            conn,
            hospital_id=sr.hospital_id,
            shift_date=sr.shift_date,
            shift_start_time=sr.shift_start_time,
            credential_categories=cred_cats,
        )
        if existing is not None:
            sr.flagged_ambiguities.append(
                AmbiguityFlag(
                    type=AmbiguityType.DUPLICATE_SUSPECTED,
                    description=f"Possible duplicate of existing shift_request {existing}",
                    source_excerpt=source_text[:300],
                )
            )
            sr.status = ShiftRequestStatus.CLARIFICATION_NEEDED

        # Apply confidence-driven routing
        if sr.confidence_score < _low_threshold():
            sr.status = ShiftRequestStatus.CLARIFICATION_NEEDED

        # FM-3 visible to coordinator
        if profile_was_missing and sr.status != ShiftRequestStatus.CLARIFICATION_NEEDED:
            sr.flagged_ambiguities.append(
                AmbiguityFlag(
                    type=AmbiguityType.INSUFFICIENT_INFORMATION,
                    description="Hospital profile unavailable; defaults used",
                    source_excerpt=hospital_id[:300],
                )
            )

        # Persist
        sr_id = db.insert_shift_request(conn, sr)
        outcome.created_shift_request_ids.append(sr_id)
        db.write_audit(
            conn,
            entity_type="shift_request",
            entity_id=sr_id,
            action="CREATED",
            servicenow_ticket_id=ticket_id,
            to_status=sr.status.value,
            agent_version=AGENT_VERSION,
            confidence_score=sr.confidence_score,
            metadata={"ticket_sequence_num": seq},
        )

    return outcome


def _build_shift_request(
    *,
    ticket_id: str,
    ticket_sequence_num: int,
    hospital_id: str,
    source_text: str,
    hospital_profile: dict,
    result: LLMParseResult,
    shift_date_override: Optional[_dt.date],
    multi_shift_total: Optional[int],
) -> ShiftRequest:
    sd = shift_date_override if shift_date_override is not None else result.shift_date
    duration = None
    if result.shift_start_time and result.shift_end_time:
        start_minutes = result.shift_start_time.hour * 60 + result.shift_start_time.minute
        end_minutes = result.shift_end_time.hour * 60 + result.shift_end_time.minute
        if end_minutes <= start_minutes:
            end_minutes += 24 * 60  # crosses midnight
        duration = (end_minutes - start_minutes) / 60.0

    special_notes = result.special_notes
    if multi_shift_total:
        msg = f"Part of {multi_shift_total}-shift block request"
        special_notes = msg if not special_notes else f"{special_notes}; {msg}"

    sr = ShiftRequest(
        servicenow_ticket_id=ticket_id,
        ticket_sequence_num=ticket_sequence_num,
        hospital_id=hospital_id,
        source_text=source_text,
        hospital_location=hospital_profile.get("coordinates"),
        shift_date=sd,
        shift_start_time=result.shift_start_time,
        shift_end_time=result.shift_end_time,
        shift_duration_hours=duration,
        unit_type=result.unit_type,
        urgency=result.urgency,
        required_credentials=result.required_credentials,
        preferred_credentials=result.preferred_credentials,
        special_notes=special_notes,
        confidence_score=round(result.overall_confidence_score, 2),
        flagged_ambiguities=list(result.flagged_ambiguities),
    )
    return sr


# ---------------- Poll cycle ----------------

def run_one_cycle(
    conn: sqlite3.Connection,
    *,
    sn_client: ServiceNowClient,
    hospital_client: HospitalAPIClient,
    llm_client,
    current_datetime_utc: Optional[_dt.datetime] = None,
) -> list[ProcessOutcome]:
    try:
        tickets = sn_client.fetch_tickets()
    except ServiceNowError as e:
        log.error("servicenow_fetch_failed err=%s", e)
        return []
    outcomes = []
    for t in tickets:
        outcomes.append(
            process_ticket(
                conn,
                t,
                llm_client=llm_client,
                hospital_client=hospital_client,
                current_datetime_utc=current_datetime_utc,
            )
        )
    return outcomes


# ---------------- CLI entrypoint ----------------

def _build_llm_client():
    if os.environ.get("INTAKE_USE_FAKE_LLM") == "true" or not os.environ.get("ANTHROPIC_API_KEY"):
        return build_default_fake()
    return RealLLMClient()


def main():  # pragma: no cover — entry point exercised separately
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        stream=sys.stderr,
    )

    conn = db.connect(os.environ.get("DATABASE_URL", "/tmp/medflex_agent1.sqlite"))
    sn = ServiceNowClient()
    hosp = HospitalAPIClient()
    llm = _build_llm_client()

    poll_interval = int(os.environ.get("SERVICENOW_POLL_INTERVAL_SECONDS", "120"))
    once = os.environ.get("INTAKE_RUN_ONCE", "false").lower() == "true"

    log.info(
        "agent1_starting servicenow=%s medflex=%s once=%s",
        sn.base_url, hosp.base_url, once,
    )

    while True:
        try:
            outcomes = run_one_cycle(conn, sn_client=sn, hospital_client=hosp, llm_client=llm)
            for o in outcomes:
                log.info(
                    "poll_outcome ticket=%s created=%s skipped=%s manual_queue=%s err=%s",
                    o.ticket_id, o.created_shift_request_ids, o.skipped, o.routed_to_manual_queue, o.error,
                )
        except Exception as e:  # noqa: BLE001
            log.exception("poll_cycle_failed err=%s", e)
        if once:
            break
        _time.sleep(poll_interval)


if __name__ == "__main__":
    main()
