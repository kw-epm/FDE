# Cognitive Load Map: MiniBase Content Moderation

**Project**: MiniBase Community Content Moderation Agent  
**Phase**: ATX Cognitive Work Assessment  
**Date**: 2026-04-29  
**Version**: 1.0

---

## Executive Summary

This document decomposes MiniBase's content moderation work into **Jobs to be Done**, **micro-tasks**, and **cognitive dimensions** following ATX methodology. The analysis reveals:

1. **Routine spam removal** is 95% rule-bound, pattern-matching work with minimal cognitive load - ideal for full automation
2. **Grey-zone case review** has 40% knowledge-retrieval (automatable) and 60% judgment (human-required)
3. **Primary breakpoints** occur at pattern recognition (spam vs. grey) and confidence assessment (decide vs. escalate)
4. **Cognitive zones** show that context-gathering consumes disproportionate time relative to decision value

### Key Findings

| Work Stream | Cognitive Load Distribution | Automation Potential |
|-------------|----------------------------|---------------------|
| **Routine Spam** | 95% rule-bound, 5% exception-handling | ⭐⭐⭐⭐⭐ Very High (70-80% cases) |
| **Grey-Zone Cases** | 40% knowledge-retrieval, 30% rule-application, 30% judgment | ⭐⭐⭐ Medium (context support, not decision) |

**Primary opportunity**: Automate routine spam (save 7 hrs/day) + automate grey-zone context retrieval (save 12-18 hrs/day).

---

## ATX Framework: Jobs to be Done

### What is a "Job to be Done"?

From ATX methodology: A Job to be Done (JtD) is a **cognitive contract** between an actor and an outcome. It's not a task list - it's the complete cognitive work required to achieve a business outcome.

For MiniBase moderation, a JtD includes:
- Understanding **intent** (what is this post trying to do?)
- Validating **context** (who posted it, where, under what norms?)
- Applying **policy** (what rules apply?)
- Choosing a **resolution path** (remove, approve, escalate, warn)
- Communicating a **decision** (to user, to moderators, to logs)

### The Four Moderation Jobs

| Job to be Done | Business Outcome | Volume (daily) | Cognitive Profile |
|----------------|------------------|----------------|-------------------|
| **JtD-1: Remove obvious spam** | Keep platform clean of commercial spam, bots, off-topic ads | 1,080 | Rule-bound pattern matching |
| **JtD-2: Assess grey-zone content** | Balance community discourse vs. harmful content | 360 | Judgment + context integration |
| **JtD-3: Resolve user appeals** | Restore trust after moderation errors, uphold fair decisions | 60 | Review + justification reasoning |
| **JtD-4: Adjudicate IP claims** | Protect sculptors' rights, avoid legal liability | 3-5/week | Legal reasoning + relationship management |

This document focuses on **JtD-1** (routine spam) and **JtD-2** (grey-zone cases) as they represent 96% of daily volume and are the primary targets for agent design.

---

## Work Stream 1: Routine Spam Removal

### Job to be Done: Remove Obvious Spam

**Business outcome**: Keep the MiniBase platform clean of commercial spam, bots, gibberish, and off-topic advertisements that provide no community value and erode user experience.

