"""Ops alerting via webhook POST.

Per spec: if OPS_ALERT_WEBHOOK_URL is unset, write to stderr only.
A POST failure is logged and swallowed — alerts must never block the main loop.
"""
from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Optional

import httpx


log = logging.getLogger(__name__)


def send_alert(alert_type: str, message: str, details: Optional[dict] = None) -> None:
    payload = {
        "alert_type": alert_type,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "details": details or {},
    }

    webhook = os.environ.get("OPS_ALERT_WEBHOOK_URL", "").strip()
    if not webhook:
        sys.stderr.write(f"[OPS_ALERT] {json.dumps(payload)}\n")
        return

    try:
        with httpx.Client(timeout=5.0) as client:
            client.post(
                webhook,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
    except Exception as e:
        log.warning("ops alert POST failed (swallowed): %s | payload=%s", e, payload)
        sys.stderr.write(f"[OPS_ALERT_FALLBACK] {json.dumps(payload)}\n")
