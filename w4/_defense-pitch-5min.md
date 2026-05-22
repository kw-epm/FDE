# Defense Pitch — ResolveOne (Option C, financial services)

Working file — not a deliverable. 14-min defense = 5-min pitch + 7-min coach challenge + 2-min curveball (not graded).

---

# 📋 CHEAT SHEET — read this first

**Scenario in one line.** US bank. 4,500 customer interactions/day across 5 channels. 18-min handle time. 34% FCR. 6 backend systems. CFPB regulation.

**Buyer trio.**
- **Amanda Torres** (CCO) — NPS pressure, wanted 60 days
- **Jennifer Park** (Chief Compliance Officer) — HITL on entitlements, Legal sign-off on logic
- **David Okonkwo** (CTO) — no Avaya touch, modernise first

**Their compromise** (Slack thread, 9 Apr): chat + email pilot, dedicated modern infrastructure, narrow auto-resolve allow-list (read-only ops only), 8–10 weeks.

**Three data sources.** Context VDB (Chroma) + Customer Record API + Compliance Policy API.

**Three agentic additions.** Issue clarification · multi-direction resolution · honest escalation.

**Three tiers.** Tier 1 auto-resolve (read-only only, three independent gates) · Tier 2 human review (default) · Tier 3 specialist routing.

**Headline numbers.** Phase 1 ~$1.16M/year sustaining saving on the slice. $60K build. **Ramp-adjusted payback ~4 months** (not the naive 0.6m). Phase 2 unlocks +$1M/year but ~12-month calendar gap due to regulatory ramp.

**The defense-killer line.** *"The agent never auto-sends in Tier 2 or Tier 3. Tier 1 fires only when confidence ≥ 0.90 AND low-risk AND issue on the allow-list jointly owned by Amanda and Jennifer."*

**Scope honesty for §8.** Multi-direction resolution and Phase 2 auto-resolve are designed but NOT built in the 4-day prototype. Built: three-tier routing + disclosure-check + audit log on three demo interactions + one failure-mode test.

---

# 🎤 5-MIN PITCH — minute-by-minute beats

Speak from the bullets in your own words. ~150 spoken words/min ≈ 750 words. Aim for 4:30 to leave panel slack.

### 0:00–0:30 · Problem

- US financial services company
- 4,500 customer interactions/day across 5 channels (phone, email, chat, social, branch)
- 18-min average handle, 34% FCR — two thirds of customers come back
- Most of the 18 min is juggling 6 backend systems, not deciding
- CFPB + state banking watching; audit trail non-optional

### 0:30–1:00 · The three executives + the compromise

- **Amanda (CCO):** NPS, wants 60 days
- **Jennifer (Chief Compliance Officer):** human-in-loop on entitlements; Legal sign-off on AI logic
- **David (CTO):** no AI on the 2010 Avaya stack; modernise platform first
- **Compromise:** chat + email pilot, modern infrastructure, narrow read-only auto-resolve allow-list, 8–10 weeks
- ResolveOne is the design response to that compromise

### 1:00–1:15 · What it does (one line)

> *"Reads inbound chat or email, pulls context from three sources, drafts a response with reasoning, routes to one of three tiers, logs everything for CFPB examination."*

### 1:15–2:00 · Architecture (draw if there's a board)

- **VDB (Chroma local):** top 20 similar prior cases by semantic match
- **Customer Record API:** account state, transactions, prior tickets, KYC, fraud
- **Compliance Policy API:** regulations, mandatory disclosures, escalation triggers
- Agent stitches all three
- **Deterministic** where it can be (disclosure-check, risk-score table, allow-list filter, escalation triggers)
- **LLM** where it has to be (classification, draft composition, routing reasoning)

> *"Regulations live in code Legal can read, not in LLM prompts they cannot audit. That is the structural answer to Jennifer."*

### 2:00–3:00 · Why an agent and not a workflow tool

The three agentic additions:

