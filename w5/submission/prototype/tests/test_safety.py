"""Safety negatives — the properties that make this not just an LLM wrapper."""
import pytest

from helpers import ctx, load_chat
from core import guardrails
from core.disposition import triage
from core.entitlement import handle_entitlement, sanitize_holding_message
from core.llm import MockProvider
from models import (Action, RouteTarget, IssueType, Ticket, Channel, CustomerRecord,
                    Disposition, GuardrailFlag)


def test_guardrail_independence_refund_mislabelled_as_billing():
    """A refund worded as a billing question (mislabelled BILLING) must still hit the gate."""
    t = Ticket(id="T-X", channel=Channel.CHAT, subject="charge query",
               body="There is a charge on my card I want my money back for.",
               customer_id="CUST-001000")
    rec = CustomerRecord("CUST-001000", "starter", 49, 90, 8, 20, "standard")
    classification = {"issue_type": IssueType.BILLING_QUESTION, "confidence": 0.9,
                      "entitlement_signal": True, "legal_signal": False,
                      "distress_signal": False, "multi_intent": False}
    g = guardrails.apply(t, classification, rec)
    assert g["is_entitlement"] is True
    assert g["forced_tier"] >= 2
    assert GuardrailFlag.ENTITLEMENT.value in g["flags"]


def test_forbidden_phrase_filter_blocks_approval_promise():
    bad = "Good news — your refund is approved and you'll get your refund in 3 days."
    cleaned = sanitize_holding_message(bad)
    assert "approved" not in cleaned.lower()
    assert "you'll get your refund" not in cleaned.lower()


def test_legal_overrides_entitlement_route():
    """Return + attorney-general language -> Tier 3 / Uma, not Tier 2 / Billing."""
    store, kb, provider, audit = ctx()
    d = triage(load_chat("CS-2026-0000306"), store, kb, provider, audit)
    assert d.tier == 3
    assert d.route_to == RouteTarget.COMPLIANCE_UMA_BARDWAJ
    assert GuardrailFlag.LEGAL.value in d.guardrail_flags


def test_auto_resolve_requires_kb_citation_invariant():
    with pytest.raises(ValueError):
        Disposition("T-Y", 1, "PASSWORD_RESET", 0.9, [], Action.AUTO_RESOLVE,
                    None, "draft", [], "should fail: no kb")


def test_missing_customer_record_fails_loud():
    """customer_master unreachable / record missing -> fail loud to a human, no auto-resolve (#7 INT-1)."""
    store, kb, provider, audit = ctx()
    t = Ticket(id="T-NOCUST", channel=Channel.CHAT, subject="help",
               body="please reset my password", customer_id="CUST-999999")  # not in the store
    d = triage(t, store, kb, provider, audit)
    assert d.tier == 3
    assert d.action == Action.ESCALATE
    assert d.route_to == RouteTarget.CSR_POOL
    assert GuardrailFlag.CUSTOMER_RECORD_MISSING.value in d.guardrail_flags
    assert d.kb_articles == []        # never auto-resolved on a degraded source
    assert provider.calls == 0        # fails loud before any model call


def test_no_entitlement_type_is_ever_auto_approved():
    provider = MockProvider()
    rec = CustomerRecord("CUST-001000", "business", 499, 400, 7, 30, "priority")
    cases = {
        IssueType.REFUND_REQUEST: "I want a refund please",
        IssueType.SERVICE_CANCELLATION: "I want to cancel my subscription",
        IssueType.SERVICE_DOWNGRADE: "please downgrade my plan",
        IssueType.RETURN_REQUEST: "I want to return the welcome kit",
    }
    for it, body in cases.items():
        t = Ticket(id=f"T-{it.value}", channel=Channel.CHAT, subject="x",
                   body=body, customer_id="CUST-001000")
        classification = {"issue_type": it, "confidence": 0.9, "entitlement_signal": True,
                          "legal_signal": False, "distress_signal": False, "multi_intent": False}
        req = handle_entitlement(t, rec, classification, provider)
        assert req.approved is False
        assert req.requires_human_approval is True
