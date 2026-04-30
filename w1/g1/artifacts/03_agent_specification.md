# Artifact 3 — Agent Specification

## Agent Identity

**Name:** FNOL Processing Agent (FPA)
**Version:** 1.0
**Purpose:** Automate the intake parsing, policy lookup, coverage validation, severity classification, adjuster routing, and claimant acknowledgment of First Notice of Loss reports. Reduce per-claim handling time for routine cases, eliminate manual routing errors, and guarantee claimant acknowledgment within the 2-hour SLA.

**Implementation scope note:** This spec defines behaviour — what the agent decides, when it escalates, what it writes to which systems, and what constitutes a correct vs. incorrect output. Technology choices (language, framework, NLP model, deployment platform) are the builder's decision and are intentionally not prescribed here.

**Scope (V1):**
- FNOL reports received via email, phone transcript (post-call upload), or web form
- Claims against personal and commercial lines policies in the legacy policy admin system
- Integration with: Salesforce CRM (REST), legacy policy admin system (SOAP), document management system (REST)
- Single operating environment (one claims centre)

**Out of scope (V1):**
- In-call real-time transcription and processing (phone transcripts are post-call uploads)
- Claims amendment or supplemental FNOL processing
- Coverage denial letter generation
- Adjuster-facing workflow management (downstream of routing)
- Multi-site deployment
- Claimant portal status updates

---

## Configuration Parameters

These values are set at deployment and adjustable by the claims operations team without code changes. **All defaults below are initial build estimates with no historical data basis; every threshold must be calibrated against Phase 0 shadow mode data before Phase 1 go/no-go [Assumption D5].**

| Parameter | Default | Description |
|---|---|---|
| `HIGH_VALUE_THRESHOLD` | $50,000 | Estimated loss above which is_high_value = true |
| `PARSE_CONFIDENCE_THRESHOLD` | 0.90 | Minimum field confidence for autonomous processing |
| `EXCLUSION_SIMILARITY_THRESHOLD` | 0.75 | NLP cosine similarity above which exclusion match is flagged |
| `MAX_ADJUSTER_QUEUE_SIZE` | 15 | Open claims count above which adjuster is excluded from assignment |
| `SLA_AT_RISK_BUFFER_MINUTES` | 30 | Minutes before sla_deadline at which AT_RISK alert fires |
| `SERIAL_CLAIMANT_WINDOW_DAYS` | 365 | Lookback window for prior claims count (fraud signal) |
| `SERIAL_CLAIMANT_THRESHOLD` | 5 | Prior claims count above which SERIAL_CLAIMANT signal fires |
| `DUPLICATE_WINDOW_MINUTES` | 10 | Time window for potential duplicate FNOL detection |

---

## Data Model

### Entity: Claim
```
Claim:
  id: UUID, primary key, immutable, generated on receipt
  received_at: ISO 8601 timestamp, UTC, immutable
    — SLA clock starts here; set at the moment the raw input enters the system,
      NOT at the start of parsing
  source_channel: enum [EMAIL, PHONE_TRANSCRIPT, WEB_FORM], required
  raw_input_document_id: string, FK to DMS document (stored in IN-001), nullable; required when DMS store succeeds, null only when DMS store fails and raw_input is held in ephemeral memory for retry
  source_message_id: string, max 500 chars, nullable; inbound deduplication key: EMAIL = MIME Message-ID, PHONE_TRANSCRIPT = upload session ID, WEB_FORM = form submission token; null for channels that provide no deduplication key
  processing_status: enum [
    RECEIVED,
    PARSING,
    AWAITING_FIELD_COMPLETION,
    AWAITING_DUPLICATE_REVIEW,
    POLICY_LOOKUP,
    COVERAGE_VALIDATION,
    AWAITING_COVERAGE_REVIEW,
    SEVERITY_SCORING,
    AWAITING_SEVERITY_REVIEW,
    ROUTING,
    AWAITING_ROUTING_OVERRIDE,
    ACKNOWLEDGED,
    COMPLETED,
    HALTED
  ], required, default RECEIVED
  
  State machine:
    RECEIVED → PARSING                       (immediately on receipt)
    PARSING → AWAITING_FIELD_COMPLETION      (parse_confidence < PARSE_CONFIDENCE_THRESHOLD
                                              or required field missing; IN-002)
    PARSING → AWAITING_DUPLICATE_REVIEW      (duplicate candidate detected by IN-003)
    PARSING → POLICY_LOOKUP                  (all required fields, confidence ≥ threshold, no duplicate; IN-002/IN-003)
    AWAITING_FIELD_COMPLETION → POLICY_LOOKUP (human resolves FIELD_COMPLETION WorkItem)
    AWAITING_DUPLICATE_REVIEW → POLICY_LOOKUP (specialist resolves DUPLICATE_REVIEW as DISTINCT or REPLACE)
    AWAITING_DUPLICATE_REVIEW → HALTED       (specialist resolves DUPLICATE_REVIEW as MERGE; this claim discarded)
    POLICY_LOOKUP → COVERAGE_VALIDATION      (policy found, PL-001 success)
    POLICY_LOOKUP → AWAITING_FIELD_COMPLETION (policy not found — human re-verifies policy number)
    COVERAGE_VALIDATION → AWAITING_COVERAGE_REVIEW (CV-001 or CV-002 triggers hold)
    COVERAGE_VALIDATION → SEVERITY_SCORING   (coverage_status = CONFIRMED; CV-001)
    AWAITING_COVERAGE_REVIEW → SEVERITY_SCORING (specialist confirms coverage)
    AWAITING_COVERAGE_REVIEW → HALTED        (coverage denied by human)
    SEVERITY_SCORING → AWAITING_SEVERITY_REVIEW (SV-002 triggers hold: HIGH/CRITICAL or is_high_value)
    SEVERITY_SCORING → ROUTING               (LOW/MEDIUM, not high-value, no bodily injury)
    AWAITING_SEVERITY_REVIEW → ROUTING       (supervisor confirms severity and approves routing)
    ROUTING → AWAITING_ROUTING_OVERRIDE      (no eligible adjuster; RT-001)
    ROUTING → ACKNOWLEDGED                   (adjuster assigned; RT-002 complete)
    AWAITING_ROUTING_OVERRIDE → ACKNOWLEDGED (supervisor manually assigns adjuster)
    ACKNOWLEDGED → COMPLETED                 (AC-001 send confirmed)
    Any → HALTED                             (PL-001 or CV-002 SOAP failure after all retries)
    HALTED → POLICY_LOOKUP                   (supervisor manually re-queues after IT resolves SOAP_FAILURE/PL-001)
    HALTED → COVERAGE_VALIDATION             (supervisor manually re-queues after IT resolves SOAP_FAILURE/CV-002)
    — Claims halted with halt_reason starting "DUPLICATE:" are permanently halted; the resume transition is not available. Resuming a DUPLICATE-merge claim would create exactly the duplicate processing the merge was designed to prevent.

  claimant_id: string, FK to CRM Contact (on CRM contact deletion: set null), nullable until IN-002 enrichment
  policy_number: string, max 20 chars (the regex [A-Z]{2,3}-\d{6,10} yields max 14 chars; 20 allows for namespace variations), extracted by IN-002, required after AWAITING_FIELD_COMPLETION resolves
  policy_id: string, FK to PolicyAdmin (returned by PL-001), nullable until PL-001
  policy_status: enum [ACTIVE, LAPSED, CANCELLED, SUSPENDED], nullable until PL-001
  policy_effective_date: ISO 8601 date, nullable until PL-001
  policy_expiration_date: ISO 8601 date, nullable until PL-001
  claim_type: enum [AUTO_COLLISION, AUTO_THEFT, PROPERTY_DAMAGE, PROPERTY_THEFT,
    BODILY_INJURY, LIABILITY], nullable until IN-002 or human confirmation
  incident_date: ISO 8601 date, nullable until IN-002 or human confirmation
  incident_location: string, max 500 chars, nullable
  incident_state: string, 2-char ISO 3166-2 state code, nullable (derived from incident_location or extracted)
  estimated_loss_amount: decimal(12,2), nullable (null if not stated in claim text)
  is_high_value: boolean, computed: true if estimated_loss_amount >= HIGH_VALUE_THRESHOLD; read-only
  bodily_injury_flag: boolean, default false; set to true by IN-002 if bodily injury phrase detected
    or claim_type = BODILY_INJURY
  multiple_parties_flag: boolean, default false; set by IN-002
  parse_confidence: decimal(4,3), range 0.000–1.000, nullable; minimum confidence across required extracted fields
  coverage_status: enum [CONFIRMED, EXCLUDED, LAPSED, DISPUTED, DENIED],
    nullable until CV-001
    — DENIED may only be written by human WorkItem resolution; the agent MUST NOT set this value
  coverage_denial_reason: string, max 1000 chars, nullable; populated only when specialist sets
    coverage_status = DENIED
  severity_score: integer, range ≥ 1 (maximum achievable: 13), nullable until SV-001
  severity_level: enum [LOW, MEDIUM, HIGH, CRITICAL], computed from severity_score; read-only
    (LOW: 1–3, MEDIUM: 4–5, HIGH: 6–7, CRITICAL: ≥ 8; maximum achievable score is 13)
  assigned_adjuster_id: string, FK to CRM User (on CRM user deactivation: set null), nullable until RT-001 or human override
  crm_claim_id: string, FK to CRM Claim record (returned by RT-002), nullable until RT-002
  interim_acknowledged_at: ISO 8601 timestamp, UTC, nullable; set when INTERIM acknowledgment is sent; remains null if FULL was sent as the first (and only) acknowledgment
  full_acknowledged_at: ISO 8601 timestamp, UTC, nullable; set when FULL acknowledgment is sent, regardless of whether INTERIM preceded it; null until FULL ack is sent
  acknowledged_at: ISO 8601 timestamp, UTC, nullable; computed = COALESCE(interim_acknowledged_at, full_acknowledged_at); set once the first acknowledgment fires (FULL or INTERIM); SLA computation uses this field; immutable once set
  sla_deadline: ISO 8601 timestamp, UTC, computed: received_at + 2 hours, immutable
  sla_status: enum [ON_TRACK, AT_RISK, BREACHED], computed; updated by AC-002 on schedule
  halt_reason: string, max 500 chars, nullable; set when processing_status = HALTED; describes failure type (e.g., "SOAP_FAILURE: policy admin system unresponsive after 3 retries")
  created_at: ISO 8601 timestamp, UTC, immutable
  updated_at: ISO 8601 timestamp, UTC
```