1. **Issue clarification.** *"I see a charge I don't recognise"* — fraud? billing error? forgotten subscription? Agent surfaces 2–3 interpretations.
2. **Multi-direction resolution.** *"refund OR credit OR fee waiver"* — agent proposes tiered options with the trade-off named per option.
3. **Honest escalation.** When confidence drops, agent escalates with a complete briefing — not a panic punt.

> *"A workflow tool handles if-this-then-that. Customer interactions are not deterministic. The same inbound message covers fraud, billing error, forgotten subscription, chargeback abuse — each a different resolution under a different rule."*

### 3:00–3:40 · Success metrics + HITL safeguard

**Seven measurable numbers:**

- Handle time **18 → 12 → 9 min**
- FCR **34% → 50% → 60%**
- Agent acceptance of draft **≥ 70%** sent without rewrite
- Auto-resolution accuracy **≥ 99%** (CCO pulls plug below)
- **CSAT delta** — Amanda's KPI; at parity Phase 1, **+5 points** by month 6
- Latency p95 **≤ 30 s**, fail-loud within 5 s on source outage
- Audit-trail completeness **100%** (CFPB non-optional)

**Say this out loud — closes Jennifer's biggest concern:**

> *"The agent never auto-sends in Tier 2 or Tier 3. In Tier 1, three independent conditions must all hold — confidence ≥ 0.90 AND low-risk AND the issue is on an allow-list jointly owned by Amanda and Jennifer. The customer never sees a degraded response. The bank's regulatory standing does not depend on the agent being perfect; it depends on the human agent staying in the loop on anything outside the narrow allow-list."*

### 3:40–4:15 · Why it is hard enough

1. **Six-system coordination IS the cognitive load.** Retrieval-heavy, decision-light. Different shape from most demo agents.
2. **Regulatory compliance is a hard filter, not a soft preference.** LLM cannot be trusted with disclosure rules → deterministic disclosure-check is non-negotiable.
3. **Knowing when to escalate is the hardest call.** Calibrated confidence — the agent knowing what it does not know.

### 4:15–4:50 · Business case

- **Phase 1** (chat + email, agent-assist): **~$1.16M/year sustaining**, $60K build, **ramp-adjusted payback ~4 months** (naive 0.6m assumes Day-1 full saving — not how regulated FS works)
- **Phase 2** (selective auto-resolve): **+$1M/year**, but **~12-month calendar gap** from start because of the regulatory ramp
- **Floor** (combined stress: low rate × half volume × half time saved × shrunk allow-list): ~$143K/year, ~10–12 month payback. Still positive inside 18-month enterprise hurdle.
- Currency: USD. US bank, CFPB jurisdiction.

> *"Every figure is calibrated against industry pattern, not measured. Seven specific doubts named in §5.7. The honest constraint is not the economic case — it is the regulatory acceptance ramp."*

### 4:50–5:00 · Close

**What I expect to learn:**
- Calibrated confidence for regulated decisions
- The deterministic-vs-LLM split when regulations cannot trust the LLM
- Where the mock-data realism boundary sits in a 4-day FS project

> *"The 4-day build delivers three-tier routing, disclosure-check, and audit log on three demo interactions. Multi-direction resolution and Phase 2 auto-resolve are in the design but not built — scoped out honestly rather than half-shipped."*

---

# 🎯 7-MIN CHALLENGE — quick reference

Coach probes scope, difficulty, economic viability, primary risks. Read these once, answer aloud without looking.

