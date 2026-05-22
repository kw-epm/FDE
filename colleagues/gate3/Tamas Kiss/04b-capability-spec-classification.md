# Deliverable 4b — Capability Spec: Free-text Intake Classification (D1.1, D1.3)

**Author:** Tamas Kiss
**Engagement:** MedFlex agentic transformation  
**Date:** 2026-05-13
**Gate:** Gate 3 — Final submission
**Substrate origin:** lifted from `output/submit/05-agent-purpose.md` §3b Capability 1 (D1.1 + D1.3 covered)
**Archetype:** Agent-Led + Human Oversight (ALHO) — coordinator approves/edits low-confidence drafts; agent never sends to hospital directly
**Glossary:** see `04-shared-glossary.md` for canonical entity definitions

---

## 1. Purpose

Convert a hospital's free-text shift request into a complete structured `classification` record ready for downstream matching and submission. The classification record carries six required structured fields plus per-field and aggregate confidences. Coordinator approves below threshold; agent never auto-sends clarifications to hospital.

## 2. Inputs

- One `ticket` from ServiceNow (per glossary §`ticket`).
- LLM classifier prompt (loaded from prompt-registry; see §6 Bootstrap).
- `credential_taxonomy` snapshot (per glossary §`credential_taxonomy`; refreshed by Bootstrap Day 3).
- 500-row eval set (historical ticket classifications, validated; used for accuracy regression at deploy).

## 3. Outputs

A `classification` record (per glossary §`classification`) attached to the ticket, with an explicit tier assignment per the autonomy matrix:

- **Tier T1** — agent executes; coordinator notified non-blocking.
- **Tier T2 (default for ALHO archetype above 0.85)** — agent finalises classification; 1-click coordinator ack queued.
- **Tier T3 (0.70 ≤ confidence < 0.85)** — agent drafts; coordinator approves/edits before downstream use.
- **Tier T4 (confidence < 0.70)** — coordinator mandatory: agent drafts a clarification text addressed to the hospital; **the coordinator (not the agent) sends it** via existing email channel.

## 4. Behaviour rules

```
INVARIANT: ticket.body extracted; LLM classifier prompt loaded;
           ticket.submission_channel ∈ {email, portal, phone_transcribed}

classification_record = extract_fields(
    text = ticket.body,
    schema = credential_taxonomy
)

classification_confidence = mean(per_field_confidences)

IF classification_confidence ≥ 0.85
   AND required_fields_complete = true
   AND no boundary violation
THEN
   tier = T2 (D1.1 ALHO; agent executes + coordinator 1-click ack)
   notify coordinator (non-blocking)
   downstream_dispatch(classification_record)

ELSE IF 0.70 ≤ classification_confidence < 0.85
THEN
   tier = T3
   hold for coordinator review in HITL queue
   coordinator reviews: approve | edit | reject
   on approve  → downstream_dispatch
   on edit     → coordinator-edited classification → downstream_dispatch
   on reject   → ticket returns to coordinator-clarification queue

ELSE IF classification_confidence < 0.70
THEN
   tier = T4
   route to coordinator-mandatory queue (NO auto-execute)
   agent drafts clarification text addressed to hospital
   coordinator sends the clarification via existing email channel
   on coordinator-receives-clarification → re-classify
```

## 5. Hard agent action boundaries

