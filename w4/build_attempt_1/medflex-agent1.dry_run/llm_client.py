"""Anthropic LLM client for the intake parse call.

Loads the system prompt from prompts/intake_parse_system.txt at runtime (per spec).
Enforces JSON output via Pydantic schema validation.
"""
from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from anthropic import Anthropic

from models import LLMParseResult, Urgency


log = logging.getLogger(__name__)

_DEFAULT_MODEL = "claude-haiku-4-5-20251001"
_SONNET_MODEL = "claude-sonnet-4-6"

_client: Optional[Anthropic] = None
_system_prompt_cache: Optional[str] = None


def _client_instance() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def _load_system_prompt() -> str:
    global _system_prompt_cache
    if _system_prompt_cache is None:
        path = Path(__file__).parent / "prompts" / "intake_parse_system.txt"
        _system_prompt_cache = path.read_text(encoding="utf-8")
    return _system_prompt_cache


class LLMParseError(Exception):
    """Raised when the LLM returns non-JSON or schema-invalid output."""


def _select_model(source_text: str, hospital_profile: Optional[dict]) -> str:
    """Per spec: use Sonnet for CRITICAL urgency requests or high-complexity hospitals.

    We don't yet know urgency before parsing, so we use a keyword heuristic on the
    source text. Hospital "high complexity" is approximated as profile containing
    more than 4 common_unit_types (a rough proxy — spec doesn't define this).
    """
    configured = os.environ.get("INTAKE_LLM_MODEL", _DEFAULT_MODEL)
    lower = source_text.lower()
    critical_kw = ("asap", "immediately", "emergency cover")
    if any(kw in lower for kw in critical_kw):
        return _SONNET_MODEL
    if hospital_profile and len(hospital_profile.get("common_unit_types", []) or []) > 4:
        return _SONNET_MODEL
    return configured


def parse_shift_request(
    source_text: str,
    hospital_profile: Optional[dict],
    now_utc: Optional[datetime] = None,
) -> LLMParseResult:
    """Call the LLM and return a validated LLMParseResult.

    Implements:
      - JSON-mode-style enforcement (parse + Pydantic validate; reject on failure)
      - 15s timeout with one 5s retry (per spec)
      - Model selection per source text content
    """
    system_prompt = _load_system_prompt()
    if now_utc is None:
        now_utc = datetime.now(timezone.utc)

    user_payload = {
        "source_text": source_text[:5000],
        "hospital_profile": hospital_profile or {},
        "current_datetime_utc": now_utc.isoformat(),
    }

    model = _select_model(source_text, hospital_profile)
    client = _client_instance()

    def _attempt() -> str:
        resp = client.messages.create(
            model=model,
            max_tokens=2000,
            system=system_prompt,
            timeout=15.0,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": json.dumps(user_payload)}
                    ],
                }
            ],
        )
        # Concatenate text blocks
        parts = []
        for block in resp.content:
            if getattr(block, "type", None) == "text":
                parts.append(block.text)
        return "".join(parts).strip()

    raw: Optional[str] = None
    try:
        raw = _attempt()
    except Exception as e1:
        log.warning("LLM call failed (%s); retrying once in 5s", e1)
        time.sleep(5)
        try:
            raw = _attempt()
        except Exception as e2:
            raise LLMParseError(f"LLM call failed after retry: {e2}") from e2

    # Strip possible markdown code fences defensively (prompt says not to use them)
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        # remove the first fence line and any trailing fence
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned
        if cleaned.endswith("```"):
            cleaned = cleaned[: -3]
        cleaned = cleaned.strip()
        # Drop a possible leading "json" language tag
        if cleaned.lower().startswith("json\n"):
            cleaned = cleaned[5:].strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise LLMParseError(f"LLM output is not valid JSON: {e}; raw={raw[:500]!r}")

    try:
        return LLMParseResult.model_validate(data)
    except Exception as e:
        raise LLMParseError(f"LLM output failed schema validation: {e}; data={data!r}")
