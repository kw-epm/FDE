"""Edge case: a phone ticket is deferred with ZERO LLM calls (never transcribed)."""
from helpers import ctx, load_phone
from core.disposition import triage
from models import Action, RouteTarget


def test_phone_deferred_zero_llm_calls():
    store, kb, provider, audit = ctx()
    t = load_phone("CS-2026-0000010")
    before = provider.calls
    d = triage(t, store, kb, provider, audit)
    assert d.action == Action.DEFER_PHONE
    assert d.tier == 3
    assert d.route_to == RouteTarget.HUMAN_QUEUE
    assert provider.calls == before, "phone path must make ZERO LLM calls"


def test_phone_body_never_read():
    # the adapter must not pull transcript content into the ticket body
    t = load_phone("CS-2026-0000010")
    assert t.body == ""
    assert t.customer_id == "CUST-001797"
