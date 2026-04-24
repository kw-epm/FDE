# Iteration 1 — RC-003 Reason Code Classifier

**Scenario:** Scenario 3 — Retail Returns Disposition  
**Week:** Week 1 — AI-Native Specification  
**Build-loop iteration:** 1 of N  
**Status:** closed — 10/10 tests pass

---

## What this is

A standalone Python implementation of the **RC-003 reason code classifier** from the Returns
Disposition Agent spec (`03_agent_specification.md §Module RC`). It is a pure function — no
database, no network calls, no side effects.

Given a customer's return reason text, the item condition grade, and the shipped vs. returned
SKU pair, it outputs one of five reason codes (`DEFECTIVE`, `DIDNT_FIT`, `CHANGED_MIND`,
`WRONG_ITEM`, `AMBIGUOUS`) with a confidence score and an optional diagnostic note.

The gap found in this iteration: the spec phrase list contained only contracted forms
(`doesn't fit`, `didn't fit`). Non-contracted equivalents (`does not fit`, `did not fit`)
returned AMBIGUOUS. Fix: both forms added to the fit phrase list. See `../diagnosis.md`
and `../fix.md` for the full record.

---

## Files

| File | Purpose |
|---|---|
| `classifier.py` | RC-003 classifier implementation |
| `test_classifier.py` | 10 acceptance tests (T1–T8 from spec; T9–T10 added by fix) |
| `README.md` | This file |

The build prompt is at `../prompt.md`. Output notes, diagnosis, and fix record are at
`../output.md`, `../diagnosis.md`, `../fix.md`.

---

## How to run

```bash
cd w1/build-loop/iteration-1/src
python3 -m pytest test_classifier.py -v
```

Expected output: `10 passed`.

**Requirements:** Python 3.10+, pytest. No other dependencies.
