# Deliverable #8 — Reflection
**Engagement:** MedFlex Healthcare Staffing
**Participant:** Pavel Klimasheuski
**Date:** 2026-05-13

---

## What would change with more time

### 1. Shadow Kim before designing the coordinator interface

The entire coordinator review experience — the queue, the override window, the confidence score display, the action buttons — was designed without watching Kim work once. With more time, I'd spend 90 minutes shadowing her before writing the architecture, not after. The specific things I'd want to see: does she work cases sequentially or batch-process approvals? Does she treat requests from familiar hospitals differently from new ones? What does she actually look at before feeling confident enough to approve a match — and does it match the fields I assumed she needs?

There's also a question the architecture doesn't answer: if phone calls are 30% of request volume and coordinators currently handle them by taking notes and acting on them directly, will they agree to change that behavior — logging call summaries into ServiceNow so Agent 1 can pick them up? That's not a technical question, it's a behavioral one. If the answer is no, Agent 1 processes only 70% of volume and the headline fill-time improvement number drops accordingly. I accepted "coordinator enters phone requests into ServiceNow" as a given without validating whether it will actually happen. Kim's answer to "would your team do this consistently?" shapes the whole throughput argument.

Coordinators also have the clearest view of where the real friction is. Marcus gave executive-layer metrics (4.2 hours, 7% mismatch, 12% no-show). Kim would tell me where the 4.2 hours actually go — which part is the search, which part is the credential verification, which part is the back-and-forth with hospitals. The architecture would be more targeted if it was aimed at the specific bottleneck rather than the entire pipeline.

### 2. Validate technical infrastructure before committing to the architecture

The two capability specs contain 8 `[ASSUMED]` flags, all of which are build blockers. The architecture was committed to a three-agent pipeline before confirming whether the nurse database has a queryable API, whether credential expiry dates are structured fields or manual notes, whether ServiceNow supports webhooks or requires polling, and how stale the availability data actually is. With more time, I'd run the Aaron session before finalizing the architecture, not as a prerequisite before build.

This matters because some of the [ASSUMED] flags could change the design significantly. If credential status turns out to be a manual lookup rather than a system field, Agent 2's hard constraint filtering doesn't work as designed — it degrades to a "flag for coordinator verification" pattern rather than an automated exclusion. If the nurse database API doesn't exist at all and the data lives in a legacy system with no programmatic access, the matching agent has no data surface to work with. These aren't edge cases — they're the foundation. Discovering them after the architecture is written means rework; discovering them before means the architecture is grounded in reality from the start.

### 3. Find the smallest useful increment first

The current design proposes a full three-agent pipeline. With more time, I'd explicitly design a v0.1 that delivers a useful result without requiring all three agents to be production-ready simultaneously. The most natural starting point: Agent 1 alone, running in display-only mode — no matching, no submission. Coordinators see the structured parse (date, credentials, unit type, urgency) alongside the raw request text in ServiceNow. That's it. No pipeline, no database writes to a matching system, no Agent 2 dependency.

This gives two things: a real test of whether the parsing is accurate enough to be trusted (coordinators will immediately tell you if the parsed output is wrong), and a week-one value story that doesn't require Agent 2 or 3 to exist. If Agent 1 alone compresses coordinator decision time, that's evidence. If the parses are consistently wrong for a certain hospital's writing style, you know before any matching decisions are made on bad data.

The risk of starting with the full pipeline is that when something breaks — and something will — it's harder to isolate whether the failure is in parsing, matching, or submission. A staged rollout (parse-display → advisory matching → autonomous submission) creates natural diagnostic checkpoints.

### 4. Understand the prior AI failures before designing around them

Marcus mentioned two failed AI projects — a chatbot hospitals rejected and a recommendation engine nobody used. The architecture I designed tries to avoid similar failures (trust deficit from coordinators, advisory mode before autonomous submission, explainable reasoning summaries). But I don't actually know why those projects failed. Was the chatbot rejected because the UX was wrong, because it gave bad answers, or because it was solving a problem hospital staff didn't have? Was the recommendation engine unused because coordinators didn't trust the recommendations, or because the interface was buried, or because the data it used was stale?

The failure mode matters for the design. If the recommendation engine failed because coordinators didn't understand why it recommended a particular nurse, my reasoning summaries in Agent 2 are the right mitigation. If it failed because it was too slow to be useful, latency is the constraint I should be optimising for. I designed around a generic "trust deficit" without knowing what specifically broke trust. With more time, I'd push Marcus harder on the specifics — or talk directly to the coordinators who were there.

### 5. The spec-to-build gap appeared earlier than expected

Running Agent 1's spec through an actual build (D9) surfaced four gaps, three of which were in my own spec — not builder errors. The urgency enum contradicted the system prompt I wrote in the same document. A configurable threshold was defined but never given a mechanical use. Duplicate detection behavior for null fields was specified in principle but not in SQL terms. None of these would have been caught by re-reading the spec; they only became visible when the spec was executed.

The lesson is that spec quality can't be fully assessed by reading — it has to be run. With more time, I'd build and test a minimal version of Agent 1 (parse one fixture ticket end-to-end, write the result to the database) before finalising the spec and handing it off. The small gaps that slip through written review become obvious in 30 minutes of execution. That iteration belongs inside the spec-writing phase, not after it.

### 6. The no-show rate deserves more investigation

The architecture accepts the passive acceptance model (silence = accepted) and defers active nurse confirmation to Wave 2. That's the right call given what Marcus said — nurse confirmation wasn't flagged as a pain point. But 12% no-show is a significant number, and I don't know how much of it comes from nurses taking competing agency assignments after being notified. If the primary driver is nurses accepting silently and then being placed by a competitor, better matching (sending the right nurse) won't move the no-show rate much. The 12% improvement target in the validation plan may be optimistic if matching quality isn't the root cause. With more time, I'd ask Kim what coordinators believe actually drives no-shows — that answer shapes whether Agent 2's matching improvements will move the metric at all.
