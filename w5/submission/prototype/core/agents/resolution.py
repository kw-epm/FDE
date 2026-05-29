"""Resolution worker — composes a KB-grounded Tier-1 reply (Sonnet, P2-compose).

Only invoked after the coordinator has decided Tier 1 AND the deterministic envelope
allows it. Returns {"draft", "kb_articles"}; draft is null if no KB article supports
an answer (the coordinator then routes to a human).
"""


class ResolutionAgent:
    role = "resolution"
    model = "sonnet"

    def __init__(self, provider):
        self.provider = provider

    def run(self, ticket, classification, kb_top) -> dict:
        return self.provider.compose_reply(ticket, classification, kb_top)
