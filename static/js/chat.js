/**
 * Advanced Chatbot Frontend JavaScript
 * Handles real-time chat interface, API communication, and user interactions
 */

class ChatBot {
    constructor() {
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        this.chatMessages = document.getElementById('chat-messages');
        this.typingIndicator = document.getElementById('typing-indicator');
        
        this.isTyping = false;
        this.messageHistory = [];
        this.apiEndpoint = '/chat';
        
        this.initializeEventListeners();
        this.scrollToBottom();
    }
    
    /**
     * Initialize all event listeners
     */
    initializeEventListeners() {
        // Send message on Enter key
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Send button click
        this.sendButton.addEventListener('click', () => {
            this.sendMessage();
        });
        
        // Auto-resize input
        this.messageInput.addEventListener('input', () => {
            this.autoResizeInput();
        });
        
        // Focus input on page load
        window.addEventListener('load', () => {
            this.messageInput.focus();
        });
    }
    
    /**
     * Send message to chatbot
     */
    async sendMessage() {
        const message = this.messageInput.value.trim();
        
        if (!message) {
            this.showInputError('Please enter a message');
            return;
        }
        
        // Clear input and disable send button
        this.messageInput.value = '';
        this.setLoading(true);
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Send request to backend
            const response = await this.sendApiRequest(message);
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            if (response.error) {
                this.addErrorMessage(response.error);
            } else {
                // Add bot response with intent info
                this.addMessage(response.response, 'bot', response.intent);
            }
            
        } catch (error) {
            console.error('Chat error:', error);
            this.hideTypingIndicator();
            this.addErrorMessage('Failed to connect to the chatbot. Please try again.');
            this.showErrorModal('Connection failed. Please check your internet connection and try again.');
        } finally {
            this.setLoading(false);
            this.messageInput.focus();
        }
    }
    
    /**
     * Send API request to backend
     * @param {string} message - User message
     * @returns {Promise<Object>} - API response
     */
    async sendApiRequest(message) {
        const response = await fetch(this.apiEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message }),
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    /**
     * Add message to chat interface
     * @param {string} message - Message content
     * @param {string} sender - 'user' or 'bot'
     * @param {string} intent - Detected intent (optional)
     */
    addMessage(message, sender, intent = null) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${sender}-message`;
        
        const currentTime = new Date().toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        const avatar = sender === 'user' 
            ? '<i class="fas fa-user"></i>' 
            : '<i class="fas fa-robot"></i>';
        
        const intentBadge = intent && sender === 'bot' 
            ? `<small class="text-muted ms-2"><i class="fas fa-tag"></i> ${intent}</small>` 
            : '';
        
        messageElement.innerHTML = `
            <div class="message-avatar">
                ${avatar}
            </div>
            <div class="message-content">
                <div class="message-bubble">
                    ${this.formatMessage(message)}
                </div>
                <div class="message-time">
                    ${currentTime}${intentBadge}
                </div>
            </div>
        `;
        
        this.chatMessages.appendChild(messageElement);
        this.messageHistory.push({ message, sender, time: currentTime, intent });
        this.scrollToBottom();
        
        // Add animation
        messageElement.style.opacity = '0';
        messageElement.style.transform = 'translateY(20px)';
        
        requestAnimationFrame(() => {
            messageElement.style.transition = 'all 0.3s ease';
            messageElement.style.opacity = '1';
            messageElement.style.transform = 'translateY(0)';
        });
    }
    
    /**
     * Add error message to chat
     * @param {string} errorMessage - Error message to display
     */
    addErrorMessage(errorMessage) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message bot-message';
        
        const currentTime = new Date().toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        messageElement.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-exclamation-triangle text-warning"></i>
            </div>
            <div class="message-content">
                <div class="message-bubble error-message">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    ${errorMessage}
                </div>
                <div class="message-time">${currentTime}</div>
            </div>
        `;
        
        this.chatMessages.appendChild(messageElement);
        this.scrollToBottom();
    }
    
    /**
     * Format message content (handle line breaks, links, etc.)
     * @param {string} message - Raw message
     * @returns {string} - Formatted HTML
     */
    formatMessage(message) {
        // Convert line breaks to <br>
        let formatted = message.replace(/\n/g, '<br>');
        
        // Add basic HTML formatting for common patterns
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        return `<p>${formatted}</p>`;
    }
    
    /**
     * Show typing indicator
     */
    showTypingIndicator() {
        this.typingIndicator.style.display = 'block';
        this.isTyping = true;
        this.scrollToBottom();
    }
    
    /**
     * Hide typing indicator
     */
    hideTypingIndicator() {
        this.typingIndicator.style.display = 'none';
        this.isTyping = false;
    }
    
    /**
     * Set loading state
     * @param {boolean} loading - Loading state
     */
    setLoading(loading) {
        if (loading) {
            this.sendButton.disabled = true;
            this.sendButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            this.messageInput.disabled = true;
        } else {
            this.sendButton.disabled = false;
            this.sendButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
            this.messageInput.disabled = false;
        }
    }
    
    /**
     * Auto-resize input field
     */
    autoResizeInput() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = this.messageInput.scrollHeight + 'px';
    }
    
    /**
     * Scroll chat to bottom
     */
    scrollToBottom() {
        setTimeout(() => {
            const chatContainer = document.querySelector('.chat-container');
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }, 100);
    }
    
    /**
     * Show input error
     * @param {string} errorMessage - Error message
     */
    showInputError(errorMessage) {
        const inputGroup = this.messageInput.parentElement;
        inputGroup.classList.add('is-invalid');
        
        // Remove error after 3 seconds
        setTimeout(() => {
            inputGroup.classList.remove('is-invalid');
        }, 3000);
        
        // Show tooltip or alert
        this.showToast(errorMessage, 'warning');
    }
    
    /**
     * Show toast notification
     * @param {string} message - Toast message
     * @param {string} type - Toast type (success, warning, error)
     */
    showToast(message, type = 'info') {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${this.getToastIcon(type)} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        // Add to page
        document.body.appendChild(toast);
        
        // Initialize and show toast
        const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
        bsToast.show();
        
        // Remove from DOM after hiding
        toast.addEventListener('hidden.bs.toast', () => {
            document.body.removeChild(toast);
        });
    }
    
    /**
     * Get icon for toast type
     * @param {string} type - Toast type
     * @returns {string} - Font Awesome icon class
     */
    getToastIcon(type) {
        const icons = {
            success: 'check-circle',
            warning: 'exclamation-triangle',
            error: 'exclamation-circle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
    
    /**
     * Show error modal
     * @param {string} message - Error message
     */
    showErrorModal(message) {
        document.getElementById('error-message').textContent = message;
        const modal = new bootstrap.Modal(document.getElementById('errorModal'));
        modal.show();
    }
    
    /**
     * Clear chat history
     */
    clearChat() {
        if (confirm('Are you sure you want to clear the chat history?')) {
            // Remove all messages except welcome message
            const messages = this.chatMessages.querySelectorAll('.message');
            for (let i = 1; i < messages.length; i++) {
                messages[i].remove();
            }
            
            this.messageHistory = [];
            this.showToast('Chat history cleared', 'success');
            this.messageInput.focus();
        }
    }
}

// Global functions for HTML onclick handlers
function clearChat() {
    if (window.chatBot) {
        window.chatBot.clearChat();
    }
}

function sendMessage() {
    if (window.chatBot) {
        window.chatBot.sendMessage();
    }
}

function toggleTypingIndicator() {
    if (window.chatBot) {
        if (window.chatBot.isTyping) {
            window.chatBot.hideTypingIndicator();
        } else {
            window.chatBot.showTypingIndicator();
            setTimeout(() => {
                window.chatBot.hideTypingIndicator();
            }, 3000);
        }
    }
}

function showHelp() {
    const modal = new bootstrap.Modal(document.getElementById('helpModal'));
    modal.show();
}

// Initialize chatbot when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.chatBot = new ChatBot();
    
    // Add some helpful keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl+L to clear chat
        if (e.ctrlKey && e.key === 'l') {
            e.preventDefault();
            clearChat();
        }
        
        // Ctrl+/ to show help
        if (e.ctrlKey && e.key === '/') {
            e.preventDefault();
            showHelp();
        }
        
        // Escape to focus input
        if (e.key === 'Escape') {
            window.chatBot.messageInput.focus();
        }
    });
    
    // Add connection status monitoring
    window.addEventListener('online', function() {
        window.chatBot.showToast('Connection restored', 'success');
    });
    
    window.addEventListener('offline', function() {
        window.chatBot.showToast('Connection lost. Please check your internet.', 'warning');
    });
    
    console.log('🤖 Chatbot initialized successfully!');
    console.log('💡 Keyboard shortcuts:');
    console.log('  • Ctrl+L: Clear chat');
    console.log('  • Ctrl+/: Show help');
    console.log('  • Escape: Focus input');
});
