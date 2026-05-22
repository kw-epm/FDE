# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

This is an **FDE Program Week 2 project** focused on ATX (Agentic Transformation) methodology. The goal is to build a functional prototype for **Scenario 4: Community Content Moderation** from the FDE program scope, applying cognitive work assessment and agent design principles.

**Scenario Context:** MiniBase — UK-incorporated tabletop-miniature hobbyist community platform (~180K active users, 12K posts/day across 14 sub-forums). We are designing and building an AI agent to support the hybrid moderation team (8 volunteer moderators + 2 paid staff) in handling ~1,500 daily posts that enter the moderation queue.

This project is a learning exercise for understanding FDE engineering principles, not a production deployment. The focus is on demonstrating thoughtful delegation architecture, clear agent boundaries, and ATX methodology application.

## Problem Statement

MiniBase's hybrid moderation team (8 volunteers + 2 paid staff) is at capacity handling ~1,500 posts/day that enter the moderation queue (12.5% of total posts). The team's total effort is ~47 hours/day with no ability to scale linearly.

**Core constraints:**

1. **Capacity bottleneck**: 72% of the queue (1,080 posts/day) is routine spam consuming ~9 hours/day of moderator time. This prevents focus on the 24% grey-zone cases (360 posts/day, 30 hours/day) that require genuine human judgment.

2. **Risk asymmetry**: "False positives are survivable; one viral false negative is existential." The platform's reputation depends on catching harmful content while tolerating community-appropriate harsh critique. This creates high cognitive load on every decision.

3. **Volunteer model constraint**: Cannot scale by hiring. 80% of the team are volunteers across time zones (US, UK, Germany, Australia, Japan) who donate limited hours. Burnout risk is real.

4. **Complexity in lived work**: The 14-page moderation policy doesn't capture subforum-specific norms (e.g., painters sub "no critique without invitation"), sponsor account sensitivities (the "2024 incident"), or tribal-knowledge patterns tracked in Tom's Google Sheet.

5. **Coordination overhead**: Volunteer moderators discuss edge cases in Discord; decisions are inconsistent; Tom personally reviews high-risk patterns.

**Business impact if unsolved:**
- Volunteer moderator burnout → reduced coverage → moderation delays → community trust erosion
- Cannot handle growth (platform at 180K users, growing) without degrading quality
- Routine spam consumes capacity that should go to nuanced cases
- Revenue risk: £1.4M/yr depends on premium memberships and sponsor relationships, both sensitive to moderation quality

**The opportunity:** Automate routine spam removal (high volume, low judgment) to free moderator capacity for grey-zone cases (high judgment), while preserving the safety bar and community norms.

## Success Metrics

### Primary Metrics (Business Value)

**Moderator Time Savings:**
- Target: Reduce routine spam handling from 9 hrs/day to <2 hrs/day (77% reduction)
- Measured by: Agent-handled cases × avg time saved per case
- Acceptable range: 60-80% reduction (allows for sampling and edge cases)

**Grey-Zone Case Quality Time:**
- Target: Increase moderator time on grey-zone cases by 7 hrs/day (redirected from spam)
- Measured by: Human moderator time distribution before/after agent deployment
- Goal: Better outcomes on complex cases, not just faster processing

**Throughput at Capacity:**
- Current: 1,500 posts/day with team at 47 hrs/day capacity
- Target: Handle 2,000+ posts/day at same capacity (33% growth headroom)
- Measured by: Posts processed per day without adding moderators

### Quality and Safety Metrics (Non-Negotiable)

**Moderation Accuracy:**
- Routine spam: ≥95% precision (false positive rate ≤5%)
- Grey-zone escalation: 100% of grey-zone cases routed to human review (no auto-removal)
- Measured by: Human audit of agent decisions (daily sample of 50 cases)

**False Negative Rate (Viral Risk):**
- Target: Zero viral false negatives (harmful content reaching community at scale)
- Acceptable: ≤0.1% false negative rate on clear policy violations
- Measured by: Community reports of agent-approved harmful content
- **This is the existential risk metric - cannot be compromised for efficiency**

**Subforum Norm Compliance:**
- Target: 100% compliance with subforum-specific rules (e.g., painters critique rule, historical sub permissiveness)
- Measured by: Moderator override rate by subforum (overrides indicate norm violations)

### Operational Metrics (Agent Performance)

