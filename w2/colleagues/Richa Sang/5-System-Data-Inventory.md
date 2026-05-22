# System/Data Inventory — Westbridge Family Medicine Patient Intake

**Scenario**: Scenario 5 — Small-Clinic Patient Intake  
**Company**: Westbridge Family Medicine  
**Function**: 4-person front-desk intake team  
**Stakeholder**: Dana Velazquez, Practice Manager

---

## Overview

This System/Data Inventory identifies what the agent needs to access, what's available, what's missing, and what's risky. The analysis addresses the scenario's mention of a legacy billing system with batch-file-only exports.

---

## System Inventory

### 1. athenahealth (EHR)

| Attribute | Value |
|-----------|-------|
| **Purpose** | Core electronic health record |
| **API Availability** | REST APIs available |
| **Data Fields** | Patient demographics, visit records, medication history, allergy list, chart notes |
| **Integration Complexity** | Medium |
| **Risk Classification** | High (PHI, clinical data) |

**Available Data for Agent**:
- Patient ID, name, DOB
- Visit history and scheduled visits
- Current medication list
- Allergy list
- Chart notes from prior visits

**Integration Notes**:
- Modern SaaS with REST APIs
- Scenario brief confirms: "athenahealth (EHR, modern SaaS, REST APIs)"
- Artefact 5.2 shows ticker exists but not integrated to check-in workflow

---

### 2. Availity (Insurance Eligibility)

| Attribute | Value |
|-----------|-------|
| **Purpose** | Insurance eligibility verification and prior-authorisation |
| **API Availability** | REST APIs available |
| **Data Fields** | Eligibility status, PA status, denial reasons, insurer-specific rules |
| **Integration Complexity** | Low |
| **Risk Classification** | Medium (billing data, not clinical) |

**Available Data for Agent**:
- Eligibility response (active/inactive/partial)
- PA submission status
- PA denial reasons
- Insurer-specific SLA data

**Integration Notes**:
- Scenario brief: "Availity (insurance eligibility, separate REST-API tool)"
- Used for both verification and PA tracking
- Artefact 5.1 shows insurer-specific patterns can be derived from responses

---

### 3. DoseSpot (Pharmacy/Medication Reconciliation)

| Attribute | Value |
|-----------|-------|
| **Purpose** | Pharmacy history and medication reconciliation |
| **API Availability** | Integrated with athenahealth |
| **Data Fields** | Current prescriptions, pharmacy history, drug interactions, allergy alerts |
| **Integration Complexity** | Low (integrated) |
| **Risk Classification** | High (PHI, medication data) |

**Available Data for Agent**:
- Patient's current medications
- Prescription history
- Drug interaction alerts
- Allergy alerts from pharmacy

**Integration Notes**:
- Scenario brief: "DoseSpot (pharmacy / medication reconciliation, integrated with athenahealth)"
- Primary data source for Medication Reconciliation work stream
- Artefact 5.3 shows medication reconciliation is a pain point

---

### 4. Google Sheets (Internal Tracking)

| Attribute | Value |
|-----------|-------|
| **Purpose** | PA chase list, flagged-patient tracker |
| **API Availability** | Google Sheets API available |
| **Data Fields** | PA status, chase dates, patient flags, notes |
| **Integration Complexity** | Low |
| **Risk Classification** | Low (internal tracking, no PHI) |

**Available Data for Agent**:
- PA submission dates
- Target chase dates
- Status (pending/approved/denied)
- Notes (insurer-specific patterns)

**Integration Notes**:
- Scenario brief: "Google Sheets (Dana's PA chase list and flagged-patient tracker)"
- Artefact 5.1 shows this is the primary tracking tool
- Manual workaround because athenahealth ticker doesn't surface needed patterns

---

### 5. Phone + Paper Intake Forms

| Attribute | Value |
|-----------|-------|
| **Purpose** | Patient self-reported information for those without portal accounts |
| **API Availability** | None — manual data entry |
| **Data Fields** | Patient-provided information, insurance cards, medication lists |
| **Integration Complexity** | N/A (manual) |
| **Risk Classification** | Medium (potential for data entry errors) |

**Data for Agent**:
- Limited — agent cannot directly access phone or paper forms
- Front-desk staff would need to enter data into athenahealth first

**Integration Notes**:
- Scenario brief: "Phone + paper intake forms (for patients without portal accounts)"
- Not a direct data source for the agent
- Represents a gap in automation for certain patient populations

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           PATIENT INTAKE FLOW                          │
└─────────────────────────────────────────────────────────────────────────┘

Patient Arrives → Front Desk Check-in → Agent Processing → Clinical Review
      │                                    │
      ▼                                    ▼
┌─────────────────┐                 ┌─────────────────────┐
│ Patient ID      │                 │ MEDRECON AGENT      │
│ Verification    │                 │                     │
└─────────────────┘                 │ 1. Query DoseSpot  │
      │                             │    (med history)    │
      ▼                             │                     │
┌─────────────────┐                 │ 2. Query athenahealth│
│ Insurance       │                 │    (allergies)      │
│ Verification    │                 │                     │
│ (Availity)      │                 │ 3. Compare & Flag   │
      │                             │                     │
      ▼                             │ 4. Write to chart   │
