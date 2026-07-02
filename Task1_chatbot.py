print("Welcome to Rule-Based Chatbot")

while True:
    user = input("You: ").lower()

    if user == "hi" or user == "hello":
        print("Bot: Hello! How can I help you?")

    elif "how are you" in user:
        print("Bot: I am fine. Thank you!")

    elif "name" in user:
        print("Bot: My name is RuleBot.")

    elif "bye" in user:
        print("Bot: Goodbye!")
        break

    else:
        print("Bot: Sorry, I don't understand.")