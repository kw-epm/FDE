# D#4b Capability Spec: Urgent Re-matching

*Source domain: MedFlex Healthcare Staffing. Sibling spec: `04a-capability-spec-planned-matching.md` (shares entities and state machine, defined there; this spec inherits and adds).*

## 1. Capability overview

When a nurse no-shows or cancels late, the agent fires a compressed re-match flow: same engine as planned matching, but with a shorter Decision 2 window, a narrower candidate pool (currently-available nurses only), and a more forgiving confidence threshold for autonomous action. The architectural argument: hospital review remains the safety net in both modes; the alternative to fast urgent action is an unfilled shift, which is a known-bad outcome with measurable cost (hospital relationship hit, lost revenue, the discount Marcus admitted giving). Coordinator pre-review is skipped when time-to-shift is below the urgent SLA threshold; post-hoc audit is mandatory for those auto-sent cases.

## 2. Trigger and inputs

**Trigger:** one of two events:
- Hospital reports nurse no-show at or before shift start (inbound, often by phone, captured by coordinator into ServiceNow)
- Nurse cancels confirmed shift < X hours before start (X is a D#4 tuning parameter; default 4h)

**Inputs:**
- Original ConfirmedFill record (per D#4a entity definitions)
- UrgentTrigger enum: `noShow` | `nurseLateCancel`
- TimeToShiftStart: remaining minutes/hours
- (Inherits) full historical context as in D#4a

## 3. Shared entities (uses D#4a glossary)

All entities (ShiftRequest, CandidateShortlist, NurseOffer, NurseAcceptance, HospitalSubmission, HospitalAcceptance, ConfirmedFill, LockState) defined in **D#4a §3** and shared.

**D#4b adds:**

| Entity | Definition | Key fields |
|---|---|---|
| **UrgentTrigger** | enum: `noShow` \| `nurseLateCancel` | type, triggered_at, source (hospital/nurse) |
| **TimeToShiftStart** | Minutes remaining before original shift start | minutes_remaining |
| **OriginalFill** | Reference to the ConfirmedFill that triggered urgent re-match | confirmed_fill_id, cancellation_reason |
| **UrgentSubmission** | Hospital submission that includes context (the re-match story) | extends HospitalSubmission; adds: context_message, original_fill_ref |
| **UrgentSLA** | Time budget for urgent re-match resolution, committed in D#3 urgent autonomy defence | resolution_target_minutes (default: 30 when time-to-shift < 2h), coordinator_response_target_minutes (default: 15), hard_cap_partial_commitment (default: 2h) |

**State machine:** same four-state lock as D#4a, with shorter windows (see §4 below).

## 4. Process steps (compressed vs D#4a)

| # | Step | Pre-condition | Action | Post-condition | Notes (urgent vs planned) |
|---|---|---|---|---|---|
| 1 | Mark OriginalFill as cancelled | UrgentTrigger received | Update audit trail with cancellation reason, time-to-shift | OriginalFill flagged | (No-show or late-cancel; same path) |
| 2 | Compressed eligibility filter | Filtered pool needed | Rules: currently-available nurses (last-known-online within last 30 min) + tighter geo radius + standard HR rules | Pool of currently-reachable candidates | Narrower than planned mode |
| 3 | Compliance precondition | Pool | Read credential expiry vs shift date | Pool with valid-credential nurses only | Same as D#4a |
| 4 | Contextual reasoning under time pressure | Filtered pool + TimeToShiftStart | LLM ranks with time-to-shift as an explicit signal: lean toward known-reliable over credential-leader | Ranked shortlist + reasoning | Time-to-shift signal explicit; fatigue inference applies |
| 5 | Confidence scoring | Ranked shortlist | Same definition (D#4a §5) | Confidence label | Same |
| 6 | Confidence gate × urgent threshold | Confidence + time-to-shift | High confidence + time-to-shift < urgent SLA (default 30 min): auto-send, skip coordinator pre-review. Otherwise: flag to coordinator | Decision: auto / flag | More forgiving threshold than planned mode |
| 7 | Coordinator pre-review (when not auto-sent) | Flagged shortlist | Same as D#4a §7 | Approved candidate | Skipped when time-to-shift critical |
| 8 | Soft-lock fires | Approved candidate | Lock state machine starts with shorter window (~30 min urgent) | Candidate locked | Tighter window than planned mode |
| 9 | NurseOffer sent (urgent-priority) | Locked candidate | SMS first, email second; Decision 2 window starts (~30 min urgent) | Offer in flight | Channel order tuned for urgency |
| 10 | NurseAcceptance waits (~30 min urgent) | Offer in flight | Listen for explicit yes/no within window | Acceptance OR timeout | Shorter window than D#4a |
| 11 | UrgentSubmission to hospital with context | Nurse accepted | Submit with "re-match for shift X originally filled by Nurse N who cancelled at Y due to Z" context message | UrgentSubmission record | Different template from D#4a's initial submission |
| 12 | HospitalAcceptance | Submission in flight | Hospital confirms or rejects | Acceptance | Same flow as D#4a |
| 13 | ConfirmedFill (urgent) | Both sides accepted | Lock state → Confirmed. Flagged in audit for no-show driver analysis. | ConfirmedFill record | Flagged for analytics |
| 14 | Coordinator post-hoc audit (when step 7 was skipped) | Auto-sent decision | Coordinator reviews the decision and reasoning within 1h of the offer | Audit complete or override action | New step vs D#4a; required for skipped pre-review |

## 5. Confidence threshold tuning (urgent vs planned)

Same confidence definition as D#4a §5. Urgent mode uses a more forgiving auto-action threshold:

- **High confidence:** auto-send (skipping coordinator pre-review, even in weeks 1–2 of ranker operation, if time-to-shift is below the urgent SLA threshold)
- **Medium confidence:** auto-send only if time-to-shift is critical (< urgent SLA) AND coordinator is unreachable; flag to coordinator queue otherwise
- **Low confidence:** coordinator decides (same as planned)

Rationale defended in D#3 "Why urgent re-matching gets a different threshold." Hospital review remains the safety net for all submissions; what changes between modes is coordinator pre-review, not hospital review.

## 6. AI-native decision point (urgent-mode specific)

**Worked example.** Hospital reports a nurse no-show at 6:55 AM for a 7 AM ICU shift. Five minutes to fill, fatigue-and-reliability inference under time pressure.

A rules engine produces a list of currently-available ICU nurses within geo radius. End of analysis.

The agent reasons further:

1. **Reliability under pressure.** Of the 3 available candidates, Nurse P has 100% on-time-arrival history at Hospital A across 8 prior shifts; Nurse Q has 90% (one prior late arrival); Nurse R has only one prior shift at this hospital. At 5 min lead time, reliability beats marginal credential gain.
2. **Fatigue signal.** Nurse R worked a 14h shift ending at midnight. Even though they're "currently available" on paper, fatigue likely affects performance. Agent surfaces this as a soft de-rank with reasoning citation, allowing coordinator override.
3. **Proximity-vs-reliability tradeoff.** Nurse R is 5 min away; Nurse P is 10 min away. At 5 min lead time, distance matters more than usual. But the fatigue + reliability gap tips the decision toward Nurse P despite the proximity disadvantage.

**Result:** top pick is Nurse P (Hospital A history, no fatigue signal, 10 min away). Nurse Q is the second pick (still reliable, 7 min away). Nurse R is third (closer but fatigued and unfamiliar with Hospital A). A rules engine would have ranked these in a different order, almost certainly prioritising Nurse R (closest, "currently available" in the binary sense).

The agent's reasoning is shown alongside the recommendation, so the coordinator on post-hoc audit can validate the trade-off. *This is the urgent-mode AI-native moment: fatigue and reliability inference under time pressure, with reasoning visible.*

## 7. Integration contracts

Same as D#4a §7, plus:

| Integration | Direction | Purpose | Failure handling |
|---|---|---|---|
| **Priority queue (urgent re-match)** | internal | Urgent triggers jump ahead of standard shift requests in the agent's processing queue | Concurrency cap to prevent cascade overload |
| **Hospital re-submission template** | outbound | Different from D#4a; includes context message ("re-match for shift X, original nurse cancelled at Y due to Z") | Standard retry path |
| **Coordinator post-hoc audit dashboard** | outbound | For auto-sent cases that skipped pre-review, surfaces the decision within 1h | If audit dashboard unavailable, fall back to email alert |
| **No-show driver tagging** | internal | UrgentTrigger type captured in the new ConfirmedFill audit trail for analytics (Decision 2's structural-vs-addressable split) | Required for ongoing validation |

## 8. Worked examples / edge cases (urgent-specific)

| # | Scenario | Agent behaviour |
|---|---|---|
| 1 | **Nurse calls in sick at 5 AM for 7 AM shift** | Autonomous re-match (urgent + high confidence). Coordinator alerted at 6 AM for post-hoc audit. |
| 2 | **Hospital reports no-show at shift start** | Urgent re-match + apology context in submission ("we're reaching out with a replacement candidate within X minutes"). |
| 3 | **No replacement candidate available** in eligible pool | Exception path. Agent surfaces nearest-fit alternatives with explicit credential gaps named. Coordinator-only routing for the decision. |
| 4 | **Multiple urgent re-matches stacking** (same time window) | Priority queue. Agent processes sequentially. Concurrency cap (e.g., 5 urgent in flight at once) to prevent cascade overload. Excess re-matches queue with FIFO ordering. |
| 5 | **Original nurse calls back during re-match window** ("misunderstanding, I'm coming") | Race condition. Agent surfaces both options to coordinator immediately: original nurse vs replacement candidate. Coordinator decides which to honor (relationship management decision). |
| 6 | **Urgent re-match itself produces a no-show downstream** (replacement also doesn't show) | Second-order urgent re-match. Rate-limit: if a single shift triggers >2 urgent re-matches, escalate to coordinator-only routing for that shift (avoid cascade). |
| 7 | **Decision 2 alternative path is active** (no-reply finding wrong; see D#3 Decision 2 §Alternatives) | Use same-day re-check ping pattern: 12h before the urgent shift, ping the replacement nurse. Confirmation tracked, but no hard "explicit yes" gate. |
| 8 | **Coordinator post-hoc audit reveals a bad auto-send** | Coordinator overrides with a different candidate (sends a corrected submission to the hospital, who can choose). Bad-decision pattern captured for confidence-threshold tuning. |

## 9. Marked assumptions (inherited from D#4a + urgent-specific)

> Reference D#4a §9 for shared assumptions A1–A10. D#4b adds:

| # | Assumption | Confidence | Source / risk |
|---|---|---|---|
| U1 | Coordinator may not be available within urgent SLA (no overnight staffing data) | **Medium** | Per D#3 urgent autonomy defence; open question for Head of Ops Monday |
| U2 | Hospital will accept urgent re-submission within the urgent window | **Medium** | Reasonable for staffing crises; not measured today |
| U3 | Currently-available nurse pool is large enough for urgent re-match at scale | **Low** | Depends on slice + nurse pool density; validate in D#7 |
| U4 | Re-match cascade rate is bounded (urgent re-matches don't trigger more urgent re-matches at unsustainable rate) | **Low** | Rate-limit applied at edge case #6; monitor in D#7 |
| U5 | Post-hoc audit by coordinator happens within 1h of auto-sent decision | **Medium** | Operational discipline question; depends on coordinator workload |
| U6 | "Currently available" signal (last-known-online within 30 min) is reliable | **Low** | Depends on nurse app last-seen tracking; unconfirmed in MedFlex |

---

### Revisions added AFTER the D#9 buildability test ran

> **Transparency note (per pack §9 protocol: "flag it as a revision"):** the assumption below (U7) was added to this spec **AFTER** D#9 ran on the D#4a sibling. D#4b was not the spec CC built from, but it inherits A11 and A12 from D#4a §9 (added as revisions there) and adds urgent-specific precision gaps below. The values remain deferred; only the flag is new.

| # | Assumption | Status | Source / risk |
|---|---|---|---|
| U7 | **Urgent-mode precision parameters deliberately left as parameters in v1 spec.** Inherits A11 / A12 from D#4a §9 (revisions added post-D#9). Urgent-specific items: (a) post-hoc audit timing of 1 h (§4 step 14, §7) is hard-coded; should be parameter. (b) Cascade rate-limit threshold of ">2 urgent re-matches per shift triggers escalation" (§8 edge case 6) is hard-coded; should be parameter. (c) "Currently available" signal (last-known-online within 30 min in §4 step 2) needs explicit definition contract with nurse-app team. (d) Tighter geo radius for urgent eligibility (§4 step 2) is referenced but not numerically pinned. (e) Priority-queue concurrency cap of "e.g., 5 urgent in flight at once" (§7) is illustrative, not pinned. | **Flagged (post-D#9 self-audit)** | Added after self-audit against the production-spec checklist (separately from D#9). Items deferred deliberately for v1 prototype phase; closure during integration-design phase (engagement week 0–1). |

## 10. Validation hooks (cross-reference D#7)

| Metric | Target | Trigger |
|---|---|---|
| **Primary urgent KPI** (time from urgent trigger to hospital re-submission) | ≤30 min (urgent mode SLA) | Pause and investigate if breached for >2 weeks |
| **Hospital acceptance rate on urgent submissions** | Tracked separately from planned-mode acceptance rate (expect slightly lower; quantify after 4 weeks) | Diagnostic, not primary trigger |
| **Cascade signal** (rate at which urgent re-matches themselves produce no-shows) | <5% of urgent re-matches trigger second-order urgents | Pause cascade auto-routing if breached |
| **Coordinator post-hoc audit rate** | 100% of auto-sent urgent cases reviewed within 1h | Operational metric; track compliance |
| **Auto-send override rate (post-hoc)** | <15% of auto-sent decisions are overridden in audit | If higher, tune urgent confidence threshold up |

Full pause/rollback in D#1, D#3, D#7.

---

## Cross-spec consistency check (D#4a ↔ D#4b)

**Shared and aligned:**
- ✅ Same canonical entities (defined in D#4a §3, inherited here)
- ✅ Same four-state lock machine (D#3 Decision 3)
- ✅ Same Decision 2 explicit-yes mechanism (conditional, with windows: ~90 min planned, ~30 min urgent)
- ✅ Same AI-native principle (reason over context, not learn from labels)
- ✅ Same confidence definition (D#4a §5)
- ✅ Same compliance handoff pattern
- ✅ Same pause/rollback triggers (D#1 + D#3 + D#7)

**Workflow-specific differences (intended):**
- ⚠️ Decision 2 window: 90 min planned / 30 min urgent
- ⚠️ Confidence threshold for auto-action: stricter in planned, more forgiving in urgent (defended in D#3)
- ⚠️ Coordinator pre-review: present in planned (weeks 1–2 of ranker), optionally skipped in urgent when time-to-shift < SLA, replaced by post-hoc audit
- ⚠️ Hospital submission template: standard for D#4a, "re-match with context" for D#4b
- ⚠️ Eligibility pool: full pool in planned, "currently available" subset in urgent
- ⚠️ Process step count: 13 in D#4a, 14 in D#4b (extra step for post-hoc audit)
