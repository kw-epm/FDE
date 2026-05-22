# Internal — Methodology Coverage & Maintenance Notes
**NOT a Gate 2 deliverable. NOT included in concatenated submission.**

This file is for the submitter's own use — to track methodology coverage against the pack §8 anti-patterns, to keep cross-deliverable references aligned, and to maintain the high-repeat figures in sync if anything changes.

---

## How this submission addresses each pack §8 anti-pattern

| Anti-pattern (pack §8) | Where addressed in deliverables |
|---|---|
| "Everything is fully agentic" | DSM matrix mix 0/6/3/2/1 (zero Fully Agentic); per-cluster archetype rationale; DSM §Notes on the matrix distribution; APD activity-catalog Imp. column shows 12 of 16 tasks are deterministic code |
| Documented-not-lived work | CLM Lived Process Narrative; A-1 (DispatchHub stale Oct 2024 per artefact 4 footnote); A-2 (§4.3 = TBD per artefact 4); 50% of open disputes downstream of WS1 damages (CLM §Cross-stream value chain) |
| Bluffing domain knowledge | All proxy answers in `00_elicitation_log.md` are evidence-grounded; where source is silent, proxy is silent and `OPEN` records the gap. Tag discipline: `[Stated]` / `[Inferred:confidence]` / `[Derived]` / `[Estimated]` / `[Unconfirmed]` |
| Legacy system hand-wave | Aurum addressed concretely: schema-validation contract per file (System Inventory P0); halt-on-drift; UI-vs-API distinction (B-1); 48hr ticket vs Aurum UI vs service-account-UI distinction; quarterly schema-change risk explicit |
| Generic discovery questions | Each Q tied to specific evidence (Sandra's £170, BlueSky AM mismatch, D-342 forward-dated, D-337 stalled, Northstar £45 fuel-recalc); quantifier follow-ups; design forks per answer; testimony-vs-artefact watch annotations |
| Vanishing dispatcher | DSM C1A Human Only (Wave 1) → Human-led + AS (Wave 3); APD honest-scope-note explicit ("Wave 1 BDRA does NOT touch dispatcher work"); CLM hotspot summary names dispatcher attention as shared scarce resource |
| Filler assumptions | Every gap in CLAUDE.md gap register ties to a specific design decision; nothing padded; G-N glossary defines each referenced code |

---

## Where to find what (cross-reference index)

| To check | Look at |
|---|---|
| Why BDRA over WS1 (cluster surface, not raw V×V) | V×V §Primary target (5 grounds) + §Why not WS1 first |
| Audit-bypass (A-4) as structural, not misconduct | Elicitation A-4 + Q4 + CLAUDE.md KDD #3 |
| Cross-stream value chain (BP-X1) | CLM §Cross-stream value chain + register C-1 + CLAUDE.md KDD #5 |
| Cost figure status (estimates with sensitivity) | V×V §3 assumption log + Scenario A/B tables |
| Live-round priority | Discovery #06 §Live-round playbook — Top 4 |
| Working analysis (evidence register, role decode, AM coverage map) | `00_elicitation_log.md` (not a deliverable) |
| LLM-vs-deterministic split | APD activity catalog Imp. column + CLAUDE.md KDD #16 |

---

## Maintenance note (DRY hot spots)

These figures appear in multiple deliverables and must be updated together if any change:

| Figure | Canonical source | Also appears in |
|---|---|---|
| £30–67K (Scenario A) / £25–60K (Scenario B) saving | V×V §3 Agent target state | Submission TL;DR; Discovery Q5 design fork; V×V Self-funding logic |
| ~2,700 hr/yr (35% absorption) | V×V §3 Agent target state | Submission TL;DR; APD Compounding Roadmap; V×V Strategic sequencing |
| 50% of open disputes downstream of WS1 | CLM §Cross-stream value chain + register C-1 | DSM C1C; V×V Wave 3; APD Purpose; CLAUDE.md KDD #5 |
| AUDIT_REF format `AUD-{YYYY}-BDRA-{processing_id}-{seq}` | APD task 4.8 | CLAUDE.md KDD #7 (referenced); System Inventory `AGENT_VERSION` note (referenced) |
| Top-4 priority order Q3→Q2→Q5→Q4 + backup Q1 | Discovery #06 §Live-round playbook | Submission TL;DR (implicit via "Sandra-class audit-bypass — Discovery Q3") |
| LLM count: 2 pure (4.6, 4.11) + 2 hybrid (4.5, 4.13) | APD §Activity catalog implementation summary | CLAUDE.md KDD #16; submission TL;DR |
