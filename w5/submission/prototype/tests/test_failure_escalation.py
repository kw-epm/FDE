"""Failure-mode escalation: a refund is pre-filled and routed to a human, never approved."""
from helpers import ctx, load_chat
from core.disposition import triage
from core.entitlement import handle_entitlement
from models import Action, RouteTarget, Ticket, Channel


def test_refund_goes_to_human_gate():
    store, kb, provider, audit = ctx()
    d = triage(load_chat("CS-2026-0000011"), store, kb, provider, audit)
    assert d.tier == 2
    assert d.action == Action.PREFILL_AND_ROUTE
    assert d.route_to == RouteTarget.BILLING_RAVI_CHEN
    # holding message must not promise an outcome
    assert "approved" not in (d.draft or "").lower()


def test_entitlement_request_never_auto_approved():
    store, kb, provider, audit = ctx()
    t = load_chat("CS-2026-0000011")
    rec = store.get(t.customer_id)
    req = handle_entitlement(t, rec, provider.classify(t), provider)
    assert req.approved is False
    assert req.requires_human_approval is True
    assert req.eligibility_category == "FORGOT_TO_CANCEL_DISCRETIONARY"


def test_enterprise_cancellation_routes_to_account_mgmt_not_filed():
    """Enterprise + entitlement -> Tier 3, routed to Victoria Lim, NEVER filed directly (Spec B.5)."""
    store, kb, provider, audit = ctx()
    rec = store.get("CUST-001053")  # an enterprise customer in the fixtures
    assert rec and rec.plan_tier == "enterprise", "fixture CUST-001053 should be enterprise"
    t = Ticket(id="T-ENT-CANCEL", channel=Channel.CHAT, subject="cancel",
               body="We want to cancel our enterprise subscription.", customer_id="CUST-001053")
    d = triage(t, store, kb, provider, audit)
    assert d.tier == 3
    assert d.route_to == RouteTarget.ACCOUNT_MGMT_VICTORIA_LIM
    assert "ENTERPRISE_CONTRACT" in d.guardrail_flags
    assert d.action == Action.ESCALATE  # escalated to a human, not auto-filed (no PREFILL_AND_ROUTE)
