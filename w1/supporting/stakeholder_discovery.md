# Virtual Stakeholder Discovery
## What This Document Is

This document simulates a structured discovery process with the key stakeholders at the retailer. In a real FDE engagement, these would be conducted as 30–60 minute interviews before any spec is written.

Because this is a practice scenario, the answers are **inferred from scenario context + retail industry knowledge**. Every answer that goes beyond what the scenario states is marked `[Inferred]`. These inferences directly feed the Assumptions & Unknowns register.

The purpose is: **know what you know, know what you don't know, and make your bets explicit.**

---

## Stakeholders Interviewed

| Role | Name (fictional) | Why They Matter |
|---|---|---|
| VP of Operations | Sandra Kowalski | Primary sponsor; owns the mandate and the budget |
| Returns Team Lead | Tomasz Nowak | Operational ground truth; knows what actually breaks |
| CFO / Finance Director | Maria Chen | Owns the margin-improvement mandate; needs the payback story |
| Loss Prevention Manager | David Osei | Owns fraud detection; the hardest constraint in the spec |

---

## Interview 1 — VP of Operations (Sandra Kowalski)

**FDE:** Sandra, thanks for your time. Let me start with the core pain: what made you decide now is the moment to act on this?

**Sandra:** Two things collided. One, Q4 volume was brutal — we hit 6,000 returns in one week around Christmas and the team just couldn't keep up. We had a four-day backlog and merchandise sitting idle. Two, the CFO finally saw the chargeback report and asked me directly why we weren't catching more fraud upfront. That was an uncomfortable conversation.

> *Learning: volume spikes are a real operational constraint — the system needs to scale above 4,500/week. Peak capacity matters.*

**FDE:** You mentioned you want agentic handling for easy cases and human judgment for hard ones. Can you describe a return you'd call "easy"?

**Sandra:** Something like: customer bought a blouse, tried it on, said it didn't fit, condition is basically new. That's 70% of what we see. The processor spends four minutes confirming the obvious. The agent should handle that in seconds.

> *Learning: VP estimates 70% of returns are routine. Current state analysis estimated 65–70%. This is a usable baseline for the autonomous handling rate target.*

**FDE:** And a "hard" one?

**Sandra:** The fraud cases are the hard ones. But also anything expensive — over, say, $100 retail. And if a customer has called the contact centre and escalated, those need human eyes because there's a relationship risk now.

> *Learning: VP volunteered a threshold for "high-value" — $100 retail price. This is an assumption that can now be documented as "VP indicated $100 as approximate threshold" rather than purely inferred. Still needs formal confirmation.*

**FDE:** One thing I want to make sure I understand: the agent flagging fraud vs. the agent deciding on fraud — where's your line?

**Sandra:** The agent absolutely cannot clear a fraud-flagged return. That is Loss Prevention's call. The agent can flag, the agent can hold, but the decision to proceed or reject sits with David's team. That's non-negotiable — we had a situation two years ago where someone overrode a fraud flag on a $400 jacket and it turned into a $12K chargeback exposure. Never again.

> *Learning: Confirmed hard constraint — fraud disposition requires Loss Prevention sign-off. This is an explicit escalation gate, not a soft guideline.*

**FDE:** What systems does the team currently work with at the processing station?

**Sandra:** They have a screen with our WMS — Manhattan Associates — and they can look up orders in our OMS which is Salesforce Commerce Cloud. Returns are initiated through our Narvar return portal. The station itself is just a barcode scanner and a keyboard. No camera.

> *Learning: Systems confirmed — Manhattan WMS, Salesforce Commerce Cloud OMS, Narvar returns portal. **No camera at intake station** — image-based condition assessment is not feasible. This eliminates a common AI approach and shapes the spec significantly.*

**FDE:** Last question for now: if you had to describe success in 12 months, what would it look like?

**Sandra:** Half the team redeployed to higher-value work. The backlog gone. Fraud chargebacks down 50%. And I want to be able to tell the CFO what our actual return rate by reason is, with data I trust.

> *Learning: CFO success metric = fraud chargebacks down 50%. Team redeployment target = ~6 FTEs. Data trust = reason-code accuracy as a measurable KPI. These are the success metrics for Artifact 1.*

---

## Interview 2 — Returns Team Lead (Tomasz Nowak)

**FDE:** Tomasz, I want to understand what the work actually feels like on the floor. Walk me through a typical morning.

**Tomasz:** We start with whatever came in overnight. Usually 150–200 items waiting. We scan, we check the order, we look at the reason they gave, we look at the item, we tag it, we put it in the bin. Most of the time it's obvious. But when it's not obvious, everyone handles it differently. Lisa will call something defective; Michal will call the same thing changed-mind. Drives the data crazy.

