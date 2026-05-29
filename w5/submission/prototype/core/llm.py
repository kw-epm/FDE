"""The model boundary — shared by every agent (06 'Prompt templates' P1–P4).

Two interchangeable providers behind one interface. Each *agent* (triage,
coordinator, resolution, entitlement, escalation) calls the method it needs; the
provider is the shared model access (like a shared API key), and `.calls` counts
total model calls so the phone path can assert ZERO.

  • LiveProvider  — real Claude: Haiku classifies (P1); Sonnet decides the residual
                    tier (P2-decide), composes the KB-grounded reply (P2-compose),
                    writes the entitlement holding message (P3) and the Tier-3
                    human briefing (P4).
  • MockProvider  — deterministic stand-in so the prototype RUNS and tests pass
                    offline. Validates architecture + guardrails, not model accuracy.

The deterministic disposition layer (coordinator + core/guardrails) enforces the
Tier-1 safety envelope AFTER the model proposes: a proposed Tier 1 that fails the
allow-list / confidence / retrieval / guardrail checks is downgraded to a human gate.
"""
from __future__ import annotations
import json
import os
import re

import config
from models import Ticket, IssueType, Action, RouteTarget

# ── Prompt templates (the contract with 06) ───────────────────────────────────
P1_SYSTEM = """You triage CloudServe support tickets. Read the customer's message and return JSON only.
Do NOT resolve, advise, or decide routing — you only classify and surface signals.
Classify by the MESSAGE CONTENT, not the subject line (subjects are often wrong). Classify the
customer's ACTUAL request — not merely a topic they mention. A declined, hypothetical, or
informational mention is NOT a request (e.g. deciding to KEEP an item is not a RETURN_REQUEST;
"thinking about cancelling but won't" is not a SERVICE_CANCELLATION).

issue_type: one of [PASSWORD_RESET, BILLING_QUESTION, REFUND_REQUEST, HOW_TO_QUESTION,
  TECHNICAL_ISSUE, ACCOUNT_ACCESS, INVOICE_CLARIFICATION, SERVICE_CANCELLATION, COMPLAINT,
  OUTAGE_INQUIRY, DATA_EXPORT, SERVICE_DOWNGRADE, RETURN_REQUEST, SSO_SETUP]
Also return these independent signals (true/false), each based on the raw text:
  entitlement_signal: the customer is ACTIVELY asking for a refund, cancellation, downgrade, or return
    right now. If they mention one but decline it, change their mind, say they'll keep it / stay, or are
    just informing you ("I'll keep it", "never mind", "just letting you know"), set this FALSE.
  legal_signal: mentions lawyer, attorney, regulator, BBB, chargeback, "sue", legal action
  distress_signal: the customer is ANGRY/frustrated/abusive, contacting repeatedly ("third time",
    "again"), threatening to cancel or leave, or explicitly demanding a human/manager. A deadline or
    time pressure ALONE (e.g. "I have a meeting soon", "need this fast") is NOT distress. Be
    conservative — only true on clear emotional escalation, not mere urgency.
  multi_intent: TWO OR MORE genuinely DISTINCT requests (e.g. "reset my password AND cancel my plan").
    A single problem phrased as several questions ("I can't log in — can you help? is it my password?
    how do I proceed?") is ONE intent — set FALSE.
confidence: 0.0-1.0
candidate_issue_types: list if multi_intent or ambiguous

OUTPUT (JSON only):
{"issue_type": "...", "confidence": 0.0, "entitlement_signal": false, "legal_signal": false,
 "distress_signal": false, "multi_intent": false, "candidate_issue_types": []}"""

P2_DECIDE_SYSTEM = """You are the COORDINATOR's disposition decision for a CloudServe support agent.
Deterministic guardrails have ALREADY run and did NOT force a tier — you decide only the residual.
You DECIDE the tier; you do NOT write the customer reply (a specialist worker does that).

Inputs: the ticket, the classification, the customer record, and whether a KB article supports an answer.

Rules:
- TIER 1 (auto-resolve) is allowed ONLY if ALL hold: issue_type in
  {PASSWORD_RESET, BILLING_QUESTION, HOW_TO_QUESTION, INVOICE_CLARIFICATION, SSO_SETUP},
  classification confidence >= 0.75, and a KB article clearly answers it.
- If distress_signal or the message reads as a complaint -> TIER 3 (a human specialist).
- If you are not confident -> TIER 2 (a human). Never guess into TIER 1.

OUTPUT (JSON only): {"tier": 1|2|3, "rationale": "one sentence"}"""

