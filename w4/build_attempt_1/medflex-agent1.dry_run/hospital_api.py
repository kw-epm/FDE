"""Hospital profile fetch with 1-hour in-memory cache.

When MEDFLEX_API_BASE_URL=mock, reads from fixtures/hospital_profiles.json.
Otherwise issues a real GET against the configured MedFlex API.
"""
from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Optional

import httpx


log = logging.getLogger(__name__)

_CACHE_TTL_SECONDS = 60 * 60  # 1 hour per spec
_cache: dict[str, tuple[float, dict]] = {}
_fixture_cache: Optional[dict] = None


def _is_mock() -> bool:
    return os.environ.get("MEDFLEX_API_BASE_URL", "").lower() == "mock"


def _load_fixture() -> dict:
    global _fixture_cache
    if _fixture_cache is None:
        path = Path(__file__).parent / "fixtures" / "hospital_profiles.json"
        with path.open("r", encoding="utf-8") as f:
            _fixture_cache = json.load(f)
    return _fixture_cache


def _fetch_from_fixture(hospital_id: str) -> dict:
    data = _load_fixture()
    if hospital_id in data:
        return data[hospital_id]
    log.info("hospital_id %s not in fixture; using _default", hospital_id)
    return data.get("_default", {})


def _fetch_from_api(hospital_id: str) -> Optional[dict]:
    base_url = os.environ["MEDFLEX_API_BASE_URL"].rstrip("/")
    api_key = os.environ.get("MEDFLEX_API_KEY")
    url = f"{base_url}/hospitals/{hospital_id}/profile"
    headers = {"X-API-Key": api_key or "", "Accept": "application/json"}
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(url, headers=headers)
    except httpx.RequestError as e:
        log.warning("hospital profile fetch failed for %s: %s", hospital_id, e)
        return None
    if resp.status_code == 200:
        return resp.json()
    log.warning(
        "hospital profile fetch returned HTTP %s for %s", resp.status_code, hospital_id
    )
    return None


def get_hospital_profile(hospital_id: str) -> Optional[dict]:
    """Return cached profile or fetch fresh. Returns None on hard failure (non-mock).

    Per spec: missing hospital profile is NOT a blocker — caller should proceed
    with defaults and log a warning.
    """
    now = time.time()
    entry = _cache.get(hospital_id)
    if entry is not None and (now - entry[0]) < _CACHE_TTL_SECONDS:
        return entry[1]

    if _is_mock():
        profile = _fetch_from_fixture(hospital_id)
    else:
        profile = _fetch_from_api(hospital_id)

    if profile is not None:
        _cache[hospital_id] = (now, profile)
    return profile


def hospital_exists(hospital_id: str) -> bool:
    """EC-6 support: does the hospital_id resolve to a real registry entry?

    In mock mode, an entry must be present explicitly (we do NOT count _default as
    "exists" — _default is a fallback only when the hospital IS known but the
    profile fetch fails). This lets EC-6 (unknown hospital) be exercised.
    """
    if _is_mock():
        data = _load_fixture()
        return hospital_id in data and hospital_id != "_default"
    profile = get_hospital_profile(hospital_id)
    return profile is not None


def default_profile() -> dict:
    """Profile shape used when hospital profile API is unavailable (FM-3)."""
    return {
        "standard_shift_times": {
            "days": {"start": "07:00", "end": "19:00"},
            "nights": {"start": "19:00", "end": "07:00"},
            "evenings": {"start": "15:00", "end": "23:00"},
        },
        "preferred_credential_categories": ["RN"],
        "common_unit_types": ["MED_SURG", "GENERAL"],
        "coordinates": None,
    }
