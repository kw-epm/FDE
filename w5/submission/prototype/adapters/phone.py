"""Phone adapter: WebVTT -> Ticket, HEADER ONLY (ADR-4, hard constraint #2).

Reads the NOTE block (ticket_id, customer_id, channel) and STOPS at the first
cue. It never parses or transcribes the conversation — phone is out of scope
pending platform modernisation, and reading the transcript would breach that.
"""
from pathlib import Path
from models import Ticket, Channel


def parse_phone(path: str) -> Ticket:
    notes = {}
    for line in Path(path).read_text().splitlines():
        if line.startswith("NOTE ") and ":" in line:
            k, v = line[5:].split(":", 1)
            notes[k.strip()] = v.strip()
        elif line.strip() and not line.startswith(("WEBVTT", "NOTE")):
            break  # first cue (or its index) — we do NOT read transcript content
    return Ticket(
        id=notes.get("ticket_id", Path(path).stem),
        channel=Channel.PHONE,
        subject="(phone call)",
        body="",                      # intentionally empty — transcript never read
        customer_id=notes.get("customer_id", ""),
        created_at=notes.get("intake_ts"),
        pack_issue_type=None,
        raw={"notes": notes},
    )