### Entity: ParsedField
```
ParsedField:
  id: UUID, primary key, immutable
  claim_id: UUID, foreign key to Claim (cascade delete), required
  field_name: string, max 100 chars, required
    (one of: policy_number, claimant_name, claimant_email, claimant_phone,
     claim_type, incident_date, incident_location, estimated_loss_amount,
     bodily_injury_mentioned, multiple_parties_mentioned)
  raw_span: string, format "{start_char}-{end_char}", required
    (character range in raw_input where extraction was sourced)
  extracted_value: string, max 2000 chars, required
  confidence: decimal(4,3), range 0.000–1.000, required
  human_verified: boolean, default false
  verified_value: string, max 2000 chars, nullable
    (human's correction; null if human confirmed extracted_value unchanged)
  verified_by: UUID, foreign key to User, nullable
  verified_at: ISO 8601 timestamp, UTC, nullable
```

### Entity: WorkItem
```
WorkItem:
  id: UUID, primary key, immutable
  type: enum [FIELD_COMPLETION, DUPLICATE_REVIEW, COVERAGE_REVIEW, SEVERITY_REVIEW,
    ROUTING_OVERRIDE, SOAP_FAILURE, SYSTEM_ERROR], required
  claim_id: UUID, foreign key to Claim (restrict delete — a Claim with open WorkItems cannot be deleted), required
  status: enum [OPEN, IN_PROGRESS, RESOLVED, ESCALATED], required, default OPEN
  assigned_role: enum [SPECIALIST, SUPERVISOR, CLAIMS_MANAGER, IT_ONCALL], required
  assigned_to: UUID, foreign key to User, nullable
  content: JSON object, required (type-specific payload defined in the module that creates it)
  agent_recommendation: string, max 500 chars, nullable
  resolution: string, max 1000 chars, nullable
  resolved_by: UUID, foreign key to User, nullable
  created_at: ISO 8601 timestamp, UTC, immutable
  updated_at: ISO 8601 timestamp, UTC
  sla_deadline: ISO 8601 timestamp, UTC, required
  escalated_at: ISO 8601 timestamp, UTC, nullable

  State machine:
    OPEN → IN_PROGRESS  (user opens WorkItem in UI)
    IN_PROGRESS → RESOLVED  (user submits resolution)
    OPEN or IN_PROGRESS → ESCALATED  (sla_deadline passes; re-assigned to next role)
    ESCALATED → RESOLVED  (escalation target resolves)
```

### Specialist WorkItem UI (Scope Note)

The WorkItem JSON schemas above define what data is carried. The actual UI that specialists and supervisors see when resolving WorkItems is out of scope for this spec but is a hard delivery dependency — without a usable UI, the WorkItem SLA times (20 min FIELD_COMPLETION, 30 min SEVERITY_REVIEW) are not achievable. The UI must support at minimum:
- Raw input text + extracted fields displayed side-by-side for FIELD_COMPLETION
- Inline edit of any extracted field (including claim_type and estimated_loss_amount, regardless of agent confidence)
- Explicit enforcement of the coverage_status = DENIED restriction: the DENIED value must not be available as a direct field edit; it is only settable via COVERAGE_REVIEW WorkItem resolution
- One-click WorkItem resolution with required resolution note field
- Queue view showing all OPEN WorkItems for the logged-in role, sorted by sla_deadline ascending

UI wireframes, resolution-time targets, and accessibility requirements must be specified jointly with the build team before UI development begins [Assumption B6].

