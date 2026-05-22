# Deliverable #6 — Capstone Proposal: ResolveOne

**Author:** Krzysztof Wilniewczyc, FDE
**Date:** 2026-05-22
**Capstone scenario:** Option C — Multi-Channel Customer Resolution (financial services)
**Project name:** ResolveOne — multi-channel customer-resolution agent

---

## 1. The problem

A US financial services company — a regional bank or fintech — handles **4,500 customer interactions every day** across five channels: phone, email, chat, social media, and branch referrals. The Chief Customer Officer is the buyer. Today the average handle time is **18 minutes per interaction**, and only **34% of interactions are resolved on the first contact**. Two thirds of customers have to come back, which loads the queue, frustrates the customer, and drives complaint volume.

A customer service agent today juggles six different backend systems for every single interaction: the core banking system, the CRM, the prior-tickets store, the dispute system, the KYC/fraud signals store, and the regulatory policy reference. Most of the 18 minutes is spent navigating systems and assembling context — only a small part is spent on the actual decision the customer needs.

The CCO does not want to outsource customer judgement to a chatbot. The financial industry has tried that and customer satisfaction collapsed. The CCO wants the human agent kept in the loop on every meaningful decision, but the routine context-pulling automated away — and the system has to produce a complete audit trail for CFPB and state banking examinations.

**The buyer is a trio** — Amanda Torres (CCO), Jennifer Park (Chief Compliance Officer), and David Okonkwo (CTO) — named in the participant-pack stakeholder exchange (2026-04-08 → 2026-04-09). They had a real disagreement; they reached a compromise. ResolveOne is the design response to that compromise, not a pitch over their heads. Detail on the positions and the negotiated outcome is in §3.

---

## 2. Success metrics

Seven numbers that would prove ResolveOne works — four about quality of service, one about speed, one about the regulator, and one about the customer.

