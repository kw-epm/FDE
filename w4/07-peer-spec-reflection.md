# Deliverable #7 — Build-loop reflection on a peer spec
**Engagement:** MedFlex Healthcare Staffing
**Spec under test:** Pavel Klimasheuski — `04a-capability-spec-intake.md`
**Peer review under test:** Pavel section of `03-peer-reviews.md`
**Date:** 2026-05-22

---

## 1. What the cold build produced

A fresh Claude Code session built the agent and ran it end-to-end against the mock fixtures. Three ServiceNow fixture tickets were processed and persisted with the right statuses (one `CLARIFICATION_NEEDED`, two `PENDING_MATCH`). Ten tests covering EC-1..EC-7 and FM-1..FM-3 were written; nine passed on the first run and one (EC-7) passed after a regex fix. A second poll cycle confirmed idempotency — zero duplicate rows. The build punted on real environment frictions the spec did not anticipate: no Postgres available (switched to SQLite), no `python3-venv` (used `--break-system-packages`), no Anthropic API key (built and used a `FakeLLMClient`).

## 2. Issues my peer review caught that the build confirmed

- **Concern #3 — three confidence formulas in 04a.** The builder wrote the system prompt verbatim with rule 6's three-tier buckets, and then skipped the math entirely by using a `FakeLLMClient` with canned scores. The three formulas in the spec never collided because the math never ran. As silent as it gets — the builder made the contradiction irrelevant rather than choosing between versions.
- **Concern #6 — shared `$50` cost limit with no shared counter.** Builder defined the env var, never built the counter or the store. Same reason: the spec does not name a place for it to live.
- **Concern #4 — EC-5 null-time route.** Test passed: null-time requests went to `PENDING_MATCH` with `TIME_UNCLEAR`, exactly as the review warned. The downstream zero-match risk needs Agent 2 to fire.

## 3. Issues my peer review missed (false negatives)

Most are contradictions *inside 04a alone*. A careful re-read should have caught them. The bullets are the evidence; the pattern is named at the end.

- **EC-7 multi-shift expansion — detection responsibility is undefined.** Spec gives the expected output (three rows with sequence numbers) but never says whether the LLM or the orchestrator does the split. The builder added an orchestrator-side regex, the first version failed its own test, and the builder called the regex brittle. My review did not mention EC-7 at all.
- **EC-4 versus delegation table — what status does a duplicate get?** The delegation table says MEDIUM confidence with flags → `PENDING_MATCH`. EC-4 says a duplicate → `CLARIFICATION_NEEDED`. A real contradiction inside 04a alone. The builder picked CLARIFICATION_NEEDED both times. I missed it.
- **Data model does not match the SQL.** `shift_duration_hours` is required in the data model but missing from the DDL. `hospital_location` is in the DDL but missing from the data model. Builder kept the first as a Pydantic property and silently accepted the second.
- **EC-6 (unknown hospital) vs FM-3 (profile API down).** Two different rules for two different failures, but only one lookup path. The builder treated `_default` as "hospital not found" to make EC-6 work — a choice the spec did not name.
- **FM-2 retry scope.** "Retry once after 5s" — does that cover only timeouts, or schema-validation failures too? Builder retries both. Spec is silent.
- **FM-3 visibility.** Spec says "log warning" when profile is missing. Builder added an `INSUFFICIENT_INFORMATION` flag to the record on top of the log. Reasonable, but not in the spec.
- **FM-1 stateful failure counter.** Spec describes the behavior ("3 consecutive 5xx → ops alert + 15-min pause") but does not specify the state machine. Builder noticed and skipped. Test only checks non-crash on a single failure.
- **"JSON mode or tool use" is not literally true for the Anthropic SDK.** No OpenAI-style JSON mode parameter. Builder fell back to prompt instruction + Pydantic validation. A real-world gap I did not catch.
- **Postgres dependency assumed cleanly available.** Spec demands Postgres + `psycopg2-binary`. Real-world WSL has neither, and `python3 -m venv` was also missing. The spec gives the builder no fallback path. Builder switched to SQLite and used `--break-system-packages`. Both are real friction my review did not anticipate.
- **`current_datetime_utc` — receipt timestamp or wall-clock?** Builder picked `sys_created_on`. Under polling lag the two differ. I did not raise this.
- **PHI-safe logging.** Spec says do not log `source_text` in plain text. The review did not mention it. The build kept `source_text` out of the `audit_log` table, but exception messages and other log lines can still carry it. A predicted miss I never predicted.
- **`FakeLLMClient` as a build choice.** The spec does not endorse or forbid it, and the builder used it not just for tests but as the default when no API key is set. That decision made the build runnable AND made the spec's confidence math untestable in this run. Real engineering decision the spec gave no guidance for.

**The pattern.** I caught contradictions between *numbers* — three confidence formulas, two proximity formulas, a shared cost limit with no shared counter, a CRITICAL timeout longer than the standard one. I missed contradictions between *states, schemas, and rules* — duplicate status, schema vs data model, EC-6 vs FM-3, FM-1 state machine, FM-2 retry scope. And I missed *build-only realities* — EC-7's missing LLM mechanism, the SDK reality of "JSON mode", Postgres not available in a standard environment, and the easy choice to build a `FakeLLMClient` that hides the spec's own contradictions. The review read the spec. It did not simulate the build.

## 4. Issues my peer review flagged that the build did not trigger (false positives)

These are real bugs the exam could not surface, not weaknesses in the review.

- **Blocker #1 — `shift_date` as UTC across five states.** The bug only fires when Agent 2 compares overlap windows. Invisible in a single-agent build.
- **Blocker #2 (proximity formulas), Concern #5 (`OTHER` enum), Missing #7 (CRITICAL timeout)** all live in 04b. The exam covered 04a only.

The structural point: my peer review covered 04a and 04b together. The build exam covered 04a only. Four of seven items in the review are not testable by this exam.

## 5. What I would change in Pavel's spec if I had another 30 minutes

1. Pick one confidence formula. Delete the other two. Make the prompt and the data model match.
2. Either remove EC-7 from 04a or specify the detection mechanism — does the LLM output a list of shifts, or does the orchestrator split? Pick one.
3. Fix the conflict between EC-4 and the delegation table. State plainly what status a duplicate gets.
4. Add `shift_duration_hours` to the SQL DDL or remove it from the data model. Do the same for `hospital_location`.
5. Separate EC-6 from FM-3 in the integration contract. One is "hospital not in registry", the other is "profile API unreachable". They need different code paths.
6. Specify FM-1 as a state machine, not a behavior sketch. Counter, pause state, resume condition.
7. Specify FM-2 retry scope: which failure classes are retried.
8. Replace "JSON mode or tool use" with the actual SDK call. For the Anthropic SDK that means tool-use with the schema as the tool's `input_schema`.
9. Move `shift_date` timezone handling into the spec's main rules: store local date plus hospital timezone, convert when comparing.
10. Address the environment gap directly: if the spec mandates Postgres, name a fallback (SQLite for local dev, container for setup) or accept that 30 minutes of build time will mostly be infrastructure setup.
