"""Data contracts — mirrors 06-capability-specs.md §0.1, §0.4, §0.7.

Enums are exhaustive and SCREAMING_SNAKE_CASE; there is no OTHER bucket. An
unmappable enum value is a validation error, not a silent default.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class Channel(str, Enum):
    CHAT = "CHAT"
    EMAIL = "EMAIL"
    PHONE = "PHONE"


class IssueType(str, Enum):
    PASSWORD_RESET = "PASSWORD_RESET"
    BILLING_QUESTION = "BILLING_QUESTION"
    REFUND_REQUEST = "REFUND_REQUEST"
    HOW_TO_QUESTION = "HOW_TO_QUESTION"
    TECHNICAL_ISSUE = "TECHNICAL_ISSUE"
    ACCOUNT_ACCESS = "ACCOUNT_ACCESS"
    INVOICE_CLARIFICATION = "INVOICE_CLARIFICATION"
    SERVICE_CANCELLATION = "SERVICE_CANCELLATION"
    COMPLAINT = "COMPLAINT"
    OUTAGE_INQUIRY = "OUTAGE_INQUIRY"
    DATA_EXPORT = "DATA_EXPORT"
    SERVICE_DOWNGRADE = "SERVICE_DOWNGRADE"
    RETURN_REQUEST = "RETURN_REQUEST"
    SSO_SETUP = "SSO_SETUP"


class Action(str, Enum):
    AUTO_RESOLVE = "AUTO_RESOLVE"
    PREFILL_AND_ROUTE = "PREFILL_AND_ROUTE"
    ESCALATE = "ESCALATE"
    DEFER_PHONE = "DEFER_PHONE"
    DECLINE_REDIRECT = "DECLINE_REDIRECT"


class RouteTarget(str, Enum):
    BILLING_RAVI_CHEN = "BILLING_RAVI_CHEN"
    COMPLIANCE = "COMPLIANCE"
    ACCOUNT_MGMT_VICTORIA_LIM = "ACCOUNT_MGMT_VICTORIA_LIM"
    COMPLIANCE_UMA_BARDWAJ = "COMPLIANCE_UMA_BARDWAJ"
    CSR_POOL = "CSR_POOL"
    HUMAN_QUEUE = "HUMAN_QUEUE"


class GuardrailFlag(str, Enum):
    ENTITLEMENT = "ENTITLEMENT"
    ENTERPRISE_CONTRACT = "ENTERPRISE_CONTRACT"
    LEGAL = "LEGAL"
    ABUSIVE = "ABUSIVE"
    IDENTITY_VERIFICATION = "IDENTITY_VERIFICATION"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"
    PHONE_OUT_OF_SCOPE = "PHONE_OUT_OF_SCOPE"
    CUSTOMER_RECORD_MISSING = "CUSTOMER_RECORD_MISSING"
    KB_UNAVAILABLE = "KB_UNAVAILABLE"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    MULTI_INTENT = "MULTI_INTENT"
    DISTRESS = "DISTRESS"


class EntitlementType(str, Enum):
    REFUND = "REFUND"
    CANCELLATION = "CANCELLATION"
    DOWNGRADE = "DOWNGRADE"
    RETURN = "RETURN"


class EligibilityCategory(str, Enum):
    WITHIN_7_DAYS = "WITHIN_7_DAYS"
    POST_CANCELLATION_CHARGE = "POST_CANCELLATION_CHARGE"
    OUTAGE_CREDIT_PRORATA = "OUTAGE_CREDIT_PRORATA"
    MID_CYCLE_DOWNGRADE_INELIGIBLE = "MID_CYCLE_DOWNGRADE_INELIGIBLE"
    FORGOT_TO_CANCEL_DISCRETIONARY = "FORGOT_TO_CANCEL_DISCRETIONARY"
    NEEDS_HUMAN_LOOKUP = "NEEDS_HUMAN_LOOKUP"
    INELIGIBLE = "INELIGIBLE"


@dataclass
class Ticket:
    id: str
    channel: Channel
    subject: str
    body: str
    customer_id: str
    created_at: str | None = None
    sla_target_minutes: int | None = None
    pack_issue_type: str | None = None  # fixture hint; audit only, NEVER ground truth (ADR-5)
    raw: dict = field(default_factory=dict)


@dataclass
class CustomerRecord:
    customer_id: str
    plan_tier: str
    mrr_usd: int
    tenure_days: int
    last_nps: int
    churn_score: int
    support_tier: str


@dataclass
class Disposition:
    ticket_id: str
    tier: int
    issue_type: str | None
    confidence: float
    kb_articles: list[str]
    action: Action
    route_to: RouteTarget | None
    draft: str | None
    guardrail_flags: list[str]
    rationale: str
    model_used: str | None = None
    handled_by: str | None = None   # which agent produced the output (multi-agent trace)

    def __post_init__(self):
        # invariant: an AUTO_RESOLVE must cite at least one KB article (§0.7)
        if self.action == Action.AUTO_RESOLVE and not self.kb_articles:
            raise ValueError(
                f"{self.ticket_id}: AUTO_RESOLVE with empty kb_articles violates the "
                "Tier-1 grounding invariant (06 §0.7)."
            )


@dataclass
class EntitlementRequest:
    ticket_id: str
    customer_id: str
    type: str                  # EntitlementType value, lowercased for the human queue
    eligibility_category: str
    pre_filled_fields: dict
    route_to: RouteTarget
    customer_message: str
    approved: bool = False               # ALWAYS False on creation — only a human flips this
    requires_human_approval: bool = True  # ALWAYS True
