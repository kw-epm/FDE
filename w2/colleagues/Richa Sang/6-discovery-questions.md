# Discovery Questions — Westbridge Family Medicine Patient Intake

**Scenario**: Scenario 5 — Small-Clinic Patient Intake  
**Company**: Westbridge Family Medicine  
**Stakeholder**: Dana Velazquez, Practice Manager

---

## Overview

These Discovery Questions are designed to elicit information that would *materially change the agent design* — not generic discovery questions. Each question is tied to specific tensions in the scenario brief or artefacts.

---

## Category 1: System & Data Gaps

### Question 1.1: Legacy Billing System

> **"The scenario brief mentions a legacy billing system with batch-file-only exports, but it doesn't name it. What is the name of the billing system, and what data does it hold?"**

**What I'm trying to elicit**: The existence and nature of a data integration gap. If the legacy system holds critical data (e.g., billing history, payment status), the agent may need to work around it.

**Why it would change my design**: 
- If the legacy system holds patient billing data relevant to intake, the agent may need to handle batch-file ingestion
- If it's irrelevant to intake, it can be deprioritised
- The batch-file-only constraint affects whether real-time processing is possible

**Evidence from artefacts**: None — this is a gap in the brief that must be filled

---

### Question 1.2: athenahealth Ticker Integration

> **"Artefact 5.2 shows a patient visit was aborted because the front desk didn't flag a pending PA at check-in. You mentioned athenahealth has a ticker — why isn't the front desk using it, and what would it take to integrate it into the check-in workflow?"**

**What I'm trying to elicit**: Why existing system features aren't being used and what integration work is needed

**Why it would change my design**:
- If the ticker is functional but unknown to staff → training issue, not agent issue
- If the ticker doesn't surface the right data → agent must replicate the correlation
- Integration effort affects build timeline and cost

**Evidence from artefacts**: Artefact 5.2 — "see athenahealth ticker. Front desk did not flag this at check-in"

---

## Category 2: Process & Practice

### Question 2.1: Medication Reconciliation Gaps

> **"Artefact 5.3 mentions a patient whose verification was stale after 6 months, causing a billing miss. Is there a similar pattern with medication reconciliation — are there patients whose medication history becomes stale or incomplete?"**

**What I'm trying to elicit**: Whether medication data has similar refresh issues as insurance verification

**Why it would change my design**:
- If medication history goes stale → agent needs refresh logic
- If DoseSpot maintains currency → no change needed
- Affects the agent's data freshness requirements

**Evidence from artefacts**: Artefact 5.3 — "Patient verification refresh window > 6 months caused billing miss"

---

### Question 2.2: Wellpath Denial Pattern

> **"The PA chase list shows Wellpath always denies first time and wants the prior visit note attached. Is this pattern documented anywhere, or is it tribal knowledge? Are there similar patterns with other insurers?"**

**What I'm trying to elicit**: The extent of insurer-specific tribal knowledge that would need to be codified

**Why it would change my design**:
- If documented → can be incorporated into agent rules
- If tribal knowledge → needs elicitation and validation
- Affects the agent's exception handling logic

**Evidence from artefacts**: Artefact 5.1 — "Wellpath always denies first time on this — resubmit with the August visit note"

---

### Question 2.3: Patient Populations Not in Standard Flow

> **"The scenario mentions phone and paper intake forms for patients without portal accounts. What patient populations don't fit the standard digital flow, and how is the team accommodating them today?"**

**What I'm trying to elicit**: Edge cases in the intake process that the agent must handle

**Why it would change my design**:
- If significant population → agent needs to handle manual data entry
- If minimal → can be deprioritised
- Affects the agent's input handling requirements

**Evidence from artefacts**: Scenario brief — "Phone + paper intake forms (for patients without portal accounts)"

---

## Category 3: Risk & Compliance

### Question 3.1: HIPAA Constraints on AI

> **"What specific HIPAA or malpractice insurance constraints govern AI usage at the practice? Are there constraints on what data the agent can access, process, or store?"**

**What I'm trying to elicit**: The compliance boundaries for the agent

