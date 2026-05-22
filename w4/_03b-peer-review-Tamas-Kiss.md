# Deliverable #3b — Peer Review: Tamas Kiss

**Files reviewed:** `04-shared-glossary.md`, `04a-capability-spec-parallel-submit.md`, `04b-capability-spec-classification.md`
**Reviewer:** Krzysztof Wilniewczyc
**Date:** 2026-05-19

## Verdict

Not buildable from this package alone. The thinking behind the design is strong. A builder who has only these three files cannot start without inventing too many missing pieces.

## Triage

| Bucket | Count | What |
|---|---|---|
| Blocker | 3 | Spec depends on files not in the package; 04b has no LLM contract; submission engine has no integration contracts |
| Concern | 2 | Confidence is a plain arithmetic mean of six fields; T2 tier behaviour contradicts the ALHO archetype |
| Acceptable difference | — | Shared glossary as a separate file; 11-state machine covers ADR-1 and ADR-3 via one boolean |
| Missing | 1 | SMS holding signal has no failure mode |

## Issues

**1. Spec depends on files not in the submission. [Blocker]**
04a and 04b repeatedly cite `output/submit/05-agent-purpose.md` §3b, `03-delegation-matrix.md` §3, `output/submit/adr.md`, `assumptions-log.md`, `06-client-feedback.md`, `07-validation-plan.md`. Many short codes ride on top of those references: GR-13, PB-3, PB-6, C-CA1, C-CA5, R3, R7.18, Phase 10 R1, Hartwood B-1, A4-F1. A reader who only has the Gate-3 folder cannot resolve the rule that each code carries.
*Fix:* Inline the rule itself wherever a citation appears. Where a citation is unavoidable, add an "External references" appendix and copy the rule body into it.

**2. 04b has no LLM contract. [Blocker]**
04b describes the classifier as `extract_fields(text, schema=credential_taxonomy)` and the inbound-event classifier as `LLM_classify(event, prompt="Classify as confirm | ack | reject; return confidence")`. There is no output schema, no model choice, no token budget, no timeout, no retry policy, and no rule for what to do when the LLM returns invalid output.
*Fix:* Add an "LLM contract" section. Name a model. Define the JSON output as a fixed schema. Specify timeout (e.g. 15s), retry (one retry), and the fallback path when the output fails schema validation.

**3. The submission engine has no integration contracts. [Blocker]**
04a calls verbs like `send via request.hospital.preferred_channel`, `send_holding_signal_sms(...)`, and `wait_for_revoke_acks(timeout=60s, retries=2)`. No SMTP server, no portal endpoint, no SMS provider, no authentication, no payload format, no rate limit.
*Fix:* Add one integration contract per channel (Email, Hospital Portal, SMS). Each must include endpoint, authentication source, request body, success and error responses, timeout, and retry rule.

**4. Confidence aggregation is a plain mean of six fields. [Concern]**
04b §"Behaviour rules" sets `classification_confidence = mean(per_field_confidences)`. Six fields, six equal weights. A wrong `count` field (say 0.20) gets washed out by five strong fields and the ticket still passes T2. Assumption A1.2 flags the risk; the design ships the unweighted mean anyway.
*Fix:* Either weight the fields (e.g. `count` and `start_at` heavier than `unit`) or cap the aggregate at the lowest per-field confidence.

**5. T2 tier bypasses the ALHO archetype. [Concern]**
04b §3 describes T2 as *"agent finalises classification; 1-click coordinator ack queued"*, and the flow in §4 calls `downstream_dispatch(classification_record)` immediately. ALHO is supposed to mean the coordinator approves before downstream use. T2 sends downstream without waiting for the ack. The label and the behaviour disagree.
*Fix:* Either change T2 to "wait for coordinator ack, then `downstream_dispatch`", or relabel T2 as Fully Agentic with coordinator visibility (no ack required).

**6. SMS holding signal has no failure mode. [Missing]**
04a §4.1 calls `send_holding_signal_sms(...)` right after the submission is sent. The spec does not say what happens if the SMS gateway is down. Does the submission stand? Is it rolled back? Is the nurse marked as un-notified?
*Fix:* Add an explicit failure rule. Suggested: the submission proceeds; the SMS failure is logged with a retry job; the coordinator dashboard shows a "missing holding signal" flag for that nurse.

## Strengths worth keeping

The shared glossary as its own file is the cleanest example I have seen in the squad — entities defined once, both specs referencing the same source, no parallel divergence. The submission factuality ledger (every claim slot-by-slot exact-matched against the source-of-record before any send) is a strong governance idea — it would catch the hallucinated-field bug that other specs leave to luck. ADR-3 (sequential-with-optimistic-batching) shows real engagement with the legal/MSA risk that Pavel's pair under-weights.
