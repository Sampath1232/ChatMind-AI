import os
import logging
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, send_from_directory
from local_agent import LocalLLMAgent
from chatbot import Chatbot

# =========================================================
# LOAD ENV VARIABLES
# =========================================================
load_dotenv()

# =========================================================
# CONFIGURE LOGGING
# =========================================================
logging.basicConfig(level=logging.DEBUG)

# =========================================================
# INITIALIZE FLASK APP
# =========================================================
app = Flask(__name__)

app.secret_key = os.getenv(
    "SESSION_SECRET",
    "chatbot_secret_key_2024"
)

# =========================================================
# INITIALIZE CHATBOT
# =========================================================
chatbot = Chatbot()


llm_agent = LocalLLMAgent()
# =========================================================
# HOME ROUTE
# =========================================================
@app.route('/')
def index():
    return render_template('index.html')

# =========================================================
# CHAT API
# =========================================================
@app.route('/chat', methods=['POST'])
def chat():

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "error": "No JSON data received"
            }), 400

        user_message = data.get("message", "").strip()
        user_name = data.get("user_name", "Sampath")

        if not user_message:
            return jsonify({
                "error": "Message cannot be empty"
            }), 400

        # =================================================
        # DETECT NEWS REQUEST
        # =================================================
        include_news = any(
            word in user_message.lower()
            for word in [
                "news",
                "headlines",
                "current affairs",
                "latest news"
            ]
        )

        # =================================================
        # IMAGE GENERATION REQUEST
        # =================================================
        if any(
            word in user_message.lower()
            for word in [
                "generate image",
                "create image",
                "make image",
                "picture",
                "photo",
                "drawing"
            ]
        ):

            image_response = handle_image_generation_request(
                user_message
            )

            return jsonify({
                "response": image_response,
                "intent": "image_generation"
            })

        # =================================================
        # NLP CHATBOT RESPONSE
        # =================================================
        response, intent = chatbot.get_response(user_message)

        # =================================================
        # FALLBACK TO GEMINI AI
        # =================================================
        if (
            not response
            or intent == "unknown"
            or response.lower() in [
                "i don't understand",
                "sorry, i didn't understand that"
            ]
        ):

            response = llm_agent.generate(user_message)

            intent = "gemini_ai"

        logging.info(
            f"User: {user_message} | "
            f"Intent: {intent}"
        )

        return jsonify({
            "response": response,
            "intent": intent
        })

    except Exception as e:

        logging.error(
            f"Error processing chat request: {str(e)}"
        )

        return jsonify({
            "error": "An internal server error occurred"
        }), 500

# =========================================================
# IMAGE GENERATION PLACEHOLDER
# =========================================================
def handle_image_generation_request(user_message):

    try:

        prompt = user_message.lower()

        remove_words = [
            "generate",
            "create",
            "make",
            "image",
            "picture",
            "photo",
            "drawing",
            "of",
            "a",
            "an"
        ]

        for word in remove_words:
            prompt = prompt.replace(word, " ")

        prompt = " ".join(prompt.split()).strip()

        if not prompt:
            return (
                "Please provide a description "
                "for the image."
            )

        return (
            f"🎨 Image generation request received.\n\n"
            f"Prompt: '{prompt}'\n\n"
            f"The image generation system is ready "
            f"for integration."
        )

    except Exception as e:

        logging.error(
            f"Image generation error: {str(e)}"
        )

        return (
            "Error processing image generation request."
        )

# =========================================================
# DOWNLOAD GENERATED FILES
# =========================================================
@app.route('/download/<path:filename>')
def download_file(filename):

    try:

        directory = "generated_content"

        file_path = os.path.join(
            directory,
            filename
        )

        if os.path.exists(file_path):

            return send_from_directory(
                directory,
                filename,
                as_attachment=True
            )

        return jsonify({
            "error": "File not found"
        }), 404

    except Exception as e:

        logging.error(
            f"Download error: {str(e)}"
        )

        return jsonify({
            "error": "Error downloading file"
        }), 500

# =========================================================
# HEALTH CHECK
# =========================================================
@app.route('/health')
def health():

    return jsonify({
        "status": "healthy",
        "model_loaded": chatbot.is_model_loaded()
    })

# =========================================================
# START SERVER
# =========================================================
if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )