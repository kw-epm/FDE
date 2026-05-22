"""Action mapping — task 1.5 (rule lookup, no inference).

APD "Action Mapping Table" determines the Discourse endpoint per action.
The decision input is (violation_type, confidence) plus prior escalation
flags from the classification step.

This module is pure logic. No I/O. Unit-testable.
"""
from __future__ import annotations

from typing import Tuple

from .types import Action, ViolationType, Classification, EscalationReason


# Confidence thresholds — APD escalation triggers section.
# [Unconfirmed: provisional values 0.6 / 0.8 — open blocker per APD.]
CONFIDENCE_LOW = 0.6
CONFIDENCE_HIGH = 0.8

# Multi-label trigger
TOP2_DELTA_THRESHOLD = 0.15


def map_to_action(c: Classification) -> Action:
    """Return the action to execute given a classification.

    The classifier itself may already have set action=ESCALATE with a reason;
    in that case we honour the escalation. Otherwise we apply the rules.
    """
    # Honour classifier escalation
    if c.action == Action.ESCALATE:
        return Action.ESCALATE

    # Defensive: classifier returned a non-escalate action but the data
    # actually triggers an escalation rule. Re-route.
    if c.confidence < CONFIDENCE_LOW:
        return Action.ESCALATE
    if c.top2_score_delta < TOP2_DELTA_THRESHOLD:
        return Action.ESCALATE

    # No-violation -> dismiss_flag (post stays)
    if c.violation_type == ViolationType.NO_VIOLATION:
        return Action.DISMISS_FLAG

    # Default mapping for clear violations.
    # APD does not specify warn-vs-remove for spam/off_topic/miscategorised
    # at the rule level — see clarifying questions. We default to remove for
    # spam (matches "routine spam removal" stream framing) and dismiss-with-warn
    # is reserved for the classifier to choose explicitly via action=warn.
    if c.action in (Action.REMOVE, Action.WARN, Action.DISMISS_FLAG):
        return c.action

    # Fallback — escalate rather than guess. Never silent-default.
    return Action.ESCALATE


def needs_hitl_reeval(c: Classification) -> bool:
    """Task 1.5H gate: confidence in [0.6, 0.8) AND no escalation already set."""
    if c.action == Action.ESCALATE:
        return False
    return CONFIDENCE_LOW <= c.confidence < CONFIDENCE_HIGH


def derive_escalation_reason(c: Classification) -> EscalationReason:
    """Pick the most specific escalation reason for routing."""
    if c.escalation_reason is not None:
        return c.escalation_reason
    if c.confidence < CONFIDENCE_LOW:
        return EscalationReason.LOW_CONFIDENCE
    if c.top2_score_delta < TOP2_DELTA_THRESHOLD:
        return EscalationReason.MULTI_LABEL
    if CONFIDENCE_LOW <= c.confidence < CONFIDENCE_HIGH:
        return EscalationReason.LOW_CONFIDENCE
    # Should not reach here for non-escalate paths
    return EscalationReason.LOW_CONFIDENCE
