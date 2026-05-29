"""Append-only audit log + idempotency (06 §0.5, §0.8).

Write-ahead is the commit point: the audit record is written BEFORE a reply is
sent or an entitlement is routed. If the write fails, the action does not occur,
which makes the flow replay-safe. One immutable JSON line per ticket.
"""
import json
from pathlib import Path
from dataclasses import asdict
from datetime import datetime, timezone


class AuditLog:
    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._seen = set()
        if self.path.exists():
            for line in self.path.read_text().splitlines():
                try:
                    self._seen.add(json.loads(line)["ticket_id"])
                except Exception:
                    pass

    def already_processed(self, ticket_id: str) -> bool:
        return ticket_id in self._seen  # idempotency: re-delivery is a no-op

    def write(self, disposition, entitlement=None):
        rec = {
            **asdict(disposition),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "idempotency_key": disposition.ticket_id,
            "processing_status": "TERMINAL",
        }
        rec["action"] = getattr(disposition.action, "value", disposition.action)
        rec["route_to"] = disposition.route_to.value if disposition.route_to else None
        if entitlement is not None:
            rec["entitlement"] = {
                "type": entitlement.type,
                "approved": entitlement.approved,
                "requires_human_approval": entitlement.requires_human_approval,
                "route_to": entitlement.route_to.value,
                "eligibility_category": entitlement.eligibility_category,
                "pre_filled_fields": entitlement.pre_filled_fields,
            }
        with self.path.open("a") as f:
            f.write(json.dumps(rec, default=str) + "\n")  # write-ahead = commit point
        self._seen.add(disposition.ticket_id)
