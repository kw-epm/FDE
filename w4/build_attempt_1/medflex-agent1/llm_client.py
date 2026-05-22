"""LLM clients.

Two implementations:
  * RealLLMClient — calls Anthropic. Used when ANTHROPIC_API_KEY is set
    and INTAKE_USE_FAKE_LLM is not 'true'.
  * FakeLLMClient — returns canned responses keyed on source_text substrings.
    Used in tests and in the live mock-run when no API key is available.
"""
from __future__ import annotations

import json
import logging
import os
import time as _time
from pathlib import Path
from typing import Callable, Dict, Optional

from models import LLMParseResult

log = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent / "prompts" / "intake_parse_system.txt"


class LLMError(Exception):
    pass


class LLMSchemaError(LLMError):
    """Raised when LLM output cannot be parsed/validated (FM-2)."""


def _load_system_prompt() -> str:
    return PROMPT_PATH.read_text()


# ---------------- Real client ----------------

class RealLLMClient:
    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None, timeout: float = 15.0):
        self.model = model or os.environ.get("INTAKE_LLM_MODEL", "claude-haiku-4-5-20251001")
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.timeout = timeout
        try:
            import anthropic  # noqa: F401
            self._anthropic = anthropic
        except Exception as e:  # noqa: BLE001
            self._anthropic = None
            log.warning("anthropic SDK unavailable: %s", e)

    def parse(self, source_text: str, hospital_profile: dict, current_datetime_utc: str) -> LLMParseResult:
        if self._anthropic is None:
            raise LLMError("anthropic SDK not installed")
        if not self.api_key:
            raise LLMError("ANTHROPIC_API_KEY not set")
        client = self._anthropic.Anthropic(api_key=self.api_key)
        system_prompt = _load_system_prompt()
        user_payload = json.dumps(
            {
                "source_text": source_text,
                "hospital_profile": hospital_profile,
                "current_datetime_utc": current_datetime_utc,
            }
        )

        def _call():
            return client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=system_prompt,
                messages=[{"role": "user", "content": user_payload}],
            )

        try:
            resp = _call()
        except Exception:
            _time.sleep(5)
            resp = _call()  # retry-once; if this raises, caller catches

        # Extract text from the message
        try:
            text = "".join(getattr(b, "text", "") for b in resp.content)
        except Exception as e:  # noqa: BLE001
            raise LLMSchemaError(f"could not read response text: {e}")

        return _parse_and_validate(text)


# ---------------- Fake client ----------------

class FakeLLMClient:
    """Returns canned LLMParseResult JSON keyed on input source_text.

    Match is by substring (case-insensitive) against the source_text. The
    first matching rule wins. If no rule matches, raise LLMError (so tests
    can assert FM-2 paths).
    """

    def __init__(self, canned: Optional[Dict[str, dict]] = None):
        self.canned: Dict[str, dict] = canned or {}
        # log of (source_text, returned_dict) for debugging
        self.calls: list[tuple[str, dict]] = []
        # optional override that returns whatever JSON string the caller wants
        self.raw_override: Optional[Callable[[str], str]] = None

    def add(self, match_substr: str, payload: dict) -> "FakeLLMClient":
        self.canned[match_substr.lower()] = payload
        return self

    def parse(self, source_text: str, hospital_profile: dict, current_datetime_utc: str) -> LLMParseResult:
        if self.raw_override is not None:
            raw = self.raw_override(source_text)
            return _parse_and_validate(raw)
        st = source_text.lower()
        for sub, payload in self.canned.items():
            if sub in st:
                self.calls.append((source_text, payload))
                # validate fresh each call so test mutation can't poison
                return LLMParseResult.model_validate(payload)
        raise LLMSchemaError(f"FakeLLMClient: no canned response for: {source_text[:80]!r}")


def _parse_and_validate(text: str) -> LLMParseResult:
    text = text.strip()
    # tolerate fenced output even though prompt forbids
    if text.startswith("```"):
        text = text.strip("`")
        nl = text.find("\n")
        if nl != -1:
            text = text[nl + 1 :]
        if text.endswith("```"):
            text = text[:-3]
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise LLMSchemaError(f"invalid JSON: {e}") from e
    try:
        return LLMParseResult.model_validate(data)
    except Exception as e:  # noqa: BLE001 — pydantic ValidationError
        raise LLMSchemaError(f"schema validation failed: {e}") from e


