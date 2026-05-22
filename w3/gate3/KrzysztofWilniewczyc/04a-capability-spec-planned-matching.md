# D#4a Capability Spec: Planned Matching

*Source domain: MedFlex Healthcare Staffing. Sibling spec: `04b-capability-spec-urgent-rematching.md` (shares entities and state machine).*

## 1. Capability overview

Given an inbound shift request from a hospital, the agent extracts structured intent, reasons over historical context to rank eligible nurses, and produces a candidate shortlist with explicit reasoning. Coordinator approves every offer early in v1; agent gains autonomy as the trust ramp progresses (Ranker weeks 1–2 manual approval, weeks 3–4 high-confidence auto-send, week 8 sample audits). After explicit nurse acceptance (Decision 2, conditional), MedFlex submits to the hospital. Primary KPI clock ends at hospital submission.

## 2. Trigger and inputs

**Trigger:** new shift request arrives in ServiceNow (email parsed via ServiceNow ingestion). Polling-based or webhook-driven (D#4 implementation parameter; defaults to webhook if available).

**Queue source: ServiceNow is the single system of record for all inbound shift requests across the slice.** No other intake channels (no separate inbox, no shared spreadsheet, no Slack channel). All discovery, prioritisation, and downstream agent action runs from this one queue. If ServiceNow is down, the agent halts new offers; coordinator-only mode continues from email until restored.

**Inputs:**
- Raw email body (free text)
- Hospital identifier (from sender or routing rule)
- Receipt timestamp (for primary KPI clock)
- (Implicit) historical context: hospital acceptance/rejection records, past hospital–nurse pairings, coordinator notes if structured, nurse credential/availability/profile data

## 3. Shared entities (canonical glossary, also used by D#4b)

| Entity | Definition | Key fields |
|---|---|---|
| **ShiftRequest** | Free-text inbound from hospital with parsed structured intent | id, hospital_id, raw_text, parsed_intent, received_at |
| **CandidateShortlist** | Agent's ranked top-N eligible nurses with per-candidate reasoning citations | shift_request_id, candidates[N], reasoning_per_candidate, confidence |
| **NurseOffer** | Specific shift offered to a specific nurse | shortlist_id, nurse_id, shift_id, offered_at, channel (sms/email) |
| **NurseAcceptance** | Explicit yes from nurse within the Decision 2 window | offer_id, response (yes/no/timeout), responded_at |
| **HospitalSubmission** | MedFlex sends the candidate to the hospital | nurse_id, hospital_id, shift_id, submitted_at, reasoning_summary |
| **HospitalAcceptance** | Hospital confirms the candidate | submission_id, response (yes/no), responded_at |
| **ConfirmedFill** | Both nurse and hospital accepted | nurse_id, shift_id, confirmed_at |
| **LockState** | enum: SoftLock \| PartialCommitment \| Confirmed \| Released | candidate_id, current_state, entered_at, expires_at |

**State transitions** (per Decision 3 in D#3): SoftLock fires on commitment event → on first side accepting moves to PartialCommitment → on second side accepting moves to Confirmed; any decline/timeout/expiry transitions to Released. Hard cap on PartialCommitment bounds the worst case (24h non-urgent, 2h urgent).

## 4. Process steps

| # | Step | Pre-condition | Action | Post-condition | Error path |
|---|---|---|---|---|---|
| 1 | Extract structured intent | Raw email body received | LLM reads email, outputs (specialty, dates, location, credential requirements, urgency, hospital preferences). Two-stage extraction: each field validated against source text spans. | Structured ShiftRequest with citations | If field-level confidence <85%, route to coordinator review |
| 2 | Eligibility filter | Structured ShiftRequest | Rules-based: credential match, availability, location proximity, DNR check | Eligible nurse pool | If pool is empty, route to coordinator (exception path) |
| 3 | Compliance precondition | Eligible pool | Read each nurse's credential expiry vs shift date | Pool with valid-credential nurses only | Expired credentials filter out + flag to compliance team |
| 4 | Contextual reasoning over history | Filtered pool | LLM ranks candidates over: hospital acceptance patterns, past hospital-nurse pairings, profile note signals, soft signals in request | Ranked CandidateShortlist with reasoning citations per candidate | If no high-signal data exists for any candidate, fall back to rules-only ranking + flag to coordinator |
| 5 | Confidence scoring | Ranked shortlist | Compute agreement-between-signals metric: high/medium/low confidence | Shortlist with confidence label | (No error; confidence drives next step) |
| 6 | Confidence gate × trust ramp | Confidence label + current ramp state | Map to action: auto-send (high confidence, late trust ramp) / flag-to-coordinator (medium or early ramp) / coordinator-decides (low confidence) | Decision: auto / flag / human | (No error) |
| 7 | Coordinator review (if not auto-send) | Flagged shortlist | Coordinator sees shortlist with per-candidate reasoning, approves top pick, edits, or escalates | Approved candidate selection | If coordinator rejects all, escalation path (exception) |
| 8 | Soft-lock fires (Decision 3) | Approved candidate | Lock state machine starts: candidate locked against parallel offers. Trigger event depends on workflow order (nurse-first: lock fires on NurseOffer send) | Candidate locked, LockState = SoftLock | If lock-state store unavailable, halt the offer; alert ops |
| 9 | NurseOffer sent | Locked candidate | Send SMS + email with shift details; Decision 2 window starts (~90 min planned) | Offer in flight | If comms layer fails, retry with backoff; alert after 3 failures |
| 10 | Wait for nurse acceptance (Decision 2 conditional) | Offer in flight | Listen for explicit yes/no within window | NurseAcceptance OR timeout | On accept: → PartialCommitment. On decline/timeout: → Released, re-pool, next candidate |
| 11 | Hospital submission | Nurse accepted | MedFlex submits the candidate to the hospital. **Primary KPI clock ends here.** | HospitalSubmission record | If hospital comms fails, retry; flag if persistent |
| 12 | Hospital acceptance | Submission in flight | Hospital confirms or rejects | HospitalAcceptance | On reject: re-rank from same shortlist; on accept: → Confirmed state |
| 13 | Confirmed fill | Both sides accepted | Lock state → Confirmed. Audit trail written. | ConfirmedFill record | (No error) |

*Note: this spec is the nurse-first baseline. If Head of Ops confirms a hospital-first or parallel workflow Monday, the submission step (11) moves earlier in the sequence. See D#3 glossary footnote on workflow order. In those variants, submission is provisional until nurse acceptance per Decision 2; the architecture absorbs either order.*

## 5. Confidence definition (carries from D#3)

- **High:** strong eligibility match + strong historical signal (the hospital has accepted similar profiles before) + clear top pick (not a near-tie at the top)
- **Medium:** mixed signals, or top candidate close to second in score
- **Low:** eligibility-only match, no strong historical signal, or unfamiliar request type

D#7 validates that high-confidence cases are empirically the ones approved without override.

## 6. AI-native decision point (the specific moment a rules engine can't reach)

**Worked example.** Hospital A sends: *"Need an ICU nurse for tomorrow's night shift. Prefer someone we've worked with before. The unit just admitted a pediatric patient with a rare medication allergy."*

A rules engine extracts: `specialty=ICU, date=tomorrow, time=night, certs=ICU+RN`. Done.

The agent reads further and picks up three context signals a rules engine can't:

1. *"someone we've worked with before"* is a soft preference, not a hard requirement. Hospital A's past acceptance history boosts Nurse N (3 prior shifts at Hospital A) over Nurse M (none, despite identical credentials).
2. *"pediatric"* + *"rare medication allergy"* implies the unit wants experience with allergic pediatric cases. The agent searches nurse profile notes for relevant prior shifts and weighs the result.
3. *"tomorrow night"* signals urgency. The agent leans toward known-reliable candidates over pure-credential-leaders, because at short lead time a no-show costs more than a marginal credential gain.

Result: top of the shortlist is Nurse N (Hospital A history + prior pediatric-allergy shift + acceptable credential profile), not Nurse M (slightly stronger credentials but no Hospital A history). A rules engine cannot make this distinction. The agent reasons over context, produces the shortlist, and shows its reasoning. The coordinator audits the *why* at the review step, not just the *who*.

That moment is the agent's actual job. "Matching" is just the label; the work is in the three signals above.

## 7. Integration contracts

| Integration | Direction | Purpose | Failure handling |
|---|---|---|---|
| **ServiceNow read API** | inbound | Read shift request queue, hospital identifiers, existing placement records | Buffer locally, retry; coordinator-only mode if persistent |
| **ServiceNow write API** | outbound | Write ShiftRequest, CandidateShortlist, NurseOffer, HospitalSubmission, audit trail | Queue, retry, alert on persistent failure |
| **Nurse database** | read | Query nurses by credential, specialty, availability, geo, profile notes | If unavailable, agent rejects all candidates safely (better than wrong-credential nurse to hospital) |
| **Comms layer** | outbound | SMS + email for NurseOffer; required for Decision 2 | Retry with backoff; alert ops after 3 failures |
| **Compliance handoff** | outbound | Flag credential gaps to compliance team via coordinator dashboard | Manual escalation path |
| **LLM provider** | external | Extraction + reasoning + citation generation | Fall back to coordinator-only routing for the duration; queue requests |
| **Lock-state data store** | read/write | Per-candidate lock state, transitions, expiry | Halt new offers until store recovers |

## 8. Worked examples / edge cases

| # | Scenario | Agent behaviour |
|---|---|---|
| 1 | **Standard request, clear top pick** (high confidence) | Auto-send the offer (week 8 trust ramp target). Coordinator sees the decision in the dashboard for sample audit. |
| 2 | **Ambiguous specialty in email** ("ICU or PICU?") | Extraction confidence below threshold. Flag the structured ShiftRequest to coordinator with both interpretations surfaced for resolution before ranking runs. |
| 3 | **Nurse declines first offer** | Soft-lock releases. Re-rank from the same shortlist (cached); send second offer. If shortlist exhausted, exception path: flag to coordinator with the option of expanding eligibility or escalating. |
| 4 | **Hospital cancels shift mid-flow** | Any LockState transitions to Released. Outstanding NurseOffer is withdrawn (apologetic SMS to nurse). Audit trail captures cancellation reason. |
| 5 | **Candidate's credential expires between shortlist and offer** | Re-check at offer time (step 9 pre-condition). If expired, candidate dropped, next candidate in shortlist promoted. Compliance team notified for cred-status confirmation. |
| 6 | **Multi-submission race** (Nurse N has 2 in-flight offers) | Soft-lock prevents the second offer. Second shift request waits, or surfaces alternative candidate. Logged for lock-impact metrics (per Decision 3). |
| 7 | **No-reply scenario before Decision 2 confirmed** | If Head of Ops Monday confirms no-reply-as-yes is current practice, Decision 2 holds: explicit-yes required. If not, fall back to confirmation-channel-improvement path (per D#3 Decision 2 alternative). |
| 8 | **Hospital rejects submitted candidate** | Move back to step 4 (re-rank from same shortlist with rejected candidate excluded). If shortlist exhausted, coordinator escalation. |

## 9. Marked assumptions (with confidence)

| # | Assumption | Confidence | Source / risk |
|---|---|---|---|
| A1 | Email is the dominant intake channel | **High** | Marcus stated in discovery; engagement scope confirms |
| A2 | ServiceNow exposes read/write API in time for v1 | **Medium** | Industry standard for ServiceNow; not validated for MedFlex specifically |
| A3 | At least one high-signal contextual data source (hospital acceptance history OR past pairings) is usable | **Medium** | Gated by D#3 go/no-go gate; pause and rescope if absent |
| A4 | Decision 2 (no-reply-as-yes finding) holds | **Conditional** | Per D#3 Decision 2; alternative path defined if false |
| A5 | Nurse profile notes contain queryable text | **Low** | Marcus implied unstructured notes exist; structured form unconfirmed |
| A6 | Hospital preference history is accessible (not just in coordinator memory) | **Low** | Marcus quote suggests partial; structured form unconfirmed |
| A7 | "$14M revenue" means net agency revenue (not gross billings) | **Medium** | Affects D#1 math; CFO clarification Monday |
| A8 | Slice volume on chosen 2 hospitals is ≥15 fills/day | **Placeholder** | Slice-selection question for Head of Ops Monday |
| A9 | Lock-state data store can be persisted with sub-second latency | **Medium** | Standard database capability; specific tech TBD in D#4 implementation |
| A10 | Nurse comms latency (SMS/email) is sufficient for Decision 2 window | **Medium** | Standard infrastructure; coordinator escalation if persistent comms failures |

---

### Revisions added AFTER the D#9 buildability test ran

> **Transparency note (per pack §9 protocol: "flag it as a revision"):** the two assumptions below (A11, A12) were added to this spec **AFTER** D#9 was generated. The reflection in `09-self-spec-reflection.md` is based on the **pre-A11/A12** version of this spec. If anyone re-runs D#9 against the current spec, Claude Code's `ASSUMPTIONS.md` output will likely differ from the diagnostic table in D#9, because A11 and A12 now explicitly flag (but do not pin) the precision and maturity gaps that D#9 surfaced and that a separate production-spec checklist self-audit identified. The values themselves remain deferred; only the flag is new.

| # | Assumption | Status | Source / risk |
|---|---|---|---|
| A11 | **Numeric precision parameters deliberately left as parameters in v1 spec, surfaced by D#9 buildability test:** near-tie threshold (§5), Top-N shortlist size (§3), location proximity bound (§4 step 2), `HospitalSubmission.reasoning_summary` template format (§4 step 11), trust-ramp weeks 5–7 behaviour (§1), Decision 2 windows labelled distinctly from response-time targets (§10). | **Flagged (post-D#9)** | Added after D#9 surfaced these as the parameters CC had to invent to compile. Pinning the values is the first production-deployment task (engagement week 0–1). Status remains "deferred", not "resolved". |
| A12 | **Other production-spec checklist gaps deliberately deferred to integration-design phase, surfaced by self-audit against `Reference/production-spec-checklist.md`:** (a) entity field full types / constraints / ISO 8601 timestamps / enum casing / foreign-key cascade behaviour in §3 (key fields listed only); (b) integration-contract details in §7 (endpoint URLs, authentication methods, request/response JSON shapes, specific timeout values, rate-limit budgets; system names and direction listed only); (c) economics / cost classification (token budgets per agent call, batch / cache opportunities) not addressed; (d) governance retention policy (HIPAA flagged separately in D#7 §7.3 as a regulatory blocker; specific retention windows not in this spec). | **Flagged (post-D#9 self-audit)** | Added after self-audit against the production-spec checklist (separately from D#9). Items deferred deliberately for v1 prototype phase; closure during integration-design phase (engagement week 0–1). Where the spec stands: structurally complete for this gate (all 10 sections present, eight edge cases, named entities, validation hooks); precision/maturity items remain deferred to engagement week 0–1. |

## 10. Validation hooks (cross-reference D#7)

| Metric | Target | Trigger |
|---|---|---|
| **Primary KPI** (request → hospital submission) | ≤2h nurse-first / ≤1h parallel-or-hospital-first | Pause if worse than baseline at week 3; rollback at week 4 |
| **Decision 1 quality** (first-pick acceptance rate) | ≥75% on slice | Pause <60%, rollback <50% |
| **Diagnostic step 1** (request → nurse-offer-sent) | <30 min | Investigate if exceeded |
| **Hospital acceptance rate** | No more than 5pp below baseline | Pause >10% drop WoW, rollback >20% |
| **Coordinator override rate** | <40% by week 4, <25% by week 8 | Pause >50% by week 4, rollback >70% sustained |
| **Per-offer nurse response time** | Median <60 min planned, <15 min urgent | Pause >70 min planned / >22 min urgent; rollback at window limit |
| **No-show rate** (post Decision 2) | ≤8% on slice | Pause if worse than baseline 4 weeks post-explicit-yes |
| **Mismatch rate (guardrail)** | Hold or improve on slice | Pause >7% on slice 2 weeks, rollback >10% |
| **Submission withdrawal rate (anti-gaming)** | <5% on slice | Pause >5%, rollback >10% or rising 2 weeks |
| **Direct locking-impact** | Lock-timeout rate + lock-release-then-immediate-reuse rate (per Decision 3) | Tune lock window if thresholds tripped |

Full pause/rollback table mirrored in D#1, D#3, and D#7.
