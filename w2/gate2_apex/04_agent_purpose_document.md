# Agent Purpose Document
**Gate 2 — Apex Distribution Ltd**
**Source:** DSM (`02`), V×V (`03`); CLM (`01`); Source Index in `00`

> Design choices that depend on data not in brief are tagged `[Unconfirmed: requires X]` — these are deployment blockers, not assumptions.
>
> **Code legend:** `4.1`–`4.13Q` = activity-catalog tasks defined below; `C4A`–`C4E` = DSM task clusters; `WS1–4` = work streams; `A-N` / `B-N` / `C-N` = cross-artefact evidence (canonical: `00_elicitation_log.md`); `G-N` = open gaps (canonical: `CLAUDE.md` §Open gaps); `BP-X1` = cross-stream breakpoint (canonical: CLM).

## Agent selection

V×V committed **WS4 BDRA** as Wave 1. Largest contiguous Agent-led cluster surface; internal-facing (so no rerun of the 2024 chatbot); the audit-bypass fix becomes a feature; reads Aurum data but doesn't depend on Aurum's stability for writes. Wave 2 = C4C (Aurum auto-write, blocked on G-12). Wave 3 = C1C cross-stream handoff (blocked on G-11).

**Honest scope note:** Wave 1 BDRA does NOT touch dispatcher work in WS1. C1A (where dispatcher discretion lives) is **Human Only in Wave 1 per DSM**, becoming Human-led + AS only in Wave 3 when both Driver App (G-10) and dispatch console (G-11) APIs resolve and the agent can pre-stage context in real-time. So WS1 capacity is unchanged in Wave 1. WS1 enhancement waits for Wave 3.

---

## Agent 1 — Billing Dispute Resolution Assistant (BDRA)

### Purpose document

```
Agent Name: BDRA — Billing Dispute Resolution Assistant
Job to be Done: Investigate the root cause of a customer billing dispute,
                decide the remedy within authority bounds, prepare a credit
                packet with proper APPROVER_ID + AUDIT_REF, draft
                customer-closing comms, and chase stalled disputes on cadence.

Business context: WS4 — 60 disputes/day, 28 min handling/case, 28 hr/day
                  CO effort. Highest unit-value stream; sits downstream of
                  WS1 damages on the cross-stream value chain
                  (see CLM §Cross-stream value chain + register C-1 for
                  the 50%-of-disputes evidence).

Primary objectives:
  1. Eliminate the audit-bypass pattern (A-4) by emitting APPROVER_ID +
     AUDIT_REF on 100% of agent-prepared credits.
  2. Absorb routine disputes end-to-end; escalate novel patterns with
     full context for human decision.
  3. Close the chase-logic gap (B-3): no dispute stalls untouched
     beyond the cadence threshold on AWAITING_CUST.

KPIs (paired so they cannot conflict):
  - Audit completeness:  100% of agent-emitted credits carry APPROVER_ID +
                         AUDIT_REF (vs current bypass)
  - Packet acceptance:   ≥95% of agent-prepared packets accepted by
                         CO/AM without material modification
  - Routine coverage:    ≥60% of WS4 cases handled agent-led (routine
                         pattern); ≥35% total effort absorbed
                         (NOT 1:1 — routine cases keep C4C human-keystroke
                         step in Wave 1; "absorbed" is per-case-time-saved,
                         not per-case-count)
                         [Estimated — sensitivity ±10pp, see V×V §3]
  - Chase coverage:      100% of disputes ≥7d on AWAITING_CUST receive
                         a nudge per cadence (cadence set by stakeholder)
  - Cost per case:       <£0.10 (token + tool + infra)
                         [Estimated — see V×V §3 token assumptions]

Delegation archetype: Agent-led + Human Oversight (routine);
                      Human-led + Agent Support (novel patterns, C4C write).

Hard constraints (non-negotiable):
  - Never apply a credit without APPROVER_ID + AUDIT_REF in the packet
  - Never send customer comms without human confirmation in Wave 1
  - Never proceed past Aurum read on schema-validation failure (halt + alert)
  - Never auto-close a dispute with open customer comms <72h old
  - Never modify an Aurum invoice (UI write blocked Wave 1; ticket route
    only via human; service-account write conditional on G-12)

Escalation triggers (must match Autonomy Matrix exactly):
  - Novel pattern (no codified remedy template match)
       → CO agent queue with full dossier
  - Aurum schema-validation failure on any required file read
       → Halt + alert ops + flag dispute as "agent unavailable"
  - Dispute touches active delivery exception (cross-stream WS1)
       → Human pickup with cross-stream context surfaced
  - Customer escalates via channel other than reply (phone, manager-cc)
       → CO agent picks up; agent presents context dossier read-only
  - Confidence below threshold (provisional 0.8) on remedy classification
       → CO agent queue [calibrate in mock testing]

Authority routing (NOT escalation — routine):
  - Amount > CO authority threshold [Unconfirmed: threshold pending Sarah Q14]
       → AM (per AM coverage map) receives prepared packet for UI entry
```

