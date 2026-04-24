# Orientation — Scenario 3: Retail Returns Disposition
## What This File Is

This is your private thinking companion for Week 1. It explains **why** the scenario is harder than it looks, **what tensions** you need to resolve before you can write a credible spec, and **how all the files in this folder relate** to each other. Coaches never see this file — it exists so you walk into the peer review and Gate 1 with a clear head, not just a filled-in template.

---

## The Scenario in Plain Language

A 12-person team at a returns facility manually handles ~4,500 returned items per week. For each item they do three things:

1. **Classify** — assign a reason code (why did the customer return it?)
2. **Inspect** — assess physical condition
3. **Route** — send to the right disposition lane (restock, outlet, refurbish, donate, destroy)

They do this "visually and by memory." No decision-support system. No consistent rulebook. Pure human judgment, person by person.

The numbers tell you the process is failing:
- **78% reason-code accuracy** means roughly 1 in 4 reason codes is wrong. Wrong reason codes corrupt return analytics, skew inventory decisions, and in fraud cases can mean a fraudulent return gets flagged with an innocent reason code.
- **40% fraud detection rate** means 60% of fraudulent returns pass through undetected and only surface weeks later in chargeback reports — at which point the merchandise is already restocked or destroyed, and the refund has already been issued.

The VP of Operations wants an agent to handle the easy cases and preserve human judgment for the hard ones. The CFO wants a payback story.

---

## The Four Hard Questions You Must Answer Before Writing the Spec

### 1. What does "suspected fraud" actually mean operationally?

This is the deepest tension in the scenario. The VP says "preserve human judgment for suspected fraud." But who suspects fraud right now? The 12 processors. And they catch only 40% of it — meaning either:

- (a) The remaining 60% shows no detectable signal at intake, OR
- (b) The remaining 60% shows signals that a trained human would catch, but the current team lacks consistency or training

If (a) is true: no agent will do better than the current 40%, because the signals don't exist at intake. The agent should match or modestly exceed human detection, and you need to note this limitation.

If (b) is true: an agent with consistent rule application could significantly outperform the current 40%, because it won't have the fatigue, inconsistency, and memory-reliance that the current team has.

**Your working assumption** (documented in `05_assumptions_unknowns.md`): both are partially true. Some fraud is undetectable at intake; some is detectable but currently missed due to inconsistency. The agent should flag more consistently than the current team while escalating borderline cases to Loss Prevention.

**Why this matters for delegation**: The VP's constraint ("preserve human judgment for suspected fraud") does NOT mean the agent can't flag fraud — it means the agent cannot *decide* to reject or approve a return on fraud grounds alone. The agent flags; a human decides.

---

### 2. What is "high-value"? Nobody defined it.

The VP says preserve human judgment for "high-value items." The scenario gives you no threshold. This is a genuine unknown.

Possible definitions:
- Original retail price above $X (e.g., $150 for apparel)
- Items in specific categories (outerwear, footwear, leather goods)
- Items with special handling requirements (limited edition, brand-partner items)
- Any item where the disposition decision affects margin by more than $Y

**You should not “pick a number in a vacuum”** — the threshold belongs in the Assumptions & Unknowns with a default for discussion. The virtual discovery in this folder uses **$100 retail (VP-indicated)**, still recorded as `[Flagged for Validation]` in `05_assumptions_unknowns.md` until a formal policy exists.

**Why it matters for delegation**: If "high-value" is undefined, your delegation boundary is a leaky abstraction. A spec that says "escalate high-value items to humans" without defining the threshold will produce a builder that either guesses or asks a clarifying question — both are failures.

---

### 3. What data does the agent actually receive?

This is the most dangerous assumption in the scenario. The team currently works "visually and by memory." That means:

- **Physical condition** is assessed by looking at the item. The agent does **not** get pixels in V1: virtual stakeholder discovery in `supporting/stakeholder_discovery.md` has **no camera** at the intake station.
- **Reason code** is currently entered by a processor who has also read the customer's return note/reason. The agent can consume structured order data plus customer text (e.g. from OMS + returns portal) where APIs exist; exact contracts are in the assumptions register.
- **Item identity** — barcode/SKU scan is the typical anchor (standard practice); the scenario + discovery assume scan + WMS/OMS.

**Your working assumption for this workstream**: Intake = barcode scan, processor-entered **condition grade** from a rubric (drop-down), and customer return text from systems you integrate. **No photo** in V1. The spec treats condition as **structured + human**, not computer vision over the garment.

**Why it matters for the spec**: A spec that assumes image-based condition assessment when there are no cameras is unbuildable. This pack assumes **no image capture** at intake unless you re-validate and change the assumption in `05_assumptions_unknowns.md`.

---

### 4. What is the CFO's payback story?

The VP is "under a margin-improvement mandate from the CFO and needs a credible payback story, not a 'maybe someday' pitch."

This means your Problem Statement cannot just say "improve accuracy and efficiency." It needs numbers. Work from what you have:

**Current state costs (estimable from the scenario):**
- 12 processors × ~$X loaded cost/year (assume ~$45K fully loaded = $540K/year for the team)
- 4,500 returns/week × 52 weeks = 234,000 returns/year
- 78% reason-code accuracy → ~51,480 mis-classified returns/year
  - Mis-classification has downstream cost: wrong inventory allocation, lost recovery value, incorrect fraud records
