# Iteration 1 — Fix Record

## Gap fixed: Non-contracted fit phrases not matched (Category 1 — Spec Ambiguity)

### What was changed

**`prompt.md §5 — Fit phrases`**  
Added two entries to the fit phrase list:
```
`does not fit`, `did not fit`
```

**`classifier.py — _FIT_PHRASES`**  
Added the same two entries to the constant.

**`test_classifier.py`**  
Added T9 and T10 to cover the previously failing cases:
- T9: `"This does not fit me at all"` → DIDNT_FIT, 0.95
- T10: `"This did not fit me"` → DIDNT_FIT, 0.95

### Re-run result

```
10 passed in 0.11s
```

All 10 tests pass. The two previously failing probes now classify correctly.

### Fix location

Root cause was in the spec (prompt.md), not the builder implementation.  
The builder correctly implemented what was written — the phrase list was under-specified.  
Fix applied to both prompt.md (spec) and classifier.py (implementation) together.

### Secondary gap deferred

The bare `stitching` over-firing as defect (see `diagnosis.md`) is logged for iteration 2.
The compound phrase `stitching came loose` should replace standalone `stitching` / `stitch`
in the defect list to match the original agent spec's QA note.
