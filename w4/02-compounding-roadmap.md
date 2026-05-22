# Deliverable #2 — Compounding Roadmap (3 Waves)

**Author:** Krzysztof Wilniewczyc, FDE
**Date:** 2026-05-22
**Anchor:** Wave 1 is MedFlex matching (Week 3). Wave 2 extends MedFlex into nurse onboarding & credential lifecycle. Wave 3 turns MedFlex into a multi-agent operations stack (Matching + Credential-watcher + Coverage-risk agents).

---

## 1. The compounding thesis (one paragraph)

A first FDE engagement spends most of its budget on two kinds of work that compound: **domain integrations** (the ServiceNow adapter, the credential database, the nurse profile schema, the hospital adapter) and **platform plumbing** (LLM call wrapper, HITL queue, eval harness, cost meter, audit log). If the next engagement is *in the same business* — same data, same stakeholders, same regulatory shape — both layers carry. The second engagement only pays for the new capability and the new domain logic. Compounding kicks in on Wave 2 (one engagement's payback) and is fully realised by Wave 3, where three coordinating agents share a single platform and a single MedFlex domain model. Past Wave 3 the platform plateaus and the leverage shifts from engineering compounding to commercial compounding (faster sales cycles to other staffing clients).

---

## 2. The three waves

### Wave 1 — MedFlex Matching (months 0–2)

**Scope.** Healthcare staffing — agentic matching engine for shift requests. Planned matching + urgent rematching capability specs. 8-week build per the scenario engagement framing.

**What gets built (new, from scratch):**

*Platform plumbing (engineering-layer assets):*
- LLM call wrapper (retry, timeout, JSON validation, cost meter, circuit breaker)
- Confidence-threshold framework (config-driven escalation rules; thresholds tuned per workflow)
- HITL queue + coordinator dashboard
- State machine library (offer → lock → confirm; same engine handles planned and urgent modes)
- Structured-API integration template (the FastAPI thin-wrapper pattern reused later)
- Eval harness (golden tests, regression detection, threshold-drift alerts)
- Prompt registry with version control
- Notification rails (SMS + email send infrastructure)
- Cost/token meter + daily reporting + cost circuit breaker
- Trust-ramp framework (weeks 1–2 manual → week 8 auto)

*MedFlex domain integrations (the assets that compound into Waves 2 and 3):*
- **Credential pre-flight engine** — checks a nurse has the licenses, certifications, immunizations required for a target shift. Built for matching; reused by onboarding and credential-watching.
- **Nurse profile schema + repository** — canonical record format (demographics, licenses, certs, prior pairings, preferences). Every downstream agent reads and writes this.
- **Hospital profile schema + adapter** — hospital preferences, policies, ward-specific requirements. Reused for onboarding readiness and coverage forecasting.
- **ServiceNow integration adapter** — read shift requests, write back match decisions. Reused for onboarding tickets and coverage alerts.
- **Immutable audit log** — per-decision record with reasoning citations. Extended (not rebuilt) for onboarding and credential events.

**Domain-specific (not reusable past Wave 1):**
- MedFlex credential taxonomy *as encoded in matching rules*
- Planned-matching system prompt, urgent-rematching system prompt
- MedFlex matching eval set (~500 historical tickets)

**Build cost:** ~$95,000 (per Deliverable #1). Of that, ~$72,000 is platform + MedFlex-domain-integration work that compounds into Waves 2 and 3 (see §3 matrix and §4 cost trajectory); ~$23,000 is matching-specific build that does not compound (system prompts, eval set, trust-ramp tuning).

### Wave 2 — MedFlex Nurse Onboarding & Credential Lifecycle (months 3–5)

**Scope.** Two related workflows that are currently manual paperwork at MedFlex:

1. **Nurse onboarding** — a new contractor uploads license PDFs, certification cards, immunization records, BLS/ACLS proofs, references. Today an onboarding coordinator hand-keys this into the nurse repository over 3–5 working days. An onboarding agent extracts the structured data, cross-checks against state nursing-board APIs, and produces a ready-to-match profile that goes through HITL approval. Target: 24-hour onboarding for clean dossiers.
2. **Credential lifecycle** — licenses and certs expire. Today MedFlex discovers expired credentials at match time (the worst possible moment — the Wave 1 credential pre-flight currently *blocks* the match). A credential-watcher service tracks every credential's expiry, sends reminders at 60/30/7 days, auto-refreshes from state boards where APIs allow, and flags at-risk credentials before they affect matching.

**What gets reused from Wave 1 (the compounding):**

| Wave 1 asset | How Wave 2 uses it |
|---|---|
| Credential pre-flight engine | Re-run at onboarding time (not just match time). Same logic; new trigger. |
| Nurse profile schema + repository | Wave 2 *creates* records in the core schema Wave 1 *reads*. New document metadata can be added as an extension, not a rewrite. |
| Hospital profile adapter | Used to validate which hospitals an onboarded nurse can be matched to (ward credentials, immunization requirements per facility). |
| ServiceNow adapter | Onboarding requests come through ServiceNow tickets; renewal alerts are written back as ServiceNow tasks. Same adapter, new ticket types. |
| Immutable audit log | Extended with onboarding-event types and credential-state-change events. Same store, same regulator-readable format. |
| LLM call wrapper, prompt registry, cost meter, circuit breaker | No change. |
| HITL queue + coordinator dashboard | Tweaked: onboarding ops team needs a "dossier review" view; renewal team needs a "credentials at risk" view. ~2 days of dashboard work, not a rebuild. |
| Eval harness | Add onboarding + renewal golden sets. Framework unchanged. |
| Structured-API integration template | Reused for every state-board API adapter (each state board is one more thin wrapper). |
| Trust-ramp framework | Onboarding starts cold-start the same way matching did — full HITL for the first batch of dossiers, ramping to high-confidence auto-approval. |
| Notification rails | Email reminders for credential renewals reuse the same rails. |

**What gets newly built (becomes Wave 3 platform asset):**

- **Document OCR pipeline** (license PDFs, immunization cards, scanned forms — handles printed + handwritten + photographed sources).
- **State nursing-board API adapters** — one thin wrapper per state, reusing the Wave 1 structured-API template. Initial scope: top 5 states by MedFlex volume (~80% coverage).
- **Renewal-tracking state machine** (active → 60d-warning → 30d-warning → 7d-warning → expired-grace → expired-locked). Reuses the Wave 1 state machine library.
- **Dossier completeness checker** (deterministic — what's missing? what's expired? what needs HITL?).

**Domain-specific (not reusable past Wave 2):**
- State-by-state credential expectations and BLS/ACLS/PALS renewal cadences
- Per-state license board API quirks
- Onboarding coordinator system prompt + renewal-reminder prompts
- Onboarding + renewal eval sets

**Build cost:** ~$58,000. Standalone build of these two workflows from zero (no Wave 1 platform) would cost ~$95,000 — the credential pre-flight engine, nurse schema, ServiceNow adapter, HITL queue, audit log, and trust-ramp framework would all need to be built from scratch.

**Saving vs standalone: ~$37,000.**

### Wave 3 — MedFlex Multi-Agent Operations (months 6–8)

**Scope.** Per ATX scoring §Step 4 — *"Wave 3+: multi-agent workflows, agents that coordinate with each other, platform-level optimisation"* — Wave 3 turns MedFlex's day-to-day operations into a coordinated agent stack:

- **Matching agent** (the Wave 1 agent, with its core ranking logic unchanged).
- **Credential-watcher agent** (the Wave 2 service, promoted to first-class agent — it now proactively pushes alerts into the matching flow: *"nurse N is about to lose her ACLS in 30 days; if you match her to a cardiology shift after Dec 12 it will fail credential pre-flight"*).
- **Coverage-risk agent** (new — forecasts under-staffed shifts 3–7 days out by reading current matched coverage against historical demand patterns; pre-fires urgent-rematch flows before the gap becomes critical).

The three agents coordinate via an inter-agent message bus and read/write a shared state store. The matching agent can *ask* the credential-watcher whether a candidate's credentials are stable through a shift window. The coverage-risk agent can *trigger* the matching agent to pre-fill candidates for shifts that are statistically likely to need them.

**What gets reused from Waves 1 + 2:**

| Asset | Source | Reuse in Wave 3 |
|---|---|---|
| Credential pre-flight engine | Wave 1 | Used by the Credential-watcher agent for "stability through window" checks. |
| Nurse profile + repository | Wave 1 | Single source of truth for all three agents. |
| Hospital profile + adapter | Wave 1 | Coverage-risk agent reads hospital demand patterns. |
| ServiceNow adapter | Wave 1 | All three agents write back to ServiceNow (matches, alerts, forecasts). |
| Audit log | Wave 1 (extended by Wave 2) | All three agents log decisions to the same store, with the same regulator-readable format. |
| LLM call wrapper, prompt registry, cost meter, circuit breaker | Wave 1 | No change. |
| HITL queue + dashboard | Wave 1 (extended by Wave 2) | A third view added: "coverage-risk forecasts pending review." |
| Eval harness | Wave 1 (extended by Wave 2) | Per-agent golden sets + cross-agent integration tests. |
| State machine library | Wave 1 | Coverage-risk agent uses it for forecast → alert → action flow. |
| Renewal-tracking state machine | Wave 2 | Underpins the Credential-watcher agent's proactive alerting. |
| State-board API adapters | Wave 2 | Credential-watcher consumes these directly. |
| Document OCR pipeline | Wave 2 | Available if a hospital-side document workflow is added later (not in core Wave 3 scope). |
| Trust-ramp framework | Wave 1 | Coverage-risk agent ramps from advisory-only to auto-trigger over weeks 1–8. |

**What gets newly built (Wave 3-specific platform assets — per ATX §Step 4):**

- **Inter-agent message bus** — lets agents coordinate without hard-coupling. Matching can ask Credential-watcher; Coverage-risk can trigger Matching. Same bus reusable for any future multi-agent MedFlex workflow.
- **Shared state store** — single source of truth for the in-flight match/shift/forecast record across agents.
- **Platform-level cost router** — routes each agent's calls to the cheapest sufficient model (Haiku for Coverage-risk's deterministic forecasts where they suffice; Sonnet for Matching's ranking; Sonnet for Credential-watcher's reasoning over edge cases).
- **Forecasting plumbing** — historical-pattern features pipeline for the Coverage-risk agent (statistical baselines + LLM-on-top for narrative anomaly detection).

**Domain-specific (not reusable past Wave 3):**
- Coverage-risk thresholds (per-hospital and per-ward)
- At-risk credential heuristics (state + cert-type specific)
- Multi-agent orchestration system prompts
- Coverage-risk eval set (historical under-staffing events)

**Build cost:** ~$48,000. Standalone build of three coordinating agents from zero (no Wave 1 or Wave 2 platform) would cost ~$130,000 — every agent would need its own matching/credential/hospital plumbing rebuilt.

**Saving vs standalone: ~$82,000.**

---

## 3. Integration reuse matrix

Each row is an asset. Each cell shows whether the asset is built new (B), reused as-is (R), or reused with tweaks (R+). Days shown are FDE engineering days.

| Asset | Layer | Wave 1 (Matching) | Wave 2 (Onboarding + Credentials) | Wave 3 (Multi-agent ops) |
|---|---|---|---|---|
| LLM call wrapper (retry / timeout / cost meter / circuit breaker) | Platform | **B (3d)** | R | R |
| JSON schema validator | Platform | **B (1d)** | R | R |
| Confidence-threshold framework | Platform | **B (2d)** | R+ (1d tuning) | R+ (1d tuning) |
| HITL queue + coordinator dashboard | Platform | **B (4d)** | R+ (2d new views) | R+ (1d new view) |
| State machine library | Platform | **B (3d)** | R (renewal SM) | R (forecast SM) |
| Structured-API integration template | Platform | **B (1d)** | R (per state board) | R |
| Eval harness (golden tests + regression) | Platform | **B (2d)** | R+ (new eval sets: 1d) | R+ (new eval sets: 1d) |
| Prompt registry + version control | Platform | **B (1d)** | R | R |
| Notification rails (SMS + email) | Platform | **B (2d)** | R+ (renewal templates: 1d) | R |
| Cost/token meter + daily reporting | Platform | **B (1d)** | R | R |
| Trust-ramp framework | Platform | **B (1d)** | R+ (onboarding cadence: 1d) | R+ (coverage-risk cadence: 1d) |
| **Credential pre-flight engine** | MedFlex domain | **B (4d)** | R (triggered at onboarding too) | R (used by Credential-watcher) |
| **Nurse profile schema + repository** | MedFlex domain | **B (3d)** | R (W2 *writes*, W1 *reads*) | R |
| **Hospital profile + adapter** | MedFlex domain | **B (2d)** | R | R |
| **ServiceNow integration adapter** | MedFlex domain | **B (3d)** | R+ (new ticket types: 1d) | R+ (forecast alerts: 1d) |
| **Immutable audit log** | MedFlex domain | **B (2d)** | R+ (onboarding events: 1d) | R+ (cross-agent events: 1d) |
| Document OCR pipeline | MedFlex domain | not used | **B (5d)** | R (if hospital-side workflow added) |
| State nursing-board API adapters | MedFlex domain | not used | **B (7d, 5 states)** | R |
| Renewal-tracking state machine | MedFlex domain | not used | **B (3d)** | R (Credential-watcher core) |
| Dossier completeness checker | MedFlex domain | not used | **B (2d)** | R (extended for shift-window checks) |
| **Inter-agent message bus** | Platform | not used | not used | **B (4d)** |
| **Shared state store** | Platform | not used | not used | **B (3d)** |
| **Platform-level cost router** | Platform | not used | not used | **B (3d)** |
| **Forecasting plumbing (features + baselines)** | MedFlex domain | not used | not used | **B (5d)** |

**Reading the matrix:**

- **Wave 1** builds 16 assets (11 platform + 5 MedFlex-domain) — ~35 FDE days of reusable engineering (~$52.5k at $1,500/day). The reusable asset-layer allocation is higher, ~$72k, because it also includes the one-off platform infrastructure setup from Deliverable #1 (~$15k) and a small reusable share of assessment/design. The remaining ~$23k of the $95k Wave 1 cost is matching-specific build and change work that does *not* compound.
- **Wave 2** reuses every Wave 1 asset (R or R+), builds 4 new assets — ~17 days new build + ~8 days reuse-tuning = ~25 days, ~$38k. The remaining ~$20k is onboarding/renewal-specific build (prompts, eval sets, change management with the onboarding team).
- **Wave 3** reuses every Wave 1 + Wave 2 asset (R or R+), builds 4 new assets — ~15 days new build + ~6 days reuse-tuning = ~21 days, ~$32k. The remaining ~$16k is multi-agent-orchestration-specific build (orchestration prompts, cross-agent eval set, coverage-risk threshold calibration).

The asset pool grows from 16 (Wave 1) to 20 (Wave 2) to 24 (Wave 3). Every new asset is paid for once and amortised over every future MedFlex engagement that needs it.

---

## 4. Cost trajectory

| Wave | Total build cost | Asset-layer work (platform + MedFlex domain) | Wave-specific build | Saving vs standalone |
|---|---|---|---|---|
| Wave 1 — Matching | $95,000 | ~$72,000 | ~$23,000 | baseline (standalone Wave 1 alone: ~$80k, $15k platform premium) |
| Wave 2 — Onboarding + Credentials | $58,000 | ~$38,000 | ~$20,000 | $37,000 (standalone: ~$95k) |
| Wave 3 — Multi-agent operations | $48,000 | ~$32,000 | ~$16,000 | $82,000 (standalone: ~$130k) |
| **Total 3 waves** | **$201,000** | **$142,000** | **$59,000** | **$134,000 vs three standalone builds at ~$305k** |

Three standalone builds (no compounding — every Wave starts from zero) would cost about $305,000. The 3-wave plan costs $201,000 — a **~34% reduction**, banked into a MedFlex asset pool of 24 reusable building blocks.

**The Wave 1 platform premium.**

Wave 1 standalone (build only matching, no abstraction discipline) would cost ~$80,000. Wave 1 done as a *platform-aware* build costs $95,000 — a **$15,000 premium** for proper abstraction and clean separation between MedFlex-domain logic and platform plumbing. That $15,000 is recovered on the very first Wave 2 saving ($37,000). Net positive after one future engagement.

---

## 5. Honest about what is NOT reusable

Roughly **30% of every Wave's cost is wave-specific** — work that does not transfer even within MedFlex:

- **Per-workflow system prompts.** Matching's "rank these candidates" prompt is not the same prompt as onboarding's "extract structured fields from this license PDF." Each new workflow re-authors and tunes its own prompts.
- **Per-workflow eval sets.** Golden tests need real, in-domain examples. Matching's 500-ticket eval set does not validate the onboarding agent.
- **Trust-ramp tuning per workflow.** The ramp from 100% HITL to auto-action has to be re-calibrated for each new workflow because the failure modes are different. Coordinators trust matching after they've seen 4 weeks of clean decisions; they trust credential auto-renewals only after a different 4 weeks of clean decisions in *that* domain.
- **Stakeholder discovery and change management.** Wave 2's onboarding team is not the same group of people as Wave 1's coordinator team. The platform does not shorten the time to gain Kim-from-onboarding's trust. Discovery still costs what discovery costs.
- **Compliance scope check.** Each new workflow touches different parts of HIPAA / state nurse-practice acts / data-residency rules. Wave 1 was about matching decisions; Wave 2 onboarding touches PII at scale; Wave 3 forecasting touches workforce planning. Each gets its own compliance pass.

The compounding is on the **~70% asset-layer portion** (platform plumbing + MedFlex domain integrations). Saying "Wave 3 is 50% cheaper than Wave 1" would be misleading. Saying "Wave 3 spends almost nothing rebuilding the credential engine, the nurse repository, the ServiceNow adapter, the audit log, or the HITL queue, because Waves 1 and 2 already paid for them" is accurate.

---

## 6. How to pick Wave 2 to maximise compounding

A good Wave 2 — inside the same client/account — satisfies three rules:

1. **Reuses the Wave 1 domain integrations.** If the next workflow does not use the credential engine, the nurse schema, the hospital adapter, the ServiceNow adapter, and the audit log, you are *starting another engagement*, not extending this one. Onboarding + credential lifecycle uses all five.
2. **Adds at least one new asset that becomes a Wave 3 prerequisite.** Wave 2's renewal-tracking state machine and state-board API adapters are exactly what the Credential-watcher agent needs in Wave 3. Wave 2 isn't just *cheaper because of Wave 1* — it actively *enables* Wave 3.
3. **Reaches a different stakeholder cohort within the same buyer.** Wave 1's user is the staffing coordinator. Wave 2's user is the onboarding coordinator (and the credentialing team). Wave 3's user is operations leadership. Reaching new internal champions broadens the buyer's commitment to the platform without the discovery cost of a new client.

**Onboarding + Credential Lifecycle fits all three.** It reuses every Wave 1 MedFlex-domain asset, it builds the renewal infrastructure that Wave 3's Credential-watcher will need, and it brings the onboarding/credentialing teams onto the platform as new internal champions.

**A bad Wave 2 would be:** a hospital-side scheduling agent (different buyer entirely, no shared stakeholders, MedFlex's nurse schema is irrelevant) or a single-prompt tweak to matching (no new assets, no compounding). Both look like "another project" rather than "the next stage of this one."

---

## 7. Where compounding plateaus (and what to do then)

Past Wave 3, MedFlex's internal asset pool is largely complete: every nurse-facing workflow shares one nurse profile; every credential workflow shares one credential engine; every coordination need has the message bus. New MedFlex workflows past Wave 3 look like **~$30–40k each** — mostly prompts, eval sets, and ramp tuning.

From that point the compounding shifts from *engineering* compounding (cheaper builds) to *commercial* compounding:

- **Platform-portability into other staffing clients.** The asset layer that is *MedFlex-domain* (credential engine, nurse schema, ServiceNow adapter, audit log) is also *healthcare-staffing-domain* with light adaptation. Selling the platform to a competitor staffing agency reuses 60–70% of the MedFlex domain layer; the new client pays for their own ServiceNow tenancy, their own credential taxonomy variants, and their own eval set, but not for the engine that consumes them.
- **Platform-portability into adjacent verticals.** With deeper investment, the platform-layer assets (LLM wrapper, HITL queue, eval harness, audit log, cost meter, message bus) carry to non-healthcare engagements. The domain layer does not. This is the *next* level of compounding — and it is what the user's separate capstone (ResolveOne, financial services customer resolution) tests as a hypothesis: how much of the platform layer actually carries cross-vertical?

To delay the engineering plateau and stretch Wave 3+'s asset pool, deliberately pick a fourth workflow that needs one new capability future clients will want. Examples that would add genuine platform value beyond Wave 3:

- **Multi-tenant deployment pattern** — needed the first time we serve two staffing clients on the same agent codebase.
- **Active-learning loop** — agent learns from coordinator overrides without prompt rewrites.
- **Real-time streaming pattern** — needed if a hospital partner requires <1-second match latency.
- **Federated retrieval** — needed if a client wants the agent to query their data without it leaving their tenancy.

Each of these would add 5–10 platform days and would amortise across every future engagement that needs them.

---

## 8. One-paragraph summary for the partner

Three workflows built sequentially inside MedFlex — matching, then onboarding + credential lifecycle, then a coordinated multi-agent operations stack — cost about $201,000 against ~$305,000 for the same three built standalone, a 34% reduction banked into a MedFlex asset pool of 24 reusable building blocks. The Wave 1 platform premium ($15,000 of extra abstraction work) pays back inside the first follow-on workflow. About 30% of every Wave remains wave-specific (prompts, eval sets, ramp tuning, stakeholder change management) and does not compound; the compounding is on the 70% asset-layer portion — platform plumbing plus MedFlex-domain integrations like the credential engine, nurse schema, hospital adapter, ServiceNow adapter, and audit log. The compounding plateaus past Wave 3, at which point the leverage shifts from cheaper builds to platform-portability — first into other healthcare-staffing clients, then potentially into adjacent verticals (the cross-vertical hypothesis is what the separate ResolveOne capstone is set up to test).
