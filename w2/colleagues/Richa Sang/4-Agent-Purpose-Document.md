# Agent Purpose Document — Westbridge Family Medicine Patient Intake

**Scenario**: Scenario 5 — Small-Clinic Patient Intake  
**Company**: Westbridge Family Medicine  
**Function**: 4-person front-desk intake team  
**Stakeholder**: Dana Velazquez, Practice Manager  
**Agent Name**: MedRecon Agent

---

## 1. Job to be Done

**Medication Reconciliation & Allergy-Flag Review Agent**

Automate the review of patient medication histories and allergy alerts during the intake process, flagging changes, interactions, and discrepancies for front-desk and clinical staff review.

---

## 2. Business Context

| Attribute | Value |
|-----------|-------|
| Department | Front-Desk Intake Team |
| Process | Patient intake and pre-visit preparation |
| Customer Journey Step | Pre-visit — after check-in, before clinical encounter |
| Primary Users | Front-desk staff (4-person team) |
| Oversight | Dana Velazquez, Practice Manager |

---

## 3. Primary Objectives

| # | Objective | Success Metric |
|---|-----------|----------------|
| 1 | Automatically reconcile patient medication history with visit record | 90% of cases reconciled without human intervention |
| 2 | Flag allergy alerts and medication changes | 95% of critical alerts flagged before visit |
| 3 | Reduce medication-related intake errors | Zero patient safety incidents from medication errors in 12 months |
| 4 | Reduce front-desk staff time on medication reconciliation | 50% reduction in time spent per patient |
| 5 | Maintain HIPAA compliance | 100% compliance with audit requirements |

---

## 4. KPIs

| KPI | Target | Acceptable Ceiling |
|-----|--------|-------------------|
| **Accuracy** | >95% correct medication reconciliation | >90% |
| **Coverage** | >90% of cases handled without human escalation | >80% |
| **Throughput** | >50 patients/hour | >30 patients/hour |
| **Cost per case** | <$0.10 | <$0.20 |
| **HITL rate** | <10% requiring human review | <20% |
| **Alert recall** | >95% of critical allergy alerts identified | >90% |
| **False positive rate** | <5% | <10% |

---

## 5. Failure Modes

| Failure Mode | What It Looks Like | Consequence | Recovery Path |
|--------------|-------------------|-------------|---------------|
| **Missed allergy alert** | Patient has documented allergy but agent doesn't flag it | Patient receives contraindicated medication | Human review catches at clinical station; incident reporting |
| **Missed medication change** | New medication not flagged vs. prior visit | Clinical decision on outdated information | Physician catches during visit; chart note correction |
| **False positive alert** | Agent flags non-issue as critical | Staff alert fatigue; wasted review time | Human review filters; feedback to agent training |
| **HIPAA breach** | Protected health information exposed | Regulatory violation; patient harm | Incident response protocol; breach notification |
| **System unavailable** | DoseSpot or athenahealth API down | Intake process stalls | Manual fallback; queue processing |

---

## 6. Delegation Archetype

**Agent-led + Human Oversight**

**Rationale**: 
- High volume (180 patients/day) justifies autonomous processing
- Clear structured inputs from DoseSpot and athenahealth
- Non-determinism (Score 4.5) requires reasoning but within bounds
- Hard constraint: "No clinical judgment by the agent" — clinical interpretation stays with human
- High risk but reversible with human review before clinical decision

---

## 7. Autonomy Matrix

### AGENT DECIDES ALONE (no HITL required)

| Decision/Action | Examples |
|-----------------|----------|
| Medication reconciliation | Compare current medication list with prior visit; identify additions/removals |
| Allergy flagging | Flag new allergies, removed allergies, allergy status changes |
| Change detection | Identify medication dosage changes, frequency changes |
| Standard alerts | Flag known drug interactions per formulary rules |
| Documentation | Write reconciliation summary to patient chart |

### AGENT ACTS, HUMAN NOTIFIED AFTER

| Decision/Action | Examples |
|-----------------|----------|
| Non-critical discrepancies | Medication mismatch that doesn't affect visit; update patient record |
| Routine updates | Patient self-reported medication changes during check-in |
| System status | API availability notifications (logged, not blocking) |

### AGENT PROPOSES, HUMAN APPROVES BEFORE ACTION

