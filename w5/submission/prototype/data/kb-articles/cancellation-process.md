# Cancel your CloudServe account

Account cancellation is an entitlement-affecting action. The AI agent **cannot cancel an account on the customer's behalf** — a human approves all cancellations. The agent **can** confirm the customer's intent, lay out the consequences, and pre-fill the cancellation ticket.

## What cancellation means

- Effective at the end of the current billing period (no refund for the unused portion unless within the 7-day window — see [refund-policy](refund-policy.md)).
- Account data is retained read-only for 30 days, then permanently deleted.
- API keys, integrations, and team seats are revoked at the cancellation effective date.

## Steps

1. Customer requests cancellation (chat, email, or phone).
2. Agent confirms identity (account email + plan tier + last invoice amount).
3. Agent surfaces the [data-export](data-export.md) reminder so they can save anything they need.
4. Agent files the cancellation ticket with reason code (price, missing-feature, switching-vendor, no-longer-needed, other).
5. **Compliance reviews and confirms** within 1 business day.
6. Cancellation email sent on confirmation.

## Save attempts

For Business and Enterprise tiers, attempt one save offer (15% discount for 3 months, or moved to a lower tier) before completing cancellation. For Free / Starter tiers, do **not** attempt save offers — the friction is worse than the retained MRR.

## When to escalate

- Cancellation reason is "your service caused harm" or mentions legal / regulator language → escalate to compliance immediately.
- Customer is on Enterprise contract → route to Account Management (Victoria Lim).
