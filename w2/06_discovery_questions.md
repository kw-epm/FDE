# Discovery Questions for the Main Stakeholder
**Scenario 4 — Community Content Moderation (MiniBase)**
**Date:** 2026-04-30
**Stakeholder:** Tom Włodarczyk (primary, Community Manager) + Senior Moderator (secondary)

> Each question is grounded in a specific design dependency. The answer Tom gives would materially change the agent design — these are not generic discovery questions. Every question references the artifact section it's testing.

---

## Format

- **60-minute structured interview** (Tom)
- **30-minute follow-up** (Senior Moderator if not in main session)
- **Bring:** artefacts 4.1–4.3 printed; effort breakdown; the Open Gap Register from `01_elicitation_log.md`
- **Senior Moderator scope:** Q1, Q3, Q4, Q6 should be run with Senior Moderator present or in a follow-up — the tracker is shared with them only, so they may know the full VIP list, real escalation patterns, and possibly the 2024 incident detail.
- **Record both sessions** for reference.

---

## Discovery Round (P0/P1 — what Tom must answer to move past current gaps)

| # | Question | Gap it closes | Priority |
|---|---|---|---|
| 1 | "Walk me through the 2024 sponsor incident — what happened, and what specifically made you write the rule the way you did?" | 2024 incident specifics | P0 |
| | ⚠️ **Testimony-vs-artefact watch:** Artefact 4.2 (Aki: "the 2024 thing") and artefact 4.3 (@sculpturedragon rule also tagged "after 2024 incident") may be referencing two separate events conflated under one label. Klaus distinguishes them: "that was the sponsor incident. Different." If Tom gives one coherent story that doesn't cleanly map to artefact 4.3's framing, do not smooth it over — the divergence is the lived-vs-documented gap. Record both versions and note the discrepancy explicitly. | | |
| 2 | "For IP claims that aren't from @sculpturedragon or @vintage_kitbasher — walk me through the last one you handled. What made it standard or not?" | IP triage criteria for non-named claimants | P0 |
| 3 | "When do you personally get pulled into a volunteer disagreement? Give me a real case where you did." | Escalation trigger: volunteer disagreement → Tom | P0 |
| | ⚠️ **Testimony-vs-artefact watch:** Artefact 4.2 shows Aki and Klaus resolving without Tom — but Aki's "Tom said before to be careful about harshness reports" implies Tom shaped the norm upstream even if absent from the decision. Tom may describe his role as more hands-off than the artefact implies (individual decisions) or more active (norm-setting). Either divergence is signal: if he says he rarely intervenes, the artefact evidence suggests he still influences outcomes indirectly; if he says he intervenes often, artefact 4.2 is an unrepresentative sample. Note which account he gives and cross-check against the actual example. | | |
| 4 | "Beyond the three accounts in your tracker, are there others — on your own list or the Senior Moderator's — that have informal handling rules?" | VIP list completeness | P1 |
| 5 | "In the 11 sub-forums not in your tracker — have you ever had to step in because a mod applied a local norm you weren't aware of?" | Undocumented sub-forum norms | P1 |
| 6 | "Who does what on an IP claim — you, the Senior Moderator, or shared? Where does the handoff happen?" | RACI on IP claims | P0 |
| 7 | "If we built a system that auto-removed obvious spam — what's the failure mode that would make you pull the plug on it?" *(Grounded in: Q7 effort analysis — spam = 19% of effort, 1,080 cases/day; Q6 scoping — founder's asymmetric-error principle was stated for sponsor/high-profile content, not spam; this question tests whether Tom extends the principle.)* | Risk tolerance for spam delegation | P0 |

---

## Build-Design Round (P1/P2 — surfaced by APD audit and build loop)

*These three depend on Tom's preference, not engineering. Add to the same interview if time allows; otherwise schedule a 30-min follow-up.*

| # | Question | Gap it closes | Priority |
|---|---|---|---|
| 8 | "If we ship Wave 1 with provisional confidence thresholds 0.6 and 0.8 — would you tolerate a 25–30% HITL rate during the first month of calibration, or is < 20% a hard floor from day one?" *(Grounded in: APD KPI pairing — Coverage ≥ 80% implies HITL ≤ 20%; calibration data does not yet exist.)* | HITL tolerance during Wave 1 calibration | P1 |
| 9 | "When the agent flags a VIP-account post (@vortex_minis, @sculpturedragon, @vintage_kitbasher) — (a) do you want a real-time Discord DM, or a batched summary at the start of your day? (b) Should the agent auto-hide the post pending your review, leave it visible until you decide, or remove-and-recover-on-disagree?" *(Grounded in: APD task 1.3E channel + visibility design; current draft assumes Discord webhook + auto-hide. The visibility question is high-stakes for sponsor accounts — auto-hide a sponsor's commercial post by default could itself be the failure mode.)* | VIP escalation routing + post visibility | P1 |
| 10 | "For the QA sampling of agent-dismissed items (5%/day) — would a Discourse tag you scan as part of existing review work, or a separate dashboard?" *(Grounded in: APD task 1.7Q surface design; current draft uses Discourse tag.)* | QA review surface preference | P2 |

---

## How questions map to artifact sections

| Question | Artifact section it tests | What changes if the answer differs from current draft |
|---|---|---|
| Q1 | APD failure modes (VIP miss); DSM Cluster 1 risk basis | If incident was a false-negative (post not removed), confirms current model. If false-positive (sponsor wrongly removed), VIP rule is calibrated for a *different* failure mode and the auto-hide default in 1.3E is exactly wrong. |
| Q2 | DSM Cluster 6 (Human Only); APD WS4 scope | If Tom has implicit triage criteria, WS4 may have agent-supportable sub-paths (currently zero). |
| Q3 | DSM Cluster 3 (grey-zone decision); APD Wave 2 scope | If Tom intervenes routinely, the volunteer queue routing for confidence < 0.6 may need a Tom-tier escalation for repeat consultations. |
| Q4 | APD VIP controlled-list service; DSM Cluster 1 control gap | If list is larger than 3, controlled-list service must be sized accordingly and governance is more critical. |
| Q5 | DSM Cluster 2 (sub-forum norms); APD Wave 2 prerequisite | If Tom has stepped in for undocumented norms, those norms exist as tacit knowledge — Wave 2 is harder than the brief implies. |
| Q6 | DSM Cluster 6 (IP claims); APD Wave 1 scope | If Senior Moderator owns non-named-claimant triage, build effort for any future IP-stream agent shifts owner. |
| Q7 | APD failure modes (false negative on spam); DSM Cluster 1 archetype | If Tom *does* extend the asymmetric-error principle to spam, autonomous removal must be reframed as agent-led + oversight, not a future fully-agentic candidate. |
| Q8 | APD KPI pairing (Coverage / HITL); deployment blockers (calibration) | If hard floor < 20% from day one, calibration must precede launch — pushes Wave 1 timeline. |
| Q9 | APD task 1.3E + escalation triggers + autonomy matrix + action mapping | If "leave visible" is preferred, four APD locations need updating and the auto-hide implementation in 1.3E is removed. |
| Q10 | APD task 1.7Q surface | Cosmetic to the agent design; affects ops/dashboard build cost only. |

---

## Out-of-Scope Notes

- These questions are pre-Gate-2. The 10-minute live clarification round on Friday afternoon (coach plays Tom) is the actual elicitation moment — these questions are the prepared agenda, not the substitute.
- AI-proxy reconstructions of Tom's likely answers are in `01_elicitation_log.md` (Q1–Q8). Those are simulation, not testimony — do not cite them as Tom-confirmed.
