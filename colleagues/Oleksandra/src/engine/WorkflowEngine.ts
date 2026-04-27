import { Visit } from '../models/Visit';
import { Task } from '../models/Task';
import { TaskType, EscalationTarget, AuditEventType, DecisionType, Owner } from '../types/enums';
import { PatientInfo, TaskInput, DecisionExplanation } from '../types/interfaces';

export class WorkflowEngine {
  private visits: Map<string, Visit>;
  private taskCounter: number;

  constructor() {
    this.visits = new Map();
    this.taskCounter = 0;
  }

  createVisit(patientInfo: PatientInfo): Visit {
    const visitId = `visit-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const visit = new Visit(visitId, patientInfo);

    const requiredTaskTypes = [
      TaskType.INSURANCE_VERIFICATION,
      TaskType.PRIOR_AUTH_CHECK,
      TaskType.QUESTIONNAIRE,
      TaskType.VISIT_REASON,
      TaskType.MEDICATION_REVIEW,
      TaskType.ALLERGY_REVIEW
    ];

    for (const taskType of requiredTaskTypes) {
      const taskId = `task-${++this.taskCounter}`;
      const task = new Task(taskId, taskType);
      visit.addTask(task);

      // Log task creation
      visit.logAuditEvent(AuditEventType.TASK_CREATED, {
        taskId: task.id,
        taskType: task.type
      });
    }

    this.visits.set(visitId, visit);
    return visit;
  }

  getVisit(visitId: string): Visit | undefined {
    return this.visits.get(visitId);
  }

  processTask(visitId: string, taskType: TaskType, input: TaskInput): void {
    const visit = this.visits.get(visitId);
    if (!visit) {
      throw new Error(`Visit ${visitId} not found`);
    }

    const task = visit.getTask(taskType);
    if (!task) {
      throw new Error(`Task ${taskType} not found for visit ${visitId}`);
    }

    switch (taskType) {
      case TaskType.INSURANCE_VERIFICATION:
        this.processInsuranceVerification(task, input, visit);
        break;
      case TaskType.PRIOR_AUTH_CHECK:
        this.processPriorAuthCheck(task, input, visit);
        break;
      case TaskType.QUESTIONNAIRE:
        this.processQuestionnaire(task, input, visit);
        break;
      case TaskType.VISIT_REASON:
        this.processVisitReason(task, input, visit);
        break;
      case TaskType.MEDICATION_REVIEW:
        this.processMedicationReview(task, input, visit);
        break;
      case TaskType.ALLERGY_REVIEW:
        this.processAllergyReview(task, input, visit);
        break;
      default:
        throw new Error(`Unknown task type: ${taskType}`);
    }

    visit.updateState();
  }

  completeReview(visitId: string, reviewerName: string): void {
    const visit = this.visits.get(visitId);
    if (!visit) {
      throw new Error(`Visit ${visitId} not found`);
    }

    visit.completeReview(reviewerName);
  }

  private processInsuranceVerification(task: Task, input: TaskInput, visit: Visit): void {
    // Missing external data: block task instead of escalating
    if (!input.insurance) {
      const explanation: DecisionExplanation = {
        decision: DecisionType.BLOCKED,
        reasonCode: 'INS_DATA_UNAVAILABLE',
        reasonText: 'Insurance verification data unavailable from external system',
        ruleApplied: 'RULE: If insurance data is missing → BLOCK task (external system issue)',
        confidence: 'deterministic',
        nextAction: 'Retry insurance verification system or manually verify coverage',
        owner: Owner.FRONT_DESK,
        missingData: ['insurance verification status', 'policy details']
      };

      task.block('Insurance verification data unavailable from external system', explanation);
      visit.logAuditEvent(AuditEventType.TASK_BLOCKED, {
        taskId: task.id,
        taskType: task.type,
        reason: 'Insurance verification data unavailable',
        explanation
      });
      return;
    }

    const { verified, active } = input.insurance;

    if (!verified) {
      const explanation: DecisionExplanation = {
        decision: DecisionType.ESCALATED,
        reasonCode: 'INS_NOT_VERIFIED',
        reasonText: 'Insurance verification failed or returned unknown status',
        ruleApplied: 'RULE: If insurance.verified = false → ESCALATE to front_desk',
        confidence: 'deterministic',
        nextAction: 'Contact insurance provider to verify coverage and resolve verification failure',
        owner: Owner.FRONT_DESK
      };

      task.escalate(
        EscalationTarget.FRONT_DESK,
        'Insurance verification failed or unknown',
        explanation
      );
      visit.logAuditEvent(AuditEventType.TASK_ESCALATED, {
        taskId: task.id,
        taskType: task.type,
        escalationTarget: EscalationTarget.FRONT_DESK,
        reason: 'Insurance verification failed',
        explanation
      });
      return;
    }

    if (!active) {
      const explanation: DecisionExplanation = {
        decision: DecisionType.ESCALATED,
        reasonCode: 'INS_NOT_ACTIVE',
        reasonText: 'Insurance policy is not currently active',
        ruleApplied: 'RULE: If insurance.active = false → ESCALATE to front_desk',
        confidence: 'deterministic',
        nextAction: 'Contact patient to update insurance information or arrange alternative payment',
        owner: Owner.FRONT_DESK
      };

      task.escalate(
        EscalationTarget.FRONT_DESK,
        'Insurance policy is not active',
        explanation
      );
      visit.logAuditEvent(AuditEventType.TASK_ESCALATED, {
        taskId: task.id,
        taskType: task.type,
        escalationTarget: EscalationTarget.FRONT_DESK,
        reason: 'Insurance not active',
        explanation
      });
      return;
    }

    // Insurance verified and active - complete task
    const explanation: DecisionExplanation = {
      decision: DecisionType.COMPLETED,
      reasonCode: 'INS_VERIFIED',
      reasonText: 'Insurance successfully verified and policy is active',
      ruleApplied: 'RULE: If insurance.verified = true AND insurance.active = true → COMPLETE',
      confidence: 'deterministic',
      nextAction: 'Task completed, no further action needed'
    };

    task.metadata.insurance = input.insurance;
    task.complete(explanation);
    visit.logAuditEvent(AuditEventType.TASK_COMPLETED, {
      taskId: task.id,
      taskType: task.type,
      explanation
    });
  }

  private processPriorAuthCheck(task: Task, input: TaskInput, visit: Visit): void {
    // Missing external data: block task
    if (!input.priorAuth) {
      const explanation: DecisionExplanation = {
        decision: DecisionType.BLOCKED,
        reasonCode: 'PA_DATA_UNAVAILABLE',
        reasonText: 'Prior authorization data unavailable from external system',
        ruleApplied: 'RULE: If prior auth data is missing → BLOCK task (external system issue)',
        confidence: 'deterministic',
        nextAction: 'Retry prior authorization system check or manually verify authorization status',
        owner: Owner.FRONT_DESK,
        missingData: ['prior authorization requirement status', 'approval status', 'expiration date']
      };

      task.block('Prior authorization data unavailable from external system', explanation);
      visit.logAuditEvent(AuditEventType.TASK_BLOCKED, {
        taskId: task.id,
        taskType: task.type,
        reason: 'Prior auth data unavailable',
        explanation
      });
      return;
    }

    const { required, approved, expirationDate } = input.priorAuth;

    if (required && !approved) {
      const explanation: DecisionExplanation = {
        decision: DecisionType.ESCALATED,
        reasonCode: 'PA_NOT_APPROVED',
        reasonText: 'Prior authorization is required but has not been approved',
        ruleApplied: 'RULE: If priorAuth.required = true AND priorAuth.approved = false → ESCALATE to front_desk',
        confidence: 'deterministic',
        nextAction: 'Submit prior authorization request to insurance or contact provider to obtain approval',
        owner: Owner.FRONT_DESK
      };

      task.escalate(
        EscalationTarget.FRONT_DESK,
        'Prior authorization required but not approved',
        explanation
      );
      visit.logAuditEvent(AuditEventType.TASK_ESCALATED, {
        taskId: task.id,
        taskType: task.type,
        escalationTarget: EscalationTarget.FRONT_DESK,
        reason: 'Prior auth not approved',
        explanation
      });
      return;
    }

    if (required && approved && expirationDate) {
      const now = new Date();
      if (expirationDate < now) {
        const explanation: DecisionExplanation = {
          decision: DecisionType.ESCALATED,
          reasonCode: 'PA_EXPIRED',
          reasonText: `Prior authorization expired on ${expirationDate.toLocaleDateString()}`,
          ruleApplied: 'RULE: If priorAuth.required = true AND priorAuth.expirationDate < now → ESCALATE to front_desk',
          confidence: 'deterministic',
          nextAction: 'Request renewal of prior authorization from insurance provider',
          owner: Owner.FRONT_DESK
        };

        task.escalate(
          EscalationTarget.FRONT_DESK,
          'Prior authorization has expired',
          explanation
        );
        visit.logAuditEvent(AuditEventType.TASK_ESCALATED, {
          taskId: task.id,
          taskType: task.type,
          escalationTarget: EscalationTarget.FRONT_DESK,
          reason: 'Prior auth expired',
          explanation
        });
        return;
      }
    }

    // Prior auth check passed
    const explanation: DecisionExplanation = {
      decision: DecisionType.COMPLETED,
      reasonCode: required ? 'PA_APPROVED' : 'PA_NOT_REQUIRED',
      reasonText: required ? 'Prior authorization approved and valid' : 'Prior authorization not required for this visit',
      ruleApplied: required
        ? 'RULE: If priorAuth.required = true AND priorAuth.approved = true AND not expired → COMPLETE'
        : 'RULE: If priorAuth.required = false → COMPLETE',
      confidence: 'deterministic',
      nextAction: 'Task completed, no further action needed'
    };

    task.metadata.priorAuth = input.priorAuth;
    task.complete(explanation);
    visit.logAuditEvent(AuditEventType.TASK_COMPLETED, {
      taskId: task.id,
      taskType: task.type,
      explanation
    });
  }

  private processQuestionnaire(task: Task, input: TaskInput, visit: Visit): void {
    if (!input.questionnaire) {
      const explanation: DecisionExplanation = {
        decision: DecisionType.ESCALATED,
        reasonCode: 'QUEST_MISSING',
        reasonText: 'Questionnaire data not provided by patient',
        ruleApplied: 'RULE: If questionnaire data is missing → ESCALATE to front_desk',
        confidence: 'deterministic',
        nextAction: 'Contact patient to complete pre-visit questionnaire',
        owner: Owner.FRONT_DESK,
        missingData: ['questionnaire responses']
      };

      task.escalate(
        EscalationTarget.FRONT_DESK,
        'Questionnaire data missing',
        explanation
      );
      visit.logAuditEvent(AuditEventType.TASK_ESCALATED, {
        taskId: task.id,
        taskType: task.type,
        escalationTarget: EscalationTarget.FRONT_DESK,
        reason: 'Questionnaire data missing',
        explanation
      });
      return;
    }

    if (!input.questionnaire.completed) {
      const explanation: DecisionExplanation = {
        decision: DecisionType.ESCALATED,
        reasonCode: 'QUEST_INCOMPLETE',
        reasonText: 'Pre-visit questionnaire is incomplete',
        ruleApplied: 'RULE: If questionnaire.completed = false → ESCALATE to front_desk',
        confidence: 'deterministic',
        nextAction: 'Contact patient to complete remaining questionnaire items',
        owner: Owner.FRONT_DESK
      };

      task.escalate(
        EscalationTarget.FRONT_DESK,
        'Questionnaire is incomplete',
        explanation
      );
      visit.logAuditEvent(AuditEventType.TASK_ESCALATED, {
        taskId: task.id,
        taskType: task.type,
        escalationTarget: EscalationTarget.FRONT_DESK,
        reason: 'Questionnaire incomplete',
        explanation
      });
      return;
    }

    // Questionnaire completed
    const explanation: DecisionExplanation = {
      decision: DecisionType.COMPLETED,
      reasonCode: 'QUEST_COMPLETE',
      reasonText: 'Pre-visit questionnaire completed by patient',
      ruleApplied: 'RULE: If questionnaire.completed = true → COMPLETE',
      confidence: 'deterministic',
      nextAction: 'Task completed, no further action needed'
    };

    task.metadata.questionnaire = input.questionnaire;
    task.complete(explanation);
    visit.logAuditEvent(AuditEventType.TASK_COMPLETED, {
      taskId: task.id,
      taskType: task.type,
      explanation
    });
  }

  private processVisitReason(task: Task, input: TaskInput, visit: Visit): void {
    if (!input.visitReason) {
      const explanation: DecisionExplanation = {
        decision: DecisionType.ESCALATED,
        reasonCode: 'VR_MISSING',
        reasonText: 'Visit reason not provided',
        ruleApplied: 'RULE: If visitReason is missing → ESCALATE to nurse',
        confidence: 'deterministic',
        nextAction: 'Contact patient to obtain visit reason and assess appropriateness',
        owner: Owner.NURSE,
        missingData: ['visit reason']
      };

      task.escalate(
        EscalationTarget.NURSE,
        'Visit reason missing',
        explanation
      );
      visit.logAuditEvent(AuditEventType.TASK_ESCALATED, {
        taskId: task.id,
        taskType: task.type,
        escalationTarget: EscalationTarget.NURSE,
        reason: 'Visit reason missing',
        explanation
      });
      return;
    }

    const { reason } = input.visitReason;

    if (!reason || reason.trim().length === 0) {
      const explanation: DecisionExplanation = {
        decision: DecisionType.ESCALATED,
        reasonCode: 'VR_EMPTY',
        reasonText: 'Visit reason field is empty',
        ruleApplied: 'RULE: If visitReason.reason is empty → ESCALATE to nurse',
        confidence: 'deterministic',
        nextAction: 'Contact patient to obtain visit reason',
        owner: Owner.NURSE
      };

      task.escalate(
        EscalationTarget.NURSE,
        'Visit reason is empty',
        explanation
      );
      visit.logAuditEvent(AuditEventType.TASK_ESCALATED, {
        taskId: task.id,
        taskType: task.type,
        escalationTarget: EscalationTarget.NURSE,
        reason: 'Visit reason empty',
        explanation
      });
      return;
    }

    // ROUTING TRIGGER CHECK (NOT CLINICAL INTERPRETATION):
    // This check uses conservative keyword matching to identify visit reasons
    // that should be routed to nursing staff for administrative review.
    const triggerMatch = this.detectRoutingTrigger(reason);
    if (triggerMatch) {
      const explanation: DecisionExplanation = {
        decision: DecisionType.ESCALATED,
        reasonCode: 'VR_ROUTING_TRIGGER',
        reasonText: `Visit reason contains routing trigger phrase: "${triggerMatch}"`,
        ruleApplied: 'RULE: If visitReason contains routing trigger keywords → ESCALATE to nurse for administrative review (NOT clinical diagnosis)',
        confidence: 'deterministic',
        nextAction: 'Nurse review to assess scheduling priority and ensure appropriate appointment type',
        owner: Owner.NURSE
      };

      task.escalate(
        EscalationTarget.NURSE,
        'Visit reason contains routing trigger phrase - requires nurse review',
        explanation
      );
      visit.logAuditEvent(AuditEventType.TASK_ESCALATED, {
        taskId: task.id,
        taskType: task.type,
        escalationTarget: EscalationTarget.NURSE,
        reason: 'Routing trigger detected in visit reason',
        explanation
      });
      return;
    }

    // Visit reason provided and no routing triggers
    const explanation: DecisionExplanation = {
      decision: DecisionType.COMPLETED,
      reasonCode: 'VR_ROUTINE',
      reasonText: 'Visit reason provided and appears routine',
      ruleApplied: 'RULE: If visitReason provided AND no routing triggers detected → COMPLETE',
      confidence: 'deterministic',
      nextAction: 'Task completed, no further action needed'
    };

    task.metadata.visitReason = input.visitReason;
    task.complete(explanation);
    visit.logAuditEvent(AuditEventType.TASK_COMPLETED, {
      taskId: task.id,
      taskType: task.type,
      explanation
    });
  }

  private processMedicationReview(task: Task, input: TaskInput, visit: Visit): void {
    if (!input.medication) {
      const explanation: DecisionExplanation = {
        decision: DecisionType.ESCALATED,
        reasonCode: 'MED_DATA_MISSING',
        reasonText: 'Medication data not provided',
        ruleApplied: 'RULE: If medication data is missing → ESCALATE to nurse',
        confidence: 'deterministic',
        nextAction: 'Obtain current medication list from patient or EHR',
        owner: Owner.NURSE,
        missingData: ['current medications', 'medication changes']
      };

      task.escalate(
        EscalationTarget.NURSE,
        'Medication data missing',
        explanation
      );
      visit.logAuditEvent(AuditEventType.TASK_ESCALATED, {
        taskId: task.id,
        taskType: task.type,
        escalationTarget: EscalationTarget.NURSE,
        reason: 'Medication data missing',
        explanation
      });
      return;
    }

    if (input.medication.changeReported) {
      const changedMeds = input.medication.changedMedications?.join(', ') || 'unspecified medications';
      const explanation: DecisionExplanation = {
        decision: DecisionType.ESCALATED,
        reasonCode: 'MED_CHANGE_REPORTED',
        reasonText: `Patient reported medication changes: ${changedMeds}`,
        ruleApplied: 'RULE: If medication.changeReported = true → ESCALATE to nurse for reconciliation',
        confidence: 'deterministic',
        nextAction: 'Nurse to perform medication reconciliation and update EHR',
        owner: Owner.NURSE
      };

      task.escalate(
        EscalationTarget.NURSE,
        'Medication change reported - requires nurse review',
        explanation
      );
      visit.logAuditEvent(AuditEventType.TASK_ESCALATED, {
        taskId: task.id,
        taskType: task.type,
        escalationTarget: EscalationTarget.NURSE,
        reason: 'Medication change reported',
        explanation
      });
      return;
    }

    // No medication changes
    const explanation: DecisionExplanation = {
      decision: DecisionType.COMPLETED,
      reasonCode: 'MED_NO_CHANGE',
      reasonText: 'No medication changes reported',
      ruleApplied: 'RULE: If medication.changeReported = false → COMPLETE',
      confidence: 'deterministic',
      nextAction: 'Task completed, no further action needed'
    };

    task.metadata.medication = input.medication;
    task.complete(explanation);
    visit.logAuditEvent(AuditEventType.TASK_COMPLETED, {
      taskId: task.id,
      taskType: task.type,
      explanation
    });
  }

  private processAllergyReview(task: Task, input: TaskInput, visit: Visit): void {
    if (!input.allergy) {
      const explanation: DecisionExplanation = {
        decision: DecisionType.ESCALATED,
        reasonCode: 'ALLERGY_DATA_MISSING',
        reasonText: 'Allergy data not provided',
        ruleApplied: 'RULE: If allergy data is missing → ESCALATE to nurse',
        confidence: 'deterministic',
        nextAction: 'Obtain current allergy list from patient or EHR',
        owner: Owner.NURSE,
        missingData: ['current allergies', 'allergy changes']
      };

      task.escalate(
        EscalationTarget.NURSE,
        'Allergy data missing',
        explanation
      );
      visit.logAuditEvent(AuditEventType.TASK_ESCALATED, {
        taskId: task.id,
        taskType: task.type,
        escalationTarget: EscalationTarget.NURSE,
        reason: 'Allergy data missing',
        explanation
      });
      return;
    }

    if (input.allergy.changeReported) {
      const changedAllergies = input.allergy.changedAllergies?.join(', ') || 'unspecified allergies';
      const explanation: DecisionExplanation = {
        decision: DecisionType.ESCALATED,
        reasonCode: 'ALLERGY_CHANGE_REPORTED',
        reasonText: `Patient reported allergy changes: ${changedAllergies}`,
        ruleApplied: 'RULE: If allergy.changeReported = true → ESCALATE to nurse for reconciliation',
        confidence: 'deterministic',
        nextAction: 'Nurse to review allergy changes and update EHR',
        owner: Owner.NURSE
      };

      task.escalate(
        EscalationTarget.NURSE,
        'Allergy change reported - requires nurse review',
        explanation
      );
      visit.logAuditEvent(AuditEventType.TASK_ESCALATED, {
        taskId: task.id,
        taskType: task.type,
        escalationTarget: EscalationTarget.NURSE,
        reason: 'Allergy change reported',
        explanation
      });
      return;
    }

    // No allergy changes
    const explanation: DecisionExplanation = {
      decision: DecisionType.COMPLETED,
      reasonCode: 'ALLERGY_NO_CHANGE',
      reasonText: 'No allergy changes reported',
      ruleApplied: 'RULE: If allergy.changeReported = false → COMPLETE',
      confidence: 'deterministic',
      nextAction: 'Task completed, no further action needed'
    };

    task.metadata.allergy = input.allergy;
    task.complete(explanation);
    visit.logAuditEvent(AuditEventType.TASK_COMPLETED, {
      taskId: task.id,
      taskType: task.type,
      explanation
    });
  }

  // ROUTING TRIGGER DETECTION (NOT CLINICAL INTERPRETATION)
  // Returns the matched trigger phrase or null if none found
  private detectRoutingTrigger(text: string): string | null {
    const routingTriggers = [
      'chest pain',
      'shortness of breath',
      'difficulty breathing',
      'severe pain',
      'bleeding',
      'heavy bleeding',
      'fainting',
      'fainted',
      'self-harm',
      'suicide',
      'suicidal',
      'urgent',
      'same day',
      'getting worse',
      'worsening',
      'emergency',
      'severe',
      'fever',
      'high fever',
      'dizzy',
      'dizziness',
      'confusion',
      'confused',
      'unresponsive'
    ];

    const lowerText = text.toLowerCase();
    for (const trigger of routingTriggers) {
      if (lowerText.includes(trigger)) {
        return trigger;
      }
    }
    return null;
  }
}
