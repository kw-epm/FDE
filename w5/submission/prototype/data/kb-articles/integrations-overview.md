# Integrations

CloudServe integrates with Slack, Salesforce, Zapier, and supports outbound webhooks.

## Slack

`Settings → Integrations → Slack → Connect workspace`. The agent can confirm steps but cannot install on the customer's behalf — Slack requires the customer's admin token.

## Salesforce

OAuth flow from `Settings → Integrations → Salesforce`. Requires Salesforce admin role.

## Zapier

CloudServe is on the Zapier directory — search "CloudServe" in Zapier's app catalog.

## Webhooks

`Settings → Webhooks → Add endpoint`. Supports HMAC-SHA256 signing. The agent can explain the signing format but does not provision endpoints.
