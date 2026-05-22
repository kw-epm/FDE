# Viva prep: "What kills this in production?"

*Not part of submission. For my own preparation. Pre-mortem written as imagined post-mortem from week 8 looking back at the failure. Each scenario names the detection signal and the recovery path.*

---

## Frame for the viva

*"I won't pretend nothing kills this. The pack tells me to acknowledge a weakness honestly, not to wave it away. Here are the five scenarios I think about most, and what we did about each. The honest weakness I own is scenario 1, because it's the one we can't fully defend against by week 0."*

---

## Scenario 1: Data assumptions break (the honest weakness)

**Imagined post-mortem from week 8.** *"We shipped v1 architecture that depended on at least one high-signal contextual source: hospital acceptance history or past nurse-hospital pairings. Week 1 data audit found that hospital records existed but were not structured (free-text emails from hospitals on whether a placement worked or not), and past pairings existed only as coordinator memory in Slack threads. We could not back the architecture's reasoning step with queryable data, so the ranker degraded to rules-only, the recommender trap we explicitly warned about in Decision 1. v1 launched anyway, coordinators saw rule-based ranking dressed in LLM citations, override rate climbed past 50% by week 3, we paused at the go/no-go gate. Three weeks lost."*

**Detection.** D#3 go/no-go gate at week 1. The audit was designed exactly for this. The failure here is not failing to detect; it's that we didn't audit before signing the engagement.

**Recovery.** Pause and rescope per D#3 §"What the architecture cannot fix." Either invest 2–3 weeks of week-0 work building queryable history (ETL from email archives + coordinator interviews) and restart; or descope to a rules+citations product without the agentic claim, which is a different engagement.

**Why I own this as the honest weakness.** It's mitigated by the go/no-go gate, but not eliminated. Pre-engagement data audit (Idea 5 in week-0 plan, D#2) would close it more. We didn't have the access to do that before kickoff. So it's a residual risk by design.

---

## Scenario 2: Override rate stays high, doesn't drop

**Imagined post-mortem.** *"Override rate at week 4 was 55%. Trust ramp held. By week 6 it was 48%. The architecture works structurally but coordinators don't trust the ranker's reasoning on ~half the cases. We narrowed deployment to the 60% of shift requests where override is below 25% (mostly standard ICU + RN shifts with stable hospital partners); the other 40% stay coordinator-decided. v1 worked for the slice that suited it; the broader v1 didn't ship to those categories."*

**Detection.** D#1 pause/rollback table row 4 (override rate). >50% at week 4 = pause. >70% sustained = rollback.

**Recovery.** Narrow the deployment to where override is low. Per D#3 §"What the architecture cannot fix": *"v1 doesn't have to work for every shift. It has to work for some, well."* This is operational, not architectural, segment-level metrics in D#4 from day 1 enable this.

**Why this is bounded.** The architecture is built for it. The override rate metric is exactly what tells us we're regressing toward the recommender failure, and the narrowing response is pre-planned.

---

## Scenario 3: HIPAA blocker / regulatory drift in production

**Imagined post-mortem.** *"Week 0 legal review confirmed the LLM provider had a BAA in place. Week 6, the model provider released a new model version; their BAA was for the prior version only. We had to either pin to the old model (degraded quality) or pause new shift submissions until the new BAA closed (operational outage). We pinned. Quality dropped by ~2pp on first-pick acceptance. Coordinator override rate climbed for two weeks until the BAA was signed off."*

**Detection.** D#7 §6.3 (model accuracy drift) extraction-accuracy benchmark re-runs before any model upgrade. But the policy gap (BAA timing) needed compliance team's quarterly review (D#7 §6.2 mitigation) to catch.

**Recovery.** Two-track: technical (pin to known-good model) + legal (drive BAA closure). D#7 §7.3 flags this as a regulatory blocker class.

**Why it's a real risk.** Compliance moves on its own clock. The architecture's circuit-breaker is the pin; the engagement's exposure is the BAA gap.

---

## Scenario 4: Hospital moves to a structured portal (channel change)

**Imagined post-mortem.** *"Hospital A, one of the two slice hospitals, moved to a vendor-managed shift-marketplace portal in week 5. Our intake parser was tuned for their email format. Portal data arrived in a different schema; the agent was effectively blind to Hospital A's requests for 10 days while we built the portal connector. Coordinators went back to manual for Hospital A only. Hospital B continued in agent mode. Net impact: slice volume effectively halved for those 10 days; hospital acceptance rate looked fine because we weren't submitting to Hospital A at all."*

**Detection.** D#3 §"What the architecture cannot fix" row 4. The shift in intake volume per hospital would surface within 48 hours via the D#7 production cadence (daily pause/rollback metric snapshot).

**Recovery.** Coordinator-only routing for the affected hospital while we build the portal connector. Architecture supports this because the slice is per-hospital, not per-channel. D#3 architecture explicitly absorbs this case.

**Why this is bounded.** It's annoying, not fatal. The slice survives if one of two hospitals goes manual for two weeks.

---

## Scenario 5: Coordinator burnout from week-1 trust ramp reviews

**Imagined post-mortem.** *"Week 1, every decision required coordinator approval. Volume was 184 fills/day across the slice. Even at 30 seconds per review, that's ~90 minutes of new review work per coordinator per day on top of their existing workflow. By week 3, two coordinators had stopped reading the reasoning citations and were rubber-stamping. Override rate dropped to 5%, looks great on paper, but high-confidence cases were not actually being audited. We didn't know we had a problem until a hospital acceptance rate drop in week 5 surfaced a bad auto-send pattern we should have caught earlier."*

**Detection.** D#7 §3.3 (confidence calibration) high-confidence cases approved without override should be ≥95%, but if the *audit* is rubber-stamping, this metric becomes a confidence-on-confidence loop. Better detection: per-coordinator audit time + reasoning-read time, instrumented in the dashboard.

**Recovery.** Adjust the trust ramp: move to "auto, sample audits" earlier for the cases that are clearly high-confidence, freeing coordinator capacity. Or reduce the per-shift review burden via a "read the reasoning once per hospital per day" pattern, with override-on-exception still required.

**Why I didn't fully solve this.** D#3 trust ramp assumes coordinators have capacity to review at week-1 volume. That assumption is itself the risk. D#2 risk row 1 ("agent makes visible mistakes early") covers the *trust* dimension; this scenario covers the *capacity* dimension. Both are real.

---

## The one-sentence version

*"Five scenarios kill this. Data dependency is the one I can't fully defend against by week 0, and that's the weakness I'd own. The other four are detectable inside the pause/rollback table and have pre-planned operational responses, none of them require us to redesign the architecture mid-engagement."*

## The hardest follow-up

**Coach:** *"You named scenario 1 as the honest weakness. But you also said in D#9 your spec was structurally complete but precision-vague. Aren't those two weaknesses? Or are you picking one to avoid the other?"*

**My answer:** *"They're connected, not interchangeable. The D#9 precision-vague point is a spec-discipline issue: the spec doesn't pin numbers and the buildability test surfaced it. The data-dependency point is an engagement risk: the architecture rests on data we haven't yet confirmed exists. The honest weakness for production is the data one because it could kill the v1 even with a perfectly precise spec. The D#9 finding is fixable in week 0, the data finding might not be."*
