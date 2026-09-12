"""Logging goes to stderr and never swallows the program's real output."""

from __future__ import annotations

import logging

import pytest

from app.logging_config import configure_logging, get_logger


@pytest.fixture(autouse=True)
def restore_root_logger():
    """Put the root logger back after each test so runs stay independent."""
    root = logging.getLogger()
    saved_handlers, saved_level = list(root.handlers), root.level
    yield
    root.handlers[:] = saved_handlers
    root.setLevel(saved_level)


def test_configure_logging_sets_the_requested_level() -> None:
    configure_logging("DEBUG")
    assert logging.getLogger().level == logging.DEBUG


def test_level_is_case_insensitive() -> None:
    configure_logging("warning")
    assert logging.getLogger().level == logging.WARNING


def test_calling_twice_does_not_duplicate_handlers() -> None:
    configure_logging("INFO")
    configure_logging("INFO")
    assert len(logging.getLogger().handlers) == 1


def test_logs_go_to_stderr_not_stdout(capsys: pytest.CaptureFixture[str]) -> None:
    configure_logging("INFO")
    get_logger("app.test").info("internal detail")

    captured = capsys.readouterr()
    assert "internal detail" in captured.err
    assert captured.out == ""


def test_http_libraries_are_quietened() -> None:
    configure_logging("DEBUG")
    assert logging.getLogger("httpx").level == logging.WARNING
    assert logging.getLogger("openai").level == logging.WARNING


def test_get_logger_returns_a_named_logger() -> None:
    assert get_logger("app.thing").name == "app.thing"
