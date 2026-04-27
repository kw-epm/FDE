# Virtual Stakeholder Discovery — FNOL Processing Agent

## What This Document Is

This document simulates a structured discovery process with key stakeholders at the insurance company. In a real FDE engagement, these would be conducted as 30–60 minute interviews before any spec is written.

Because this is a practice scenario, the answers are **inferred from scenario context + insurance industry knowledge**. Every answer that goes beyond what the scenario explicitly states is marked `[Inferred]`. These inferences feed directly into the Assumptions & Unknowns register.

---

## Stakeholders Interviewed

| Role | Name (fictional) | Why They Matter |
|---|---|---|
| Head of Claims Operations | Sarah Brennan | Primary sponsor; owns the SLA mandate and team |
| Senior Claims Specialist / Team Lead | Marcus Webb | Operational ground truth; knows what actually breaks |
| CFO | Daniel Choi | Owns investment decision; needs payback story |
| VP Customer Experience | Priya Mehta | Owns claimant satisfaction; represents the claimant perspective |

---

## Interview 1 — Head of Claims Operations (Sarah Brennan)

**FDE:** Sarah, what's the immediate pressure driving this initiative?

**Sarah:** Two things. First, we had a bad weather quarter — a hailstorm event in March added 80 claims in a single day on top of our normal 300. The team simply could not absorb it. We had claims sitting unacknowledged for five, six hours. Claimants were calling the main line angry. Second, our state regulator flagged us on SLA compliance in the last audit. We're at 69% compliance on the 2-hour acknowledgment. The threshold they care about is 90%. We're nowhere near it.

> *Learning: Volume spike resilience is a real operational constraint — not just a design aspiration. Regulatory compliance is a direct driver.*

**FDE:** When you say "human oversight for high-value or ambiguous claims" — can you define those terms for me?

**Sarah:** High-value: any claim where the estimated loss is over $50,000. Also any bodily injury claim, regardless of amount — those always need an experienced set of eyes before we route them because of the litigation exposure. Ambiguous: when the text is unclear about what actually happened, or when we're not sure the policy covers it. The specialist has to make a judgment call there.

> *Learning: High-value threshold = $50K estimated loss [Inferred, flagged as Assumption B1]. Bodily injury = always human oversight, independent of financial threshold [Inferred, flagged as Assumption B2]. Ambiguity = coverage uncertainty or unclear incident description.*

**FDE:** What about coverage denial decisions — can those be automated?

**Sarah:** Absolutely not. If we're denying coverage, that has to be a human decision, documented, with the claimant contacted directly. That's a regulatory requirement. The agent can flag that a claim might not be covered, but a specialist has to review and confirm any denial before we communicate it to the claimant.

> *Learning: Coverage denial is a hard human-only constraint — regulatory basis. [Confirmed constraint C1]*

**FDE:** What systems does the team use today?

**Sarah:** The CRM is Salesforce — it has a proper REST API. The policy admin system is older — it's a SOAP-based system our IT team maintains. It's slow sometimes, but it's reliable. And we have a document management system for storing claim documents. The agents don't have direct API documentation for the policy system — that lives with IT.

> *Learning: SOAP system is real but underdocumented. API contracts must be validated with IT. DMS has some API capability but details unknown.*

---

## Interview 2 — Senior Claims Specialist / Team Lead (Marcus Webb)

**FDE:** Marcus, if you had to describe the 70% of claims that feel routine, what do they look like?

**Marcus:** Someone rear-ends another car, they've got comprehensive auto coverage, the policy's active, no injuries. The text is usually clear — "I was in an accident, here's my policy number." I can tell in the first 30 seconds what it is and who to send it to. The whole thing should take 5 minutes, not 22. But it takes 22 because I still have to log into the policy system, look up the policy, check it's active, check the coverage type, find the right adjuster, draft the email. There's no tool helping me.

> *Learning: Structured lookup steps (policy verification, adjuster assignment) are the time sink, not judgment. Automating these is low-risk and high-value.*

**FDE:** What makes a claim genuinely hard?

**Marcus:** Bodily injury. Someone's saying they were hurt — we don't know how badly, there might be a third party involved, there could be a lawyer involved within days. That's not something I'd want a system touching autonomously. Also when the customer's description doesn't match the coverage — "my car got damaged" and they have liability-only, not comprehensive. The agent needs to flag that as a coverage issue, not just route it.