**Coverage Rate:**
- Target: 70-80% of routine spam handled without human intervention
- Measured by: (Agent auto-actions) / (Total routine spam cases)
- Remaining 20-30% escalated for human review (sampling, low confidence, edge cases)

**Escalation Precision:**
- Target: ≥90% of escalations are justified (human agrees case needed review)
- Measured by: Human moderator assessment of escalated cases
- Avoid: Over-escalation (defeats the purpose) or under-escalation (safety risk)

**Confidence Calibration:**
- Target: Agent confidence scores correlate with actual accuracy
- Measured by: When agent reports 0.9 confidence, accuracy is 90%±5%
- Required for: Tuning escalation thresholds and building moderator trust

**Response Time:**
- Target: Routine spam flagged and removed within 5 minutes (currently ~15-30 min avg human response)
- Measured by: Timestamp delta between flag and agent action
- Impact: Reduces spam visibility to community

### Team Sustainability Metrics (Volunteer Health)

**Volunteer Moderator Time Allocation:**
- Current: ~60% routine spam, ~35% grey-zone, ~5% coordination
- Target: ~20% routine spam (sampling/oversight), ~70% grey-zone, ~10% coordination
- Measured by: Time-tracking before/after (weekly volunteer surveys)
- Goal: Volunteers spend time on judgment work they value, not repetitive spam removal

**Moderator Override Rate:**
- Target: <10% of agent actions overridden by human moderators
- Measured by: Human moderator corrections/reversals of agent decisions
- High override rate indicates poor agent calibration or missed norms

**Time-to-Escalation-Resolution:**
- Target: Escalated cases resolved by humans within 30 min (not slower than today)
- Measured by: Timestamp delta between agent escalation and human decision
- Goal: Agent context-gathering speeds up human decisions, not creates backlog

### Cost Metrics (Economics)

**Cost per Case:**
- Routine spam: Target <£0.05/case (token cost + infrastructure)
- Grey-zone triage: Target <£0.10/case (context gathering only, human decides)
- Measured by: Total monthly cost / cases handled
- Compared to: Equivalent human moderator time at £15-20/hr blended rate

**ROI Threshold:**
- Target: 3:1 value/cost ratio (£3 moderator time saved per £1 agent cost)
- Measured by: (Moderator hours saved × blended rate) / (Agent operational cost)
- Acceptable: 2:1 minimum (still economically justified)

### Risk and Compliance Metrics

**Audit Trail Completeness:**
- Target: 100% of agent actions logged with rationale, confidence, and policy reference
- Measured by: Automated log validation
- Required for: Legal compliance, post-incident review, trust/transparency

**Sponsor Account Safety:**
- Target: Zero automated actions on sponsor accounts without Tom's review
- Measured by: Agent escalation rate on sponsor-flagged accounts (should be 100%)
- Business risk: "2024 incident" precedent means this is non-negotiable

**Appeal Handling:**
- Target: User appeals of agent decisions resolved within same SLA as human decisions (currently 24-48 hrs)
- Measured by: Average time to appeal resolution
- Goal: Agent decisions feel as legitimate as human decisions to community

## Success Definition (Gate 2 Context)

For this Week 2 learning project, success means demonstrating that you can:

1. **Identify the right delegation boundaries** - Not everything is "fully agentic"; routine spam is, grey-zone isn't
2. **Quantify the value opportunity** - 9 hrs/day savings on routine spam vs. risk on grey-zone cases
3. **Design for lived work** - Subforum norms, Tom's tracker patterns, sponsor sensitivities
4. **Establish clear escalation triggers** - Confidence thresholds, special account handling, community engagement levels
5. **Balance automation value against operational risk** - The asymmetric "false negatives are existential" constraint shapes everything

The metrics above aren't just targets - they're the **measurement framework** that would allow MiniBase to validate whether the agent is creating value or liability.

## Repository Structure

