"""Step 8 — Soft-lock state machine (Decision 3).

States: SoftLock -> PartialCommitment -> Confirmed; any decline/timeout -> Released.
Hard cap on PartialCommitment: 24h non-urgent, 2h urgent (D#4a §3).
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from .entities import LockRecord, LockState, Urgency


class LockStoreUnavailable(Exception):
    pass


class LockStore:
    """In-memory store. Real impl would back this with Redis/DDB (A9)."""

    def __init__(self, *, available: bool = True):
        self._records: dict[str, LockRecord] = {}
        self._available = available
        self.events: list[str] = []   # audit trail

    # ---- ops surface ----

    def healthcheck(self) -> bool:
        return self._available

    def soft_lock(self, candidate_id: str, now: datetime, urgency: Urgency,
                  soft_lock_window: timedelta = timedelta(minutes=90)) -> LockRecord:
        if not self._available:
            raise LockStoreUnavailable("lock-state store unavailable")
        # Multi-submission race (edge case 6): refuse if already locked
        existing = self._records.get(candidate_id)
        if existing and existing.current_state in (LockState.SoftLock,
                                                   LockState.PartialCommitment):
            raise RuntimeError(
                f"Multi-submission race: candidate {candidate_id} already in "
                f"{existing.current_state}"
            )
        rec = LockRecord(
            candidate_id=candidate_id,
            current_state=LockState.SoftLock,
            entered_at=now,
            expires_at=now + soft_lock_window,
        )
        self._records[candidate_id] = rec
        self._log(f"{candidate_id} -> SoftLock until {rec.expires_at.isoformat()}")
        return rec

    def to_partial(self, candidate_id: str, now: datetime, urgency: Urgency) -> LockRecord:
        rec = self._must_get(candidate_id)
        if rec.current_state != LockState.SoftLock:
            raise RuntimeError(f"cannot move to PartialCommitment from {rec.current_state}")
        rec.current_state = LockState.PartialCommitment
        cap = timedelta(hours=2) if urgency == Urgency.Urgent else timedelta(hours=24)
        rec.expires_at = now + cap
        rec.entered_at = now
        self._log(f"{candidate_id} -> PartialCommitment (cap {cap})")
        return rec

    def to_confirmed(self, candidate_id: str, now: datetime) -> LockRecord:
        rec = self._must_get(candidate_id)
        if rec.current_state != LockState.PartialCommitment:
            raise RuntimeError(f"cannot Confirm from {rec.current_state}")
        rec.current_state = LockState.Confirmed
        rec.entered_at = now
        self._log(f"{candidate_id} -> Confirmed")
        return rec

    def release(self, candidate_id: str, reason: str, now: datetime) -> LockRecord:
        rec = self._must_get(candidate_id)
        rec.current_state = LockState.Released
        rec.entered_at = now
        self._log(f"{candidate_id} -> Released ({reason})")
        return rec

    def get(self, candidate_id: str) -> Optional[LockRecord]:
        return self._records.get(candidate_id)

    # ---- internals ----

    def _must_get(self, cid: str) -> LockRecord:
        rec = self._records.get(cid)
        if rec is None:
            raise RuntimeError(f"no lock record for {cid}")
        return rec

    def _log(self, msg: str) -> None:
        self.events.append(msg)
