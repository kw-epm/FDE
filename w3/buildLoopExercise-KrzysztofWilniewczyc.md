# W3D3 Build-Loop Exercise — Cascade Public Libraries Hold Queue

**Author:** Krzysztof Wilniewczyc
**Fixture:** 'inputs/Week3/W3D3-BuildLoop-Exercise.md'
**Submitted to:** squad lead, Wednesday EOD

---

### Signal 1 — 72-hour expiry: open assumption + no rule on how often to check

*notification_deadline.expire_unclaimed_holds() - cutoff = datetime.now() - timedelta(hours=72), hourly job, calendar hours.*

**Classification:** spec gap

**Rationale (1 sentence with citation):** R3 leaves two things unclear about "72 hours" - calendar vs business hours (flagged in the Assumptions section but never resolved) and how often the expiry job should run (R3 says nothing about it, so the builder picked hourly on their own).

**Response (2–4 sentences):**

This one's on me. The calendar vs business hours question was flagged in Assumptions and I never closed it. Closing it now as calendar hours - it's digital lending, branch hours don't matter. I also didn't say anything about how often the expiry job should run. The builder picked hourly, so in the worst case a patron gets about 73 hours. That's fine, but the spec should say so. Updating R3 to: *"A notified patron has 72 calendar hours from 'notified_at' to claim the hold. The expiry job runs at least every hour, so a hold may last up to about 73 hours at most. If unclaimed past this window, the hold expires and the queue moves on to the next eligible patron."* Code already matches the revised R3, no change needed there.

---

### Signal 2 — Accessibility treated as a weight instead of a position jump

*accessibility_priority.py introduces an ACCESSIBILITY = 0.25 weight multiplier in compute_effective_position.*

**Classification:** builder misread

**Rationale (1 sentence with citation):** R4 says accessibility patrons jump to slot 1. The builder instead added a 0.25 weight to the R5 math (a different rule), and the 0.25 came from nowhere because R4 doesn't have a number to base it on.

**Response (2–4 sentences):**

R4 and R5 are doing different things. R5 multiplies your queue position by a weight when picking who to notify next. The queue order itself doesn't change. R4 is different - it just moves accessibility patrons to slot 1, so the queue actually rearranges. The builder mixed the two together and made up the 0.25 number to win the R5 math, but R4 isn't a math rule at all. Please remove 'ACCESSIBILITY' from PriorityWeights, drop the accessibility branch in compute_effective_position, and on hold placement insert accessibility patrons at slot 1 (FIFO between two of them if both are already there).

---

### Signal 3 — Return reminder no one asked for, plus a hinted-at renewal feature

*auto_checkout_handler schedules a 3-day-before-return reminder no one asked for, on top of doing the loan.*

**Classification:** unjustified implementation choice

**Rationale (1 sentence with citation):** R7 just says do the loan automatically, R10 says loans auto-return at 21 days, and that's it - nothing about reminders, and renewing isn't in the spec at all.

**Response (2–4 sentences):**

Thanks for adding the reminder, but the spec doesn't ask for it. R7 just says do the loan. R10 handles auto-return at 21 days. That's the whole flow. The reminder also talks about renewing, which isn't anywhere in the spec, so patrons will start looking for a renew button that doesn't exist. Please drop the schedule_reminder call. If you think it's worth keeping let's talk first and put it in the spec.

---

### Signal 4 — Test breaks as the year changes because 'expected_advances' is hardcoded

*test_overdrive_refresh_advances_queue passes in 2025, fails in 2026 - 'expected_advances' is hardcoded to the Q4-2025 queue state.*

**Classification:** test/environment issue

**Rationale (1 sentence with citation):** The code matches R8 (advance once per new copy), but the test compares against 'expected_advances' which is hardcoded to the Q4 2025 queue state, so the test goes stale every year even though the code is still right.

**Response (2–4 sentences):**

Code is fine. R8 says advance by the number of new copies, which is exactly what on_overdrive_catalog_refresh does. The problem is in the test - 'expected_advances' was set against the Q4 2025 queue state, so it goes stale as soon as the calendar moves on. Two options to fix this. Either mock the queue state at test time so the test doesn't depend on the real clock, or just compute the expected count inside the test as sum(fixture_refresh.added_copies.values()). There's no reason 'expected_advances' needs to be a separate frozen number. The second option is simpler and stops the rot for good.

---

### Signal 5 — Duplicate-hold check ignores format

