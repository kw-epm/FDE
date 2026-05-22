"""Steps 2 + 3 — Eligibility filter and compliance precondition."""
from __future__ import annotations

from datetime import datetime, timedelta

from .entities import Nurse, ShiftRequest


# Geo proximity bound — A6 says structure is uncertain; we just use distance_km.
MAX_DISTANCE_KM = 25.0


def eligible(nurse: Nurse, req: ShiftRequest) -> tuple[bool, str]:
    intent = req.parsed_intent

    if not nurse.available:
        return False, "unavailable"

    if intent.specialty and intent.specialty not in nurse.specialties:
        return False, f"specialty {intent.specialty!r} not in {nurse.specialties}"

    missing = [c for c in intent.credentials if c not in nurse.credentials]
    if missing:
        return False, f"missing credentials {missing}"

    if nurse.distance_km > MAX_DISTANCE_KM:
        return False, f"distance {nurse.distance_km}km exceeds {MAX_DISTANCE_KM}km"

    if req.hospital_id in nurse.dnr_hospitals:
        return False, f"DNR: {req.hospital_id}"

    return True, "eligible"


def credentials_valid_for_shift(nurse: Nurse, shift_date: datetime) -> tuple[bool, str]:
    # Step 3: credential expiry vs shift date.
    if nurse.credential_expiry < shift_date:
        return False, (
            f"credential expires {nurse.credential_expiry.date()} "
            f"before shift {shift_date.date()}"
        )
    return True, "valid"


def filter_pool(
    nurses: list[Nurse], req: ShiftRequest, shift_date: datetime
) -> tuple[list[Nurse], list[tuple[Nurse, str]]]:
    """Return (eligible_pool, rejections_with_reasons)."""
    keep: list[Nurse] = []
    drop: list[tuple[Nurse, str]] = []
    for n in nurses:
        ok, why = eligible(n, req)
        if not ok:
            drop.append((n, why))
            continue
        ok2, why2 = credentials_valid_for_shift(n, shift_date)
        if not ok2:
            drop.append((n, f"compliance: {why2}"))
            continue
        keep.append(n)
    return keep, drop
