"""Application configuration, loaded from the environment and validated.

The old version read os.getenv() and raised at *import* time, which meant
merely importing anything under app/ required a valid .env - so tests could
not import the code without real credentials.

Here the config is a pydantic-settings model instead. Building a Settings
object is an explicit, callable step, so validation errors happen when
someone asks for the settings, not when Python imports the module.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config.providers import PROVIDER_CONFIG

LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


class Settings(BaseSettings):
    """Everything the app needs to know, read from .env / the environment.

    Each field name maps to the upper-case environment variable of the same
    name: llm_provider <- LLM_PROVIDER, and so on.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    llm_provider: str = Field(description="Which API to call: openai, gemini, groq or nvidia.")
    llm_model: str = Field(description="Model id, spelled the way the provider spells it.")
    llm_api_key: SecretStr = Field(description="API key for the provider above.")

    system_prompt: str = Field(
        default="teacher",
        description="Name of a file in app/prompts/system/, without the .txt suffix.",
    )
    log_level: str = Field(default="INFO", description="Logging verbosity for internal logs.")

    @field_validator("llm_provider")
    @classmethod
    def _provider_must_be_known(cls, value: str) -> str:
        provider = value.strip().lower()
        if provider not in PROVIDER_CONFIG:
            supported = ", ".join(sorted(PROVIDER_CONFIG))
            raise ValueError(f"unsupported provider {value!r}; supported providers are: {supported}")
        return provider

    @field_validator("log_level")
    @classmethod
    def _log_level_must_be_known(cls, value: str) -> str:
        level = value.strip().upper()
        if level not in LOG_LEVELS:
            raise ValueError(f"unknown log level {value!r}; use one of: {', '.join(sorted(LOG_LEVELS))}")
        return level

    @property
    def base_url(self) -> str:
        """The OpenAI-compatible endpoint for the configured provider."""
        return PROVIDER_CONFIG[self.llm_provider]["base_url"]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the app's settings, building them once and reusing them.

    lru_cache makes this a lazy singleton: the .env file is read on the first
    call and cached afterwards. Tests that need different values build their
    own Settings(...) directly instead of calling this.
    """
    return Settings()