### WorkItem Assignment Algorithm
When a WorkItem is created, assigned_to is set as follows:
1. Query active Users (is_active = true) with role matching WorkItem.assigned_role
2. Exclude users with any WorkItem currently IN_PROGRESS
3. Among remaining: select user with fewest OPEN WorkItems; tie-break by earliest last_resolved_at
4. If no eligible user: set assigned_to = null; retry every 60 seconds
5. If sla_deadline - now < 25% of original SLA duration and assigned_to still null: immediately escalate to next role

### Entity: User
```
User:
  id: UUID, primary key, immutable
  name: string, max 100 chars, required
  role: enum [SPECIALIST, SUPERVISOR, CLAIMS_MANAGER, IT_ONCALL], required
  specializations: array of enum [AUTO_COLLISION, AUTO_THEFT, PROPERTY_DAMAGE,
    PROPERTY_THEFT, BODILY_INJURY, LIABILITY], required for SPECIALIST role
  coverage_regions: array of string (2-char state codes), required for SPECIALIST role
  is_active: boolean, required, default true
  last_resolved_at: ISO 8601 timestamp, UTC, nullable
```

### Entity: AuditEvent
```
AuditEvent:
  id: UUID, primary key, immutable
  claim_id: UUID, foreign key to Claim (restrict delete — audit records must not be deleted with claim), required
  event_type: enum [
    CLAIM_RECEIVED,
    PARSING_STARTED, PARSING_COMPLETED, PARSING_LOW_CONFIDENCE,
    FIELD_COMPLETED_BY_HUMAN, FIELD_OVERRIDDEN_BY_HUMAN,
    POLICY_LOOKUP_SUCCESS, POLICY_LOOKUP_NOT_FOUND, POLICY_LOOKUP_FAILED,
    COVERAGE_VALIDATED, COVERAGE_EXCLUSION_FLAGGED, COVERAGE_CONFIRMED_BY_HUMAN,
    COVERAGE_DENIED_BY_HUMAN,
    SEVERITY_SCORED, SEVERITY_CONFIRMED_BY_HUMAN, SEVERITY_OVERRIDDEN_BY_HUMAN,
    ADJUSTER_ASSIGNED, ADJUSTER_OVERRIDE_BY_HUMAN,
    ACKNOWLEDGMENT_SENT,
    WORKITEM_CREATED, WORKITEM_ASSIGNED, WORKITEM_RESOLVED, WORKITEM_ESCALATED,
    SLA_AT_RISK_ALERT, SLA_BREACHED,
    DMS_STORE_FAILED, DUPLICATE_DETECTED, DUPLICATE_REVIEW_RESOLVED, CALLBACK_TASK_CREATED,
    CLAIM_COMPLETED, CLAIM_HALTED, CLAIM_RESUMED
  ], required
  actor_type: enum [AGENT, HUMAN], required
  actor_id: string, required (agent version string or User.id)
  from_value: string, nullable
  to_value: string, nullable
  timestamp: ISO 8601 timestamp, UTC, immutable
```

Logs are immutable. Retention: 7 years (regulatory compliance). Claimant PII in audit log is stored as salted SHA-256 hashed values: SHA-256(value + claim_id) for name, email, and phone. This is **pseudonymization for audit correlation** — not anonymization. An auditor with access to the claim record can still reverse-correlate via the claim_id salt. Do not cite audit log hashes as evidence of anonymization in compliance filings. Full PII is accessible only through WorkItem and CRM UIs for authorised users.

---

## Processing Modules

### End-to-End Processing Order

Run modules in this order so that inputs exist before they are consumed:

1. **IN-001** (receipt + DMS store) → **IN-002** (parse + enrich) → **IN-003** (duplicate detection)
2. **IN-003** complete (no duplicate or duplicate resolved as DISTINCT/REPLACE) → **PL-001** (policy lookup) — only if parse passes threshold; otherwise FIELD_COMPLETION or DUPLICATE_REVIEW WorkItem holds the claim
3. **PL-001** success → **CV-001** (coverage type check) → **CV-002** (exclusion check)
4. **CV-002** complete with CONFIRMED → **SV-001** (severity scoring) → **SV-002** (escalation check)
5. **SV-002** complete → **RT-001** (adjuster assignment) → **RT-002** (CRM update)
6. **AC-001** (acknowledgment) — triggered as soon as ACKNOWLEDGED status is reachable:
   - Standard path: after RT-002
   - Hold path: immediately when claim enters AWAITING_SEVERITY_REVIEW or AWAITING_ROUTING_OVERRIDE
     (sends INTERIM acknowledgment without adjuster name)

---

### Module IN — Intake & Parsing

**IN-001 — Claim Receipt**
- Trigger: inbound claim event from any channel (email webhook, transcript upload, web form submit)
- **Idempotency check (before creating a Claim record):** check for an existing Claim with the same source_message_id received within the last `DUPLICATE_WINDOW_MINUTES`. If found: discard the incoming event (webhook retry or double-submit); do not create a second Claim; return the existing Claim.id to the caller. Idempotency keys by channel: EMAIL = MIME Message-ID header; PHONE_TRANSCRIPT = upload session ID provided by the transcript system; WEB_FORM = form submission token. Store source_message_id on the Claim record (max 500 chars, nullable for channels that provide no deduplication key).
- Action:
  1. Set Claim.received_at = current UTC timestamp (immutable; SLA clock starts)
  2. Set Claim.processing_status = PARSING
  3. Store raw_input in DMS: POST /documents with document_type = FNOL_RAW (see Integration 3)
  4. Set Claim.raw_input_document_id from DMS response (or null when DMS store fails)
  5. Set Claim.source_channel from inbound channel identifier
  6. Log CLAIM_RECEIVED to AuditEvent
- This step must complete within 30 seconds of receipt; if DMS store fails, log warning and continue (DMS store is non-blocking — see Integration 3 fallback)

**IN-002 — Field Extraction and Enrichment**
- Trigger: immediately after IN-001
- Inputs: raw_input retrieved from DMS by raw_input_document_id when not null; otherwise from in-memory fallback buffer initialized in IN-001; source_channel

**Channel pre-processing before NLP extraction:**
- EMAIL: extract body text only; strip headers and footers; if attachments present (PDF or text), append attachment text after body; images in attachments are noted in a ParsedField with field_name = "attachment_images_present" and extracted_value = "true" (for adjuster review later — not processed by V1)
- PHONE_TRANSCRIPT: look for lines prefixed "Caller:" or "Customer:" (case-insensitive); extract only those lines as the claimant's text for NLP; agent/representative lines are preserved in raw_input but excluded from field extraction
- WEB_FORM: treat named form fields as pre-extracted with confidence = 0.95; treat the free-text "incident description" field as unstructured input for NLP extraction of claim_type, bodily_injury, and multiple_parties

