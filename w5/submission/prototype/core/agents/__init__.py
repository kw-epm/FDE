"""Multi-agent topology (ADR-6): a Coordinator orchestrating specialist workers.

Hub-and-spoke delegation — the coordinator invokes each worker and synthesises the
result; workers never talk to each other. Communication is in-process typed
messages (Ticket -> classification dict -> Disposition / EntitlementRequest), not a
wire protocol. The deterministic guardrail gate sits between the coordinator and the
workers and can only downgrade autonomy (ADR-1).
"""
from core.agents.coordinator import Coordinator
from core.agents.triage import TriageAgent
from core.agents.resolution import ResolutionAgent
from core.agents.entitlement import EntitlementAgent
from core.agents.escalation import EscalationAgent

__all__ = ["Coordinator", "TriageAgent", "ResolutionAgent", "EntitlementAgent", "EscalationAgent"]
