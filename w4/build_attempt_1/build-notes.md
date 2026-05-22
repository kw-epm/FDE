# Build Notes — Pavel 4a Cold Run

**Date of run:** 2026-05-22
**Builder:** Fresh Claude Code session, cold context
**Result:** End-to-end live run against mock fixtures succeeded (3 tickets persisted). 10 tests run, all pass on second iteration.

---

## a. What Claude Code asked clarifying questions about

The exam prompt told the builder not to ask mid-build (pick an interpretation and flag it). So this column is empty by design. The questions a cold builder would have asked are captured in the self-report under "Questions I would have asked" and in (c) below as silent picks.

---

## b. What Claude Code said it couldn't build

- **Postgres → SQLite.** `pg_isready` returned not-installed. Builder switched to SQLite (stdlib), kept the original Postgres `schema.sql` verbatim, wrote a parallel `schema_sqlite.sql`. Postgres-specific features (`gen_random_uuid`, `JSONB`, `CHECK char_length`) are documented but unverified.
- **`python3 -m venv` failed.** `python3-venv` package missing. Builder used `pip install --break-system-packages` into user-site, ignoring PEP 668.
- **`RealLLMClient` never exercised.** No Anthropic API key available. Build is functional but the real timeout + 5s retry path is untested.
- **FM-1 stateful failure counter.** The spec's "3 consecutive 5xx → ops alert + 15-min pause" loop was not implemented. Builder noticed and skipped. FM-1 test only checks single-cycle non-crash.
- **`OPS_ALERT_WEBHOOK_URL` POST.** Payload defined in spec, no `httpx.post` wired up. Alerts go to stderr only.
- **`DAILY_LLM_COST_LIMIT_USD` circuit breaker.** Env var defined; no counter, no store.
- **`CLARIFICATION_TIMEOUT_MINUTES` escalation.** Requires a scheduled job; none built.

---

## c. What Claude Code silently chose / added (most important)

- **Confidence formula entirely bypassed.** Builder wrote the system prompt verbatim (three-tier rule 6), then for testing used `FakeLLMClient` with canned responses keyed by source-text substrings. The three formulas in the spec never collide because the math never runs. More silent than picking one version — the contradiction was made irrelevant.
- **Duplicate suspected → `CLARIFICATION_NEEDED`.** Builder picked EC-4's status over the delegation table's confidence-driven status. Same call as the dry run, on a real contradiction inside 04a.
- **EC-7 multi-shift split: orchestrator-side regex, not LLM-side.** Builder added a regex ordinal-day scanner in `agent1_intake.py` after the LLM returned a single date. Spec gives the expected behavior but never says whether detection belongs in the LLM or the orchestrator. Builder called the regex "brittle."
- **FM-2 retry scope.** Builder retries both timeout AND schema-validation failures. Spec says "retry once after 5s" without saying which classes of failure that covers.
- **FM-3 visibility.** When the profile API is down, builder added an `INSUFFICIENT_INFORMATION` ambiguity flag to records that would otherwise be `PENDING_MATCH`. Spec says "log warning" without mandating a record-level flag.
- **`hospital_exists` semantics in mock mode.** Builder treats `_default` profile as "hospital not found" for EC-6 purposes. Explicit keys only. Alternative reading would break EC-6.
- **`shift_duration_hours`** still a Pydantic computed property only. Not in either SQL schema. Same drift the spec has.
- **`hospital_location`** copied from profile to the SQL row at parse time. Matches the DDL, not the data model.
- **`FakeLLMClient` as the default when no API key.** Builder made local dev frictionless by auto-selecting Fake instead of hard-failing at startup.
- **Python 3.13 instead of spec's Python 3.11.** Builder noted it and continued.
- **`EC-2` "step-down" → `GENERAL` + `RN` at confidence 0.75.** Builder hardcoded this in the canned `FakeLLMClient` response. Spec gives this as an expected output but the builder essentially had to be the LLM to make the test pass.
- **Idempotency uniqueness only application-side.** No UNIQUE INDEX in the SQLite schema. Builder checks via `already_processed` query, not DB constraint.
- **UTC `shift_date` across 5 states.** Copied without question. Cross-agent bug — only fires in Agent 2.

---

## d. What it built cleanly (matched spec intent)

- File layout matches the spec's project structure.
- 3 fixture tickets processed end-to-end on a live mock run:
  - `ticket_001` → `PENDING_MATCH`, 0.95, ICU + RN + ICU_CERTIFIED
  - `ticket_002` → `CLARIFICATION_NEEDED`, 0.55, urgency CRITICAL, DATE_UNCLEAR + TIME_UNCLEAR
  - `ticket_003` → `PENDING_MATCH`, 0.93, PEDIATRIC, RN + PEDS_CERTIFIED
- 10 tests pass on second iteration. EC-1, EC-2, EC-3, EC-4, EC-5, EC-6, EC-7, FM-1, FM-2, FM-3.
- EC-7 test failed first run (regex too rigid), fixed and passed second run.
- Idempotency confirmed: second poll cycle skipped all 3 tickets, zero duplicate rows.
- ServiceNow error matrix: 200/204/401/403/429/5xx/timeout all mapped per spec.
- FM-3 fallback to default shift times: implemented, ShiftRequest still created.
- Hospital profile 1-hour TTL in-memory cache.
- Confidence routing: `≥ 0.65 → PENDING_MATCH`, `< 0.65 → CLARIFICATION_NEEDED`.
- Audit log writes for `CREATED` and `LLM_PARSE_FAILURE`.
- System prompt loaded at runtime, not build time.

---

## Anything else worth flagging

- **Real environment friction is the new story.** Postgres absent, `venv` absent, PEP 668 blocked `pip`. None of these were anticipated by the peer review. The spec assumes a clean environment; the broader run shows that 30 minutes in a real builder's hands gets eaten by setup, not by spec interpretation.
- **`FakeLLMClient` is a real engineering choice the spec doesn't endorse or forbid.** It made tests possible, but it also bypassed the spec's confidence formula entirely. A diagnosis the dry run missed.
- **Python 3.13 vs 3.11.** Worked fine but a real deviation from `requirements.txt` intent.
