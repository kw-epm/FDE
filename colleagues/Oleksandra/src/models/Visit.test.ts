import { Visit } from './Visit';
import { Task } from './Task';
import { VisitState, TaskType, TaskStatus, AuditEventType } from '../types/enums';
import { PatientInfo } from '../types/interfaces';

describe('Visit', () => {
  const mockPatient: PatientInfo = {
    patientId: 'P001',
    name: 'John Doe',
    dateOfBirth: '1980-01-01'
  };

  describe('constructor', () => {
    it('should create a visit with NOT_STARTED state', () => {
      const visit = new Visit('visit-1', mockPatient);

      expect(visit.id).toBe('visit-1');
      expect(visit.patientInfo).toEqual(mockPatient);
      expect(visit.state).toBe(VisitState.NOT_STARTED);
      expect(visit.tasks.size).toBe(0);
    });
  });

  describe('state transitions', () => {
    it('should transition to IN_PROGRESS when tasks are added', () => {
      const visit = new Visit('visit-1', mockPatient);
      const task = new Task('task-1', TaskType.INSURANCE_VERIFICATION);

      visit.addTask(task);

      expect(visit.state).toBe(VisitState.IN_PROGRESS);
    });

    it('should transition to READY_FOR_REVIEW when all tasks are completed', () => {
      const visit = new Visit('visit-1', mockPatient);
      const task1 = new Task('task-1', TaskType.INSURANCE_VERIFICATION);
      const task2 = new Task('task-2', TaskType.QUESTIONNAIRE);

      visit.addTask(task1);
      visit.addTask(task2);

      task1.complete();
      task2.complete();
      visit.updateState();

      expect(visit.state).toBe(VisitState.READY_FOR_REVIEW);
    });

    it('should transition to ESCALATED when any task is escalated', () => {
      const visit = new Visit('visit-1', mockPatient);
      const task1 = new Task('task-1', TaskType.INSURANCE_VERIFICATION);
      const task2 = new Task('task-2', TaskType.QUESTIONNAIRE);

      visit.addTask(task1);
      visit.addTask(task2);

      task1.complete();
      task2.escalate('front_desk' as any, 'Questionnaire incomplete');
      visit.updateState();

      expect(visit.state).toBe(VisitState.ESCALATED);
    });

    it('should transition to ESCALATED when any task is blocked', () => {
      const visit = new Visit('visit-1', mockPatient);
      const task1 = new Task('task-1', TaskType.INSURANCE_VERIFICATION);
      const task2 = new Task('task-2', TaskType.PRIOR_AUTH_CHECK);

      visit.addTask(task1);
      visit.addTask(task2);

      task1.complete();
      task2.block('Waiting for external system');
      visit.updateState();

      expect(visit.state).toBe(VisitState.ESCALATED);
    });

    it('should remain IN_PROGRESS when some tasks are pending', () => {
      const visit = new Visit('visit-1', mockPatient);
      const task1 = new Task('task-1', TaskType.INSURANCE_VERIFICATION);
      const task2 = new Task('task-2', TaskType.QUESTIONNAIRE);
      const task3 = new Task('task-3', TaskType.VISIT_REASON);

      visit.addTask(task1);
      visit.addTask(task2);
      visit.addTask(task3);

      task1.complete();
      visit.updateState();

      expect(visit.state).toBe(VisitState.IN_PROGRESS);
    });
  });

  describe('task management', () => {
    it('should add and retrieve tasks', () => {
      const visit = new Visit('visit-1', mockPatient);
      const task = new Task('task-1', TaskType.INSURANCE_VERIFICATION);

      visit.addTask(task);

      const retrieved = visit.getTask(TaskType.INSURANCE_VERIFICATION);
      expect(retrieved).toBe(task);
    });

    it('should return all tasks', () => {
      const visit = new Visit('visit-1', mockPatient);
      const task1 = new Task('task-1', TaskType.INSURANCE_VERIFICATION);
      const task2 = new Task('task-2', TaskType.QUESTIONNAIRE);

      visit.addTask(task1);
      visit.addTask(task2);

      const allTasks = visit.getAllTasks();
      expect(allTasks).toHaveLength(2);
      expect(allTasks).toContain(task1);
      expect(allTasks).toContain(task2);
    });

    it('should return undefined for non-existent task', () => {
      const visit = new Visit('visit-1', mockPatient);

      const retrieved = visit.getTask(TaskType.INSURANCE_VERIFICATION);
      expect(retrieved).toBeUndefined();
    });
  });

  describe('audit events', () => {
    it('should log audit events', () => {
      const visit = new Visit('visit-1', mockPatient);

      visit.logAuditEvent(AuditEventType.TASK_CREATED, {
        taskId: 'task-1',
        taskType: 'insurance_verification'
      });

      expect(visit.auditEvents).toHaveLength(1);
      expect(visit.auditEvents[0].type).toBe(AuditEventType.TASK_CREATED);
      expect(visit.auditEvents[0].details.taskId).toBe('task-1');
    });

    it('should log state changes automatically', () => {
      const visit = new Visit('visit-1', mockPatient);
      const task = new Task('task-1', TaskType.INSURANCE_VERIFICATION);

      visit.addTask(task);

      const stateChangeEvents = visit.auditEvents.filter(
        e => e.type === AuditEventType.VISIT_STATE_CHANGED
      );
      expect(stateChangeEvents.length).toBeGreaterThan(0);
    });
  });

  describe('completeReview', () => {
    it('should transition from READY_FOR_REVIEW to CLEARED', () => {
      const visit = new Visit('visit-1', mockPatient);
      const task1 = new Task('task-1', TaskType.INSURANCE_VERIFICATION);
      const task2 = new Task('task-2', TaskType.QUESTIONNAIRE);

      visit.addTask(task1);
      visit.addTask(task2);
      task1.complete();
      task2.complete();
      visit.updateState();

      expect(visit.state).toBe(VisitState.READY_FOR_REVIEW);

      visit.completeReview('Test Reviewer');

      expect(visit.state).toBe(VisitState.CLEARED);
      expect(visit.reviewedBy).toBe('Test Reviewer');
      expect(visit.reviewedAt).toBeInstanceOf(Date);
    });

    it('should transition from ESCALATED to CLEARED', () => {
      const visit = new Visit('visit-1', mockPatient);
      const task = new Task('task-1', TaskType.INSURANCE_VERIFICATION);

      visit.addTask(task);
      task.escalate('front_desk' as any, 'Test escalation');
      visit.updateState();

      expect(visit.state).toBe(VisitState.ESCALATED);

      visit.completeReview('Test Reviewer');

      expect(visit.state).toBe(VisitState.CLEARED);
      expect(visit.reviewedBy).toBe('Test Reviewer');
    });

    it('should throw error if not in reviewable state', () => {
      const visit = new Visit('visit-1', mockPatient);
      const task = new Task('task-1', TaskType.INSURANCE_VERIFICATION);
      visit.addTask(task);

      expect(visit.state).toBe(VisitState.IN_PROGRESS);

      expect(() => visit.completeReview('Test Reviewer')).toThrow();
    });

    it('should log review completed audit event', () => {
      const visit = new Visit('visit-1', mockPatient);
      const task1 = new Task('task-1', TaskType.INSURANCE_VERIFICATION);
      const task2 = new Task('task-2', TaskType.QUESTIONNAIRE);

      visit.addTask(task1);
      visit.addTask(task2);
      task1.complete();
      task2.complete();
      visit.updateState();

      visit.completeReview('Test Reviewer');

      const reviewEvents = visit.auditEvents.filter(
        e => e.type === AuditEventType.REVIEW_COMPLETED
      );
      expect(reviewEvents).toHaveLength(1);
      expect(reviewEvents[0].details.reviewedBy).toBe('Test Reviewer');
    });
  });

  describe('toJSON', () => {
    it('should serialize visit to JSON', () => {
      const visit = new Visit('visit-1', mockPatient);
      const task = new Task('task-1', TaskType.INSURANCE_VERIFICATION);
      visit.addTask(task);

      const json = visit.toJSON();

      expect(json.id).toBe('visit-1');
      expect(json.patientInfo).toEqual(mockPatient);
      expect(json.state).toBe(VisitState.IN_PROGRESS);
      expect(json.tasks).toHaveLength(1);
      expect(json.auditEvents).toBeDefined();
      expect(json.createdAt).toBeInstanceOf(Date);
      expect(json.updatedAt).toBeInstanceOf(Date);
    });

    it('should include review information when reviewed', () => {
      const visit = new Visit('visit-1', mockPatient);
      const task = new Task('task-1', TaskType.INSURANCE_VERIFICATION);
      visit.addTask(task);
      task.complete();
      visit.updateState();
      visit.completeReview('Test Reviewer');

      const json = visit.toJSON();

      expect(json.reviewedBy).toBe('Test Reviewer');
      expect(json.reviewedAt).toBeInstanceOf(Date);
    });
  });
});
