# Intake Orchestration Sequence Diagrams

## Happy Path: Successful Intake Flow

```mermaid
sequenceDiagram
    participant Patient
    participant System
    participant ExternalSystems
    participant FrontDesk
    participant Visit

    Patient->>System: Submit intake information
    System->>Visit: Create visit (NOT_STARTED)
    Note over Visit: 6 tasks created: pending
    
    System->>Visit: Update state → IN_PROGRESS
    
    rect rgb(200, 230, 200)
        Note over System,ExternalSystems: Automated Processing
        System->>ExternalSystems: Verify insurance
        ExternalSystems-->>System: Verified, Active
        System->>Visit: Complete insurance task
        Note over Visit: Log audit: task_completed
        
        System->>ExternalSystems: Check prior auth
        ExternalSystems-->>System: Not required
        System->>Visit: Complete prior auth task
        Note over Visit: Log audit: task_completed
        
        System->>Visit: Validate questionnaire
        Note over Visit: Questionnaire complete
        System->>Visit: Complete questionnaire task
        Note over Visit: Log audit: task_completed
        
        System->>Visit: Check visit reason
        Note over Visit: "Annual physical" - no triggers
        System->>Visit: Complete visit reason task
        Note over Visit: Log audit: task_completed
        
        System->>Visit: Review medication data
        Note over Visit: No changes reported
        System->>Visit: Complete medication task
        Note over Visit: Log audit: task_completed
        
        System->>Visit: Review allergy data
        Note over Visit: No changes reported
        System->>Visit: Complete allergy task
        Note over Visit: Log audit: task_completed
    end
    
    System->>Visit: Compute visit state
    Visit-->>System: State = READY_FOR_REVIEW
    Note over Visit: Log audit: visit_state_changed<br/>NOT_STARTED → IN_PROGRESS → READY_FOR_REVIEW
    
    System->>FrontDesk: Notify: visit ready for review
    
    rect rgb(200, 200, 230)
        Note over FrontDesk,Visit: Human Review
        FrontDesk->>Visit: Review all tasks
        FrontDesk->>Visit: Approve and clear visit
        Note over Visit: Log audit: review_completed
        Visit-->>FrontDesk: State = CLEARED
    end
    
    FrontDesk->>Patient: Intake cleared, ready for appointment
```

## Escalation Path: Routing Trigger Detected

```mermaid
sequenceDiagram
    participant Patient
    participant System
    participant ExternalSystems
    participant Nurse
    participant Visit

    Patient->>System: Submit intake with "chest pain"
    System->>Visit: Create visit (NOT_STARTED)
    Note over Visit: 6 tasks created: pending
    
    System->>Visit: Update state → IN_PROGRESS
    
    rect rgb(200, 230, 200)
        Note over System,ExternalSystems: Automated Processing
        System->>ExternalSystems: Verify insurance
        ExternalSystems-->>System: Verified, Active
        System->>Visit: Complete insurance task
        Note over Visit: Log audit: task_completed
        
        System->>ExternalSystems: Check prior auth
        ExternalSystems-->>System: Not required
        System->>Visit: Complete prior auth task
        Note over Visit: Log audit: task_completed
        
        System->>Visit: Validate questionnaire
        System->>Visit: Complete questionnaire task
        Note over Visit: Log audit: task_completed
        
        System->>Visit: Check visit reason: "chest pain"
        Note over System: Routing trigger detected!<br/>(NOT clinical diagnosis)
        System->>Visit: Escalate visit reason task → nurse
        Note over Visit: Log audit: task_escalated<br/>Target: nurse<br/>Reason: Routing trigger detected
    end
    
    System->>Visit: Compute visit state
    Visit-->>System: State = ESCALATED
    Note over Visit: Log audit: visit_state_changed<br/>Any escalated task → ESCALATED state
    
    System->>Nurse: ALERT: Visit requires nurse review
    Note over Nurse: Visit reason contains routing trigger<br/>"chest pain"
    
    rect rgb(255, 200, 200)
        Note over Nurse,Visit: Human Triage & Review
        Nurse->>Visit: Review escalated task
        Nurse->>Patient: Contact patient to assess
        Note over Nurse: Determine appropriate scheduling<br/>(same-day, urgent, etc.)
        Nurse->>Visit: Complete remaining tasks
        Nurse->>Visit: Complete review and clear
        Note over Visit: Log audit: review_completed
        Visit-->>Nurse: State = CLEARED
    end
    
    Nurse->>Patient: Intake cleared with adjusted scheduling
```

## Blocked Path: Missing External Data

```mermaid
sequenceDiagram
    participant Patient
    participant System
    participant InsuranceAPI
    participant FrontDesk
    participant Visit

    Patient->>System: Submit intake information
    System->>Visit: Create visit (NOT_STARTED)
    Note over Visit: 6 tasks created: pending
    
    System->>Visit: Update state → IN_PROGRESS
    
    rect rgb(255, 230, 200)
        Note over System,InsuranceAPI: Automated Processing with External System Failure
        System->>InsuranceAPI: Verify insurance
        InsuranceAPI-->>System: ❌ Service Unavailable (503)
        Note over System: No insurance data available
        System->>Visit: BLOCK insurance task
        Note over Visit: Log audit: task_blocked<br/>Reason: External system unavailable<br/>Status: BLOCKED (not escalated)
    end
    
    System->>Visit: Compute visit state
    Visit-->>System: State = ESCALATED
    Note over Visit: Log audit: visit_state_changed<br/>Blocked task → ESCALATED state<br/>(human intervention required)
    
    System->>FrontDesk: ALERT: External system issue
    
    rect rgb(230, 230, 230)
        Note over FrontDesk,Visit: Human Resolution
        FrontDesk->>InsuranceAPI: Check system status
        alt System recovered
            FrontDesk->>System: Retry insurance verification
            System->>Visit: Complete insurance task
        else Manual verification
            FrontDesk->>Visit: Manually verify insurance
            FrontDesk->>Visit: Update task with manual verification
        end
        FrontDesk->>Visit: Process remaining tasks
        FrontDesk->>Visit: Complete review and clear
        Visit-->>FrontDesk: State = CLEARED
    end
```

## State Transition Legend

- **NOT_STARTED**: Visit created, no tasks processed yet
- **IN_PROGRESS**: At least one task is pending (being processed)
- **READY_FOR_REVIEW**: All tasks completed, no escalations/blocks, awaiting human approval
- **ESCALATED**: One or more tasks escalated or blocked, requires human intervention
- **CLEARED**: Human review completed, visit ready for appointment

## Key Principles

1. **READY_FOR_REVIEW ≠ CLEARED**: Automated processing can reach READY_FOR_REVIEW, but only human review can set CLEARED
2. **BLOCKED ≠ ESCALATED semantics**: BLOCKED means external dependency unavailable; ESCALATED means data requires human review
3. **Both BLOCKED and ESCALATED**: Result in visit state = ESCALATED (human intervention needed)
4. **Routing triggers are NOT clinical**: Visit reason escalation uses keyword matching for administrative routing only
5. **Audit trail**: Every state transition and task change is logged with timestamp and details
