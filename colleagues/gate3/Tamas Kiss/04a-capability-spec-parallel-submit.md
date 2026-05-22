# Deliverable 4a — Capability Spec: Multi-hospital Parallel Submission + Atomic Revoke Cascade (D3.2, D3.3, D3.4)

**Author:** Tamas Kiss
**Engagement:** MedFlex agentic transformation  
**Date:** 2026-05-13
**Gate:** Gate 3 — Final submission
**Substrate origin:** lifted from `output/submit/05-agent-purpose.md` §3b Capability 4 + Capability 5 (combined; cascade is the safety boundary of parallel submission per ADR-2). Cross-references `adr.md` ADR-1, ADR-2, ADR-3 (verbatim in `03-architecture.md`).
**Archetype:** D3.2 = Fully Agentic (FA, T1 within boundaries); D3.3 + D3.4 = Agent-Led + Human Oversight (ALHO, T2 default with hard ledger-consistency gate)
**Glossary:** see `04-shared-glossary.md` for canonical entity definitions

---

## 1. Purpose

Send each shortlisted candidate to applicable hospital `shift_request`s in parallel; track each as a `submission` row through an 11-state machine; detect the first-confirm event from any hospital; atomically revoke all parallel submissions for the same nurse; verify ledger consistency; commit the (nurse, hospital, shift) assignment with audit trail.

Two architectural safeguards are non-negotiable:

1. **Submission-packet factuality check** (per Phase 10 R1 / Hartwood B-1 mitigation): every submission packet's factual claims (`nurse.full_name`, `required_certifications`, `start_at`, `end_at`, `availability windows`, `hospital`, `unit`, `count`) are slot-by-slot exact-matched against source-of-record **before** SMTP/portal send. Any mismatch halts the submission and routes T4.

2. **MSA-state gating** (per ADR-1 / Phase 10 Conflict-2): per-hospital `exclusivity_window_minutes` defaulted to BLOCK; parallel submission enabled only on `hospital.msa_state = "green"` until Legal sign-off in writing. Yellow/red/unreviewed hospitals route through Capability sequential-with-optimistic-batching (ADR-3 standby; see `03-architecture.md`).

## 2. Inputs

- An approved `candidate_queue` from Capability 3 (cross-store retrieval + ranking).
- The corresponding `classification` record (per glossary; produced by Capability 1).
- Open `shift_request` set for hospitals reachable by the candidate.
- Per-hospital `msa_state` ENUM (per glossary §`hospital`).
- `max_parallel_submissions_per_nurse` config (default 5; PENDING_CALIBRATION).

## 3. Outputs

- One `submission` row per (candidate, applicable_open_request) pair; state evolves through the 11-state machine.
- One row per submission slot in `submission_factuality_ledger` (per glossary).
- On first-confirm: revoke cascade across siblings; consistency-gated `assignment.state = COMMITTED` OR `INCONSISTENT_FROZEN` with coordinator escalation.
- Per-submission audit-trail event (hash-chained; immutable).
- Nurse holding-signal SMS at submission time (per Phase 10 C-CA1).

## 4. Behaviour rules

### 4.1 Parallel submission (D3.2 — FA, T1)

```
INVARIANT: candidate_queue approved by Capability 3 (D2.5 ranking ALHO);
           classification.confidence ≥ 0.85;
           candidate.compliance_status = "verified";
           candidate.license_expires_at_for_state[hospital.state] > now() + 7 days

FOR each candidate in approved candidate_queue:
   applicable_open_requests = open_requests.filter(
      required_certs ⊆ candidate.certs,
      candidate.availability covers request.window,
      hospital_id NOT IN candidate.block_list_for_nurse,
      // Per ADR-1 / Phase 10 Conflict-2 — per-hospital MSA gating:
      (hospital.msa_state = "green") OR
        (hospital.msa_state IN {"yellow", "red"} AND parallel_count_for_nurse_in_window = 0)
   )

   IF count(applicable_open_requests) > max_parallel_submissions_per_nurse
   THEN
      hold; route to coordinator with rationale (B5 breakpoint)
      RETURN
   
   FOR each request in applicable_open_requests:
      submission_packet = compose_submission(candidate, request)
      
      // ─── Per Phase 10 R1 / Hartwood B-1 — factuality check BEFORE send ───
      factuality_results = check_packet_factuality(submission_packet, candidate, request)
        // Slot-by-slot exact match against source-of-record:
        //   nurse.full_name           → credentialing_db.nurses[candidate.id].full_name
        //   required_certifications   → credentialing_db.nurses[candidate.id].credentials
        //   start_at, end_at          → classification.start_at, classification.end_at
        //   availability_window       → availability_db.windows[candidate.id]
        //   hospital, unit, count     → classification fields
        // Write one row per slot to submission_factuality_ledger
      
      IF any factuality_results.exact_match = false
      THEN
         GR-13 constraint violation → tier = T4
         submission.state = FACTUALITY_CHECK_PENDING  (halt)
         alert coordinator with failing slot(s) surfaced
         DO NOT call SMTP / portal
         CONTINUE next request
      ELSE
         send via request.hospital.preferred_channel
         submission.state = SUBMITTED
         log to audit trail
         
         // Per Phase 10 C-CA1 — nurse holding signal at submission time:
         send_holding_signal_sms(
            nurse_id = candidate.id,
            submission_id = submission.id,
            channel = candidate.preferred_channel
         )
         write nurse_submission_notification row
```

