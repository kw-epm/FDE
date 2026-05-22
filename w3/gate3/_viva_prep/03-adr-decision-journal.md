# Viva prep: ADR decision journal

*Not part of submission. For my own preparation against the coach picking one architectural decision to defend. For each of the three Decisions in D#3, this expands the public ADR with: the alternatives I considered but rejected fastest (and why), what would trigger me to reopen, and what I'd specifically revise if I learned X.*

---

## Decision 1: Reason over context, don't learn

### Public ADR summary

v1 agent doesn't learn. Reasons over historical context as input; shows reasoning. Coordinator audits; override rate is the trust signal. Phase 2 adds a learned soft-signal layer after Decision 2 produces clean labels.

### Alternatives considered fastest, then rejected

1. **Smarter ranking model (recommender pattern).** Rejected because that's exactly what failed. Not a clever rejection, a structural one.
2. **Rules-only in v1, learned in Phase 2.** Rejected because it doesn't solve the tacit-knowledge bottleneck (the actual problem). v1 would be thin.
3. **Force hospitals into structured forms.** Rejected because Marcus already told us hospitals rejected the chatbot.
4. **End-to-end model doing extraction + ranking.** Rejected because explainability collapses.

### Branch I considered but didn't write up

**LLM-fine-tuned ranker (no reasoning citations).** Could be faster at inference, cheaper per call. Rejected because explainability is the differentiator against the prior recommender. But, if Decision 2 produces 6+ months of clean labels and the override rate keeps trending down, this is a Phase 2.5 option. Not now.

### What would trigger me to reopen this ADR