```
FDE_ContentModerator_2/
├── FDE_Program/          # Program materials and ATX reference documents
│   ├── Week2/            # Week 2 materials including scenario briefs
│   │   ├── enriched_scenarios.md        # Full Scenario 4 details
│   │   ├── README-Participants-Week2.md # Week 2 requirements
│   │   └── references/                  # ATX methodology references
│   │       ├── atx-concepts.md          # Core ATX concepts
│   │       ├── atx-agent-mapping.md     # Agent design patterns
│   │       ├── atx-assessment.md        # Assessment methodology
│   │       ├── atx-scoring.md           # Delegation suitability scoring
│   │       └── atx-economics.md         # Economics of digital labour
│   └── Intro+Week1/      # Week 1 materials (for context)
├── Specification/        # Project specifications and analysis artifacts
├── Deliverables/         # Week 2 deliverables (7 required artifacts)
└── CLAUDE.md            # This file
```

## Core Entities (MiniBase Scenario 4)

### Post
Represents user-generated content on the MiniBase platform.

Attributes:
- `id`: UUID, immutable
- `author_id`: foreign key to User, required
- `subforum_id`: foreign key to Subforum, required (one of 14 subforums or gallery)
- `content`: text, required, max 10,000 characters
- `created_at`: ISO 8601 timestamp, immutable
- `edited_at`: ISO 8601 timestamp, nullable (last edit)
- `status`: enum [PUBLISHED, FLAGGED, UNDER_REVIEW, REMOVED, APPROVED], default PUBLISHED
- `flag_count`: non-negative integer (user reports)
- `flagged_reasons`: array of strings (spam, harassment, off-topic, commercial, ip-claim)
- `moderation_history`: array of ModerationAction objects

State machine:
- PUBLISHED → FLAGGED (when flag_count >= 4, or moderator samples, or automated detection)
- FLAGGED → UNDER_REVIEW (moderator claims the case)
- UNDER_REVIEW → APPROVED (moderator clears, post returns to PUBLISHED state)
- UNDER_REVIEW → REMOVED (moderator removes)
- REMOVED is terminal (unless appealed)

### ModerationAction
Nested in Post, tracks moderation decisions.

Attributes:
- `action_id`: UUID
- `moderator_id`: foreign key to Moderator (nullable if agent)
- `agent_id`: identifier if action taken/proposed by agent
- `action_type`: enum [NO_ACTION, WARNING, REMOVAL, BAN_USER, ESCALATE]
- `rationale`: text, required for REMOVAL and BAN_USER
- `confidence`: float 0-1 (agent confidence score, null for human actions)
- `reviewed_by_human`: boolean (true if human reviewed agent proposal)
- `timestamp`: ISO 8601 timestamp
- `policy_reference`: string (which rule/norm applied)

### Subforum
Represents content categories with distinct norms.

Key subforums:
- Painters sub: "no critique without invitation" norm (not in global policy)
- Historical sub: more permissive on historically-charged imagery
- Japanese painters sub: English critiques may read harsher than intended
- Gallery: different moderation patterns (focus on IP claims, self-promotion)

Each subforum has:
- `norm_overrides`: JSON object defining subforum-specific rules
- `escalation_required_for`: array of action types requiring escalation for this subforum

### IPClaim
Separate workflow from post moderation.

Attributes:
- `claim_id`: UUID
- `claimant_email`: string, required
- `post_id`: foreign key to Post
- `claim_type`: enum [COPYRIGHT, TRADEMARK]
- `description`: text, required
- `evidence_urls`: array of strings
- `status`: enum [PENDING, UNDER_REVIEW, RESOLVED_TAKEDOWN, RESOLVED_NO_ACTION, DISPUTED]
- `assigned_to`: "Tom" (Community Manager) or "Senior Moderator"
- `resolution_time_avg`: 30 minutes + escalation

State machine:
- PENDING → UNDER_REVIEW (Tom claims)
- UNDER_REVIEW → RESOLVED_TAKEDOWN (claim valid)
- UNDER_REVIEW → RESOLVED_NO_ACTION (claim invalid)
- UNDER_REVIEW → DISPUTED (complex, needs legal review)

## The Four Work Streams (from Scenario 4)

Of ~12K daily posts, 12.5% (~1,500/day) enter moderation queue via flags, detection, or sampling:

1. **Routine spam / clear-violation removal** (~1,080/day; ~30 sec/case; 72% of queue)
   - Obvious spam, off-topic, miscategorized posts
   - High delegation suitability: fully agentic with human oversight sampling

2. **Grey-zone case review** (~360/day; ~5 min/case; 24% of queue)
   - Hobbyist critique that reads harsh, commercial posts from community members, regional disputes
   - Medium delegation suitability: agent-led with human review before action

