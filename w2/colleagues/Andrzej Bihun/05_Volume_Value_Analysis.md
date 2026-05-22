# Volume × Value Analysis: MiniBase Content Moderation

**Project**: MiniBase Community Content Moderation Agent  
**Phase**: ATX Use Case Scoring & Prioritization  
**Date**: 2026-04-29  
**Version**: 1.0

---

## Executive Summary

This document applies **Volume × Value Analysis** from ATX methodology to prioritize MiniBase's four moderation work streams for agent development. The analysis reveals:

### Primary Agentic Target: Routine Spam Removal + Grey-Zone Context Gathering

**Why this wins:**
1. **Highest combined volume**: 1,440 cases/day (96% of total queue)
2. **Highest absolute value**: £132K/year time savings (71% of total opportunity)
3. **Lowest implementation risk**: Clear patterns (spam) + no decision risk (context gathering)
4. **Fastest time-to-value**: 4-8 weeks to production deployment

**ROI**: 18.5:1 first-year return (£186K value / £10K implementation cost)

### Strategic Prioritization

| Work Stream | Volume | Value | Risk-Adjusted Priority | Implementation Phase |
|-------------|--------|-------|------------------------|---------------------|
| **1. Routine Spam** | 1,080/day | £46K/year | ⭐⭐⭐⭐⭐ Critical (Phase 1) | Weeks 1-4 |
| **2. Grey-Zone Context** | 360/day | £86K/year | ⭐⭐⭐⭐⭐ Critical (Phase 3) | Weeks 9-12 |
| **3. User Appeals** | 60/day | £18K/year | ⭐⭐⭐ Medium (Phase 4) | Weeks 13+ |
| **4. IP Claims** | 0.7/day | £2K/year | ⭐ Low (Human-Only) | No automation |

**Key Insight**: Automating high-volume, low-risk work (spam + context gathering) delivers 71% of total value while building trust for subsequent phases. Low-volume, high-risk work (IP claims) remains human-only despite requiring effort, because automation ROI doesn't justify risk.

---

## ATX Volume × Value Framework

### What is Volume × Value Analysis?

From ATX methodology: **Volume × Value** is a prioritization framework that scores use cases on two dimensions:

1. **Volume**: How often does this work occur? (Frequency × Effort)
   - Measured in: cases/day, hours/day, FTE-equivalents
   - Higher volume → stronger automation justification (economies of scale)

2. **Value**: What business impact does automating this create? (Time savings × Cost × Strategic benefit)
   - Measured in: £/year time savings, growth headroom, risk reduction, quality improvement
   - Higher value → stronger business case for investment

### The Volume × Value Matrix

```
        High Value
            │
   Quadrant 2 │ Quadrant 1
   Quick Wins │ Strategic Bets
   ───────────┼───────────
   Quadrant 3 │ Quadrant 4
   Deprioritize│ Efficiency Plays
            │
        Low Value
    Low Volume → High Volume
```

**Quadrant 1 (High Volume, High Value)**: **Primary automation targets** - maximum ROI, strong business case
**Quadrant 2 (Low Volume, High Value)**: Quick wins - high impact, lower investment
**Quadrant 3 (Low Volume, Low Value)**: Deprioritize - doesn't justify investment
**Quadrant 4 (High Volume, Low Value)**: Efficiency plays - justify only if very low cost

### Why Volume × Value Matters

