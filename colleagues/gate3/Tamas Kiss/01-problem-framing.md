# Deliverable 1 — Problem Framing & Success Metrics

**Author:** Tamas Kiss
**Engagement:** MedFlex agentic transformation  
**Date:** 2026-05-13
**Gate:** Gate 3 — Final submission

---

### The real problem (vs the stated request)

*[Lifted from `01-analysis.md` §1 Scenario Summary]*

MedFlex is a US healthcare staffing agency (~200 employees, 5-state region) that supplies travel nurses to hospital systems on shift contracts. Hospitals submit shift requests via email (dominant channel), web portal, and phone, all converging into a ServiceNow queue; 8 coordinators manually classify free-text requests against MedFlex's structured credential taxonomy and match nurses to shifts by joining four separate stores (profile, availability, request, qualification). Average time-to-fill is 4.2 hours against a target of <1 hour; "mismatch rate" is reported at 7% but conflates qualification error with competitive preference loss (A2); no-show rate is 12% with reactive-only detection. CEO Marcus Reyes (post-Series-B, board pressure for growth) is targeting **$14M → $200M revenue over 24 months**, with the 8-week milestone framed as "start getting money back" rather than full scale. The engagement is to design an agentic transformation of matching + intake-classification + nurse-side coordination, with **speed-to-submit as the primary win/loss driver** in a competitive multi-agency market where hospitals submit to several agencies in parallel and the first qualified candidate frequently wins. Compliance verification, hospital-facing portals, nurse-facing apps, and pricing are explicitly out of scope.

### Architectural requirements that "10x without 10x-ing" actually demands

*[Lifted from `01-analysis.md` §6 Hard Constraints]*

Non-negotiable rules drawn from the brief and Marcus's discovery statements.

1. **No hospital-facing agent surface.** Hospital intake remains via email / portal / phone (BRIEF §1 Out-of-scope L33, reinforced by A4-F1 channel/UX-fit failure).
2. **No nurse-facing mobile app.** Nurse reach remains via phone / SMS / email (BRIEF §1 L34).
3. **Compliance verification and credential lifecycle are out of scope.** "Separate process, separate team, end of the story." (BRIEF §1 L11). The agent *consumes* the compliance-verified status as a precondition; it does not modify, query, or replicate the compliance team's process.
4. **Pricing engine / margin optimisation out of scope** (BRIEF §1 L35).
5. **8-week milestone = "start getting money back"**, not full $200M scale (BRIEF §1 L25). The first wave must demonstrate value-flow, not full transformation.
6. **Speed-to-submit is the primary win/loss driver** in the competitive multi-agency market (BRIEF §1 L28; A2 + A3 supporting). Quality-maximisation is subordinate to throughput-with-acceptable-quality.
7. **HITL placement deferred to the FDE** — Marcus: "automate as much as possible … I'm not an expert in this area, tell me the consequences and I'll decide." (BRIEF §1 L19). The FDE *must* surface delegation-boundary trade-offs as named decisions; Marcus chooses.
8. **Multi-submit + revoke-when-confirmed is the operating mechanic**, not an edge case (A3). 1:1 matching is the wrong mental model.
9. **Coordinator transformation acceptable, not coordinator replacement marketed** (BRIEF §2 L58 + A4-F2 implication). Job change is permitted; layoff framing is not.
10. **The 7% mismatch metric is unsplittable today** (A2 L95). Any KPI design that uses 7% as input is poisoned; the agent must produce the split.

### Success metrics — three stakeholder groups

*[Lifted from `05-agent-purpose.md` §1d 5 mandatory KPIs]*

| KPI | Baseline | Target | Measurement methodology | Data source | Frequency |
|---|---|---|---|---|---|
| **Accuracy** (classification_accuracy_at_confidence ≥ 0.85) | Currently uninstrumented (A2 L95). Baseline-equivalent established in Phase 1 pilot via coordinator-coded review of ~200 historical tickets. | ≥0.90 by Phase 2 advance-gate; ≥0.95 by Phase 3 | Sample 100 randomly-selected tickets/week from the T1/T2 path; coordinator codes each as `classification_correct ∈ {true, false}`; accuracy = mean | New `classification_eval_log` table; coordinator-fed via review dashboard | Weekly |
| **Coverage** (% of tickets handled by agent without T3/T4 escalation) | 0% today (every ticket is manual) | ≥0.75 by Phase 2 advance-gate; ≥0.85 by Phase 3 | Count(T1 + T2) / Count(all tickets) per week | `decision_log` table | Weekly |
| **Throughput** (median + p95 time-to-first-submission from classified ticket) | Median 4.2h, p95 unknown (BRIEF §1) | Median <60 min by Phase 3 advance-gate; p95 <4h by Phase 3 | Wall-clock from `ticket.classified_at` → `submission.first_sent_at` per fill | `submission_state_ledger` | Daily |
| **Cost-per-case** — split into two per Phase 10 / Adversarial A10 label-drift fix: <br>(a) `tokens_per_decision` (operative from Phase 1) <br>(b) `blended_cost_per_decision` (operative per phase including HITL hours) | (a) ~$0.18 avg today; (b) ~$2.67 fully-loaded labor today | (a) ≤ $0.30 from Phase 1 onward; (b) ≤ $0.85 in Phase 2 / ≤ $0.55 in Phase 3 | (a) Token meter / decision count; (b) (a) + tool calls + infra alloc + HITL hours × $40/hr | Provider invoice + decision_log + infra cost report | Monthly |
| **HITL rate** (% of decisions routed to T3 or T4) | 100% today | ≤0.25 by Phase 2 advance-gate; ≤0.15 by Phase 3 | Count(T3 + T4 routes) / Count(all decisions) per week | `decision_log` | Weekly |

