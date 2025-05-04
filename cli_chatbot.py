from chatbot import CollegeChatbot

if __name__ == "__main__":
    bot = CollegeChatbot()
    print("College Chatbot: Blessings upon thee, seeker of wisdom. Type 'quit' to exit.")
    
    while True:
        user_input = input("You: ")
        
        # Check for exit command
        if user_input.lower() in ['quit', 'exit']:
            print("College Chatbot: Until our paths cross again, wise one.")
            break
        
        # Handle user input and fetch response from the chatbot
        response = bot.handle_user_query(user_input, "cli_user", "student")
        
        # Display the bot's response
        print("College Chatbot:", response)
