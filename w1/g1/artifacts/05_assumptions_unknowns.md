# Artifact 5 — Assumptions & Unknowns

## How to Read This Document

Every assumption is a bet. If the assumption is wrong, something in the spec breaks. The **Impact if Wrong** column tells you how badly. The **Status** column tells you what is known:

- `[Stated]` — explicitly confirmed in the scenario text
- `[Inferred]` — reasonable inference from context or industry knowledge; not yet validated
- `[Flagged for Validation]` — must be confirmed before building this component; proceeding without validation risks rework

---

## A — System & Integration Assumptions

### A1 — Legacy Policy Admin System Has Documented SOAP Operations
**Statement:** The policy administration system exposes GetPolicyByNumber and CheckExclusions SOAP operations (or functionally equivalent operations) with a WSDL available from the IT team. The coverage type codes in the policy admin system can be mapped to the FPA's internal claim_type enum.
**Why it matters:** The entire PL and CV modules depend on these SOAP calls. If the SOAP API has different operation names, different response schema, or no exclusion-check capability, the spec must be rewritten for those modules.
**Impact if wrong (no exclusion check operation):** CV-002 cannot be built as specified. Exclusion flagging must be implemented differently — possibly as a local rules table populated from the policy admin system's data export. This is a significant rework risk.
**Status:** `[Flagged for Validation]`
**Validation question:** "Can you share the WSDL and any existing API documentation for the policy admin system? Does it have an exclusion-check operation, or are exclusions returned as a list in the policy record itself?"

---

### A2 — Policy Admin Coverage Type Codes Map Cleanly to Claim Types
**Statement:** The coverage type codes in the legacy policy admin system can be deterministically mapped to the FPA's six internal claim_type values (AUTO_COLLISION, AUTO_THEFT, PROPERTY_DAMAGE, PROPERTY_THEFT, BODILY_INJURY, LIABILITY). This mapping is a deployment configuration item, not a runtime decision.
**Why it matters:** CV-001's coverage match logic is "claim_type ∈ policy coverage_types_list." If the legacy system uses codes like "HO3" or "PAP" that don't map cleanly, the FPA would need to implement a more complex coverage interpretation layer.
**Impact if wrong:** The mapping table must be jointly authored with the IT team and legal/underwriting before deployment. This is a documentation dependency, not a code dependency — but it blocks go-live.
**Status:** `[Flagged for Validation]`
**Validation question:** "What are the coverage type codes your policy admin system uses? Can you provide a list of all active coverage codes and their plain-language descriptions?"

---

### A3 — Base URLs and Credentials Available Before Development
**Statement:** IT will provide base URLs and authentication credentials for all three integrations (CRM, policy admin SOAP, DMS) before development begins. SOAP namespace strings are also included.
**Why it matters:** All integration contracts use placeholder URLs. Without real values, integration tests cannot run.
**Impact if wrong:** Development can proceed with mocks, but integration testing is blocked. Each unresolved URL is a delivery risk item.
**Status:** `[Flagged for Validation]`
**Validation question:** "Who is the IT contact who can provide API credentials and base URLs for Salesforce CRM, the policy admin SOAP service, and the DMS?"

---

### A4 — DMS Has a REST API for Document Storage
**Statement:** The document management system exposes an HTTP API for storing and retrieving claim documents. The scenario mentions a DMS but provides no API details.
**Why it matters:** IN-001 stores the raw claim input to DMS immediately on receipt. If the DMS has no API (e.g., it is a file-share system), the storage mechanism must be redesigned.
**Impact if wrong (DMS is file-share only):** Raw input storage becomes a file write operation. This is a simpler integration but changes the Integration 3 spec significantly. Non-blocking for core claim processing but affects audit record completeness.
**Status:** `[Flagged for Validation]`
**Validation question:** "Does the DMS have a REST API for programmatic document storage? If not, how is document storage currently automated (if at all)?"

---

