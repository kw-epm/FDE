# Discovery Questions: MiniBase Content Moderation Agent

**Project**: MiniBase Community Content Moderation Agent  
**Purpose**: Critical questions whose answers would materially change the agent design  
**Date**: 2026-04-30  
**Version**: 1.0

---

## How to Use This Document

These are **not generic discovery questions** ("tell me about your typical day"). These are **sharp, design-changing questions** where different answers lead to fundamentally different agent architectures, delegation boundaries, or implementation approaches.

Each question includes:
- **Impact severity**: 🔴 Critical (blocks Phase 1-2) | 🟡 High (changes architecture) | 🟢 Medium (changes scope/effort)
- **What changes**: Specific design decisions affected by the answer
- **Decision tree**: How different answers lead to different paths

**Instructions for asking**:
1. Ask Tom (Community Manager) these questions during discovery interviews (Week 1-2)
2. Do NOT ask all at once (interview fatigue) - prioritize 🔴 Critical questions first
3. For each answer, document: answer + confidence level (low/medium/high) + follow-up questions surfaced
4. Use answers to update Agent Purpose Document, System Inventory, and implementation plan

---

## Category 1: Risk Tolerance & Safety Thresholds

### Q1: What exactly happened in the "2024 sponsor incident"?

**Impact Severity**: 🔴 **CRITICAL** - Blocks Phase 1 design

**Current State**: Artefacts reference "2024 sponsor incident" multiple times, noting @vortex_minis is "THE 2024 SPONSOR — never get this wrong." We don't know what actually happened.

**Why This Matters**:
- If incident was: "Moderator auto-flagged sponsor commercial post as spam, sponsor threatened to withdraw £50K/year partnership" → Extremely high consequence
  - **Design change**: 100% escalate ALL sponsor posts to Tom, no confidence threshold exceptions
  - **Watchlist priority**: Sponsor accounts are highest-priority escalation (above harassment)
  
- If incident was: "Moderator missed sponsor feedback request, sponsor complained to founder" → Moderate consequence
  - **Design change**: Escalate sponsor posts, but agent can gather context first
  - **Lower priority**: Sponsor escalation is important but not existential

**What Changes**:
- **Escalation rules severity**: How paranoid must we be about sponsor accounts?
- **Watchlist completeness requirements**: Must we audit ALL sponsor accounts, or just @vortex_minis?
- **False positive tolerance**: If sponsor false positive = existential, zero tolerance on sponsor errors
- **Testing requirements**: Must we include sponsor account test cases in Phase 1 validation?

**Follow-up Questions** (if needed):
- Which sponsor was involved? (@vortex_minis or another?)
- What was the exact content that was mishandled?
- What was the financial/relationship consequence?
- Has this happened more than once?
- Are there other sponsors with similar sensitivity?

---

### Q2: How many false positives (wrongly removed legitimate posts) per day are "survivable"?

**Impact Severity**: 🟡 **HIGH** - Changes confidence threshold calibration

**Current State**: Tom says "false positives are survivable; one viral false negative is existential." We've designed for <5% false positive rate (≤40 errors/day at 800 cases/day). Is this acceptable?

**Why This Matters**:
- If Tom's tolerance is: "5-10 per day, we can reverse them" → Current design is fine
  - **Design change**: None - proceed with confidence threshold 0.9 (90% accuracy)
  
- If Tom's tolerance is: "Zero tolerance - every false positive erodes trust" → Must be much more conservative
  - **Design change**: Raise confidence threshold to 0.95 (95% accuracy)
  - **Trade-off**: Lower coverage (60% automation instead of 74%)
  - **Effort impact**: More manual review, less time savings (5 hrs/day instead of 7 hrs/day)
  
- If Tom's tolerance is: "50 per day is fine, we have appeal process" → Can be more aggressive
  - **Design change**: Lower confidence threshold to 0.85 (85% accuracy)
  - **Trade-off**: Higher coverage (85% automation) but more appeals
  - **User experience risk**: Higher appeal volume may overwhelm Tom

**What Changes**:
- **Confidence threshold**: 0.85, 0.9, or 0.95?
- **Coverage target**: 60%, 74%, or 85% automation?
- **Time savings**: 5, 7, or 9 hrs/day?
- **Appeal volume**: Directly proportional to false positive rate
- **Phase 1 success criteria**: What false positive rate triggers rollback?

**How to Ask**:
Present scenario: "In Phase 1, the agent will auto-remove ~800 spam posts/day. At 95% accuracy, that's ~40 false positives per day - legitimate posts wrongly removed. Users can appeal, you reverse within 24 hours. Is 40/day acceptable? What's your ceiling?"

---

### Q3: What's your actual tolerance for moderator override rate?

**Impact Severity**: 🟡 **HIGH** - Changes agent-led vs. fully agentic boundaries

**Current State**: We've designed for <10% moderator override rate (humans reverse ~80 of 800 agent decisions/day). Is this acceptable?

**Why This Matters**:
- If Tom's tolerance is: "10-15% is fine, shows humans are engaged" → Current design is fine
  - **Design change**: None - proceed with fully agentic spam removal
  
