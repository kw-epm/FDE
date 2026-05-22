"""Type definitions matching the APD's structured-output schema.

APD section: "Prompt principles" item 3 (structured output schema) and
"Activity Catalog" notes (1.7 log schema).
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone


class ViolationType(str, Enum):
    SPAM = "spam"
    OFF_TOPIC = "off_topic"
    MISCATEGORISED = "miscategorised"
    NO_VIOLATION = "no_violation"


class Action(str, Enum):
    REMOVE = "remove"
    WARN = "warn"
    DISMISS_FLAG = "dismiss_flag"
    ESCALATE = "escalate"


class EscalationReason(str, Enum):
    VIP = "vip"
    LOW_CONFIDENCE = "low_confidence"
    MULTI_LABEL = "multi_label"
    POLICY_GAP = "policy_gap"
    API_FAILURE = "api_failure"  # added for dead-letter route; APD lists separately


class EscalationQueue(str, Enum):
    TOM = "tom_queue"  # Discord webhook + #mod-vip-escalation
    VOLUNTEER = "volunteer_mod_queue"  # #mod-review-queue
    OPS_ONCALL = "ops_oncall"  # Discord #ops; dead-lettered


@dataclass
class FlagItem:
    """Output of task 1.2 — extracted from Discourse flag queue."""
    processing_id: str  # assigned at 1.1; idempotency key
    item_id: str  # Discourse post id
    flag_id: str
    account_id: int  # integer per APD note on 1.3 (no string usernames)
    sub_forum_id: str
    post_text: str
    reporter_count: int
    flag_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Classification:
    """Structured output of task 1.4. Schema enforced; deviation = error.

    Invariant per APD: action == 'escalate' iff escalation_reason is not None.
    """
    violation_type: ViolationType
    confidence: float  # [0, 1]
    action: Action
    escalation_reason: Optional[EscalationReason]
    top2_score_delta: float  # for multi-label trigger
    reasoning: str = ""  # chain of thought for confidence in [0.6, 0.8]

    def __post_init__(self) -> None:
        # Schema invariant
        is_escalate = self.action == Action.ESCALATE
        has_reason = self.escalation_reason is not None
        if is_escalate != has_reason:
            raise ValueError(
                f"Schema invariant violated: action={self.action.value} "
                f"escalation_reason={self.escalation_reason}"
            )
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"confidence out of range: {self.confidence}")


@dataclass
class EscalationDossier:
    """Routed at any 1.xE step."""
    processing_id: str
    item: FlagItem
    queue: EscalationQueue
    reason: EscalationReason
    classification: Optional[Classification] = None
    account_history: Optional[Dict[str, Any]] = None
    annotation: str = ""
    vip_rule_key: Optional[str] = None


@dataclass
class LogEntry:
    """Task 1.7 — structured JSON code block in Discourse moderation log topic.

    Schema per APD note on 1.7. Re-used by Agent 2 (Wave 2) for WS2 logs.
    """
    processing_id: str
    item_id: str
    account_type: str  # 'vip' | 'standard'
    violation_type: str
    confidence: float
    action: str
    sub_forum_id: str
    reporter_count: int
    agent_version: str
    timestamp: str  # ISO8601 UTC

    @classmethod
    def build(
        cls,
        item: FlagItem,
        classification: Optional[Classification],
        action_taken: Action,
        account_type: str,
        agent_version: str,
    ) -> "LogEntry":
        return cls(
            processing_id=item.processing_id,
            item_id=item.item_id,
            account_type=account_type,
            violation_type=(classification.violation_type.value
                            if classification else "n/a"),
            confidence=(classification.confidence if classification else 0.0),
            action=action_taken.value,
            sub_forum_id=item.sub_forum_id,
            reporter_count=item.reporter_count,
            agent_version=agent_version,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