Plus a Phase-10 USER-CONFIRMED revision to **HITL rate signal** (per Adversarial A4 + Joint-Stakeholder O1): the `coordinator_NPS_delta` numeric metric is replaced with a **tri-state qualitative signal** sampled weekly. Trust-pause fires on any of: (a) named senior coord champion (Kim TBC) withdraws endorsement, OR (b) ≥3 of 8 coordinators rate the agent below "neutral" on a 5-point dashboard pulse, OR (c) opt-out / sick-leave / formal-complaint events. n=8 makes numeric NPS-delta statistically incoherent; the tri-state signal is the operationally defendable proxy. Carried into Phase 4 §4 phase-gate criteria and §6 circuit-breaker.

Plus two defendable bonus KPIs:

KPI #6 per SL-077 (Component-1 lift instrumentation requirement):

| KPI (bonus, load-bearing per SL-077) | Baseline | Target | Measurement methodology | Data source | Frequency |
|---|---|---|---|---|---|
| **Component-1 lift** (qualification-accurate-submission rate vs the 30%–70% C1 share of the historical 7%) | Baseline established in Phase 1 via coordinator-coded sample of 30-50 historical rejections (Phase 7 question) | +25% relative lift by Phase 3 advance-gate (conservative C1=30% scenario); +60% under high C1=70% scenario | Per-rejection capture: coordinator codes outcome as `mismatch_component ∈ {C1_qualification, C2_competitive, both, neither}`; agent reports its own confidence on submission as predictor | New `rejection_log` table; populated by the agent's instrumentation + coordinator review | Weekly |

KPI #7 per Phase 10 Joint-Stakeholder R1 (factuality audit; Hartwood B-1 pattern mitigation):

| KPI | Baseline | Target | Measurement methodology | Data source | Frequency |
|---|---|---|---|---|---|
| **Submission factuality audit pass rate** — share of outbound submissions where every factual slot (credentials, name, dates, availability) exact-matches the source-of-record | 100% target from Phase 1 (read-only does not send; gate activates when sends begin in Phase 3) | ≥ 0.999 weekly sustained | Per-submission factuality check before SMTP send: every claim trace-checked against `credentialing_db` / `availability_db` / `nurse` projection; logged to `submission_factuality_ledger` | New `submission_factuality_ledger` table | Weekly + alarm on any fail |

### Time horizons

*[Lifted from `04-volume-value.md` §4 Phase-Gating Matrix]*

| Phase | Streams in scope | Build cost | Conditional Go/No-Go gate to advance to next phase | Expected FTE change |
|---|---|---|---|---|
| **Phase 1 — Wave 1 read-only (months 0–4)** | Stream 1 (D2.A read-only retrieval as a coordinator support tool); Stream 3 (D3.5a context surfacing only) | ~$150k | IF `D2.A retrieval_p95_latency ≤ 30s AND retrieval_accuracy ≥ 0.95 AND coordinator_NPS_delta ≥ 0` THEN PROCEED | 0 (no change; agent assists coordinators) |
| **Phase 2 — Wave 1 classification + ranking (months 4–8)** | Stream 1 full (D1.1, D1.3, D1.4); Stream 2 (D2.A, D2.5 with HITL) | ~$280k (cumulative ~$430k) | IF `D1.1 classification_accuracy_at_0.85 ≥ 0.90 AND HITL_rate ≤ 0.25 AND coordinator_NPS_delta ≥ 0` THEN PROCEED | 0 (HITL volume drops; coordinator role shifts toward review) |
| **Phase 3 — Wave 1 preferences + orchestration (months 8–12)** | Stream 2 full (D1.2, D2.4); Stream 3 full (D3.2, D3.3, D3.4, D3.5a) | ~$560k (cumulative ~$990k) | IF `parallel_submission_throughput ≥ 1.5× baseline AND Component-1_mismatch_rate ≤ baseline × 0.75 AND ledger_consistency_failure_rate < 0.5% AND coordinator_NPS_delta ≥ 0` THEN PROCEED to Wave 2 | -1 FTE coordinator absorbable into senior-quality-audit + tribal-knowledge-authoring role; net headcount stable in Wave 1 |
| **Phase 4 — Wave 2 nurse-side + scale (months 12+)** | Stream 4 if A12 validates; pref-store maturation; cross-agent compounding | TBD (Phase 7+) | IF `no-show_rate ≤ 0.09 AND pref_store_confidence ≥ 0.85 AND coordinator_NPS ≥ +30` THEN platform-wide scale-up | Coordinator-role evolves to specialist-quality-audit + senior pref-author + exception handler |

---

