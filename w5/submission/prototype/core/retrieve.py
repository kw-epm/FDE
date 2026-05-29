"""KBIndex — keyword retrieval over the 20 KB articles (ADR-2, 07 INT-2).

The KB articles are the agent's TOOL SURFACE: a Tier-1 reply must quote a
retrieved article, never latent model knowledge (hard constraint #4).

retrieval_confidence (06 §A.3 step 4) = query-token coverage of the top article:
the fraction of distinct query tokens (len > 2) that appear in the article. This
is the number compared against TAU_R. BM25/embeddings are an easy future swap for
20 docs; coverage is sufficient and transparent for the prototype.
"""
import re
from pathlib import Path


def _tok(s: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", s.lower())


class KBUnavailable(RuntimeError):
    """KB index could not be loaded — a fail-loud condition (06 §A.5)."""


class KBIndex:
    def __init__(self, kb_dir: str):
        self._raw = {}
        self._toks = {}
        for p in sorted(Path(kb_dir).glob("*.md")):
            text = p.read_text()
            self._raw[p.name] = text
            self._toks[p.name] = set(_tok(text))
        if not self._raw:
            raise KBUnavailable(f"No KB articles found under {kb_dir}")

    @property
    def available(self) -> bool:
        return bool(self._raw)

    def text(self, name: str) -> str:
        return self._raw.get(name, "")

    def search(self, query: str, k: int = 3) -> list[tuple[str, float]]:
        """Return [(filename, retrieval_confidence)] for the top-k articles."""
        q = {t for t in _tok(query) if len(t) > 2}
        if not q:
            return []
        scored = [
            (name, round(len(q & toks) / len(q), 3))
            for name, toks in self._toks.items()
        ]
        scored.sort(key=lambda x: -x[1])
        return scored[:k]