> *Learning: Confirms the accuracy problem is primarily inter-processor inconsistency, not systemic inability to classify. A rulebook (enforced by an agent) would close most of this gap.*

**FDE:** What's the trickiest classification call you make regularly?

**Tomasz:** "Defective" versus "customer damage." Customer says the seam split — was it our fault or did they stress it? We're supposed to put defective, but if it's customer damage it should go back to the outlet at their expense in theory. Nobody enforces this consistently. And "changed mind" versus "didn't fit" — matters a lot for the analytics but customers often just pick whichever sounds better for a free return.

> *Learning: The DEFECTIVE / CUSTOMER_DAMAGE distinction is a real edge case. The agent spec needs a rule for this. Also: customers deliberately mis-classify to avoid fees — this is input noise the agent must handle.*

**FDE:** When you suspect fraud, what tips you off?

**Tomasz:** Usually it's weight. A $300 jacket comes back and it feels lighter than it should. Someone swapped the lining or stuffed it with newspaper. Or the tags are slightly off — not our tags. Or it's someone who returns every month like clockwork. But I can't look up order history at my station right now, so the history signals I miss.

> *Learning: Key fraud signals are: (1) item weight anomaly, (2) tag authenticity, (3) return frequency. The agent can address (3) directly via OMS lookup. Items (1) and (2) require physical inspection — currently not automated. The spec must be honest about which signals the agent can access.*

**FDE:** If a tool showed you a fraud risk score for each item before you even touched it, would you trust it?

**Tomasz:** If it showed me why — yes. If it was just a number — no. I need to see "this customer has returned 5 times in 30 days" or "this SKU has a 12% fraud rate historically." Then I can make a call. Just a red flag with no explanation, I'd ignore it.

> *Learning: Fraud flag must include explainable evidence — not just a score. This is a spec requirement for the escalation notification.*

**FDE:** How long does it take a new person to be fully productive?

**Tomasz:** Six weeks if they're good. Sometimes eight. It's all muscle memory — knowing what $100 worth of fabric looks like, knowing which SKUs get targeted for fraud. Can't really write it down because we've never had to.

> *Learning: Confirms the tribal knowledge problem. Encoding this knowledge into the agent's classification logic is the core value of the project. Onboarding time reduction is an additional ROI lever.*

---

## Interview 3 — CFO / Finance Director (Maria Chen)

**FDE:** Maria, what does success look like financially for this project?

**Maria:** I need to see a return within 18 months. The mandate I gave Sandra is $400K in margin improvement year-one. That can come from anywhere: labor redeployment, recovered merchandise value, reduced fraud loss, faster restocking.

> *Learning: 18-month payback target. $400K year-one margin improvement mandate. This is the financial bar the problem statement must address.*

**FDE:** How do you currently account for return losses?

**Maria:** We have three buckets. Merchandise recovery — the difference between what we actually recover vs. what we could have recovered if disposition was optimal. Fraud losses — chargebacks where we can't recover the merchandise value. And processing cost — the labor and overhead at the facility. Combined they run about $2.1 million a year.

> *Learning: Total addressable loss is $2.1M/year. A $400K improvement target = 19% improvement on a $2.1M base. This is achievable and defensible. Document in problem statement.*

**FDE:** What's the merchandise recovery piece specifically?

**Maria:** Roughly $900K. A lot of it is items going to outlet or donate that should have been restocked. If an item is LIKE_NEW it should go back on the shelf, not to a 40% off rack. That's a $60 item becoming a $24 recovery. We estimate 15% of restockable items end up misrouted, which at our volume is meaningful.

> *Learning: Merchandise recovery loss = $900K/year. 15% misrouting rate confirmed. If agent improves routing accuracy by 50% on those cases, that's $225K recovered — more than half the $400K target from this bucket alone.*

**FDE:** What level of agent error is acceptable to you?

**Maria:** On fraud — zero autonomous errors. The agent cannot clear a fraud case. On general classification — if it's better than the current 78% human accuracy and we can measure it, I'm satisfied. Show me the accuracy dashboard and the trend, and I'll accept occasional errors as the cost of speed.

> *Learning: Finance is comfort with imperfect automation on classification (as long as it beats 78% and is measured), but zero tolerance for autonomous fraud decisions.*

---

## Interview 4 — Loss Prevention Manager (David Osei)

**FDE:** David, the VP mentioned fraud detection is your domain. How does it work today?

