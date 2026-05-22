# Deliverable #6 — Client Feedback Response
**Engagement:** MedFlex Healthcare Staffing
**Participant:** Pavel Klimasheuski
**Date:** 2026-05-13
**Re:** Marcus Reyes pushback memo, received 2026-05-13 09:00

---

Marcus —

Three points addressed in order.

---

**1. Week-one value doesn't require autonomous submission**

You're right that the ADR framing made the advisory period look like dead time. It isn't.

Here's what changes on day one without autonomous submission: coordinators stop searching and start reviewing. Today, a coordinator reads a free-text request, manually parses it, manually searches the database across credentials, availability, proximity, and preference history, builds a candidate list mentally, and decides. That's the active matching work that backs up under volume spikes.

With the agent running in advisory mode: the parse and ranked candidate list arrive before the coordinator touches the case. Her job is to review and approve — roughly 60–90 seconds of active decision time instead of 3–4 minutes. At ~960 decisions per day, that compression materially shortens the queue, which directly reduces fill time. This is the week-one value: faster coordinator throughput, shorter queue, earlier responses to hospitals. Autonomous submission adds further improvement once calibrated — it isn't the prerequisite.

On the calibration timeline: the threshold isn't set after two fixed weeks. It's set after sufficient ground truth accumulates. At ~960 decisions per day, that data arrives in days, not weeks. Conservative estimate: enough cases to set an initial threshold by end of week one; autonomous submission for high-confidence cases begins week two. Board update at six weeks has four weeks of autonomous submission data to show, not zero.

---

**2. The split exists to catch parse errors before they reach the hospital**

The ADR justified the two-agent split on engineering grounds. That was the wrong argument.

The right argument: if Agent 1 and Agent 2 are integrated, a misparsed ICU request becomes a med-surg candidate ranked confidently, invisibly, and submitted before anyone reviews it. The wrong nurse reaches the hospital faster than before.

The split creates a visible checkpoint. Agent 1 outputs a structured ShiftRequest with a confidence score. Low-confidence parses and flagged ambiguities go to the coordinator clarification queue before Agent 2 runs. The coordinator sees the parsed request, can correct it, and only then does matching proceed. The cost of a parse error is a 30-second coordinator correction, not a wrong-nurse submission to a hospital.

This is the hospital outcome the split delivers: errors are caught at the cheapest possible point in the workflow, not discovered after submission.

On inference cost: Agent 1 runs on a lighter model — parsing is structured extraction, not complex multi-factor reasoning. The marginal cost is low relative to eliminating a class of wrong-match submissions.

---

**3. Kim and Aaron: here's the plan**

Flagging unknowns without a resolution path was a gap. Two sessions required before Phase 1 engineering begins — not as nice-to-haves, as build blockers.

**Kim — 90-minute workflow shadowing session:**

Goal: validate three assumptions that change the design if wrong — (a) whether she processes cases sequentially or batches approvals, (b) how she handles repeat hospitals differently from new ones, (c) what information she needs to feel confident approving without independently searching the database.

Day-one coordinator experience as currently designed: Kim opens a queue of pre-parsed shift requests. Each shows the structured ShiftRequest (editable if the parse is wrong), top 3 candidates with confidence scores and reasoning summaries, and an approve / select alternative / flag for clarification action. All overrides are logged with a reason category. During the advisory period, every case goes through her — nothing submits without her approval.

What changes if her workflow differs: if she batches approvals rather than working sequentially, the interface needs batch mode. If she applies informal priority rules for urgent shifts or preferred hospitals, the queue needs priority sorting she controls. The shadowing session surfaces these before the interface is built.

**Aaron — 2-hour API discovery session:**

Required outputs: ServiceNow API capabilities confirmed, nurse database schema documented, hospital preference data structure and completeness confirmed, credential status mechanism clarified (system flag vs. manual lookup).

Engineering does not start on the affected components until both sessions complete. The architecture holds; the interface design and integration contracts are confirmed against reality before a line of code is written.

**What happens if validation reveals surprises:**

The three-agent pipeline is architecturally resilient to workflow differences because the confidence threshold is the shock absorber. If Kim batches approvals — the coordinator interface switches to batch mode; the agents don't change. If hospital preference data is thinner than expected — Agent 2's soft ranking degrades gracefully, confidence scores drop on affected cases, and those cases route to coordinator review rather than auto-submission. If ServiceNow API access is more limited than assumed — the integration layer changes; the agent reasoning doesn't. If credential status turns out to be a manual lookup — Agent 2 flags those cases as "credential status unconfirmed" for coordinator verification rather than treating them as hard constraints.

In each scenario, the system responds to uncertainty by increasing coordinator involvement, not by producing wrong outputs. That's by design. What Kim and Aaron change is the configuration of the interface and the integration layer — not the core matching logic or the delegation architecture. The cases where their answers would require a structural rethink are named as open assumptions in the architecture document; those components are not built until the assumptions are confirmed.

---

Pavel
