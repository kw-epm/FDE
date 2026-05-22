"""LLM classifier — task 1.4.

The LLM call is mocked. The PROMPT is real and faithfully translates the APD
"Prompt principles" section. A reviewer reading SYSTEM_PROMPT should be able
to verify the spec round-trip.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import List, Callable, Optional, Dict, Any

from .types import Classification, ViolationType, Action, EscalationReason
from .policy_rag import PolicyChunk


# ---------------------------------------------------------------------------
# Prompt — translates APD "Prompt principles" 1-6 verbatim where possible.
# ---------------------------------------------------------------------------

CLASSIFICATION_JSON_SCHEMA = {
    "type": "object",
    "required": ["violation_type", "confidence", "action",
                 "escalation_reason", "top2_score_delta"],
    "properties": {
        "violation_type": {
            "type": "string",
            "enum": ["spam", "off_topic", "miscategorised", "no_violation"],
        },
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "action": {
            "type": "string",
            "enum": ["remove", "warn", "dismiss_flag", "escalate"],
        },
        "escalation_reason": {
            "type": ["string", "null"],
            "enum": ["vip", "low_confidence", "multi_label",
                     "policy_gap", None],
        },
        "top2_score_delta": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "reasoning": {"type": "string"},
    },
}


SYSTEM_PROMPT = """You are the MiniBase Routine Moderation Agent. Classify and action clear violations from Work Stream 1 (routine spam / clear-violation removal). You do not decide grey-zone cases.

HARD CONSTRAINTS (numbered rules — must not be violated):
Rule 1. If the case has been routed to you, the VIP check has already passed (account is non-VIP). You must not classify or action a VIP account; if you suspect the input is for a VIP, return action="escalate" with escalation_reason="vip".
Rule 2. Output a single JSON object that matches the schema below. No prose outside the JSON.
Rule 3. The invariant action == "escalate" iff escalation_reason != null is mandatory.
Rule 4. If your top-2 violation scores are within 0.15 of each other, return action="escalate" with escalation_reason="multi_label" and report the delta in top2_score_delta.
Rule 5. If no policy chunk above the relevance threshold supports your classification, return action="escalate" with escalation_reason="policy_gap".
Rule 6. If your confidence is below 0.6, return action="escalate" with escalation_reason="low_confidence".
Rule 7. Confidence in [0.6, 0.8) requires a brief reasoning chain in the "reasoning" field. The orchestrator may fetch account history and re-prompt you once before escalating.
Rule 8. Detect post language. For posts in Japanese in the painters-Japan sub-forum, default to action="warn" before escalating to action="remove" — soft-warning preferred (per artefact 4.3).

OUTPUT SCHEMA (strict JSON):
{schema}

ACTION SEMANTICS:
- remove: clear violation; will trigger DELETE /posts/{{id}}
- warn: behaviour is borderline-but-actionable; PM to OP + flag entry
- dismiss_flag: report is invalid; post stays
- escalate: human review required; you MUST set escalation_reason

VIOLATION TYPES:
- spam: commercial / repetitive / bot content
- off_topic: not relevant to the sub-forum's subject
- miscategorised: belongs in a different sub-forum
- no_violation: report is invalid (use with action="dismiss_flag")

FEW-SHOT (Wave 1 launch — replace with Tom-validated examples before production):

Example A — invited critique within sub norms (artefact 4.1):
  Sub-forum: painters
  Post excerpt: "Honestly mate, your highlights are gone... If you're entering this in Golden Demon you'll get DQ'd at the table."
  OP context: thread title invites critique; OP replied positively.
  Output:
  {{"violation_type": "no_violation", "confidence": 0.86, "action": "dismiss_flag", "escalation_reason": null, "top2_score_delta": 0.42, "reasoning": "invited critique within painters norms"}}

[Unconfirmed: requires Tom-validated examples — APD prompt principle 6.]
"""


USER_PROMPT_TEMPLATE = """CASE:
processing_id: {processing_id}
sub_forum_id: {sub_forum_id}
reporter_count: {reporter_count}

POLICY CHUNKS (top {k}):
{policy_chunks}

POST TEXT:
\"\"\"
{post_text}
\"\"\"

Return the JSON object now."""


def render_prompt(
    *,
    processing_id: str,
    sub_forum_id: str,
    reporter_count: int,
    post_text: str,
    chunks: List[PolicyChunk],
) -> Dict[str, str]:
    chunk_lines = "\n".join(
        f"  [{i+1}] (score={c.score:.2f}, source={c.source}) {c.text}"
        for i, c in enumerate(chunks)
    ) or "  (none retrieved — policy gap)"
    user = USER_PROMPT_TEMPLATE.format(
        processing_id=processing_id,
        sub_forum_id=sub_forum_id,
        reporter_count=reporter_count,
        post_text=post_text,
        policy_chunks=chunk_lines,
        k=len(chunks),
    )
    system = SYSTEM_PROMPT.format(
        schema=json.dumps(CLASSIFICATION_JSON_SCHEMA, indent=2)
    )
    return {"system": system, "user": user}


# ---------------------------------------------------------------------------
# Mock LLM call. Real implementation would call Anthropic / OpenAI / etc.
# ---------------------------------------------------------------------------

LlmFn = Callable[[Dict[str, str]], Dict[str, Any]]


def default_mock_llm(prompt: Dict[str, str]) -> Dict[str, Any]:
    """Deterministic stub. Returns a high-confidence spam classification.

    Tests should inject their own LlmFn to exercise specific paths.
    """
    return {
        "violation_type": "spam",
        "confidence": 0.92,
        "action": "remove",
        "escalation_reason": None,
        "top2_score_delta": 0.5,
        "reasoning": "",
    }


def classify(
    *,
    processing_id: str,
    sub_forum_id: str,
    reporter_count: int,
    post_text: str,
    chunks: List[PolicyChunk],
    llm: Optional[LlmFn] = None,
) -> Classification:
    prompt = render_prompt(
        processing_id=processing_id,
        sub_forum_id=sub_forum_id,
        reporter_count=reporter_count,
        post_text=post_text,
        chunks=chunks,
    )
    raw = (llm or default_mock_llm)(prompt)
    # Strict parse — APD: schema is enforced; deviation = error.
    return Classification(
        violation_type=ViolationType(raw["violation_type"]),
        confidence=float(raw["confidence"]),
        action=Action(raw["action"]),
        escalation_reason=(EscalationReason(raw["escalation_reason"])
                           if raw.get("escalation_reason") else None),
        top2_score_delta=float(raw["top2_score_delta"]),
        reasoning=raw.get("reasoning", ""),
    )
