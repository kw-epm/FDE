# Build Attempt 1 (Gate 1 Spec Slice)

This is a minimal implementation slice built from the Gate 1 FNOL specification.

Implemented:

- Core `Claim` model and key enums
- `coverage_status = DENIED` write-protection guardrail (human-only)
- SLA evaluation ordering (`BREACHED` before `AT_RISK`)
- Duplicate review outcomes (`MERGE`, `DISTINCT`, `REPLACE`)
- HALTED recovery guard (`HALTED -> POLICY_LOOKUP` only for `SOAP_FAILURE/PL-001`)
- DMS fallback contract (`raw_input_document_id` can be null on DMS failure path)

Run:

- `npm test`
- `npm run typecheck`

This is intentionally a vertical slice, not the full production implementation.
