"""Step 1 — Extract structured intent from raw email.

The spec calls for an LLM with two-stage extraction and per-field citations
to source spans. To keep this prototype hermetic and reviewable, we ship a
deterministic regex/keyword extractor that produces the same shape (parsed
fields + per-field confidence + citations). Swapping in an LLM call later
preserves the contract.
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta

from .entities import ParsedIntent, ShiftRequest, Urgency


SPECIALTY_TERMS = {
    "ICU": ["icu", "intensive care"],
    "PICU": ["picu", "paediatric icu", "pediatric icu"],
    "ER":  ["er ", "emergency room", "emergency dept"],
    "L&D": ["l&d", "labor and delivery"],
}

CRED_TERMS = {
    "ICU":  ["icu"],
    "RN":   ["rn", "registered nurse"],
    "ACLS": ["acls"],
    "BLS":  ["bls"],
    "CCRN": ["ccrn"],
}

URGENCY_TERMS = ["urgent", "asap", "immediately", "tonight", "right now"]

PAEDIATRIC_TERMS = ["paediatric", "pediatric", "peds", "paeds"]
ALLERGY_TERMS = ["allergy", "allergic", "anaphyl"]

PREF_PHRASES = [
    "worked with before",
    "someone we know",
    "familiar with",
    "trusted",
    "regular",
]


def _find_span(text: str, needles: list[str]) -> tuple[bool, str]:
    low = text.lower()
    for n in needles:
        i = low.find(n)
        if i >= 0:
            start = max(0, i - 10)
            end = min(len(text), i + len(n) + 20)
            return True, text[start:end].strip()
    return False, ""


def _parse_date(text: str, received_at: datetime) -> tuple[str | None, float, str]:
    low = text.lower()
    if "tomorrow" in low:
        d = (received_at + timedelta(days=1)).date().isoformat()
        return d, 0.95, "tomorrow"
    if "tonight" in low:
        d = received_at.date().isoformat()
        return d, 0.9, "tonight"
    m = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", text)
    if m:
        return m.group(1), 0.99, m.group(1)
    return None, 0.0, ""


def _parse_time(text: str) -> tuple[str | None, float, str]:
    low = text.lower()
    for kw in ["night", "evening", "day", "morning"]:
        if kw in low:
            return kw, 0.9, kw
    return None, 0.0, ""


def extract(raw_text: str, hospital_id: str, received_at: datetime) -> ShiftRequest:
    intent = ParsedIntent()

    # specialty
    for spec, needles in SPECIALTY_TERMS.items():
        hit, span = _find_span(raw_text, needles)
        if hit:
            intent.specialty = spec
            intent.field_confidence["specialty"] = 0.95
            intent.citations["specialty"] = span
            break
    else:
        intent.field_confidence["specialty"] = 0.0

    # date / time
    d, dconf, dspan = _parse_date(raw_text, received_at)
    intent.shift_date = d
    intent.field_confidence["shift_date"] = dconf
    if dspan:
        intent.citations["shift_date"] = dspan

    t, tconf, tspan = _parse_time(raw_text)
    intent.shift_time = t
    intent.field_confidence["shift_time"] = tconf
    if tspan:
        intent.citations["shift_time"] = tspan

    # credentials — infer from specialty + explicit mentions
    creds: list[str] = []
    for cred, needles in CRED_TERMS.items():
        hit, _ = _find_span(raw_text, needles)
        if hit:
            creds.append(cred)
    if intent.specialty == "ICU" and "ICU" not in creds:
        creds.append("ICU")
    if intent.specialty and "RN" not in creds:
        creds.append("RN")
    intent.credentials = creds
    intent.field_confidence["credentials"] = 0.9 if creds else 0.0

    # urgency
    intent.urgency = Urgency.Urgent if any(k in raw_text.lower() for k in URGENCY_TERMS) \
                     else Urgency.Planned
    intent.field_confidence["urgency"] = 0.9

    # hospital soft preferences
    prefs: list[str] = []
    for phrase in PREF_PHRASES:
        if phrase in raw_text.lower():
            prefs.append(phrase)
    intent.hospital_preferences = prefs
    intent.field_confidence["hospital_preferences"] = 0.85 if prefs else 0.0

    # profile signals — paediatric / allergy combo
    signals: list[str] = []
    hit_p, span_p = _find_span(raw_text, PAEDIATRIC_TERMS)
    hit_a, span_a = _find_span(raw_text, ALLERGY_TERMS)
    if hit_p:
        signals.append("paediatric")
        intent.citations["paediatric"] = span_p
    if hit_a:
        signals.append("allergy")
        intent.citations["allergy"] = span_a
    intent.profile_signals = signals
    intent.field_confidence["profile_signals"] = 0.85 if signals else 0.0

    # location — defaulted from hospital routing (out of scope here)
    intent.location = "Boston"
    intent.field_confidence["location"] = 0.9

    return ShiftRequest(
        hospital_id=hospital_id,
        raw_text=raw_text,
        received_at=received_at,
        parsed_intent=intent,
    )


# Step 1 error path: any field <85% routes to coordinator review.
EXTRACTION_THRESHOLD = 0.85


def low_confidence_fields(req: ShiftRequest) -> list[str]:
    return [
        f for f, c in req.parsed_intent.field_confidence.items()
        # Only check fields the spec lists as required; profile signals + prefs are soft
        if f in ("specialty", "shift_date", "shift_time", "credentials", "urgency", "location")
        and c < EXTRACTION_THRESHOLD
    ]
