# System & Data Inventory: MiniBase Content Moderation Agent

**Project**: MiniBase Community Content Moderation Agent  
**Phase**: System Integration Assessment & Data Architecture  
**Date**: 2026-04-30  
**Version**: 1.0

---

## Executive Summary

This document maps every system the MiniBase Content Moderation Agent must access, the data it needs from each, integration approaches, gaps, and risks. **This is not hand-waving** - it addresses real technical constraints including limited APIs, manual data sources, and integration risks.

### Integration Complexity Assessment

| System | Availability | Integration Risk | Effort (hrs) | Blocker Status |
|--------|-------------|------------------|-------------|----------------|
| **Discourse Forum** | ✅ Modern REST API | 🟢 Low | 16 hrs | None |
| **In-house Gallery** | ⚠️ Limited API | 🟡 Medium | 32 hrs | API gaps require workarounds |
| **Stripe Billing** | ✅ REST API | 🟢 Low | 8 hrs | None (read-only) |
| **Discord** | ✅ Bot API | 🟢 Low | 12 hrs | None (optional Phase 4) |
| **Tom's Watchlist** | ❌ Google Sheet (manual) | 🟡 Medium | 4 hrs | Migration required |
| **Subforum Norms** | ❌ Tribal knowledge | 🔴 High | 16 hrs | Codification required |
| **Precedent Cases** | ❌ Fragmented (Docs/Discord) | 🔴 High | 32 hrs | Centralization required |
| **Email (IP Claims)** | ⚠️ Gmail/IMAP | 🟡 Medium | 16 hrs | Optional Phase 4 |

**Critical Path Blockers**: Subforum norms codification (16 hrs) and precedent case centralization (32 hrs) must complete before Phase 3 (grey-zone context automation).

**Total Integration Effort**: 136 hours (17 person-days) across all systems.

---

## System 1: Discourse (Forum Platform)

### System Overview

**Type**: Open-source forum platform (self-hosted on AWS)  
**Version**: Discourse 3.1+ (assumed modern version)  
**Hosting**: AWS (us-east-1, assumed - needs confirmation)  
**API Documentation**: https://docs.discourse.org/  
**Authentication**: API keys (admin + read-only tiers)

### What the Agent Needs

| Data Type | Purpose | Update Frequency | Sensitivity |
|-----------|---------|------------------|-------------|
| **Flagged posts** | Moderation queue source | Real-time (poll every 30 sec) | Public content |
| **Post content** | Spam classification, grey-zone analysis | On-demand per flagged post | Public content |
| **Post metadata** | Author, subforum, timestamp, edit history | On-demand | Public metadata |
| **User profiles** | Account age, post count, reputation, badges | On-demand | Public profile data |
| **User post history** | Prior posts, moderation actions, warnings | On-demand (last 20 posts) | Public + moderator-visible |
| **Subforum metadata** | Subforum name, description, category | Cached (daily refresh) | Public |
| **Moderation history** | Prior actions on post/user | On-demand | Moderator-visible only |
| **Flag details** | Who flagged, reasons, timestamps | Real-time with flagged post | Moderator-visible only |
| **Reactions/engagement** | Reaction count, reaction types | On-demand with post | Public |

### API Availability

✅ **Available via REST API**:
- GET `/posts/{id}.json` - Full post details including content, author, metadata
- GET `/posts/{id}/replies.json` - Thread context (preceding/following posts)
- GET `/posts/flags.json` - Moderation queue (flagged posts)
- GET `/users/{username}.json` - User profile, post count, badges
- GET `/users/{username}/summary.json` - User reputation, post history stats
- GET `/user_actions.json?username={username}` - User post history (paginated)
- GET `/categories.json` - Subforum list and metadata
- POST `/posts/{id}/moderate.json` - Remove post, log action
- POST `/users/{username}/notifications.json` - Notify user of action
- GET `/admin/logs/staff_action_logs.json` - Moderation history audit trail

**Rate Limits**: 
- Default: 60 requests/minute per API key (per Discourse docs)
- Burst: 100 requests/minute for 60 seconds
- **Risk**: 1,500 posts/day × 3-5 API calls/post = 4,500-7,500 calls/day = ~5 calls/min avg (well under limit)

**Authentication**:
- Admin API key (write access for post removal, moderation actions)
- Read-only API key (context gathering, user history)
- Recommend separate keys for production vs. development

---

### Integration Approach

**Phase 1-2 (Spam Removal)**:
1. Poll `/posts/flags.json` every 30 seconds for new flagged posts
2. For each flagged post:
   - GET post content + metadata
   - GET user profile (account age, post count)
   - Classify as spam, grey-zone, or escalation
   - If spam (confidence >0.9): POST `/posts/{id}/moderate.json` (remove)
   - Log action to audit trail

**Phase 3 (Grey-Zone Context)**:
1. For grey-zone posts, expand data retrieval:
   - GET `/posts/{id}/replies.json` (thread context)
   - GET `/user_actions.json` (user post history, last 20 posts)
   - GET moderation history (prior warnings, removals)
2. Aggregate into context card (no removal action)

**Caching Strategy**:
- **User profiles**: Cache for 1 hour (same user may have multiple flags in short period)
- **Subforum metadata**: Cache for 24 hours (rarely changes)
- **Post content**: Never cache (freshness required for moderation)

**Error Handling**:
- API timeout (>5 sec): Retry once, then escalate to manual queue
- 429 Rate Limit: Implement exponential backoff (5 sec, 10 sec, 30 sec)
- 404 Post Not Found: Post may have been deleted by another moderator - log and skip
- 401 Auth Error: Alert on-call engineer (broken API key)

---

### Data Gaps and Workarounds

❌ **Gap 1: Subforum-specific norms not in Discourse data**
- **Impact**: Agent cannot apply painters "no critique without invitation" rule without external database
- **Workaround**: Build separate subforum norms database (see System 6)
- **Effort**: 16 hours codification + 8 hours integration

❌ **Gap 2: "Reputation score" is not a native Discourse field**
- **Impact**: Agent Purpose Document assumes reputation scoring (e.g., 4.2/5)
- **Reality**: Discourse has trust levels (0-4) + badges, not a single reputation score
- **Workaround**: Calculate reputation score from:
  - Trust level (weight: 40%)
  - Post count (weight: 20%)
  - Likes received/given ratio (weight: 20%)
  - Days since account creation (weight: 10%)
  - Moderation history (weight: 10% - penalty for warnings)
