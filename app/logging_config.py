"""One place that decides what internal logs look like.

The rule this project follows:

- print()   -> things the *user* asked to see (the answer, the prompts).
- logging   -> things the *developer* needs to see (which model was called,
               how long it took, which prompt file was loaded).

Keeping them separate means we can turn the internal chatter up to DEBUG
while debugging, or off entirely, without touching the program's real
output. Logs go to stderr, so piping the CLI's stdout somewhere still
gives clean output.
"""

from __future__ import annotations

import logging
import sys

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%H:%M:%S"


def configure_logging(level: str = "INFO") -> None:
    """Set up logging for the whole application. Call this once, at startup.

    Only the entry point (main) should call this. Library modules just do
    `logger = logging.getLogger(__name__)` and never configure anything -
    that way importing our code never hijacks someone else's log setup.
    """
    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setFormatter(logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT))

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())

    # The HTTP libraries under the OpenAI SDK log every request at INFO,
    # which drowns out our own messages. Only show their warnings.
    for noisy in ("httpx", "httpcore", "openai"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return the logger a module should use: get_logger(__name__)."""
    return logging.getLogger(name)