*place_hold rejects any second hold by the same patron on the same title_id, no matter what format_type is.*

**Classification:** builder misread

**Rationale (1 sentence with citation):** R11 says ebook and audiobook of the same title count as two separate holds, but the duplicate check in place_hold only looks at title_id and ignores format_type entirely (it's passed in as a parameter and then never used).

**Response (2–4 sentences):**

R11 says ebook and audiobook of the same title are two separate holds, and they both count toward the limit. The check patron_has_active_hold_on_title(patron, title_id) only looks at the title. So a patron who already has the ebook hold can't place the audiobook hold, which R11 explicitly allows. Also worth pointing out: format_type is even passed in to place_hold and then never used in the check. Please change the check to key on both title_id and format_type - something like patron_has_active_hold_on_title_and_format(patron, title_id, format_type).

---

### Signal 6 — Email to every paused patron, every time a copy comes back

*handle_title_available sends an email to every paused-hold patron in the queue before notifying the first eligible one.*

**Classification:** unjustified implementation choice

**Rationale (1 sentence with citation):** R6 says skip paused holds and notify the next eligible patron - nothing in there about emailing the skipped ones; the builder added that on their own, and it gets worse the more paused patrons there are (50 paused patrons = 50 unwanted emails every time a copy comes back).

**Response (2–4 sentences):**

R6 says skip paused holds and notify the next eligible patron. Nothing in there about emailing the skipped ones. That part the builder added on their own. And it gets worse the more paused patrons there are: a popular title with 50 paused holds before the first active one would spam all 50 patrons every single time a copy comes back, which sort of defeats the whole point of pausing. Please drop the send_email block in the paused branch and just 'continue' to the next hold. If you think paused patrons should be told something, let's spec it properly - how often, opt-out behaviour, etc - rather than firing on every event.

---

### Signal 7 — SMS only or SMS plus email - still undecided

*send_hold_notification sends SMS-only when a patron is SMS-opted (no email); otherwise email.*

**Classification:** spec gap

**Rationale (1 sentence with citation):** R12 and the Assumptions section both say the SMS-only-vs-both decision hasn't been made yet, and the builder shipped SMS-only with no default in the spec to follow.

**Response (2–4 sentences):**

This one's partly on me, partly on the business. R12 says the SMS-only-vs-both decision hasn't been made yet, the Assumptions section flagged it, and I never closed the loop. The builder picked SMS-only by themselves, which isn't really their call to make on something the business should decide. I'll get an answer from the business this week and revise R12 to spell out exactly what gets sent. Until then, treat the current behaviour as a placeholder, not the final answer.

---

### Signal 8 — Builder asked about R4 and R5 together

*Builder filed a PR-blocking question on where R4 and R5 both apply, listing three readings and refusing to go with option (b).*

**Classification:** legitimate clarification request

**Rationale (1 sentence with citation):** The case where R4 and R5 both apply is flagged in the Assumptions section as "Pending FDE confirmation". The builder didn't ship a guess, they held the PR and asked, which is the right move on a spec point that wasn't decided yet.

**Response (2–4 sentences):**

Thanks for holding the PR. That's exactly the move I'd want here. Confirming what the spec already assumed: an academic + accessibility-priority patron jumps to slot 1 (R4 wins), and the 0.5x academic weight doesn't apply once they're at slot 1. One thing - the way you described option (b) ("position-1-with-0.5x-weight") shows the same R4-as-weight mix-up I'm flagging in Signal 2. R4 is a position jump, not a weight rule, so there's no "weighted slot 1" to compute - it just doesn't make sense as a thing. Updating the Assumptions section to remove the "pending" tag and rewording R4 to make the position jump explicit. Please pick up the new spec and ship.

---

## Reflection (100–150 words)

The hardest part was sitting with each signal long enough to second-guess my first read. On Signal 1 my first thought went straight to the calendar vs business hours gap - only on a second pass did I see the quieter one (the hourly job adds slack to the 72-hour window), which matched my prediction about missing "skipped parts in my own spec". On Signal 3 I almost called it "missing design" before catching that the builder had *added* something the spec doesn't ask for. Opposite direction. Signals 7 and 8 nearly went into "builder misread" too, until I caught that Signal 7's spec was openly undecided (spec gap), and Signal 8 was the builder asking instead of shipping (legitimate clarification). Next time, two questions first: what am I looking at - code, test, or a question? And did the spec pin this down, or did it leave it open?
