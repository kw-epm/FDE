# D#9 Self-Spec Build-Loop Reflection

*Spec run: D#4a (Planned Matching). Builder: fresh Claude Code instance, 30-min hard cap. Build finished in ~5 minutes; remaining ~25 min spent on this reflection.*

> **Timeline note for any third-party re-run.** This reflection was written immediately after the D#9 buildability test, against the **pre-A11/A12 version of D#4a**. After D#9 was complete, two revisions were added to D#4a §9 (A11 + A12) and one to D#4b §9 (U7), explicitly flagged as post-D#9 revisions per pack §9 protocol *"flag it as a revision"*. The revisions **flag** the precision and maturity gaps surfaced here; they do not **pin** the values. If anyone re-runs D#9 against the current D#4a, Claude Code's `ASSUMPTIONS.md` output will likely differ from the diagnostic table below, because A11 and A12 now explicitly acknowledge the gaps. The substantive diagnosis below remains valid; only the spec's flagging posture has changed.

## (a) What Claude Code built, and whether it matches intent

A runnable Python 3 prototype in `d9_build/` (~1,200 lines, stdlib only). **The happy-path version of all 13 process steps** from D#4a §4 maps 1:1 to code modules. Seven happy-path scenarios in `demo.py` exercise the worked example (§6), week-2 trust-ramp, expired credentials, comms retry, nurse decline, lock-store outage, and low-confidence extraction. All seven pass. The §6 scenario (instantiated in the prototype as Nicole vs Mark, mapping to the spec's Nurse N vs Nurse M) produces Nicole #1 over Mark #2 with reasoning citations and confirms in 33 min vs the ≤2h KPI target. **Re-entry flows (lock-expiry timer, re-pool on collision, re-rank on hospital reject) are not in the prototype.** See §(b) and §(c) below.

**Matches intent.** The entity model, eligibility precondition, ranker contract, four-state lock, Decision 2 explicit-yes, and audit trail all came through. The fast finish is a signal that the spec was precise enough to build from without clarification, **not** that the spec was perfect. CC made eleven named assumptions to keep moving, all logged in `ASSUMPTIONS.md`. Those assumptions are the diagnostic material.

## (b) Questions it asked, things it said it couldn't build

CC didn't ask questions (ground rule said it couldn't). It logged 11 build-time assumptions and 5 explicit "couldn't build" items. The "couldn't build" list:

