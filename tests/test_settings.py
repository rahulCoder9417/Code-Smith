"""Config must validate when it is asked for - never at import time."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.config.settings import Settings, get_settings


def test_importing_settings_does_not_require_credentials() -> None:
    """The whole point of the refactor: importing must never explode."""
    import importlib

    import app.config.settings as module

    importlib.reload(module)  # would raise if validation ran at import time


def test_missing_required_values_raise_validation_error() -> None:
    with pytest.raises(ValidationError) as error:
        Settings(_env_file=None)

    message = str(error.value)
    assert "llm_provider" in message
    assert "llm_model" in message
    assert "llm_api_key" in message


def test_unknown_provider_is_rejected_with_a_helpful_message() -> None:
    with pytest.raises(ValidationError) as error:
        Settings(_env_file=None, llm_provider="hal9000", llm_model="m", llm_api_key="k")

    assert "unsupported provider" in str(error.value)
    assert "groq" in str(error.value)  # lists what IS supported


def test_provider_is_normalised_to_lowercase() -> None:
    settings = Settings(_env_file=None, llm_provider="  GROQ  ", llm_model="m", llm_api_key="k")
    assert settings.llm_provider == "groq"


def test_base_url_comes_from_the_provider_table(settings: Settings) -> None:
    assert settings.base_url == "https://api.groq.com/openai/v1/"


def test_api_key_is_hidden_from_reprs_and_logs() -> None:
    settings = Settings(_env_file=None, llm_provider="groq", llm_model="m", llm_api_key="sk-secret")

    assert "sk-secret" not in repr(settings)
    assert "sk-secret" not in str(settings)
    assert settings.llm_api_key.get_secret_value() == "sk-secret"


def test_optional_values_have_defaults(settings: Settings) -> None:
    assert settings.system_prompt == "teacher"
    assert settings.log_level == "INFO"


def test_unknown_log_level_is_rejected() -> None:
    with pytest.raises(ValidationError, match="unknown log level"):
        Settings(_env_file=None, llm_provider="groq", llm_model="m", llm_api_key="k", log_level="LOUD")


def test_settings_are_read_from_environment_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_MODEL", "gpt-from-env")
    monkeypatch.setenv("LLM_API_KEY", "key-from-env")

    settings = Settings(_env_file=None)

    assert settings.llm_provider == "openai"
    assert settings.llm_model == "gpt-from-env"


def test_get_settings_is_cached(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("LLM_MODEL", "m")
    monkeypatch.setenv("LLM_API_KEY", "k")
    get_settings.cache_clear()

    assert get_settings() is get_settings()

    get_settings.cache_clear()
