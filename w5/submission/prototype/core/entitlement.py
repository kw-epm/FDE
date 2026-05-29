"""Spec B — entitlement pre-fill + human-gate routing.

Does everything EXCEPT the decision: confirms type, classifies eligibility against
the KB policy tables (deterministically — not LLM judgment), pre-fills the request,
and routes it to the right human. It NEVER approves, issues, or promises an outcome.
`approved` is False on creation and no code path here sets it True (hard constraint #7).
"""
import config
from models import EntitlementRequest, RouteTarget


def _eligibility(body: str, ent_type: str) -> str:
    """Map to a refund-policy / cancellation-process category (06 §B.3 / Spec B.3)."""
    b = body.lower()
    if ent_type == "downgrade":
        return "MID_CYCLE_DOWNGRADE_INELIGIBLE"
    if "outage" in b or "service was down" in b or "down for" in b:
        return "OUTAGE_CREDIT_PRORATA"
    if ("cancelled" in b or "canceled" in b) and ("charged" in b or "charge" in b):
        return "POST_CANCELLATION_CHARGE"
    if "haven't used" in b or "havent used" in b or "forgot" in b or "didn't realise" in b \
            or "didnt realise" in b or "just realised" in b or "just realized" in b:
        return "FORGOT_TO_CANCEL_DISCRETIONARY"
    if "7 day" in b or "within a week" in b or "last week" in b:
        return "WITHIN_7_DAYS"
    return "NEEDS_HUMAN_LOOKUP"


def sanitize_holding_message(text: str) -> str:
    """Deterministic guarantee (B.4): block any outcome promise -> safe template.

    The model instruction (P3) is the first layer; this filter is the GUARANTEE.
    """
    low = (text or "").lower()
    if not text or any(p in low for p in config.FORBIDDEN_OUTCOME_PHRASES):
        return ("Thanks — I've submitted your request and routed it to a human reviewer. "
                "They'll confirm by email, usually within 1 business day. "
                "I can't decide the outcome myself.")
    return text


def handle_entitlement(ticket, record, classification, provider, route_override=None) -> EntitlementRequest:
    it = classification["issue_type"]
    ent_type = config.ISSUE_TO_ENTITLEMENT.get(it, "refund")

    route = route_override or config.ROUTE[ent_type]
    if record and record.plan_tier == "enterprise":
        route = RouteTarget.ACCOUNT_MGMT_VICTORIA_LIM  # never filed directly (hard constraint #3)

    category = _eligibility(ticket.body, ent_type)
    save_offer = (record is not None
                  and record.plan_tier in ("business", "enterprise")
                  and ent_type in ("cancellation", "downgrade"))

    pre_filled = {
        "plan_tier": record.plan_tier if record else None,
        "tenure_days": record.tenure_days if record else None,
        "mrr_usd": record.mrr_usd if record else None,
        "eligibility_category": category,
        "reason_summary": ticket.body[:160],
        "save_offer_available": save_offer,  # Free/Starter -> always False (Stated)
    }

    # P3 holding message (Sonnet live / template offline); the filter is the guarantee.
    raw = provider.holding_message(ent_type, pre_filled, record)
    message = sanitize_holding_message(raw)

    return EntitlementRequest(
        ticket_id=ticket.id,
        customer_id=ticket.customer_id,
        type=ent_type,
        eligibility_category=category,
        pre_filled_fields=pre_filled,
        route_to=route,
        customer_message=message,
        approved=False,                 # invariant — only a human flips this
        requires_human_approval=True,   # invariant
    )
