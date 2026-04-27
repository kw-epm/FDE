import { Task } from './Task';
import { TaskType, TaskStatus, EscalationTarget } from '../types/enums';

describe('Task', () => {
  describe('constructor', () => {
    it('should create a task with pending status', () => {
      const task = new Task('task-1', TaskType.INSURANCE_VERIFICATION);

      expect(task.id).toBe('task-1');
      expect(task.type).toBe(TaskType.INSURANCE_VERIFICATION);
      expect(task.status).toBe(TaskStatus.PENDING);
      expect(task.completedAt).toBeUndefined();
    });
  });

  describe('complete', () => {
    it('should mark task as completed', () => {
      const task = new Task('task-1', TaskType.INSURANCE_VERIFICATION);
      task.complete();

      expect(task.status).toBe(TaskStatus.COMPLETED);
      expect(task.completedAt).toBeInstanceOf(Date);
    });

    it('should throw error if task is already completed', () => {
      const task = new Task('task-1', TaskType.INSURANCE_VERIFICATION);
      task.complete();

      expect(() => task.complete()).toThrow('Task task-1 is already completed');
    });
  });

  describe('escalate', () => {
    it('should escalate task to front desk', () => {
      const task = new Task('task-1', TaskType.INSURANCE_VERIFICATION);
      task.escalate(EscalationTarget.FRONT_DESK, 'Insurance verification failed');

      expect(task.status).toBe(TaskStatus.ESCALATED);
      expect(task.escalationTarget).toBe(EscalationTarget.FRONT_DESK);
      expect(task.escalationReason).toBe('Insurance verification failed');
      expect(task.escalatedAt).toBeInstanceOf(Date);
    });

    it('should escalate task to nurse', () => {
      const task = new Task('task-1', TaskType.MEDICATION_REVIEW);
      task.escalate(EscalationTarget.NURSE, 'Medication change reported');

      expect(task.status).toBe(TaskStatus.ESCALATED);
      expect(task.escalationTarget).toBe(EscalationTarget.NURSE);
      expect(task.escalationReason).toBe('Medication change reported');
    });

    it('should throw error if trying to escalate completed task', () => {
      const task = new Task('task-1', TaskType.INSURANCE_VERIFICATION);
      task.complete();

      expect(() => task.escalate(EscalationTarget.FRONT_DESK, 'reason')).toThrow(
        'Cannot escalate completed task task-1'
      );
    });
  });

  describe('block', () => {
    it('should block task with reason', () => {
      const task = new Task('task-1', TaskType.PRIOR_AUTH_CHECK);
      task.block('Waiting for external system');

      expect(task.status).toBe(TaskStatus.BLOCKED);
      expect(task.metadata.blockReason).toBe('Waiting for external system');
    });

    it('should throw error if trying to block completed task', () => {
      const task = new Task('task-1', TaskType.INSURANCE_VERIFICATION);
      task.complete();

      expect(() => task.block('reason')).toThrow('Cannot block completed task task-1');
    });
  });

  describe('toJSON', () => {
    it('should serialize task to JSON', () => {
      const task = new Task('task-1', TaskType.INSURANCE_VERIFICATION);
      task.complete();

      const json = task.toJSON();

      expect(json.id).toBe('task-1');
      expect(json.type).toBe(TaskType.INSURANCE_VERIFICATION);
      expect(json.status).toBe(TaskStatus.COMPLETED);
      expect(json.completedAt).toBeInstanceOf(Date);
    });
  });
});
