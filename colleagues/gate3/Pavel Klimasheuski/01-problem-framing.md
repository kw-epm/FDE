# Deliverable #1 — Problem Framing & Success Metrics
**Engagement:** MedFlex Healthcare Staffing
**Participant:** Pavel Klimasheuski
**Date:** 2026-05-12

---

## The stated request vs. the real problem

The stated engagement request: *"10x the business without 10x-ing the coordinators — in 8 weeks."*

This is half right. The real problem is **competitive response time**. Hospitals submit shift requests to multiple staffing agencies simultaneously. The agency that responds fastest with a qualified candidate wins the shift. MedFlex is losing shifts not because it lacks nurses — the nurse database is confirmed sufficient — but because the matching and submission process is slow relative to competitors.

The 4.2-hour average fill time is a symptom of a manual, fragmented workflow:
- Hospital requests arrive as free text and must be manually parsed
- Coordinators manually cross-reference nurse profiles, availability, credentials, and hospital preferences across a database
- Experienced coordinators carry tacit knowledge that newer staff lack, creating inconsistency and onboarding cost
- The whole process runs in a queue that backs up under volume spikes

**The bottleneck is cognitive load per decision, not headcount.** An agent doesn't replace coordinators — it compresses the data-gathering and first-pass matching so coordinators can supervise more decisions per hour instead of executing each one manually.

---

## Decoding "10x" into architectural requirements

| Business target | Architectural requirement |
|---|---|
| 10x shift volume with 8 coordinators | Agent must handle first-pass matching for all incoming requests; coordinator supervises and reviews exceptions |
| Fill time: 4.2h → <1h | Agent must parse and return a ranked candidate list within minutes of request landing in ServiceNow |
| Revenue: $40M → $200M (2-year target) | System must scale to handle ~10x the current request volume without proportional coordinator growth |
| 8-week ROI start | Phase 1 must deliver measurable fill time reduction on a subset of request types within 8 weeks |
| Reduce mismatch rate (currently 7%) | Agent matching must be at least as accurate as average coordinator; confidence scoring must surface low-confidence matches for human review |
| Competitive differentiation | Submission speed must improve materially; agent response time is measured from request receipt to hospital submission |

---

## Success metrics

### MedFlex (business outcomes)
- **Fill time:** average time from request receipt to hospital submission < 1 hour (baseline: 4.2h)
- **Coordinator throughput:** shift-matching decisions per coordinator per day (baseline: ~120; target: 3× or more)
- **Mismatch rate:** hospital-reported qualification mismatches < 4% (baseline: 7%)
- **Revenue per coordinator:** revenue attributed to each coordinator's shift volume (tracks 10x-without-10x progress)
- **Onboarding time for new coordinators:** time to reach full productivity (baseline: unknown — flagged as open assumption)

### Hospitals (downstream quality)
- **Response time:** time from request submission to receiving a candidate proposal
- **Proposal acceptance rate:** proportion of MedFlex proposals accepted (vs. rejected or left unfilled)
- **Repeat preference rate:** proportion of hospitals that request specific nurses again (proxy for match quality)

### Nurses (supply-side reliability)
- **No-show rate:** shifts where notified nurse did not appear (baseline: 12%)
- **Notification-to-shift accuracy:** proportion of nurses notified for shifts they actually attended (proxy for availability data quality)

---

## What "8 weeks" actually means

The CEO did not have a specific 8-week milestone — the intent is to start seeing ROI as quickly as possible. This means:

- 8 weeks = earliest meaningful value delivery, not full transformation
- Phase 1 target: request intake parsing + first-pass candidate matching + confidence-calibrated auto-submission + race condition handling live on a subset of request types
- Active nurse confirmation and no-show prediction are Wave 2 — not because they're unimportant, but because they weren't flagged as pain points in discovery and would introduce friction before trust is established

---

## Open assumptions

- **Onboarding time baseline** — not captured in discovery; needed to measure coordinator productivity improvement
- **Breakdown of 4.2h fill time** — how much is queue wait vs. active matching vs. nurse response lag; this determines whether the agent primarily reduces matching time or also needs to address nurse confirmation latency
- **Competitive response time benchmarks** — how fast do competitors typically respond; not known but determines what fill time target actually wins more shifts