┌─────────────────┐                 │    (athenahealth)   │
│ PA Check       │                 │                     │
│ (Availity)      │                 │ 5. Alert if needed  │
      │                             │    (human review)   │
      ▼                             └─────────────────────┘
┌─────────────────┐                        │
│ Visit Reason    │                        ▼
│ Triage          │                 ┌─────────────────────┐
└─────────────────┘                 │ Human Review       │
      │                            │ (Nurse/Physician)   │
      ▼                            └─────────────────────┘
```

---

## Missing Data / Gaps

### Gap 1: athenahealth Ticker Integration

| Gap | Description | Impact | Mitigation |
|-----|-------------|--------|------------|
| PA status not integrated to check-in | athenahealth has ticker but front desk didn't flag (Artefact 5.2) | Patient visit aborted | Agent correlates PA status with visit calendar |

### Gap 2: Verification Refresh Window

| Gap | Description | Impact | Mitigation |
|-----|-------------|--------|------------|
| Insurance verification stale after 6 months | Artefact 5.3 shows billing miss from stale verification | Billing errors, patient complaints | Agent tracks verification age, triggers refresh |

### Gap 3: Paper/Phone Intake

| Gap | Description | Impact | Mitigation |
|-----|-------------|--------|------------|
| No digital access to paper forms or phone calls | Patients without portal accounts | Incomplete data for some patients | Staff enters data into athenahealth first |

### Gap 4: Legacy Billing System

| Gap | Description | Impact | Mitigation |
|-----|-------------|--------|------------|
| Scenario mentions "legacy billing system with batch-file-only exports" | Not explicitly named in scenario | Potential data integration gap | **Address in Discovery Questions** — need to elicit what this system is |

**Note**: The scenario brief does not name the legacy billing system. This is a gap that must be addressed through elicitation with the stakeholder.
### Gap 5: API Authentication Details

| Gap | Description | Impact | Mitigation |
|-----|-------------|--------|------------|
| Authentication method not specified | OAuth? API key? Service account? | Agent cannot connect to systems | Added to Agent Purpose Document Section 11 |

### Gap 6: Rate Limits Unknown

| Gap | Description | Impact | Mitigation |
|-----|-------------|--------|------------|
| API rate limits not specified | Could cause throttling errors | Agent may fail under load | Added estimated limits with handling strategy |

### Gap 7: Interaction Data Format

| Gap | Description | Impact | Mitigation |
|-----|-------------|--------|------------|
| Drug interaction response format unknown | How does DoseSpot return interactions? | Agent can't parse results | Added expected JSON structure and severity classification |
---

## Risk Classification

| System | Data Type | Risk Level | Compliance |
|--------|-----------|------------|------------|
| athenahealth | Clinical (PHI) | High | HIPAA |
| DoseSpot | Medication (PHI) | High | HIPAA |
| Availity | Billing | Medium | PCI-DSS (if payment data) |
| Google Sheets | Internal tracking | Low | Internal policies |
| Legacy Billing | Unknown | **Unknown** | **Requires assessment** |

---

## API Summary Table

| System | API Type | Data Available | Complexity | Risk | Integration Priority |
|--------|----------|----------------|-------------|------|---------------------|
| athenahealth | REST | Patient data, visits, chart | Medium | High | **P1 — Required** |
| DoseSpot | Integrated | Medications, allergies | Low | High | **P1 — Required** |
| Availity | REST | Eligibility, PA status | Low | Medium | P2 — Insurance/PA flows |
| Google Sheets | REST | Internal tracking | Low | Low | P3 — PA chase list only |
| Legacy Billing | **Unknown** | **Unknown** | **Unknown** | **Unknown** | **Elicit from stakeholder** |

---

## Compliance Considerations

### HIPAA Requirements

| Requirement | How Addressed |
|-------------|---------------|
| Minimum necessary | Agent only accesses patient data for reconciliation |
| Audit Trail | All API calls logged with user, timestamp, action |
| Access Controls | Role-based access; agent uses service account with limited permissions |
| Encryption | All API calls over HTTPS; data encrypted at rest |
| Breach Notification | Escalation protocol defined in Agent Purpose Document |

### State Medical-Records Compliance

| Requirement | How Addressed |
|-------------|---------------|
| Medical-records retention | athenahealth handles per state requirements |
| Patient access requests | Agent doesn't modify access policies |
| Data accuracy | Human review before clinical decisions |

---

## Assumptions

| Assumption | Confidence | Evidence |
|------------|------------|----------|
| athenahealth REST API supports chart updates | Medium | Scenario brief: "modern SaaS, REST APIs" |
| DoseSpot integration provides complete medication data | Medium | "integrated with athenahealth" but gaps shown in Artefact 5.3 |
| Legacy billing system exists but is not named | High | Scenario brief mentions it; must elicit details |
| Google Sheets API is accessible | High | Standard Google API availability |

---

## Discovery Questions for System/Data

1. **What is the legacy billing system name?** The scenario mentions "a legacy billing system with batch-file-only exports" but doesn't name it. Need to identify to assess integration feasibility.

2. **What data does the legacy billing system hold?** Understanding what data is in the legacy system determines whether it's relevant to the agent.

3. **What is the batch export schedule?** If exports are daily/weekly, agent may need to work with stale data.

4. **Is there a path to modernise the billing system?** Or is this a long-term constraint?