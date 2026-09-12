"""The CLI loop, driven end to end with a fake client and scripted input.

No mocking library needed: run_cli() takes its dependencies as arguments,
so the test simply passes in different ones.
"""

from __future__ import annotations

from collections.abc import Callable

import pytest

from app.main import run_cli
from app.prompts.manager import PromptManager
from tests.fakes import FakeChatClient


def scripted_input(*answers: str) -> Callable[[str], str]:
    """Return an input() replacement that replays the given answers."""
    queue = list(answers)

    def read(_prompt: str) -> str:
        if not queue:
            raise EOFError
        return queue.pop(0)

    return read


def test_asks_the_model_and_prints_the_answer(
    fake_client: FakeChatClient, prompts: PromptManager
) -> None:
    printed: list[str] = []

    run_cli(
        client=fake_client,
        prompts=prompts,
        system_prompt_name="teacher",
        read_input=scripted_input("decorators", "beginner", "exit"),
        write_output=printed.append,
    )

    assert len(fake_client.calls) == 1
    call = fake_client.calls[0]
    assert call.system_prompt == "You are a teacher."
    assert call.user_prompt == "Explain decorators at beginner level."
    assert "a fake explanation" in printed


@pytest.mark.parametrize("word", ["exit", "quit", "q", "EXIT", "Quit"])
def test_exit_words_end_the_loop_without_calling_the_model(
    word: str, fake_client: FakeChatClient, prompts: PromptManager
) -> None:
    run_cli(
        client=fake_client,
        prompts=prompts,
        system_prompt_name="teacher",
        read_input=scripted_input(word),
        write_output=lambda _: None,
    )

    assert fake_client.calls == []


def test_end_of_input_ends_the_loop(fake_client: FakeChatClient, prompts: PromptManager) -> None:
    """Ctrl-D / a closed pipe should exit cleanly, not raise EOFError."""
    run_cli(
        client=fake_client,
        prompts=prompts,
        system_prompt_name="teacher",
        read_input=scripted_input(),
        write_output=lambda _: None,
    )

    assert fake_client.calls == []


def test_blank_topic_is_reprompted_not_sent(
    fake_client: FakeChatClient, prompts: PromptManager
) -> None:
    printed: list[str] = []

    run_cli(
        client=fake_client,
        prompts=prompts,
        system_prompt_name="teacher",
        read_input=scripted_input("", "   ", "exit"),
        write_output=printed.append,
    )

    assert fake_client.calls == []
    assert printed.count("Please type a topic.") == 2


def test_blank_difficulty_defaults_to_beginner(
    fake_client: FakeChatClient, prompts: PromptManager
) -> None:
    run_cli(
        client=fake_client,
        prompts=prompts,
        system_prompt_name="teacher",
        read_input=scripted_input("decorators", "", "exit"),
        write_output=lambda _: None,
    )

    assert "beginner" in fake_client.calls[0].user_prompt


def test_multiple_questions_in_one_session(
    fake_client: FakeChatClient, prompts: PromptManager
) -> None:
    run_cli(
        client=fake_client,
        prompts=prompts,
        system_prompt_name="teacher",
        read_input=scripted_input("decorators", "beginner", "generators", "advanced", "exit"),
        write_output=lambda _: None,
    )

    assert len(fake_client.calls) == 2
    assert "generators" in fake_client.calls[1].user_prompt


def test_system_prompt_is_loaded_once_not_per_question(
    fake_client: FakeChatClient, prompts: PromptManager
) -> None:
    run_cli(
        client=fake_client,
        prompts=prompts,
        system_prompt_name="teacher",
        read_input=scripted_input("a", "beginner", "b", "beginner", "exit"),
        write_output=lambda _: None,
    )

    assert {call.system_prompt for call in fake_client.calls} == {"You are a teacher."}
