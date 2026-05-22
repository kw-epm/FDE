# System & Data Inventory
**Gate 2 — Apex Distribution Ltd**
**Source:** APD (`04`), brief tooling sketch, Aurum CSV catalogue (artefact 5), CSV samples

> Inventory for **Wave 1 BDRA** + **Wave 2 (C4C Aurum auto-write)** + **Wave 3 (DECA-light damage→billing watch)**. System boundaries match `04`.
>
> **Code legend:** `C4C` etc. = DSM task clusters; `4.10` etc. = APD activity-catalog tasks; `G-N` = open gaps (canonical: `CLAUDE.md` §Open gaps); `A-N` = cross-artefact evidence (canonical: `00_elicitation_log.md`).

## Wave 1 — BDRA

### Required systems

| System | Data needed | Access | Availability | Gap / Risk |
|---|---|---|---|---|
| **Salesforce CRM** | Dispute records, customer records, cases (cross-stream WS1 check), dispute-state writes, QA tags | Read + Write (REST, OAuth 2.0) | Modern SaaS; brief: "REST APIs available" | Confirm dispute object model (G-9b) — disputes may live as Cases, custom object, or in dedicated app |
| **Aurum CSV file-watch** | 7 daily/weekly/monthly files: BILL_DAILY, FUEL_SURCH, CREDITS, RECON, DISPUTES_OPEN, AGED_RECEIVABLES, CUSTOMER_MASTER | Read-only (file system / SFTP) | Brief: "Batch-file exports only … 02:00–04:00 GMT" | **P0:** access path (SFTP? shared mount? service account scope?). **P0:** schema validation contract per file. **P1:** quarterly Aurum schema-change risk (per `00` elicitation Q7) |
| **Aurum schema-validation contract store** | Per-file schema spec (column count, names, order, types, value ranges) | Read | Does not exist | **P0 build.** Generated from current CSV samples; versioned in repo |
| **AM email queue (Wave 1 only)** | Credit packet handoff for human Aurum UI entry (4.9E) | Write | Email exists | **P0:** AM coverage map config; routing rules for A-5 mismatch fallback |
| **Internal config store** | AM coverage map, remedy template library, authority thresholds, chase cadence, confidence thresholds | Read | YAML in repo | Versioned; deploy review on change |
| **Slack/email ops channel** | Schema validation failures, silent-failure alerts, calibration alerts | Write | Channel exists `[Inferred — standard ops practice; confidence Med]` | **P0:** Channel + webhook configured |

### Out-of-scope systems (Wave 1)

| System | Status | Reason |
|---|---|---|
| Aurum UI write | Wave 2 | Blocked on G-12 (service-account auth) |
| Aurum support ticket queue | Out of scope | 48hr SLA path is a fallback, not an agent integration |
| Driver App | Wave 3 | Blocked on G-10 (API surface); only needed for DECA-light |
| Dispatch console | Wave 3 | Blocked on G-11 (limited API surface unconfirmed) |
| Phone IVR | Out of scope | Not in BDRA's intake path; disputes arrive via CRM/email |
| Customer-facing UI | Out of scope | Sarah wary of customer-facing (Q1); BDRA is internal-facing |
| Stripe | Out of scope | Not in dispute resolution flow |

---

## Wave 2 — C4C Aurum auto-write

| System | Reuse / new | Notes |
|---|---|---|
| Salesforce CRM | Reuse | Same client |
| Aurum schema validator | Reuse + extend | Add validation for credits-write response (next-day APEX_CREDITS export AUDIT_REF lookup at 4.10) |
| **Aurum UI service-account client** | **New** | Blocked on G-12. Likely Selenium/Playwright pattern; needs Aurum login credentials with credit-write scope |
| AM email queue | Demoted | Used only as fallback if UI client fails |

---

## Wave 3 — DECA-light (damage→billing watch)

| System | Reuse / new | Notes |
|---|---|---|
| Salesforce CRM | Reuse | Write billing-watch records as CRM custom object or Case child |
| **Dispatch console / Driver App damage-flag read** | **New** | Blocked on G-11 (console) or G-10 (app). Either source works; pick whichever has better damage-flag fidelity |
| Aurum schema validator | Reuse | Same contract |
| Internal config store | Reuse + extend | Add damage-flag → billing-watch routing rules |

---

## Credentials

All API keys / secrets via environment variables; never committed.