### A5 — CRM Handles Outbound Email Acknowledgments
**Statement:** Salesforce CRM's Endpoint 4 (POST /communications) can send templated emails to claimants. If not, the FPA needs a separate SMTP integration or email service API for acknowledgments.
**Why it matters:** AC-001 sends the claimant acknowledgment via CRM. If CRM cannot send outbound email, an additional integration is required — and the 2-hour SLA delivery depends on that integration working reliably.
**Impact if wrong:** An additional integration contract (email service provider) must be added to the spec and the integration budget. Not a spec-breaking change but a scope addition.
**Status:** `[Inferred]` — Salesforce CRM typically has outbound email capability. Confirm with IT.

---

### A6 — CRM Adjuster Records Include Specialization, Region, and Queue Depth
**Statement:** CRM User records for adjusters include: (1) specialization (list of claim types they handle), (2) coverage_regions (list of state codes), (3) open_claims_count (maintained in real-time or near-real-time). RT-001's assignment algorithm depends on all three attributes being queryable via the CRM API.
**Why it matters:** RT-001 is the primary mechanism for eliminating the 18% routing error rate. If CRM adjuster records lack specialization or region data, the routing logic degrades to queue-depth-only matching — better than the current manual approach but less accurate.
**Impact if wrong (no specialization data):** Routing quality is reduced. A data enrichment project is required before go-live to populate adjuster attributes in CRM. This is a deployment dependency.
**Status:** `[Flagged for Validation]`
**Validation question:** "Do adjuster records in Salesforce CRM include specialization by claim type and geographic coverage regions? Is open claims count a maintained field? If not, can these attributes be added before go-live?"

---

## B — Business Rule Assumptions

### B1 — High-Value Threshold is $50,000 Estimated Loss
**Statement:** A claim is classified as "high-value" (requiring supervisor review before routing) if the estimated loss amount stated in the claim is ≥ $50,000.
**Why it matters:** The HIGH_VALUE_THRESHOLD directly controls how many claims go through the AWAITING_SEVERITY_REVIEW path. At $50K, approximately 10–15% of claims trigger the threshold. At $25K, that rises significantly; at $100K, it drops to perhaps 5%.
**Source:** Working threshold selected in this draft for buildability. Not confirmed in a formal policy document.
**Impact if wrong:** Either too many claims in human review queue (threshold too low → throughput degraded) or high-value claims being autonomously routed (threshold too high → financial exposure).
**Status:** `[Flagged for Validation]`
**Validation question:** "Is $50,000 estimated loss the formal threshold for 'high-value' claim review? Is the threshold uniform across claim types, or does it differ (e.g., lower for liability, higher for property)?"

---

### B2 — Bodily Injury Always Requires Human Review, Regardless of Financial Value
**Statement:** Any claim where bodily injury is mentioned — regardless of estimated loss amount — is held for supervisor review before adjuster routing. This applies even for seemingly minor injuries (e.g., "I have a small bruise").
**Why it matters:** This is the C2 hard constraint in this draft. If the business later decides that minor injury claims can be auto-routed, the SV-002 escalation logic must be updated. The current spec treats this as binary (bodily_injury_flag = true → always escalate).
**Impact if wrong (if there is a severity threshold for bodily injury):** A graduated approach would be needed: e.g., self-reported minor injury at LOW severity could be auto-routed to a combined auto/injury adjuster. This would increase autonomous handling rate but requires a more nuanced escalation rule.
**Status:** `[Inferred — draft boundary choice pending stakeholder validation]`
**Validation question:** "Is any bodily injury claim a hard escalation regardless of apparent severity, or is there a threshold (e.g., hospitalisation required) below which bodily injury claims can be auto-routed?"

---