**Required fields and extraction rules:**
| Field | Extraction method | Required? |
|---|---|---|
| policy_number | NLP + regex (pattern: [A-Z]{2,3}-\d{6,10} or as defined by Integration 2 WSDL [Assumption A1]) | Yes |
| claimant contact | NLP entity extraction: name + (email OR phone) — at least one of email/phone required | Yes |
| claim_type | NLP classification against 6-class enum (AUTO_COLLISION, AUTO_THEFT, PROPERTY_DAMAGE, PROPERTY_THEFT, BODILY_INJURY, LIABILITY); if web form, map from form dropdown | Yes |
| incident_date | NLP date extraction; relative dates ("yesterday", "last Tuesday") resolved to absolute date using received_at | Yes |
| incident_location | NLP location extraction; derive incident_state from location string | No (nullable) |
| estimated_loss_amount | NLP numeric extraction; currency normalised to USD | No (nullable) |
| bodily_injury_mentioned | Binary NLP classification: true if any of: injury, hurt, injured, hospital, ambulance, pain, medical treatment, fracture, broken bone, broken arm, broken leg, broken rib found in text. "broken" alone is NOT a trigger — must be followed by a body-part term. | No (but flags bodily_injury_flag) |
| multiple_parties_mentioned | Binary NLP: true if: other driver, third party, another vehicle, other person involved | No (but flags multiple_parties_flag) |

**Unknown label policy (no `OTHER` enum in V1):**
- If NLP classifier outputs a label outside the 6 allowed claim types, treat claim_type as missing data.
- Set parse_confidence to 0.00 for claim_type and route to FIELD_COMPLETION (AWAITING_FIELD_COMPLETION).
- Log PARSING_LOW_CONFIDENCE with `low_confidence_fields = [{"field":"claim_type","confidence":0.00}]`.
- The system MUST NOT invent new enum values at runtime.

**Confidence and thresholds:**
- parse_confidence = minimum confidence across the 4 required fields (policy_number, claimant contact, claim_type, incident_date)
- If parse_confidence ≥ PARSE_CONFIDENCE_THRESHOLD (0.90) AND all 4 required fields present:
  - Attempt CRM enrichment: GET /contacts?email={email}&phone={phone} (see Integration 1, Endpoint 1)
  - Set claimant_id from CRM response (or leave null if not found — not a blocking failure)
  - Set processing_status = POLICY_LOOKUP; proceed to PL-001
- If parse_confidence < PARSE_CONFIDENCE_THRESHOLD OR any required field missing:
  - Create WorkItem of type FIELD_COMPLETION (see content schema below)
  - Set processing_status = AWAITING_FIELD_COMPLETION
  - Trigger AC-001 (INTERIM acknowledgment — claim received, reference number, adjuster will contact)

**FIELD_COMPLETION WorkItem content:**
```json
{
  "claim_id": "<uuid>",
  "source_channel": "<channel>",
  "raw_input_preview": "<first 500 chars of raw_input>",
  "extracted_fields": [
    { "field_name": "<name>", "extracted_value": "<value>", "confidence": 0.00, "raw_span": "0-45" }
  ],
  "missing_or_low_confidence_fields": ["<field_name>", ...],
  "agent_note": "<reason for low confidence>"
}
```
SLA: WorkItem must be resolved within 20 minutes during operating hours; unresolved after 20 minutes → escalate to SUPERVISOR.

**IN-003 — Duplicate Detection**
- Trigger: immediately after IN-002 (only if IN-002 exits with processing_status = POLICY_LOOKUP; not triggered for claims already in AWAITING_FIELD_COMPLETION)
- Inputs: Claim.policy_number, Claim.incident_date, Claim.claimant_id (or claimant email/phone SHA-256 hash if claimant_id is null)
- Action: query the FPA claim store for claims received in the past `DUPLICATE_WINDOW_MINUTES` where ALL of the following match:
  - policy_number = this claim's policy_number, AND
  - incident_date = this claim's incident_date, AND
  - claimant_id = this claim's claimant_id (if both non-null), OR SHA-256(email) or SHA-256(phone) matches if claimant_id is null
- If no match: continue to PL-001 (no action)
- If match found:
  - Log DUPLICATE_DETECTED
  - Create DUPLICATE_REVIEW WorkItem (see content schema below); set assigned_role = SPECIALIST
  - Set processing_status = AWAITING_DUPLICATE_REVIEW
  - Do NOT proceed to PL-001 until WorkItem is resolved
  - INTERIM acknowledgment: if not already sent, trigger AC-001 (INTERIM) with note that the claim is under review

**DUPLICATE_REVIEW WorkItem content:**
```json
{
  "claim_id": "<uuid of this claim>",
  "duplicate_candidate_id": "<uuid of matching claim>",
  "duplicate_candidate_received_at": "<ISO 8601>",
  "match_basis": "<policy_number+incident_date+claimant_id | policy_number+incident_date+email_hash | ...>",
  "agent_note": "Potential duplicate FNOL. Review both claims and choose a resolution."
}
```
**Resolution options (specialist selects one):**
- `MERGE`: this claim is a true duplicate; discard this claim, continue processing the earlier duplicate_candidate_id; set this claim's processing_status = HALTED with halt_reason = "DUPLICATE: merged into {duplicate_candidate_id}"
- `DISTINCT`: claims are distinct (different incidents or different parties); resume this claim from POLICY_LOOKUP; log DUPLICATE_REVIEW_RESOLVED
- `REPLACE`: this claim supersedes the earlier one (claimant resubmitted with corrections); halt duplicate_candidate_id, resume this claim from POLICY_LOOKUP; log DUPLICATE_REVIEW_RESOLVED on both claims

WorkItem SLA: 20 minutes during operating hours; escalate to SUPERVISOR after 20 minutes.

---

### Module PL — Policy Lookup

**PL-001 — Policy Lookup via SOAP**
- Trigger: processing_status = POLICY_LOOKUP
- Input: Claim.policy_number
- Action: call GetPolicyByNumber SOAP operation (see Integration 2)
- On success (policy found):
  - Populate: policy_id, policy_status, policy_effective_date, policy_expiration_date, coverage_types_list, exclusions_list; also store deductible_amount and coverage_limits (reserved for V2 adjuster-facing use — not consumed by any V1 processing module)
  - Evaluate policy_status:
    - ACTIVE: proceed to CV-001
    - LAPSED or CANCELLED or SUSPENDED: set coverage_status = LAPSED; create COVERAGE_REVIEW WorkItem; set processing_status = AWAITING_COVERAGE_REVIEW; trigger AC-001 (INTERIM)
- On PolicyFault POLICY_NOT_FOUND:
  - Do NOT set any coverage fields
  - Create FIELD_COMPLETION WorkItem with note "Policy number {policy_number} not found in policy admin system. Please verify policy number with claimant."
  - Set processing_status = AWAITING_FIELD_COMPLETION
- On SOAP fault or timeout:
  - Retry per Integration 2 retry spec
  - If all retries fail: create SOAP_FAILURE WorkItem; set processing_status = HALTED; alert IT_ONCALL

---

### Module CV — Coverage Validation

