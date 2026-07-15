from app.llm.chat_client import ChatClient
from app.prompts.manager import PromptManager
def main():
    chat = ChatClient()
    prompts = PromptManager()
    print("=" * 50)
    print("Code Smith AI Agent")
    print("=" * 50)

    while True:
        topic = input("\n Topic (or exist) :  ")

        if topic.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        difficulty = input("Difficulty: ")

        prompt = prompts.render(
            "explaination",
            topic=topic,
            difficulty=difficulty
        )

        answer = chat.generate(prompt)

        print("\nAssistant:\n")
        print(answer)
if __name__ == "__main__":
    main()