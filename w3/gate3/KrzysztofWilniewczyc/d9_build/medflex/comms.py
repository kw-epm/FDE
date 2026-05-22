"""Step 9 — Outbound comms layer (SMS + email). Mocked.

Production impl would call Twilio/SendGrid; here we record sent messages
and let the test harness simulate a nurse response.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class SentMessage:
    to_nurse_id: str
    channel: str
    body: str
    when: datetime


class CommsLayer:
    def __init__(self, *, fail_first_n: int = 0):
        self.sent: list[SentMessage] = []
        self._fail_first_n = fail_first_n
        self._attempts = 0

    def send(self, *, nurse_id: str, body: str, channels: list[str],
             when: datetime) -> list[SentMessage]:
        # Retry-with-backoff (D#4a §7) — simulated: count attempts, raise on early ones
        self._attempts += 1
        if self._attempts <= self._fail_first_n:
            raise RuntimeError(f"comms transient failure (attempt {self._attempts})")
        out = []
        for ch in channels:
            msg = SentMessage(to_nurse_id=nurse_id, channel=ch, body=body, when=when)
            self.sent.append(msg)
            out.append(msg)
        return out
