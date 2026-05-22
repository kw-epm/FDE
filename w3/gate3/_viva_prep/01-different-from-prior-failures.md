# Viva prep: "How is yours different from the CEO's two failed AI projects?"

*Not part of submission. For my own preparation. The pack §8 says the coach picks one of two standard probes: this OR "what kills this in production?", see `02-pre-mortem.md` for the other.*

---

The two failures (per Marcus, in discovery and in the pack):

1. **Hospital-facing chatbot.** Hospitals wouldn't use it. They preferred email.
2. **Recommendation engine for matching.** Coordinators said "too many mistakes" and stopped using it.

Both failures share a deep pattern: **AI was added to the existing workflow as a feature, not designed as the mechanism.** The chatbot was a UI layer on top of how hospitals already worked; hospitals just kept doing email. The recommender was a black box on top of how coordinators already worked; coordinators rejected outputs they couldn't explain.

Ours is structurally different on five specific axes, each tied to one of the failure modes:

## Axis 1. Channel respect, not channel change

**Their failure (chatbot):** asked hospitals to adopt a new channel. Hospitals declined.

**Our defense:** the agent reads the existing email channel. Hospitals don't change a single thing about how they request shifts. The ServiceNow ingestion sits behind the email, where they already are. No new UI for hospitals.

**Architectural witness:** D#4a §2 (Trigger and inputs) explicitly names email + ServiceNow as the single intake channel; D#2 §"Out of scope" explicitly rules out a hospital portal or chatbot.

## Axis 2. Reason over context, don't learn

**Their failure (recommender):** the model learned a ranking from historical labels that were probably noisy (no Decision-2-equivalent meant "no reply" was being counted as yes, polluting labels).

**Our defense:** v1 agent **does not learn**. It reads historical context as input and shows its reasoning per decision. Coordinators audit the *why*, not just the *who*. Phase 2 adds a learned soft-signal layer, *but only after Decision 2 produces clean explicit-yes labels*. The same recommender trap is what the go/no-go gate at week 1 explicitly tests for and pauses on.

**Architectural witness:** D#3 Decision 1 ("Reason over context, don't learn"), with the alternative "smarter ranking model" explicitly rejected and tied to the prior failure. D#3 go/no-go gate prevents v1 degrading to rules-only with an LLM call sprinkled on top.

## Axis 3. Explainability on every decision

**Their failure (recommender):** coordinators couldn't see why decisions were made, so couldn't fix them, so abandoned the tool.

**Our defense:** every decision the agent makes has reasoning citations linked to specific data sources. The paediatric worked example (D#3 + D#4a §6) shows this concretely: the agent picks Nurse N over Nurse M and the coordinator sees the three context signals that drove the decision. If the reasoning is wrong, the coordinator can fix the input or override the decision, and the override itself is a tracked signal feeding the trust ramp.

**Architectural witness:** D#3 "Hallucinated reasoning" edge case ("Citations mandatory: every claim links to a data source. D#7 validates."). D#7 §3.4 (reasoning citation accuracy as ongoing validation).

## Axis 4. Earn the autonomy, don't claim it

**Their failure (both):** the AI was deployed at the autonomy level the *designers* believed it deserved, not the level *coordinators trusted it to operate at*.

**Our defense:** trust ramp. Weeks 1–2 of the ranker, every decision is coordinator-approved. Weeks 3–4, high-confidence cases auto-send. Week 8, sample audits. Override rate is a tracked metric (target <40% by week 4, <25% by week 8); >50% pause, >70% rollback. The autonomy is earned through measured coordinator agreement, not assumed.

**Architectural witness:** D#3 trust ramp table + D#1 success metrics row + D#4a §4 step 6 (confidence gate × trust ramp).

## Axis 5. Detectable regression toward either failure

**Their failure (both):** there was no metric that said "this is starting to look like our chatbot / recommender failure mode." By the time it was obvious, adoption was already lost.

**Our defense:** the pause/rollback table (D#1, mirrored in D#3 and D#7) has eight metrics, all of which would detect regression toward either prior failure mode early. Override rate climbing means we're heading toward the recommender exit. Hospital acceptance rate dropping means we're heading toward "tool that doesn't deliver." Submission withdrawal rate rising means we're gaming a metric instead of solving the problem.

**Architectural witness:** D#1 §pause/rollback table (8 rows), mirrored in D#3 and D#7. Each row has a named owner and a defined operational response within 1 working day (D#7 §4).

---

## The one-sentence version (if I only have 30 seconds in the viva)

*"The chatbot failed because it changed how hospitals worked; ours doesn't. The recommender failed because it learned from noisy labels and couldn't explain itself; ours doesn't learn in v1 and shows reasoning on every decision. And eight tracked metrics would catch us regressing toward either failure mode before adoption is lost."*

## The hardest follow-up I should be ready for

**Coach:** *"That sounds clean. But your Decision 2 is conditional. If Head of Ops says 'no, we don't treat no-reply as yes,' your entire clean-label argument for Phase 2 of Decision 1 falls. How is that not the same trap?"*

**My answer:** *"It's not the same trap because we name the dependency before building. Decision 2 is explicitly conditional on Head of Ops confirming the pattern (D#3 Decision 2 §Status). If the finding doesn't hold, we move to confirmation-channel improvements + same-day re-check, the alternative path is in the ADR, not a footnote. The recommender's failure was that it assumed clean labels existed; ours says 'we'll know by Monday whether they do, and we have a plan for both outcomes.' Naming the dependency is the architectural move, not assuming it away."*
