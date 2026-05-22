# Pre-Interview Brief Analysis & Design Hypotheses
**Scenario 4 — Community Content Moderation**
**Subject:** Tom Włodarczyk, Community Manager, MiniBase
**Method:** AI proxy simulation constrained to brief content (artefacts 4.1–4.3, founder brief, tooling sketch)
**Date:** 2026-04-30

> **Epistemic status:** The TOM: sections below are AI proxy reconstructions from brief artefacts — not real stakeholder testimony. Every [Stated] tag means "present in the brief," not "confirmed by Tom." Open gaps are gaps in the brief, not failures of elicitation. This document is input to a real stakeholder interview, not a substitute for one.
>
> **Note on archetype assignments:** A provisional delegation archetype table appeared in an earlier draft and was withdrawn as premature. Archetype assignment requires exception-rate data, reversibility evidence, and escalation boundary confirmation — none of which are available from the brief alone. Archetypes will be assigned in the Delegation Suitability Matrix after the stakeholder interview.

---

## Confidence Rubric

| Level | Definition |
|---|---|
| **High** | Corroborated by ≥2 independent artefacts or brief statements; no plausible alternative interpretation |
| **Medium** | Single artefact or brief statement; plausible mechanism; alternative interpretations possible |
| **Low** | Inference from context only; no direct artefact support; requires stakeholder confirmation |

---

**Q1: The 2024 sponsor incident — what rule did it create?**

TOM: There was an incident with our main sponsor account — @vortex_minis. The outcome is a standing rule: I personally review every commercial post from that account. No volunteer handling, no auto-flagging.

`[Stated: artefact 4.3]`
`OPEN (Brief gap): Nature, severity, and what specifically went wrong are not in the brief.`
`OPEN (Stakeholder gap): Whether the rule is correctly calibrated for the actual incident, and whether it should generalise to future sponsor relationships, can only be answered by Tom.`
`DESIGN NOTE: Account IDs should provisionally trigger human-only routing via controlled-list lookup, not classifier output, pending governance confirmation.`
`[Inferred: deterministic VIP routing is the safer provisional choice given explicit standing rule and asymmetric risk tolerance stated by founder; confidence: High]`

---

**Q2: How many accounts have standing individual rules?**

TOM: Three named accounts: @vortex_minis (sponsor), @sculpturedragon (established sculptor with recurring IP claims), and @vintage_kitbasher (IP credibility unclear, watch for retaliatory reports). Beyond those, no other explicit standing rules are documented.

`[Stated: artefact 4.3 — exactly 3 account-specific rows]`
`OPEN (Brief gap): The tracker is Tom's personal document. Absence from it ≠ absence in practice. Senior moderator or volunteers may carry undocumented standing rules for other accounts. Population completeness is unconfirmed.`
`DESIGN NOTE: Treat 3 as the known minimum, not a closed list. Controlled configuration with explicit governance for additions.`
`[Inferred: VIP list must be treated as controlled configuration rather than classifier input until completeness is confirmed by both Tom and Senior Moderator; confidence: Medium]`

---

**Q3: Sub-forum norms — what's not in the global policy?**

TOM: Three documented gaps. Painters sub: "no critique without invitation" — critique threads make invitation implicit, so it's context-dependent. Historical sub: more permissive on historically-charged imagery; don't apply the global controversial-imagery rule strictly. Japanese painters sub: English critiques read harsher than intended — soft-warning before any removal action.

`[Stated: artefact 4.3 — all three rows explicit]`
`OPEN (Brief gap): 14 sub-forums exist; only 3 norms are documented. Whether the other 11 have undocumented norms is unknown.`
`DESIGN NOTE: Sub-forum ID is a required routing input. Norms should be structured data, not PDF-only text, pending validation of exception handling.`
`[Inferred: structured norm data is needed for reliable runtime enforcement; confidence: High — two independent supports: (1) artefact 4.3 explicitly flags 3 norms as "not in global policy"; (2) 14 sub-forums documented vs 3 norms = structural coverage gap]`

---

