"""Coordinator — the orchestrator agent (ADR-6).

Owns the load-bearing disposition decision and the delegation. Per ticket it:
  1. checks idempotency; short-circuits phone (ZERO worker calls); fails loud on a
     missing customer record;
  2. asks the Triage worker to classify (Haiku);
  3. retrieves KB context;
  4. runs the deterministic guardrail GATE (ADR-1) — the binding safety layer it may
     never override upward;
  5. routes: a forced Tier-3 -> Escalation worker; an entitlement -> Entitlement
     worker; a forced Tier-2 -> human review; otherwise it makes the bounded residual
     tier DECISION (Sonnet) and, only if the Tier-1 envelope holds, delegates the
     reply to the Resolution worker;
  6. assembles the Disposition (with handled_by) and writes the audit line.

`handle(ticket, on_event=...)` accepts an optional callback that receives structured
step events as each agent runs — used by the streaming API to show live progress.
The callback defaults to a no-op, so tests / demo.py / eval.py are unaffected.
"""
import config
from core import guardrails
from core.agents.triage import TriageAgent
from core.agents.resolution import ResolutionAgent
from core.agents.entitlement import EntitlementAgent
from core.agents.escalation import EscalationAgent
from models import Disposition, Action, RouteTarget, Channel, GuardrailFlag

AGENTS = ["coordinator", "triage", "resolution", "entitlement", "escalation"]


def _retrieval(kb, issue_type, query):
    hits = kb.search(query, k=3)
    top_name, top_score = (hits[0] if hits else (None, 0.0))
    anchor = config.ISSUE_ANCHOR.get(issue_type)
    if anchor:
        # An allow-list issue type has a canonical KB article. Trust it as the grounding for a
        # confidently-classified topic — keyword search is brittle on synonyms ("credentials" vs
        # "password"), and the Tier-1 confidence gate (τ) + guardrails already guard misclassification.
        # Keyword retrieval is only the fallback for issues with NO anchor (e.g. HOW_TO_QUESTION).
        return {"name": anchor, "text": kb.text(anchor), "score": top_score}, True
    kb_top = {"name": top_name, "text": kb.text(top_name) if top_name else "", "score": top_score}
    return kb_top, top_score >= config.TAU_R


