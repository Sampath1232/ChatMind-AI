import json
import os
import logging
from typing import Tuple
import joblib

from nlp_processor import NLPProcessor
from content_generator import ContentGenerator


class Chatbot:
    """
    Main chatbot class that handles
    intent classification and response generation
    """

    def __init__(self):

        self.nlp_processor = NLPProcessor()

        self.intents_data = self._load_intents()

        self.model = None
        self.vectorizer = None
        self.label_encoder = None

        self.content_generator = ContentGenerator()

        self.conversation_context = []

        self.user_name = None

        self._load_or_train_model()

    # =====================================================
    # LOAD INTENTS
    # =====================================================
    def _load_intents(self) -> dict:

        try:

            with open(
                'intents.json',
                'r',
                encoding='utf-8'
            ) as file:

                return json.load(file)

        except FileNotFoundError:

            logging.error(
                "intents.json file not found!"
            )

            return {"intents": []}

        except json.JSONDecodeError as e:

            logging.error(
                f"Error parsing intents.json: {str(e)}"
            )

            return {"intents": []}

    # =====================================================
    # LOAD OR TRAIN MODEL
    # =====================================================
    def _load_or_train_model(self):

        model_files = [
            'model.pkl',
            'vectorizer.pkl',
            'label_encoder.pkl'
        ]

        if all(os.path.exists(file) for file in model_files):

            try:

                self.model = joblib.load('model.pkl')

                self.vectorizer = joblib.load(
                    'vectorizer.pkl'
                )

                self.label_encoder = joblib.load(
                    'label_encoder.pkl'
                )

                logging.info(
                    "Loaded existing model successfully"
                )

                return

            except Exception as e:

                logging.error(
                    f"Error loading model: {str(e)}"
                )

        # ================================================
        # TRAIN MODEL
        # ================================================
        logging.info("Training new model...")

        from train_model import ModelTrainer

        trainer = ModelTrainer()

        (
            self.model,
            self.vectorizer,
            self.label_encoder
        ) = trainer.train_model()

        logging.info("Model training completed")

    # =====================================================
    # MAIN RESPONSE FUNCTION
    # =====================================================
    def get_response(
        self,
        user_input: str
    ) -> Tuple[str, str]:

        if (
            not self.model
            or not self.vectorizer
            or not self.label_encoder
        ):

            return (
                "Sorry, chatbot model unavailable.",
                "error"
            )

        try:

            # ============================================
            # STORE CONTEXT
            # ============================================
            self._add_to_context(
                f"User: {user_input}"
            )

            # ============================================
            # PREPROCESS INPUT
            # ============================================
            processed_input = (
                self.nlp_processor.preprocess_text(
                    user_input
                )
            )

            if not processed_input:

                return (
                    self._get_fallback_response(),
                    "fallback"
                )

            # ============================================
            # VECTORIZE
            # ============================================
            input_vector = (
                self.vectorizer.transform(
                    [processed_input]
                )
            )

            # ============================================
            # PREDICT INTENT
            # ============================================
            predicted_intent = (
                self.model.predict(input_vector)[0]
            )

            confidence = max(
                self.model.predict_proba(
                    input_vector
                )[0]
            )

            intent_name = (
                self.label_encoder.inverse_transform(
                    [predicted_intent]
                )[0]
            )

            logging.debug(
                f"Intent: {intent_name}, "
                f"Confidence: {confidence:.3f}"
            )

            # ============================================
            # LOW CONFIDENCE → FALLBACK
            # ============================================
            if confidence < 0.3:

                return (
                    self._get_fallback_response(),
                    "unknown"
                )

            # ============================================
            # INTRODUCTION HANDLING
            # ============================================
            if intent_name == "introduction":

                self._extract_user_name(
                    user_input
                )

            # ============================================
            # CONTENT GENERATION
            # ============================================
            if intent_name == "content_generation":

                return (
                    self._handle_content_generation(
                        user_input
                    ),
                    intent_name
                )

            # ============================================
            # NORMAL RESPONSE
            # ============================================
            response = (
                self._get_intent_response(
                    intent_name
                )
            )

            self._add_to_context(
                f"Bot: {response}"
            )

            return response, intent_name

        except Exception as e:

            logging.error(
                f"Error getting response: {str(e)}"
            )

            return (
                "I'm sorry, I encountered an error. "
                "Please try again.",
                "error"
            )

    # =====================================================
    # GET INTENT RESPONSE
    # =====================================================
    def _get_intent_response(
        self,
        intent_name: str
    ) -> str:

        import random

        for intent in self.intents_data.get(
            'intents',
            []
        ):

            if intent['tag'] == intent_name:

                return random.choice(
                    intent['responses']
                )

        return self._get_fallback_response()

    # =====================================================
    # FALLBACK RESPONSE
    # =====================================================
    def _get_fallback_response(self) -> str:

        import random

        fallback_responses = [

            "I'm sorry, I didn't understand that.",

            "Could you rephrase your question?",

            "I'm not sure what you mean.",

            "Please ask differently.",

            "Can you clarify your request?"
        ]

        return random.choice(
            fallback_responses
        )

    # =====================================================
    # ADD CONTEXT
    # =====================================================
    def _add_to_context(
        self,
        message: str
    ):

        self.conversation_context.append(
            message
        )

        if len(self.conversation_context) > 20:

            self.conversation_context = (
                self.conversation_context[-20:]
            )

        logging.debug(
            f"Added to context: {message}"
        )

    # =====================================================
    # EXTRACT USER NAME
    # =====================================================
    def _extract_user_name(
        self,
        user_input: str
    ):

        import re

        patterns = [

            r"(?:i am|i'm|my name is|call me)\s+([a-zA-Z]+)"
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                user_input.lower()
            )

            if match:

                self.user_name = (
                    match.group(1).capitalize()
                )

                logging.info(
                    f"User name: {self.user_name}"
                )

                break

    # =====================================================
    # CONTENT GENERATION
    # =====================================================
    def _handle_content_generation(
        self,
        user_input: str
    ) -> str:

        user_lower = user_input.lower()

        try:

            # ============================================
            # IMAGE
            # ============================================
            if any(
                word in user_lower
                for word in [
                    'image',
                    'picture',
                    'photo',
                    'drawing'
                ]
            ):

                return (
                    "🎨 Image generation request "
                    "received."
                )

            # ============================================
            # PDF
            # ============================================
            elif any(
                word in user_lower
                for word in [
                    'pdf',
                    'document'
                ]
            ):

                prompt = user_input

                result = (
                    self.content_generator.generate_pdf(
                        prompt
                    )
                )

                return result.get(
                    "message",
                    "PDF generated."
                )

            # ============================================
            # WORD
            # ============================================
            elif any(
                word in user_lower
                for word in [
                    'word',
                    'docx'
                ]
            ):

                prompt = user_input

                result = (
                    self.content_generator.generate_word_doc(
                        prompt
                    )
                )

                return result.get(
                    "message",
                    "Word document generated."
                )

            # ============================================
            # TEXT
            # ============================================
            else:

                result = (
                    self.content_generator.generate_text_content(
                        user_input,
                        "article"
                    )
                )

                return result.get(
                    "content",
                    "Content generated."
                )

        except Exception as e:

            logging.error(
                f"Content generation error: {str(e)}"
            )

            return (
                "Error generating content."
            )

    # =====================================================
    # MODEL STATUS
    # =====================================================
    def is_model_loaded(self) -> bool:

        return all([
            self.model,
            self.vectorizer,
            self.label_encoder
        ])