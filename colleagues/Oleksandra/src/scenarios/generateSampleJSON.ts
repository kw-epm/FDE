import { WorkflowEngine } from '../engine/WorkflowEngine';
import { TaskType } from '../types/enums';
import { mockPatients, successfulIntakeData } from './mockData';
import * as fs from 'fs';
import * as path from 'path';

// Generate sample JSON output for a complete visit workflow
function generateSampleJSON() {
  const engine = new WorkflowEngine();
  const visit = engine.createVisit(mockPatients.patient1);

  // Process all tasks
  engine.processTask(visit.id, TaskType.INSURANCE_VERIFICATION, successfulIntakeData);
  engine.processTask(visit.id, TaskType.PRIOR_AUTH_CHECK, successfulIntakeData);
  engine.processTask(visit.id, TaskType.QUESTIONNAIRE, successfulIntakeData);
  engine.processTask(visit.id, TaskType.VISIT_REASON, successfulIntakeData);
  engine.processTask(visit.id, TaskType.MEDICATION_REVIEW, successfulIntakeData);
  engine.processTask(visit.id, TaskType.ALLERGY_REVIEW, successfulIntakeData);

  // Complete human review
  engine.completeReview(visit.id, 'Jane Doe (Front Desk)');

  const visitData = engine.getVisit(visit.id);
  if (!visitData) {
    throw new Error('Visit not found');
  }

  const jsonOutput = JSON.stringify(visitData.toJSON(), null, 2);

  // Create output directory if it doesn't exist
  const outputDir = path.join(__dirname, '../../output');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // Write to file
  const outputPath = path.join(outputDir, 'sample-visit-state.json');
  fs.writeFileSync(outputPath, jsonOutput);

  console.log(`Sample JSON written to: ${outputPath}`);
  console.log('\nSample Output:');
  console.log(jsonOutput);

  return jsonOutput;
}

if (require.main === module) {
  generateSampleJSON();
}

export { generateSampleJSON };
