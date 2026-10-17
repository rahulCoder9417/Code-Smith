"""Loads prompt text from files instead of hard-coding it in Python.

Prompts are the part of an LLM app that changes most often, so they live in
plain .txt files that can be edited, diffed and reviewed without touching
code. Two kinds:

- system/  - who the model is and the rules it follows (loaded as-is).
- user/    - the actual request, with {placeholders} filled in per call.
"""

from __future__ import annotations

from pathlib import Path

from app.logging_config import get_logger

logger = get_logger(__name__)


class PromptManager:
    """Reads prompt files from a base directory.

    `base_dir` is injectable so tests can point at a temporary folder of
    fixture prompts instead of depending on the real ones shipped in the
    package.
    """

    def __init__(self, base_dir: Path | None = None) -> None:
        base = base_dir if base_dir is not None else Path(__file__).parent
        self.system_dir = base / "system"
        self.user_dir = base / "user"

    def available_system_prompts(self) -> list[str]:
        """Names of every system prompt on disk, without the .txt suffix."""
        if not self.system_dir.is_dir():
            return []
        return sorted(path.stem for path in self.system_dir.glob("*.txt"))

    def load_system(self, name: str) -> str:
        """Return the system prompt stored as system/<name>.txt."""
        path = self.system_dir / f"{name}.txt"

        if not path.is_file():
            available = ", ".join(self.available_system_prompts()) or "none found"
            raise FileNotFoundError(f"System prompt {name!r} not found. Available: {available}")

        logger.debug("Loaded system prompt %r", name)
        return path.read_text(encoding="utf-8")

    def render_user(self, template_name: str, **values: object) -> str:
        """Fill user/<template_name>.txt with the given values.

        Missing placeholders raise a ValueError naming the variable, rather
        than the bare KeyError str.format would give us.
        """
        path = self.user_dir / f"{template_name}.txt"

        if not path.is_file():
            raise FileNotFoundError(f"User template {template_name!r} not found in {self.user_dir}")

        template = path.read_text(encoding="utf-8")

        try:
            rendered = template.format(**values)
        except KeyError as error:
            missing = error.args[0]
            raise ValueError(
                f"Template {template_name!r} needs a value for {missing!r}, which was not provided."
            ) from error

        logger.debug("Rendered user template %r", template_name)
        return rendered
