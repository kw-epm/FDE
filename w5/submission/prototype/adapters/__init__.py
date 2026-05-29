"""Channel adapters: chat JSON / email .eml / phone .vtt -> normalised Ticket (06 §0.1)."""
from adapters.chat import parse_chat
from adapters.email import parse_email
from adapters.phone import parse_phone

__all__ = ["parse_chat", "parse_email", "parse_phone", "load_ticket"]


def load_ticket(path: str):
    """Dispatch on extension. Convenience for the demo / UI."""
    if path.endswith(".json"):
        return parse_chat(path)
    if path.endswith(".vtt"):
        return parse_phone(path)
    if path.endswith(".eml"):
        return parse_email(path)
    raise ValueError(f"Unsupported ticket file: {path}")