| Decision/Action | Examples |
|-----------------|----------|
| Critical allergy alert | New severe allergy (anaphylaxis risk); confirm before clinical staff notified |
| Potential contraindication | New medication that may interact with existing prescriptions |
| High-risk patient flag | Immunocompromised, pregnant, other clinical risk factors |
| Unusual medication | Controlled substance, high-cost biologic, specialty medication |

### HUMAN TAKES OVER (agent supports)

| Trigger | Agent Role |
|---------|------------|
| Clinical interpretation needed | Agent gathers data, presents to nurse/physician |
| Patient disputes medication list | Agent retrieves history, human resolves |
| System unavailable | Agent queues alerts, human processes manually |
| Audit request | Agent compiles reconciliation reports for compliance |

---

## 8. Escalation Triggers

| Condition | Escalate To | Action |
|-----------|-------------|--------|
| New severe allergy (anaphylaxis) | Dana + Clinical Lead | Immediate phone notification |
| Potential drug interaction | Nursing Station | Flag in athenahealth with priority |
| System API failure >15 min | Dana | Activate manual fallback |
| HITL rate >20% for 3 days | Dana | Review and adjust thresholds |
| Patient safety near-miss | Dana + Medical Director | Incident report within 24 hrs |
| HIPAA concern | Dana + Compliance | Immediate escalation per protocol |

---

## 9. Activity Catalog

| Task | Type | Delegation Level | Data Required | Tool Required | Risk Level |
|------|------|-----------------|---------------|---------------|------------|
| Retrieve patient medication history | Retrieval | Fully agentic | Patient ID | DoseSpot API | Low |
| Retrieve allergy list | Retrieval | Fully agentic | Patient ID | athenahealth API | Low |
| Compare current vs. prior medications | Reasoning | Fully agentic | Both medication lists | Internal logic | Medium |
| Flag dosage/frequency changes | Decision | Fully agentic | Comparison output | Internal logic | Medium |
| Check drug interactions | Reasoning | Agent-led + HITL | Medication list + formulary | DoseSpot + internal rules | High |
| Flag new severe allergies | Decision | Agent proposes, human approves | Allergy list | athenahealth | High |
| Write reconciliation summary | Generation | Fully agentic | Reconciliation data | athenahealth write API | Low |
| Compile audit report | Generation | Fully agentic | Reconciliation logs | Reporting tool | Low |

---

## 10. System Requirements

| Requirement | Specification |
|-------------|---------------|
| **DoseSpot API** | Medication history, allergy data, interaction checking |
| **athenahealth API** | Patient demographics, visit records, chart updates |
| **HIPAA compliance** | Audit logging, access controls, data encryption |
| **Latency** | <5 seconds per reconciliation |
| **Availability** | 99.5% uptime during clinic hours |

---

## 11. API Authentication & Integration Details

### 11.1 Authentication Method

| System | Authentication Type | Implementation Notes |
|--------|-------------------|---------------------|
| athenahealth | OAuth 2.0 / Service Account | Use clinic's service account with RBAC; token refresh via refresh_token grant |
| Availity | API Key + Secret | Include in request headers; rotate per security policy |
| DoseSpot | Integrated with athenahealth | Same auth as athenahealth; data flows through integration |
| Google Sheets | Service Account | Domain-wide delegation for read/write access |

### 11.2 Rate Limits & Throttling

| System | Expected Rate Limit | Handling Strategy |
|--------|--------------------|--------------------|
| athenahealth | 1000 requests/hour | Implement exponential backoff; queue requests if limit approached |
| Availity | 500 requests/hour | Cache eligibility results for 24 hours; batch PA submissions |
| DoseSpot | 200 requests/hour | Cache medication history for 4 hours; refresh on patient visit |
| Google Sheets | 100 requests/100 seconds | Batch writes; use append mode for chase list updates |

### 11.3 API Response Handling

| System | Response Format | Error Handling |
|--------|----------------|----------------|
| athenahealth | JSON with patient object | Retry on 5xx; escalate on 4xx auth errors |
| Availity | JSON with eligibility status | Cache "active" results; log "inactive" for review |
| DoseSpot | JSON with medication array + interaction object | Parse interaction object for severity (critical/moderate/minor) |

---

## 12. Drug Interaction Checking Logic

