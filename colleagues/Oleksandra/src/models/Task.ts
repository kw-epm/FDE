import { TaskType, TaskStatus, EscalationTarget, Owner } from '../types/enums';
import { DecisionExplanation } from '../types/interfaces';

export class Task {
  public id: string;
  public type: TaskType;
  public status: TaskStatus;
  public escalationTarget?: EscalationTarget;
  public escalationReason?: string;
  public completedAt?: Date;
  public escalatedAt?: Date;
  public blockedAt?: Date;
  public metadata: Record<string, any>;
  public decisionExplanation?: DecisionExplanation;
  public owner: Owner;
  public nextAction?: string;

  constructor(id: string, type: TaskType) {
    this.id = id;
    this.type = type;
    this.status = TaskStatus.PENDING;
    this.metadata = {};
    this.owner = Owner.SYSTEM;
    this.nextAction = 'Awaiting automated processing';
  }

  complete(explanation?: DecisionExplanation): void {
    if (this.status === TaskStatus.COMPLETED) {
      throw new Error(`Task ${this.id} is already completed`);
    }
    this.status = TaskStatus.COMPLETED;
    this.completedAt = new Date();
    this.decisionExplanation = explanation;
    this.owner = Owner.SYSTEM;
    this.nextAction = undefined;
  }

  escalate(target: EscalationTarget, reason: string, explanation?: DecisionExplanation): void {
    if (this.status === TaskStatus.COMPLETED) {
      throw new Error(`Cannot escalate completed task ${this.id}`);
    }
    this.status = TaskStatus.ESCALATED;
    this.escalationTarget = target;
    this.escalationReason = reason;
    this.escalatedAt = new Date();
    this.decisionExplanation = explanation;
    this.owner = target === EscalationTarget.FRONT_DESK ? Owner.FRONT_DESK : Owner.NURSE;
    this.nextAction = explanation?.nextAction || 'Review and resolve escalated task';
  }

  block(reason: string, explanation?: DecisionExplanation): void {
    if (this.status === TaskStatus.COMPLETED) {
      throw new Error(`Cannot block completed task ${this.id}`);
    }
    this.status = TaskStatus.BLOCKED;
    this.blockedAt = new Date();
    this.metadata.blockReason = reason;
    this.decisionExplanation = explanation;
    this.owner = Owner.FRONT_DESK; // Default blocked tasks to front desk for resolution
    this.nextAction = explanation?.nextAction || 'Resolve blocked task';
  }

  toJSON() {
    return {
      id: this.id,
      type: this.type,
      status: this.status,
      owner: this.owner,
      nextAction: this.nextAction,
      escalationTarget: this.escalationTarget,
      escalationReason: this.escalationReason,
      completedAt: this.completedAt,
      escalatedAt: this.escalatedAt,
      blockedAt: this.blockedAt,
      decisionExplanation: this.decisionExplanation,
      metadata: this.metadata
    };
  }
}
