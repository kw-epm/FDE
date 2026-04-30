# Artifact 4 — Validation Design

## Purpose

This document defines how to verify that the FNOL Processing Agent (FPA) is working correctly. It covers: what to test, how to test it, what failure looks like — including the *quiet* failure modes where the agent is wrong and no one notices — and what thresholds must be met before the agent is trusted for production.

---

## Validation Principles

1. **Test the delegation boundary, not just the happy path.** The most consequential tests are the ones that probe where the agent hands off to a human. An agent that passes happy-path tests but fails at the boundary causes systematic harm before anyone notices.

2. **Define quiet failure explicitly.** Quiet failure is worse than loud failure. An agent that routes a bodily injury claim to a property adjuster (wrong specialization) fails loudly when the adjuster calls back confused. An agent that misidentifies a claim type and routes to the right specialty by accident passes audit reviews until a coverage dispute surfaces weeks later. Test for both.

3. **The SLA clock is not the agent's SLA clock.** The 2-hour SLA starts at receipt, not at processing start. Tests must verify that received_at is set before any parsing, and that AC-001 fires correctly in both FULL and INTERIM paths.

---

## Test Suite Structure

| Suite | Focus | Minimum test count |
|---|---|---|
| V1 — Happy Path | End-to-end autonomous claim processing | 3 |
| V2 — Parsing Edge Cases | Field extraction accuracy and confidence thresholds | 7 |
| V3 — Coverage Validation | Coverage match, exclusion, lapsed policy | 5 |
| V4 — Severity & Delegation Boundary | Severity scoring, escalation triggers, hard constraints | 7 |
| V5 — SLA Monitoring | SLA clock, AT_RISK alerting, INTERIM acknowledgment | 4 |
| V6 — Integration Failure Modes | SOAP timeout, CRM failure, DMS unavailable | 5 |
| V7 — Concurrency | Duplicate claim receipt, simultaneous field edit | 2 |
| V8 — Post-Launch Monitoring | Continuous production drift signals (not pre-launch tests) | 4 |

---

## V1 — Happy Path

### V1-01 — Standard Auto Collision, Low Value (Fully Autonomous)
**Given:**
- Email received: "Hi, I was in a rear-end collision on the highway. My policy number is AA-123456. The other driver hit me from behind. No injuries. My car has significant bumper damage. It happened yesterday around 3pm on I-95 in Georgia. My contact is jane.doe@email.com"
- Policy AA-123456: ACTIVE, covers AUTO_COLLISION, effective dates encompass incident_date, no matching exclusions
- Estimated loss: not stated in text
- Claimant has 1 prior claim in the last 12 months
- Adjuster available: AUTO_COLLISION specialist, Georgia coverage, open_claims_count = 8

**When:** Agent processes claim end-to-end

**Then:**
- received_at set at email receipt time (before IN-002 begins)
- claim_type = AUTO_COLLISION, parse_confidence ≥ 0.90
- bodily_injury_flag = false (no injury language detected)
- coverage_status = CONFIRMED
- severity_score: estimated_loss null (+2) = 2 → severity_level = LOW
- **Verify:** prior claims count (1) < SERIAL_CLAIMANT_THRESHOLD (5) → SERIAL_CLAIMANT signal does NOT fire; severity_score remains 2 (not 3)
- No SV-002 escalation (LOW, not high-value, no bodily injury)
- Adjuster assigned: AUTO_COLLISION specialist, Georgia coverage, not at queue limit
- CRM claim record created (crm_claim_id populated)
- Acknowledgment: FULL, sent to jane.doe@email.com, contains claim reference + adjuster name + "within 24 hours" commitment
- acknowledged_at set; sla_status = ON_TRACK at acknowledgment
- Total agent processing time (received_at → acknowledged_at): ≤ 5 minutes
- No WorkItem created
- processing_status = COMPLETED

---

### V1-02 — Web Form Claim, GOOD Coverage Match (Fully Autonomous)
**Given:**
- Web form submitted with: policy_number = PR-789012, claim_type = PROPERTY_DAMAGE (dropdown), incident_date = 2026-04-20, incident_location = "Miami, FL", estimated_loss_amount = $8,500, description = "Storm damage to roof and windows"
- Policy PR-789012: ACTIVE, covers PROPERTY_DAMAGE, no exclusions matching storm/roof
- Adjuster available: PROPERTY_DAMAGE specialist, FL coverage, open_claims_count = 10

