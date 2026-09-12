"""Shared pytest fixtures.

conftest.py is loaded automatically by pytest; anything defined here is
available to every test file without importing it.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.config.settings import Settings
from app.prompts.manager import PromptManager
from tests.fakes import FakeChatClient, FakeOpenAI


@pytest.fixture(autouse=True)
def isolated_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stop the developer's real environment from leaking into the tests.

    autouse=True means this runs for every test. Without it, a machine that
    happens to export LLM_PROVIDER would get different results from a clean
    CI runner - the classic "passes on my machine" bug.
    """
    for name in ("LLM_PROVIDER", "LLM_MODEL", "LLM_API_KEY", "SYSTEM_PROMPT", "LOG_LEVEL"):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def settings() -> Settings:
    """Valid settings built in memory, never read from a real .env file."""
    return Settings(
        _env_file=None,
        llm_provider="groq",
        llm_model="test-model",
        llm_api_key="test-key-not-real",
    )


@pytest.fixture
def fake_client() -> FakeChatClient:
    return FakeChatClient(answers=["a fake explanation"])


@pytest.fixture
def fake_openai() -> FakeOpenAI:
    return FakeOpenAI()


@pytest.fixture
def prompt_dir(tmp_path: Path) -> Path:
    """A throwaway prompt folder, so tests do not depend on shipped prompts."""
    (tmp_path / "system").mkdir()
    (tmp_path / "user").mkdir()
    (tmp_path / "system" / "teacher.txt").write_text("You are a teacher.", encoding="utf-8")
    (tmp_path / "user" / "explanation.txt").write_text(
        "Explain {topic} at {difficulty} level.", encoding="utf-8"
    )
    return tmp_path


@pytest.fixture
def prompts(prompt_dir: Path) -> PromptManager:
    return PromptManager(base_dir=prompt_dir)
