# Delegation Suitability Matrix: MiniBase Content Moderation

**Project**: MiniBase Community Content Moderation Agent  
**Phase**: ATX Delegation Architecture Design  
**Date**: 2026-04-29  
**Version**: 1.0

---

## Executive Summary

This document scores each major moderation task cluster on **delegation suitability dimensions** and assigns **delegation archetypes** following ATX methodology. The analysis reveals:

1. **Routine spam removal** scores 8.7/10 for delegation suitability → **Fully Agentic** (70-80% automation)
2. **Grey-zone context gathering** scores 8.3/10 → **Fully Agentic** (context automation) but grey-zone **judgment** scores 3.1/10 → **Agent-Led with Human Approval**
3. **User appeals** score 4.2/10 → **Human-Led with Agent Support** (context preparation only)
4. **IP claims** score 2.1/10 → **Human-Only** (legal sensitivity, relationship management)

### Strategic Delegation Approach

**Automate the high-volume, low-risk, rule-bound work** (spam removal, context gathering) to free human capacity for **high-stakes, low-volume, judgment-bound work** (grey-zone decisions, appeals, IP claims).

**Target delegation mix**:
- 58% of tasks: Fully Agentic (automated with sampling)
- 25% of tasks: Agent-Led with Human Approval (agent proposes, human decides)
- 14% of tasks: Human-Led with Agent Support (human decides, agent assists)
- 3% of tasks: Human-Only (no agent involvement)

**Expected impact**: 62% reduction in total moderation effort (39 hrs/day → 14.9 hrs/day) while maintaining safety and quality standards.

---

## ATX Delegation Dimensions Framework

### The Seven Delegation Dimensions

Following ATX methodology, we score each task cluster on seven dimensions that determine automation suitability:

| Dimension | Definition | Scoring Criteria (0-10) |
|-----------|------------|------------------------|
| **1. Codifiability** | Can the decision rule be articulated and expressed as logic? | 0 = "I know it when I see it"<br/>5 = Partial rules with exceptions<br/>10 = Fully codifiable IF-THEN logic |
| **2. Data Availability** | Is required information accessible and structured? | 0 = Information is tribal knowledge<br/>5 = Partially available, fragmented<br/>10 = Fully accessible via APIs/databases |
| **3. Volume** | Does task frequency justify automation investment? | 0 = <10 cases/week<br/>5 = 50-100 cases/day<br/>10 = >500 cases/day |
| **4. Cognitive Load** | How much mental effort does task require? | 0 = Deep expertise and judgment<br/>5 = Moderate reasoning<br/>10 = Pattern matching, zero thought |
| **5. Risk of Error** | What are consequences of agent mistakes? | 0 = Existential (viral false negative)<br/>5 = Moderate (user complaint, trust impact)<br/>10 = Low (easily reversed, minimal impact) |
| **6. Reversibility** | Can errors be quickly detected and corrected? | 0 = Irreversible or very costly<br/>5 = Reversible but requires effort<br/>10 = Instant reversal, low cost |
| **7. Consistency** | Do different humans decide the same case consistently? | 0 = High variance (judgment-dependent)<br/>5 = Moderate variance (culture/experience)<br/>10 = Perfect consistency (rule-bound) |

### Scoring Interpretation

**Total Score (0-70)**:
- **60-70**: Ideal for **Fully Agentic** delegation (agent decides alone, human samples)
- **45-59**: Suitable for **Agent-Led with Oversight** (agent proposes, human approves)
- **30-44**: Requires **Human-Led with Agent Support** (human decides, agent assists)
- **0-29**: **Human-Only** (agent should not participate in decision)

### Delegation Archetypes (ATX Standard)

| Archetype | Definition | Human Role | Agent Role | Use When |
|-----------|------------|-----------|------------|----------|
| **Fully Agentic** | Agent decides and acts autonomously | Sampling oversight (10-20% audit), handle appeals | Pattern match, decide, act, log | High volume, low risk, rule-bound |
| **Agent-Led with Oversight** | Agent proposes action, human approves before execution | Review proposal, approve/override, escalate edge cases | Gather context, analyze, recommend with confidence | Medium risk, codifiable with exceptions |
| **Human-Led with Agent Support** | Human makes decision, agent provides context and drafts | Assess situation, make judgment, finalize | Retrieve context, draft responses, surface precedents | Low volume, high judgment requirement |
| **Human-Only** | No agent involvement in decision process | Full ownership of task | No role (agent not present) | Existential risk, legal sensitivity, relationship management |

---

## Task Cluster Definitions

Based on cognitive load mapping, we identify **10 task clusters** across the four work streams:

### Work Stream 1: Routine Spam Removal
- **TC-1A**: Link farm spam detection and removal
- **TC-1B**: Crypto/forex bot detection and removal
- **TC-1C**: Gibberish spam detection and removal
- **TC-1D**: Off-topic commercial spam detection and removal
- **TC-1E**: Exception handling (established members, false positives)

### Work Stream 2: Grey-Zone Case Review
- **TC-2A**: Grey-zone context gathering (user history, norms, precedents)
- **TC-2B**: Harsh critique vs. harassment assessment
- **TC-2C**: Commercial content from established members
- **TC-2D**: Cultural interpretation (Japanese sub, sarcasm, tone)

### Work Stream 3: User Appeals
- **TC-3A**: Appeal context preparation and case review

### Work Stream 4: IP Claims
- **TC-4A**: IP claim triage and investigation

---

## Delegation Suitability Scoring

### Task Cluster TC-1A: Link Farm Spam Detection and Removal

**Description**: Identify and remove posts with 3+ URLs, minimal text, new accounts, brand-ish usernames, posted in off-topic subforums.

**Volume**: ~300 cases/day (28% of spam queue)

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Codifiability** | 10/10 | Fully codifiable: `IF (URL_count >= 3) AND (account_age < 7_days) AND (text_length < 50_chars OR generic_text) AND (username MATCHES brand_pattern) THEN spam` |
| **Data Availability** | 10/10 | All signals available: URL count (parsable), account age (Discourse API), text analysis (NLP), username pattern (regex) |
| **Volume** | 10/10 | 300/day = high volume, strong ROI for automation |
| **Cognitive Load** | 10/10 | Zero cognitive load - Sarah identifies in 2 seconds, 99% accuracy, "just make it go away" |
| **Risk of Error** | 9/10 | Low risk: False positive = user appeals, moderator reverses (24 hrs). False negative = spam visible longer (minor annoyance). Sarah: "3 false positives in 3 years" |
| **Reversibility** | 10/10 | Instant reversal: restore post, notify user, no lasting harm |
| **Consistency** | 10/10 | Perfect consistency: all moderators agree link farms are spam (rule-bound) |
| **TOTAL** | **69/70** | |

