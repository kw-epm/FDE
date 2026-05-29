"""Deterministic guardrail layer (ADR-1, 06 §A.5) — the load-bearing safety component.

Runs on raw text + customer record, INDEPENDENTLY of the LLM's predicted issue_type
(SPIKE FINDING #2). It can only DOWNGRADE autonomy (raise the forced tier), never
upgrade. This is the answer to "isn't this just an LLM wrapper?": the binding
decisions about money, identity, and legal exposure are made here, in code.
"""
import config
from util import kw_match
from models import IssueType, RouteTarget, GuardrailFlag, Action


def apply(ticket, classification, record) -> dict:
    text = (ticket.subject + " " + ticket.body).lower()
    flags: list[str] = []
    forced_tier = 1
    route: RouteTarget | None = None
    ent_type = None
    action_override: Action | None = None

    it = classification["issue_type"]

    # entitlement (issue_type OR independent signal) -> human gate
    is_entitlement = it in config.ENTITLEMENT_TYPES or classification.get("entitlement_signal", False)
    if is_entitlement:
        flags.append(GuardrailFlag.ENTITLEMENT.value)
        forced_tier = max(forced_tier, 2)
        ent_type = config.ISSUE_TO_ENTITLEMENT.get(it, "refund")
        route = config.ROUTE[ent_type]

    # enterprise contract change -> Tier 3 / Account Mgmt (overrides the entitlement route)
    if record and record.plan_tier == "enterprise" and is_entitlement:
        flags.append(GuardrailFlag.ENTERPRISE_CONTRACT.value)
        forced_tier = max(forced_tier, 3)
        route = RouteTarget.ACCOUNT_MGMT_VICTORIA_LIM

    # legal / regulator -> Tier 3 / Uma (highest routing precedence)
    if classification.get("legal_signal") or kw_match(text, config.LEGAL_KEYWORDS):
        flags.append(GuardrailFlag.LEGAL.value)
        forced_tier = max(forced_tier, 3)
        route = RouteTarget.COMPLIANCE_UMA_BARDWAJ

    # identity / account-recovery -> human gate, independent of issue_type (SPIKE FINDING #2)
    if kw_match(text, config.IDENTITY_RECOVERY_KEYWORDS):
        flags.append(GuardrailFlag.IDENTITY_VERIFICATION.value)
        forced_tier = max(forced_tier, 2)
        route = route or RouteTarget.CSR_POOL

    # abuse / threats -> Tier 3
    if kw_match(text, config.ABUSE_LEXICON):
        flags.append(GuardrailFlag.ABUSIVE.value)
        forced_tier = max(forced_tier, 3)
        route = route or RouteTarget.CSR_POOL

    # complaint / distress -> Tier 3 (record the flag so the escalation is explained)
    if it == IssueType.COMPLAINT or classification.get("distress_signal"):
        flags.append(GuardrailFlag.DISTRESS.value)
        forced_tier = max(forced_tier, 3)
        route = route or RouteTarget.CSR_POOL

    # out-of-scope -> decline + redirect
    if kw_match(text, config.OUT_OF_SCOPE_KEYWORDS):
        flags.append(GuardrailFlag.OUT_OF_SCOPE.value)
        forced_tier = max(forced_tier, 2)
        action_override = Action.DECLINE_REDIRECT
        route = route or RouteTarget.CSR_POOL

    # multi-intent -> human
    if classification.get("multi_intent"):
        flags.append(GuardrailFlag.MULTI_INTENT.value)
        forced_tier = max(forced_tier, 2)

    # low classification confidence -> human (never auto-resolve on a shaky read)
    if classification.get("confidence", 1.0) < config.TAU_FLOOR:
        flags.append(GuardrailFlag.LOW_CONFIDENCE.value)
        forced_tier = max(forced_tier, 2)

    return {
        "forced_tier": forced_tier,
        "flags": flags,
        "route": route,
        "entitlement_type": ent_type,
        "is_entitlement": is_entitlement,
        "action_override": action_override,
    }
