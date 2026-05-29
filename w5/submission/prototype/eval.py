"""Score the agent against data/ground-truth-labels.csv (09 §3 metrics).

V1 entitlement-gate precision (0 auto-resolved entitlements), V2 phone leakage (0),
V3 tier accuracy on the CERTAIN rows. Uses the offline mock by default; pass a live
provider to validate model accuracy with a key.
"""
import csv
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from adapters import parse_chat, parse_email, parse_phone
from core.stores import CustomerStore
from core.retrieve import KBIndex
from core.audit import AuditLog
from core.disposition import triage
from core.llm import build_provider
from models import Action

DATA = config.DATA_DIR
LABELS = os.path.join(DATA, "ground-truth-labels.csv")


def _load(tid, ch):
    if ch == "chat":
        return parse_chat(os.path.join(DATA, "tickets", f"{tid}.json"))
    if ch == "phone":
        return parse_phone(os.path.join(DATA, "phone-calls", f"{tid}.vtt"))
    g = glob.glob(os.path.join(DATA, "email-threads", f"{tid}-msg-01.eml"))
    return parse_email(g[0]) if g else None


def main():
    store = CustomerStore(os.path.join(DATA, "customers", "customer_master.csv"))
    kb = KBIndex(os.path.join(DATA, "kb-articles"))
    provider = build_provider()
    audit_path = "/tmp/resolveone_eval.jsonl"
    if os.path.exists(audit_path):
        os.remove(audit_path)
    audit = AuditLog(audit_path)

    rows = list(csv.DictReader(open(LABELS)))
    tier_hit = tier_total = unc_hit = unc_total = 0
    v1, v2, disagreements = [], [], []

    for r in rows:
        t = _load(r["ticket_id"], r["channel"])
        if t is None:
            continue
        d = triage(t, store, kb, provider, audit)
        if r["channel"] == "phone" and d.action != Action.DEFER_PHONE:
            v2.append(r["ticket_id"])
        if r["true_action"] == "PREFILL_AND_ROUTE" and d.action == Action.AUTO_RESOLVE:
            v1.append(r["ticket_id"])
        match = d.tier == int(r["true_tier"])
        if r["uncertain"].strip() == "Y":
            unc_total += 1
            unc_hit += match
        else:
            tier_total += 1
            tier_hit += match
            if not match:
                disagreements.append((r["ticket_id"], r["fixture_issue_type"],
                                      f"oracle T{r['true_tier']} -> agent T{d.tier} ({d.action.value})"))

    print(f"provider={provider.name}  N={len(rows)}  LLM calls={provider.calls}")
    print(f"V1 entitlement-gate precision (0 auto-resolved): {'PASS' if not v1 else 'FAIL ' + str(v1)}")
    print(f"V2 phone leakage (0): {'PASS' if not v2 else 'FAIL ' + str(v2)}")
    print(f"V3 tier accuracy on CERTAIN rows: {tier_hit}/{tier_total} "
          f"= {(tier_hit / tier_total if tier_total else 0):.0%}")
    print(f"   (uncertain rows reported separately: {unc_hit}/{unc_total})")
    if disagreements:
        print("\nDisagreements on certain rows (diagnostic):")
        for tid, it, delta in disagreements:
            print(f"  {tid} [{it}] {delta}")


if __name__ == "__main__":
    main()
