"""
Tests against real Gate 2 artefact data.

Run: python -m bdra.tests
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path

from bdra.aurum_schema_validator import (
    APEX_SCHEMAS, SchemaDriftError, validate_csv_header, validate_all,
)
from bdra.audit_ref_generator import (
    SchemaCollisionError, generate_audit_ref, is_agent_emitted,
)
from bdra.credit_packet import (
    CreditPacket, PacketValidationError, ReasonCode, validate_for_submission,
)


# Real Gate 2 artefact files.
ARTEFACTS_DIR = Path(
    "/mnt/c/xyh/fde/inputs/Week2/Gate2-Artefacts"
)


class SchemaValidatorTests(unittest.TestCase):
    """Exercises against the real Aurum CSVs from the Gate 2 artefact pack."""

    def test_credits_csv_matches_contract(self) -> None:
        result = validate_csv_header(
            ARTEFACTS_DIR / "APEX_CREDITS_20260414.csv", "APEX_CREDITS"
        )
        self.assertTrue(result.is_valid)
        self.assertEqual(result.contract_hash, result.actual_hash)

    def test_bill_daily_csv_matches_contract(self) -> None:
        result = validate_csv_header(
            ARTEFACTS_DIR / "APEX_BILL_DAILY_20260414.csv", "APEX_BILL_DAILY"
        )
        self.assertTrue(result.is_valid)

    def test_disputes_csv_matches_contract(self) -> None:
        result = validate_csv_header(
            ARTEFACTS_DIR / "APEX_DISPUTES_OPEN_20260414.csv",
            "APEX_DISPUTES_OPEN",
        )
        self.assertTrue(result.is_valid)

    def test_customer_master_csv_matches_contract(self) -> None:
        result = validate_csv_header(
            ARTEFACTS_DIR / "APEX_CUSTOMER_MASTER_20260401.csv",
            "APEX_CUSTOMER_MASTER",
        )
        self.assertTrue(result.is_valid)

    def test_drift_detection_column_added(self) -> None:
        """Simulates the prior-RPA failure mode: Aurum adds a column quarterly."""
        with tempfile.NamedTemporaryFile(
            "w", delete=False, suffix=".csv", newline=""
        ) as f:
            f.write("CREDIT_ID,INVOICE_NO,CUSTOMER_ID,CREDIT_AMT,REASON_CODE,"
                    "APPROVER_ID,AUDIT_REF,APPLIED_DT,NEW_COLUMN_ADDED_BY_AURUM\n")
            f.write("CR-1,INV-1,C-1,10.00,GOODWILL,U-001,AUD-1,2026-01-01,x\n")
            tmp = Path(f.name)
        try:
            with self.assertRaises(SchemaDriftError) as ctx:
                validate_csv_header(tmp, "APEX_CREDITS")
            self.assertIn("column count", str(ctx.exception))
            self.assertIn("Halt agent", str(ctx.exception))
        finally:
            tmp.unlink()

    def test_drift_detection_column_renamed(self) -> None:
        with tempfile.NamedTemporaryFile(
            "w", delete=False, suffix=".csv", newline=""
        ) as f:
            f.write("CREDIT_ID,INVOICE_NO,CUSTOMER_ID,CREDIT_AMT,REASON_CODE,"
                    "APPROVED_BY,AUDIT_REF,APPLIED_DT\n")
            tmp = Path(f.name)
        try:
            with self.assertRaises(SchemaDriftError) as ctx:
                validate_csv_header(tmp, "APEX_CREDITS")
            self.assertIn("APPROVER_ID", str(ctx.exception))
            self.assertIn("APPROVED_BY", str(ctx.exception))
        finally:
            tmp.unlink()

    def test_unknown_contract_raises_keyerror(self) -> None:
        with self.assertRaises(KeyError):
            validate_csv_header(Path("anything.csv"), "APEX_NONEXISTENT")


class AuditRefGeneratorTests(unittest.TestCase):

    def test_normal_format(self) -> None:
        ref = generate_audit_ref(
            "P12345", now=datetime(2026, 5, 6, tzinfo=timezone.utc), seq=1,
        )
        self.assertEqual(ref, "AUD-2026-BDRA-P12345-01")
        self.assertTrue(is_agent_emitted(ref))

    def test_human_audit_ref_recognised_as_not_agent(self) -> None:
        # Real human format from APEX_CREDITS data.
        self.assertFalse(is_agent_emitted("AUD-2026-00211"))
        self.assertFalse(is_agent_emitted("AUD-2026-00212"))

    def test_long_processing_id_truncated(self) -> None:
        """SPEC GAP #6: collision risk if Aurum has a length cap.
        Build mitigation: cap output at 30 chars, mark truncation with ~.
        """
        long_pid = "C-DSP-2026-04-00342-EXTRA-CONTEXT"
        ref = generate_audit_ref(
            long_pid, now=datetime(2026, 1, 1, tzinfo=timezone.utc), seq=1,
        )
        self.assertLessEqual(len(ref), 30)
        self.assertTrue(ref.endswith("-01"))
        # Truncation marker present:
        self.assertIn("~", ref)
        self.assertTrue(is_agent_emitted(ref))

    def test_seq_increments_per_processing_id(self) -> None:
        ref1 = generate_audit_ref("P-NEW-001")
        ref2 = generate_audit_ref("P-NEW-001")
        self.assertNotEqual(ref1, ref2)
        self.assertTrue(ref1.endswith("-01"))
        self.assertTrue(ref2.endswith("-02"))

    def test_empty_processing_id_rejected(self) -> None:
        with self.assertRaises(ValueError):
            generate_audit_ref("")


class CreditPacketTests(unittest.TestCase):

    def _make_packet(self) -> CreditPacket:
        return CreditPacket(
            invoice_no="INV-2026-04318",
            customer_id="C-04451",  # Hayes & Sons
            credit_amt=Decimal("170.00"),  # The artefact-2 case.
            reason_code=ReasonCode.GOODWILL,
            audit_ref="AUD-2026-BDRA-P-001-01",
            processing_id="P-001",
            dispute_id="D-2026-00342",
        )

    def test_packet_aurum_record_omits_approver_and_applied_dt(self) -> None:
        record = self._make_packet().to_aurum_record()
        self.assertEqual(record["APPROVER_ID"], "")
        self.assertEqual(record["APPLIED_DT"], "")
        self.assertEqual(record["AUDIT_REF"], "AUD-2026-BDRA-P-001-01")
        self.assertEqual(record["CREDIT_AMT"], "170.00")

    def test_validate_for_submission_requires_approver(self) -> None:
        packet = self._make_packet()
        with self.assertRaises(PacketValidationError) as ctx:
            validate_for_submission(packet, approver_id="", applied_dt=date.today())
        self.assertIn("BDRA cannot self-approve", str(ctx.exception))

    def test_validate_for_submission_succeeds_with_approver(self) -> None:
        packet = self._make_packet()
        record = validate_for_submission(
            packet, approver_id="U-0089", applied_dt=date(2026, 5, 6),
        )
        self.assertEqual(record["APPROVER_ID"], "U-0089")
        self.assertEqual(record["APPLIED_DT"], "2026-05-06")

    def test_zero_amount_rejected(self) -> None:
        packet = CreditPacket(
            invoice_no="INV-X", customer_id="C-X",
            credit_amt=Decimal("0.00"),
            reason_code=ReasonCode.GOODWILL,
            audit_ref="AUD-2026-BDRA-X-01",
            processing_id="X",
        )
        with self.assertRaises(PacketValidationError):
            validate_for_submission(packet, "U-001", date.today())


class SandraScenarioReplay(unittest.TestCase):
    """End-to-end: replay the Sandra-£170 scenario with BDRA enforcement.

    Demonstrates: the audit gap from Artefact 2 cannot occur in the BDRA
    flow — APPROVER_ID enforcement is system-enforced, not procedural.
    """

    def test_sandra_170_scenario_blocked_without_approver(self) -> None:
        # Setup matches Artefact 2: Hayes & Sons fuel surcharge dispute.
        audit_ref = generate_audit_ref(
            "P-D342",
            now=datetime(2026, 4, 20, tzinfo=timezone.utc),
            seq=1,
        )
        packet = CreditPacket(
            invoice_no="INV-2026-04318",
            customer_id="C-04451",
            credit_amt=Decimal("170.00"),  # 50% of disputed £340
            reason_code=ReasonCode.GOODWILL,
            audit_ref=audit_ref,
            processing_id="P-D342",
            dispute_id="D-2026-00342",
        )

        # Sandra's manual override would have skipped approver here.
        # BDRA cannot:
        with self.assertRaises(PacketValidationError):
            validate_for_submission(packet, approver_id="", applied_dt=date.today())

        # With AM signoff (U-0089 = Sandra's customer's AM per CUSTOMER_MASTER):
        record = validate_for_submission(
            packet, approver_id="U-0089", applied_dt=date(2026, 4, 20),
        )

        # Verify the record cannot be confused with a human-emitted credit:
        self.assertTrue(is_agent_emitted(record["AUDIT_REF"]))
        # And carries the structural fix:
        self.assertEqual(record["APPROVER_ID"], "U-0089")


if __name__ == "__main__":
    # Run with verbose output for the build report.
    unittest.main(verbosity=2)
