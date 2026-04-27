# Pre-Visit Intake Orchestration Engine

> **FDE Week 1 — Scenario 5: Small-Clinic Patient Intake**

A prototype demonstrating workflow orchestration and escalation logic for a family medicine clinic's pre-visit intake process.

---

## Scenario Overview

A 6-physician family medicine practice (2 locations, ~180 patients per day) relies on a 4-person front-desk team to perform patient intake. Physicians frequently discover during visits that required intake steps were missed — most commonly expired prior authorizations or unreviewed medication changes.

The clinic wants to reduce administrative burden using an agentic workflow, with three constraints:

1. **No clinical judgment** by the agent
2. **Visit-reason interactions** must preserve human escalation
3. **HIPAA and medical-record compliance** is non-negotiable

---

## What This Prototype Demonstrates

### Core Capability
**Pre-visit intake orchestration and escalation engine** that:
- Creates and tracks 6 intake task types
- Executes deterministic workflow rules
- Routes issues to appropriate human roles (front desk, nurse, manager)
- Maintains explicit state transitions and audit trails
- Provides decision transparency with structured explanations

### Visit States
- `NOT_STARTED` → Visit created, no processing yet
- `IN_PROGRESS` → Tasks being processed automatically
- `ESCALATED` → Human intervention required (blocked or escalated task)
- `READY_FOR_REVIEW` → All tasks resolved, awaiting approval
- `CLEARED` → Human review completed, ready for appointment

### Task Types
1. **insurance_verification** — Verify insurance coverage
2. **prior_auth_check** — Check prior authorization status
3. **questionnaire** — Pre-visit questionnaire completion
4. **visit_reason** — Capture and evaluate visit reason (routing triggers)
5. **medication_review** — Review medication list changes
6. **allergy_review** — Review allergy list changes

### Decision Transparency (Loop 3)
Every task decision includes structured explanation:
- **Decision type**: completed / escalated / blocked
- **Reason code**: Machine-readable code (e.g., `INS_DATA_UNAVAILABLE`)
- **Reason text**: Human-readable explanation
- **Rule applied**: Explicit business rule that triggered the decision
- **Confidence**: Always "deterministic" (no ML)
- **Next action**: Specific guidance on what should happen next
- **Owner**: Who is responsible (system/front_desk/nurse/manager)
- **Missing data**: What's unavailable (for blocked tasks)

### BLOCKED vs ESCALATED
- **BLOCKED**: External system/data unavailable (technical issue)
  - Example: Insurance API returns 503 error
  - Resolution: Retry system or manual workaround
- **ESCALATED**: Business rule requires human review (policy/clinical issue)
  - Example: Prior authorization expired
  - Resolution: Human decision and action

---

## Quick Start

### Prerequisites
- Node.js 18+
- npm

### Installation
```bash
npm install
```

### Run Demo Scenarios
```bash
npm run demo:all
```

Shows 5 scenarios:
1. **Successful intake** → All tasks complete, visit cleared
2. **Prior auth expired** → Escalated to front desk
3. **Routing trigger detected** → Escalated to nurse (e.g., "chest pain")
4. **Medication change** → Escalated to nurse
5. **External data unavailable** → Task blocked, visit escalated

### Run Tests
```bash
npm test
```

58 unit tests covering:
- Task state transitions
- Visit state management
- Workflow rules and escalation logic
- Decision explanation generation
- Owner assignment logic

### View in Browser
Open `output/visit-viewer.html` in a browser to see:
- Visual workflow stepper (NOT_STARTED → CLEARED)
- Visit and task ownership indicators
- Decision explanations for each task
- Next action guidance
- Audit trail with formatted events

### Build
```bash
npm run build
```

---

## Repository Structure

