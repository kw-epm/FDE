"""Spec A entrypoint — now a thin shim over the multi-agent Coordinator (ADR-6).

The disposition logic moved into core/agents/coordinator.py when the design went
multi-agent on the Wednesday checkpoint steer. `triage(...)` is kept as the stable
call signature so demo.py / server.py / eval.py / tests don't care about the topology.
"""
from core.agents.coordinator import Coordinator


def triage(ticket, store, kb, provider, audit):
    return Coordinator(store, kb, provider, audit).handle(ticket)
