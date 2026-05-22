"""ServiceNow polling client.

When SERVICENOW_BASE_URL=mock, reads from fixtures/servicenow_fixture.json.
Otherwise issues a real GET against the configured ServiceNow REST endpoint.
"""
from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import List

import httpx

from models import ServiceNowTicket


log = logging.getLogger(__name__)


class ServiceNowError(Exception):
    """Recoverable failure (5xx, timeout). Caller may retry."""


class ServiceNowAuthError(Exception):
    """401/403 — pause polling until token refreshed."""


class ServiceNowRateLimitError(Exception):
    """429 — honour Retry-After."""

    def __init__(self, retry_after_seconds: int):
        self.retry_after_seconds = retry_after_seconds
        super().__init__(f"429 rate limited, retry after {retry_after_seconds}s")


def _fixture_path() -> Path:
    return Path(__file__).parent / "fixtures" / "servicenow_fixture.json"


def _is_mock() -> bool:
    return os.environ.get("SERVICENOW_BASE_URL", "").lower() == "mock"


def fetch_new_tickets(poll_interval_minutes: int) -> List[ServiceNowTicket]:
    """Fetch tickets created in the last `poll_interval_minutes`.

    Returns a list of ServiceNowTicket objects. Raises ServiceNowError on 5xx/timeout,
    ServiceNowAuthError on 401/403, ServiceNowRateLimitError on 429.
    """
    if _is_mock():
        return _fetch_from_fixture()
    return _fetch_from_api(poll_interval_minutes)


def _fetch_from_fixture() -> List[ServiceNowTicket]:
    path = _fixture_path()
    if not path.exists():
        log.warning("ServiceNow fixture not found: %s", path)
        return []
    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    return [ServiceNowTicket(**row) for row in raw]


def _fetch_from_api(poll_interval_minutes: int) -> List[ServiceNowTicket]:
    base_url = os.environ["SERVICENOW_BASE_URL"].rstrip("/")
    table = os.environ.get("SHIFT_REQUEST_TABLE_NAME", "u_shift_requests")
    token = os.environ.get("SERVICENOW_OAUTH_TOKEN")
    if not token:
        raise ServiceNowAuthError("SERVICENOW_OAUTH_TOKEN not set")

    url = f"{base_url}/api/now/table/{table}"
    params = {
        "sysparm_query": (
            f"state=open^sys_created_on>javascript:gs.minutesAgoStart({poll_interval_minutes})"
        ),
        "sysparm_fields": "sys_id,description,u_hospital_id,sys_created_on",
        "sysparm_limit": 100,
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url, params=params, headers=headers)
    except httpx.TimeoutException as e:
        raise ServiceNowError(f"timeout: {e}") from e
    except httpx.RequestError as e:
        raise ServiceNowError(f"request error: {e}") from e

    status = resp.status_code
    if status == 200:
        body = resp.json()
        rows = body.get("result", []) or []
        return [ServiceNowTicket(**row) for row in rows]
    if status == 204:
        return []
    if status in (401, 403):
        raise ServiceNowAuthError(f"HTTP {status}")
    if status == 429:
        retry_after = int(resp.headers.get("Retry-After", "60"))
        raise ServiceNowRateLimitError(retry_after)
    if 500 <= status < 600:
        raise ServiceNowError(f"HTTP {status}")
    raise ServiceNowError(f"unexpected HTTP {status}: {resp.text[:200]}")


def fetch_with_retry(poll_interval_minutes: int) -> List[ServiceNowTicket]:
    """Wrap fetch_new_tickets with one 30s retry on 5xx/timeout (spec FM-1 prep)."""
    try:
        return fetch_new_tickets(poll_interval_minutes)
    except ServiceNowError as first_err:
        log.warning("ServiceNow poll failed (%s); retrying in 30s", first_err)
        time.sleep(30)
        return fetch_new_tickets(poll_interval_minutes)