**When:** Agent processes claim end-to-end

**Then:**
- Web form fields extracted with confidence = 0.95 (pre-structured)
- parse_confidence ≥ 0.90, all required fields present
- coverage_status = CONFIRMED (no exclusion match for storm/roof)
- severity_score: $8,500 < $10K (+1) = 1 → LOW
- Autonomous routing
- Acknowledgment: FULL, via email (if available in CRM) + web portal status updated
- No WorkItem created

---

### V1-03 — Phone Transcript, Bodily Injury — INTERIM Ack Then FULL
**Given:**
- Phone transcript uploaded: "Caller: I need to report an accident. I was hit by another driver, I'm in the hospital. My policy is LI-456789. It happened this morning in Austin, Texas. I think the damages might be around $30,000 to my car."
- Policy LI-456789: ACTIVE, covers LIABILITY
- bodily_injury_flag = true ("I'm in the hospital")
- multiple_parties_flag = true ("another driver" matches IN-002 trigger phrase "other driver")
- Adjuster assigned after supervisor severity review (dual-qualified adjuster: specializations = [LIABILITY, BODILY_INJURY], TX coverage; required by RT-001 bodily injury exception)

**When:** Agent processes

**Then:**
- Caller lines extracted; representative lines excluded from NLP
- bodily_injury_flag = true; multiple_parties_flag = true; claim_type = LIABILITY; severity scoring: bodily_injury (+3) + LIABILITY (+2) + $30K loss (+2) + multiple_parties (+1) = 8 → severity_level = CRITICAL; SEVERITY_REVIEW WorkItem triggered (CRITICAL severity + bodily_injury_flag = true)
- SV-002 creates SEVERITY_REVIEW WorkItem → processing_status = AWAITING_SEVERITY_REVIEW
- INTERIM acknowledgment sent immediately on AWAITING_SEVERITY_REVIEW entry: claim reference, "An adjuster will contact you within 24 hours"
- acknowledged_at set at INTERIM send time (SLA met)
- After supervisor confirms severity and routing: FULL acknowledgment sent with adjuster name
- No autonomous adjuster assignment without supervisor confirmation

---

## V2 — Parsing Edge Cases

### V2-01 — Policy Number Ambiguity: Billing Number Provided
**Given:** Email contains "account number 4420-001" but no policy number in expected format

**When:** IN-002 extracts fields

**Then:**
- policy_number field extracted with confidence < 0.90 (or not extracted)
- FIELD_COMPLETION WorkItem created within 10 seconds
- WorkItem content shows: extracted value = "4420-001", confidence = low, note "Value does not match expected policy number format"
- processing_status = AWAITING_FIELD_COMPLETION
- INTERIM acknowledgment sent

---

### V2-02 — Relative Date Resolution
**Given:** Email states "the accident happened last Tuesday"; received_at = 2026-04-27 (Monday)

**When:** IN-002 extracts incident_date

**Then:**
- incident_date resolved to 2026-04-21 (the Tuesday prior to received_at)
- Confidence ≥ 0.85 (relative dates carry slightly lower confidence than absolute)
- AuditEvent records: extracted_value = "last Tuesday", resolved_to = "2026-04-21"
- **Verify:** resolution uses received_at as the reference point, not the current processing time

---

### V2-03 — Bodily Injury in Phone Transcript Not Misidentified
**Given:** Phone transcript contains representative line "Agent: Are you injured?" followed by "Caller: No, I'm fine, just the car is damaged"

**When:** IN-002 processes

**Then:**
- Only Caller: lines processed by NLP
- bodily_injury_flag = false (claimant explicitly denies injury; agent question is excluded)
- **Verify:** representative lines containing injury words do NOT set bodily_injury_flag

---

### V2-04 — All Required Fields Missing (Minimal Web Form Submission)
**Given:** Web form submitted with only incident_description = "My stuff was damaged"

**When:** IN-002 runs

**Then:**
- policy_number: not extracted
- claimant contact: not extracted
- claim_type: ambiguous (for example PROPERTY_DAMAGE vs LIABILITY; low confidence)
- incident_date: not extracted
- parse_confidence = 0.00 (no required fields)
- FIELD_COMPLETION WorkItem created with all 4 required fields in missing_or_low_confidence_fields list
- INTERIM acknowledgment still sent (claim reference created and sent before field completion)
- **Verify:** INTERIM ack is sent even when claim has zero parseable fields