**CV-001 — Coverage Type Check**
- Trigger: processing_status = COVERAGE_VALIDATION, policy_status = ACTIVE
- Hard constraint: the agent MUST NOT set coverage_status = DENIED. Only a human via WorkItem resolution may set DENIED. The agent sets EXCLUDED, DISPUTED, or LAPSED only.
- Action:
  1. Check: claim_type ∈ policy coverage_types_list
  2. Check: incident_date ∈ [policy_effective_date, policy_expiration_date] (inclusive)
  3. If both conditions true: proceed to CV-002
  4. If claim_type NOT in coverage_types_list: set coverage_status = EXCLUDED; create COVERAGE_REVIEW WorkItem (type: coverage exclusion confirmed); set processing_status = AWAITING_COVERAGE_REVIEW; trigger AC-001 (INTERIM)
  5. If incident_date outside policy period: set coverage_status = EXCLUDED; same as above with note "Incident date outside policy coverage period"

**CV-002 — Exclusion Check**
- Trigger: CV-001 passes (claim_type in coverage_types, incident_date in period)
- Action: call CheckExclusions SOAP operation with policy_id, incident description, claim_type (see Integration 2)
- If excluded = false (no exclusion match): set coverage_status = CONFIRMED; proceed to SV-001
- If excluded = true AND any matched exclusion has similarity ≥ EXCLUSION_SIMILARITY_THRESHOLD:
  - Set coverage_status = DISPUTED
  - Create COVERAGE_REVIEW WorkItem (content includes: exclusion clause text, matched phrases, similarity score, incident description)
  - Set processing_status = AWAITING_COVERAGE_REVIEW
  - Trigger AC-001 (INTERIM)
- If CheckExclusions SOAP fails (any fault after retries): log error; create SOAP_FAILURE WorkItem; set processing_status = HALTED; alert IT_ONCALL. Do NOT proceed to severity scoring with unverified exclusion status. This is the same halt behaviour as PL-001 SOAP failure — consistent with the Artifact 2 constraint that processing does not continue on unverified coverage.

**COVERAGE_REVIEW WorkItem content:**
```json
{
  "claim_id": "<uuid>",
  "coverage_status": "<EXCLUDED|DISPUTED|LAPSED>",
  "claim_type": "<type>",
  "policy_coverage_types": ["<type>", ...],
  "incident_date": "<date>",
  "policy_effective_date": "<date>",
  "policy_expiration_date": "<date>",
  "matched_exclusions": [
    { "code": "<code>", "text": "<clause text>", "similarity": 0.00 }
  ],
  "agent_recommendation": "<confirm exclusion / confirm coverage / review required>",
  "incident_description_preview": "<first 300 chars>"
}
```
Assigned to SUPERVISOR. SLA: 45 minutes during operating hours; escalate to CLAIMS_MANAGER after 45 minutes.
**Resolution requirement:** when the supervisor resolves this WorkItem with decision = DENIED, Claim.coverage_denial_reason (max 1000 chars) is a required field — the resolution must not be submittable without it. The WorkItem UI must enforce this: the DENIED resolution path shows a mandatory free-text reason field before submission. The agent must not set coverage_denial_reason; it is only written via WorkItem resolution.

---

### Module SV — Severity Classification

**SV-001 — Severity Scoring**
- Trigger: processing_status = SEVERITY_SCORING (coverage_status = CONFIRMED or human-confirmed)
- Inputs: claim_type, estimated_loss_amount, bodily_injury_flag, multiple_parties_flag, policy_status, coverage_status, claimant_id (for prior claims query)

**Scoring rules (additive):**
| Condition | Points |
|---|---|
| estimated_loss_amount is null (unknown) | +2 |
| estimated_loss_amount < $10,000 | +1 |
| $10,000 ≤ estimated_loss_amount < $50,000 | +2 |
| $50,000 ≤ estimated_loss_amount < $150,000 | +4 |
| estimated_loss_amount ≥ $150,000 | +6 |
| bodily_injury_flag = true | +3 |
| claim_type = LIABILITY | +2 |
| multiple_parties_flag = true | +1 |
| Prior FNOL claims by this claimant_id in past SERIAL_CLAIMANT_WINDOW_DAYS ≥ SERIAL_CLAIMANT_THRESHOLD | +1 (flag for adjuster note; does not change severity level alone). **Data source:** use `prior_claims_count` from CRM Endpoint 1 (returned during IN-002 enrichment) as the authoritative value — it covers claims predating FPA deployment. The FPA's own claim store supplements this after 12 months of operation. If CRM contact not found (claimant_id = null): score 0 for this component and log absence in SEVERITY_SCORED AuditEvent. |

**Scoring note:** The null estimated_loss row scores +2 — higher than the known-small (<$10K) row at +1. Absent loss information is itself a risk signal: the claimant either has not yet assessed the damage or has chosen not to state it. Both cases warrant more cautious adjuster attention than a confidently stated small loss.

**Severity level derivation:**
- Score 1–3: LOW
- Score 4–5: MEDIUM
- Score 6–7: HIGH
- Score ≥ 8: CRITICAL

**Threshold rationale:** CRITICAL (≥ 8) requires at least two compounding risk factors, or one extreme factor combined with a secondary signal. For example: high financial loss ($150K+, +6 points) alone reaches HIGH (6); it requires bodily injury (+3) to reach CRITICAL (9). LIABILITY + bodily injury + loss ≥ $50K (+2+3+4 = 9) also reaches CRITICAL. A claim with only financial risk ($150K+, no injury, no liability) scores HIGH — which still receives human review via is_high_value = true. The boundary reflects the design assumption that compound risk is categorically more dangerous than any single factor in isolation. Pending calibration against historical outcome data [Assumption D3].

Set Claim.severity_score and Claim.severity_level. Log SEVERITY_SCORED.

**SV-002 — Escalation Check**
- If severity_level = HIGH or CRITICAL OR is_high_value = true OR bodily_injury_flag = true:
  - Create SEVERITY_REVIEW WorkItem
  - Set processing_status = AWAITING_SEVERITY_REVIEW
  - Trigger AC-001 (INTERIM) if not already triggered
- If severity_level = LOW or MEDIUM AND is_high_value = false AND bodily_injury_flag = false:
  - Proceed directly to RT-001

**SEVERITY_REVIEW WorkItem content:**
```json
{
  "claim_id": "<uuid>",
  "agent_severity_score": 0,
  "agent_severity_level": "<level>",
  "scoring_components": [
    { "condition": "<condition>", "points": 0 }
  ],
  "is_high_value": false,
  "bodily_injury_flag": false,
  "estimated_loss_amount": 0.00,
  "claim_type": "<type>",
  "agent_recommended_adjuster_specialization": "<type>",
  "agent_note": "<free text>"
}
```
Assigned to SUPERVISOR. SLA: 30 minutes during operating hours; escalate to CLAIMS_MANAGER after 30 minutes.
After supervisor resolves: supervisor may confirm severity_level or override it; agent proceeds to RT-001 with the confirmed/overridden severity_level.

---

### Module RT — Routing

**RT-001 — Adjuster Assignment**
- Trigger: processing_status = ROUTING
- Inputs: claim_type, severity_level, incident_state, bodily_injury_flag