def build_default_fake() -> FakeLLMClient:
    """Build a FakeLLMClient with canned responses covering the fixture
    tickets and the EC-1..EC-7 test inputs.
    """
    fake = FakeLLMClient()

    # ticket_001 — happy path ICU nights
    fake.add(
        "icu-trained rn for nights january 20th",
        {
            "shift_date": "2026-01-20",
            "shift_start_time": "19:00",
            "shift_end_time": "07:00",
            "unit_type": "ICU",
            "urgency": "STANDARD",
            "required_credentials": [
                {"credential_category": "RN", "inference_confidence": 0.95},
                {"credential_category": "ICU_CERTIFIED", "inference_confidence": 0.95},
            ],
            "preferred_credentials": [],
            "special_notes": None,
            "overall_confidence_score": 0.95,
            "flagged_ambiguities": [],
        },
    )

    # ticket_002 / EC-1 — ASAP, med-surg
    fake.add(
        "asap",
        {
            "shift_date": None,
            "shift_start_time": None,
            "shift_end_time": None,
            "unit_type": "MED_SURG",
            "urgency": "CRITICAL",
            "required_credentials": [
                {"credential_category": "RN", "inference_confidence": 0.95},
            ],
            "preferred_credentials": [],
            "special_notes": None,
            "overall_confidence_score": 0.55,
            "flagged_ambiguities": [
                {
                    "type": "DATE_UNCLEAR",
                    "description": "No explicit shift date; ASAP keyword used.",
                    "source_excerpt": "ASAP",
                },
                {
                    "type": "TIME_UNCLEAR",
                    "description": "No shift time specified.",
                    "source_excerpt": "ASAP",
                },
            ],
        },
    )

    # ticket_003 / EC-5 — pediatric day shift Feb 3rd
    fake.add(
        "pediatric rn, day shift, february 3rd",
        {
            "shift_date": "2026-02-03",
            "shift_start_time": "07:00",
            "shift_end_time": "19:00",
            "unit_type": "PEDIATRIC",
            "urgency": "STANDARD",
            "required_credentials": [
                {"credential_category": "RN", "inference_confidence": 0.95},
                {"credential_category": "PEDS_CERTIFIED", "inference_confidence": 0.90},
            ],
            "preferred_credentials": [],
            "special_notes": None,
            "overall_confidence_score": 0.93,
            "flagged_ambiguities": [],
        },
    )

    # EC-5 explicit: "RN needed for pediatric ward on February 3rd" — no time
    fake.add(
        "rn needed for pediatric ward on february 3rd",
        {
            "shift_date": "2026-02-03",
            "shift_start_time": None,
            "shift_end_time": None,
            "unit_type": "PEDIATRIC",
            "urgency": "STANDARD",
            "required_credentials": [
                {"credential_category": "RN", "inference_confidence": 0.95},
                {"credential_category": "PEDS_CERTIFIED", "inference_confidence": 0.90},
            ],
            "preferred_credentials": [],
            "special_notes": None,
            "overall_confidence_score": 0.74,
            "flagged_ambiguities": [
                {
                    "type": "TIME_UNCLEAR",
                    "description": "No shift time specified.",
                    "source_excerpt": "February 3rd",
                }
            ],
        },
    )

    # EC-2 — step-down non-standard shorthand
    fake.add(
        "step-down unit nurse",
        {
            "shift_date": "2026-05-25",  # "next Monday" relative resolved
            "shift_start_time": "07:00",
            "shift_end_time": "19:00",
            "unit_type": "GENERAL",
            "urgency": "STANDARD",
            "required_credentials": [
                {"credential_category": "RN", "inference_confidence": 0.75},
            ],
            "preferred_credentials": [],
            "special_notes": None,
            "overall_confidence_score": 0.72,
            "flagged_ambiguities": [
                {
                    "type": "CREDENTIAL_UNCLEAR",
                    "description": "Non-standard credential shorthand 'step-down unit nurse'.",
                    "source_excerpt": "Step-down unit nurse",
                }
            ],
        },
    )

    # EC-3 — conflicting requirements
    fake.add(
        "icu nurse for general ward",
        {
            "shift_date": "2026-05-23",  # tomorrow rel to 2026-05-22
            "shift_start_time": "15:00",
            "shift_end_time": "23:00",
            "unit_type": "GENERAL",
            "urgency": "URGENT",
            "required_credentials": [
                {"credential_category": "RN", "inference_confidence": 0.90},
                {"credential_category": "ICU_CERTIFIED", "inference_confidence": 0.85},
            ],
            "preferred_credentials": [],
            "special_notes": None,
            "overall_confidence_score": 0.55,
            "flagged_ambiguities": [
                {
                    "type": "CONFLICTING_REQUIREMENTS",
                    "description": "ICU-certified nurse requested for a general ward.",
                    "source_excerpt": "ICU nurse for general ward",
                }
            ],
        },
    )

    # EC-7 — multi-shift block (each call returns one shift; the orchestrator
    # is responsible for calling the LLM once per shift. For simplicity we
    # treat the block as ONE LLM call that returns the first shift; the
    # orchestrator uses the special_notes to spawn more. The actual EC-7
    # test in this build expands manually.)
    fake.add(
        "3 icu rns for nights the 20th, 21st, and 22nd",
        {
            "shift_date": "2026-01-20",
            "shift_start_time": "19:00",
            "shift_end_time": "07:00",
            "unit_type": "ICU",
            "urgency": "STANDARD",
            "required_credentials": [
                {"credential_category": "RN", "inference_confidence": 0.95},
                {"credential_category": "ICU_CERTIFIED", "inference_confidence": 0.95},
            ],
            "preferred_credentials": [],
            "special_notes": "Part of 3-shift block request (dates 20th, 21st, 22nd)",
            "overall_confidence_score": 0.95,
            "flagged_ambiguities": [],
        },
    )

    return fake