```
.
├── README.md                       # This file (main entry point)
├── DECISION_TRANSPARENCY.md        # Decision explanation model (Loop 3)
├── CLAUDE.md                       # Agent instructions
│
├── docs/                           # Formal Week 1 deliverables
│   ├── 00-assumptions-log.md
│   ├── 01-problem-statement-and-success-metrics.md
│   ├── 02-delegation-analysis.md
│   ├── 03-agent-specification.md
│   ├── 04-validation-design.md
│   └── 05-assumptions-and-unknowns.md
│
├── build_loop/                     # Iteration notes and summaries
│   ├── claude-build-notes.md
│   ├── loop1-implementation.md     # Initial prototype (39 tests)
│   ├── loop1-prototype-readme.md   # Original detailed docs
│   ├── loop2-revision-notes.md     # Audit logging, BLOCKED state
│   └── loop3-refinement.md         # Decision transparency
│
├── diagrams/                       # Workflow visuals
│   ├── workflow-overview.md
│   └── sequence-diagram.md
│
├── output/                         # Demo artifacts
│   ├── visit-viewer.html           # Interactive HTML viewer
│   ├── sample-visit-state.json     # Example JSON output
│   ├── scenario-walkthrough.md     # Step-by-step example
│   └── viewer-update-summary.md
│
├── src/                            # Source code
│   ├── types/
│   │   ├── enums.ts                # States, owners, decision types
│   │   └── interfaces.ts           # DecisionExplanation, PatientInfo
│   ├── models/
│   │   ├── Task.ts                 # Task entity with decisions
│   │   ├── Visit.ts                # Visit entity with ownership
│   │   └── AuditEvent.ts           # Audit logging
│   ├── engine/
│   │   └── WorkflowEngine.ts       # Core orchestration logic
│   └── scenarios/
│       ├── mockData.ts             # Mock patient data
│       └── runAll.ts               # Demo runner
│
├── package.json
├── tsconfig.json
└── jest.config.js
```

---

## Key Design Decisions

### 1. Deterministic Rule Engine
The system uses explicit, deterministic rules rather than ML-based classification. This ensures:
- Predictable, auditable behavior
- No black-box decisions
- Easy to explain to non-technical stakeholders
- Regulatory compliance (healthcare explainability requirements)

### 2. Decision Transparency Layer (Loop 3)
Every workflow decision includes structured explanations showing:
- What was decided
- Why it was decided (business rule)
- What to do next
- Who should do it

### 3. Explicit Ownership
Every task and visit has a clear owner (system, front_desk, nurse, manager):
- Reduces confusion
- Enables work queue routing
- Manager coordinates when both admin and clinical escalations exist

### 4. Conservative Escalation
The system errs on the side of escalation. When data is ambiguous or missing, it escalates rather than making assumptions. This prioritizes safety over automation.

### 5. Human-in-the-Loop
The `READY_FOR_REVIEW` state ensures explicit human approval before `CLEARED`:
- Separates automated completion from final approval
- Creates audit trail of who reviewed and approved
- Enforces human oversight requirement

### 6. No Clinical Judgment
Visit reason "routing triggers" use keyword matching only:
- **NOT**: Clinical interpretation, diagnosis, or triage
- **IS**: Administrative routing to appropriate staff member
- Conservative: flags phrases like "chest pain" for nurse review

---

## Prototype Limitations

### Intentionally NOT Implemented
- ❌ Database persistence (in-memory only)
- ❌ Real external integrations (mock data only)
- ❌ HIPAA compliance controls
- ❌ Authentication/authorization
- ❌ Encryption (at rest or in transit)
- ❌ Production monitoring or alerting
- ❌ Advanced NLP for visit reason classification
- ❌ Concurrent visit handling
- ❌ Web-based staff dashboard

### What This IS
- ✅ Workflow logic demonstration
- ✅ Decision transparency model
- ✅ State machine prototype
- ✅ Escalation routing logic
- ✅ Testable, maintainable code

### What This IS NOT
- ❌ Production-ready system
- ❌ Clinical decision support tool
- ❌ Diagnostic system
- ❌ HIPAA-compliant application

---

## Testing

```bash
npm test
```

**Results:**
```
Test Suites: 3 passed, 3 total
Tests:       58 passed, 58 total
```

**Coverage:**
- Task state transitions (pending → completed/escalated/blocked)
- Visit state computation based on task statuses
- Workflow rules for all 6 task types
- Decision explanation structure
- Owner assignment logic
- Edge cases (missing data, expired auth, routing triggers)

---

## Documentation Map

