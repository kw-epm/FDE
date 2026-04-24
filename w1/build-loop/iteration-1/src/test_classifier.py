import pytest
from classifier import classify_reason


def test_t1_wrong_item_overrides_text():
    result = classify_reason(
        customer_reason_text="I just wanted to return this",
        condition_grade="GOOD",
        shipped_sku_id="APP-PANTS-32-GRY",
        returned_sku_id="APP-PANTS-32-BLK",
    )
    assert result.reason_code == "WRONG_ITEM"
    assert result.confidence == 0.97


def test_t2_competing_fit_and_defect():
    result = classify_reason(
        customer_reason_text="it didn't fit and also the stitching came loose",
        condition_grade="FAIR",
        shipped_sku_id="SKU-A",
        returned_sku_id="SKU-A",
    )
    assert result.reason_code == "AMBIGUOUS"
    assert result.confidence == 0.00


def test_t3_possible_customer_damage():
    result = classify_reason(
        customer_reason_text="the seam split after I washed it at high temperature",
        condition_grade="POOR",
        shipped_sku_id="SKU-A",
        returned_sku_id="SKU-A",
    )
    assert result.reason_code == "AMBIGUOUS"
    assert result.confidence == 0.00
    assert result.note == "Possible customer damage — manual review required"


def test_t4_pure_defect_claim():
    result = classify_reason(
        customer_reason_text="arrived damaged, zipper broken",
        condition_grade="LIKE_NEW",
        shipped_sku_id="SKU-A",
        returned_sku_id="SKU-A",
    )
    assert result.reason_code == "DEFECTIVE"
    assert result.confidence == 0.90


def test_t5_fit_return():
    result = classify_reason(
        customer_reason_text="didn't fit, too small",
        condition_grade="LIKE_NEW",
        shipped_sku_id="SKU-A",
        returned_sku_id="SKU-A",
    )
    assert result.reason_code == "DIDNT_FIT"
    assert result.confidence == 0.95


def test_t6_changed_mind_with_text():
    result = classify_reason(
        customer_reason_text="changed my mind",
        condition_grade="GOOD",
        shipped_sku_id="SKU-A",
        returned_sku_id="SKU-A",
    )
    assert result.reason_code == "CHANGED_MIND"
    assert result.confidence == 0.92


def test_t7_null_text_good_condition():
    result = classify_reason(
        customer_reason_text=None,
        condition_grade="GOOD",
        shipped_sku_id="SKU-A",
        returned_sku_id="SKU-A",
    )
    assert result.reason_code == "CHANGED_MIND"
    assert result.confidence == 0.70


def test_t8_empty_string_treated_as_null():
    result = classify_reason(
        customer_reason_text="",
        condition_grade="GOOD",
        shipped_sku_id="SKU-A",
        returned_sku_id="SKU-A",
    )
    assert result.reason_code == "CHANGED_MIND"
    assert result.confidence == 0.70


def test_t9_non_contracted_does_not_fit():
    """Non-contracted 'does not fit' must match fit phrase list (Gap 1 fix)."""
    result = classify_reason(
        customer_reason_text="This does not fit me at all",
        condition_grade="GOOD",
        shipped_sku_id="SKU-A",
        returned_sku_id="SKU-A",
    )
    assert result.reason_code == "DIDNT_FIT"
    assert result.confidence == 0.95


def test_t10_non_contracted_did_not_fit():
    """Non-contracted 'did not fit' must match fit phrase list (Gap 1 fix)."""
    result = classify_reason(
        customer_reason_text="This did not fit me",
        condition_grade="GOOD",
        shipped_sku_id="SKU-A",
        returned_sku_id="SKU-A",
    )
    assert result.reason_code == "DIDNT_FIT"
    assert result.confidence == 0.95
