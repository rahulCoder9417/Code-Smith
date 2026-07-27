from app.config.settings import SYSTEM_PROMPT
from app.llm.chat_client import ChatClient
from app.prompts.manager import PromptManager


def main():

    chat = ChatClient()
    prompts = PromptManager()

    print("=" * 50)
    print("Code Smith AI Agent")
    print("=" * 50)

    while True:

        topic = input("\nTopic: ")

        if topic.lower() in {"exit", "quit"}:
            break

        difficulty = input("Difficulty: ")

        system = prompts.load_system(
            SYSTEM_PROMPT
        )

        user = prompts.render_user(
            "explanation",
            topic=topic,
            difficulty=difficulty
        )

        answer = chat.generate(
            system,
            user
        )

        print("\nAssistant:\n")
        print(answer)


if __name__ == "__main__":
    main()