"""Triage worker — classifies the ticket and surfaces signals (Haiku, P1).

Decides nothing and routes nothing: it only labels. Its output is advisory input to
the coordinator and the deterministic guardrails, which make the binding calls.
"""


class TriageAgent:
    role = "triage"
    model = "haiku"

    def __init__(self, provider):
        self.provider = provider

    def run(self, ticket) -> dict:
        return self.provider.classify(ticket)
