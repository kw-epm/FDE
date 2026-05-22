"""Orchestrates the 13 process steps from D#4a §4.

`run()` walks each step in order, prints a trace, writes audit lines, and
returns the final outcome. It is deliberately linear so the spec mapping is
obvious; a production version would split this across a queue worker, a
ranker service, and a state-machine driver.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Callable, Optional

from .comms import CommsLayer
from .eligibility import filter_pool
from .entities import (
    Candidate,
    ConfirmedFill,
    HospitalAcceptance,
    HospitalSubmission,
    NurseAcceptance,
    NurseOffer,
    ShiftRequest,
    Urgency,
)
from .extractor import EXTRACTION_THRESHOLD, extract, low_confidence_fields
from .lock_store import LockStore, LockStoreUnavailable
from .ranker import rank
from .trust_ramp import TrustRamp


@dataclass
class CoordinatorDecision:
    """Step 7 input — what the human approver returns."""
    approve_top: bool = True
    chosen_nurse_id: Optional[str] = None  # None = take rank 1
    reject_all: bool = False
    note: str = ""


@dataclass
class RunResult:
    shift_request: ShiftRequest
    shortlist_top_n: list[Candidate]
    confidence: str
    decision: str                  # auto-send / flag-to-coordinator / coordinator-decides
    offered_to_nurse_id: Optional[str] = None
    nurse_response: Optional[str] = None
    hospital_submission: Optional[HospitalSubmission] = None
    hospital_response: Optional[str] = None
    confirmed: Optional[ConfirmedFill] = None
    audit: list[str] = field(default_factory=list)
    halted_at_step: Optional[int] = None
    halt_reason: Optional[str] = None
    primary_kpi_seconds: Optional[float] = None    # request → hospital submission


def _ts(audit: list[str], msg: str) -> None:
    audit.append(msg)
    print(msg)


def run(
    *,
    raw_email: str,
    hospital_id: str,
    received_at: datetime,
    nurses: list,
    trust_ramp: TrustRamp,
    lock_store: LockStore,
    comms: CommsLayer,
    coordinator: Callable[[CoordinatorDecision], CoordinatorDecision] = None,
    nurse_decision: str = "yes",   # "yes" | "no" | "timeout"
    hospital_decision: str = "yes",
) -> RunResult:
    audit: list[str] = []
    result_shift = None

    # --- Step 1: extract structured intent
    _ts(audit, "Step 1: extract structured intent")
    req = extract(raw_email, hospital_id, received_at)
    result_shift = req
    _ts(audit, f"  parsed: specialty={req.parsed_intent.specialty} "
               f"date={req.parsed_intent.shift_date} time={req.parsed_intent.shift_time} "
               f"creds={req.parsed_intent.credentials} "
               f"urgency={req.parsed_intent.urgency.value} "
               f"signals={req.parsed_intent.profile_signals} "
               f"prefs={req.parsed_intent.hospital_preferences}")
    low = low_confidence_fields(req)
    if low:
        _ts(audit, f"  HALT at step 1: low-confidence fields {low} (<{EXTRACTION_THRESHOLD}). "
                   "Routing to coordinator review.")
        return RunResult(shift_request=req, shortlist_top_n=[], confidence="n/a",
                         decision="coordinator-review-extraction",
                         audit=audit, halted_at_step=1,
                         halt_reason=f"low-confidence fields: {low}")

    # --- Step 2 + 3: eligibility + compliance
    shift_dt = datetime.fromisoformat(req.parsed_intent.shift_date)
    _ts(audit, "Step 2 + 3: eligibility filter + compliance precondition")
    pool, drops = filter_pool(nurses, req, shift_dt)
    for n, why in drops:
        _ts(audit, f"  drop {n.name}: {why}")
    if not pool:
        _ts(audit, "  HALT at step 2/3: empty pool. Coordinator exception path.")
        return RunResult(shift_request=req, shortlist_top_n=[], confidence="n/a",
                         decision="coordinator-exception",
                         audit=audit, halted_at_step=2,
                         halt_reason="no eligible nurses")
    _ts(audit, f"  pool size: {len(pool)} "
               f"({', '.join(n.name for n in pool)})")

    # --- Step 4 + 5: contextual reasoning + confidence
    _ts(audit, "Step 4 + 5: contextual reasoning + confidence scoring")
    shortlist = rank(req, pool, top_n=3)
    for i, c in enumerate(shortlist.candidates, 1):
        _ts(audit, f"  #{i} {c.nurse.name}  score={c.score:.2f}")
        for r in c.reasoning:
            _ts(audit, f"      - {r}")
    _ts(audit, f"  confidence: {shortlist.confidence}")

    # --- Step 6: confidence gate × trust ramp
    _ts(audit, "Step 6: confidence gate × trust ramp")
    decision = trust_ramp.decision(shortlist.confidence)
    _ts(audit, f"  trust ramp = {trust_ramp.label()}; decision = {decision}")

    # --- Step 7: coordinator review (skipped if auto-send)
    top = shortlist.candidates[0]
    chosen = top
    if decision != "auto-send":
        _ts(audit, "Step 7: coordinator review")
        cd = CoordinatorDecision()
        if coordinator is not None:
            cd = coordinator(cd)
        if cd.reject_all:
            _ts(audit, "  HALT at step 7: coordinator rejected all candidates. Escalation.")
            return RunResult(shift_request=req, shortlist_top_n=shortlist.candidates,
                             confidence=shortlist.confidence, decision=decision,
                             audit=audit, halted_at_step=7,
                             halt_reason="coordinator rejected all")
        if cd.chosen_nurse_id:
            chosen = next(c for c in shortlist.candidates if c.nurse.id == cd.chosen_nurse_id)
        _ts(audit, f"  coordinator approved: {chosen.nurse.name}. "
                   f"Note: {cd.note or 'none'}")
    else:
        _ts(audit, "Step 7: skipped (auto-send)")

    # --- Step 8: soft-lock
    _ts(audit, "Step 8: soft-lock fires")
    try:
        lock = lock_store.soft_lock(chosen.nurse.id, received_at,
                                    req.parsed_intent.urgency)
        _ts(audit, f"  {lock.candidate_id} -> SoftLock until {lock.expires_at.isoformat()}")
    except LockStoreUnavailable as e:
        _ts(audit, f"  HALT at step 8: {e}")
        return RunResult(shift_request=req, shortlist_top_n=shortlist.candidates,
                         confidence=shortlist.confidence, decision=decision,
                         audit=audit, halted_at_step=8, halt_reason=str(e))

    # --- Step 9: send NurseOffer
    _ts(audit, "Step 9: send NurseOffer (SMS + email)")
    offered_at = received_at + timedelta(minutes=12)  # diagnostic step 1 < 30 min
    body = (f"Shift offer: {req.parsed_intent.specialty} "
            f"{req.parsed_intent.shift_time} on {req.parsed_intent.shift_date} "
            f"at {req.hospital_id}. Reply YES/NO within 90 min.")
    sent_ok = False
    last_err = None
    for attempt in range(3):
        try:
            comms.send(nurse_id=chosen.nurse.id, body=body,
                       channels=["sms", "email"], when=offered_at)
            sent_ok = True
            break
        except RuntimeError as e:
            last_err = e
            _ts(audit, f"  comms attempt {attempt+1} failed: {e}")
    if not sent_ok:
        _ts(audit, "  HALT at step 9: 3 comms failures; alert ops; lock released.")
        lock_store.release(chosen.nurse.id, "comms failure", offered_at)
        return RunResult(shift_request=req, shortlist_top_n=shortlist.candidates,
                         confidence=shortlist.confidence, decision=decision,
                         audit=audit, halted_at_step=9,
                         halt_reason=f"comms: {last_err}")
    _ts(audit, f"  offer sent to {chosen.nurse.name} via sms+email")

    offer = NurseOffer(shortlist_id=shortlist.id, nurse_id=chosen.nurse.id,
                       shift_id=req.id, offered_at=offered_at,
                       channel=["sms", "email"], window=timedelta(minutes=90))

    # --- Step 10: wait for nurse acceptance
    _ts(audit, "Step 10: wait for nurse acceptance (Decision 2 window)")
    if nurse_decision == "yes":
        responded_at = offered_at + timedelta(minutes=18)
        NurseAcceptance(offer_id=offer.id, response="yes", responded_at=responded_at)
        lock_store.to_partial(chosen.nurse.id, responded_at, req.parsed_intent.urgency)
        _ts(audit, f"  nurse said YES at {responded_at.isoformat()} -> PartialCommitment")
    else:
        responded_at = offered_at + (timedelta(minutes=90) if nurse_decision == "timeout"
                                     else timedelta(minutes=22))
        lock_store.release(chosen.nurse.id, f"nurse {nurse_decision}", responded_at)
        _ts(audit, f"  nurse {nurse_decision} at {responded_at.isoformat()} -> Released; "
                   "re-pool flow would re-rank from same shortlist (edge case 3).")
        return RunResult(shift_request=req, shortlist_top_n=shortlist.candidates,
                         confidence=shortlist.confidence, decision=decision,
                         offered_to_nurse_id=chosen.nurse.id,
                         nurse_response=nurse_decision,
                         audit=audit, halted_at_step=10,
                         halt_reason=f"nurse {nurse_decision}")

    # --- Step 11: hospital submission (PRIMARY KPI CLOCK ENDS)
    _ts(audit, "Step 11: hospital submission (PRIMARY KPI CLOCK ENDS HERE)")
    submitted_at = responded_at + timedelta(minutes=3)
    summary = "; ".join(chosen.reasoning[:2])  # short rationale to hospital
    submission = HospitalSubmission(
        nurse_id=chosen.nurse.id, hospital_id=req.hospital_id, shift_id=req.id,
        submitted_at=submitted_at, reasoning_summary=summary)
    kpi = (submitted_at - received_at).total_seconds()
    _ts(audit, f"  submitted {chosen.nurse.name} to {req.hospital_id} "
               f"({kpi/60:.1f} min after request received)")

    # --- Step 12: hospital acceptance
    _ts(audit, "Step 12: hospital acceptance")
    h_resp_at = submitted_at + timedelta(minutes=20)
    HospitalAcceptance(submission_id=submission.id, response=hospital_decision,
                       responded_at=h_resp_at)
    if hospital_decision == "no":
        _ts(audit, "  hospital REJECTED -> back to step 4 with this candidate excluded "
                   "(edge case 8).")
        lock_store.release(chosen.nurse.id, "hospital rejection", h_resp_at)
        return RunResult(shift_request=req, shortlist_top_n=shortlist.candidates,
                         confidence=shortlist.confidence, decision=decision,
                         offered_to_nurse_id=chosen.nurse.id, nurse_response="yes",
                         hospital_submission=submission, hospital_response="no",
                         audit=audit, halted_at_step=12,
                         halt_reason="hospital rejected", primary_kpi_seconds=kpi)
    lock_store.to_confirmed(chosen.nurse.id, h_resp_at)
    _ts(audit, f"  hospital ACCEPTED at {h_resp_at.isoformat()} -> Confirmed")

    # --- Step 13: confirmed fill
    confirmed = ConfirmedFill(nurse_id=chosen.nurse.id, shift_id=req.id,
                              confirmed_at=h_resp_at)
    _ts(audit, f"Step 13: ConfirmedFill {confirmed.id} written; audit trail closed.")

    return RunResult(
        shift_request=req,
        shortlist_top_n=shortlist.candidates,
        confidence=shortlist.confidence,
        decision=decision,
        offered_to_nurse_id=chosen.nurse.id,
        nurse_response="yes",
        hospital_submission=submission,
        hospital_response="yes",
        confirmed=confirmed,
        audit=audit,
        primary_kpi_seconds=kpi,
    )
