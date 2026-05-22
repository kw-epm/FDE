# D#6 Client Feedback Response

*To: Marcus Reyes*
*From: Krzysztof Wilniewczyc, FDE Programme*
*Date: Friday, 15 May 2026*
*Subject: Re: Three things, response in detail*

---

Hi Marcus,

Hope you got some sleep between flights. You're right on all three. Here's what changes.

## 1. Timeline. You're right, we should ship in week 1, not measure in week 1

You read my D#2 risk row correctly. *"Week 1 reserved for instrumentation, improvement clock starts week 2"* is a 7-week build dressed as 8, and I can see how it pattern-matches the dead first month of your two prior AI projects. That's a fair call, and I'm happy to concede it.

**Here's the revised plan.** Week 1 ships a thin live increment that coordinators can actually use. Specifically, the **intake parser** for the v1 specialty (slice to be confirmed Monday; please see point 2 below). The agent reads inbound free-text shift requests from ServiceNow and extracts structured intent (specialty, dates, location, credential requirements) into a field coordinators can click. It's the smallest useful piece of the architecture. Coordinators stop manually re-typing what hospitals have already written.

**Baselines come along for the ride.** Every message the parser processes gets timestamped, so by end of week 1 we have request-arrival and parse-completion times on real data. No separate measurement effort.

- **Week 2.** Candidate ranking ships. Coordinators see ranked shortlists with reasoning. Manual approval on every offer.
- **Week 3 to 4.** Trust ramp moves high-confidence cases to autonomous send.
- **Week 6.** Numbers ready for your board update. Request-to-hospital-submission drop measured against the week-1 baseline that ran inside the live system. Hospital acceptance rate. Override rate trend.

I'd noted the 8-week milestone in my Thursday plan; clearly the board update at week 6 is the actual clock. Noted, and adjusted accordingly.

## 2. Slice. You're right, "working hypothesis" isn't a decision

I picked ICU + 2 hospitals from healthcare industry norms (high-volume, high-margin, uniform credentials) without grounding it in MedFlex's actual workload. That's a placeholder, not a decision. A fair point, and I appreciate the clarification.

**I'd very much like to take you up on the Monday 30-minute slot with Head of Ops.** That's exactly the conversation we need, and thank you for setting it up. Here's how I'll come prepared.

**Criteria I'll use to decide the slice:**

1. **Volume.** At least ~15 fills/day on the slice, so the mismatch and no-show baselines are statistically meaningful by week 4. Below that threshold, the signal is buried in noise.
2. **Hospital partners.** Two hospitals willing to participate AND with at least 12 months of MedFlex history. The agent reasons over historical acceptance patterns; if there's no history, there's nothing to reason over.
3. **Coordinator depth.** At least one experienced coordinator familiar with the slice as the calibration signal for the trust ramp.
4. **Manageable credential complexity.** v1 already has many moving parts; picking a specialty with high state-by-state credential variance would compound risk unnecessarily.
5. **Visible impact at week 6.** Material enough that "the slice works" reads as business progress, not as a pilot footnote.

**Five questions I'll bring into the 30 minutes:**

1. Fills/day breakdown by specialty. Which give us ≥15/day?
2. Which two hospital accounts would be willing to participate AND have 12+ months of MedFlex history?
3. Which coordinator has the deepest experience on each candidate specialty?
4. Is historical hospital acceptance/rejection data complete on the candidates, or patchy?
5. Are there specialties or hospitals we should avoid in v1, politically, technically, or contractually?

**By Monday EOD**, I'll have the slice locked in writing, with the reasoning. If ICU survives the conversation, you'll have the data that confirms it. If Med-Surg or Telemetry surfaces instead (same paper trail, different answer), you'll have it before Monday board prep.

I appreciate that knowing in week 1 is much more valuable than knowing in week 3. Agreed on every count.

## 3. CFO. A fair point. Here's a number, with the math.

On this one, I owe both you and your CFO a careful answer.

You told me at discovery that cost-per-shift wasn't relevant, and I took you at your word. Built the framing around throughput. Your CFO is reading the same line and disagreeing, and he's the one writing the board deck. That's a completely reasonable reversal, and please pass my apologies along to him for not anchoring on dollars in the original framing.

The honest situation: I don't have MedFlex's unit economics yet, because you (very reasonably) didn't share them at discovery. So what follows is back-of-envelope using public healthcare-staffing industry numbers, with every assumption explicitly flagged. **If the CFO can share the unit economics (revenue interpretation, net per shift) and Head of Ops can share the operational rates (slice volume, competitive-loss, no-show breakdown) on Monday, the precision will tighten significantly.**

