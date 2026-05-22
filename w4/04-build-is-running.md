# Deliverable #4 — The Build Is Running: 9 Signal Classification

**Author:** Krzysztof Wilniewczyc
**Engagement:** Pinnacle Financial Services, Customer Inquiry Resolution Agent
**Date:** 2026-05-20

## Summary


| #   | Signal                                  | Classification                        |
| --- | --------------------------------------- | ------------------------------------- |
| 1   | 'Dispute in Progress' loop              | Builder Mistake                       |
| 2   | High-risk fraud response time (43 min)  | Spec Ambiguity                        |
| 3   | Identity verification surprise          | Builder Mistake (see Additional Info) |
| 4   | Fraud alert escalation to nowhere       | Spec Ambiguity                        |
| 5   | Confirmation email delayed              | Builder Mistake                       |
| 6   | Ambiguous 'all fraud alerts' definition | Spec Ambiguity                        |
| 7   | 30-second SLA vs batching               | Unjustified Builder Addition          |
| 8   | Audit trail in memory only              | Builder Mistake (see Additional Info) |
| 9   | v3 fixture stale in CI                  | Test/Environment Issue                |


---

## Signal 1: The 'Dispute in Progress' Loop

**Classification:** Builder Mistake

**Reasoning:** Spec says no second escalation if the dispute is already in 'ESCALATED_TO_HUMAN' or 'PENDING_SPECIALIST_REVIEW'. Logs show two escalations at 14:32:45 and 14:39:45 with no status check between them.

**Correct Response:** Builder adds a status check before any escalation. If the dispute is already escalated, the agent returns the existing status, timestamp, and expected response window. Regression test for the reopen case. Outcome: no duplicate escalations for the same dispute.

## Signal 2: High-Risk Fraud Response Time

**Classification:** Spec Ambiguity

**Reasoning:** Spec sets a 15-min SLA on human review but says nothing about what the agent does if the queue stalls. Agent tagged the alert as 'HIGH_RISK_FRAUD' and routed to the compliance queue, which fits the spec as written.

**Correct Response:** FDE updates the spec to add a stale-queue rule: if a HIGH_RISK_FRAUD alert sits more than 10 min unreviewed, the agent pages on-call compliance. Builder implements after the spec is firm. Queue staffing is an ops issue, raised separately to the engagement lead. Outcome: the 15-min SLA is actually enforceable.

## Signal 3: Identity Verification Surprise

**Classification:** Builder Mistake (see Additional Info)

**Reasoning:** Spec says verify identity via security questions before showing account data. Agent skipped verification entirely and treated channel ID (email, phone, chat) as identity. Customer flagged it as a security concern in production.

**Correct Response:** Builder hotfixes: block account data disclosure until the verification step runs and passes. Regression test for the not-verified case. FDE drafts the minimum verification standard in parallel (see Additional Info). Outcome: no account data leaves the system without verified identity.

## Signal 4: Fraud Alert Escalation to Nowhere

**Classification:** Spec Ambiguity

**Reasoning:** Spec says 'escalated to human review' but doesn't define what that means. Agent routed the alert to 'fraud_review_queue', which fits the literal spec. Same shape as Signal 2.

**Correct Response:** FDE updates the spec to define what escalation actually means: page on-call when the queue is empty, require 24/7 staffing, or set a hard timeout that auto-pages. Pick one. Builder implements after. Outcome: HIGH_RISK alerts reach a human within a known time bound, including off-hours.

## Signal 5: Billing Dispute Closed Too Fast

**Classification:** Builder Mistake

**Reasoning:** Spec says the confirmation email goes out immediately after the credit is applied. Email went out 43 hours later (April 10 14:25 credit, April 12 09:03 email).

**Correct Response:** Builder finds the root cause first (async path, retry policy, or batching), not just patches the symptom. Fix so the email goes out in the same transaction as 'apply_credit'. Regression test: email dispatched within 30 seconds of credit. Could be linked to the batching in Signal 7, worth checking. Outcome: customers get the confirmation the spec promises.

## Signal 6: Ambiguous 'Fraud Alert' Definition

**Classification:** Spec Ambiguity

**Reasoning:** Spec says 'route all fraud alerts to human review'. Doesn't say if 'all' means LOW + MEDIUM + HIGH, only HIGH, or HIGH + MEDIUM. Engineer and FDE already disagree per the scenario.

**Correct Response:** FDE updates the spec. My call: HIGH + MEDIUM routed to humans, LOW logged only. Assumption: LOW is noise; validate by sampling 30 days of LOW alerts and reconsider if false negatives go above 1%. Builder updates the routing after the spec is firm. Outcome: routing rule is explicit and defensible.

## Signal 7: 30-Second SLA vs Batching

**Classification:** Unjustified Builder Addition

**Reasoning:** Spec sets a 30-sec response SLA. Builder added 5-min batching to save API cost, which the spec didn't ask for. The SLA breach is the symptom; the unrequested addition is the cause.

**Correct Response:** FDE and engineer discuss it together. Builder explains why batching was added and brings real API cost numbers. Three options: remove batching, allow it only on non-SLA flows, or add a fast lane for SLA-bound responses. Decision goes back into the spec. Also check whether batching is causing the Signal 5 email delay. Outcome: either the 30-sec SLA is restored, or the spec is renegotiated with cost numbers on the table.

## Signal 8: Audit Trail Missing in Action

**Classification:** Builder Mistake (see Additional Info)

**Reasoning:** 'Audit trail for compliance review' in financial services means a persistent, retrievable record. An 8-hour in-memory buffer that wipes on restart doesn't fit. Compliance can't pull records weeks later, which is the core purpose of an audit trail.

**Correct Response:** Builder hotfixes: replace the in-memory buffer with a persistent store keyed by 'inquiry_id' and queryable by compliance. FDE drafts the spec follow-up in parallel (see Additional Info). Outcome: compliance can pull audit trails weeks or years later as the regulatory regime requires.

## Signal 9: Billing API Response Format Test Fails

**Classification:** Test/Environment Issue

**Reasoning:** Spec is v4, agent returns v4, production billing API expects v4. Only the mock fixture in the integration test is still v3. Missed in the v3 to v4 migration.

**Correct Response:** Test owner updates the mock fixture to v4. Audit the migration PR for other v3 references that were missed (other tests, docs, sample requests). No blame on the builder. Add a checklist item for future API contract migrations: grep all fixtures, update or delete, verify CI passes before closing the migration ticket. Outcome: CI green, no other v3 leftovers hiding.

---

## Additional Information

**Signal 3.**

First read was spec ambiguity, because the spec doesn't list which security questions count as enough. But the agent did no verification at all, which is a builder mistake, not an ambiguity. The 'which questions' gap is still real and needs a spec follow-up: FDE drafts the minimum verification standard (for example, ask 2 security questions from a defined list, like date of birth or last 4 digits of the account number) so the builder doesn't end up inventing security policy.

**Signal 8.**

I went with Builder Mistake but this one is very close to the Spec ambiguity. My reasoning:

Spec doesn't explicitly say 'persistent'. It doesn't give a retention period, doesn't name a storage medium. But, I used to work in financial services, so for me the 'audit trail for compliance review' is a clear, unambiguous domain term. From a business requirement perspective - it is about persistent retrievable records. It definitely IMPLIES implementation requirements (and possibly a lot of clarifications).

However, a Builder might genuinely not know that. Therefore, it is a good practice to clarify it and drill down in the spec: retention period (for example, 7 years for FS compliance), storage medium category (persistent store, append-only, immutable), query interface and the regulatory regime.