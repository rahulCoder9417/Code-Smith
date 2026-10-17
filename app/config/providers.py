"""The OpenAI-compatible endpoints we can talk to.

Every provider here speaks the same wire format as the OpenAI API, so one
client class works for all of them - only the base_url and the model id
change. Adding a provider means adding a line to this table.
"""

from __future__ import annotations

from typing import Final

PROVIDER_CONFIG: Final[dict[str, dict[str, str]]] = {
    "openai": {
        "base_url": "https://api.openai.com/v1/",
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1/",
    },
    "nvidia": {
        "base_url": "https://integrate.api.nvidia.com/v1",
    },
}
