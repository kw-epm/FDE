# Stakeholder Elicitation Log
**Scenario 4 — Community Content Moderation**
**Stakeholder:** Tom Włodarczyk, Community Manager, MiniBase
**Method:** AI proxy (brief-constrained)
**Date:** 2026-04-30

---

**Q1: The 2024 sponsor incident — what rule did it create?**

TOM: There was an incident with our main sponsor account — @vortex_minis. The outcome is a standing rule: I personally review every commercial post from that account. No volunteer handling, no auto-flagging.

`[Stated: artefact 4.3]`
`OPEN: What specifically happened is not in the brief. Nature, severity, and whether it was public are unknown.`
`DESIGN NOTE: Specific account IDs should provisionally route to human-only review via controlled-list lookup (not classifier-only output), pending governance confirmation.`
`[Inferred: deterministic VIP routing is a safer design choice; confidence: Medium]`

---

**Q2: How many accounts have standing individual rules like that?**

TOM: Three named accounts: @vortex_minis (sponsor), @sculpturedragon (established sculptor with recurring IP claims), and @vintage_kitbasher (IP credibility unclear, watch for retaliatory reports). Beyond those, I have no other explicit standing rules documented.

`[Stated: artefact 4.3 — exactly 3 account-specific rows]`
`DESIGN NOTE: VIP account list has exactly 3 known entries. No evidence of additional accounts — do not assume.`
`[Inferred: list should be treated as controlled configuration until governance is clarified; confidence: Medium]`

---

**Q3: Sub-forum norms — what's not in the global policy?**

TOM: Three documented gaps. Painters sub: "no critique without invitation" — but critique threads make invitation implicit, so it's context-dependent. Historical sub: more permissive on historically-charged imagery; don't apply the global controversial-imagery rule strictly. Japanese painters sub: English critiques read harsher than intended — soft-warning before any removal action.

`[Stated: artefact 4.3 — all three rows explicit]`
`OPEN: Whether other sub-forums have undocumented norms is unknown. The brief covers 14 sub-forums; only 3 norms are documented here.`
`DESIGN NOTE: Sub-forum ID should be treated as a required routing input. Norms should be captured as structured data (not PDF-only text), pending validation of exception handling.`
`[Inferred: structured norm data is needed for reliable enforcement at runtime; confidence: Medium]`

---

**Q4: When volunteer mods disagree, what's the resolution path?**

TOM: They work it out in the #mod-decisions Discord channel. One of them logs the final call in Discourse with a rationale note.

`[Stated: artefact 4.2 — Aki and Klaus exchange, Aki logs decision]`
`OPEN: Whether Tom is pulled in for escalation, and under what conditions, is not stated. Artefact 4.2 shows one resolved case without Tom involvement — cannot be generalized.`
`DESIGN NOTE: Discord is the inter-moderator coordination surface, not Discourse. Any agent integration must account for decisions being discussed outside the primary platform.`
`[Inferred: missing Discord visibility creates decision-context loss risk for any Discourse-only agent; confidence: High]`

---

**Q5: IP claims — who handles them and how are they triaged?**

TOM: Email is the intake channel. @sculpturedragon claims I review personally every time — established sculptor, recurring pattern, standing rule since 2024. @vintage_kitbasher gets standard escalation, no fast-track; their credibility is uncertain. For other claimants, I can't give you a detailed breakdown right now.

`[Stated: artefact 4.3, tooling sketch]`
`OPEN: Triage criteria for non-named claimants are not in the brief. Who handles non-@sculpturedragon claims (Tom vs Senior Moderator) is not stated. This is a genuine gap — do not infer.`
`DESIGN NOTE: IP stream is low volume (3–5/wk) and currently human-handled. Provisionally keep out of autonomous scope until triage criteria are documented.`
`[Inferred: agent support should stay recommendation-only for IP claims until triage rules are explicit; confidence: High]`

---

**Q6: What failure mode do you fear most with automated moderation?**

TOM: A missed removal on content involving a sponsor or high-profile account that spreads before we catch it. That's the founder's position and it shapes how I think about risk tolerance here.

`[Stated: founder brief "False positives are survivable; one viral false negative is existential"; artefact 4.3 "THE 2024 SPONSOR — never get this wrong"]`
`[Inferred: Tom's personal alignment with founder position — reasonable but not explicitly stated]`
`DESIGN NOTE: Asymmetric error tolerance is explicit (false negative cost >> false positive cost). Provisional policy: when confidence is below threshold, route to human review rather than auto-approve.`

---

**Q7: Where does the team's time actually go?**

TOM: Grey-zone cases are the biggest load by far. Routine spam is high volume but fast. Appeals are draining because they require decision context. IP claims are rare.

`[Stated: brief volumes and handling times]`

Effort by stream (calculated from brief):

| Stream | Volume/day | Time/case | Total hrs/day | % of effort |
|---|---|---|---|---|
| Grey-zone review | 360 | 5 min | 30.0 | 64% |
| Routine spam | 1,080 | 0.5 min | 9.0 | 19% |
| Appeals | 60 | 8 min | 8.0 | 17% |
| IP claims | ~0.6 | 30 min | 0.3 | <1% |
| **Total** | | | **47.3** | ✓ matches brief |

