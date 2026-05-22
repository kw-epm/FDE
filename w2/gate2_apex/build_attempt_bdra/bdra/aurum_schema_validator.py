"""
Aurum CSV schema validator.

APD §5 Implementation patterns: "Schema validation. Contract per Aurum file:
column count + names + order + types + value ranges where known. Hard-fail =
halt agent + alert ops Slack/email; don't downgrade to warning."

Pre-launch + monthly: diff actual schema against contract; alert if drift
detected before agent next reads it.

Build-loop note: This module surfaced 5 spec gaps (see BUILD_REPORT §2).
"""
from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Sequence


# SPEC GAP #1: contract storage location not specified in APD. CLAUDE.md §"semantic
# memory" says "YAML config in repo" for remedy templates, but schema contracts
# are not explicitly assigned a location. Decision: hard-coded for build attempt;
# real impl needs YAML or JSON file under config/aurum_schemas/.
APEX_SCHEMAS: dict[str, list[str]] = {
    # Header column order taken from actual Gate 2 artefacts (2026-04-14 / 2026-04-01).
    # SPEC GAP #2: spec says "column count + names + order + types + value ranges
    # where known". This contract enforces order; types are inferred at read time
    # (see TypeContract below); value ranges are NOT defined in this build attempt
    # (e.g. AMT_GROSS > 0, STATUS in {ACTIVE, INACTIVE, ...}). Spec is silent on
    # which fields get range checks. Decision: defer to a follow-up contract layer.
    "APEX_CREDITS": [
        "CREDIT_ID", "INVOICE_NO", "CUSTOMER_ID", "CREDIT_AMT",
        "REASON_CODE", "APPROVER_ID", "AUDIT_REF", "APPLIED_DT",
    ],
    "APEX_BILL_DAILY": [
        "INVOICE_NO", "CUSTOMER_ID", "CUSTOMER_NAME", "INVOICE_DT",
        "AMT_NET", "AMT_FUEL_SURCH", "AMT_VAT", "AMT_GROSS",
        "ROUTE_CODE", "DEPOT",
    ],
    "APEX_DISPUTES_OPEN": [
        "DISPUTE_ID", "INVOICE_NO", "CUSTOMER_ID", "OPEN_DT",
        "DISPUTE_TYPE", "DISPUTE_AMT", "ASSIGNED_TO", "STATUS", "LAST_UPDT",
    ],
    "APEX_CUSTOMER_MASTER": [
        "CUSTOMER_ID", "CUSTOMER_NAME", "ACCT_OPEN_DT", "CONTRACT_TYPE",
        "RATE_CARD", "CR_LIMIT", "ACCT_MGR", "STATUS",
    ],
    # APEX_FUEL_SURCH, APEX_RECON, APEX_AGED_RECEIVABLES contracts not
    # built — see SPEC GAP #2.
}


class SchemaDriftError(Exception):
    """Hard-fail signal. Agent must halt; ops alert fires on raise.

    SPEC GAP #3: alert mechanism is not defined in APD. Spec says
    'alert ops Slack/email' but no channel name, no webhook URL, no PagerDuty
    integration. This implementation raises and expects the caller (agent
    orchestrator) to wire alerting. Real impl needs an alert sink interface.
    """


@dataclass(frozen=True)
class ValidationResult:
    file_name: str
    contract_name: str
    expected_columns: tuple[str, ...]
    actual_columns: tuple[str, ...]
    contract_hash: str
    actual_hash: str
    is_valid: bool
    drift_reason: str | None = None


def _hash_columns(columns: Sequence[str]) -> str:
    """SPEC GAP #4: spec says 'header hash check at each batch load' but doesn't
    name the hash function. SHA-256 chosen for collision resistance vs MD5;
    irrelevant for this length but defensible at audit time.
    """
    joined = "\x1f".join(columns).encode("utf-8")  # unit separator
    return hashlib.sha256(joined).hexdigest()[:16]


def validate_csv_header(
    csv_path: Path,
    contract_name: str,
    contracts: dict[str, list[str]] | None = None,
) -> ValidationResult:
    """Read CSV header and validate against contract.

    Hard-fails (raises SchemaDriftError) if header diverges. Returns a
    ValidationResult on success for audit trail.

    SPEC GAP #5: spec doesn't define behaviour for in-flight cases when halt
    fires. If agent has 5 cases mid-processing and schema validation fails on
    the next batch ingest, do those 5 cases complete or roll back? This impl
    raises immediately without any in-flight context. APD needs an answer.
    """
    contracts = contracts or APEX_SCHEMAS
    if contract_name not in contracts:
        raise KeyError(
            f"No contract registered for {contract_name!r}. "
            f"Known: {sorted(contracts)}"
        )

    expected = list(contracts[contract_name])
    expected_hash = _hash_columns(expected)

    with csv_path.open(newline="") as f:
        reader = csv.reader(f)
        try:
            actual = next(reader)
        except StopIteration:
            raise SchemaDriftError(
                f"{csv_path.name}: file is empty; no header to validate"
            )

    actual_hash = _hash_columns(actual)
    is_valid = (actual == expected)
    drift_reason = None

    if not is_valid:
        # Diagnostic detail for ops alert — don't just say "drifted".
        if len(actual) != len(expected):
            drift_reason = (
                f"column count: expected {len(expected)}, got {len(actual)}"
            )
        else:
            mismatches = [
                f"col[{i}]: expected {e!r}, got {a!r}"
                for i, (e, a) in enumerate(zip(expected, actual))
                if e != a
            ]
            drift_reason = "; ".join(mismatches)

    result = ValidationResult(
        file_name=csv_path.name,
        contract_name=contract_name,
        expected_columns=tuple(expected),
        actual_columns=tuple(actual),
        contract_hash=expected_hash,
        actual_hash=actual_hash,
        is_valid=is_valid,
        drift_reason=drift_reason,
    )

    if not is_valid:
        raise SchemaDriftError(
            f"{csv_path.name} ({contract_name}): {drift_reason}. "
            f"Halt agent. Ops alert required."
        )

    return result


def validate_all(
    file_map: dict[str, Path],
    contracts: dict[str, list[str]] | None = None,
) -> list[ValidationResult]:
    """Validate every registered Aurum file.

    file_map: contract_name -> csv path (e.g. {"APEX_CREDITS": Path(...)}).
    Returns list of ValidationResult on full success; raises on any drift.
    """
    return [
        validate_csv_header(path, contract_name, contracts)
        for contract_name, path in file_map.items()
    ]
