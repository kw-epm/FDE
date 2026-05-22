# Deliverable 5 — Build-loop Response Memo (Cascade Public Libraries fixture)

**Author:** Tamas Kiss
**Engagement:** MedFlex agentic transformation (D5 cross-domain; Cascade fixture is Wednesday W3D3 exercise material)  
**Date:** 2026-05-13
**Gate:** Gate 3 — Final submission
**Source:** `program-materials/W3D3-BuildLoop-Exercise.md` — 8 signals across files, tests, and one builder question.

---

## Classification distribution

| Category | Signals |
|---|---|
| spec gap | 1, 7 |
| builder misread | 2, 5 |
| unjustified implementation choice | 3, 6 |
| test/environment issue | 4 |
| legitimate clarification request | 8 |

Three pairs across the eight signals. Read each signal carefully against the spec — surface impressions miss the second-order content.

---

### Signal 1 — 72-hour notification expiry window

**Classification:** spec gap

**Rationale (1 sentence with citation):** R3 specifies "72 hours" but does not define calendar vs business hours, timezone semantics, or sub-hour precision; the Assumptions section flags calendar-hours as a tentative answer ("calendar hours, but flagged for FDE review") — the builder defaulted to the assumption with `timedelta(hours=72)` and server-time `datetime.now()`, which is consistent with the assumption but underspecified.

**Response (2–4 sentences in the correct tone):**

I should have specified R3 more precisely. Updating R3 to say: *"A notified patron has 72 hours (calendar hours, measured from `notified_at` in the patron's registered timezone, with hourly polling latency tolerated) to claim the hold."* The Assumptions clause's calendar-hours interpretation is promoted to spec body; timezone semantics are new and address a real correctness gap that the current `datetime.now()` server-time usage glosses over. Your implementation aligns with the calendar-hours portion — please add timezone-adjusted comparison against `patron.timezone` and confirm the hourly polling cadence is acceptable for the SLA.

---

### Signal 2 — Accessibility priority implemented as queue weight

**Classification:** builder misread

**Rationale (1 sentence with citation):** R4 specifies "Accessibility-priority patrons jump to queue position 1 when they place a hold" — a positional jump, not a weight — but `accessibility_priority.py` implements it as a 0.25x weight (`PriorityWeights.ACCESSIBILITY = 0.25`), which produces incorrect ordering whenever an accessibility-priority patron is at any non-1 raw_position and also invents a multiplier value the spec never names.

**Response (2–4 sentences in the correct tone):**

R4 specifies a position-1 jump, not a weight — please change `accessibility_priority.py` so that on `place_hold(patron)` with `patron.has_accessibility_modifier == True`, the hold is inserted at queue position 1 (unless another accessibility-priority patron already holds position 1, in which case standard FIFO applies between them per R4 second clause). Remove the `PriorityWeights.ACCESSIBILITY = 0.25` constant; it doesn't correspond to anything in the spec. The Academic 0.5x weight in R5 is correctly a multiplier; only the accessibility rule is positional. Signal 8 also touches the R4/R5 intersection — handle Signal 8's resolution before re-implementing this so the two land together.

---

### Signal 3 — Auto-checkout adds a 3-day return reminder not in spec

**Classification:** unjustified implementation choice

**Rationale (1 sentence with citation):** R7 specifies the auto-checkout flow ("the system performs the loan automatically"), R10 specifies auto-return at the end of the 21-day loan period, and neither requires a 3-day-before-end return reminder — the `schedule_reminder` call in `auto_checkout_handler.py` is a feature addition the spec does not authorise.

**Response (2–4 sentences in the correct tone):**

Appreciate the thinking on retention, but the 3-day return reminder isn't in the spec — R7 + R10 cover the auto-checkout and auto-return flows without notifications between them. Please remove the `schedule_reminder` block unless we agree to add it explicitly. If you think it's worth keeping, file a spec change request and I'll evaluate the addition — it touches notification volume, channel costs, and the R12 channel-rule that we haven't fully resolved yet. Ship-by-default features without a corresponding spec line are noise we can't validate against intent.

---

### Signal 4 — Test fixture date-bound to Q4 2025

**Classification:** test/environment issue

**Rationale (1 sentence with citation):** The fixture `overdrive_refresh_2025_q4.json` encodes `expected_advances` as queue state at fixture-creation time; the implementation `on_overdrive_catalog_refresh` advances by `count` per title (consistent with R8), but the test fails in 2026 because the queue state has drifted since the fixture was captured.

**Response (2–4 sentences in the correct tone):**

The test is date-bound to 2025 fixture data — the implementation looks correct per R8 ("advance the queue by the number of new copies"); the assertion against `fixture_refresh.expected_advances` is what fails. Two fixes: either regenerate the fixture for the current quarter (mechanical refresh — easy short-term) or refactor the test to mock the catalog state explicitly (build the queue state inline rather than loading a date-bound fixture). I'd prefer the refactor — embedded state expectations in fixtures are a recurring source of date-drift test failures and the maintenance burden compounds. Either way, the production code doesn't need a change.

---

### Signal 5 — Duplicate-hold rejection ignores format