**Must not** (D1.1):
- Auto-finalise a classification with `confidence < 0.85` (routes to coordinator review per §4).
- Send clarifying messages directly to the hospital — drafts only; coordinator sends. (Constraint #1 / A4-F1.)

**Must not** (D1.3):
- Auto-clarify by contacting hospital booking staff. (Constraint #1 / A4-F1.)
- Drop a `confidence < 0.70` ticket out of the queue — escalates to coordinator-clarification queue, never silently discarded.

## 6. Bootstrap dependencies

- **PB-2** — credentialing DB snapshot pulled for `credential_taxonomy` and `cert taxonomy`; eval set of 500 historical tickets prepared. Without this, classifier prompt has no controlled vocab to anchor against.
- **DG-2** — credential taxonomy authoritative source confirmed with MedFlex compliance owner (Linda); locked snapshot in versioned prompt registry.
- **DG-3** — the 6 required structured fields enumerated (this spec uses `shift_type`, `unit`, `required_certifications`, `start_at`, `end_at`, `count`); confirmed during Thursday discovery.

## 7. Edge cases

Each edge case below is a confirmed substrate-derived edge case from gate2 Capability 1 plus marked confidence. Builder MUST handle all four:

| ID | Edge case | Behaviour | Confidence |
|---|---|---|---|
| EC-1.1 | **Body in two languages** (Spanish in TX/CA borders) | Detect language; if non-English, set `tier = T3` and flag for bilingual coordinator if available, or human translation otherwise. | HIGH (substrate-confirmed; TX/CA discovery datapoint) |
| EC-1.2 | **Body references hospital department by acronym not in taxonomy** | `classification_confidence` falls below threshold by virtue of the unmatched token; routes T3; surface the acronym in coordinator dashboard for clarification. | HIGH (substrate-confirmed) |
| EC-1.3 | **Ticket is a modification of an earlier ticket** ("scratch yesterday's RN request, we need ICU now") | Detect linked ticket via LLM-classified intent; route the modification as a new shift_request linked via `previous_shift_request_id`; do NOT in-place mutate prior classification. | MED (substrate names the pattern; the data-model addition is design-time) |
| EC-1.4 | **Phone-transcribed channel with low transcription quality** (substrate-derived from channel ENUM) | Treat `submission_channel = phone_transcribed` as automatically lowering all per-field confidences by a calibration multiplier (PENDING_CALIBRATION — Phase 1 instrumented). | LOW (PENDING_CALIBRATION) |

## 8. Worked example (concrete test case)

```
INPUT ticket.body:
"Need 2 RNs for Tuesday night, ICU, must have CCRN, prefer
 someone we've used before. Tues 7pm-7am. Call 555-1234 if questions."

EXPECTED OUTPUT classification:
  shift_type                          = "RN"
  unit                                = "ICU"
  required_certifications             = ["CCRN", "RN"]
  start_at                            = (next Tuesday) 19:00 local hospital TZ
  end_at                              = (following Wednesday) 07:00
  hospital_preferences_referenced     = ["prior_history"]   // signals D1.2 lookup (Capability 2 territory)
  count                               = 2
  per_field_confidence                = [0.95, 0.95, 0.92, 0.88, 0.88, 0.95]
  classification_confidence           = 0.92
  
EXPECTED TIER: T2
  (confidence ≥ 0.85; archetype ALHO → notify coordinator + 1-click ack)
EXPECTED ESCALATION FLAG: false (no clarification needed)
EXPECTED DOWNSTREAM: Capability 2 (preference lookup), Capability 3 (cross-store retrieval + ranking)
```

## 9. Assumptions (with confidence tags)

These assumptions are inherited from the gate2 `assumptions-log.md` and re-asserted here to make the spec buildable. The builder may flag any disagreement.

| A# | Assumption | Confidence | Revisit trigger |
|---|---|---|---|
| A1.1 | The 0.85 / 0.70 confidence thresholds are calibrated against the 500-row eval set at deploy time. The thresholds named in §4 are starting values; Phase 1 instruments the recalibration. | MED | First 200 production tickets; mismatch rate vs eval-set baseline. |
| A1.2 | Per-field confidence is independent of other-field confidence (allows arithmetic-mean aggregation). | MED | Cross-field correlation analysis post-200-tickets; if confidences correlate >0.6, re-architect aggregation. |
| A1.3 | The `credential_taxonomy` snapshot is sufficient for 95%+ of incoming tickets without external NER. | MED | If <90% of incoming tickets match taxonomy in Phase 1, add prompt-engineering pass on residual tokens. |
| A1.4 | Phone-transcribed tickets carry a stable per-channel confidence penalty (modelled as a multiplier; PENDING_CALIBRATION). | LOW | Phase 1 instrumented; calibrate against transcription-vs-text-channel accuracy delta. |
| A1.5 | Coordinator's "approve/edit/reject" review takes <60s median; the HITL queue depth stays bounded by classification volume. | MED | Queue-depth monitoring; SLO breach if median review > 90s or queue ages > 30 min. |

## 10. Validation & test plan (Phase 1 instrumentation)

- **Accuracy regression** — re-run 500-row eval set on every prompt revision; classification accuracy must not drop below baseline (TBD — established during Day 3 prompt-tuning).
- **Per-field confidence calibration** — log every per-field confidence + the eventual coordinator approve/edit/reject signal; compute Brier score weekly.
- **Tier-boundary stability** — monitor distribution of tickets across T2/T3/T4; if T3 or T4 share spikes (>30% of any week), re-prompt or re-calibrate threshold.
- **Compliance audit** — D1.3 must NEVER send clarification directly; log every clarification-text composition with `sent_by = coordinator | agent` field; any `sent_by = agent` row triggers GR-1 violation alert.

## 11. Cross-references

- **Downstream capability:** see `04a-capability-spec-parallel-submit.md` for what happens to a T2 classification record (matching → ranking → submission).
- **Shared entities:** `04-shared-glossary.md`.
- **Architecture context:** `03-architecture.md` §"Agent decision points where contextual reasoning beats rules" (D1.1 + D1.3 rows in delegation matrix).
- **D9 self-spec build:** this spec is the target of the D9 30-minute Claude Code build under exam conditions; diagnosis recorded in `09-self-spec-reflection.md`.