| Document | Purpose |
|----------|---------|
| `README.md` | Main entry point (you are here) |
| `DECISION_TRANSPARENCY.md` | Decision explanation model and reason codes |
| `docs/03-agent-specification.md` | Complete agent specification (formal) |
| `build_loop/loop1-implementation.md` | Initial prototype summary |
| `build_loop/loop2-revision-notes.md` | Audit logging and BLOCKED state additions |
| `build_loop/loop3-refinement.md` | Decision transparency refinement |
| `output/scenario-walkthrough.md` | Step-by-step example with full decision explanations |
| `output/visit-viewer.html` | Interactive visual viewer |

---

## Example Output

### Successful Intake
```
Visit State: READY_FOR_REVIEW
Owner: Front Desk
Next Action: Ready for human review and approval

Tasks:
  ✓ insurance_verification (completed)
  ✓ prior_auth_check (completed)
  ✓ questionnaire (completed)
  ✓ visit_reason (completed)
  ✓ medication_review (completed)
  ✓ allergy_review (completed)
```

### Blocked Task (External System Issue)
```
Visit State: ESCALATED
Owner: Front Desk
Next Action: Resolve blocked administrative tasks or escalated items

Tasks:
  ⚠ insurance_verification (BLOCKED)
    Decision: blocked
    Reason: INS_DATA_UNAVAILABLE
    Reason Text: Insurance verification data unavailable from external system
    Rule: If insurance data is missing → BLOCK task (external system issue)
    Next Action: Retry insurance verification system or manually verify coverage
    Missing Data:
      • insurance verification status
      • policy details
```

### Escalated Task (Business Rule)
```
Visit State: ESCALATED
Owner: Nurse
Next Action: Nurse review required: resolve escalated clinical tasks

Tasks:
  ⚠ visit_reason (ESCALATED)
    Decision: escalated
    Reason: VR_ROUTING_TRIGGER
    Reason Text: Visit reason contains routing trigger phrase - requires nurse review
    Rule: If visitReason contains routing trigger → ESCALATE to nurse
    Matched Trigger: "chest pain"
    Next Action: Nurse to review visit reason and triage appropriately
```

---

## Extension Points for Production

If building a production system:

1. **Persistence**: PostgreSQL database with audit tables
2. **External Integrations**: Real insurance APIs, EHR connectors, prior auth systems
3. **User Interface**: Web dashboard for staff work queues
4. **Notifications**: Alert staff when tasks escalated
5. **Advanced NLP**: ML models for better visit reason classification
6. **HIPAA Compliance**: Encryption, access controls, audit logs, BAAs
7. **Analytics**: Track escalation rates, bottlenecks, completion times
8. **Scheduling Integration**: Connect with appointment scheduling system
9. **Rule Configuration**: Allow clinics to customize escalation rules
10. **Multi-tenancy**: Support multiple clinics with isolated data

---

## HIPAA Considerations

This prototype does **NOT** implement HIPAA compliance. A production system would require:

- Encryption at rest and in transit
- Comprehensive access audit logs
- Role-based access control (RBAC)
- Data retention and destruction policies
- Secure authentication (MFA)
- PHI handling procedures
- Business Associate Agreements (BAAs)
- Incident response plan
- Regular security assessments

---

## Questions or Feedback?

This is a **prototype** for stakeholder review and requirements validation.

For questions about:
- **Workflow logic**: See `DECISION_TRANSPARENCY.md` and `docs/03-agent-specification.md`
- **Implementation**: See source code in `src/` with inline comments
- **Build iterations**: See `build_loop/` directory
- **Visual demo**: Open `output/visit-viewer.html`

---

## Summary

This prototype successfully demonstrates:

✅ **Workflow orchestration** with 6 task types and 5 visit states  
✅ **Decision transparency** with structured explanations  
✅ **Appropriate escalation** to front desk, nurse, or manager  
✅ **Conservative guardrails** to prevent overstepping clinical boundaries  
✅ **Explicit ownership** and next actions for operational clarity  
✅ **BLOCKED vs ESCALATED** semantic distinction  
✅ **Human-in-the-loop** requirement with READY_FOR_REVIEW state  
✅ **Complete audit trail** with reason codes and business rules  
✅ **Clean, testable, maintainable code** (58/58 tests passing)  

The system is ready for stakeholder review, requirements validation, and feedback on workflow logic before production planning.