**Why it would change my design**:
- If strict → may limit what the agent can do
- If moderate → agent can operate with standard safeguards
- Affects the agent's data handling and audit requirements

**Evidence from artefacts**: Scenario brief — "HIPAA and state medical-records compliance is non-negotiable"

---

### Question 3.2: Clinical Judgment Boundary

> **"The hard constraint says 'no clinical judgment by the agent.' Can you give me examples of what that means in practice? Where is the line between administrative flagging and clinical judgment?"**

**What I'm trying to elicit**: The precise boundary between what the agent can and cannot do

**Why it would change my design**:
- If vague → agent may over- or under-reach
- If clear → can define autonomy matrix precisely
- Critical for the agent's escalation triggers

**Evidence from artefacts**: Scenario brief — "No clinical judgment by the agent"

---

### Question 3.3: Previous Intake Misses

> **"The senior physician discovered three intake misses in the last quarter (expired prior auths). What were the root causes, and what would have prevented them?"**

**What I'm trying to elicit**: The specific failure modes the agent must prevent

**Why it would change my design**:
- If PA tracking → agent must improve PA flagging
- If verification → agent must improve verification refresh
- Defines the agent's primary failure mode targets

**Evidence from artefacts**: Scenario brief — "Senior physician has discovered three intake misses in the last quarter (all expired prior auths)"

---

## Category 4: Stakeholder Concerns

### Question 4.1: Dana's Personal Stake

> **"What's your personal stake in this project? What are you planning for beyond this project — are you positioning for a larger role, or is this about solving a specific operational pain?"**

**What I'm trying to elicit**: The stakeholder's motivation and long-term vision

**Why it would change my design**:
- If operational → focus on efficiency gains
- If strategic → may need to consider scalability
- Affects the agent's success metrics and KPIs

**Evidence from artefacts**: Scenario brief — "what is she planning for beyond this project?"

---

### Question 4.2: Fear About AI-Driven Approach

> **"What do you fear about an AI-driven approach? What's the worst-case scenario that keeps you up at night?"**

**What I'm trying to elicit**: The stakeholder's risk concerns

**Why it would change my design**:
- If HIPAA breach → need stronger compliance controls
- If patient safety → need clinical review layer
- If staff replacement → need to frame as augmentation
- Defines the agent's failure mode priorities

**Evidence from artefacts**: Scenario brief — "what does she fear about an AI-driven approach?"

---

### Question 4.3: Previous Automation Attempts

> **"What automation has been tried at the practice before, and what happened? What worked, what didn't, and why?"**

**What I'm trying to elicit**: Lessons learned from prior automation attempts

**Why it would change my design**:
- If previous attempts failed → understand why to avoid repeat
- If previous attempts succeeded → understand what to build on
- Reduces risk of failed implementation

**Evidence from artefacts**: Not explicitly in artefacts — must elicit

---

## Summary: Questions by Category

| Category | Questions | Primary Design Impact |
|----------|-----------|----------------------|
| System & Data Gaps | 1.1, 1.2 | Integration requirements, data freshness |
| Process & Practice | 2.1, 2.2, 2.3 | Exception handling, input handling |
| Risk & Compliance | 3.1, 3.2, 3.3 | Agent boundaries, failure modes |
| Stakeholder Concerns | 4.1, 4.2, 4.3 | Success metrics, risk mitigation |

---

## Questions NOT to Ask (Generic)

| Generic Question | Why Not |
|-----------------|---------|
| "Walk me through your process" | Too broad; answerable from brief |
| "What are your pain points?" | Vague; people revert to standard complaints |
| "Tell me about your current system" | Feature tour, not work patterns |
| "What tasks would you automate?" | Leads to feature requests, not cognitive work |

---

## Assumptions

| Assumption | Confidence | Evidence |
|------------|------------|----------|
| Legacy billing system exists but is not named | High | Scenario brief mentions it |
| athenahealth ticker exists but isn't used | Medium | Artefact 5.2 shows front desk didn't flag |
| Insurer-specific patterns exist beyond Wellpath | Medium | Artefact 5.1 shows UHC and Humana patterns |
| HIPAA constraints are well-defined | Medium | Scenario brief states compliance is non-negotiable |