---

### V2-05 — Web Form Double-Submit Blocked by IN-001 Idempotency Check
**Given:** Claimant clicks "Submit" twice in quick succession; both submissions carry the same form submission token (source_message_id = "FORM-TOKEN-abc123"); second submission arrives 3 seconds after the first

**When:** Both submissions are received by IN-001

**Then:**
- First submission (token FORM-TOKEN-abc123): IN-001 finds no existing Claim with this source_message_id → creates Claim, stores source_message_id, processing begins normally
- Second submission (same token FORM-TOKEN-abc123): IN-001 idempotency check finds existing Claim with source_message_id = FORM-TOKEN-abc123 received within DUPLICATE_WINDOW_MINUTES → incoming event discarded; no second Claim record created; existing Claim.id returned to caller
- No DUPLICATE_DETECTED AuditEvent logged (this is a pre-creation technical guard, not a business logic duplicate — IN-003 is never reached)
- Claimant receives one acknowledgment only
- **Verify:** IN-001 idempotency operates on source_message_id (the form submission token), not on claim content fields (policy_number + incident_date + claimant_id); content-based deduplication is IN-003's responsibility (tested in V7-01)

---

### V2-06 — Estimated Loss Exceeds HIGH_VALUE_THRESHOLD During Parsing
**Given:** Email states "I estimate damage around $75,000 to my property"

**When:** IN-002 extracts

**Then:**
- estimated_loss_amount = 75000.00 (USD normalised)
- is_high_value = true (75000 ≥ 50000)
- SV-001 scoring: $50K–$150K range (+4); SV-002 triggers SEVERITY_REVIEW because is_high_value = true
- **Verify:** is_high_value flag is computed at parse time and flows through to SV-002 trigger correctly

---

### V2-07 — Ambiguous Claim Type: "Water Damage"
**Given:** Email states "there was water damage to my basement after the storm"

**When:** IN-002 classifies claim_type

**Then:**
- NLP classification: PROPERTY_DAMAGE (most likely) with confidence ~0.82 (below threshold; storm vs. flood ambiguity)
- FIELD_COMPLETION WorkItem created with claim_type in low-confidence list
- WorkItem shows: agent's top classification = PROPERTY_DAMAGE (0.82), note "Storm vs. flood coverage distinction may apply — verify claim type with specialist"
- **Verify:** agent does NOT autonomously classify flood-related claims as PROPERTY_DAMAGE if confidence is below threshold

---

## V3 — Coverage Validation

### V3-01 — Clear Coverage Match
**Given:** claim_type = AUTO_COLLISION; policy covers AUTO_COLLISION; no exclusions return from CheckExclusions

**When:** CV-001 and CV-002 run

**Then:**
- coverage_status = CONFIRMED
- No COVERAGE_REVIEW WorkItem created
- Processing continues to SV-001

---

### V3-02 — Claim Type Not in Policy (Clear Exclusion)
**Given:** claim_type = AUTO_COLLISION; policy coverage_types = [LIABILITY] only (liability-only policy)

**When:** CV-001 runs

**Then:**
- claim_type NOT in coverage_types_list
- coverage_status = EXCLUDED
- COVERAGE_REVIEW WorkItem created: content shows claim_type = AUTO_COLLISION, policy_coverage_types = [LIABILITY]
- INTERIM acknowledgment sent if not already sent
- processing_status = AWAITING_COVERAGE_REVIEW
- **Verify:** agent does NOT proceed to severity scoring with coverage_status = EXCLUDED

---

### V3-03 — Lapsed Policy
**Given:** policy_status = LAPSED (returned by PL-001)

**When:** PL-001 returns policy record

**Then:**
- coverage_status = LAPSED
- COVERAGE_REVIEW WorkItem created with note "Policy is in LAPSED status — specialist must determine if grace period applies"
- Agent does NOT deny coverage; specialist reviews
- **Verify:** processing does not continue to coverage type check while policy is lapsed

---

### V3-04 — Exclusion Similarity Threshold: Below
**Given:** Exclusion clause text: "damage arising from intentional acts by the insured"
Incident description: "my roof collapsed due to heavy snowfall"
Similarity score returned by CheckExclusions: 0.42

**When:** CV-002 evaluates

