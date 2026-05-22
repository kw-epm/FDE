# D#7 Validation Plan

*MedFlex Healthcare Staffing | Validation strategy for the planned matching + urgent re-matching capabilities. Cross-references D#1 success metrics, D#3 edge cases and data assumptions, D#4a/b validation hooks.*

## 1. How we validate, in plain terms

Two layers, both running all the time once we ship.

**Before we build anything risky (week 0–1):** we check the things that decide whether to ship at all. Does the data the agent needs actually exist? Does the parser actually get the right fields out of real emails? Are the agent's confidence labels honest, or does it call "high" what coordinators would have overridden?

**Once it's live, every week:** we read the same metrics that gate the trust ramp in D#3, and pause or roll back if any one of them trips. The point isn't to test once and forget. The point is to make every assumption visible enough that we notice when it's wrong, before it becomes a hospital phone call.

## 2. Pre-launch validation (week 0–1)

### 2.1 Data go/no-go audit (week 1, **before any ranking/autonomy build**)

Per D#3 data assumptions section: the architecture rests on at least one high-signal contextual source (hospital acceptance/rejection records OR past hospital-nurse pairings) being usable. The audit answers this question with a yes/no by Friday of week 1.

**Important sequencing note:** the audit runs in parallel with the week-1 parser ship (D#6 commitment, coordinators see the parser working on real ServiceNow records by end of week 1). The audit gates only the *ranker / autonomous ranking* work that starts week 2. Parsing free-text shift requests doesn't depend on contextual data sources; ranking does. So week 1 is parser live + audit, not "audit blocks everything." If the audit says no-go, we still ship a working parser and pause before building the ranker layer.

**What we audit:**
- Hospital accept/reject records: present, structured, queryable? Sample volume?
- Past hospital-nurse pairings: present, queryable? Coverage over which time window?
- Coordinator notes (free text): present in any system? Volume?
- Formal hospital preference profiles: present, structured? (Expected to be absent; Marcus said no industry standard exists.)
- Nurse credential expiry dates: present, current? (Critical. Without this, the agent cannot enforce eligibility.)

**Output:** a one-page audit report with go/no-go signal per D#3's gate. If neither high-signal source is usable, **we pause the engagement and rescope before building.**

### 2.2 Spec-consistency check

Verify that D#4 entities (ShiftRequest, NurseOffer, etc.) map to real fields in MedFlex's ServiceNow + nurse database. Any missing mapping is a buildability blocker. Surface it before week 2 development starts.

### 2.3 Check the parser is actually right (week 1)

Take 50 to 100 real shift requests from the last few months. Have someone read them by hand and write down what they mean (specialty, dates, location, credentials needed). Then run the parser on the same emails. Compare.

Pass bar:
- The parser gets the hard fields right at least 95% of the time (specialty, dates, location, credentials)
- It doesn't invent soft signals (preferences, urgency tags) more than 5% of the time
- Every field it pulled out can be traced back to actual words in the email, no hallucinated fields

If the parser doesn't clear the bar, the spec needs another pass before we deploy. The parser is the foundation; if it's wrong, everything downstream is wrong.

### 2.4 Check the agent's confidence is honest (week 1)

For the same 50 to 100 cases, look at what confidence label the agent gives each decision (high / medium / low). Then look at what coordinators historically did with similar cases. If "high confidence" matches "coordinator approved without changing anything," confidence is calibrated. If "high confidence" gets overridden 40% of the time in the historical data, the threshold is too loose and needs tightening before any coordinator sees the agent live.

## 3. Ongoing accuracy validation (production)

### 3.1 Extraction accuracy (weekly)

Random sample of 20 parsed requests per week, manually verified. Tracks parser drift over time. Alert if accuracy falls below 90%.

### 3.2 Ranking quality (weekly)

Tracked via **first-pick acceptance rate** (D#1 metric, target ≥75%). Decomposes the agent's "did the right pick get picked?" question. Pause trigger: <60% sustained 2 weeks. Roll-back: <50% sustained 2 weeks.

### 3.3 Confidence calibration (continuous)

For every coordinator decision logged with the agent's confidence label, track:
- High-confidence cases approved without override: should be ≥95%
- Medium-confidence cases approved without modification: 60–80% expected
- Low-confidence cases that needed coordinator intervention: 100% by design

Drift signals threshold-tuning need.

### 3.4 Reasoning citation accuracy (random sample)

Per D#3 anti-hallucination measure: every claim in the agent's reasoning links to a specific data source. Validation: weekly sample of 10 decisions, verify each citation actually points to the data claimed. Catches hallucinated reasoning before it propagates.

## 4. Pause / rollback triggers (mirrored from D#1)

The exact same triggers as D#1, repeated here so the validation plan is readable on its own. Owners and the "what happens when it trips" line are the D#7-specific additions.

| Metric | Pause | Roll back |
|---|---|---|
| Primary KPI (request → hospital submission) | Worse than baseline at week 3 | Worse at week 4 |
| First-pick acceptance | <60% sustained 2 weeks (target at risk) | <50% sustained 2 weeks (Decision 1 quality failing) |
| Hospital accept rate | >10% drop WoW | >20% drop or below baseline 2 weeks |
| Override rate | >50% by week 4 | >70% sustained 2 weeks |
| Per-offer nurse response | Median >70 min planned / >22 min urgent | Median ≥90 min planned / ≥30 min urgent (response distribution saturating the window) |
| No-show (after explicit-yes is live, or after channel-improvement rollout if Decision 2 alternative path applies) | Worse than baseline at week 4 | 5+ points worse |
| Mismatch (guardrail) | >7% on slice 2 weeks | >10% on slice |
| Submission withdrawal rate | >5% on slice | >10% or rising 2 weeks |

**Owner of each metric:** designated coordinator-lead per metric; weekly review with engagement lead. **Trigger fires → defined response runs within 1 working day** (not "we'll think about it next sprint").

## 5. Edge cases, coverage matrix (cross-ref D#3)

Reference D#3 edge cases section for the full catalogue. D#7 confirms which edge cases have validation hooks vs. which are accepted-risk:

| Edge case category (from D#3) | Validation approach |
|---|---|
| Race conditions inside the lock (late acceptance, withdrawal, mid-flow changes) | D#4 state-machine unit tests + lock-state-store integration tests |
| Cross-system failures (agent crash, ServiceNow outage, LLM outage) | Chaos/failure-injection tests in pre-launch; runbooks for production |
| LLM-specific failure modes (hallucination, prompt injection) | Two-stage extraction + citation validation + sample audits |
| Compliance edge cases (credential lag, regulatory drift) | Reverse-direction handoff (compliance team update → agent re-evaluates eligibility) |
| What architecture cannot fix (override stays high, data absent, plug pulled) | Detected by D#1 metrics; response = narrow / pause / shutdown gracefully |

## 6. Specifically named failure modes (rate limits, regulatory drift, model drift, SPOFs)

### 6.1 Portal rate limits

**Risk:** ServiceNow API enforces request rate caps; LLM provider enforces token-rate caps. At scale, agent could hit limits and silently degrade.

**Mitigation:**
- Queue requests internally; never drop a shift request
- Retry with exponential backoff on rate-limit errors
- Circuit-breaker pattern: if 20% of requests in 5-min window get rate-limited, fall back to coordinator-only routing for the duration
- Monitor: rate-limit-hit rate as a weekly metric

**Open question for Head of Ops / IT lead:** confirm ServiceNow API tier and current rate limits. Likely fine at v1 slice volume (~15 fills/day per the slice criteria in D#2); manageable at current full-MedFlex volume (~184 fills/day under the net-revenue interpretation, per D#1 §Year-1); becomes a real risk at the ~13,500/day target.

### 6.2 Regulatory drift

**Risk:** State-level credential rules change (a state mandates a new certification, an existing one becomes optional, etc.). Agent applies stale rules and either rejects valid candidates or accepts invalid ones.

**Mitigation:**
- Credential rules stored as configurable parameters, not hardcoded in the agent
- Compliance team reviews eligibility rules quarterly (or more often if a state announces a change)
- The agent shows the rule it applied in its reasoning citations, so coordinators can spot a "this rule looks wrong" case on a specific decision
- Open question for compliance lead: cadence at which the compliance team re-checks state-by-state rules

### 6.3 Model accuracy drift

**Risk:** LLM model upgrades (provider releases a new version) may change extraction quality, reasoning behaviour, or citation accuracy. Silent regression in production.

**Mitigation:**
- Pin to specific model version in production
- Pre-launch extraction-accuracy benchmark (§2.3) re-runs before any model upgrade
- Confidence calibration baseline re-runs before any model upgrade
- Rollback criterion: if extraction accuracy drops ≥3pp on the benchmark, revert to previous model version

### 6.4 Single points of failure

**Risk inventory:**

| SPOF | Impact | Mitigation |
|---|---|---|
| LLM provider outage | Agent can't extract or reason | Fall back to coordinator-only routing for the duration; queue requests; alert ops |
| ServiceNow outage | Agent can't read inbound or write outbound | Buffer locally, retry; coordinator-only operates from email until restored |
| Nurse database outage | Eligibility filter blind | Agent rejects all candidates safely (better than wrong-credentialed nurse to hospital); coordinator surfaces from memory until restored |
| Lock-state data store outage | Race-condition protection lost | Agent halts new offers until store recovers; existing in-flight offers continue per last-known state |
| Coordinator dashboard outage | Coordinator can't review agent decisions | Agent reverts to low-autonomy mode (all decisions queued for review when dashboard returns) |
| Single coordinator out (sick, leave) | Slice's calibration signal degraded | Cross-train at least 2 coordinators on the slice; not 1 |

## 7. Compliance and regulatory validation

### 7.1 Credential gate hold (hard requirement)

Validation: regression suite that asserts the agent *cannot* generate an offer for a nurse with an expired credential. Test cases (covering the four boundary conditions):
- Nurse credential expired before shift start → must reject
- Nurse credential expires *during* the shift → must reject
- Nurse credential expires after shift end → must accept
- Nurse credential renewal in flight → defer to compliance handoff

This regression suite runs on every architecture change. Cannot be skipped.

### 7.2 Audit trail completeness

Per Decision 1: every agent decision persists (input email, extracted intent with citations, ranking context used, reasoning text with citations, decision, coordinator override if any, timestamp). Audit:
- Sample 10 decisions/week, verify all fields are populated and traceable
- Compliance team can request audit on any decision; turnaround <24h

### 7.3 Patient data handling (HIPAA)

This needs a legal answer before v1 ships, not a technical one. Three things to confirm with the compliance + legal teams in week 0:

1. **What data leaves MedFlex's environment** when the agent calls the LLM provider? Shift requests may mention patient context ("pediatric patient with rare medication allergy" in the worked example). If patient context counts as PHI under MedFlex's interpretation of HIPAA, the agent's prompts may need redaction before they go to the LLM provider.
2. **Where does the agent run?** Cloud, on-prem, hybrid. Affects data residency and the BAA (Business Associate Agreement) with the LLM provider.
3. **Audit trail location.** The audit trail (Decision 1 reasoning citations + everything else logged) needs to live in a system that meets HIPAA storage and access controls.

This is a regulatory blocker, not just an open question. Flag for week-0 escalation. If unanswered by start of week 1, the engagement pauses until resolved.

## 8. Production validation cadence

| Cadence | What | Owner |
|---|---|---|
| **Continuous** | Lock-state integrity, agent error rate, LLM provider health | Ops |
| **Daily** | Pause/rollback metric snapshot | Engagement lead |
| **Weekly** | Extraction accuracy sample, ranking quality (first-pick rate), citation accuracy sample, override rate trend | Engagement lead + coordinator-lead |
| **Monthly** | Mismatch rate audit, no-show driver analysis (split structural vs. addressable), regulatory-rule review | Compliance team + engagement lead |
| **Quarterly** | Full audit-trail sample review, model accuracy benchmark re-run, regulatory rules refresh | Compliance team + Ops + engagement lead |

## 9. Validation that the architecture's worst case is bounded (cross-ref D#3 "what arch can't fix")

The five failure scenarios where the architecture cannot save us:
1. Override rate stays high → response: narrow deployment to categories that work
2. Data assumptions break → response: go/no-go gate fires, pause and rescope
3. Marcus pulls the plug → response: slice is stand-alone, turn off safely
4. Hospital moves to a structured portal → response: coordinator-only for that hospital until portal integration
5. Insider misuse (rogue coordinator override pattern) → response: audit trail makes it visible after the fact; investigation is operational, not architectural. Detection is what §7.2 (audit-trail completeness) is for.

Each has a tracked metric and a defined operational response. Validation here is *that the response is genuinely available*, i.e., not just words on a page. Specifically:
- "Narrow deployment" requires segment-level metrics that distinguish high-override categories from low-override; instrument this in D#4 from day 1
- "Pause and rescope" requires Marcus to approve a rescope conversation; pre-agree the format in week 0
- "Turn off safely" requires the slice's tech debt to be quarantined from MedFlex's main workflow; D#3 architecture supports this; D#4 specs enforce it

## 10. Open validation questions

The things we don't yet know that affect validation. Each has an owner and a deadline.

| Question | Owner | Deadline |
|---|---|---|
| ServiceNow API rate limits (current tier) | IT lead | Week 0 |
| Coordinator availability across shifts (overnight, weekend) | Head of Ops | Week 0 |
| Compliance team audit cadence and tools | Compliance lead | Week 0 |
| HIPAA / patient data handling for LLM provider calls | Compliance + Legal | Week 0 (regulatory blocker) |
| Cross-state credential rule refresh frequency | Compliance | Week 1 |
| Baseline: hospital acceptance rate today | Engagement lead | Week 1 (must be in place before agent ships) |
| Baseline: actual no-show driver split (structural vs. addressable) | Engagement lead | Week 4 |
| What "$14M revenue" means in MedFlex's accounts (net agency revenue vs. gross billings) | CFO | Monday week 0 (per D#6) |
| Slice volume on chosen 2 hospitals | Head of Ops | Monday week 0 (per D#6) |
| Whether nurse profile notes contain queryable structured data | Head of Ops + IT | Week 1 (gates D#3 data assumption A5) |

---

## Cross-reference summary

This validation plan inherits, doesn't replace:
- **D#1**: success metrics + pause/rollback triggers (the WHAT)
- **D#3**: edge cases catalogue, data assumptions, architectural worst cases (the WHEN-things-break)
- **D#4a, D#4b**: validation hooks per capability (the WHERE-to-look)
- **D#5**: diagnostic move for build-loop signals (the HOW-to-classify when validation flags something)

D#7 ties them into one operational document: who validates what, when, with what threshold, and what happens when the threshold trips.
