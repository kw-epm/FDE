# Deliverable 8 — Reflection

**Author:** Tamas Kiss
**Engagement:** MedFlex agentic transformation  
**Date:** 2026-05-13
**Gate:** Gate 3 — Final submission

---



## Three specific lessons from this gate

### 1. Substrate-honesty as the decision driver under stakeholder pushback

When Marcus's pushback memo arrived Friday morning, two of the three points (P1 and P2) named internal inconsistencies in my own substrate — KC-7's "value flow begins" framing vs Phase-1's 0-FTE V×V row, and ADR-1's ≥80%-non-green threshold vs ADR-3's <50%-green coexistence table. Both pointed at substrate flaws I hadn't fully reconciled at the end of Thursday. The lesson is procedural, not just substantive: when pushback names an internal-consistency gap in the spec, the honest move is flixibility and correct self-negotiation, not defence — holding scope would have meant defending something that is not correct. It is a psychological bias. P3 (Kim engagement) was different: the gap was real but in the discharge path, not the spec. Three points, three different shapes of response (concede / concede / acknowledge complication), all substrate-honest. What I'd change with more time: I would have closed the KC-7 vs Phase-1 phase-gating gap in the end of Thursday submission itself — the inconsistency was visible if I'd cross-checked V×V rows against KPI commitments, and catching it Thursday would have removed Marcus's strongest P1 lever.

### 2. The deferred-calibration anti-pattern is structural, not stylistic

When the D9 build-simulation ran against `04b-capability-spec-classification.md`, the most consequential finding wasn't any single ambiguity — it was a pattern across multiple gaps. I had written `PENDING_CALIBRATION` for the PHONE_MULTIPLIER (EC-1.4), `TBD — established during Day 3 prompt-tuning` for the accuracy baseline (§10), and "calibrated against the 500-row eval set at deploy time" for the confidence thresholds (§9 A1.1). Each individually looks reasonable; the pattern across three places is structural — I keep deferring values to a build phase that needs the values to start. This is the same critique Marcus made of Phase 1 architecturally ("not a revisitation condition") applied at the capability-spec level. With more time, every value the spec defers needs a starting value that the calibration plan can replace, not a placeholder that the calibration plan has to invent.

### 3. Discipline transferability mid-session is real but fragile

When running the `gate3-pushback` pipeline on Marcus's memo, the orchestrator pre-named response strategies in substrate notes during Phase 01 — a contamination shape that would have biased the Phase 02 classifier's "never pick — always propose candidates" hard rule. After one explicit instruction (strip strategy names from substrate notes), the orchestrator caught two more instances of the same contamination independently — including ones in my own earlier substrate-note additions. The lesson: discipline is teachable in-session even when not encoded in the prompt structurally, but the teaching is fragile (depends on the user catching the contamination and routing through an oracle). For v0.1 of the pipeline, the discipline needs to be encoded in the prompt template (substrate-notes form has no field for strategy names), not relied on as runtime guidance. The broader pattern: any discipline that requires repeated mid-session correction is a structural gap waiting to be fixed in the prompt, not a weirdness of execution.

## What would change with another half-day

- **D9 reflection compressed to actual 1 page** per pack. Current clay is ~3 pages; the diagnostic richness can be preserved with tighter selection (5 most build-impactful gaps rather than 11; (d) cut to 4 prioritised edits rather than 8). The instinct to be thorough fought the pack constraint to be concise; with more time I would have honoured the constraint better.
- **CBL re-run against the revised D3** (Phase 1.5 + ADR-1 threshold realignment). Named as deferred in `07-validation-plan.md` §4 with Monday scheduling; in a counterfactual half-day I would have run it. 
- **D5 (Cascade build-loop) via the `gate3-buildloop` pipeline** rather than hand-written classification. The hand-written version covers the 8 signals correctly to my read, but the pipeline output would carry the same audit discipline as `06-client-feedback.md` (substrate-cited rationale per signal, citation audit at the end, machine-checkable consistency). Time budget didn't permit the pipeline run today.
- **D4 cross-spec glossary tightening.** The shared glossary is one file referenced by both `04a` and `04b` — but the cross-references are prose ("see `04-shared-glossary.md`"), not structural enforcement. With more time, a glossary-coverage check (does every entity used in 04a/04b appear in `04-shared-glossary.md`?) would be a CI-style gate, similar to the citation audit in `gate3-pushback` Phase 04.
- **D9 manual exam-conditions build added alongside the subagent.** The subagent path produced rich diagnostic substrate (13 ambiguities, 11 gaps, 8 spec edits) inside the time budget, but it's substrate I received rather than lived through. With more time I would have run a subagent breadth pass first, then a manual exam-conditions deep-dive on the 2–3 highest-leverage gaps the subagent surfaced. Subagent + manual, not subagent vs manual — each captures what the other can't (subagent for diagnostic breadth and citation discipline; manual for the lived "what surprised me as I watched" frame the coach can probe in verbal defense).

## Honest about what's still rough

The Thursday discovery role-play caught one of the three Marcus contradictions explicitly (the "credentials verified before joining roster" vs "re-verify within a week after state ping" pair); the other two surfaced indirectly through pushback rather than in-room. Discovery skill is a real gap I want to close before the next engagement — specifically, the muscle of holding two answers in working memory long enough to surface their contradiction rather than processing each answer on its own merits and moving on.

The gate3-pushback pipeline was operationally tested on a single-stakeholder pushback (Marcus); multi-stakeholder pushback (e.g., Marcus + CFO + Kim disagreeing) is a different problem shape that v0 doesn't address. The pipeline is useful as-is, but I'd want at least one multi-stakeholder dry-run before relying on it for a second engagement.

The mermaid diagram for the per-request flow in `03-architecture.md` is at capability-level granularity (D1.1 → D2.A → D2.5 → D3.2 etc.); a board-level diagram showing what changes for Marcus's stakeholders (coordinators, hospitals, nurses) would be a more useful artefact for verbal defense than the engineering flow. I'd add a stakeholder-impact diagram with more time.
