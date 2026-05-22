# Cognitive Load Map — Westbridge Family Medicine Patient Intake

**Scenario**: Scenario 5 — Small-Clinic Patient Intake  
**Company**: Westbridge Family Medicine  
**Function**: 4-person front-desk intake team  
**Stakeholder**: Dana Velazquez, Practice Manager

---

## Overview

This Cognitive Load Map decomposes all 4 work streams into Jobs to be Done (JtDs), micro-tasks, Cognitive Zones, and Breakpoints. The analysis is grounded in the scenario brief and sample artefacts.

---

## Work Stream 1: Insurance Verification

### Job to be Done 1.1: Verify Patient Insurance Eligibility

| Micro-task | Cognitive Zone | Breakpoint Type | Notes |
|------------|----------------|-----------------|-------|
| Retrieve patient demographics from athenahealth | Data Retrieval | System→System | Automated lookup |
| Query Availity for insurance eligibility | External API Call | System→System | 3 min automated |
| Interpret eligibility response (active/inactive/partial) | Decision | System→Human | Classification decision |
| Handle verification failures (~30% of cases) | Diagnosis | Human→System | Requires human judgment |
| Update patient record with verification status | Documentation | Human→System | Write back to athenahealth |

### Job to be Done 1.2: Resolve Insurance Verification Failures

| Micro-task | Cognitive Zone | Breakpoint Type | Notes |
|------------|----------------|-----------------|-------|
| Identify failure reason (expired, wrong info, system error) | Diagnosis | System→Human | Artefact 5.3 shows verification refresh issue |
| Contact patient for updated insurance info | Communication | Human→Human | Phone call required |
| Re-submit verification with corrected data | Execution | Human→System | Manual retry |
| Document resolution in patient chart | Documentation | Human→System | Required for audit trail |

### Cognitive Zones — Insurance Verification

| Zone | Description | Key Activities |
|------|-------------|----------------|
| **Intent Recognition** | Identify verification request trigger | New patient, returning patient, procedure scheduled |
| **Data Retrieval** | Fetch patient and insurance data | athenahealth lookup, Availity query |
| **Diagnosis** | Interpret verification response | Active/inactive/partial classification, failure reason |
| **Resolution** | Fix verification failures | Contact patient, correct data, resubmit |
| **Documentation** | Record verification outcome | Update athenahealth, flag for billing |

### Breakpoints — Insurance Verification

| Breakpoint | From | To | Trigger |
|------------|------|-----|---------|
| Verification failure | System | Human | Availity returns failure code |
| Data mismatch | System | Human | Patient info doesn't match insurer records |
| Manual retry needed | Human | System | Staff resubmits after patient contact |

---

## Work Stream 2: Prior-Authorisation Check

### Job to be Done 2.1: Initiate and Track Prior-Authorisation

| Micro-task | Cognitive Zone | Breakpoint Type | Notes |
|------------|----------------|-----------------|-------|
| Identify procedure requiring PA | Intent Recognition | System→System | Based on procedure code + insurer |
| Gather required clinical documentation | Data Retrieval | Human→System | Chart notes, prior visit records |
| Submit PA request to insurer via Availity | External API Call | System→System | 12 min/case average |
| Track PA status in Google Sheets | Monitoring | Human→System | Dana's chase list |
| Handle PA denial | Diagnosis | Human→System | Artefact 5.1 shows Wellpath denial pattern |

### Job to be Done 2.2: Chase Pending Prior-Authorisations

| Micro-task | Cognitive Zone | Breakpoint Type | Notes |
|------------|----------------|-----------------|-------|
| Review chase list for overdue PAs | Monitoring | Human→System | Dana's Google Sheet |
| Identify insurer-specific SLA patterns | Pattern Recognition | Human→Human | UHC Choice = 6 days, Humana = 6 days |
| Contact insurer for status update | Communication | Human→External | Phone call to insurer |
| Escalate to practice billing if needed | Coordination | Human→Human | Flag for billing team |
| Resubmit with additional documentation | Execution | Human→System | Artefact 5.1: Wellpath wants prior visit note |

### Job to be Done 2.3: Flag Visit Impact from PA Delays

| Micro-task | Cognitive Zone | Breakpoint Type | Notes |
|------------|----------------|-----------------|-------|
| Identify visit date approaching with pending PA | Monitoring | System→Human | Check athenahealth ticker |
| Flag patient at check-in | Alert | Human→Human | Artefact 5.2: TJ's visit aborted |
| Communicate delay to patient | Communication | Human→Human | Reschedule if PA not confirmed |
| Update visit status in system | Documentation | Human→System | Mark as pending PA |

