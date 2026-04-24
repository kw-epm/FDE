# FDE Week 1 — Retail Returns Disposition Agent

**Author:** Krzysztof Wilniewczyc  
**Scenario:** 3  
**Status:** Gate-1 draft

---

This repo is my Week 1 working space for the FDE programme. It contains the full specification pack for an AI agent built against a retail returns scenario — problem statement, delegation analysis, agent spec, validation design, and assumptions register — plus a closed build-loop log where parts of the spec are handed to Claude Code, built, tested, and diagnosed for gaps.

---

## Scenario description

*Based on: [`w1/scenario_definition.txt`](./w1/scenario_definition.txt)*

A 12-person team at a central returns facility processes ~4,500 items per week by eye and by memory — no rulebook, no tooling. They get the reason code wrong 1 in 4 times, and miss 60% of fraudulent returns at intake. This project specifies an agent that takes over the routine cases, surfaces fraud signals before the item leaves the floor, and routes everything else to the right human with enough context to decide quickly.

The hard constraint that shapes the whole design: the agent never releases or rejects a fraud-flagged return. It flags, scores, and holds. Loss Prevention decides.

---

## What's in here

| File | What it is |
|---|---|
| [`w1/artifacts/01_problem_statement.md`](./w1/artifacts/01_problem_statement.md) | The business case — losses, stakeholders, success metrics, CFO payback |
| [`w1/artifacts/02_delegation_analysis.md`](./w1/artifacts/02_delegation_analysis.md) | What the agent does alone, what it flags, what requires a human signature |
| [`w1/artifacts/03_agent_specification.md`](./w1/artifacts/03_agent_specification.md) | The full spec — data model, processing modules, integrations, escalation rules |
| [`w1/artifacts/04_validation_design.md`](./w1/artifacts/04_validation_design.md) | Test scenarios: happy path, edge cases, failure modes, delegation boundaries |
| [`w1/artifacts/05_assumptions_unknowns.md`](./w1/artifacts/05_assumptions_unknowns.md) | What the spec is betting on being true, and what's still open |
| [`w1/supporting/current_state_process.md`](./w1/supporting/current_state_process.md) | The as-is process in detail |
| [`w1/supporting/stakeholder_discovery.md`](./w1/supporting/stakeholder_discovery.md) | Discovery findings — confirmed facts vs. open questions |
| [`w1/00_orientation.md`](./w1/00_orientation.md) | Private orientation doc — the tensions, the hard questions, how the files fit together |
| [`w1/build-loop/`](./w1/build-loop/README.md) | Closed build-loop log: one iteration completed on the reason code classifier |

---

## Gate 1 deliverables

Artifacts 1–5 above map directly to the five Gate 1 deliverables.

---

## Build loop

One iteration complete. The RC-003 reason code classifier was built from a self-contained prompt, tested, and a spec ambiguity was found and fixed (non-contracted fit phrases — `"did not fit"` vs `"didn't fit"` — were missing from the keyword list). 10/10 tests pass. Full record in `w1/build-loop/iteration-1/`.
