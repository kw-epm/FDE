"""Pydantic models mirroring the shared glossary in spec.md.

These models are used to:
  1. Validate LLM JSON output (LLMParseResult).
  2. Represent in-memory ShiftRequest entities before persistence.
  3. Capture sub-entities (CredentialRequirement, AmbiguityFlag).
"""
from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import Optional, List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict, field_validator


# ---------------------------------------------------------------------------
# Enums (shared glossary)
# ---------------------------------------------------------------------------


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


class AmbiguityType(str, Enum):
    CREDENTIAL_UNCLEAR = "CREDENTIAL_UNCLEAR"
    DATE_UNCLEAR = "DATE_UNCLEAR"
    TIME_UNCLEAR = "TIME_UNCLEAR"
    UNIT_TYPE_UNCLEAR = "UNIT_TYPE_UNCLEAR"
    CONFLICTING_REQUIREMENTS = "CONFLICTING_REQUIREMENTS"
    INSUFFICIENT_INFORMATION = "INSUFFICIENT_INFORMATION"
    DUPLICATE_SUSPECTED = "DUPLICATE_SUSPECTED"


class ShiftRequestStatus(str, Enum):
    PENDING_MATCH = "PENDING_MATCH"
    CLARIFICATION_NEEDED = "CLARIFICATION_NEEDED"
    MATCHED = "MATCHED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"


class ParsedBy(str, Enum):
    AGENT_1 = "AGENT_1"
    COORDINATOR = "COORDINATOR"


# ---------------------------------------------------------------------------
# Sub-entities
# ---------------------------------------------------------------------------


class CredentialRequirement(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    credential_category: CredentialCategory
    inference_confidence: float = Field(ge=0.0, le=1.0)

    @field_validator("inference_confidence")
    @classmethod
    def _round_two(cls, v: float) -> float:
        return round(float(v), 2)


class AmbiguityFlag(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    type: AmbiguityType
    description: str = Field(max_length=500)
    source_excerpt: str = Field(max_length=300)


# ---------------------------------------------------------------------------
# LLM output schema (what the model returns; pre-persistence)
# ---------------------------------------------------------------------------


class LLMParseResult(BaseModel):
    """Schema for the JSON object the LLM must return.

    Matches the OUTPUT SCHEMA in prompts/intake_parse_system.txt.
    """
    model_config = ConfigDict(use_enum_values=True)

    shift_date: Optional[date] = None
    shift_start_time: Optional[time] = None
    shift_end_time: Optional[time] = None
    unit_type: UnitType
    urgency: Urgency
    required_credentials: List[CredentialRequirement] = Field(default_factory=list)
    preferred_credentials: List[CredentialRequirement] = Field(default_factory=list)
    special_notes: Optional[str] = None
    overall_confidence_score: float = Field(ge=0.0, le=1.0)
    flagged_ambiguities: List[AmbiguityFlag] = Field(default_factory=list)

    @field_validator("overall_confidence_score")
    @classmethod
    def _round_two(cls, v: float) -> float:
        return round(float(v), 2)


# ---------------------------------------------------------------------------
# ShiftRequest entity (post-persistence shape)
# ---------------------------------------------------------------------------


class ShiftRequest(BaseModel):
    model_config = ConfigDict(use_enum_values=True, arbitrary_types_allowed=True)

    id: UUID = Field(default_factory=uuid4)
    servicenow_ticket_id: str = Field(max_length=64)
    ticket_sequence_num: int = 1
    hospital_id: str
    source_text: str = Field(max_length=5000)
    hospital_location: Optional[dict] = None
    shift_date: Optional[date] = None
    shift_start_time: Optional[time] = None
    shift_end_time: Optional[time] = None
    unit_type: UnitType = UnitType.UNKNOWN
    urgency: Urgency = Urgency.STANDARD
    required_credentials: List[CredentialRequirement] = Field(default_factory=list)
    preferred_credentials: List[CredentialRequirement] = Field(default_factory=list)
    special_notes: Optional[str] = Field(default=None, max_length=2000)
    status: ShiftRequestStatus = ShiftRequestStatus.PENDING_MATCH
    confidence_score: float = Field(ge=0.0, le=1.0)
    flagged_ambiguities: List[AmbiguityFlag] = Field(default_factory=list)
    parsed_by: ParsedBy = ParsedBy.AGENT_1
    coordinator_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def shift_duration_hours(self) -> Optional[float]:
        """Computed: hours between start and end time. Handles midnight crossover."""
        if self.shift_start_time is None or self.shift_end_time is None:
            return None
        s = self.shift_start_time
        e = self.shift_end_time
        start_minutes = s.hour * 60 + s.minute
        end_minutes = e.hour * 60 + e.minute
        if end_minutes <= start_minutes:
            # midnight crossover
            end_minutes += 24 * 60
        return round((end_minutes - start_minutes) / 60.0, 2)


# ---------------------------------------------------------------------------
# ServiceNow ticket shape
# ---------------------------------------------------------------------------


class ServiceNowTicket(BaseModel):
    sys_id: str
    description: str
    u_hospital_id: str
    sys_created_on: str  # ISO 8601 string
