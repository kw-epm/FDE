# Deliverable #2 — Engagement Intake & Scope
**Engagement:** MedFlex Healthcare Staffing
**Participant:** Pavel Klimasheuski
**Date:** 2026-05-12

---

## Business context

**MedFlex** is a regional healthcare staffing agency: 200 employees, 5-state US coverage. Two business lines: B2B (placing travel nurses at hospital systems) and B2C (recruiting and managing travel nurses). Core operation: matching nurse availability and qualifications to hospital shift requests.

Key operational numbers:
- 8 coordinators handling ~120 matching decisions each per day (~960/day total)
- Average fill time: 4.2 hours
- Mismatch rate: 7% (hospital-reported qualification mismatches)
- No-show rate: 12%
- Current revenue: ~$40M; board target: $200M in 2 years

**Series B recently closed.** Board wants significant growth. CEO has seen two prior AI projects fail (chatbot rejected by hospitals; recommendation engine with too many errors and poor adoption).

---

## Stakeholder map

| Stakeholder | Role | Status | Notes |
|---|---|---|---|
| Marcus Reyes | CEO, primary engagement contact | Interviewed | Results-oriented, sceptical of AI based on prior failures, defers operational detail; open to full automation if risks are clearly presented |
| Kim | Head of Operations | Not interviewed | Owns the coordinator workflow; critical for lived-process detail and agent adoption |
| Aaron | IT | Not interviewed | Owns ServiceNow and nurse/hospital database infrastructure; critical for API access and data model |
| Linda | Compliance | Not interviewed | Owns credential verification process; out of scope for v1 but needed for Wave 2 |
| 8 Coordinators | End users | Not interviewed | Key adoption risk; two prior failed AI projects created trust deficit and job-security anxiety |

**Gap:** Only the CEO was interviewed. Kim is the key missing voice — she holds the lived operational process knowledge that determines whether the agent design matches how work actually happens. This is flagged as a design risk.

---

## Constraints

- **Technology:** All channels (email, portal, phone) land in ServiceNow as a queue. Hospital requests arrive as free text. Nurse availability is self-updated by nurses. Matching currently done by manual database search.
- **Timeline:** 8 weeks to first value delivery. Not full transformation — Phase 1 must show measurable ROI.
- **Market dynamics:** Hospitals submit requests to multiple agencies simultaneously. Speed to submit a qualified candidate is the competitive differentiator.
- **Adoption:** Coordinators have experienced two prior AI failures. Any solution must build trust incrementally; full automation from day one is a risk even if leadership is open to it.
- **Budget:** Series B funded, but no specific AI tooling budget stated. Leadership expects a cost/problem/risk case.

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Coordinator rejection/workarounds | High | High | Phased rollout; start with agent as assistant, not replacement; involve Kim in design |
| Matching accuracy below human baseline | Medium | High | Confidence threshold with human review for low-confidence matches; track and compare |
| Free text parsing failures | Medium | Medium | Parsing agent with explicit failure modes and fallback to coordinator queue |
| Race condition: nurse confirmed by two hospitals | High | Medium | Agent must handle withdrawal from competing submissions as first-class workflow |
| Data quality: nurse availability staleness | Medium | Medium | Flag as assumption; agent should surface low-confidence availability matches |
| Missing Kim/Aaron/Linda input creating spec gaps | High | Medium | Name as open assumptions; design for flexibility in Wave 2 |

---

## MVP scope

**In scope (Phase 1 — 8 weeks):**
- Request intake agent: parse free text hospital requests from ServiceNow into structured ShiftRequest entities
- Nurse matching agent: given a structured ShiftRequest, return a ranked candidate list with confidence scores based on qualifications, availability, proximity, and preference history
- Coordinator review interface: coordinators review agent-proposed candidates, approve or override
- Confidence-threshold auto-submission: high-confidence matches submitted to hospital automatically; low-confidence escalated to coordinator
- Multi-hospital race condition handling: when a nurse is confirmed by one hospital, agent withdraws her from concurrent submissions

**In scope (Wave 2 — post Phase 1):**
- Active nurse confirmation (explicit accept/decline vs. current passive default)
- No-show prediction and prevention
- Credential expiry proactive notification system (push alerts to compliance team / nurse when a credential is approaching expiry; distinct from the Phase 1 proximity warning surfaced to coordinators during match review)
- Coordinator-facing analytics (match quality, fill time, per-coordinator throughput)

---

## Out-of-scope — with rationale

| Item | Rationale |
|---|---|
| Hospital-facing submission portal | Hospitals prefer existing channels (email dominant, confirmed in discovery). Changing submission channels requires hospital-side adoption effort and is a separate product problem unrelated to the matching bottleneck. It would also require hospital IT integration — out of scope for this engagement. |
| Nurse-facing mobile app | Nurses are reached today by SMS/email with no identified problem in this channel. Building a native app is a separate product investment with its own adoption curve. Not the bottleneck. |
| Pricing / margin optimisation | Out of scope per engagement framing. MedFlex's pricing and margin decisions remain a human process. |
| Credential renewal automation | Compliance verification is a separate team with a separate legally-mandated process. This is not coordinator work and is not the problem this engagement solves. It becomes relevant at scale (Wave 2 candidate). |
| Full coordinator elimination | Architecture augments coordinators, not eliminates them. Adoption risk from prior AI failures makes full replacement a non-starter in Phase 1. Coordinators shift from executing matches to supervising and reviewing agent output. |
| Billing / invoicing / payroll | Downstream financial processes are not part of the matching workflow and not mentioned as a pain point. |

---

## Open assumptions requiring validation before spec finalisation

- **Kim interview not completed** — lived operational workflow may differ from what was described at the CEO level; treat all process details as assumed until validated with Kim
- **ServiceNow API capabilities** — unknown; assumed accessible and queryable by the agent (flagged for Aaron)
- **Nurse database schema** — described as "a database" but structure, API, and query capabilities unknown (flagged for Aaron)
- **Hospital preference data** — confirmed to be tracked in the system; structure and completeness unknown
- **Current credential check at matching time** — coordinators check the nurse profile card at time of matching; whether this is a system flag or manual lookup is unknown
