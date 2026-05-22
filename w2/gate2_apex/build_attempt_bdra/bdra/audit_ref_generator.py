"""
AUDIT_REF generator for agent-emitted credits.

APD §4 task 4.8: AUDIT_REF format `AUD-{YYYY}-BDRA-{processing_id}-{seq}`.
Spec note: 'BDRA-namespaced so audit can distinguish agent-emitted credits
from human-emitted (current `AUD-YYYY-NNNNN` pattern stays intact for human
credits)'.

Build-loop note: This module surfaced the highest-impact spec gap of the
build attempt — see SPEC GAP #6 below.
"""
from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock


# SPEC GAP #6 (CRITICAL): Format collision risk between human and agent
# AUDIT_REFs.
#
# Spec says human credits use `AUD-YYYY-NNNNN` (5-digit sequence).
# Spec says agent credits use `AUD-{YYYY}-BDRA-{processing_id}-{seq}`.
#
# Real APEX_CREDITS data shows existing AUDIT_REFs like:
#   - AUD-2026-00211 (human)
#   - AUD-2026-00212 (human)
#
# Total length: 14 chars.
#
# A BDRA AUDIT_REF with a CRM case ID like "C-DSP-2026-04-00342" and seq=01
# would be: AUD-2026-BDRA-C-DSP-2026-04-00342-01 = 35 chars.
#
# CRITICAL UNKNOWNS:
#   - Does Aurum's AUDIT_REF column have a length cap? (Spec is silent.)
#   - If Aurum truncates silently, the BDRA-namespacing is destroyed and
#     audit cannot distinguish agent vs human credits — defeating the
#     entire compliance feature.
#   - If Aurum rejects > N chars, the credit write fails and BDRA halts
#     on every write attempt.
#
# This must be confirmed with Aurum support BEFORE Wave 1 deploys. It's
# not in the discovery questions for Sarah (she wouldn't know); it's an
# Aurum vendor question.
#
# Build-attempt mitigation: cap output at 30 chars; truncate processing_id
# from the right with marker char if needed. Real impl needs the actual
# Aurum constraint.
#
# This is the closed-loop discovery: building surfaced an integration risk
# that the spec didn't name.

_MAX_LEN = 30  # Conservative until confirmed with Aurum vendor.


# SPEC GAP #7: processing_id source unspecified.
#
# Spec uses {processing_id} in the format but never defines where it comes
# from. Three plausible sources:
#   (a) CRM case ID (Salesforce auto-generated, e.g., 5003k00001abcXXAB)
#   (b) Internal monotonic counter assigned at intake
#   (c) Hash of (invoice_no, customer_id, dispute_id) for idempotency
#
# CLAUDE.md §"non-obvious" decision 7 mentions "BDRA-namespaced" but doesn't
# define processing_id. APD §"Single-instance Wave 1" mentions
# "processing_id assigned at 4.2" but not the format/source.
#
# This impl accepts processing_id as a string parameter (caller's responsibility);
# real impl needs a decision. Recommendation: option (b) — internal counter
# stored in CRM custom field, ensures uniqueness and brevity.
#
# Note: option (c) also enables idempotency (same dispute = same processing_id,
# duplicate retries are no-ops) per APD §"Idempotency". Worth considering.


# SPEC GAP #8: seq scope unspecified.
#
# `{seq}` in the format — is it:
#   (a) per-day global counter (resets midnight)
#   (b) per-processing_id counter (resets per case; usually = 01)
#   (c) per-invoice counter (allows multiple credits per invoice)
#
# Default chosen: (b) per-processing_id, two-digit zero-padded.
# Most common case will be seq=01 (one credit per dispute).
# seq>01 occurs only if a single dispute requires multiple corrective credits
# — this is an edge case the spec doesn't address.


_seq_counters: dict[str, int] = {}
_seq_lock = Lock()


def _next_seq(processing_id: str) -> int:
    """Per-processing_id monotonic counter. Thread-safe.

    SPEC GAP #8 implementation: per-processing_id scope.
    """
    with _seq_lock:
        _seq_counters[processing_id] = _seq_counters.get(processing_id, 0) + 1
        return _seq_counters[processing_id]


def generate_audit_ref(
    processing_id: str,
    *,
    now: datetime | None = None,
    seq: int | None = None,
) -> str:
    """Generate a BDRA-namespaced AUDIT_REF.

    Args:
        processing_id: case/dispute identifier (see SPEC GAP #7).
        now: timestamp for year extraction; defaults to UTC now.
        seq: explicit sequence number; if None, allocates next per
            processing_id (see SPEC GAP #8).

    Returns:
        AUDIT_REF string of the form `AUD-YYYY-BDRA-{processing_id}-{seq}`,
        capped at 30 chars (see SPEC GAP #6).
    """
    if not processing_id:
        raise ValueError("processing_id is required and must be non-empty")

    if now is None:
        now = datetime.now(timezone.utc)

    if seq is None:
        seq = _next_seq(processing_id)

    candidate = f"AUD-{now.year:04d}-BDRA-{processing_id}-{seq:02d}"

    if len(candidate) <= _MAX_LEN:
        return candidate

    # Truncate processing_id from the right; preserve year, BDRA marker, seq.
    # Use ~ as truncation indicator so audit can detect that truncation occurred.
    fixed_overhead = len(f"AUD-{now.year:04d}-BDRA--{seq:02d}")  # 18 chars
    avail_for_pid = _MAX_LEN - fixed_overhead
    if avail_for_pid < 4:
        # Pathological case: even the fixed parts exceed cap. Should never happen.
        raise SchemaCollisionError(
            f"AUDIT_REF format cap ({_MAX_LEN}) too tight for fixed structure"
        )
    truncated = processing_id[: avail_for_pid - 1] + "~"
    return f"AUD-{now.year:04d}-BDRA-{truncated}-{seq:02d}"


def is_agent_emitted(audit_ref: str) -> bool:
    """Check whether an AUDIT_REF was written by BDRA vs a human.

    Used by the daily compliance scan: distinguish agent credits (which
    must have all required fields) from human credits (subject to the
    structural authority gap from Sandra's £170 case).
    """
    if not audit_ref:
        return False
    parts = audit_ref.split("-")
    # Format: AUD-YYYY-BDRA-{pid}-{seq}
    return len(parts) >= 5 and parts[0] == "AUD" and parts[2] == "BDRA"


class SchemaCollisionError(Exception):
    """Raised if AUDIT_REF format cap cannot accommodate fixed structure."""
