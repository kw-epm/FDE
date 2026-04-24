from dataclasses import dataclass
from typing import Optional


@dataclass
class ClassificationResult:
    reason_code: str
    confidence: float
    note: Optional[str]


_DEFECT_PHRASES = [
    "broken", "torn", "split", "snapped", "fell apart", "stopped working",
    "zipper broken", "button missing", "seam split", "defective",
    "damaged on arrival", "arrived damaged", "stitching", "stitch",
]

_FIT_PHRASES = [
    "too small", "too large", "too tight", "too loose", "wrong size",
    "doesn't fit", "didn't fit", "does not fit", "did not fit",
    "runs small", "runs large", "fit issue", "size issue", "sizing",
]

_CHANGED_MIND_PHRASES = [
    "changed my mind", "don't want", "no longer need", "found better",
    "bought by mistake", "gift duplicate", "impulse buy",
]

_SELF_BLAME_PHRASES = [
    "my fault", "i dropped", "i washed", "i altered", "i damaged", "i ruined",
]


def _contains_any(text: str, phrases: list[str]) -> bool:
    lowered = text.lower()
    return any(phrase in lowered for phrase in phrases)


def classify_reason(
    customer_reason_text: Optional[str],
    condition_grade: str,
    shipped_sku_id: str,
    returned_sku_id: str,
) -> ClassificationResult:
    # Normalise empty string to None
    if customer_reason_text is not None:
        customer_reason_text = customer_reason_text.strip()
        if customer_reason_text == "":
            customer_reason_text = None

    # Rule 1 — Wrong item (system-verified)
    if shipped_sku_id != returned_sku_id:
        return ClassificationResult(reason_code="WRONG_ITEM", confidence=0.97, note=None)

    if customer_reason_text is not None:
        has_defect = _contains_any(customer_reason_text, _DEFECT_PHRASES)
        has_fit = _contains_any(customer_reason_text, _FIT_PHRASES)
        has_self_blame = _contains_any(customer_reason_text, _SELF_BLAME_PHRASES)
        has_changed_mind = _contains_any(customer_reason_text, _CHANGED_MIND_PHRASES)

        # Rule 2 — Competing fit + defect narratives
        if has_fit and has_defect:
            return ClassificationResult(reason_code="AMBIGUOUS", confidence=0.00, note=None)

        # Rule 3 — Possible customer damage
        if has_defect and has_self_blame:
            return ClassificationResult(
                reason_code="AMBIGUOUS",
                confidence=0.00,
                note="Possible customer damage — manual review required",
            )

        # Rule 4 — Defective
        if has_defect:
            return ClassificationResult(reason_code="DEFECTIVE", confidence=0.90, note=None)

        # Rule 5 — Didn't fit
        if has_fit:
            return ClassificationResult(reason_code="DIDNT_FIT", confidence=0.95, note=None)

        # Rule 6 — Changed mind
        if has_changed_mind:
            return ClassificationResult(reason_code="CHANGED_MIND", confidence=0.92, note=None)

    # Rule 7 — Null text, likely changed mind
    if (
        customer_reason_text is None
        and shipped_sku_id == returned_sku_id
        and condition_grade in ("LIKE_NEW", "GOOD")
    ):
        return ClassificationResult(reason_code="CHANGED_MIND", confidence=0.70, note=None)

    # Rule 8 — Catch-all
    return ClassificationResult(reason_code="AMBIGUOUS", confidence=0.00, note=None)
