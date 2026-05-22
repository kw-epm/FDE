"""Discourse REST API client — STUB.

APD: Discourse write API auth scope is unconfirmed (P0 launch blocker).
We define the surface the agent calls so the orchestrator can be wired and
tested. Real endpoints from APD action mapping table:

  - DELETE /posts/{id}                       (remove; soft delete)
  - PUT    /posts/{id}/recover               (reversal; admin only)
  - POST   /private_messages                 (warn)
  - POST   /flags/{id} disagree=true         (dismiss_flag)
  - POST   /categories/.../topics            (escalate -> mod-review-queue)

Until auth scope is confirmed, the stub records calls and returns success.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


class DiscourseApiError(Exception):
    pass


@dataclass
class CallRecord:
    method: str
    path: str
    payload: Dict[str, Any] = field(default_factory=dict)


class DiscourseClient:
    """Stub Discourse client. Records all calls; raises on demand for tests."""

    def __init__(self, fail_on: Optional[str] = None) -> None:
        self.calls: List[CallRecord] = []
        self._fail_on = fail_on  # path substring to trigger failure

    def _record(self, method: str, path: str, payload: Optional[Dict] = None) -> None:
        self.calls.append(CallRecord(method=method, path=path, payload=payload or {}))
        if self._fail_on and self._fail_on in path:
            raise DiscourseApiError(f"injected failure on {path}")

    # --- Read ---
    def poll_flag_queue(self) -> List[Dict[str, Any]]:
        """Task 1.1. Returns raw flag records."""
        self._record("GET", "/review.json?status=pending")
        return []

    def fetch_post(self, post_id: str) -> Dict[str, Any]:
        """Task 1.2."""
        self._record("GET", f"/posts/{post_id}.json")
        return {}

    def fetch_account_history(self, account_id: int) -> Dict[str, Any]:
        """Task 1.5H — only called when confidence in [0.6, 0.8]."""
        self._record("GET", f"/users/by-id/{account_id}.json")
        return {"prior_flags": 0, "prior_actions": []}

    # --- Write (P0: auth scope unconfirmed) ---
    def remove_post(self, post_id: str, processing_id: str) -> None:
        self._record("DELETE", f"/posts/{post_id}", {"processing_id": processing_id})

    def recover_post(self, post_id: str) -> None:
        self._record("PUT", f"/posts/{post_id}/recover")

    def send_warning_pm(self, account_id: int, body: str, processing_id: str) -> None:
        self._record("POST", "/private_messages",
                     {"target_user_id": account_id, "raw": body,
                      "processing_id": processing_id})

    def dismiss_flag(self, flag_id: str, processing_id: str) -> None:
        self._record("POST", f"/flags/{flag_id}",
                     {"disagree": True, "processing_id": processing_id})

    def write_to_category(self, category: str, title: str, body: str,
                          processing_id: str) -> None:
        """Used for escalation queues (mod-review-queue, mod-vip-escalation)
        and for the moderation log topic (task 1.7)."""
        self._record("POST", f"/categories/{category}/topics",
                     {"title": title, "raw": body,
                      "processing_id": processing_id})

    def tag_for_qa(self, post_id: str, tag: str = "agent-qa-sample") -> None:
        """Task 1.7Q — tag 5% of agent-dismissed items for daily review."""
        self._record("PUT", f"/posts/{post_id}/tags", {"tag": tag})

    # --- Idempotency check (relies on log/action history) ---
    def has_action_for_processing_id(self, processing_id: str) -> bool:
        """Per APD Operational Constraints — idempotency check before 1.6.

        Production implementation: query the moderation log topic (or a
        side-table) for a row with this processing_id. Stub: returns False.
        """
        self._record("GET", f"/idempotency/{processing_id}")
        return False
