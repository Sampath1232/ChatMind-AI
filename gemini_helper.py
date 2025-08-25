import json
import logging
import os
from typing import Optional

from google import genai
from google.genai import types


class GeminiHelper:
    """
    Gemini AI integration for enhanced chatbot responses
    """
    
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Gemini client with API key"""
        try:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                logging.warning("GEMINI_API_KEY not found. Gemini features will be disabled.")
                return
            
            self.client = genai.Client(api_key=api_key)
            logging.info("Gemini client initialized successfully")
            
        except Exception as e:
            logging.error(f"Failed to initialize Gemini client: {str(e)}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Gemini is available for use"""
        return self.client is not None
    
    def get_response(self, user_message: str, conversation_context: Optional[str] = None) -> Optional[str]:
        """
        Get response from Gemini for complex questions
        
        Args:
            user_message: User's question/message
            conversation_context: Optional context from previous conversation
            
        Returns:
            Gemini's response or None if unavailable
        """
        if not self.is_available():
            return None
        
        try:
            # Create a helpful system prompt for the chatbot
            system_prompt = (
                "You are a helpful, friendly AI assistant chatbot. "
                "Provide clear, concise, and helpful responses to user questions. "
                "Be conversational and engaging. Keep responses informative but not too long. "
                "If you don't know something, admit it politely and suggest alternatives."
            )
            
            # Add conversation context if available
            if conversation_context:
                prompt = f"Context: {conversation_context}\n\nUser question: {user_message}"
            else:
                prompt = user_message
            
            response = self.client.models.generate_content(  # type: ignore
                model="gemini-2.5-flash",
                contents=[
                    types.Content(role="user", parts=[types.Part(text=prompt)])
                ],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    max_output_tokens=500,  # Keep responses concise
                    temperature=0.7  # Balanced creativity
                )
            )
            
            if response and response.text:
                return response.text.strip()
            else:
                logging.warning("Empty response from Gemini")
                return None
                
        except Exception as e:
            logging.error(f"Error getting Gemini response: {str(e)}")
            return None
    
    def get_conversational_response(self, user_message: str, user_name: Optional[str] = None) -> Optional[str]:
        """
        Get a conversational response for general chat
        
        Args:
            user_message: User's message
            user_name: User's name if known
            
        Returns:
            Conversational response or None
        """
        if not self.is_available():
            return None
        
        try:
            context = ""
            if user_name:
                context = f"The user's name is {user_name}. "
            
            system_prompt = (
                "You are a friendly, conversational AI chatbot assistant. "
                f"{context}"
                "Engage in natural conversation, answer questions helpfully, "
                "and maintain a warm, supportive tone. Keep responses concise and engaging."
            )
            
            response = self.client.models.generate_content(  # type: ignore
                model="gemini-2.5-flash",
                contents=[
                    types.Content(role="user", parts=[types.Part(text=user_message)])
                ],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    max_output_tokens=300,
                    temperature=0.8
                )
            )
            
            if response and response.text:
                return response.text.strip()
            else:
                return None
                
        except Exception as e:
            logging.error(f"Error getting conversational response: {str(e)}")
            return None