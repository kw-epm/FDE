import { VisitState, TaskType, TaskStatus, AuditEventType, Owner } from '../types/enums';
import { PatientInfo } from '../types/interfaces';
import { Task } from './Task';
import { AuditEvent } from './AuditEvent';

export class Visit {
  public id: string;
  public patientInfo: PatientInfo;
  public state: VisitState;
  public tasks: Map<TaskType, Task>;
  public auditEvents: AuditEvent[];
  public createdAt: Date;
  public updatedAt: Date;
  public reviewedAt?: Date;
  public reviewedBy?: string;
  public owner: Owner;
  public nextAction: string;

  constructor(id: string, patientInfo: PatientInfo) {
    this.id = id;
    this.patientInfo = patientInfo;
    this.state = VisitState.NOT_STARTED;
    this.tasks = new Map();
    this.auditEvents = [];
    this.createdAt = new Date();
    this.updatedAt = new Date();
    this.owner = Owner.SYSTEM;
    this.nextAction = 'Visit will begin automated intake processing';
  }

  logAuditEvent(type: AuditEventType, details: Record<string, any> = {}): AuditEvent {
    const event = new AuditEvent(type, this.id, 'visit', details);
    this.auditEvents.push(event);
    return event;
  }

  addTask(task: Task): void {
    this.tasks.set(task.type, task);
    this.updateState();
  }

  getTask(type: TaskType): Task | undefined {
    return this.tasks.get(type);
  }

  getAllTasks(): Task[] {
    return Array.from(this.tasks.values());
  }

  updateState(): void {
    const previousState = this.state;
    const tasks = this.getAllTasks();

    if (tasks.length === 0) {
      this.state = VisitState.NOT_STARTED;
      this.owner = Owner.SYSTEM;
      this.nextAction = 'Visit will begin automated intake processing';
      this.updatedAt = new Date();
      return;
    }

    const hasEscalated = tasks.some(t => t.status === TaskStatus.ESCALATED);
    const hasBlocked = tasks.some(t => t.status === TaskStatus.BLOCKED);
    const hasPending = tasks.some(t => t.status === TaskStatus.PENDING);
    const allCompleted = tasks.every(t => t.status === TaskStatus.COMPLETED);

    // Determine new state based on task statuses
    // ESCALATED: Any task requires human intervention (escalated or blocked)
    // READY_FOR_REVIEW: No pending tasks, not all completed (some escalated/blocked, but workflow done)
    // CLEARED: Only reachable via explicit human review after READY_FOR_REVIEW
    // IN_PROGRESS: Some tasks still pending

    if (hasEscalated || hasBlocked) {
      this.state = VisitState.ESCALATED;

      // Determine primary owner based on escalated/blocked tasks
      const escalatedTasks = tasks.filter(t => t.status === TaskStatus.ESCALATED || t.status === TaskStatus.BLOCKED);
      const hasNurseEscalation = escalatedTasks.some(t => t.owner === Owner.NURSE);
      const hasFrontDeskEscalation = escalatedTasks.some(t => t.owner === Owner.FRONT_DESK);

      if (hasNurseEscalation && hasFrontDeskEscalation) {
        this.owner = Owner.MANAGER; // Multiple escalation types require manager coordination
        this.nextAction = 'Manager review required: visit has both administrative and clinical escalations';
      } else if (hasNurseEscalation) {
        this.owner = Owner.NURSE;
        this.nextAction = 'Nurse review required: resolve escalated clinical tasks';
      } else {
        this.owner = Owner.FRONT_DESK;
        this.nextAction = 'Front desk review required: resolve escalated administrative tasks or blocked items';
      }
    } else if (hasPending) {
      this.state = VisitState.IN_PROGRESS;
      this.owner = Owner.SYSTEM;
      this.nextAction = 'Automated processing in progress';
    } else if (allCompleted && previousState !== VisitState.CLEARED) {
      // All tasks completed - move to READY_FOR_REVIEW
      // CLEARED state can only be reached via completeReview()
      this.state = VisitState.READY_FOR_REVIEW;
      this.owner = Owner.FRONT_DESK;
      this.nextAction = 'Ready for human review and approval';
    }

    this.updatedAt = new Date();

    // Log state change if it occurred
    if (previousState !== this.state) {
      this.logAuditEvent(AuditEventType.VISIT_STATE_CHANGED, {
        previousState,
        newState: this.state
      });
    }
  }

  completeReview(reviewerName: string): void {
    if (this.state !== VisitState.READY_FOR_REVIEW && this.state !== VisitState.ESCALATED) {
      throw new Error(`Cannot complete review for visit ${this.id} in state ${this.state}`);
    }

    const previousState = this.state;
    this.state = VisitState.CLEARED;
    this.reviewedAt = new Date();
    this.reviewedBy = reviewerName;
    this.updatedAt = new Date();
    this.owner = Owner.SYSTEM;
    this.nextAction = 'Visit cleared and ready for appointment';

    this.logAuditEvent(AuditEventType.REVIEW_COMPLETED, {
      reviewedBy: reviewerName,
      previousState: previousState
    });
  }

  toJSON() {
    return {
      id: this.id,
      patientInfo: this.patientInfo,
      state: this.state,
      owner: this.owner,
      nextAction: this.nextAction,
      tasks: Array.from(this.tasks.values()).map(t => t.toJSON()),
      auditEvents: this.auditEvents.map(e => e.toJSON()),
      createdAt: this.createdAt,
      updatedAt: this.updatedAt,
      reviewedAt: this.reviewedAt,
      reviewedBy: this.reviewedBy
    };
  }
}
