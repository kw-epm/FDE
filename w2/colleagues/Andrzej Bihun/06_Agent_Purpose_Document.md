# Agent Purpose Document: MiniBase Content Moderation Agent

**Project**: MiniBase Community Content Moderation Agent  
**Phase**: ATX Agent Mapping & Design Specification  
**Date**: 2026-04-29  
**Version**: 1.0

---

## Executive Summary

This document specifies the **MiniBase Content Moderation Agent** - an AI agent designed to automate routine spam removal and grey-zone context gathering for a UK-based tabletop miniature hobbyist platform (180K users, 1,500 moderation cases/day).

**Primary Purpose**: Automate routine spam removal to free 7+ hours/day of moderator capacity for grey-zone cases requiring human judgment, while maintaining zero viral false negatives and preserving subforum-specific community norms.

**Business Value**: £182,889/year time savings (62% reduction in moderation effort), 2.5× growth headroom without hiring, improved volunteer satisfaction.

**Delegation Strategy**: Fully Agentic on routine spam (74% automation), Agent-Led on spam edge cases (human approval), Fully Agentic context gathering + Human-Led judgment on grey-zone cases.

**Implementation Timeline**: 12 weeks (3 phases), £14,300 investment, 10.8:1 first-year ROI.

---

## Agent Identity

### Agent Name
**MiniBase Content Moderation Agent** (internal codename: "Guardian")

### Job to be Done
Given a flagged post in MiniBase's moderation queue, **determine whether it is routine spam** (auto-remove), **grey-zone content** (gather context for human review), **edge case** (escalate), or **high-risk** (escalate to Tom/Senior Mod) — and execute the appropriate action while logging full rationale for audit and appeal.

### Business Context
- **Platform**: MiniBase, UK-incorporated hobbyist community (180K users, 12K posts/day)
- **Department**: Community Moderation (hybrid team: 8 volunteer moderators + 2 paid staff)
- **Process**: Post moderation queue (1,500 flagged posts/day enter via user flags, automated detection, or sampling)
- **Customer Journey**: Content creators post → community flags → moderation review → decision (approve, remove, warn, escalate)
- **Revenue Model**: £1.4M/year from premium memberships (£9-15/month), gallery commissions (10% platform fee), sponsor partnerships

---

## Primary Objectives

### Objective 1: Automate Routine Spam Removal (Phase 1-2)
**Target**: Reduce routine spam handling from 9 hrs/day to <2 hrs/day (77% reduction)

**Success Definition**:
- 70-80% of routine spam (800 cases/day) handled without human intervention
- False positive rate <5% (wrongly remove legitimate content)
- False negative rate <0.1% on clear policy violations (miss harmful content)
- Moderator trust: "I no longer think about link farms, the agent just handles them"

**Value**: £49,284/year time savings, volunteer satisfaction ↑

---

### Objective 2: Automate Grey-Zone Context Gathering (Phase 3)
**Target**: Reduce grey-zone case time from 4-5 min to 1.5-2 min (50-60% reduction)

**Success Definition**:
- Context gathering time <30 sec (vs. 2-4 min manual gathering)
- Context completeness: user history, subforum norms, precedents, escalation triggers
- Human judgment quality maintained (false negative/positive rates unchanged)
- Moderator feedback: "I spend my time judging, not gathering context"

**Value**: £108,414/year time savings, decision quality ↑

---

### Objective 3: Maintain Safety Bar (Non-Negotiable)
**Constraint**: "False positives are survivable; one viral false negative is existential" (Tom, Community Manager)