3. **User dispute appeals** (~60/day; ~8 min/case; 4% of queue)
   - Appeals of prior moderation actions
   - Low delegation suitability: human-led with agent support (context gathering)

4. **IP-claim resolution** (~3-5/week; ~30 min/case)
   - Copyright/trademark claims
   - Very low delegation suitability: human-only with agent-assisted triage

## Value vs. Risk Trade-off Framework

This agent design is shaped by an asymmetric risk profile that must inform every delegation decision:

### The Value Opportunity (Where to Automate)

**Routine spam removal: 1,080 posts/day, ~30 sec each = 9 hrs/day**
- High volume, low judgment required
- Clear patterns (link farms, gibberish, off-topic ads)
- Low reversal cost (false positive = restore post + apologize)
- **Value lever**: 70-80% automation → save 7 hrs/day → reallocate to grey-zone cases
- **Risk**: Low (community tolerates occasional false positive)
- **Delegation archetype**: Fully agentic with sampling oversight

### The Risk Zone (Where NOT to Automate)

**Grey-zone cases: 360 posts/day, ~5 min each = 30 hrs/day**
- Low volume (relative to spam), high judgment required
- Nuanced (harsh critique vs. harassment, cultural context, subforum norms)
- High reversal cost (false negative = viral incident, existential risk)
- **Risk**: Asymmetric ("false negatives are existential")
- **Delegation archetype**: Agent-led with human approval (agent gathers context, human decides)

### The Strategic Choice

**Why not automate grey-zone cases if they consume 30 hrs/day?**

1. **Economics of error**: One viral false negative costs more than 30 hrs/day of human time
2. **Compounding risk**: Grey-zone errors erode community trust, which erodes flagging quality, which increases moderation load
3. **Judgment value**: Volunteer moderators value complex decisions; they resent repetitive spam work
4. **Calibration difficulty**: Grey-zone cases require cultural context, tribal knowledge, and stakeholder judgment that's hard to codify

**The win**: Automate 9 hrs/day of low-risk spam to create capacity for 30 hrs/day of high-risk grey-zone work.

### Volume × Value Prioritization

From ATX scoring methodology, the four work streams rank:

| Work Stream | Volume (daily) | Time per case | Total effort | Delegation suitability | Priority |
|-------------|----------------|---------------|--------------|------------------------|----------|
| Routine spam | 1,080 | 30 sec | 9 hrs | High (fully agentic) | **#1: Primary target** |
| Grey-zone cases | 360 | 5 min | 30 hrs | Medium (agent-led) | #2: Human judgment required |
| User appeals | 60 | 8 min | 8 hrs | Low (human-led) | #3: Agent context support |
| IP claims | 3-5/week | 30 min | ~2 hrs/week | Very low (human-only) | #4: Legal sensitivity |

