"""Email adapter: RFC 5322 .eml thread -> Ticket (06 §0.1).

Reassemble a thread by X-CloudServe-Ticket-Id, order by Date, decode
quoted-printable. body = the CUSTOMER-authored messages only (agent replies come
from @cloudserve.example and are not the customer's request). Note: `import email`
resolves to the stdlib top-level module, not this file (adapters.email).
"""
import email
from email import policy
from pathlib import Path
from models import Ticket, Channel

AGENT_DOMAIN = "cloudserve.example"


def _content(msg) -> str:
    body = msg.get_body(preferencelist=("plain",))
    if body is not None:
        return body.get_content()
    if not msg.is_multipart():
        return msg.get_content()
    return ""


def _strip_quoted(text: str) -> str:
    return "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith(">")).strip()


def parse_email(path: str) -> Ticket:
    p = Path(path)
    first = email.message_from_bytes(p.read_bytes(), policy=policy.default)
    ticket_id = first["X-CloudServe-Ticket-Id"] or p.stem.split("-msg-")[0]

    # gather the whole thread
    siblings = sorted(p.parent.glob(f"{ticket_id}-msg-*.eml"))
    msgs = [email.message_from_bytes(s.read_bytes(), policy=policy.default) for s in siblings] or [first]
    msgs.sort(key=lambda m: m["Date"] or "")

    customer_turns = [
        _strip_quoted(_content(m))
        for m in msgs
        if AGENT_DOMAIN not in (m["From"] or "")
    ]
    body = "\n\n".join(t for t in customer_turns if t) or _strip_quoted(_content(msgs[0]))

    subject = (first["Subject"] or "").removeprefix("Re: ").removeprefix("RE: ").strip()
    return Ticket(
        id=ticket_id,
        channel=Channel.EMAIL,
        subject=subject,
        body=body,
        customer_id=first["X-CloudServe-Customer-Id"] or "",
        created_at=first["Date"],
        pack_issue_type=None,
        raw={"headers": dict(first.items()), "message_count": len(msgs)},
    )
