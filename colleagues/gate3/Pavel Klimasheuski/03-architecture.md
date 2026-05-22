# Deliverable #3 — Agentic Solution Architecture
**Engagement:** MedFlex Healthcare Staffing
**Participant:** Pavel Klimasheuski
**Date:** 2026-05-12

---

## Architecture overview

The MedFlex agentic system transforms the manual coordinator workflow with three cooperating agents. The key design principle: **agents handle data-gathering, parsing, and structured reasoning; coordinators handle exceptions, edge cases, and relationship decisions.**

```
[Hospital Request]
    ├── Email  ───────────────────────────────┐
    ├── Portal ───────────────────────────────┤→ ServiceNow queue
    └── Phone → Coordinator enters manually ──┘
                                              ↓
                     [Agent 1: Request Intake] — parse free text → structured ShiftRequest
        ↓
[Agent 2: Nurse Matching] — rank candidates → candidate list + confidence scores
        ↓
    confidence ≥ threshold?
        ├── YES → [Agent 3: Submission] — auto-submit to hospital + notify nurse
        └── NO  → Coordinator review queue → coordinator approves/overrides → Agent 3
        ↓
[Agent 3: Submission & Race Condition Handler]
    — submit candidate to hospital
    — notify nurse (SMS/email)
    — on hospital confirmation: withdraw nurse from concurrent submissions
```

---

## Agent 1 — Request Intake Agent

**Purpose:** Convert free text hospital requests from ServiceNow into a structured `ShiftRequest` entity.

**Channel convergence:** All three submission channels (email, portal, phone) converge in ServiceNow before the agent acts. Email and portal entries land there automatically. Phone calls are handled by a coordinator who enters the request into ServiceNow manually — the coordinator is the transcription layer. The agent reads from ServiceNow only, making the channel irrelevant to its design. This means phone support requires no additional integration in Phase 1.

**Why this is an agent, not a rule-based parser:**
Hospital requests arrive in natural language with variable phrasing, implied requirements, and domain-specific shorthand (e.g., "ICU-trained RN for nights starting Tuesday" requires inferring credential categories, shift timing, and start date from partial context). A rule-based system would require exhaustive pattern libraries for every hospital's writing style. An LLM agent can reason over ambiguity and make explicit what is implied.

**Decision points handled by this agent:**
- Credential category inference (free text skill description → structured credential requirement)
- Date/time resolution (relative references → absolute timestamps)
- Ambiguity flagging: if the request is too ambiguous to parse with sufficient confidence, the agent adds it to the coordinator clarification queue rather than guessing

**Delegation archetype:** Agent-led + log. Parsing is high-volume, low-risk (output is reviewed before submission), and reversible (coordinator can correct a bad parse before it propagates). All parsing decisions logged with source text and confidence.

**Inputs:** Raw text string from ServiceNow, hospital profile (for context on their typical requirements)
**Outputs:** Structured `ShiftRequest` entity (shift date/time, location, required credential categories, hospital preferences, urgency flag) + confidence score + flagged ambiguities

---

## Agent 2 — Nurse Matching Agent

**Purpose:** Given a structured `ShiftRequest`, query the nurse database and return a ranked list of eligible candidates with confidence scores and reasoning.

**Why this is an agent, not a rule-based matcher:**
Experienced coordinators (10+ years) make better matches than newer ones because they hold tacit knowledge: which nurses work well at which hospital types, which nurses have strong performance history in specific roles, how to weigh proximity vs. preference vs. credential edge cases. A rule-based matcher applies fixed weights. An LLM agent can reason contextually across these factors — the same way a senior coordinator does — and explain its reasoning.

**Decision points handled by this agent:**
- Multi-factor ranking: qualifications (hard constraint) → availability (hard constraint) → proximity, hospital preference history, nurse preference history, historical performance (soft ranking)
- Credential edge case handling: nurse's credential expires before the shift date → exclude from candidates; flag for compliance team
- Confidence scoring: when no strong match exists (e.g., specialist shift with thin candidate pool), agent scores low and escalates rather than forcing a weak match
- Multi-submission strategy: agent can propose multiple candidates to the same hospital when confidence is moderate (confirmed competitive market norm)

**Delegation archetypes:**
- Confidence ≥ threshold: Agent-led + human oversight. Agent auto-selects top candidate; coordinator can review and override within a time window before submission.
- Confidence < threshold: Human-led + agent support. Agent presents ranked candidates with reasoning; coordinator makes the call.
- No viable candidates: Agent escalates to coordinator immediately with a summary of why (thin pool, credential gap, availability conflict).

