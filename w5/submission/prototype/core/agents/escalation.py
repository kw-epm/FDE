"""Escalation worker — composes the Tier-3 human briefing (Sonnet, P4).

Invoked when a guardrail forces Tier 3 (legal / abuse / enterprise) or the coordinator
judges genuine complexity / distress. Produces an internal briefing for the named human
specialist — never a promise to the customer.
"""


class EscalationAgent:
    role = "escalation"
    model = "sonnet"

    def __init__(self, provider):
        self.provider = provider

    def run(self, ticket, classification, record, flags) -> str:
        return self.provider.briefing(ticket, classification, record, flags)
