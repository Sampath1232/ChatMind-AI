import re
import nltk
import logging
from typing import List
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

class NLPProcessor:
    """
    Natural Language Processing utilities for text preprocessing
    """
    
    def __init__(self):
        self._download_nltk_data()
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
    def _download_nltk_data(self):
        """Download required NLTK data"""
        try:
            nltk_downloads = ['punkt', 'punkt_tab', 'stopwords', 'wordnet', 'omw-1.4']
            for item in nltk_downloads:
                try:
                    if item == 'punkt':
                        nltk.data.find('tokenizers/punkt')
                    elif item == 'punkt_tab':
                        nltk.data.find('tokenizers/punkt_tab')
                    elif item == 'stopwords':
                        nltk.data.find('corpora/stopwords')
                    elif item == 'wordnet':
                        nltk.data.find('corpora/wordnet')
                    elif item == 'omw-1.4':
                        nltk.data.find('corpora/omw-1.4')
                except LookupError:
                    logging.info(f"Downloading NLTK data: {item}")
                    nltk.download(item, quiet=True)
        except Exception as e:
            logging.error(f"Error downloading NLTK data: {str(e)}")
    
    def preprocess_text(self, text: str) -> str:
        """
        Complete text preprocessing pipeline
        
        Args:
            text: Raw input text
            
        Returns:
            Preprocessed text string
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits but keep important punctuation
        text = re.sub(r'[^a-zA-Z\s\?\!\.]', '', text)
        text = re.sub(r'[\.]+', ' ', text)  # Replace multiple dots with space
        text = re.sub(r'[\?\!]+', '', text)  # Remove question/exclamation marks
        
        # Tokenize
        tokens = self.tokenize(text)
        
        # Remove stopwords
        tokens = self.remove_stopwords(tokens)
        
        # Lemmatize
        tokens = self.lemmatize_tokens(tokens)
        
        # Join back to string
        return ' '.join(tokens)
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        try:
            return word_tokenize(text)
        except Exception as e:
            logging.error(f"Error tokenizing text: {str(e)}")
            return text.split()
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """
        Remove stopwords from token list but keep important words for intent recognition
        
        Args:
            tokens: List of tokens
            
        Returns:
            Filtered tokens without stopwords
        """
        # Keep important words for intent recognition
        keep_words = {'you', 'are', 'how', 'what', 'who', 'when', 'where', 'why', 'can', 'do', 'tell', 'me', 'i', 'am', 'my', 'name', 'is'}
        return [token for token in tokens if (token not in self.stop_words or token in keep_words) and len(token) > 1]
    
    def lemmatize_tokens(self, tokens: List[str]) -> List[str]:
        """
        Lemmatize tokens to their root forms
        
        Args:
            tokens: List of tokens
            
        Returns:
            List of lemmatized tokens
        """
        try:
            return [self.lemmatizer.lemmatize(token) for token in tokens]
        except Exception as e:
            logging.error(f"Error lemmatizing tokens: {str(e)}")
            return tokens
    
    def preprocess_training_data(self, patterns: List[str]) -> List[str]:
        """
        Preprocess multiple patterns for training data
        
        Args:
            patterns: List of pattern strings
            
        Returns:
            List of preprocessed patterns
        """
        return [self.preprocess_text(pattern) for pattern in patterns]
