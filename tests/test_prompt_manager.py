"""Prompt loading and rendering, against a temp folder of fixture prompts."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.prompts.manager import PromptManager


def test_loads_a_system_prompt(prompts: PromptManager) -> None:
    assert prompts.load_system("teacher") == "You are a teacher."


def test_missing_system_prompt_lists_the_available_ones(prompts: PromptManager) -> None:
    with pytest.raises(FileNotFoundError) as error:
        prompts.load_system("nonexistent")

    assert "nonexistent" in str(error.value)
    assert "teacher" in str(error.value)  # tells you what you could have used


def test_renders_a_user_template(prompts: PromptManager) -> None:
    rendered = prompts.render_user("explanation", topic="decorators", difficulty="beginner")
    assert rendered == "Explain decorators at beginner level."


def test_missing_template_variable_names_the_variable(prompts: PromptManager) -> None:
    with pytest.raises(ValueError, match="difficulty"):
        prompts.render_user("explanation", topic="decorators")


def test_missing_user_template_raises(prompts: PromptManager) -> None:
    with pytest.raises(FileNotFoundError, match="quiz"):
        prompts.render_user("quiz", topic="x")


def test_available_system_prompts_is_sorted(prompt_dir: Path) -> None:
    (prompt_dir / "system" / "debugger.txt").write_text("debug", encoding="utf-8")
    manager = PromptManager(base_dir=prompt_dir)

    assert manager.available_system_prompts() == ["debugger", "teacher"]


def test_real_shipped_prompts_are_loadable() -> None:
    """The prompts that actually ship must exist and be readable."""
    manager = PromptManager()

    assert "teacher" in manager.available_system_prompts()
    assert manager.load_system("teacher").strip()
    assert "decorators" in manager.render_user(
        "explanation", topic="decorators", difficulty="beginner"
    )