### Cognitive Zones — Prior-Authorisation

| Zone | Description | Key Activities |
|------|-------------|----------------|
| **Intent Recognition** | Identify PA requirement | Procedure + insurer combination |
| **Data Retrieval** | Gather clinical documentation | Chart notes, prior visit records |
| **Submission** | Submit PA request | Availity API call |
| **Monitoring** | Track pending PAs | Google Sheets chase list |
| **Diagnosis** | Interpret denial reasons | Insurer-specific patterns |
| **Coordination** | Chase and escalate | Billing, patient communication |
| **Alert** | Flag visit impact | Check-in flag, rescheduling |

### Breakpoints — Prior-Authorisation

| Breakpoint | From | To | Trigger |
|------------|------|-----|---------|
| PA denial | System | Human | Insurer denies request |
| SLA breach | System | Human | Target chase date passed |
| Visit at risk | System | Human | PA pending, visit approaching |
| Resubmit needed | Human | System | Additional documentation gathered |

---

## Work Stream 3: Pre-Visit Questionnaire & Visit-Reason Triage

### Job to be Done 3.1: Process Pre-Visit Questionnaire

| Micro-task | Cognitive Zone | Breakpoint Type | Notes |
|------------|----------------|-----------------|-------|
| Retrieve patient questionnaire responses | Data Retrieval | System→System | From athenahealth patient portal |
| Parse free-text responses | Reasoning | System→System | NLP to extract key information |
| Classify visit reason (routine/urgent/same-day) | Decision | System→Human | Classification decision |
| Flag inconsistencies between questionnaire and scheduled visit | Diagnosis | System→Human | Requires human review |
| Update visit record with triage classification | Documentation | Human→System | Write to athenahealth |

### Job to be Done 3.2: Handle Visit-Reason Discrepancies

| Micro-task | Cognitive Zone | Breakpoint Type | Notes |
|------------|----------------|-----------------|-------|
| Identify discrepancy between patient-stated and scheduled reason | Diagnosis | System→Human | Requires human judgment |
| Contact patient for clarification | Communication | Human→Human | Phone call may be needed |
| Update visit classification based on clarification | Decision | Human→System | Human makes final call |
| Document discrepancy resolution | Documentation | Human→System | Required for audit trail |

### Cognitive Zones — Pre-Visit Questionnaire

| Zone | Description | Key Activities |
|------|-------------|----------------|
| **Data Retrieval** | Fetch questionnaire responses | Patient portal, athenahealth |
| **Intent Recognition** | Understand patient's stated reason | NLP parsing of free-text |
| **Classification** | Categorise visit type | Routine vs urgent vs same-day |
| **Diagnosis** | Identify discrepancies | Compare stated vs scheduled |
| **Resolution** | Clarify and correct | Patient contact, classification update |

### Breakpoints — Pre-Visit Questionnaire

| Breakpoint | From | To | Trigger |
|------------|------|-----|---------|
| Classification needed | System | Human | NLP confidence <80% |
| Discrepancy found | System | Human | Stated reason differs from scheduled |
| Clarification needed | Human | Human | Patient contact required |

### Why Not the Primary Target

**Note**: This work stream scored 17.5 on the Volume × Value analysis (secondary target), but was not selected as the primary agentic target because:
- Hard constraint: "Any contact with stated visit reason must preserve a clear human escalation path"
- The visit reason classification has clinical implications that require human judgment
- Agent can process and flag, but human must make final triage decision

---

## Work Stream 4: Medication Reconciliation & Allergy-Flag Review

### Job to be Done 4.1: Reconcile Medication History

| Micro-task | Cognitive Zone | Breakpoint Type | Notes |
|------------|----------------|-----------------|-------|
| Retrieve current medication list from DoseSpot | Data Retrieval | System→System | API call to DoseSpot |
| Retrieve prior visit medication list from athenahealth | Data Retrieval | System→System | Historical comparison |
| Compare current vs. prior medications | Reasoning | System→System | Automated comparison |
| Identify additions, removals, dosage changes | Decision | System→System | Pattern matching |
| Flag significant changes for review | Alert | System→Human | Requires human review |

### Job to be Done 4.2: Review Allergy Alerts

