# Problem Statement & Success Metrics

## Problem Statement

The clinic operates a high-volume intake workflow without a reliable mechanism to ensure all required administrative checks are completed before the visit.

As a result:
- intake defects are discovered during the visit
- physicians are interrupted by administrative issues
- staff must perform reactive rework

This creates operational inefficiency and workflow disruption.

## Context

- ~180 patients per day  
- 4 front-desk staff  
- ~45 patients per staff member  
- multiple intake steps per patient  

## Design Goal

Ensure intake completeness before the visit while reducing manual administrative effort.

## Success Metrics

### Baseline (Industry-Informed Estimate)

Based on healthcare administration benchmarks and the described manual workflow:

- Manual intake error rates in similar settings range between **5–15%**
- Missing or incomplete intake data is commonly observed in **~8–20% of visits**

For this clinic, we assume:
- ~8–10% of visits have intake defects discovered during the visit  
  (e.g. missing prior auth, unreviewed medication changes)

Contributing factors:
- manual verification steps
- high workload (~45 patients per staff member per day)
- lack of structured validation workflow

---

### Target Outcomes

Based on typical improvements from structured workflow automation:

- Reduce intake defects discovered during visit:  
  → from ~8–10% → **<2%**

- Increase pre-visit intake completeness:  
  → from ~90–92% → **>98%**

- Reduce manual rework by front desk:  
  → estimated **20–30% reduction**

---

### Expected Impact

Reducing intake defects from ~10% to <2% could eliminate approximately **10–15 disrupted visits per day** across the clinic.

---

### Leading Indicators (Operational)

- % of visits reaching READY_FOR_REVIEW before appointment
- % of tasks auto-completed vs escalated
- % of BLOCKED cases (system/data issues)
- average time to resolve escalations

---

### Assumptions & Notes

- Baseline metrics are derived from industry benchmarks for manual administrative workflows
- Actual values should be validated with clinic-specific data
- Targets assume conservative, deterministic automation with human escalation