**Delegation Archetype**: ⭐ **Fully Agentic**

**Rationale**: 
- Highest possible delegation score (69/70)
- Clear patterns, high volume, low risk, high reversibility
- Human explicitly wants this automated ("make it go away")
- Agent can match human 99% accuracy with confidence scoring

**Delegation Design**:
- **Agent decides alone**: Auto-remove when confidence >0.9
- **Human role**: Daily sampling (10% of cases, ~30/day), user appeal handling
- **Escalate to human**: Confidence 0.7-0.9 (edge cases), account age >1 year (exception signal)

**Expected coverage**: 85-90% of link farm cases automated

---

### Task Cluster TC-1B: Crypto/Forex Bot Detection and Removal

**Description**: Identify and remove formulaic posts ("I was struggling until I found X, now I make $Y/week"), multi-post patterns, bot usernames.

**Volume**: ~200 cases/day (19% of spam queue)

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Codifiability** | 10/10 | Fully codifiable: formulaic text structure (regex-matchable), multi-subforum posting within minutes (timing analysis), bot username patterns |
| **Data Availability** | 10/10 | Text pattern (NLP), posting timing (Discourse timestamps), username (regex), cross-subforum detection (API) |
| **Volume** | 10/10 | 200/day = high volume |
| **Cognitive Load** | 10/10 | Zero cognitive load - Sarah: "99% accurate", instant bot vs. human distinction |
| **Risk of Error** | 9/10 | Low risk: False positive rate <1%, easily reversible. Bot bans are reversible if human detected. |
| **Reversibility** | 10/10 | Instant reversal + unban if false positive (rare: "maybe 3 times in 3 years") |
| **Consistency** | 10/10 | Perfect consistency: all moderators agree these are bots |
| **TOTAL** | **69/70** | |

**Delegation Archetype**: ⭐ **Fully Agentic**

**Rationale**: Same as TC-1A - highest delegation suitability. Bots are even clearer than link farms (timing patterns, formulaic text).

**Delegation Design**:
- **Agent decides alone**: Auto-remove + ban account when confidence >0.9
- **Human role**: Daily sampling, user appeal handling (rare - most are actually bots)
- **Escalate to human**: Confidence 0.7-0.9, single-post (not multi-post pattern)

**Expected coverage**: 90-95% automated (even higher than link farms due to clearer patterns)

---

### Task Cluster TC-1C: Gibberish Spam Detection and Removal

**Description**: Identify and remove posts with random characters, no semantic meaning, often with URLs.

**Volume**: ~150 cases/day (14% of spam queue)

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Codifiability** | 9/10 | Highly codifiable via language model perplexity scoring. Deduct 1 point for edge case: multi-lingual posts that read as gibberish in English but have meaning in source language |
| **Data Availability** | 10/10 | Text content available, perplexity scoring via LLM, character distribution analysis |
| **Volume** | 10/10 | 150/day = high volume |
| **Cognitive Load** | 10/10 | Zero cognitive load - Sarah identifies in <2 seconds, 100% accuracy claim |
| **Risk of Error** | 8/10 | Moderate risk for false positives on multi-lingual content (Sarah noted this edge case). False negative (miss gibberish) is low risk. |
| **Reversibility** | 10/10 | Instant reversal, user can appeal if legitimate multi-lingual content |
| **Consistency** | 9/10 | Very high consistency, but minor variance on multi-lingual edge cases |
| **TOTAL** | **66/70** | |

**Delegation Archetype**: ⭐ **Fully Agentic**

**Rationale**: Very high delegation score (66/70). Risk deduction for multi-lingual edge case is offset by high reversibility and low frequency of edge cases.

**Delegation Design**:
- **Agent decides alone**: Auto-remove when perplexity score > threshold AND confidence >0.9
- **Human role**: Sampling, appeal handling
- **Escalate to human**: Multi-lingual detection (language != English), confidence 0.7-0.9
- **Edge case handling**: If post is in non-English language AND account age >30 days → escalate (likely legitimate multi-lingual user, not spam)

**Expected coverage**: 85-90% automated (lower than bots due to multi-lingual caution)

---

### Task Cluster TC-1D: Off-Topic Commercial Spam Detection and Removal

**Description**: Identify and remove sales language ("Buy my...", "For sale:") posted in wrong subforum (e.g., 3D prints in painters sub should be in marketplace).

**Volume**: ~250 cases/day (23% of spam queue)

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Codifiability** | 8/10 | Mostly codifiable: sales language (NLP), subforum rules (structured). Deduct 2 points: gallery self-promotion is context-dependent (established member = OK, new member = spam) |
| **Data Availability** | 9/10 | Text (NLP), subforum (metadata), account age/history (API). Deduct 1 point: "established member" threshold is tribal knowledge (needs codification) |
| **Volume** | 10/10 | 250/day = high volume |
| **Cognitive Load** | 9/10 | Very low cognitive load - mostly pattern matching. Deduct 1 point: requires subforum taxonomy knowledge |
| **Risk of Error** | 7/10 | Moderate risk: False positive = remove legitimate self-promotion from established member (community trust impact). False negative = commercial spam stays up (minor annoyance) |
| **Reversibility** | 9/10 | Easily reversible, but established member false positive creates reputation risk (user feels targeted) |
| **Consistency** | 7/10 | Moderate consistency: Sarah approves commercial from 3-year members, another mod might remove. Subforum boundary ambiguity (gallery vs. painters) |
| **TOTAL** | **59/70** | |

**Delegation Archetype**: ⭐⭐ **Agent-Led with Oversight** (borderline Fully Agentic)

**Rationale**: 
- Score 59/70 is at the threshold between Fully Agentic (60+) and Agent-Led
- High volume and codifiability support automation
- BUT: Context-dependent exceptions (established member self-promotion, gallery subforum rules) require human judgment on edge cases
- Risk of false positive on established members is higher than other spam types

