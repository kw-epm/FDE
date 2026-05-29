"""FastAPI backend wrapping the ResolveOne agent — the demo surface for the React UI.

Reuses the exact agent (core/disposition.triage); the API is a thin presentation
layer, not a second implementation. Run:

    pip install -r requirements.txt fastapi "uvicorn[standard]"
    uvicorn server:app --reload --port 8000

Endpoints:
    GET  /api/health             provider + corpus sizes
    GET  /api/tickets            the demo paths + a sample of fixtures
    POST /api/resolve            {ticket_id} OR {channel,subject,body,customer_id} -> Disposition
"""
import json
import os
import queue
import sys
import threading
from dataclasses import asdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import config
from adapters import parse_chat, parse_phone, parse_email
from core.stores import CustomerStore
from core.retrieve import KBIndex
from core.audit import AuditLog
from core.disposition import triage
from core.agents.coordinator import AGENTS, Coordinator
from core.llm import build_provider
from models import Ticket, Channel

DATA = config.DATA_DIR


class _DemoAudit(AuditLog):
    """Interactive demo: allow re-running the same ticket (re-click). Still writes
    every disposition. Idempotency itself remains a real AuditLog property (tested
    in tests/, enforced in the batch demo.py / eval.py)."""
    def already_processed(self, ticket_id: str) -> bool:
        return False


# load once at startup
STORE = CustomerStore(os.path.join(DATA, "customers", "customer_master.csv"))
KB = KBIndex(os.path.join(DATA, "kb-articles"))
PROVIDER = build_provider()
AUDIT = _DemoAudit(os.path.join(DATA, "..", "audit_server.jsonl"))

# the four demo paths, in defense order
DEMO_TICKETS = [
    {"id": "CS-2026-0000002", "channel": "chat", "label": "Happy — password reset (Tier 1 auto-resolve)"},
    {"id": "CS-2026-0000011", "channel": "chat", "label": "Failure-mode — refund (Tier 2 human gate)"},
    {"id": "CS-2026-0000010", "channel": "phone", "label": "Edge — phone (defer, zero LLM calls)"},
    {"id": "CS-2026-0000306", "channel": "chat", "label": "Edge — return + legal threat (Tier 3 / Uma)"},
]

app = FastAPI(title="ResolveOne", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # prototype only; tighten for production
    allow_methods=["*"],
    allow_headers=["*"],
)


class ResolveRequest(BaseModel):
    ticket_id: str | None = None
    channel: str | None = "chat"
    subject: str | None = ""
    body: str | None = ""
    customer_id: str | None = None


def _load_ticket(tid: str) -> Ticket:
    chat = os.path.join(DATA, "tickets", f"{tid}.json")
    phone = os.path.join(DATA, "phone-calls", f"{tid}.vtt")
    if os.path.exists(chat):
        return parse_chat(chat)
    if os.path.exists(phone):
        return parse_phone(phone)
    import glob
    eml = glob.glob(os.path.join(DATA, "email-threads", f"{tid}-msg-01.eml"))
    if eml:
        return parse_email(eml[0])
    raise HTTPException(status_code=404, detail=f"ticket {tid} not found in fixtures")


def _build_ticket(req: "ResolveRequest") -> Ticket:
    if req.ticket_id:
        return _load_ticket(req.ticket_id)
    if not req.customer_id:
        raise HTTPException(status_code=422, detail="customer_id required for a pasted ticket")
    try:
        channel = Channel(req.channel.upper())
    except ValueError:
        raise HTTPException(status_code=422, detail=f"bad channel {req.channel}")
    return Ticket(id=f"CS-LIVE-{abs(hash((req.subject, req.body))) % 10**7:07d}",
                  channel=channel, subject=req.subject or "", body=req.body or "",
                  customer_id=req.customer_id)


def _serialize(d, ticket: Ticket) -> dict:
    out = asdict(d)
    out["action"] = d.action.value
    out["route_to"] = d.route_to.value if d.route_to else None
    out["channel"] = ticket.channel.value
    out["customer_id"] = ticket.customer_id
    out["subject"] = ticket.subject
    return out


# demo-path customers, resolved once at startup so they always appear in the dropdown
DEMO_CUSTOMER_IDS = []
for _t in DEMO_TICKETS:
    try:
        DEMO_CUSTOMER_IDS.append(_load_ticket(_t["id"]).customer_id)
    except Exception:
        pass


@app.get("/api/health")
def health():
    return {"provider": PROVIDER.name, "customers": len(STORE), "kb_articles": 20,
            "live": PROVIDER.name.startswith("live"),
            "topology": "coordinator + workers", "agents": AGENTS}


@app.get("/api/tickets")
def tickets():
    return {"demo": DEMO_TICKETS}


@app.get("/api/customers")
def customers():
    """A tier-spread set of real example customers for the form dropdown."""
    return {"customers": STORE.sample(include_ids=DEMO_CUSTOMER_IDS)}


@app.get("/api/tickets/{ticket_id}")
def ticket_detail(ticket_id: str):
    """Parsed ticket fields, so the UI can prefill the editable form from a demo path."""
    t = _load_ticket(ticket_id)  # raises 404 if unknown
    return {"ticket_id": t.id, "channel": t.channel.value.lower(),
            "subject": t.subject, "body": t.body, "customer_id": t.customer_id}


@app.post("/api/resolve")
def resolve(req: ResolveRequest):
    ticket = _build_ticket(req)
    calls_before = PROVIDER.calls
    d = triage(ticket, STORE, KB, PROVIDER, AUDIT)
    result = _serialize(d, ticket)
    result["llm_calls_this_request"] = PROVIDER.calls - calls_before
    result["customer_record_found"] = STORE.get(ticket.customer_id) is not None
    return result


@app.post("/api/resolve/stream")
def resolve_stream(req: ResolveRequest):
    """Same disposition, streamed as Server-Sent Events: one `step` event per agent
    call as it happens, then a final `result` event. Lets the UI show live progress."""
    ticket = _build_ticket(req)          # 404/422 raised here, before streaming starts
    q: "queue.Queue" = queue.Queue()
    DONE = object()

    def work():
        calls_before = PROVIDER.calls
        try:
            d = Coordinator(STORE, KB, PROVIDER, AUDIT).handle(ticket, on_event=q.put)
            result = _serialize(d, ticket)
            result["llm_calls_this_request"] = PROVIDER.calls - calls_before
            result["customer_record_found"] = STORE.get(ticket.customer_id) is not None
            q.put({"type": "result", "disposition": result})
        except Exception as e:  # surface as a stream event, not a 500 mid-stream
            q.put({"type": "error", "detail": str(e)})
        finally:
            q.put(DONE)

    threading.Thread(target=work, daemon=True).start()

    def gen():
        while True:
            ev = q.get()
            if ev is DONE:
                break
            yield f"data: {json.dumps(ev)}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


# Serve the built React UI from the same origin (container / production). Mounted last so
# the /api routes win; skipped in dev when there's no build (use `npm run dev` + proxy instead).
_UI_DIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui", "dist")
if os.path.isdir(_UI_DIST):
    app.mount("/", StaticFiles(directory=_UI_DIST, html=True), name="ui")

# Serve the whole app under /2905 and redirect / -> /2905/.
# (The React build is compiled with base "/2905/"; keep these in sync.)
BASE_PATH = "/2905"
_inner = app
app = FastAPI()


@app.get("/")
def _redirect_to_base():
    return RedirectResponse(url=f"{BASE_PATH}/", status_code=307)


app.mount(BASE_PATH, _inner)