| Question | One-line answer |
|---|---|
| **Why an agent, not a workflow tool?** | Workflow handles deterministic flows. Customer interactions are not deterministic — the same message covers fraud, billing error, forgotten subscription. The agent classifies and chooses the path. |
| **What does the LLM actually decide?** | Three things: classifies the issue, composes the draft, picks the resolution direction. Hard filters (disclosure-check, risk-score, allow-list, escalation triggers) are deterministic. |
| **Why financial services?** | Higher per-interaction volume + cost, and CFPB makes audit-trail completeness non-optional. The "every source and edit logged" architecture is a feature in FS instead of an afterthought. |
| **Why the CCO and not the ops manager?** | Ops manager owns headcount (triggers floor resistance). CCO owns customer outcomes and regulatory standing — measured on FCR and audit, ops floor receptive. |
| **What are the unit economics?** | Phase 1 saves ~$1.16M/year sustaining on the slice. Ramp-adjusted payback ~4 months on a $60K build. Phase 2 unlocks +$1M/year but ~12-month calendar gap due to regulatory ramp. Worst case ~$143K/year, ~10–12 months. |
| **What happens at full bank scale?** | Slice is ~30% of company volume. Full scale extrapolates to ~$3.9M/year sustaining. Enterprise integration +$200K upfront. Binding constraint is not economics — it is the regulatory acceptance ramp. |
| **How do you know responses are good?** | Four layers — CSAT delta (Amanda's KPI), FCR, agent acceptance rate, auto-resolution accuracy (100 sampled per week, CCO + Compliance). Human has veto on every Tier 2/3 draft; auto-resolve operates only inside three independent gates. |
| **Where did the 18 min come from?** | Stated in the Option C scenario. The 12 min and 9 min Phase 1/2 targets are mine — design targets, not measured. |
| **Where did $35/hour come from?** | US FS customer-service mid-range fully loaded. Sensitivity row covers $25 (lower-tier / offshore). |

---

# 📌 OTHER DELIVERABLES — anticipated probes

The capstone defense is about D#6, but a coach can ask about any submitted artefact. Pre-canned answers for known soft spots:

| If asked... | Lead with... |
|---|---|
| **D#4 Signal 2 — "isn't the 15-min SLA explicit? Why did you classify it as Spec Ambiguity?"** | "The SLA itself is clear — 15 minutes. The ambiguity I flagged is **ownership and enforcement mechanism when the queue stalls** — who pages, on what timeout, under what authority. The 15 min is a target without a teeth-bearing mechanism in the spec. In a real engagement I would tighten the wording; for the gate the structural reasoning is what I am defending." |

---

# 🎲 2-MIN CURVEBALL (not graded)

**Generic pattern (works for any curveball):**

1. **Name what does NOT change** — architecture, data sources, agent loop, HITL discipline
2. **Name what changes** — the specific step the constraint targets
3. **Quantify adapt time** — hours / days / weeks (be honest, don't lowball)
4. **Close with confidence** — the design absorbs it, here is how

**Pre-rehearsed example — CFPB AI-disclosure rule:**

> *"Effective immediately — every AI-touched customer response must include an AI-use disclosure."*

- (15 s) **What does NOT change:** architecture, data sources, agent loop, HITL discipline.
- (30 s) **What changes — code:** the deterministic disclosure-check picks up a new mandatory clause. One prompt update + one policy entry + a regression test. Small in code.
- (30 s) **What changes — calendar:** Legal review of the disclosure wording + customer-experience A/B test = **~2 weeks before we ship**, not half a day. Honest framing matters here.
- (30 s) **Second-order:** auto-resolve allow-list contracts immediately. Phase 2 slips 3–6 months while Tier 1 reverts to Tier 2. Phase 1 (agent-assist) unaffected — human stays in the loop.
- (15 s) **Close:** *"Data sources do not change. Agent loop does not change. The disclosure-check absorbs the rule because regulation lives in the deterministic layer."*

---

# 🏃 REHEARSAL PROTOCOL

**If you have 45 min:** three passes.
1. **Pass 1 (15 min) — read straight through.** Tweak any sentence that feels like the wrong word for your voice.
2. **Pass 2 (15 min) — say it aloud with a timer.** Aim 4:30, not 5:00. If long, cut the business case minute first (numbers are in the proposal).
3. **Pass 3 (15 min) — challenge drill.** Read each table question, answer aloud without looking.

**If you have 30 min:** pass 1 + pass 3.

**If you have 15 min:** read the cheat sheet at the top twice, then pass 3.

**If you have 5 min:** read the cheat sheet, the defense-killer line, and the curveball pattern.