P2_COMPOSE_SYSTEM = """You are the RESOLUTION worker for a CloudServe support agent. The coordinator has
ALREADY decided this ticket is Tier 1 and selected the CANONICAL KB article for the topic — treat it as
the right article. Write the customer reply, grounded in and QUOTING that article.

Keep it SHORT and direct: lead with the answer or steps; 2-4 sentences or a short numbered list; no
filler greetings or sign-offs beyond a brief courtesy. Quote the steps that apply. A terse or vague
request (e.g. "forgot my pass, help") STILL gets the standard answer from the article — do NOT refuse
over brevity. Return draft=null ONLY if the article is plainly about a DIFFERENT topic than the ticket
(a true mismatch), never because the request is short. Put the cited filename in kb_articles.

OUTPUT (JSON only): {"draft": "...", "kb_articles": ["..."]}"""

P3_SYSTEM = """A refund/cancellation/downgrade/return has been routed to a HUMAN approver. Write a short, warm
holding reply to the customer.

HARD RULES — you are drafting on behalf of a company under a compliance gate:
- DO NOT approve, promise, or imply the outcome. Never say "approved", "you'll get your refund",
  "I've refunded", "this is confirmed".
- State only that the request has been submitted and a human reviewer will confirm, typically within
  1 business day, by email.
- Be specific about what was submitted (type, amount if known) but neutral on the result.
- Keep it to 1-2 short sentences. No filler.

OUTPUT (JSON only): {"customer_message": "..."}"""

P4_BRIEF_SYSTEM = """You are the ESCALATION worker for a CloudServe support agent. This ticket is going to a
named human specialist (Tier 3). Write a TIGHT internal briefing — not a customer reply.

Terse and factual, no narration. At most 4 short lines covering: what the customer wants; key account
facts; why it was escalated (the guardrail flags); suggested next step. No promises to the customer.

OUTPUT (JSON only): {"briefing": "..."}"""


def _loads(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE).strip()
    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    return json.loads(m.group(0) if m else text)


def _kb_snippet(kb_text: str, max_lines: int = 6) -> str:
    lines = [ln.strip() for ln in kb_text.splitlines()]
    out = [ln for ln in lines if ln and not ln.startswith("#")]
    return "\n".join(out[:max_lines])


class _Provider:
    name = "base"

    def __init__(self):
        self.calls = 0