| Variable | Purpose |
|---|---|
| `SF_CLIENT_ID` / `SF_CLIENT_SECRET` / `SF_PRIVATE_KEY` (or `SF_REFRESH_TOKEN`) | Salesforce OAuth — **JWT bearer flow preferred for unattended service** (no user interaction at refresh); refresh-token flow is a fallback if JWT not approved by SF admin. Engineering decides at provisioning. |
| `SF_API_VERSION` | Pinned Salesforce API version (avoid breaking on auto-upgrade) |
| `AURUM_FILE_PATH` | File watch root (`/exports/aurum/` per artefact 5) |
| `AURUM_FILE_AUTH` | SFTP credentials OR mount permissions, depending on access mode |
| `AM_ROUTING_CONFIG_PATH` | Path to AM coverage map YAML |
| `OPS_ALERT_WEBHOOK` | Slack/email webhook for ops alerts |
| `AGENT_VERSION` | Git SHA at deploy (written into per-case event log only — NOT into AUDIT_REF, which stays compact for Aurum-side ID matching) |
| `BDRA_AUTHORITY_THRESHOLDS_PATH` | Path to threshold YAML (CO max, AM tiers) |
| `AURUM_UI_SERVICE_ACCOUNT` (Wave 2) | Aurum login for service-account UI write |

---

## Shared Wave 1 → Wave 2/3 assets

Built in Wave 1, reused downstream:
- Salesforce CRM client + dispute-state writer
- Aurum CSV file watch + schema validator (the most-reused shared asset — Wave 2 reuses for write-back verification, Wave 3 reuses if billing-watch needs invoice context)
- Internal config store pattern (YAML + versioning + deploy review)
- AM coverage map (Wave 2 reuses for service-account approval routing)
- AUDIT_REF generator (Wave 2 reuses for service-account-emitted credits)
- Remedy template library + pattern matcher (Wave 2 reuses; Wave 3 reuses to predict downstream remedy)
- Per-case event log + ops alert pipeline

---

## Pre-launch P0 checklist (Wave 1)

- [ ] Dispute system identified (G-9b) — CRM cases vs custom object vs dedicated app
- [ ] Aurum CSV access path provisioned (SFTP/mount) + service account permissions verified
- [ ] Schema validation contract written for all 7 files; tested against current samples
- [ ] AM coverage map config loaded; A-5 mismatch fallback rule decided with Sarah
- [ ] CO authority threshold (£) defined with Sarah
- [ ] Remedy template library seeded for FUEL_SURCH_DAMAGE, DIM_WEIGHT, REDELIVERY_FEE
- [ ] Confidence thresholds set (provisional; mock-test calibrated)
- [ ] Chase cadence approved by Sarah (T+7 nudge, T+14 escalate, T+30 close-proposal)
- [ ] Salesforce OAuth app registered; refresh token issued
- [ ] Ops alert webhook live; tested with synthetic schema-failure event
- [ ] First 100 cases human-confirmed customer-comms send (tone calibration window)
- [ ] Idempotency tested: same dispute_id processed twice = no duplicate packets
- [ ] Schema-drift drill: deliberately corrupt a CSV; confirm agent halts cleanly
- [ ] Schema-failure alert latency test: confirm ops Slack/email webhook fires ≤15 min from agent halt; ops can disable BDRA Aurum reads within 1 hour of alert
- [ ] Partial-failure recovery test: simulate CRM write failure between tasks 4.9 (packet prepared) and 4.12 (state update); confirm agent re-reads dispute by `processing_id` on retry and any committed step is no-op (idempotency holds across the 4.9 → 4.12 sequence)

## Pre-launch P0 checklist (Wave 2)

- [ ] G-12 resolved: Aurum UI accepts service-account login with credit-write scope
- [ ] Service-account credentials issued + rotated to secrets manager
- [ ] UI automation client built + tested in Aurum sandbox (if available) or with throwaway test customer
- [ ] Verification loop: AUDIT_REF emitted by agent appears in next-day APEX_CREDITS export
- [ ] Rollback plan: how to reverse a wrongly-applied credit if UI write succeeds but logic was wrong (manual reverse via Aurum support 48hr ticket)

## Pre-launch P0 checklist (Wave 3)

- [ ] G-11 (dispatch console) OR G-10 (Driver App) damage-flag read API confirmed
- [ ] Damage-flag → billing-watch mapping rule defined
- [ ] BDRA Wave 1 stable (≥3 months production) before Wave 3 starts feeding it pre-emptive cases
