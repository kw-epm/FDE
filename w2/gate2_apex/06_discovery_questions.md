# Discovery Questions for the Main Stakeholder
**Gate 2 — Apex Distribution Ltd**
**Stakeholder:** Sarah Whitmore, COO

> Optimised for the 10-min live round (or ~3 min in small-group). **Q-numbering is stable — preserved from the discovery catalog so cross-references in CLAUDE.md, APD, DSM remain valid.** The Top-4 are flagged in priority order; everything else is reference.
>
> **Code legend:** `Q1–Q15` = questions defined below; `G-N` = open gaps (canonical: `CLAUDE.md` §Open gaps); `A-N` / `B-N` = cross-artefact evidence (canonical: `00_elicitation_log.md`); `BP-X1` = cross-stream breakpoint (canonical: CLM).

---

## Live-round priority order (the four to actually fire)

**Fire in this order:** **Q3** (highest chance to change the implementation) → **Q2** (lived-vs-documented anchor) → **Q5** (success criteria) → **Q4** (TCO baseline). **Backup: Q1** (only if you've burned through Top 4 with time left).

Each one carries the *spoken question* (plain English for Sarah), a *quantifier follow-up* (force a number when she hedges), and the *design fork* (what changes per answer — facilitator-only).

### Q3 — Sandra audit-bypass pattern (highest chance to change the implementation)

**Spoken:** *"Sandra applied £170 in goodwill credit on Pete's case without proper sign-off from a manager. How often is that happening across your team?"*

**Quantifier follow-up:** *"Out of 10 recent goodwill credits — how many would have the right manager's sign-off on them?"*

**Design fork:**
- "Most have it" → governance-upgrade is polish, not headline. BDRA's APPROVER_ID enforcement = nice-to-have
- "Maybe half" → governance-upgrade IS the primary metric; Wave 1 ROI reframes as compliance
- "Hardly any" → entire AM authority model needs Sarah to choose: (a) raise CO authority, (b) AM async approval, (c) CO supervisor counter-sign

### Q2 — Damaged-consignment actual workflow (lived-vs-doc anchor)

**Spoken:** *"Your SOP doesn't have a procedure for damaged pallets — it's left blank. When a damaged pallet is rejected, like in Mark's call, what does your dispatcher actually check before deciding what happens next?"*

**Quantifier follow-up:** *"Out of 10 recent damaged-pallet calls — how many came back to the depot, how many were left with the customer, how many were photographed and abandoned?"*

**Design fork:**
- Codifiable criteria → DECA-light Wave 3 unlocks earlier; agent can pre-stage and recommend
- "It varies, judgment call" → DECA-light stays context-only, dispatcher decides; honest Wave 3 scope

### Q5 — CEO success metric vs £1.2M anchor

**Spoken:** *"Your CEO heard about a competitor saving £1.2M. What result would HE consider a success in year one — in plain terms?"*

**Quantifier follow-up:** *"If you had to pick a number to put in front of the board — caveats fine — what would land?"*

**Design fork:**
- Hard target ≥ £500K → Wave 1 alone insufficient; need committed Wave 2/3 in the plan
- "A story he can tell, no number" → Wave 1 £25–67K (Scenario B–A range, V×V §3) + governance upgrade is enough
- "Match £1.2M" → Wave 1 BDRA insufficient; portfolio approach (BDRA + non-agent rules/RPA on ETA lookup)

### Q4 — 35-headcount split (cost baseline)

**Spoken:** *"Roughly how is your 35-person team split — dispatchers, customer-facing agents, account managers, supervisors?"*

**Quantifier follow-up:** *"To give your CFO a clean hours-saved-per-person figure, which group should I divide my numbers into?"*

**Design fork:**
- <15 are CO agents (the BDRA target sub-population) → all £-figures in V×V halve; FTE-equivalent drops
- 20+ CO agents → V×V baseline holds; cleaner ROI per agent

---

### Backup — Q1: 2024 chatbot failure mode

**Spoken:** *"The 2024 chatbot — what specifically went wrong that made you pull it?"* (let her describe; classify silently)

**Quantifier follow-up:** *"How long did it run before you killed it?"*

**Design fork:**
- Script-trap-shaped → BDRA's customer-comms drafts must be free-form
- Tone/voice → human-confirm window stays longer than 100 cases
- Misclassification → confidence-threshold floor 0.8 is non-negotiable

---

## Other P0 questions (catalog — for follow-up sessions, not live round)

| # | Spoken | Closes |
|---|---|---|
| Q6 | *"When a damaged delivery becomes a billing dispute weeks later — like Pete's case — who owns it through to resolution? Does the original dispatcher even know it became a dispute?"* | G-7, BP-X1 |
| Q7 | *"Looking at BlueSky's account, its named manager is one person but the credit was approved by another. Who's actually allowed to approve credits in practice — always the customer's own manager, or can any manager step in?"* | A-5 + AM authority routing gap (CLAUDE.md gap register) |
| Q8 | *"When your team applies a credit, what's the real process today? Could that step ever be done automatically by software, or must a person always do it?"* | G-12 (engineering) |

## Build-design questions (P1 — calibration / preference)

| # | Spoken | Closes |
|---|---|---|
| Q9 | *"I'm seeing a date mismatch in your dispute export — D-342 has an open-date that's later than the file's date. Which date should we trust as the 'as of' date when reading these files?"* | A-7 |
| Q10 | *"If the system handles about two-thirds of routine cases in month one and your team picks up the rest, is that acceptable while we tune it? Or do you want a higher floor from day one?"* | Calibration tolerance |
| Q11 | *"Where should action requests go so account managers actually see them quickly — email, Slack, a task in your CRM, somewhere else?"* | 4.9E channel |
| Q12 | *"Do you have sample 'good' customer-closing emails I can use as templates, or someone I can sit with for an hour to learn your team's voice?"* | Tone calibration |
| Q13 | *"For disputes waiting on the customer to respond — like D-337 which has been waiting since March — how often should we be following up?"* | Chase cadence |
| Q14 | *"At what credit amount must a manager approve, instead of customer ops handling it directly? Today, what's the most Sandra can do on her own?"* | CO authority threshold |
| Q15 | *"Sandra's email said fuel surcharge can't be adjusted on individual invoices — but I see a £45 fuel-recalculation credit was applied to Northstar. In which situations IS fuel recalculation actually allowed, and what proof is needed?"* | A-6 |

## Out-of-scope (do not ask — burns live time)

- Anything answerable from the brief or CSVs (volumes, vehicle count, system names)
- Open-ended process tours ("walk me through your operations" / "what are your pain points" / "tell me about your tooling")

---

## Interviewer cheat sheet (Appendix)

### Evasion / hedge handling

| Sarah says | Move |
|---|---|
| "It varies" / "it depends" | *"If you had to guess, what's the number — caveats fine?"* |
| "My team handles that" | *"Who specifically? Could I follow up with them after?"* |
| Long anecdote | Let her finish (don't cut off COO), then: *"What's the rule that comes out of that?"* |
| "We follow the SOP" | *"That's the SOP — what actually happens when [specific case]?"* |
| Specific number, no caveat | If contradicts CSV/artefact: *"I'm seeing X in the data — help me square that"* |

### Testimony-vs-artefact watch (where Sarah may give COO-frame answers that diverge from lived evidence)

- **Q3 (Sandra pattern):** if Sarah says "rare", probe — A-4 is structural (Sandra has no APPROVER_ID role), so it's the system, not the person. Push: *"It happened on the case in front of me — how would you measure 'rare'?"*
- **Q2 (damaged workflow):** Sarah is ex-dispatch — she'll likely give a confident, tidy answer. Cross-check against artefact 1 specifics (damage-extent + receiving-party posture + remaining-route-pressure). If her version omits any of those, that's a real-vs-self-image gap. Don't argue — note silently.
- **Q5 (CEO metric):** the £1.2M is an external anchor, not Sarah's. Listen for HER framing — what she thinks would land, not what she's been told.
- **Backup Q1 (chatbot):** if she gives a tone answer when context suggests script-trap, probe both. Failure narrative is often clean; lived failure is often messier.

### The "update live" move (rubric-rewarded)

When Sarah's answer overturns a design assumption:
> *"That changes my [X] — let me adjust. So if I'm hearing right, [paraphrase], which means [design implication]. Does that land?"*

One of these is worth more than two extra questions.

### Closing move (last 60s)

> *"Quick check — three things I'm taking away to update my design: [Q3 answer], [Q5 answer], [Q2 answer]. Did I miss anything you'd want me to weight differently?"*

Forces Sarah to confirm OR add the thing she didn't volunteer.

### Source pointer

AI-proxy reconstructions of Sarah's likely answers and the gap register are in `00_elicitation_log.md`. Do not cite them as Sarah-confirmed during the live round.
