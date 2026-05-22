# Peer Review — Richa Sang (Scenario 5: Westbridge Family Medicine)

**Reviewer:** Krzysztof Wilniewczyc *(with a little help from AI :D)*
**Date:** 2026-05-04
**Submission scope:** 9 files (`0-ATX-Assessment-Brief.md` through `9-ATX-Terminology-Explained.md`)

---

Hi Richa — really good submission to read through. You picked the clinic intake scenario and ran it through the full ATX loop with discipline. Below: first what's working well, then a small handful of things I'd flag for a second look. The second half is friendly nudges, not gotchas.

---

## Part 1 — What's working well

### 1. Framework discipline is visible end-to-end
You decomposed **all four work streams** (rather than the required two), assigned **11 task clusters** to delegation archetypes, and importantly — **not everything is "Fully Agentic."** That's the Week 2 anti-pattern the rubric is hunting for, and you sidestep it cleanly with `Human-led + Agent Support` for failure resolution, denial handling, visit flagging, and discrepancy handling. That alone puts you ahead of most submissions.

### 2. Lived-vs-documented work is anchored in artefacts
CLM and DSM cite **Artefact 5.1 (Wellpath always denies first time — tribal knowledge), 5.2 (athenahealth ticker not used at check-in), and 5.3 (verification stale after 6 months)** repeatedly. The Wellpath note in particular is a sharp catch — exactly the kind of insurer-specific tribal knowledge an SOP would never capture, and you've used it to justify keeping denial handling out of the agent's hands.

### 3. The "why this wins" rationale is defensible
Med Recon at 22.5 vs Pre-Visit 17.5 vs Insurance 8.0 vs PA 6.0 — and your explicit reason for **not** picking Insurance Verification despite high volume ("70% follow a straight path; rules-based automation is more appropriate than an agent") shows you actually applied the suitability gate from `atx-scoring.md`. The "agent vs script" distinction is something a lot of submissions skip.

### 4. Discovery Questions tied to actual tensions
Q1.2 (athenahealth ticker — training gap or system gap?), Q2.2 (Wellpath pattern documented or tribal?), Q3.3 (root cause of the three intake misses) — each would *materially* change the design depending on the answer. The "questions NOT to ask" list at the bottom is a nice meta-touch.

### 5. Build loop showed reflection and revision
Going from 2.3/5 → 3.5/5 with explicit gap-resolution mapping in `8-Buildability-Assessment.md` is the closed-loop discipline the week is after. The "Sections 11–16 added in response to" framing makes the iteration trail readable.

### 6. AI-ingestibility is generally strong
Heavy use of clean tables, consistent H/M/L legends, summary matrices at the end of CLM and DSM. An LLM picking this up as input would have an easy time parsing the structure.

### 7. Doc #9 (Terminology Explained) is a thoughtful add
Not strictly required, but the "JtD → Micro-task → Cognitive Zone → Breakpoint → Autonomy Matrix → Escalation Trigger" chain at the bottom is genuinely useful for a reader trying to follow how the artefacts feed each other.

---

## Part 2 — A few things worth a second look

### A. APD Sections 11–16 read as design fact but were added post-hoc
After the build-loop revision, you added some quite specific-looking technical specs:

- **Section 11.2** — "athenahealth: 1000 requests/hour, Availity: 500 req/hr, DoseSpot: 200 req/hr." None of these are in the brief, and they're not in your assumptions table either.
- **Section 12.1** — A specific JSON schema for DoseSpot's drug-interaction response. Plausible, but the brief doesn't tell us the format.
- **Section 15** — AES-256 at rest, SHA-256 patient-ID hashing, 7-year retention, breach-notification step list. Reasonable HIPAA boilerplate, but it reads as design fact rather than as an industry-default assumption pending confirmation.