**Then:**
- 0.42 < EXCLUSION_SIMILARITY_THRESHOLD (0.75)
- excluded = false → coverage_status = CONFIRMED
- No COVERAGE_REVIEW WorkItem
- **Verify:** low similarity scores do NOT trigger a hold

---

### V3-05 — Exclusion Similarity Threshold: Above
**Given:** Exclusion clause text: "damage arising from flood or surface water intrusion"
Incident description: "water came into my basement during the rainstorm"
Similarity score: 0.81

**When:** CV-002 evaluates

**Then:**
- 0.81 ≥ EXCLUSION_SIMILARITY_THRESHOLD (0.75)
- coverage_status = DISPUTED
- COVERAGE_REVIEW WorkItem includes: exclusion clause text, similarity = 0.81, incident description preview
- processing_status = AWAITING_COVERAGE_REVIEW
- **Verify:** boundary is enforced at exactly 0.75 — a score of 0.74 does NOT trigger the hold

---

## V4 — Severity & Delegation Boundary

### V4-01 — LOW Severity Routes Autonomously
**Given:** claim_type = AUTO_THEFT, estimated_loss_amount = $5,000, bodily_injury_flag = false, no prior claims

**When:** SV-001 and SV-002 run

**Then:**
- severity_score: $5K < $10K (+1) = 1 → severity_level = LOW
- SV-002: no escalation (LOW, not high-value, no bodily injury)
- No SEVERITY_REVIEW WorkItem
- Proceeds directly to RT-001

---

### V4-02 — Bodily Injury Always Escalates (Hard Constraint C2)
**Given:** claim_type = AUTO_COLLISION, estimated_loss_amount = $3,000, bodily_injury_flag = true

**When:** SV-002 runs

**Then:**
- severity_score: $3K < $10K (+1) + bodily_injury (+3) = 4 → MEDIUM; BUT bodily_injury_flag = true
- SEVERITY_REVIEW WorkItem created regardless of severity_level (bodily_injury_flag = true is a hard trigger)
- processing_status = AWAITING_SEVERITY_REVIEW
- INTERIM acknowledgment sent
- **Verify:** bodily_injury_flag = true ALWAYS triggers SEVERITY_REVIEW, even at MEDIUM severity and low financial value

---

### V4-03 — HIGH_VALUE_THRESHOLD Boundary Precision
**Given:** Two claims — Claim A: estimated_loss_amount = $49,999.99; Claim B: estimated_loss_amount = $50,000.00
Both: AUTO_COLLISION, no bodily injury, coverage CONFIRMED

**When:** Both processed

**Then:**
- Claim A: is_high_value = false; if severity otherwise LOW/MEDIUM → no SEVERITY_REVIEW → autonomous routing
- Claim B: is_high_value = true → SEVERITY_REVIEW WorkItem created regardless of severity_level
- **Verify:** threshold is inclusive at exactly $50,000.00; the ≥ comparison uses decimal(12,2) arithmetic — no floating-point ambiguity
- **Verify:** estimated_loss_amount is stored and compared as decimal(12,2) per the schema; test rejects any implementation using floating-point types (float/double) for this field
- **How to verify the type constraint:** runtime logic tests alone cannot prove decimal storage. Use both: (a) Phase 0 code review checklist item — "Confirm estimated_loss_amount column is declared DECIMAL/NUMERIC in database schema, not FLOAT or DOUBLE; verify ORM model definition"; and (b) storage-layer precision assertion — insert $49999.99 and $50000.00, read back both values, assert they are exactly equal to the inserted values to 2 decimal places. A float64 implementation rounds $49999.999... to $50000.00, which would erroneously trigger is_high_value = true for a claim just below threshold.

---

### V4-04 — Coverage Denial Requires Human (Hard Constraint C1)
**Given:** Specialist resolves COVERAGE_REVIEW WorkItem with decision = DENIED

**When:** Human decision recorded

**Then:**
- coverage_status = DENIED (only set by human; never by agent)
- Claim.coverage_denial_reason is populated by the specialist (required for DENIED resolution; WorkItem UI enforces this field as mandatory on the DENIED resolution path — resolution cannot be submitted without it)
- processing_status = HALTED
- AuditEvent: actor_type = HUMAN, event_type = COVERAGE_DENIED_BY_HUMAN, to_value = coverage_denial_reason text
- No adjuster assignment occurs
- No FULL acknowledgment with adjuster name is sent
- **Verify:** the agent cannot set coverage_status = DENIED at any point in any module
- **Verify:** coverage_denial_reason is non-null when coverage_status = DENIED; the schema permits null only until a human sets DENIED

