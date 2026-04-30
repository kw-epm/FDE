import {
  CoverageStatus,
  DuplicateResolution,
  ProcessingStatus,
  SlaStatus,
  type DuplicateReviewInput,
} from "./types.js";

type ClaimInit = {
  id: string;
  receivedAt: Date;
  slaAtRiskBufferMinutes: number;
};

export class Claim {
  readonly id: string;
  readonly receivedAt: Date;
  readonly slaDeadline: Date;

  processingStatus: ProcessingStatus = ProcessingStatus.RECEIVED;
  coverageStatus: CoverageStatus | null = null;
  haltReason: string | null = null;
  rawInputDocumentId: string | null = null;
  interimAcknowledgedAt: Date | null = null;
  fullAcknowledgedAt: Date | null = null;
  slaStatus: SlaStatus = SlaStatus.ON_TRACK;
  readonly slaAtRiskBufferMinutes: number;

  constructor(init: ClaimInit) {
    this.id = init.id;
    this.receivedAt = init.receivedAt;
    this.slaDeadline = new Date(init.receivedAt.getTime() + 2 * 60 * 60 * 1000);
    this.slaAtRiskBufferMinutes = init.slaAtRiskBufferMinutes;
  }

  get acknowledgedAt(): Date | null {
    return this.interimAcknowledgedAt ?? this.fullAcknowledgedAt;
  }

  setRawInputDocumentId(documentId: string | null): void {
    this.rawInputDocumentId = documentId;
  }

  setCoverageStatus(status: CoverageStatus, byHuman: boolean): void {
    if (status === CoverageStatus.DENIED && !byHuman) {
      throw new Error("Agent MUST NOT set coverage_status = DENIED");
    }
    this.coverageStatus = status;
  }

  acknowledgeInterim(at: Date): void {
    if (this.interimAcknowledgedAt !== null) return;
    this.interimAcknowledgedAt = at;
    this.processingStatus = ProcessingStatus.ACKNOWLEDGED;
  }

  acknowledgeFull(at: Date): void {
    this.fullAcknowledgedAt = at;
    this.processingStatus = ProcessingStatus.ACKNOWLEDGED;
  }

  halt(reason: string): void {
    this.processingStatus = ProcessingStatus.HALTED;
    this.haltReason = reason;
  }

  resumeFromSoapFailure(): void {
    if (!this.haltReason?.includes("SOAP_FAILURE/PL-001")) {
      throw new Error("HALTED -> POLICY_LOOKUP allowed only for PL-001 SOAP failure");
    }
    this.processingStatus = ProcessingStatus.POLICY_LOOKUP;
  }

  evaluateSla(now: Date): SlaStatus {
    if (this.acknowledgedAt) {
      return this.slaStatus;
    }
    if (now > this.slaDeadline) {
      this.slaStatus = SlaStatus.BREACHED;
      return this.slaStatus;
    }

    const remainingMs = this.slaDeadline.getTime() - now.getTime();
    if (remainingMs <= this.slaAtRiskBufferMinutes * 60 * 1000) {
      this.slaStatus = SlaStatus.AT_RISK;
      return this.slaStatus;
    }

    this.slaStatus = SlaStatus.ON_TRACK;
    return this.slaStatus;
  }

  applyDuplicateReview(input: DuplicateReviewInput): ProcessingStatus {
    switch (input.resolution) {
      case DuplicateResolution.MERGE: {
        this.halt(`DUPLICATE: merged into ${input.duplicateCandidateId}`);
        return this.processingStatus;
      }
      case DuplicateResolution.DISTINCT:
      case DuplicateResolution.REPLACE: {
        this.processingStatus = ProcessingStatus.POLICY_LOOKUP;
        return this.processingStatus;
      }
      default:
        return this.processingStatus;
    }
  }
}