### 12.1 Interaction Data Format

DoseSpot returns drug interaction data in the following structure:

```json
{
  "interactions": [
    {
      "drug1": "warfarin",
      "drug2": "aspirin",
      "severity": "critical",
      "description": "Increased risk of bleeding",
      "recommendation": "Monitor for signs of bleeding"
    }
  ]
}
```

### 12.2 Severity Classification

| Severity | Definition | Agent Action |
|----------|------------|--------------|
| **Critical** | Life-threatening interaction; immediate clinical review required | Flag for immediate human review; do not proceed to visit |
| **Moderate** | Significant interaction; may require dose adjustment | Flag for same-day clinical review |
| **Minor** | Minimal clinical significance; note only | Flag in chart; proceed with visit |

### 12.3 Interaction Response Rules

| Condition | Agent Action |
|-----------|--------------|
| No interactions returned | Proceed normally; log "no interactions found" |
| Critical interaction found | Escalate to Dana + Clinical Lead immediately; block visit scheduling |
| Moderate interaction found | Flag in athenahealth with priority tag; notify nursing station |
| Minor interaction found | Add to reconciliation summary; no immediate action |
| DoseSpot unavailable | Log error; proceed without interaction check; flag for manual review |

---

## 13. Alert Threshold Calibration

### 13.1 Critical Alert Criteria

| Alert Type | Criteria | Escalation |
|------------|----------|------------|
| **New Severe Allergy** | Patient reports allergy with anaphylaxis history OR new penicillin/antibiotic class | Immediate phone notification to Dana + Clinical Lead |
| **Potential Contraindication** | New medication + existing prescription with known interaction | Flag in athenahealth with "PHARMACY REVIEW" tag |
| **High-Risk Patient** | Immunocompromised, pregnant, dialysis patient flagged in chart | Add to daily summary for Dana review |
| **Controlled Substance** | New prescription for Schedule II-III medication | Flag for pharmacist review |

### 13.2 Alert Priority Levels

| Priority | Definition | SLA |
|----------|------------|-----|
| **P1 - Critical** | Patient safety at risk | <15 minutes |
| **P2 - High** | Clinical review needed | <1 hour |
| **P3 - Medium** | Note for chart | <4 hours |
| **P4 - Low** | Informational | Next business day |

### 13.3 False Positive Tolerance

| Metric | Target | Acceptable Ceiling |
|--------|--------|-------------------|
| False positive rate | <5% | <10% |
| Alert precision | >95% | >90% |
| Alert recall | >95% | >90% |

**Calibration approach**: Review first 100 alerts with Dana; adjust thresholds based on feedback

---

## 14. Error Handling & Fallback Logic

### 14.1 API Timeout Handling

| System | Timeout | Retry Strategy | Fallback |
|--------|---------|----------------|----------|
| athenahealth | 10 seconds | 3 retries with exponential backoff (1s, 2s, 4s) | Manual lookup; queue for retry |
| Availity | 15 seconds | 2 retries (5s, 10s) | Use cached eligibility if <24h old; else flag |
| DoseSpot | 15 seconds | 2 retries (5s, 10s) | Skip interaction check; flag for manual review |
| Google Sheets | 10 seconds | 3 retries (1s, 2s, 4s) | Log locally; sync when available |

### 14.2 Circuit Breaker Pattern

| State | Condition | Action |
|-------|-----------|--------|
| **Closed** | <5% failure rate | Normal operation |
| **Open** | >20% failures in 5 minutes | Stop calling; route to fallback |
| **Half-Open** | 30 seconds after Open | Test with single request |
| **Reset** | Test successful | Resume normal operation |

### 14.3 Data Staleness Tolerance

| Data Type | Max Age | Action if Stale |
|-----------|--------|----------------|
| Medication history | 4 hours | Refresh before use |
| Allergy list | 24 hours | Flag for verification |
| Eligibility status | 24 hours | Re-verify before visit |
| PA status | 1 hour | Query again |

### 14.4 Manual Fallback Procedures

| Scenario | Fallback Procedure |
|----------|-------------------|
| athenahealth unavailable | Front desk performs manual chart review; agent queues reconciliation |
| DoseSpot unavailable | Skip interaction check; add note "interaction check pending" |
| All systems unavailable | Cancel agent processing; front desk uses paper forms |
| Partial failure | Process available data; flag incomplete items for manual completion |

