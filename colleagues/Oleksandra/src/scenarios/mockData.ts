import { PatientInfo, TaskInput } from '../types/interfaces';

export const mockPatients: Record<string, PatientInfo> = {
  patient1: {
    patientId: 'P001',
    name: 'John Smith',
    dateOfBirth: '1980-05-15'
  },
  patient2: {
    patientId: 'P002',
    name: 'Sarah Johnson',
    dateOfBirth: '1975-08-22'
  },
  patient3: {
    patientId: 'P003',
    name: 'Michael Chen',
    dateOfBirth: '1990-03-10'
  },
  patient4: {
    patientId: 'P004',
    name: 'Emily Rodriguez',
    dateOfBirth: '1985-11-30'
  },
  patient5: {
    patientId: 'P005',
    name: 'David Williams',
    dateOfBirth: '1978-12-05'
  }
};

export const successfulIntakeData: TaskInput = {
  insurance: {
    verified: true,
    active: true,
    policyNumber: 'INS-12345',
    verificationDate: new Date()
  },
  priorAuth: {
    required: false
  },
  questionnaire: {
    completed: true,
    responses: {
      currentMedications: ['Lisinopril 10mg'],
      allergies: ['Penicillin'],
      recentChanges: 'none'
    }
  },
  visitReason: {
    reason: 'Annual physical examination',
    urgency: 'routine'
  },
  medication: {
    changeReported: false,
    medications: ['Lisinopril 10mg']
  },
  allergy: {
    changeReported: false,
    allergies: ['Penicillin']
  }
};

export const priorAuthMissingData: TaskInput = {
  insurance: {
    verified: true,
    active: true,
    policyNumber: 'INS-67890'
  },
  priorAuth: {
    required: true,
    approved: false
  },
  questionnaire: {
    completed: true,
    responses: {}
  },
  visitReason: {
    reason: 'Follow-up for specialist referral',
    urgency: 'routine'
  },
  medication: {
    changeReported: false,
    medications: []
  },
  allergy: {
    changeReported: false,
    allergies: []
  }
};

export const sensitiveVisitReasonData: TaskInput = {
  insurance: {
    verified: true,
    active: true,
    policyNumber: 'INS-11111'
  },
  priorAuth: {
    required: false
  },
  questionnaire: {
    completed: true,
    responses: {}
  },
  visitReason: {
    reason: 'Chest pain and shortness of breath for 2 days',
    urgency: 'urgent'
  },
  medication: {
    changeReported: false,
    medications: []
  },
  allergy: {
    changeReported: false,
    allergies: []
  }
};

export const medicationChangeData: TaskInput = {
  insurance: {
    verified: true,
    active: true,
    policyNumber: 'INS-22222'
  },
  priorAuth: {
    required: false
  },
  questionnaire: {
    completed: true,
    responses: {}
  },
  visitReason: {
    reason: 'Medication review',
    urgency: 'routine'
  },
  medication: {
    changeReported: true,
    medications: ['Lisinopril 10mg', 'Metformin 500mg'],
    changedMedications: ['Metformin 500mg']
  },
  allergy: {
    changeReported: false,
    allergies: ['Penicillin']
  }
};

// Missing external data scenario - insurance verification system unavailable
export const missingExternalData: TaskInput = {
  // No insurance data - simulating external system unavailable
  priorAuth: {
    required: false
  },
  questionnaire: {
    completed: true,
    responses: {}
  },
  visitReason: {
    reason: 'Annual checkup',
    urgency: 'routine'
  },
  medication: {
    changeReported: false,
    medications: ['Aspirin 81mg']
  },
  allergy: {
    changeReported: false,
    allergies: []
  }
};