**Q4: When volunteer mods disagree, what's the resolution path?**

TOM: They work it out in the #mod-decisions Discord channel. One of them logs the final call in Discourse with a rationale note.

`[Stated: artefact 4.2 — one exchange between Aki and Klaus, resolved without Tom]`
`OPEN (Brief gap): One observed case. Cannot generalise the resolution pattern.`
`OPEN (Stakeholder gap): Conditions under which Tom is pulled in are not stated anywhere in the brief.`
`DESIGN NOTE: Discord is the inter-moderator coordination surface. Decisions are made outside Discourse before being logged in it. A Discourse-only agent integration would miss the deliberation layer.`
`[Inferred: missing Discord visibility creates decision-context loss risk; confidence: Medium — single data point only]`

---

**Q5: IP claims — who handles them and how are they triaged?**

TOM: Email is the intake channel. @sculpturedragon I review personally every time — established sculptor, recurring pattern, standing rule since 2024. @vintage_kitbasher gets standard escalation, no fast-track; their credibility is uncertain. For other claimants I can't give you a detailed breakdown right now.

`[Stated: artefact 4.3, tooling sketch]`
`OPEN (Brief gap): Triage criteria for non-named claimants are not described anywhere in the brief.`
`OPEN (Stakeholder gap): Who handles non-@sculpturedragon claims — Tom, Senior Moderator, or shared — is not stated. RACI is unknown.`
`DESIGN NOTE: IP stream (3–5/wk) is provisionally out of autonomous agent scope until triage criteria and ownership are documented.`
`[Inferred: recommendation-only agent support is the safe default until triage rules are explicit; confidence: Medium — single artefact absence (no criteria in brief) + plausible mechanism; no second independent support]`

---

**Q6: What failure mode do you fear most with automated moderation?**

TOM: A missed removal on content involving a sponsor or high-profile account that spreads before we catch it. That's the founder's position and it shapes how I think about risk tolerance here.

`[Stated: founder brief "False positives are survivable; one viral false negative is existential"; artefact 4.3 "THE 2024 SPONSOR — never get this wrong"]`
`[Inferred: Tom's personal alignment with founder position — consistent with artefacts but not explicitly stated; confidence: Medium]`
`DESIGN NOTE: Asymmetric error tolerance is explicit. Provisional policy: below-threshold confidence routes to human review, not auto-approve. Applies specifically to sponsor/high-profile content — the founder's concern does not explicitly extend to routine spam false negatives.`
`[Inferred: conservative threshold is the correct design response given stated asymmetry; confidence: High]`

---

**Q7: Where does the team's time actually go?**

TOM: Grey-zone cases are the biggest load by far. Routine spam is high volume but fast. Appeals are draining because they require decision context. IP claims are rare.

`[Stated: brief volumes and handling times]`

Effort by stream — calculated from brief, denominator = 10-person team (8 volunteer mods + 2 paid staff), total brief-stated effort = 47 hrs/day:

| Stream | Volume/day | Time/case | Total hrs/day | % of team effort |
|---|---|---|---|---|
| Grey-zone review | 360 | 5 min | 30.0 | 64% |
| Routine spam | 1,080 | 0.5 min | 9.0 | 19% |
| Appeals | 60 | 8 min | 8.0 | 17% |
| IP claims | ~0.6 | 30 min | 0.3 | <1% |
| **Total** | | | **47.3** | ✓ matches brief |

`[Derived: percentages computed from brief volumes and times, not confirmed by Tom]`
`DESIGN NOTE: Grey-zone dominates total team effort (64%). Routine spam is volume-dominant but time-cheap (19%). Two distinct design targets: routine spam → full-delegation candidate; grey-zone → effort-reduction candidate requiring human oversight at decision point. Separate agent designs required.`
`[Inferred: provisional delegation hypothesis; requires exception-rate and reversibility evidence before archetype assignment; confidence: Medium]`

---

**Q8: Do volunteers know about the VIP account rules?**