---

## 15. HIPAA Compliance Implementation

### 15.1 Audit Log Schema

| Field | Type | Description |
|-------|------|-------------|
| timestamp | ISO 8601 | When action occurred |
| user_id | UUID | Service account ID (not patient ID) |
| patient_id | Hashed | SHA-256 hash of patient ID |
| action | Enum | READ, WRITE, FLAG, ESCALATE |
| resource | String | System and resource accessed |
| result | Enum | SUCCESS, FAIL, ERROR |
| correlation_id | UUID | Links related actions |

### 15.2 Access Control Model

| Role | Permissions |
|------|-------------|
| MedRecon Agent (service account) | READ: medication, allergy / WRITE: reconciliation summary, flags |
| Front Desk | READ: all / WRITE: notes |
| Dana (Practice Manager) | READ: all / WRITE: all / EXPORT: audit logs |
| Clinical Staff | READ: medication, allergy, flags / WRITE: clinical notes |

### 15.3 Data Handling

| Data | Storage | Retention | Encryption |
|------|---------|-----------|------------|
| Patient ID | Hashed | 7 years | AES-256 at rest |
| Medication data | Encrypted | 7 years | TLS 1.3 in transit |
| Audit logs | Plaintext | 7 years | N/A (no PHI) |
| Alerts | Encrypted | 7 years | TLS 1.3 in transit |

### 15.4 Breach Response

| Step | Action | Owner |
|------|--------|-------|
| 1 | Detect anomaly (unusual access pattern) | System |
| 2 | Alert Dana within 15 minutes | System |
| 3 | Isolate affected data | IT Security |
| 4 | Assess scope | Compliance Officer |
| 5 | Notify HHS if >500 affected | Legal |
| 6 | Document incident | Dana |

---

## 16. System Integration Specification

### 16.1 Data Flow

```
Patient Check-in
       │
       ▼
┌──────────────────┐
│  athenahealth   │ ← Get patient ID, visit info
│  (demographics) │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│     DoseSpot    │ ← Get medication history, allergies
│  (medications)  │
└────────┬─────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
Check     Check
interactions  allergies
    │         │
    └────┬────┘
         │
         ▼
┌──────────────────┐
│  athenahealth   │ ← Write reconciliation summary
│  (chart update) │
└────────┬─────────┘
         │
         ▼
    Flag if needed
         │
         ▼
   Human Review
```

### 16.2 Source of Truth

| Data Type | Primary Source | Cache Duration | Conflict Resolution |
|-----------|----------------|----------------|---------------------|
| Patient demographics | athenahealth | 4 hours | athenahealth wins |
| Medication history | DoseSpot | 4 hours | DoseSpot wins |
| Allergies | athenahealth + DoseSpot | 24 hours | Union of both; flag conflicts |
| Visit status | athenahealth | Real-time | athenahealth wins |

### 16.3 Sync Frequency

| Data Type | Sync Trigger | Expected Latency |
|-----------|--------------|-------------------|
| New patient check-in | Real-time | <5 seconds |
| Medication change | Real-time | <5 seconds |
| Allergy update | Real-time | <5 seconds |
| Chase list update | Every 15 minutes | <1 minute |

---

## 17. Assumptions

| Assumption | Confidence | Evidence |
|------------|------------|----------|
| DoseSpot API provides complete medication history | Medium | Scenario brief: "integrated with athenahealth" |
| athenahealth REST API supports chart updates | Medium | Scenario brief: "modern SaaS, REST APIs" |
| No clinical judgment by agent is technically feasible | High | Hard constraint from scenario brief |
| HITL rate can be kept below 10% | Low | Requires validation in production |
| OAuth 2.0 is the authentication method | Medium | Standard for modern SaaS EHR |
| Rate limits are as estimated | Low | May need adjustment based on actual API documentation |

---

## 18. Build Loop Feedback Areas

When feeding to Claude Code, specifically ask about:

1. **Interaction checking logic**: How to handle incomplete formulary data from DoseSpot
2. **Alert threshold calibration**: How to balance recall vs. false positives
3. **System fallback**: How to handle DoseSpot/athenahealth API timeouts gracefully
4. **Audit trail design**: How to meet HIPAA audit requirements while maintaining efficiency