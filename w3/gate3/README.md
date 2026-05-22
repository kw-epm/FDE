# Gate 3 — MedFlex engagement

**Participant:** Krzysztof Wilniewczyc
**Scenario:** MedFlex healthcare staffing agency (200 employees, "10x without 10x-ing the coordinators")
**Source pack:** `../../inputs/Week3/Gate3-Participant-Pack.md` *(released Thu 09:00 CET)*

## Timeline

| Slot | What happens here |
|---|---|
| Thu 09:00 | Pack released — read end-to-end |
| Thu 09:00–09:30 | Discovery questions prepared → `discovery_questions.md` |
| Thu 09:30–10:30 | Live discovery call → notes into `discovery_notes.md` |
| Thu afternoon | Rough drafts of D#1 / D#2 / D#3 |
| Thu 23:59 | Interim submission to squad lead (D#1–D#3, not graded) |
| Fri 09:00 | Marcus Reyes pushback email arrives |
| Fri 09:00–13:30 | Prep window — process pushback, plan D#6 |
| Fri 13:30–17:00 | Timed gate — finalise all 9 deliverables |
| Fri 17:00 | Submission cutoff (sharp) |
| Fri 17:50–19:00 | 10-min verbal defense |

## Deliverables

**Thursday EOD (interim, not graded):**
- `D1_problem_framing.md` — what's actually broken + measurable success metrics
- `D2_intake_and_scope.md` — context, stakeholders, constraints, MVP, out-of-scope
- `D3_architecture_and_adrs.md` — agentic architecture + ≥2 ADRs with trade-offs

**Friday gate (timed):**
- `D4_capability_specs/` — two production-grade specs, shared entities consistent
- `D5_buildloop_response.md` — references the Cascade fixture diagnosed Wed
- `D6_client_feedback_response.md` — response to Marcus pushback
- `D7_validation_plan.md`
- `D8_reflection.md`
- `D9_selfspec_buildloop_reflection.md` — 1 page, run one D#4 spec through Claude Code, diagnose honestly

## Key reminders (from inputs/Week3/README*.md)

- **AI-native, not AI-bolted-on.** Architecture must have a real agentic decision point — reasoning over context, not a deterministic matcher with an LLM call sprinkled in.
- **Frame the real problem, not the stated one.** "10x without 10x-ing" is a business outcome, not a requirement.
- **ADRs must name alternatives + consequences**, not justify a single choice.
- **D#6: hold scope without alienating.** Concede with concrete alternatives where appropriate; refuse where it would break the engagement.
- **D#9 graded on diagnosis honesty, not code correctness.** A broken build diagnosed precisely beats a working build diagnosed defensively.
