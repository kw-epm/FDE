# Iteration 1 — Output

## What Was Built

`classifier.py` — a pure Python module implementing the RC-003 rule set.  
`test_classifier.py` — 8 acceptance tests matching the prompt's §6 test suite.

### Implementation approach

- `ClassificationResult` dataclass with `reason_code`, `confidence`, `note`
- Four keyword lists as module-level constants (defect, fit, changed-mind, self-blame)
- `_contains_any(text, phrases)` helper — lowercased substring search
- `classify_reason()` applies rules 1–8 in priority order, returns on first match
- Pre-processing: strips whitespace, normalises `""` → `None`

### Test results

```
8 passed in 0.15s
```

All 8 spec-defined acceptance tests pass.

---

## Post-Build Probing

After the 8 spec tests passed, additional cases were run to probe boundaries
not covered by the test suite.

### Probe A — non-contracted fit phrases

| Input text | Expected | Actual |
|---|---|---|
| "This does not fit me at all" | DIDNT_FIT | **AMBIGUOUS** |
| "This did not fit me" | DIDNT_FIT | **AMBIGUOUS** |
| "This doesn't fit me" | DIDNT_FIT | DIDNT_FIT ✓ |

The fit phrase list contains only `doesn't fit` and `didn't fit` (contracted forms).
Non-contracted equivalents (`does not fit`, `did not fit`) produce no fit match →
fall through to Rule 8 → AMBIGUOUS. In real returns data, customers write both forms.

### Probe B — 'stitching' in a positive context alongside a fit complaint

| Input text | Expected | Actual |
|---|---|---|
| "Nice stitching but too tight" | DIDNT_FIT | **AMBIGUOUS** |

`stitching` is in the defect phrase list as a standalone token. When a customer
praises the stitching but then mentions a fit complaint, the classifier fires
Rule 2 (competing fit + defect) → AMBIGUOUS instead of DIDNT_FIT.

The original agent spec note reads: `stitch (match stitching and came loose together in QA tests)`.
This suggests the QA intent was for "stitching came loose" as a compound phrase, not bare
"stitching" as a defect trigger on its own. The prompt simplified it to a standalone entry.