The rubric is keen on "marked assumptions with confidence levels" and treats unmarked inference as the failure mode it's looking for. A builder reading this would code against rate limits that might be off by 10×. **Light fix:** add a one-liner like `[Inferred — Medium confidence — verify with stakeholder/vendor docs]` at the top of each sub-section, or move the figures into the assumptions table at §17. The content is fine; it's just the labelling.

### B. Volume × Value scores use fractional values that aren't in the ATX scale
The reference (`atx-scoring.md`) defines Volume and Non-Determinism as **integer 1–5** scores. You're computing weighted averages (1.6, 2.0, 3.5, 4.5), giving final scores of 8.0, 6.0, 17.5, 22.5. Mathematically defensible, but it diverges from the scale being practiced — meaning the "≥15 = strong candidate" threshold is being applied differently than the reference defines. **Easiest fix:** either round to integers, or add one sentence saying "I'm using a weighted average rather than the integer 1–5 score because…"

### C. Annual-hours uses a 365-day operating year
`6 min × 180 patients × 365 / 60 = 6,570 hrs/yr` for Med Recon. A US family practice typically operates closer to ~250 working days, so the absolute dollar figures (`$295,650 → $3,942 → 98.7% saving`) are inflated by roughly a third. The *ratio* doesn't change. **Fix:** swap 365 → ~250 (or whatever Westbridge's actual workdays figure would be) and re-state the totals — or add an explicit "assuming 365-day operation" assumption.

### D. Two summary docs add bulk for limited extra value
You have `0-ATX-Assessment-Brief.md` (~170 lines) and `0.1-Summary.md` (~250 lines) that mostly restate content from the seven required deliverables. For an LLM loading the full submission as context, this means burning tokens reading the same Med Recon scoring three times. **Suggestion:** keep one (the Brief is more reviewer-friendly; the Summary is more LLM-friendly), drop the other. Doc #9 is worth keeping — it's the only one that adds genuinely new content.

---

## Lived-work vs documented-process check

Pass. Three of your four "lived work" notes (verification refresh, Wellpath denial pattern, Google Sheets workaround) are tied to specific artefacts; the fourth (PA flagging at check-in) is tied to Artefact 5.2. The CLM doesn't read like a re-skinned SOP.

One small ask: there isn't a standalone "lived process narrative" as the `atx-assessment.md` Phase 2 output suggests ("1-page description of what really happens vs. what the SOP says"). The lived-work observations are scattered across CLM/DSM/APD instead. Probably not gate-blocking, but worth knowing.

---

## Delegation-archetype calibration check

Strong pass. Your matrix splits 11 clusters across **Agent-led + Oversight (7)** and **Human-led + Agent Support (4)** with explicit rationale per cluster. The 70%/30% framing on Insurance Verification and the "tribal knowledge required" framing on PA Denial Handling are both well-justified. **Nothing in your matrix defaults to Fully Agentic** — you've actively avoided the anti-pattern.

One push-back: **TC-4.3 Drug Interaction Check** is `Agent-led + Oversight`, but you've also written into the APD that *critical* interactions go to "Agent proposes, human approves." That's a stronger guard than the archetype label suggests — worth surfacing into the matrix rationale so it's visible there.

---

## AI-ingestibility grade

**Score: 4 / 5** (would be 4.5 with the redundancy trim)

**What works:** consistent table structure, clean H/M/L legends, explicit summary matrices, every assumption has a confidence column, terminology doc helps an LLM understand the framework being applied.

**What hurts the score:** the two top-of-stack summary docs duplicate downstream content; some of the APD's invented specs (point A above) would mislead a builder LLM into encoding wrong assumptions as fact. Address those two and this is a 5/5 ingestion target.

---

## Calibration note

Tracking toward a Gate-2 pass as drafted — structure, archetype discipline, and artefact grounding are at-or-above the rubric bar; the remaining work is labelling the inferred technical specs in the APD and trimming the duplicated summary content, not rewriting anything substantive.

---

Solid submission overall, Richa.

— Krzysztof
