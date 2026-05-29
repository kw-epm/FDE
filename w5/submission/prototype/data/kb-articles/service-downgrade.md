# Downgrade your CloudServe plan

You can move from a higher-tier plan to a lower one. Downgrades take effect at the **next** billing cycle — they are not retroactive.

## Steps (self-service when possible)

1. **Profile → Billing → Change plan** lets the customer downgrade Free / Starter / Pro on their own.
2. Business and Enterprise tiers must downgrade via support — the agent files the ticket and **compliance approves** because contracts and SLAs change.

## Feature impact

The agent should warn about feature loss before the downgrade is filed:

- Pro → Starter: API rate limits drop 10x, no SLA, max 5 seats.
- Business → Pro: Loses dedicated subdomain, audit log, SSO/SAML.
- Enterprise → Business: Loses HIPAA-eligible mode, custom DPA, named CSM.

## What the AI does

- Confirms the downgrade choice.
- Lists the features that will be lost.
- Checks for active integrations that depend on dropped features.
- **Pre-fills the downgrade ticket and routes to human approval.**
- Does not execute the downgrade itself.
