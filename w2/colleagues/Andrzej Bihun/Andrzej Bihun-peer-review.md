# Peer Review — Andrzej Bihun (Scenario 4: MiniBase Content Moderation)

**Reviewer:** Krzysztof Wilniewczyc *(with a little help from AI :D)*
**Date:** 2026-05-04
**Submission scope:** 7 markdown files (CLAUDE.md, 03–08 deliverables) + presentation PDF

---

Hi Andrzej — full disclosure: I worked the same scenario, so I came in with strong opinions about MiniBase before opening your files. That made reading your submission more interesting, because you went in genuinely different directions on several decisions, and a lot of them were sharp. Below: first what's working, then a small handful of things I'd flag for a second look. Take the second half as friendly nudges, not gotchas.

---

## Part 1 — What's working well

### 1. The value/risk asymmetry framing is the strongest I've seen
Tom's "false positives are survivable; one viral false negative is existential" line shows up in your work as **load-bearing design pressure**, not just a quote on the side. It actually shapes the autonomy matrix, the escalation triggers, the confidence thresholds, and the phasing. Most submissions paste the line in and forget it; yours uses it.

### 2. "Context automation ≠ decision automation" is the move of the week
Your Phase 3 design where the agent fully automates **grey-zone context gathering** (TC-2A, score 65/70, Fully Agentic) but leaves the **judgment** to humans (TC-2B, score 34/70, Human-Led + Support) is exactly the FDE-level decomposition the rubric is hunting for. Pulling £108K/yr out of grey-zone *without* delegating any decision risk is a clean piece of arbitrage — I wish I'd structured my own work this way.

### 3. The 7-dimension scoring rubric is rigorous
Codifiability / Data Availability / Volume / Cognitive Load / Risk of Error / Reversibility / Consistency, each scored 0–10 with rationale per dimension per task cluster. Even where someone might want to argue with individual scores, the **structure** makes disagreement productive — you can point at "this is a 9/10 not a 6/10 because…" rather than waving at the whole archetype assignment.

### 4. Discovery questions with decision trees
Q1 (the 2024 sponsor incident) with three branched answers each mapped to specific design changes is exactly what the rubric means by "questions whose answers would materially change the design." The severity tagging (🔴 Critical / 🟡 High / 🟢 Medium) and the "how to ask" sub-sections turn this into something a coach could actually role-play against. Q5 (watchlist completeness — "are there accounts just in your head?") is the sharpest one in the file.

### 5. The compounding roadmap and integration-reuse matrix
Three waves, with explicit "✓ Build" / "✓ Reuse" markings per integration per phase, and the observation that "Phase 1-2 builds 60% of infrastructure for Phase 3-4." That's the exact compounding logic from `atx-agent-mapping.md` applied seriously. The compounding-value chain at the end of `05_Volume_Value_Analysis.md` (spam saved → grey-zone capacity → fewer errors → fewer appeals → less Tom load → trust ↑ → revenue ↑) is the kind of second-order thinking that lifts this above a checklist exercise.

