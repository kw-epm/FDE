# Pre-Visit Intake Orchestration Engine - Prototype

A small-scale prototype demonstrating workflow orchestration and escalation logic for a family medicine clinic's patient intake process.

## Overview

This prototype models the core workflow logic for managing pre-visit intake tasks and escalating issues to appropriate staff members (front desk or nurses) based on deterministic rules.

## Project Structure

```
.
├── src/
│   ├── types/
│   │   ├── enums.ts           # Visit states, task types, task statuses
│   │   └── interfaces.ts       # Data interfaces
│   ├── models/
│   │   ├── Task.ts            # Task entity with state transitions
│   │   ├── Task.test.ts       # Task unit tests
│   │   ├── Visit.ts           # Visit entity with state management
│   │   └── Visit.test.ts      # Visit unit tests
│   ├── engine/
│   │   ├── WorkflowEngine.ts  # Core orchestration logic
│   │   └── WorkflowEngine.test.ts # Engine tests
│   └── scenarios/
│       ├── mockData.ts        # Mock patient and scenario data
│       └── runAll.ts          # Demo script for all scenarios
├── package.json
├── tsconfig.json
└── jest.config.js
```

## Core Entities

### Visit States
- `NOT_STARTED` - No work has begun
- `IN_PROGRESS` - Tasks are being processed
- `ESCALATED` - One or more tasks require human intervention
- `READY_FOR_REVIEW` - All tasks processed, pending final review
- `CLEARED` - All tasks completed successfully

### Task Types
- `insurance_verification` - Verify insurance coverage
- `prior_auth_check` - Check prior authorization status
- `questionnaire` - Pre-visit questionnaire completion
- `visit_reason` - Capture and evaluate visit reason
- `medication_review` - Review medication list
- `allergy_review` - Review allergy list

### Task Statuses
- `pending` - Not yet processed
- `completed` - Successfully completed
- `escalated` - Requires human intervention
- `blocked` - Cannot proceed due to dependency

## Workflow Rules

### Insurance Verification
- ✅ **Complete**: Insurance verified and active
- ⚠️ **Escalate to Front Desk**: Verification failed, insurance not active, or data missing

### Prior Authorization Check
- ✅ **Complete**: No prior auth required, or auth approved and not expired
- ⚠️ **Escalate to Front Desk**: Auth required but not approved, or auth expired

### Questionnaire
- ✅ **Complete**: Questionnaire marked as completed
- ⚠️ **Escalate to Front Desk**: Questionnaire incomplete

### Visit Reason
- ✅ **Complete**: Reason provided and contains no sensitive language
- ⚠️ **Escalate to Nurse**: Reason missing, empty, or contains sensitive keywords

**Sensitive keywords include**: pain, bleeding, fever, chest, breath, dizzy, urgent, emergency, severe, suicide, depression, anxiety, abuse

### Medication Review
- ✅ **Complete**: No medication changes reported
- ⚠️ **Escalate to Nurse**: Medication change reported

### Allergy Review
- ✅ **Complete**: No allergy changes reported
- ⚠️ **Escalate to Nurse**: Allergy change reported

## Guardrails

The engine implements the following guardrails:

1. **No Clinical Judgment**: The system uses deterministic keyword matching, not clinical interpretation
2. **Conservative Escalation**: When in doubt, escalate to appropriate staff
3. **No Silent Completions**: Tasks cannot be completed when data is missing
4. **No Record Updates**: The system does not modify medication or allergy records autonomously
5. **Explicit State Transitions**: All task and visit state changes are explicit and auditable

## Setup and Installation

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Install Dependencies

```bash
npm install
```

### Build

```bash
npm run build
```

## Running the Prototype

### Run All Demo Scenarios

```bash
npm run demo:all
```

This will execute four scenarios:
1. **Successful intake** - All tasks complete successfully
2. **Prior auth missing** - Escalated to front desk
3. **Sensitive visit reason** - Escalated to nurse
4. **Medication change** - Escalated to nurse

### Run Tests

```bash
npm test
```

