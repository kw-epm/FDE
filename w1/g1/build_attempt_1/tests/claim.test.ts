import { describe, expect, test } from "vitest";
import { Claim } from "../src/claim.js";
import {
  CoverageStatus,
  DuplicateResolution,
  ProcessingStatus,
  SlaStatus,
} from "../src/types.js";

function makeClaim(): Claim {
  return new Claim({
    id: "claim-1",
    receivedAt: new Date("2026-04-27T08:00:00.000Z"),
    slaAtRiskBufferMinutes: 30,
  });
}

describe("Claim coverage guardrail", () => {
  test("prevents agent from setting DENIED", () => {
    const claim = makeClaim();
    expect(() => claim.setCoverageStatus(CoverageStatus.DENIED, false)).toThrow(
      /MUST NOT set coverage_status = DENIED/,
    );
  });

  test("allows human to set DENIED", () => {
    const claim = makeClaim();
    claim.setCoverageStatus(CoverageStatus.DENIED, true);
    expect(claim.coverageStatus).toBe(CoverageStatus.DENIED);
  });
});

describe("SLA evaluation order", () => {
  test("marks BREACHED before AT_RISK when deadline has passed", () => {
    const claim = makeClaim();
    const status = claim.evaluateSla(new Date("2026-04-27T10:00:01.000Z"));
    expect(status).toBe(SlaStatus.BREACHED);
  });

  test("freezes status after acknowledgment", () => {
    const claim = makeClaim();
    claim.acknowledgeInterim(new Date("2026-04-27T08:15:00.000Z"));
    claim.slaStatus = SlaStatus.ON_TRACK;
    const status = claim.evaluateSla(new Date("2026-04-27T11:59:00.000Z"));
    expect(status).toBe(SlaStatus.ON_TRACK);
  });
});

describe("Duplicate review outcomes", () => {
  test("MERGE halts claim with reason", () => {
    const claim = makeClaim();
    const status = claim.applyDuplicateReview({
      duplicateCandidateId: "claim-0",
      resolution: DuplicateResolution.MERGE,
    });
    expect(status).toBe(ProcessingStatus.HALTED);
    expect(claim.haltReason).toContain("claim-0");
  });

  test.each([DuplicateResolution.DISTINCT, DuplicateResolution.REPLACE])(
    "%s resumes to POLICY_LOOKUP",
    (resolution) => {
      const claim = makeClaim();
      claim.processingStatus = ProcessingStatus.AWAITING_DUPLICATE_REVIEW;
      const status = claim.applyDuplicateReview({
        duplicateCandidateId: "claim-0",
        resolution,
      });
      expect(status).toBe(ProcessingStatus.POLICY_LOOKUP);
    },
  );
});

describe("HALTED recovery rule", () => {
  test("allows recovery only from PL-001 SOAP failure", () => {
    const claim = makeClaim();
    claim.halt("SOAP_FAILURE/PL-001: policy admin timeout");
    claim.resumeFromSoapFailure();
    expect(claim.processingStatus).toBe(ProcessingStatus.POLICY_LOOKUP);
  });

  test("rejects recovery for other halt reasons", () => {
    const claim = makeClaim();
    claim.halt("DUPLICATE: merged into claim-0");
    expect(() => claim.resumeFromSoapFailure()).toThrow(/allowed only/);
  });
});

describe("DMS fallback handling", () => {
  test("allows null rawInputDocumentId on DMS failure path", () => {
    const claim = makeClaim();
    claim.setRawInputDocumentId(null);
    expect(claim.rawInputDocumentId).toBeNull();
  });
});