### Activity catalog

> **Sequence note:** The agent intake-polls disputes from CRM (or dedicated dispute system, pending G-9b). Aurum CSV reads are *enrichment*, not the source-of-truth for dispute existence — that lives in the operational system.

> **Honest implementation note (per pack §8 anti-pattern check):** "Fully agentic" delegation does NOT mean "uses an LLM." Most BDRA tasks below are deterministic code (script / rule / API call / RPA) wrapped inside the agent's autonomous flow. Only the **Imp.** column flagged **LLM** uses the LLM; everything else is conventional IT (cheaper, faster, debuggable). This matches the ATX guidance: *"if a task could be solved with static rules, RPA, or a simple script — do not build an agent."* The LLM is the smallest moving part; the rest is plumbing. Per-case token cost in V×V §3 reflects only the LLM operations (4.5 partial + 4.6 + 4.11), not the full catalog.
>
> **Imp. legend:** **Script** = procedural code (poll, parse, format); **Rule** = deterministic logic / lookup table; **API** = system-integration call; **RPA** = UI automation; **LLM** = true agent reasoning (probabilistic, requires tokens); **Hybrid** = combination.

| # | Task | Type | Delegation | Imp. | Data | Tool | Risk |
|---|---|---|---|---|---|---|---|
| 4.1 | Poll dispute system for new + stalled records (5-min interval) | Retrieval | Fully agentic | **Script** | Dispute records | CRM/dispute REST | Low |
| 4.2 | Extract dispute fields + assign `processing_id` (idempotency from 4.6 onward) | Retrieval | Fully agentic | **Script** | Record | None | Low |
| 4.3 | Cross-source enrichment: pull invoice (APEX_BILL_DAILY), surcharge calc (APEX_FUEL_SURCH), prior credits (APEX_CREDITS), recon status (APEX_RECON), customer master (APEX_CUSTOMER_MASTER) — all behind schema-validation gate | Retrieval | Fully agentic (schema-gated) | **Script** | Aurum CSVs | Aurum file watch + schema validator | Medium — halt on schema fail |
| 4.4 | Cross-stream check: any open WS1 delivery exception linked to invoice? (CRM case query by invoice_no) | Retrieval | Fully agentic | **API** | CRM cases | CRM REST | Low |
| 4.5 | Compose context dossier (customer + dispute + invoice + cause-evidence + prior-pattern matches) | Generation | Fully agentic | **Hybrid** (script aggregation + LLM summary) | Aggregated context | Internal | Low |
| 4.6 | Pattern-match remedy template (e.g. FUEL_SURCH_DAMAGE → goodwill ≤ 50% of surcharge per Hayes/Pete precedent; DIM_WEIGHT → re-verify before crediting per Tom J.'s caseload pattern) | Reasoning | Agent-led (routine); Human-led + AS (novel) | **LLM + Rule** (LLM proposes, rule-table validates allowed remedies) | Dossier + remedy template library | LLM + rule lookup | Medium |
| 4.6E | If novel pattern OR confidence below threshold → escalate to CO queue with full dossier; STOP at 4.6 | Escalation | Human takes over | **Rule** | Dossier | CRM queue | Low |
| 4.7 | Authority routing: if amount within CO authority → assign self as preparer + AM as APPROVER_ID per coverage map; if above → AM-only path | Decision | Agent-led | **Rule** | Amount + AM coverage map | None (rule lookup) | Medium |
| 4.8 | Generate AUDIT_REF (deterministic format: `AUD-{YYYY}-BDRA-{processing_id}-{seq}`) | Generation | Fully agentic | **Script** | processing_id | None | Low |
| 4.9 | Prepare credit packet: REASON_CODE, amount, APPROVER_ID, AUDIT_REF, justification text | Generation | Fully agentic | **Script** (template fill) | All preceding | None | Low |
| 4.9E | If C4C blocked (G-12 unresolved) → packet to AM email queue for human Aurum UI entry; STOP at 4.9 | Escalation | Human-led + AS | **Script** (email send) | Packet | Email | Low |
| **— Wave 2 only (G-12-gated) below this line —** | | | | | | | |
| 4.10 | (Wave 2 only) Apply credit via Aurum UI service account; verify in next-day APEX_CREDITS export by AUDIT_REF lookup `[Inferred — Aurum may normalise AUDIT_REF on ingest; verify shape preservation in mock testing]` | Action | Agent-led + Oversight | **RPA** (Selenium/Playwright pattern) | Packet | Aurum UI client | Medium |
| **— Wave 1 (resumed) below this line —** | | | | | | | |
| 4.11 | Draft customer-closing comms; route to CO agent for confirm-and-send (Wave 1) | Generation | Agent-led + Oversight | **LLM** (template-guided) | Outcome | CRM email composer | Medium |
| 4.12 | Update dispute record: status, resolution code, link to APEX_CREDITS row (once visible) | Action | Fully agentic | **API** | Outcome | CRM REST | Low |
| 4.13 | Chase-cadence engine: scan AWAITING_CUST disputes daily; cadence `[Provisional — Sarah Q13]` T+7 = nudge draft (human send); T+14 = escalation flag; T+30 = auto-close proposal (CO confirms) | Generation + Action | Agent-led + Oversight | **Hybrid** (rule-driven timer + LLM-drafted nudge text) | Dispute records | CRM REST | Low |
| 4.13Q | QA: tag 5% of agent-led closed disputes (uniform random) for daily CO review | Generation | Fully agentic | **Script** | Disposition | CRM tag API | Low |

**Implementation summary across the catalog (16 tasks total):**
- **Pure LLM (2 tasks):** 4.6 (remedy classification), 4.11 (customer comms drafting)
- **Hybrid LLM + deterministic (2 tasks):** 4.5 (script aggregation + LLM summary), 4.13 (rule timer + LLM nudge text)
- **Pure deterministic (12 tasks):** 4.1, 4.2, 4.3, 4.4, 4.6E, 4.7, 4.8, 4.9, 4.9E, 4.10 (RPA, Wave 2), 4.12, 4.13Q
- **Engineering cost is mostly NOT in the LLM** — it's in the deterministic plumbing (Aurum schema validation, CRM client, AM router, idempotency, monitoring). LLM is the cheap part to swap if pricing changes; per-case token cost in V×V §3 reflects only the 2 pure + 2 partial LLM operations.

**Note on 4.6:** "Routine" = dispute matches a codified pattern (customer × dispute_type × known remedy precedent). Initial pattern library seeded from APEX_DISPUTES_OPEN history + artefact 2 precedent. Library expands via 4.13Q sample review. **Novel = always escalate.** (Cross-mapping enforcement detailed in Action Mapping Table + Hard Constraints.)

**Note on 4.7:** Authority routing uses the AM coverage map (`00` actor table). **Default = "any active AM"** — matches the lived practice (A-5: 2 of 4 sampled credits had APPROVER_ID ≠ customer's specific AM, so role-based authority is in use today). Customer-specific AM is the *configurable variant* to confirm with Sarah at Q7. Alert if no AM available.

**Note on 4.8:** AUDIT_REF format is BDRA-namespaced so audit can distinguish agent-emitted credits from human-emitted (current `AUD-YYYY-NNNNN` pattern stays intact for human credits).

### Action mapping table

**Default `dispute_type → remedy candidate set` (LLM constrained at 4.6 to choose from this set; cross-mapping is a schema error):**

| dispute_type | Remedy candidate set | Notes |
|---|---|---|
| `FUEL_SURCH_DAMAGE` | `GOODWILL` (≤ 50% of surcharge), `FUEL_RECALC` (if calc error verifiable), `REJECT` | Hayes-class precedent: goodwill default. FUEL_RECALC requires evidence of calc fault (A-6: criteria pending Q-A6). |
| `DIM_WEIGHT` | `INV_CORR` (if measurement re-verified), `GOODWILL` (≤ amount), `REJECT` | Tom J. handles current load; pattern: re-verify before crediting |
| `REDELIVERY_FEE` | `GOODWILL` (≤ amount), `REJECT` (if customer cause), escalate if amount > authority | |
| `OTHER` | Always escalate to CO/AM | Novel pattern by definition |

**REASON_CODE → APEX_CREDITS column** mapping is exact (must match Aurum's existing enum: `FUEL_RECALC`, `GOODWILL`, `INV_CORR`, plus any others in the schema we haven't seen — `[Unconfirmed: full enum from Aurum schema doc — engineering discovery]`).

### Autonomy matrix

```
AGENT DECIDES AND ACTS ALONE (routine pattern, all schema gates passed):
  - Polling, intake, processing_id assignment (4.1, 4.2)
  - Aurum CSV reads (schema-gated) (4.3)
  - Cross-stream WS1 check (4.4)
  - Context dossier composition (4.5)
  - AUDIT_REF generation (4.8)
  - Credit packet preparation (4.9) — but does NOT submit to Aurum in Wave 1
  - Dispute record updates (4.12)
  - Chase-cadence draft generation (4.13 — drafts only, send is human in Wave 1)
  - QA sample tagging (4.13Q)

AGENT ACTS, HUMAN NOTIFIED AFTER (audit/sample review, no blocking):
  - Routine remedy classification (4.6 routine path)
  - Authority routing (4.7) — AM sees the assignment
  - Dispute auto-close on T+30 stale (4.13) — CO confirms via daily review
  - QA sample (4.13Q) — daily CO review of 5% sampled closures

AGENT PROPOSES, HUMAN APPROVES BEFORE ACTION:
  - Credit packet → AM/CO for Aurum UI entry (4.9E in Wave 1)
  - Customer comms drafts → CO confirms before send (4.11)
  - Chase nudges → CO confirms before send (4.13)

HUMAN TAKES OVER (agent supports with dossier):
  - Novel remedy pattern (4.6E) — agent dossier, human decides
  - Confidence below threshold (4.6E) — agent dossier, human decides
  - Cross-stream WS1-active dispute (4.4 hit) — human pickup, agent context
  - Customer escalates off-channel — human pickup, agent context
  - Aurum schema-validation failure — agent halts, ops investigates
  - Amount above CO authority + AM coverage gap (rare) — escalate to ops
```

### System and data summary

**Extracted to `05_system_data_inventory.md`** for full inventory (Wave 1 + Wave 2 + 3, credentials, shared assets, P0 pre-launch checklist).

Key Wave 1 systems: Salesforce CRM (REST, OAuth), Aurum CSV file-watch + schema validator, AM email queue (for packet handoff in Wave 1), QA tag API (CRM).
Key Wave 1 P0 blockers: Dispute system identification (G-9b), Aurum CSV access path + service account credentials, schema validation contract per file, AM coverage map config.

### Context engineering design

**Memory architecture:**

| Type | Content | Storage | Lifecycle |
|---|---|---|---|
| **In-context** | Current dispute + dossier (invoice, customer, prior credits, cross-stream check) | Prompt window | Per case; cleared after 4.12 |
| **Episodic** | Customer dispute history (last N disputes, remedies, outcomes) | CRM query (cached 1hr) | **Fetched at 4.5** (always — it's small and load-bearing) |
| **Semantic** | Remedy template library; AM coverage map; authority thresholds; Aurum schema contracts | YAML config in repo | Versioned; deploy review on change |
| **Procedural** | Decision rules, escalation triggers, AUDIT_REF format, hard constraints | System prompt | Version-controlled |

**Retrieval strategy:**
- **Aurum CSVs (4.3):** file-watch latest snapshot per file; schema-validate before read; halt on mismatch. Joins by INVOICE_NO + CUSTOMER_ID.
- **CRM (4.4 + 4.12):** REST query by invoice_no for cross-stream WS1 check; case-write on close.
- **Cost control:** dossier composition is the single highest-token operation. Token ceiling per case: 3K input + 800 output. Episodic history truncated to last 5 disputes per customer.

**Prompt principles:**
1. **Role + scope first:** "You are BDRA. You investigate billing disputes and prepare credit packet with proper APPROVER_ID + AUDIT_REFs. You do not modify Aurum invoices. You do not send customer comms without human confirmation."
2. **Hard constraints as numbered rules** (matches "Hard constraints" section above).
3. **Structured output (JSON schema enforced):**
   ```
   { processing_id, dispute_id, classification (routine|novel|cross_stream),
     remedy: { type ∈ allowed candidate set per dispute_type, amount,
               justification, confidence },
     packet: { APPROVER_ID, AUDIT_REF, REASON_CODE, customer_id, invoice_no },
     escalation_reason | null,
     audit_trail (list of decision points + sources cited) }
   ```
   Invariants: (a) `remedy.type ∈ candidate_set[dispute_type]`; (b) `escalation_reason != null` ⟺ classification ∈ {novel, cross_stream, low_confidence}; (c) packet fields populated iff classification == routine AND amount ≤ authority.
4. **Chain-of-thought** required for routine classification (the audit_trail field) — every cited source explicit.
5. **Few-shot examples:** seed with artefact 2 (Pete H. case, FUEL_SURCH_DAMAGE → £170 goodwill ≈ 50% of £340 surcharge). Replace with stakeholder-validated examples in mock testing.
6. **Token discipline:** system prompt ~2K (role + scope + 5 hard constraints + 6 prompt principles + JSON schema); per-case dossier < 3K; episodic capped at last 5; no full-history retrieval.

### Operational constraints

- **Single-instance Wave 1.** Dispute polling has no claim semantics in CRM (assumed); horizontal scaling would race. Single-writer pattern.
- **Idempotency.** `processing_id` assigned at 4.2; lookup at 4.6/4.9/4.12 via CRM custom field. Duplicate retries are no-ops.
- **Polling.** 5-min interval on dispute system; 24hr cadence on chase scan (4.13). Webhook upgrade pending CRM/dispute-system capability discovery.
- **Schema validation.** Contract per Aurum file: column count + names + order + types + value ranges where known. Hard-fail = halt agent + alert ops Slack/email; don't downgrade to warning.
- **Aurum quarterly schema risk.** Pre-launch + monthly: diff actual schema against contract; alert if drift detected before agent next reads it.

### Monitoring

- **Per-case event:** processing_id, latency (4.1→4.12), dispute_type, classification, remedy.type, remedy.amount, escalation_reason, audit-trail-completeness boolean
- **Daily aggregation:** case count, routine/novel split, escalation count by reason, packet acceptance rate (when AM/CO confirms), avg time-to-close
- **Surface:** CRM dashboard or Google Sheet (whichever Sarah/CO supervisor prefers — choose at Wave 1 setup)
- **Alerts:**
  - Schema-validation failure (any) → ops + halt
  - Packet acceptance rate < 90% over rolling 7d → calibration alert to CO supervisor
  - Routine coverage < 50% over rolling 7d → calibration alert (under-confident classifier)
  - Chase nudges sent > expected daily volume → cadence calibration alert
  - 0 cases processed in any 6hr window during business hours → ops (silent failure check)

---

## Agent 2 — Cross-Stream Damage→Billing Watch (DECA-light, Wave 3)

```
Agent Name: DECA-light — Damage→Billing Watch
Job to be Done: When WS1 records a damage exception, generate a "billing-watch"
                record on the customer + invoice + delivery context — feeding
                BDRA's intake at 4.4 with the upstream cause already known.
                Reduces WS4 dispute volume at source.

Covers: CLM C1C cross-stream handoff (BP-X1 prevention).

Delegation archetype: Agent-led + Human Oversight.

Wave 3 prerequisites:
  - G-11 resolution (dispatch console) OR G-10 (Driver App) for damage-flag read
  - Wave 1 BDRA stable (so the billing-watch records have a consumer)
  - Dispatcher-side process change: structured damage flag emitted at WS1 task 1.6
    (otherwise the read-side has no signal to lift). This is a process
    prerequisite, not a downstream wave.
```

---

## Compounding roadmap

| Wave | Agent | Build | Reuses | Effort recovered (central) |
|---|---|---|---|---|
| 1 | BDRA core (C4A + C4B-routine + C4D + C4E) | Aurum schema validator; AM router; CRM dispute writer; chase engine; dossier composer; remedy template library | — | ~2,700 hr/yr (35% of WS4) |
| 2 | C4C Aurum auto-write | Aurum UI service-account client | Wave 1 schema validator + packet generator | +800–1,200 hr/yr |
| 3 | DECA-light (C1C) | Dispatch console / Driver App damage-flag read; billing-watch generator | Wave 1 CRM writer + dossier composer | +500–800 hr/yr (upstream prevention) |

### Integration reuse matrix

| Asset | Wave 1 | Wave 2 | Wave 3 |
|---|---|---|---|
| Salesforce CRM REST | Build | Reuse | Reuse |
| Aurum CSV file watch | Build | Reuse | Reuse |
| Aurum schema validator | Build | Reuse | Reuse |
| AM coverage map config | Build | Reuse | Reuse |
| Remedy template library | Build | Reuse + extend | Reuse |
| AUDIT_REF generator | Build | Reuse | Reuse |
| Dispute-state writer | Build | Reuse | Reuse |
| Aurum UI service-account client | — | Build | Reuse |
| Dispatch-console / Driver App reader | — | — | Build |
| Billing-watch generator | — | — | Build |

---

## Open deployment blockers

| Blocker | Wave | Priority | Owner |
|---|---|---|---|
| Dispute system identification (CRM cases? dedicated app?) | 1 | P0 launch | Engineering + Sarah |
| Aurum CSV access path + service account credentials | 1 | P0 launch | Engineering + Aurum support |
| Schema validation contract per Aurum file (BILL_DAILY, FUEL_SURCH, CREDITS, RECON, DISPUTES_OPEN, AGED_RECEIVABLES, CUSTOMER_MASTER) | 1 | P0 launch | Engineering |
| AM coverage map config (Q7 — also resolve A-5 routing fallback rule) | 1 | P0 launch | Sarah + AMs |
| CO authority threshold for self-prepared packets (£) | 1 | P0 launch | Sarah |
| Remedy template library seed (FUEL_SURCH_DAMAGE pattern + DIM_WEIGHT pattern + REDELIVERY_FEE pattern) | 1 | P1 — affects accuracy | Sarah + CO supervisor |
| Confidence thresholds (provisional: routine ≥ 0.8; mock-tested) | 1 | P1 — calibration | ML/ops + Sarah |
| Aurum UI service-account auth model | 2 | P0 Wave 2 | Engineering + Aurum support |
| Chase cadence (T+7, T+14, T+30 — provisional) | 1 | P1 — Sarah preference | Sarah |
| Customer comms tone calibration (first 100 cases human-confirmed) | 1 | P1 — trust build | CO supervisor |
| Dispatch console / Driver App damage-flag read API | 3 | P0 Wave 3 | Engineering |
