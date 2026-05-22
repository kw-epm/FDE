"""Agent 1 — Request Intake.

Long-running polling loop that:
  1. Polls ServiceNow for new tickets (or reads from mock fixture)
  2. Looks up hospital profile (cached)
  3. Calls the LLM with the parse prompt
  4. Validates JSON output against LLMParseResult
  5. Detects duplicates against existing PENDING_MATCH / MATCHED rows
  6. Persists ShiftRequest + credential_requirements + ambiguity_flags
  7. Writes audit log entries for CREATED / AMBIGUITY_FLAGGED transitions
  8. Routes by confidence threshold to PENDING_MATCH or CLARIFICATION_NEEDED

Stop with Ctrl+C. Does NOT post-process clarification-queue items — those are
resolved by coordinators via a separate UI (out of scope for Agent 1).
"""
from __future__ import annotations

import logging
import os
import signal
import sys
import time
from datetime import datetime, timezone
from typing import List, Optional

from dotenv import load_dotenv

import db
import hospital_api
import llm_client
import ops_alert
import servicenow_client
from models import (
    AmbiguityFlag,
    AmbiguityType,
    LLMParseResult,
    ParsedBy,
    ServiceNowTicket,
    ShiftRequest,
    ShiftRequestStatus,
)


log = logging.getLogger("agent1_intake")


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


def _cfg_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


def _cfg_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    return float(raw)


# ---------------------------------------------------------------------------
# Ticket processing
# ---------------------------------------------------------------------------


def _required_categories(parse: LLMParseResult) -> List[str]:
    out = []
    for c in parse.required_credentials:
        val = c.credential_category
        out.append(val if isinstance(val, str) else val.value)
    return out


def _add_duplicate_flag(parse: LLMParseResult) -> None:
    """Append a DUPLICATE_SUSPECTED ambiguity flag in-place."""
    parse.flagged_ambiguities.append(
        AmbiguityFlag(
            type=AmbiguityType.DUPLICATE_SUSPECTED,
            description=(
                "An existing PENDING_MATCH or MATCHED ShiftRequest with the same "
                "hospital, shift_date, shift_start_time, and at least one required "
                "credential was found. Coordinator review required."
            ),
            source_excerpt="(see ticket history)",
        )
    )


def _decide_status(
    confidence_score: float,
    has_duplicate: bool,
    low_threshold: float,
) -> ShiftRequestStatus:
    """Per spec delegation table + EC-4."""
    if has_duplicate:
        # EC-4: duplicates ALWAYS go to CLARIFICATION_NEEDED for coordinator review
        return ShiftRequestStatus.CLARIFICATION_NEEDED
    if confidence_score < low_threshold:
        return ShiftRequestStatus.CLARIFICATION_NEEDED
    return ShiftRequestStatus.PENDING_MATCH


