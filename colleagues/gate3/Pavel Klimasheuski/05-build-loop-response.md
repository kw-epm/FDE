# Deliverable #5 — Build-Loop Response Memo
# Cascade Public Libraries: Hold Queue Management & Notification
**Participant:** Pavel Klimasheuski
**Date:** 2026-05-13

---

### Signal 1 — 72-hour notification window

**Classification:** Spec gap

**Rationale (1 sentence with citation):** R3 specifies a 72-hour claim window, but the Assumptions section explicitly marks the definition of "72 hours" (calendar hours vs business hours) as unconfirmed and pending FDE review — the builder correctly followed the stated assumption (calendar hours), but that assumption was never confirmed before build started.

**Response:**

I should have resolved this before handing the spec to the builder. The builder did the right thing — they followed the stated assumption — but the assumption was explicitly flagged as pending my confirmation and I never gave it. Updating R3 to read: "A notified patron has 72 calendar hours to claim the hold (i.e., 72 clock hours from the time of notification, regardless of library opening hours)." If the business intends business hours instead, R3 must be revised before build continues — please confirm.

---

### Signal 2 — Accessibility queue jump replaced with weight multiplier

**Classification:** Builder misread

**Rationale (1 sentence with citation):** R4 specifies that accessibility-priority patrons jump to queue position 1 (a positional assignment), not that they receive a weight multiplier; the builder invented a 0.25x weight (ACCESSIBILITY = 0.25) which contradicts both the mechanism described in R4 and the plain text of the requirement.

**Response:**

R4 specifies a queue-position jump to position 1 — not a weighted position calculation. Please remove ACCESSIBILITY from PriorityWeights and replace the accessibility branch in `compute_effective_position` with a direct position assignment: if `patron.has_accessibility_modifier`, set position to 1 subject to R4's tie-breaking rule (standard FIFO applies between two accessibility-priority patrons already at position 1). The 0.5x academic weight is correct per R5 and should be retained.

---

### Signal 3 — Return reminder added without spec basis

**Classification:** Unjustified implementation choice

**Rationale (1 sentence with citation):** The spec defines auto-checkout in R7 and the loan period in R10 (21 days), but contains no requirement for a return reminder or any pre-return notification at any point.

**Response:**

Appreciate the thinking on return reminders — it's a reasonable product feature — but it's not in the spec and I don't want unrequested behaviour shipped. Please remove the `schedule_reminder` call and associated logic from `auto_checkout_handler.py`. If you think it's worth adding, file a spec change request and we can scope it deliberately.

---

### Signal 4 — Date-bound test fixture

**Classification:** Test/environment issue

**Rationale (1 sentence with citation):** The implementation in `overdrive_refresh.py` correctly matches R8 (advance queue by the number of new copies), and the test logic is sound — the failure is caused entirely by the fixture `overdrive_refresh_2025_q4.json` encoding Q4 2025 queue state, making `expected_advances` stale when run in 2026.

**Response:**

The implementation is correct per R8 — don't touch the code. The fixture is the problem: it encodes a specific historical queue state that no longer matches current state. Either regenerate the fixture to reflect a current queue snapshot and rename it to something date-neutral (e.g., `overdrive_refresh_3copies.json`), or refactor the test to set up its own queue state in-test rather than relying on a snapshot. The latter is more resilient long-term.

---

### Signal 5 — Duplicate hold check ignores format type

**Classification:** Builder misread

**Rationale (1 sentence with citation):** R11 explicitly states that ebook and audiobook editions of the same title are treated as two separate holds, but `patron_has_active_hold_on_title(patron, title_id)` checks only `title_id` — meaning a patron trying to hold both formats of the same title would be incorrectly rejected with a DuplicateHoldError.

**Response:**

R11 requires format-distinct holds to be treated as separate holds. Change the duplicate check to include `format_type` — the condition should be `patron_has_active_hold_on_title(patron, title_id, format_type)` and the underlying query must check the combination `(patron_id, title_id, format_type)` rather than `(patron_id, title_id)` alone. Both holds still count toward the active-hold limit per R11, which your limit logic already handles correctly — no change needed there.

---

### Signal 6 — Skip notification sent to paused patrons

**Classification:** Unjustified implementation choice

**Rationale (1 sentence with citation):** R6 specifies only that paused holds are skipped and the next eligible patron is notified; it contains no requirement to send any notification to the patron whose paused hold was skipped over.

**Response:**

The skip-and-advance logic is correct per R6, but the email to the paused patron has no spec basis. Please remove the `send_email` call in the paused-hold branch entirely — the paused patron should receive no notification at this point. If a "your hold was skipped" UX turns out to be valuable, that needs to be specified and sized deliberately before it ships.

---

### Signal 7 — SMS-only implemented for opted-in patrons

**Classification:** Spec gap

**Rationale (1 sentence with citation):** R12's Assumptions section explicitly marks the SMS dual-channel vs SMS-only decision as "pending business decision" — the builder implemented SMS-only without that decision having been made, picking one interpretation from an openly unresolved spec assumption.

**Response:**

I should have resolved this before the build started. The builder made a defensible default choice (SMS-only), but the Assumptions section explicitly flagged this as a pending business call and I never made it. I'm treating SMS-only as the interim implementation: updating R12's assumption to read "SMS-opted patrons receive SMS only (no email fallback), pending final business confirmation." If the business confirms dual-channel instead, I'll revise R12 and the builder will need to update `send_hold_notification` accordingly. Will confirm by EOD.

---

### Signal 8 — Builder question: Academic + Accessibility-priority intersection

**Classification:** Legitimate clarification request

**Rationale (1 sentence with citation):** The Assumptions section explicitly acknowledges that the Academic + Accessibility-priority intersection is "not specified" and "pending FDE confirmation," and the builder correctly identified that interpretation (b) — applying 0.5x weight to position 1 — produces a counter-intuitive outcome where academic+accessibility-priority always beats accessibility-priority alone.

**Response:**

Good catch, and the right call to hold the PR. The builder's analysis is correct — interpretation (b) is nonsensical and should not ship. Confirming interpretation (a): R4 wins. If a patron has an accessibility modifier, they jump to position 1 and the academic 0.5x weight (R5) does not apply. Updating the Assumptions section: "If a patron is both Academic and Accessibility-priority, R4 takes precedence — the patron jumps to position 1 and the R5 academic weight does not apply. FIFO applies between two Accessibility-priority patrons at position 1 per R4's existing tie-breaking rule." Please implement interpretation (a) and unblock the PR.

---

## Reflection

The hardest move for me was detecting some of the unjustified implementations, because sometimes they look really natural — close to what you'd usually do in     
real-world scenarios. In Signals 3 and 6 there were additional notification features added by the builder that didn't click immediately, but then I noticed they  
were not required or even hinted at in the initial requirements. These things are important to catch, even if the resulting code looks rational to you — it might 
simply not be required. I also like the fact that while finding such extras the builder produced, you can really use them as a question to a stakeholder: for
example, maybe it would be worth notifying users in those places, even if it wasn't designed in from the beginning. This is especially useful early in a product,
when the AI's broad knowledge of common patterns can surface things worth considering — even if they don't belong in the current spec. So my main takeaway is that
it's important not only to detect and classify issues, but also to find the reason why they happen and what they tell us — can we actually benefit from those issues?

Spotting spec gaps (as in Signals 1 and 7) is equally important — and part of that is knowing which parts of the product are built on top of unconfirmed assumptions. That said, gaps aren't always a problem: in a prototype or POC context they can be the right call. What matters most is that those gaps are tracked, their presence in the code is known, and the reasoning behind the decision to proceed anyway is documented.
