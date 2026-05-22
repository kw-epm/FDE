# ATX Terminology Explained — With Examples from Westbridge

This document explains the key ATX terms using concrete examples from the Cognitive Load Map.

---

## 1. Job to be Done (JtD)

**Definition**: A **cognitive contract** between an actor and an outcome. It's NOT a task — it's the *purpose* the actor is trying to achieve.

### Example from Work Stream 1 (Insurance Verification)

| JtD | What It Means |
|-----|---------------|
| **1.1: Verify Patient Insurance Eligibility** | The front-desk staff's job is to *confirm the patient has valid insurance coverage* before the visit. This is the outcome they need to achieve. |
| **1.2: Resolve Insurance Verification Failures** | When verification fails, the job becomes *getting the patient's insurance corrected so the visit can proceed*. |

**Why it matters**: A task is "check insurance" — a JtD is "ensure the patient can be billed correctly." The JtD defines the *goal*, not the *activity*.

---

## 2. Micro-tasks

**Definition**: The individual steps needed to complete a JtD. These are the *atomic actions* someone performs.

### Example from JtD 1.1 (Verify Patient Insurance Eligibility)

| Micro-task | What It Is |
|------------|------------|
| Retrieve patient demographics from athenahealth | Go to EHR, find patient record |
| Query Availity for insurance eligibility | Call the eligibility API |
| Interpret eligibility response (active/inactive/partial) | Read the API response, decide what it means |
| Handle verification failures (~30% of cases) | Do something when it doesn't work |
| Update patient record with verification status | Write the result back to the system |

**Why it matters**: Each micro-task can be evaluated for delegation suitability. Some are fully automatable, others need human judgment.

---

## 3. Cognitive Zones

**Definition**: **Clusters of similar cognitive activity** — groups of micro-tasks that require the same type of thinking.

### Example from Insurance Verification

| Cognitive Zone | What It Means | Micro-tasks in This Zone |
|----------------|---------------|-------------------------|
| **Data Retrieval** | Fetching information from systems | Retrieve demographics, query eligibility |
| **Decision** | Making a choice or classification | Interpret response |
| **Diagnosis** | Figuring out *why* something went wrong | Identify failure reason |
| **Resolution** | Fixing a problem | Contact patient, resubmit |
| **Documentation** | Recording the outcome | Update record, document resolution |

### Why Cognitive Zones Matter

Different zones have different characteristics:

| Zone | Typical Cognitive Load | Automation Difficulty |
|------|------------------------|----------------------|
| Data Retrieval | Low | Easy — just API calls |
| Decision | Medium | Moderate — rules can help |
| Diagnosis | High | Hard — requires judgment |
| Resolution | High | Hard — requires human interaction |
| Documentation | Low | Easy — write to system |

---

## 4. Breakpoints

**Definition**: **Points where control must be handed off** — moments when the work transitions from one actor (or system) to another.

### Types of Breakpoints

| Type | Meaning | Example from Map |
|------|---------|------------------|
| **System → Human** | Computer can't decide, needs human | Verification failure → human needs to intervene |
| **Human → System** | Human done, system takes over | Human contacts patient → system resubmits |
| **Human → Human** | One person hands to another | Front desk → billing for help |
| **System → System** | One system to another (automated) | athenahealth → Availity API call |

### Example Breakpoints from the Map

| Breakpoint | From | To | Trigger |
|------------|------|-----|---------|
| Verification failure | System | Human | Availity returns failure code |
| Data mismatch | System | Human | Patient info doesn't match insurer |
| Manual retry needed | Human | System | Staff resubmits after patient contact |

---

## Putting It All Together: An Example Walkthrough

### Work Stream: Insurance Verification

**JtD 1.1: Verify Patient Insurance Eligibility**

```
Micro-task 1: Retrieve patient demographics from athenahealth
  → Cognitive Zone: Data Retrieval
  → Breakpoint: System → System (automated API call)

Micro-task 2: Query Availity for insurance eligibility  
  → Cognitive Zone: Data Retrieval
  → Breakpoint: System → System (automated API call)

Micro-task 3: Interpret eligibility response (active/inactive/partial)
  → Cognitive Zone: Decision
  → Breakpoint: System → Human (needs classification decision)

Micro-task 4: Handle verification failures (~30% of cases)
  → Cognitive Zone: Diagnosis
  → Breakpoint: System → Human (needs human judgment)

Micro-task 5: Update patient record with verification status
  → Cognitive Zone: Documentation
  → Breakpoint: Human → System (write back to EHR)
```

### What This Tells Us

1. **Most is automatable** (micro-tasks 1, 2, 5) — data retrieval and documentation are routine
2. **Some needs human** (micro-tasks 3, 4) — interpretation and failure handling require judgment
3. **Breakpoints show handoff points** — where we need to design escalation paths

---

## Summary Table

| Term | Definition | Example |
|------|------------|---------|
| **Job to be Done (JtD)** | The outcome the actor is trying to achieve | "Verify patient insurance eligibility" |
| **Micro-task** | Individual steps to complete the JtD | "Query Availity for eligibility" |
| **Cognitive Zone** | Group of similar cognitive activity | "Data Retrieval" — all fetching tasks |
| **Breakpoint** | Point where control transfers | "System → Human" when verification fails |

---

## Why This Matters for Delegation

| Cognitive Zone | Delegation Implication |
|----------------|----------------------|
| Data Retrieval | Can be fully automated |
| Decision | May be automatable with rules |
| Diagnosis | Needs human or agent with oversight |
| Resolution | Needs human |
| Documentation | Can be fully automated |

The Cognitive Load Map shows us *where* to place the delegation boundaries — not everything should be fully agentic, and the zones help us identify where human judgment is needed.

---

## How the Terms Feed Into Other Deliverables

| ATX Term | Used In | How |
|----------|---------|-----|
| **JtD** | Delegation Suitability Matrix | Each task cluster maps to a JtD |
| **Micro-task** | Delegation Suitability Matrix | Each row in the matrix is a micro-task cluster |
| **Cognitive Zone** | Volume × Value Analysis | Zones with high "Diagnosis" and "Resolution" drive non-determinism scores |
| **Breakpoint** | Agent Purpose Document (Autonomy Matrix) | Each System→Human breakpoint becomes an escalation trigger |

### Example: How Breakpoints Become Escalation Triggers

From the Cognitive Load Map, the Medication Reconciliation work stream has this breakpoint:

> *Critical interaction → System → Human (Severity = critical)*

In the Agent Purpose Document (Section 8), this becomes:

> *Escalate to Dana + Clinical Lead immediately; block visit scheduling*

The terminology forms a chain: **JtDs → Micro-tasks → Cognitive Zones → Breakpoints → Autonomy Matrix → Escalation Triggers**.