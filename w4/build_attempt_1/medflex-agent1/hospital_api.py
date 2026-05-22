"""Hospital profile fetch with 1-hour in-memory cache."""
from __future__ import annotations

import json
import logging
import os
import time as _time
from pathlib import Path
from typing import Optional, Dict, Any

import httpx

log = logging.getLogger(__name__)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "hospital_profiles.json"
CACHE_TTL_SECONDS = 3600


class HospitalAPIError(Exception):
    pass


class HospitalAPIClient:
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None, timeout: float = 10.0):
        self.base_url = base_url or os.environ.get("MEDFLEX_API_BASE_URL", "mock")
        self.api_key = api_key or os.environ.get("MEDFLEX_API_KEY")
        self.timeout = timeout
        self.is_mock = self.base_url == "mock"
        self._cache: Dict[str, tuple[float, Dict[str, Any]]] = {}
        self._mock_data: Optional[Dict[str, Any]] = None

    def _load_mock(self) -> Dict[str, Any]:
        if self._mock_data is None:
            self._mock_data = json.loads(FIXTURE_PATH.read_text())
        return self._mock_data

    def get_profile(self, hospital_id: str) -> Optional[Dict[str, Any]]:
        """Return hospital profile dict, or None on failure (FM-3 fallback).

        For mock mode, returns _default if hospital_id is not present (which
        is treated as 'found'). Returns None ONLY for the real-API failure
        path so callers can detect FM-3.
        """
        # cache
        cached = self._cache.get(hospital_id)
        if cached and (_time.time() - cached[0]) < CACHE_TTL_SECONDS:
            return cached[1]

        if self.is_mock:
            data = self._load_mock()
            profile = data.get(hospital_id) or data.get("_default")
            if profile is not None:
                self._cache[hospital_id] = (_time.time(), profile)
            return profile

        # real
        url = f"{self.base_url}/hospitals/{hospital_id}/profile"
        headers = {"X-API-Key": self.api_key} if self.api_key else {}
        try:
            with httpx.Client(timeout=self.timeout) as client:
                r = client.get(url, headers=headers)
        except Exception as e:  # noqa: BLE001
            log.warning("hospital_profile_fetch_failed hospital_id=%s err=%s", hospital_id, e)
            return None
        if r.status_code == 200:
            profile = r.json()
            self._cache[hospital_id] = (_time.time(), profile)
            return profile
        log.warning("hospital_profile_bad_status hospital_id=%s status=%s", hospital_id, r.status_code)
        return None

    def hospital_exists(self, hospital_id: str) -> bool:
        """For EC-6 (unknown hospital). In mock mode this means: explicit key
        (not just the _default fallback) is present.
        """
        if self.is_mock:
            data = self._load_mock()
            return hospital_id in data and hospital_id != "_default"
        # in real mode we treat 200 vs 404 as the answer
        prof = self.get_profile(hospital_id)
        return prof is not None
