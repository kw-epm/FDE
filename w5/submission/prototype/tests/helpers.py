import os
import tempfile

import config
from adapters import parse_chat, parse_phone
from core.stores import CustomerStore
from core.retrieve import KBIndex
from core.audit import AuditLog
from core.llm import MockProvider

DATA = config.DATA_DIR


def ctx():
    """Fresh deterministic context (offline mock) for a single test."""
    store = CustomerStore(os.path.join(DATA, "customers", "customer_master.csv"))
    kb = KBIndex(os.path.join(DATA, "kb-articles"))
    provider = MockProvider()
    audit = AuditLog(tempfile.mktemp(suffix=".jsonl"))
    return store, kb, provider, audit


def load_chat(tid):
    return parse_chat(os.path.join(DATA, "tickets", f"{tid}.json"))


def load_phone(tid):
    return parse_phone(os.path.join(DATA, "phone-calls", f"{tid}.vtt"))
