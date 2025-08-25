import json
import os
import logging
from typing import Tuple, List, Optional
import joblib
from nlp_processor import NLPProcessor
from gemini_helper import GeminiHelper
from content_generator import ContentGenerator

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
        self.gemini_helper = GeminiHelper()
        self.content_generator = ContentGenerator()
        self.conversation_context = []
        self.user_name = None
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
            # Store conversation context
            self._add_to_context(f"User: {user_input}")
            
            # Preprocess user input
            processed_input = self.nlp_processor.preprocess_text(user_input)
            
            if not processed_input:
                return self._get_intelligent_fallback(user_input), "gemini_fallback"
            
            # Vectorize input
            input_vector = self.vectorizer.transform([processed_input])
            
            # Predict intent
            predicted_intent = self.model.predict(input_vector)[0]
            confidence = max(self.model.predict_proba(input_vector)[0])
            
            # Get intent name
            intent_name = self.label_encoder.inverse_transform([predicted_intent])[0]
            
            # Handle introduction intent to extract user name
            if intent_name == "introduction" and confidence > 0.3:
                self._extract_user_name(user_input)
                response = self._get_intent_response(intent_name)
                self._add_to_context(f"Bot: {response}")
                return response, intent_name
            
            # Handle content generation requests
            if intent_name == "content_generation" and confidence > 0.3:
                return self._handle_content_generation(user_input), intent_name
            
            # Use Gemini for low confidence or complex questions
            if confidence < 0.3:
                return self._get_intelligent_fallback(user_input), "gemini_fallback"
            
            # Get response for predicted intent
            response = self._get_intent_response(intent_name)
            
            # Enhance certain intents with Gemini if available
            if intent_name in ["help", "chatbot_info"] and self.gemini_helper.is_available():
                enhanced_response = self._enhance_with_gemini(user_input, response, intent_name)
                if enhanced_response:
                    response = enhanced_response
            
            self._add_to_context(f"Bot: {response}")
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
    
    def _add_to_context(self, message: str):
        """Add message to conversation context"""
        self.conversation_context.append(message)
        # Keep only last 6 exchanges to manage context size
        if len(self.conversation_context) > 12:
            self.conversation_context = self.conversation_context[-12:]
    
    def _extract_user_name(self, user_input: str):
        """Extract user name from introduction"""
        import re
        # Look for patterns like "I am John", "My name is John", etc.
        patterns = [
            r"(?:i am|i'm|my name is|call me|i am called)\s+([a-zA-Z]+)",
            r"([a-zA-Z]+)\s+(?:is my name|here)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_input.lower())
            if match:
                self.user_name = match.group(1).capitalize()
                logging.info(f"Extracted user name: {self.user_name}")
                break
    
    def _get_intelligent_fallback(self, user_input: str) -> str:
        """Get intelligent response using Gemini for fallback cases"""
        if self.gemini_helper.is_available():
            context = " ".join(self.conversation_context[-4:]) if self.conversation_context else None
            response = self.gemini_helper.get_conversational_response(user_input, self.user_name)
            if response:
                return response
        
        # Fallback to traditional response if Gemini unavailable
        return self._get_fallback_response()
    
    def _enhance_with_gemini(self, user_input: str, base_response: str, intent: str) -> Optional[str]:
        """Enhance certain responses with Gemini for more detailed information"""
        if not self.gemini_helper.is_available():
            return None
        
        if intent == "help":
            prompt = f"The user asked: '{user_input}'. Provide helpful, specific guidance."
        elif intent == "chatbot_info":
            prompt = f"Explain what you are as an AI chatbot, your capabilities, and how you can help users. Be friendly and informative."
        else:
            return None
        
        enhanced = self.gemini_helper.get_response(prompt)
        return enhanced if enhanced else base_response
    
    def _handle_content_generation(self, user_input: str) -> str:
        """Handle content generation requests"""
        user_lower = user_input.lower()
        
        try:
            # Determine what type of content to generate
            if any(word in user_lower for word in ['image', 'picture', 'photo', 'drawing']):
                return self._handle_image_generation(user_input)
            elif any(word in user_lower for word in ['pdf', 'document']):
                return self._handle_pdf_generation(user_input)
            elif any(word in user_lower for word in ['word', 'docx']):
                return self._handle_word_generation(user_input)
            elif any(word in user_lower for word in ['text', 'article', 'story', 'essay', 'content']):
                return self._handle_text_generation(user_input)
            else:
                return ("I can help you generate content! Please specify what you'd like me to create:\n"
                       "• Images: 'generate image of a sunset'\n"
                       "• PDFs: 'create PDF about artificial intelligence'\n" 
                       "• Word documents: 'make Word document about cooking'\n"
                       "• Text content: 'write article about space exploration'\n\n"
                       "What would you like me to generate?")
        
        except Exception as e:
            logging.error(f"Error handling content generation: {str(e)}")
            return "I encountered an error while trying to generate content. Please try again with a different prompt."
    
    def _handle_image_generation(self, user_input: str) -> str:
        """Handle image generation requests"""
        # Extract the prompt for image generation
        prompt = self._extract_generation_prompt(user_input, ['generate', 'create', 'make', 'image', 'picture'])
        
        if not prompt:
            return "Please provide a description for the image you'd like me to generate. For example: 'generate image of a beautiful sunset over mountains'"
        
        # Note: In a real implementation, this would use the image generation tool
        return f"🎨 I'll generate an image based on your prompt: '{prompt}'\n\nNote: Image generation requires additional setup. For now, I can help you refine your prompt or suggest image generation tools you could use!"
    
    def _handle_pdf_generation(self, user_input: str) -> str:
        """Handle PDF generation requests"""
        prompt = self._extract_generation_prompt(user_input, ['generate', 'create', 'make', 'pdf', 'document'])
        
        if not prompt:
            return "Please tell me what you'd like the PDF to be about. For example: 'create PDF about renewable energy'"
        
        result = self.content_generator.generate_pdf(prompt)
        
        if result["success"]:
            return f"📄 {result['message']}\n\nThe PDF has been created with the following content preview:\n\n{result['content'][:200]}..."
        else:
            return f"❌ {result['message']}"
    
    def _handle_word_generation(self, user_input: str) -> str:
        """Handle Word document generation requests"""
        prompt = self._extract_generation_prompt(user_input, ['generate', 'create', 'make', 'word', 'document'])
        
        if not prompt:
            return "Please tell me what you'd like the Word document to be about. For example: 'make Word document about healthy eating'"
        
        result = self.content_generator.generate_word_doc(prompt)
        
        if result["success"]:
            return f"📝 {result['message']}\n\nThe Word document has been created with the following content preview:\n\n{result['content'][:200]}..."
        else:
            return f"❌ {result['message']}"
    
    def _handle_text_generation(self, user_input: str) -> str:
        """Handle text content generation requests"""
        prompt = self._extract_generation_prompt(user_input, ['generate', 'create', 'write', 'make', 'text', 'article', 'story', 'essay'])
        
        if not prompt:
            return "Please tell me what you'd like me to write about. For example: 'write article about climate change'"
        
        # Determine content type
        content_type = "article"
        if "story" in user_input.lower():
            content_type = "story"
        elif "essay" in user_input.lower():
            content_type = "essay"
        
        result = self.content_generator.generate_text_content(prompt, content_type)
        
        if result["success"]:
            return f"✍️ Here's your generated {content_type}:\n\n{result['content']}"
        else:
            return f"❌ {result['message']}"
    
    def _extract_generation_prompt(self, user_input: str, keywords: list) -> str:
        """Extract the actual prompt from user input by removing command keywords"""
        words = user_input.lower().split()
        
        # Find where the actual prompt starts (after command keywords)
        prompt_start = 0
        for i, word in enumerate(words):
            if word not in keywords and not any(kw in word for kw in keywords):
                # Remove common connecting words
                if word not in ['of', 'about', 'on', 'for', 'with', 'a', 'an', 'the']:
                    prompt_start = i
                    break
        
        # Extract the prompt part
        prompt_words = user_input.split()[prompt_start:]
        prompt = ' '.join(prompt_words).strip()
        
        # Clean up common prefixes
        prefixes = ['of ', 'about ', 'on ', 'for ', 'with ']
        for prefix in prefixes:
            if prompt.lower().startswith(prefix):
                prompt = prompt[len(prefix):].strip()
                break
        
        return prompt
    
    def is_model_loaded(self) -> bool:
        """Check if the model is properly loaded"""
        return all([self.model, self.vectorizer, self.label_encoder])