### B3 — Coverage Denial is a Human-Only Decision with Regulatory Basis
**Statement:** No AI agent can autonomously deny coverage on a claim. The agent can identify a clear coverage exclusion (coverage_status = EXCLUDED), but a human specialist must review and confirm the denial before any communication is sent to the claimant. This has a regulatory basis under state insurance regulations.
**Why it matters:** This is the C1 hard constraint. If this is wrong — e.g., if for certain clear-cut exclusions the regulatory framework permits automated denial — then coverage_status = DENIED could potentially be set autonomously for some claim types. The current spec treats this as absolute.
**Impact if wrong (upside):** For very clear exclusions (e.g., policy explicitly cancelled before incident date), autonomous denial processing would increase throughput and reduce the AWAITING_COVERAGE_REVIEW queue. But this is a significant legal risk to take on without explicit regulatory sign-off.
**Status:** `[Inferred — conservative legal-control choice; regulatory basis not specifically cited in scenario]`
**Validation question:** "Is coverage denial automation prohibited by regulation in your operating states, or is it an internal policy choice? Has legal reviewed this constraint?"

---

### B4 — Regulatory Exposure from SLA Non-Compliance
**Statement:** The 2-hour acknowledgment SLA may be tighter than many state DOI regulatory floors (which vary by state and line of business). Financial exposure should be treated primarily as audit/remediation risk unless legal confirms direct per-breach penalties for specific jurisdictions.
**Why it matters:** This underpins the regulatory compliance value lever in the business case. If any operating states have a 2-hour acknowledgment requirement in regulation, the per-breach financial exposure could be significant. If no states have this requirement, the regulatory risk is audit risk, not direct fine risk.
**Impact if wrong (if fines apply):** Financial exposure is higher, strengthening the business case. If fines do NOT apply, the regulatory lever is reframed as "audit risk reduction" rather than direct financial exposure.
**Status:** `[Inferred — requires legal and compliance validation with state-level citations]`
**Validation question:** "In which states does the company operate? Do any operating states have regulations requiring FNOL acknowledgment within 2 hours or faster? What were the specific findings in the last DOI audit?"

---

### B5 — Phone Transcripts Are Post-Call, Not Real-Time
**Statement:** When a claimant calls to report a loss, the call is handled by a call centre agent (not the FPA). After the call, a transcript is uploaded to the intake system, at which point the FPA begins processing. The FPA does not process calls in real-time.
**Why it matters:** If phone transcripts are available in real-time (i.e., from a live transcription feed), the FPA could begin processing during the call — potentially acknowledging the claimant before they hang up. This would significantly change the SLA profile for the phone channel.
**Impact if wrong (real-time transcription available):** A real-time processing path could be added as a Phase 2 enhancement. V1 is designed for post-call uploads, which is the simpler and more reliable integration pattern.
**Status:** `[Inferred — standard call centre practice; not stated in scenario]`
**Validation question:** "Does the call centre use real-time transcription? Is the transcript available immediately on call completion, or is there a processing delay before upload? Who uploads the transcript — the agent, or is it automated?"

---

## C — Operational Assumptions

### C1 — Operating Hours and SLA Calibration
**Statement:** The claims operations centre operates during business hours (assumed Monday–Friday, 08:00–18:00 local time). WorkItem SLAs (e.g., 20 min for FIELD_COMPLETION, 30 min for SEVERITY_REVIEW) count only during operating hours. The 2-hour FNOL SLA applies 24/7 (claims arrive at any time and must be acknowledged within 2 hours regardless of whether it is business hours).
**Why it matters:** If claims arrive outside business hours and no specialist is available, the 2-hour SLA cannot be met for claims requiring human WorkItem resolution (AWAITING_* states). An INTERIM acknowledgment is always sent autonomously, but if specialist review is required, the SLA may breach overnight.
**Impact if wrong (24/7 operations):** WorkItem SLA calibration is straightforward for 24/7. If the centre is business-hours-only, the spec must define a "business hours SLA" vs. a "calendar SLA" and clarify what happens to claims received overnight (next-day queue vs. after-hours on-call).
**Status:** `[Flagged for Validation]`
**Validation question:** "What are the claims centre's operating hours? Is there an after-hours on-call team for urgent claims? How are overnight claims currently handled?"

---

