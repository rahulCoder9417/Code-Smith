"""The Code Smith command-line app.

Structure worth noticing: main() does the wiring (read config, build the
real client) and run_cli() does the work. run_cli() receives everything it
needs as arguments - the LLM client, the prompt manager, and even the
functions used for input and output - so a test can drive the whole loop
with a fake client and scripted keystrokes, with nothing to mock.
"""

from __future__ import annotations

from collections.abc import Callable

from app.config.settings import Settings, get_settings
from app.llm.base import LLMClient
from app.llm.chat_client import ChatClient
from app.logging_config import configure_logging, get_logger
from app.prompts.manager import PromptManager

logger = get_logger(__name__)

BANNER = "=" * 50
EXIT_WORDS = {"exit", "quit", "q"}


def run_cli(
    client: LLMClient,
    prompts: PromptManager,
    system_prompt_name: str,
    read_input: Callable[[str], str] = input,
    write_output: Callable[[str], None] = print,
) -> None:
    """Run the ask-a-topic loop until the user exits or the input ends."""
    system_prompt = prompts.load_system(system_prompt_name)

    write_output(BANNER)
    write_output("Code Smith AI Agent")
    write_output(f"Ask about any topic. Type {' / '.join(sorted(EXIT_WORDS))} to leave.")
    write_output(BANNER)

    while True:
        try:
            topic = read_input("\nTopic: ").strip()
        except EOFError:
            logger.debug("Input stream closed; leaving the loop")
            break

        if not topic:
            write_output("Please type a topic.")
            continue

        if topic.lower() in EXIT_WORDS:
            break

        try:
            difficulty = read_input("Difficulty: ").strip() or "beginner"
        except EOFError:
            break

        user_prompt = prompts.render_user("explanation", topic=topic, difficulty=difficulty)

        logger.info("Explaining %r at %r level", topic, difficulty)
        answer = client.generate(system_prompt, user_prompt)

        write_output("\nAssistant:\n")
        write_output(answer)

    write_output("\nBye.")


def build_client(settings: Settings) -> LLMClient:
    """Create the real, network-calling client from validated settings."""
    return ChatClient(settings)


def main() -> None:
    """Entry point: load config, wire the pieces together, run the loop."""
    settings = get_settings()
    configure_logging(settings.log_level)

    logger.debug("Starting Code Smith with provider %s", settings.llm_provider)

    run_cli(
        client=build_client(settings),
        prompts=PromptManager(),
        system_prompt_name=settings.system_prompt,
    )


if __name__ == "__main__":
    main()
