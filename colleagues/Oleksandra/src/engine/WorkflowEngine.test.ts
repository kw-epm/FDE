import { WorkflowEngine } from './WorkflowEngine';
import { TaskType, TaskStatus, VisitState, EscalationTarget } from '../types/enums';
import { PatientInfo, TaskInput } from '../types/interfaces';

describe('WorkflowEngine', () => {
  const mockPatient: PatientInfo = {
    patientId: 'P001',
    name: 'Jane Doe',
    dateOfBirth: '1985-06-15'
  };

  describe('createVisit', () => {
    it('should create a visit with all required tasks', () => {
      const engine = new WorkflowEngine();
      const visit = engine.createVisit(mockPatient);

      expect(visit.id).toBeDefined();
      expect(visit.patientInfo).toEqual(mockPatient);
      expect(visit.tasks.size).toBe(6);
      expect(visit.getTask(TaskType.INSURANCE_VERIFICATION)).toBeDefined();
      expect(visit.getTask(TaskType.PRIOR_AUTH_CHECK)).toBeDefined();
      expect(visit.getTask(TaskType.QUESTIONNAIRE)).toBeDefined();
      expect(visit.getTask(TaskType.VISIT_REASON)).toBeDefined();
      expect(visit.getTask(TaskType.MEDICATION_REVIEW)).toBeDefined();
      expect(visit.getTask(TaskType.ALLERGY_REVIEW)).toBeDefined();
    });
  });

  describe('insurance verification', () => {
    it('should complete task when insurance is verified and active', () => {
      const engine = new WorkflowEngine();
      const visit = engine.createVisit(mockPatient);

      const input: TaskInput = {
        insurance: { verified: true, active: true }
      };

      engine.processTask(visit.id, TaskType.INSURANCE_VERIFICATION, input);

      const task = visit.getTask(TaskType.INSURANCE_VERIFICATION);
      expect(task?.status).toBe(TaskStatus.COMPLETED);
    });

    it('should escalate when insurance verification fails', () => {
      const engine = new WorkflowEngine();
      const visit = engine.createVisit(mockPatient);

      const input: TaskInput = {
        insurance: { verified: false, active: true }
      };

      engine.processTask(visit.id, TaskType.INSURANCE_VERIFICATION, input);

      const task = visit.getTask(TaskType.INSURANCE_VERIFICATION);
      expect(task?.status).toBe(TaskStatus.ESCALATED);
      expect(task?.escalationTarget).toBe(EscalationTarget.FRONT_DESK);
      expect(task?.escalationReason).toContain('verification failed');
    });

    it('should escalate when insurance is not active', () => {
      const engine = new WorkflowEngine();
      const visit = engine.createVisit(mockPatient);

      const input: TaskInput = {
        insurance: { verified: true, active: false }
      };

      engine.processTask(visit.id, TaskType.INSURANCE_VERIFICATION, input);

      const task = visit.getTask(TaskType.INSURANCE_VERIFICATION);
      expect(task?.status).toBe(TaskStatus.ESCALATED);
      expect(task?.escalationTarget).toBe(EscalationTarget.FRONT_DESK);
    });

    it('should block when insurance data is missing', () => {
      const engine = new WorkflowEngine();
      const visit = engine.createVisit(mockPatient);

      engine.processTask(visit.id, TaskType.INSURANCE_VERIFICATION, {});

      const task = visit.getTask(TaskType.INSURANCE_VERIFICATION);
      expect(task?.status).toBe(TaskStatus.BLOCKED);
      expect(task?.metadata.blockReason).toContain('unavailable');
    });
  });

  describe('prior authorization', () => {
    it('should complete when prior auth not required', () => {
      const engine = new WorkflowEngine();
      const visit = engine.createVisit(mockPatient);

      const input: TaskInput = {
        priorAuth: { required: false }
      };

      engine.processTask(visit.id, TaskType.PRIOR_AUTH_CHECK, input);

      const task = visit.getTask(TaskType.PRIOR_AUTH_CHECK);
      expect(task?.status).toBe(TaskStatus.COMPLETED);
    });

    it('should complete when prior auth approved and not expired', () => {
      const engine = new WorkflowEngine();
      const visit = engine.createVisit(mockPatient);

      const futureDate = new Date();
      futureDate.setDate(futureDate.getDate() + 30);

      const input: TaskInput = {
        priorAuth: {
          required: true,
          approved: true,
          expirationDate: futureDate
        }
      };

      engine.processTask(visit.id, TaskType.PRIOR_AUTH_CHECK, input);

      const task = visit.getTask(TaskType.PRIOR_AUTH_CHECK);
      expect(task?.status).toBe(TaskStatus.COMPLETED);
    });

    it('should escalate when prior auth required but not approved', () => {
      const engine = new WorkflowEngine();
      const visit = engine.createVisit(mockPatient);

      const input: TaskInput = {
        priorAuth: { required: true, approved: false }
      };

      engine.processTask(visit.id, TaskType.PRIOR_AUTH_CHECK, input);

      const task = visit.getTask(TaskType.PRIOR_AUTH_CHECK);
      expect(task?.status).toBe(TaskStatus.ESCALATED);
      expect(task?.escalationTarget).toBe(EscalationTarget.FRONT_DESK);
      expect(task?.escalationReason).toContain('not approved');
    });

    it('should escalate when prior auth expired', () => {
      const engine = new WorkflowEngine();
      const visit = engine.createVisit(mockPatient);

      const pastDate = new Date();
      pastDate.setDate(pastDate.getDate() - 10);

      const input: TaskInput = {
        priorAuth: {
          required: true,
          approved: true,
          expirationDate: pastDate
        }
      };

      engine.processTask(visit.id, TaskType.PRIOR_AUTH_CHECK, input);

      const task = visit.getTask(TaskType.PRIOR_AUTH_CHECK);
      expect(task?.status).toBe(TaskStatus.ESCALATED);
      expect(task?.escalationReason).toContain('expired');
    });
  });

  describe('questionnaire', () => {
    it('should complete when questionnaire is completed', () => {
      const engine = new WorkflowEngine();
      const visit = engine.createVisit(mockPatient);

      const input: TaskInput = {
        questionnaire: { completed: true }
      };

      engine.processTask(visit.id, TaskType.QUESTIONNAIRE, input);

      const task = visit.getTask(TaskType.QUESTIONNAIRE);
      expect(task?.status).toBe(TaskStatus.COMPLETED);
    });

    it('should escalate when questionnaire is incomplete', () => {
      const engine = new WorkflowEngine();
      const visit = engine.createVisit(mockPatient);

      const input: TaskInput = {
        questionnaire: { completed: false }
      };

      engine.processTask(visit.id, TaskType.QUESTIONNAIRE, input);

      const task = visit.getTask(TaskType.QUESTIONNAIRE);
      expect(task?.status).toBe(TaskStatus.ESCALATED);
      expect(task?.escalationTarget).toBe(EscalationTarget.FRONT_DESK);
    });
  });

  describe('visit reason', () => {
    it('should complete with routine visit reason', () => {
      const engine = new WorkflowEngine();
      const visit = engine.createVisit(mockPatient);

      const input: TaskInput = {
        visitReason: {
          reason: 'Annual physical examination',
          urgency: 'routine'
        }
      };

      engine.processTask(visit.id, TaskType.VISIT_REASON, input);

      const task = visit.getTask(TaskType.VISIT_REASON);
      expect(task?.status).toBe(TaskStatus.COMPLETED);
    });

    it('should escalate when visit reason contains routing triggers', () => {
      const engine = new WorkflowEngine();
      const visit = engine.createVisit(mockPatient);

      const routingTriggers = [
        'chest pain',
        'difficulty breathing',
        'severe headache',
        'fever and chills',
        'bleeding heavily'
      ];

      for (const reason of routingTriggers) {
        const newVisit = engine.createVisit(mockPatient);
        const input: TaskInput = {
          visitReason: { reason }
        };

        engine.processTask(newVisit.id, TaskType.VISIT_REASON, input);

        const task = newVisit.getTask(TaskType.VISIT_REASON);
        expect(task?.status).toBe(TaskStatus.ESCALATED);
        expect(task?.escalationTarget).toBe(EscalationTarget.NURSE);
        expect(task?.escalationReason).toContain('routing trigger');
      }
    });

    it('should escalate when visit reason is empty', () => {
      const engine = new WorkflowEngine();
      const visit = engine.createVisit(mockPatient);

      const input: TaskInput = {
        visitReason: { reason: '' }
      };

      engine.processTask(visit.id, TaskType.VISIT_REASON, input);

      const task = visit.getTask(TaskType.VISIT_REASON);
      expect(task?.status).toBe(TaskStatus.ESCALATED);
      expect(task?.escalationTarget).toBe(EscalationTarget.NURSE);
    });
  });

  describe('medication review', () => {
    it('should complete when no medication change reported', () => {
      const engine = new WorkflowEngine();
      const visit = engine.createVisit(mockPatient);

      const input: TaskInput = {
        medication: {
          changeReported: false,
          medications: ['Aspirin 81mg']
        }
      };

      engine.processTask(visit.id, TaskType.MEDICATION_REVIEW, input);

      const task = visit.getTask(TaskType.MEDICATION_REVIEW);
      expect(task?.status).toBe(TaskStatus.COMPLETED);
    });

    it('should escalate when medication change reported', () => {
      const engine = new WorkflowEngine();
      const visit = engine.createVisit(mockPatient);

      const input: TaskInput = {
        medication: {
          changeReported: true,
          changedMedications: ['New medication']
        }
      };

      engine.processTask(visit.id, TaskType.MEDICATION_REVIEW, input);

      const task = visit.getTask(TaskType.MEDICATION_REVIEW);
      expect(task?.status).toBe(TaskStatus.ESCALATED);
      expect(task?.escalationTarget).toBe(EscalationTarget.NURSE);
    });
  });

  describe('allergy review', () => {
    it('should complete when no allergy change reported', () => {
      const engine = new WorkflowEngine();
      const visit = engine.createVisit(mockPatient);

      const input: TaskInput = {
        allergy: {
          changeReported: false,
          allergies: ['Penicillin']
        }
      };

      engine.processTask(visit.id, TaskType.ALLERGY_REVIEW, input);

      const task = visit.getTask(TaskType.ALLERGY_REVIEW);
      expect(task?.status).toBe(TaskStatus.COMPLETED);
    });

    it('should escalate when allergy change reported', () => {
      const engine = new WorkflowEngine();
      const visit = engine.createVisit(mockPatient);

      const input: TaskInput = {
        allergy: {
          changeReported: true,
          changedAllergies: ['New allergy']
        }
      };

      engine.processTask(visit.id, TaskType.ALLERGY_REVIEW, input);

      const task = visit.getTask(TaskType.ALLERGY_REVIEW);
      expect(task?.status).toBe(TaskStatus.ESCALATED);
      expect(task?.escalationTarget).toBe(EscalationTarget.NURSE);
    });
  });

  describe('visit state management', () => {
    it('should set visit to READY_FOR_REVIEW when all tasks completed', () => {
      const engine = new WorkflowEngine();
      const visit = engine.createVisit(mockPatient);

      const completeInput: TaskInput = {
        insurance: { verified: true, active: true },
        priorAuth: { required: false },
        questionnaire: { completed: true },
        visitReason: { reason: 'Annual checkup' },
        medication: { changeReported: false },
        allergy: { changeReported: false }
      };

      engine.processTask(visit.id, TaskType.INSURANCE_VERIFICATION, completeInput);
      engine.processTask(visit.id, TaskType.PRIOR_AUTH_CHECK, completeInput);
      engine.processTask(visit.id, TaskType.QUESTIONNAIRE, completeInput);
      engine.processTask(visit.id, TaskType.VISIT_REASON, completeInput);
      engine.processTask(visit.id, TaskType.MEDICATION_REVIEW, completeInput);
      engine.processTask(visit.id, TaskType.ALLERGY_REVIEW, completeInput);

      const updatedVisit = engine.getVisit(visit.id);
      expect(updatedVisit?.state).toBe(VisitState.READY_FOR_REVIEW);
    });

    it('should set visit to CLEARED after human review', () => {
      const engine = new WorkflowEngine();
      const visit = engine.createVisit(mockPatient);

      const completeInput: TaskInput = {
        insurance: { verified: true, active: true },
        priorAuth: { required: false },
        questionnaire: { completed: true },
        visitReason: { reason: 'Annual checkup' },
        medication: { changeReported: false },
        allergy: { changeReported: false }
      };

      engine.processTask(visit.id, TaskType.INSURANCE_VERIFICATION, completeInput);
      engine.processTask(visit.id, TaskType.PRIOR_AUTH_CHECK, completeInput);
      engine.processTask(visit.id, TaskType.QUESTIONNAIRE, completeInput);
      engine.processTask(visit.id, TaskType.VISIT_REASON, completeInput);
      engine.processTask(visit.id, TaskType.MEDICATION_REVIEW, completeInput);
      engine.processTask(visit.id, TaskType.ALLERGY_REVIEW, completeInput);

      let updatedVisit = engine.getVisit(visit.id);
      expect(updatedVisit?.state).toBe(VisitState.READY_FOR_REVIEW);

      engine.completeReview(visit.id, 'Test Reviewer');

      updatedVisit = engine.getVisit(visit.id);
      expect(updatedVisit?.state).toBe(VisitState.CLEARED);
      expect(updatedVisit?.reviewedBy).toBe('Test Reviewer');
    });

    it('should set visit to ESCALATED when any task escalated', () => {
      const engine = new WorkflowEngine();
      const visit = engine.createVisit(mockPatient);

      const input: TaskInput = {
        medication: { changeReported: true }
      };

      engine.processTask(visit.id, TaskType.MEDICATION_REVIEW, input);

      const updatedVisit = engine.getVisit(visit.id);
      expect(updatedVisit?.state).toBe(VisitState.ESCALATED);
    });
  });

  describe('missing external data', () => {
    it('should block insurance task when data unavailable', () => {
      const engine = new WorkflowEngine();
      const visit = engine.createVisit(mockPatient);

      // No insurance data provided
      engine.processTask(visit.id, TaskType.INSURANCE_VERIFICATION, {});

      const task = visit.getTask(TaskType.INSURANCE_VERIFICATION);
      expect(task?.status).toBe(TaskStatus.BLOCKED);
      expect(task?.metadata.blockReason).toContain('unavailable');
    });

    it('should block prior auth task when data unavailable', () => {
      const engine = new WorkflowEngine();
      const visit = engine.createVisit(mockPatient);

      // No prior auth data provided
      engine.processTask(visit.id, TaskType.PRIOR_AUTH_CHECK, {});

      const task = visit.getTask(TaskType.PRIOR_AUTH_CHECK);
      expect(task?.status).toBe(TaskStatus.BLOCKED);
      expect(task?.metadata.blockReason).toContain('unavailable');
    });

    it('should set visit to ESCALATED when task is blocked', () => {
      const engine = new WorkflowEngine();
      const visit = engine.createVisit(mockPatient);

      engine.processTask(visit.id, TaskType.INSURANCE_VERIFICATION, {});

      const updatedVisit = engine.getVisit(visit.id);
      expect(updatedVisit?.state).toBe(VisitState.ESCALATED);
    });
  });

  describe('audit events', () => {
    it('should log task creation events', () => {
      const engine = new WorkflowEngine();
      const visit = engine.createVisit(mockPatient);

      expect(visit.auditEvents.length).toBeGreaterThan(0);
      const creationEvents = visit.auditEvents.filter(e => e.type === 'task_created');
      expect(creationEvents).toHaveLength(6);
    });

    it('should log task completion events', () => {
      const engine = new WorkflowEngine();
      const visit = engine.createVisit(mockPatient);

      const input: TaskInput = {
        insurance: { verified: true, active: true }
      };

      engine.processTask(visit.id, TaskType.INSURANCE_VERIFICATION, input);

      const completionEvents = visit.auditEvents.filter(e => e.type === 'task_completed');
      expect(completionEvents.length).toBeGreaterThan(0);
    });

    it('should log task escalation events', () => {
      const engine = new WorkflowEngine();
      const visit = engine.createVisit(mockPatient);

      const input: TaskInput = {
        medication: { changeReported: true }
      };

      engine.processTask(visit.id, TaskType.MEDICATION_REVIEW, input);

      const escalationEvents = visit.auditEvents.filter(e => e.type === 'task_escalated');
      expect(escalationEvents.length).toBeGreaterThan(0);
    });

    it('should log task blocked events', () => {
      const engine = new WorkflowEngine();
      const visit = engine.createVisit(mockPatient);

      engine.processTask(visit.id, TaskType.INSURANCE_VERIFICATION, {});

      const blockedEvents = visit.auditEvents.filter(e => e.type === 'task_blocked');
      expect(blockedEvents.length).toBeGreaterThan(0);
    });
  });

  describe('routing triggers', () => {
    it('should escalate for chest pain', () => {
      const engine = new WorkflowEngine();
      const visit = engine.createVisit(mockPatient);

      const input: TaskInput = {
        visitReason: { reason: 'chest pain' }
      };

      engine.processTask(visit.id, TaskType.VISIT_REASON, input);

      const task = visit.getTask(TaskType.VISIT_REASON);
      expect(task?.status).toBe(TaskStatus.ESCALATED);
      expect(task?.escalationTarget).toBe(EscalationTarget.NURSE);
    });

    it('should escalate for shortness of breath', () => {
      const engine = new WorkflowEngine();
      const visit = engine.createVisit(mockPatient);

      const input: TaskInput = {
        visitReason: { reason: 'shortness of breath' }
      };

      engine.processTask(visit.id, TaskType.VISIT_REASON, input);

      const task = visit.getTask(TaskType.VISIT_REASON);
      expect(task?.status).toBe(TaskStatus.ESCALATED);
    });

    it('should escalate for severe pain', () => {
      const engine = new WorkflowEngine();
      const visit = engine.createVisit(mockPatient);

      const input: TaskInput = {
        visitReason: { reason: 'severe pain in abdomen' }
      };

      engine.processTask(visit.id, TaskType.VISIT_REASON, input);

      const task = visit.getTask(TaskType.VISIT_REASON);
      expect(task?.status).toBe(TaskStatus.ESCALATED);
    });

    it('should complete for routine visit', () => {
      const engine = new WorkflowEngine();
      const visit = engine.createVisit(mockPatient);

      const input: TaskInput = {
        visitReason: { reason: 'Annual physical examination' }
      };

      engine.processTask(visit.id, TaskType.VISIT_REASON, input);

      const task = visit.getTask(TaskType.VISIT_REASON);
      expect(task?.status).toBe(TaskStatus.COMPLETED);
    });
  });
});