**Assignment algorithm:**
1. Query CRM Endpoint 2: GET /users with role=adjuster, specialization includes claim_type, is_active=true (see Integration 1)
   **Bodily injury exception:** when bodily_injury_flag = true, additionally require that the adjuster's specializations array includes BODILY_INJURY. This selects only adjusters dual-qualified for both the primary claim_type and bodily injury handling. A LIABILITY adjuster without BODILY_INJURY in their specializations must not receive a bodily-injury-flagged claim. If no dual-qualified adjuster is available after step 5, fall through to the ROUTING_OVERRIDE WorkItem path — do NOT relax the dual-qualification requirement.
2. Filter by: incident_state ∈ user.coverage_regions
3. Filter out: users with open_claims_count ≥ MAX_ADJUSTER_QUEUE_SIZE
4. From remaining: rank by open_high_severity_claims_count ascending, then by open_claims_count ascending; select top rank (first eligible)
5. If no eligible adjuster after filters:
   - Create ROUTING_OVERRIDE WorkItem (assigned to SUPERVISOR)
   - Set processing_status = AWAITING_ROUTING_OVERRIDE
   - If INTERIM acknowledgment not yet sent: trigger AC-001 (INTERIM)
   - Do NOT assign a wrong-specialty adjuster as fallback
6. If eligible adjuster found: set Claim.assigned_adjuster_id; proceed to RT-002

**ROUTING_OVERRIDE WorkItem content:**
```json
{
  "claim_id": "<uuid>",
  "claim_type": "<type>",
  "severity_level": "<level>",
  "incident_state": "<state>",
  "available_adjusters_checked": 0,
  "filter_result": "<reason no adjuster found: queue full / no coverage region / no specialization>",
  "agent_note": "All eligible adjusters for this claim type and region are at queue capacity."
}
```
Assigned to SUPERVISOR. SLA: 15 minutes; escalate to CLAIMS_MANAGER after 15 minutes.

**RT-002 — CRM Claim Record Create/Update**
- Trigger: after RT-001 (or after ROUTING_OVERRIDE is resolved by human)
- Action: POST /claims to Salesforce CRM (see Integration 1, Endpoint 3)
- Request body:
```json
{
  "fnol_id": "<Claim.id>",
  "claimant_id": "<claimant_id>",
  "policy_number": "<policy_number>",
  "claim_type": "<claim_type>",
  "severity_level": "<severity_level>",
  "coverage_status": "<coverage_status>",
  "assigned_adjuster_id": "<adjuster_id>",
  "received_at": "<ISO 8601>",
  "sla_deadline": "<ISO 8601>",
  "incident_date": "<ISO 8601>",
  "incident_location": "<string>",
  "estimated_loss_amount": 0.00,
  "bodily_injury_flag": false,
  "source_channel": "<channel>"
}
```
- On success: set Claim.crm_claim_id from response; set processing_status = ACKNOWLEDGED; proceed to AC-001
- On CRM failure: retry per Integration 1 retry spec; if all retries fail: create SYSTEM_ERROR WorkItem; alert IT_ONCALL

---

### Module AC — Acknowledgment

**AC-001 — Claimant Acknowledgment**
- Trigger: processing_status reaches ACKNOWLEDGED — OR — claim enters any AWAITING_* state AND this is the first time that status is reached (sends INTERIM acknowledgment)
- Acknowledgment types:
  - **FULL**: sent when adjuster is already assigned. Contains: claim reference, adjuster name + direct phone/email, next-contact commitment by severity (LOW/MEDIUM: within 24h; HIGH: within 4h; CRITICAL: within 2h)
  - **INTERIM**: sent when claim is in human review (adjuster not yet assigned). Contains: claim reference, "An adjuster will contact you within 24 hours (or sooner for urgent claims)". Does NOT name an unconfirmed adjuster.

- Delivery by channel:
  - EMAIL source: send via CRM Endpoint 4 to claimant email
  - WEB_FORM source: trigger CRM Endpoint 4 (email); also set portal status to "Received and Processing"
  - PHONE_TRANSCRIPT source: if claimant email available in CRM, send via CRM Endpoint 4; also create an adjuster callback task in CRM and log `CALLBACK_TASK_CREATED`
    If no email available: create callback task only; log warning that email acknowledgment was not possible

- If sending INTERIM: set Claim.interim_acknowledged_at = current UTC timestamp
- If sending FULL: set Claim.full_acknowledged_at = current UTC timestamp
- (Claim.acknowledged_at = computed COALESCE; set automatically)
- Log ACKNOWLEDGMENT_SENT (to_value = "FULL" or "INTERIM")

**If INTERIM was sent and routing completes later:**
- When processing_status transitions to COMPLETED: send a follow-up FULL acknowledgment (with adjuster name) to claimant via same channel. Set Claim.full_acknowledged_at = current UTC timestamp. Log ACKNOWLEDGMENT_SENT with to_value = "FULL".

**AC-002 — SLA Monitoring**
- **Operating hours note:** Claim SLA (received_at + 2 hours) counts on calendar time, 24/7. WorkItem SLAs count only during operating hours [Assumption C1: assumed M–F 08:00–18:00 local time]. Claims received outside operating hours that enter an AWAITING_* state will breach the Claim SLA if an INTERIM acknowledgment has not already been sent. The autonomous INTERIM acknowledgment path has no operating-hours dependency — it fires at any time.
- Runs on two triggers:
  1. On every processing_status change for any Claim
  2. On a background timer: every 5 minutes, evaluate all Claims with processing_status ≠ COMPLETED and processing_status ≠ HALTED
- SLA computation:
  - time_remaining = Claim.sla_deadline - now
  - If acknowledged_at is not null: sla_status remains as set at acknowledgment time (do not retroactively change)
  - Else if now > Claim.sla_deadline:
    - Set sla_status = BREACHED
    - Log SLA_BREACHED
    - Notify CLAIMS_MANAGER
  - Else if time_remaining ≤ SLA_AT_RISK_BUFFER_MINUTES:
    - Set sla_status = AT_RISK
    - Log SLA_AT_RISK_ALERT
    - Notify assigned SUPERVISOR via CRM notification (push to supervisor dashboard)
    - If any OPEN WorkItem exists for this claim: escalate WorkItem immediately (do not wait for WorkItem SLA timer)
  - Else:
    - sla_status = ON_TRACK

---

## Integration Contracts

### Integration 1 — Salesforce CRM (REST API)

**Purpose:** Claimant lookup, adjuster query, claim record creation, acknowledgment delivery
**Authentication:** OAuth 2.0 client credentials; credentials and token endpoint URL are deployment configuration items provided by IT [Assumption A3]
**Base URL:** `[CRM_BASE_URL]` — to be provided by client IT team [Assumption A3]
**Timeout:** 5 seconds per request
**Retry:** HTTP 5xx → 3 retries, exponential backoff; intervals are deployment configuration items. HTTP 4xx → no retry; log error.
**Rate limits:** Must be confirmed with client IT before build [Assumption A3]; implement configurable rate limits (`CRM_RATE_LIMIT_SUSTAINED_RPM`, `CRM_RATE_LIMIT_BURST_RPM` deployment config). 429 handling: honor `Retry-After` header if present; otherwise exponential backoff; on final failure create SYSTEM_ERROR WorkItem.
**Authentication failure:** If token refresh fails after retries: create SYSTEM_ERROR WorkItem; set sla_status = AT_RISK for all claims currently in processing; alert IT_ONCALL. Do not proceed with CRM calls during token failure.