Run tests in watch mode:

```bash
npm run test:watch
```

## Demo Scenarios

### Scenario 1: Successful Intake Flow
Patient with verified insurance, no prior auth needed, completed questionnaire, routine visit reason, no medication/allergy changes.

**Result**: All tasks completed, visit state = `CLEARED`

### Scenario 2: Prior Auth Missing
Patient needs specialist follow-up but prior authorization not approved.

**Result**: Prior auth task escalated to front desk, visit state = `ESCALATED`

### Scenario 3: Sensitive Visit Reason
Patient reports "chest pain and shortness of breath" as visit reason.

**Result**: Visit reason task escalated to nurse, visit state = `ESCALATED`

### Scenario 4: Medication Change Reported
Patient reports new medication (Metformin 500mg).

**Result**: Medication review task escalated to nurse, visit state = `ESCALATED`

## Design Decisions

### 1. Deterministic Rule Engine
The workflow engine uses explicit, deterministic rules rather than ML-based classification. This ensures predictable behavior and makes the system auditable.

### 2. Task-Based Architecture
Each intake step is modeled as an independent task with its own state. This provides:
- Clear separation of concerns
- Easy tracking of completion status
- Ability to identify bottlenecks
- Audit trail for each step

### 3. Explicit State Machines
Both Visit and Task use explicit state enums rather than booleans. This makes the system:
- More maintainable as states evolve
- Self-documenting
- Type-safe (TypeScript enums)

### 4. Conservative Escalation
The system errs on the side of escalation. When data is ambiguous or missing, it escalates rather than making assumptions. This prioritizes safety over automation.

### 5. Separation of Business Logic and Data
The WorkflowEngine contains all business rules, while models (Task, Visit) handle state management. This makes rules easy to test and modify independently.

### 6. Immutable State Transitions
Task states can only transition forward (pending → completed/escalated/blocked). Completed tasks cannot be modified. This ensures data integrity.

### 7. Mock Data Only
All scenarios use mock data. No external system integration. This keeps the prototype focused on workflow logic.

### 8. TypeScript for Type Safety
TypeScript provides compile-time guarantees that:
- Task types are valid
- State transitions follow rules
- Data structures are consistent

## Limitations (Intentional for Prototype)

1. **No persistence** - Data exists in memory only
2. **No external integrations** - Insurance, EHR, prior auth systems are mocked
3. **Simple keyword matching** - Sensitive language detection is basic pattern matching
4. **No user interface** - Command-line demo only
5. **No authentication/authorization** - Access control not implemented
6. **No audit logging** - Minimal tracking beyond state changes
7. **No concurrent visit handling** - Single-threaded processing

## Extension Points

If building a production system, consider:

1. **Persistence Layer**: Add database storage (PostgreSQL, MongoDB)
2. **External Integrations**: Connect to real insurance verification APIs, EHR systems
3. **Advanced NLP**: Use ML models for better visit reason classification
4. **User Interface**: Build web-based dashboard for staff
5. **Notifications**: Alert front desk/nurses when tasks escalated
6. **Analytics**: Track escalation rates, bottlenecks, completion times
7. **Scheduling**: Integrate with appointment scheduling system
8. **Audit Logging**: Comprehensive HIPAA-compliant audit trail
9. **Access Control**: Role-based permissions for staff
10. **Workflow Customization**: Allow clinics to configure rules

## Testing Coverage

- **Task state transitions** - Complete, escalate, block operations
- **Visit state management** - State computation based on task statuses
- **Workflow rules** - All escalation conditions
- **Edge cases** - Missing data, expired authorizations, sensitive language

Run tests with coverage:

```bash
npm test -- --coverage
```

## HIPAA Considerations (Not Implemented)

This prototype does **not** implement HIPAA compliance. Production system would require:

- Encryption at rest and in transit
- Access audit logs
- Role-based access control
- Data retention policies
- Secure authentication
- PHI handling procedures
- Business Associate Agreements

## License

MIT

## Contact

For questions about this prototype, contact the development team.