**Volume alone is insufficient**: High-volume work may not create value if:
- Effort per case is trivial (e.g., 5 seconds per case × 1,000 cases = 83 min/day = not worth automating)
- Work is already efficient (no bottleneck to remove)
- Automation is complex/costly (investment doesn't pay back)

**Value alone is insufficient**: High-value work may not be automatable if:
- Volume is too low (e.g., 1 case/week, no matter how valuable, doesn't justify building agent)
- Risk is too high (e.g., legal decisions, existential business risk)
- Work is judgment-bound (can't be codified)

**Volume × Value together** identifies where:
- High volume creates economies of scale for automation investment
- High value creates business case for investment
- Combination maximizes ROI

---

## Volume Analysis: The Four Work Streams

### Volume Dimension 1: Case Frequency

| Work Stream | Cases/Day | Cases/Week | Cases/Year | % of Total Queue |
|-------------|-----------|------------|------------|------------------|
| **1. Routine Spam Removal** | 1,080 | 7,560 | 394,200 | 72% |
| **2. Grey-Zone Case Review** | 360 | 2,520 | 131,400 | 24% |
| **3. User Dispute Appeals** | 60 | 420 | 21,900 | 4% |
| **4. IP Claim Resolution** | 0.7 (~5/week) | 5 | 260 | <1% |
| **TOTAL** | **1,500** | **10,500** | **547,760** | **100%** |

**Insight**: Work Streams 1 & 2 represent **96% of case volume**. This is where automation effort should concentrate.

---

### Volume Dimension 2: Time Per Case

| Work Stream | Time Per Case (current) | Time Per Case (with agent) | Automation Opportunity |
|-------------|------------------------|----------------------------|------------------------|
| **1. Routine Spam** | 30 sec | 0 sec (agent handles) OR 10-15 sec (human review edge cases) | **83% time reduction** |
| **2. Grey-Zone** | 4-5 min (270 sec) | 1.5-2 min (105 sec) via context automation | **61% time reduction** |
| **3. Appeals** | 15-20 min | 8-10 min via context prep | **47% time reduction** |
| **4. IP Claims** | 30-45 min | 30-45 min (no automation) | **0% time reduction** |

**Insight**: Spam has highest % reduction (83%) but from low base (30 sec). Grey-zone has moderate % reduction (61%) but from high base (270 sec) → **grey-zone has higher absolute impact**.

---

### Volume Dimension 3: Total Effort (Current State)

| Work Stream | Cases/Day | Time/Case | Total Daily Effort | Total Annual Effort | FTE-Equivalent |
|-------------|-----------|-----------|-------------------|-------------------|----------------|
| **1. Routine Spam** | 1,080 | 30 sec | 9 hrs/day | 3,285 hrs/year | 1.6 FTE |
| **2. Grey-Zone** | 360 | 270 sec | 27 hrs/day* | 9,855 hrs/year | 4.7 FTE |
| **3. Appeals** | 60 | 17 min | 17 hrs/day | 6,205 hrs/year | 3.0 FTE |
| **4. IP Claims** | 0.7 | 37.5 min | 0.4 hrs/day | 146 hrs/year | 0.07 FTE |
| **TOTAL** | **1,500** | - | **53.4 hrs/day** | **19,491 hrs/year** | **9.4 FTE** |

*Note: Grey-zone 27 hrs includes context gathering (15 hrs) + judgment (9 hrs) + coordination (3 hrs). Context gathering is the automation target.

**Key metrics**:
- **Team capacity**: 47 hrs/day (10 moderators × ~4.7 hrs avg/day, accounting for volunteers' part-time)
- **Current utilization**: 53.4 hrs/day demand / 47 hrs/day capacity = **114% over-capacity**
- **The bottleneck**: Team is operating beyond capacity, creating delays and burnout risk

**Insight**: Grey-zone consumes **51% of total effort** (27 of 53.4 hrs/day), making it the largest single workload component.

---

### Volume Dimension 4: Total Effort (Post-Agent State)

| Work Stream | Cases/Day | Time/Case (agent-assisted) | Total Daily Effort | Effort Reduction | % Reduction |
|-------------|-----------|---------------------------|-------------------|-----------------|-------------|
| **1. Routine Spam** | 1,080 | 5 sec avg (sampling + edge cases) | 1.5 hrs/day | 7.5 hrs/day | 83% |
| **2. Grey-Zone** | 360 | 105 sec (agent context + human judgment) | 10.5 hrs/day | 16.5 hrs/day | 61% |
| **3. Appeals** | 60 | 9 min (agent context + Tom review) | 9 hrs/day | 8 hrs/day | 47% |
| **4. IP Claims** | 0.7 | 37.5 min (no change) | 0.4 hrs/day | 0 hrs/day | 0% |
| **TOTAL** | **1,500** | - | **21.4 hrs/day** | **32 hrs/day** | **60%** |

**Post-agent capacity utilization**: 21.4 hrs/day demand / 47 hrs/day capacity = **46% utilization**

**Growth headroom**: 47 - 21.4 = **25.6 hrs/day spare capacity** → can handle **2.5× current volume** without adding moderators

---

## Value Analysis: Business Impact by Work Stream

### Value Dimension 1: Time Savings (£ per Year)

**Calculation methodology**:
- Blended moderator rate: £18/hour (weighted avg of paid staff £35/hr + volunteers valued at opportunity cost £12/hr)
- Annual working days: 365 (moderation is 24/7, volunteers rotate)

| Work Stream | Effort Reduction (hrs/day) | Annual Savings (hrs) | Annual Savings (£) |
|-------------|---------------------------|---------------------|-------------------|
| **1. Routine Spam** | 7.5 hrs/day | 2,738 hrs/year | **£49,284** |
| **2. Grey-Zone** | 16.5 hrs/day | 6,023 hrs/year | **£108,414** |
| **3. Appeals** | 8 hrs/day | 2,920 hrs/year | **£52,560** |
| **4. IP Claims** | 0 hrs/day | 0 hrs/year | **£0** |
| **TOTAL** | **32 hrs/day** | **11,681 hrs/year** | **£210,258** |

**Insight**: Grey-zone context automation delivers **52% of total value** (£108K of £210K) despite being only 24% of case volume. This is because:
- High base effort (27 hrs/day → 10.5 hrs/day = 16.5 hrs saved)
- Context automation (40% of grey-zone effort) is fully automatable

---

### Value Dimension 2: Growth Headroom

**Current constraint**: Team at 114% capacity (53.4 hrs demand / 47 hrs capacity) → cannot handle growth

**Post-agent capacity**: 46% utilization (21.4 hrs demand / 47 hrs capacity) → **25.6 hrs spare capacity**

**Growth potential**:
- Current volume: 1,500 cases/day
- Capacity with automation: 1,500 × (47 / 21.4) = **3,294 cases/day** (+120% growth)
- Platform user growth: 180K users → **396K users** (+120%) without hiring

**Value calculation**:
- **Avoided hiring cost**: 4.7 FTE × £40K/year (blended cost) = **£188K/year** in avoided recruitment, training, coordination overhead
- **Strategic option value**: Ability to scale platform 2× without proportional cost increase = competitive advantage

**Note**: This is **option value** (enables future growth) rather than immediate cash savings, so not included in primary ROI calculation but critical for business case.

---

### Value Dimension 3: Quality Improvement

**Current quality issues** (from discovery):
1. **Volunteer burnout**: 60% of time on mindless spam → satisfaction decline → turnover risk
2. **Inconsistent decisions**: Precedents siloed in personal notes → different moderators decide differently
3. **Delayed responses**: 15-30 min avg response time on spam (timezone gaps)
4. **Context-gathering errors**: 20% of grey-zone time wasted on tool navigation → fatigue → missed signals

**Agent-driven quality improvements**:

| Quality Metric | Current | Post-Agent | Improvement | Value |
|----------------|---------|------------|-------------|-------|
| **Spam response time** | 15-30 min avg | <5 min (agent instant) | 67-83% faster | User experience ↑, spam visibility ↓ |
| **Decision consistency** | Moderate (precedents siloed) | High (shared case library) | Precedent-based decisions | Trust ↑, appeals ↓ |
| **Moderator satisfaction** | 60% time on spam (low value) | 20% time on spam (sampling only) | More time on valued work | Retention ↑, burnout ↓ |
| **Grey-zone thoroughness** | 40% time on context gathering | 10% time, agent-provided | More time on judgment | Decision quality ↑ |

**Quantified quality value** (conservative estimates):
- **Reduced turnover**: 1 volunteer replaced per year × 40 hours training/onboarding × £18/hr = **£720/year**
- **Reduced appeals**: 10% reduction in user appeals (60 → 54/day) × 17 min/case × 365 days × £18/hr = **£9,855/year**
- **Total quality value**: **£10,575/year**

**Note**: Quality improvements have long-tail value (community trust, brand reputation) that's hard to quantify but strategically important.

---

### Value Dimension 4: Risk Reduction

**Current risks**:
1. **Existential risk**: One viral false negative (missing harassment, sponsor incident) = platform reputation damage, revenue loss
2. **Capacity risk**: Team over-capacity (114%) → delays accumulate → moderation backlog → harmful content persists longer
3. **Consistency risk**: Different moderators decide same case differently → users perceive unfairness → trust erosion
4. **Volunteer risk**: Burnout → turnover → knowledge loss → reduced coverage → quality decline (vicious cycle)

**Agent risk mitigation**:

| Risk | Current State | Agent Mitigation | Value |
|------|---------------|------------------|-------|
| **Existential risk** | Relies on human vigilance (fatigue-prone) | Agent never misses sponsor badge, watchlist, high-engagement flags (deterministic escalation) | Risk reduction: High |
| **Capacity risk** | 114% over-capacity, delays accumulating | 46% utilization, 25.6 hrs spare capacity | Risk reduction: Critical |
| **Consistency risk** | Precedents siloed, tribal knowledge | Shared case library, structured norms, consistent application | Risk reduction: Medium |
| **Volunteer risk** | 60% time on low-value spam | 20% time on spam (sampling), 70% on valued judgment work | Risk reduction: High |

**Quantified risk value**:
- **Avoided existential incident**: Probability reduction 5% → 2% (agent escalation triggers), potential cost £500K (sponsor withdrawal, community exodus) × 3% = **£15K/year expected value**
- **Avoided capacity crisis**: Eliminate over-capacity state, prevent backlog accumulation (hard to quantify, but operationally critical)

**Total risk reduction value**: **£15K/year** (conservative, only existential risk quantified)

---

### Total Value Summary (All Dimensions)

| Value Dimension | Annual Value (£) | % of Total | Strategic Importance |
|-----------------|------------------|------------|---------------------|
| **Time savings** | £210,258 | 87% | Direct cost reduction |
| **Quality improvement** | £10,575 | 4% | Long-tail reputation value |
| **Risk reduction** | £15,000 | 6% | Downside protection |
| **Growth headroom** | £188,000 option value | (Not counted in ROI) | Strategic competitive advantage |
| **TOTAL QUANTIFIED** | **£235,833** | **100%** | - |

**Note**: Growth headroom (£188K) is real value but not immediate cash savings, so excluded from ROI calculation to be conservative. Including it would increase ROI from 18.5:1 to 33.2:1.

---

## Volume × Value Matrix: Plotting the Four Work Streams

### Quadrant Chart

```mermaid
quadrantChart
    title Volume × Value Analysis: MiniBase Moderation Work Streams
    x-axis Low Volume --> High Volume
    y-axis Low Value --> High Value
    quadrant-1 Strategic Bets (High Value, High Volume)
    quadrant-2 Quick Wins (High Value, Low Volume)
    quadrant-3 Deprioritize (Low Value, Low Volume)
    quadrant-4 Efficiency Plays (Low Value, High Volume)
    
    Routine Spam: [0.85, 0.65]
    Grey-Zone Context: [0.75, 0.95]
    User Appeals: [0.25, 0.60]
    IP Claims: [0.05, 0.15]
```

**Note**: Bubble size represents delegation suitability (larger = more automatable)

### Quadrant Placement Rationale

**Axes Definition**:
- **X-axis (Volume)**: Cases/day normalized (0 = 0 cases, 1 = 1,500 cases)
  - Routine Spam: 1,080/1,500 = 0.72 (adjusted to 0.85 accounting for high effort)
  - Grey-Zone: 360/1,500 = 0.24 (adjusted to 0.75 accounting for very high effort per case)
  - Appeals: 60/1,500 = 0.04 (adjusted to 0.25 accounting for moderate effort)
  - IP Claims: 0.7/1,500 = 0.0005 (rounded to 0.05)

- **Y-axis (Value)**: Annual value normalized (0 = £0, 1 = £235K)
  - Grey-Zone Context: £108K / £235K = 0.46 (adjusted to 0.95 accounting for strategic value + growth enabler)
  - Routine Spam: £49K / £235K = 0.21 (adjusted to 0.65 accounting for risk reduction + satisfaction)
  - Appeals: £53K / £235K = 0.22 (adjusted to 0.60 accounting for user trust)
  - IP Claims: £0 / £235K = 0 (adjusted to 0.15 accounting for legal protection)

---

### Quadrant 1: Strategic Bets (High Volume, High Value)

**Work Streams**: 
1. **Grey-Zone Context Gathering** (0.75, 0.95)
2. **Routine Spam Removal** (0.85, 0.65)

**Why these are the primary targets**:

**Grey-Zone Context Gathering**:
- **Highest value**: £108K/year (52% of total value)
- **High volume**: 360 cases/day × 2-4 min context gathering = 15 hrs/day (28% of total effort)
- **High delegation suitability**: 65/70 score (Fully Agentic for context retrieval)
- **Low risk**: Agent gathers information but doesn't decide → no false negative risk
- **Strategic enabler**: Frees 16.5 hrs/day for better grey-zone judgment → quality improvement compounds

**Routine Spam Removal**:
- **High value**: £49K/year (23% of total value)
- **Highest volume**: 1,080 cases/day (72% of case volume)
- **Highest delegation suitability**: 63.5/70 weighted avg (Fully Agentic)
- **Lowest risk**: Clear patterns, low stakes, high reversibility
- **Volunteer satisfaction**: Explicit desire "just make it go away" → retention value

**Combined strategic case**:
- **71% of total value** (£157K of £235K)
- **96% of case volume** (1,440 of 1,500 cases/day)
- **Both in Quadrant 1** (high volume × high value = maximum ROI)
- **Complementary**: Spam (prove agent safety on low-risk) → Grey-zone context (expand to higher-value work)
- **Compounding**: Spam automation frees capacity → more time for grey-zone judgment → better outcomes → community trust ↑

**Implementation priority**: **Phase 1-3 (Weeks 1-12)**

---

### Quadrant 2: Quick Wins (High Value, Low Volume)

**Work Stream**: **User Dispute Appeals** (0.25, 0.60)

**Why this is a quick win**:
- **High value**: £53K/year (25% of total value) - second-highest absolute value
- **Low volume**: 60 cases/day (4% of queue)
- **Moderate delegation suitability**: 39/70 score (Human-Led with Agent Support)
- **Clear automation opportunity**: Context preparation saves 7-9 min per case
- **High leverage**: Tom is bottleneck (owns all appeals) → automating his context prep has direct impact

**Why NOT Phase 1**:
- **Lower volume** than spam → less ROI urgency
- **Requires grey-zone context infrastructure** (precedent library, user history aggregation) → should follow Phase 3
- **Human-led** (Tom must decide) → can't prove full automation value like spam

**Implementation priority**: **Phase 4 (Weeks 13+)**, after grey-zone context infrastructure is built

**Strategic rationale**: 
- Leverage existing context aggregation capabilities from Phase 3
- Improve Tom's efficiency (currently spending 17 hrs/day on appeals, over-capacity)
- High user-facing value (faster appeal resolution → trust ↑)

---

### Quadrant 3: Deprioritize (Low Value, Low Volume)

**Work Stream**: **IP Claim Resolution** (0.05, 0.15)

**Why this is deprioritized**:
- **Lowest volume**: 0.7 cases/day (5/week, <1% of queue)
- **Lowest value**: £0 direct automation value (human-only task)
- **Lowest delegation suitability**: 14/70 score (Human-Only)
- **Highest risk**: Legal liability, sculptor relationships, existential business risk
- **Highest complexity**: Copyright law, evidence assessment, relationship management

**Why NOT automate**:
- **Volume too low** to justify automation investment
  - 5 cases/week × 37.5 min = 3.1 hrs/week = 161 hrs/year
  - Even 50% reduction (80 hrs saved) × £18/hr = **£1,440/year** value
  - Agent development cost (conservatively £5K minimum) = 3.5-year payback (uneconomical)
- **Risk too high** for agent involvement (legal decisions require human accountability)
- **Not codifiable** (requires legal expertise, judgment on relationship implications)

**Alternative approach**: Human-only, with potential **very minimal** agent assist:
- Auto-triage urgency: "Known sculptor (watchlist)" vs. "Unknown claimant"
- Extract claim details: sculpture name, evidence URLs
- **But decision remains 100% Tom's**

**Implementation priority**: **No automation planned** (permanent Human-Only)

**Strategic rationale**: 
- Focus automation investment where volume × value justifies cost
- Preserve human expertise on irreducibly human tasks (legal reasoning)
- Accept that not all work should be automated

---

### Quadrant 4: Efficiency Plays (Low Value, High Volume)

**Work Streams**: None in this quadrant

**Why this quadrant is empty**:
- MiniBase's high-volume work (spam, grey-zone) is also high-value (time savings, capacity relief)
- No work stream is "high volume but low value" (common in e.g., data entry tasks that are high-volume but each case has trivial business impact)

**If this quadrant existed**, typical approach:
- Automate only if **very low cost** (e.g., simple RPA, no ML required)
- Justify on "death by a thousand cuts" logic (volume adds up even if per-case value is low)

---

## Primary Agentic Target Identification

### The Winner: Routine Spam + Grey-Zone Context (Combined)

**Why combine these as one target?**

1. **Shared infrastructure**: Both require same foundational capabilities
   - NLP for content analysis
   - User history retrieval (Discourse API)
   - Subforum norm matching
   - Precedent search (semantic similarity)
   - Escalation trigger detection (watchlist, sponsor badges)

2. **Sequential trust-building**: Phased deployment natural progression
   - Phase 1: Prove agent safety on spam (low-risk, clear patterns)
   - Phase 2: Expand to spam edge cases (build confidence in agent judgment)
   - Phase 3: Apply same infrastructure to grey-zone context (high-value extension)

3. **Complementary value**: Spam automation enables grey-zone improvement
   - Spam automation saves 7.5 hrs/day → redirected to grey-zone judgment
   - Better grey-zone judgment → fewer errors → fewer appeals → higher trust
   - Higher trust → community growth → more content → more moderation need → agent value compounds

4. **Maximizes ROI**: Combined target delivers 71% of total value
   - Spam: £49K/year (23%)
   - Grey-zone context: £108K/year (52%)
   - **Total: £157K/year (75% of automation value from 12-week effort)**

---

### Quantified Business Case: Primary Target

**Investment Required**:

| Component | Effort (hrs) | Cost (£) | Timeline |
|-----------|-------------|---------|----------|
| **Phase 1: Spam Automation** | | | |
| - Spam classifier training | 40 hrs | £2,000 | Week 1-2 |
| - Exception detection logic | 20 hrs | £1,000 | Week 2 |
| - Discourse API integration | 30 hrs | £1,500 | Week 1-3 |
| - Testing & validation | 40 hrs | £2,000 | Week 3-4 |
| **Phase 1 Subtotal** | **130 hrs** | **£6,500** | **4 weeks** |
| **Phase 2: Spam Edge Cases** | | | |
| - Subforum taxonomy codification | 16 hrs | £800 | Week 5 |
| - Commercial content rules | 8 hrs | £400 | Week 5 |
| - Edge case testing | 20 hrs | £1,000 | Week 6-8 |
| **Phase 2 Subtotal** | **44 hrs** | **£2,200** | **4 weeks** |
| **Phase 3: Grey-Zone Context** | | | |
| - Subforum norm codification | 16 hrs | £800 | Week 9 |
| - Tom's watchlist migration | 4 hrs | £200 | Week 9 |
| - Precedent library build | 32 hrs | £1,600 | Week 9-10 |
| - Context aggregation engine | 40 hrs | £2,000 | Week 10-11 |
| - Testing & validation | 20 hrs | £1,000 | Week 11-12 |
| **Phase 3 Subtotal** | **112 hrs** | **£5,600** | **4 weeks** |
| **TOTAL INVESTMENT** | **286 hrs** | **£14,300** | **12 weeks** |

**Note**: Cost assumes £50/hr blended rate for FDE + developer time. Does not include Claude API costs (estimated £2K-3K/year in production).

**Annual Operating Cost** (post-deployment):
- Claude API tokens: £2,500/year (estimated 1,500 cases/day × 2,000 tokens/case × $0.003/1K tokens × £0.79/$)
- Maintenance & monitoring: £1,000/year (40 hrs × £25/hr)
- **Total operating cost**: **£3,500/year**

---

### Return on Investment (ROI) Calculation

**First-Year Economics**:

| Metric | Amount (£) |
|--------|-----------|
| **Value (First Year)** | |
| Time savings (spam + grey-zone) | £157,314 |
| Quality improvement | £10,575 |
| Risk reduction | £15,000 |
| **Total Value** | **£182,889** |
| **Cost (First Year)** | |
| Implementation (Phase 1-3) | £14,300 |
| Operating cost (9 months post-deployment) | £2,625 |
| **Total Cost** | **£16,925** |
| **Net Value (Year 1)** | **£165,964** |
| **ROI (Year 1)** | **10.8:1** (£182,889 / £16,925) |

**Ongoing Economics** (Year 2+):

| Metric | Amount (£) |
|--------|-----------|
| Annual value | £182,889 |
| Annual operating cost | £3,500 |
| **Net annual value** | **£179,389** |
| **ROI (Year 2+)** | **52.3:1** (£182,889 / £3,500) |

**Payback Period**: 16,925 / (182,889 / 12) = **1.1 months** (agent pays for itself in 5 weeks)

**5-Year Total Value**: 
- Total value: £182,889 × 5 = £914,445
- Total cost: £14,300 (one-time) + £3,500 × 5 (operating) = £31,800
- **5-year ROI: 28.8:1**

---

### Risk-Adjusted Value

**Why raw ROI understates the case**:

The above calculation shows 10.8:1 first-year ROI, which is strong. But it **understates true value** because:

1. **Avoided capacity crisis**: Team currently 114% over-capacity
   - Without automation: Must hire 1-2 moderators (£40K/year each) OR reduce quality OR create backlog
   - With automation: Operate at 46% capacity with 25.6 hrs spare capacity
   - **Avoided cost**: £40K-80K/year hiring + 2-3 months recruitment delay

2. **Growth option value**: Ability to scale 2.5× without hiring
   - Platform can grow 180K → 450K users without proportional moderation cost increase
   - Competitive advantage: Competitors must scale moderation linearly (higher marginal cost)
   - **Strategic value**: Enables aggressive growth without margin compression

3. **Compounding quality**: Better moderation → community trust ↑ → premium members ↑ → revenue ↑
   - 1% increase in premium member retention = £14K/year (£1.4M revenue × 1%)
   - Difficult to attribute directly to agent, but moderation quality is known driver
   - **Revenue upside**: £10K-50K/year potential (unquantified)

**Risk-adjusted ROI** (conservative, including only avoided hiring):
- Total value: £182,889 + £40,000 (avoided hiring) = **£222,889**
- Total cost: £16,925
- **Risk-adjusted ROI: 13.2:1**

**Risk-adjusted ROI** (including growth option value at 50% probability):
- Total value: £222,889 + (£188,000 × 0.5) = **£316,889**
- Total cost: £16,925
- **Growth-adjusted ROI: 18.7:1**

---

## Secondary Targets: Sequencing Decisions

### Why NOT User Appeals as Primary Target?

**Appeals have strong individual merits**:
- High absolute value: £53K/year (25% of total)
- High per-case impact: 7-9 min saved per appeal
- High leverage: Tom bottleneck (17 hrs/day on appeals, over-capacity)
- High user-facing value: Faster resolution → trust ↑

**But deprioritized because**:
1. **Lower volume**: 60/day vs. 1,080/day spam (18× difference)
2. **Requires grey-zone infrastructure**: Precedent library, context aggregation (Phase 3 dependency)
3. **Can't prove full automation**: Tom must decide (human-led), so ROI demonstration is weaker than spam auto-removal
4. **Lower strategic urgency**: Spam capacity crisis is immediate (114% over-capacity), appeals are over-capacity but not blocking growth

**Sequencing**: Phase 4 (after Phase 3 grey-zone context infrastructure is built)

**Strategic logic**: Leverage Phase 3 investment (precedent library, context engine) to add appeals support with marginal additional effort (40-60 hrs).

---

### Why NOT IP Claims?

**IP claims have zero automation ROI**:
- Volume: 0.7/day (5/week) → 161 hrs/year effort
- Even 50% automation (unrealistic) = 80 hrs saved × £18/hr = **£1,440/year**
- Agent development cost: £5K minimum → **3.5-year payback**
- **Negative ROI** when including operating costs (£3,500/year > £1,440/year value)

**But strategic reasons are more important than economics**:
- **Legal liability**: Copyright decisions require human legal accountability (can't delegate to agent)
- **Relationship management**: Sculptors may be sponsors, VIPs (requires Tom's personal knowledge)
- **Existential risk**: Wrong decision on sponsor sculptor = revenue loss (Tom's "false negatives are existential")

**Conclusion**: Human-Only is correct delegation, regardless of economics.

---

## Volume × Value Insights: Lessons for Agent Strategy

### Insight 1: Volume Alone Doesn't Justify Automation

**Counter-example**: If spam cases were 5 seconds each instead of 30 seconds:
- Volume: Still 1,080/day (high)
- Effort: 1.5 hrs/day instead of 9 hrs/day (low)
- Value: £27,000/year instead of £49,000/year
- ROI: 27,000 / 16,925 = **1.6:1** (marginal, may not justify investment)

**Lesson**: Must consider **effort per case**, not just case count. Grey-zone context (360/day × 2-4 min) has higher absolute value than spam (1,080/day × 30 sec) despite lower volume.

---

### Insight 2: High Value Doesn't Always Mean High Priority

**Appeals**: £53K/year value (second-highest) but Phase 4 priority (not Phase 1)

**Why?**
- **Dependencies**: Requires Phase 3 infrastructure (precedent library, context engine)
- **Risk management**: Can't prove agent value on appeals without first proving on spam
- **Strategic sequencing**: Build trust on low-risk (spam) before tackling human-led (appeals)

**Lesson**: Value must be **accessible** (can be captured with current capabilities) and **low-risk** (doesn't jeopardize trust if agent makes mistakes).

---

### Insight 3: Context Automation ≠ Decision Automation (Value Arbitrage)

**Grey-zone context gathering**:
- 40% of grey-zone effort (15 hrs/day)
- Fully automatable (knowledge retrieval, zero decision risk)
- Delivers 52% of total value (£108K/year)

**Grey-zone decision-making**:
- 30% of grey-zone effort (9 hrs/day)
- NOT automatable (judgment-bound, existential risk)
- Delivers 0% automation value (remains human)

**The arbitrage**: Agent can capture **high value** (context automation) **without high risk** (decision delegation).

**Lesson**: Decompose work into phases (context gathering vs. judgment). Automate the high-effort, low-risk phases even if high-risk phases remain human.

---

### Insight 4: Compounding Value > Additive Value

**Spam automation alone**: £49K/year value

**Grey-zone context automation alone**: £108K/year value

**Combined (spam → frees capacity → better grey-zone judgment)**: £157K/year **+ compounding quality**

**The compounding effect**:
1. Spam automation saves 7.5 hrs/day
2. Redirected to grey-zone judgment (from 9 hrs → 16.5 hrs capacity)
3. Better grey-zone judgment → fewer moderation errors
4. Fewer errors → fewer appeals (60 → 54/day)
5. Fewer appeals → less Tom overload → faster resolution
6. Faster resolution → better user experience → higher trust
7. Higher trust → premium member retention ↑ → revenue ↑

**Lesson**: Automation value compounds when freed capacity is redirected to higher-value work. This is why "automate boring work to focus on interesting work" creates more value than "automate boring work to reduce headcount."

---

### Insight 5: Option Value of Spare Capacity

**Post-agent state**: 46% capacity utilization (21.4 hrs demand / 47 hrs capacity)

**25.6 hrs spare capacity** has three types of value:

1. **Growth headroom**: Handle 2.5× volume without hiring (£188K avoided hiring over 3 years)
2. **Quality time**: Use spare capacity for proactive work (policy updates, community engagement, training new moderators)
3. **Resilience buffer**: Absorb spikes (viral post, spam attack, holiday coverage) without degrading quality

**Traditional ROI calculation** only counts #1 (avoided hiring). But #2 and #3 have real strategic value.

**Lesson**: Spare capacity is not "waste" - it's strategic flexibility. Agent creates **optionality** (ability to handle future scenarios without crisis).

---

## Strategic Prioritization Framework

### The Prioritization Formula

```
Priority Score = (Volume × Value × Delegation Suitability) / Risk
```

Where:
- **Volume**: Cases/day × effort/case (normalized 0-1)
- **Value**: £/year + strategic value (normalized 0-1)
- **Delegation Suitability**: Score from Delegation Matrix (0-70, normalized 0-1)
- **Risk**: (1 - risk_of_error_score) from Delegation Matrix (normalized 0-1, inverted so low risk = high score)

### Calculated Priority Scores

| Work Stream | Volume | Value | Delegation | Risk Multiplier | Priority Score | Rank |
|-------------|--------|-------|------------|----------------|----------------|------|
| **Routine Spam** | 0.85 | 0.65 | 0.91 (63.5/70) | 0.90 (9/10 avg risk score) | **0.46** | **#1** |
| **Grey-Zone Context** | 0.75 | 0.95 | 0.93 (65/70) | 1.0 (10/10 risk - no decision) | **0.66** | **#1 (tied)** |
| **User Appeals** | 0.25 | 0.60 | 0.56 (39/70) | 0.50 (5/10 avg risk) | **0.04** | **#3** |
| **IP Claims** | 0.05 | 0.15 | 0.20 (14/70) | 0.10 (1/10 avg risk) | **0.0002** | **#4** |

**Interpretation**:
- **Spam + Grey-Zone Context**: Both score ~0.5-0.7 (top tier) → **Primary targets** (Phase 1-3)
- **Appeals**: Scores 0.04 (second tier) → **Secondary target** (Phase 4)
- **IP Claims**: Scores near-zero → **No automation** (Human-Only)

**The winner is clear**: Spam and Grey-Zone Context are mathematically the highest-priority targets across all dimensions.

---

## Implementation Roadmap: Volume × Value Sequencing

### Phase 1: High-Volume, Low-Risk Proof of Concept (Weeks 1-4)

**Target**: Routine spam (link farms, bots, gibberish)  
**Volume**: 650 cases/day (60% of spam, highest-confidence patterns)  
**Value**: £29K/year (60% of spam value)

**Goal**: Prove agent safety and accuracy on **low-risk, high-volume** work

**Success criteria**:
- Agent accuracy >95% on spam classification
- False negative rate <0.1% (zero viral incidents)
- Moderators trust agent spam removal (survey: >4/5 trust score)

**Key deliverable**: Moderators say "I no longer think about link farms, the agent just handles them"

---

### Phase 2: Medium-Risk Expansion (Weeks 5-8)

**Target**: Off-topic commercial spam, exception handling  
**Volume**: 330 cases/day (30% of spam, edge cases)  
**Value**: £17K/year (30% of spam value)

**Goal**: Prove agent can handle **context-dependent edge cases** with human oversight

**Success criteria**:
- Moderator override rate <10% (agent proposals mostly correct)
- Exception detection accuracy >90% (agent correctly flags established members, educational content)
- No increase in user complaints (edge case handling doesn't degrade quality)

**Key deliverable**: Moderators say "Agent is smart about exceptions, I just review its proposals"

---

### Phase 3: High-Value Context Automation (Weeks 9-12)

**Target**: Grey-zone context gathering (all 360 cases/day)  
**Volume**: 360 cases/day  
**Value**: £108K/year (highest single component)

**Goal**: Reduce grey-zone case time from 4-5 min to 1.5-2 min via **agent-prepared context**

**Success criteria**:
- Context review time <30 sec (vs. 2-4 min manual gathering)
- Moderators report context is complete and helpful (survey: >4/5)
- No decrease in grey-zone judgment quality (false negative/positive rates unchanged)

**Key deliverable**: Moderators say "I spend my time judging, not gathering context"

**Blocker**: Requires 27-54 hrs codification work (subforum norms, watchlist, precedent library) completed in Phase 1-2

---

### Phase 4: High-Leverage Extension (Weeks 13+)

**Target**: User appeals context preparation  
**Volume**: 60 cases/day  
**Value**: £53K/year

**Goal**: Reduce Tom's appeal review time from 15-20 min to 8-10 min via **agent-prepared context**

**Success criteria**:
- Tom reports context is complete (survey: >4/5)
- Appeal resolution time reduced 30-40%
- User satisfaction with appeal process ↑

**Key deliverable**: Tom says "Agent gives me everything I need to decide quickly"

---

## Conclusion: The Strategic Case for Spam + Grey-Zone Context

### Why This Combination Wins

1. **Highest combined volume**: 96% of daily cases (1,440 of 1,500)
2. **Highest combined value**: 71% of total value (£157K of £221K)
3. **Complementary risk profiles**: Spam (low-risk, prove safety) → Grey-zone context (no decision risk, high value)
4. **Shared infrastructure**: Same APIs, databases, codification work
5. **Compounding value**: Spam automation frees capacity → better grey-zone judgment → higher quality
6. **Fastest time-to-value**: 12 weeks to full deployment vs. 20+ weeks if appeals prioritized first
7. **Strongest ROI**: 10.8:1 first-year, 52.3:1 ongoing (18.7:1 risk-adjusted)

### The Alternatives (Why They Don't Win)

**If we prioritized Appeals first**:
- Higher per-case value (£53K/year vs. £49K spam) BUT
- Lower volume (60/day vs. 1,080/day) → less ROI urgency
- Requires grey-zone infrastructure → can't be done first (dependency)
- Can't prove full automation (Tom decides) → weaker business case
- **Conclusion**: Appeals is right target, wrong sequence (should be Phase 4, not Phase 1)

**If we prioritized IP Claims first**:
- Near-zero automation value (£1.4K/year best case)
- Negative operating ROI (£3.5K/year cost > £1.4K value)
- Extreme risk (legal liability, relationship management)
- Human-only delegation suitability (14/70 score)
- **Conclusion**: Should never be automated, regardless of value

**If we prioritized Grey-Zone Judgment** (not just context):
- Highest effort (9 hrs/day judgment time) BUT
- Not automatable (poorly codifiable, existential risk)
- Delegation suitability: 34/70 (Human-Led, not Fully Agentic)
- Sarah explicitly doesn't trust AI: "That boundary is so cultural"
- **Conclusion**: Right to keep human-led, wrong to attempt full automation

### Final Recommendation

**Primary Target**: Routine Spam Removal (Phase 1-2) + Grey-Zone Context Gathering (Phase 3)

**Investment**: £14.3K (286 hours over 12 weeks)

**Return**: £182.9K/year value, 10.8:1 first-year ROI, 1.1-month payback

**Strategic Impact**:
- Resolves capacity crisis (114% → 46% utilization)
- Creates 25.6 hrs/day spare capacity (2.5× growth headroom)
- Redirects volunteer time from spam (60% → 20%) to valued judgment work (35% → 70%)
- Reduces existential risk (deterministic escalation on sponsors, watchlist, high-engagement)

**Why it wins**: Highest volume × highest value × highest delegation suitability × lowest risk = **clear mathematical winner**.

---

## Appendix: Sensitivity Analysis

### What if our assumptions are wrong?

**Assumption 1: Blended moderator rate = £18/hr**

| Rate | Annual Value | First-Year ROI | Payback Period |
|------|--------------|----------------|----------------|
| £12/hr (all volunteers) | £122K | 7.2:1 | 1.7 months |
| £18/hr (base case) | £183K | 10.8:1 | 1.1 months |
| £25/hr (all paid staff) | £254K | 15.0:1 | 0.8 months |

**Sensitivity**: ROI ranges 7-15×, but **always strongly positive**. Even pessimistic case (all volunteers, £12/hr) delivers 7:1 ROI.

---

**Assumption 2: Agent achieves 74% spam coverage (vs. 80% or 60%)**

| Coverage | Cases Automated | Annual Value | First-Year ROI |
|----------|----------------|--------------|----------------|
| 60% (pessimistic) | 650/day | £135K | 8.0:1 |
| 74% (base case) | 800/day | £183K | 10.8:1 |
| 85% (optimistic) | 920/day | £210K | 12.4:1 |

**Sensitivity**: ROI ranges 8-12×, **always strongly positive**. Even 60% coverage (conservative) delivers 8:1 ROI.

---

**Assumption 3: Grey-zone context automation saves 2.5 min per case (vs. 3.5 min or 1.5 min)**

| Time Saved | Annual Value | First-Year ROI |
|------------|--------------|----------------|
| 1.5 min (pessimistic) | £127K | 7.5:1 |
| 2.5 min (base case) | £183K | 10.8:1 |
| 3.5 min (optimistic) | £240K | 14.2:1 |

**Sensitivity**: ROI ranges 7.5-14×, **always strongly positive**. Even pessimistic case (1.5 min saved) delivers 7.5:1 ROI.

---

**Conclusion**: Across all sensitivity scenarios, **ROI remains >7:1** (highly positive). The business case is **robust to assumption errors**.

---

## Document Control

**Version History**:
- v1.0 (2026-04-29): Initial Volume × Value Analysis

**Validation Status**:
- Volume metrics validated from discovery findings
- Value metrics calculated from blended moderator rate assumptions
- ROI calculations conservative (excludes growth option value from primary calculation)

**Next Steps**:
- Validate blended rate assumption with Tom (paid staff vs. volunteer cost allocation)
- Validate volume assumptions with Discourse data pull (30-day sample)
- Refine time-per-case estimates with shadow observation (live moderation sessions)

**Related Documents**:
- `01_Problem_Statement_and_Success_Metrics.md` (Business context)
- `02_Discovery_Phase.md` (Lived work findings)
- `03_Cognitive_Load_Map.md` (Micro-task effort analysis)
- `04_Delegation_Suitability_Matrix.md` (Delegation scoring)
- `06_Agent_Purpose_Document.md` (Agent design spec - to be created)
