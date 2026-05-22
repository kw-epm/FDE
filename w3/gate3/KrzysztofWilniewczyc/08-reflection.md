# D#8 Reflection

*MedFlex Healthcare Staffing engagement. An honest account of where my thinking moved during the week. Not a victory lap on the deliverables.*

## Three lessons that earned themselves

### Lesson 1. Assumptions need a closure date, not just a flag

The Wednesday Cascade Public Libraries exercise gave me 8 builder signals to diagnose. Three of them (Signals 1, 7, 8) traced back to my own spec. They were open assumptions I had flagged in an "Assumptions" section and then never closed. The pattern was the same each time: I noted the uncertainty, then forgot about it once the spec went to build.

The same pattern then showed up in MedFlex two days later. I assumed the slice (ICU + 2 hospitals) was reasonable based on healthcare industry norms. I flagged it as a "working hypothesis." Marcus correctly called it a placeholder and forced a decision by Monday EOD. Separately, I assumed cost-per-shift wasn't relevant because Marcus said so at discovery. The CFO reversed that within a week. Both were assumptions I had flagged but not closed.

**The carry-forward.** Every assumption needs a named owner and a closure deadline, not just a confidence label. D#3's data assumptions table now has a go/no-go gate at week 1. D#1 lists the open questions; D#7 adds owners and deadlines for the validation-critical ones. That's the operational fix.

### Lesson 2. Industry norms aren't client truth

Two places I leaned on healthcare industry norms instead of MedFlex's actual numbers. First, the $300 net revenue per filled shift, used to back-solve fills/day in D#1 §year-1 contribution. Second, I mentally leaned on typical ICU share patterns when picking the slice hypothesis in D#2, though I never wrote a number into the spec. Both leanings turned out to be the wrong calibration for a CFO-facing answer. Worse: I initially called the $300 figure a "margin" when in fact it's the agency's net revenue per shift, and the difference matters a lot when you're back-solving volume from a $14M revenue figure.

The lesson isn't "stop using industry norms." They're a fine starting point when you don't have client data. The lesson is to flag the gap aggressively and put the clarification in the first week, not the third. D#6's response to Marcus now lists the five clarifications I need from the CFO on Monday before any number is committed. That's what should have been in D#1 from the start.

### Lesson 3. Conditional honesty beats false certainty

Decision 2 in D#3 (treating "no reply from a confirmed nurse" as an implicit yes) was the place I had a clean choice. I could commit to the finding or mark it conditional on Pavel (FDE squad mate) / the squad (FDE cohort) confirming the no-reply pattern in MedFlex's actual data. I marked it conditional and wrote an explicit alternative path (confirmation channel improvements) if the finding doesn't hold.

That turned out to be the strongest position I took in the architecture. Marcus's Friday pushback hit three things and didn't touch Decision 2. A conditional with a stated fallback is harder to attack than a committed decision built on a shaky assumption, because the conditional already names its own weakness and has the answer for what happens if it breaks. Peer submissions tended to either skip the dependency or commit to a finding without naming what they were betting on. Both are riskier than naming the dependency out loud.

**The carry-forward.** When a decision rests on a finding that isn't fully confirmed, frame the decision as conditional with an explicit alternative path. Name the dependency. Name what happens if it breaks. That's the move.

## What worked (kept short, not a victory lap)

- **The four-state lock state machine for race conditions.** Most peers had locking plus a timeout. Adding the partial-commitment state turned the worst case from "candidate frozen forever" or "double-commitment chaos" into a bounded escalation path. The depth in the architectural choice is the part senior reviewers value most, and it's where the design earns the trust to be autonomous in urgent mode.
- **The conditional framing of Decision 2.** Anchored the architecture in honesty rather than false certainty. Survived Marcus's read on Friday.
- **The Cascade exercise feeding back into MedFlex spec discipline.** The meta-lesson (close your assumptions) became a direct architectural commitment in D#3 (the data go/no-go gate at week 1). Cross-domain transfer of a hard-won habit, not a generic platitude.

## What I'd change if I had another 30 minutes

- **Pre-engagement data audit, not week-1 data audit.** The single biggest architectural risk is that the contextual data sources (hospital acceptance records, past nurse–hospital pairings) don't exist in MedFlex's systems in a usable form. The go/no-go gate at week 1 is the right safety net, but the better answer is to audit before signing the engagement. A 30-minute call with Head of Ops before kick-off would have closed the question and reshaped D#3.
- **A real worked example in D#3 from day one.** The AI-native moment (the Hospital A pediatric allergy case) only got into D#3 on Friday, after I realised the architecture was answering the "where does AI actually think?" question in categories, not in scenes. A technical reader of D#3 needs to see the agent reasoning in a real situation, not just be told it reasons. The example should have been in the first draft.
- **One more metric in D#7: cost per decision.** The validation plan doesn't track agent cost per decision. At the ~13,500 decisions/day target, LLM API cost is a real budget line. It should be a monitored metric from day one, not an afterthought added when the bill arrives.
- **Slice criteria written before the discovery call.** I picked ICU + 2 hospitals based on industry norms after the call. With another 30 minutes I'd have written the slice criteria first (the same 5 criteria that now sit in D#2 and D#6) and asked Marcus to apply them in the discovery call. The slice would have been locked in week 1 instead of pushed to a Monday post-pushback meeting.

## What I'd carry into the next engagement

- **The "every assumption has a named owner and a closure deadline" rule.** The Cascade exercise made it concrete. D#3's data assumptions section and the D#7 open-questions list operationalise it. Bring this to every future spec, and write the deadlines into the spec itself, not into a separate to-do list that gets forgotten.
- **The conditional ADR pattern.** When a decision rests on a finding that isn't fully confirmed, frame the decision as conditional with an explicit alternative path. Decision 2 is the proof point. Marcus didn't touch it on Friday because there was nothing to push back on. The dependency was already named.

## What this engagement taught me about my own bias

My instinct on Thursday was to write thorough, complete-looking deliverables. The first version of D#1, D#2 and D#3 was around 6500 words and read like polished consulting prose. The Friday rewrite cut it to about 4000 words and made it sound like I'd actually written it on a Thursday evening rather than copied a template. The lesson: thorough doesn't mean longer. Rigour is in the structure (the four-state lock, the conditional ADR, the go/no-go gate), not in the word count. Length without depth is the easiest mistake to make under exam pressure, and the hardest one to catch from the inside.

---

*Notes for the verbal defense. The honest weakness to own out loud is the data dependency on contextual sources, mitigated by the go/no-go gate at week 1. That's the same diagnosis as Lesson 1 and as "what I'd change" item 1 above. Consistent across all three surfaces, no rescuing.*
