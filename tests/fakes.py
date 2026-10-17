"""Stand-ins for the real, network-calling objects.

Rule for this project: **tests never call a real LLM.** A real call costs
money, needs a key, returns something different every run, and fails when
the wifi does - none of which belongs in a unit test. Quality of the real
model's answers is measured separately, with evals (Chapter 10).

So the tests use these two fakes:

- FakeChatClient  - satisfies the LLMClient protocol; records the prompts
                    it was given and returns canned answers.
- FakeOpenAI      - imitates just the sliver of the OpenAI SDK that
                    ChatClient touches, so we can assert on the exact
                    request ChatClient builds.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RecordedCall:
    """One generate() call, captured for the test to inspect."""

    system_prompt: str
    user_prompt: str


class FakeChatClient:
    """An LLMClient that answers from a script instead of from a model."""

    def __init__(self, answers: list[str] | None = None) -> None:
        self.answers = list(answers) if answers else ["a fake explanation"]
        self.calls: list[RecordedCall] = []

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        self.calls.append(RecordedCall(system_prompt=system_prompt, user_prompt=user_prompt))
        # Repeat the last answer if the test asks for more calls than answers.
        index = min(len(self.calls) - 1, len(self.answers) - 1)
        return self.answers[index]


# --- A minimal imitation of the OpenAI SDK response shape -----------------
# ChatClient reads response.choices[0].message.content, so that is all we
# need to build.


@dataclass
class _FakeMessage:
    content: str | None


@dataclass
class _FakeChoice:
    message: _FakeMessage


@dataclass
class _FakeResponse:
    choices: list[_FakeChoice]


class _FakeCompletions:
    def __init__(self, owner: FakeOpenAI) -> None:
        self._owner = owner

    def create(self, **kwargs: Any) -> _FakeResponse:
        self._owner.requests.append(kwargs)
        return _FakeResponse(choices=[_FakeChoice(message=_FakeMessage(content=self._owner.reply))])


class _FakeChat:
    def __init__(self, owner: FakeOpenAI) -> None:
        self.completions = _FakeCompletions(owner)


@dataclass
class FakeOpenAI:
    """Imitates openai.OpenAI well enough for ChatClient, with no network."""

    reply: str | None = "hello from the fake model"
    requests: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.chat = _FakeChat(self)
