# Deliverable #7 — Validation Plan
**Engagement:** MedFlex Healthcare Staffing
**Participant:** Pavel Klimasheuski
**Date:** 2026-05-13

---

## Purpose

This plan defines how the MedFlex agentic system is validated before production and monitored in operation. It covers three agents (Request Intake, Nurse Matching, Submission) across four validation dimensions: accuracy, edge cases, failure modes, and compliance risk. Each named risk includes a detection mechanism and a mitigation.

---

## Baseline metrics

Validation has no meaning without a baseline. The three operational metrics that define success for this engagement:

| Metric | Current baseline | Phase 1 target | How measured |
|---|---|---|---|
| Average fill time | 4.2 hours | < 1 hour | `matching_results.submission_timestamp − shift_requests.created_at`, joined on `shift_request_id` (Agent 3 writes `submission_timestamp`; Agent 1 writes `created_at` from ServiceNow `sys_created_on`). **Note:** this measures time-to-first-candidate-submission, not actual fill time. Hospital confirmation latency is outside MedFlex's control and is not captured here; submission time is the correct leading indicator. |
| Mismatch rate | 7% | < 4% | Hospital-flagged dissatisfaction reports / total fills; Agent 2 logs `selected_candidate_nurse_id` and credential match for post-hoc audit |
| No-show rate | 12% | < 10% (Phase 1); active confirmation design in Wave 2 if not improving | Agent 3 logs `fill_outcome = NO_SHOW` per MatchingResult; compare pre/post deployment |
| Coordinator throughput | ~120 decisions/day per coordinator | ≥ 360/day per coordinator | Decisions logged per `coordinator_id` per day from `audit_log`; compare pre-deployment baseline vs. weeks 2–4 of Phase 1 |

**Measurement commitment:** All three metrics are measurable only if Agent 3's logging is correctly instrumented from day one (see Operational Logging section of Architecture document). Partial logging invalidates all comparisons.

---

## Section 1 — Accuracy validation

### 1.1 Agent 1: Request Intake parsing accuracy

**What to measure:** Does the structured `ShiftRequest` output correctly represent the hospital's intent in the source free text?

**Evaluation approach — advisory period as the measurement instrument:**