**Classification:** builder misread

**Rationale (1 sentence with citation):** R11 specifies "Format-distinct holds: if a patron places holds on the ebook and audiobook editions of the same title, the system treats them as two separate holds" — but the duplicate-detection check `patron_has_active_hold_on_title(patron, title_id)` in `place_hold.py` ignores `format_type` and would incorrectly raise `DuplicateHoldError` when a patron places an audiobook hold on a title where they already hold the ebook.

**Response (2–4 sentences in the correct tone):**

R11 explicitly distinguishes ebook and audiobook holds on the same title as separate — the check `patron_has_active_hold_on_title(patron, title_id)` collapses them by ignoring `format_type`. Please change to `patron_has_active_hold_on(patron, title_id, format_type)` so format-distinct holds correctly pass the duplicate check. The active-hold *limit* (R9: 5 standard / 10 academic) still counts both formats toward the cap per R11 ("Both count toward the active-hold limit") — that part of the implementation is correct; only the duplicate check needs the format dimension added.

---

### Signal 6 — Paused patrons sent a "we skipped you" email

**Classification:** unjustified implementation choice

**Rationale (1 sentence with citation):** R6 specifies that paused holds are "skipped over when the title becomes available; the next eligible patron is notified instead" — silently — but `paused_holds.py` sends a "we've skipped over it" email to the paused patron, which the spec doesn't ask for and partially defeats the purpose of pause (patrons typically pause to suppress notifications during periods they can't engage).

**Response (2–4 sentences in the correct tone):**

R6 specifies paused holds are skipped silently — the patron retains queue position but is not notified. The "we've skipped over it" email contradicts this; please remove the `send_email` call to paused patrons inside `handle_title_available`. The silent-skip + continue is the spec'd behaviour; the paused patron will see queue progress in their account when they next log in. If you think notifying paused patrons of skips has product value (e.g., re-engagement nudge), file a spec change request; do not ship it by default.

---

### Signal 7 — SMS replaces email for opted-in patrons (dual-channel decision shipped)

**Classification:** spec gap

**Rationale (1 sentence with citation):** R12 explicitly flags "the business has not yet decided whether SMS-opted patrons should receive both email and SMS, or only SMS" and the Assumptions section names this as pending business decision — but `sms_notification.py` ships the SMS-only path (`if patron.sms_opted_in: send_sms; else: send_email`) without escalation, filling in a decision the spec said was undecided.

**Response (2–4 sentences in the correct tone):**

R12 had the SMS dual-channel decision explicitly flagged as pending business resolution; I should have closed it before the build phase rather than leaving it as an Assumption. Resolving now: business confirms SMS-only when opted in (no dual-channel email). Updating R12 to remove the parenthetical Note and replace with: *"When a patron has opted in to SMS and registered a mobile number, hold notifications are sent via SMS only; email is suppressed for that patron for hold-notification messages."* Your implementation aligns with the resolved direction — no code change required. For the future, please surface explicitly-flagged-pending items as PR comments before merging an interpretation — Signal 8 is exactly the right shape for this kind of question.

---

### Signal 8 — Builder question on R4/R5 intersection (academic + accessibility-priority)

**Classification:** legitimate clarification request

**Rationale (1 sentence with citation):** The Assumptions section flagged "Academic + Accessibility-priority intersection is not specified" and tentatively answered ("Accessibility R4 wins") but did not fully resolve interpretation (a), (b), (c) the builder enumerated; the builder correctly held the PR pending FDE direction, surfacing the under-specification rather than shipping interpretation (b) which has the perverse-ordering property the builder named.

**Response (2–4 sentences in the correct tone):**

Good catch — the R4/R5 intersection is exactly the under-specified edge case I flagged in Assumptions but didn't fully resolve, and your interpretation (b) walk-through correctly identifies the perverse ordering it would produce. The right answer is your interpretation (a): R4 wins entirely for accessibility-priority patrons (jump to position 1, no academic weight applied), regardless of academic tier. Updating R5 to clarify: *"Academic 0.5x queue weight applies only when the patron's R4 jump-to-position-1 does not apply (i.e., the patron is academic but not accessibility-priority). For accessibility-priority patrons of any tier, R4 supersedes R5."* Please proceed with interpretation (a) — and thanks for blocking the merge; interpretation (b) would have shipped an incorrect ordering pattern that production would have surfaced as an equity complaint, not as a unit-test failure.

---

## Reflection (≈120 words)

The hardest diagnostic move for me was the spec-gap vs unjustified-implementation distinction on Signal 7 (SMS dual-channel). The builder shipped a decision the spec explicitly named as pending — that has surface shape "unjustified implementation choice" (builder filled in an unauthorised choice) but second-order shape "spec gap" (the spec itself flagged the question without resolving it; the FDE owns the fix). I landed on spec gap because the FDE response protocol points there: I update R12 with the resolved decision rather than asking the builder to retract. If I ran this again, I'd close every explicitly-flagged Assumption to a positive resolution before any spec leaves the FDE — the W3 vocabulary is precise enough that "pending business decision" in shipping spec text is itself a build-failure-in-waiting, regardless of the category we'd assign downstream.
