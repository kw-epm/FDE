"""Entitlement worker — Spec B: eligibility + pre-fill + human-gate routing (Sonnet, P3).

Does everything except the decision. Wraps core.entitlement.handle_entitlement, which
classifies eligibility deterministically against the KB tables, pre-fills the request,
and writes a holding message that the deterministic filter guarantees promises nothing.
It NEVER sets approved=True — only a human does.
"""
from core.entitlement import handle_entitlement


class EntitlementAgent:
    role = "entitlement"
    model = "sonnet"

    def __init__(self, provider):
        self.provider = provider

    def run(self, ticket, record, classification, route_override=None):
        return handle_entitlement(ticket, record, classification, self.provider, route_override)
