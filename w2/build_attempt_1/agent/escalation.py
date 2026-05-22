"""Escalation routing — pure decision logic.

APD "Escalation triggers" + "Autonomy Matrix" map (reason -> queue):

  vip            -> Tom queue           (Discord webhook + #mod-vip-escalation)
  low_confidence -> volunteer mod queue (#mod-review-queue)
  multi_label    -> volunteer mod queue (annotated 'borderline')
  policy_gap     -> volunteer mod queue (annotated 'policy gap')
  api_failure    -> ops on-call (Discord #ops); item dead-lettered
"""
from __future__ import annotations

from .types import EscalationReason, EscalationQueue


_ROUTING = {
    EscalationReason.VIP: EscalationQueue.TOM,
    EscalationReason.LOW_CONFIDENCE: EscalationQueue.VOLUNTEER,
    EscalationReason.MULTI_LABEL: EscalationQueue.VOLUNTEER,
    EscalationReason.POLICY_GAP: EscalationQueue.VOLUNTEER,
    EscalationReason.API_FAILURE: EscalationQueue.OPS_ONCALL,
}


def route(reason: EscalationReason) -> EscalationQueue:
    """Total function. Raises on unknown reason rather than silent default."""
    try:
        return _ROUTING[reason]
    except KeyError as e:
        raise ValueError(f"unknown escalation reason: {reason}") from e


def annotation_for(reason: EscalationReason) -> str:
    return {
        EscalationReason.MULTI_LABEL: "borderline",
        EscalationReason.POLICY_GAP: "policy gap",
        EscalationReason.LOW_CONFIDENCE: "low confidence",
        EscalationReason.VIP: "vip account match",
        EscalationReason.API_FAILURE: "discourse api failure",
    }[reason]
