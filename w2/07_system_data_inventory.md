# System and Data Inventory
**Scenario 4 — Community Content Moderation (MiniBase)**
**Date:** 2026-04-30
**Source:** APD (`04_agent_purpose_document.md`), brief tooling sketch (`scenario4.md`)

> Inventory for the **WS1 Routine Moderation Agent** (Wave 1) and the **WS2/WS3 Context Assembly Agent** (Wave 2). System boundaries match the agent design in `04_agent_purpose_document.md` — if a row here changes, update there.

---

## Wave 1 — Routine Moderation Agent

### Required systems

| System | Data needed | Access | Availability | Gap / Risk |
|---|---|---|---|---|
| **Discourse** (self-hosted, AWS) | Flag queue, post content, account history, write actions (remove / hide / recover / PM / flag-disagree) | Read + Write (REST) | API exists `[Stated: tooling sketch]` | Write auth scope unconfirmed — **P0** |
| **VIP controlled-list service** | account_ids (integer Discourse IDs) + escalation routing rules | Live read (per case) | **Does not exist** `[Stated: artefact 4.3]` | **P0 launch blocker.** Must be built; populated from Tom's Sheet; live query, not static config |
| **Global moderation policy RAG** | 14-page policy chunked + indexed | Read (vector search) | Document exists `[Stated: brief]` | Needs chunking pipeline; policy updates trigger re-index |
| **Sub-forum norm data** | 3 of 14 norms (painters, historical, painters-japan) `[Stated: artefact 4.3]` | Read | Partially documented | Wave 2 blocker only; Wave 1 falls back to global policy with sub-forum routing signal |
| **Discourse moderation log topic** | Per-case structured log entries (idempotency source of truth) | Write + search by title | Does not exist | **P0 setup task.** Create the topic during Wave 1 setup. Title format: `[mod-log] {processing_id}`. |
| **Discourse `#mod-review-queue` category** | Volunteer-moderator escalations (low confidence, multi-label, [0.6, 0.8] re-eval failed) | Write | Does not exist | **P0 setup task.** Standard Discourse category, low effort. |
| **Discourse `#mod-vip-escalation` category** | Tom-tier escalations (VIP match, policy RAG miss) | Write | Does not exist | **P0 setup task.** Standard Discourse category. |
| **Discord webhook to Tom** | VIP escalation real-time alerts; HITL rate calibration alerts | Write | Discord exists `[Stated: tooling sketch]`; webhook config required | **P0** — without this configured, VIP escalations have no destination; the existential risk path fails silently |
| **Discord `#ops` channel** | API failure alerts; VIP service outage alerts | Write | Discord exists | P1 — configure during Wave 1 setup |
| **Dead-letter store** | API failure cases pending retry | Read + Write | Local SQLite (to be built) | P1; ~50 LOC, single-instance |
| **Gallery (Rails, custom)** | Whether gallery flags hit Discourse queue or arrive separately | Read | Limited API surface `[Stated: tooling sketch]` | **P0 — promoted from gap to blocker.** If gallery posts arrive on a different intake path, task 1.1 needs a second code path. Resolve before build. |

### Out-of-scope systems

| System | Status |
|---|---|
| Google Sheets (Tom's tracker) | Migration source only; not a runtime dependency. Migrate to VIP service before launch. |
| Discord moderator deliberation channels | None (out of WS1 scope). Not API-accessible. Future work; Wave 1 does not observe deliberation layer. |
| Email | None (out of scope). WS4 only. |
| Stripe | None. Not in moderation flow. |

---

## Wave 2 — Context Assembly Agent (additional systems)

| System | Reuse / new | Notes |
|---|---|---|
| Discourse REST API (read + write) | Reuse from Wave 1 | Same client library |
| VIP controlled-list service | Reuse from Wave 1 | Same live-query path |
| Policy RAG pipeline | Reuse + extend | Add structured sub-forum norms (all 14) once Tom + Senior Moderator complete documentation |
| Structured log schema | Reuse + extend | Wave 2 logs WS2 decisions; schema is a superset of Wave 1's, adding `norm_applied`, `decision_rationale`, `human_moderator_id` fields |
| Sub-forum norm data store | **New (Wave 2 only)** | All 14 sub-forums structured. Currently 3 of 14 documented. **P0 Wave 2 blocker.** |
| `#mod-review-queue` | Reuse | Wave 2 reads from this category to assemble dossiers |
| Decision log vector index | — (Wave 3) | Future cross-case precedent retrieval |

---

## Credentials

All API keys and secrets via environment variables. Never committed:

| Variable | Purpose |
|---|---|
| `DISCOURSE_API_KEY` | Discourse REST authentication |
| `DISCOURSE_API_USERNAME` | Discourse API user (must have moderation + admin scope for `recover`) |
| `VIP_SERVICE_TOKEN` | VIP controlled-list service auth |
| `DISCORD_WEBHOOK_URL_TOM` | Tom's VIP escalation channel |
| `DISCORD_WEBHOOK_URL_OPS` | Ops alerting channel |
| `AGENT_VERSION` | Set at deploy time (git SHA) — written into every 1.7 log entry |

---

## Shared Wave 1 → Wave 2 Assets

Built in Wave 1, reused in Wave 2:
- Discourse REST API client library
- VIP controlled-list lookup service
- Policy RAG pipeline (extended with sub-forum norms in Wave 2)
- Structured log schema (extended with WS2 fields in Wave 2)
- Volunteer mod review queue (`#mod-review-queue`)
- Mod-VIP-escalation category (`#mod-vip-escalation`)
- Discord webhook setup
- Dead-letter store
- Action mapping table
- Idempotency mechanism (search-by-title in moderation log topic)

This is the compounding-roadmap dependency: Wave 1 build cost is largely Wave 2's avoided integration cost.

---

## Pre-launch Checklist (P0 only)

- [ ] VIP controlled-list service built and seeded from Tom's Sheet
- [ ] Discourse write API credentials provisioned with confirmed scope
- [ ] Gallery posts intake path resolved (single Discourse queue or separate channel)
- [ ] Discourse moderation log topic created
- [ ] Discourse `#mod-review-queue` category created
- [ ] Discourse `#mod-vip-escalation` category created
- [ ] Discord webhook to Tom configured and tested
- [ ] `AGENT_VERSION` env var deploy mechanism wired
