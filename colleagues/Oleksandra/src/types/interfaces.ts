import { TaskType, TaskStatus, EscalationTarget, DecisionType, Owner } from './enums';

export interface TaskData {
  id: string;
  type: TaskType;
  status: TaskStatus;
  escalationTarget?: EscalationTarget;
  escalationReason?: string;
  completedAt?: Date;
  escalatedAt?: Date;
  metadata?: Record<string, any>;
}

export interface PatientInfo {
  patientId: string;
  name: string;
  dateOfBirth: string;
}

export interface InsuranceData {
  verified: boolean;
  active: boolean;
  policyNumber?: string;
  verificationDate?: Date;
}

export interface PriorAuthData {
  required: boolean;
  approved?: boolean;
  expirationDate?: Date;
  authNumber?: string;
}

export interface QuestionnaireData {
  completed: boolean;
  responses?: Record<string, any>;
}

export interface VisitReasonData {
  reason: string;
  urgency?: 'routine' | 'urgent' | 'same-day';
  containsSensitiveLanguage?: boolean;
}

export interface MedicationData {
  changeReported: boolean;
  medications?: string[];
  changedMedications?: string[];
}

export interface AllergyData {
  changeReported: boolean;
  allergies?: string[];
  changedAllergies?: string[];
}

export interface TaskInput {
  insurance?: InsuranceData;
  priorAuth?: PriorAuthData;
  questionnaire?: QuestionnaireData;
  visitReason?: VisitReasonData;
  medication?: MedicationData;
  allergy?: AllergyData;
}

export interface DecisionExplanation {
  decision: DecisionType;
  reasonCode: string;
  reasonText: string;
  ruleApplied: string;
  confidence: 'deterministic';
  nextAction: string;
  owner?: Owner;
  missingData?: string[];
}
