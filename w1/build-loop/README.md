# Closed Build-Loop Log

Per `README-Participants-Intro-Week1.md` §The closed build loop, every participant must complete **at least one** full closed loop against their chosen scenario between Virtual Monday and end-of-day Virtual Thursday.

The loop:

1. Draft a spec for one feature or capability
2. Hand it to Claude Code — let it build
3. Review the output; identify at least one gap between what you asked for and what got built
4. Diagnose the gap using `spec-ambiguity-vs-builder-mistakes.md`:
   - **Category 1 — Spec Ambiguity** (you own the fix; rewrite the spec)
   - **Category 2 — Builder Misread** (builder owns the fix; re-prompt with the section highlighted)
   - **Category 3 — Test Problem** (validation owns the fix)
   - **Category 4 — Design Gap** (spec was silent on something obviously needed; add it)
5. Apply the fix to the root cause
6. Re-run and verify the fix actually closed the gap

---

## Target capability for iteration 1

**RC-003 Reason Code Classifier** — a pure function implementing the reason code classification
rules from `03_agent_specification.md §Module RC`. Picked because:

- Narrowest self-contained module (input: text + condition + SKU pair → reason code + confidence)
- Most testable (explicit priority-ordered rule set with keyword lists)
- No external integrations required — pure logic, verifiable in isolation
- Exercises the core classification contract that the rest of the agent depends on

Planned iteration-2+: bare `stitching` compound-phrase gap (secondary finding from iteration 1),
then fraud signal evaluator, then disposition routing table.

---

## Folder layout

Each iteration lives in its own folder:

```
build-loop/
  iteration-1/
    prompt.md      # the spec handed to Claude Code (standalone, no pack-loading required)
    output.md      # what Claude Code produced (code + commentary)
    diagnosis.md   # gap(s) identified + category per the spec-ambiguity-vs-builder-mistakes taxonomy
    fix.md         # what was changed, where, and re-run evidence
  iteration-2/
    ...
```

## Iteration log

| # | Date | Capability | Gap category | Fix location | Status |
|---|------|-----------|---------------|--------------|--------|
| 1 | 2026-04-24 | RC-003 Reason Code Classifier | 1 — Spec Ambiguity (non-contracted fit phrases) | `iteration-1/prompt.md §5`; `iteration-1/classifier.py _FIT_PHRASES` | closed — 10/10 tests pass |

---

## How to run iteration 1

1. Open a fresh Claude Code session in this folder.
2. Hand it `iteration-1/prompt.md` as the task description. **Do not** let it load the full spec pack — the prompt is deliberately self-contained so that gaps in the prompt are visible, not papered over by the pack.
3. Save Claude Code's output (code + commentary) to `iteration-1/output.md`.
4. Run the provided acceptance tests (see prompt §6). Record outcomes in `output.md`.
5. Identify ≥ 1 gap between ask and output. Classify per `spec-ambiguity-vs-builder-mistakes.md`. Write `diagnosis.md`.
6. Apply the fix **at the root cause**:
   - Category 1 (spec ambiguity) → edit `prompt.md` and/or `03-agent-spec.md`
   - Category 2 (builder misread) → re-prompt Claude Code highlighting the missed section
   - Category 3 (test problem) → fix acceptance test in `prompt.md §6`
   - Category 4 (design gap) → add the missing rule to the spec artifacts
7. Re-run. Record in `fix.md`.
8. Update the log table above with date, gap category, fix location, status.
