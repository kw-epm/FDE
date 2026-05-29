"""Happy path: a password-reset chat auto-resolves at Tier 1, grounded in the KB."""
from helpers import ctx, load_chat
from core.disposition import triage
from models import Action


def test_password_reset_is_tier1_kb_cited():
    store, kb, provider, audit = ctx()
    d = triage(load_chat("CS-2026-0000002"), store, kb, provider, audit)
    assert d.tier == 1
    assert d.action == Action.AUTO_RESOLVE
    assert d.kb_articles, "Tier 1 must cite at least one KB article"
    assert d.kb_articles == ["password-reset.md"]
    assert d.draft and "password-reset.md" in d.draft


def test_tier1_draft_is_grounded_not_empty():
    store, kb, provider, audit = ctx()
    d = triage(load_chat("CS-2026-0000002"), store, kb, provider, audit)
    # grounding: the draft quotes article content (the reset URL appears in the KB)
    assert "cloudserve.example/login" in d.draft
