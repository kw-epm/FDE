# Deliverable 7 — Validation Plan

**Author:** Tamas Kiss
**Engagement:** MedFlex agentic transformation  
**Date:** 2026-05-13
**Gate:** Gate 3 — Final submission

---

## 1. Validation framework — the four required categories

Per pack: accuracy + edge cases + failure modes + compliance risk, each with explicitly-named risk vectors and mitigation strategies. This plan organises by category, then by capability spec (`04a-parallel-submit`, `04b-classification`), then by Phase (1, 1.5, 2+).

The plan also names four explicit risk vectors the pack requires: **(a) portal rate limits, (b) regulatory drift, (c) model accuracy drift, (d) single-points-of-failure** — each addressed in §3 with mitigation strategy.

---

## 2. Per-category validation

### 2.1 Accuracy

| Metric | Capability | Threshold | Measurement | Action on breach |
|---|---|---|---|---|
| **Classification accuracy vs eval set** (KPI #6 territory) | 04b classification | Match or exceed historical 93% baseline (= 100% - 7% mismatch rate per BRIEF L67). Phase 1 calibrates against 500-row eval set. | Re-run eval set on every prompt revision; per-field accuracy logged. | Block deploy; revert to last passing prompt; root-cause in prompt-engineering pass. |
| **Component-1 lift on piloted cohort** (KPI #6, Phase 1.5 deliverable) | 04b → 04a feeder | Measurable lift vs cohort-restricted baseline by Week 6; 30%-70% sensitivity range per KC-7. | Cohort-level pre/post comparison; coordinator-sends only (no parallel-submit confound in Phase 1.5). | Halt Phase 1.5 build; revert to Phase 1 read-only spec; surface to Marcus with revised commitment per `06-client-feedback.md` Phase 1.5 revisitation condition. |
| **Submission-packet factuality** (KPI #7) | 04a parallel-submit | ≥ 0.999 slot-level exact-match rate (per `submission_factuality_ledger`). | Slot-level exact-match logged per submission; weekly aggregate. | Halt Stream 3 D3.2 autonomy; coordinator-mandatory mode until root-caused. GR-13 alert fires. |
| **Confidence calibration** (Brier score) | 04b classification | Weekly Brier score on per-field confidences vs coordinator approve/edit/reject signal stays below threshold (PENDING_CALIBRATION — Phase 1 instruments). | Confidence + coordinator action both logged per ticket. | Recalibrate confidence thresholds (§4 of 04b); update Assumption A1.1. |
| **Ranking quality** | 04a (D2.5 input) | Top-3 candidate ranking matches coordinator's top-3 pick on ≥ 85% of T2 cases. | Coordinator approve/edit/reject on ranking decisions logged. | Re-train ranking weights; surface in Phase 1 coordinator dashboard. |

### 2.2 Edge cases

Edge cases are enumerated per-capability in 04a §7 (8 cases) and 04b §7 (4 cases). The validation plan requires:

- **Every enumerated edge case has a corresponding test case** in the Phase 1 test harness; CI gate blocks deploy if any edge case is unimplemented.
- **One-edge-case-per-week deep-dive** in Phase 1 retros: pick the highest-risk edge case observed in production logs, trace through implementation, verify it matches the spec's edge-case clause.
- **EC-1.4 PHONE_MULTIPLIER** is `PENDING_CALIBRATION` — Phase 1 must produce a calibrated starting value within the first 50 phone-transcribed tickets, captured in an Assumption-update review.

Specific high-stakes edge cases (substantive validation work attached):

| Edge case | Capability | Validation work | Mitigation if observed in production |
|---|---|---|---|
| EC-3.4.1 — Revoke stuck (R7.18 manifest) | 04a | Synthetic test fires REVOKE_STUCK; verifies coordinator alert + nurse freeze; verifies 24/7 on-call rotation page-out works (PB-On-Call). | Coordinator manual recovery dashboard; 24/7 on-call rotation; R7.18 sweep on every shift change. |
| EC-MSA-1 — MSA state flips green→yellow mid-flight | 04a | Synthetic test: parallel submission in flight when `msa_state` is updated; verifies new submissions blocked + in-flight allowed to complete + audit-trail `msa_state_at_submit` captured. | Per ADR-1 revisitation condition: any hospital-trust signal flip → revisit assumption. |
| EC-Factuality-1 — Factuality ledger write fails | 04a | Synthetic test: DB outage at factuality-check step; verifies submission halts + alert fires + does NOT proceed. | Ops runbook: ledger DB outage → halt Stream 3 D3.2 autonomy fleet-wide until ledger restored. |
| EC-1.2 — Acronym not in taxonomy | 04b | Test set includes 30 synthetic tickets with edge-case department acronyms (substrate from Linda compliance owner). | Coordinator clarification queue + per-acronym taxonomy-extension PR template. |

### 2.3 Failure modes (named risk vectors)

Each named per pack requirement, each with mitigation. Many lift from gate2 substrate (`02-cognitive-load-map.md` Failure Modes, `assumptions-log.md` Risk Register).

| Failure mode | Where it surfaces | Mitigation strategy |
|---|---|---|
| **Coordinator non-adoption (R7.8, CRITICAL)** — coordinators bypass agent; Failure-2 replay | 04b classification + 04a coordinator escalation paths | Phase 1 read-only baseline before automated decisions (de-risking spine); senior coord champion sign-off (Kim — see deployment readiness §5); coordinator-visible audit trail per decision; D8 reflection captures pattern. |
| **Hospital portal RPA fragility (Adversarial A9)** — portal change breaks submission channel | 04a parallel-submit | Portal contract tests run nightly; revoke success-rate monitor per channel; <95% triggers FA suspension on that tier; route ALHO until channel hardened. |
| **Ledger inconsistency** (ET-9 circuit-breaker) | 04a revoke cascade | Hard gate: `ledger_consistency_failure_rate > 1.0%` per 24h → halt Stream 3 D3.2 autonomy. Sustained > 0.5% over 14 days → ADR-2 revisitation. |
| **Submission-packet factuality failure (GR-13, KPI #7 below 0.999)** | 04a | KPI #7 below threshold → halt Stream 3 D3.2 autonomy; coordinator-mandatory mode; alert sink: PagerDuty service + compliance audit log row. |
| **Audit-trail tamper detection (R7.13, Adversarial A8)** | 04a | Hash-chain daily validation; chain break → GR-7 alert + ADR-2 revisitation; off-DB witness commitment (per Phase 10 A8 proposed answer) for high-value transactions. |
| **R7.18 — Revoke stuck at 02:14 Sunday with no on-call** | 04a | 24/7 on-call rotation (PB-On-Call); R7.18 sweep at shift change; coordinator-mandatory mode on revoke-stuck volume > 1%/24h. |
| **Champion attrition before Phase 3 advancement** (Kim TBC; touched in Marcus pushback P3) | Cross-capability deployment | Kim walkthrough today (per `06-client-feedback.md` P3 discharge); formal PC-3 + PC-5 sign-off recorded; backup-champion identified during Phase 1 (operational, not in spec). |

### 2.4 Compliance risk

| Compliance vector | Mitigation |
|---|---|
| **GR-1 — Agent never contacts hospital directly (D1.3 + D3.2)** | Audit log `sent_by` field on every clarification + submission; `sent_by = agent` triggers GR-1 alert; weekly compliance review by Linda. |
| **Per-state license check (Phase 10 R4)** | `nurse.licensed_states` validation in 04a §4 invariant; `license_expires_at_for_state[hospital.state] > now() + 7 days` gate; nightly licensure-DB sync. |
| **Protected-class preferences not applied** (per `05-agent-purpose.md` §3b Capability 2 edge case) | Pattern matcher in classification flags age/gender/protected-class references; routes T4 with constraint-violation flag; agent never applies regardless of confidence; compliance audit log. |
| **Audit-trail immutability** | Hash-chained event log; daily validation (§2.3); cryptographic signature on commit events. |
| **Data retention + PII handling** | Out-of-scope for this validation plan (per `02-intake-scope.md` — engagement scope explicit on this point); to be defined Phase 2 with MedFlex security/legal. |

---

## 3. Four explicitly-named risk vectors (pack requirement)

### 3.1 Portal rate limits

**Risk:** Hospital portals impose undocumented rate limits; high parallel-submission volume triggers throttling or temporary blocking; sender-reputation penalties accrue.

**Mitigation:**
- Per-portal `requests_per_minute_cap` config (default 30; PENDING_CALIBRATION per portal, set during PB-6).
- Per-portal request-history monitor; submissions queued and throttled at 80% of observed limit.
- Rate-limit-exhausted detection: if portal returns 429 (or hospital-specific equivalent), exponential backoff; ALL submissions to that portal go ALHO until rate observable.
- Weekly rate-limit telemetry review (operational); per-portal rate cap revised per observed behaviour.
- Failover: if portal unavailable > 30 min, route submissions for that hospital to email channel (per `06-client-feedback.md` Phase 1.5 PB-Phase1.5 — coordinator-sends architecture provides email-only fallback path).

### 3.2 Regulatory drift

**Risk:** State licensure rules or federal nurse-staffing regulations change; agent submits candidates who were valid at submission time but become invalid mid-engagement (the spec's per-state license check is point-in-time).

**Mitigation:**
- Nightly licensure-DB sync against state regulatory data sources (currently manual per BRIEF; Phase 2 automation).
- 7-day forward-window check on licensure expiry (per 04a invariant): submission requires `license_expires_at_for_state[hospital.state] > now() + 7 days`; tighter than the operational expiry to absorb regulatory lag.
- Quarterly regulatory-change review (operational; owned by Linda); spec updates flow through ADR or assumption-log addendum.
- Marrakesh Treaty / federal ADA changes propagate via the same review cadence; affects accessibility-priority hold logic in any future ADR.
- Compliance violation discovery → halt fleet immediately; coordinator-mandatory mode until cleared.

### 3.3 Model accuracy drift

**Risk:** LLM classifier accuracy degrades over time as ticket-language patterns shift, hospital communication conventions evolve, or model providers update underlying weights without notice.

**Mitigation:**
- Continuous accuracy regression: every prompt revision OR every quarter (whichever sooner), the 500-row eval set re-runs; drop below baseline → automatic rollback to last passing prompt.
- Weekly Brier-score check on per-field confidence; calibration drift > 0.1 → re-tune confidence thresholds (Assumption A1.1 update).
- Tier-distribution monitor: if T3/T4 share spikes > 30% in any week, prompt-engineering review triggered (model has drifted toward lower-confidence outputs).
- Model-provider notification subscription: vendor weight-updates flagged within 24h; eval-set re-run within 7 days.
- Per-capability shadow-deploy harness: new prompt versions run in shadow mode against last 1000 production tickets before production cutover.

### 3.4 Single-points-of-failure (SPOF)

**Risk:** Any single system whose outage halts the capability fleet — including the LLM provider, the credentialing DB, the submission-channel infrastructure, the on-call rotation, and the human champion (Kim).

**Mitigation:**

| SPOF | Mitigation |
|---|---|
| **LLM provider** | Multi-provider abstraction in prompt-registry; primary + failover provider; latency-SLA fallback to failover; cold-start time < 5 min. |
| **Credentialing DB** | Read-replica for queries (04a + 04b read operations); writes go to primary; outage > 10 min → coordinator-mandatory mode (no automated submission). |
| **Submission-channel (SMTP + portal)** | Per-hospital `preferred_channel` with fallback channel; ADR-3 sequential-with-optimistic-batching as architectural fallback per `03-architecture.md` ADR-3. |
| **`submission_factuality_ledger` DB** | Ledger DB is itself a SPOF (per EC-Factuality-1 in 04a); read-write must be transactional with submission send; outage halts Stream 3 D3.2 autonomy fleet-wide (this is by design — the ledger IS the audit substrate, not a logging convenience). |
| **24/7 on-call rotation** (R7.18 mitigation) | Two-tier on-call (primary + secondary); page-out drill once per quarter; written runbook for revoke-stuck + ledger-inconsistency + factuality-fail scenarios. |
| **Human champion (Kim TBC)** | Backup-champion identified during Phase 1 (operational; not a spec change). Per `06-client-feedback.md` P3 commitment, Kim walkthrough Friday close + formal PC-3 + PC-5 sign-off; backup-champion identification is a Phase 1 deliverable. |

---

## 4. Deferred validation work (post-pushback)

Per Marcus pushback (`06-client-feedback.md`), two spec revisions landed in this submission that have **not yet been re-validated** against the gate2 Closed Build Loop (CBL). The original CBL (`output/submit/closed-build-loop-results.md`, 18 KB) was performed against the pre-pushback spec; the revised D3 includes (a) Phase 1.5 Component-1 ranking pilot and (b) ADR-1 revisitation threshold realigned with ADR-3 coexistence table.

**CBL re-run required against revised D3.** Original CBL remains valid for unchanged sections (D2 intake/scope, V×V Streams 1/3 pre-Phase-1.5, ADR-2 atomic revoke cascade); re-validation needed for:

| Section | What re-validation must cover |
|---|---|
| **Phase 1.5 build path** | D2.5 ranking on bounded cohort + coordinator-sends architecture (new in revised D3); operational pre-requisites PB-Phase1.5-1 / -2 / -3 buildable in 6 weeks. |
| **ADR-1 revisitation trigger** | New threshold language ("<50% green-list" replacing "≥80% non-green-list") aligned with ADR-3 coexistence table; revisitation flow under the new threshold produces the same ADR-3-promotion artefact. |
| **PB-3 multi-week rolling Legal review** | New cadence (replacing 3-day pre-build batch); per-hospital `parallel_enabled` flip-on-clear logic does not introduce ledger-consistency regressions. |
| **Kim engagement discharge** | PC-3 + PC-5 sign-off recorded (operational; not architectural — but ADR-2's atomic revoke cascade load-bearing on PC-3 means the sign-off itself is validation substrate). |

**Scheduling:** CBL re-run scheduled for Monday post-Friday-submission (operational follow-through; tracked in D8 reflection as a real follow-up commitment). The validation gap is explicitly named here, not silently elided — substrate-honest framing per the discipline applied to the pushback work itself.

---

## 5. Deployment readiness checklist (operational)

Pre-Phase-1 deploy gates:

- [ ] Kim walkthrough complete + formal PC-3 + PC-5 sign-off recorded (commit per `06-client-feedback.md` P3 — by Friday close 2026-05-13).
- [ ] Marcus + Legal PC-1 sign-off recorded (per ADR-1 + ADR-2 + ADR-3 decision-owner table).
- [ ] PB-1 through PB-6 status confirmed (per `03-architecture.md` ADR consequences); any AMBER blocker triggers deploy hold.
- [ ] CBL re-run against revised D3 — at least Phase 1.5 path + ADR-1 threshold flow (per §4 above).
- [ ] Backup-champion identification for Kim's role (Phase 1 operational deliverable; not deploy-blocking but Phase 3 advancement-blocking).
- [ ] 24/7 on-call rotation staffed + drill completed (PB-On-Call; R7.18 mitigation).
- [ ] Compliance audit log + GR-1/GR-7/GR-13 alert sinks wired (compliance review by Linda).
- [ ] Submission-factuality ledger schema deployed + populated against synthetic test fixtures.

Phase-1.5 pilot deploy gates (separable from Phase 1):

- [ ] Bounded specialty/hospital cohort identified Day 0 (PB-Phase1.5-1).
- [ ] Component-1 (KPI #6) measurement instrumentation in place by Week 1 (PB-Phase1.5-2).
- [ ] D2.5 ranking model trained on historical match data with cohort-restricted validation (PB-Phase1.5-3).
- [ ] Coordinator-sends UX confirmed acceptable with senior coord champion (Kim or backup).

Phase-2 advancement gates (carried forward from gate2 substrate):

- [ ] PB-3 rolling Legal review has cleared ≥ 50% green-list per ADR-3 coexistence table; if < 50%, ADR-3 stays default per ADR-1 revisitation condition.
- [ ] KPI #6 + KPI #7 + ledger-consistency thresholds all green for 14 consecutive days at Phase-2 readiness review.
- [ ] PC-1 + PC-3 + PC-5 sign-offs all CONFIRMED.

---

## 6. Cross-references

- **Capability spec validation hooks:** `04a-capability-spec-parallel-submit.md` §10 (KPI #7 + ledger consistency + revoke success + audit-trail integrity + revoke-tone audit); `04b-capability-spec-classification.md` §10 (accuracy regression + per-field confidence calibration + tier-boundary stability + compliance audit).
- **Risk register substrate:** `02-intake-scope.md` §"Risks (top 7 from R7.x)"; gate2 sealed bundle `assumptions-log.md` for full register including R7.7 / R7.13 / R7.18 / Adversarial A8 / A9 / B-1 (Hartwood factuality pattern).
- **Architecture decisions validated:** `03-architecture.md` §ADRs — ADR-1 / ADR-2 / ADR-3, each with revisitation conditions explicitly defined.
- **Pushback-driven spec changes:** `06-client-feedback.md` — Phase 1.5 + ADR-1 threshold realignment + Kim engagement discharge.
- **Self-spec build-loop diagnosis substrate:** `09-self-spec-reflection.md` — capability-level spec gaps identified during D9 build simulation (esp. deferred-calibration anti-pattern, machine-checkability of §5 boundaries).
