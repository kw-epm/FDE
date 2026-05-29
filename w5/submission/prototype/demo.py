"""ResolveOne capstone demo — runs the required paths in sequence (target < 5 min).

  HAPPY         CS-2026-0000002  password reset  -> Tier 1 auto-resolve, KB-cited
  FAILURE-MODE  CS-2026-0000011  refund request  -> Tier 2 human gate, never approved
  EDGE (phone)  CS-2026-0000010  phone call       -> defer, ZERO LLM calls
  EDGE (legal)  CS-2026-0000306  return + AG      -> Tier 3, legal override (bonus)

Runs LIVE (Haiku/Sonnet) when ANTHROPIC_API_KEY + the anthropic SDK are present,
otherwise the offline deterministic mock (architecture validated, not model accuracy).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from adapters import parse_chat, parse_phone
from core.stores import CustomerStore
from core.retrieve import KBIndex
from core.audit import AuditLog
from core.disposition import triage
from core.llm import build_provider

DATA = config.DATA_DIR

# Folded-in architecture diagram (ADR-6) — full version in ../agent-architecture.md
TOPOLOGY = r"""
                              Inbound ticket (chat / email / phone)
                                            |
        +-----------------------------------v-----------------------------------+
        |  COORDINATOR (orchestrator)        consults ->  GUARDRAIL GATE         |
        |   - Triage worker (Haiku) classifies            (deterministic,        |
        |   - decides the residual tier (Sonnet)           downgrade-only, ADR-1)|
        +----+---------------+----------------+----------------+-----------------+
             | read-only     | entitlement    | legal/abuse/   | phone /
             v               v                v  enterprise    v  no record
       RESOLUTION       ENTITLEMENT       ESCALATION       defer (0 LLM) /
       (Sonnet)         (Sonnet)          (Sonnet)         fail-loud
       Tier 1           Tier 2            Tier 3           Tier 3
       KB-cited reply   never approves    human briefing   human queue
             |               |                |                |
             +---------------+--------+-------+----------------+
                                      v
                       Disposition + immutable audit line (handled_by)

   Hub-and-spoke: the Coordinator is the only caller; workers never call each other.
"""


def _trace(d) -> str:
    hb = d.handled_by or ""
    if hb == "resolution":
        return "Coordinator -> Triage(Haiku) -> gate: clear -> decide: Tier 1 -> RESOLUTION(Sonnet)"
    if hb == "entitlement":
        return "Coordinator -> Triage(Haiku) -> gate: ENTITLEMENT -> ENTITLEMENT(Sonnet) -> human gate"
    if hb == "escalation":
        return "Coordinator -> Triage(Haiku) -> gate: escalate -> ESCALATION(Sonnet) -> human briefing"
    if "deferred" in hb:
        return "Coordinator -> phone short-circuit (no worker invoked, 0 LLM calls)"
    if "fail-loud" in hb:
        return "Coordinator -> customer lookup failed -> human (fail-loud)"
    return "Coordinator -> Triage(Haiku) -> gate -> human review (no worker compose)"


def _load(tid):
    chat = os.path.join(DATA, "tickets", f"{tid}.json")
    if os.path.exists(chat):
        return parse_chat(chat)
    return parse_phone(os.path.join(DATA, "phone-calls", f"{tid}.vtt"))


def _show(label, d):
    print(f"\n=== {label} :: {d.ticket_id} ===")
    print(f"  handled_by={d.handled_by}")
    print(f"  path: {_trace(d)}")
    print(f"  tier={d.tier}  action={d.action.value}  route={d.route_to.value if d.route_to else '-'}")
    print(f"  issue={d.issue_type}  conf={d.confidence}  kb={d.kb_articles}  flags={d.guardrail_flags}")
    print(f"  rationale: {d.rationale}")
    if d.draft:
        print("  --- customer-facing draft ---")
        for line in d.draft.splitlines():
            print(f"  | {line}")


def main():
    audit_path = os.path.join(DATA, "..", "audit_demo.jsonl")
    if os.path.exists(audit_path):
        os.remove(audit_path)

    store = CustomerStore(os.path.join(DATA, "customers", "customer_master.csv"))
    kb = KBIndex(os.path.join(DATA, "kb-articles"))
    provider = build_provider()  # live if key+SDK, else offline mock
    audit = AuditLog(audit_path)

    print("CloudServe ResolveOne — capstone prototype demo")
    print(f"provider: {provider.name}   customers: {len(store)}   kb_articles: 20")
    print(TOPOLOGY)
    print("Watch `handled_by` + `path` on each ticket below trace a branch of the diagram above.")

    paths = [
        ("HAPPY (read-only auto-resolve)", "CS-2026-0000002"),
        ("FAILURE-MODE (refund -> human gate)", "CS-2026-0000011"),
        ("EDGE (phone -> defer, zero LLM calls)", "CS-2026-0000010"),
        ("EDGE (legal override -> Tier 3 / Uma)", "CS-2026-0000306"),
    ]
    calls_before_phone = None
    for label, tid in paths:
        if "phone" in label:
            calls_before_phone = provider.calls
        d = triage(_load(tid), store, kb, provider, audit)
        _show(label, d)
        if "phone" in label:
            ok = provider.calls == calls_before_phone
            print(f"  [check] LLM calls before={calls_before_phone} after={provider.calls} "
                  f"(phone must add 0): {'PASS' if ok else 'FAIL'}")

    print(f"\naudit log -> {os.path.abspath(audit_path)} (one immutable JSON line per ticket)")


if __name__ == "__main__":
    main()
