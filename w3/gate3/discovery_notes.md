# Discovery call notes — MedFlex (virtual Thursday, Week 3)

*Squad-based 60-minute role-play. Coach Aliaksandr Batashou played CEO ("Marcus Reyes"). Co-coach Benoit Charrier facilitated. ~17 participants on the call (Krzysztof's squad merged with one other squad). Full transcript: `/mnt/c/Users/xyh/Downloads/Mid-week coach _ peer checkpoint.vtt`.*

## What Marcus said (the things that matter)

### On the bottleneck

- **Speed is the binding constraint.** *"If someone submits quicker than I do, the hospital picks them."*
- Coordinator's senior job: *"Make sure we are filling all the requests as quick as possible... if there is a queue, then it takes us even longer to submit our proposal and time is a problem."*
- The matching step is *"the biggest, the biggest time-consuming part."*

### On hospitals' decision-making

- *"Still, the final decision is with hospital. They decide with whom to go. Our role is to submit the best matching profile as possible. We better to offer something than nothing."*
- *"We would prefer submit at least something than nothing and let the hospital decide."*

### On free-text data (the agentic gold)

- Alexandra asked if credentials in requests are structured or free text. Marcus: *"Free text, free text."*
- *"All the data is in a pretty much raw format... if it's email, it's just a free text. ServiceNow is mostly used to manage the queue."*

### On compliance

- *"It's process of nurses onboarding is absolutely separate process."*
- *"That's Compliance team. I'm not currently to optimize it for this."*
- *"So the compliance verification is not an issue. We don't think we need to actually focus on that."*
- Closing coach feedback (out of role): *"You and the other team, you focused a lot on that legal sort of things. Like I, from the very beginning, I mentioned that's a separate process."*

### On the 7% mismatch

- *"It's purely based on the data we get from the hospital."*
- Two causes named: qualification mismatch flagged on rejection, and hospitals sometimes picking on prior nurse feedback rather than pure qualification fit.

### On the 12% no-show

- Hospitals notify MedFlex of no-shows (not the other way).
- Nurses sometimes accept a parallel shift from a competitor agency.
- A discount was given to a hospital because of no-shows (financial impact admitted reluctantly; no number).

### On competitive dynamics

- *"Same nurse will be submitted by two different agencies."*
- Competitors sometimes pay nurses more or offer better contract terms.
- MedFlex itself routinely submits the same nurse to multiple hospitals in parallel and pulls back when one confirms.
- Marcus admitted at the end this was a contradiction he hadn't fully thought through: *"I was just thinking how it actually could work if we submit nurses to multiple hospitals."*

### On the two prior AI failures

- **Chatbot:** failed because hospitals didn't want to chat. *"They still prefer to use emails."*
- **Recommendation engine:** *"making too many mistakes... combination of technical gaps in the solution, and not enough training which we put towards the stuff."*

### On "10x without 10x-ing"

- Concrete: *"My target in two years time to have 200 millions in revenue, which in the current way is like 14."* ($14M today → $200M target.)
- 8-week ask: *"You tell me what is the best to do in eight weeks so I could get my money back. Starting to get my money back."* (Marcus explicitly refused to define the milestone — asked the squad to scope it.)

### On credential gate / culture

- Qualification is a legal gate: *"if you're not qualifying for the job, legally it's not possible."*
- Periodic re-checks legally mandated: *"There is a cadence where they are legally obligated to recheck qualification."*

### On cost of failures

- Mismatches: *"reputational area for us... no direct financial impact."*
- No-show financial cost: *"Not lost a client, but I had to give a discount to one of my clients."* — refused to give numbers, said cost-per-shift *"is not relevant."*

### On coordinator behaviour and judgment

- Experienced coordinators (10+ years): *"They know how to act better in specific cases, assuming the specific request and even sometimes specialization of the hospital, matching into the nurses."* Newcomers slower.
- No defined threshold for borderline-fit nurses: *"it's more like there is no yet well-defined... I rely on the coordinators."*
- Hospital preference data (which nurses a given hospital has liked) lives in coordinator memory + ad-hoc system notes.
- Marcus admits: *"I don't think there is like an industry standard in this regard."*

### On automation appetite

- *"My goal is automated as much as possible."*
- But also: *"I'm just hoping this is not something you do for the first time, so... what are the consequences of removing humans from the loop? I'm all yours. Tell me."* — clearly not actually willing to remove humans, wants the squad to own the risk call.

## Contradictions surfaced during the call

| Early statement | Later statement | The gap |
|---|---|---|
| Match flow described as discrete pipeline — coordinator picks up one request, finds one nurse | Same nurse submitted to multiple hospitals at once and pulled back | Marcus acknowledged this himself at session end |
| Compliance is fully separate, "not an issue" | System does NOT proactively flag a nurse whose certification expires before the assigned shift; coordinators expected to catch it manually | Unenforced rule, not a system guardrail |
| 4 hours fill time average, "never goes beyond that" | "Sometimes it takes longer than four hours" — within minutes | The 4.2h number is loose |
| Wants 14x revenue without growing operations team | Also: *"actually be prepared as a business to grow the number of people I have in the team to support the business"* | Coordinator headcount story is unsettled |
| "We have a quality score" | 7% mismatch comes from hospital data (complaint count, not score) | The "quality score" may just be the complaint count rebranded |

## What Marcus deferred (no one available during the call)

- **Head of Operations** — coordinator-day-shape, end-to-end fulfillment walkthrough, time breakdown
- **Compliance team** — cadence, API for verification
- **Legal team** — qualification rules, contract terms
- **Marketing team** — nurse supply growth

Marcus also pre-disclaimed: *"some question will be just my interpretation, it's nothing with reality."*

## Pavel's finding (uncovered during the role-play)

The system counts "nurse didn't reply" as "accepted." Marcus did not fully refute it but also did not fully confirm. This is the basis for Decision 2 in D#3, currently flagged as conditional pending Head of Operations confirmation.

## Coach feedback (out of role, end of session)

> *"You and the other team, you focused a lot on that legal sort of things. From the very beginning, I mentioned that's a separate process... I would prefer you at least solve one business problem, but solve it properly... Two different paths, like two different teams. It's not the same single process."*

This is the strongest steer in the session. It shaped: keeping compliance OUT of v1 automation, and the one-problem-well discipline.

## What we still don't know

These are open follow-ups for Head of Operations (also listed in D#1 and D#2):

1. Where do the 4 hours actually go — working or waiting?
2. Is 4h an average or a median? What does the tail look like?
3. What do 10-year coordinators do that newcomers don't?
4. When hospitals reject an offer, why? (Categories.)
5. Is "no reply from a nurse = yes" really how it works today? *(Decision 2 in D#3 is conditional on this.)*
6. How does shift volume scale with revenue? More hospitals, bigger contracts, more shifts per hospital — or some mix?
7. What's the email/portal/phone share of incoming hospital requests today?
