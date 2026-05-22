# Deliverable #9 — Self-Spec Build-Loop Reflection
**Engagement:** MedFlex Healthcare Staffing
**Participant:** Pavel Klimasheuski
**Date:** 2026-05-13
**Spec used:** Deliverable #4a — Request Intake Agent (04a-capability-spec-intake.md)

---

## (a) What was built and whether it matches intent

The builder produced a complete, runnable Agent 1 implementation: a polling loop, LLM-based parsing via tool use, Pydantic models with validators, atomic PostgreSQL inserts across four tables, a ServiceNow client with real and mock paths, a hospital profile client with in-memory caching, ops alerting, and a cost circuit breaker. The project structure matches the spec's Build Context section closely.

The core pipeline — poll ServiceNow, parse with LLM, write structured ShiftRequest — works as intended. The delegation boundaries (low confidence → CLARIFICATION_NEEDED, otherwise → PENDING_MATCH) are correctly implemented. Idempotency, duplicate detection, and ambiguity flagging are all present. From a structural standpoint, the build matches the intent.

Four specific behaviors diverge from the spec. None are catastrophic; two silently misbehave.

---

## (b) What the builder asked or said it couldn't build

In an autonomous build loop there are no explicit questions — the builder makes decisions and moves on. But two places in the code reveal where the builder hit ambiguity and chose rather than asked:

- **`_should_use_sonnet` heuristic** — the spec says "use Sonnet for CRITICAL urgency requests," but urgency is only known after the LLM parses the request — a chicken-and-egg problem the spec doesn't address. The builder resolved it with keyword pre-flight detection, which is a reasonable interpretation, but implements a different mechanism than the spec describes. That's a question about the intended mechanism disguised as a decision.
- **`INTAKE_CONFIDENCE_HIGH` loaded but unused** — the builder loaded the variable, wrote no branch for it, and moved on. That's the builder signalling "I see this threshold but I don't know what Agent 1 is supposed to do with it."

---

## (c) Gap diagnosis

| Signal | Classification | Root |
|---|---|---|
| Urgency enum says "ASAP" → URGENT; system prompt (rule 4) and date resolution rule (rule 5) both say "ASAP" → CRITICAL | Spec gap | Internal contradiction between two parts of the same document. Note: the builder resolved this correctly by following the system prompt (`_CRITICAL_KEYWORDS = {"asap", ...}`); the code has no defect. The fix is to update the enum to match the system prompt — which is the authoritative source for the LLM's behavior. |
| `INTAKE_CONFIDENCE_HIGH` loaded, never used | Spec gap | Configurable threshold defined without a specified mechanical action in Agent 1's routing |
| Dynamic Sonnet escalation for CRITICAL keywords | Spec gap | Spec says "use Sonnet for CRITICAL urgency" but urgency is determined by the LLM — the mechanism for model selection before parsing is unspecified; builder filled the gap with keyword pre-flight |
| Duplicate check silently skips when `shift_start_time` is null | Spec gap | SQL null-handling not specified; builder followed natural pattern that fails the edge case |

---

## (d) What I would change in the spec with 30 more minutes

**Fix 1 — Resolve the urgency contradiction.** The Urgency enum assigns "ASAP", "immediately", and "emergency cover" to URGENT, while both the date resolution rules and the system prompt assign them to CRITICAL. The system prompt and date resolution rules are authoritative (ASAP with no date is a genuine emergency, not merely urgent). Update the Urgency enum: move those keywords from URGENT to CRITICAL. URGENT becomes time-proximity only (24–48 hours) plus the explicit keyword "urgent". Also specify the model selection mechanism: since urgency is only known after parsing, keyword pre-screening before the LLM call is the correct approach — if source text contains "ASAP", "immediately", or "emergency cover", use Sonnet; otherwise use Haiku.

**Fix 2 — Specify or remove `INTAKE_CONFIDENCE_HIGH` from Agent 1.** Add a note to the delegation boundaries table: "Agent 1 routing is binary — LOW threshold determines CLARIFICATION_NEEDED vs PENDING_MATCH. The HIGH threshold is not used for routing in Agent 1; it is passed downstream as `confidence_score` and interpreted by Agent 2." This gives the builder a clear instruction instead of a loaded variable and no use.

**Fix 3 — Add null-handling to the duplicate detection rule.** Current spec: "query existing records where shift_date, shift_start_time, and at least one required_credential match." Add: "When shift_start_time is null, match on hospital_id + shift_date + credential only (null = null must be handled explicitly — do not use SQL = comparison for nullable time fields)."

**Fix 4 — Define the cost-limit path's persistence contract.** Current spec says "route to coordinator manual queue." The builder interpreted this as an early return with a log line — no DB record created, no coordinator notification. Specify: "When the cost limit is exceeded, create a ShiftRequest record with status = CLARIFICATION_NEEDED and a flag indicating LLM unavailability, so the coordinator sees it in the queue and the ticket is not silently dropped."