TOM: Sub-forum mods know their own sub's norms — they apply them. The account-specific rules in my tracker are not shared with volunteers. That document goes to the senior moderator only.

`[Stated: artefact 4.3 "Shared with the senior moderator only; not in the volunteer Discord"]`
`[Inferred: sub-forum mods know their own norms — one confirmed case (Aki, painters sub, artefact 4.2); cannot generalise to all 14 subs; confidence: Low]`
`DESIGN NOTE: VIP routing logic must be system-level, not visible in volunteer-facing tooling.`
`[Design hypothesis — not inferred from Tom: hiding VIP logic from volunteer UI may reduce gaming and leakage risk. This framing is not from the brief; needs stakeholder validation.]`

---

## Elicitation Summary

| Finding | Source | Status |
|---|---|---|
| 3 named accounts with individual standing rules | Artefact 4.3 | Stated in brief |
| 3 sub-forum norm gaps from global policy | Artefact 4.3 | Stated in brief |
| Asymmetric error tolerance (FN >> FP) | Founder brief + artefact 4.3 | Stated in brief |
| Grey-zone = 64% of total team effort | Calculated from brief | Derived |
| VIP rules not visible to volunteers | Artefact 4.3 | Stated in brief |
| 2024 incident specifics | — | **Brief gap + Stakeholder gap** |
| IP triage criteria for non-named claimants | — | **Brief gap + Stakeholder gap** |
| Tom vs Senior Moderator RACI on IP claims | — | **Brief gap + Stakeholder gap** |
| Escalation trigger: volunteer disagreement → Tom | — | **Stakeholder gap only** |
| VIP list completeness beyond 3 named accounts | — | **Stakeholder gap only** |
| Norms in remaining 11 sub-forums | — | **Brief gap (partial) + Stakeholder gap** |

---

## Open Gap Register

### Brief Gaps
*Answerable via additional documentation — request from client before interview.*

| Gap | Priority | Confidence | Design Impact | What to Request |
|---|---|---|---|---|
| IP triage criteria for non-named claimants | P0 | Low | High | Any SOP, checklist, or decision log for IP claim handling |
| Undocumented norms in remaining 11 sub-forums | P1 | Low | Medium-High | Request moderation decision log export by sub-forum (do not assume Discourse API structure supports this) |
| Governance process for VIP list | P2 | Low | Medium | Any existing process doc for account-level policy exceptions |

### Stakeholder Gaps
*Require real interview with Tom (and possibly Senior Moderator). Cannot be resolved from brief.*

| Gap | Priority | Confidence | Design Impact | Interview Target |
|---|---|---|---|---|
| 2024 sponsor incident — what happened | P0 | Low | High | Tom: needed to assess whether @vortex_minis rule is correctly fitted and generalisable |
| Tom vs Senior Moderator RACI on IP claims | P0 | Low | High | Tom + Senior Moderator: needed to scope IP agent design boundary |
| Escalation trigger: volunteer disagreement → Tom | P0 | Low | High | Tom: needed to define grey-zone agent handoff conditions |
| VIP list completeness — accounts beyond the 3 named | P1 | Low | High | Tom + Senior Moderator: controlled list cannot be built on incomplete data |
| HITL tolerance during Wave 1 calibration | P1 | Low | Medium | Tom: determines whether ≥80% coverage KPI can be relaxed during first month |
| VIP escalation routing preference (real-time vs batched) | P1 | Low | Medium | Tom: determines Discord webhook vs Discourse-category-only routing |
| QA sampling surface (existing dashboard vs new) | P2 | Low | Low-Medium | Tom: determines build cost of QA review surface |

---

## Real Stakeholder Interview Plan

**Extracted to standalone deliverable: see `06_discovery_questions.md`** for the full 10-question interview agenda, conflict-watch notes, gap-closure mapping, and stakeholder/format details.

This file (01) retains the AI-proxy elicitation analysis (Q1–Q8 simulated answers, confidence rubric, gap register) — that is the *analysis* artifact. The interview plan itself (Q1–Q10) is the *discovery questions* artifact (deliverable #6) and lives in 06.