**David:** Not well. My team reviews the SUSPECTED_FRAUD flags that come from the floor — maybe 15–20 cases a week that get flagged. But chargebacks come in 30–60 days later and I can see we missed 50–60 cases per week that should have been flagged. My team is small — 2 investigators — and they can't do retrospective review at that scale.

> *Learning: Loss Prevention reviews ~15–20 flagged cases/week but misses 50–60/week in hindsight. Current manual flag rate ≈ 25–35 cases/week total (flagged + what would have been flagged). Agent target: flag 80%+ of the cases that are currently only caught retrospectively.*

**FDE:** What data would your team need to investigate a case?

**David:** The item's order history — what was originally ordered, when, and the full customer return history. The return reason claimed vs. what the processor actually saw. A photo if we have one (we usually don't). And the fraud signals — what specifically triggered the flag. We need all of that in one screen, not scattered across three systems.

> *Learning: The fraud escalation notification must aggregate: order history, customer return history, claimed reason, processor observations, and fraud signal list. This is a specific spec requirement.*

**FDE:** What threshold would trigger an escalation to your team?

**David:** Any item where two or more fraud signals fire. One signal is noise — everyone has a bad customer day. Two signals means something's off. Three is almost certainly fraud.

> *Learning: Escalation threshold = 2+ fraud signals. Below threshold → agent classifies normally. At 2+ → hold for Loss Prevention review. This is a numeric, specifiable rule.*

**FDE:** If the agent misses a fraud case and we find it in the chargeback report, what's the protocol?

**David:** That's a feedback loop I want to build. Right now those chargebacks just become a loss. Going forward, every chargeback should generate a retroactive flag on the return record so we can train the model and adjust thresholds.

> *Learning: Chargeback-to-flag feedback loop is a desired future capability. Not in scope for V1 but should be noted as a design consideration.*

**FDE:** One more: do you have a SKU-level fraud rate database?

**David:** Informally, in my head and in a spreadsheet. Some SKUs are targeted much more than others — high-end outerwear, footwear, specific electronics accessories we carry. I can give you the top 20 fraud-targeted SKUs. But it's not in a system.

> *Learning: SKU-level fraud rate data exists but only as a spreadsheet maintained by Loss Prevention. Integration would require data migration. This is an assumption/dependency in the spec.*

---

## Discovery Summary: Confirmed vs. Open

### Confirmed (can be treated as known in spec)

| Item | Source |
|---|---|
| VP threshold for "high-value": ~$100 retail price | Sandra K., Interview 1 |
| No camera at intake station | Sandra K., Interview 1 |
| Systems: Manhattan WMS, Salesforce OMS, Narvar portal | Sandra K., Interview 1 |
| Fraud disposition requires Loss Prevention sign-off | Sandra K., Interview 1 |
| ~70% of returns are "easy" per VP estimate | Sandra K., Interview 1 |
| 18-month payback target, $400K year-one improvement | Maria C., Interview 3 |
| Total addressable return-related loss: ~$2.1M/year | Maria C., Interview 3 |
| Merchandise recovery loss: ~$900K/year, 15% misrouting | Maria C., Interview 3 |
| Fraud escalation threshold: 2+ fraud signals | David O., Interview 4 |
| Fraud flag must include explainable evidence (not just score) | Tomasz N. + David O. |
| Loss Prevention team size: 2 investigators | David O., Interview 4 |

### Still Open (must go in Assumptions & Unknowns)

| Item | Why It Matters | Who to Ask |
|---|---|---|
| Exact API contracts for Manhattan WMS, Salesforce OMS, Narvar | Agent integration design depends on this | IT / Systems team |
| Formal definition of condition grades (LIKE_NEW, GOOD, FAIR, POOR) | Agent classification rubric | Sandra / Tomasz |
| SKU-level fraud rate data — format, completeness, update frequency | Fraud signal design | David O. |
| Seasonal volume peaks (Black Friday, Christmas) — exact multiplier | Capacity planning, SLA design | Sandra / Operations |
| Real-time vs. batch inventory sync in Manhattan WMS | Disposition routing design | IT |
| Customer return history data retention period | Fraud signal lookback window | IT / Legal |
| Loss Prevention SLA for fraud review | Escalation timeout design | David O. |
| DEFECTIVE vs. CUSTOMER_DAMAGE — is there a written policy? | Classification rule for the agent | Sandra / Legal |
| What happens to held items if Loss Prevention doesn't respond within SLA? | Escalation timeout logic | Sandra + David |
| Weight / authenticity signals — is there any scanning equipment at intake? | Fraud signal scope | Operations |
