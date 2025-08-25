import os
import logging
from flask import Flask, render_template, request, jsonify
from chatbot import Chatbot

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "chatbot_secret_key_2024")

# Initialize chatbot
chatbot = Chatbot()

@app.route('/')
def index():
    """Render the main chat interface"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """
    Handle chat messages from the frontend
    Accepts JSON: {"message": "user input"}
    Returns JSON: {"response": "bot response", "intent": "detected_intent"}
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Invalid request format. Expected JSON with "message" field.'
            }), 400
        
        user_message = data['message'].strip()
        
        if not user_message:
            return jsonify({
                'error': 'Message cannot be empty.'
            }), 400
        
        # Get chatbot response
        response, intent = chatbot.get_response(user_message)
        
        logging.debug(f"User: {user_message} | Intent: {intent} | Response: {response}")
        
        return jsonify({
            'response': response,
            'intent': intent
        })
        
    except Exception as e:
        logging.error(f"Error processing chat request: {str(e)}")
        return jsonify({
            'error': 'An error occurred while processing your message. Please try again.'
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'model_loaded': chatbot.is_model_loaded()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
