"""The contract every LLM client in this project honours.

Why a Protocol instead of a base class: anything with a matching
generate() method satisfies LLMClient - it does not have to inherit from
anything. That is what lets tests pass in a FakeChatClient that never
touches the network, while the real ChatClient calls a paid API.

This is the seam that makes dependency injection possible: code that needs
an LLM asks for an LLMClient, not for ChatClient specifically.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMClient(Protocol):
    """Something that can turn a system + user prompt into an answer."""

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Send the two prompts to a model and return its reply as text."""
        ...