### 4.2 First-confirm detection (D3.3 — ALHO, T2)

```
ON inbound_event_from_hospital (email/portal event):
   confirm_evidence_strength = LLM_classify(
       event,
       prompt = "Classify as confirm | ack | reject; return confidence"
   )
   
   IF event.intent = "confirm" AND confirm_evidence_strength ≥ 0.85
   THEN
      submission.state = CONFIRMED
      submission.confirmed_at = now()
      trigger D3.4 (revoke cascade)
   
   ELSE IF event.intent = "confirm" AND confirm_evidence_strength < 0.85
   THEN
      tier = T3
      hold for coordinator review (B8 breakpoint)
      // Do NOT proceed to revoke cascade until coordinator confirms intent
```

**Must not** (D3.3):
- Treat hospital-portal acknowledgements (`received` ≠ `confirmed`) as confirmation events.
- Trigger the revoke cascade without a `confirm_evidence_strength ≥ 0.85`.

### 4.3 Atomic revoke cascade with ledger-consistency gate (D3.4 — ALHO, T2)

```
ON submission.state = CONFIRMED (from D3.3):
   sibling_submissions = submission.query(
       nurse_id = this.nurse_id,
       shift_request_id ≠ this.shift_request_id,
       state ∈ {SUBMITTED, ACKED_BY_HOSPITAL, CONFIRMED}
   )
   
   // ─── Simultaneous-confirm check (escalation to D3.5a tie-break) ───
   simultaneous_confirms = sibling_submissions.filter(
       state = CONFIRMED,
       confirmed_at within ±30s of this.confirmed_at
   )
   
   IF simultaneous_confirms.exists
   THEN
      trigger D3.5a (surface tie-break panel; pause cascade)
      tier = T4 for D3.5b (Human-Only decision)
      RETURN
   
   // ─── Standard cascade ───
   FOR each sibling in sibling_submissions:
      send revoke message via sibling.hospital.preferred_channel
      sibling.state = REVOKE_PENDING
   
   wait_for_revoke_acks(timeout = 60s, retries = 2)
   
   // ─── Ledger-consistency check (HARD GATE — per ADR-2) ───
   IF all sibling_submissions.state ∈ {REVOKED, COMMITTED_ELSEWHERE}
   THEN
      assignment.state = COMMITTED
      emit immutable audit-trail event (hash-chained)
   ELSE
      assignment.state = INCONSISTENT_FROZEN
      freeze nurse state (D3.4 separability: agent owns freeze; human owns recovery)
      tier = T4 (coordinator recovery via dashboard)
```

**Must not** (D3.4):
- Complete a revoke cycle unless ledger-consistency check (`all parallel rows ∈ {REVOKED, COMMITTED_ELSEWHERE}`) passes.
- On consistency-check failure, mutate the nurse's downstream state — freeze and alert coordinator. (Safety boundary per A3 L118 / R3 / ADR-2.)

## 5. Hard agent action boundaries (consolidated)

**Must not** (D3.2):
- Submit a candidate to a hospital flagged `block_list_for_nurse = true` for that nurse.
- Exceed `max_parallel_submissions_per_nurse` (default 5); beyond that → hold for coordinator review.
- Send SMTP/portal traffic if `factuality_results` carries any `exact_match = false`. (GR-13 hard rule.)
- Run parallel submission on a hospital with `msa_state ∈ {"yellow", "red", "unreviewed"}` while another active parallel submission exists for the same nurse (per Conflict-2 USER-CONFIRMED).

**Must not** (cascade-level):
- Skip the `submission_factuality_ledger` write — the ledger is the audit substrate, not a logging convenience.
- Auto-resolve `INCONSISTENT_FROZEN` — coordinator-only recovery.

## 6. Bootstrap dependencies