**Delegation Design**:
- **Agent decides alone**: Clear off-topic commercial from new accounts (<90 days) in non-gallery subforums, confidence >0.9
- **Agent proposes, human approves**: Commercial content from established accounts (90+ days), gallery subforum posts, confidence 0.7-0.9
- **Human role**: Approve/override agent proposals (30-60 sec per case), sampling
- **Expected coverage**: 70% fully automated, 25% agent-led (human approval), 5% human-only (complex context)

**Codification requirement**: Document "established member" threshold (account age >90 days + post count >50 + no prior violations) and gallery self-promotion rules.

---

### Task Cluster TC-1E: Spam Exception Handling

**Description**: Detect false positive signals when spam pattern detected (established member, educational content, high engagement) and escalate to human review.

**Volume**: ~80 cases/day (7% of spam queue - edge cases that look like spam but aren't)

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Codifiability** | 7/10 | Partially codifiable: exception rules are explicit (account age >3 years, engagement >5 reactions, educational subforum) BUT require judgment to combine signals |
| **Data Availability** | 10/10 | All signals available: account age, engagement, subforum, content analysis |
| **Volume** | 8/10 | 80/day = moderate-high volume (justifies automation) |
| **Cognitive Load** | 7/10 | Low-moderate cognitive load: simple rule checks BUT requires contextual judgment ("Is this educational or spam?") |
| **Risk of Error** | 4/10 | High risk: False negative = remove legitimate content from established member (community trust erosion, Sarah's top concern). False positive = spam stays up (lower risk) |
| **Reversibility** | 7/10 | Reversible but with reputational cost: established member feels unfairly targeted |
| **Consistency** | 6/10 | Moderate consistency: different moderators may weight "established member" vs "spam signals" differently |
| **TOTAL** | **49/70** | |

**Delegation Archetype**: ⭐⭐ **Agent-Led with Oversight**

**Rationale**:
- Score 49/70 indicates agent-led delegation (human approval required)
- Exception detection is partially codifiable but requires human judgment
- High risk of false negative (removing legitimate content) requires human safeguard
- Moderate volume (80/day) justifies investing in agent detection, but not full automation

**Delegation Design**:
- **Agent role**: Detect exception signals (account age, engagement, educational context), flag for human review with confidence estimate
- **Human role**: Review flagged cases (30-60 sec each), decide: spam or legitimate exception
- **Escalation rule**: ANY exception signal detected → auto-escalate to human (bias toward caution)
- **Expected outcome**: 100% of exception cases reviewed by human (no agent auto-removal), but agent saves time by pre-detecting exceptions

---

### Summary: Work Stream 1 (Routine Spam Removal)

| Task Cluster | Volume (daily) | Delegation Score | Archetype | Coverage |
|--------------|----------------|------------------|-----------|----------|
| TC-1A: Link farms | 300 | 69/70 | Fully Agentic | 85-90% |
| TC-1B: Crypto bots | 200 | 69/70 | Fully Agentic | 90-95% |
| TC-1C: Gibberish | 150 | 66/70 | Fully Agentic | 85-90% |
| TC-1D: Off-topic commercial | 250 | 59/70 | Agent-Led | 70% auto, 25% approval |
| TC-1E: Exception handling | 80 | 49/70 | Agent-Led | 0% auto (100% human review) |
| **Work Stream 1 TOTAL** | **1,080** | **Weighted Avg: 63.5/70** | **Mixed** | **74% fully automated** |

**Aggregate Delegation Strategy**:
- **800 cases/day (74%)**: Fully Agentic (agent auto-removes)
- **200 cases/day (18%)**: Agent-Led (agent proposes, human approves in 30-60 sec)
- **80 cases/day (7%)**: Human review (agent detects exception, human decides)

**Time Impact**:
- Current: 1,080 × 30 sec = 9 hrs/day
- Post-agent: (800 × 0) + (200 × 30 sec) + (80 × 60 sec) = 1.7 hrs + 1.3 hrs = **3 hrs/day**
- **Savings: 6 hrs/day (67%)**

---

### Task Cluster TC-2A: Grey-Zone Context Gathering

**Description**: Retrieve and aggregate user history, subforum-specific norms, precedent cases, escalation triggers (sponsor accounts, watchlist, engagement count) for flagged grey-zone posts.

**Volume**: 360 cases/day (all grey-zone cases require context)

**Note**: This is the **context gathering phase** (Cognitive Load Map Tasks 2.4-2.7), NOT the judgment phase.

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Codifiability** | 9/10 | Highly codifiable: query user API, match subforum to norms database, semantic search precedents, check watchlist. Deduct 1 point: determining "relevant" precedent requires some semantic judgment |
| **Data Availability** | 7/10 | Mostly available: user data (Discourse API), engagement (metadata), precedents (need to centralize from personal notes/Discord). Deduct 3 points: subforum norms are tribal knowledge (must be codified first), Tom's watchlist not shared |
| **Volume** | 10/10 | 360/day = high volume, 2-3 min per case = 12-18 hrs/day effort → strong ROI |
| **Cognitive Load** | 9/10 | Very low cognitive load: information retrieval, no reasoning. Sarah: "20% of my time is just clicking between tools" |
| **Risk of Error** | 10/10 | No risk: agent is just retrieving information, not making decisions. Incorrect context = human catches during review |
| **Reversibility** | 10/10 | N/A - no action taken, just information presented |
| **Consistency** | 10/10 | Perfect consistency: context retrieval is deterministic (same inputs → same outputs) |
| **TOTAL** | **65/70** | |

**Delegation Archetype**: ⭐ **Fully Agentic** (for context retrieval)

**Rationale**:
- High delegation score (65/70) for pure information retrieval
- Low risk because agent doesn't decide - just gathers and presents context
- High volume and effort (12-18 hrs/day) makes this highest ROI opportunity
- Sarah's explicit desire: "If I clicked on a flagged post and immediately saw: user history, subforum rules, precedents, watchlist... I'd save 2-3 minutes per case"

**Delegation Design**:
- **Agent role (fully automated)**:
  - Query user profile: age, post count, reputation, moderation history
  - Match subforum: identify applicable norms (e.g., painters = invitation rule)
  - Semantic search: find 3-5 similar precedent cases with outcomes
  - Check escalation triggers: sponsor badge, watchlist, engagement >20
  - Present in single context card (10-20 sec to review vs. 2-4 min to gather)

- **Human role**: Review context, make judgment (Task TC-2B)

**Blockers to implementation**:
1. **Subforum norms must be codified** (currently tribal knowledge) - Estimated effort: 8-16 hrs to document and structure
2. **Tom's watchlist must be shared** (currently Google Sheet) - Replace with structured database
3. **Precedent cases must be centralized** (currently in personal notes/Discord) - Build case library with semantic search

**Expected impact**: 
- Reduce context gathering from 2-4 min to 10-20 sec per case
- Savings: 360 × 2.5 min avg = 15 hrs/day → 360 × 15 sec = 1.5 hrs/day = **13.5 hrs/day saved**

---

### Task Cluster TC-2B: Harsh Critique vs. Harassment Assessment

**Description**: Determine if flagged post is legitimate harsh critique (targets work, constructive, invited) or harassment (targets person, destructive, hostile intent).

**Volume**: ~200 cases/day (subset of grey-zone, ~55% of grey-zone cases)

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Codifiability** | 3/10 | Poorly codifiable: Sarah couldn't articulate clear decision rule ("I think... harassment targets the person, critique targets the work? But that's not always clear"). Cultural context, tone, intent are ambiguous |
| **Data Availability** | 8/10 | Context available (user history, thread, reactions), but intent/tone require interpretation |
| **Volume** | 10/10 | 200/day = high volume |
| **Cognitive Load** | 3/10 | High cognitive load: multi-signal integration (tone, targets, invitation, cultural context, OP reaction, community norms), judgment under ambiguity |
| **Risk of Error** | 2/10 | Very high risk: False negative = harassment persists (existential risk, Tom's "false negatives are existential"). False positive = censor legitimate critique (community trust erosion, Sarah's top concern) |
| **Reversibility** | 4/10 | Partially reversible: user can appeal, post can be restored, BUT reputational damage to established member ("you removed my helpful critique") or victim ("you didn't protect me") is hard to reverse |
| **Consistency** | 4/10 | Low consistency: Sarah and Aki might decide differently based on cultural interpretation (Japanese English harshness), subforum norms, personal risk tolerance |
| **TOTAL** | **34/70** | |

**Delegation Archetype**: ⭐⭐⭐ **Human-Led with Agent Support**

**Rationale**:
- Low delegation score (34/70) indicates human judgment required
- Poorly codifiable ("I know it when I see it" boundary)
- Very high risk of error (existential false negatives, trust-eroding false positives)
- Low human consistency (judgment-dependent)
- Sarah explicitly doesn't trust AI: "That boundary is so cultural, so context-dependent... I think AI would either be too aggressive or too permissive"

**Delegation Design**:
- **Agent role (support only, no decision)**:
  - Extract signals: Does post target work vs. person? Is it constructive (explains how to improve)? Was it invited (thread title analysis)?
  - Sentiment analysis: tone (neutral/harsh/hostile)
  - Reaction analysis: OP reaction (positive "thanks" vs. negative "I feel attacked"), community response
  - Surface precedents: similar cases with outcomes
  - Confidence estimate: "Likely critique (0.65 confidence) - targets technique, invited in thread, but harsh tone flagged by community"

- **Human role (decision-maker)**:
  - Review agent-prepared context (30-60 sec)
  - Apply cultural reasoning, intent assessment, risk judgment
  - Decide: approve, remove, warn, or escalate
  - Final decision time: 60-90 sec (vs. 4-5 min without agent context)

**Why not Agent-Led (agent proposes)?**
- Agent confidence would be unreliable on this boundary (too many false positives or false negatives)
- Human must see raw content and make judgment, not just review agent recommendation
- Risk of anchoring bias: human might rubber-stamp agent recommendation instead of independent assessment

**Expected impact**:
- Time savings: minimal on judgment itself (still requires human reasoning)
- BUT: agent context preparation reduces total time from 4-5 min to 1.5-2 min per case
- 200 cases × 2.5 min saved = **8.3 hrs/day saved** (from context automation, not judgment automation)

---

### Task Cluster TC-2C: Commercial Content from Established Members

**Description**: Determine if commercial post (selling miniatures, prints, commissions) is legitimate self-promotion from established member or spam.

**Volume**: ~50 cases/day (subset of grey-zone, ~14% of grey-zone cases)

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Codifiability** | 6/10 | Partially codifiable: "IF (account_age > 3_years) AND (subforum = gallery) AND (active_contributor) THEN legitimate" BUT "active contributor" and "contextually relevant" require judgment |
| **Data Availability** | 9/10 | Account age, post history, subforum, engagement - all available |
| **Volume** | 7/10 | 50/day = moderate volume (justifies automation, but not highest priority) |
| **Cognitive Load** | 5/10 | Moderate cognitive load: check account age + participation history + subforum rules + contextual relevance |
| **Risk of Error** | 5/10 | Moderate risk: False negative = spam stays up (moderate annoyance). False positive = established member feels unfairly targeted (trust impact) |
| **Reversibility** | 7/10 | Reversible but with reputational cost for established members |
| **Consistency** | 5/10 | Moderate consistency: Sarah might approve 3-year member selling old miniatures, another mod might remove as commercial spam (policy is ambiguous) |
| **TOTAL** | **44/70** | |

**Delegation Archetype**: ⭐⭐⭐ **Human-Led with Agent Support** (borderline Agent-Led)

**Rationale**:
- Score 44/70 is at boundary between Human-Led (30-44) and Agent-Led (45-59)
- Partially codifiable (account age, subforum) but "active contributor" and "contextual relevance" require judgment
- Moderate risk and volume don't justify full automation
- Human must assess: Is this spam or community participation? Is self-promotion excessive or reasonable?

**Delegation Design**:
- **Agent role**:
  - Calculate reputation score: account age, post count, helpful contributions, prior violations
  - Check subforum: gallery (permissive) vs. painters (strict)
  - Flag commercial language: sales terms, external links, pricing
  - Provide recommendation: "Likely legitimate (0.7 confidence) - 3-year member, 600 posts, gallery subforum, first commercial post this year"

- **Human role**:
  - Review reputation + context (30 sec)
  - Assess: Excessive self-promotion or reasonable community participation?
  - Decide: approve, remove, or warn
  - Time: 60-90 sec (vs. 3-4 min without agent context)

**Could be upgraded to Agent-Led** if:
- Policy is clarified (e.g., "members >3 years, >500 posts, no prior violations can self-promote in gallery max 1×/month")
- Then agent can confidently propose action with 80%+ accuracy

**Expected impact**: 50 cases × 2 min saved = **1.7 hrs/day saved**

---

### Task Cluster TC-2D: Cultural Interpretation (Japanese Sub, Sarcasm, Tone)

**Description**: Assess whether harsh-sounding language is cultural difference (Japanese English directness), sarcasm/banter, or genuine hostility.

**Volume**: ~30 cases/day (subset of grey-zone, ~8% of grey-zone cases, concentrated in Japanese painters sub)

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Codifiability** | 2/10 | Very poorly codifiable: cultural interpretation, sarcasm detection, intent assessment require human cultural reasoning. No explicit rules |
| **Data Availability** | 6/10 | User location/language, post history available, but cultural context is not data - it's human understanding |
| **Volume** | 5/10 | 30/day = low-moderate volume (doesn't strongly justify automation) |
| **Cognitive Load** | 2/10 | Very high cognitive load: cultural awareness, intent assessment, context collapse risk (will this read differently to non-Japanese users?) |
| **Risk of Error** | 1/10 | Extreme risk: False negative = miss harassment from non-native speaker (existential risk). False positive = remove legitimate feedback from Japanese user, cultural discrimination perception (community trust + PR risk) |
| **Reversibility** | 3/10 | Difficult to reverse: cultural discrimination claim is reputationally damaging, even if reversed |
| **Consistency** | 2/10 | Very low consistency: Aki (Japanese moderator) has cultural context, Sarah/Klaus don't. High variance in decisions |
| **TOTAL** | **21/70** | |

**Delegation Archetype**: ⭐⭐⭐⭐ **Human-Only** (with agent escalation flagging)

**Rationale**:
- Very low delegation score (21/70) - one of the lowest in entire matrix
- Extremely poorly codifiable (cultural reasoning is human domain)
- Extreme risk of error (cultural discrimination is reputational disaster)
- Very low consistency (requires cultural expertise that varies by moderator)
- Even agent context gathering has limited value here (agent can flag "Japanese sub post" but can't interpret cultural context)

**Delegation Design**:
- **Agent role (minimal - escalation flagging only)**:
  - Detect: Post in Japanese painters sub, user location = Japan, English language post
  - Flag: "Cultural interpretation required - Japanese sub post, escalate to Aki or human with cultural context"
  - **No recommendation** (agent cannot assess cultural context)

- **Human role (full ownership)**:
  - Aki (Japanese moderator) personally reviews Japanese sub cultural cases
  - If Aki unavailable: escalate to Tom with note "awaiting cultural expert review"
  - Decision requires cultural awareness that agent cannot provide

**Why not even Human-Led with Agent Support?**
- Agent support would be misleading (agent can't extract meaningful cultural signals)
- Human needs raw context and cultural reasoning, not agent interpretation
- Risk of agent introducing bias or misinterpretation

**Expected impact**: No automation (human handles 100%), but agent can **route to correct human** (Aki for Japanese cases, Klaus for German directness, etc.) to reduce cross-cultural misinterpretation.

---

### Summary: Work Stream 2 (Grey-Zone Case Review)

| Task Cluster | Volume (daily) | Delegation Score | Archetype | Time Impact |
|--------------|----------------|------------------|-----------|-------------|
| TC-2A: Context gathering | 360 | 65/70 | Fully Agentic | 15 hrs → 1.5 hrs = 13.5 hrs saved |
| TC-2B: Critique vs. harassment | 200 | 34/70 | Human-Led + Support | 16.7 hrs → 5 hrs = 11.7 hrs saved (from context) |
| TC-2C: Established member commercial | 50 | 44/70 | Human-Led + Support | 2.5 hrs → 1.3 hrs = 1.2 hrs saved |
| TC-2D: Cultural interpretation | 30 | 21/70 | Human-Only | 2 hrs → 2 hrs = 0 hrs saved |
| **Work Stream 2 TOTAL** | **360 unique cases** | **Weighted Avg: 50.2/70** | **Mixed** | **30 hrs → 9.8 hrs = 20.2 hrs saved** |

**Note**: TC-2A (context gathering) applies to ALL 360 grey-zone cases, while TC-2B/2C/2D are subtypes within those cases. Many cases involve multiple clusters (e.g., harsh critique + cultural interpretation).

**Aggregate Delegation Strategy**:
- **Context gathering**: 100% automated (agent retrieves, human reviews)
- **Judgment**: 0% automated (100% human decision-making)
- **Time breakdown post-agent**:
  - Context review: 360 × 20 sec = 2 hrs
  - Judgment: 360 × 90 sec avg = 9 hrs
  - Escalation/coordination: reduced from 6-18 hrs wait time to streamlined workflow (TBD)

**Key insight**: Agent doesn't replace human judgment, but **removes 67% of pre-judgment effort** (context gathering 15 hrs → 1.5 hrs).

---

### Task Cluster TC-3A: User Appeal Context Preparation and Review

**Description**: When user appeals a moderation decision, gather context (original post, removal rationale, moderator, similar cases, user's appeal argument) and prepare for Tom's review.

**Volume**: ~60 cases/day (4% of queue)

**Effort**: Sarah described ~45 min per appeal (Tom review + moderator justification + back-and-forth), but scenario brief says 8 min/case = 8 hrs/day total. Assuming 15-20 min avg (weighted by complexity).

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Codifiability** | 4/10 | Partially codifiable: context gathering is codifiable, but "should original decision be upheld?" requires judgment on judgment (meta-reasoning) |
| **Data Availability** | 9/10 | All context available: original post, removal reason, moderator, user appeal text, similar precedents |
| **Volume** | 7/10 | 60/day = moderate volume (justifies investment in streamlining) |
| **Cognitive Load** | 5/10 | Moderate-high cognitive load: review original decision, assess if moderator applied policy correctly, consider user's appeal argument, weigh precedent vs. edge case |
| **Risk of Error** | 4/10 | High risk: False negative (uphold wrong decision) = user loses trust, may leave platform. False positive (overturn correct decision) = undermine moderator confidence |
| **Reversibility** | 5/10 | Partially reversible: can change decision, but user/moderator trust impact is hard to reverse |
| **Consistency** | 5/10 | Moderate consistency: Tom must balance policy consistency vs. edge case flexibility, judgment-dependent |
| **TOTAL** | **39/70** | |

**Delegation Archetype**: ⭐⭐⭐ **Human-Led with Agent Support**

**Rationale**:
- Score 39/70 indicates human-led delegation
- Appeals are inherently human (reviewing human judgment requires human meta-judgment)
- Tom must personally decide (management responsibility, accountability)
- BUT: Context gathering and preparation can be fully automated
- Volume (60/day × 15 min = 15 hrs/day) justifies streamlining effort

**Delegation Design**:
- **Agent role (context preparation - fully automated)**:
  - Retrieve original post content, timestamp, author
  - Retrieve removal reason, moderator who decided, rationale logged
  - Retrieve user's appeal text, appeal timestamp
  - Search similar cases: how were comparable appeals decided?
  - Highlight: What changed since original decision? New information? Moderator error?
  - Present in appeal review card (5 min to review vs. 15 min to gather manually)

- **Human role (Tom - decision-maker)**:
  - Review agent-prepared context (3-5 min)
  - Assess: Was original decision correct? Is appeal valid?
  - Decide: Uphold, overturn (restore post), or partial (warning instead of removal)
  - Notify user + original moderator
  - Time: 8-10 min total (vs. 15-20 min without agent)

**Expected impact**: 
- 60 cases/day × 7 min saved = **7 hrs/day saved**
- Appeals resolved faster → improved user satisfaction
- Tom spends time on judgment, not context gathering

---

### Task Cluster TC-4A: IP Claim Triage and Investigation

**Description**: When sculptor emails claiming copyright on posted miniature photo, investigate claim validity, assess evidence, determine if legitimate sculptor or troll, recommend takedown or no action.

**Volume**: 3-5 per week (~0.7/day)

**Effort**: 30-45 min per case = ~2 hrs/week total

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Codifiability** | 2/10 | Very poorly codifiable: copyright law interpretation, evidence assessment (is sculptor's website authoritative?), commercial license fine print, relationship management (is sculptor a sponsor?) |
| **Data Availability** | 4/10 | Limited: sculptor's email claim, user's post, sculptor's website (external), commercial license text. Much requires manual investigation |
| **Volume** | 1/10 | 3-5/week = very low volume (doesn't justify automation investment) |
| **Cognitive Load** | 1/10 | Very high cognitive load: legal reasoning, copyright assessment, evidence evaluation, relationship management (sculptor may be sponsor or VIP), precedent law |
| **Risk of Error** | 1/10 | Extreme risk: False negative (ignore valid claim) = legal liability, sculptor relationship damage. False positive (wrongly remove user content) = user trust erosion, potential counter-claim |
| **Reversibility** | 2/10 | Very difficult to reverse: legal/reputational damage is hard to undo |
| **Consistency** | 3/10 | Low consistency: requires legal expertise, varies by claim type (copyright vs. trademark), relationship context (known sculptor vs. unknown) |
| **TOTAL** | **14/70** | |

**Delegation Archetype**: ⭐⭐⭐⭐ **Human-Only**

**Rationale**:
- Lowest delegation score across all task clusters (14/70)
- Extremely poorly codifiable (legal reasoning, relationship management)
- Extreme risk (legal liability, sponsor relationships)
- Very low volume (3-5/week) doesn't justify automation investment
- Tom explicitly owns this (management responsibility, legal accountability)

**Delegation Design**:
- **Agent role**: None (human-only task)
- **Potential agent assist (very limited)**: 
  - Auto-triage urgency: "Known sculptor @sculpturedragon (on watchlist)" vs. "Unknown claimant (first-time email)"
  - Extract claim details: sculpture name, alleged copyright, evidence URLs
  - **But decision is 100% Tom**

- **Human role (Tom + Senior Mod)**:
  - Full investigation: sculptor's website, commercial license, user's post, prior relationship
  - Legal reasoning: is claim valid under copyright law?
  - Relationship management: is sculptor a sponsor? High-profile community member?
  - Decision: takedown, no action, or escalate to legal review
  - Time: 30-45 min per case (cannot be reduced meaningfully)

**Why not even minimal agent support?**
- Low volume (3-5/week) means automation investment doesn't pay off
- Legal sensitivity means human must review all evidence directly (no delegation)
- Relationship management requires Tom's personal knowledge (not codifiable)

**Expected impact**: No automation, no time savings. Human-only is appropriate for this task cluster.

---

## Overall Delegation Summary

### Delegation Mix Across All Task Clusters

| Delegation Archetype | # Task Clusters | Cases/Day | % of Volume | Effort (current) | Effort (post-agent) | Savings |
|---------------------|-----------------|-----------|-------------|------------------|---------------------|---------|
| **Fully Agentic** | 4 (TC-1A, 1B, 1C, TC-2A) | 1,010 | 68% | 21 hrs/day | 3.2 hrs/day | 17.8 hrs/day |
| **Agent-Led with Oversight** | 2 (TC-1D, TC-1E) | 280 | 19% | 2.6 hrs/day | 1.9 hrs/day | 0.7 hrs/day |
| **Human-Led with Agent Support** | 3 (TC-2B, 2C, TC-3A) | 250 | 17% | 19.2 hrs/day | 6.3 hrs/day | 12.9 hrs/day |
| **Human-Only** | 2 (TC-2D, TC-4A) | 31 | 2% | 2 hrs/day | 2 hrs/day | 0 hrs/day |
| **TOTAL** | **10** | **~1,500** | **100%** | **44.8 hrs/day** | **13.4 hrs/day** | **31.4 hrs/day (70%)** |

**Note**: Volume doesn't sum perfectly to 1,500 because TC-2A (context gathering) overlaps with other TC-2 tasks.

### Weighted Average Delegation Scores

| Work Stream | Weighted Avg Score | Dominant Archetype | Automation Level |
|-------------|-------------------|-------------------|------------------|
| **Work Stream 1: Routine Spam** | 63.5/70 | Fully Agentic + Agent-Led | 74% fully automated |
| **Work Stream 2: Grey-Zone** | 50.2/70 | Mixed (context automated, judgment human) | 0% decision automation, 67% context automation |
| **Work Stream 3: Appeals** | 39/70 | Human-Led + Support | Context prep automated |
| **Work Stream 4: IP Claims** | 14/70 | Human-Only | No automation |
| **OVERALL** | **58.7/70** | **Agent-Led (trending Fully Agentic on high-volume tasks)** | **68% of volume fully automated, 100% receive agent support** |

---

## Strategic Delegation Principles

### Principle 1: Automate Volume, Preserve Judgment

**What to automate**: High-volume (>100/day), rule-bound, low-risk tasks
- Routine spam (1,080/day, 95% rule-bound, low risk) → Fully Agentic
- Context gathering (360/day, knowledge retrieval, zero decision risk) → Fully Agentic

**What NOT to automate**: Low-volume, judgment-bound, high-risk tasks
- Harsh critique vs. harassment (200/day, poorly codifiable, existential risk) → Human decides
- Cultural interpretation (30/day, requires human cultural reasoning) → Human-Only
- IP claims (0.7/day, legal reasoning, relationship management) → Human-Only

**Result**: Agent handles 68% of volume (high-volume, clear patterns) while human focuses on 32% (high-stakes, nuanced judgment).

---

### Principle 2: Context Automation ≠ Decision Automation

**Key insight**: Agent can automate context gathering (40% of grey-zone effort) WITHOUT automating decisions (30% of grey-zone effort).

**Grey-zone delegation**:
- Agent retrieves: user history, subforum norms, precedents, escalation triggers (2-4 min → 10-20 sec)
- Human decides: critique vs. harassment, commercial legitimacy, cultural interpretation (still 60-90 sec)
- **Total time**: 4-5 min → 1.5-2 min (50-60% reduction) **while maintaining human judgment quality**

**Why this works**:
- Context gathering is codifiable (knowledge retrieval) → high automation suitability
- Judgment is not codifiable (cultural reasoning) → low automation suitability
- Separating these phases allows agent to add value WITHOUT replacing human judgment

---

### Principle 3: Risk-Adjusted Delegation

**Delegation level should match risk of error:**

| Risk Level | Consequence | Delegation Approach | Examples |
|------------|-------------|---------------------|----------|
| **Low Risk** | Easily reversed, minimal impact | Fully Agentic (agent decides alone) | Link farms, bots, gibberish |
| **Moderate Risk** | Reversible but with effort/reputation cost | Agent-Led (agent proposes, human approves) | Off-topic commercial, established member content |
| **High Risk** | Difficult to reverse, trust/reputation impact | Human-Led (human decides, agent supports) | Harsh critique vs. harassment, appeals |
| **Existential Risk** | Irreversible, legal/business liability | Human-Only (no agent decision role) | Cultural interpretation, IP claims, sponsor accounts |

**Tom's constraint**: "False negatives are existential" → any task with existential risk must be human-owned, even if high volume.

---

### Principle 4: Codification as Prerequisite

**Tribal knowledge blocks automation:**

| Blocker | Current State | Required Action | Effort | Impact |
|---------|---------------|-----------------|--------|--------|
| **Subforum norms** | Tribal knowledge (painters invitation rule, historical permissiveness) | Document in structured format, build decision trees | 8-16 hrs | Unblocks TC-2A (context gathering) and TC-1D (off-topic commercial) |
| **Tom's watchlist** | Google Sheet, not shared | Replace with structured database, share with agent | 2-4 hrs | Unblocks TC-2A (escalation triggers) |
| **Precedent cases** | Personal notes, Discord logs | Build centralized case library with semantic search | 16-32 hrs | Unblocks TC-2A (precedent matching) |
| **Established member rules** | "Sarah approves 3-year members, another mod doesn't" | Define thresholds (age >90 days + posts >50) | 1-2 hrs | Reduces TC-1D and TC-2C inconsistency |

**Total codification effort**: 27-54 hrs one-time investment

**Return on investment**: Unlocks 13.5 hrs/day savings on context gathering + 6 hrs/day savings on spam automation = **19.5 hrs/day × 365 days = 7,118 hrs/year** saved from 27-54 hrs investment.

**ROI**: 132:1 to 264:1 (first year), compounding thereafter.

---

### Principle 5: Progressive Delegation (Phased Rollout)

**Don't automate everything at once** - build trust through phased deployment:

#### Phase 1: Prove Safety on Low-Risk Tasks (Weeks 1-4)
**Scope**: TC-1A, TC-1B, TC-1C (link farms, bots, gibberish)
- Fully Agentic delegation, confidence >0.9
- Human sampling: 20% daily audit (calibration phase)
- **Goal**: Prove agent accuracy (>95%) and safety (zero viral false negatives)

**Success criteria**:
- Moderators trust agent spam removal
- False positive rate <5%
- Zero false negatives on clear policy violations
- Tom approves Phase 2 expansion

---

#### Phase 2: Expand to Medium-Risk Tasks (Weeks 5-8)
**Scope**: TC-1D, TC-1E (off-topic commercial, exception handling)
- Agent-Led delegation (agent proposes, human approves)
- Reduce human sampling to 10% (maintenance phase)
- **Goal**: Prove agent can handle context-dependent edge cases with human oversight

**Success criteria**:
- Moderator override rate <10% (agent proposals are mostly correct)
- Time per case reduced from 30 sec to 10-15 sec (agent pre-filters edge cases)
- No increase in user complaints or appeals

---

#### Phase 3: Grey-Zone Context Automation (Weeks 9-12)
**Scope**: TC-2A (context gathering for all grey-zone cases)
- Fully Agentic context retrieval, Human-Led judgment
- Integrate subforum norms database, watchlist, precedent library
- **Goal**: Reduce grey-zone case time from 4-5 min to 1.5-2 min

**Success criteria**:
- Moderators report "agent context is helpful" (survey)
- Context review time <30 sec (vs. 2-4 min manual gathering)
- No decrease in judgment quality (false negative/positive rates unchanged)

**Blockers**: Requires completing codification work (subforum norms, watchlist, precedents) - 27-54 hrs effort in Phase 1-2.

---

#### Phase 4: Appeals and Platform Integration (Weeks 13+)
**Scope**: TC-3A (appeal context prep), streamlined escalation workflows
- Human-Led with Agent Support
- Build appeal review dashboard, integrate Discord escalation
- **Goal**: Reduce Tom's appeal review time from 15-20 min to 8-10 min

**Success criteria**:
- Tom reports appeal context is complete and saves time
- Appeal resolution time reduced 30-40%
- Volunteer moderator satisfaction improved (more time on valued work)

---

#### Never Automate (Permanent Human-Only)
**Scope**: TC-2D (cultural interpretation), TC-4A (IP claims), sponsor account decisions
- These remain 100% human-owned
- Agent may assist with routing (e.g., "escalate Japanese sub posts to Aki") but not decision-making

**Rationale**: Existential risk, legal liability, relationship management, extremely low codifiability.

---

## Validation and Calibration Plan

### Pre-Deployment Validation

Before deploying agent to production, validate delegation suitability scores:

1. **Test dataset creation** (Week 1-2):
   - 1,000 spam cases (300 link farms, 200 bots, 150 gibberish, 250 commercial, 100 exceptions)
   - 500 grey-zone cases (200 harsh critique, 100 commercial, 100 cultural, 100 other)
   - Ground truth labels from human moderators (3 moderators label each case, consensus required)

2. **Agent accuracy benchmarking** (Week 3):
   - Test spam classifier: precision, recall, F1 score by spam type
   - Test exception detection: false positive rate (removing legitimate content)
   - Test grey-zone context gathering: completeness, relevance, accuracy
   - **Pass threshold**: >95% precision on spam, >90% recall, <5% false positive rate

3. **Confidence calibration** (Week 4):
   - Plot agent confidence (0-1) vs. actual accuracy
   - Target: 0.9 confidence → 90%±5% accuracy, 0.7 confidence → 70%±10% accuracy
   - Adjust confidence thresholds based on calibration curve
   - Set escalation threshold: confidence <0.7 → auto-escalate to human

4. **Shadow mode testing** (Week 5-6):
   - Agent runs in parallel with human moderators (doesn't take action, just recommends)
   - Compare agent decisions vs. human decisions on 500 live cases
   - Measure agreement rate, identify disagreement patterns
   - **Pass threshold**: >90% agreement with humans on spam, >80% on context relevance

---

### Post-Deployment Calibration

After deploying to production, continuously calibrate:

1. **Daily sampling audit** (20% in Phase 1, 10% in Phase 2+):
   - Random sample of agent actions reviewed by human
   - Measure: accuracy, false positive/negative rates, confidence calibration
   - Flag drift: if accuracy drops below 90%, pause and recalibrate

2. **Weekly moderator feedback** (survey):
   - "Do you trust agent spam removal?" (1-5 scale)
   - "Is agent context helpful for grey-zone cases?" (1-5 scale)
   - "How many agent decisions did you override this week?" (count)
   - Target: trust >4/5, override rate <10%

3. **Monthly Tom review** (business validation):
   - Appeal rate: has agent increased user complaints?
   - False negative incidents: any viral incidents or sponsor issues?
   - ROI validation: time savings vs. cost, actual vs. projected
   - **Go/no-go decision**: continue to next phase or roll back

4. **Quarterly recalibration**:
   - Retrain classifier on 3 months of production data (agent actions + human overrides)
   - Update confidence thresholds based on drift
   - Refine exception rules based on discovered edge cases
   - Update subforum norms as community culture evolves

---

## Appendix: Delegation Dimension Weights

### Why Equal Weighting?

This matrix uses **equal weighting** (7 dimensions × 10 points = 70 max) for transparency and simplicity. In practice, dimensions could be weighted based on organizational priorities.

### Alternative Weighting Schemes

**Risk-Weighted** (Tom's "false negatives are existential" priority):

| Dimension | Standard Weight | Risk-Weighted |
|-----------|----------------|---------------|
| Codifiability | 1× (10 pts) | 1× (10 pts) |
| Data Availability | 1× (10 pts) | 1× (10 pts) |
| Volume | 1× (10 pts) | 0.5× (5 pts) - less important than safety |
| Cognitive Load | 1× (10 pts) | 1× (10 pts) |
| **Risk of Error** | **1× (10 pts)** | **2× (20 pts)** - double weight |
| **Reversibility** | **1× (10 pts)** | **1.5× (15 pts)** - weight safety |
| Consistency | 1× (10 pts) | 1× (10 pts) |
| **Total** | **70 pts** | **80 pts** |

**Effect**: Harsh critique vs. harassment (TC-2B) score drops from 34/70 (49%) to 32/80 (40%), reinforcing Human-Led classification.

**Volume-Weighted** (efficiency-focused organization):

| Dimension | Standard Weight | Volume-Weighted |
|-----------|----------------|-----------------|
| **Volume** | **1× (10 pts)** | **2× (20 pts)** - prioritize high-volume tasks |
| Codifiability | 1× (10 pts) | 1× (10 pts) |
| Data Availability | 1× (10 pts) | 1× (10 pts) |
| **Cognitive Load** | **1× (10 pts)** | **1.5× (15 pts)** - reward low-effort automation |
| Risk of Error | 1× (10 pts) | 1× (10 pts) |
| Reversibility | 1× (10 pts) | 0.5× (5 pts) - less critical if volume is high |
| Consistency | 1× (10 pts) | 1× (10 pts) |
| **Total** | **70 pts** | **80 pts** |

**Effect**: Link farms (TC-1A) score rises from 69/70 (99%) to 79/80 (99%), reinforcing Fully Agentic classification.

**For MiniBase**: Standard equal weighting is appropriate given Tom's explicit "false negatives are existential" constraint (safety = efficiency in priority).

---

## Document Control

**Version History**:
- v1.0 (2026-04-29): Initial delegation suitability matrix with scoring and archetypes

**Validation Status**:
- Scores based on discovery findings (Sarah interview, cognitive load analysis)
- Pending validation: Tom interview, cross-moderator consistency check, test dataset benchmarking

**Next Steps**:
- Validate scores with Tom (business risk perspective)
- Validate with Aki and Klaus (cross-moderator consistency)
- Build test dataset and benchmark agent accuracy
- Refine scores based on shadow mode results

**Related Documents**:
- `01_Problem_Statement_and_Success_Metrics.md` (Business context)
- `02_Discovery_Phase.md` (Lived work findings)
- `03_Cognitive_Load_Map.md` (Micro-task decomposition)
- `05_Agent_Purpose_Document.md` (Agent design spec - to be created)
- `06_Volume_Value_Analysis.md` (Prioritization matrix - to be created)