---

### V4-05 — SERIAL_CLAIMANT Flag: Score Contribution Only
**Given:** claimant_id has 7 prior claims in last 365 days (≥ SERIAL_CLAIMANT_THRESHOLD of 5)
Claim: AUTO_COLLISION, estimated_loss_amount = $4,000, bodily_injury_flag = false

**When:** SV-001 runs

**Then:**
- severity_score: $4K (+1) + SERIAL_CLAIMANT (+1) = 2 → LOW
- No SEVERITY_REVIEW escalation on SERIAL_CLAIMANT signal alone (score is 2, still LOW)
- Flag is noted in adjuster WorkItem content as "claimant has elevated prior claim frequency"
- **Verify:** SERIAL_CLAIMANT adds +1 to score but does NOT independently trigger a hold if total score remains LOW/MEDIUM

---

### V4-06 — No Eligible Adjuster: Routing Override
**Given:** claim_type = PROPERTY_DAMAGE, incident_state = HI (Hawaii); no active PROPERTY_DAMAGE adjusters with coverage_regions including HI

**When:** RT-001 runs

**Then:**
- No eligible adjuster found after all filters
- ROUTING_OVERRIDE WorkItem created: "No PROPERTY_DAMAGE adjuster with Hawaii coverage available"
- processing_status = AWAITING_ROUTING_OVERRIDE
- INTERIM acknowledgment sent if not already sent
- Agent does NOT assign a wrong-specialization adjuster as a fallback
- **Verify:** queue overflow triggers human WorkItem, not a compromise routing

---

### V4-07 — Semantic Classification Error Produces Auditable Signal
**Given:** Email describes an AUTO_THEFT incident ("my car was stolen from the parking lot"), but NLP classifies claim_type = AUTO_COLLISION at confidence 0.91 (above threshold — extraction proceeds autonomously)

**When:** Claim is routed and completed

**Then:**
- Claim routes to an AUTO_COLLISION adjuster (wrong specialty — the routing algorithm uses the extracted claim_type)
- The routing is wrong, but no WorkItem is created (confidence was above threshold)
- **Verify:** AuditEvent PARSING_COMPLETED event contains to_value = `{"claim_type": "AUTO_COLLISION", "confidence": 0.91, "parse_confidence": 0.91}` per the required schema (Artifact 3 Audit & Logging section) — this is the record that makes the monthly accuracy audit possible
- **Verify:** the monthly labeled-test accuracy measurement (Artifact 1: ≥ 93% claim type classification accuracy) would catch this failure in sample review
- **Verify:** when the adjuster identifies the error and the WorkItem is updated with corrected claim_type = AUTO_THEFT, AuditEvent records FIELD_OVERRIDDEN_BY_HUMAN with from_value = AUTO_COLLISION, to_value = AUTO_THEFT

**Purpose:** This test verifies that high-confidence misclassifications are auditable (not silently wrong). The system cannot prevent all semantic errors at runtime, but it must produce the signals that allow humans to detect them in audit.

---

## V5 — SLA Monitoring

### V5-01 — SLA Clock Starts at Receipt, Not at Parsing Start
**Given:** Email arrives at 10:00:00 UTC; parsing begins at 10:00:05 UTC (5-second DMS store delay)

**When:** received_at is set

**Then:**
- Claim.received_at = 10:00:00 UTC (not 10:00:05)
- sla_deadline = 12:00:00 UTC (not 12:00:05)
- **Verify:** received_at is immutable and set before IN-002 begins

---

### V5-02 — AT_RISK Alert Fires at Correct Time
**Given:** Claim received at 09:00:00 UTC; SLA_AT_RISK_BUFFER_MINUTES = 30; sla_deadline = 11:00:00 UTC; claim is in AWAITING_SEVERITY_REVIEW at 10:31:00 UTC

**When:** AC-002 runs on its 5-minute timer at 10:35:00 UTC

