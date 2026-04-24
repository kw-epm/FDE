# Iteration 1 — Diagnosis

## Primary Gap — Non-contracted fit phrases not matched

**Observed behaviour:** `"This did not fit me"` → AMBIGUOUS (confidence 0.00)  
**Expected behaviour:** DIDNT_FIT (confidence 0.95)

**Root cause:** The fit phrase list in the prompt (§5) contains only contracted forms:
`doesn't fit`, `didn't fit`. The builder correctly implemented exactly what was specified.
The spec was silent on non-contracted equivalents, so they were never added to the list.

**Gap category: 1 — Spec Ambiguity**  
The spec owns the fix. The prompt's phrase list was under-specified.

**Fix:** Add `does not fit` and `did not fit` to the fit phrase list in `prompt.md §5`.
Update `classifier.py` accordingly. Add two new tests (T9, T10) to `test_classifier.py`.

---

## Secondary Gap — Bare 'stitching' over-fires as defect

**Observed behaviour:** `"Nice stitching but too tight"` → AMBIGUOUS  
**Expected behaviour:** DIDNT_FIT

**Root cause:** The prompt listed `stitching` and `stitch` as standalone defect phrases.
The original agent spec has a note: `stitch (match stitching and came loose together in QA tests)`,
which reads as: the intended defect trigger is the compound phrase `stitching came loose`, not
bare `stitching`. The prompt dropped this compound-phrase constraint when transcribing the list.

**Gap category: 1 — Spec Ambiguity**  
The prompt over-simplified the keyword list. The builder implemented what was written; the
written spec was incomplete.

**Fix:** Replace the separate `stitching` / `stitch` entries in the defect phrase list with the
compound phrase `stitching came loose` (and optionally `stitch came loose`). Update `classifier.py`
and add a regression test.

---

## Decision: Fix Primary Gap in This Iteration

The non-contracted fit phrase gap (Gap 1) is chosen for the iteration-1 fix because:
- Higher frequency impact: `did not fit` / `does not fit` are common natural-language forms
- Clear, unambiguous fix: two phrase additions to the list
- Directly testable: two new test cases

The stitching gap will be logged and addressed in iteration 2 alongside a review of
other keyword entries that may have the same compound-phrase ambiguity.
