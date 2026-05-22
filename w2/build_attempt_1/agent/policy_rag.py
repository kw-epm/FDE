"""Policy RAG retriever — STUB.

APD: Global moderation policy (14 pages) chunked + indexed; sub-forum norms
structured for 3 of 14 (painters, historical, Japanese painters). Wave 1 falls
back to global policy when sub-forum norm is missing.

Retrieval strategy per APD:
  - sub_forum_id routes to sub-forum-specific norm if structured, else global
  - Top-3 chunks by cosine similarity
  - Violation-type label included as query context

This stub returns synthetic chunks; the real implementation would call a
vector store (e.g. pgvector / Qdrant) — NOT installed per build instructions.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


# Wave 1: 3 of 14 sub-forums have structured norms (artefact 4.3)
STRUCTURED_SUB_FORUMS = {
    "painters",
    "historical",
    "painters-japan",
}


@dataclass
class PolicyChunk:
    chunk_id: str
    text: str
    score: float
    source: str  # 'global' | 'sub_forum:<id>'


class PolicyRag:
    """Stub. Real impl: vector search with a relevance threshold."""

    RELEVANCE_THRESHOLD = 0.35  # below this = "policy gap" (APD escalation trigger)

    def retrieve(
        self,
        post_text: str,
        sub_forum_id: str,
        violation_hint: Optional[str] = None,
        k: int = 3,
    ) -> List[PolicyChunk]:
        # Stub: returns one fake chunk just to exercise wiring
        source = (f"sub_forum:{sub_forum_id}"
                  if sub_forum_id in STRUCTURED_SUB_FORUMS
                  else "global")
        return [
            PolicyChunk(
                chunk_id=f"{source}:0",
                text=f"[stub policy chunk for {source}]",
                score=0.7,
                source=source,
            )
        ]

    def is_policy_gap(self, chunks: List[PolicyChunk]) -> bool:
        """Escalation trigger: no chunks above relevance threshold."""
        if not chunks:
            return True
        return max(c.score for c in chunks) < self.RELEVANCE_THRESHOLD
