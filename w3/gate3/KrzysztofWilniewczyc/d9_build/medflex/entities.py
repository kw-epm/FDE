"""Canonical entities (D#4a §3). Plain dataclasses; in-memory only."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from uuid import uuid4


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:8]}"


class LockState(str, Enum):
    SoftLock = "SoftLock"
    PartialCommitment = "PartialCommitment"
    Confirmed = "Confirmed"
    Released = "Released"


class Urgency(str, Enum):
    Planned = "planned"
    Urgent = "urgent"


@dataclass
class ParsedIntent:
    specialty: Optional[str] = None
    shift_date: Optional[str] = None
    shift_time: Optional[str] = None   # e.g. "night"
    location: Optional[str] = None
    credentials: list[str] = field(default_factory=list)
    urgency: Urgency = Urgency.Planned
    hospital_preferences: list[str] = field(default_factory=list)  # soft signals
    profile_signals: list[str] = field(default_factory=list)       # e.g. "paediatric allergy"
    # Per-field confidence (D#4a step 1: each field validated against source spans)
    field_confidence: dict[str, float] = field(default_factory=dict)
    citations: dict[str, str] = field(default_factory=dict)        # field -> source span


@dataclass
class ShiftRequest:
    hospital_id: str
    raw_text: str
    received_at: datetime
    parsed_intent: ParsedIntent = field(default_factory=ParsedIntent)
    id: str = field(default_factory=lambda: _id("sr"))


@dataclass
class Nurse:
    name: str
    specialties: list[str]
    credentials: list[str]
    credential_expiry: datetime          # earliest expiry across required certs
    available: bool
    location: str
    distance_km: float
    dnr_hospitals: list[str] = field(default_factory=list)   # do-not-rotate
    profile_notes: str = ""              # unstructured (per A5)
    id: str = field(default_factory=lambda: _id("n"))


@dataclass
class Candidate:
    nurse: Nurse
    score: float = 0.0
    reasoning: list[str] = field(default_factory=list)        # citations
    rules_only: bool = False


@dataclass
class CandidateShortlist:
    shift_request_id: str
    candidates: list[Candidate]
    confidence: str = "low"             # high|medium|low
    id: str = field(default_factory=lambda: _id("sl"))


@dataclass
class NurseOffer:
    shortlist_id: str
    nurse_id: str
    shift_id: str
    offered_at: datetime
    channel: list[str]                  # ["sms", "email"]
    window: timedelta                   # Decision 2 window
    id: str = field(default_factory=lambda: _id("of"))


@dataclass
class NurseAcceptance:
    offer_id: str
    response: str                       # yes|no|timeout
    responded_at: datetime


@dataclass
class HospitalSubmission:
    nurse_id: str
    hospital_id: str
    shift_id: str
    submitted_at: datetime
    reasoning_summary: str
    id: str = field(default_factory=lambda: _id("hs"))


@dataclass
class HospitalAcceptance:
    submission_id: str
    response: str                       # yes|no
    responded_at: datetime


@dataclass
class ConfirmedFill:
    nurse_id: str
    shift_id: str
    confirmed_at: datetime
    id: str = field(default_factory=lambda: _id("cf"))


@dataclass
class LockRecord:
    candidate_id: str
    current_state: LockState
    entered_at: datetime
    expires_at: datetime


@dataclass
class HospitalAcceptanceRecord:
    """Historical context: which nurses Hospital A has accepted before."""
    hospital_id: str
    nurse_id: str
    accepted: bool
    when: datetime
    note: str = ""
