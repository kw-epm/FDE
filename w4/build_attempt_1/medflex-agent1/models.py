"""Pydantic models for ShiftRequest and sub-entities."""
from __future__ import annotations

from datetime import date, datetime, time
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ---------------- Enums ----------------

class CredentialCategory(str, Enum):
    RN = "RN"
    LPN = "LPN"
    CNA = "CNA"
    NP = "NP"
    CRNA = "CRNA"
    ICU_CERTIFIED = "ICU_CERTIFIED"
    ER_CERTIFIED = "ER_CERTIFIED"
    OR_CERTIFIED = "OR_CERTIFIED"
    PEDS_CERTIFIED = "PEDS_CERTIFIED"
    ONCOLOGY_CERTIFIED = "ONCOLOGY_CERTIFIED"
    L_D_CERTIFIED = "L_D_CERTIFIED"
    PSYCH_CERTIFIED = "PSYCH_CERTIFIED"
    BLS = "BLS"
    ACLS = "ACLS"
    PALS = "PALS"


class UnitType(str, Enum):
    ICU = "ICU"
    ER = "ER"
    OR = "OR"
    MED_SURG = "MED_SURG"
    PEDIATRIC = "PEDIATRIC"
    ONCOLOGY = "ONCOLOGY"
    LABOR_DELIVERY = "LABOR_DELIVERY"
    PSYCH = "PSYCH"
    GENERAL = "GENERAL"
    UNKNOWN = "UNKNOWN"


class Urgency(str, Enum):
    STANDARD = "STANDARD"
    URGENT = "URGENT"
    CRITICAL = "CRITICAL"


class ShiftRequestStatus(str, Enum):
    PENDING_MATCH = "PENDING_MATCH"
    CLARIFICATION_NEEDED = "CLARIFICATION_NEEDED"
    MATCHED = "MATCHED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"


class AmbiguityType(str, Enum):
    CREDENTIAL_UNCLEAR = "CREDENTIAL_UNCLEAR"
    DATE_UNCLEAR = "DATE_UNCLEAR"
    TIME_UNCLEAR = "TIME_UNCLEAR"
    UNIT_TYPE_UNCLEAR = "UNIT_TYPE_UNCLEAR"
    CONFLICTING_REQUIREMENTS = "CONFLICTING_REQUIREMENTS"
    INSUFFICIENT_INFORMATION = "INSUFFICIENT_INFORMATION"
    DUPLICATE_SUSPECTED = "DUPLICATE_SUSPECTED"


class ParsedBy(str, Enum):
    AGENT_1 = "AGENT_1"
    COORDINATOR = "COORDINATOR"


# ---------------- Sub-entities ----------------

class CredentialRequirement(BaseModel):
    credential_category: CredentialCategory
    inference_confidence: float = Field(ge=0.0, le=1.0)


class AmbiguityFlag(BaseModel):
    type: AmbiguityType
    description: str = Field(max_length=500)
    source_excerpt: str = Field(max_length=300)


# ---------------- LLM I/O ----------------

class LLMParseResult(BaseModel):
    """Schema the LLM must return. Mirrors the contract in the system prompt."""
    shift_date: Optional[date] = None
    shift_start_time: Optional[time] = None
    shift_end_time: Optional[time] = None
    unit_type: UnitType
    urgency: Urgency
    required_credentials: List[CredentialRequirement]
    preferred_credentials: List[CredentialRequirement] = Field(default_factory=list)
    special_notes: Optional[str] = None
    overall_confidence_score: float = Field(ge=0.0, le=1.0)
    flagged_ambiguities: List[AmbiguityFlag] = Field(default_factory=list)

    @field_validator("shift_start_time", "shift_end_time", mode="before")
    @classmethod
    def _coerce_time(cls, v):
        if v is None or v == "":
            return None
        if isinstance(v, str) and len(v) == 5:
            # accept HH:MM
            return v
        return v


# ---------------- ShiftRequest entity ----------------

class ShiftRequest(BaseModel):
    id: Optional[UUID] = None
    servicenow_ticket_id: str = Field(max_length=64)
    ticket_sequence_num: int = 1
    hospital_id: str
    source_text: str = Field(max_length=5000)
    hospital_location: Optional[dict] = None
    shift_date: Optional[date] = None
    shift_start_time: Optional[time] = None
    shift_end_time: Optional[time] = None
    shift_duration_hours: Optional[float] = None
    unit_type: UnitType = UnitType.UNKNOWN
    urgency: Urgency = Urgency.STANDARD
    required_credentials: List[CredentialRequirement] = Field(default_factory=list)
    preferred_credentials: List[CredentialRequirement] = Field(default_factory=list)
    special_notes: Optional[str] = None
    status: ShiftRequestStatus = ShiftRequestStatus.PENDING_MATCH
    confidence_score: float = Field(ge=0.0, le=1.0, default=0.0)
    flagged_ambiguities: List[AmbiguityFlag] = Field(default_factory=list)
    parsed_by: ParsedBy = ParsedBy.AGENT_1
    coordinator_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