### C2 — Specialists Have Individual User Accounts in the CRM
**Statement:** Each specialist logs in with a unique CRM user ID. WorkItem assignment (assigned_to) is per-person, not per-station or per-team. This enables per-specialist quality tracking (field completion accuracy, coverage review outcomes) over time.
**Why it matters:** The WorkItem assignment algorithm selects by least-loaded individual. If specialists share login accounts, assignment cannot be personalised and quality tracking is lost.
**Impact if wrong:** WorkItem assignment must fall back to role-level (assign to SPECIALIST team, first available). Quality tracking by individual is lost. This is a configuration issue, not a spec-breaking change.
**Status:** `[Inferred]`

---

### C3 — Claim Reference Number Format and Acknowledgment Templates
**Statement:** The claim reference number format used in acknowledgments is "FNOL-{YYYY}-{UUID_SHORT}" (first 8 chars of UUID). The acknowledgment email templates (FNOL_ACK_FULL_V1 and FNOL_ACK_INTERIM_V1) must be authored in the CRM before go-live. The 24/7 emergency line number referenced in acknowledgments must be confirmed with operations.
**Why it matters:** AC-001 sends acknowledgments using these templates. If templates are not loaded in CRM, acknowledgments cannot be sent. The emergency line number is a hardcoded configuration item.
**Impact if wrong (templates not ready):** Go-live is blocked until templates are configured. This is a deployment dependency, not a builder dependency.
**Status:** `[Flagged for Validation — deployment dependency]`
**Validation question:** "Who will author the FNOL acknowledgment email templates in Salesforce CRM before go-live? What is the correct 24/7 claims emergency line number to include?"

---

## D — Scope & Design Assumptions

### D1 — NLP Extraction Accuracy is Sufficient Without Custom Training
**Statement:** An off-the-shelf NLP model (or a pre-trained insurance-domain model) can extract the required fields (policy number, claim type, incident date, estimated loss, bodily injury flag) from FNOL claim text with sufficient accuracy to achieve the ≥ 95% extraction accuracy threshold. Custom model training on the company's historical FNOL data is a Phase 2 option if V1 accuracy is insufficient.
**Why it matters:** The parse_confidence threshold (0.90) determines how many claims fall into the AWAITING_FIELD_COMPLETION path. If extraction accuracy is lower than expected, more claims require human field completion, reducing the autonomous handling rate.
**Impact if wrong:** The FIELD_COMPLETION WorkItem queue grows, specialists spend more time on field completion than routing — a different bottleneck from today, but still a bottleneck. Phase 2 custom model training would resolve this.
**Status:** `[Inferred — off-the-shelf NLP performance on insurance text is well-documented; custom training improves but may not be necessary for V1]`

---

### D2 — Volume Distribution is Relatively Uniform During Operating Hours
**Statement:** 300 claims/day arrive with some variation but without extreme concentration at specific times. Peak arrival rate is estimated at no more than 1.5× the average rate for any sustained 30-minute window.
**Why it matters:** The SLA monitoring (AC-002) fires every 5 minutes and the autonomous processing path is designed for near-real-time throughput. If claims arrive in large batches (e.g., 150 claims in the first 30 minutes of the operating day), queue depth and SLA performance may differ significantly from the steady-state model.
**Impact if wrong (extreme batching):** The architecture may need queue-depth-based scaling to handle peak arrival. This is an infrastructure decision for the builder.
**Status:** `[Inferred — email and web form submissions typically distribute through the day; phone transcripts depend on call centre hours]`

---

## Summary: What Must Be Validated Before Building

**Priority 1 (blocks building):**
- A1 — SOAP operations exist and are documented (required for PL and CV modules)
- A3 — Base URLs and credentials available
- A6 — CRM adjuster attributes (specialization, region, queue depth) are populated
- B1 — High-value threshold formally confirmed

**Priority 2 (blocks accurate operations):**
- A2 — Coverage type code mapping confirmed with IT and underwriting
- A4 — DMS API confirmed
- B5 — Phone transcript upload mechanism confirmed
- C1 — Operating hours and after-hours handling defined

**Priority 3 (affects go-live readiness but not build):**
- A5 — CRM outbound email confirmed
- C3 — Acknowledgment templates authored; emergency line confirmed
- B3 — Regulatory basis for coverage denial constraint confirmed with legal
