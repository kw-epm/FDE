# Build Notes — Pavel 4a Cold Run

**Date of run:** 2026-05-22
**Builder:** Fresh subagent session, cold context (no prior FDE conversation)
**Wall-clock duration:** ~7.5 min (18 tool calls); a real 30-min terminal run would have allowed more code paths and tests
**Result:** All 12 Python files compile clean. No end-to-end execution test was run.

---

## a. What Claude Code asked clarifying questions about

The exam prompt told the builder not to ask mid-build (pick an interpretation and flag it). So this column is empty by design. The questions a cold builder would have asked are captured in (c) as silent picks and in the self-report under "Questions I would have asked".

---

## b. What Claude Code said it couldn't build

- **EC-7 multi-shift expansion.** The LLM output schema is single-object. The system prompt has no rule for detecting "3 ICU RNs for nights the 20th, 21st, and 22nd". Builder treated each ticket as one ShiftRequest and left a code comment.
- **Daily `$50` LLM cost circuit breaker.** Env var `DAILY_LLM_COST_LIMIT_USD` was wired into `.env.example`, but no counter, no shared store, no per-call accounting was built.
- **Coordinator clarification UI and the 60-min supervisor escalation.** Spec says the queue is just a SQL query; builder built only the status side, no resolution flow, no scheduler.
- **`shift_duration_hours` range check (1.0–24.0).** Builder computed it as a property but did not validate the range.
- **`preferred_credential_categories` propagation.** Builder passes the whole hospital-profile dict to the LLM, but the system prompt only tells the model to read `standard_shift_times` and `common_unit_types`. The other fields are visible but uninstructed — the broader spec hints they could be useful context.
- **Tests.** None written.
- **PHI-safe logging.** Builder logs `servicenow_ticket_id` everywhere but does not strip `source_text` from exception messages.

---

## c. What Claude Code silently chose / added (most important)

- **Confidence formula:** picked the system prompt's three-tier 1.0 / 0.5 / 0.0 buckets. Did not notice the data model's binary version or the "weighted minimum" wording. No reconciliation code.
- **Duplicate suspected status:** picked `CLARIFICATION_NEEDED` (EC-4) over the delegation table's confidence-driven status. Real spec conflict.
- **`shift_duration_hours`:** kept as a Pydantic computed property only, not persisted in SQL. Did not add a column.
- **`hospital_location`:** copied from hospital profile to the SQL column at parse time (matches the DDL, not the data model).
- **EC-6 vs FM-3:** picked "no row written, ops alert fired" for unknown hospital. Conflated "hospital registry" with "hospital profile API" because the spec doesn't separate them.
- **`current_datetime_utc` in the LLM call:** passed `sys_created_on` (receipt timestamp) instead of wall-clock `datetime.now()`. Under polling lag the two differ.
- **"JSON mode or tool use":** fell back to system-prompt instruction + Pydantic validation. Did not use Anthropic tool-use (the realistic option).
- **Sonnet trigger:** keyword scan on `source_text` *before* the LLM call (CRITICAL keyword detection). Date-based CRITICAL (shift in 6 hours, no keyword) still uses Haiku.
- **"High complexity" hospital:** chose `len(common_unit_types) > 4` as the proxy. Spec did not define it.
- **Idempotency:** added a unique index on `(servicenow_ticket_id, ticket_sequence_num)` that the spec's SQL doesn't have. Improved on the spec without flagging.
- **Markdown fence stripping:** defensive strip added to LLM output despite the prompt forbidding fences.
- **`shift_date ≥ today`:** not enforced. A past date from the LLM would be stored.
- **UTC `shift_date` across 5 states:** copied without question. (Cross-agent bug — only fires in Agent 2.)

---

## d. What it built cleanly (matched spec intent)

- File layout matches the spec's project structure exactly.
- `requirements.txt`, `schema.sql`, `.env.example`, mock fixtures all present.
- Pydantic models for the full shared glossary (CredentialCategory, UnitType, Urgency, AmbiguityType, ShiftRequestStatus, ParsedBy).
- Atomic insert across `shift_requests` + `credential_requirements` + `ambiguity_flags` in one transaction.
- ServiceNow error handling matrix: 200, 204, 401/403 pause, 429 Retry-After, 5xx retry-once, timeout treated as 5xx.
- FM-1 three-consecutive-failure ops alert + 15-min polling pause.
- FM-2 LLM parse failure → ticket routed to coordinator manual queue, raw response logged.
- FM-3 hospital profile unavailable → default profile, no block.
- Hospital profile 1-hour TTL in-memory cache; mock-vs-real switch.
- Confidence routing: `≥ 0.65 → PENDING_MATCH`, `< 0.65 → CLARIFICATION_NEEDED`.
- Audit log writes for `CREATED` and `AMBIGUITY_FLAGGED`.
- SIGINT / SIGTERM graceful shutdown.
- System prompt loaded at runtime, not build time (matches the spec's deployment-review rule).

---

## Anything else worth flagging

- Builder thought `claude-sonnet-4-6` would 404 because it has no date suffix like the Haiku ID. Real misconception, but did not change the build outcome — the model is correctly named per current Anthropic IDs.
- Builder added the unique index on `(servicenow_ticket_id, ticket_sequence_num)` without being told to. A spec improvement, but EC-7 wasn't built, so the index only protects the single-shift path today.
- Soft budget (7.5 min, 18 tool calls) was generous enough to cover the main paths. A stricter 30-min wall-clock with real `pip install` + DB setup would likely have cut tests, audit writes, or one of the failure-mode branches.