1. Background lock-expiry sweeper (no event loop)
2. Re-pool flow when a second shift request collides with an existing SoftLock (LockStore raises, pipeline doesn't handle)
3. Re-rank loop on hospital rejection (single-shot orchestrator, can't loop back to step 4)
4. Real LLM extractor / ranker (deliberately deferred)
5. ServiceNow webhook / poller (no transport layer)

## (c) Per-gap diagnosis, using the W3 taxonomy

| Gap | Classification | Honest read |
|---|---|---|
| Numeric "near-tie" threshold (§5 confidence) | **Spec ambiguity** | "Clear top pick" / "near-tie" is qualitative. CC picked 3.0 points to make the gate decidable. The spec should have pinned a number. |
| Location proximity bound (§4) | **Spec ambiguity** | "Proximity" with no km figure. CC picked 25 km. Same root cause as above. |
| Top-N shortlist size (§3) | **Spec ambiguity** | Spec says "ranked top-N" without N. CC picked 3. |
| HospitalSubmission.reasoning_summary shape (§4 step 11) | **Spec ambiguity** | Output schema named but format unspecified. CC concatenated top-two reasoning lines. Production needs a template, including PII-handling. |
| Trust-ramp weeks 5–7 (§1) | **Spec ambiguity** | Spec lists weeks 1–2 / 3–4 / 8. CC extrapolated "continue weeks-3-4 behaviour." Bookended without filling the middle. |
| Decision 2 window stated as "~90 min" | **Spec ambiguity** | The "~" is the gap. CC hard-coded 90. Production needs a tunable parameter, not a hardcoded number. |
| LLM extractor → regex stand-in | **Test-environment issue** | CC mocked the LLM to keep the prototype hermetic, with the same input/output contract. A legitimate prototype substitution, **but the spec didn't say "the LLM is the production target; substitutes are acceptable for prototypes if they match the contract."** That clarification should be in the spec. |
| LLM ranker → weighted scoring stand-in | **Test-environment issue** | Same root cause as above. |
| Lock-expiry sweeper missing | **Spec ambiguity** | Spec §3 names the hard cap (24h / 2h) but doesn't say what fires it. A background timer service is implied by the state machine, not specified by it. |
| Re-pool flow for concurrent collision (edge case 6) | **Spec ambiguity** | Spec lists the edge case but doesn't specify the recovery flow when LockStore blocks a second offer. The 13-step process table in §4 is **single-shot** and doesn't accommodate re-entry. |
| Re-rank loop on hospital rejection (edge case 8) | **Spec ambiguity** | Same root cause as above. Edge case is named, recovery flow isn't. |
| CC's A-B6 reads "<15 min urgent" as the urgent Decision 2 **window** | **Builder misread + spec ambiguity** | The "<15 min urgent" in §10 is the response-time **target**, not the window. The window is 30 min (per D#3 and D#4a §4 step 9). CC conflated the two. The misread is genuine, but the spec §10 validation-hooks table is also at fault: it states targets and pause/rollback triggers in the same row without making the target-vs-window distinction explicit. Honest classification: half builder, half spec. |

**One genuine builder misread**, identified above. **No unjustified additions** beyond the numeric defaults CC had to invent to compile. Those trace back to spec ambiguity, not builder overreach.

**The big finding:** three of the five "couldn't build" items (#1, #2, #3) share the same root cause. The D#4a §4 process table is a **linear, single-shot flow**. The actual capability is a **re-entrant state machine** (Decision 3's four-state lock is the clue, but it's in D#3, not surfaced in D#4a's process table). My spec described the happy path step by step and put the edge cases in a separate section, but didn't reconcile the two views into one orchestration model. A precise spec needs both, joined.

## (d) What I would change in another 30 minutes

1. **Convert §4 from a linear 13-step table to a state-machine view.** Same content, but with explicit re-entry edges: on hospital rejection, return to step 4 with `rejected_candidate_id` excluded; on lock-expiry, return to step 7 with re-pool; on Decision 2 timeout, advance shortlist cursor. Three edges fix three "couldn't build" items.
2. **Pin numbers that should be parameters, not prose.** Confidence near-tie threshold; Top-N shortlist size; max distance km; Decision 2 windows (planned and urgent) **clearly labelled as windows, separately from the response-time targets that share §10 with them** (this would have caught CC's window-vs-target misread); HospitalSubmission.reasoning_summary template; trust-ramp weeks 5–7 behaviour. Add a `§4 Parameters` block at the top of the spec.
3. **Add a "what's mocked in prototypes" line.** "Extraction and ranking nodes are LLM calls in production; prototypes may substitute a deterministic stub provided it matches the schema." Closes the test-environment gap explicitly.
4. **Specify the timer service.** Lock-expiry, re-ping at 1h, coordinator alert at 2h, hard cap at 24h / 2h. List them as one timer table in §3 with the firing conditions and the state transitions they cause.

These four changes together turn a "good enough to ship a prototype in 5 minutes" spec into a "good enough to ship production without an FDE in the room" spec. The diagnostic value of this exercise was not that the spec failed, it was that the precise places it was vague were also the precise places a builder needed numbers to keep moving.

---

*Bias self-check: it would be tempting to read the 5-minute build as a win and stop there. The honest read is that the spec was tight enough on the happy path and visibly thin on the state-machine reconciliation. The four fixes above are not polish, they are the difference between a spec that produces working code and a spec that produces auditable production code.*