**Agent MVP scope**: Automate routine spam (#1) + provide context support for grey-zone triage (#2). Do not attempt to automate appeals or IP claims.

## ATX Methodology — Key Concepts to Apply

When working on this project, apply these ATX principles:

### Delegation Archetypes
- **Fully agentic**: Agent decides and acts; human reviews samples for quality assurance
- **Agent-led with oversight**: Agent proposes action; human approves before execution
- **Human-led with agent support**: Human decides; agent gathers context and drafts
- **Human-only**: Agent has no role; preserve human judgment

**Critical**: Not everything should be "fully agentic." Week 2's primary anti-pattern is defaulting all tasks to full automation. Delegation boundaries must be justified by risk, reversibility, and business constraints.

### Lived Work vs. Documented Work
The 14-page MiniBase moderation policy is the **documented** work. The **lived** work includes:
- Subforum-specific norms (e.g., painters sub "no critique without invitation")
- Tom's pattern tracker for high-risk users and sponsors
- Volunteer moderator disagreements resolved in Discord
- The "2024 sponsor incident" that shapes current risk tolerance
- Cultural interpretation differences (Japanese sub English critiques)

**Build for lived work, not just policy.** Discovery questions to Tom (stakeholder) are essential for uncovering these gaps.

### Escalation Triggers
Define clear conditions when the agent must hand off to a human:
- Commercial posts from sponsor accounts (Tom reviews personally)
- IP claims from @sculpturedragon (established sculptor, full review every time)
- Historical sub content flagged for controversial imagery (requires Tom if uncertain)
- Any case where confidence < 0.7
- Posts with >12 reactions (high community engagement)

### Failure Modes
From Tom's briefing: **"False positives are survivable; one viral false negative is existential."**

This asymmetry shapes the agent's risk posture:
- Bias toward escalation on grey-zone cases
- Sponsor/VIP posts require extra scrutiny (never auto-remove)
- Harsh-but-accurate critique is acceptable; harassment is not (distinction is subtle)

## Project Deliverables (Week 2 Requirements)

When building or refining this project, work toward these 7 deliverables:

1. ✅ **Cognitive Load Map** — Jobs to be Done, cognitive zones, breakpoints for the 4 work streams
   - Location: `Specification/03_Cognitive_Load_Map.md`
   - Status: Complete - shows 95% of spam work is rule-bound, 40% of grey-zone is context-gathering (automatable)

2. ✅ **Delegation Suitability Matrix** — Scoring each task cluster on delegation dimensions
   - Location: `Specification/04_Delegation_Suitability_Matrix.md`
   - Status: Complete - 10 task clusters scored, weighted avg 58.7/70 (agent-led trending fully agentic)

3. ✅ **Volume × Value Analysis** — Plotting 4 work streams to identify primary agentic target
   - Location: `Specification/05_Volume_Value_Analysis.md`
   - Status: Complete - spam + grey-zone context = 71% of value (£157K of £235K/year)

4. ✅ **Agent Purpose Document** — Purpose, scope, KPIs, autonomy matrix, escalation triggers
   - Location: `Specification/06_Agent_Purpose_Document.md`
   - Status: Complete - full agent specification with 4 delegation archetypes, 18 micro-tasks catalogued

5. ✅ **System/Data Inventory** — What the agent needs to access (Discourse API, gallery API, Discord, Google Sheets, email)
   - Location: `Specification/07_System_Data_Inventory.md`
   - Status: Complete - 8 systems analyzed, 212-224 hrs integration effort (revised from 136 hrs)

6. ✅ **Discovery Questions** — Questions for Tom that would materially change the design
   - Location: `Specification/08_Discovery_Questions.md`
   - Status: Complete - 18 sharp questions with impact analysis (6 critical, 9 high, 3 medium severity)

7. ✅ **This CLAUDE.md** — Workflow discipline and build guidance
   - Status: Updated with completed deliverables and critical findings

## Tooling and System Constraints

MiniBase runs on:
- **Discourse** (forum platform, self-hosted AWS, REST APIs available)
- **In-house gallery** (Rails app, custom, limited API surface)
- **Stripe** (premium memberships, commissions)
- **Discord** (volunteer moderator coordination)
- **Google Sheets** (Tom's moderation patterns tracker)
- **Email** (IP-claim correspondence, legal record)

### Integration Notes
- Discourse API provides post content, flags, user history, subforum metadata
- Gallery API is limited — may require scraping or manual data entry for some fields
- Tom's Google Sheet patterns are not in any system — must be translated into agent rules
- Discord mod discussions are informal — agent should not auto-post there without explicit design

## The Closed Build Loop (Week 2 Requirement)

Before Thursday early afternoon, you must complete a **closed build loop** to validate the Agent Purpose Document:

1. **Build what you're confident about** from the Agent Purpose Document
2. **Identify gaps**: What questions did you ask? What couldn't you build? What did you build incorrectly?
3. **Diagnose gaps** using the Week 1 taxonomy + Week 2 delegation boundary gaps
4. **Revise the Agent Purpose Document** based on diagnosis (especially autonomy matrix and escalation triggers)
5. **Re-run and verify** the revised document produces better results

**Delegation boundary gaps** occur when the document doesn't specify whether a step should be fully agentic, agent-led, or human-led — and the builder defaults to whichever is easiest to implement.

If asked to "build the agent described in this document," respond with:
1. What you can build confidently without questions
2. What you need to clarify before building
3. Then build only the confident parts

## Agent Design Principles (From ATX)

When designing or implementing the moderation agent:

### Purpose Statement
"Automate routine spam removal to free 7+ hours/day of moderator capacity for grey-zone cases requiring human judgment, while maintaining zero viral false negatives and preserving subforum-specific community norms."

**Value hypothesis:** By automating 70-80% of routine spam (9 hrs/day → 2 hrs/day), moderators can redirect time to the 360 daily grey-zone cases that shape community trust and safety.

**Risk constraint:** The asymmetric risk profile ("false negatives are existential") means the agent must bias toward escalation on ambiguous cases rather than optimizing for coverage.

### Autonomy Matrix

This matrix directly maps to the success metrics:
- **Agent decides alone** → drives Moderator Time Savings and Throughput metrics
- **Agent proposes, human approves** → protects Moderation Accuracy and False Negative Rate
- **Human takes over** → maintains Grey-Zone Case Quality and Team Sustainability
- **Human-only** → preserves business-critical controls (sponsor safety, legal compliance)

**Agent decides alone (no human approval required):**
- Intent classification (spam, off-topic, miscategorized)
- Post metadata retrieval (author history, subforum, flag reasons)
- Drafting removal rationale for clear violations
- Auto-removal of obvious spam (e.g., link farms, gibberish) when confidence > 0.9
- Logging all actions for human audit

**Agent proposes, human approves before action:**
- Removal of grey-zone posts (harsh critique, commercial-adjacent, cultural ambiguity)
- Warning issuance to established community members
- Any action on sponsor account posts
- Any action on posts with >12 reactions (high engagement)

**Human takes over (agent supports):**
- User dispute appeals (agent gathers context, human decides)
- IP-claim resolution (agent triages urgency, Tom handles)
- Subforum norm conflicts (agent flags, volunteer mods discuss)
- Any case where confidence < 0.7

**Human-only (agent has no role):**
- Policy changes or norm updates
- Banning users (permanent action)
- Legal/compliance decisions

## Validation and Testing

When implementing features, validate against the success metrics:

### Critical Tests (Must Pass - Safety)

1. **False Negative Prevention** (Existential Risk Metric)
   - Test: 100 known policy violations (harassment, doxxing, hate speech) → agent must escalate or remove 100%
   - Failure mode: Agent approves harmful content
   - Pass threshold: 100% (zero tolerance)

2. **Grey-Zone Escalation** (Quality Metric)
   - Test: 50 ambiguous cases (harsh critique, cultural references, commercial-adjacent) → agent must escalate, not auto-remove
   - Failure mode: Agent removes legitimate community content
   - Pass threshold: 100% escalation (no auto-removal on grey-zone)

3. **Sponsor Account Safety** (Business Risk Metric)
   - Test: Flagged posts from sponsor accounts → agent must escalate 100% to Tom
   - Failure mode: Agent auto-removes sponsor content
   - Pass threshold: 100% escalation (zero automated actions)

### Performance Tests (Must Pass - Value)

4. **Routine Spam Accuracy** (Efficiency Metric)
   - Test: 200 clear spam cases (link farms, gibberish, off-topic ads) → agent correctly identifies and removes
   - Failure mode: False positives (removes legitimate content) or false negatives (misses spam)
   - Pass threshold: ≥95% precision, ≥90% recall

5. **Coverage Rate** (Throughput Metric)
   - Test: 1,000 queue cases → measure % handled without human intervention
   - Target: 70-80% of routine spam automated
   - Pass threshold: ≥60% (justifies agent deployment)

6. **Confidence Calibration** (Trust Metric)
   - Test: When agent reports 0.9 confidence, actual accuracy should be 90%±5%
   - Measured across 100+ decisions at each confidence band (0.5-0.6, 0.6-0.7, 0.7-0.8, 0.8-0.9, 0.9+)
   - Pass threshold: Confidence bands correlate with accuracy within ±10%

### Norm Compliance Tests (Must Pass - Community)

7. **Subforum-Specific Rules**
   - Test: Painters sub critique post without explicit invitation → agent must consider "no critique without invitation" norm
   - Test: Historical sub historically-charged imagery → agent applies more permissive standard
   - Pass threshold: 100% correct norm application by subforum

8. **Cultural Context Handling**
   - Test: Japanese painters sub English-language critiques → agent flags potential harshness-interpretation issues
   - Pass threshold: Escalates when cultural context may affect interpretation

### Operational Tests (Should Pass - Sustainability)

9. **Escalation Quality** (Moderator Time Metric)
   - Test: Human moderators assess 50 escalated cases → "was this escalation justified?"
   - Target: ≥90% of escalations are useful (human agrees case needed review)
   - Pass threshold: ≥80% (avoids over-escalation fatigue)

10. **Context Completeness** (Efficiency Metric)
    - Test: Escalated cases include: post content, author history, subforum norms, flag reasons, confidence score
    - Target: Human can decide within 30 seconds (faster than gathering context manually)
    - Pass threshold: 100% of escalations include minimum required context

11. **Audit Trail Completeness** (Compliance Metric)
    - Test: Every agent action logged with: action_id, timestamp, rationale, confidence, policy_reference
    - Pass threshold: 100% (non-negotiable for legal/transparency)

### Test Data Requirements

Create test fixtures covering:
- **Routine spam**: link farms, gibberish, duplicate posts, off-topic ads (200+ examples)
- **Grey-zone**: harsh critique (invited/uninvited), commercial posts from community members, cultural references (100+ examples)
- **Clear violations**: harassment, doxxing, hate speech, IP theft (100+ examples)
- **Subforum edge cases**: painters critique, historical imagery, Japanese sub English posts (50+ examples)
- **Special accounts**: sponsor posts, established sculptors, high-engagement posts (50+ examples)

Store in `tests/fixtures/` with labels for ground truth validation.

## Assumptions and Discovery Gaps

**Known unknowns** (require discovery questions to Tom):
- What exactly triggered the "2024 sponsor incident" and what are the consequences?
- How do volunteer moderators coordinate on grey-zone disagreements?
- Which established users have tribal status that affects moderation tolerance?
- What IP claim patterns distinguish legitimate claims from retaliatory reports?
- How does Tom's Google Sheet tracker actually get used day-to-day?

**Assumptions to validate**:
- Confidence threshold of 0.7 for escalation (needs calibration against real cases)
- 4 flags as the threshold for entering the queue (may vary by subforum or user reputation)
- Harsh critique vs. harassment distinction can be codified (may require human judgment)

## Build Commands and Workflow

This is a specification and design project, not a production codebase (yet). When building a prototype:

1. **Start with analysis**, not code:
   - Read `FDE_Program/Week2/enriched_scenarios.md` for full Scenario 4 context
   - Review `FDE_Program/Week2/references/atx-*.md` for methodology
   - Draft deliverables in `Deliverables/` directory

2. **When ready to prototype**:
   - Use Python or JavaScript/TypeScript (choose based on familiarity and API libraries)
   - Structure as: `src/agent.py` or `src/agent.ts` (main agent logic)
   - Include `src/escalation_rules.py` or `src/escalation_rules.ts` (delegation boundaries)
   - Mock Discourse API calls initially (use `tests/fixtures/` for sample data)

3. **Testing approach**:
   - Create test cases for each work stream (routine spam, grey-zone, appeals, IP)
   - Include subforum-specific test cases (painters critique, historical imagery)
   - Test escalation triggers explicitly (sponsor posts, high-engagement posts, low confidence)

4. **No production deployment**: This is a learning artifact. Focus on demonstrating sound design, not operational readiness.

## What NOT to Do

- **Do not** default everything to "fully agentic" — this is the Week 2 anti-pattern
- **Do not** build from the 14-page policy alone — lived work differs from documented work
- **Do not** ignore subforum-specific norms — they are critical to MiniBase's culture
- **Do not** auto-remove grey-zone content — escalate for human review
- **Do not** claim domain expertise you don't have — mark assumptions explicitly
- **Do not** skip the closed build loop — it's required to validate the Agent Purpose Document
- **Do not** create documentation files unless explicitly requested — focus on deliverables
- **Do not** treat Tom's patterns tracker as optional — it contains the lived rules

## Stakeholder Brief

**Tomasz "Tom" Włodarczyk**, Community Manager:
- Warsaw-based, ex-volunteer moderator promoted to paid role
- Risk-averse due to prior incidents: "False positives are survivable; one viral false negative is existential"
- Manages sponsor relationships (commercial constraint on content decisions)
- Coordinates 8 volunteer moderators across time zones
- Uses a Google Sheet tracker for high-risk patterns (not in formal systems)

When in doubt about a moderation decision, **ask what Tom would do** and whether it requires his personal review.

## Decision Framework for Builders

When making implementation choices, use this framework to align with the problem statement and success metrics:

### Should this task be automated?

Ask these questions in order:

1. **Volume test**: Is this task high-volume (>100/day)? If no → deprioritize automation
2. **Pattern test**: Can the decision rule be codified with >80% confidence? If no → human-led or human-only
3. **Risk test**: What happens if the agent gets it wrong? If existential → require human approval; if survivable → fully agentic
4. **Reversibility test**: Can errors be quickly detected and reversed? If yes → lower risk; if no → require human oversight
5. **Value test**: Does automation free human capacity for higher-value work? If no → not worth building

**Example: Should we automate removal of harsh critique posts?**
- Volume: ~50/day (subset of grey-zone 360) — moderate volume
- Pattern: Harsh critique vs. harassment distinction requires cultural context, subforum norms, author intent — **cannot codify with >80% confidence**
- Risk: False negative (miss harassment) = community safety issue; false positive (remove legitimate critique) = community trust erosion — **both high risk**
- Reversibility: Difficult — wrongly removed critique can go viral ("platform censors criticism")
- Value: Frees some moderator time, but risk outweighs value
- **Decision: Do NOT automate. Agent gathers context (author history, subforum norms, flag reasons), human decides.**

**Example: Should we automate removal of link-farm spam?**
- Volume: ~300/day (subset of routine 1,080) — high volume
- Pattern: Multiple URLs, no substantive content, new user, generic text — **can codify with >95% confidence**
- Risk: False negative (spam stays up) = minor annoyance; false positive (remove legitimate post with links) = survivable, easily reversed
- Reversibility: High — user can appeal, post can be restored immediately
- Value: Saves ~2.5 hrs/day of moderator time on brain-dead task
- **Decision: Fully automate with confidence >0.9. Human sampling for calibration.**

### Should this feature be built now or later?

Use a phased approach aligned with compounding thesis:

**Phase 1 (MVP - This project):**
- Automate routine spam removal (link farms, gibberish, off-topic ads)
- Build confidence scoring and escalation framework
- Create audit logging and human override mechanisms
- **Goal**: Prove value (time savings) and safety (no viral false negatives) on low-risk cases

**Phase 2 (Post-validation):**
- Expand to more ambiguous spam (subtle self-promotion, low-quality content)
- Add context-gathering for grey-zone cases (author history, subforum norms, similar cases)
- Improve confidence calibration based on Phase 1 data
- **Goal**: Increase coverage while maintaining safety bar

**Phase 3 (Platform integration):**
- Integrate with volunteer moderator Discord (escalation notifications)
- Build dashboards for Tom's pattern tracking
- Add appeal-handling support (context gathering for disputes)
- **Goal**: Compound value by making existing infrastructure more effective

**Never build**: Full automation of grey-zone removal, user banning, policy changes, IP claim decisions

### How should this metric be prioritized?

When metrics conflict, use this hierarchy:

1. **Safety metrics** (False Negative Rate, Sponsor Account Safety) — non-negotiable, cannot trade for efficiency
2. **Quality metrics** (Moderation Accuracy, Norm Compliance) — protect before optimizing throughput
3. **Efficiency metrics** (Moderator Time Savings, Coverage Rate) — optimize within safety/quality constraints
4. **Cost metrics** (Cost per Case, ROI) — last consideration; wrong to optimize cost at expense of safety

**Example conflict**: Agent can achieve 85% coverage (efficiency) by lowering confidence threshold to 0.6, but this reduces precision from 95% to 88% (quality).
- **Resolution**: Prioritize quality. Keep confidence threshold at 0.7+, accept 70% coverage. The 15% coverage gain isn't worth the 7% quality drop.

**Example conflict**: Agent costs £0.08/case (above target of £0.05), but achieves 95% accuracy and saves 7 hrs/day of moderator time.
- **Resolution**: Accept cost overrun. ROI is still 3:1+ (£7 × 20 = £140 saved / £0.08 × 1,080 = £86 cost). Cost optimization is secondary to value delivery.

## Success Criteria

By Week 2 Friday, this project should demonstrate:
- Thoughtful cognitive work decomposition (not just task lists)
- Justified delegation archetypes (not "fully agentic" everywhere)
- Clear agent boundaries and escalation triggers
- Evidence of eliciting lived work (not just reading the policy)
- A buildable Agent Purpose Document (validated via closed build loop)
- Discovery questions that would materially change the design (not generic questions)

The goal is to show FDE-level thinking: understanding cognitive work, designing delegation architecture, and balancing automation value against operational risk.
