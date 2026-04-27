import { WorkflowEngine } from '../engine/WorkflowEngine';
import { TaskType } from '../types/enums';
import {
  mockPatients,
  successfulIntakeData,
  priorAuthMissingData,
  sensitiveVisitReasonData,
  medicationChangeData,
  missingExternalData
} from './mockData';

function printVisitSummary(visit: any, scenarioName: string, showAudit: boolean = false) {
  console.log(`\n${'='.repeat(60)}`);
  console.log(`SCENARIO: ${scenarioName}`);
  console.log('='.repeat(60));
  console.log(`Visit ID: ${visit.id}`);
  console.log(`Patient: ${visit.patientInfo.name} (${visit.patientInfo.patientId})`);
  console.log(`Visit State: ${visit.state}`);
  if (visit.reviewedBy) {
    console.log(`Reviewed By: ${visit.reviewedBy} at ${new Date(visit.reviewedAt).toLocaleTimeString()}`);
  }
  console.log('\nTasks:');

  visit.tasks.forEach((task: any) => {
    console.log(`  - ${task.type}:`);
    console.log(`    Status: ${task.status}`);
    if (task.escalationTarget) {
      console.log(`    Escalated to: ${task.escalationTarget}`);
      console.log(`    Reason: ${task.escalationReason}`);
    }
    if (task.metadata.blockReason) {
      console.log(`    Block Reason: ${task.metadata.blockReason}`);
    }
  });

  if (showAudit && visit.auditEvents && visit.auditEvents.length > 0) {
    console.log('\nAudit Trail (last 10 events):');
    const recentEvents = visit.auditEvents.slice(-10);
    recentEvents.forEach((event: any) => {
      const time = new Date(event.timestamp).toLocaleTimeString();
      console.log(`  [${time}] ${event.type}`);
      if (event.details && Object.keys(event.details).length > 0) {
        console.log(`    Details: ${JSON.stringify(event.details)}`);
      }
    });
  }
}

function runScenario1() {
  console.log('\n### Scenario 1: Successful Intake with Human Review ###');
  const engine = new WorkflowEngine();
  const visit = engine.createVisit(mockPatients.patient1);

  engine.processTask(visit.id, TaskType.INSURANCE_VERIFICATION, successfulIntakeData);
  engine.processTask(visit.id, TaskType.PRIOR_AUTH_CHECK, successfulIntakeData);
  engine.processTask(visit.id, TaskType.QUESTIONNAIRE, successfulIntakeData);
  engine.processTask(visit.id, TaskType.VISIT_REASON, successfulIntakeData);
  engine.processTask(visit.id, TaskType.MEDICATION_REVIEW, successfulIntakeData);
  engine.processTask(visit.id, TaskType.ALLERGY_REVIEW, successfulIntakeData);

  let updatedVisit = engine.getVisit(visit.id);
  console.log('\n>>> After automated processing (before human review):');
  printVisitSummary(updatedVisit?.toJSON(), 'Successful Intake - READY_FOR_REVIEW', true);

  // Simulate human review
  console.log('\n>>> Simulating human review by front desk...');
  engine.completeReview(visit.id, 'Jane Doe (Front Desk)');

  updatedVisit = engine.getVisit(visit.id);
  console.log('\n>>> After human review:');
  printVisitSummary(updatedVisit?.toJSON(), 'Successful Intake - CLEARED', true);
}

function runScenario2() {
  console.log('\n### Scenario 2: Prior Auth Missing ###');
  const engine = new WorkflowEngine();
  const visit = engine.createVisit(mockPatients.patient2);

  engine.processTask(visit.id, TaskType.INSURANCE_VERIFICATION, priorAuthMissingData);
  engine.processTask(visit.id, TaskType.PRIOR_AUTH_CHECK, priorAuthMissingData);
  engine.processTask(visit.id, TaskType.QUESTIONNAIRE, priorAuthMissingData);
  engine.processTask(visit.id, TaskType.VISIT_REASON, priorAuthMissingData);
  engine.processTask(visit.id, TaskType.MEDICATION_REVIEW, priorAuthMissingData);
  engine.processTask(visit.id, TaskType.ALLERGY_REVIEW, priorAuthMissingData);

  const updatedVisit = engine.getVisit(visit.id);
  printVisitSummary(updatedVisit?.toJSON(), 'Prior Auth Missing - Escalated to Front Desk');
}

