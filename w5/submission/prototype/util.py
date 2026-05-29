"""Keyword matching helper.

SPIKE FINDING #3: naive substring matching gives false positives — "sue" matches
inside "issue", false-flagging an account-access ticket as LEGAL. Match on word
boundaries so a lexicon entry only fires as a whole word/phrase.
"""
import re
from functools import lru_cache


@lru_cache(maxsize=1024)
def _pat(kw: str):
    return re.compile(r"\b" + re.escape(kw) + r"\b", re.IGNORECASE)


def kw_match(text: str, keywords) -> bool:
    return any(_pat(k).search(text) for k in keywords)


def kw_hits(text: str, keywords) -> list[str]:
    return [k for k in keywords if _pat(k).search(text)]
