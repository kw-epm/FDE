"""Chat adapter: Zendesk-style JSON -> Ticket.

body = customer turns where internal_note is false; agent turns and internal notes
are ignored for classification (they are the *previous human's* work, not the
customer's request).
"""
import json
from pathlib import Path
from models import Ticket, Channel


def parse_chat(path: str) -> Ticket:
    d = json.loads(Path(path).read_text())
    cust_turns = [
        m["message"]
        for m in d.get("chat_transcript", [])
        if m.get("speaker") == "customer" and not m.get("internal_note")
    ]
    req = d.get("requester", {})
    return Ticket(
        id=d["id"],
        channel=Channel.CHAT,
        subject=d.get("subject", ""),
        body="\n".join(cust_turns) or d.get("description", ""),
        customer_id=req.get("customer_id", ""),
        created_at=d.get("created_at"),
        sla_target_minutes=d.get("sla_target_minutes"),
        pack_issue_type=d.get("issue_type"),  # audit only — never ground truth
        raw=d,
    )
