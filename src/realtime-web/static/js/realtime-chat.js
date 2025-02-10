// Realtime Chat Implementation
class RealtimeChat {
    constructor() {
        this.messageHistory = document.getElementById('message-history');
        this.userInput = document.getElementById('user-input');
        this.sendButton = document.getElementById('send-btn');
        this.cliffModeButton = document.getElementById('cliff-mode');
        this.clearHistoryButton = document.getElementById('clear-history');
        this.statusText = document.getElementById('status-text');
        this.statusIndicator = document.getElementById('status-indicator');
        this.audioPlayer = document.getElementById('response-audio');
        
        this.messageTemplate = document.getElementById('message-template');
        this.cliffMode = false;
        this.isConnected = false;
        this.currentMessageBuffer = [];
        
        this.setupSocketIO();
        this.setupEventListeners();
    }
    
    setupSocketIO() {
        // Initialize Socket.IO connection
        this.socket = io();
        
        // Connection events
        this.socket.on('connect', () => this.handleConnection());
        this.socket.on('disconnect', () => this.handleDisconnection());
        this.socket.on('error', (error) => this.handleError(error));
        
        // Message events
        this.socket.on('status', (data) => this.handleStatusUpdate(data));
        this.socket.on('response_chunk', (data) => this.handleResponseChunk(data));
        this.socket.on('response_complete', () => this.handleResponseComplete());
        this.socket.on('audio', (data) => this.handleAudio(data));
        this.socket.on('error', (data) => this.handleErrorMessage(data));
    }
    
    setupEventListeners() {
        // Send message on button click or Enter (without shift)
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Toggle Cliff Mode
        this.cliffModeButton.addEventListener('click', () => this.toggleCliffMode());
        
        // Clear history
        this.clearHistoryButton.addEventListener('click', () => this.clearHistory());
        
        // Audio playback complete
        this.audioPlayer.addEventListener('ended', () => {
            this.audioPlayer.style.display = 'none';
        });
    }
    
    handleConnection() {
        this.isConnected = true;
        this.statusText.textContent = 'Connected';
        this.statusIndicator.classList.add('connected');
        this.sendButton.disabled = false;
    }
    
    handleDisconnection() {
        this.isConnected = false;
        this.statusText.textContent = 'Disconnected - Attempting to reconnect...';
        this.statusIndicator.classList.remove('connected');
        this.sendButton.disabled = true;
    }
    
    handleError(error) {
        console.error('Socket error:', error);
        this.addSystemMessage('Error: Connection failed. Retrying...');
    }
    
    handleStatusUpdate(data) {
        this.addSystemMessage(data.message);
    }
    
    handleResponseChunk(data) {
        if (this.currentMessageBuffer.length === 0) {
            // Start new message
            this.addMessage('assistant', '');
        }
        
        this.currentMessageBuffer.push(data.chunk);
        
        // Update the last message with accumulated text
        const lastMessage = this.messageHistory.lastElementChild;
        if (lastMessage) {
            const content = lastMessage.querySelector('.message-content');
            content.textContent = this.currentMessageBuffer.join('');
            
            // Scroll to bottom
            this.messageHistory.scrollTop = this.messageHistory.scrollHeight;
        }
    }
    
    handleResponseComplete() {
        // Clear buffer
        this.currentMessageBuffer = [];
        
        // Enable input
        this.userInput.disabled = false;
        this.sendButton.disabled = false;
    }
    
    handleAudio(data) {
        // Convert base64 to audio
        const audio = new Audio(`data:audio/wav;base64,${data.audio}`);
        this.audioPlayer.src = audio.src;
        this.audioPlayer.style.display = 'block';
        this.audioPlayer.play();
    }
    
    handleErrorMessage(data) {
        this.addSystemMessage(`Error: ${data.message}`);
    }
    
    sendMessage() {
        const message = this.userInput.value.trim();
        if (!message || !this.isConnected) return;
        
        // Add user message
        this.addMessage('user', message);
        
        // Clear input
        this.userInput.value = '';
        
        // Disable input while processing
        this.userInput.disabled = true;
        this.sendButton.disabled = true;
        
        // Send to server
        this.socket.emit('message', {
            message: message,
            cliff_mode: this.cliffMode
        });
    }
    
    toggleCliffMode() {
        this.cliffMode = !this.cliffMode;
        this.cliffModeButton.textContent = `Cliff Mode: ${this.cliffMode ? 'ON' : 'OFF'}`;
        this.socket.emit('toggle_cliff_mode', {
            enabled: this.cliffMode
        });
    }
    
    clearHistory() {
        this.messageHistory.innerHTML = '';
        this.socket.emit('clear_history');
        this.addSystemMessage('History cleared');
    }
    
    addMessage(role, content) {
        const messageNode = this.messageTemplate.content.cloneNode(true);
        const message = messageNode.querySelector('.message');
        const sender = messageNode.querySelector('.sender');
        const timestamp = messageNode.querySelector('.timestamp');
        const messageContent = messageNode.querySelector('.message-content');
        
        message.classList.add(role);
        sender.textContent = role === 'user' ? 'You' : 'Trooper';
        timestamp.textContent = new Date().toLocaleTimeString();
        messageContent.textContent = content;
        
        this.messageHistory.appendChild(messageNode);
        this.messageHistory.scrollTop = this.messageHistory.scrollHeight;
    }
    
    addSystemMessage(content) {
        const messageNode = this.messageTemplate.content.cloneNode(true);
        const message = messageNode.querySelector('.message');
        const sender = messageNode.querySelector('.sender');
        const timestamp = messageNode.querySelector('.timestamp');
        const messageContent = messageNode.querySelector('.message-content');
        
        message.classList.add('system');
        sender.textContent = 'System';
        timestamp.textContent = new Date().toLocaleTimeString();
        messageContent.textContent = content;
        
        this.messageHistory.appendChild(messageNode);
        this.messageHistory.scrollTop = this.messageHistory.scrollHeight;
    }
}

// Initialize chat when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chat = new RealtimeChat();
}); 