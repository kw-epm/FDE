# API rate limits

| Plan | Requests / minute | Burst |
|---|---:|---:|
| Free | 60 | 120 |
| Starter | 600 | 1,200 |
| Pro | 6,000 | 12,000 |
| Business | 30,000 | 60,000 |
| Enterprise | Negotiated | Negotiated |

## When you hit the limit

`HTTP 429 Too Many Requests`. The `Retry-After` header tells you how long to wait.

## Increasing limits

- Pro and below: upgrade plan.
- Business: upgrade to Enterprise for negotiated limits.
- Enterprise: contact your CSM.

The AI agent **cannot raise rate limits** — it pre-fills a request and routes it to Account Management.