**Then:**
- time_remaining = 11:00:00 - 10:35:00 = 25 min (< 30 min buffer)
- sla_status set to AT_RISK
- SLA_AT_RISK_ALERT logged
- Supervisor notified via dashboard
- If SEVERITY_REVIEW WorkItem is OPEN: WorkItem immediately escalated (does not wait for WorkItem's 30-min timer)

---

### V5-03 — INTERIM Ack Sent on AWAITING State Entry
**Given:** Claim enters AWAITING_SEVERITY_REVIEW at 10:15 UTC (received_at = 10:00 UTC; 1:45 remaining)

**When:** processing_status = AWAITING_SEVERITY_REVIEW is set

**Then:**
- AC-001 fires immediately (not after SEVERITY_REVIEW is resolved)
- INTERIM acknowledgment sent; acknowledged_at set
- sla_status = ON_TRACK (1:45 remaining; acknowledged within window)
- **Verify:** INTERIM ack fires on AWAITING state entry, not on COMPLETED

---

### V5-04 — SLA Boundary: Email Ingestion Delay
**Given:** Email was sent at 08:00 UTC but not ingested until 10:05 UTC (email server delay); received_at = 10:05 UTC; sla_deadline = 12:05 UTC

**When:** Claim is processed and acknowledged at 10:08 UTC

**Then:**
- sla_status = ON_TRACK (acknowledged_at 10:08 < sla_deadline 12:05)
- **Verify:** sla_deadline = received_at + 2h; sent timestamps from email metadata are NOT used as the SLA start

**Design rationale and known limitation:** The FPA measures SLA from system receipt (received_at), not from claimant send time. This is necessary because email infrastructure delays are outside the insurer's control. However, a claimant who sent at 08:00 and was not acknowledged until 10:08 experienced a 2h8min wait — technically "on-track" by system measure but potentially unsatisfactory. **V1 mitigation (partial):** If the email Date header is present, not in the future, and within 15 minutes before system ingestion time, use the Date header as received_at. Date header must be rejected (fall back to ingestion time) if: (a) header is absent; (b) header timestamp is in the future (sender clock misconfiguration or timezone error); (c) header predates ingestion by more than 15 minutes (infrastructure or relay delay). This guards against backdated headers — either malicious or from misconfigured sender mail servers — being used to artificially advance the SLA clock. Document the system-receipt convention in claimant-facing operational procedures.

---

## V6 — Integration Failure Modes

### V6-01 — SOAP System Unavailable After All Retries
**Given:** Policy admin SOAP returns connection timeout on all retry attempts (PL-001 exhausts retry policy)

**When:** PL-001 exhausts retries

**Then:**
- SOAP_FAILURE WorkItem created with claim ID, policy_number attempted, error detail
- processing_status = HALTED
- IT_ONCALL alerted
- SLA risk notification sent to supervisor (halted claim with time remaining)
- No coverage_status set; no fields from policy admin populated
- Agent does NOT attempt to infer coverage from claim text

---

### V6-02 — CRM Adjuster Query Returns Empty (All at Capacity)
**Given:** All PROPERTY_DAMAGE adjusters in FL have open_claims_count ≥ 15

**When:** RT-001 runs

**Then:**
- Distinct from V4-06 (different cause: queue full, not specialization mismatch)
- ROUTING_OVERRIDE WorkItem created: filter_result = "All PROPERTY_DAMAGE adjusters in FL are at queue capacity (≥ 15 open claims)"
- **Verify:** system clearly distinguishes "no adjuster with this specialization" from "all eligible adjusters are full"

---

### V6-03 — CRM Acknowledgment Email Send Fails (404 Contact Not Found)
**Given:** claimant_id was not enriched (CRM contact not found in IN-002); CRM Endpoint 4 returns 404 for contact_id

**When:** AC-001 attempts to send acknowledgment

**Then:**
- No SMTP fallback (SMTP is out of scope for V1 — no SMTP integration contract exists)
- SYSTEM_ERROR WorkItem created; log acknowledgment as FAILED; specialist must manually contact claimant
- **Verify:** acknowledgment failure does NOT silently pass — SYSTEM_ERROR WorkItem is created so a human knows a claimant was not reached
- **Verify:** agent does NOT attempt any out-of-spec channel (no SMTP, no direct API) — failure is surfaced via WorkItem only

---

### V6-04 — DMS Store Fails at Intake (IN-001)

**Given:** DMS returns HTTP 503 at IN-001

**When:** IN-001 attempts to store raw_input

**Then:**
- IN-001 proceeds (DMS is non-blocking); raw_input_document_id = null; raw_input cached in-memory for current processing session; AuditEvent log: DMS_STORE_FAILED
- Parsing continues in-memory; WorkItem NOT created for DMS failure alone
- Background retry: every 60 seconds for 30 minutes
- After 30 minutes still failing: SYSTEM_ERROR WorkItem created for IT_ONCALL; supervisor dashboard flag
- **Verify:** DMS failure does NOT halt claim processing; it is a compliance and record-keeping risk, not a processing blocker

---

### V6-05 — CV-002 CheckExclusions SOAP Failure
**Given:** Claim has passed PL-001 (policy found, ACTIVE) and CV-001 (claim_type in coverage_types, incident_date in period). CheckExclusions SOAP call returns SERVICE_UNAVAILABLE on all retry attempts.

**When:** CV-002 exhausts retries

**Then:**
- SOAP_FAILURE WorkItem created; processing_status = HALTED; IT_ONCALL alerted
- No severity scoring begins; no routing proceeds
- coverage_status is NOT set (remains null — exclusion status unverified)
- INTERIM acknowledgment sent if not already sent (claim is halted, no adjuster assigned)
- **Verify:** CheckExclusions SOAP failure does NOT set coverage_status = CONFIRMED or treat excluded = false — coverage cannot be cleared when verification is unavailable
- **Verify:** When IT resolves the SOAP issue and supervisor re-queues the claim, processing resumes from COVERAGE_VALIDATION (CV-002 re-runs), not from the beginning of the pipeline

---

## V7 — Concurrency

### V7-01 — Same Claim Received via Two Channels Simultaneously
**Given:** Claimant submits web form at 10:00:00 AND calls at 10:00:30, transcript uploaded at 10:02:00; same policy_number, same incident_date, both processed simultaneously

**When:** Both are processed

**Then:**
- First receipt (web form, 10:00:00): creates Claim with unique ID; processing begins
- Second receipt (transcript, 10:02:00): IN-002 completes parsing successfully; IN-003 then runs and detects matching policy_number + incident_date + claimant contact within 10-minute window; flags as potential duplicate
- DUPLICATE_DETECTED event logged; specialist notified; second claim held for manual deduplication
- Only one claim proceeds to full processing
- **Verify:** deduplication check uses policy_number + incident_date + claimant_id (not source_channel) as the key — this is IN-003 (business-logic deduplication). The two submissions arrive on different channels and have different source_message_ids (web form submission token vs. phone transcript upload session ID), so IN-001's source_message_id idempotency check does not trigger. IN-003's content-based matching is the correct deduplication mechanism for this cross-channel scenario.

---

### V7-02 — Two Specialists Edit the Same WorkItem Simultaneously
**Given:** FIELD_COMPLETION WorkItem assigned to Specialist A; Specialist B opens and begins editing the same WorkItem 30 seconds later (after A but before A submits)

**When:** Both submit their resolutions

**Then:**
- First submit (A, at 10:05:30): resolution recorded; WorkItem status = RESOLVED
- Second submit (B, at 10:05:45): system detects WorkItem already in RESOLVED state; B's submission rejected with error "This WorkItem has already been resolved"
- AuditEvent records both submission attempts; only A's is recorded as the resolution
- **Verify:** optimistic locking or status check prevents double-resolution of a WorkItem

---

## V8 — Post-Launch Monitoring (Drift Detection)

These checks run continuously in production; they are not one-time tests.

### V8-01 — NLP Extraction Accuracy Drift
**Signal:** Monthly labeled-set accuracy for claim_type classification drops ≥ 3 percentage points below the baseline established in Phase 0 shadow mode; OR falls below 90% absolute (floor regardless of baseline).
**Trigger threshold:** Any single month triggering either condition above.
**Baseline establishment:** Baseline is set at the end of Phase 0 shadow mode (first 4 weeks). If baseline comes in below 93% (the year-1 target), the Phase 1 go/no-go decision must be reviewed — do not proceed to autonomous processing if shadow-mode accuracy is already below target.
**Response:** Retrain or fine-tune NLP model on recent claims data. Lower PARSE_CONFIDENCE_THRESHOLD temporarily to route more claims to FIELD_COMPLETION while retraining completes.
**Why this matters:** If the company expands into new lines of business (commercial trucking, marine) or new terminology enters claim descriptions, the pre-trained model's vocabulary distribution shifts. Drift is invisible until accuracy metrics drop.

### V8-02 — Routing Error Rate Monitoring
**Signal:** Monthly routing accuracy audit (n=200 sample) shows adjuster confirmed wrong > 2% (the ≤ 2% year-1 target).
**Trigger threshold:** Any month above 2%; two consecutive months above 1.5% (early warning).
**Response:** Review recent WorkItem FIELD_OVERRIDDEN_BY_HUMAN events for systematic claim_type misclassification patterns; recalibrate scoring weights if needed.

### V8-03 — Coverage False-Clear Rate
**Signal:** Quarterly reconciliation: claims autonomously cleared (coverage_status = CONFIRMED by agent, no human review) that subsequently raised a coverage dispute.
**Trigger threshold:** Rate exceeds 1% in any quarterly reconciliation.
**Response:** Immediate reduction of EXCLUSION_SIMILARITY_THRESHOLD (lower it to flag more claims for COVERAGE_REVIEW) while root cause is identified.

### V8-04 — SLA Breach Pattern
**Signal:** Weekly SLA compliance rate drops below 92% (below the 95% target, with 3-point buffer for early warning).
**Trigger threshold:** Two consecutive weeks below 92%.
**Response:** Review AWAITING_* queue depths and WorkItem resolution times; check if specialist team has been reduced or redeployed.

---

## Production Readiness Thresholds

All of the following must be true before go-live:

| Criterion | Threshold | Test |
|---|---|---|
| Field extraction accuracy (labeled set, n=500) | ≥ 95% correct on required fields | V2 suite + labeled historical claims data |
| SLA compliance in controlled pilot (n=200 claims) | ≥ 95% acknowledged within 2 hours | V1 + V5 suite |
| Routing accuracy (specialist review of n=200 autonomous routes) | ≥ 98% correct adjuster specialization and region | V1 + V4 suite |
| Bodily injury flag never autonomously routed (0 exceptions) | 100% | V4-02 |
| Coverage denial never set by agent (0 exceptions) | 100% | V4-04 |
| SOAP failure handled gracefully (no unhandled exceptions) | 100% | V6-01 |
| Duplicate claim detection (no duplicate Claim records) | 100% | V7-01 |
| INTERIM ack fires on AWAITING state entry | 100% | V5-03 |
All thresholds above must be met in a pre-production pilot of minimum 200 live claims with human shadow review before autonomous processing begins (Phase 0 → Phase 1 gate).

**Phase 1 → Phase 2 exit criterion (coverage false-clear rate):** Coverage false-clear rate cannot be statistically measured at n=200. Instead: after Phase 1 processes ≥ 1,000 autonomous claims, perform a reconciliation check (claims agent-cleared that subsequently raised a coverage dispute). If false-clear rate ≤ 1% at that point, proceed to Phase 2 full rollout. If > 1%: hold Phase 2; investigate root cause; lower EXCLUSION_SIMILARITY_THRESHOLD and re-run Phase 1.

**Statistical power note for coverage false-clear rate:** At n=200, a 1% false-clear rate corresponds to 2 expected events. The probability of observing 0 events from a true 1% rate is ~13% (Poisson approximation) — meaning the pilot could pass this threshold by chance even if the true rate is 1%. For a statistically valid measurement of a ≤ 1% rate, n ≥ 1,000 claims is required (95% confidence interval width ≈ ±0.6%). The coverage false-clear threshold must therefore be validated on a 30-day production sample of ≥ 1,000 autonomously processed claims, not solely on the initial pilot. Pilot evaluation uses the test suite (V3); production evaluation uses reconciliation data.

**Statistical power note for routing accuracy threshold:** At n=200, a 2% error rate corresponds to ~4 expected errors. The 95% binomial confidence interval for an observed 98% accuracy at n=200 spans approximately 95.3%–99.4% — meaning the pilot cannot reliably distinguish 98.0% from 96.0%. The go-live gate at ≥ 98% on n=200 confirms there is no catastrophic routing failure, not that the year-1 target is precisely achieved. Sustained measurement is provided by V8-02 (monthly n=200 audit); that rolling signal — not the one-time pilot — is the meaningful accuracy monitor over time. If a higher-confidence go-live gate is required, increase pilot sample to n=500 (95% CI ≈ ±1.2pp at 98% accuracy).