| Metric | Target | How we measure |
|---|---|---|
| **Average handle time** | 18 min → 12 min in Phase 1 (agent-assist); → 9 min in Phase 2 (selective auto-resolve) | Wall-clock per interaction, captured by the CRM as today; compare against a held-back control group |
| **First-contact resolution rate** | 34% → 50% in Phase 1; 60% by month 6 | CRM flag: did the same customer reopen the same issue within 14 days? |
| **Agent acceptance of drafted response** | ≥ 70% of agent-drafted responses sent without rewrite | Sample 200 interactions/week, compare draft vs sent |
| **Auto-resolution accuracy** | ≥ 99% on the auto-resolve slice (balance inquiries, transaction status, fee-waiver standard cases) | Audit sample 100 auto-resolved interactions/week; CCO + compliance review |
| **CSAT delta (the buyer's KPI)** | At least at parity with control group in Phase 1; +5 points by month 6 | Post-interaction CSAT survey, captured by the CRM; Amanda Torres (CCO) is measured on this — without it, the proposal is not actually answering the buyer's question |
| **Latency (p95)** | ≤ 30 s for the agent to surface context + draft. If any of the six systems is unreachable, surface explicit error within 5 s rather than producing a partial-context response. | Per-request logs; alert if p95 over a rolling 7-day window breaches the target |
| **Audit-trail completeness** | 100% of agent-touched interactions log: source data used, draft produced, agent edits, final sent text, decision rationale. Immutable. 7-year retention. | Schema enforcement at write time; weekly compliance audit |

The fifth metric — CSAT delta — is the one Amanda is measured on. The fourth — auto-resolution accuracy — is the one Jennifer pulls the plug on. The seventh is the one the CFPB examiner reads.

---

## 3. Stakeholder tensions and the design's response

The Option C scenario carries three real-world tensions surfaced in the participant-pack executive exchanges. Each shaped a specific design choice.

### The three positions

- **Amanda Torres — CCO.** NPS is her KPI. Wants 60-day deployment.
- **Jennifer Park — Chief Compliance Officer.** Demands human-in-the-loop for any decision affecting customer entitlements (refunds, cancellations, account modifications). Wants Legal sign-off on the AI decision logic before go-live.
- **David Okonkwo — CTO.** Says the legacy telephony stack (Avaya, 2010) cannot safely host an AI agent. Wants the platform modernised first (his 6-month, $800K project) before AI integration. Rejects "AI on the old stack" as a 2 AM Saturday incident waiting to happen.

### Tension A — Speed vs compliance vs infrastructure (the 3-way one)

Amanda wants 60-day deployment. Jennifer wants Legal-reviewed decision logic before anything ships. David wants a 7-month platform modernisation before any AI touches production.

The compromise they reached (Slack thread, 2026-04-09): **chat + email pilot on dedicated modern infrastructure** (no phone integration, no Avaya touch), **8–10 week timeline**, **narrow auto-resolve allow-list restricted to read-only operations** (password resets, balance inquiries, billing questions); refunds, cancellations, account modifications all route to a human with pre-filled context that drops human review time from ~5 minutes to ~30 seconds.

**ResolveOne adopts this compromise clause by clause:**

- **Phase 1 covers chat + email only.** Real-time phone (Phase 2) waits for David's platform modernisation to land. Pre-transcribed phone is in scope only if the bank already has a clean transcript pipeline; otherwise it waits with phone.
- **Auto-resolve allow-list is strict and short.** The FDE-proposed Tier 1 list: account lookups, balance inquiries, billing questions, address changes, password resets. **Refunds, fee waivers, cancellations, account closures: never Tier 1, always Tier 2 (human-approved) with pre-filled context.** **The final allow-list is owned by Amanda + Jennifer jointly — this is the FDE's proposal, subject to their joint approval.** The agent reads the allow-list from the Compliance Policy API as a config, so it can be tightened or loosened without code changes.
- **Production timeline: 8–10 weeks**, not 60 days, not 7 months. The 4-day Week 5 capstone is the *prototype* demonstrating the design; the production deployment is a separate engagement window with discovery + integration + ramp.

**Where I would push back on the compromise.** The "no real-time phone, ever, until the platform modernises" position is too absolute. Phone is ~40% of inbound interaction volume — leaving it untouched for 6+ months caps the saving at ~60% of potential. I would propose, after Phase 1 has built trust (~month 4), a **phone-by-callback workflow**: phone interactions get queued, the agent prepares a callback briefing for the human agent (just like the Tier 2 chat/email flow), and the agent calls back within 15 minutes on the modernised callback channel. That gets phone coverage without touching the legacy Avaya inbound stack. Worth raising in the stakeholder memo as a Phase 1.5 option.

### Tension B — Auditable decision logic (Jennifer's hard requirement)

Jennifer's pre-go-live requirement is Legal sign-off on the AI decision logic. LLM prompts are not auditable by a legal team in any useful sense.

**Design response:** the regulatory rules live in deterministic code, not in LLM prompts. The disclosure-check, the risk-score table, the auto-resolve allow-list, and the escalation triggers are all configuration that Legal can read, mark up, and re-tune without a model re-train. The LLM handles classification, drafting, and reasoning; the regulatory boundary is enforced before and after the LLM call by code Legal owns. The full deterministic-vs-LLM table is in §4.

### Tension C — No legacy infrastructure touch (David's hard requirement)

David's red line: no AI deployment on the existing telephony or core systems. He has watched that movie before.

**Design response:** ResolveOne deploys on dedicated cloud-native infrastructure. Chroma local for the prototype, managed service if production volume demands. Legacy systems (the six existing backends) are queried read-only through thin FastAPI adapters — no AI code ever runs inside a legacy system, and no legacy system has to change to host ResolveOne. If any legacy backend is unavailable, the agent fails loud per §4 "reliability and source-availability" — the human agent reverts to today's manual workflow. There is no agent-on-legacy-stack architecture; that is what David is rejecting.

**Where this proposal interprets David's red line.** David's stated objection is inbound on Avaya. The Phase 1.5 phone-callback proposal (Tension A above) uses *outbound* calls on the modernised callback channel, not the legacy inbound stack. I have read this as inside David's red line, but the tensions file does not say outbound explicitly — confirm with David before committing to Phase 1.5.

### Stakeholder alignment memo — preview of what it will say

The full memo is Deliverable #10 in the Week 5 capstone package and lands on Virtual Monday Week 5 once the sealed scenario pack is open. Outline of what the memo commits each party to:

- **Amanda (CCO):** commits to the 8–10 week Phase 1 timeline (not 60 days). In return: gets a CSAT metric in §2 of the design, a phone-callback Phase 1.5 option to consider after month 4, and a board-readable cumulative-saving curve she can defend at month 6.
- **Jennifer (Chief Compliance Officer):** commits to joint ownership of the auto-resolve allow-list with Amanda. In return: gets Legal-readable deterministic rules (not LLM prompts) as the regulatory boundary, a sampling-audit programme on Tier 1 from day one, and a hard "agent fails loud on any policy-source outage" guarantee.
- **David (CTO):** commits to dedicated cloud-native infrastructure for ResolveOne in parallel with his own platform modernisation. In return: gets a "no AI code in legacy systems, ever" architectural promise, and a phone path that does not depend on his timeline (the Phase 1.5 callback proposal above, on the modernised callback channel).
- **FDE commitments:** named scope cuts in §8 (4-day plan honest about what is built vs designed-but-not-built); the deterministic-vs-LLM split (§4) as the audit substrate; weekly review of the success metrics in §2 against actuals.

The memo arrives with sign-off lines for all four parties. The proposal above is the substrate the memo will reference.

---

## 4. Approach — architecture

**Three data sources. Two ways to look things up. One agent on top.**

```
[Inbound interaction]
       │
       ▼
[Agent: parse + clarify if ambiguous]
       │
       ├──────────────┬──────────────┐
       ▼              ▼              ▼
[Context VDB]   [Record API]   [Policy API]
 (vector search   (structured:    (structured:
  on similar       account state,  regulatory
  prior cases →    transactions,   rules per
  top ~20)         prior tickets,  issue type,
                   KYC + fraud)    mandatory
                                   disclosures)
       │              │              │
       └──────┬───────┴──────────────┘
              ▼
[Agent: classify + draft + route]
              │
              ▼
[Tier 1: auto-resolve (high-confidence + low-risk)]
[Tier 2: agent reviews drafted response, edits, sends]
[Tier 3: route to specialist (complex / regulated)]
              │
              ▼
[Audit log: all sources used + draft + edits + final text + rationale]
```

**Source 1 — Customer Context VDB.** Chroma, local for the prototype. Indexes prior resolved interactions across the bank — semantically searchable, so "customer says her card was declined at a Migros checkout" retrieves the right cohort of prior cases even without exact keyword match. First-pass retrieval: top ~20 similar cases.

**Source 2 — Customer Record API.** Thin FastAPI wrapper over a JSON store. Per customer: account state, last 90 days of transactions, prior ticket history (last 24 months), KYC status, fraud signals, communication preferences. This is the hard data the agent must ground every response in.

**Source 3 — Compliance Policy API.** Thin FastAPI wrapper over a JSON store. Per issue type: applicable regulations the response must comply with, mandatory disclosures the response must include, escalation triggers (suspected fraud > $X automatically routes to fraud team), retention rules. The exact regulation set depends on the bank's product mix (consumer banking, lending, payments, deposits) and is owned by the bank's compliance team — the FDE's job is to provide the substrate where these rules live as readable, editable config. Hard filter — the agent's draft is checked against required disclosures before send.

**Three things that make this an agent, not a fancy autocomplete:**

1. **Issue clarification.** If the customer message is ambiguous (*"I see a charge I don't recognise"* — is this a fraud claim or a forgotten subscription?), the agent does not guess. It surfaces 2–3 interpretations and either asks the customer one follow-up question (within auto-resolve scope) or surfaces the options to the human agent (Tier 2).
2. **Multi-direction resolution.** Some issues have multiple valid resolutions — *"I want a refund OR a credit OR a fee waiver."* The agent proposes 2–3 tiered options with the trade-off named for each, and the human agent picks. Example output for a fee dispute:

   ```
   Option A — instant fee waiver. Customer satisfaction +. Bank revenue −$25.
   Option B — 30-day no-fee trial. Customer satisfaction +. Bank revenue 0.
   Option C — explanation of the fee. Customer satisfaction −. Bank revenue 0.
   ```
3. **Honest escalation.** When the issue is outside the agent's confidence (unusual dispute pattern, regulatory edge case, signs of customer distress), the agent escalates to a specialist with a complete one-paragraph briefing — not a panic punt.

**Which steps are plain code, which steps are the LLM:**

| Stage | Type |
|---|---|
| Channel intake + transcript normalisation | Deterministic |
| Customer-record lookup (by account ID) | Deterministic |
| Compliance-policy lookup (by issue type) | Deterministic |
| Vector retrieval (top 20 by cosine on prior cases) | Deterministic |
| Disclosure-check on drafted response | Deterministic (rule-based) |
| Issue classification | LLM (Sonnet) |
| Issue clarification (ambiguity detection) | LLM (Sonnet) |
| Draft response composition | LLM (Sonnet) |
| Multi-direction proposal | LLM (Sonnet) |
| Routing decision (auto-resolve / agent / specialist) | LLM (Sonnet) — output validated against deterministic risk-score table |

LLM calls per interaction: 2 on the clean path (classify + draft), 3–4 on the clarification or multi-direction path. At Sonnet rates, ~$0.07 per interaction.

**Phase 3 enhancement (not in scope for the 4-day build):** an internal-knowledge retrieval layer over the bank's intranet, Slack threads, and senior-agent notes — used here as *supplementary context for the agent's drafting*, not as a standalone tribal-knowledge-capture system (which would be Capstone Option B, a different scenario). Sits outside Phase 2 because it requires ingestion plumbing and per-source data-classification clearance.

### End-to-end workflow — who does what

1. **Customer initiates an interaction** on any of the five channels.
2. **Channel adapter** normalises the inbound (phone transcript via Whisper, chat/email/social as text) and posts it to the agent's intake queue.
3. **Agent parses the message** into structured signals (issue type, customer ID, claimed facts, sentiment). If ambiguous, agent generates 2–3 interpretations and asks one clarifying question to the customer (auto-resolve scope) or surfaces them to the human agent (Tier 2 / Tier 3 scope).
4. **Agent pulls context:** customer record, top 20 similar prior cases (VDB), applicable policy. All three in parallel, ~1–2 seconds combined.
5. **Agent drafts the resolution:** classifies the issue, composes the response text, picks the action, computes a confidence score against the deterministic risk-score table.
6. **Routing decision:**
   - **Tier 1 — auto-resolve.** Confidence ≥ 0.90 AND risk-score ≤ low-risk threshold AND issue type in the auto-resolve allow-list (balance inquiries, transaction status, standard fee waivers, address changes). Agent sends the response and books the action. **Audit log captures everything.**
   - **Tier 2 — agent review.** Default for most interactions. Human agent sees the drafted response with sources, confidence score, and any flagged risks. Agent can approve, edit, swap to a different option, or escalate.
   - **Tier 3 — specialist routing.** Complex disputes, fraud, regulatory edge cases, distressed customers. Agent surfaces a complete one-paragraph briefing and routes to the right specialist team.
7. **Human agent (Tier 2) sends the response** after review. Final text + edits captured.
8. **Outcome captured back** — did the customer respond? did they re-open? was the resolution accepted? Feeds the success metrics and the learning loop.

### HITL moments — three places the human stays in the loop

- **A. Pre-send review (default).** Workflow step 6 Tier 2. **The agent never auto-sends in Tier 2 or Tier 3. The agent never auto-sends in Tier 1 unless three independent conditions all hold (confidence ≥ 0.90 AND low-risk AND issue in allow-list). Both the allow-list and the thresholds are owned by the CCO and the Chief Compliance Officer, not by the FDE.**
- **B. Clarification surface.** Workflow step 3. If the message is ambiguous, the agent never guesses what the customer meant.
- **C. Specialist escalation.** Workflow step 6 Tier 3. When the agent is below confidence threshold or detects a regulatory edge case, it routes with a complete briefing.

### The credibility safeguard

ResolveOne is invisible to the customer. The customer sees the bank's branded response, not an AI tool. If the agent ever produces a bad draft or a wrong policy citation, the human agent intercepts it at step 6 — the customer never sees the failure. **The bank's regulatory standing does not depend on the agent being perfect; it depends on the human agent staying in the loop on anything outside the narrow auto-resolve allow-list.**

The audit log records, per interaction: what data the agent pulled, what it drafted, what the human agent edited, what was finally sent, why. Over time, the gap between draft and sent is the drift signal — if it stays small, the agent is calibrated. If it grows, prompts or thresholds are re-tuned before a CFPB examiner notices.

### Reliability and source-availability

The agent depends on three internal data sources (Context VDB, Customer Record API, Compliance Policy API) and one LLM provider (Anthropic for Sonnet). Honest accounting of what happens when any of them are degraded:

- **Clean path latency target (p95):** ≤ 30 s end-to-end with all sources healthy. Mean ≤ 12 s. Composition: vector retrieval (~0.5 s) + two structured API calls (~0.5 s) + two Sonnet calls for classify + draft (~10–15 s combined).
- **Source-degradation behaviour.** If any of the three sources is unreachable, the agent surfaces an explicit error to the human agent within 5 s ("Compliance Policy API unreachable — cannot verify required disclosures; routing to manual handling"). The agent does NOT silently produce a draft missing disclosure citations.
- **Business impact of agent downtime.** Human agent reverts to today's manual workflow (18-min handle time, six-system juggle). No customer sees a degraded response. Loss of speed gain, not loss of compliance.
- **Availability target.** Agent uptime ≥ 99.5%. Anthropic typically runs 99.9%+; the binding constraint is the bank's own infrastructure and the internal APIs.

---

## 5. Channels and business case

The agent processes inbound interactions across five channels. **Phase 1 of the build covers chat and email only** — per the David Okonkwo (CTO) red line in §3, the legacy Avaya telephony stack must not be touched. Phase 2 adds real-time phone via Whisper transcription, but only on the modernised platform David is independently building. Social media and branch referrals are out of scope for Phase 1 — social-media direct messages can join Phase 1.5 with light additional work; branch referrals remain a human-only motion.

**Honesty on the numbers below.** Every figure in this section is an estimate calibrated against industry pattern, not measured against a real bank's data. Sources for each value are in the right-hand column of every table. The seven specific doubts I have already named — issue-type mix, agent rate, auto-resolve eligibility share, regulatory acceptance timeline, integration complexity, customer satisfaction impact, drift over time — sit in §5.7, each with what breaks if it is wrong. The combined-worst-case floor sits in §5.6. **All figures are in USD — the scenario is a US financial services company under CFPB jurisdiction, so the contract would be denominated in USD.**

### 5.1 Pilot slice — named boundaries, all flagged

The full enterprise (4,500 interactions/day across the company) is the Phase 2/3 target, not the Phase 1 pilot. Phase 1 narrows the engagement to a slice with named boundaries — a coach will (rightly) push back on "30% of volume" as a percentage without anchors:

| Slice dimension | Phase 1 scope | Source |
|---|---|---|
| **Customer segment** | Retail banking (consumer checking + savings); commercial accounts out of scope | Lowest regulatory complexity; largest issue volume; CCO + Compliance choice |
| **Issue type** | Balance inquiries + transaction-status checks + standard fee waivers ≤ $50 | Lowest-risk subset; **the allow-list I propose, pending Amanda + Jennifer joint approval** |
| **Channels** | Email + chat only | Per §3 — David's red line on Avaya stack. Social DMs join Phase 1.5 if Tier-2 acceptance holds. Phone waits for the modern infrastructure |
| **Geography** | East-Coast region first, then expand | Single time-zone for the support team; single regulatory state-overlay (NY, CT, MA, PA) |
| **Team** | One customer service team (~25 agents) serving the slice | Single trust-ramp population; single set of feedback loops |
| **Volume** | ~30% of company daily = ~1,350 interactions/day, ~337,500/year | **FDE estimate, not measured.** 30% is the *combined* effect of the four dimensions above — could be 15% at a complex commercial bank or 50% at a retail-focused fintech. Sensitivity row in §5.6 covers the 15% case. To be confirmed during discovery week. |
| **Duration of pilot** | 90 days agent-assist; +90 days before any auto-resolve enabled | Per §5.7 doubt #4 regulatory ramp |

Phase 1 covers the named slice above. Phase 2 adds real-time phone via Whisper on the modernised platform. Phase 3 expands across customer segments, issue types, and the full agent population. (ResolveOne's internal phases are independent of the Deliverable #2 compounding roadmap, which is MedFlex-internal — see D#2 §7 for the cross-vertical hypothesis the capstone tests separately.)

### 5.2 Time and volume assumptions — all flagged

| Variable | Value | Source |
|---|---|---|
| Pilot interactions per day | ~1,350 | Derived from the four §5.1 dimensions |
| Working days per year | 250 | US calendar standard |
| Annual pilot volume | ~337,500 | 1,350 × 250 |
| Average handle time today | 18 min | Stated in §1 from Option C scenario |
| Phase 1 target handle time (agent-assist) | 12 min | Saves ~6 min/interaction from context-pulling and drafting; deterministic part of the workflow |
| Phase 2 target handle time | 9 min | Plus selective auto-resolve on a subset within the slice |
| Customer service agent fully loaded rate | $35/hour | US FS customer-service mid-range. Breakdown: salary ~$24/h + benefits ~$7/h + management overhead ~$4/h. Sensitivity row in §5.6 covers a $25/hour stress case (offshore or lower-tier) |
| LLM cost per interaction (Sonnet, 2 calls clean path) | ~$0.07 | Per §4; Sonnet at public mid-2025 rates (Anthropic pricing page) |

### 5.3 Annual saving on the pilot slice — Phase 1 (agent-assist)

- Interactions per year on slice: 337,500
- Time saved per interaction: 18 min − 12 min = **6 min**
- Annual time saved: 337,500 × 6 min ÷ 60 = ~33,750 hours
- Annual labour saving: 33,750 × $35 = **~$1,181,250/year**
- LLM cost: 337,500 × $0.07 = ~$23,625/year
- **Net Phase 1 saving on the slice at full sustaining rate: ~$1,157,600/year**

### 5.4 Annual saving on the pilot slice — Phase 2 (selective auto-resolve added)

- Auto-resolve eligible subset: ~25% of slice = ~84,400 interactions/year
- Time saved per auto-resolved interaction: 18 min (full replacement of agent time) = **18 min**
- Agent-assist on the remaining 75% of slice (~253,100 interactions): time saved per interaction = ~9 min (deeper assist as the agent matures)
- Auto-resolve saving: 84,400 × 18 min × $35 ÷ 60 = ~$886,200/year
- Agent-assist saving: 253,100 × 9 min × $35 ÷ 60 = ~$1,328,775/year
- LLM cost: ~$23,625/year (constant; auto-resolve uses same agent loop)
- **Net Phase 2 saving on the slice at full sustaining rate: ~$2,191,350/year**

### 5.5 Build cost and payback (ramp-adjusted)

| Line | Value | Source |
|---|---|---|
| Phase 1 build cost (POC for the slice) | ~$60,000 | FDE estimate: ~6 weeks × $1,500/day FDE rate + ~$15k client-side change management. Standalone build with no platform precedent. |
| Phase 2 marginal build cost | ~$25,000 | Estimate; Whisper integration + auto-resolve guardrails + compliance review |
| Enterprise integration cost (6 systems, full bank) — out of Phase 1 scope | ~$200,000 | Named here for honesty; not in the Phase 1 / Phase 2 payback math |

**Headline payback numbers are NOT the naive build-cost-over-monthly-saving ratio.** Customer-service AI in regulated FS has a real trust-ramp curve:

- **Months 1–3 (cold start):** agent draft quality is low, sync agents rewrite ~60% of drafts, average net time saving per interaction ~2 min (not 6). Effective Phase 1 saving in this period: ~30% of sustaining rate = ~$87,000/quarter.
- **Months 4–6 (mid-ramp):** rewrite rate drops to ~40%, time saving climbs to ~4 min. Effective saving: ~$200,000/quarter.
- **Month 7 onwards (sustaining):** rewrite rate ~30%, time saving ~6 min. Effective saving: ~$290,000/quarter.
- **Cumulative net saving by end of month 6:** ~$287,000 vs build cost $60,000.

**Phase 1 ramp-adjusted payback: ~4 months** (vs naive 0.6 months — the naive number assumes Day-1 full saving, which is not how regulated FS deployments work).

**Phase 2 incremental payback timing.** Phase 2 build is incurred around month 9 (during agent-assist sustaining). Auto-resolve cannot enable until regulatory acceptance — realistically month 12 (per §5.7 doubt #4). Once enabled, Phase 2 marginal saving runs at ~$1M/year. Marginal payback once auto-resolve enabled: ~0.3 months. **But the calendar gap from project start to first Phase 2 saving is ~12 months.** That is the honest number to put in front of the CCO.

The economics still hold — even with the ramp, Phase 1 cumulative net is positive inside the first year and Phase 2 unlocks a multi-million-dollar saving once regulators clear it. **The honest constraint is not the economic case; it is the regulatory and trust ramp** — see §5.7 doubt #4.

### 5.6 Sensitivity — one variable at a time (at sustaining rate, not ramp-adjusted)

| Stress | New Phase 1 sustaining saving | Ramp-adjusted payback |
|---|---|---|
| Customer service agent rate $25/hour (lower-tier or offshore) | ~$827,000/year | ~6 months |
| Pilot volume 15% of total (half the assumed slice share) | ~$579,000/year | ~7 months |
| Time saved per interaction only 3 min (not 6) | ~$579,000/year | ~7 months |
| Auto-resolve allow-list shrinks to 5% of slice (vs 25% in Phase 2) | Phase 2 sustaining drops to ~$1.5M/year | Phase 2 calendar still ~12 months, then fast |

Each individual stress keeps Phase 1 payback under 9 months. **Combined worst case** (low rate × half volume × half time saved × shrunk allow-list = 0.124 multiplier on the sustaining baseline): saving falls to **~$143,000/year sustaining**, ramp-adjusted payback **~10–12 months**. Still positive within a standard 18-month enterprise hurdle; no longer compelling. That is the floor under which we should not pitch this product.

### 5.7 What I do not know yet — honest

The seven doubts I have already named, each with what breaks if it is wrong.

1. **Real issue-type mix at any given bank.** The 30% balance + transaction-status + standard fee waiver share is my estimate. Could be 15% at a complex commercial bank or 50% at a retail-focused fintech. If wrong: slice volume shifts, sensitivity row in §5.6 covers the 15% case.
2. **Customer service agent fully loaded rate.** $35/hour is US FS mid-range. Could be $25 (low / offshore) or $50 (senior or specialist). If wrong: linear shift in absolute saving; sensitivity row covers $25.
3. **Time saved per interaction.** 6 minutes is the design target — splits across context-pulling (~3 min) and draft composition (~3 min). If the human agent does not trust the drafted response and re-writes it from scratch, the draft-composition saving evaporates and per-interaction saving drops to ~3 min.
4. **Regulatory acceptance timeline.** CFPB and state banking regulators are conservative. Even with auto-resolve restricted to low-risk + high-confidence, the CCO + Chief Compliance Officer will demand a long pilot period before opening the auto-resolve allow-list. **Realistic auto-resolve ramp: 6–9 months of agent-assist only before any auto-resolve is enabled.** Phase 2 numbers assume this gate is passed; if regulators push back, Phase 2 slips by 6+ months.
5. **Integration complexity across six systems.** Each system's API quality, auth model, and rate limits is unknown until discovery. The $200k enterprise integration estimate is a rough number; could be $100k or $500k depending on how cleanly the bank's systems expose data.
6. **Customer satisfaction impact.** Faster handle time can correlate with worse customer experience if the agent's draft feels formulaic. The acceptance rate (success metric #3) is the leading indicator; if it stays below 70%, the time saving is real but customer trust is at risk.
7. **Drift over time.** Regulatory rules change, banking products change, fraud patterns change. The Compliance Policy API needs an owner inside the bank to keep it current. Without one, the agent silently cites stale disclosures and the audit trail looks fine until an examiner finds the gap.

---

## 6. Why it is hard enough

**ATX Volume × Value score** (per `inputs/atx/atx-scoring.md` §Step 2):

- **Volume = 5.** Very frequent — 4,500 interactions/day, continuous stream.
- **Non-deterministic decision effort = 5.** High reasoning — synthesis across six systems, policy interpretation, contextual judgment per regulation.
- **V×V = 25.** Top of the scale, strong agentic candidate.

**ATX suitability gate** (§Step 1) passes on all four checks: input structure at least Medium (channel-normalised text), decision determinism Medium (patterns with contextual exceptions), tool coverage High (six existing backends), compliance risk High but with viable HITL + audit design per §3.

Three places where the agent has to actually think:

**a. Six-system coordination is the cognitive load, not the response.** A customer service agent today spends most of the 18 minutes navigating six systems and assembling the picture. The "what to do" is often obvious once the picture is complete. So the agent's job is mostly *retrieval and synthesis under regulatory constraints*, not generative cleverness. That is a different shape from most demo agents — context-heavy, decision-light.

**b. Regulatory compliance is a hard filter, not a soft preference.** Different issue types carry different mandatory disclosures and response-timeline requirements. Missing one is a regulatory finding, not a polish issue. The agent has to enforce these as hard pre-send checks against the Compliance Policy API — *the LLM cannot be trusted to remember every rule*, so the deterministic disclosure-check stage is non-negotiable.

**c. Knowing when to escalate to a specialist is the hardest call.** Customer distress, suspected fraud, regulatory edge cases — the agent has to recognise these without being able to verify them, and route with a complete briefing rather than a panic punt. This is calibrated confidence — the agent knowing what it does not know — and it is the hardest single thing to build right.

---

## 7. What I expect to learn

- How to build calibrated confidence into an LLM agent specifically for regulated decisions. The gap between *"the LLM thinks this is high-confidence"* and *"the deterministic risk-score table agrees"* is where most agentic FS systems fail.
- How to design the deterministic-vs-LLM split when regulatory rules cannot be trusted to the LLM. The disclosure-check stage is a worked example; I expect to discover more in the build.
- Whether the multi-direction resolution pattern (tiered options with explicit trade-offs) is actually useful for human agents, or whether it slows them down vs a single ranked recommendation. Testable by demoing both shapes side by side.
- Where the boundary sits for mock-data realism in a 4-day FS project. Mock customer records, mock prior tickets, mock policies — too little and the demo feels fake, too much and the build never starts.

---

## 8. Scope and 4-day plan (Week 5)

**Honest scope discipline.** A 4-day build cannot deliver everything in the design. What follows is what gets built, and what gets demonstrated architecturally but not built.

**What IS built (the prototype):**
- Three-source architecture (Chroma VDB + Customer Record API + Compliance Policy API)
- Intake pipeline + classification + risk-score table (deterministic)
- LLM draft composition + issue clarification
- Three-tier routing (Tier 1 auto-resolve / Tier 2 review / Tier 3 escalate)
- Deterministic disclosure-check (the load-bearing component)
- Audit log
- Three demo interactions — one per tier
- One failure-mode test (a source unavailable)
- Simple Gradio UI

**What is designed-but-NOT-built (named explicitly in the demo):**
- **Multi-direction resolution.** The tiered-options pattern (§4 third agentic addition) is described in the design and shown on a slide, but the prototype demonstrates only single ranked recommendation. Reason: prompt engineering for the tiered trade-off output is the highest-complexity component and would consume Wednesday's whole budget at the expense of clarification + escalation. Promoted to Phase 1.5 build.
- **Phase 2 auto-resolve flow.** Talked through with the architecture and the §5.4 economics; not built. Reason: auto-resolve requires the regulatory ramp before it can be exercised meaningfully, so a demo of "agent auto-sends to a mock customer" is a fake demo. Honest framing in the defense: *"here is what auto-resolve will look like once Compliance opens the allow-list."*
- **Full 10-policy library.** Built with 5 representative policy entries, one per major regulation family. The shape transfers; the volume does not need to be in the prototype.

| Day | Output |
|---|---|
| **Monday** | Mock data: ~50 customer records (account states, transactions 60 days, prior tickets 12 months, KYC, fraud signals). ~15 prior resolved interactions across the issue-type taxonomy for the VDB (cut from 30 — covers the three demo paths plus margin). 5 compliance policy entries representing the major regulation families. 3 sample inbound interactions (clean Tier 1 / clarification / escalation). Issue-type and risk-score taxonomy locked. |
| **Tuesday** | All three sources standing locally. Intake pipeline + classification + risk-score table working end-to-end. First interaction returns a routed response using only deterministic logic — no LLM drafting yet. |
| **Wednesday** | LLM draft composition wired in. Issue clarification flow. Routing decision against the risk-score table. **Dedicated 2-hour block to tune the disclosure-check prompt and the risk-score thresholds against the 5 policy entries** — these are the load-bearing components per §6b/c. End-to-end works on all three sample interactions. |
| **Thursday** | Gradio UI (paste an inbound interaction, see classification + draft + routing + audit log). Three demo interactions hand-picked to show clean Tier 1 / Tier 2 review / Tier 3 escalate. Failure-mode test: Compliance Policy API unavailable, verify agent fails loud within 5 s. Demo dry-run + edge-case sweep. |
| **Friday morning** | Demo recording. Capstone write-up polish. Defense prep. |

---

## 9. Risks and what I would do about each

| Risk | What I would do |
|---|---|
| Mock data takes longer than Monday | Cap at 50 customers, 30 prior cases, 10 policies. Use an LLM to bulk-draft the prior cases and customer histories; hand-curate the policies (those need to be accurate to the regulations). |
| LLM produces a non-compliant draft | Deterministic disclosure-check after every draft. If the check fails, the draft is rejected and re-prompted with the missing-disclosure list. Human agent never sees a draft that failed compliance. |
| Demo feels static | Three pre-scripted inbound interactions that each trigger a different agent behaviour. The variety is the demo. |
| *"This is just GPT-4 wrapped in a UI"* | Show the deterministic-vs-LLM table from §4. Name the three external sources. The deterministic disclosure-check is the load-bearing component the LLM cannot do alone. |
| Vector DB choice over-engineered | Chroma local, nothing managed. If a coach asks about scale, the answer is "Chroma handles ~1M vectors before we would think about migrating; the bank's prior-case corpus is probably 10–100k records." |
| Auto-resolve produces a wrong response | The auto-resolve allow-list is owned by the CCO and the Chief Compliance Officer, not by the FDE. The agent's confidence + risk-score must clear thresholds set by them. Sampling audit on 100 auto-resolved interactions/week catches drift early. |
| Phase 2 phone audio quality | Whisper handles clean audio well; phone audio is often noisy. If transcription quality drops, route to manual handling rather than producing a degraded draft. |

---

## 10. Coach challenge — questions I expect

**"Why an agent, not a workflow automation tool?"**
Workflow automation handles deterministic flows — if-this-then-that. Customer interactions are not deterministic. The same inbound message ("I want to dispute a charge") covers fraud, billing error, forgotten subscription, and chargeback abuse — each with a different resolution and a different regulatory regime. The agent classifies the issue and chooses the resolution path; workflow tools cannot.

**"What does the LLM actually decide?"**
Three things. It classifies the inbound issue (mapping free-text into the taxonomy). It composes the draft response (grounded in the customer record and policy). It picks the resolution direction when multiple are valid. The hard filters (disclosure check, risk-score, auto-resolve allow-list, escalation triggers) are deterministic. The agent stitches the three sources together and produces a draft a human agent can defend; the LLM is one tool inside that.

**"Why financial services and not retail?"**
Higher volume per interaction, higher cost per interaction (specialist agents earn more), higher regulatory premium on the audit trail (CFPB makes audit-trail completeness non-optional, which makes the agent's "every source + every edit logged" architecture a feature instead of an afterthought). Retail customer service has the same shape but weaker pull on the audit-trail premium.

**"Why the CCO and not the customer service operations manager?"**
The ops manager owns headcount and queue throughput; the CCO owns customer outcomes and regulatory standing. Customer service AI sold to ops manager focuses on cost reduction (headcount), which raises ops-floor resistance. Sold to the CCO, it focuses on first-contact resolution and audit-trail completeness, which the CCO is measured on and the ops floor is more receptive to.

**"What are the unit economics?"**
See §5. Phase 1 on the slice (1,350 interactions/day, ~30% of company volume) saves ~$1,157,600/year at sustaining rate, net of LLM cost. **Ramp-adjusted payback ~4 months** on a $60,000 build — the naive 0.6-month number assumes Day-1 full saving, which is not how regulated FS deployments work. Phase 2 (selective auto-resolve) unlocks an additional ~$1M/year of saving but needs regulatory acceptance — calendar gap from project start to first Phase 2 saving is ~12 months. Combined worst-case stress (low rate × half volume × half time saved × shrunk allow-list) drops sustaining saving to ~$143,000/year, payback ~10–12 months. Still positive inside a standard 18-month enterprise hurdle.

**"What happens at full bank scale?"**
The slice is ~30% of company volume. At full scale (all issue types, all customer service agents, retail + commercial), Phase 1 saving extrapolates to ~$3.9M/year at sustaining rate. Enterprise integration adds ~$200k upfront. Payback at the company level stays under 6 months even ramp-adjusted. The binding constraint at scale is not economics — it is the regulatory acceptance ramp.

**"How do you know the responses are good?"**
Four layers. **CSAT delta (#5)** — the customer says so directly via post-interaction survey. **First-contact resolution (#2)** — the customer does not come back. **Agent acceptance rate (#3)** — the human agent sends the drafted response without rewriting it. **Auto-resolution accuracy (#4)** — sampling audit on 100 auto-resolved interactions per week, CCO + Compliance review. CSAT is the buyer's KPI (Amanda); without it the proposal is not actually answering her question. The human agent has veto on every draft in Tier 2/3; auto-resolve operates only inside a narrow allow-list with three independent confidence + risk checks.

---

## 11. Curveball rehearsal (2-minute practice answer)

**Curveball:** *"The CFPB just issued guidance that any AI-generated response sent to a customer must include an explicit AI-use disclosure. Effective immediately."*

**Response.** The architecture survives; the response template changes. Three concrete adaptations.

First, the deterministic disclosure-check (already in the pipeline per §4) picks up a new mandatory clause: an AI-disclosure line appended to every agent-touched draft. Compliance Policy API gets a new entry. The code change itself is small (one prompt update + one policy entry + a regression test), but the *real* work is Legal review of the disclosure language and customer-experience review of the A/B test — those add ~2 weeks of calendar time before we ship.

Second, the auto-resolve allow-list contracts immediately. CFPB conservatism means the CCO will pause auto-resolution until the disclosure language is reviewed. Phase 2 slips by 3–6 months while Tier 1 reverts to Tier 2 (every response human-reviewed). Net economic impact: lose the auto-resolve incremental saving (~$1M/year on the slice). Phase 1 saving (~$1.2M/year from agent-assist) is unaffected because the human agent stays in the loop.

Third, customer satisfaction needs explicit re-measurement. An AI-use disclosure can be neutral, positive (transparency), or negative (eroded trust). Set up an A/B comparison over 30 days. Use that data to negotiate the disclosure wording with the CCO and the compliance team.

Data sources do not change. Agent loop does not change. The disclosure-check stage absorbs the new rule the way it was designed to absorb regulatory change. That is the point of the deterministic-vs-LLM split — regulation lives in the deterministic layer, where it can be edited as a config change, not retrained.
