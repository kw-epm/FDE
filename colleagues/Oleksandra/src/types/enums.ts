export enum VisitState {
  NOT_STARTED = 'NOT_STARTED',
  IN_PROGRESS = 'IN_PROGRESS',
  READY_FOR_REVIEW = 'READY_FOR_REVIEW',
  ESCALATED = 'ESCALATED',
  CLEARED = 'CLEARED'
}

export enum TaskType {
  INSURANCE_VERIFICATION = 'insurance_verification',
  PRIOR_AUTH_CHECK = 'prior_auth_check',
  QUESTIONNAIRE = 'questionnaire',
  VISIT_REASON = 'visit_reason',
  MEDICATION_REVIEW = 'medication_review',
  ALLERGY_REVIEW = 'allergy_review'
}

export enum TaskStatus {
  PENDING = 'pending',
  COMPLETED = 'completed',
  ESCALATED = 'escalated',
  BLOCKED = 'blocked'
}

export enum EscalationTarget {
  FRONT_DESK = 'front_desk',
  NURSE = 'nurse'
}

export enum AuditEventType {
  TASK_CREATED = 'task_created',
  TASK_COMPLETED = 'task_completed',
  TASK_ESCALATED = 'task_escalated',
  TASK_BLOCKED = 'task_blocked',
  VISIT_STATE_CHANGED = 'visit_state_changed',
  REVIEW_COMPLETED = 'review_completed'
}

export enum Owner {
  SYSTEM = 'system',
  FRONT_DESK = 'front_desk',
  NURSE = 'nurse',
  MANAGER = 'manager',
  PATIENT = 'patient'
}

export enum DecisionType {
  COMPLETED = 'completed',
  ESCALATED = 'escalated',
  BLOCKED = 'blocked'
}
