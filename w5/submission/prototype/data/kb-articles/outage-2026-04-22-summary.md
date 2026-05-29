# Postmortem — 2026-04-22 us-east-1 partial outage

**Incident ID:** INC-2026-04-22-001
**Window:** 2026-04-22 14:32 UTC → 17:48 UTC (3h 16min)
**Impact:** ~22% of us-east-1 customers experienced API timeouts and dashboard 5xx errors.

## Root cause

A configuration push to the load balancer fleet introduced a malformed health-check rule. Traffic to one of three availability zones was drained.

## Customer-visible signals

- API: `HTTP 504 Gateway Timeout` from `/api/v2/*`.
- Dashboard: 5xx errors on most pages.
- Status page acknowledged at 14:48 UTC, resolved 17:48 UTC.

## Service-credit eligibility

Customers on Pro / Business / Enterprise plans whose API error rate was > 5% during the window may apply for service credits. **Compliance approves credits, not the AI agent.**

If a customer references this incident, the agent should:

- Confirm the incident occurred.
- Provide the incident ID for their records.
- File a service-credit request and route to compliance.
- Not commit to a specific credit amount.