**Inputs:** Structured `ShiftRequest`, nurse database (profiles, availability, credentials, history), hospital preference data
**Outputs:** Ranked candidate list (top N candidates, each with confidence score, credential status, availability confirmation, and reasoning summary)

---

## Agent 3 — Submission & Race Condition Handler

**Purpose:** Submit approved candidates to hospitals, notify nurses, and manage the multi-agency race condition (same nurse submitted to multiple hospitals simultaneously).

**Why this needs to be an agent:**
The race condition is non-trivial: MedFlex submits the same nurse to multiple hospitals concurrently (competitive market norm). When Hospital A confirms a nurse, Agent 3 must immediately withdraw that nurse from pending submissions to Hospitals B, C, etc. — and trigger re-matching for those hospitals if needed. This is a stateful coordination problem with real-time constraints that requires reasoning about submission states, not just rule execution.

**Decision points handled by this agent:**
- On hospital confirmation: identify all concurrent submissions for the confirmed nurse; withdraw from pending; determine whether to trigger re-matching or escalate to coordinator
- On nurse no-response: current model (silence = accepted) maintained for Phase 1; agent logs notification-to-shift time for future active confirmation design
- On nurse decline call: agent updates availability record and re-triggers matching agent for the affected shift

**Delegation archetype:** Agent-led + log for standard submission and withdrawal. Escalation to coordinator if re-matching after withdrawal returns low confidence.

**Inputs:** Approved candidate + ShiftRequest, hospital communication channel, nurse notification preferences
**Outputs:** Hospital submission confirmation, nurse notification, updated submission state log

---

## Delegation archetypes by workflow

| Workflow step | Archetype | Rationale |
|---|---|---|
| Free text parsing | Agent-led + log | High volume, low risk, reversible; output reviewed before submission |
| Matching (high confidence) | Agent-led + human oversight | Senior coordinator-level accuracy targeted; override window preserves human control |
| Matching (low confidence) | Human-led + agent support | Agent presents options with reasoning; coordinator decides; preserves trust during rollout |
| Hospital submission | Agent-led + log | Deterministic once candidate approved; full audit trail |
| Nurse notification | Fully agentic | Deterministic, low risk, high volume |
| Race condition resolution | Agent-led + log | Stateful but deterministic once hospital confirms; escalate if re-match fails |
| No viable candidate | Human-led | Agent flags and summarises; coordinator decides how to proceed |

---

## Integration dependencies

The three agents share a common data surface. The table below maps what each agent requires, what it produces, and what remains unknown pending validation with IT.

| Agent | Reads from | Writes to | Key unknowns |
|---|---|---|---|
| Agent 1 — Request Intake | ServiceNow queue (raw request text + hospital profile) | Structured ShiftRequest entity | ServiceNow API capabilities; whether hospital profiles are accessible programmatically |
| Agent 2 — Nurse Matching | ShiftRequest entity; nurse database (profiles, availability, credentials, history); hospital preference data | Ranked candidate list with confidence scores | Nurse database schema and query API; data freshness model for self-reported availability; whether credential status is a system flag or manual lookup; structure and completeness of hospital preference data |
| Agent 3 — Submission | Approved candidate + ShiftRequest; hospital communication channel config; nurse notification preferences | Hospital submission confirmation; nurse notification; submission state log | Hospital email/portal integration method; nurse contact preference storage location |

**No new external systems are required.** All agent data surfaces should exist within ServiceNow and the current nurse/hospital database. The unknowns are access and schema questions — they determine build feasibility and must be validated with IT before Phase 1 engineering begins.

---

## ADR-1: Confidence threshold for auto-submission

**Decision:** Use a configurable confidence threshold to determine when the matching agent auto-submits vs. escalates to coordinator review.

**Alternatives considered:**
- (a) Always require human review — eliminates all autonomous matching decisions
- (b) Configurable confidence threshold — high-confidence matches auto-submit; low-confidence escalate
- (c) Full automation, no threshold — agent always auto-submits

**Chosen:** Option (b), starting with a conservative threshold.

**Rationale:** Leadership is open to full automation, but coordinator adoption risk is real — two prior AI failures created a trust deficit. Starting with a high bar for auto-submission builds trust incrementally. Coordinators see the agent working well on clear-cut cases before they see it make borderline calls. Option (a) delivers no speed improvement; Option (c) risks a high-profile wrong match early in the engagement, which could kill adoption entirely.

**Consequences:** Phase 1 will not achieve the full fill time reduction possible; coordinators still handle a meaningful review queue. This is intentional — the threshold loosens as accuracy is validated.