**Endpoint 1 — Claimant lookup:**
```
GET /contacts?email={email}&phone={phone}
(at least one of email or phone required; both preferred)
Response 200:
{
  "contact_id": string,
  "name": string,
  "email": string (nullable),
  "phone": string (nullable),
  "prior_claims_count": integer,   ← for SERIAL_CLAIMANT scoring in SV-001; window must match SERIAL_CLAIMANT_WINDOW_DAYS (default 365 days) — confirm with CRM admin whether this field is a rolling 365-day count or a lifetime count; if lifetime, the SERIAL_CLAIMANT signal will be miscalibrated [See Assumption A6 — Additional validation required (claimant contact records)]
  "policy_numbers": [string]
}
Response 404: no matching contact (non-blocking; claimant_id remains null)
```

**Endpoint 2 — Adjuster query:**
```
GET /users?role=adjuster&specialization={claim_type}&region={incident_state}&active=true
Response 200:
{
  "adjusters": [
    {
      "id": string,
      "name": string,
      "direct_phone": string,
      "direct_email": string,
      "specializations": [string],
      "coverage_regions": [string],
      "open_claims_count": integer,
      "open_high_severity_claims_count": integer
    }
  ]
}
```

**Endpoint 3 — Create claim record:**
```
POST /claims
Request body: (see RT-002 above)
Response 200:
{
  "crm_claim_id": string,
  "created_at": ISO 8601 timestamp
}
Response 422: validation error (e.g., invalid adjuster_id) → create SYSTEM_ERROR WorkItem; do not retry
```

**Endpoint 4 — Send acknowledgment:**
```
POST /communications
Request:
{
  "contact_id": string,
  "channel": "EMAIL",
  "template_id": "FNOL_ACK_FULL_V1" | "FNOL_ACK_INTERIM_V1",
  "variables": {
    "claim_reference": string,           ← formatted as "FNOL-{YYYY}-{claim_id_short}"
    "adjuster_name": string,             ← omitted in INTERIM template
    "adjuster_phone": string,            ← omitted in INTERIM template
    "adjuster_email": string,            ← omitted in INTERIM template
    "next_contact_by": ISO 8601 timestamp  ← omitted in INTERIM; "within 24h" is baked into INTERIM template
  }
}
Response 200: { "communication_id": string, "sent_at": ISO 8601 timestamp }
Response 404: contact_id not found → log error; create SYSTEM_ERROR WorkItem; a specialist must manually send the acknowledgment. Direct SMTP is out of scope for V1 — no SMTP integration contract exists in this spec.
```

---

### Integration 2 — Legacy Policy Administration System (SOAP)

**Purpose:** Policy lookup and exclusion check
**Authentication:** WS-Security token; credentials provided by IT [Assumption A3]
**WSDL:** `[POLICY_ADMIN_BASE_URL]/PolicyService?wsdl` — to be provided by client IT [Assumption A1]
**Base URL:** `[POLICY_ADMIN_BASE_URL]` — to be provided by client IT [Assumption A3]

**Timeout:** 10 seconds (legacy system; allow generous timeout)
**Retry:** SOAP fault → 3 retries, exponential backoff; connection timeout → 3 retries, exponential backoff. HTTP 4xx (proxy errors) → no retry; create SOAP_FAILURE WorkItem immediately. Retry intervals are deployment configuration items.
**Rate limits:** Must be confirmed with client IT before build [Assumption A3]; implement configurable rate limits (`SOAP_RATE_LIMIT_SUSTAINED_RPM`, `SOAP_RATE_LIMIT_BURST_RPM` deployment config).
**Concurrency:** Limit concurrent SOAP calls via the `MAX_SOAP_CONCURRENT_CALLS` configuration parameter (see Configuration Parameters table). If all connections occupied, incoming requests queue (do not fail fast). Pool size must be confirmed with IT before load testing.

**Operation 1 — GetPolicyByNumber:**
- **Input:** policyNumber (string, max 20 chars)
- **Returns — success:** policyId, status (ACTIVE|LAPSED|CANCELLED|SUSPENDED), effectiveDate (YYYY-MM-DD), expirationDate (YYYY-MM-DD), deductibleAmount (decimal), coverageTypes (list of strings), coverageLimits (list of {coverageType, amount}), exclusions (list of {code, text})
- **Returns — fault (POLICY_NOT_FOUND):** fault code POLICY_NOT_FOUND with message string

Note: exact SOAP element names and namespace are defined in the WSDL from IT [Assumption A1]. Coverage type codes in the response require mapping to the FPA's internal claim_type enum [Assumption A2]; the mapping table is a deployment configuration item.

**Operation 2 — CheckExclusions:**
- **Input:** policyId (string), incidentDescription (text extracted from claim), claimType (string)
- **Returns — success:** excluded (boolean), matchedExclusions (list of {code, text, similarity: decimal 0.00–1.00})
- **Returns — fault:** INVALID_POLICY_ID or SERVICE_UNAVAILABLE

On INVALID_POLICY_ID fault: log error; create SOAP_FAILURE WorkItem; set processing_status = HALTED; alert IT_ONCALL (policy record inconsistency — cannot verify exclusion status without a valid policy ID).
On SERVICE_UNAVAILABLE fault (after retries): create SOAP_FAILURE WorkItem; set processing_status = HALTED; alert IT_ONCALL.

Note: exact SOAP element names and namespace are defined in the WSDL from IT [Assumption A1].

**Fallback if SOAP unavailable:** Do NOT proceed with unverified coverage. Create SOAP_FAILURE WorkItem; halt claim processing; alert IT_ONCALL. This is the hardest failure mode — no workaround in V1.

---

### Integration 3 — Document Management System (REST)

**Purpose:** Store raw claim input; retrieve for processing
**Authentication:** API key; mechanism and credentials provided by IT [Assumption A3, A4]
**Base URL:** `[DMS_BASE_URL]` — to be provided by client IT [Assumption A3]
**Timeout:** 5 seconds
**Retry:** HTTP 5xx → 2 retries, exponential backoff; intervals are deployment configuration items
**Rate limits:** Must be confirmed with client IT before build [Assumption A4]; implement configurable rate limits (`DMS_RATE_LIMIT_SUSTAINED_RPM`, `DMS_RATE_LIMIT_BURST_RPM` deployment config).

**Endpoint 1 — Store document:**
```
POST /documents
Request:
{
  "claim_id": string,
  "document_type": "FNOL_RAW" | "PARSED_CLAIM",
  "content_base64": string (base64-encoded UTF-8 text),
  "content_type": "text/plain" | "application/pdf",
  "source_channel": string
}
Response 200: { "document_id": string, "stored_at": ISO 8601 timestamp }
Response 413: content too large (>10MB) → log warning; proceed without storing; alert IT
```

