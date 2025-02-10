"""Realtime Web Server for Trooper Chat.

This module provides a WebSocket-based server for realtime chat interaction.
It handles streaming responses and audio generation for the Trooper chat interface.
"""

import asyncio
import base64
import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional, cast

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from loguru import logger

from src.audio.processor import process_and_play_text
from src.openai.ai_response import get_stormtrooper_response
from src.openai.config import config
from src.openai.conversation import clear_history, load_history, save_history
from src.realtime import client

app = Flask(__name__, 
    template_folder=str(Path(__file__).parent / 'templates'),
    static_folder=str(Path(__file__).parent / 'static')
)
app.config['SECRET_KEY'] = 'trooper-realtime-key'
socketio = SocketIO(app, cors_allowed_origins='*')  # Let SocketIO auto-detect async mode

# Global state
active_connections = {}

class ChatConnection:
    """Manages state for a single chat connection."""
    
    def __init__(self, sid):
        """Initialize connection state.
        
        Args:
            sid: Socket.IO session ID
        """
        self.sid = sid
        self.client = None
        self.cliff_mode = False
        self.current_response = []
        
    def initialize(self):
        """Initialize realtime client."""
        self.client = client.RealtimeClient()
        self.client.connect()
        
    def cleanup(self):
        """Clean up resources."""
        if self.client:
            self.client.close()
            self.client = None

@app.route('/')
def index():
    """Serve the realtime chat interface."""
    return render_template('realtime.html')

# Keep the /realtime route for backward compatibility
@app.route('/realtime')
def realtime():
    """Serve the realtime chat interface (alias for backward compatibility)."""
    return render_template('realtime.html')

@socketio.on('connect')
def handle_connect():
    """Handle new client connection."""
    # Access sid through SocketIO's request context
    sid = cast(str, getattr(request, 'sid', None))
    if not sid:
        logger.error("No session ID available")
        return
        
    active_connections[sid] = ChatConnection(sid)
    
    try:
        # Initialize client
        active_connections[sid].initialize()
        emit('status', {'message': 'Connected to Trooper Chat'})
        logger.info(f"Client connected: {sid}")
    except Exception as e:
        logger.error(f"Failed to initialize connection: {e}")
        emit('error', {'message': 'Failed to initialize connection'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    sid = cast(str, getattr(request, 'sid', None))
    if sid and sid in active_connections:
        try:
            active_connections[sid].cleanup()
            del active_connections[sid]
            logger.info(f"Client disconnected: {sid}")
        except Exception as e:
            logger.error(f"Error during disconnect cleanup: {e}")

@socketio.on('message')
def handle_message(data):
    """Handle incoming chat messages."""
    try:
        sid = cast(str, getattr(request, 'sid', None))
        if not sid:
            emit('error', {'message': 'Invalid session'})
            return
            
        conn = active_connections.get(sid)
        if not conn or not conn.client:
            emit('error', {'message': 'Connection not initialized'})
            return
            
        user_input = data.get('message', '').strip()
        if not user_input:
            return
            
        # Load conversation history
        previous_input, previous_response = load_history()
        
        # Notify client
        emit('status', {'message': 'Trooper is typing...'})
        
        # Configure session
        conn.client.send_event({
            "type": "session.update",
            "session": {
                "instructions": config.instructions,
                "modalities": ["text"]
            }
        })
        
        # Add previous context if available
        if previous_input and previous_response:
            conn.client.send_event({
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [{
                        "type": "input_text",
                        "text": previous_input
                    }]
                }
            })
            conn.client.send_event({
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "assistant",
                    "content": [{
                        "type": "text",
                        "text": previous_response
                    }]
                }
            })
        
        # Send user message
        conn.client.send_event({
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [{
                    "type": "input_text",
                    "text": user_input
                }]
            }
        })
        
        # Request response
        conn.client.send_event({
            "type": "response.create",
            "response": {
                "modalities": ["text"]
            }
        })
        
        # Stream response
        conn.current_response = []
        for event in conn.client.events():
            if event.get('type') == 'text_delta':
                chunk = event.get('delta', {}).get('text', '')
                if chunk:
                    conn.current_response.append(chunk)
                    emit('response_chunk', {'chunk': chunk})
            elif event.get('type') == 'response.end':
                break
        
        # Complete response
        full_response = ''.join(conn.current_response)
        
        # Save history
        save_history(user_input, full_response)
        
        # Generate audio
        try:
            output_path = process_and_play_text(
                text=full_response,
                urgency="normal",
                context="general",
                play_immediately=False,
                cleanup=False
            )
            
            if output_path and output_path.exists():
                with open(output_path, 'rb') as audio_file:
                    audio_data = audio_file.read()
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                    
                emit('audio', {
                    'audio': audio_base64,
                    'content_type': 'audio/wav'
                })
                
                output_path.unlink()
                
        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
            emit('error', {'message': f"Audio processing failed: {str(e)}"})
        
        # Signal completion
        emit('response_complete', {})
        
    except Exception as e:
        logger.error(f"Message handling failed: {e}")
        emit('error', {'message': str(e)})

@socketio.on('toggle_cliff_mode')
def handle_toggle_cliff(data):
    """Toggle Cliff mode."""
    sid = cast(str, getattr(request, 'sid', None))
    if not sid:
        emit('error', {'message': 'Invalid session'})
        return
        
    if sid in active_connections:
        active_connections[sid].cliff_mode = data.get('enabled', False)
        emit('status', {
            'message': f"Cliff mode: {'ON' if active_connections[sid].cliff_mode else 'OFF'}"
        })

@socketio.on('clear_history')
def handle_clear_history():
    """Clear conversation history."""
    clear_history()
    emit('status', {'message': 'Conversation history cleared'})

def main():
    """Run the realtime web server."""
    host = os.environ.get('TROOPER_WEB_HOST', '0.0.0.0')
    port = int(os.environ.get('TROOPER_REALTIME_PORT', 5002))  # Default to 5002 for realtime
    
    print(f"\nStarting Trooper Realtime Chat Server on http://{host}:{port}")
    print("Press Ctrl+C to stop the server")
    
    try:
        socketio.run(app, host=host, port=port, allow_unsafe_werkzeug=True)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\nError: Port {port} is already in use.")
            print("Please ensure no other instances are running or set TROOPER_REALTIME_PORT to a different value.")
            sys.exit(1)
        raise

if __name__ == '__main__':
    main() 