# ── Offline deterministic mock ─────────────────────────────────────────────────
class MockProvider(_Provider):
    """Deterministic keyword classifier + deterministic decisions. Intentionally
    fallible (keyword-based) so guardrail-INDEPENDENCE is actually exercised."""
    name = "offline-mock"

    def classify(self, ticket: Ticket) -> dict:
        self.calls += 1
        from util import kw_match
        b = (ticket.subject + " " + ticket.body).lower()

        def has(*words):
            return any(w in b for w in words)

        if has("refund", "money back"):
            it = IssueType.REFUND_REQUEST
        elif has("cancel my", "want to cancel", "close my account", "cancel my subscription", "cancelling"):
            it = IssueType.SERVICE_CANCELLATION
        elif has("downgrade", "move us to", "move us from", "fewer seats"):
            it = IssueType.SERVICE_DOWNGRADE
        elif has("return") and has("kit", "token", "device", "hardware"):
            it = IssueType.RETURN_REQUEST
        elif has("gdpr", "dsar", "data subject", "export my data", "export request", "delete my data"):
            it = IssueType.DATA_EXPORT
        elif has("saml", "scim", "sso", "azure ad", "okta", "binding mismatch", "single sign"):
            it = IssueType.SSO_SETUP
        elif has("authenticator", "backup code", "2fa", "locked out", "can't sign in", "cant sign in"):
            it = IssueType.ACCOUNT_ACCESS
        elif has("password", "reset link", "forgot my password", "log in", "sign in") or "locked" in b:
            it = IssueType.PASSWORD_RESET
        elif has("invoice", "line item", "itemis", "per seat", "per-seat"):
            it = IssueType.INVOICE_CLARIFICATION
        elif has("504", "/api", "webhook", "crash", "upload fails", "rate limit", "500 error"):
            it = IssueType.TECHNICAL_ISSUE
        elif has("status page", "is the api up", "outage", "/health", "is it down"):
            it = IssueType.OUTAGE_INQUIRY
        elif has("charge", "billed", "billing", "proration", "prorated", "next charge", "tax", "invoice"):
            it = IssueType.BILLING_QUESTION
        elif has("furious", "unacceptable", "disappointed", "complaint", "third time", "real human", "not a bot"):
            it = IssueType.COMPLAINT
        elif has("how do i", "where do i", "where is", "where can i", "how can i"):
            it = IssueType.HOW_TO_QUESTION
        else:
            it = IssueType.HOW_TO_QUESTION

        distress = has("furious", "unacceptable", "disappointed", "third time",
                       "real human", "not a bot", "angry", "ridiculous", "fed up")
        confident = it != IssueType.HOW_TO_QUESTION or has("how do i", "where", "how can i")
        return {
            "issue_type": it,
            "confidence": 0.9 if confident else 0.5,
            "entitlement_signal": kw_match(b, config.ENTITLEMENT_KEYWORDS),
            "legal_signal": kw_match(b, config.LEGAL_KEYWORDS),
            "distress_signal": distress,
            "multi_intent": False,
            "candidate_issue_types": [it.value],
        }

    def decide(self, ticket, classification, record, kb_top, retrieval_ok) -> dict:
        self.calls += 1
        it = classification["issue_type"]
        eligible = (it in config.READ_ONLY_ALLOWLIST
                    and classification["confidence"] >= config.TAU
                    and retrieval_ok
                    and bool(kb_top.get("name")))
        if eligible:
            return {"tier": 1, "rationale": (f"Read-only allow-list + confidence "
                    f"{classification['confidence']} + KB grounding ({kb_top['name']}).")}
        if classification["distress_signal"] or it == IssueType.COMPLAINT:
            return {"tier": 3, "rationale": "Distress / complaint signal -> human specialist."}
        return {"tier": 2, "rationale": (f"Tier-1 conditions not all met (issue={it.value}, "
                f"conf={classification['confidence']}, retrieval_ok={retrieval_ok}) -> human review.")}

    def compose_reply(self, ticket, classification, kb_top) -> dict:
        self.calls += 1
        issue_h = classification["issue_type"].value.lower().replace("_", " ")
        snippet = _kb_snippet(kb_top.get("text", ""))
        draft = (f"Thanks for reaching out about your {issue_h}. Based on our help "
                 f"article ({kb_top['name']}):\n\n{snippet}\n\n"
                 f"If that doesn't fully resolve it, just reply and we'll bring in a specialist.")
        return {"draft": draft, "kb_articles": [kb_top["name"]]}

    def holding_message(self, ent_type, fields, record) -> str:
        self.calls += 1
        return (f"Thanks for reaching out. I've prepared your {ent_type} request and routed it to a "
                f"human reviewer, who will confirm by email — typically within 1 business day. "
                f"I'm not able to decide the outcome myself.")

    def briefing(self, ticket, classification, record, flags) -> str:
        self.calls += 1
        return (f"[ESCALATION BRIEFING] Ticket {ticket.id} ({ticket.channel.value}). "
                f"Customer ({record.plan_tier if record else '?'} tier) wrote: "
                f"\"{ticket.body[:140]}\". Classified {classification['issue_type'].value}. "
                f"Escalated by guardrails: {flags or 'model judgment'}. "
                f"Suggested next step: a human specialist reviews and replies directly.")


