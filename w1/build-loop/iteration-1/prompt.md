# RC-003 Reason Code Classifier — Build Spec

## 1. What to Build

A standalone Python module implementing the **RC-003 reason code classifier** for a retail returns
processing system. This is a pure function — no database, no network calls, no side effects.

Deliver:
- `classifier.py` — the classifier implementation
- `test_classifier.py` — acceptance tests (see §6)

---

## 2. Interface

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class ClassificationResult:
    reason_code: str        # one of: DEFECTIVE, DIDNT_FIT, CHANGED_MIND, WRONG_ITEM, AMBIGUOUS
    confidence: float       # range 0.000–1.000, three decimal places
    note: Optional[str]     # only populated for specific cases (see §4)

def classify_reason(
    customer_reason_text: Optional[str],   # may be None or empty string — treat both as null
    condition_grade: str,                  # LIKE_NEW | GOOD | FAIR | POOR | UNSELLABLE
    shipped_sku_id: str,
    returned_sku_id: str,
) -> ClassificationResult:
    ...
```

---

## 3. Pre-processing Rules

Before applying any classification rule:

- Treat `customer_reason_text = ""` (empty string) identically to `None`. Normalise to `None`.
- All keyword matching is **case-insensitive**.
- Strip leading/trailing whitespace from `customer_reason_text` before matching.

---

## 4. Classification Rules (Priority Order — First Match Wins)

Apply **one** rule. Stop at the first match.

### Rule 1 — Wrong Item (System-Verified)
**Condition:** `shipped_sku_id != returned_sku_id`  
**Result:** `reason_code = WRONG_ITEM`, `confidence = 0.97`, `note = None`  
_Text content is irrelevant — system evidence overrides._

---

### Rule 2 — Competing Fit + Defect Narratives
**Condition:** `customer_reason_text` contains at least one **fit** phrase AND at least one **defect**
phrase (after Rule 1 did not match)  
**Result:** `reason_code = AMBIGUOUS`, `confidence = 0.00`, `note = None`

---

### Rule 3 — Possible Customer Damage
**Condition:** `customer_reason_text` contains any **defect** phrase AND any **self-blame** phrase
(after Rules 1–2 did not match)  
**Result:** `reason_code = AMBIGUOUS`, `confidence = 0.00`,
`note = "Possible customer damage — manual review required"`

---

### Rule 4 — Defective
**Condition:** `customer_reason_text` contains any **defect** phrase
(and Rules 1–3 did not match)  
**Result:** `reason_code = DEFECTIVE`, `confidence = 0.90`, `note = None`

---

### Rule 5 — Didn't Fit
**Condition:** `customer_reason_text` contains any **fit** phrase  
**Result:** `reason_code = DIDNT_FIT`, `confidence = 0.95`, `note = None`

---

### Rule 6 — Changed Mind
**Condition:** `customer_reason_text` contains any **changed-mind** phrase  
**Result:** `reason_code = CHANGED_MIND`, `confidence = 0.92`, `note = None`

---

### Rule 7 — Null Text, Likely Changed Mind
**Condition:** `customer_reason_text` is None AND `shipped_sku_id == returned_sku_id` AND
`condition_grade` is `LIKE_NEW` or `GOOD`  
**Result:** `reason_code = CHANGED_MIND`, `confidence = 0.70`, `note = None`

---

### Rule 8 — Catch-All
**Condition:** None of the above matched  
**Result:** `reason_code = AMBIGUOUS`, `confidence = 0.00`, `note = None`

---

## 5. Keyword Lists

All matching is case-insensitive substring search unless noted.

### Defect phrases
`broken`, `torn`, `split`, `snapped`, `fell apart`, `stopped working`, `zipper broken`,
`button missing`, `seam split`, `defective`, `damaged on arrival`, `arrived damaged`,
`stitching`, `stitch`

### Fit phrases
`too small`, `too large`, `too tight`, `too loose`, `wrong size`, `doesn't fit`, `didn't fit`,
`does not fit`, `did not fit`,
`runs small`, `runs large`, `fit issue`, `size issue`, `sizing`

> Note: bare word `size` is **not** in the fit list — it is too broad.
> Only the compound phrases above match.

### Changed-mind phrases
`changed my mind`, `don't want`, `no longer need`, `found better`, `bought by mistake`,
`gift duplicate`, `impulse buy`

### Self-blame phrases
`my fault`, `i dropped`, `i washed`, `i altered`, `i damaged`, `i ruined`

---

## 6. Acceptance Tests

Implement all tests in `test_classifier.py` using `pytest`. All 8 must pass.

### T1 — Wrong item overrides text (Rule 1)
```
shipped_sku_id = "APP-PANTS-32-GRY"
returned_sku_id = "APP-PANTS-32-BLK"
customer_reason_text = "I just wanted to return this"
condition_grade = "GOOD"
Expected: reason_code=WRONG_ITEM, confidence=0.97
```

### T2 — Competing fit + defect narratives (Rule 2)
```
customer_reason_text = "it didn't fit and also the stitching came loose"
condition_grade = "FAIR"
shipped_sku_id = returned_sku_id = "SKU-A"
Expected: reason_code=AMBIGUOUS, confidence=0.00
```

### T3 — Possible customer damage (Rule 3)
```
customer_reason_text = "the seam split after I washed it at high temperature"
condition_grade = "POOR"
shipped_sku_id = returned_sku_id = "SKU-A"
Expected: reason_code=AMBIGUOUS, confidence=0.00,
          note="Possible customer damage — manual review required"
```

### T4 — Pure defect claim (Rule 4)
```
customer_reason_text = "arrived damaged, zipper broken"
condition_grade = "LIKE_NEW"
shipped_sku_id = returned_sku_id = "SKU-A"
Expected: reason_code=DEFECTIVE, confidence=0.90
```

### T5 — Fit return (Rule 5)
```
customer_reason_text = "didn't fit, too small"
condition_grade = "LIKE_NEW"
shipped_sku_id = returned_sku_id = "SKU-A"
Expected: reason_code=DIDNT_FIT, confidence=0.95
```

### T6 — Changed mind with text (Rule 6)
```
customer_reason_text = "changed my mind"
condition_grade = "GOOD"
shipped_sku_id = returned_sku_id = "SKU-A"
Expected: reason_code=CHANGED_MIND, confidence=0.92
```

### T7 — Null text, good condition, same SKU (Rule 7)
```
customer_reason_text = None
condition_grade = "GOOD"
shipped_sku_id = returned_sku_id = "SKU-A"
Expected: reason_code=CHANGED_MIND, confidence=0.70
```

### T8 — Empty string treated as null
```
customer_reason_text = ""
condition_grade = "GOOD"
shipped_sku_id = returned_sku_id = "SKU-A"
Expected: reason_code=CHANGED_MIND, confidence=0.70
(same result as T7 — empty string normalised to None)
```

---

## 7. Constraints

- Python 3.10+
- No external dependencies beyond the standard library and `pytest`
- The module must be importable on its own (`python -m pytest test_classifier.py` must work)
- Do not implement any module other than RC-003 — no OMS calls, no database, no WorkItem creation
