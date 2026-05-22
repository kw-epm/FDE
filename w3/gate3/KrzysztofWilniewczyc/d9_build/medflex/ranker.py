"""Steps 4 + 5 — Contextual reasoning over history, then confidence scoring.

The spec §6 names three context signals the agent must reason over:
  1. Hospital acceptance history (soft "worked with before" preference)
  2. Profile-note match (e.g. paediatric allergy experience)
  3. Urgency tilts toward known-reliable over pure-credential leader

We implement these as transparent, weighted contributions to a score, with
each contribution captured as a reasoning citation. Swapping in an LLM
(Anthropic SDK) would replace `_score_candidate` while keeping the same
contract: a numeric score plus a list of human-readable reasoning lines.
"""
from __future__ import annotations

from .entities import (
    Candidate,
    CandidateShortlist,
    Nurse,
    ShiftRequest,
    Urgency,
)
from .seed import hospital_history


# Weights — tuned so that hospital history + profile-note match dominate
# raw credential count for the worked example. Tweakable in one place.
W_HOSPITAL_HISTORY_PER_SHIFT = 6.0
W_PROFILE_NOTE_MATCH          = 8.0
W_EXTRA_CREDENTIAL            = 1.5
W_URGENCY_RELIABILITY_BOOST   = 4.0   # only kicks in if urgent + history exists
W_DISTANCE_PENALTY_PER_KM     = 0.2


def _profile_note_matches(nurse: Nurse, signals: list[str]) -> list[str]:
    notes = nurse.profile_notes.lower()
    hits: list[str] = []
    for sig in signals:
        if sig.lower() in notes:
            hits.append(sig)
    # Soft co-occurrence: paediatric + allergy in same note counts as a stronger hit
    if "paediatric" in signals and "allergy" in signals:
        if ("paediatric" in notes or "pediatric" in notes) and "allerg" in notes:
            hits.append("paediatric+allergy combined")
    return hits


def _score_candidate(nurse: Nurse, req: ShiftRequest) -> tuple[float, list[str]]:
    score = 0.0
    why: list[str] = []
    intent = req.parsed_intent

    # 1. Hospital acceptance history (soft "worked with before" signal)
    history = hospital_history(req.hospital_id, nurse.id)
    if history:
        score += W_HOSPITAL_HISTORY_PER_SHIFT * len(history)
        why.append(
            f"Hospital history: {len(history)} prior accepted shift(s) at this hospital "
            f"(+{W_HOSPITAL_HISTORY_PER_SHIFT * len(history):.1f}). "
            f"Latest note: {history[0].note!r}."
        )
    else:
        why.append(f"Hospital history: no prior shifts at {req.hospital_id} (+0).")

    # 2. Profile-note match for soft signals from the request
    sig_hits = _profile_note_matches(nurse, intent.profile_signals)
    if sig_hits:
        boost = W_PROFILE_NOTE_MATCH * len(sig_hits)
        score += boost
        why.append(
            f"Profile note match: {sig_hits} (+{boost:.1f}). "
            f"Source span(s): "
            + ", ".join(
                f"{s}={intent.citations.get(s, '')!r}" for s in intent.profile_signals
            )
        )
    elif intent.profile_signals:
        why.append(
            f"Profile note match: none for signals {intent.profile_signals} (+0)."
        )

    # 3. Credential surplus (mild factor — credentials beyond the requirement)
    extras = [c for c in nurse.credentials if c not in intent.credentials]
    if extras:
        boost = W_EXTRA_CREDENTIAL * len(extras)
        score += boost
        why.append(f"Extra credentials beyond requirement: {extras} (+{boost:.1f}).")

    # 4. Urgency → reliability tilt (only if request is urgent AND nurse has history)
    if intent.urgency == Urgency.Urgent and history:
        score += W_URGENCY_RELIABILITY_BOOST
        why.append(
            f"Urgent request + known-reliable nurse (history present): "
            f"+{W_URGENCY_RELIABILITY_BOOST:.1f}."
        )

    # 5. Distance penalty (small)
    pen = W_DISTANCE_PENALTY_PER_KM * nurse.distance_km
    score -= pen
    why.append(f"Distance {nurse.distance_km}km penalty (-{pen:.2f}).")

    return score, why


def rank(req: ShiftRequest, pool: list[Nurse], top_n: int = 3) -> CandidateShortlist:
    rules_only = not any(
        hospital_history(req.hospital_id, n.id) or _profile_note_matches(n, req.parsed_intent.profile_signals)
        for n in pool
    )
    cands: list[Candidate] = []
    for n in pool:
        score, why = _score_candidate(n, req)
        cands.append(Candidate(nurse=n, score=score, reasoning=why, rules_only=rules_only))
    cands.sort(key=lambda c: c.score, reverse=True)
    top = cands[:top_n]
    shortlist = CandidateShortlist(shift_request_id=req.id, candidates=top)
    shortlist.confidence = _confidence(top, rules_only=rules_only)
    return shortlist


def _confidence(top: list[Candidate], *, rules_only: bool) -> str:
    """Step 5 — agreement-between-signals metric. D#4a §5 definitions.

    High:   strong eligibility + strong historical signal + clear top pick (not a near-tie)
    Medium: mixed signals OR top close to second
    Low:    eligibility-only or unfamiliar
    """
    if rules_only or not top:
        return "low"
    leader = top[0]
    if len(top) >= 2:
        gap = leader.score - top[1].score
        if gap < 3.0:
            return "medium"
    # Strong historical signal = leader's reasoning includes hospital history
    strong_history = any("prior accepted shift" in r for r in leader.reasoning)
    profile_hit    = any("Profile note match: ['" in r or "Profile note match: [" in r and "+" in r for r in leader.reasoning)
    if strong_history and profile_hit:
        return "high"
    if strong_history or profile_hit:
        return "medium"
    return "low"