- **Effort**: 8 hours to build reputation scoring algorithm

❌ **Gap 3: Thread title not included in `/posts/{id}.json` by default**
- **Impact**: Agent cannot detect "invitation signals" in thread titles (e.g., "tips wanted?")
- **Workaround**: Query `/t/{topic_id}.json` (topic endpoint) to get thread title
- **Effort**: 2 hours (minor refactor, adds 1 API call per flagged post)

---

### Integration Risks

🔴 **Risk 1: Rate limit exhaustion under spam attack**
- **Scenario**: Spam bot posts 500 posts in 10 minutes → 500 × 5 API calls = 2,500 calls in 10 min = 250 calls/min (exceeds 60/min limit)
- **Consequence**: Agent throttled, cannot process queue, spam persists
- **Mitigation**: 
  - Request rate limit increase from Discourse admins (increase to 200/min for agent API key)
  - Implement priority queue (sponsor accounts, high-engagement posts processed first)
  - Fallback: If rate limit hit, escalate all new flags to human queue until API recovers
- **Likelihood**: Low (spam attacks are rare, ~2/year per Tom's estimate)

🟡 **Risk 2: Post edited after agent processes but before removal**
- **Scenario**: Agent classifies post as spam (confidence 0.95), queues removal action. User edits post to remove URLs before agent executes removal.
- **Consequence**: Agent removes now-legitimate post (false positive)
- **Mitigation**:
  - Check `edited_at` timestamp before removal (if edited after classification, re-classify)
  - Add 5-second delay between classification and removal (window for user self-correction)
- **Likelihood**: Medium (estimated 1-2/week based on user behavior patterns)

🟡 **Risk 3: Discourse version upgrade breaks API compatibility**
- **Scenario**: MiniBase upgrades Discourse 3.1 → 3.3, API endpoint structure changes
- **Consequence**: Agent API calls fail, moderation stops
- **Mitigation**:
  - Pin Discourse version in agent dependency config
  - Subscribe to Discourse changelog (https://meta.discourse.org/c/release-notes)
  - Implement API health check (daily ping to Discourse, alert if response format changes)
  - Maintain rollback plan (can revert Discourse upgrade if agent breaks)
- **Likelihood**: Low (Discourse maintains backward compatibility, breaking changes are rare)

---

## System 2: In-House Gallery (Rails App)

### System Overview

**Type**: Custom Rails application (legacy, built 2018-2020)  
**Hosting**: AWS (same VPC as Discourse, assumed)  
**API**: Limited - only partial REST API exists  
**Database**: PostgreSQL (direct read access possible but not recommended)  
**Gallery Purpose**: User-uploaded miniature photos, artist profiles, commission marketplace

### What the Agent Needs

| Data Type | Purpose | Update Frequency | Sensitivity |
|-----------|---------|------------------|-------------|
| **Gallery post metadata** | Author, upload date, commercial flags | On-demand | Public |
| **Artist profiles** | Established artist status, commission history | On-demand (cached) | Public |
| **Commercial flags** | Self-promotion tags, commission listings | On-demand | Public |
| **IP claim history** | Prior IP claims on this artist/image | On-demand | Moderator-visible |

### API Availability

⚠️ **Partially Available**:
- GET `/api/v1/gallery/posts/{id}` - Basic post metadata (title, author, upload_date)
- GET `/api/v1/users/{id}` - Artist profile (username, join_date, bio)

❌ **NOT Available via API**:
- Commercial flags (commission listings, self-promotion tags)
- IP claim history (stored in separate admin panel, no API)
- Artist "established status" (no formal definition, needs to be inferred)

---

### Integration Approach

**Phase 1-2 (Spam Removal)**:
- Gallery integration NOT required (spam moderation focuses on forum posts)
- Skip in initial implementation

**Phase 3 (Grey-Zone Context)**:
- **Scenario**: User posts in gallery "Commission slots open!" - is this legitimate self-promotion or spam?
- **Required data**: Is user established artist? Does gallery allow self-promotion?
- **Integration approach**:
  1. **Option A (Recommended)**: Build minimal API endpoints in gallery Rails app
     - GET `/api/v1/posts/{id}/commercial_flags` - Returns commission tags
     - GET `/api/v1/users/{id}/artist_status` - Returns: account_age, commission_count, established: true/false
     - **Effort**: 16 hours (Rails controller + routes + authentication)
  2. **Option B (Workaround)**: Direct database read (read-only replica)
     - Query gallery PostgreSQL directly (SELECT * FROM posts WHERE id=X)
     - **Risk**: Tight coupling to gallery schema, breaks if schema changes
     - **Effort**: 8 hours (SQL queries + connection pooling)
  3. **Option C (Manual fallback)**: Escalate all gallery posts to human review
     - Treat gallery as "out of scope" for agent automation
     - **Impact**: 50-80 gallery posts/day escalated (increases moderator load)

**Recommendation**: Option A (build minimal API). 16 hours investment is justified by:
- 50-80 gallery posts/day × 3 min/case = 2.5-4 hrs/day saved
- Cleaner architecture (no direct DB coupling)
- Reusable for future agent features

---

### Data Gaps and Workarounds

❌ **Gap 1: No "established artist" flag in gallery database**
- **Impact**: Agent cannot distinguish legitimate self-promotion (established artist) from spam (new account commercial post)
- **Workaround**: Define "established artist" rule:
  - Account age >1 year AND commission_count >5 AND no prior commercial flags removed
  - Compute this on-the-fly in API endpoint (cache result for 24 hours)
- **Effort**: 4 hours (rule codification + caching logic)

❌ **Gap 2: IP claim history not in gallery database**
- **Reality**: IP claims tracked in separate admin panel (no database table, CSV exports only)
- **Impact**: Agent cannot check "has this artist had valid IP claims before?"
- **Workaround**: 
  - **Phase 3**: Manually export CSV, load into agent database (one-time migration)
  - **Phase 4**: Build IP claim API endpoint (if prioritized)
- **Effort**: 2 hours (CSV import script) OR 12 hours (build API endpoint)

---

### Integration Risks

🟡 **Risk 1: Gallery API development requires Rails expertise**
- **Challenge**: MiniBase dev team is small (2 developers), Rails app is legacy, original developer left
- **Consequence**: 16-hour API build estimate may expand to 32+ hours if current dev is unfamiliar with Rails codebase
- **Mitigation**: 
  - Assess current dev's Rails proficiency before committing to Option A
  - If proficiency is low, pivot to Option C (escalate gallery posts to human) for Phase 3
  - Revisit API build in Phase 4 when timeline is less constrained
- **Likelihood**: Medium (small team, legacy code risk is real)

🔴 **Risk 2: Direct database read (Option B) breaks on schema change**
- **Scenario**: Gallery team refactors `posts` table, renames `commercial_flags` column to `listing_type`
- **Consequence**: Agent SQL queries fail, all gallery posts escalate, or worse - silent misclassification
- **Mitigation**: If Option B is chosen (not recommended):
  - Implement schema versioning checks (SELECT column_name FROM information_schema.columns...)
  - Alert if schema doesn't match expected structure
  - Fallback to human escalation if schema check fails
- **Likelihood**: High over 12-month horizon (schema changes are common in active codebases)

---

## System 3: Stripe (Billing & Memberships)

### System Overview

**Type**: SaaS payment processor  
**Integration**: Stripe API v2024-04-10  
**Authentication**: Stripe API secret key (restricted read-only scope)  
**Purpose**: Premium memberships, gallery commission payments

### What the Agent Needs

| Data Type | Purpose | Update Frequency | Sensitivity |
|-----------|---------|------------------|-------------|
| **Premium member status** | Identify VIP users for moderation | On-demand (cached 1 hour) | PII (subscription status) |
| **Sponsor account flag** | 100% escalate sponsor posts | On-demand (cached 24 hours) | Business-sensitive |

### API Availability

✅ **Available via REST API**:
- GET `/v1/customers/{customer_id}` - Customer metadata, subscription status
- GET `/v1/subscriptions/{subscription_id}` - Active/cancelled subscriptions
- GET `/v1/customers/search` - Search by email (map to Discourse user)

**Rate Limits**: 100 requests/second (Stripe default) - not a concern for our volume

---

### Integration Approach

**Phase 1-2**: Stripe integration NOT required (premium status doesn't affect spam classification)

**Phase 3**: Optional - check if user is premium member (weight in reputation scoring)
- Map Discourse user email → Stripe customer email
- Query Stripe for active subscription
- Cache result for 1 hour (subscription changes are infrequent)

**Phase 4**: Optional - identify sponsor accounts (if sponsor list is managed in Stripe metadata)
- Stripe customer metadata field `sponsor_account: true`
- Query once, cache for 24 hours

**Recommendation**: Deprioritize Stripe integration. Sponsor accounts should be managed in Tom's watchlist (System 6), not Stripe. Premium member status is a "nice to have" but not critical for agent functionality.

**Effort**: 8 hours if built (map users, query API, cache), but likely **not needed** - skip unless Tom confirms sponsor accounts are in Stripe.

---

### Integration Risks

🟡 **Risk 1: PII exposure via Stripe data**
- **Concern**: Stripe API returns customer emails, payment methods, subscription amounts (PII)
- **GDPR/Privacy Impact**: Agent should not log PII in audit trail or context cards visible to volunteer moderators
- **Mitigation**:
  - Query Stripe only for boolean flags (is_premium: true/false, is_sponsor: true/false)
  - Do NOT store Stripe emails, payment amounts, or subscription details in agent database
  - Implement data retention policy (cache expires after 1 hour, never persisted long-term)
- **Likelihood**: N/A (compliance requirement, not a risk to mitigate)

---

## System 4: Discord (Moderator Coordination)

### System Overview

**Type**: SaaS chat platform  
**Integration**: Discord Bot API  
**Authentication**: Bot token (OAuth2)  
**Purpose**: Volunteer moderator coordination, edge-case discussions

### What the Agent Needs (Phase 4 Only)

| Data Type | Purpose | Update Frequency | Sensitivity |
|-----------|---------|------------------|-------------|
| **Escalation notifications** | Alert moderators of flagged cases | Real-time (push) | Internal |
| **Moderator availability** | Who is online to handle escalations | Real-time (status check) | Internal |

### API Availability

✅ **Available via Discord Bot API**:
- POST `/channels/{channel_id}/messages` - Send escalation notification
- GET `/guilds/{guild_id}/members` - List online moderators
- POST webhooks - Push notifications to Discord channel

**Rate Limits**: 50 requests/second (Discord default) - sufficient for our use

---

### Integration Approach

**Phase 1-3**: Discord integration NOT required (escalations handled via Discourse notifications)

**Phase 4** (Optional - workflow improvement):
1. Create Discord bot ("MiniBase Guardian Bot")
2. When agent escalates a case:
   - POST message to `#mod-escalations` channel in volunteer Discord
   - Include: post link, escalation reason, confidence score, quick-action buttons
3. Moderator clicks button → opens Discourse moderation panel in browser

**Benefit**: Faster moderator response (Discord notifications are real-time, Discourse emails may be delayed)

**Effort**: 12 hours (bot setup, OAuth, message formatting, testing)

**Recommendation**: Phase 4 only (nice-to-have, not critical for agent MVP)

---

### Integration Risks

🟢 **Risk: Low** - Discord API is stable, well-documented, rate limits are generous. Primary risk is volunteer moderator adoption ("do we actually check Discord notifications?") - needs user research before building.

---

## System 5: Tom's Watchlist (Google Sheets)

### System Overview

**Type**: Manual spreadsheet (Google Sheets)  
**Owner**: Tom (Community Manager)  
**Sharing**: Shared with Senior Moderator only, not with volunteer moderators  
**Purpose**: High-risk users, sponsor accounts, established sculptors, fraud patterns  
**Current Location**: Google Drive > Tom's folder > "Moderation Patterns Tracker.xlsx"

### What the Agent Needs

| Data Type | Purpose | Update Frequency | Sensitivity |
|-----------|---------|------------------|-------------|
| **Watchlist users** | 100% escalate flagged posts from these accounts | Real-time (check on every flagged post) | Business-critical |
| **Sponsor accounts** | 100% escalate sponsor posts (revenue risk) | Real-time | Business-critical |
| **Escalation rules** | Per-user escalation logic (e.g., @sculpturedragon IP claims → Tom) | Real-time | Internal |

### Current Format (Based on Artefacts)

Columns in Tom's Google Sheet:
- `User / topic` (e.g., "@vortex_minis", "Painters sub")
- `Pattern` (e.g., "Sponsor account; commercial-content posts")
- `Action default` (e.g., "Tom personally reviews; do not auto-flag")
- `Notes` (e.g., "THE 2024 SPONSOR — never get this wrong")

**Sample rows**:
| User / topic | Pattern | Action default | Notes |
|---|---|---|---|
| @sculpturedragon | Established sculptor; IP claims | Tom reviews every claim | After 2024 incident |
| @vortex_minis | Sponsor account | Tom reviews; no auto-flag | THE 2024 SPONSOR |
| Painters sub | "No critique without invitation" | Apply norm; flag uninvited | Sub-forum specific |

---

### Integration Approach

❌ **Problem**: Google Sheets is not a production data source. Cannot poll Sheets API in real-time for every flagged post (latency, auth complexity, version control issues).

✅ **Solution**: Migrate watchlist from Google Sheet → Agent database (PostgreSQL or equivalent)

**Migration Process** (Phase 1-2, before spam automation goes live):

1. **One-time export** (Week 1):
   - Tom exports Google Sheet as CSV
   - Engineer imports CSV into agent database (table: `watchlist`)
   - Schema:
     ```sql
     CREATE TABLE watchlist (
       id SERIAL PRIMARY KEY,
       entity_type VARCHAR(20), -- 'user', 'subforum', 'topic'
       entity_identifier VARCHAR(255), -- '@vortex_minis', 'painters_sub'
       pattern VARCHAR(500),
       action_default VARCHAR(500),
       escalation_required BOOLEAN DEFAULT true,
       escalation_target VARCHAR(50), -- 'tom', 'senior_mod', 'any_mod'
       notes TEXT,
       created_at TIMESTAMP,
       updated_at TIMESTAMP
     );
     ```

2. **Ongoing updates** (Week 2+):
   - **Option A**: Tom updates agent database directly via simple web UI
     - Build lightweight CRUD interface (add/edit/delete watchlist entries)
     - Effort: 12 hours (UI + auth + testing)
   - **Option B**: Tom continues updating Google Sheet, engineer syncs weekly
     - Manual process (re-export CSV, re-import)
     - Effort: 1 hour/week (operational overhead)
   - **Option C**: Automated sync (Google Sheets API → agent database)
     - Poll Google Sheet daily, sync changes
     - Effort: 16 hours (Sheets API integration + diff logic)

**Recommendation**: Option A (build CRUD UI). 12 hours investment eliminates ongoing manual sync and gives Tom direct control.

---

### Integration Risks

🔴 **Risk 1: Watchlist migration loses critical entries**
- **Scenario**: CSV export from Google Sheets → engineer imports → discovers 3 sponsor accounts missing (wrong CSV export, hidden rows not included)
- **Consequence**: Agent auto-removes sponsor post (false positive), revenue risk, reputational damage
- **Mitigation**:
  - **Validation step**: After migration, Tom manually reviews agent watchlist UI, confirms all entries present
  - **Checksum**: Count rows in Google Sheet vs. agent database (must match)
  - **Dry run**: Run agent in shadow mode for 1 week, flag any sponsor/watchlist posts it would have processed (Tom reviews, confirms correct escalation)
- **Likelihood**: Medium (manual migrations are error-prone)

🔴 **Risk 2: Tom's watchlist is incomplete (tribal knowledge gap)**
- **Scenario**: Tom's Google Sheet has 12 entries. Agent goes live. Week 2: Tom realizes he forgot to add 3 sponsor accounts that he "just knows" to escalate but never wrote down.
- **Consequence**: Agent auto-flags sponsor posts as spam, Tom catches it in daily audit, but damage to sponsor relationship
- **Mitigation**:
  - **Discovery question to Tom**: "Walk me through every account you personally review. Are they all in your Google Sheet? What do you remember that isn't written down?"
  - **Grace period**: Phase 1 runs in "escalate-only" mode for 1 week (no auto-removals), Tom audits all escalations, catches missing watchlist entries
- **Likelihood**: High (tribal knowledge by definition is not documented)

---

## System 6: Subforum Norms (Tribal Knowledge)

### System Overview

**Type**: NOT A SYSTEM - currently exists only in moderators' heads + scattered Discord discussions  
**Status**: **CRITICAL BLOCKER** - must codify before Phase 3  
**Purpose**: Subforum-specific moderation rules that override global 14-page policy

### What the Agent Needs

| Subforum | Norms | Example | Escalation Rule |
|----------|-------|---------|----------------|
| **Painters** | "No critique without invitation" | Thread title must contain invitation keywords ("tips?", "feedback?", "critique?") | If critique detected + no invitation → remove |
| **Historical** | Permissive on historically-charged imagery | WWII miniatures with period-accurate markings (swastikas) allowed if historical context | If flagged for "hate symbol" → check historical context, escalate to Tom if uncertain |
| **Japanese painters** | English critiques read harsh | Cultural interpretation: Japanese English may sound blunt, not hostile | If flagged + author location=Japan → escalate to Aki (cultural expert) |
| **Gallery** | Established members can self-promote | Commissions, sales allowed if account age >1 year + active contributor | If commercial post + new account → spam. If commercial + established → allow |

### Current State

❌ **Documented**: Partial - painters "no critique without invitation" is mentioned in a few Discord threads, but not formalized  
❌ **Structured**: No database, no decision tree  
❌ **Version-controlled**: No history of norm changes  
✅ **Known**: Volunteer moderators have internalized these norms through practice

---

### Integration Approach

**Codification Process** (Must complete in Phase 1-2, before Phase 3):

**Step 1: Discovery** (4 hours)
- Interview Tom, Sarah (volunteer mod), Aki, Klaus
- Questions:
  - "Walk me through every subforum-specific rule you apply that isn't in the global policy."
  - "When do you disagree with another moderator about a decision? What subforum norms cause that disagreement?"
  - "What unwritten rules do new moderators learn in their first month?"

**Step 2: Documentation** (8 hours)
- Create decision trees for each subforum
- Example (Painters sub - critique detection):
  ```
  IF (post contains critique language: "your X is wrong", "fix your Y", "this looks like Z")
    AND (thread_title does NOT contain invitation keywords: ["tips?", "feedback?", "critique?", "help", "CC", "C&C"])
    THEN → NORM VIOLATION (remove post, message user: "Painters sub requires invitation for critique")
  ELSE
    THEN → NORM COMPLIANT (approve)
  ```

**Step 3: Database Schema** (4 hours)
- Store norms in agent database:
  ```sql
  CREATE TABLE subforum_norms (
    id SERIAL PRIMARY KEY,
    subforum_identifier VARCHAR(100), -- 'painters_sub', 'historical_sub'
    norm_name VARCHAR(200), -- 'no_critique_without_invitation'
    norm_type VARCHAR(50), -- 'content_rule', 'tone_rule', 'commercial_rule'
    decision_tree_json JSONB, -- structured rule logic
    escalation_trigger TEXT, -- when to escalate to human
    created_at TIMESTAMP,
    updated_at TIMESTAMP
  );
  ```

**Step 4: Validation** (4 hours)
- Present codified norms to Tom + volunteer moderators
- Test against 20 historical edge cases (from Discord discussions)
- Refine rules based on feedback

**Total Effort**: 20 hours (not 16 as estimated in summary - complexity is higher than initially assessed)

---

### Integration Risks

🔴 **Risk 1: Codified norms don't capture lived practice**
- **Scenario**: Engineer interviews Tom, codifies "painters sub: no critique without invitation." Week 3: Moderator overrides agent decision, says "we actually allow critique in long-running threads, even without explicit invitation - that's a 'soft rule'."
- **Consequence**: Agent over-removes legitimate critique, moderators lose trust
- **Mitigation**:
  - **Closed build loop**: Build agent with codified norms → run on historical cases → identify mismatches → refine norms
  - **Gray-box testing**: Show moderators 50 agent decisions, ask "would you decide the same?" before going live
  - **Escape hatch**: For first 2 weeks, all norm-based removals are "propose-only" (human approves), not auto-remove
- **Likelihood**: Very High (this is the #1 failure mode in lived-work agent design)

🔴 **Risk 2: Subforum norms evolve, database becomes stale**
- **Scenario**: Month 6, MiniBase community votes to relax painters sub critique rule to "no critique on first-time posts, but OK on subsequent posts." Moderators start applying new rule. Agent database still has old rule.
- **Consequence**: Agent removes legitimate critique (now allowed under new norm), moderators override, trust erodes
- **Mitigation**:
  - **Norm versioning**: Store norms with effective_date, allow multiple versions
  - **Quarterly norm review**: Tom reviews agent norms database every 3 months, updates as needed
  - **Override monitoring**: If override rate on specific norm >20%, flag for Tom review (may indicate norm has changed)
- **Likelihood**: High (community norms drift over 6-12 month timescale)

---

## System 7: Precedent Cases (Fragmented Sources)

### System Overview

**Type**: NOT A SYSTEM - currently fragmented across:
- Personal Google Docs (Sarah, Tom, other mods have individual "moderation notes" docs)
- Discord `#mod-decisions` channel (text logs, searchable but unstructured)
- Discourse moderation logs (actions recorded, but rationale often missing)
- Tribal memory ("we decided X in that case last year, remember?")

**Status**: **CRITICAL BLOCKER** - must centralize before Phase 3

### What the Agent Needs

| Data Type | Purpose | Query Pattern | Volume |
|-----------|---------|---------------|--------|
| **Similar past cases** | Consistency - "how did we decide similar cases before?" | Semantic similarity search (embed post content, search for top 5 matches) | ~360 grey-zone cases/year = ~1,800 cases over 5 years (estimated) |
| **Decision rationale** | Context - "why did we approve/remove?" | Text search, display alongside similar case | Required for all precedent cases |
| **Outcome** | Result - "what action was taken?" | Structured field (approved, removed, warned, escalated) | Required |
| **Moderator** | Attribution - "who decided?" | Structured field (Sarah, Tom, Aki, etc.) | Optional but useful |

---

### Integration Approach

**Centralization Process** (Phase 2-3, 32 hours total):

**Step 1: Data Collection** (12 hours)
1. **Discord export**: Export `#mod-decisions` channel history (last 2 years)
   - Tool: Discord data export OR DiscordChatExporter (open-source)
   - Format: JSON or CSV
   - Volume estimate: ~1,000 messages (3-5 per day × 365 × 2)

2. **Google Docs scrape**: Request moderators share their personal notes docs
   - Manual review: identify cases with decision rationale
   - Extract: post link, decision, rationale
   - Volume estimate: ~500 cases across 4 moderators

3. **Discourse logs query**: Export moderation actions via API
   - GET `/admin/logs/staff_action_logs.json` (last 2 years)
   - Volume estimate: ~270K actions (1,500/day × 365 × 2) - filter to grey-zone only (~18K)

**Step 2: Data Structuring** (12 hours)
- Parse exported data into structured format:
  ```json
  {
    "case_id": "unique_id",
    "post_content": "truncated to 500 chars",
    "post_id": "discourse_post_id",
    "subforum": "painters_sub",
    "issue_type": "harsh_critique", "commercial_ambiguous", "cultural_interpretation"],
    "decision": "approved", "removed", "warned", "escalated"],
    "rationale": "OP asked for feedback, critique targets technique not person",
    "moderator": "sarah_k",
    "decided_at": "2024-06-15T14:30:00Z",
    "precedent_weight": 1.0 // 0-1 score, higher = more authoritative
  }
  ```

**Step 3: Vector Embedding** (4 hours)
- Embed `post_content` field using OpenAI text-embedding-3-small (or similar)
- Store embeddings in vector database (Pinecone, Weaviate, or pgvector extension in PostgreSQL)
- Index by subforum, issue_type for faster retrieval

**Step 4: Validation** (4 hours)
- Test semantic search: Query with 20 current flagged posts, retrieve top 5 precedents
- Moderator review: "Are these precedents actually similar? Useful?"
- Tune retrieval parameters (embedding model, top-k, similarity threshold)

**Total Effort**: 32 hours (as estimated in summary)

---

### Integration Risks

🔴 **Risk 1: Precedent case data is incomplete or low-quality**
- **Scenario**: Discord logs have cases, but rationale is often missing ("removed. spam." - no detail). Google Docs have detailed rationale, but only ~100 cases across 4 moderators.
- **Consequence**: Agent retrieves precedents, but they don't provide useful context ("similar case was removed, but I don't know why - not helpful")
- **Mitigation**:
  - **Quality over quantity**: Prioritize cases with detailed rationale (Google Docs, Tom's notes) over high-volume low-detail Discord logs
  - **Minimum viable precedent**: Define precedent case quality bar (must have: post content, decision, rationale ≥50 words)
  - **Graceful degradation**: If no high-quality precedents found, agent says "no strong precedents found" instead of showing low-quality matches
- **Likelihood**: Very High (historical data quality is always a challenge)

🔴 **Risk 2: Semantic search retrieves irrelevant precedents**
- **Scenario**: Flagged post: "This mini looks like garbage, redo it." Semantic search retrieves precedent: "Your weathering technique looks like rust, great job!" (both contain "looks like", but opposite tone)
- **Consequence**: Agent shows irrelevant precedent, moderator ignores all precedent suggestions, feature becomes unused
- **Mitigation**:
  - **Hybrid search**: Combine semantic similarity (embeddings) + keyword filters (subforum, issue_type)
  - **Relevance scoring**: Show moderator: "Similarity: 0.82 (high)" or "Similarity: 0.51 (low - use caution)"
  - **Human feedback loop**: "Was this precedent useful? Yes/No" button → retrain retrieval model
- **Likelihood**: Medium (semantic search is imperfect, but modern embeddings are quite good)

🟡 **Risk 3: Precedents become stale (community norms drift)**
- **Scenario**: Year 1 precedent: "Commercial posts from new accounts → remove as spam." Year 3: Community norm shifts, established sculptors now welcome new artists selling.
- **Consequence**: Agent retrieves stale precedent, recommends removal based on outdated norm
- **Mitigation**:
  - **Precedent aging**: Weight recent precedents higher (last 12 months = 1.0, 12-24 months = 0.7, >24 months = 0.3)
  - **Precedent review**: Quarterly, Tom reviews oldest precedents (>2 years), marks as "stale" if norm has changed
  - **Override signal**: If moderators override agent + cite stale precedent, flag precedent for review
- **Likelihood**: High over 2-3 year timescale (norms drift)

---

## System 8: Email (IP Claims)

### System Overview

**Type**: Gmail (Tom's MiniBase email account, assumed)  
**Integration**: IMAP or Gmail API  
**Purpose**: Sculptors email IP claims (copyright, trademark disputes)  
**Volume**: 3-5 claims/week (~0.7/day)

### What the Agent Needs (Phase 4 Only)

| Data Type | Purpose | Update Frequency | Sensitivity |
|-----------|---------|------------------|-------------|
| **IP claim emails** | Triage urgency, extract claim details | Poll every 4 hours | Legal-sensitive |
| **Claim metadata** | Sculptor name, image URL, claim type | On receipt | Legal-sensitive |

---

### Integration Approach

**Phase 1-3**: Email integration NOT required (IP claims are low-volume, human-only)

**Phase 4** (Optional - triage automation):
1. Connect to Gmail via IMAP or Gmail API
2. Poll inbox every 4 hours for emails with subject containing "IP claim", "copyright", "trademark"
3. Extract:
   - Claimant name + email
   - Claimed image URL (if provided)
   - Claim type (copyright vs. trademark)
4. Create case in agent database, flag for Tom review

**Effort**: 16 hours (Gmail API auth, parsing email bodies, case creation)

**Recommendation**: Phase 4 only, LOW priority (3-5 cases/week doesn't justify automation investment)

---

### Integration Risks

🟡 **Risk: Email parsing is brittle**
- Sculptors send IP claims in unstructured email formats (plain text, attachments, varied phrasing)
- NLP-based extraction required (GPT-4 prompt: "extract claimant name, image URL, claim type from this email")
- False negatives: Agent misses claim → Tom manually finds it anyway (no worse than current state)

---

## Cross-System Integration: Data Flow Architecture

### Agent Data Flow (Phase 3 - Full Context Automation)

```
[Discourse] ──(poll every 30s)──> [Flagged Post]
                                         │
                                         ▼
                                  [Spam Classifier]
                                    ⎿      ⎾
                       Spam (0.9+)   │   Grey-Zone (0.7-)
                           │         │         │
                           ▼         ▼         ▼
                    [Auto-Remove] [Edge Case] [Context Gathering]
                                                 │
                      ┌──────────────────────────┼──────────────────────────┐
                      ▼                          ▼                          ▼
              [Discourse User API]      [Watchlist DB]         [Subforum Norms DB]
              - Account age             - Check user            - Match subforum
              - Post history            - Check sponsor          - Retrieve norms
              - Reputation                                      - Invitation detection
                      │                          │                          │
                      └──────────────────────────┼──────────────────────────┘
                                                 ▼
                                        [Precedent Search]
                                        - Semantic similarity
                                        - Top 5 matches
                                                 │
                                                 ▼
                                          [Context Card]
                                        (Aggregate all data)
                                                 │
                                                 ▼
                                          [Human Moderator]
                                         (Review + Decide)
```

### Data Latency Requirements

| Operation | Target Latency | Acceptable Max | Consequence if Exceeded |
|-----------|---------------|----------------|------------------------|
| Discourse poll (new flags) | 30 sec | 60 sec | Spam stays visible longer |
| Spam classification | 2 sec | 5 sec | User waits for moderation |
| User profile retrieval | 1 sec (cached) | 3 sec (uncached) | Context gathering slows |
| Watchlist lookup | 100 ms | 500 ms | Escalation delay |
| Precedent search | 2 sec | 5 sec | Context card incomplete |
| Total (spam removal) | <5 sec | <10 sec | Acceptable |
| Total (grey-zone context) | <10 sec | <20 sec | Acceptable |

---

## Data Storage & Infrastructure

### Agent Database Schema (PostgreSQL)

**Core Tables**:
1. `flagged_posts` - Queue of posts to process
2. `moderation_actions` - Agent decisions + human overrides (audit trail)
3. `watchlist` - Tom's high-risk users + sponsors
4. `subforum_norms` - Codified moderation rules by subforum
5. `precedent_cases` - Historical moderation decisions
6. `user_profiles_cache` - Discourse user data (1-hour TTL)

**Vector Store** (Pinecone or pgvector):
- `precedent_embeddings` - Vector embeddings of precedent case content

**Estimated Storage**:
- Year 1: ~500K moderation actions × 2 KB/action = 1 GB
- Precedent cases: ~2,000 cases × 5 KB/case = 10 MB
- Embeddings: ~2,000 cases × 1.5 KB/embedding = 3 MB
- **Total Year 1**: ~1.5 GB (negligible)

**Backup & Retention**:
- Daily backups to S3 (encrypted)
- Retain moderation actions indefinitely (audit trail, legal compliance)
- Retain cache <24 hours (GDPR - user profiles are PII, don't over-retain)

---

## Missing Data & Unsolvable Gaps

### Gap 1: User Intent (Cannot Be Determined)
**What's Missing**: Did user intend harsh critique as feedback or harassment?  
**Why It Matters**: This is the core grey-zone judgment  
**Workaround**: Agent cannot determine intent. Extract signals (targets work vs. person, OP reaction), human decides.  
**Status**: Not a gap - by design, agent doesn't decide grey-zone cases

---

### Gap 2: Cultural Context (Cannot Be Codified)
**What's Missing**: Is Japanese English phrasing harsh due to translation, or genuinely hostile?  
**Why It Matters**: Painters sub has Japanese members, English critiques may read differently  
**Workaround**: Agent flags cultural interpretation needed, escalates to Aki (Japanese moderator)  
**Status**: Not a gap - escalation is the correct design

---

### Gap 3: "Common Sense" Moderation (Cannot Be Automated)
**What's Missing**: Sarah (moderator): "Sometimes you just know a post is off, even if it doesn't break a specific rule."  
**Why It Matters**: Tribal knowledge, pattern recognition built over years  
**Workaround**: Agent doesn't replace this - it handles clear cases (spam) and gathers context (grey-zone), human applies "common sense"  
**Status**: Not a gap - human judgment is preserved by design

---

## Implementation Roadmap: System Integration Schedule

### Phase 1 (Weeks 1-4): Spam Automation - Core Systems

| Week | System | Tasks | Hours |
|------|--------|-------|-------|
| **Week 1** | Discourse API | - Connect to Discourse REST API<br>- Implement flagged post polling<br>- Build post retrieval<br>- Test auth & rate limits | 16 hrs |
| **Week 1** | Agent Database | - Set up PostgreSQL<br>- Create moderation_actions table<br>- Create watchlist table<br>- Implement logging | 8 hrs |
| **Week 2** | Tom's Watchlist | - Export Google Sheet → CSV<br>- Import to agent database<br>- Build CRUD UI for Tom<br>- Validation with Tom | 12 hrs |
| **Week 3** | Spam Classifier | - Train spam detection model<br>- Integrate with Discourse data<br>- Confidence scoring<br>- Testing on historical data | 24 hrs |
| **Week 4** | Testing & Validation | - Shadow mode (agent recommends, human decides)<br>- Calibration<br>- Bug fixes | 20 hrs |

**Phase 1 Total**: 80 hours

---

### Phase 2 (Weeks 5-8): Spam Edge Cases

| Week | System | Tasks | Hours |
|------|--------|-------|-------|
| **Week 5** | Subforum Norms | - Discovery interviews (Tom, mods)<br>- Document decision trees<br>- Build norms database | 16 hrs |
| **Week 6** | Subforum Norms | - Integrate norms into spam classifier<br>- Exception detection logic<br>- Testing with edge cases | 12 hrs |
| **Week 7** | Validation | - Gray-box testing (50 historical cases)<br>- Moderator feedback<br>- Refinement | 16 hrs |

**Phase 2 Total**: 44 hours

---

### Phase 3 (Weeks 9-12): Grey-Zone Context Automation

| Week | System | Tasks | Hours |
|------|--------|-------|-------|
| **Week 9** | Precedent Cases | - Export Discord logs<br>- Scrape Google Docs<br>- Structure data<br>- Build case library | 16 hrs |
| **Week 10** | Precedent Search | - Vector embedding (OpenAI API)<br>- Set up Pinecone/pgvector<br>- Semantic search implementation<br>- Test retrieval quality | 16 hrs |
| **Week 11** | Context Aggregation | - Build context card engine<br>- Integrate all data sources (Discourse + watchlist + norms + precedents)<br>- Format for human review | 20 hrs |
| **Week 12** | Gallery Integration | - Build minimal Rails API endpoints (if prioritized)<br>- OR implement fallback (escalate gallery posts)<br>- Testing | 16 hrs (Option A)<br>4 hrs (Option C) |
| **Week 12** | Testing & Validation | - Test on 100 grey-zone cases<br>- Moderator feedback: "Is context complete?"<br>- Refinement | 20 hrs |

**Phase 3 Total**: 88-100 hours (depending on gallery integration approach)

---

### Phase 4 (Weeks 13-16): Appeals & Optional Integrations

| Week | System | Tasks | Hours |
|------|--------|-------|-------|
| **Week 13** | Appeal Context | - Reuse context aggregation engine<br>- Build appeal-specific UI<br>- Testing with Tom | 16 hrs |
| **Week 14** | Discord (Optional) | - Build Discord bot<br>- Escalation notifications<br>- Testing with volunteer mods | 12 hrs |
| **Week 15** | Email (Optional) | - Gmail API integration<br>- IP claim parsing (NLP)<br>- Triage automation | 16 hrs |
| **Week 16** | Stripe (Optional) | - Premium member check<br>- Sponsor flag (if in Stripe)<br>- Testing | 8 hrs |

**Phase 4 Total**: 52 hours (includes all optional systems)

---

## Total Integration Effort Summary

| Phase | Duration | Hours | Systems Integrated |
|-------|----------|-------|-------------------|
| **Phase 1** | 4 weeks | 80 hrs | Discourse, Watchlist, Agent DB |
| **Phase 2** | 4 weeks | 44 hrs | Subforum Norms |
| **Phase 3** | 4 weeks | 88-100 hrs | Precedents, Context Engine, (Gallery) |
| **Phase 4** | 4 weeks | 52 hrs | Appeals, (Discord), (Email), (Stripe) |
| **TOTAL (Phase 1-3)** | **12 weeks** | **212-224 hrs** | Core agent functionality |
| **TOTAL (All Phases)** | **16 weeks** | **264-276 hrs** | Full agent + optional features |

**Initial estimate (from Agent Purpose Document)**: 136 hours  
**Revised estimate (after detailed analysis)**: 212-224 hours for Phase 1-3  
**Difference**: +76-88 hours (56% increase)

**Why the increase?**
- Subforum norms codification more complex than initially assessed (20 hrs vs. 16 hrs estimated)
- Precedent case centralization effort was underestimated (32 hrs as stated, but data quality work adds time)
- Gallery integration requires more decision-making and testing than initial estimate
- Watchlist CRUD UI adds 12 hours not in original estimate

**Revised ROI** (using higher effort estimate):
- Phase 1-3 cost: 224 hrs × £50/hr = £11,200 (vs. £14,300 original estimate)
- First-year value: £183,273 (unchanged)
- **Revised first-year ROI**: 16.4:1 (vs. 10.7:1 original)
- **Still strongly positive**

---

## Risk Summary & Mitigation Priorities

### Critical Risks (Must Address Before Go-Live)

| Risk | System | Mitigation | Owner | Status |
|------|--------|------------|-------|--------|
| **Watchlist migration data loss** | Tom's Watchlist | Validation checklist, dry run | Engineer + Tom | Phase 1 |
| **Subforum norms codification incomplete** | Subforum Norms | Closed build loop, moderator validation | Engineer + Mods | Phase 2 |
| **Precedent case data low-quality** | Precedent Cases | Quality-over-quantity, minimum viable precedent | Engineer | Phase 3 |
| **Discourse rate limit exhaustion** | Discourse API | Request limit increase, priority queue | Engineer + MiniBase DevOps | Phase 1 |

### Medium Risks (Monitor During Operation)

| Risk | System | Mitigation | Owner | Status |
|------|--------|------------|-------|--------|
| **Gallery API development delay** | Gallery | Option C fallback (escalate gallery posts) | Tom + Engineer | Phase 3 decision |
| **Post edited after classification** | Discourse | Re-classify if edited_at changes | Engineer | Phase 1 |
| **Precedent semantic search irrelevant** | Precedent Cases | Hybrid search, relevance scoring, feedback loop | Engineer | Phase 3 testing |

### Low Risks (Accept or Defer)

| Risk | System | Response | Owner | Status |
|------|--------|----------|-------|--------|
| **Discord bot adoption** | Discord | Build in Phase 4 only if mods confirm they'll use it | Tom + Mods | Phase 4 research |
| **Email IP claim parsing errors** | Email | Low volume (3-5/week), manual fallback acceptable | Tom | Phase 4 optional |
| **Stripe PII exposure** | Stripe | Don't integrate unless sponsor accounts confirmed in Stripe | Tom + Engineer | TBD |

---

## Assumptions & Validation Checklist

### Critical Assumptions to Validate with Tom (Week 1)

- [ ] **Discourse version**: Confirm MiniBase runs Discourse 3.1+ (modern API)
- [ ] **Discourse API access**: Confirm admin API key can be provisioned (write access for agent)
- [ ] **Discourse rate limits**: Confirm 60 req/min is default, request increase to 200 req/min for agent
- [ ] **Gallery API**: Confirm in-house gallery has NO API for commercial flags (requires building Option A or Option C)
- [ ] **Stripe sponsor accounts**: Confirm sponsor accounts are NOT managed in Stripe metadata (manage in watchlist instead)
- [ ] **Tom's watchlist completeness**: Walk through every account Tom personally reviews, confirm all are in Google Sheet
- [ ] **Subforum norms stability**: Confirm painters "no critique without invitation" is stable rule (not changing soon)
- [ ] **Precedent case access**: Confirm moderators will share personal Google Docs (privacy concern?)
- [ ] **Discord export permissions**: Confirm Tom has admin access to export `#mod-decisions` channel history
- [ ] **Gmail access**: Confirm Tom will grant agent access to MiniBase email account (IP claims) if Phase 4 prioritized

### Technical Validation (Week 2)

- [ ] **Discourse API test**: Successfully retrieve flagged posts via `/posts/flags.json`
- [ ] **Discourse rate limit test**: Simulate 100 API calls in 1 minute, confirm no 429 errors
- [ ] **PostgreSQL setup**: Agent database provisioned, tables created, backups configured
- [ ] **Watchlist migration**: CSV export → database import → Tom validates all entries present
- [ ] **Spam classifier training data**: Acquire 500+ labeled spam cases (from Discourse logs)

---

## Conclusion: Integration Feasibility

### Verdict: **FEASIBLE** with caveats

**What's achievable (Phase 1-3, 12 weeks)**:
✅ Discourse integration (mature API, low risk)  
✅ Watchlist migration (12-hour effort, manageable)  
✅ Spam classifier (standard ML, proven approach)  
✅ Subforum norms codification (20 hours, critical but doable)  
✅ Precedent case centralization (32 hours, data quality is main challenge)  
✅ Context aggregation engine (20 hours, reusable across phases)

**What's challenging**:
⚠️ Gallery integration (limited API, requires building endpoints OR accepting scope reduction)  
⚠️ Precedent case data quality (historical data fragmented, may need manual curation)  
⚠️ Subforum norms completeness (tribal knowledge gap, requires intensive discovery)

**What's optional (Phase 4, can defer)**:
🔵 Discord notifications (12 hours, workflow improvement but not critical)  
🔵 Email IP claim triage (16 hours, low volume doesn't justify effort)  
🔵 Stripe integration (8 hours, likely not needed if sponsors in watchlist)

**Critical path blockers**:
1. **Subforum norms codification** - Must complete before Phase 3 (20 hours)
2. **Precedent case centralization** - Must complete before Phase 3 (32 hours)
3. **Watchlist migration** - Must complete before Phase 1 go-live (12 hours)

**Overall assessment**: Integration is feasible within 12-week timeline (Phase 1-3) with 212-224 hours effort. Primary risks are data quality (precedent cases) and tribal knowledge capture (subforum norms), not technical API limitations. 

**Recommendation**: Proceed with phased rollout. De-scope Gallery integration to Phase 4 if Rails API development is delayed (fallback: escalate gallery posts to human review).

---

## Document Control

**Version History**:
- v1.0 (2026-04-30): Initial System & Data Inventory with detailed integration assessment

**Authors**: FDE Program Week 2 Team

**Validation Required**:
- Tom (Community Manager): Confirm system access, watchlist completeness, subforum norms
- MiniBase Dev Team: Confirm Discourse version, API limits, gallery API status
- Volunteer Moderators: Confirm precedent case access, Discord export permissions

**Related Documents**:
- `06_Agent_Purpose_Document.md` (Agent design specification)
- `04_Delegation_Suitability_Matrix.md` (Delegation boundaries)
- `05_Volume_Value_Analysis.md` (ROI justification)

**Next Steps**:
1. **Week 1**: Validate assumptions with Tom (checklist above)
2. **Week 1**: Test Discourse API access (provision API keys, test endpoints)
3. **Week 1-2**: Begin watchlist migration (export Google Sheet, build database)
4. **Week 2**: Begin subforum norms discovery (interview Tom + moderators)
5. **Week 3-4**: Begin precedent case data collection (Discord export, Google Docs scrape)

**Last Review**: 2026-04-30