- If Tom's tolerance is: "<5% - high overrides mean agent isn't trusted" → Must be more conservative
  - **Design change**: Shift more cases from "fully agentic" to "agent-led with human approval"
  - **Trade-off**: Humans review 200 cases/day (not 80), less time savings (5 hrs/day not 7 hrs/day)
  - **Scope reduction**: Only remove link farms + crypto bots (clear patterns), escalate all commercial spam
  
- If Tom's tolerance is: "20% is fine, as long as pattern improves over time" → Can be more aggressive
  - **Design change**: Include more edge cases in fully agentic bucket
  - **Trade-off**: Higher initial override rate (20% in Week 1), but retraining reduces it to 10% by Month 2

**What Changes**:
- **Delegation boundaries**: What stays fully agentic vs. moves to agent-led?
- **Edge case handling**: Off-topic commercial, established member exceptions - auto-remove or human approve?
- **Retraining frequency**: If high overrides are tolerated short-term, can retrain monthly to improve
- **Volunteer trust building**: Low override rate (5%) builds trust faster, but limits automation value

**How to Ask**:
Present scenario: "In Phase 1, moderators will override ~10-15% of agent decisions (80-120 cases/day). This means the agent got it wrong - maybe removed a tutorial with URLs, or missed cultural context. The agent learns from overrides and improves. Is 10-15% acceptable in the first month? What's your ceiling?"

---

### Q4: Have you tried automation before at MiniBase? What happened?

**Impact Severity**: 🔴 **CRITICAL** - May reveal fatal failure modes we haven't considered

**Current State**: We don't know if MiniBase has attempted moderation automation in the past.

**Why This Matters**:
- If answer is: "Yes, we tried an auto-flagging tool in 2022, it flagged all Japanese posts as spam because of encoding issues, we disabled it after 3 days" → Huge red flag
  - **Design change**: Must explicitly test multi-byte character handling (Japanese, German special chars)
  - **Risk mitigation**: Run Japanese sub posts through separate validation pipeline
  - **Trust building**: Tom will be skeptical of automation - requires longer shadow mode (2 weeks not 1 week)
  
- If answer is: "Yes, we tried Discourse's built-in spam filter, it worked for link farms but missed crypto bots" → Informs baseline
  - **Design change**: Focus agent effort on crypto bot detection (higher value than link farms)
  - **Competitive positioning**: Agent must outperform Discourse built-in (>90% vs. their 70%)
  
- If answer is: "No, this is our first automation attempt" → Clean slate
  - **Design change**: None, but lower trust barrier to overcome
  - **Risk**: No institutional knowledge of what fails - must discover ourselves

**What Changes**:
- **Testing requirements**: What specific failure modes must we test against?
- **Shadow mode duration**: 1 week vs. 2 weeks based on trust level
- **Baseline performance**: What's the bar to beat? (Discourse built-in? Manual-only?)
- **Stakeholder skepticism**: How hard will it be to get buy-in for Phase 2?

**Follow-up Questions** (if needed):
- What tool/approach was tried?
- Why did it fail? (Technical? Trust? Policy mismatch?)
- What did you learn from it?
- Are there lingering concerns from that experience?

---

## Category 2: Operational Reality & Data Quality

### Q5: Walk me through your Google Sheet watchlist. Are ALL accounts you personally review in here, or are some "just in your head"?

**Impact Severity**: 🔴 **CRITICAL** - Watchlist completeness is existential risk

**Current State**: Tom's Google Sheet has 6 entries (from artefacts). Artefact notes include "@vortex_minis" as "THE 2024 SPONSOR." Are there other sponsors not in the sheet?

**Why This Matters**:
- If Tom's answer is: "Yes, the sheet is complete, these are all the accounts I track" → Low risk
  - **Design change**: Migrate sheet → database, no additional discovery needed
  - **Validation**: Tom reviews migrated database, confirms completeness
  
- If Tom's answer is: "The sheet has most of them, but I also just know to escalate accounts like @minipainter_uk, @forge_world_rep, and @sculptors_guild - they're not written down" → High risk
  - **Design change**: URGENT - extended discovery to extract ALL implicit watchlist entries
  - **Process change**: Tom must do brain dump (30-60 min session: "every account you personally review")
  - **Validation**: Run agent on 6 months historical data, flag any sponsor/VIP posts it would have processed, Tom reviews
  - **Ongoing risk**: If Tom's memory is the source of truth, future sponsors may be missed
  
- If Tom's answer is: "The sheet is outdated, I actually use a different tracker now" → Major discovery gap
  - **Design change**: Obtain current tracker, reconcile differences
  - **Risk**: We may have designed against stale data

**What Changes**:
- **Watchlist migration effort**: 4 hrs (simple migration) vs. 16 hrs (extended discovery + brain dump)
- **Phase 1 go-live risk**: Can we go live if watchlist is incomplete? (Answer: NO - existential risk)
- **Validation requirements**: Must dry-run agent on historical data to catch missing watchlist entries
- **Ongoing maintenance**: If watchlist is in Tom's head, need weekly sync process (not monthly)

**How to Ask**:
Present watchlist: "I see your Google Sheet has @vortex_minis, @sculpturedragon, and 4 others. Walk me through every account you personally review before taking action. Are they all in this sheet? If I gave you 100 flagged posts, how many would you recognize by username alone and think 'I need to handle this one'?"