# ── Live Anthropic provider (Haiku + Sonnet) ───────────────────────────────────
class LiveProvider(_Provider):
    name = "live (haiku/sonnet)"

    def __init__(self):
        super().__init__()
        import anthropic
        self._client = anthropic.Anthropic()

    def _json_call(self, model, system, user, max_tokens) -> dict:
        msg = self._client.messages.create(
            model=model, max_tokens=max_tokens, system=system,
            messages=[{"role": "user", "content": user}],
        )
        return _loads(msg.content[0].text)

    def classify(self, ticket: Ticket) -> dict:
        self.calls += 1
        user = f"Subject: {ticket.subject}\nMessage: {ticket.body}"
        for attempt in range(2):
            try:
                d = self._json_call(config.MODEL_CLASSIFY, P1_SYSTEM, user, 400)
                d["issue_type"] = IssueType(d["issue_type"])
                for k in ("entitlement_signal", "legal_signal", "distress_signal", "multi_intent"):
                    d.setdefault(k, False)
                d.setdefault("candidate_issue_types", [d["issue_type"].value])
                return d
            except Exception:
                if attempt == 1:
                    break
        return {"issue_type": IssueType.HOW_TO_QUESTION, "confidence": 0.0,
                "entitlement_signal": False, "legal_signal": False, "distress_signal": False,
                "multi_intent": False, "candidate_issue_types": [], "degraded": True}

    def decide(self, ticket, classification, record, kb_top, retrieval_ok) -> dict:
        self.calls += 1
        user = (f"TICKET: subject={ticket.subject!r} body={ticket.body!r}\n"
                f"CLASSIFICATION: {classification['issue_type'].value} conf={classification['confidence']}\n"
                f"CUSTOMER: plan_tier={getattr(record, 'plan_tier', None)} "
                f"churn_score={getattr(record, 'churn_score', None)}\n"
                f"KB_SUPPORTS_ANSWER: {retrieval_ok} (article={kb_top.get('name')})")
        for attempt in range(2):
            try:
                d = self._json_call(config.MODEL_REASON, P2_DECIDE_SYSTEM, user, 200)
                d["tier"] = int(d["tier"])
                d.setdefault("rationale", "")
                return d
            except Exception:
                if attempt == 1:
                    break
        return {"tier": 2, "rationale": "Decision call degraded -> human review."}

    def compose_reply(self, ticket, classification, kb_top) -> dict:
        self.calls += 1
        user = (f"Ticket: {ticket.body}\n\nKB article ({kb_top.get('name')}):\n{kb_top.get('text', '')[:4000]}")
        try:
            d = self._json_call(config.MODEL_REASON, P2_COMPOSE_SYSTEM, user, 350)
            d.setdefault("kb_articles", [kb_top["name"]] if kb_top.get("name") else [])
            return d
        except Exception:
            return {"draft": None, "kb_articles": []}

    def holding_message(self, ent_type, fields, record) -> str:
        self.calls += 1
        user = f"type={ent_type} fields={fields} plan_tier={getattr(record, 'plan_tier', None)}"
        try:
            return self._json_call(config.MODEL_REASON, P3_SYSTEM, user, 220)["customer_message"]
        except Exception:
            return (f"Thanks — I've submitted your {ent_type} request to a human reviewer, "
                    f"who will confirm by email, usually within 1 business day.")

    def briefing(self, ticket, classification, record, flags) -> str:
        self.calls += 1
        user = (f"Ticket {ticket.id} ({ticket.channel.value}). body={ticket.body!r}. "
                f"classification={classification['issue_type'].value}. "
                f"customer plan_tier={getattr(record, 'plan_tier', None)}. guardrail_flags={flags}.")
        try:
            return self._json_call(config.MODEL_REASON, P4_BRIEF_SYSTEM, user, 260)["briefing"]
        except Exception:
            return f"[ESCALATION] Ticket {ticket.id}: {classification['issue_type'].value}; flags={flags}."


def build_provider(force: str | None = None) -> _Provider:
    """force='live'|'mock' to pin; default auto-detects key + SDK."""
    if force == "mock":
        return MockProvider()
    has_key = bool(os.getenv("ANTHROPIC_API_KEY"))
    try:
        import anthropic  # noqa: F401
        has_sdk = True
    except Exception:
        has_sdk = False
    if force == "live" or (has_key and has_sdk):
        if not (has_key and has_sdk):
            raise RuntimeError("force='live' but ANTHROPIC_API_KEY and/or the anthropic SDK is missing.")
        return LiveProvider()
    return MockProvider()
