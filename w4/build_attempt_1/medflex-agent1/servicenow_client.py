"""ServiceNow client. Real HTTP when SERVICENOW_BASE_URL != 'mock'.

For 'mock' mode we read fixtures/servicenow_fixture.json each poll cycle
and return its contents.
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import List, Dict, Any

import httpx

log = logging.getLogger(__name__)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "servicenow_fixture.json"


class ServiceNowError(Exception):
    pass


class ServiceNowClient:
    def __init__(
        self,
        base_url: str | None = None,
        oauth_token: str | None = None,
        table_name: str | None = None,
        timeout: float = 10.0,
    ):
        self.base_url = base_url or os.environ.get("SERVICENOW_BASE_URL", "mock")
        self.oauth_token = oauth_token or os.environ.get("SERVICENOW_OAUTH_TOKEN")
        self.table_name = table_name or os.environ.get(
            "SHIFT_REQUEST_TABLE_NAME", "u_shift_requests"
        )
        self.timeout = timeout
        self.is_mock = self.base_url == "mock"

    def fetch_tickets(self, poll_interval_minutes: int = 2) -> List[Dict[str, Any]]:
        """Return a list of ticket dicts with keys sys_id, description,
        u_hospital_id, sys_created_on.
        """
        if self.is_mock:
            return self._fetch_mock()
        return self._fetch_real(poll_interval_minutes)

    def _fetch_mock(self) -> List[Dict[str, Any]]:
        if not FIXTURE_PATH.exists():
            log.warning("ServiceNow mock fixture not found: %s", FIXTURE_PATH)
            return []
        return json.loads(FIXTURE_PATH.read_text())

    def _fetch_real(self, poll_interval_minutes: int) -> List[Dict[str, Any]]:
        if not self.oauth_token:
            raise ServiceNowError("SERVICENOW_OAUTH_TOKEN not configured")
        url = f"{self.base_url}/api/now/table/{self.table_name}"
        params = {
            "sysparm_query": (
                f"state=open^sys_created_on>javascript:gs.minutesAgoStart({poll_interval_minutes})"
            ),
            "sysparm_fields": "sys_id,description,u_hospital_id,sys_created_on",
            "sysparm_limit": "100",
        }
        headers = {"Authorization": f"Bearer {self.oauth_token}"}
        try:
            with httpx.Client(timeout=self.timeout) as client:
                r = client.get(url, params=params, headers=headers)
        except httpx.TimeoutException as e:
            raise ServiceNowError(f"timeout: {e}") from e
        if r.status_code == 204:
            return []
        if r.status_code == 200:
            return r.json().get("result", [])
        if r.status_code in (401, 403):
            raise ServiceNowError(f"auth_failed:{r.status_code}")
        if r.status_code == 429:
            raise ServiceNowError(f"rate_limited:{r.headers.get('Retry-After', '')}")
        if 500 <= r.status_code < 600:
            raise ServiceNowError(f"server_error:{r.status_code}")
        raise ServiceNowError(f"unexpected:{r.status_code}")