- 40% fraud detection → 60% pass-through
  - Average chargeback loss per fraudulent return in apparel: typically $30–$80 (item value + processing cost)
  - If 1% of 234,000 returns are fraudulent = 2,340 fraud attempts, 1,404 undetected = $42K–$112K annual chargeback exposure (conservative estimate)

**Potential upside from agent:**
- Reason-code accuracy improvement from 78% → 92%+ (conservative target) = better analytics, better recovery routing
- Fraud detection improvement from 40% → 70%+ on detectable signals = meaningful chargeback reduction
- Processor capacity: if agent handles 65–70% of volume autonomously, 12 processors → potential to redeploy 7–8 FTEs (not necessarily eliminate, but redeploy to higher-value work)

These are estimates you will document as assumptions. They are directionally correct and give the CFO a real number to pressure-test.

---

## The Delegation Boundary — Where to Draw It

The hardest decision in this scenario is not whether to automate — it's **where exactly the line sits**. Two defensible positions:

**Position A — Conservative (agent-assists):**
- Agent pre-fills reason code and suggests disposition
- Human reviews and confirms every item
- Rationale: 78% accuracy baseline means trust must be earned; start with augmentation
- Weakness: no labor savings, hard to build CFO case

**Position B — Aggressive (agent-decides with exceptions):**
- Agent decides autonomously for clean cases (no fraud signals, clear condition, commodity items)
- Human reviews only: suspected fraud, high-value, customer-escalated, ambiguous condition
- Rationale: majority of returns are routine; you can defend the boundary with explicit criteria
- Weakness: requires defining "clean case" precisely, which requires knowing the data

**Your working position** (documented in `02_delegation_analysis.md`): **Position B**, with fraud always escalating. The specific criteria for "clean case" become explicit requirements in the spec, not judgment calls. This is the only position that produces a credible CFO payback story.

---

## Key Constraint: No Disposition Decision on Fraud Grounds Without a Human

This is the VP's explicit hard rule, equivalent to the general counsel's sign-off rule in Scenario 2. You cannot soften it or route around it. The agent:

- CAN flag suspected fraud with a confidence score and evidence list
- CANNOT approve, reject, or disposition a return that has a fraud flag without Loss Prevention sign-off

This constraint shapes escalation logic throughout the spec.

---

## How the Files in This Folder Relate

```
supporting/
  current_state_process.md     ← What is happening right now, in detail
  stakeholder_discovery.md     ← What we learned by asking stakeholders; what we still don't know

artifacts/
  01_problem_statement.md      ← Gate Artifact 1: the "why invest" frame
  02_delegation_analysis.md    ← Gate Artifact 2: where the human/agent line sits and why
  03_agent_specification.md    ← Gate Artifact 3: precise enough to hand to Claude Code
  04_validation_design.md      ← Gate Artifact 4: how you know it works
  05_assumptions_unknowns.md   ← Gate Artifact 5: what you're betting on being true
```

**Read order for someone new to the scenario:**
1. This file (orientation)
2. `current_state_process.md` — to understand what the agent is replacing
3. `stakeholder_discovery.md` — to see what was confirmed vs. what remains open
4. `05_assumptions_unknowns.md` — to see the risk register before reading the spec
5. `01_problem_statement.md` → `02_delegation_analysis.md` → `03_agent_specification.md` → `04_validation_design.md`

**Read order for a coach doing a fast 15-minute review:**
`01` → `02` → skim `03` for precision signals → `05` for honesty signals

---

## What Coaches Are Actually Looking For

Based on the program guidance:

**1. Are the delegation boundaries defensible, not arbitrary?**

Bad: "The agent handles routine cases." (What is routine? Undefined.)
Good: "The agent decides autonomously when: reason code matches one of [5 unambiguous codes], condition is GRADE_A or GRADE_B per the rubric, original retail price < $100, and no fraud signal is present. Any deviation escalates."

The word "defensible" means: if a coach asks "why did you put the line there?", you can answer with a business constraint or a data property — not "it seemed reasonable."

**2. Is the spec precise enough that Claude Code wouldn't ask a clarifying question?**

Every "if," "when," and "unless" in the spec needs explicit criteria and outcomes. Test yourself: read each requirement and ask "what would an agent that has never seen an apparel return do with this?" If the answer is "ask the FDE what they meant," the requirement fails.

**3. Are the assumptions honest?**

At least 5 genuine unknowns. The scenario has many real unknowns (systems, image capture, threshold definitions, volume by reason code, integration APIs). If your assumptions section reads like "I assume the system will work" you haven't done the thinking.

---

## One More Thing: The Closed Build Loop

Before Friday's peer review, you need to run a closed build loop:

1. Take one feature from `03_agent_specification.md` — suggest starting with the **reason code classification** feature (Requirement RC-001 through RC-004)
2. Hand it to Claude Code: "Build the reason code classifier as specified"
3. See what it produces
4. Diagnose the gap using `spec-ambiguity-vs-builder-mistakes.md` taxonomy:
   - Did the builder misread a clear requirement? (re-prompt)
   - Did the spec have an ambiguity? (rewrite the spec)
   - Did the spec have a design gap? (add the missing requirement)
5. Fix the root cause, re-run, verify

The most likely gap to find: Claude Code will ask what the input format is for condition data, because the spec may underspecify it. That's a Category 1 (Spec Ambiguity) — fix the spec, not the prompt.
