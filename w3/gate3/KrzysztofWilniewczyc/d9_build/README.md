# D#9 build — Planned Matching prototype

Implements **D#4a Capability Spec: Planned Matching** end-to-end as a runnable
Python prototype. Single-process, in-memory, no external dependencies.

## Run

```
python3 demo.py                 # all 7 scenarios
python3 demo.py worked          # spec §6 worked example only
python3 demo.py worked week2 expired comms decline lockdown lowconf
```

Requires Python 3.10+. No `pip install` needed.

## What it implements

All 13 process steps from D#4a §4, the lock state machine from §3, the
confidence ladder from §5, the trust ramp from §1, and the integration error
paths from §7. Each step prints a trace line so the spec ↔ code mapping is
visible.

| Spec step | File |
|---|---|
| 1 — Extract structured intent | `medflex/extractor.py` |
| 2 — Eligibility filter | `medflex/eligibility.py::eligible` |
| 3 — Compliance precondition | `medflex/eligibility.py::credentials_valid_for_shift` |
| 4 — Contextual reasoning over history | `medflex/ranker.py::_score_candidate` |
| 5 — Confidence scoring | `medflex/ranker.py::_confidence` |
| 6 — Confidence gate × trust ramp | `medflex/trust_ramp.py` |
| 7 — Coordinator review | `medflex/pipeline.py::CoordinatorDecision` |
| 8 — Soft-lock fires | `medflex/lock_store.py` |
| 9 — NurseOffer sent | `medflex/pipeline.py` + `medflex/comms.py` |
| 10 — Wait for nurse acceptance | `medflex/pipeline.py` |
| 11 — Hospital submission (KPI clock ends) | `medflex/pipeline.py` |
| 12 — Hospital acceptance | `medflex/pipeline.py` |
| 13 — Confirmed fill | `medflex/pipeline.py` |

## Scenarios

1. **worked** — §6 example. ICU + paediatric allergy at Hospital A. Nicole
   ranks above Mark on history + profile match → high confidence → auto-send
   at week 8 → confirmed fill in 33 min (KPI target ≤2h).
2. **week2** — same request, week-2 trust ramp. Every offer needs coordinator
   approval even at high confidence.
3. **expired** — edge case 5. Paula's credentials are expired so compliance
   drops her at step 3 with a flag.
4. **comms** — first two send attempts fail; retry loop succeeds on third.
5. **decline** — edge case 3. Nurse says no; soft-lock releases.
6. **lockdown** — lock-state store unavailable; step 8 halts; ops alerted.
7. **lowconf** — edge case 2. Vague email; extraction confidence below 0.85
   threshold so it routes to coordinator before ranking runs.

## Assumptions made during build (logged separately from spec §9)

See `ASSUMPTIONS.md`.

## What an LLM-backed version would change

Two functions:

- `extractor.extract()` — swap the regex/keyword extractor for a structured
  output LLM call (Anthropic SDK, JSON schema, two-pass with citation
  validation). Field-confidence values would come from the model.
- `ranker._score_candidate()` — swap the weighted scoring for an LLM that
  reasons over the nurse profile, hospital history, and the inbound email,
  returning a score + reasoning string per candidate. The orchestrator and
  contracts above and below would not change.
