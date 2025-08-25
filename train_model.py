import json
import logging
import joblib
from typing import Tuple, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from nlp_processor import NLPProcessor

class ModelTrainer:
    """
    Machine Learning model trainer for intent classification
    """
    
    def __init__(self):
        self.nlp_processor = NLPProcessor()
        self.vectorizer = TfidfVectorizer(
            max_features=2000,
            ngram_range=(1, 3),
            stop_words='english',
            lowercase=True,
            analyzer='word'
        )
        self.model = MultinomialNB(alpha=0.01)
        self.label_encoder = LabelEncoder()
    
    def load_training_data(self) -> Tuple[List[str], List[str]]:
        """
        Load and prepare training data from intents.json
        
        Returns:
            Tuple of (patterns, labels)
        """
        try:
            with open('intents.json', 'r', encoding='utf-8') as file:
                intents_data = json.load(file)
        except FileNotFoundError:
            logging.error("intents.json file not found!")
            return [], []
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing intents.json: {str(e)}")
            return [], []
        
        patterns = []
        labels = []
        
        for intent in intents_data.get('intents', []):
            intent_tag = intent['tag']
            for pattern in intent['patterns']:
                patterns.append(pattern)
                labels.append(intent_tag)
        
        logging.info(f"Loaded {len(patterns)} patterns across {len(set(labels))} intents")
        return patterns, labels
    
    def preprocess_data(self, patterns: List[str]) -> List[str]:
        """
        Preprocess all patterns using NLP pipeline
        
        Args:
            patterns: Raw pattern strings
            
        Returns:
            Preprocessed patterns
        """
        logging.info("Preprocessing training data...")
        preprocessed = []
        
        for pattern in patterns:
            processed = self.nlp_processor.preprocess_text(pattern)
            if processed:  # Only add non-empty processed text
                preprocessed.append(processed)
            else:
                preprocessed.append(pattern.lower())  # Fallback
        
        return preprocessed
    
    def train_model(self) -> Tuple:
        """
        Complete model training pipeline
        
        Returns:
            Tuple of (model, vectorizer, label_encoder)
        """
        # Load training data
        patterns, labels = self.load_training_data()
        
        if not patterns or not labels:
            raise ValueError("No training data available")
        
        # Preprocess patterns
        preprocessed_patterns = self.preprocess_data(patterns)
        
        # Encode labels
        encoded_labels = self.label_encoder.fit_transform(labels)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            preprocessed_patterns, encoded_labels, 
            test_size=0.2, random_state=42, stratify=encoded_labels
        )
        
        # Vectorize text
        X_train_vectorized = self.vectorizer.fit_transform(X_train)
        X_test_vectorized = self.vectorizer.transform(X_test)
        
        # Train model
        logging.info("Training Naive Bayes model...")
        self.model.fit(X_train_vectorized, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test_vectorized)
        accuracy = accuracy_score(y_test, y_pred)
        
        logging.info(f"Model training completed with accuracy: {accuracy:.4f}")
        logging.info("Classification Report:")
        logging.info(classification_report(
            y_test, y_pred, 
            target_names=self.label_encoder.classes_
        ))
        
        # Save model components
        self._save_model()
        
        return self.model, self.vectorizer, self.label_encoder
    
    def _save_model(self):
        """Save trained model, vectorizer, and label encoder"""
        try:
            joblib.dump(self.model, 'model.pkl')
            joblib.dump(self.vectorizer, 'vectorizer.pkl')
            joblib.dump(self.label_encoder, 'label_encoder.pkl')
            logging.info("Model saved successfully")
        except Exception as e:
            logging.error(f"Error saving model: {str(e)}")

if __name__ == "__main__":
    # For standalone training
    logging.basicConfig(level=logging.INFO)
    trainer = ModelTrainer()
    trainer.train_model()