### 6. Memory architecture and prompt-engineering principles in the APD
You actually fill out the Memory Architecture table from the agent-mapping reference (in-context / episodic / semantic / procedural / **operational** — adding the operational tier for Tom's watchlist is a smart extension). The structured JSON context card has the right keys for an actual builder to wire up.

### 7. Failure-mode analysis is exhaustive
Four named failure modes (viral false negative, established-member false positive, context incompleteness, drift) each with prevention controls mapped to specific agent behaviour. Drift detection — "does 0.9 confidence still equal 90% accuracy after 6 months?" — is the kind of failure mode most submissions don't consider.

### 8. KPI tiering is genuinely useful
Tier 1 Safety (non-negotiable) → Tier 2 Quality → Tier 3 Efficiency → Tier 4 Cost, with the explicit rule "when metrics conflict, safety beats efficiency beats cost." Clear contract for how to make trade-off calls during build.

---

## Part 2 — A few things worth a second look

### A. The fabricated stakeholder "Sarah" is the biggest one
Across CLM, DSM, APD, V×V, and Discovery Qs there are **28+ direct quotes attributed to a "Sarah"** described as a Senior Moderator. A few examples:

- *"That boundary is so cultural, so context-dependent... I think AI would either be too aggressive or too permissive."* (CLM line 750, DSM line 353, V×V line 797)
- *"20% of my time is just clicking between tools."* (DSM line 294)
- *"3 false positives in 3 years."* (DSM line 107)
- *"Just make it go away."* (APD line 216)
- *"I think... harassment targets the person, critique targets the work? But that's not always clear."* (DSM line 337)

The brief has no Senior Moderator named Sarah. The Senior Moderator is referenced but unnamed; Aki and Klaus appear *only* as Discord usernames in a single artefact (4.2) discussing one specific case, not as people interviewed. Your docs elevate them to "Japanese moderator with cultural expertise" / "German directness" with design-load-bearing conclusions ("Aki personally reviews Japanese sub cultural cases").

The Week 2 brief flags this directly — *"Stating client behaviour or system internals as fact when the brief did not give it to you is the most common Week 2 failure mode. Marked assumptions with confidence levels are the alternative."* The risk is that those quotes read as elicited evidence and get discounted, which would unfairly weaken otherwise-strong design decisions (TC-2A's 65/70 doesn't actually need Sarah to defend it — the dimension scores stand on their own).

**Two fix paths, either works:**
1. **Rename and re-frame:** swap each "Sarah said X" for `[Inferred from artefact 4.X — Medium confidence]` or `[AI-proxy stakeholder simulation — Low confidence, validate in role-play]`. The *content* of the inferences is mostly reasonable; it's the unmarked sourcing that's the issue.
2. **Add a stakeholder ledger up front** in CLAUDE.md: "Real stakeholder = Tom (named in brief). Other moderator perspectives are AI-proxy simulations or inferences from artefacts; quotes are reconstructions for design pressure-testing, not transcripts."

This is the only finding I'd call gate-blocking. The rest below are smaller.

### B. Spam category breakdowns are inferred but presented as fact
In CLM Task 1.3 you list:
- Link farm: ~300/day, Crypto/forex bot: ~200/day, Gibberish: ~150/day, Off-topic commercial: ~250/day, Duplicate post: ~100/day, Miscategorised: ~80/day

That sums to 1,080/day — matching the brief's WS1 total — but the **breakdowns themselves are nowhere in the brief**. They drive downstream sequencing logic ("focus Phase 1 on link farms because they're 28% of spam") and £-value calculations. **Quick fix:** one line at the top of the table — `[Per-category breakdowns inferred from typical spam taxonomies; totals reconcile to brief but per-category volumes need stakeholder validation]`.

### C. Submission volume is overwhelming for a 25-min peer review
Total: **6,470 lines** across 7 files. CLAUDE.md alone is **672 lines** — larger than many participants' entire submissions. The required deliverables average **900+ lines each** (CLM is 1,280; APD is 1,058).

The peer review window allocates ~25 min per submission — a reviewer probably won't read all of this carefully and will end up skimming, meaning some of your best material (the context-automation insight, the compounding chain) gets lost in the bulk. There's also significant duplication: CLAUDE.md restates ~40% of the APD; each deliverable opens with a 30-line executive summary that re-covers ground from earlier deliverables.

**Two paths:**
- *(If time):* trim by ~50% — drop the in-deliverable executive summaries, slim CLAUDE.md to ~150–200 lines (it's a workflow doc, not another deliverable), and trust that the APD doesn't need a long preamble.
- *(If no time):* at least add a **"reviewer's path"** to CLAUDE.md — "if you only read 3 sections, read these: §APD Autonomy Matrix, §V×V Insight 3 (context vs decision), §Discovery Q1 + Q5."

### D. The 0–70 scoring scale isn't from the ATX reference
The methodology pack uses **H/M/L** on 7 dimensions (Input Structure, Decision Determinism, Tool Coverage, Context Complexity, Exception Rate, Latency, Risk/Compliance). You've replaced this with 0–10 across a different 7-dimension set (Codifiability, Data Availability, Volume, Cognitive Load, Risk of Error, Reversibility, Consistency) summed to /70. The scoring is rigorous, but it's not what `atx-scoring.md` defines — and the priority formula in `05_Volume_Value_Analysis.md` (`Priority = Volume × Value × Delegation Suitability / Risk`) is fully bespoke too.

It's not strictly *wrong*, and your scale is arguably more legible — but a coach scoring against the rubric will notice the divergence. **Fix:** add a one-paragraph note at the top of DSM saying "I'm using a 0–10 × 7 = /70 scale instead of the H/M/L scale from `atx-scoring.md` because [reason]; the archetype-assignment thresholds are calibrated against the methodology's qualitative bands." Makes the divergence intentional rather than accidental.

### E. Cost figures are precise to a level the inputs don't support
£49,284/yr, £108,414/yr, £14,300 implementation, 10.8:1 ROI, 18.7:1 risk-adjusted. The precision implies an analytical confidence the underlying assumptions (£15-20/hr blended rate, 7 hrs/day saved, etc.) don't support — they're estimates compounded on estimates. **Fix:** round to the nearest £5K (£50K/yr, £110K/yr, £15K) and switch the ratios to "approximately 10:1." Same conclusion, honest precision.

---

## Lived-work vs documented-process check

Pass. The painters "no critique without invitation" sub-rule, the historical-sub permissiveness, Tom's Google-Sheet tracker, the 2024 sponsor incident, and the cultural-interpretation surface (Japanese painters sub) all show up as design pressure, not just recited brief content. The only concern is the one in finding A above — some lived-work claims are sourced to the fabricated Sarah persona rather than to artefacts directly.

---

## Delegation-archetype calibration check

Very strong pass. Your archetype mix (58% Fully Agentic / 25% Agent-Led / 14% Human-Led / 3% Human-Only) is justified per-cluster, not assumed. **TC-2D (cultural interpretation, 21/70, Human-Only with agent escalation flagging only)** is particularly well-handled — explicitly *refusing* even agent-supported context because "agent support would be misleading" is the kind of restraint the rubric rewards.

One push-back: **TC-2A (context gathering) at 65/70 → Fully Agentic** is correct *as a delegation pattern*, but the sub-tasks within it (e.g. "determining 'relevant' precedent requires some semantic judgment" — your own note in the Codifiability rationale) make Fully-Agentic-with-sampling more honest than pure Fully-Agentic. Worth a sentence acknowledging the precedent-search semantic judgment as a quality-check breakpoint.

---

## AI-ingestibility grade

**Score: 2.5 / 5**

This is the place where the *quality* of your thinking is being undercut by the *volume* of the artefacts.

**What works:** structured tables throughout, consistent dimension legends, JSON context card schema, explicit memory-architecture table — all good for an LLM consumer.

**What hurts the score:**
1. **Volume.** A model loading the full submission as context burns tokens reading the same metric definitions 3-4 times across CLAUDE.md, APD, V×V, and CLM executive summaries. Most consumers will hit a context limit before reaching your strongest content.
2. **Inferred content presented as fact.** A builder LLM ingesting your APD would encode the Sarah quotes, the per-category spam volumes, and the precise £-figures as ground truth. Worse than a human reader, who'd at least notice "wait, who's Sarah?"
3. **Bespoke-scale scoring** without explicit calibration to the ATX reference will confuse a model that's also been given the ATX docs — it has to reconcile two scoring systems.

The single highest-leverage fix is point A (label the inferred content). Volume reduction is a close second.

---

## Calibration note

Tracking toward a Gate-2 pass on substance, with execution-level housekeeping to do — the design thinking and methodology depth are clearly above the bar; what could undercut you is point A (the unmarked-inference issue) being read as bluffed domain knowledge, plus the volume making it hard for a reviewer to find your best material.

---

Genuinely strong submission, Andrzej — the context-vs-decision insight in particular is something I'm tempted to borrow for my own thinking.

— Krzysztof
