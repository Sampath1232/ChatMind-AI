import logging
from chatbot.chatbot import Chatbot

def console_chat():
    """
    Console-based chat interface for testing the chatbot
    """
    print("🤖 Chatbot Console Mode")
    print("=" * 50)
    print("Type 'quit', 'exit', or 'bye' to end the conversation")
    print("=" * 50)
    
    # Initialize chatbot
    try:
        chatbot = Chatbot()
        if not chatbot.is_model_loaded():
            print("❌ Error: Chatbot model failed to load. Please check the training data.")
            return
        print("✅ Chatbot initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing chatbot: {str(e)}")
        return
    
    print("\nYou can start chatting now!\n")
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                print("Bot: Goodbye! Have a great day! 👋")
                break
            
            # Skip empty input
            if not user_input:
                continue
            
            # Get chatbot response
            response, intent = chatbot.get_response(user_input)
            
            # Display response with intent
            print(f"Bot: {response}")
            print(f"[Intent: {intent}]\n")
            
        except KeyboardInterrupt:
            print("\n\nBot: Goodbye! Have a great day! 👋")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            continue

if __name__ == "__main__":
    # Configure logging for console mode
    logging.basicConfig(level=logging.WARNING)  # Reduce noise in console
    console_chat()