### Year-1 contribution impact on the slice (illustrative, not committed)

**Caveat first:** the numbers below are *illustrative contribution impact*, not committed revenue. The math depends on what "$14M revenue" actually represents in MedFlex's accounts: net agency revenue (your cut after paying the nurse) vs. gross billings (what hospitals pay before you pay the nurse). Two different answers. **CFO can confirm which figure is meant.** That single clarification shifts the math materially.

**Working assumptions (placeholders, to be replaced Monday):**

- **MedFlex's net revenue per filled shift:** ~$300 (industry norm: agency typically keeps 15 to 25% of a ~$1,500 to $2,000 hospital bill rate; using mid-range $300 as the agency's net per fill). If $14M is gross billings instead, the per-shift figure is closer to $1,800 and volume is roughly 6× lower.
- **Total fills/day at $14M net revenue:** $14M ÷ $300 ÷ 250 working days ≈ **~184 fills/day** *(if $14M = net agency revenue)*.
- **Placeholder slice volume:** ~10 to 20 fills/day across the two chosen hospitals, illustrative only, since the slice is ICU at 2 specific hospitals, not ICU across all MedFlex. Actual slice volume is a slice-selection question for Monday's Head of Ops conversation.

### Three improvement levers, illustrative math at 15 fills/day on the slice

| Lever | Math | Year-1 contribution impact |
|---|---|---|
| **Speed recovery** (shifts currently lost to faster competitors) | 15 × 30% lost × 50% recoverable × $300 × 250 | **~$170K** |
| **Mismatch reduction** (7% to ~3% on slice) | 4pp × 15 × $300 × 250 | **~$45K** |
| **No-show reduction** (12% to ~8% on slice, conditional on Decision 2) | 4pp × 15 × $300 × 250 | **~$45K** |
| **Year-1 contribution impact on the slice (illustrative)** | | **~$260K** |

Plausible range with the placeholder volume (10 to 20 fills/day) and the speed-recovery assumption (which is the single biggest uncertainty): **~$150K to ~$400K**.

### Across MedFlex, scaled

If the slice works and the architecture extends to the rest of MedFlex's fill volume, the same three levers extrapolate to roughly **$2M to $5M/year addressable contribution** at current scale. Directionally large, but the precise number depends entirely on the revenue/margin clarification and the slice-extension rate. That's the foundation of the path to $200M; the architecture is designed to absorb ~14× decision volume to get there.

### What would let me give the CFO a real number, not an illustration

Five things, ideally clarified on Monday morning before board prep:

1. **Confirm what "$14M revenue" represents** in your accounts: net agency revenue or gross billings? (single biggest math input)
2. **MedFlex's actual net revenue per filled shift,** to replace the $300 industry norm.
3. **Volume on the chosen 2-hospital slice,** replaces the 10 to 20 fills/day placeholder.
4. **Actual competitive-loss rate.** What percentage of MedFlex submissions today lose to a faster competitor?
5. **Whether the no-show rate breakdown** (~2pp structural cross-agency double-acceptance vs. ~10pp addressable) is roughly right.

With those five clarifications, the year-1 figure becomes a real number rather than an illustration. If some aren't readily available, please flag. I'd rather know what's missing than carry unknowns forward.

---

## Summary, by when, what

- **Today (Friday):** this response. Revised plan + the illustrative calculation above.
- **Monday morning:** 30-min with Head of Ops. Five questions on the slice, five clarifications for the CFO.
- **Monday afternoon, ahead of board prep:** slice locked in writing. Revised year-1 number using real MedFlex inputs. Both go to you and the CFO directly.
- **Tripwire:** if the Head of Ops conversation surfaces something that can't resolve in 30 minutes, I'll flag Monday morning. Better you adjust the board prep window than walk into it with an unfinished number.
- **Week 1 (project):** intake parser live on real ServiceNow records. Coordinators see it working. Baselines captured by the running system.
- **Week 6:** board-defensible numbers from real production data.

Thanks for raising these now rather than later. Easier to course-correct in week 1 than in week 3.

Kind regards,
Krzysztof

-- 
Krzysztof Wilniewczyc
FDE Programme | EPAM Systems (Switzerland) GmbH
Boulevard Lilienthal 2, 8152 Opfikon, Switzerland