| Micro-task | Cognitive Zone | Breakpoint Type | Notes |
|------------|----------------|-----------------|-------|
| Retrieve allergy list from DoseSpot | Data Retrieval | System→System | Pharmacy-sourced allergies |
| Retrieve allergy list from athenahealth | Data Retrieval | System→System | Clinical-documented allergies |
| Compare and reconcile allergy lists | Decision | System→Human | Union of both; flag conflicts |
| Check for new severe allergies | Diagnosis | System→Human | Requires clinical interpretation |
| Flag critical allergies for immediate review | Alert | System→Human | Escalation trigger |

### Job to be Done 4.3: Check Drug Interactions

| Micro-task | Cognitive Zone | Breakpoint Type | Notes |
|------------|----------------|-----------------|-------|
| Query DoseSpot for drug interactions | Reasoning | System→System | API call with medication list |
| Parse interaction response (critical/moderate/minor) | Decision | System→System | Severity classification |
| Flag critical interactions | Alert | System→Human | Immediate escalation |
| Document interaction check in chart | Documentation | Human→System | Required for audit |

### Cognitive Zones — Medication Reconciliation

| Zone | Description | Key Activities |
|------|-------------|----------------|
| **Data Retrieval** | Fetch medication and allergy data | DoseSpot, athenahealth |
| **Comparison** | Compare current vs. prior | Automated pattern matching |
| **Diagnosis** | Identify changes and interactions | Rule-based and AI analysis |
| **Alert** | Flag critical items | Priority-based escalation |
| **Documentation** | Record reconciliation outcome | Chart updates |

### Breakpoints — Medication Reconciliation

| Breakpoint | From | To | Trigger |
|------------|------|-----|---------|
| New medication found | System | Human | Addition to prior list |
| Allergy change detected | System→Human | Human | New, removed, or changed severity |
| Critical interaction | System | Human | Severity = critical |
| Interaction check failed | System | Human | DoseSpot unavailable |

### Why This Is the Primary Target

This work stream scored 22.5 on the Volume × Value analysis (highest) because:
- Highest volume (180 patients/day)
- Highest non-determinism (requires reasoning beyond rules)
- Clear pain point from Artefact 5.3: "third time" medication issue
- Agent can handle reconciliation autonomously with human review for critical alerts
- Hard constraint "no clinical judgment" is manageable — agent flags, human interprets

---

## Summary: Cognitive Load by Work Stream

| Work Stream | JtDs | Micro-tasks | Primary Cognitive Zones | Key Breakpoints |
|-------------|------|-------------|-------------------------|------------------|
| Insurance Verification | 2 | 9 | Data Retrieval, Diagnosis, Resolution | Verification failure, data mismatch |
| Prior-Authorisation Check | 3 | 14 | Intent Recognition, Monitoring, Diagnosis, Coordination | PA denial, SLA breach, visit at risk |
| Pre-Visit Questionnaire | 2 | 9 | Data Retrieval, Intent Recognition, Classification, Diagnosis, Resolution | NLP confidence <80%, discrepancy found, clarification needed |
| Medication Reconciliation | 3 | 14 | Data Retrieval, Comparison, Diagnosis, Alert, Documentation | New medication found, allergy change detected, critical interaction |

---

## Assumptions

| Assumption | Confidence | Evidence |
|------------|------------|----------|
| Availity API is reliable for eligibility queries | High | Scenario brief states "REST-API tool" |
| ~30% of insurance verifications fail auto-verify | Medium | Scenario brief states "~30% that fail auto-verify" |
| Dana's chase list is the primary tracking tool | High | Artefact 5.1 shows Google Sheet |
| Insurer-specific SLA patterns are consistent | Medium | Artefact 5.1 shows patterns (UHC=6d, Humana=6d, Wellpath=deny first) |
| Verification refresh window >6 months causes billing issues | High | Artefact 5.3 explicitly documents this |

---

## Notes on Lived Work vs. Documented Process

From the artefacts:

1. **Verification refresh issue** (Artefact 5.3): Documented process assumes insurance stays valid; lived work shows verification stale after 6 months causes billing misses.

2. **Wellpath denial pattern** (Artefact 5.1): Documented SLA is 5 days; lived work shows they always deny first time and want prior visit note attached — tribal knowledge not in SOP.

3. **PA flagging at check-in** (Artefact 5.2): Documented process may include PA tracking; lived work shows front desk failed to flag at check-in, causing aborted visit.

4. **Chase list manual tracking** (Artefact 5.1): System exists (athenahealth) but staff use Google Sheets because the built-in tracker doesn't surface the patterns they need.