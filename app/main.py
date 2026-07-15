from app.llm.chat_client import ChatClient

def main():
    chat = ChatClient()
    print("=" * 50)
    print("Code Smith AI Agent")
    print("=" * 50)

    while True:

        question = input("\nYou: ")

        if question.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        answer = chat.generate(question)

        print("\nAssistant:\n")
        print(answer)
if __name__ == "__main__":
    main()