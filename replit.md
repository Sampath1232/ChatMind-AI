# AI Chatbot System

## Overview

This is a Flask-based AI chatbot application that uses machine learning for intent classification and natural language processing. The system provides both web and console interfaces for interacting with an intelligent conversational agent. The chatbot uses NLTK for text processing, scikit-learn for intent classification, and stores conversation patterns in a JSON configuration file.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Web Interface**: Bootstrap-based responsive web UI with real-time chat functionality
- **Console Interface**: Command-line chat mode for testing and development
- **JavaScript Client**: Handles real-time messaging, typing indicators, and API communication
- **Responsive Design**: Mobile-friendly interface with sidebar navigation

### Backend Architecture
- **Flask Web Framework**: RESTful API server handling HTTP requests and JSON responses
- **Modular Design**: Separated concerns with dedicated modules for chatbot logic, NLP processing, and model training
- **Intent Classification**: Machine learning pipeline using TF-IDF vectorization and Naive Bayes classification
- **Session Management**: Flask sessions for maintaining conversation context

### Core Components
- **Chatbot Engine**: Central orchestrator managing intent detection and response generation
- **NLP Processor**: Text preprocessing pipeline with tokenization, lemmatization, and stop word removal
- **Model Trainer**: Machine learning training pipeline with cross-validation and model persistence
- **Intent Configuration**: JSON-based intent definitions with patterns and responses

### Data Processing Pipeline
- **Text Preprocessing**: Lowercase conversion, special character removal, tokenization
- **Feature Extraction**: TF-IDF vectorization with n-gram support
- **Model Training**: Automated training with model persistence using joblib
- **Response Generation**: Intent-based response selection with fallback handling

### Model Architecture
- **Algorithm**: Multinomial Naive Bayes classifier
- **Features**: TF-IDF vectors with unigram and bigram support
- **Training Data**: Intent patterns from JSON configuration
- **Model Persistence**: Serialized models saved as pickle files for fast loading

## External Dependencies

### Python Libraries
- **Flask**: Web framework for API server and routing
- **NLTK**: Natural language processing toolkit for tokenization and text preprocessing
- **scikit-learn**: Machine learning library for classification and vectorization
- **joblib**: Model serialization and persistence

### Frontend Dependencies
- **Bootstrap 5.3.0**: CSS framework for responsive design and components
- **Font Awesome 6.4.0**: Icon library for UI elements
- **Vanilla JavaScript**: Custom chat interface without additional frameworks

### Development Tools
- **Python 3.x**: Runtime environment
- **Flask Development Server**: Local development and testing
- **JSON Configuration**: Intent definitions and training data storage

### NLTK Data Requirements
- **punkt**: Tokenization models
- **stopwords**: English stop word corpus
- **wordnet**: WordNet lexical database
- **omw-1.4**: Open Multilingual Wordnet