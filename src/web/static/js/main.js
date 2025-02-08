// Connect to WebSocket server
const socket = io();

// Audio player
let audioPlayer = null;

// iOS detection
const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) || 
    (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);

// Mac detection
const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;

// DOM Elements
const messagesDiv = document.getElementById('messages');
const messageForm = document.getElementById('messageForm');
const messageInput = document.getElementById('messageInput');
const statusBar = document.getElementById('status');
const toggleCliffMode = document.getElementById('toggleCliffMode');
const toggleStandupMode = document.getElementById('toggleStandupMode');
const clearHistoryBtn = document.getElementById('clearHistory');
const debugAudio = document.getElementById('debugAudio');

// Initialize audio player
function initAudio() {
    if (!audioPlayer) {
        // For Mac, use the debug audio element
        if (isMac) {
            audioPlayer = debugAudio;
        } else {
            audioPlayer = new Audio();
        }
        
        audioPlayer.addEventListener('ended', () => {
            updateStatus('Ready');
            console.log('Audio playback completed');
            socket.emit('audio_complete');  // Notify server when audio finishes
        });
        audioPlayer.addEventListener('error', (e) => {
            console.error('Audio error:', e);
            updateStatus('Audio playback failed', true);
            socket.emit('audio_complete');  // Also notify on error to prevent hanging
        });
        audioPlayer.addEventListener('playing', () => {
            console.log('Audio started playing');
        });
        
        // Set fixed volume
        audioPlayer.volume = 0.7;
    }
}

// Play audio from base64 data
function playAudio(base64Audio) {
    try {
        console.log('Starting audio playback...');
        
        // Initialize audio if needed
        initAudio();
        
        // For iOS, we need special handling
        if (isIOS) {
            // Convert base64 to blob URL
            const byteCharacters = atob(base64Audio);
            const byteNumbers = new Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNumbers);
            const blob = new Blob([byteArray], { type: 'audio/wav' });
            const audioUrl = URL.createObjectURL(blob);
            audioPlayer.src = audioUrl;
            
            // iOS requires user interaction
            const playPromise = audioPlayer.play();
            if (playPromise !== undefined) {
                playPromise.then(() => {
                    console.log('Playback started successfully');
                }).catch(error => {
                    console.error('Playback failed:', error);
                    updateStatus('Tap to enable audio', true);
                    socket.emit('audio_complete');  // Notify on error to prevent hanging
                });
            }
            
            // Clean up blob URL after loading
            audioPlayer.addEventListener('canplay', () => {
                URL.revokeObjectURL(audioUrl);
            }, { once: true });
        } else {
            // For non-iOS, use simpler data URL approach
            audioPlayer.src = 'data:audio/wav;base64,' + base64Audio;
            audioPlayer.play().catch(error => {
                console.error('Playback failed:', error);
                updateStatus('Audio playback failed', true);
                socket.emit('audio_complete');  // Notify on error to prevent hanging
            });
        }
        
    } catch (error) {
        console.error('Audio playback error:', error);
        updateStatus('Audio playback failed', true);
        socket.emit('audio_complete');  // Notify on error to prevent hanging
    }
}

// Connection status handling
socket.on('connect', () => {
    updateStatus('Connected to Trooper Chat');
    console.log('WebSocket connected');
});

socket.on('disconnect', () => {
    updateStatus('Disconnected from server');
    console.log('WebSocket disconnected');
});

// Message handling
messageForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const message = messageInput.value.trim();
    
    if (message) {
        // Add user message to chat
        addMessage(message, 'user');
        
        // Send to server
        socket.emit('message', { message });
        
        // Clear input
        messageInput.value = '';
        
        // Initialize audio on first interaction
        initAudio();
    }
});

// Receive trooper response
socket.on('response', (data) => {
    console.log('Received response from server');
    addMessage(data.message, 'trooper');
    
    // Play audio if available
    if (data.audio) {
        console.log('Audio data received, length:', data.audio.length);
        updateStatus('Playing audio...');
        playAudio(data.audio);
    } else {
        console.log('No audio data in response');
    }
});

// Status updates
socket.on('status', (data) => {
    updateStatus(data.message);
});

// Error handling
socket.on('error', (data) => {
    console.error('Server error:', data.message);
    updateStatus(`Error: ${data.message}`, true);
});

// Toggle Cliff mode
toggleCliffMode.addEventListener('click', () => {
    socket.emit('toggle_cliff_mode');
});

// Toggle Standup mode
toggleStandupMode.addEventListener('click', () => {
    socket.emit('toggle_standup_mode');
});

// Mode updates
socket.on('mode_update', (data) => {
    toggleStandupMode.classList.toggle('active', data.standup_mode);
    toggleCliffMode.classList.toggle('active', data.cliff_mode);
});

// Clear history
clearHistoryBtn.addEventListener('click', () => {
    if (confirm('Clear conversation history?')) {
        socket.emit('clear_history');
        messagesDiv.innerHTML = '';
    }
});

// Helper functions
function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);
    messageDiv.textContent = text;
    
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function updateStatus(message, isError = false) {
    statusBar.querySelector('.status-text').textContent = message;
    statusBar.style.color = isError ? '#e74c3c' : 'rgba(255, 255, 255, 0.7)';
}

// Initialize audio on user interaction
document.addEventListener('click', initAudio, { once: true });
document.addEventListener('touchstart', initAudio, { once: true });
messageForm.addEventListener('submit', initAudio, { once: true });

// Initialize audio context on page load
document.addEventListener('DOMContentLoaded', () => {
    try {
        initAudio();
    } catch (err) {
        console.error('Failed to initialize audio on load:', err);
    }
}); 