class Coordinator:
    role = "coordinator"

    def __init__(self, store, kb, provider, audit):
        self.store = store
        self.kb = kb
        self.provider = provider
        self.audit = audit
        self.triage = TriageAgent(provider)
        self.resolution = ResolutionAgent(provider)
        self.entitlement = EntitlementAgent(provider)
        self.escalation = EscalationAgent(provider)

    def _d(self, *, ticket, tier, issue_type, confidence, kb_articles, action, route_to,
           draft, flags, rationale, handled_by):
        return Disposition(
            ticket_id=ticket.id, tier=tier, issue_type=issue_type, confidence=confidence,
            kb_articles=kb_articles, action=action, route_to=route_to, draft=draft,
            guardrail_flags=flags, rationale=rationale,
            model_used=self.provider.name, handled_by=handled_by,
        )

    def handle(self, ticket, on_event=None) -> Disposition:
        def emit(agent, phase, label, model=None, detail=""):
            if on_event:
                on_event({"type": "step", "agent": agent, "phase": phase,
                          "model": model, "label": label, "detail": detail})

        emit("coordinator", "info", "Coordinator received ticket", detail=ticket.id)

        # 0. idempotency — a re-delivered ticket is a no-op (06 §0.8)
        if self.audit.already_processed(ticket.id):
            emit("coordinator", "info", "Duplicate delivery — no-op (idempotent)")
            return self._d(ticket=ticket, tier=3, issue_type=None, confidence=0.0, kb_articles=[],
                           action=Action.ESCALATE, route_to=RouteTarget.HUMAN_QUEUE, draft=None,
                           flags=["ALREADY_PROCESSED"], rationale="Duplicate delivery; no-op.",
                           handled_by="(idempotent no-op)")

        # 1. PHONE short-circuit — no worker invoked, ZERO LLM calls (ADR-4)
        if ticket.channel == Channel.PHONE:
            emit("coordinator", "info", "Phone channel → short-circuit (0 LLM calls, transcript never read)")
            d = self._d(ticket=ticket, tier=3, issue_type=None, confidence=0.0, kb_articles=[],
                        action=Action.DEFER_PHONE, route_to=RouteTarget.HUMAN_QUEUE, draft=None,
                        flags=[GuardrailFlag.PHONE_OUT_OF_SCOPE.value],
                        rationale="Phone deferred pending platform modernisation (CTO constraint).",
                        handled_by="(deferred — no agent)")
            self.audit.write(d)
            emit("coordinator", "done", "Done → deferred to human queue", detail="tier 3 · DEFER_PHONE")
            return d

        # 2. resolve customer — fail loud, never a default record
        record = self.store.get(ticket.customer_id)
        if record is None:
            emit("coordinator", "info", "Customer record not found → fail-loud to human")
            d = self._d(ticket=ticket, tier=3, issue_type=None, confidence=0.0, kb_articles=[],
                        action=Action.ESCALATE, route_to=RouteTarget.CSR_POOL, draft=None,
                        flags=[GuardrailFlag.CUSTOMER_RECORD_MISSING.value],
                        rationale="Customer record not found; routed to a human.",
                        handled_by="(fail-loud)")
            self.audit.write(d)
            emit("coordinator", "done", "Done → fail-loud to human", detail="tier 3 · ESCALATE")
            return d

        # 3. Triage worker (Haiku)
        emit("triage", "calling", "Triage — classifying issue + signals", model="haiku")
        c = self.triage.run(ticket)
        emit("triage", "done", "Triage", model="haiku",
             detail=f"{c['issue_type'].value} (conf {c['confidence']})")

        # 4. retrieve KB
        kb_top, retrieval_ok = _retrieval(self.kb, c["issue_type"], ticket.subject + " " + ticket.body)

        # 5. deterministic guardrail GATE (binding; downgrade-only)
        g = guardrails.apply(ticket, c, record)
        flags = g["flags"]
        emit("coordinator", "info", "Guardrail gate (deterministic)",
             detail=(", ".join(flags) if flags else "clear"))
        entitlement = None

        if g["action_override"] == Action.DECLINE_REDIRECT:
            emit("coordinator", "info", "Out-of-scope → decline & redirect")
            d = self._d(ticket=ticket, tier=2, issue_type=c["issue_type"].value, confidence=c["confidence"],
                        kb_articles=[], action=Action.DECLINE_REDIRECT,
                        route_to=g["route"] or RouteTarget.CSR_POOL, draft=None, flags=flags,
                        rationale=f"Out-of-scope ({flags}) -> declined and redirected.",
                        handled_by="coordinator")

        elif g["forced_tier"] >= 3:
            emit("escalation", "calling", "Escalation — briefing the human specialist", model="sonnet")
            briefing = self.escalation.run(ticket, c, record, flags)
            emit("escalation", "done", "Escalation", model="sonnet", detail="briefing written")
            d = self._d(ticket=ticket, tier=3, issue_type=c["issue_type"].value, confidence=c["confidence"],
                        kb_articles=[], action=Action.ESCALATE, route_to=g["route"] or RouteTarget.CSR_POOL,
                        draft=briefing, flags=flags,
                        rationale=f"Guardrail(s) {flags} forced escalation; escalation worker briefed the human.",
                        handled_by="escalation")

        elif g["is_entitlement"]:
            emit("entitlement", "calling", "Entitlement — pre-fill + holding message", model="sonnet")
            entitlement = self.entitlement.run(ticket, record, c, g["route"])
            emit("entitlement", "done", "Entitlement", model="sonnet",
                 detail=f"{entitlement.type} · {entitlement.eligibility_category} · approved=False")
            d = self._d(ticket=ticket, tier=2, issue_type=c["issue_type"].value, confidence=c["confidence"],
                        kb_articles=[], action=Action.PREFILL_AND_ROUTE, route_to=entitlement.route_to,
                        draft=entitlement.customer_message, flags=flags,
                        rationale=(f"Entitlement ({entitlement.type}/{entitlement.eligibility_category}) "
                                   f"pre-filled and routed to a human gate — agent never approves."),
                        handled_by="entitlement")

        elif g["forced_tier"] == 2:
            emit("coordinator", "info", "Forced to human review (no auto-resolve)", detail=", ".join(flags))
            d = self._d(ticket=ticket, tier=2, issue_type=c["issue_type"].value, confidence=c["confidence"],
                        kb_articles=[], action=Action.PREFILL_AND_ROUTE, route_to=g["route"] or RouteTarget.CSR_POOL,
                        draft=None, flags=flags,
                        rationale=f"Human review required (flags={flags}); not auto-resolved.",
                        handled_by="coordinator")

        else:
            # residual: the coordinator makes the bounded tier DECISION (Sonnet),
            # then ENFORCES the Tier-1 envelope before delegating to the Resolution worker.
            emit("coordinator", "calling", "Coordinator — deciding tier", model="sonnet")
            decision = self.provider.decide(ticket, c, record, kb_top, retrieval_ok)
            emit("coordinator", "done", "Coordinator", model="sonnet", detail=f"proposes Tier {decision['tier']}")
            tier1_allowed = (
                c["issue_type"] in config.READ_ONLY_ALLOWLIST
                and c["confidence"] >= config.TAU
                and retrieval_ok
                and not flags
                and bool(kb_top["name"])
            )
            if decision["tier"] == 1 and tier1_allowed:
                emit("resolution", "calling", "Resolution — composing KB-cited reply", model="sonnet")
                comp = self.resolution.run(ticket, c, kb_top)
                if comp.get("draft"):
                    emit("resolution", "done", "Resolution", model="sonnet", detail=f"cited {kb_top['name']}")
                    d = self._d(ticket=ticket, tier=1, issue_type=c["issue_type"].value,
                                confidence=c["confidence"], kb_articles=[kb_top["name"]],
                                action=Action.AUTO_RESOLVE, route_to=None, draft=comp["draft"], flags=flags,
                                rationale=decision.get("rationale") or "Auto-resolved from the read-only allow-list.",
                                handled_by="resolution")
                else:
                    emit("resolution", "done", "Resolution", model="sonnet", detail="no KB support → human review")
                    d = self._d(ticket=ticket, tier=2, issue_type=c["issue_type"].value,
                                confidence=c["confidence"], kb_articles=[], action=Action.PREFILL_AND_ROUTE,
                                route_to=RouteTarget.CSR_POOL, draft=None, flags=flags,
                                rationale="Resolution worker found no KB support -> human review.",
                                handled_by="resolution")
            elif decision["tier"] == 3:
                emit("escalation", "calling", "Escalation — briefing the human specialist", model="sonnet")
                briefing = self.escalation.run(ticket, c, record, flags)
                emit("escalation", "done", "Escalation", model="sonnet", detail="briefing written")
                d = self._d(ticket=ticket, tier=3, issue_type=c["issue_type"].value, confidence=c["confidence"],
                            kb_articles=[], action=Action.ESCALATE, route_to=RouteTarget.CSR_POOL,
                            draft=briefing, flags=flags,
                            rationale=decision.get("rationale") or "Coordinator judged complexity/distress -> escalate.",
                            handled_by="escalation")
            else:
                emit("coordinator", "info", "Tier-1 conditions not met → human review")
                d = self._d(ticket=ticket, tier=2, issue_type=c["issue_type"].value, confidence=c["confidence"],
                            kb_articles=[], action=Action.PREFILL_AND_ROUTE, route_to=RouteTarget.CSR_POOL,
                            draft=None, flags=flags,
                            rationale=decision.get("rationale") or "Tier-1 conditions not met -> human review.",
                            handled_by="coordinator")

        self.audit.write(d, entitlement)
        emit("coordinator", "done", f"Done → handled_by: {d.handled_by}",
             detail=f"tier {d.tier} · {d.action.value}")
        return d