**Success Definition**:
- Zero viral false negatives (harmful content reaching community at scale)
- 100% sponsor account escalation (no automated actions without Tom's review)
- 100% subforum norm compliance (painters critique rule, historical permissiveness, etc.)
- Audit trail completeness: 100% of actions logged with rationale, confidence, policy reference

**Value**: Existential risk mitigation, £15,000/year risk reduction value

---

## Key Performance Indicators (KPIs)

### Tier 1: Safety Metrics (Non-Negotiable)
| Metric | Target | Measurement | Failure Consequence |
|--------|--------|-------------|---------------------|
| **False Negative Rate** | ≤0.1% on clear violations | Daily human audit (50 cases) | One viral incident = project failure |
| **Sponsor Account Safety** | 100% escalation to Tom | Agent escalation rate on sponsor posts | Revenue loss, relationship damage |
| **Audit Trail Completeness** | 100% actions logged | Automated log validation | Legal compliance, transparency |

### Tier 2: Quality Metrics
| Metric | Target | Measurement | Acceptable Range |
|--------|--------|-------------|------------------|
| **Moderation Accuracy (Spam)** | ≥95% precision, ≥90% recall | Weekly human audit (100 cases) | 90-98% precision |
| **Subforum Norm Compliance** | 100% correct application | Moderator override rate by subforum | <10% override rate |
| **Escalation Precision** | ≥90% justified escalations | Human assessment of escalations | 80-95% |

### Tier 3: Efficiency Metrics
| Metric | Target | Measurement | Acceptable Range |
|--------|--------|-------------|------------------|
| **Moderator Time Savings** | 7 hrs/day (77% spam reduction) | Agent cases × avg time saved | 5-9 hrs/day (60-80%) |
| **Coverage Rate (Spam)** | 70-80% automated | Agent actions / total spam cases | 60-85% |
| **Response Time (Spam)** | <5 min flag-to-removal | Timestamp delta | <10 min |

### Tier 4: Cost Metrics
| Metric | Target | Measurement | Acceptable Range |
|--------|--------|-------------|------------------|
| **Cost per Case (Spam)** | <£0.05/case | Monthly cost / cases handled | £0.03-0.08 |
| **Cost per Case (Grey-Zone)** | <£0.10/case (context only) | Monthly cost / cases handled | £0.08-0.15 |
| **ROI** | ≥3:1 value/cost | (Time saved × £18/hr) / cost | 2:1 minimum |

---

## Failure Modes and Risk Mitigation

### Failure Mode 1: Viral False Negative (Existential Risk)
**What it looks like**: Agent approves or misses harassment, hate speech, doxxing, or sponsor-related harmful content that spreads virally in community or to Twitter/Reddit.

**Consequence**: 
- Community trust erosion → user attrition
- Sponsor withdrawal → revenue loss (£100K-500K)
- PR crisis → brand damage
- Tom's assessment: "existential threat to platform"

**Recovery Path**: Emergency response (immediate removal, apology, transparency report), but reputational damage is irreversible.

**Prevention**:
1. **Confidence-based escalation**: Confidence <0.7 → auto-escalate to human
2. **High-engagement escalation**: Reactions >20 → escalate (viral risk)
3. **Sponsor account escalation**: 100% escalate to Tom (no auto-action)
4. **Watchlist escalation**: Tom's high-risk users → 100% escalate
5. **Grey-zone escalation**: Harsh critique, cultural interpretation, ambiguous cases → human decides (agent gathers context only)
6. **Daily safety audit**: 50 random cases reviewed for false negatives

---

### Failure Mode 2: False Positive on Established Member (Trust Erosion)
**What it looks like**: Agent removes legitimate content from 3+ year community member (e.g., tutorial with multiple reference URLs, gallery self-promotion, invited harsh critique).

**Consequence**:
- Established member feels unfairly targeted → loses trust
- User complains publicly → "platform censors established members"
- Moderator override required → erodes agent credibility
- Volunteer perception: "I have to double-check everything anyway"

**Recovery Path**: Restore post immediately, apologize, explain error, log as false positive for retraining.

**Prevention**:
1. **Exception detection**: Account age >1 year AND spam pattern → escalate to human
2. **Gallery self-promotion**: Established members in gallery → escalate (context-dependent)
3. **High engagement**: Reactions >5 → escalate (community values this content)
4. **Subforum-specific rules**: Painters invitation rule, historical permissiveness → codified in agent logic
5. **Weekly false positive review**: Track by subforum, user tenure, content type

---

### Failure Mode 3: Context Incompleteness (Grey-Zone Quality Degradation)
**What it looks like**: Agent prepares grey-zone context but misses key signals (subforum-specific norm, precedent case, watchlist status), leading human to make wrong decision.

**Consequence**:
- Human makes uninformed decision → moderation error
- Missed norm violation → community perceives inconsistency
- Moderator loses trust in agent context: "I can't rely on this"

**Recovery Path**: Human discovers missing context, agent retrains on gap, but decision may have been wrong.

**Prevention**:
1. **Context checklist validation**: Every grey-zone case includes user history, subforum norms, precedents, escalation triggers
2. **Completeness scoring**: Agent self-assesses context completeness (e.g., "precedent search: 5 similar cases found")
3. **Moderator feedback loop**: "Was this context complete?" (weekly survey)
4. **Quarterly context audit**: Review 100 cases for missing signals

---

### Failure Mode 4: Drift (Accuracy Degradation Over Time)
**What it looks like**: Agent accuracy declines from 95% → 85% over 6 months as community norms evolve, new spam patterns emerge, or model confidence miscalibrates.

**Consequence**:
- Higher false positive/negative rates → trust erosion
- Moderator override rate increases → efficiency loss
- Tom pauses or rolls back agent → lost value

**Recovery Path**: Retrain on production data (agent actions + human overrides), recalibrate confidence thresholds, update subforum norms.

**Prevention**:
1. **Monthly drift detection**: Compare current accuracy vs. baseline (>90% required)
2. **Quarterly retraining**: Incorporate 3 months of production data (overrides, appeals, new spam patterns)
3. **Dynamic norm updates**: Subforum norms versioned, updated when community rules change
4. **Confidence recalibration**: Quarterly check: does 0.9 confidence = 90% accuracy?

---

## Delegation Archetype and Rationale

### Agent Mapping Framework (ATX)
Following ATX methodology, this agent uses **three delegation archetypes** depending on work stream:

### Archetype 1: Fully Agentic (Routine Spam)
**Work Stream**: Link farms, crypto/forex bots, gibberish spam  
**Volume**: 800 cases/day (74% of spam queue)  
**Delegation Suitability Score**: 68/70 (very high)

**Agent Decides Alone**:
- Pattern match: 3+ URLs + new account + generic text → link farm
- Confidence >0.9 → auto-remove
- Log rationale: "Removed link farm spam (0.92 confidence) - 5 URLs, 2-day-old account, off-topic in painters sub"
- Notify user: template message with appeal option

**Human Role**:
- Daily sampling: 10% random audit (80 cases/day)
- User appeals: review within 24 hrs (rare: 3-5/day)
- Calibration: adjust confidence threshold if false positive rate >5%

**Rationale**: 
- High volume (800/day) + low risk (easily reversed) + clear patterns (99% accuracy) = ideal for full automation
- Volunteers explicitly want this: "Just make it go away" (Sarah, volunteer moderator)

---

### Archetype 2: Agent-Led with Oversight (Spam Edge Cases)
**Work Stream**: Off-topic commercial, exception handling  
**Volume**: 280 cases/day (26% of spam queue)  
**Delegation Suitability Score**: 54/70 (medium)

**Agent Proposes, Human Approves**:
- Pattern match: sales language + established account (1+ year) + gallery subforum → ambiguous
- Confidence 0.7-0.9 → escalate with recommendation
- Context card: "Likely commercial spam (0.75 confidence) BUT user is 2-year member with 450 helpful posts. Gallery subforum allows self-promotion. Recommend: human review."

**Human Role**:
- Review agent proposal (30-60 sec)
- Decide: approve agent recommendation, override, or escalate further
- Total time: 280 × 45 sec = 3.5 hrs/day (vs. 9 hrs without agent)

**Rationale**:
- Context-dependent (gallery self-promotion, established member exceptions) requires human judgment
- Moderate risk (false positive on established member = trust impact)
- Agent can detect patterns + gather context, but human decides edge cases

---

### Archetype 3: Human-Led with Agent Support (Grey-Zone Cases)
**Work Stream**: Harsh critique vs. harassment, cultural interpretation, ambiguous content  
**Volume**: 360 cases/day  
**Delegation Suitability Score**: 34/70 (low - judgment-bound)

**Agent Gathers Context, Human Decides**:
- **Agent role** (fully automated context gathering):
  - Retrieve user profile: age, post count, reputation, moderation history
  - Match subforum: identify applicable norms (e.g., painters = invitation rule)
  - Semantic search: find 3-5 similar precedent cases with outcomes
  - Check escalation triggers: sponsor badge, watchlist, engagement >20
  - Extract signals: targets work vs. person, constructive vs. destructive, invited vs. uninvited
  - Present context card (10-20 sec to review vs. 2-4 min to gather)

- **Human role** (decision-maker):
  - Review context (30-60 sec)
  - Apply cultural reasoning, intent assessment, risk judgment
  - Decide: approve, remove, warn, or escalate
  - Total time: 360 × 2 min = 12 hrs/day (vs. 27 hrs without agent)

**Rationale**:
- Poorly codifiable (Sarah: "That boundary is so cultural, so context-dependent")
- Extreme risk (false negative = harassment persists → existential; false positive = censor critique → trust erosion)
- Agent can automate 40% of work (context gathering) WITHOUT automating 30% judgment → captures value without risk

---

### Archetype 4: Human-Only (Cultural Interpretation, IP Claims)
**Work Stream**: Japanese sub cultural cases, IP claims, sponsor account decisions  
**Volume**: 31 cases/day (2% of queue)  
**Delegation Suitability Score**: 18/70 (very low)

**No Agent Decision Role**:
- Agent may flag: "Japanese painters sub post detected - escalate to Aki (cultural expert)"
- Agent may extract claim details (IP claims), but **decision is 100% human**
- Rationale: Legal reasoning, cultural expertise, relationship management not automatable

**Human Role**: Full ownership (Tom, Aki, Senior Mod)

---

## Autonomy Matrix (Decision Authority)

### AGENT DECIDES ALONE (No Human Approval Required)

**Spam Removal** (confidence >0.9):
- Link farm spam: 3+ URLs, new account (<7 days), generic/no text, off-topic subforum
- Crypto/forex bots: formulaic text pattern, multi-post across subforums, bot username
- Gibberish spam: high perplexity score (random characters), no semantic meaning
- Duplicate posts: exact content posted multiple times across subforums

**Context Gathering** (all grey-zone cases):
- Retrieve user profile: account age, post count, reputation score, moderation history
- Match subforum: identify applicable norms from database
- Search precedents: semantic similarity search on case library (top 5 matches)
- Check escalation triggers: sponsor badge, watchlist, engagement count

**Logging** (all actions):
- Action ID, timestamp, post ID, action type, rationale, confidence, policy reference
- Store in audit log for compliance and appeal handling

---

### AGENT ACTS, HUMAN NOTIFIED AFTER (Post-Action Review)

**Not applicable** for this agent. All automated spam removal is logged, but human is not notified per-action (volume too high). Instead:
- **Daily digest**: Summary of 800 agent actions sent to moderators (review high-level patterns)
- **User appeals**: Human notified when user appeals agent decision (3-5/day)

---

### AGENT PROPOSES, HUMAN APPROVES BEFORE ACTION

**Spam Edge Cases** (confidence 0.7-0.9):
- Off-topic commercial from established account (1+ year)
- Gallery self-promotion from user with 500+ posts
- Post with spam signals BUT positive engagement (reactions >5)
- Educational content with multiple URLs in non-educational subforum

**Grey-Zone Escalation** (any ambiguity):
- Harsh critique (targets work, but harsh tone flagged by community)
- Commercial content from community member (legitimate or spam?)
- Cultural interpretation needed (Japanese sub, sarcasm, satire)

**Sponsor Account Posts** (any action):
- 100% escalate to Tom (no auto-action, even on clear violations)

**High Engagement Posts** (reactions >20):
- 100% escalate to human (community backlash risk if wrong decision)

**Watchlist Users** (Tom's tracker):
- 100% escalate to Tom (relationship management, fraud patterns)

---

### HUMAN TAKES OVER (Agent Supports, Doesn't Decide)

**Triggers**:
- **Confidence <0.7**: Agent genuinely uncertain → escalate with context, no recommendation
- **Policy ambiguity**: No clear precedent, multiple valid interpretations → human decides
- **Cultural interpretation**: Japanese sub, German directness, sarcasm → escalate to cultural expert (Aki, Klaus)
- **User appeal**: User contests agent decision → Tom reviews with full context
- **IP claims**: Copyright/trademark claims → Tom + Senior Mod (legal reasoning)
- **Permanent actions**: User bans, policy changes → human-only (agent not involved)

---

## Agent Activity Catalog

| Task | Type | Delegation Level | Data Required | Tool Required | Risk Level |
|------|------|-----------------|---------------|---------------|------------|
| **1. Retrieve flagged post** | Retrieval | Fully Agentic | Discourse API | Discourse read API | Low |
| **2. Extract post metadata** | Reasoning | Fully Agentic | Post content, author, subforum | NLP, parsing | Low |
| **3. Classify intent** | Reasoning | Fully Agentic | Content, URLs, username | Spam classifier (ML) | Low |
| **4. Check user history** | Retrieval | Fully Agentic | Discourse API | User profile API | Low |
| **5. Detect spam patterns** | Reasoning | Fully Agentic | URL count, text structure, account age | Pattern matching | Low |
| **6. Check exception signals** | Decision | Fully Agentic | Account age, engagement, subforum | Context API | Low-Medium |
| **7. Estimate confidence** | Reasoning | Fully Agentic | Signal aggregation | Confidence scoring | Low |
| **8. Remove spam (high confidence)** | Action | Fully Agentic | Post ID | Discourse write API | Medium |
| **9. Escalate spam (medium confidence)** | Action | Agent-Led + HITL | Context card | Escalation queue API | Low |
| **10. Gather grey-zone context** | Retrieval | Fully Agentic | User history, subforum norms, precedents | Multi-source aggregation | Low |
| **11. Match subforum norms** | Reasoning | Fully Agentic | Subforum ID, norm database | Norm lookup API | Low |
| **12. Search precedents** | Retrieval | Fully Agentic | Case library | Semantic search (vector DB) | Low |
| **13. Check escalation triggers** | Decision | Fully Agentic | Watchlist, sponsor badges, engagement | Trigger database | Medium |
| **14. Extract grey-zone signals** | Reasoning | Human-Led + Agent Support | Content, tone, targets | NLP sentiment analysis | Low |
| **15. Prepare context card** | Generation | Fully Agentic | Aggregated context | UI rendering | Low |
| **16. Log action** | Action | Fully Agentic | Action details | Logging API | Low |
| **17. Notify user** | Action | Fully Agentic | Template message, post data | Discourse messaging | Low |
| **18. Flag for human review** | Action | Agent-Led + HITL | Context, confidence, recommendation | Escalation queue | Low |

---

## System and Data Inventory

### Core Systems

| System | Data Needed | Access Type | Availability | Gap/Risk | Integration Effort |
|--------|-------------|-------------|--------------|----------|-------------------|
| **Discourse (Forum)** | Posts, users, flags, moderation history | Read/Write | REST API | Rate limits: 60 req/min | Medium (2 weeks) |
| **In-house Gallery** | Gallery posts, artist profiles, commercial flags | Read | Limited API | API surface incomplete - may require scraping | High (4 weeks) |
| **Tom's Watchlist** | High-risk users, sponsor accounts, fraud patterns | Read | Google Sheet (manual) | Not shared - needs migration to DB | Medium (1 week) |
| **Subforum Norms** | Painters invitation rule, historical permissiveness | Read | None (tribal knowledge) | Must codify from discovery interviews | High (2-3 weeks) |
| **Precedent Cases** | Similar cases, outcomes, moderator rationale | Read | Fragmented (personal notes, Discord) | Needs centralization + semantic search | High (3-4 weeks) |
| **Discord (Mod Coordination)** | Edge case discussions, moderator consensus | Read | Discord API | Integration optional (Phase 4) | Low (1 week) |
| **Email (IP Claims)** | Copyright claims, sculptor correspondence | Read | Gmail API | Integration optional (Phase 4) | Medium (2 weeks) |

### Data Codification Requirements

| Data Type | Current State | Target State | Effort | Blocker |
|-----------|---------------|--------------|--------|---------|
| **Subforum Norms** | Tribal knowledge (not documented) | Structured decision trees (JSON) | 16 hrs | Must interview moderators (Sarah, Aki, Klaus) |
| **Tom's Watchlist** | Google Sheet (columns: user, reason, action) | Database table (user_id, risk_type, escalation_rule) | 4 hrs | Tom must share access |
| **Precedent Cases** | Personal notes (Google Docs) + Discord logs | Case library (vector DB, semantic search) | 32 hrs | Moderators must export notes, Discord history |
| **Spam Patterns** | Implicit (in moderators' heads) | Spam taxonomy (link farm, bot, gibberish, etc.) | 8 hrs | Validate with discovery findings |
| **Exception Rules** | "I know it when I see it" | Explicit rules (account age >1yr, gallery self-promo) | 8 hrs | Codify from cognitive load analysis |

**Total Codification Effort**: 68 hours (must be completed before Phase 3)

---

### Integration Reuse Matrix (Compounding Strategy)

| Integration / Asset | Phase 1 (Spam) | Phase 2 (Edge Cases) | Phase 3 (Grey-Zone) | Phase 4 (Appeals) | Notes |
|--------------------|----------------|---------------------|---------------------|-------------------|-------|
| Discourse read API | ✓ Build | ✓ Reuse | ✓ Reuse | ✓ Reuse | Shared client, rate limit handling |
| Discourse write API | ✓ Build (remove post) | ✓ Reuse | | | Shared auth, logging |
| User profile retrieval | ✓ Build | ✓ Reuse | ✓ Reuse | ✓ Reuse | Shared caching layer |
| Spam classifier (ML) | ✓ Build | ✓ Reuse | | | Shared model, confidence scoring |
| Subforum norm database | | ✓ Build | ✓ Reuse | ✓ Reuse | Shared knowledge base |
| Precedent case library | | | ✓ Build | ✓ Reuse | Shared vector DB, semantic search |
| Tom's watchlist DB | | | ✓ Build | ✓ Reuse | Shared trigger database |
| Context aggregation engine | | | ✓ Build | ✓ Reuse | Shared multi-source retrieval |
| Logging & audit trail | ✓ Build | ✓ Reuse | ✓ Reuse | ✓ Reuse | Platform-level compliance |

**Compounding Value**: Phase 1-2 builds 60% of infrastructure needed for Phase 3-4. Phase 3 context engine is fully reusable for appeal handling (Phase 4), reducing Phase 4 effort by ~50%.

---

## Context Engineering Design

### Memory Architecture

| Memory Type | Content | Storage | Lifecycle | Update Frequency |
|-------------|---------|---------|-----------|-----------------|
| **In-Context (Short-term)** | Flagged post content, immediate case details | Prompt window (8K tokens) | Per case (discarded after decision) | Real-time |
| **Episodic (Medium-term)** | User moderation history (this user's prior flags, violations, appeals) | Vector DB (per-user chunks) | Per user | Updated on each moderation action |
| **Semantic (Long-term)** | Subforum norms, precedent cases, policy docs | RAG pipeline (vector search) | Persistent, versioned | Updated quarterly or when norms change |
| **Procedural (Static)** | Agent instructions, spam taxonomy, escalation rules | System prompt | Version-controlled | Updated on agent retraining |
| **Watchlist (Operational)** | Tom's high-risk users, sponsor accounts | Structured DB (key-value) | Persistent | Updated weekly by Tom |

---

### Retrieval Strategy

#### Spam Classification (Phase 1-2)
**Trigger**: Post flagged, enters moderation queue  
**Target**: Pattern match (URL count, text structure, account signals) + ML classifier confidence  
**Quality Evaluation**: Daily human audit (50 cases), false positive rate <5%  
**Cost Management**: Minimal retrieval (metadata only, no embedding), <500 tokens/case

---

#### Grey-Zone Context Gathering (Phase 3)
**Trigger**: Post classified as grey-zone (not spam, flagged for other reasons)  
**Retrieval Sequence**:
1. **User history**: Query Discourse API (account age, post count, recent posts, prior violations)
2. **Subforum norms**: Match subforum ID → retrieve applicable norms from database
3. **Precedent search**: Embed post content → semantic search case library (top 5 similar cases)
4. **Escalation triggers**: Check watchlist (user_id), sponsor badge (Discourse metadata), engagement count (reactions)

**Quality Evaluation**: 
- Context completeness: does human moderator have all needed information? (weekly survey: >4/5)
- Precedent relevance: are retrieved cases actually similar? (monthly review: >80% relevant)

**Cost Management**: 
- User history: cache for 1 hour (same user may have multiple flags)
- Precedent search: retrieve top 5 only (limit token cost)
- Total context: <2,000 tokens/case (vs. 5,000+ for full case library)

---

#### Appeal Context Preparation (Phase 4)
**Trigger**: User submits appeal of moderation decision  
**Target**: Retrieve original post, removal rationale, moderator decision, user appeal text, similar precedents  
**Quality Evaluation**: Tom feedback: "Was context complete?" (monthly survey)  
**Cost Management**: Reuse Phase 3 context engine (marginal cost <£0.05/appeal)

---

### Prompt Engineering Principles

#### 1. Role and Purpose First
```
You are the MiniBase Content Moderation Agent. Your purpose is to:
1. Identify and remove routine spam (link farms, bots, gibberish) from MiniBase's moderation queue
2. Gather context for grey-zone cases requiring human judgment
3. Escalate high-risk cases (sponsor accounts, cultural interpretation, ambiguous harassment)

You serve a hybrid moderation team (8 volunteers + 2 paid staff) managing 1,500 flagged posts/day.
```

#### 2. Explicit Scope
```
What you MAY do:
- Classify posts as spam, grey-zone, or high-risk
- Remove clear spam (link farms, bots, gibberish) when confidence >0.9
- Gather context (user history, subforum norms, precedents) for grey-zone cases
- Escalate ambiguous or high-risk cases to human review

What you MAY NOT do:
- Remove grey-zone content without human approval
- Take any action on sponsor account posts (100% escalate to Tom)
- Make decisions on cultural interpretation (escalate to cultural expert)
- Ban users or make permanent account changes
```

#### 3. Few-Shot Examples (Spam Classification)
```
Example 1 - Link Farm:
Post: "Check out these amazing deals! www.example1.com www.example2.com www.example3.com"
User: account age 2 days, 1 post
Subforum: Painters (off-topic)
Classification: SPAM (link farm, confidence 0.96)
Action: Remove

Example 2 - Tutorial (NOT spam):
Post: "Here's my weathering tutorial with reference images: www.example1.com www.example2.com"
User: account age 3 years, 450 posts, reputation 4.5/5
Subforum: Techniques (on-topic)
Classification: NOT SPAM (educational content, established member, confidence 0.92)
Action: Approve
```

#### 4. Guardrail Instructions
```
ESCALATION TRIGGERS (auto-escalate to human, NO agent action):
- Confidence <0.7 (uncertain)
- Sponsor badge detected (100% escalate to Tom)
- Watchlist user (Tom's high-risk tracker)
- Engagement >20 reactions (viral risk)
- Japanese painters subforum + English post (cultural interpretation needed)
- Harsh critique + ambiguous target (work vs. person unclear)
```

#### 5. Structured Output (Context Card for Grey-Zone)
```json
{
  "case_id": "unique_id",
  "post": {
    "content": "truncated preview",
    "author": "username",
    "subforum": "painters",
    "created_at": "ISO 8601 timestamp",
    "flags": ["harassment", "off-topic"],
    "flag_count": 7
  },
  "user_profile": {
    "account_age_days": 730,
    "post_count": 450,
    "reputation_score": 4.2,
    "prior_violations": 0
  },
  "subforum_norms": {
    "subforum": "painters",
    "applicable_norms": ["no_critique_without_invitation"],
    "invitation_detected": true,
    "thread_title": "Tips on my latest mini?"
  },
  "precedents": [
    {
      "case_id": "case_123",
      "similarity_score": 0.87,
      "outcome": "approved",
      "rationale": "Invited critique, targets technique"
    }
  ],
  "escalation_triggers": {
    "sponsor": false,
    "watchlist": false,
    "high_engagement": false
  },
  "signals": {
    "targets": "work",
    "tone": "harsh",
    "constructive": true,
    "invited": true
  },
  "confidence": 0.75,
  "recommendation": "APPROVE (invited critique within norms, established member)",
  "escalation_reason": null
}
```

#### 6. Chain of Thought (Spam Classification)
```
When classifying a post, reason step-by-step:

1. URL Analysis: Count URLs. If ≥3, check if content is substantive.
2. Account Analysis: Check account age. If <7 days, increase spam likelihood.
3. Text Analysis: Check for semantic meaning. If gibberish/formulaic, increase spam likelihood.
4. Username Analysis: Check for brand patterns or random characters.
5. Subforum Relevance: Is post on-topic for subforum?
6. Exception Check: Any signals this is legitimate? (established member, educational, high engagement)
7. Confidence: Aggregate signals → confidence score 0-1
8. Decision: If confidence >0.9 AND no exceptions → SPAM (remove). If 0.7-0.9 → escalate. If <0.7 → escalate with context.
```

#### 7. Token Discipline
- System prompt: <1,000 tokens (concise instructions, no repetition)
- Per-case context: <2,000 tokens (user profile summary, not full history)
- Precedent retrieval: Top 5 cases only (not full case library)
- Total per case: <4,000 tokens (vs. 10K+ unoptimized)

---

## Escalation Triggers and Routing

### Escalation Matrix

| Trigger | Condition | Route To | Priority | SLA |
|---------|-----------|----------|----------|-----|
| **Sponsor account** | Sponsor badge detected | Tom (Community Manager) | Urgent | 2 hrs |
| **Watchlist user** | User ID in Tom's watchlist | Tom | Urgent | 4 hrs |
| **High engagement** | Reactions >20 | Any available moderator | High | 6 hrs |
| **Cultural interpretation** | Japanese sub + English post | Aki (Japanese moderator) | Medium | 12 hrs |
| **Low confidence spam** | Confidence 0.7-0.9 | Any available moderator | Medium | 12 hrs |
| **Grey-zone ambiguity** | Harsh critique, ambiguous targets | Any available moderator | Medium | 12 hrs |
| **Very low confidence** | Confidence <0.7 | Any available moderator | Low | 24 hrs |
| **IP claim** | Copyright/trademark claim | Tom + Senior Mod | Urgent | 4 hrs |

### Escalation Notification Format

**For Moderator Review (Slack/Discord)**:
```
🚨 New Escalation: Spam Edge Case
Post ID: #123456
Subforum: Gallery
Reason: Commercial content from established member
Confidence: 0.75 (medium)
Agent Recommendation: Human review required

Quick Context:
- User: @sculptor_jane (3 years, 600 posts, reputation 4.5/5)
- Content: Selling old miniatures collection
- Gallery allows self-promotion, but first commercial post this year
- No watchlist / sponsor flags

Action Required: Approve, Remove, or Warn?
[Review Full Context] [Approve] [Remove] [Warn]
```

**For Tom Review (Urgent)**:
```
🔴 URGENT: Sponsor Account Flagged
Post ID: #789012
Subforum: Historical
Reason: Sponsor account content flagged by community (4 flags)
Agent Action: AUTO-ESCALATED (no agent action taken)

Quick Context:
- User: @historicus_sponsor (Sponsor badge)
- Content: Historical WWII miniature (swastika visible)
- Historical sub permits historically accurate imagery
- Community flagged for "hate symbol"

⚠️ Requires Tom's personal review (sponsor relationship sensitive)
[Review Full Context] [Take Action]
```

---

## Compounding Roadmap

### Wave 1: Foundation (Spam Automation) — Weeks 1-8
**Primary Value**: £49K/year time savings, 7.5 hrs/day freed

**Agents**:
1. **Spam Removal Agent (Phase 1)** - Link farms, bots, gibberish (Weeks 1-4)
2. **Spam Edge Case Handler (Phase 2)** - Off-topic commercial, exceptions (Weeks 5-8)

**Shared Assets Built**:
- Discourse read/write API client (rate limiting, auth, error handling)
- User profile retrieval service (caching, aggregation)
- Spam classifier (ML model, confidence scoring)
- Subforum taxonomy database
- Logging & audit trail infrastructure

**Codification Work (Parallel)**:
- Subforum norms (16 hrs) - document painters invitation rule, historical permissiveness
- Spam taxonomy (8 hrs) - validate pattern definitions with moderators
- Exception rules (8 hrs) - codify "established member" thresholds

---

### Wave 2: Context Automation (Grey-Zone Support) — Weeks 9-12
**Primary Value**: £108K/year time savings, 16.5 hrs/day freed

**Agent**:
3. **Grey-Zone Context Agent (Phase 3)** - Context gathering for all grey-zone cases

**Reuses from Wave 1**:
- Discourse API client (read/write)
- User profile retrieval (caching, reputation scoring)
- Subforum taxonomy (norm matching)
- Logging infrastructure

**New Integrations Built**:
- Tom's watchlist database (migrate from Google Sheet)
- Precedent case library (vector DB, semantic search)
- Context aggregation engine (multi-source retrieval, context card generation)

**Codification Work (Parallel)**:
- Tom's watchlist migration (4 hrs) - export Google Sheet, import to DB
- Precedent case extraction (32 hrs) - scrape personal notes, Discord logs, structure in DB

---

### Wave 3: Appeals & Platform Integration — Weeks 13+
**Primary Value**: £53K/year time savings, 8 hrs/day freed (Tom's appeal backlog)

**Agent**:
4. **Appeal Context Agent (Phase 4)** - Context preparation for user appeals

**Reuses from Wave 1-2**:
- Discourse API (read original post, removal rationale)
- User profile retrieval (account history)
- Precedent case library (similar appeals)
- Context aggregation engine (repurpose for appeals)

**New Integrations Built**:
- Appeal queue dashboard (UI for Tom's review)
- Discord escalation notifications (optional, moderator workflow improvement)

**Minimal New Effort**: 40-60 hrs (mostly UI, leveraging existing context engine)

---

### Integration Reuse Summary

| Asset | Built In | Reused In | Lines of Code | Value Amplification |
|-------|----------|-----------|---------------|---------------------|
| Discourse API client | Wave 1 | Wave 1, 2, 3 | 500 | 3× reuse |
| User profile service | Wave 1 | Wave 1, 2, 3 | 300 | 3× reuse |
| Spam classifier | Wave 1 | Wave 1, 2 | 800 | 2× reuse |
| Subforum taxonomy | Wave 1 | Wave 1, 2, 3 | 200 | 3× reuse |
| Logging infrastructure | Wave 1 | Wave 1, 2, 3 | 400 | 3× reuse |
| Context aggregation engine | Wave 2 | Wave 2, 3 | 1,200 | 2× reuse |
| Precedent case library | Wave 2 | Wave 2, 3 | 1,000 | 2× reuse |

**Total Code**: ~4,400 lines written across 12 weeks  
**Effective Code**: ~8,800 lines of value delivered (2× amplification from reuse)

---

## Success Criteria by Phase

### Phase 1 Success (Week 4 Gate)
**Goal**: Prove agent safety on low-risk, high-volume spam

✅ **Technical Feasibility**:
- Agent achieves ≥95% precision on spam classification
- Confidence scores calibrated within ±10% (0.9 confidence = 90% accuracy)
- False negative rate <0.1% on clear violations

✅ **Moderator Trust**:
- Daily sampling: zero viral false negatives detected
- Moderator survey: >4/5 trust score
- Volunteer feedback: "I don't think about link farms anymore"

✅ **Infrastructure**:
- Discourse API integration complete
- Logging & audit trail operational
- User profile retrieval service tested

**Gate Decision**: Proceed to Phase 2 (edge cases) OR roll back and refine

---

### Phase 2 Success (Week 8 Gate)
**Goal**: Prove agent can handle context-dependent edge cases with human oversight

✅ **Value Delivery**:
- Moderator time savings ≥5 hrs/day (60% of 7.5 hr target)
- Coverage rate ≥70% (800 cases/day automated)
- Cost per case <£0.05

✅ **Quality**:
- Moderator override rate <15% (agent proposals mostly correct)
- Exception detection accuracy >90% (correctly flags established members)
- No increase in user complaints or appeals

✅ **Codification Complete**:
- Subforum norms documented (painters, historical, gallery, Japanese)
- Spam taxonomy validated with moderators
- Exception rules codified (account age thresholds, etc.)

**Gate Decision**: Proceed to Phase 3 (grey-zone context) OR iterate on edge case handling

---

### Phase 3 Success (Week 12 Gate)
**Goal**: Reduce grey-zone case time from 4-5 min to 1.5-2 min via agent context

✅ **Value Delivery**:
- Total time savings ≥20 hrs/day (spam 7.5 + grey-zone 13.5)
- Grey-zone case time <2 min avg (vs. 4-5 min baseline)
- Context review time <30 sec (vs. 2-4 min manual gathering)

✅ **Quality**:
- Context completeness: moderator survey >4/5 ("agent gives me everything I need")
- Precedent relevance: >80% of retrieved cases are useful
- No decrease in grey-zone judgment quality (false neg/pos rates unchanged)

✅ **Infrastructure**:
- Tom's watchlist migrated to database
- Precedent case library operational (semantic search functional)
- Context aggregation engine tested on 100+ live cases

**Gate Decision**: 
- Proceed to Phase 4 (appeals) OR 
- Iterate on context quality OR 
- Declare success and focus on optimization

---

### Phase 4 Success (Week 16+ Gate)
**Goal**: Reduce Tom's appeal review time from 15-20 min to 8-10 min

✅ **Value Delivery**:
- Appeal resolution time reduced 30-40%
- Tom reports context is complete and saves time (survey >4/5)
- Total time savings ≥28 hrs/day (spam 7.5 + grey-zone 13.5 + appeals 7)

✅ **Business Impact**:
- ROI ≥3:1 (value / cost)
- Volunteer satisfaction improved (more time on valued work)
- Platform ready for 2,000+ posts/day (33% growth)
- Tom approves agent expansion to additional use cases

**Final Validation**: Tom says "This agent has fundamentally changed how we moderate"

---

## Implementation Costs and ROI

### Investment Breakdown

| Phase | Effort (hrs) | Cost (£) | Timeline | Key Deliverable |
|-------|-------------|---------|----------|----------------|
| **Phase 1: Spam Automation** | 130 hrs | £6,500 | 4 weeks | Routine spam auto-removal (800/day) |
| **Phase 2: Spam Edge Cases** | 44 hrs | £2,200 | 4 weeks | Off-topic commercial handling (280/day) |
| **Phase 3: Grey-Zone Context** | 112 hrs | £5,600 | 4 weeks | Context automation (360/day) |
| **Phase 4: Appeals (Optional)** | 60 hrs | £3,000 | 4 weeks | Appeal context prep (60/day) |
| **TOTAL (Phase 1-3)** | **286 hrs** | **£14,300** | **12 weeks** | Core agent functionality |
| **TOTAL (All Phases)** | **346 hrs** | **£17,300** | **16 weeks** | Full agent + appeals |

**Cost Assumptions**: £50/hr blended rate (FDE + developer time)

---

### Operating Costs (Post-Deployment)

| Component | Cost | Basis |
|-----------|------|-------|
| **Claude API tokens** | £2,500/year | 1,500 cases/day × 2,000 tokens/case avg × $0.003/1K tokens × £0.79/$ × 365 days |
| **Infrastructure hosting** | £300/year | AWS (vector DB, logging, API gateway) |
| **Maintenance & monitoring** | £1,000/year | 40 hrs × £25/hr (quarterly retraining, calibration) |
| **TOTAL Operating Cost** | **£3,800/year** | |

---

### Return on Investment (ROI)

**First-Year Economics** (Phase 1-3):

| Metric | Amount (£) |
|--------|-----------|
| **Value (First Year)** | |
| Time savings (spam + grey-zone) | £157,698 |
| Quality improvement | £10,575 |
| Risk reduction | £15,000 |
| **Total Value** | **£183,273** |
| **Cost (First Year)** | |
| Implementation (Phase 1-3) | £14,300 |
| Operating cost (9 months post-deployment) | £2,850 |
| **Total Cost** | **£17,150** |
| **Net Value (Year 1)** | **£166,123** |
| **ROI (Year 1)** | **10.7:1** |

**Payback Period**: 17,150 / (183,273 / 12) = **1.1 months** (agent pays for itself in 5 weeks)

---

**Ongoing Economics** (Year 2+):

| Metric | Amount (£) |
|--------|-----------|
| Annual value | £183,273 |
| Annual operating cost | £3,800 |
| **Net annual value** | **£179,473** |
| **ROI (Year 2+)** | **48.2:1** |

---

**5-Year Total Value**:
- Total value: £183,273 × 5 = **£916,365**
- Total cost: £14,300 (one-time) + £3,800 × 5 (operating) = **£33,300**
- **5-year ROI: 27.5:1**

---

**Risk-Adjusted ROI** (including avoided hiring):
- Avoided hiring: £40,000/year (1 FTE moderator not hired due to capacity relief)
- Risk-adjusted value: £183,273 + £40,000 = **£223,273/year**
- Risk-adjusted first-year ROI: **13.0:1**

---

## Appendix A: Discovery Questions for Tom (Validation)

Before finalizing this Agent Purpose Document, validate the following assumptions with Tom (Community Manager):

### Business Context Validation
1. **Volunteer cost**: How should we value volunteer moderator time? (currently using £12/hr opportunity cost)
2. **Sponsor sensitivity**: What exactly happened in the "2024 sponsor incident"? What are the consequences?
3. **Revenue breakdown**: Confirm £1.4M/year split between premium memberships, gallery commissions, sponsors
4. **Growth trajectory**: Is 180K → 450K users (2.5×) realistic over 3 years?

### Operational Reality Check
5. **Watchlist usage**: How do you actually use your Google Sheet tracker day-to-day? What patterns do you track?
6. **Precedent tracking**: Do moderators actually consult past cases, or decide based on intuition?
7. **Discord coordination**: How often do moderators discuss edge cases in Discord? How valuable is that coordination?
8. **Appeal frequency**: You mentioned 60/day appeals - is that consistent or seasonal (spikes after bans, etc.)?

### Agent Design Validation
9. **Confidence threshold**: Would you be comfortable with agent auto-removing spam at 0.9 confidence (90% accuracy)?
10. **Escalation SLA**: Are the escalation priorities (Urgent: 2-4 hrs, Medium: 12 hrs) realistic for your team?
11. **Context completeness**: When reviewing a grey-zone case, what information do you wish you had immediately available?
12. **Override comfort**: How would you feel if moderators override 10-15% of agent decisions? Too high? Acceptable?

### Risk & Safety Validation
13. **Existential false negatives**: Besides harassment and sponsor incidents, what other false negatives are existential?
14. **Subforum norms**: Are painters invitation rule, historical permissiveness, Japanese cultural interpretation the top 3 norms? What did we miss?
15. **Established member threshold**: At what point is a user "established" enough to get exception handling? (1 year? 500 posts?)
16. **IP claim patterns**: What makes an IP claim likely legitimate vs. retaliatory? Any patterns?

### Success Criteria Validation
17. **Time savings target**: Is 7 hrs/day freed capacity (spam automation) enough to make a material difference?
18. **Coverage expectations**: Would 70-80% spam automation meet your needs, or do you need higher?
19. **Cost tolerance**: Is £0.05/case (spam) and £0.10/case (grey-zone context) acceptable? What's your ceiling?
20. **Volunteer satisfaction**: If we redirect volunteer time from 60% spam → 20% spam, 35% grey-zone → 70% grey-zone, is that the right balance?

---

## Appendix B: Technical Architecture (High-Level)

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    MiniBase Moderation Agent                 │
│                         (Guardian)                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Orchestration Layer                     │
│  - Case routing (spam vs. grey-zone vs. escalation)         │
│  - Delegation logic (fully agentic vs. HITL vs. human-only) │
│  - Workflow management (queue, escalation, appeal)          │
└─────────────────────────────────────────────────────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  Spam Removal    │  │  Context         │  │  Escalation      │
│  Agent (Phase 1) │  │  Gathering Agent │  │  Handler         │
│                  │  │  (Phase 3)       │  │                  │
│ - Pattern match  │  │ - User profile   │  │ - Watchlist      │
│ - ML classifier  │  │ - Subforum norms │  │ - Sponsor check  │
│ - Confidence     │  │ - Precedent      │  │ - Engagement     │
│ - Auto-remove    │  │   search         │  │ - Cultural flag  │
└──────────────────┘  └──────────────────┘  └──────────────────┘
          │                    │                    │
          └────────────────────┴────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data & Integration Layer                │
└─────────────────────────────────────────────────────────────┘
  │           │            │            │            │
  ▼           ▼            ▼            ▼            ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│Discourse│ │Gallery │ │Watchlist│ │Subforum│ │Precedent│
│  API   │ │  API   │ │   DB   │ │ Norms  │ │  DB     │
│        │ │        │ │        │ │   DB   │ │ (Vector)│
└────────┘ └────────┘ └────────┘ └────────┘ └────────┘

┌─────────────────────────────────────────────────────────────┐
│                      Platform Services                       │
│  - Logging & audit trail (compliance, appeals)               │
│  - Monitoring & alerting (drift detection, error tracking)   │
│  - User notification (removal messages, appeal links)        │
│  - Moderator dashboard (escalation queue, sampling audit)    │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack (Recommended)

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Agent Runtime** | Claude Opus 4.6 (Anthropic API) | Best reasoning capability, tool use, long context |
| **Orchestration** | Python (FastAPI) | Async support, rich ecosystem, moderator familiarity |
| **Vector DB** | Pinecone or Weaviate | Semantic search for precedent matching |
| **Relational DB** | PostgreSQL | Watchlist, subforum norms, audit logs |
| **Caching** | Redis | User profile caching, rate limit management |
| **Hosting** | AWS (ECS + RDS + ElastiCache) | Scalable, moderator team already uses AWS |
| **Monitoring** | Datadog or Grafana | Real-time alerting, drift detection |
| **Logging** | AWS CloudWatch + S3 | Compliance, audit trail, long-term retention |

---

## Appendix C: Glossary

**Agentic**: Describes work where the agent decides and acts autonomously (vs. advisory where human decides)

**ATX**: Agentic Transformation eXperience - methodology for designing enterprise agents (from FDE program)

**Delegation Archetype**: Standard pattern for dividing work between agent and human (Fully Agentic, Agent-Led, Human-Led, Human-Only)

**False Negative**: Agent fails to flag/remove harmful content (it "misses" a violation) - existential risk for MiniBase

**False Positive**: Agent removes legitimate content (wrongly classifies as spam) - survivable but trust-eroding

**Grey-Zone Case**: Ambiguous flagged post requiring human judgment (harsh critique, commercial content, cultural interpretation)

**HITL**: Human-In-The-Loop - human oversight or approval required before agent action

**Lived Work**: How work actually gets done (tribal knowledge, Discord discussions, Tom's Google Sheet) vs. documented policy (14-page moderation guide)

**Precedent Case**: Similar past moderation decision stored in case library for consistency (semantic search retrieval)

**Subforum Norms**: Community-specific rules that override global policy (e.g., painters "no critique without invitation")

**Watchlist**: Tom's tracker of high-risk users (fraud patterns, sponsor accounts, established sculptors) requiring special handling

**Viral False Negative**: Missed harmful content that spreads widely (Twitter, Reddit) creating PR crisis - existential risk

---

## Document Control

**Version History**:
- v1.0 (2026-04-29): Initial Agent Purpose Document

**Authors**: FDE Program Week 2 Team

**Approvals Required**:
- Tom (Community Manager): Business validation, operational feasibility
- Sarah (Volunteer Moderator): Lived work validation, trust threshold
- FDE Program Coach: ATX methodology alignment

**Related Documents**:
- `01_Problem_Statement_and_Success_Metrics.md` (Business context)
- `02_Discovery_Phase.md` (Lived work findings)
- `03_Cognitive_Load_Map.md` (Micro-task decomposition)
- `04_Delegation_Suitability_Matrix.md` (Delegation scoring)
- `05_Volume_Value_Analysis.md` (Prioritization & ROI)
- `FDE_Program/Week2/enriched_scenarios.md` (Scenario 4 details)

**Next Steps**:
1. **Validation with Tom** (Week 5): Review discovery questions (Appendix A), confirm assumptions, adjust design
2. **Moderator Workshop** (Week 5): Present Agent Purpose Document to volunteer team, gather feedback on autonomy matrix
3. **Technical Feasibility Review** (Week 5): Assess Discourse API limits, gallery API gaps, data codification effort
4. **Gate 2 Submission** (Week 5): Submit Agent Purpose Document + validation findings to FDE program
5. **Build Sprint Kickoff** (Week 6): If Gate 2 approved, begin Phase 1 implementation (spam classifier development)

**Last Review**: 2026-04-29