**Cold-start calibration:** On day one, no historical match data exists to set the threshold empirically. The proposed approach: run Phase 1 with 100% coordinator review until sufficient ground truth accumulates — what the agent proposed, what the coordinator decided, and whether the fill succeeded. At ~960 decisions per day, that data arrives in days, not weeks. Conservative estimate: initial threshold set by end of week one; autonomous submission for high-confidence cases begins week two. The calibration trigger is case volume, not a fixed time period.

**Revisitation conditions:** After 4 weeks of operation, review precision/recall on auto-submitted matches vs. coordinator-reviewed matches. If auto-submission accuracy ≥ coordinator average, lower threshold. If worse, investigate and retrain before lowering.

---

## ADR-2: Request intake as a standalone agent vs. integrated into matching

**Decision:** Request intake parsing is a separate agent (Agent 1), not integrated into the matching agent.

**Alternatives considered:**
- (a) Integrated: single agent takes raw request text and returns candidate list
- (b) Separate: parsing agent outputs structured ShiftRequest; matching agent consumes it

**Chosen:** Option (b) — separate agents.

**Rationale:** An integrated design makes parse errors invisible — a misparsed ICU request flows into matching, a wrong-credential candidate is ranked confidently, and a wrong-nurse submission reaches the hospital before anyone reviews it. The split creates a visible checkpoint: Agent 1 outputs a structured ShiftRequest with a confidence score; low-confidence parses go to the coordinator clarification queue before Agent 2 runs. The coordinator sees the parsed request, can correct it, and only then does matching proceed. The cost of a parse error is a coordinator correction, not a wrong-nurse submission to a hospital. Agent 1 also runs on a lighter model — parsing is structured extraction, not complex reasoning — so the marginal inference cost is low relative to this quality guarantee.

**Consequences:** Two-agent chain adds latency compared to integrated design. In practice, both agents run fast enough that this is unlikely to be the binding constraint on fill time. The engineering separation benefits (independent testing, reusable ShiftRequest entity) are real but secondary to the hospital outcome argument above.

**Revisitation conditions:** If end-to-end latency benchmarking shows the chain is a material bottleneck vs. a single integrated agent, consider merging. Revisit after Phase 1 latency data is available.

---

## ADR-3: Passive nurse acceptance vs. active confirmation

**Decision:** Maintain the current passive acceptance model (silence = accepted; nurse must call to cancel) for Phase 1. Do not require explicit nurse confirmation.

**Alternatives considered:**
- (a) Passive acceptance — current model; nurse notified, no reply required
- (b) Active confirmation — nurse must explicitly accept/decline; unresponded notifications escalate

**Chosen:** Option (a) for Phase 1.

**Rationale:** Nurse confirmation was not flagged as a pain point in discovery. Adding mandatory confirmation introduces friction on the nurse side and could slow fill times — a competitive disadvantage if other agencies don't require it. The 12% no-show rate has multiple causes (nurse taken by competing agency, personal reasons); requiring confirmation won't eliminate no-shows from competing agency assignments. The risk of solving the wrong problem with higher friction outweighs the potential benefit at this stage.

**Consequences:** No-show rate is unlikely to improve materially from this architecture alone. No-show monitoring is built into Agent 3's logging, which provides the data needed for a future active confirmation design.

**Revisitation conditions:** If no-show rate does not improve after Phase 1 (matching quality improvement alone should reduce some no-shows by reducing mismatches), revisit active confirmation as a Wave 2 feature.

---

## Operational logging requirements

The revisitation conditions in ADR-1 and ADR-2 require specific data that must be captured by design from the start of Phase 1. Without it, the 4-week accuracy review and latency benchmarking cannot be performed.

**Agent 2 must log per match decision:**
- ShiftRequest ID and structured requirements
- Top candidate proposed and confidence score
- Whether the coordinator approved, overrode to a different candidate, or rejected all candidates
- Eventual fill outcome (which candidate filled the shift, or unfilled)

**Agent 3 must log per submission:**
- Submission timestamp and hospital confirmation timestamp (enables fill time measurement)
- Nurse notification timestamp
- Whether a race condition withdrawal was triggered and whether re-matching was needed

**Why this matters:** The comparison "auto-submission accuracy ≥ coordinator average" (ADR-1 revisitation condition) requires knowing the ground truth outcome for both agent-led and coordinator-led decisions on comparable cases. If logging is not designed into Phase 1, this comparison is impossible and the threshold cannot be adjusted with evidence.

---

## What this architecture does not solve (by design)

- **Credential renewal automation** — separate process, separate team, out of scope for v1
- **Hospital submission channel consolidation** — hospitals continue using email/portal/phone; the intake agent handles all three
- **Pricing and margin optimisation** — remains a human process
- **Nurse recruitment** — out of scope; the agent works with the existing nurse database
