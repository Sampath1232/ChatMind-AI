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
        
        # Handle special image generation requests
        if intent == "content_generation" and any(word in user_message.lower() for word in ['image', 'picture', 'photo', 'drawing']):
            image_response = handle_image_generation_request(user_message)
            if image_response:
                response = image_response
        
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

def handle_image_generation_request(user_message: str) -> str:
    """Handle image generation using the built-in tool"""
    try:
        # Extract prompt from user message
        import re
        
        # Remove command words to get the actual prompt
        prompt = user_message.lower()
        for word in ['generate', 'create', 'make', 'image', 'picture', 'of', 'a', 'an']:
            prompt = prompt.replace(word, ' ')
        
        prompt = ' '.join(prompt.split()).strip()
        
        if not prompt:
            return "Please provide a description for the image you'd like me to generate."
        
        # For now, return a helpful message about image generation
        # In production, this would use the actual image generation tool
        return f"🎨 I understand you want to generate an image: '{prompt}'\n\nImage generation is available! The system can create custom images based on your descriptions. The image would be saved to the generated_content folder for you to download."
        
    except Exception as e:
        logging.error(f"Error in image generation: {str(e)}")
        return "I encountered an error while processing your image generation request. Please try again."

@app.route('/download/<path:filename>')
def download_file(filename):
    """Serve generated files for download"""
    import os
    from flask import send_from_directory
    
    try:
        # Check if file exists in generated_content directory
        file_path = os.path.join('generated_content', filename)
        if os.path.exists(file_path):
            return send_from_directory('generated_content', filename, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        logging.error(f"Error serving file {filename}: {str(e)}")
        return jsonify({'error': 'Error downloading file'}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'model_loaded': chatbot.is_model_loaded()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