- **PB-1** — submission state machine (11 states) implemented + tested before Pilot Week 1 launch.
- **PB-3** — MSA review for top-20 hospitals **pulled forward** from Pilot Week 1 to Day -3 of Phase-1 build (per ADR-1). Without this, every hospital is `unreviewed` → parallel-blocked → ROI collapses; the spec is non-operational. *Note: 2026-05-13 Marcus pushback memo extended PB-3 from 3-day pre-build batch to multi-week rolling Legal review; see `03-architecture.md` Phase 1.5 section and `06-client-feedback.md`.*
- **PB-6** — submission-channel credentials (SMTP, hospital portal API tokens) provisioned and tested.
- **PB-Factuality-1** — `submission_factuality_ledger` schema implemented + slot-extractor library deployed before any submission can pass the factuality gate.

## 7. Edge cases

| ID | Edge case | Behaviour | Confidence |
|---|---|---|---|
| EC-3.2.1 | **Hospital portal returns 5xx** | Retry once after 30s; if still failing, route to coordinator (B5 breakpoint). Submission remains in `DRAFT`; not counted toward `parallel_count_for_nurse_in_window`. | HIGH (substrate-confirmed) |
| EC-3.2.2 | **Email-channel delivery delayed > 5 min** (no SMTP ack) | Re-send once; alert coordinator if still pending — sender-reputation issue. Submission stays `DRAFT` until acked. | HIGH (substrate-confirmed; sender-reputation pattern) |
| EC-3.2.3 | **Candidate's `block_list_for_nurse = true` for target hospital** | Hard skip in `applicable_open_requests` filter; do not submit; surface in ranking step (Capability 3 receives the skip-list signal). | HIGH (substrate-confirmed) |
| EC-3.4.1 | **One sibling revoke fails after 2 retries** (`REVOKE_STUCK`) | Freeze the nurse; coordinator must resolve manually via dashboard. `assignment.state = INCONSISTENT_FROZEN`. R7.18 risk profile (alarm at 02:14 Sunday with no on-call) addressed by 24/7 on-call rotation per `07-validation-plan.md`. | HIGH (substrate-confirmed; R7.18 named) |
| EC-3.4.2 | **Hospital that revoke was sent to responds with "we already had your nurse"** (already-committed-elsewhere implicit confirmation race) | Mark sibling `COMMITTED_ELSEWHERE`; consistency check still passes. Assignment commits per primary confirm. | HIGH (substrate-confirmed) |
| EC-3.4.3 | **Network partition during cascade** | Cascade resumes on reconnect from last persisted state; idempotency on revoke retries via `revoke_idempotency_key`. | MED (idempotency design implied; explicit key naming is Phase 1 instrumentation) |
| EC-MSA-1 | **Hospital MSA state flips green→yellow mid-flight** (Legal revises classification while parallel submissions are pending) | New submissions blocked immediately; in-flight submissions allowed to complete the active confirm/revoke cycle; flagged in audit trail with `msa_state_at_submit` field. | MED (operationally implied; not explicit in substrate) |
| EC-Factuality-1 | **`submission_factuality_ledger` write fails** (DB outage at factuality-check step) | Submission halts; do not send; treat as factuality_results.exact_match = false. Alert ops; do NOT proceed without ledger write — the ledger IS the audit substrate. | HIGH (Phase 10 R1 reasoning preserved) |

## 8. Worked example (concrete test case)

```
INPUT candidate_queue (from Capability 3, top-3 ranked):
  candidate.id = N_222
  candidate.full_name = "Maria Sanchez"
  candidate.certs = ["RN", "CCRN", "BLS", "ACLS"]
  candidate.licensed_states = ["TX", "CA"]
  candidate.block_list_for_nurse = [H_404]

CLASSIFICATION (from Capability 1):
  shift_type = "RN", unit = "ICU", required_certifications = ["CCRN", "RN"]
  start_at = 2026-05-19T19:00:00-05:00, end_at = 2026-05-20T07:00:00-05:00, count = 1

OPEN SHIFT_REQUESTS for matching classification:
  R_701 (hospital H_101, msa_state = "green",  exclusivity_window_minutes = 0)
  R_702 (hospital H_202, msa_state = "green",  exclusivity_window_minutes = 0)
  R_703 (hospital H_303, msa_state = "yellow", exclusivity_window_minutes = 60)
  R_704 (hospital H_404, msa_state = "green",  exclusivity_window_minutes = 0)

EXPECTED applicable_open_requests after filtering:
  R_701, R_702 (R_703 yellow + 0 in-flight for nurse = first one only; R_704 blocked by block_list)

EXPECTED parallel-submission sequence:
  1. For R_701:
     - submission_packet composed for H_101
     - factuality_results: 8/8 slots exact_match=true
     - send via H_101 preferred_channel; submission.state = SUBMITTED
     - SMS holding signal to N_222
     - ledger rows written
  2. For R_702:
     - submission_packet composed for H_202
     - factuality_results: 8/8 slots exact_match=true
     - send via H_202 preferred_channel; submission.state = SUBMITTED
     - (no second SMS; one holding signal per candidate per window)

LATER — H_101 returns confirm event with confirm_evidence_strength = 0.92:
  - submission_701.state = CONFIRMED
  - cascade triggered:
      sibling = submission_702 (state = SUBMITTED, ±30s check fails — not simultaneous)
      send revoke to H_202 via preferred_channel
      submission_702.state = REVOKE_PENDING
  - wait_for_revoke_acks: H_202 acks revoke at +12s; submission_702.state = REVOKED
  - ledger-consistency check: all siblings ∈ {REVOKED} ✓
  - assignment_X.state = COMMITTED; audit-trail event emitted
```

