"""The real LLM client: talks to any OpenAI-compatible provider."""

from __future__ import annotations

from typing import Any

from openai import OpenAI

from app.config.settings import Settings
from app.llm.base import LLMClient
from app.logging_config import get_logger

logger = get_logger(__name__)


class ChatClient(LLMClient):
    """Sends chat-completion requests to the provider named in Settings.

    Both collaborators are injected rather than reached for:

    - `settings` is passed in, so this class never imports module-level
      globals and a test can hand it any configuration it likes.
    - `client` is the OpenAI SDK object. It defaults to a real one, but a
      test can pass a stub to check the request we build without making a
      network call.
    """

    def __init__(self, settings: Settings, client: Any | None = None) -> None:
        self._settings = settings
        self._client = client if client is not None else self._build_client(settings)
        logger.debug(
            "ChatClient ready: provider=%s model=%s base_url=%s",
            settings.llm_provider,
            settings.llm_model,
            settings.base_url,
        )

    @staticmethod
    def _build_client(settings: Settings) -> OpenAI:
        return OpenAI(
            api_key=settings.llm_api_key.get_secret_value(),
            base_url=settings.base_url,
        )

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Ask the model to answer `user_prompt` while playing `system_prompt`.

        Note there is no memory here: every call sends the whole conversation
        it wants the model to see. The API itself is stateless. Phase 1.4
        builds chat history on top of exactly this fact.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        logger.info("Calling %s (%s)", self._settings.llm_model, self._settings.llm_provider)
        response = self._client.chat.completions.create(
            model=self._settings.llm_model,
            messages=messages,
        )

        content = response.choices[0].message.content
        if content is None:
            logger.warning("Model returned an empty message")
            return ""

        logger.debug("Received %d characters from the model", len(content))
        return content
