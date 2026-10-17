"""ChatClient builds the right request - checked without any network call."""

from __future__ import annotations

from app.config.settings import Settings
from app.llm.base import LLMClient
from app.llm.chat_client import ChatClient
from tests.fakes import FakeOpenAI


def test_chat_client_satisfies_the_llm_client_protocol(settings: Settings) -> None:
    client = ChatClient(settings, client=FakeOpenAI())
    assert isinstance(client, LLMClient)


def test_sends_the_configured_model(settings: Settings, fake_openai: FakeOpenAI) -> None:
    ChatClient(settings, client=fake_openai).generate("system", "user")

    assert fake_openai.requests[0]["model"] == "test-model"


def test_sends_system_then_user_message(settings: Settings, fake_openai: FakeOpenAI) -> None:
    ChatClient(settings, client=fake_openai).generate("be a teacher", "explain decorators")

    messages = fake_openai.requests[0]["messages"]
    assert messages == [
        {"role": "system", "content": "be a teacher"},
        {"role": "user", "content": "explain decorators"},
    ]


def test_returns_the_models_text(settings: Settings) -> None:
    fake = FakeOpenAI(reply="decorators wrap functions")

    assert ChatClient(settings, client=fake).generate("s", "u") == "decorators wrap functions"


def test_empty_response_becomes_an_empty_string(settings: Settings) -> None:
    """Providers can return content=None; callers should still get a str."""
    fake = FakeOpenAI(reply=None)

    assert ChatClient(settings, client=fake).generate("s", "u") == ""


def test_each_call_is_independent(settings: Settings, fake_openai: FakeOpenAI) -> None:
    """The API is stateless: nothing from call one leaks into call two.

    This is the fact Phase 1.4 (conversation memory) is built on.
    """
    client = ChatClient(settings, client=fake_openai)
    client.generate("s", "first question")
    client.generate("s", "second question")

    first, second = fake_openai.requests
    assert len(first["messages"]) == len(second["messages"]) == 2
    assert second["messages"][1]["content"] == "second question"
