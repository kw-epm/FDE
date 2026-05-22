# Build-time assumptions

Per the ground rules, I couldn't ask clarifying questions; everything below is
an assumption made to keep moving. Each notes the spec ambiguity and the
choice made.

## A-B1 — Extractor: deterministic stand-in for the LLM
Spec §4 step 1 says "LLM reads email, outputs (fields). Two-stage extraction:
each field validated against source text spans." I shipped a regex/keyword
extractor that emits the same shape — parsed fields, per-field confidence,
per-field citation span — so the rest of the pipeline talks to the right
contract. Swapping in an Anthropic structured-output call is a one-file change.
**Why:** zero-dependency, hermetic, runs in CI; LLM behaviour can be tested
once the contract is locked.

## A-B2 — Ranker: transparent weighted scoring
Spec §4 step 4 says LLM ranks over hospital history, past pairings, profile
notes, soft signals. The §6 worked example names exactly three signals
(history, profile-note match, urgency-vs-credentials tilt). I encoded those
three as explicit, weighted contributions with citations. The output schema
(score + reasoning citations) is the same one an LLM call would produce.
**Why:** the worked example is concrete enough to test against; a model call
would be wasted at this stage of prototyping. Weights are at the top of
`ranker.py` so they can be tuned.

## A-B3 — Confidence definition operationalised as
- **high**: leader has both strong-history and profile-note hits, and is
  not within 3.0 points of the runner-up.
- **medium**: one of those signals OR top-two within 3.0 points.
- **low**: rules-only (no contextual signal exists for any candidate) or
  shortlist empty.
Spec §5 is qualitative ("clear top pick", "near-tie"); I picked a numeric
threshold to make the gate decidable.

## A-B4 — Trust-ramp granularity
Spec §1 lists weeks 1-2 / 3-4 / 8. I implemented weeks ≥3 = high-conf
auto-send; medium and low always coordinator-routed; weeks 1-2 = manual even
at high confidence. The week-5-to-7 gap is treated as "continue weeks-3-4
behaviour"; no separate ramp tier.

## A-B5 — ServiceNow / nurse DB / comms layer
All three are mocked in-process. Spec §7 lists the contracts; I implemented
the failure semantics (retry-with-backoff on comms, halt-on-store-unavailable
for the lock, drop-with-flag for expired credentials) but no real HTTP calls.

## A-B6 — Decision 2 window = 90 minutes
Spec §4 step 9 says "~90 min planned". Hard-coded that; urgent path would use
a shorter window (spec §10 says <15 min urgent). The urgent variant is the
D#4b sibling spec and out of scope here.

## A-B7 — Geo proximity bound = 25 km
Spec mentions "location proximity" without a number. I picked 25 km as a
working default in `eligibility.py::MAX_DISTANCE_KM`.

## A-B8 — Top-N = 3
Spec says "ranked top-N" without N. I chose 3. Adjustable in `pipeline.run`.

## A-B9 — Hospital submission reasoning summary
Spec §4 step 11 produces a `HospitalSubmission` with `reasoning_summary`
without specifying its shape. I concatenate the top two reasoning lines from
the chosen candidate. Production would template this for hospital-facing
audit and probably strip PII / soft-signal language.

## A-B10 — Hard cap on PartialCommitment
Spec §3 says 24h non-urgent / 2h urgent. Implemented exactly; expiry is set
on transition into PartialCommitment, not enforced by a background sweeper
(no event loop in this prototype). A real impl needs a timer service.

## A-B11 — `RemoteTrigger`-style audit / persistence
Audit trail is a list of strings on the `RunResult` plus the `LockStore.events`
log. No real durable storage. The shape is right for shipping to ServiceNow
via the write API (spec §7).

## What I couldn't build in 30 minutes

- **Background timeout sweeper for locks.** I capture the expiry timestamp
  but don't fire a task when it lapses. In the demo, lock state transitions
  are driven inline by the orchestrator.
- **Multi-shift parallel scheduling.** Edge case 6 (a second shift request
  arriving while Nicole has a SoftLock) is guarded in `LockStore.soft_lock`
  (it raises), but the re-pool flow that surfaces an alternative candidate
  for the *second* request isn't wired through `pipeline.run`.
- **Edge case 8 (hospital rejection re-rank).** The pipeline halts on
  hospital-no rather than looping back to step 4 with the rejected candidate
  excluded. Single-shot orchestrator; a real version would be a state
  machine that can re-enter.
- **A real LLM extractor / ranker.** Deferred to keep the prototype hermetic.
- **ServiceNow webhook / poller.** No transport layer; `run()` is invoked
  directly with the raw email.