def process_ticket(ticket: ServiceNowTicket) -> None:
    """Process one ServiceNow ticket end-to-end.

    Idempotency: if (sys_id, sequence=1) already exists, skip silently.
    Multi-shift (EC-7) expansion is delegated to the LLM via special_notes inspection
    in this iteration — a future enhancement would have the LLM emit a list of
    parse results. For now we treat each ServiceNow ticket as one ShiftRequest.
    """
    ticket_id = ticket.sys_id
    log.info("processing ticket %s", ticket_id)

    # Idempotency: already processed?
    if db.ticket_sequence_already_persisted(ticket_id, sequence_num=1):
        log.info("ticket %s already persisted; skipping", ticket_id)
        return

    # EC-6: unknown hospital → block creation, route to coordinator manual queue
    if not hospital_api.hospital_exists(ticket.u_hospital_id):
        log.error(
            "EC-6: unknown hospital_id=%s on ticket=%s; routing to coordinator manual queue",
            ticket.u_hospital_id,
            ticket_id,
        )
        ops_alert.send_alert(
            "UNKNOWN_HOSPITAL",
            f"ticket {ticket_id} references unknown hospital {ticket.u_hospital_id}",
            details={"servicenow_ticket_id": ticket_id},
        )
        # No ShiftRequest row is created (per EC-6).
        return

    # Hospital profile — best effort; fall back to defaults on failure (FM-3)
    profile = hospital_api.get_hospital_profile(ticket.u_hospital_id)
    if profile is None:
        log.warning(
            "FM-3: hospital profile unavailable for %s; using defaults",
            ticket.u_hospital_id,
        )
        profile = hospital_api.default_profile()

    # LLM parse with retry (FM-2: route to manual queue if it fails)
    try:
        parse = llm_client.parse_shift_request(
            source_text=ticket.description,
            hospital_profile=profile,
            now_utc=_parse_iso(ticket.sys_created_on) or datetime.now(timezone.utc),
        )
    except llm_client.LLMParseError as e:
        log.error("FM-2: LLM parse failed for ticket=%s: %s", ticket_id, e)
        ops_alert.send_alert(
            "LLM_PARSE_FAILURE",
            f"LLM parse failed for ticket {ticket_id}",
            details={
                "servicenow_ticket_id": ticket_id,
                "error": str(e),
            },
        )
        return

    # Duplicate detection
    duplicates = db.find_duplicate_candidates(
        hospital_id=ticket.u_hospital_id,
        shift_date=parse.shift_date,
        shift_start_time=parse.shift_start_time,
        required_categories=_required_categories(parse),
    )
    has_active_duplicate = any(
        d["status"] in ("PENDING_MATCH", "MATCHED") for d in duplicates
    )
    if has_active_duplicate:
        _add_duplicate_flag(parse)

    # Determine final status
    low_threshold = _cfg_float("INTAKE_CONFIDENCE_LOW_THRESHOLD", 0.65)
    status = _decide_status(
        parse.overall_confidence_score, has_active_duplicate, low_threshold
    )

    # Construct ShiftRequest entity
    coords = profile.get("coordinates") if profile else None
    sr = ShiftRequest(
        servicenow_ticket_id=ticket_id,
        ticket_sequence_num=1,
        hospital_id=ticket.u_hospital_id,
        source_text=ticket.description,
        hospital_location=coords,
        shift_date=parse.shift_date,
        shift_start_time=parse.shift_start_time,
        shift_end_time=parse.shift_end_time,
        unit_type=parse.unit_type,
        urgency=parse.urgency,
        required_credentials=parse.required_credentials,
        preferred_credentials=parse.preferred_credentials,
        special_notes=parse.special_notes,
        status=status,
        confidence_score=round(parse.overall_confidence_score, 2),
        flagged_ambiguities=parse.flagged_ambiguities,
        parsed_by=ParsedBy.AGENT_1,
    )

    # Persist
    sr_id = db.insert_shift_request(sr)

    # Audit
    agent_version = os.environ.get("AGENT_VERSION", "0.1.0")
    db.write_audit(
        entity_type="shift_request",
        entity_id=sr_id,
        action="CREATED",
        to_status=status.value,
        agent_version=agent_version,
        confidence_score=sr.confidence_score,
        servicenow_ticket_id=ticket_id,
        metadata={
            "ambiguity_count": len(sr.flagged_ambiguities),
            "duplicate_suspected": has_active_duplicate,
        },
    )
    if sr.flagged_ambiguities:
        db.write_audit(
            entity_type="shift_request",
            entity_id=sr_id,
            action="AMBIGUITY_FLAGGED",
            agent_version=agent_version,
            confidence_score=sr.confidence_score,
            servicenow_ticket_id=ticket_id,
            metadata={
                "flags": [
                    {
                        "type": (
                            f.type if isinstance(f.type, str) else f.type.value
                        ),
                        "description": f.description,
                    }
                    for f in sr.flagged_ambiguities
                ]
            },
        )
    log.info(
        "ticket=%s -> ShiftRequest id=%s status=%s confidence=%.2f",
        ticket_id,
        sr_id,
        status.value,
        sr.confidence_score,
    )


def _parse_iso(s: str) -> Optional[datetime]:
    try:
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        return datetime.fromisoformat(s)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Polling loop
# ---------------------------------------------------------------------------


_stopping = False


def _handle_signal(signum, frame):  # noqa: ARG001
    global _stopping
    _stopping = True
    log.info("signal %s received, stopping after current cycle", signum)


def run() -> int:
    load_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s | %(message)s",
    )
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    db.init_pool()

    poll_seconds = _cfg_int("SERVICENOW_POLL_INTERVAL_SECONDS", 120)
    poll_minutes = max(1, poll_seconds // 60)
    outage_pause_minutes = _cfg_int("SERVICENOW_OUTAGE_PAUSE_MINUTES", 15)

    consecutive_failures = 0
    auth_paused = False

    while not _stopping:
        try:
            if auth_paused:
                log.warning("polling paused due to prior 401/403; sleeping 60s")
                time.sleep(60)
                continue

            tickets = servicenow_client.fetch_with_retry(poll_minutes)
            consecutive_failures = 0
            log.info("polled servicenow: %d tickets", len(tickets))
            for t in tickets:
                try:
                    process_ticket(t)
                except Exception as e:
                    log.exception("processing failed for ticket=%s: %s", t.sys_id, e)

        except servicenow_client.ServiceNowAuthError as e:
            log.error("ServiceNow auth error: %s; pausing polling", e)
            ops_alert.send_alert(
                "SERVICENOW_AUTH_FAILURE",
                "ServiceNow returned 401/403; polling paused until token refresh",
                details={"error": str(e)},
            )
            auth_paused = True
            continue

        except servicenow_client.ServiceNowRateLimitError as e:
            log.warning("rate limited; sleeping %ds", e.retry_after_seconds)
            time.sleep(e.retry_after_seconds)
            continue

        except servicenow_client.ServiceNowError as e:
            consecutive_failures += 1
            log.warning(
                "ServiceNow poll cycle failed (%s); consecutive=%d",
                e, consecutive_failures,
            )
            if consecutive_failures >= 3:
                ops_alert.send_alert(
                    "SERVICENOW_OUTAGE",
                    "3 consecutive ServiceNow poll cycles failed",
                    details={"error": str(e)},
                )
                log.error(
                    "FM-1: 3 consecutive failures; pausing %d minutes",
                    outage_pause_minutes,
                )
                time.sleep(outage_pause_minutes * 60)
                consecutive_failures = 0

        # Sleep until next poll
        for _ in range(poll_seconds):
            if _stopping:
                break
            time.sleep(1)

    log.info("agent1_intake stopped cleanly")
    return 0


if __name__ == "__main__":
    sys.exit(run())