## 9. Assumptions (with confidence tags)

| A# | Assumption | Confidence | Revisit trigger |
|---|---|---|---|
| A3.1 | Hospital portals support a synchronous-write submission API with predictable HTTP semantics. | MED | Aaron (IT) confirmation per discovery follow-up; per-portal documentation review at PB-6. |
| A3.2 | Email channels carry a deliverability signal within 5 min (SMTP ACK / bounce). | MED | Sender-reputation calibration at Pilot Week 1. |
| A3.3 | `max_parallel_submissions_per_nurse = 5` is the operationally correct cap (calibrated against coordinator current practice; A3 L107). | LOW | PENDING_CALIBRATION — Phase 1 instruments and adjusts. |
| A3.4 | Hospital-portal acknowledgement events are distinguishable from confirmation events at the data layer (`received` field vs `confirmed` field). | MED | Aaron confirmation; if hospital portal conflates the two, D3.3 logic must escalate ambiguous events to T3. |
| A3.5 | `hospital_silent_timeout = 6h` median is correct for "no response" branch — relevant to ADR-3 standby, not primary in this spec. | MED | Calibration in Phase 1. |
| A3.6 | `revoke_idempotency_key = hash(submission_id, revoke_event_id)` is collision-safe for the operational volume (~240k tickets/year × ~3 parallel submissions ≈ 720k revoke events/year). | HIGH | If a collision is observed, the idempotency scheme is wrong (cryptographic hash makes collision practically zero). |
| A3.7 | The 11-state machine accommodates both ADR-1 (parallel) and ADR-3 (sequential-with-optimistic-batching) via per-hospital `parallel_enabled` boolean toggle — no state-machine rework required across modes. | HIGH | Per ADR-3 Consequences (verbatim); substrate-confirmed. |

## 10. Validation & test plan (Phase 1 instrumentation)

- **Submission-packet factuality** — KPI #7 ≥ 0.999 (per submission_factuality_ledger). Slot-level exact-match rate. Any week below 0.999 → halt Stream 3 D3.2 autonomy; coordinator-mandatory mode until root-caused.
- **Ledger-consistency rate** — track `ledger_consistency_failure_rate` per 24h. ET-9 circuit-breaker fires at >1.0% per 24h → halt Stream 3 D3.2 autonomy. Sustained >0.5% over 14 days → ADR-2 revisitation (re-architect to ADR-3-as-default).
- **Revoke success rate per channel** — track per-channel revoke success at 95% threshold per Adversarial A9; below threshold on any tier → suspend FA on that tier; route ALHO until channel hardened.
- **Audit-trail integrity** — hash-chain validation runs daily; any break in chain triggers GR-7 (audit-trail-tamper-detection) alert per R7.13.
- **Hospital-trust signal (revoke-tone audit per C-CA5)** — sentiment classifier on inbound hospital responses; negative drift for 4 consecutive weeks → ADR-1 revisitation per `03-architecture.md`.

## 11. Cross-references

- **Upstream capability:** `04b-capability-spec-classification.md` (Capability 1, D1.1 + D1.3) — produces the classification record this spec consumes.
- **Shared entities:** `04-shared-glossary.md`.
- **Architectural decisions:** `03-architecture.md` §"ADRs" — ADR-1 (parallel + per-hospital MSA gating), ADR-2 (atomic revoke cascade as safety boundary), ADR-3 (sequential-with-optimistic-batching standby). All three have alternatives + consequences + revisitation conditions.
- **Phase 1.5 pilot reference:** `03-architecture.md` §"Phase 1.5" notes that Phase 1.5 uses D2.5 ranking + coordinator-sends (NOT this capability) — Phase 1.5 explicitly bypasses parallel submission to avoid PB-3 MSA dependency. This spec's autonomy schedule begins Phase 2.
- **Validation plan:** `07-validation-plan.md` — full validation framework including the KPI #7 threshold, ET-9 circuit-breaker, revoke-tone audit cadence.
