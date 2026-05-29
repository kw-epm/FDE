"""Thresholds, allow-list, lexicons, routing — the deterministic config (ADR-1).

These constants are the binding safety policy. The LLM proposes; this layer
disposes. Lexicons match on WORD BOUNDARIES (util.kw_match), never substrings.
"""
import os
from models import IssueType, RouteTarget

# ── Paths ───────────────────────────────────────────────────────────────────
PROTO_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROTO_DIR, "data")

# ── Model routing (06 §0.6 — no Opus path) ───────────────────────────────────
# Pinned defaults; override via env without touching code.
MODEL_CLASSIFY = os.getenv("RESOLVEONE_MODEL_CLASSIFY", "claude-haiku-4-5")
MODEL_REASON = os.getenv("RESOLVEONE_MODEL_REASON", "claude-sonnet-4-6")

# ── Thresholds (06 §A.3) ──────────────────────────────────────────────────────
TAU = 0.75        # classification confidence floor for Tier 1
# SPIKE FINDING #1: retrieval_confidence = query-token coverage of the top KB article.
# 0.55 was uncalibrated and blocked 100% of Tier 1; recalibrated to 0.30 AND anchored to a
# canonical KB article per issue type (below). Calibrated on data/ground-truth-labels.csv.
TAU_R = 0.30      # retrieval confidence floor for Tier 1
TAU_FLOOR = 0.40  # classification confidence below this -> force Tier 2

# ── Read-only allow-list: the ONLY issue types eligible for Tier-1 auto-resolve ──
READ_ONLY_ALLOWLIST = {
    IssueType.PASSWORD_RESET,
    IssueType.BILLING_QUESTION,
    IssueType.HOW_TO_QUESTION,
    IssueType.INVOICE_CLARIFICATION,
    IssueType.SSO_SETUP,
}

# Anchor each allow-list issue type to its canonical KB article (a strong retrieval prior).
ISSUE_ANCHOR = {
    IssueType.PASSWORD_RESET: "password-reset.md",
    IssueType.BILLING_QUESTION: "billing-faq.md",
    IssueType.INVOICE_CLARIFICATION: "billing-faq.md",
    IssueType.SSO_SETUP: "sso-setup.md",
    IssueType.HOW_TO_QUESTION: None,  # varies; falls back to keyword score >= TAU_R
}

ENTITLEMENT_TYPES = {
    IssueType.REFUND_REQUEST,
    IssueType.SERVICE_CANCELLATION,
    IssueType.SERVICE_DOWNGRADE,
    IssueType.RETURN_REQUEST,
}

ISSUE_TO_ENTITLEMENT = {
    IssueType.REFUND_REQUEST: "refund",
    IssueType.SERVICE_CANCELLATION: "cancellation",
    IssueType.SERVICE_DOWNGRADE: "downgrade",
    IssueType.RETURN_REQUEST: "return",
}

# ── Deterministic lexicons (06 §A.5) — tuned on the validation set in production ──
ENTITLEMENT_KEYWORDS = [
    "refund", "money back", "cancel my", "cancel my account", "cancel my subscription",
    "charge back", "chargeback", "downgrade", "close my account", "want to cancel",
    "cancelling", "want a refund",
]
LEGAL_KEYWORDS = [
    "lawyer", "attorney", "attorney general", "regulator", "bbb", "better business bureau",
    "chargeback", "sue", "legal action", "litigation", "small claims",
]
# Real list maintained by Trust & Safety; placeholder keeps the lexicon testable offline.
ABUSE_LEXICON = ["[slur-placeholder]", "kill you", "i'll hurt", "i will hurt", "threat"]

# SPIKE FINDING #2: identity / account-recovery must be human-gated regardless of issue_type
# (a ticket mislabelled SSO_SETUP but really a 2FA recovery must NOT auto-resolve).
IDENTITY_RECOVERY_KEYWORDS = [
    "authenticator", "backup code", "backup codes", "2fa code", "2fa codes", "lost access",
    "can't sign in", "cant sign in", "locked out", "phone died", "lost my phone",
    "recovery code", "don't have the authenticator", "lost my 2fa",
]
OUT_OF_SCOPE_KEYWORDS = ["partnership", "press inquiry", "media request", "investment opportunity"]

ROUTE = {
    "refund": RouteTarget.BILLING_RAVI_CHEN,
    "cancellation": RouteTarget.COMPLIANCE,
    "downgrade": RouteTarget.COMPLIANCE,
    "return": RouteTarget.BILLING_RAVI_CHEN,
    "enterprise": RouteTarget.ACCOUNT_MGMT_VICTORIA_LIM,
    "legal": RouteTarget.COMPLIANCE_UMA_BARDWAJ,
    "complaint": RouteTarget.CSR_POOL,
    "phone": RouteTarget.HUMAN_QUEUE,
}

# B.4 guarantee: a holding message may never imply an outcome. Checked deterministically
# AFTER generation; a hit forces regeneration / a fixed safe template.
FORBIDDEN_OUTCOME_PHRASES = [
    "approved", "you'll get your refund", "you will get your refund", "i've refunded",
    "i have refunded", "your refund is approved", "refund has been approved",
    "this is confirmed", "you will be refunded", "has been processed", "i've cancelled",
]