`DESIGN NOTE: Grey-zone dominates total effort (64%). Routine spam is volume-dominant but time-cheap (19%). These are different design targets: routine spam is a provisional full-delegation candidate; grey-zone pre-triage is a provisional high-value effort-reduction candidate. Keep separate agent designs pending exception-rate evidence.`
`[Inferred: provisional delegation hypothesis only; requires exception-rate and reversibility evidence before archetype lock-in; confidence: Medium]`

---

**Q8: Do volunteers know about the VIP account rules?**

TOM: Sub-forum mods know their own sub's norms — they apply them. The account-specific rules in my tracker are not shared with volunteers. That document goes to the senior moderator only.

`[Stated: artefact 4.3 "Shared with the senior moderator only; not in the volunteer Discord"]`
`[Inferred: sub-forum mods know their own norms — supported by artefact 4.2 (Aki knows painters sub norm) but only one sub confirmed]`
`DESIGN NOTE: VIP routing logic must be system-level, invisible to volunteer-facing tooling. Sub-forum norms can be documented in a structured table accessible to the system.`
`[Inferred: hiding VIP logic from volunteer UI reduces gaming and leakage risk; confidence: Medium]`

---

## Elicitation Summary

| Finding | Source | Status |
|---|---|---|
| 3 named accounts with individual standing rules | Artefact 4.3 | Stated |
| 3 sub-forum norm gaps from global policy | Artefact 4.3 | Stated |
| Asymmetric error tolerance (FN >> FP) | Founder brief + artefact 4.3 | Stated |
| Grey-zone = 64% of total moderator effort | Calculated from brief | Derived |
| VIP rules not visible to volunteers | Artefact 4.3 | Stated |
| IP triage criteria for non-named claimants | — | **Open — not in brief** |
| Tom vs Senior Moderator split on IP claims | — | **Open — not in brief** |
| Escalation path from volunteer to Tom | — | **Open — one data point only** |
| Whether other sub-forums have undocumented norms | — | **Open — 14 subs, 3 documented** |

## Probe Round 2 (Contradiction / Evasion Checks)

**Targeted follow-ups to convert weakly-specified answers into design-grade evidence:**

1. **Q3 (sub-forum norms):** "You said there are three documented norm gaps. In the last 30 days, how often did moderators apply undocumented local norms in the other 11 sub-forums?"
   - Why it matters: tests whether "only 3 norms" is true or just documented scope.

2. **Q4 (disagreement resolution):** "You said moderators usually resolve in Discord. Give two recent cases where they could not resolve. What exact trigger brought you in?"
   - Why it matters: identifies escalation trigger from volunteer layer to Tom.

3. **Q5 (IP claims triage):** "You said non-named claimants use standard escalation. What concrete fields make a claim 'standard' versus 'priority review'?"
   - Why it matters: extracts codifiable triage criteria; reduces hidden judgment risk.

4. **Q8 (visibility boundary):** "You said VIP rules are not in volunteer Discord. How do volunteers avoid accidental policy conflicts when they cannot see those constraints?"
   - Why it matters: probes control-break risk created by partial policy visibility.

## Open Gap Register (with Confidence and Impact)

| Open Gap | Priority | Current Confidence | Design Impact | Validation Path |
|---|---|---|---|---|
| IP triage criteria for non-named claimants | P0 | Low | High | Ask for last 10 claims and decision rationale fields |
| Tom vs Senior Moderator split on IP claims | P0 | Low | High | Clarify RACI for intake, triage, final decision |
| Escalation trigger from volunteer disagreement to Tom | P0 | Low | High | Collect 3 disagreement cases; identify escalation condition |
| Undocumented norms in remaining 11 sub-forums | P1 | Low | Medium-High | Sample moderation logs by sub-forum for norm deviations |
| Governance process for VIP list updates | P2 | Medium-Low | Medium | Confirm owner, update cadence, and audit requirements |

## Provisional Delegation Archetype Calibration

| Task Cluster | Archetype (Provisional) | Evidence | Open Dependency |
|---|---|---|---|
| Routine spam handling | Fully agentic (with audit sampling) | High volume, low handling time; repetitive pattern from brief | Confirm exception rate and rollback path |
| Grey-zone review pre-triage | Agent-led with human oversight | Largest effort sink (64%); judgment-heavy but patternable front-end triage | Define confidence thresholds and escalation triggers |
| Appeals context assembly | Human-led with agent support | Context stitching load is high; decision accountability remains human | Clarify required evidence packet and reviewer rubric |
| IP claims triage | Human-only (for now) | Sparse volume; incomplete criteria; named-account special handling | Need explicit triage criteria and owner split |
| VIP account routing enforcement | Human-only gate with agent detection support | Asymmetric risk tolerance; explicit standing rules for named accounts | Confirm governance for list updates and audit controls |