A pre-launch isolated parsing evaluation (asking coordinators to parse requests manually and compare against Agent 1's output) is impractical: coordinators don't parse in isolation in their natural workflow — they parse and match in a single cognitive step. Asking them to do a separate parsing task generates low-quality ground truth at real coordination cost, and likely won't happen reliably under production pressure.

The more practical approach is to use the advisory period itself as the measurement instrument. During Phase 1 week 1 (all cases through coordinator review regardless of confidence), coordinators see the structured ShiftRequest the agent produced and act on it directly — approving the parse, correcting a field, or flagging for clarification. Their corrections are natural ground truth captured as a by-product of real work, not a separate evaluation exercise.

- **Parse correction rate** (primary signal): proportion of ShiftRequests where a coordinator edited at least one field before approving. Target: ≤ 10% correction rate after the first week (higher in week 1 is expected as coordinators learn the interface). Tracked per field — credential corrections are the highest-risk signal.
- **Correction field breakdown**: of corrections, what proportion touch `required_credentials` vs. `shift_date`/time vs. `unit_type`? A high credential correction rate indicates a systematic inference problem; a high date/time correction rate indicates a prompt or hospital-profile issue.
- **E2e accuracy as the downstream check**: if parse accuracy is high but fill outcomes are poor (high mismatch or no-show rate), the gap may still originate in parsing. The e2e fill outcome (tracked per MatchingResult via Agent 3) is the ultimate validation — parse accuracy is a leading indicator, not a goal in itself.

**Key risk: credential category inference.** A parse that maps "ICU-trained RN" to MED_SURG produces a wrong-credential submission even if Agent 2 works correctly. This is the highest-impact parse error. Credential corrections during the advisory period are the primary signal for this risk.

**Mitigation:** Low-confidence parses (confidence < 0.85 on `required_credentials`) route to coordinator clarification queue before reaching Agent 2. The advisory period's correction data calibrates whether this threshold is set correctly.

---

### 1.2 Agent 2: Nurse Matching ranking quality

**What to measure:** Does the agent's rank-1 candidate match whom an experienced coordinator would have selected?

**Evaluation approach — pre-launch shadow period:**
- Run Agent 2 in advisory-only mode for the first week (all outputs go to coordinator review regardless of confidence score). Log `proposed_nurse_id` vs. `selected_candidate_nurse_id` on every case.
- At end of week 1: compute agreement rate (how often is the agent's rank-1 the same as the coordinator's choice). Target: ≥ 80% agreement before enabling AUTO_SUBMIT path.
- Segment by case type: ICU vs. general, CRITICAL urgency vs. STANDARD, thin pool (≤ 2 eligible) vs. normal pool. Agreement rates will differ; ensure each segment meets threshold independently before enabling AUTO_SUBMIT for that segment.

**What to measure: confidence score calibration.**
- `matching_confidence` is only useful if it predicts actual fill success. Measure: for cases with `matching_confidence ≥ 0.80` that auto-submitted, what fraction filled successfully (`fill_outcome = FILLED`)? Target: ≥ 88% fill rate for HIGH_CONFIDENCE auto-submits.
- If calibration is poor (e.g., 0.80+ confidence cases filling at 70%), the threshold is mis-set. Review LLM prompt calibration guidance before lowering the threshold.

**ADR-1 revisitation data — mandatory from day one:**
- `submission_path` (AUTO_SUBMIT vs. COORDINATOR_REVIEW) and `fill_outcome` (FILLED / UNFILLED / NO_SHOW) must be logged from the first case. Without this, the 4-week accuracy comparison is impossible.
- Revisitation trigger: after 4 weeks of operation, compare `fill_outcome` distributions for AUTO_SUBMIT vs. COORDINATOR_REVIEW cases. If AUTO_SUBMIT accuracy ≥ coordinator average: lower threshold by 0.05. If worse: investigate before any threshold change.

---

### 1.3 Agent 3: Submission and race condition handling

**What to measure:** Are confirmed nurses correctly withdrawn from concurrent submissions?

**Evaluation approach:**
- Unit test: seed 3 simultaneous MatchingResults for the same nurse at different hospitals. Simulate hospital_A confirmation. Verify: nurse withdrawn from hospitals B and C; re-matching triggered for B and C (or escalation if re-match fails); audit log records all three state transitions with timestamps.
- Staging environment test: run 10 simulated concurrent submissions for the same nurse pool. Verify no double-confirmations.

---

## Section 2 — Edge cases requiring explicit test coverage

The following edge cases must have named test fixtures before go-live. Each maps to a specific failure path that a happy-path integration test will miss.

| ID | Edge case | Why it matters | Test fixture |
|---|---|---|---|
| EC-A | Credential expires before shift date | Nurse must be excluded in Phase 1; compliance flag required | Nurse with `ICU_CERTIFIED.expiry_date < shift_date`; verify exclusion reason = `CREDENTIAL_EXPIRED`; verify compliance alert fired |
| EC-B | Credential expires within 30 days after shift date | Nurse eligible but alert required; coordinator sees warning | Nurse with `expiry_date = shift_date + 16 days`; verify `credential_expiry_alert = true`; verify `warnings` field populated |
| EC-C | No eligible nurses after hard filtering | Escalation path fires immediately; not a silent failure | ICU shift with zero VERIFIED ICU_CERTIFIED nurses available; verify `routing_decision = ESCALATE_NO_CANDIDATES`; verify coordinator notified |
| EC-D | Single eligible nurse (thin pool) | Must force COORDINATOR_REVIEW regardless of composite score | CRNA shift with one eligible nurse who scores 0.92; verify `routing_decision = COORDINATOR_REVIEW` (not AUTO_SUBMIT) |
| EC-E | Shift crosses midnight | Availability overlap check must span two calendar dates | `shift_start = 19:00 Jan 20`, `shift_end = 07:00 Jan 21`; nurse has shift Jan 21 06:00–14:00; verify `AVAILABILITY_CONFLICT` exclusion |
| EC-F | Hospital ambiguity in free text | Agent 1 must flag, not guess | Request with "St Mary's" when two hospitals match "St. Mary's" in database; verify `status = CLARIFICATION_NEEDED`; verify coordinator clarification queue entry |
| EC-G | Simultaneous hospital confirmation for same nurse | Agent 3 must resolve race condition; not both confirmations accepted | Concurrent confirmations from Hospital A and Hospital B for Nurse X within 2 seconds; verify only one confirmation accepted; other withdrawn; re-match triggered |
| EC-H | LLM returns unrecognised nurse_id | FM-2 fallback fires; run does not silently corrupt | LLM mock returns nurse_id not in eligible candidate pool; verify FM-2 triggered; `routing_decision = COORDINATOR_REVIEW`; incident logged |
| EC-I | Nurse on do-not-send list for requesting hospital | Must exclude in Phase 1; not a soft signal | Nurse with `do_not_send = [hospital_id]`; shift from that hospital; verify `DO_NOT_SEND` exclusion |
| EC-J | Parse confidence at the LOW threshold boundary | Low-confidence parse must not auto-route to matching | Request with confidence_score = 0.64; verify routed to clarification queue, not PENDING_MATCH (0.64 is < 0.65; 0.65 itself routes to PENDING_MATCH per spec) |
| EC-K | CRITICAL urgency shift with no coordinator action within 15 minutes | Escalation notification must fire to queue supervisor | CRITICAL shift, MatchingResult status = AWAITING_COORDINATOR; advance clock past CRITICAL_REVIEW_TIMEOUT_MINUTES; verify escalation notification sent |

---

## Section 3 — Failure modes

### FM-1: ServiceNow API unavailable

**Trigger:** Agent 1 cannot retrieve the shift request queue.

**Detection:** HTTP 5xx or timeout on poll cycle; logged immediately.

**Impact:** New requests not processed. Existing MatchingResults in-flight continue. Coordinator queue drains; no new entries added.

**Mitigation:**
- Retry with exponential backoff (2 retries, 30s / 60s intervals).
- After retry exhaustion: fire ops alert via `OPS_ALERT_WEBHOOK_URL`; poll cycle resumes at next interval.
- Coordinator is not blocked on existing in-flight requests; only new intake is paused.
- Downstream agents are unaffected until in-flight queue empties.

**Recovery:** Polling resumes automatically on next cycle when ServiceNow is reachable. No manual restart required.

---

### FM-2: Nurse database API unavailable

**Trigger:** Agent 2 cannot retrieve nurse profiles.

**Detection:** HTTP 5xx or timeout after one retry; logged with `shift_request_id`.

**Impact:** MatchingResult created with `routing_decision = ESCALATE_NO_CANDIDATES`; coordinator must handle manually.

**Mitigation:**
- `ShiftRequest.status` remains `PENDING_MATCH` (not advanced); Agent 2 can retry the run when database recovers.
- Coordinator notified immediately: "Matching blocked — nurse database unavailable."
- Ops alert fired.
- No cascading failure to other in-flight runs; each run is independent.

**Recovery:** When database recovers, the next poll cycle picks up the stranded PENDING_MATCH records and runs matching normally.

---

### FM-3: LLM API failure or invalid output

**Trigger:** Anthropic API returns 5xx, times out, or returns schema-invalid output after one retry.

**Detection:** Schema validation failure or timeout; logged with `llm_call_id`.

**Impact:** Contextual ranking unavailable for affected run.

**Mitigation (algorithmic fallback ranking):**
- Eligible candidates sorted by pre-computed `composite_score` descending.
- `matching_confidence = composite_score × 0.85` for rank-1 (fallback discount).
- `routing_decision = COORDINATOR_REVIEW` regardless of score — no auto-submit during LLM fallback.
- `reasoning_summary = "Automated ranking — LLM reasoning unavailable"` for all candidates.
- Incident logged; model quality monitoring flag set.
- Matching run completes without blocking; coordinator sees ranked list with fallback notice.

**Recovery:** No automatic retry loop on LLM calls. Each new matching run attempts the LLM fresh.

---

### FM-4: LLM cost circuit breaker triggered

**Trigger:** Daily LLM spend exceeds `DAILY_LLM_COST_LIMIT_USD` (default $50, shared across Agent 1 and Agent 2).

**Detection:** Cost tracking per LLM call; cumulative daily total checked before each call.

**Impact — two-tier degradation:**

Agent 2 has a non-LLM fallback (FM-2 algorithmic ranking). Agent 1 does not — free-text parsing is the LLM's core job. The two agents degrade differently:

- **Agent 2:** falls back to FM-2 (algorithmic ranking by composite score); all MatchingResults route to `COORDINATOR_REVIEW` regardless of confidence. Matching continues without LLM reasoning.
- **Agent 1:** cannot parse without LLM. Two options depending on what the coordinator interface supports:

**Target behavior (Option A — requires coordinator manual intake form):**
Unprocessed ServiceNow tickets are surfaced in a coordinator manual intake queue. A coordinator opens the raw ticket text and fills in the structured ShiftRequest fields directly (date, unit type, credentials, urgency) via a form in the review interface. The record is created with `parsed_by = COORDINATOR` and enters the pipeline normally. Agent 2 still runs on coordinator-created records; only Agent 1 is bypassed. This limits the degradation surface to parsing only.

**Interim behavior (Option B — until manual intake form is built):**
Agent 1 stops processing new tickets. Coordinators revert to the pre-system workflow for new requests arriving during the outage window — parse and match manually without agent support. Tickets are re-queued when the cost limit resets at 00:00 UTC if they are still within ServiceNow's query window; otherwise they require manual re-submission.

**Build dependency:** Option A requires the coordinator interface to include a manual ShiftRequest creation form (not yet built). Until it is, Option B is the fallback. The manual intake form should be prioritised as a resilience feature before Phase 1 go-live — without it, any cost-limit event during peak hours fully degrades to manual operations.

**Ops alert:** fires immediately on limit breach with estimated reset time (00:00 UTC). This scenario implies daily volume significantly exceeds projections; investigate cause before next day.

**Mitigation:** Monitor daily spend from 09:00; alert at 70% of limit. Review volume projections if limit is routinely approached.

---

### FM-5: Database unavailable (shared PostgreSQL)

**Trigger:** PostgreSQL connection lost for any agent.

**Detection:** `psycopg2` connection error; logged immediately.

**Impact:** All three agents pause. No state writes; no state reads. In-flight submissions to hospitals may have already been sent — Agent 3 cannot record confirmation.

**Mitigation:**
- All agents implement connection retry with exponential backoff (3 retries).
- Agent 3 implements idempotency on submission: before submitting a candidate to a hospital, check `matching_results.status` — do not re-submit if already `SUBMITTED`.
- Ops alert on DB failure; human intervention required.
- **This is the single most critical dependency.** Database HA (at minimum read replica + automated failover) should be confirmed with Aaron before Phase 1 go-live.

---

### FM-6: Coordinator interface unavailable

**Trigger:** Coordinator review dashboard is down or unresponsive.

**Impact:** AUTO_SUBMIT path continues (override window expires, submissions proceed). COORDINATOR_REVIEW path accumulates backlog; no coordinator action until interface recovers.

**Mitigation:**
- `CRITICAL_REVIEW_TIMEOUT_MINUTES` escalation path fires for CRITICAL urgency shifts; these are escalated to queue supervisor via `COORDINATOR_NOTIFICATION_CHANNEL` (email/SMS fallback if dashboard is down — confirm channel type with Kim).
- Non-critical shifts wait in AWAITING_COORDINATOR; no automatic escalation; coordinator handles backlog on recovery.
- Interface outage must not trigger automated submissions that bypass coordinator review. AUTO_SUBMIT override window expiry is the only valid autonomous submission path.

---

## Section 4 — Compliance and regulatory risk

### 4.1 Credential verification freshness

**Risk:** Agent 2's hard constraint check uses credential data from the nurse database. If that data lags real-world status — a nurse's license has lapsed but the database hasn't updated — Agent 2 will pass an ineligible nurse through Phase 1.

**Detection:** Agent 2 reads `NurseCredential.verification_status` and `expiry_date`. These are only as accurate as the data source. Data freshness lag is an open assumption (A6 in the spec).

**Mitigation:**
- Confirm with Aaron: what is the maximum lag between a credential status change and the database record updating? If lag > 24 hours, Agent 2 cannot reliably enforce credential expiry.
- If lag is material: add a `last_verified_at` timestamp field to credentials; exclude nurses where `last_verified_at > 7 days` ago from the AUTO_SUBMIT path (route to COORDINATOR_REVIEW for manual credential spot-check).
- Compliance alert channel (COMPLIANCE_ALERT_CHANNEL) fires for any nurse excluded with `CREDENTIAL_LAPSED` or `CREDENTIAL_EXPIRED` where VERIFIED status was assigned within the prior 90 days. Compliance team (Linda) reviews.

---

### 4.2 State regulatory drift

**Risk:** Credential categories and licensing requirements vary by state and change over time. The credential taxonomy used in Agent 1's inference and Agent 2's filtering is point-in-time.

**Example failure:** A new state regulation requires an additional certification for ICU nurses. The `CredentialCategory` enum does not include it. Agent 2 ignores it. An under-credentialed nurse is submitted to a hospital in that state.

**Detection:** No automated detection without active monitoring. Drift is invisible until a compliance incident occurs.

**Mitigation:**
- Credential category list is defined in a configuration file (not hardcoded enum). Updates require a deployment, not a code change. Confirm deployment process with Aaron.
- Quarterly review process: compliance team (Linda) reviews MedFlex-relevant state regulatory changes; maps to `CredentialCategory` updates where required.
- For states where MedFlex operates, subscribe to relevant state nursing board notification services if available.
- Interim: flag all shifts where the hospital state is in a state with known regulatory volatility for coordinator credential spot-check until taxonomy is confirmed current.

---

### 4.3 PHI and PII handling

**Risk:** Nurse records contain personally identifiable information (PII): name, home address (home coordinates), contact details, credential documents. Audit logs and MatchingResult records reference `nurse_id` (UUID). Coordinator IDs in audit logs are also PII.

**Confirmed handling in spec:** Audit logs log UUID references only — no nurse names, coordinator names, or contact details.

**Open items requiring Linda's input:**
- Does the MedFlex nurse database store any HIPAA-protected information (health records, vaccination status, drug test results)? If so, Agent 2's data fetch and storage must be assessed under HIPAA.
- Retention period for MatchingResult records (3-year assumption — confirm).
- Right-to-erasure requirements: if a nurse leaves MedFlex's roster, can their UUID be anonymised in historical audit records, or must records be deleted?
- Where is the PostgreSQL database hosted? If cloud-hosted, confirm BAA (Business Associate Agreement) status with the cloud provider.

**Mitigation:** No code change required if audit logs remain UUID-only. PHI scoping requires Linda's confirmation before production data flows through the system.

---

### 4.4 Model accuracy drift

**Risk:** LLM reasoning quality for staffing matching may change when the underlying model is updated by Anthropic, or when MedFlex's case mix shifts (new hospital types, new credential categories, volume spikes).

**Detection:** Weekly monitoring of three signals:
- Mean `matching_confidence` for AUTO_SUBMIT cases (sudden drop indicates model regression or case mix shift).
- Agreement rate: `proposed_nurse_id = selected_candidate_nurse_id` on COORDINATOR_REVIEW cases (coordinator disagreement rate rising indicates ranking quality degrading).
- `fill_outcome = NO_SHOW` rate for AUTO_SUBMIT cases (lagging indicator but critical).

**Mitigation:**
- `MATCHING_LLM_MODEL` is a configurable environment variable — roll back to prior model version if a regression is detected without code deployment.
- System prompt changes require review before deployment (noted in spec). Maintain prompt version history.
- If mean confidence drops more than 0.10 from the prior 2-week average: automatically increase routing conservatism (lower effective threshold by 0.05) and alert ops for investigation before manual threshold adjustment.
- Agent 1 prompt similarly versioned; test against the historical parse accuracy baseline after any prompt change.

---

## Section 5 — Single points of failure

| Component | Failure impact | Mitigation |
|---|---|---|
| ServiceNow queue | Agent 1 cannot process new intake; all three channels (email, portal, phone) converge here | Retry with backoff; ops alert; coordinators can process manually via existing workflow during outage |
| PostgreSQL database | All agents pause; in-flight state at risk | Confirm HA configuration with Aaron (at minimum automated failover); Agent 3 idempotency prevents double-submission |
| Anthropic LLM API | Agent 1 cannot parse; Agent 2 falls back to algorithmic ranking | Agent 2 FM-2 fallback covers matching; Agent 1 has no non-LLM fallback — routes to manual coordinator queue |
| MEDFLEX_API_KEY (internal API) | Agent 2 cannot fetch nurse profiles; all matching fails | Separate ops alert; key rotation procedure must be documented with Aaron; never store in code |
| Coordinator notification channel | AUTO_SUBMIT override window notifications not delivered; coordinators cannot act within window | Confirm channel redundancy (dashboard + email/SMS fallback); test notification delivery in staging |
| Shared `shift_requests` table | Both Agent 1 (writes) and Agent 2 (reads) depend on it | Table-level locking strategy for concurrent reads/writes; confirm PostgreSQL connection pool settings with Aaron |

---

## Section 6 — Staging and go-live checklist

The following must pass before Phase 1 production traffic is enabled:

**Functional:**
- [ ] All 11 edge case fixtures (EC-A through EC-K) produce the expected outputs in staging
- [ ] FM-1 through FM-6 failure modes reproduced in staging; recovery verified
- [ ] ADR-1 revisitation logging confirmed: `proposed_nurse_id`, `submission_path`, `fill_outcome` fields populated correctly on test cases
- [ ] Race condition test (EC-G): concurrent confirmations handled without double-submission

**Data and integration:**
- [ ] Aaron session complete: ServiceNow API access confirmed; nurse database schema documented; credential status mechanism confirmed (system flag vs. manual); data freshness SLA established
- [ ] Kim session complete: coordinator review interface validated against her actual workflow; CRITICAL escalation channel confirmed
- [ ] Linda session: PHI/HIPAA scope confirmed; retention period confirmed

**Operations:**
- [ ] `OPS_ALERT_WEBHOOK_URL` configured and tested; alert fires on FM-1 DB failure simulation
- [ ] `COORDINATOR_NOTIFICATION_CHANNEL` configured and tested; coordinator receives notification in staging
- [ ] Daily LLM cost monitoring configured; 70% alert threshold fires in test
- [ ] Database HA confirmed with IT

**Baseline measurement:**
- [ ] Pre-deployment: 5-day baseline of current fill time, mismatch rate, and no-show rate captured from current system (comparison point for post-deployment metrics)
- [ ] Pre-deployment: advisory period correction rate baseline established; target ≤ 10% ShiftRequest correction rate within first week (Section 1.1 measurement instrument confirmed operational — coordinator corrections captured in `audit_log` with `action = COORDINATOR_CORRECTED`)

**Go-live sequence:**
1. Agent 1 intake in advisory mode (parse only; coordinators see structured output but matching doesn't run)
2. After 2-day parse accuracy confirmation: Agent 2 enabled in advisory mode (all routing to COORDINATOR_REVIEW)
3. After 5-day shadow period and ≥ 80% rank-1 agreement: AUTO_SUBMIT path enabled for STANDARD urgency only, at `MATCH_HIGH_THRESHOLD = 0.85` (conservative)
4. After 4-week ADR-1 review: threshold and urgency segment adjustments based on data
