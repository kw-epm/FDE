# Deliverable 2 — Engagement Intake & Scope

**Author:** Tamas Kiss
**Engagement:** MedFlex agentic transformation  
**Date:** 2026-05-13
**Gate:** Gate 3 — Final submission

---

### Business context

*[Lifted from `01-analysis.md` §1 Scenario Summary — same text as D1's "The real problem" sub-section. Repeated here for D2 self-containment.]*

MedFlex is a US healthcare staffing agency (~200 employees, 5-state region) that supplies travel nurses to hospital systems on shift contracts. Hospitals submit shift requests via email (dominant channel), web portal, and phone, all converging into a ServiceNow queue; 8 coordinators manually classify free-text requests against MedFlex's structured credential taxonomy and match nurses to shifts by joining four separate stores (profile, availability, request, qualification). Average time-to-fill is 4.2 hours against a target of <1 hour; "mismatch rate" is reported at 7% but conflates qualification error with competitive preference loss (A2); no-show rate is 12% with reactive-only detection. CEO Marcus Reyes (post-Series-B, board pressure for growth) is targeting **$14M → $200M revenue over 24 months**, with the 8-week milestone framed as "start getting money back" rather than full scale. The engagement is to design an agentic transformation of matching + intake-classification + nurse-side coordination, with **speed-to-submit as the primary win/loss driver** in a competitive multi-agency market where hospitals submit to several agencies in parallel and the first qualified candidate frequently wins. Compliance verification, hospital-facing portals, nurse-facing apps, and pricing are explicitly out of scope.

### Stakeholder map

*[Lifted from `01-analysis.md` §2 Stakeholder Map, with PC sign-off pairs appended from `07-discovery-questions.md` §5]*

| Name / Role | Responsibilities | Pain points | Source |
|---|---|---|---|
| **Marcus Reyes — CEO** | Strategic direction; growth from $14M → $200M; HITL placement deferred to FDE | Two failed prior AI projects; board pressure post-Series-B; not technical (operations / growth background); cuts off rambling | BRIEF §1 + §2 |
| **Senior coordinator (10+ years)** | Match nurses to shifts; keep ServiceNow queue empty | Tribal hospital-preference knowledge is uncodified; cross-store join is largest time sink; submission orchestration is parallel and revocation-heavy | BRIEF §1 + A1 + A3 |
| **Junior coordinator (newcomer)** | Same operational mandate | Takes significantly longer to ramp; lacks 10+ year tribal knowledge of hospital fit | §2 |
| **8 coordinators (team)** | ~120 shift-matching *decisions*/coord/day (decisions ≠ shifts filled) | Queue backup = competitive loss; no proactive no-show signal in their tooling | BRIEF §1 |
| **Compliance team** | License / background / training checks against state regulators; nurse onboarding | Operationally separate; legally regulated cadence | BRIEF §1 |
| **Hospital booking staff** | Submit shift requests; pick from agency-supplied candidates | Use multiple agencies in parallel; reject MedFlex bot (Failure 1); ambiguous email requirements | BRIEF §1 + A4-F1 |
| **Travel nurses (registered, credentialled)** | Pick up shifts | Notified via SMS/email only; missed notification = default accept; no-show detected only by hospital phoning in | BRIEF §1 + A1 |
| **Board (implicit; post-Series-B investor)** | Growth oversight | Demanding ~14× revenue lift; 8-week "money back" milestone | BRIEF §1 |
| **Competing staffing agencies (implicit)** | Submit candidates to same hospitals in parallel | Win by speed (first qualified candidate) and prior hospital relationship | BRIEF §1 + A2 + A3 |

Stakeholders involved-but-out-of-design-scope: compliance team (consumed as upstream gate), hospital-IT (channel unchanged), continuing-education renewal team.

**Political-cover sign-off pairs** *(lifted from `07-discovery-questions.md` §5; all 5 USER-CONFIRMED via Phase 7 active-claim checkpoint)*:

| Decision | First sign-off (obvious) | Second sign-off (load-bearing — absence breaks deployment) | Source |
|---|---|---|---|
| **PC-1: D3.2 Fully Agentic parallel submission** | Marcus Reyes (CEO) | MedFlex Legal — without Legal's go-ahead on the PB-3 MSA review, parallel submission against an MSA-restricted hospital is a contractual breach | **USER-CONFIRMED** (endorsed) |
| **PC-2: D2.4 HLAS hospital-preference scoring (cold-start with seniors authoring)** | Marcus Reyes | Senior Coordinator champion (named TBD) — without their explicit endorsement, the pref-store cold-start lacks both authoring authority and the coordinator-trust that A4-F2 mitigation requires | **USER-CONFIRMED** (endorsed) |
| **PC-3: D3.4 atomic revoke cascade — ledger-consistency safety boundary** | FDE Engineering Lead — owns atomicity guarantees, retry logic, and failure-mode design | **Senior Coordinator champion (Kim TBC)** — owns the "do the coordinators see and trust the live state of submissions?" question, which is what makes or breaks adoption when atomicity fails edge-case-style | **USER-CONFIRMED** (revised from AI-drafted Compliance Team Lead — the engineering↔coordinator pairing better reflects where the trust failure lands when the safety boundary breaks; HIPAA / audit-tamper sign-off remains covered by PB-6 / R7.5 / R7.13 governance review, separate from this load-bearing pair) |
| **PC-4: Compliance status consumption as matching precondition** | Compliance Team Lead | Marcus Reyes — without Marcus's explicit sign-off on the read-only consumption boundary, the cross-team political risk that Marcus flagged twice as out-of-scope materialises | **USER-CONFIRMED** (endorsed) |
| **PC-5: Phase 3 advancement (turning on autonomous parallel submission + pref scoring)** | Marcus Reyes — final authorisation on autonomy turn-on, **conditional on the mechanical pre-requisite gates below** | **Senior Coordinator champion (Kim TBC)** — continuing endorsement of team-level trust is the deployment lock | **USER-CONFIRMED** (refined with two-stage gate structure) |

### Constraints (KC-1..KC-13)

*[Lifted verbatim from `06-system-data.md` §1 Known Constraints]*

| ID | Constraint | Source | Category | How it shapes the design | Cross-refs |
|---|---|---|---|---|---|
| **KC-1** | ServiceNow is the single intake queue; tickets carry free-text email bodies, not structured submissions | BRIEF §1; A1 L71-73 | Legacy / Performance | APD §7 Integration 1 (ServiceNow contract); Capability 1 reads `description` field; agent must accept multi-channel raw text | G-1, R7.1, PB-1, ET-1 |
| **KC-2** | 4 separate stores (profile / availability / request / qualification) — access mechanism unknown; one or more may be black-box | BRIEF §2 L55; A2 / SL-052 (assumption) | Legacy / Performance | Primary risk per APD §1e; cross-store retrieval (D2.A) gates on this; pref-store work has a dedicated cold-start track | G-2, R7.2, PB-2, ET-2 |
| **KC-3** | Compliance verification out-of-scope; consumed as read-only precondition; agent does NOT design or query the verification process itself | BRIEF §1 L11; A1 / SL-051 | Compliance / Org-Political | All matching gates on `nurse.compliance_status = "verified"`; Compliance-Reader sibling agent (Wave-1; APD §7-bis) acts as the consumption boundary | G-3, R7.3, PB-4, ET-3 |
| **KC-4** | No hospital-facing agent surface (no chatbot, portal, or interactive ask flow). Channels remain email / portal / phone | BRIEF §1 L33; A4-F1 L129 | Compliance / Org-Political | Agent-authored submission emails sent from MedFlex coordinator account (hospitals see human sender, not bot); clarification text drafted by agent but sent by coordinator | G-4, R7.4, ET-4 |
| **KC-5** | No nurse-facing mobile app. Nurse reach remains via phone / SMS / email | BRIEF §1 L34 | Compliance / Org-Political | Stream 4 (notification) remains SMS/email; D4.2 pre-confirm (Wave-2) operates within these channels | — |
| **KC-6** | HIPAA compliance on Protected Health Information (PHI) attached to credentials, units, certifications | INDUSTRY-STD (HIPAA Privacy Rule 45 CFR Part 164; US healthcare default) | Regulatory | Field-level redaction overlay in audit trail; immutable audit-trail trigger forbids destructive deletes; PHI fields encrypted at rest | G-5, R7.5, PB-6 |
| **KC-7** | 8-week milestone = "start getting money back" (value flow begins), not full $200M scale | BRIEF §1 L25 | Org-Political / Commercial | Phase-gating in V×V §4 anchors Phase 1 read-only at Month 0-4; full operational scale-up at Month 12+; 8-week mark = first Phase-1 read-only delivery | — |
| **KC-8** | Speed-to-submit is the primary win/loss driver in the competitive multi-agency market | BRIEF §1 L28 | Performance | D3.2 (parallel submission) Fully Agentic; D3.4 atomic revoke is the safety boundary that justifies the FA defence; ledger-consistency gate prevents the speed lever degrading match quality | G-8, R7.6, ET-5 |
| **KC-9** | Multi-submission of same nurse to multiple hospitals — operationally standard (A3 L107) but legally / contractually unverified | A3 L107; A6 / SL-056 (assumption) | Legal / Org-Political | Pre-engagement legal review of master service agreements with top-N hospitals is named pre-build blocker; per-hospital block_list field provided for hospitals that demand exclusivity | G-9, R7.7, R10, PB-3 |
| **KC-10** | Coordinator transformation is acceptable; layoff framing is NOT acceptable | BRIEF §2 L58; A4-F2 implication | Org-Political | Coordinator-visible audit trail + show-your-work + HITL-queue per A4 L143-145; transformation narrative is a Wave-1 deliverable, not a Wave-2 afterthought | G-10, R7.8, PB-5, ET-6 |
| **KC-11** | The 7% mismatch metric is unsplittable today; no structured rejection log exists | A2 L95 | Performance / Data quality | Rejection-log instrumentation is a Phase-1 first-class deliverable; KPI design rests on splitting it (per SL-077 USER-CONFIRMED guidance) | G-11, R7.9, PB-9, ET-7 |
| **KC-12** | Coordinator trust is in deficit from Failure 2 (recommendation engine non-adoption + job-security concern) | A4-F2 L137 | Org-Political | Wave-1 starts read-only (DSM §6 Phase 1); show-your-work + per-shift Component-1 accuracy visible; change-management plan + senior coordinator champion are Wave-1 prereqs | G-12, R7.10, PB-5, ET-8 |
| **KC-13** | 5-state US region; state-level employment / staffing / healthcare-credential regulations vary | BRIEF §1; COMMON-SENSE | Regulatory | Pre-engagement legal sweep flags any state-specific compliance triggers; agent's matching is qualification-driven (state-license credential is part of the gate via compliance-status) so most variance is upstream of the agent | G-13, R7.11, PB-6 |

### Risks (top 7 from R7.x)

*[Lifted verbatim from `06-system-data.md` §7 Risk Register — selected top 7 by severity (all CRITICAL)]*

| Risk-ID | Risk | Impact phase | Likelihood | Severity | Mitigation | Owner |
|---|---|---|---|---|---|---|
| **R7.2** | One or more of the 4 stores is closed-system / black-box (KC-2 / Primary Risk per APD §1e) | Phase 1 build → Phase 2 advance gate | **H** | **CRITICAL** | PB-2; if 1 store fails → coordinator-assist on Stream 2; if 2+ fail → re-scope Wave 1 | FDE Eng + MedFlex IT |
| **R7.1** | ServiceNow access fails or schema differs from assumption (KC-1) | Phase 1 build | M | CRITICAL | PB-1; fallback to nightly export | FDE Eng + MedFlex IT |
| **R7.3** | Compliance status is not exposed in a consumable form (A1 / KC-3) | Phase 1 build | M | CRITICAL | PB-4; Compliance Reader sibling agent (W1 in APD §7-bis) is the consumption boundary | Compliance Team + FDE |
| **R7.5** | HIPAA / PHI breach via mis-routed email or pref-store leakage (KC-6) | Always-on | L | CRITICAL | Field-level redaction overlay; immutable audit trail; pen-test before Phase 3 | FDE Eng + Compliance |
| **R7.8** | Coordinator non-adoption / Failure-2 replay (KC-10 / KC-12 / R1) | Wave-1 throughout | M | CRITICAL | PB-5 change-management; Wave-1 read-only first; senior coord champion; coordinator NPS as a circuit-breaker | Marcus + Senior Coord |
| **R7.16** | Multi-submit FA goes live on a hospital whose MSA prohibits revoke-after-submit (Conflict-2 USER-CONFIRMED feasibility-dominant resolution) | Phase 1-3 | M | CRITICAL | `exclusivity_window_minutes` defaults to BLOCK per hospital until PB-3 clears; per-hospital green/yellow/red MSA list maintained; yellow/red hospitals route ALHO with coordinator sign-off per submission; green-list FA only after Legal sign-off in writing | MedFlex Legal + FDE Eng |
| **R7.17** | Submission packet sent with LLM-fabricated credential / mismatched nurse name (Joint-Stakeholder R1; Hartwood B-1 pattern replay) | Phase 2-3 | M | CRITICAL | `submission_packet_factuality_check` predicate (every claim trace-checked against source-of-record before SMTP send); `factuality_audit_pass_rate ≥ 0.999` weekly KPI; GR-13 forbids send on any failed exact-match | FDE Eng + Compliance |

### MVP scope (Wave 1)

*[Lifted from `04-volume-value.md` §7 Stream Rankings Summary + build-sequencing notes]*

| Rank | Stream | Annual saving (conservative) | Annual saving (high) | Build cost | Year-1 ROI (conservative) | Year-1 ROI (high) | Payback (conservative) | Primary-target? |
|---|---|---|---|---|---|---|---|---|
| 1 | **Stream 3 — Submission orchestration** | $535k | $1,827k | $360k | **+49%** | +407% | ~8 mo | No (consequential — needs S1+S2 upstream) |
| 2 | **Stream 2 — Matching** | $556k | $1,848k | $450k | **+24%** | +311% | ~10 mo | **YES (tied with Stream 1 at V×V=20; carries the BRIEF "largest single time consumer" claim + Component-1 lift)** |
| 3 | **Stream 1 — Intake & classification** | $118k | $118k | $180k | -34% | -34% | ~18 mo | YES (tied; upstream prerequisite for S2 and S3) |
| 4 | Stream 4 — Nurse coordination | — (Wave-2) | — | — | — | — | — | No (deferred) |

**Build-sequencing within Wave 1:** Stream 1 first (gate for everything downstream), Stream 2 second (after pref-store cold-start), Stream 3 third (orchestration consumes the prior two). Stream 3's high ROI is *consequential* — it materialises only after Streams 1 and 2 are operational.

**Portfolio Year-1 ROI:** **+7% conservative / +268% high** on $990k Wave-1 build; **~11 months conservative payback** (within the 18-month hurdle rate per atx-scoring.md §Step 3 economic gate).

### Out of scope (interpreted for this engagement)

*[Lifted from `05-agent-purpose.md` §1b Phase 1 boundary]*

**In scope:** Streams 1 (intake & classification), 2 (matching), 3 (submission orchestration).

**Out of scope (Wave 1):**
- Stream 4 nurse-side coordination beyond templated SMS/email notification (D4.1 → RPA path; D4.2 pre-confirm + D4.3 no-show detection deferred to Wave 2 pending A12).
- Hospital-facing portal / chatbot (BRIEF §1 + A4-F1).
- Nurse-facing mobile app (BRIEF §1 + A4-F1).
- Pricing engine / margin optimisation (BRIEF §1).
- Compliance verification / credential lifecycle (BRIEF §1 + Marcus explicit).

---

