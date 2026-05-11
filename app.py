import os
import logging

from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_from_directory
)

from agents.cloud_agent import CloudLLMAgent
from agents.sports_agent import SportsAgent
from chatbot.chatbot import Chatbot

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
# INITIALIZE COMPONENTS
# =========================================================
chatbot = Chatbot()

llm_agent = CloudLLMAgent()

sports_agent = SportsAgent()

# =========================================================
# HOME ROUTE
# =========================================================
@app.route('/')
def index():

    return render_template(
        'index.html'
    )

# =========================================================
# CHAT API
# =========================================================
@app.route('/chat', methods=['POST'])
def chat():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "error":
                "No JSON data received"
            }), 400

        user_message = data.get(
            "message",
            ""
        ).strip()

        if not user_message:

            return jsonify({
                "error":
                "Message cannot be empty"
            }), 400

        # =================================================
        # IMAGE GENERATION REQUEST
        # =================================================
        image_keywords = [

            "generate image",
            "create image",
            "make image",
            "picture",
            "photo",
            "drawing",
            "wallpaper",
            "art"
        ]

        if any(
            word in user_message.lower()
            for word in image_keywords
        ):

            image_response = (
                handle_image_generation_request(
                    user_message
                )
            )

            return jsonify({

                "response":
                image_response,

                "intent":
                "image_generation"
            })

        # =================================================
        # SPORTS / IPL REQUESTS
        # =================================================
        sports_keywords = [

                "ipl",
                "cricket",
                "ipl score",
                "live cricket",
                "match score",
                "yesterday ipl",
                "today ipl",
                "live match"
            ]

        if any(
            word in user_message.lower()
            for word in sports_keywords
        ):

            sports_prompt = f"""

        You are a live cricket assistant.

        Provide the latest IPL match details,
        scores, winners, and highlights.

        User request:
        {user_message}

        If yesterday IPL details are unavailable,
        clearly say so.
        """

            response = llm_agent.generate(
                sports_prompt
            )

            return jsonify({

                "response": response,

                "intent": "sports_ai"
            })

        # =================================================
        # AI CODING / APP GENERATION
        # =================================================
        coding_keywords = [

            "create app",
            "calculator",
            "python code",
            "generate code",
            "write code",
            "build app",
            "website",
            "flask app",
            "html",
            "css",
            "javascript",
            "react app",
            "portfolio",
            "login page",
            "dashboard",
            "api"
        ]

        if any(
            word in user_message.lower()
            for word in coding_keywords
        ):

            response = llm_agent.generate(
                user_message
            )

            return jsonify({

                "response":
                response,

                "intent":
                "cloud_llm"
            })

        # =================================================
        # NLP CHATBOT RESPONSE
        # =================================================
        response, intent = chatbot.get_response(
            user_message
        )

        # =================================================
        # CLOUD AI FALLBACK
        # =================================================
        if intent in [

            "unknown",
            "fallback",
            "error",
            "gemini_fallback"

        ]:

            response = llm_agent.generate(
                user_message
            )

            intent = "cloud_llm"

        logging.info(

            f"User: {user_message} | "
            f"Intent: {intent}"
        )

        return jsonify({

            "response":
            response,

            "intent":
            intent
        })

    except Exception as e:

        logging.exception(e)

        return jsonify({

            "error":
            str(e)

        }), 500

# =========================================================
# IMAGE GENERATION PLACEHOLDER
# =========================================================
def handle_image_generation_request(
    user_message
):

    try:

        prompt = (
            user_message.lower()
        )

        remove_words = [

            "generate",
            "create",
            "make",
            "image",
            "picture",
            "photo",
            "drawing",
            "wallpaper",
            "art",
            "of",
            "a",
            "an"
        ]

        for word in remove_words:

            prompt = prompt.replace(
                word,
                " "
            )

        prompt = (
            " ".join(
                prompt.split()
            ).strip()
        )

        if not prompt:

            return (
                "Please provide a "
                "description for the image."
            )

        return (

            f"🎨 Image generation "
            f"request received.\n\n"

            f"Prompt: '{prompt}'\n\n"

            f"Cloud image generation "
            f"can now be integrated "
            f"using Stability AI or "
            f"Together AI APIs."
        )

    except Exception as e:

        logging.error(

            f"Image generation error: "
            f"{str(e)}"
        )

        return (

            "Error processing image "
            "generation request."
        )

# =========================================================
# DOWNLOAD GENERATED FILES
# =========================================================
@app.route('/download/<path:filename>')
def download_file(filename):

    try:

        directory = (
            "generated_content"
        )

        file_path = os.path.join(

            directory,
            filename
        )

        if os.path.exists(
            file_path
        ):

            return send_from_directory(

                directory,
                filename,
                as_attachment=True
            )

        return jsonify({

            "error":
            "File not found"

        }), 404

    except Exception as e:

        logging.error(

            f"Download error: "
            f"{str(e)}"
        )

        return jsonify({

            "error":
            "Error downloading file"

        }), 500

# =========================================================
# HEALTH CHECK
# =========================================================
@app.route('/health')
def health():

    return jsonify({

        "status":
        "healthy",

        "model_loaded":
        chatbot.is_model_loaded()
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