- **Override rate target met but consistently flat.** If we hit <25% by week 8 but it just sits there for two quarters, learning may legitimately add value above reasoning-only.
- **A high-volume specialty where context is structurally absent.** If a new slice has zero historical pairings (a new hospital, brand new specialty), reasoning over context becomes weak, and a learned approach over similar shifts elsewhere may be better.
- **Reasoning cost explodes.** If LLM costs at scale become material (~$148K/year at full target per D#3 §Economics is still small, but a 10× increase changes that), a smaller fine-tuned model becomes more attractive.

### What I'd revise if I learned…

- **…that historical context is structurally unqueryable.** Rewrite Decision 1: the "reason over context" framing assumed queryable context exists. Without it, v1 becomes either pause-and-rescope or a different product.
- **…that Marcus considers explainability optional.** Strengthen the citations side of Decision 1 with a hard requirement and downgrade Phase 2's learned layer to a soft signal that augments, not replaces, the reasoning layer.

---

## Decision 2: Make nurses say yes (conditional)

### Public ADR summary

Status: conditional. If Head of Ops confirms "no reply = yes" is current practice (D#1 question 5), agent requires explicit yes within window; no-reply moves to next candidate. If not, alternative path: confirmation-channel improvements + same-day re-check ping.

### Why this is the conditional ADR, and why that's a feature, not a bug

The ADR rests on a finding (no-reply-as-yes) I cannot confirm before signing. Three options:

1. **Commit to the finding as fact.** Risk: if wrong, the architecture is built on phantom data quality (recommender trap part 2).
2. **Defer the decision until Monday.** Risk: D#3 has nothing to commit to; Marcus reads architectural hedging.
3. **Mark conditional with explicit alternative path.** What I did. Risk: looks like indecision; mitigated by naming the alternative.

Option 3 is the strongest defensible position because Marcus's pushback didn't touch Decision 2 on Friday, there was nothing to push back on. The dependency was already named.

### Alternatives within the "explicit yes" branch

- **90-min window planned, 30-min window urgent.** Picked these on Marcus's stated 4h-to-fill baseline and a desire for the parallel ranker step to have room. If Head of Ops says median nurse response is 30 min planned, both windows tighten.
- **Reminder ping closer to shift instead of explicit-yes.** Rejected because that patches the no-show symptom without ever knowing if nurses agreed. Decision 2 changes the data shape.
- **Phone confirmation by coordinator.** Rejected because it reintroduces the human-time cost the architecture exists to solve.

### Branch I considered but didn't write up

**Tiered confirmation: SMS for low-stakes, phone for high-stakes (high-credential, high-value, or new-nurse).** Could squeeze more confidence out of the channel mix. Rejected for v1 because the tier logic adds complexity, and the architectural argument is whether explicit-yes works at all, not whether multi-tier explicit-yes optimises. Phase 2 option once we've measured the explicit-yes baseline.

### What would trigger me to reopen this ADR

- **Head of Ops confirms no-reply-as-yes was real but the no-show rate didn't track it closely.** Means the assumption that explicit-yes drops no-shows was overconfident; the alternative path becomes the primary path.
- **Nurse response distribution is bimodal:** some nurses respond fast, others never reply. If the median is fine but the tail is brutal, the window length is the lever, not the explicit-yes mechanism.
- **Hospital response time variability exceeds nurse response time variability.** If most of the time-to-fill latency is on the hospital side, optimising the nurse window doesn't move the primary KPI; D#3 mode table changes more than Decision 2.

### What I'd revise if I learned…

- **…that no-reply-as-yes is real but the rate is tiny (e.g., 2%).** Decision 2 becomes a minor tuning, not a major ADR. Move to alternative path; reduce to a footnote.
- **…that nurses respond faster on hospital-first workflow.** Rework D#3 §"Two modes" and Decision 3's lock trigger; Decision 2's window shifts.

---

## Decision 3: Race conditions (four-state lock)

### Public ADR summary

Four-state lock: SoftLock → PartialCommitment → Confirmed | Released. Hard cap on PartialCommitment (24h non-urgent / 2h urgent). State machine doesn't change with workflow order; only the lock trigger event changes.

### Why this matters as the architectural defense

This is the decision that earns "scale to 13.5K decisions/day." Today MedFlex multi-submits and pulls back manually. At 14× volume the pull-back stops working. The four-state lock makes parallel submissions safe.

### Alternatives considered fastest, then rejected

1. **Manual pull-back, like today.** Doesn't scale. The whole architectural ask is about volume.
2. **Strict locking, no timeout.** Single unresponsive party freezes the candidate. Bad UX, bad metrics.
3. **No locking, tolerate double-commitment.** Chaos. Two hospitals expecting the same nurse means broken trust, broken acceptance rate.
4. **Sequential offer windows (no overlap).** Too slow. Time-to-fill blows up.

### The partial-commitment state, why it's separate

Originally I had a 3-state lock (Soft / Confirmed / Released). Reviewer flagged: what happens when one side accepts and the other is pending? If we collapse to Confirmed, we've lied; if we release, we've broken commitment to the side that accepted. The 4th state, PartialCommitment, names this gap explicitly and the hard cap bounds the worst case.

### What would trigger me to reopen this ADR

- **Lock-timeout rate is high.** If soft-locks expire with no acceptance frequently (D#3 §"Direct locking-impact metrics"), the windows are too short. Tune, don't redesign.
- **Lock-release-then-immediate-reuse rate is high.** Locking is creating delay without preventing a downstream re-offer to the same candidate. Means lock predicates were over-cautious.
- **Cross-state regulatory changes.** If state X mandates explicit nurse-acknowledgment of EVERY shift offer (not just acceptance), the soft-lock event timing changes.

### What I'd revise if I learned…

- **…that the actual workflow is hospital-first.** Lock trigger changes (fires on hospital submission, not nurse offer). State machine is the same.
- **…that the actual workflow is parallel (true simultaneous nurse + hospital).** Both sides need their own locks, or the existing lock needs to be conditional on which-event-arrived. Architecture absorbs this with a small modification to the trigger logic.
- **…that hospital response times are highly variable.** Hard cap on PartialCommitment may need to be specialty-by-specialty (24h works for med-surg, may be too long for paediatric ICU). Specialty-specific hard caps would be a small D#4 parameter change, not an ADR rewrite.

---

## How I'd use this in the viva

If the coach picks Decision 1: lead with the explicit rejection of the recommender pattern + alternative paths + Phase 2 condition. If they probe, talk about the conditional/Phase 2 dependency on Decision 2's clean labels.

If the coach picks Decision 2: lead with the conditional framing as a deliberate architectural move, not hedging. Show Marcus's Friday pushback didn't touch Decision 2 as evidence.

If the coach picks Decision 3: lead with the four-state lock + why partial commitment is its own state. Acknowledge the workflow-order conditionality. Reference the two direct lock-impact metrics that tune it.

For all three, the close is the same: *"This decision could be reopened by [trigger]. I'd revisit it within the engagement; I'd rewrite the spec if [bigger thing]. It's not locked in stone, it's locked in with a known reopening condition."*