**Fallback:** DMS is non-blocking for intake. If DMS unavailable at IN-001: log warning, proceed with processing (raw_input held in memory for duration of claim processing session), retry DMS store every 60 seconds for up to 30 minutes. If still failing after 30 minutes: alert IT_ONCALL; document processing continues in-memory but compliance gap exists.

---

## Escalation Summary

| WorkItem Type | Trigger | Assigned Role | SLA | Timeout Action |
|---|---|---|---|---|
| FIELD_COMPLETION | Parse confidence < PARSE_CONFIDENCE_THRESHOLD or required field missing | SPECIALIST | 20 min | Escalate to SUPERVISOR |
| DUPLICATE_REVIEW | Duplicate candidate found in DUPLICATE_WINDOW_MINUTES; sets AWAITING_DUPLICATE_REVIEW | SPECIALIST | 20 min | Escalate to SUPERVISOR |
| COVERAGE_REVIEW | Exclusion match, lapsed policy, or claim type mismatch | SUPERVISOR | 45 min | Escalate to CLAIMS_MANAGER |
| SEVERITY_REVIEW | HIGH/CRITICAL severity, is_high_value, or bodily_injury_flag | SUPERVISOR | 30 min | Escalate to CLAIMS_MANAGER |
| ROUTING_OVERRIDE | No eligible adjuster available | SUPERVISOR | 15 min | Escalate to CLAIMS_MANAGER |
| SOAP_FAILURE | Policy admin SOAP failure (PL-001 or CV-002) after all retries | IT_ONCALL | 30 min | Manual policy lookup or exclusion check by specialist |
| SYSTEM_ERROR | Any other integration failure after retries | IT_ONCALL | 1 hour | Manual processing |

---

## Deployment Strategy

**Phase 0 — Shadow mode (weeks 1–4 of pilot):** The FPA runs against live inbound claims but makes no autonomous decisions. All outputs (extracted fields, coverage recommendations, severity scores, routing proposals) are logged and compared against specialist decisions. Shadow metrics establish baseline accuracy before any autonomous action is taken.

**Phase 1 — Partial rollout (weeks 5–8):** EMAIL channel claims only; low-complexity filter: claim_type ∈ {AUTO_COLLISION, AUTO_THEFT, PROPERTY_DAMAGE, PROPERTY_THEFT} AND estimated_loss_amount < $10,000 AND bodily_injury_flag = false. Autonomous processing enabled for this subset. All other claims follow shadow-mode path. Pilot accuracy metrics reviewed weekly.
Note: the bodily_injury_flag = false condition is the materially restrictive element — hard constraint C2 would already hold any bodily-injury-flagged claim for SEVERITY_REVIEW regardless of claim_type. Making it explicit in the Phase 1 filter ensures the rollout boundary is transparent and does not depend implicitly on a downstream hard constraint to enforce it. LIABILITY is excluded despite potentially scoring LOW/MEDIUM because its +2 severity weight reflects third-party exposure and latent litigation risk that does not always manifest in the initial estimated loss figure — a $8,000 LIABILITY claim can escalate in ways a $8,000 AUTO_COLLISION claim typically does not. Relaxing this exclusion is a candidate Phase 2 decision once pilot data establishes autonomous handling quality for the included claim types. Note: the fraction of total volume this filter admits depends on channel distribution and loss-amount distribution — both unknown at spec time. Builder must estimate from historical intake data before Phase 1 rollout begins.

**Phase 2 — Full autonomous path (week 9+):** All claim types enabled once Phase 1 accuracy thresholds are met (per Artifact 4 production readiness table). Human shadow review shifts from full-sample to 10% random audit.

**Kill switch:** A deployment configuration flag (`AUTONOMOUS_PROCESSING_ENABLED`, default false) must be present before go-live. Setting it to false reverts all claims to AWAITING_FIELD_COMPLETION WorkItems (full human review) without code changes. Operations team must have documented procedure for activating the kill switch in under 5 minutes.

**Operating cost note:** Agent operates 24/7 per the SLA requirements. Cost estimate: ~5–8% of 300 claims/day × 365 calendar days = ~5,500–8,800 complex reasoning calls/year × $1–$2/call = ~$5,500–$17,600/year. Materially below the $115K–$135K/year rework elimination value quantified in Artifact 1, and well below any realistic estimate of conditional capacity redeployment value. Builder must validate against chosen model provider's actual per-call pricing before go/no-go.

---

## Audit & Logging

Every Claim state transition and every human action must produce an AuditEvent (see entity definition above). Logs are immutable, append-only. 7-year retention.

**Required to_value content for key events (to_value is mandatory for these; nullable only for events listed below):**
- `PARSING_COMPLETED`: to_value = `{"claim_type": "<value>", "confidence": 0.00, "parse_confidence": 0.00}` — required; this is the record that enables retrospective classification accuracy audits
- `PARSING_LOW_CONFIDENCE`: to_value = `{"missing_fields": ["<field>"], "low_confidence_fields": [{"field": "<name>", "confidence": 0.00}]}`
- `SEVERITY_SCORED`: to_value = `{"severity_score": 0, "severity_level": "<level>", "components": [{"condition": "<text>", "points": 0}]}`
- All `*_BY_HUMAN` events: from_value = old value, to_value = new value (both required; nullable only if no prior value existed)

**Applicable regulatory context:** NAIC Unfair Claims Settlement Practices Act (model law; confirm which operating states have adopted it); state DOI acknowledgment timing requirements (see Assumption B4); NAIC Insurance Data Security Model Law (for PII handling and audit log controls). Builder must confirm applicable state-level adoptions with legal before deployment. The 7-year retention period is a conservative default pending legal confirmation of the shortest applicable state requirement.

The supervisor dashboard aggregates:
- Claims in each processing_status, by hour
- SLA_AT_RISK and SLA_BREACHED counts for current shift
- WorkItem open/resolved counts by type
- Autonomous handling rate (claims reaching COMPLETED with no WorkItem created) for current shift

The claims manager dashboard adds:
- Routing accuracy rate (audit sample: adjuster confirmed correct / total sample)
- Coverage review outcome distribution (confirmed / denied / disputed resolved)
- SOAP_FAILURE and SYSTEM_ERROR counts (IT health signal)

---

## Definition Of Done (Spec Handoff)

This specification is ready for implementation handoff only when all items below are true:

- All Priority 1 assumptions in Artifact 5 are validated with named stakeholders and documented outcomes.
- Integration credentials, base URLs, and numeric rate limits are confirmed in environment configuration.
- Claim acknowledgment templates (`FNOL_ACK_FULL_V1`, `FNOL_ACK_INTERIM_V1`) are created and approved in CRM.
- WorkItem UI requirements (Artifact 3 scope note) are agreed with builder and product owner.
- Pilot gates in Artifact 4 are acknowledged by operations and compliance owners.
- Any unresolved assumption is explicitly marked as out-of-scope for V1 with rollback or contingency behavior documented.