> *Learning: Two categories of hard claims: (1) bodily injury (litigation risk), (2) coverage mismatch (requires specialist interpretation of exclusions).*

**FDE:** The policy admin system — what does it typically take to look up a policy?

**Marcus:** If the policy number is clear in the text, about 90 seconds — I paste it in, the system returns the policy, I check the status and coverage types. Where it breaks down is when the policy number is wrong, or the customer gives us their billing account number instead of the policy number. Then I have to search by name or phone, and that's 5-10 minutes of back and forth.

> *Learning: Policy number extraction from unstructured text is a key parsing challenge. Policy-not-found scenarios are not rare.*

**FDE:** How does the team currently decide which adjuster to assign?

**Marcus:** We have a spreadsheet that maps claim types to adjuster teams. Then within a team, we try to balance the queue — check who has fewer open claims. But honestly, during busy periods, people skip the balancing and just pick the first available adjuster in the right specialty. That's where a lot of the routing errors come from — someone in the wrong specialty gets the claim because they were visible and available.

> *Learning: Routing errors are primarily workload-balancing failures, not specialization mismatches alone. An explicit workload-aware assignment algorithm would directly address the 18% error rate.*

---

## Interview 3 — CFO (Daniel Choi)

**FDE:** Daniel, what does the investment need to justify?

**Daniel:** I want a payback within 18 months. The team costs roughly $750,000 a year fully loaded. If we can handle the easy 65-70% of volume without specialist time, that's labor that can be redeployed. I'm not talking about layoffs — I'd rather have the specialists handling only the complex claims, which is where they add value and where we have quality gaps right now. The regulatory SLA compliance issue is also a cost: each non-compliance event has a remediation cost, and if we get another audit finding, we're looking at potential fines.

> *Learning: Payback target = 18 months. Primary value lever = labor redeployment (not elimination). Secondary lever = regulatory compliance risk reduction.*

**FDE:** What's the regulatory exposure if SLA compliance doesn't improve?

**Daniel:** It varies by state. In our core markets, DOI regulations require acknowledgment within 10 business days for some lines, within 24 hours for others. Our internal SLA is 2 hours, which is tighter than the regulatory floor in most cases. But the pattern of non-compliance creates audit risk. We had to submit a corrective action plan last quarter.

> *Learning: The 2-hour SLA is self-imposed (tighter than regulatory minimum). Missing it doesn't immediately trigger regulatory penalty, but the pattern of misses creates audit and corrective action risk. [Assumption B4 refinement]*

---

## Interview 4 — VP Customer Experience (Priya Mehta)

**FDE:** Priya, what does the claimant experience look like right now?

**Priya:** When someone files a claim, they're usually stressed — car accident, broken window, something has gone wrong. The first thing they need is confirmation that we received it and someone is on it. Right now, 31% of the time, they don't get that within 2 hours. Some of them wait all day. We see this in our CSAT scores after a claim — if they got a fast acknowledgment, satisfaction is high even before the claim is resolved. If they had to wait or follow up themselves, satisfaction drops significantly.

> *Learning: Acknowledgment speed is the primary claimant experience driver — more important than claim resolution speed. A fast, clear acknowledgment with a reference number and adjuster name can neutralise stress even for complex claims.*

**FDE:** What happens when a claim is mis-routed?

**Priya:** The claimant gets contacted by an adjuster who doesn't know their claim type, can't answer their questions, and has to hand them off. Sometimes they have to re-explain the whole situation. It's a trust failure. They start to wonder if we know what we're doing. Retention data shows a measurable increase in non-renewal risk for claimants who experienced a routing error.

> *Learning: Routing errors have a retention cost beyond the rework cost — non-renewal uplift for claimants who experienced them.*

**FDE:** For the acknowledgment — what should it contain to actually reassure the claimant?

**Priya:** Three things: a reference number so they can call and be identified, the name and contact of the adjuster handling their case, and a realistic timeline for the adjuster's first contact. If it's a complex claim, don't overpromise. "An adjuster will contact you within 24 hours" is fine — it sets the expectation. Don't leave them wondering.

> *Learning: Acknowledgment content requirements: (1) claim reference number, (2) adjuster name + direct contact, (3) realistic next-contact timeline differentiated by severity.*