function runScenario3() {
  console.log('\n### Scenario 3: Routing Trigger in Visit Reason ###');
  const engine = new WorkflowEngine();
  const visit = engine.createVisit(mockPatients.patient3);

  engine.processTask(visit.id, TaskType.INSURANCE_VERIFICATION, sensitiveVisitReasonData);
  engine.processTask(visit.id, TaskType.PRIOR_AUTH_CHECK, sensitiveVisitReasonData);
  engine.processTask(visit.id, TaskType.QUESTIONNAIRE, sensitiveVisitReasonData);
  engine.processTask(visit.id, TaskType.VISIT_REASON, sensitiveVisitReasonData);
  engine.processTask(visit.id, TaskType.MEDICATION_REVIEW, sensitiveVisitReasonData);
  engine.processTask(visit.id, TaskType.ALLERGY_REVIEW, sensitiveVisitReasonData);

  const updatedVisit = engine.getVisit(visit.id);
  printVisitSummary(updatedVisit?.toJSON(), 'Routing Trigger Detected - Escalated to Nurse');
}

function runScenario4() {
  console.log('\n### Scenario 4: Medication Change Reported ###');
  const engine = new WorkflowEngine();
  const visit = engine.createVisit(mockPatients.patient4);

  engine.processTask(visit.id, TaskType.INSURANCE_VERIFICATION, medicationChangeData);
  engine.processTask(visit.id, TaskType.PRIOR_AUTH_CHECK, medicationChangeData);
  engine.processTask(visit.id, TaskType.QUESTIONNAIRE, medicationChangeData);
  engine.processTask(visit.id, TaskType.VISIT_REASON, medicationChangeData);
  engine.processTask(visit.id, TaskType.MEDICATION_REVIEW, medicationChangeData);
  engine.processTask(visit.id, TaskType.ALLERGY_REVIEW, medicationChangeData);

  const updatedVisit = engine.getVisit(visit.id);
  printVisitSummary(updatedVisit?.toJSON(), 'Medication Change - Escalated to Nurse');
}

function runScenario5() {
  console.log('\n### Scenario 5: Missing External Data ###');
  const engine = new WorkflowEngine();
  const visit = engine.createVisit(mockPatients.patient5);

  // Insurance verification data unavailable (external system issue)
  engine.processTask(visit.id, TaskType.INSURANCE_VERIFICATION, missingExternalData);
  engine.processTask(visit.id, TaskType.PRIOR_AUTH_CHECK, missingExternalData);
  engine.processTask(visit.id, TaskType.QUESTIONNAIRE, missingExternalData);
  engine.processTask(visit.id, TaskType.VISIT_REASON, missingExternalData);
  engine.processTask(visit.id, TaskType.MEDICATION_REVIEW, missingExternalData);
  engine.processTask(visit.id, TaskType.ALLERGY_REVIEW, missingExternalData);

  const updatedVisit = engine.getVisit(visit.id);
  printVisitSummary(updatedVisit?.toJSON(), 'External Data Unavailable - Task Blocked', true);
}

console.log('\n' + '='.repeat(60));
console.log('INTAKE ORCHESTRATION ENGINE - DEMO SCENARIOS');
console.log('='.repeat(60));

runScenario1();
runScenario2();
runScenario3();
runScenario4();
runScenario5();

console.log('\n' + '='.repeat(60));
console.log('All scenarios completed');
console.log('='.repeat(60) + '\n');