---

### Q6: How often do subforum norms change? When did "no critique without invitation" last change in painters sub?

**Impact Severity**: 🟡 **HIGH** - Determines norm versioning architecture

**Current State**: We're codifying subforum norms in Phase 2. If norms change frequently, our database will become stale.

**Why This Matters**:
- If Tom's answer is: "Subforum norms are stable, painters rule has been the same for 3 years" → Low maintenance
  - **Design change**: Simple norms database, quarterly manual review is sufficient
  - **Effort**: 16 hrs codification, minimal ongoing maintenance
  
- If Tom's answer is: "We adjust norms every 6 months based on community feedback" → High maintenance
  - **Design change**: Must build norm versioning (effective_date, deprecated_date fields)
  - **Process change**: Tom must notify engineer when norms change (integrate into quarterly review cycle)
  - **Risk**: Agent may apply outdated norms between change and database update
  - **Effort**: +8 hrs to build versioning, +2 hrs/quarter ongoing maintenance
  
- If Tom's answer is: "Norms are constantly evolving, we just decided last week to relax painters rule for long-running threads" → Very high churn
  - **Design change**: Reconsider norm codification feasibility - may be too brittle
  - **Fallback**: Agent flags norm-sensitive cases, escalates to human (don't auto-apply norms)
  - **Scope reduction**: Phase 3 grey-zone context may be limited to precedent search only (skip norms)

**What Changes**:
- **Norm versioning architecture**: Simple (current norms only) vs. complex (historical norms with effective dates)
- **Maintenance overhead**: Quarterly review vs. monthly vs. ad-hoc
- **Phase 3 scope**: Full context automation (with norms) vs. limited (precedents only)
- **Risk**: Stale norms cause false positives (remove content under old rule, now allowed under new rule)

**How to Ask**:
"The painters sub has 'no critique without invitation.' When was this rule established? Has it changed since then? How often do subforum norms change - yearly, quarterly, monthly? If the community voted tomorrow to relax this rule, how would you update it, and how would the agent learn the new rule?"

---

### Q7: Do moderators actually consult past moderation cases when deciding grey-zone posts, or do they rely on intuition?

**Impact Severity**: 🟡 **HIGH** - Determines precedent case library priority

**Current State**: We're investing 32 hours to build precedent case library (centralize Discord logs, Google Docs, build semantic search). Is this valuable?

**Why This Matters**:
- If Tom/moderators answer: "Yes, I regularly search Discord #mod-decisions for similar cases, precedents are critical for consistency" → High value
  - **Design change**: Proceed with precedent library as planned
  - **ROI justification**: Precedents save 30-60 sec/case × 360 cases/day = 3-6 hrs/day (worth 32-hour investment)
  
- If Tom/moderators answer: "I occasionally check, but honestly most decisions are gut feel based on experience" → Medium value
  - **Design change**: Deprioritize precedent library to Phase 4 (nice-to-have, not critical)
  - **Effort reallocation**: Use 32 hours for higher-priority work (e.g., better spam classifier, gallery integration)
  - **Scope reduction**: Context card shows user history + subforum norms only (no precedents)
  
- If Tom/moderators answer: "No, I never check past cases, every decision is contextual" → Low/no value
  - **Design change**: Skip precedent library entirely (32 hours saved)
  - **Architecture simplification**: Context aggregation engine is simpler (3 data sources not 4)
  - **Risk**: Miss opportunity for consistency, but don't build unused feature

**What Changes**:
- **Phase 3 scope**: Full context automation (4 data sources) vs. simplified (3 data sources)
- **Effort allocation**: 32 hours invested in precedents vs. reallocated elsewhere
- **Context card design**: Include precedents section vs. omit
- **Consistency improvement**: Precedents drive consistency vs. rely on moderator memory

**How to Ask**:
"When you're reviewing a grey-zone case - harsh critique, ambiguous commercial post - do you search for similar past cases? How often? Where do you look? (Discord, Discourse logs, personal notes?) If the agent showed you 3-5 similar past cases with outcomes, would that be useful or just noise?"

---

### Q8: Is 1,500 flagged posts/day stable year-round, or does it spike seasonally?

**Impact Severity**: 🟢 **MEDIUM** - Changes capacity planning and infrastructure sizing

**Current State**: We've designed for 1,500 flagged posts/day. Volume × Value analysis assumes this is stable.

**Why This Matters**:
- If Tom's answer is: "1,500/day is stable, maybe 1,700 during holiday season (10% variance)" → Low impact
  - **Design change**: None - infrastructure sizing is adequate
  - **Capacity headroom**: 25.6 hrs/day spare capacity handles 10% growth
  
- If Tom's answer is: "1,500 is average, but we get spam attacks 2-3 times/year that spike to 5,000/day" → High impact
  - **Design change**: Must handle 3× surge capacity
  - **Infrastructure**: Discourse rate limit increase critical (200 req/min may not be enough)
  - **Fallback plan**: During spam attack, agent processes top 2,000 (normal queue) + escalates overflow to human
  - **Cost impact**: Surge pricing on Claude API (3× volume = 3× token cost for 1-2 days)
  
- If Tom's answer is: "1,500 is winter baseline, summer drops to 800/day (hobbyist activity is seasonal)" → Moderate impact
  - **Design change**: ROI calculation should use annual average (not 1,500/day constant)
  - **Value adjustment**: Summer months save less time (4 hrs/day not 7 hrs/day)
  - **Infrastructure**: Can size for 1,500/day, will be over-provisioned in summer (acceptable)

**What Changes**:
- **Infrastructure sizing**: Discourse rate limits, database sizing, API call budgets
- **Cost forecasting**: £2,500/year token cost assumes 1,500/day constant (adjust for seasonality)
- **Capacity headroom**: 25.6 hrs/day spare capacity may be inadequate if surge to 5,000/day
- **Fallback procedures**: What happens when agent can't keep up? (Escalate overflow? Pause processing?)

**How to Ask**:
"You mentioned 1,500 flagged posts/day. Is this stable year-round? Are there seasonal patterns (summer/winter)? Have you experienced spam attacks where volume spikes to 3,000-5,000/day? How often?"

---

## Category 3: Stakeholder Priorities & Constraints

### Q9: What would Phase 1 have to demonstrate for you to approve Phase 2?

**Impact Severity**: 🟡 **HIGH** - Defines Phase 1 success criteria and go/no-go decision

**Current State**: We've defined success metrics (95% accuracy, <5% false positive rate, etc.) but we don't know Tom's actual decision criteria.

**Why This Matters**:
- If Tom's answer is: "Zero viral false negatives, and moderators trust it (survey >4/5)" → Focus on safety + trust
  - **Design change**: Phase 1 prioritizes trust-building (longer shadow mode, more sampling, transparent explanations)
  - **Success criteria**: Safety metrics + moderator sentiment survey (not just accuracy numbers)
  - **Risk**: Numerical accuracy (95%) may not be enough if moderators don't trust the agent
  
- If Tom's answer is: "Must save ≥5 hours/day of moderator time, with <10% override rate" → Focus on efficiency + accuracy
  - **Design change**: Phase 1 optimizes for coverage (target 70-80% automation, not conservative 60%)
  - **Success criteria**: Time savings (measured via time-tracking) + override rate
  - **Risk**: If we hit 5 hrs/day savings but moderators feel "rushed," Tom may not approve Phase 2
  
- If Tom's answer is: "Must cost <£5K total (not £14K), with 3:1 ROI minimum" → Focus on cost
  - **Design change**: Scope reduction - cut gallery integration, precedent library (reduce to £8-10K)
  - **Success criteria**: Cost containment + ROI demonstration
  - **Risk**: Over-investing in "nice to have" features that don't meet cost constraint

**What Changes**:
- **Phase 1 priorities**: Safety vs. efficiency vs. cost - can't optimize all three equally
- **Success metrics**: Which metrics are "gate" criteria (must pass) vs. "nice to have"
- **Phase 2 budget**: If Phase 1 costs more than expected, does Tom have budget for Phase 2?
- **Shadow mode duration**: If trust is critical, may need 2 weeks shadow mode (not 1 week)

**How to Ask**:
"Imagine we finish Phase 1 in 4 weeks. The agent is removing spam with 93% accuracy, saving 6 hours/day, and costs £7,000 so far. Moderators are cautiously optimistic (3.8/5 trust score). Do you proceed to Phase 2? What would make you say 'yes, continue' vs. 'no, roll back'? What's the single most important factor?"

---

### Q10: What's your actual budget for this project? Is £14,300 (Phase 1-3) affordable?

**Impact Severity**: 🔴 **CRITICAL** - May require scope reduction or project cancellation

**Current State**: We've estimated £14,300 for Phase 1-3 implementation (224 hrs × £50/hr + £3,500/year operating cost). We don't know if this is within MiniBase's budget.

**Why This Matters**:
- If Tom's answer is: "£14K is fine, I have £20K budget for moderation improvements this year" → Proceed as planned
  - **Design change**: None
  - **Scope**: Full Phase 1-3 implementation (spam + grey-zone context)
  
- If Tom's answer is: "I have £8K budget, £14K is too high" → Major scope reduction required
  - **Design change**: 
    - **Option A**: Phase 1 only (spam automation), defer Phase 2-3 to next year (£6,500)
    - **Option B**: Reduce Phase 3 scope (skip gallery integration, precedent library), cut to £10K
    - **Option C**: Seek additional budget from founder (business case: £183K value for £14K investment)
  - **Value impact**: Phase 1 only delivers £49K/year (not £183K), ROI drops from 16.4:1 to 7.5:1
  
- If Tom's answer is: "I don't have a budget, this was a suggestion from the founder, I need to check" → Project may be at risk
  - **Design change**: Pause implementation until budget approval
  - **Risk**: May lose 4-8 weeks waiting for budget approval (delays Phase 1 go-live)
  - **Mitigation**: Prepare lightweight business case (1-page ROI summary for founder)

**What Changes**:
- **Project scope**: Full (Phase 1-3) vs. reduced (Phase 1 only) vs. on hold
- **Timeline**: 12 weeks vs. 4 weeks vs. TBD
- **Value delivery**: £183K/year vs. £49K/year vs. £0
- **Stakeholder expectations**: If budget is constrained, must reset expectations on deliverables

**How to Ask**:
"Our estimate for Phase 1-3 is £14,300 investment (224 hours of work). This delivers £183K/year value (16:1 ROI). First year payback is 1.1 months. Is this within your budget? If not, what's your budget ceiling? Should we scope to fit, or seek additional budget approval?"

---

### Q11: Are volunteer moderators actually dissatisfied with spending 60% of time on spam, or is that an assumption?

**Impact Severity**: 🟢 **MEDIUM** - Validates problem statement and volunteer satisfaction value

**Current State**: Problem statement assumes volunteers are burned out on spam removal ("volunteers resent repetitive spam work"). Is this true?

**Why This Matters**:
- If volunteer moderators say: "Yes, spam removal is soul-crushing, I want to focus on grey-zone cases" → Validates problem statement
  - **Design change**: None - proceed with automation
  - **Value narrative**: "We're freeing volunteers from drudgery to do meaningful work" resonates
  - **Success metric**: Volunteer satisfaction survey (% time on valued work) is meaningful
  
- If volunteer moderators say: "Spam removal is easy wins, I like the quick dopamine hits, grey-zone cases are stressful" → Contradicts assumption
  - **Design change**: Reconsider value narrative - automation may not improve satisfaction
  - **Risk**: Volunteers may resist automation ("you're taking away the easy parts and leaving the hard parts")
  - **Mitigation**: Reframe as "agent handles boring spam, you focus on impactful decisions" (not "easier work")
  - **Success metric**: Volunteer satisfaction may not improve (or may worsen) - need different KPIs
  
- If volunteer moderators say: "Mixed - some like spam, some hate it" → Segmented problem
  - **Design change**: Allow volunteers to opt-in to agent-assisted workflow (not mandatory)
  - **Process change**: Some volunteers continue manual spam review (if they prefer), others use agent
  - **Complexity**: Two-track moderation workflow (manual + agent-assisted) - increases coordination overhead

**What Changes**:
- **Value narrative**: "Reduce burnout" vs. "increase efficiency" vs. "free choice"
- **Volunteer adoption**: Mandatory vs. optional vs. phased rollout
- **Success metrics**: Volunteer satisfaction vs. time savings (may trade off)
- **Change management**: Resistance vs. enthusiasm

**How to Ask**:
Interview 2-3 volunteer moderators (Sarah, Aki, Klaus): "You spend about 60% of your moderation time removing obvious spam (link farms, bots). How do you feel about this work? Is it tedious, or do you find it satisfying? If an AI handled spam automatically, would that make your volunteer experience better or worse?"

---

## Category 4: Technical Feasibility & Integration

### Q12: Gallery integration - can your Rails dev build API endpoints, or should we plan for workarounds?

**Impact Severity**: 🟡 **HIGH** - Determines Phase 3 scope and effort

**Current State**: Gallery has limited API. We need commercial flag + artist status endpoints. Options: build API (16 hrs), direct DB read (8 hrs, risky), or escalate gallery posts (0 hrs, reduces value).

**Why This Matters**:
- If Tom's answer is: "Yes, our Rails dev (Anna) can build those endpoints, she built the original gallery" → Low risk
  - **Design change**: Proceed with Option A (build API endpoints, 16 hrs)
  - **Timeline**: Week 9-10 (Phase 3)
  - **Value**: Gallery posts automated (50-80/day), saves 2.5-4 hrs/day
  
- If Tom's answer is: "Anna left last month, current dev (João) is new to Rails, this could take 40+ hours" → High risk
  - **Design change**: 
    - **Option 1**: Deprioritize gallery to Phase 4 (defer until João is ramped up)
    - **Option 2**: Use Option C (escalate all gallery posts to human review)
  - **Timeline**: Phase 3 completes without gallery integration
  - **Value reduction**: Lose 2.5-4 hrs/day savings from gallery automation
  - **Scope**: Phase 3 focuses on forum-only (not gallery)
  
- If Tom's answer is: "We're planning a gallery rewrite in 6 months, don't build API for legacy app" → Future-proofing issue
  - **Design change**: Use Option C (escalate gallery posts), revisit in 6 months for new gallery
  - **Architecture**: Build agent to be gallery-agnostic (plug-in model for future gallery API)

**What Changes**:
- **Phase 3 scope**: Forum + gallery vs. forum-only
- **Effort**: 16 hrs (build API) vs. 0 hrs (escalate) vs. 8 hrs (direct DB read)
- **Value**: £108K/year (full) vs. £96K/year (forum-only, lose gallery savings)
- **Timeline**: Phase 3 in 4 weeks vs. 3 weeks (if gallery skipped)
- **Technical debt**: Direct DB read (Option B) creates tight coupling, risky

**How to Ask**:
"The gallery Rails app needs 2 new API endpoints: GET `/api/v1/posts/{id}/commercial_flags` and GET `/api/v1/users/{id}/artist_status`. Can your Rails developer build these? How long would it take? Is the gallery codebase stable, or are you planning a rewrite? If building the API is risky, we can fall back to escalating gallery posts to human review."

---

### Q13: Discourse rate limits - can you request an increase from 60 to 200 requests/minute for the agent API key?

**Impact Severity**: 🟡 **HIGH** - Determines spam attack resilience

**Current State**: Discourse default rate limit is 60 req/min. Agent needs ~5 API calls/post × 1,500 posts/day = ~5 calls/min avg (under limit), but spam attacks could spike to 500 posts in 10 min = 250 calls/min (over limit).

**Why This Matters**:
- If Tom's answer is: "Yes, I'm the Discourse admin, I can increase rate limit to 200/min" → Low risk
  - **Design change**: None - proceed with current architecture
  - **Resilience**: Can handle 3× normal volume (spam attacks survivable)
  
- If Tom's answer is: "I don't have admin access, I'd need to ask our hosting provider (AWS managed Discourse), may take 2 weeks" → Medium risk
  - **Design change**: Must implement priority queue (process critical posts first, defer low-priority)
  - **Fallback**: During spam attack, agent processes high-priority queue (sponsor accounts, high-engagement posts), escalates overflow to human
  - **Timeline**: Phase 1 includes priority queue logic (+8 hrs effort)
  
- If Tom's answer is: "No, Discourse rate limit is fixed by our hosting tier, we can't increase it" → High risk
  - **Design change**: Must implement aggressive caching + request batching
  - **Architecture**: Batch API calls where possible (get 10 user profiles in 1 call, not 10 calls)
  - **Resilience**: During spam attack, agent may fall behind (queue backs up), humans must step in
  - **Risk**: Agent may not deliver promised value during high-volume periods

**What Changes**:
- **Spam attack handling**: Resilient (200 req/min) vs. fragile (60 req/min)
- **Architecture complexity**: Simple vs. priority queue vs. batching + caching
- **Effort**: 0 hrs (rate limit increase) vs. 8 hrs (priority queue) vs. 16 hrs (batching + caching)
- **Risk**: If rate limit can't be increased, agent value is limited during spam attacks

**How to Ask**:
"The agent will make ~5 API calls to Discourse per flagged post. During spam attacks (500 posts in 10 minutes), this could hit rate limits (60 requests/minute). Can you increase the rate limit to 200 req/min for the agent API key? Who has admin access to configure this?"

---

### Q14: Stripe sponsor accounts - are sponsor accounts tagged in Stripe customer metadata, or only in your Google Sheet?

**Impact Severity**: 🟢 **MEDIUM** - Determines Stripe integration necessity (8 hrs)

**Current State**: Assumed sponsor accounts are managed in Tom's watchlist (Google Sheet). Stripe integration was marked "optional" (8 hrs effort).

**Why This Matters**:
- If Tom's answer is: "Sponsor accounts are NOT in Stripe, they're just in my Google Sheet" → Skip Stripe integration
  - **Design change**: Remove Stripe from integration plan (8 hrs saved)
  - **Effort reduction**: Phase 3 is 88 hrs (not 96 hrs)
  - **Watchlist source of truth**: Tom's watchlist (migrated to agent database) is the only sponsor source
  
- If Tom's answer is: "Yes, sponsor accounts have Stripe metadata `sponsor_account: true`, that's the source of truth" → Build Stripe integration
  - **Design change**: Add Stripe integration to Phase 3 (8 hrs)
  - **Watchlist source**: Query Stripe API on user profile retrieval, cache sponsor flag for 24 hours
  - **Reliability**: Stripe is source of truth (more reliable than manual Google Sheet)
  
- If Tom's answer is: "Some sponsors are in Stripe, some are in my Sheet, it's inconsistent" → Risk of missing sponsors
  - **Design change**: Merge both sources (Stripe + watchlist) into agent database
  - **Validation**: Cross-check Stripe vs. watchlist, reconcile differences with Tom
  - **Ongoing**: Which source is updated when new sponsors join? (Process clarity needed)

**What Changes**:
- **Stripe integration**: Build (8 hrs) vs. skip (0 hrs)
- **Watchlist completeness**: Single source (Sheet) vs. dual source (Sheet + Stripe)
- **Effort**: Phase 3 at 88 hrs vs. 96 hrs
- **Reliability**: Manual watchlist (Tom updates) vs. automated Stripe metadata (updated on payment)

**How to Ask**:
"We're planning to migrate your watchlist (Google Sheet) to an agent database. Do sponsor accounts exist anywhere else? Are they tagged in Stripe customer metadata? If not, is your Google Sheet the single source of truth for sponsor accounts?"

---

## Category 5: Assumptions Validation

### Q15: IP claim triage - which sculptors have legitimate claims vs. retaliatory reports?

**Impact Severity**: 🟢 **MEDIUM** - Determines IP claim escalation rules (Phase 4)

**Current State**: Tom's watchlist notes "@sculpturedragon: Tom personally reviews every IP claim" and "@vintage_kitbasher: IP claims credibility unclear." Are there patterns?

**Why This Matters**:
- If Tom's answer is: "90% of IP claims are from 3 sculptors (@sculpturedragon, @forgemaster, @resinworks), they're always legitimate" → Clear pattern
  - **Design change**: Phase 4 IP claim triage - auto-escalate claims from these 3 to Tom (high priority)
  - **Effort**: Simple watchlist rule (1 hr), no complex claim assessment needed
  
- If Tom's answer is: "IP claims are 50/50 - half legitimate, half retaliatory (competitors trying to take down rivals)" → Complex triage needed
  - **Design change**: Phase 4 requires claim credibility assessment (not just sculptor identity)
  - **Triage logic**: Check claimant email domain (sculptors use business emails, trolls use Gmail)
  - **Effort**: More complex (12 hrs for triage logic, not 16 hrs for full automation)
  
- If Tom's answer is: "Every IP claim is unique, I assess case-by-case based on sculptor reputation, evidence quality, upload history" → Not automatable
  - **Design change**: Skip IP claim automation entirely (Phase 4 scope reduction)
  - **Agent role**: Extract claim details from email (claimant, image URL), create case for Tom, no triage
  - **Effort**: 4 hrs (email parsing + case creation) vs. 16 hrs (full triage automation)

**What Changes**:
- **Phase 4 scope**: Full IP claim triage (16 hrs) vs. simple escalation (1 hr) vs. email parsing (4 hrs)
- **Value**: IP claims are low-volume (3-5/week = 0.7/day), automation value is minimal regardless
- **Priority**: Phase 4 is optional anyway - this question helps decide whether to build it at all

**How to Ask**:
"You track IP claims from certain sculptors like @sculpturedragon. Are most IP claims legitimate? Can you spot retaliatory claims by sculptor identity alone, or do you need to review evidence each time? If the agent flagged claims from known-legitimate sculptors as high-priority, would that save time?"

---

### Q16: Precedent case data - can moderators share their personal Google Docs, or is that sensitive?

**Impact Severity**: 🟡 **HIGH** - Determines precedent case data availability (32 hrs effort)

**Current State**: Plan assumes moderators will share personal "moderation notes" Google Docs for precedent extraction. We haven't confirmed.

**Why This Matters**:
- If moderators answer: "Yes, happy to share, they're just work notes" → Proceed with plan
  - **Design change**: None - extract ~500 cases from Google Docs (part of 32-hour precedent library build)
  - **Quality**: Personal docs likely have detailed rationale (high-quality precedents)
  
- If moderators answer: "My notes are personal, I'm not comfortable sharing" → Data source unavailable
  - **Design change**: Rely on Discord logs + Discourse moderation logs only (no Google Docs)
  - **Impact**: Lower precedent quality (Discord logs have sparse rationale)
  - **Quantity**: May only get ~300 cases (not 1,800) - reduces precedent library utility
  - **Fallback**: Precedent library still built, but with lower-quality data (may not be useful)
  
- If moderators answer: "I can share, but I need to redact some entries (user names, personal notes)" → Delayed + reduced data
  - **Design change**: Allow 2 weeks for moderators to redact and share (vs. 1 week)
  - **Timeline**: Phase 3 delayed by 1 week (Week 10 instead of Week 9)
  - **Quality**: Redacted data may lose context (rationale tied to specific users)

**What Changes**:
- **Precedent data availability**: 1,800 cases (full) vs. 300 cases (Discord-only) vs. delayed (redaction time)
- **Precedent quality**: High (detailed rationale) vs. low (sparse Discord logs)
- **Timeline**: Phase 3 on schedule vs. delayed 1 week
- **Value**: High-quality precedents save 3-6 hrs/day, low-quality precedents may save 1-2 hrs/day

**How to Ask**:
Interview volunteer moderators: "We want to build a precedent case library - similar moderation decisions from the past, so the agent can show you 'how we decided this before.' Do you keep personal notes on moderation decisions? If so, would you be willing to share them (anonymized if needed)? Or should we rely on Discord logs + Discourse history only?"

---

### Q17: What does "established member" actually mean? Is it account age, post count, reputation, or something else?

**Impact Severity**: 🟡 **HIGH** - Defines exception detection rules (critical for false positive prevention)

**Current State**: We've assumed "established member" = account age >1 year + post count >50 + no prior violations. Is this Tom's actual definition?

**Why This Matters**:
- If Tom's answer is: "Established is 1 year + 50 posts, that's right" → Proceed with assumption
  - **Design change**: None - exception detection logic is correct
  
- If Tom's answer is: "Established is 3 years minimum, or 1 year + 500 posts, or active contributor (1+ posts/week)" → Different threshold
  - **Design change**: Update exception detection rules to match Tom's actual definition
  - **Impact**: May flag more/fewer users as exceptions (changes coverage rate)
  - **Example**: If threshold is 3 years (not 1 year), fewer users get exception handling → higher automation rate
  
- If Tom's answer is: "It's not about time or numbers, I just know who the community trusts - it's a feeling" → Not codifiable
  - **Design change**: Cannot automate exception detection based on "established member" heuristic
  - **Fallback**: Agent uses objective signals only (account age, post count), escalates borderline cases
  - **Risk**: May miss tribal-knowledge exceptions ("everyone knows @minipainter_jane is trusted"), false positives increase

**What Changes**:
- **Exception detection rules**: Clear thresholds (1 year) vs. complex (3 years + activity) vs. uncodifiable (gut feel)
- **Automation coverage**: Higher threshold = more automation (fewer exceptions), lower threshold = less automation (more exceptions)
- **False positive risk**: If "established" is tribal knowledge, agent can't replicate it (must escalate more)

**How to Ask**:
"When you see a post with spam signals (commercial language, multiple URLs) but you don't remove it because the user is 'established,' what makes them established? Is it account age? Post count? Community contributions? Can you give me specific thresholds, or is it a judgment call?"

---

## Category 6: Future-Proofing & Roadmap

### Q18: If Phase 1-3 succeeds, would you want the agent to expand beyond moderation? (e.g., welcome messages, FAQ responses)

**Impact Severity**: 🟢 **MEDIUM** - Determines architecture extensibility requirements

**Current State**: Agent is designed for moderation only (spam removal, context gathering, escalation). No consideration for other use cases.

**Why This Matters**:
- If Tom's answer is: "Yes, I'd love the agent to send welcome messages to new members, answer common questions, flag popular posts for promotion" → Broader vision
  - **Design change**: Build agent with extensible architecture (plug-in model for future tasks)
  - **Architecture**: Separate core (Discourse API client, context aggregation) from task-specific logic (spam classifier)
  - **Effort**: +8 hrs in Phase 1 to build extensible architecture (vs. moderation-only)
  - **Benefit**: Phase 4+ can add new tasks without refactoring core agent
  
- If Tom's answer is: "No, agent should only do moderation, we have other tools for welcome/FAQ" → Narrow scope
  - **Design change**: Optimize for moderation only (no extensibility overhead)
  - **Architecture**: Tightly coupled spam classifier + context aggregation (simpler, faster)
  - **Effort**: No additional effort (current design is moderation-focused)
  
- If Tom's answer is: "Maybe, but let's not over-engineer - prove moderation works first" → Pragmatic
  - **Design change**: Build for moderation now, refactor for extensibility later if needed
  - **Architecture**: Current design, document extension points for future refactor
  - **Risk**: Future expansion may require refactoring (technical debt)

**What Changes**:
- **Architecture**: Extensible (plug-in model) vs. moderation-specific (tightly coupled)
- **Effort**: +8 hrs (Phase 1) for extensibility vs. 0 hrs (current design)
- **Future cost**: Low refactor cost (extensible) vs. high refactor cost (moderation-only)
- **Scope**: Moderation-only vs. broader "community assistant" vision

**How to Ask**:
"Looking beyond spam removal, if the moderation agent succeeds, are there other tasks you'd want it to handle? New member welcome messages? FAQ responses? Flagging popular posts for social media? Or should it stay focused on moderation only?"

---

## Summary: Question Prioritization

### Week 1 Discovery (Must Ask)
1. ✅ **Q1**: 2024 sponsor incident details (🔴 Critical - shapes escalation rules)
2. ✅ **Q4**: Prior automation attempts (🔴 Critical - reveals failure modes)
3. ✅ **Q5**: Watchlist completeness (🔴 Critical - existential risk if incomplete)
4. ✅ **Q10**: Actual budget (🔴 Critical - may require scope reduction)
5. ✅ **Q2**: False positive tolerance (🟡 High - confidence threshold calibration)
6. ✅ **Q9**: Phase 1 success criteria (🟡 High - defines go/no-go decision)

### Week 2 Discovery (Important)
7. ✅ **Q3**: Override rate tolerance (🟡 High - delegation boundaries)
8. ✅ **Q6**: Subforum norm change frequency (🟡 High - versioning architecture)
9. ✅ **Q7**: Precedent case utility (🟡 High - 32 hrs effort at stake)
10. ✅ **Q12**: Gallery API feasibility (🟡 High - Phase 3 scope)
11. ✅ **Q13**: Discourse rate limit increase (🟡 High - spam attack resilience)
12. ✅ **Q17**: "Established member" definition (🟡 High - exception detection)

### Week 3+ Discovery (Nice to Have)
13. ✅ **Q8**: Volume seasonality (🟢 Medium - capacity planning)
14. ✅ **Q11**: Volunteer satisfaction validation (🟢 Medium - problem validation)
15. ✅ **Q14**: Stripe sponsor account source (🟢 Medium - 8 hrs effort)
16. ✅ **Q15**: IP claim patterns (🟢 Medium - Phase 4 scope)
17. ✅ **Q16**: Precedent data sharing (🟡 High - but Phase 3, can ask later)
18. ✅ **Q18**: Future extensibility vision (🟢 Medium - architecture choice)

---

## Document Control

**Version History**:
- v1.0 (2026-04-30): Initial discovery questions with impact analysis

**Usage Instructions**:
1. Schedule 2-3 discovery sessions with Tom (Week 1-2)
2. Ask 🔴 Critical questions first (block Phase 1 if unanswered)
3. Document answers with confidence level (low/medium/high)
4. Update Agent Purpose Document, System Inventory based on answers
5. Identify follow-up questions surfaced during interviews

**Related Documents**:
- `06_Agent_Purpose_Document.md` (Update based on Q1, Q2, Q3, Q9)
- `07_System_Data_Inventory.md` (Update based on Q5, Q12, Q13, Q14, Q16)
- `05_Volume_Value_Analysis.md` (Update based on Q8, Q10)
- `04_Delegation_Suitability_Matrix.md` (Update based on Q3, Q6, Q17)

**Last Review**: 2026-04-30
