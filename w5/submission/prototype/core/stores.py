"""CustomerStore over customer_master.csv (07 INT-1).

A missing record is a FAIL-LOUD condition (06 §A.3 step 2), never a default
record — the agent must not invent a plan tier it will then reason about.
"""
import csv
from models import CustomerRecord


class CustomerStore:
    def __init__(self, csv_path: str):
        self._rows = {}
        with open(csv_path, newline="") as f:
            for r in csv.DictReader(f):
                self._rows[r["customer_id"]] = r

    def get(self, customer_id: str) -> CustomerRecord | None:
        r = self._rows.get(customer_id)
        if not r:
            return None  # caller fails loud — no default record (INT-1)
        return CustomerRecord(
            customer_id=r["customer_id"],
            plan_tier=r["plan_tier"],
            mrr_usd=int(r["mrr_usd"]),
            tenure_days=int(r["tenure_days"]),
            last_nps=int(r["last_nps"]),
            churn_score=int(r["churn_score"]),
            support_tier=r["support_tier"],
        )

    def __len__(self):
        return len(self._rows)

    def sample(self, include_ids=(), per_tier=2):
        """A small, tier-spread set of real customers for the demo dropdown:
        the given ids first, then up to `per_tier` more from each plan tier."""
        order = ["free", "starter", "pro", "business", "enterprise"]
        out, seen = [], set()

        def add(r):
            if r["customer_id"] in seen:
                return
            seen.add(r["customer_id"])
            out.append({"customer_id": r["customer_id"],
                        "name": f'{r["contact_first"]} {r["contact_last"]}',
                        "plan_tier": r["plan_tier"]})

        for cid in include_ids:
            r = self._rows.get(cid)
            if r:
                add(r)
        per = {t: 0 for t in order}
        for r in self._rows.values():
            t = r["plan_tier"]
            if t in per and per[t] < per_tier and r["customer_id"] not in seen:
                per[t] += 1
                add(r)
        out.sort(key=lambda c: (order.index(c["plan_tier"]) if c["plan_tier"] in order else 99, c["name"]))
        return out
