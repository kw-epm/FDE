# Deliverable #5: The Handoff. ACVA v1.0 Spec Review

**Reviewer:** Krzysztof Wilniewczyc, FDE
**Date:** 2026-05-21
**Partner spec:** Automated Compliance Verification Agent v1.0 (Compliance Infrastructure Team, 2026-04-08)

---

## Part 1: Triage

**OVERALL ASSESSMENT**

The architecture is sound. The intent is right. One factual error in the spec blocks the build. Three smaller items can be fixed in parallel without holding up the start.

**BLOCKERS (must resolve before work begins)**

1. **§3.3 misuses 'SUSPENDED'.** The spec puts any licence expired over 90 days into 'Status = SUSPENDED'. But 'suspended' is a board-imposed licence status, not a synonym for 'lapsed a long time ago'. A nurse who forgot to renew gets the same operational label as one with a sanction on her record. The hospital reads the dashboard and makes the wrong call on a real person.
   *Fix:* rename to 'EXPIRED_OVER_90_DAYS'. Keep 'SUSPENDED' only for what §3.2 step 5 finds in the disciplinary record.

**CONCERNS (should be resolved; not build stops)**

1. **§8 vs §7. Impossible metric.** §8 asks for 0% false positives on VERIFIED for expired or suspended licences. But §7 already says there is a 24 to 48 hour lag at the source. The agent can hit a false positive from upstream lag alone. Pair the target with a source-freshness rule and lag-aware tolerance, or define when a result must be labelled "freshness risk" instead of VERIFIED.
2. **§3.1 secondary source = public portals.** This implies scraping. Partner legal should name which states are scrape-acceptable. Restrict the secondary path to that list.
3. **§6 throughput is 'TBD'.** Volume drives both the architecture and the state-board rate-limit conversation. We need pilot and full-rollout volumes before we size the build.

**ACCEPTABLE DIFFERENCES (no change needed)**

- §4 uses discrete confidence buckets (1.0 / 0.9 / 0.8 / 0.7). I would have gone continuous. The discrete bands are easier for the manual-review queue to act on. Fine.
- §6 sets 99.5% uptime, business hours only. Generous, but credential verification is not a real-time path. Fine.

**MISSING CONSIDERATIONS**

- **PII handling.** §5.2 stores worker name, licence number and DOB in the Compliance Database. No retention rule, no encryption rule, no access rule. The §10 Security and Privacy sign-off slot exists but the chapter is empty.
- **Audit trail schema.** Every result feeds a hiring decision. We need a log that cannot be changed: who asked, when, which source was queried, which algorithm version ran.
- **Worker dispute path.** If the agent returns 'EXPIRED' from bad upstream data, the worker has no way to correct it.

---

## Part 2: Escalation email

```
TO: Compliance Infrastructure Team Lead
FROM: Krzysztof Wilniewczyc, FDE
RE: ACVA v1.0 Spec Review
```

Thanks for the clean handoff. The architecture reads well. §3.3's line that 'the agent shall not make work-eligibility determinations' is the single sentence that keeps this a tool rather than a liability magnet. The in-scope and out-of-scope split is clear, which we appreciated.

**One thing my team needs fixed before we start.** §3.3 puts any licence past 90-day expiry into 'SUSPENDED'. That is a board-imposed licence status, not an age bucket. So a nurse who simply forgot to renew on time ends up flagged the same way as one with a sanction. The hospital reads the dashboard, declines the hire, and we have done real harm to a real person. The fix is fast: rename the bucket to 'EXPIRED_OVER_90_DAYS'. Keep 'SUSPENDED' only for actual board findings.

**Three concerns I would like resolved in parallel.** Not build stops, but they should not slip past the pilot.

1. The §8 0% false-positive target does not work with the 24 to 48 hour state-board lag that your own §7 names. Please pair it with a source-freshness rule or lag-aware tolerance.
2. §3.1's secondary path implies scraping public portals. Your legal team should clear which states are acceptable before we wire it in.
3. §6 throughput is still TBD. We need a pilot volume to plan the build against.

The full triage sits above this email if you would like the rest. Happy to take a 30-minute call this week to walk through the rename and the freshness-window proposal. Once those land I can give you a build start date.

Kind regards,
Krzysztof

-- 
Krzysztof Wilniewczyc
FDE Programme | EPAM Systems (Switzerland) GmbH
Boulevard Lilienthal 2, 8152 Opfikon, Switzerland