**Success criteria**:
- Spam is removed within 5 minutes of posting (vs. 15-30 min current)
- False positive rate <5% (don't remove legitimate content)
- False negative rate <10% (catch most spam)
- Zero moderator time wasted on obvious spam

**Cognitive contract**: Given a flagged post, determine if it matches clear spam patterns, and if so, remove it with appropriate rationale logged for audit and user appeal.

---

### Micro-Task Decomposition

#### Task 1.1: Access Flagged Post

**What happens**: Moderator opens moderation queue, clicks on flagged post

**Actions**:
- Navigate to Discourse moderation queue
- Sort by flag count or chronological order
- Click into post to view full content

**Cognitive demand**: None (mechanical navigation)

**Time**: 5 seconds

**Tools**: Discourse web interface

**Breakpoint**: None

**Automation potential**: ⭐⭐⭐⭐⭐ Full - agent can poll queue automatically

---

#### Task 1.2: Quick Visual Scan

**What happens**: Moderator performs 2-second visual pattern match

**Actions**:
- Scan post for visual spam signals:
  - Multiple URLs (link density)
  - Username pattern (brand name + numbers, "official", gibberish)
  - Post length (very short or copy-paste walls of text)
  - Language/character set (random characters, non-English in English sub)

**Cognitive demand**: Very Low - instant pattern recognition, no reasoning required

**Cognitive dimension**: **Rule-bound** - "If 3+ URLs AND new account AND generic text THEN spam"

**Time**: 2 seconds

**Decision**: Is this spam pattern obvious?
- **Yes** → Proceed to Task 1.3 (confirm and remove)
- **No** → Exit to Work Stream 2 (grey-zone assessment)

**Breakpoint**: ⚠️ **BREAKPOINT 1A: Pattern Recognition** - "Is this spam or not?"

**Success rate** (from discovery): 99% accurate on obvious spam

**Tools**: Human visual cortex, pattern matching

**Automation potential**: ⭐⭐⭐⭐⭐ Very High
- Text analysis: URL count, character distribution, language detection
- Account analysis: age, post count, username pattern matching
- Confidence scoring: combine signals into 0-1 spam probability

---

#### Task 1.3: Confirm Spam Type

**What happens**: Moderator categorizes the spam type for logging and consistency

**Spam categories** (from discovery):

| Type | Signals | Prevalence | Confidence |
|------|---------|------------|-----------|
| **Link farm** | 3+ URLs, minimal text, new account, brand username | ~300/day | 99% |
| **Crypto/forex bot** | Formulaic text ("I was struggling until..."), multi-post, bot username | ~200/day | 99% |
| **Gibberish** | Random characters, no semantic meaning, often has URLs | ~150/day | 100% |
| **Off-topic commercial** | Sales language, wrong subforum (e.g., "Buy 3D prints" in painters sub) | ~250/day | 95% |
| **Duplicate post** | Same content posted multiple times across subforums | ~100/day | 100% |
| **Miscategorized** | Legitimate post in wrong subforum (not spam, just misplaced) | ~80/day | 90% |

**Cognitive demand**: Very Low - pattern already recognized, just labeling

**Cognitive dimension**: **Rule-bound** - classification taxonomy

**Time**: 3-5 seconds

**Tools**: Mental spam taxonomy, Discourse removal reason dropdown

**Breakpoint**: None (mechanical)

**Automation potential**: ⭐⭐⭐⭐⭐ Full - classifier can output spam type with confidence

---

#### Task 1.4: Check for False Positive Signals

**What happens**: Quick sanity check - could this be legitimate despite spam signals?

**False positive scenarios** (from discovery):
- Established member (3+ years) sharing relevant links with commentary
- Tutorial post with multiple reference URLs in educational subforum
- Artist sharing portfolio links in gallery (legitimate self-promotion)
- Multi-lingual user whose English reads as "gibberish" but has semantic meaning in their language

**Actions**:
- Check account age (quick glance at profile)
- Check post context (subforum, thread topic)
- Check if post has positive engagement already (reactions, replies)

**Cognitive demand**: Low - simple rule checks

**Cognitive dimension**: **Exception-bound** - "Are there signals this is NOT spam despite pattern match?"

**Time**: 5-10 seconds (if any doubt), 0 seconds (if obviously spam)

**Decision**: Any false positive signals?
- **No** → Proceed to Task 1.5 (remove)
- **Yes** → Exit to Work Stream 2 (grey-zone assessment)

**Breakpoint**: ⚠️ **BREAKPOINT 1B: Exception Detection** - "Could this be legitimate?"

**Success rate**: 99% (1% false positives, per Sarah)

**Tools**: Discourse user profile, post metadata

**Automation potential**: ⭐⭐⭐⭐ High
- Account age check: trivial
- Engagement signals: reaction count, reply count
- Subforum context: legitimate self-promotion in gallery vs. spam in painters
- BUT: "Reads as gibberish but has meaning" requires nuanced language understanding (potential blind spot)

---

#### Task 1.5: Remove Post

**What happens**: Moderator clicks "Remove" and selects reason

**Actions**:
- Click "Remove Post" button in Discourse
- Select removal reason from dropdown:
  - Spam - Link farm
  - Spam - Bot
  - Spam - Off-topic commercial
  - Spam - Gibberish
- (Optional) Add moderator note for audit trail

**Cognitive demand**: None (mechanical)

**Time**: 5 seconds

**Tools**: Discourse moderation interface

**Breakpoint**: None

**Automation potential**: ⭐⭐⭐⭐⭐ Full - API call to remove post with reason code

---

#### Task 1.6: (Edge Case) Redirect User

**What happens**: For off-topic commercial or miscategorized posts, optionally message user with correct subforum

**Actions**:
- Send user message: "Your post about [topic] was removed from [subforum] because it belongs in [correct subforum]. Please repost there."

**Cognitive demand**: Low - template message with fill-in-blanks

**Cognitive dimension**: **Knowledge-bound** - know the subforum taxonomy and rules

**Time**: 20-30 seconds (if done)

**Frequency**: ~20% of off-topic removals (estimated, not all get redirects)

**Breakpoint**: Minor - decide if worth messaging user

**Tools**: Discourse messaging, subforum taxonomy knowledge

**Automation potential**: ⭐⭐⭐⭐ High - template messages with subforum lookup

---

#### Task 1.7: Log Decision

**What happens**: Action is logged in Discourse moderation log

**Actions**:
- Discourse automatically logs: timestamp, moderator, action, reason
- (If done manually) Moderator might add note to personal Google Doc for edge cases

**Cognitive demand**: None (automatic) or Low (manual note-taking)

**Time**: 0 seconds (automatic) or 10-20 seconds (manual notes)

**Breakpoint**: None

**Automation potential**: ⭐⭐⭐⭐⭐ Full - structured logging with JSON schema

---

### Cognitive Zones: Routine Spam Removal

**ATX concept**: Cognitive zones are phases within a JtD where mental effort concentrates.

| Zone | Tasks | Effort Distribution | Cognitive Demand | Automation Potential |
|------|-------|---------------------|------------------|----------------------|
| **Navigation** | 1.1 (Access post) | 5% | None | ⭐⭐⭐⭐⭐ |
| **Pattern Recognition** | 1.2 (Quick scan), 1.3 (Confirm type) | 10% | Very Low | ⭐⭐⭐⭐⭐ |
| **Exception Checking** | 1.4 (False positive check) | 15% | Low | ⭐⭐⭐⭐ |
| **Execution** | 1.5 (Remove), 1.6 (Redirect), 1.7 (Log) | 70% | None | ⭐⭐⭐⭐⭐ |

**Key insight**: 85% of effort is in navigation and execution (zero cognitive demand), 10% is pattern recognition (trivial for humans, easy for ML), 5% is exception checking (requires light context).

**The bottleneck is mechanical clicking, not thinking.**

---

### Breakpoints: Routine Spam Removal

**ATX concept**: Breakpoints are moments where work stops flowing and requires a decision.

#### Breakpoint 1A: Pattern Recognition
**Location**: Task 1.2 (Quick visual scan)

**Question**: "Is this spam or grey-zone?"

**Decision tree**:
```
IF (3+ URLs OR gibberish text OR bot username OR crypto pattern)
  AND (new account OR low post count)
  AND (off-topic subforum OR generic text)
THEN → Spam (proceed to 1.3)
ELSE → Grey-zone (exit to Work Stream 2)
```

**Resolution time**: 2 seconds for spam, 0 seconds for obvious non-spam

**Cognitive demand**: Very Low (instant pattern match)

**Failure mode**: 1% false positives (remove legitimate post with spam-like features)

**Current cost**: 1% × 1,080 cases/day = ~11 false positives/day, user appeals → Tom reverses

**Automation approach**:
- Train classifier on spam patterns (URLs, text structure, account signals)
- Confidence threshold: >0.9 → spam, <0.7 → grey-zone, 0.7-0.9 → human review
- Human sampling: 10-20% daily audit to calibrate

---

#### Breakpoint 1B: Exception Detection
**Location**: Task 1.4 (False positive check)

**Question**: "Could this be legitimate despite spam signals?"

**Exception scenarios**:
1. Established member (3+ years) → check account age
2. Educational content (tutorials with reference URLs) → check subforum + content
3. Gallery self-promotion (legitimate in gallery, spam elsewhere) → check subforum rules
4. High engagement (positive reactions) → check reaction count

**Decision tree**:
```
IF (account age > 3 years)
  OR (subforum = gallery AND self-promotion)
  OR (reactions > 5 AND positive)
THEN → Grey-zone (escalate to human)
ELSE → Spam (proceed to 1.5)
```

**Resolution time**: 5-10 seconds

**Cognitive demand**: Low (simple rule checks)

**Failure mode**: Miss exceptions, remove legitimate content from established members

**Current cost**: Rare (Sarah: "maybe 3 times in 3 years"), but high community impact when it happens

**Automation approach**:
- Explicit exception rules in agent logic
- Escalate when account age > 1 year AND spam pattern detected
- Escalate when subforum = gallery AND commercial content (let human judge legitimacy)

---

### Cognitive Dimensions: Routine Spam Removal

**ATX concept**: Cognitive work is distributed across three dimensions:

#### Rule-Bound Work (95%)
**Definition**: Work governed by explicit, codifiable rules

**Tasks**:
- Pattern matching (3+ URLs, new account, bot username)
- Spam type classification (link farm, crypto bot, gibberish)
- Removal execution (click button, log reason)

**Characteristics**:
- Deterministic (same input → same output)
- No ambiguity or judgment required
- Humans execute perfectly with zero cognitive load
- Machines can match or exceed human performance

**Automation suitability**: ⭐⭐⭐⭐⭐ Ideal for full automation

---

#### Exception-Bound Work (5%)
**Definition**: Work that handles cases that don't fit the standard rule

**Tasks**:
- Checking for false positive signals (established member, educational content)
- Gallery self-promotion (legitimate vs. spam)
- Multi-lingual content that reads as gibberish

**Characteristics**:
- Context-dependent (need account history, subforum rules)
- Low frequency (5% of spam cases, ~50/day)
- Humans use heuristics ("3+ years = trusted member")
- Requires knowledge of subforum norms and platform culture

**Automation suitability**: ⭐⭐⭐⭐ High with explicit exception rules + escalation fallback

---

#### Knowledge-Bound Work (<1%)
**Definition**: Work requiring domain expertise or tribal knowledge

**Tasks**:
- Knowing gallery allows self-promotion but painters sub doesn't
- Recognizing established sculptors vs. unknown users

**Characteristics**:
- Rare in spam removal (mostly in grey-zone cases)
- Requires codified knowledge base (subforum rules, user reputation)
- Can be automated IF knowledge is externalized and structured

**Automation suitability**: ⭐⭐⭐ Medium - requires building knowledge base first

---

### Time & Effort Analysis: Routine Spam Removal

**Per-case breakdown**:

| Task | Time (avg) | Cognitive Load | Bottleneck? |
|------|-----------|----------------|-------------|
| 1.1 Access post | 5 sec | None | Tool navigation |
| 1.2 Quick scan | 2 sec | Very Low | Human pattern matching |
| 1.3 Confirm type | 3-5 sec | Very Low | Mental categorization |
| 1.4 Exception check | 5-10 sec | Low | Context lookup |
| 1.5 Remove | 5 sec | None | UI clicking |
| 1.6 Redirect (optional) | 20-30 sec | Low | Template messaging |
| 1.7 Log | 0 sec (auto) | None | System automatic |
| **Total** | **20-35 sec** | **Very Low** | **Mechanical execution** |

**Workload**:
- 1,080 cases/day × 30 sec avg = **32,400 seconds = 9 hours/day**
- Distributed across 10 moderators (8 volunteers + 2 paid staff)
- Each moderator spends ~1 hour/day on spam removal

**The problem**: High-volume, low-value work consuming 20% of total moderation capacity.

**Automation impact**:
- Agent handles 800 cases/day (74% coverage)
- Time saved: 800 × 30 sec = 24,000 sec = **6.7 hours/day**
- Remaining 280 cases (26%) escalated to human review
- Human sampling: 10% of agent actions (80 cases/day × 30 sec = 40 min/day)
- **Net savings: 6.7 - 0.67 = 6 hours/day**

---

### Delegation Architecture: Routine Spam Removal

Based on cognitive load analysis, recommended delegation:

#### Fully Agentic (Agent Decides Alone)
**Coverage**: 70-80% of spam cases (~800/day)

**Conditions**:
- Clear spam pattern match (link farm, crypto bot, gibberish)
- Confidence score >0.9
- No exception signals (new account, no engagement, off-topic subforum)
- Not a sponsor account (auto-escalate all sponsors)

**Agent actions**:
- Auto-remove post
- Log rationale, confidence score, spam type
- Notify user with template message (appeal option)
- Flag for human sampling (daily audit)

**Human role**:
- Daily audit: 10% random sample (80 cases)
- User appeals: review within 24 hours
- Calibration: adjust confidence threshold based on false positive rate

---

#### Agent-Led with Human Approval
**Coverage**: 20-30% of spam cases (~200/day)

**Conditions**:
- Spam pattern match BUT with exception signals:
  - Account age >1 year
  - Positive engagement (reactions >5)
  - Gallery subforum (self-promotion ambiguity)
  - Confidence 0.7-0.9 (uncertain)

**Agent actions**:
- Flag for human review
- Provide context: spam signals, exception signals, confidence score
- Recommend action: "Likely spam (0.8 confidence) but user has 2-year history - review?"

**Human role**:
- Quick review (30 sec per case with agent-provided context)
- Decide: remove as spam, approve as legitimate, or escalate to grey-zone review
- Total time: 200 × 30 sec = 100 min/day = **1.7 hours/day**

---

#### Summary: Routine Spam Delegation

| Delegation Level | Coverage | Current Effort | Post-Agent Effort | Savings |
|------------------|----------|----------------|-------------------|---------|
| Fully Agentic (agent auto-removes) | 74% | 6.7 hrs/day | 0.67 hrs/day (sampling) | 6 hrs/day |
| Agent-Led (human approves) | 20% | 1.8 hrs/day | 1.7 hrs/day | 0.1 hrs/day |
| Human-Only (edge cases) | 6% | 0.5 hrs/day | 0.5 hrs/day | 0 hrs/day |
| **Total** | **100%** | **9 hrs/day** | **2.9 hrs/day** | **6.1 hrs/day (68%)** |

**Key insight**: Even with conservative 74% automation (high confidence threshold), we save 6+ hours/day. The remaining 2.9 hours includes human oversight (sampling, appeals, exceptions) which is necessary for trust and calibration.

---

## Work Stream 2: Grey-Zone Case Review

### Job to be Done: Assess Ambiguous Content

**Business outcome**: Balance community discourse (allow legitimate harsh critique, self-promotion, cultural expression) against harmful content (harassment, hate speech, norm violations) while preserving community trust and platform safety.

**Success criteria**:
- False negative rate <0.1% (don't miss genuine harassment)
- False positive rate <5% (don't remove legitimate community discourse)
- Decision time <2 minutes per case (vs. 4-5 min current)
- Consistent application of subforum-specific norms
- Moderator confidence in decisions (reduced escalation uncertainty)

**Cognitive contract**: Given an ambiguous flagged post, gather context (user history, subforum norms, precedents), assess whether it violates policy or norms, and decide to approve, remove, warn, or escalate - with rationale that withstands appeal scrutiny.

---

### Micro-Task Decomposition

#### Task 2.1: Recognize Grey-Zone Pattern

**What happens**: Moderator recognizes this is NOT obvious spam, requires investigation

**Triggers**:
- Post has substantive content (not gibberish, not pure link spam)
- Flagged as "harassment", "off-topic", "commercial", or "other"
- Post is from established account (1+ year) OR in sensitive subforum
- Ambiguous language (harsh critique, sarcasm, cultural phrasing)

**Cognitive demand**: Low - pattern recognition (opposite of spam signals)

**Cognitive dimension**: **Rule-bound** - "If NOT spam pattern AND flagged THEN grey-zone"

**Time**: 5 seconds

**Tools**: Quick mental categorization

**Breakpoint**: ⚠️ **BREAKPOINT 2A: Category Recognition** - "This is grey, not spam"

**Automation potential**: ⭐⭐⭐⭐⭐ High - inverse of spam classifier (low spam confidence → grey-zone)

---

#### Task 2.2: Assess Flag Severity

**What happens**: Moderator checks flag count and flagging reasons to prioritize

**Actions**:
- Check flag count (≥6 = urgent, 4-5 = standard, 1-3 = low priority)
- Read flagging reasons: "harassment", "off-topic", "commercial", "other" (custom text)
- Scan user-submitted flag text if provided

**Cognitive demand**: Low - reading and prioritization

**Cognitive dimension**: **Knowledge-bound** - understand what flag reasons mean in practice

**Time**: 10-15 seconds

**Tools**: Discourse flag interface

**Breakpoint**: Minor - decide if urgent or can wait

**Automation potential**: ⭐⭐⭐⭐⭐ Full - parse flag metadata, prioritize by count + severity

---

#### Task 2.3: Read Post Content (Full Context)

**What happens**: Moderator reads the flagged post carefully, including thread context

**Actions**:
- Read full post content (not just quick scan)
- Read thread title (look for invitation signals: "feedback wanted?", "tips?", "critique?")
- Read 1-2 preceding posts in thread (conversation context)
- Read 1-2 replies to flagged post (OP reaction, community response)

**Cognitive demand**: Low-Medium - reading comprehension, context absorption

**Cognitive dimension**: **Knowledge-bound** - understand content, detect tone, identify targets (work vs. person)

**Time**: 30-45 seconds

**Tools**: Discourse thread view, human reading comprehension

**Breakpoint**: None (continuous reading)

**Automation potential**: ⭐⭐⭐ Medium
- LLM can read and summarize content
- Can extract: tone, targets, constructive elements
- BUT: Sarcasm, cultural context, intent detection is hard

---

#### Task 2.4: Check User History

**What happens**: Moderator opens user profile, scans post history for reputation and pattern

**Actions**:
- Open user profile in new tab
- Check account age (created date)
- Check post count (activity level)
- Scan recent posts (last 10-20) for:
  - Quality (helpful contributions vs. trolling)
  - Prior moderation actions (warnings, removals)
  - Behavior pattern (constructive vs. antagonistic)

**Cognitive demand**: Medium - pattern recognition across multiple posts, reputation assessment

**Cognitive dimension**: **Knowledge-bound** - understand platform norms for "good member" vs. "troll"

**Time**: 30-60 seconds

**Tools**: Discourse user profile, post history view

**Breakpoint**: ⚠️ **BREAKPOINT 2B: Reputation Assessment** - "Is this user trustworthy or problematic?"

**Automation potential**: ⭐⭐⭐⭐ High
- Account age, post count: trivial
- Sentiment analysis on post history: doable
- Prior moderation actions: structured data
- Aggregate reputation score: feasible (similar to Reddit karma)

---

#### Task 2.5: Check Subforum-Specific Norms

**What happens**: Moderator recalls or looks up subforum-specific rules that may override global policy

**Actions**:
- Identify subforum (painters, historical, Japanese, gallery, etc.)
- Recall subforum-specific norms:
  - **Painters**: "No critique without invitation" - check thread title for invitation
  - **Historical**: Permissive on historically-charged imagery - assess historical accuracy
  - **Japanese**: English critiques may read harsh - cultural interpretation
  - **Gallery**: Established members can self-promote - check account age
- If uncertain, navigate to subforum pinned rules thread (30-60 sec additional)

**Cognitive demand**: Medium - requires tribal knowledge or rule lookup

**Cognitive dimension**: **Knowledge-bound** - subforum taxonomy and norms (not in global policy!)

**Time**: 20-40 seconds (if recalled), 60-90 seconds (if lookup required)

**Tools**: Tribal knowledge, subforum rules threads, personal notes

**Breakpoint**: ⚠️ **BREAKPOINT 2C: Norm Application** - "Does subforum-specific rule apply?"

**Automation potential**: ⭐⭐⭐⭐ High IF norms are codified
- Subforum-specific rules can be structured as decision trees
- "Invitation detection" can use NLP (search thread title for "tips?", "feedback?", "critique?")
- Historical accuracy assessment: Low (requires human judgment)
- Cultural interpretation: Low (requires human judgment)

**Current blocker**: Norms are tribal knowledge, not documented. **Must be codified first.**

---

#### Task 2.6: Search for Precedents

**What happens**: Moderator searches personal notes or Discord history for similar past cases

**Actions**:
- Open personal Google Doc, Ctrl+F for keywords (e.g., "harsh critique", "painters invitation")
- Scroll Discord #mod-decisions channel for recent similar cases
- Check if any moderator has posted about this user or similar situation

**Cognitive demand**: Medium - information retrieval, analogy matching

**Cognitive dimension**: **Knowledge-bound** - access to precedent database (currently fragmented)

**Time**: 30-60 seconds (if precedent found), 0 seconds (if moderator remembers similar case)

**Tools**: Google Docs, Discord search, human memory

**Breakpoint**: ⚠️ **BREAKPOINT 2D: Precedent Matching** - "Have we seen this before? How did we decide?"

**Automation potential**: ⭐⭐⭐⭐ High IF precedents are centralized
- Build case library with structured tags (issue type, subforum, outcome)
- Semantic search: find similar cases by content similarity
- Surface precedents automatically during grey-zone review

**Current blocker**: Precedents are siloed (personal notes, Discord logs, not shared/structured)

---

#### Task 2.7: Check for High-Risk Signals

**What happens**: Moderator checks for signals that escalate risk (sponsor accounts, high engagement, watchlist users)

**Actions**:
- Check if user has "Sponsor" badge (100% escalate to Tom)
- Check post engagement (reaction count, reply count)
  - If >20 reactions → high community engagement → escalate (CYA)
- Recall if user is on Tom's watchlist (@sculpturedragon, fraud patterns, prior incidents)
  - Scroll Discord for Tom's recent messages about this user

**Cognitive demand**: Low - checklist of escalation triggers

**Cognitive dimension**: **Rule-bound** - explicit escalation rules (sponsor = escalate)

**Time**: 10-20 seconds

**Tools**: Discourse badges, reaction count, Discord history, human memory

**Breakpoint**: ⚠️ **BREAKPOINT 2E: Escalation Trigger Check** - "Must this go to Tom?"

**Automation potential**: ⭐⭐⭐⭐⭐ Very High
- Sponsor badge: trivial
- Engagement count: trivial
- Watchlist check: High IF watchlist is structured (replace Tom's Google Sheet with DB)

**Current blocker**: Tom's watchlist is not shared with moderators or agent

---

#### Task 2.8: Assess Content Against Policy

**What happens**: Moderator makes the judgment call - does this violate policy or subforum norms?

**Assessment dimensions**:

1. **Harsh critique vs. harassment**:
   - Does it target **work/technique** (critique) or **person/ability** (harassment)?
   - Is it **constructive** (explains what's wrong + how to improve) or **destructive** (just attacks)?
   - Was it **invited** (OP asked for feedback) or **uninvited** (unsolicited critique)?

2. **Commercial content**:
   - Is user established (3+ years, active contributor) or new/low-activity?
   - Is subforum appropriate (gallery = OK, painters = not OK)?
   - Is it contextually relevant (sharing work) or pure advertising?

3. **Cultural interpretation**:
   - Is user from cultural background where direct communication is norm (e.g., Japanese, German)?
   - Could harsh phrasing be translation artifact or cultural difference?
   - Did OP/community react positively (took as helpful) or negatively (felt attacked)?

4. **Historical/sensitive imagery**:
   - Is imagery historically accurate (WWII miniatures with period-accurate markings)?
   - Is context educational/hobbyist or dogwhistle/hate symbol?
   - Is subforum = historical (permissive) or other (strict)?

**Cognitive demand**: **High** - multi-signal integration, judgment, cultural reasoning

**Cognitive dimension**: **Judgment-bound** (30% of grey-zone work) - requires human contextual reasoning

**Time**: 60-90 seconds (after context is gathered)

**Tools**: Human judgment, cultural awareness, pattern recognition

**Breakpoint**: ⚠️ **BREAKPOINT 2F: The Judgment Call** - "Critique or harassment? Legitimate or violation?"

**Automation potential**: ⭐⭐ Low
- LLM can assist with extracting signals (targets work vs. person)
- BUT: Final judgment requires human cultural reasoning and risk tolerance
- Sarah: "That boundary is so cultural, so context-dependent... I think AI would either be too aggressive or too permissive."

**Agent role**: Gather signals, highlight key factors, estimate confidence - but **human decides**.

---

#### Task 2.9: Decide Confidence Level

**What happens**: Moderator assesses their own confidence in the decision they're leaning toward

**Self-assessment**:
- **High confidence (80-100%)**: Clear precedent, obvious norm application, clear signals
  - Example: Uninvited critique in painters sub (clear norm violation)
- **Medium confidence (50-80%)**: Ambiguous signals, precedent unclear, cultural interpretation needed
  - Example: Harsh but accurate critique, OP seems OK with it but 7 flags
- **Low confidence (0-50%)**: Genuinely split 50-50, no precedent, multiple valid interpretations
  - Example: Historical imagery that could be educational or dogwhistle

**Cognitive demand**: Medium - meta-reasoning about own confidence

**Cognitive dimension**: **Judgment-bound** - self-assessment of uncertainty

**Time**: 10-20 seconds

**Decision**: Should I decide or escalate?
- **High confidence** → Proceed to Task 2.10 (take action)
- **Medium confidence** → Check precedents again or ask Discord for second opinion (Task 2.11)
- **Low confidence** → Escalate to Tom/Senior Mod (Task 2.12)

**Breakpoint**: ⚠️ **BREAKPOINT 2G: Confidence Gate** - "Am I sure enough to decide?"

**Automation potential**: ⭐⭐⭐⭐ High for agent self-assessment
- Agent can output confidence score based on signal ambiguity
- Threshold: >0.8 = high confidence (suggest action), 0.5-0.8 = medium (suggest human review), <0.5 = low (auto-escalate)

**Agent advantage**: Agent can quantify confidence objectively; humans use gut feeling (less calibrated)

---

#### Task 2.10: Take Action (High Confidence)

**What happens**: Moderator approves or removes post with logged rationale

**Actions**:
- **If approve**: Close flag as "no action - [rationale]"
  - Example: "No action - invited critique within subforum norms"
- **If remove**: Remove post with reason
  - Example: "Removed - uninvited critique violates painters sub norms"
- **If warn**: Issue warning to user + approve or remove post
  - Example: "Warning - harsh phrasing. Future similar posts will be removed."
- Log rationale in Discourse + (optional) personal notes for precedent

**Cognitive demand**: Low - execution of decision already made

**Time**: 20-30 seconds

**Tools**: Discourse moderation actions, template messages

**Breakpoint**: None

**Automation potential**: ⭐⭐⭐⭐ High - execute action IF decision is made by human or high-confidence agent

---

#### Task 2.11: Ask Discord for Second Opinion (Medium Confidence)

**What happens**: Moderator posts case in Discord #mod-decisions for peer input

**Actions**:
- Screenshot or link to post
- Summarize situation: "Post in painters sub, harsh critique, OP asked for feedback but 7 flags. Within norms or harassment?"
- Wait for responses (10-30 minutes, timezone-dependent)
- Read peer input, reach consensus or escalate if split

**Cognitive demand**: Low (communication) + wait time

**Cognitive dimension**: **Coordination-bound** - distributed decision-making

**Time**: 10 min to post + 10-30 min wait + 5 min to read responses = **25-45 minutes total**

**Frequency**: ~10% of grey-zone cases (~36/day)

**Breakpoint**: ⚠️ **BREAKPOINT 2H: Wait for Consensus** - timezone-dependent delay

**Automation potential**: ⭐⭐⭐ Medium
- Agent can escalate to Discord automatically (post context + question)
- BUT: Human moderators must still respond (can't automate peer judgment)
- Workflow improvement: reduce wait time with notifications, integrate Discord thread into moderation UI

---

#### Task 2.12: Escalate to Tom/Senior Mod (Low Confidence)

**What happens**: Moderator flags case for Tom or Senior Mod to review

**Actions**:
- Flag post in Discourse for Tom's review
- Add note: explain situation, why escalating, what's ambiguous
- Wait for Tom's decision (hours to 1 day)

**Cognitive demand**: Low (communication)

**Time**: 2-3 min to write escalation note + wait for decision

**Frequency**: ~10% of grey-zone cases (~36/day) when no Discord consensus

**Breakpoint**: ⚠️ **BREAKPOINT 2I: Wait for Tom** - longest delay (hours to 1 day)

**Automation potential**: ⭐⭐⭐⭐ High for escalation workflow
- Agent can prepare full context package for Tom (all signals, user history, precedents)
- Reduce Tom's review time from 30 min to 5 min with rich context
- BUT: Tom must still make decision (human judgment required)

---

### Cognitive Zones: Grey-Zone Case Review

| Zone | Tasks | Effort Distribution | Cognitive Demand | Automation Potential |
|------|-------|---------------------|------------------|----------------------|
| **Initial Assessment** | 2.1 (Recognize), 2.2 (Flag severity), 2.3 (Read content) | 15% | Low-Medium | ⭐⭐⭐⭐ |
| **Context Gathering** | 2.4 (User history), 2.5 (Subforum norms), 2.6 (Precedents), 2.7 (Risk signals) | **40%** | Medium | ⭐⭐⭐⭐⭐ **High** |
| **Judgment** | 2.8 (Assess vs. policy), 2.9 (Confidence) | **30%** | High | ⭐⭐ **Low** (human required) |
| **Decision Execution** | 2.10 (Action), 2.11 (Discord), 2.12 (Escalate to Tom) | 15% | Low (+ wait time) | ⭐⭐⭐⭐ |

**Critical insight**: **40% of grey-zone effort is context gathering** (user history, subforum norms, precedents, risk signals) - this is **high-effort, low-judgment** work that can be fully automated.

**The opportunity**: Automate context gathering → reduce 4-5 min per case to 1-2 min → save 12-18 hrs/day across team.

---

### Breakpoints: Grey-Zone Case Review

#### Breakpoint 2A: Category Recognition
**Time**: 5 seconds  
**Question**: "Is this spam or grey-zone?"  
**Resolution**: Pattern match (not spam → grey-zone)  
**Automation**: ⭐⭐⭐⭐⭐ Trivial (inverse spam classifier)

---

#### Breakpoint 2B: Reputation Assessment
**Time**: 30-60 seconds  
**Question**: "Is this user trustworthy or problematic?"  
**Resolution**: Account age + post quality + moderation history → reputation score  
**Automation**: ⭐⭐⭐⭐ High (build reputation scoring system)

---

#### Breakpoint 2C: Norm Application
**Time**: 20-90 seconds  
**Question**: "Does subforum-specific rule apply? (invitation rule, historical permissiveness, etc.)"  
**Resolution**: Match subforum → recall norm → apply to case  
**Automation**: ⭐⭐⭐⭐ High IF norms are codified (currently tribal knowledge)

**Codification requirement**:
- Document subforum-specific norms in structured format
- Build decision trees: "IF painters sub AND critique AND no invitation → norm violation"
- NLP to detect invitation signals in thread titles

---

#### Breakpoint 2D: Precedent Matching
**Time**: 30-60 seconds  
**Question**: "Have we seen this before? How did we decide?"  
**Resolution**: Search personal notes / Discord → find similar case → apply precedent  
**Automation**: ⭐⭐⭐⭐ High IF precedents are centralized and searchable

**Current blocker**: Precedents are siloed in personal Google Docs and Discord logs

**Solution**: Build shared case library with semantic search

---

#### Breakpoint 2E: Escalation Trigger Check
**Time**: 10-20 seconds  
**Question**: "Must this go to Tom? (sponsor, high engagement, watchlist)"  
**Resolution**: Check badges, engagement count, watchlist → escalate if any trigger  
**Automation**: ⭐⭐⭐⭐⭐ Very High (simple rule checks)

**Current blocker**: Tom's watchlist is not shared

**Solution**: Replace Tom's Google Sheet with structured watchlist accessible to agent

---

#### Breakpoint 2F: The Judgment Call
**Time**: 60-90 seconds (after context gathered)  
**Question**: "Critique or harassment? Legitimate or violation?"  
**Resolution**: Multi-signal integration + cultural reasoning + risk assessment  
**Automation**: ⭐⭐ Low - **requires human judgment**

**Why low**: Boundaries are cultural, context-dependent, ambiguous. Sarah doesn't trust AI here.

**Agent role**: Surface signals (targets work/person, constructive/destructive, invited/uninvited), estimate confidence, let human decide.

---

#### Breakpoint 2G: Confidence Gate
**Time**: 10-20 seconds  
**Question**: "Am I sure enough to decide, or should I escalate?"  
**Resolution**: Self-assess confidence → high = decide, medium = ask Discord, low = escalate to Tom  
**Automation**: ⭐⭐⭐⭐ High for agent self-assessment

**Agent advantage**: Can quantify confidence objectively based on signal ambiguity, precedent match strength, etc.

**Human challenge**: Confidence is "gut feeling" (less calibrated, overconfident or underconfident)

---

#### Breakpoint 2H: Wait for Consensus
**Time**: 25-45 minutes  
**Question**: "What do other moderators think?"  
**Resolution**: Post in Discord → wait → read responses → reach consensus or escalate  
**Automation**: ⭐⭐⭐ Medium (can automate posting, can't automate peer judgment)

**Improvement opportunity**: Streamline Discord workflow (notifications, threaded discussions linked to moderation queue)

---

#### Breakpoint 2I: Wait for Tom
**Time**: Hours to 1 day  
**Question**: "What does Tom decide?"  
**Resolution**: Flag to Tom → wait → Tom reviews → Tom decides  
**Automation**: ⭐⭐⭐⭐ High for context preparation (reduce Tom's review time)

**Agent opportunity**: Package full context (all signals, history, precedents) so Tom can decide in 5 min instead of 30 min

---

### Cognitive Dimensions: Grey-Zone Case Review

#### Knowledge-Bound Work (40%)
**Definition**: Work requiring information retrieval and synthesis

**Tasks**:
- Check user history (account age, post quality, moderation history)
- Look up subforum-specific norms (invitation rule, historical permissiveness)
- Search precedents (similar past cases)
- Check watchlist (sponsor accounts, high-risk users)

**Characteristics**:
- High effort (2-3 min per case)
- Low judgment (just retrieving information)
- Fragmented tools (3+ window switches)
- **Prime automation target**

**Automation suitability**: ⭐⭐⭐⭐⭐ Very High
- All information is retrievable from structured data or codified knowledge
- Agent can aggregate context 10x faster than human tool navigation
- Present in single view: "User X, 2-year member, helpful post history, no prior violations. Post in painters sub (invitation rule applies), thread title: 'feedback wanted?' (invitation detected). Similar case: [precedent link], outcome: approved."

---

#### Rule-Bound Work (30%)
**Definition**: Work governed by codifiable rules (if context-dependent)

**Tasks**:
- Apply subforum norms (IF painters sub AND uninvited critique THEN remove)
- Check escalation triggers (IF sponsor badge THEN escalate 100%)
- Assess engagement risk (IF reactions >20 THEN escalate)

**Characteristics**:
- Deterministic given context
- Can be expressed as decision trees or if-then rules
- Requires tribal knowledge to be codified first

**Automation suitability**: ⭐⭐⭐⭐ High IF norms are documented
- **Current blocker**: Subforum norms are tribal knowledge
- **Solution**: Codify norms as structured rules, agent applies them

---

#### Judgment-Bound Work (30%)
**Definition**: Work requiring human contextual reasoning and cultural interpretation

**Tasks**:
- Harsh critique vs. harassment boundary (targets work or person? cultural context? intent?)
- Historical imagery (educational or dogwhistle? context collapse risk?)
- Sarcasm detection (playful banter or actual hostility?)
- OP intent assessment (did they want harsh feedback or feel attacked?)

**Characteristics**:
- Ambiguous, context-dependent, cultural
- Multiple valid interpretations
- High stakes (false negative = harassment persists, false positive = censor legitimate discourse)
- Sarah explicitly doesn't trust AI here

**Automation suitability**: ⭐⭐ Low - **human judgment required**

**Agent role**:
- Surface signals (extracted from content, user history, reactions)
- Estimate confidence based on signal clarity
- Provide recommendation with reasoning ("Likely critique because targets technique, user is established, OP replied positively")
- **But human makes final call**

---

### Time & Effort Analysis: Grey-Zone Case Review

**Per-case breakdown** (current state):

| Task | Time (avg) | Cognitive Load | Automation Potential |
|------|-----------|----------------|----------------------|
| 2.1 Recognize grey-zone | 5 sec | Low | ⭐⭐⭐⭐⭐ |
| 2.2 Assess flag severity | 10-15 sec | Low | ⭐⭐⭐⭐⭐ |
| 2.3 Read post content | 30-45 sec | Medium | ⭐⭐⭐ |
| 2.4 Check user history | 30-60 sec | Medium | ⭐⭐⭐⭐⭐ |
| 2.5 Check subforum norms | 20-90 sec | Medium | ⭐⭐⭐⭐ |
| 2.6 Search precedents | 30-60 sec | Medium | ⭐⭐⭐⭐⭐ |
| 2.7 Check risk signals | 10-20 sec | Low | ⭐⭐⭐⭐⭐ |
| **Context Gathering Subtotal** | **130-230 sec (2-4 min)** | **Medium** | **⭐⭐⭐⭐⭐ Very High** |
| 2.8 Assess vs. policy | 60-90 sec | **High** | ⭐⭐ |
| 2.9 Decide confidence | 10-20 sec | Medium | ⭐⭐⭐⭐ |
| **Judgment Subtotal** | **70-110 sec (1-2 min)** | **High** | **⭐⭐ Low** |
| 2.10 Take action | 20-30 sec | Low | ⭐⭐⭐⭐ |
| **Total (no escalation)** | **220-370 sec (4-6 min)** | **High** | **Mixed** |

**Key insight**: Context gathering (2-4 min, 40% effort) is fully automatable. Judgment (1-2 min, 30% effort) requires human.

---

**With agent context support** (target state):

| Task | Time (with agent) | Time Saved |
|------|-------------------|------------|
| 2.1-2.7 Context gathering | **10-20 sec** (agent presents aggregated context) | **120-210 sec (2-3.5 min)** |
| 2.8-2.9 Judgment | 60-90 sec (human reviews context + decides) | 0 sec (still requires human) |
| 2.10 Action | 20-30 sec | 0 sec |
| **Total** | **90-140 sec (1.5-2.5 min)** | **120-230 sec (2-4 min) per case** |

**Workload impact**:
- 360 grey-zone cases/day across team
- Current: 360 × 5 min avg = **1,800 min = 30 hrs/day**
- With agent: 360 × 2 min avg = **720 min = 12 hrs/day**
- **Savings: 18 hrs/day** (60% reduction in grey-zone effort)

---

### Delegation Architecture: Grey-Zone Case Review

Based on cognitive load analysis, recommended delegation:

#### Agent-Led with Human Approval (100% of grey-zone cases)

**Agent actions**:
1. **Automatic context aggregation** (replaces Tasks 2.4-2.7):
   - Pull user profile: account age, post count, reputation score, prior moderation actions
   - Extract subforum: identify norms that apply (invitation rule, historical permissiveness, etc.)
   - Semantic search precedents: find similar cases with outcomes
   - Check escalation triggers: sponsor badge, watchlist, engagement count, confidence level
   - **Present in single context card**: "User X, 2-year member, 450 posts, reputation 4.2/5, no prior violations. Post in painters sub (invitation rule applies). Thread title: 'any tips?' (invitation detected). Flagged for: harassment (7 flags). Similar case: [link], outcome: approved as invited critique."

2. **Content analysis** (assist with Task 2.8):
   - Extract signals: targets work vs. person, constructive vs. destructive, invited vs. uninvited
   - Sentiment analysis: tone (neutral/harsh/hostile), OP reaction (positive/negative)
   - Estimate confidence: "Likely invited critique (0.75 confidence) - targets technique, invited, user is helpful member"

3. **Recommendation with reasoning**:
   - "Recommend: APPROVE as invited critique within painters sub norms"
   - "Reasoning: Thread title includes 'any tips?' (invitation detected), comment targets technique not person, user has helpful history"
   - "Risk: 7 flags indicate community concern - review carefully"

**Human actions**:
1. **Review context** (30-60 sec):
   - Read agent-prepared context card
   - Skim post content and thread (already surfaced by agent)
   - Check if agent's signal extraction is correct

2. **Make judgment call** (30-60 sec):
   - Agree with agent recommendation? → Approve or remove
   - Disagree? → Override with own reasoning
   - Uncertain? → Escalate to Discord or Tom

3. **Execute decision** (20-30 sec):
   - Click approve/remove
   - Log rationale (can use agent's reasoning or write own)

**Total time**: 80-150 sec (1.5-2.5 min) vs. 4-6 min current = **50-60% time savings**

---

#### Escalation Paths

**Auto-escalate to Tom** (no human moderator review):
- Sponsor accounts (100% - business risk)
- Watchlist users (100% - Tom personally manages)
- Confidence <0.5 (agent genuinely uncertain)

**Escalate to human moderator** (agent prepares context, moderator reviews):
- Confidence 0.5-0.7 (medium uncertainty)
- Engagement >20 reactions (community backlash risk)
- Cultural interpretation needed (Japanese sub, sarcasm, satire)

**Human decides alone** (agent provides context):
- Confidence 0.7-0.9 (moderate confidence, but agent defers to human judgment)
- All grey-zone cases by default (agent never auto-removes grey content)

---

### Summary: Grey-Zone Delegation

| Component | Current Effort | Post-Agent Effort | Savings |
|-----------|----------------|-------------------|---------|
| Context gathering (Tasks 2.4-2.7) | 2-4 min/case = 12-24 hrs/day | 10-20 sec/case = 1-2 hrs/day | **10-22 hrs/day** |
| Judgment (Tasks 2.8-2.9) | 1-2 min/case = 6-12 hrs/day | 1-1.5 min/case = 6-9 hrs/day | **0-3 hrs/day** |
| Execution (Task 2.10) | 20-30 sec/case = 2-3 hrs/day | 20-30 sec/case = 2-3 hrs/day | 0 hrs/day |
| Escalation coordination | 10-30 min wait × 36 cases/day = 6-18 hrs/day wait time | Streamlined but still human consensus needed | TBD (workflow improvement) |
| **Total** | **30 hrs/day** | **12 hrs/day** | **18 hrs/day (60%)** |

**Key insight**: Grey-zone cases will always require human judgment (30% of effort), but context gathering (40% of effort) can be fully automated. Combined with streamlined escalation, we can reduce total effort by 60% while maintaining decision quality.

---

## Cross-Stream Insights

### Combined Automation Impact

| Work Stream | Current Effort | Post-Agent Effort | Savings |
|-------------|----------------|-------------------|---------|
| **Routine spam** | 9 hrs/day | 2.9 hrs/day | **6.1 hrs/day** |
| **Grey-zone cases** | 30 hrs/day | 12 hrs/day | **18 hrs/day** |
| **Total** | **39 hrs/day** | **14.9 hrs/day** | **24.1 hrs/day (62%)** |

**With 47 hrs/day total capacity** (all 4 work streams):
- Current: 39 hrs on spam + grey-zone, 8 hrs on appeals + IP claims
- Post-agent: 14.9 hrs on spam + grey-zone, **32.1 hrs available** for appeals, IP claims, or additional growth

**Growth headroom**: 32.1 / 47 = **68% spare capacity** → can handle 2.5× current volume without adding moderators

---

### The Automation Sweet Spots

**Highest ROI opportunities** (effort reduction per automation complexity):

1. **Routine spam auto-removal** (Work Stream 1, Tasks 1.1-1.7)
   - Effort: 9 hrs/day → 2.9 hrs/day (6.1 hrs saved)
   - Complexity: Low (clear patterns, 99% accuracy achievable)
   - **ROI: Very High** ⭐⭐⭐⭐⭐

2. **Grey-zone context aggregation** (Work Stream 2, Tasks 2.4-2.7)
   - Effort: 12-24 hrs/day → 1-2 hrs/day (10-22 hrs saved)
   - Complexity: Medium (requires codifying norms, building precedent library)
   - **ROI: Very High** ⭐⭐⭐⭐⭐

3. **Escalation trigger detection** (Work Stream 2, Task 2.7)
   - Effort: 10-20 sec per case × 360 = 1-2 hrs/day → automated
   - Complexity: Low (sponsor badge, watchlist, engagement count)
   - **ROI: High** ⭐⭐⭐⭐

4. **Precedent search** (Work Stream 2, Task 2.6)
   - Effort: 30-60 sec per case × 360 = 3-6 hrs/day → 5-10 sec (semantic search)
   - Complexity: Medium (requires centralized case library with semantic search)
   - **ROI: High** ⭐⭐⭐⭐

**Lower ROI** (still valuable but secondary):

5. **User history lookup** (Work Stream 2, Task 2.4)
   - Effort: 30-60 sec per case × 360 = 3-6 hrs/day → 5-10 sec
   - Complexity: Low (structured data in Discourse)
   - **ROI: Medium-High** ⭐⭐⭐⭐

6. **Subforum norm recall** (Work Stream 2, Task 2.5)
   - Effort: 20-90 sec per case × 72 cases/day (20% of grey-zone) = 0.4-1.8 hrs/day → automated
   - Complexity: Medium (requires codifying tribal knowledge first)
   - **ROI: Medium** ⭐⭐⭐

---

### The Irreducible Human Core

**Work that cannot be automated** (even with perfect AI):

1. **Harsh critique vs. harassment judgment** (Work Stream 2, Task 2.8)
   - Why: Cultural boundaries, intent assessment, context collapse risk
   - Sarah's trust level: None ("I think AI would be too aggressive or too permissive")
   - **Delegation**: Human decides, agent surfaces signals

2. **Historical imagery assessment** (Work Stream 2, Task 2.8)
   - Why: Historical accuracy vs. hate symbol distinction, context collapse risk (viral Twitter backlash)
   - **Delegation**: Human decides, agent flags for sensitivity

3. **Sponsor account decisions** (Work Stream 1 & 2, Task 2.7)
   - Why: Business relationship management, revenue risk (2024 incident)
   - **Delegation**: 100% escalate to Tom (human-only)

4. **IP claim adjudication** (Work Stream 4)
   - Why: Legal reasoning, copyright law, sculptor relationship management
   - **Delegation**: Tom + Senior Mod only

**Estimated effort**: 8-10 hrs/day (judgment calls + high-stakes decisions)

**Agent role**: Prepare context, surface signals, estimate confidence - but **don't replace judgment**.

---

## Appendix: Cognitive Load Terminology

### ATX Definitions

**Job to be Done (JtD)**: A cognitive contract between an actor and an outcome. Not a task list, but the complete mental work required to achieve a business goal.

**Micro-task**: Atomic unit of work within a JtD. Should be observable, measurable, and have clear inputs/outputs.

**Cognitive dimension**: How work is bounded:
- **Rule-bound**: Governed by explicit, codifiable rules (IF-THEN logic)
- **Knowledge-bound**: Requires information retrieval and synthesis
- **Exception-bound**: Handles cases that don't fit standard rules
- **Judgment-bound**: Requires contextual reasoning and ambiguity resolution

**Cognitive zone**: Phase within a JtD where mental effort concentrates (e.g., "context gathering" in grey-zone review).

**Breakpoint**: Moment where work stops flowing and requires a decision, pause, or wait.

---

## Document Control

**Version History**:
- v1.0 (2026-04-29): Initial cognitive load mapping for Work Streams 1 & 2

**Next Steps**:
- Map Work Streams 3 & 4 (Appeals, IP Claims) if needed for completeness
- Validate findings with Tom interview
- Use cognitive load map to build Delegation Suitability Matrix (Document 04)

**Related Documents**:
- `01_Problem_Statement_and_Success_Metrics.md` (Business context)
- `02_Discovery_Phase.md` (Lived work findings)
- `04_Delegation_Suitability_Matrix.md` (ATX scoring - to be created)
- `05_Agent_Purpose_Document.md` (Agent design spec - to be created)
