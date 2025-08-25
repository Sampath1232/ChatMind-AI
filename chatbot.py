import json
import os
import logging
from typing import Tuple, List
import joblib
from nlp_processor import NLPProcessor

class Chatbot:
    """
    Main chatbot class that handles intent classification and response generation
    """
    
    def __init__(self):
        self.nlp_processor = NLPProcessor()
        self.intents_data = self._load_intents()
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self._load_or_train_model()
    
    def _load_intents(self) -> dict:
        """Load intents data from JSON file"""
        try:
            with open('intents.json', 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            logging.error("intents.json file not found!")
            return {"intents": []}
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing intents.json: {str(e)}")
            return {"intents": []}
    
    def _load_or_train_model(self):
        """Load existing model or train a new one"""
        model_files = ['model.pkl', 'vectorizer.pkl', 'label_encoder.pkl']
        
        if all(os.path.exists(file) for file in model_files):
            try:
                self.model = joblib.load('model.pkl')
                self.vectorizer = joblib.load('vectorizer.pkl')
                self.label_encoder = joblib.load('label_encoder.pkl')
                logging.info("Loaded existing model successfully")
                return
            except Exception as e:
                logging.error(f"Error loading model: {str(e)}")
        
        # Train new model
        logging.info("Training new model...")
        from train_model import ModelTrainer
        trainer = ModelTrainer()
        self.model, self.vectorizer, self.label_encoder = trainer.train_model()
        logging.info("Model training completed")
    
    def get_response(self, user_input: str) -> Tuple[str, str]:
        """
        Get chatbot response for user input
        
        Args:
            user_input: User's message
            
        Returns:
            Tuple of (response, intent)
        """
        if not self.model or not self.vectorizer or not self.label_encoder:
            return "Sorry, the chatbot model is not available right now.", "error"
        
        try:
            # Preprocess user input
            processed_input = self.nlp_processor.preprocess_text(user_input)
            
            if not processed_input:
                return self._get_fallback_response(), "fallback"
            
            # Vectorize input
            input_vector = self.vectorizer.transform([processed_input])
            
            # Predict intent
            predicted_intent = self.model.predict(input_vector)[0]
            confidence = max(self.model.predict_proba(input_vector)[0])
            
            # Get intent name
            intent_name = self.label_encoder.inverse_transform([predicted_intent])[0]
            
            # Use fallback if confidence is too low
            if confidence < 0.3:
                return self._get_fallback_response(), "fallback"
            
            # Get response for predicted intent
            response = self._get_intent_response(intent_name)
            
            return response, intent_name
            
        except Exception as e:
            logging.error(f"Error getting response: {str(e)}")
            return "I'm sorry, I encountered an error. Please try again.", "error"
    
    def _get_intent_response(self, intent_name: str) -> str:
        """Get a random response for the given intent"""
        import random
        
        for intent in self.intents_data.get('intents', []):
            if intent['tag'] == intent_name:
                return random.choice(intent['responses'])
        
        return self._get_fallback_response()
    
    def _get_fallback_response(self) -> str:
        """Get fallback response when intent is not recognized"""
        fallback_responses = [
            "I'm sorry, I didn't understand that. Could you please rephrase?",
            "I'm not sure what you mean. Can you try asking differently?",
            "Could you please clarify your question?",
            "I don't understand. Would you like to ask something else?",
            "Sorry, I'm having trouble understanding. Can you be more specific?"
        ]
        import random
        return random.choice(fallback_responses)
    
    def is_model_loaded(self) -> bool:
        """Check if the model is properly loaded"""
        return all([self.model, self.vectorizer, self.label_encoder])
