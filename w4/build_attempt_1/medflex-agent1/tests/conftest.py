"""Shared pytest fixtures."""
import os
import sys
from pathlib import Path

import pytest

# Make the project root importable as flat modules (agent1_intake, db, etc.)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import db  # noqa: E402
from hospital_api import HospitalAPIClient  # noqa: E402
from llm_client import FakeLLMClient, build_default_fake  # noqa: E402


@pytest.fixture
def conn():
    c = db.connect(":memory:")
    yield c
    c.close()


@pytest.fixture
def hospital_client(monkeypatch):
    monkeypatch.setenv("MEDFLEX_API_BASE_URL", "mock")
    return HospitalAPIClient()


@pytest.fixture
def fake_llm():
    return build_default_fake()


@pytest.fixture(autouse=True)
def _mock_env(monkeypatch):
    monkeypatch.setenv("SERVICENOW_BASE_URL", "mock")
    monkeypatch.setenv("MEDFLEX_API_BASE_URL", "mock")
    monkeypatch.setenv("INTAKE_USE_FAKE_LLM", "true")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
