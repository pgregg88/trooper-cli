#!/usr/bin/env python3
"""Trooper Web Chat Server.

This module provides a web interface to the Trooper chat functionality.
It runs an HTTP server that serves a single page chat UI and handles
WebSocket connections for real-time chat interaction.
"""

import base64
import os
import random
import sys
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from flask import Flask, make_response, render_template, send_file
from flask_socketio import SocketIO, emit

from src.audio.processor import process_and_play_text
from src.openai import get_stormtrooper_response
from src.openai.conversation import clear_history, load_history, save_history
from src.quotes.manager import QuoteCategory, QuoteManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'trooper-secret-key'
socketio = SocketIO(app, cors_allowed_origins='*')  # Allow cross-origin for testing

# Global state
trivia_mode = False
standup_mode = False
current_sequence = []
sequence_index = 0

# Initialize quote manager
quotes_file = Path("config/quotes.yaml")
quote_manager = QuoteManager(quotes_file)

@app.route('/')
def index():
    """Serve the chat interface."""
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    emit('status', {'message': 'Connected to Trooper Chat'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    pass

@socketio.on('message')
def handle_message(data):
    """Handle incoming chat messages."""
    try:
        user_input = data.get('message', '').strip()
        if not user_input:
            return
            
        # Load conversation history
        previous_input, previous_response = load_history()
        
        # Notify client that trooper is "typing"
        emit('status', {'message': 'Trooper is typing...'})
        
        # Get AI response with context
        response, new_input, new_response = get_stormtrooper_response(
            user_input,
            cliff_clavin_mode=trivia_mode,
            previous_user_input=previous_input,
            previous_response=previous_response
        )
        
        # Save the new context
        save_history(new_input, new_response)
        
        # Generate audio without playing
        output_path = process_and_play_text(
            text=response,
            urgency="normal",
            context="general",
            play_immediately=False,  # Don't play on server
            cleanup=False  # Keep file temporarily
        )
        
        if output_path and output_path.exists():
            try:
                # Read the audio file and encode it
                with open(output_path, 'rb') as audio_file:
                    audio_data = audio_file.read()
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                # Send response with audio
                emit('response', {
                    'message': response,
                    'cliff_mode': trivia_mode,
                    'audio': audio_base64,
                    'content_type': 'audio/wav'  # Explicitly specify content type
                })
                
                # Clean up the file
                output_path.unlink()
            except Exception as e:
                emit('error', {'message': f"Audio processing failed: {str(e)}"})
                if output_path.exists():
                    output_path.unlink()
        else:
            emit('error', {'message': "Failed to generate audio"})
        
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('toggle_cliff_mode')
def handle_toggle_cliff():
    """Toggle Trivia mode."""
    global trivia_mode, current_sequence, sequence_index
    trivia_mode = not trivia_mode
    
    if trivia_mode:
        # Get all monologue quotes first
        current_sequence = quote_manager.select_sequence(
            category=QuoteCategory.MONOLOGUES,
            context="standup",
            count=12  # Get all quotes to ensure we have both
        )
        # Sort to get opener and final_punchline only
        sequence_order = ["opener", "final_punchline"]
        current_sequence = [q for q in current_sequence if q.to_dict().get('sequence', '') in sequence_order]
        current_sequence.sort(key=lambda x: sequence_order.index(x.to_dict().get('sequence', '')))
        sequence_index = 0
        
        if len(current_sequence) == 2:  # Verify we have both quotes
            # Start the sequence
            send_next_quote()
        else:
            emit('error', {'message': "Failed to load trivia sequence"})
            current_sequence = []
            sequence_index = 0
            trivia_mode = False
    else:
        current_sequence = []
        sequence_index = 0
    
    emit('status', {
        'message': f"Trivia mode: {'ON' if trivia_mode else 'OFF'}"
    })

def send_next_quote():
    """Send the next quote in the sequence."""
    global current_sequence, sequence_index
    
    if not current_sequence or sequence_index >= len(current_sequence):
        current_sequence = []
        sequence_index = 0
        return
        
    quote = current_sequence[sequence_index]
    
    # Generate audio
    output_path = process_and_play_text(
        text=quote.text,
        urgency=quote.urgency.value,
        context=quote.context,
        play_immediately=False,
        cleanup=False
    )
    
    if output_path and output_path.exists():
        try:
            # Read and encode audio
            with open(output_path, 'rb') as audio_file:
                audio_data = audio_file.read()
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # Send response with audio
            emit('response', {
                'message': quote.text,
                'cliff_mode': trivia_mode,
                'audio': audio_base64,
                'content_type': 'audio/wav'
            })
            
            # Clean up
            output_path.unlink()
            
        except Exception as e:
            emit('error', {'message': f"Audio processing failed: {str(e)}"})
            if output_path.exists():
                output_path.unlink()
    else:
        emit('error', {'message': "Failed to generate audio"})
    
    sequence_index += 1

@socketio.on('audio_complete')
def handle_audio_complete():
    """Handle audio completion event from client."""
    global current_sequence, sequence_index
    
    if current_sequence and sequence_index < len(current_sequence):
        # Add shorter pause between quotes
        time.sleep(0.5)  # Fixed 0.5 second pause
        
        # Send next quote
        send_next_quote()

@socketio.on('toggle_standup_mode')
def handle_toggle_standup():
    """Toggle Standup mode for random humor quotes."""
    global standup_mode, current_sequence, sequence_index
    
    # Only toggle if we're turning off or if we don't have an active sequence
    if standup_mode or not current_sequence:
        standup_mode = not standup_mode
        if standup_mode:
            # Get 5-7 random humor quotes
            current_sequence = quote_manager.select_random_humor_quotes(
                count=random.randint(5, 7)
            )
            sequence_index = 0
            
            # Start the sequence if we have quotes
            if current_sequence:
                send_next_quote()
            else:
                emit('error', {'message': "No humor quotes available"})
                standup_mode = False
        else:
            current_sequence = []
            sequence_index = 0
        
        emit('status', {
            'message': f"Standup mode: {'ON' if standup_mode else 'OFF'}"
        })
        emit('mode_update', {
            'standup_mode': standup_mode,
            'cliff_mode': trivia_mode
        })

@socketio.on('clear_history')
def handle_clear_history():
    """Clear conversation history."""
    clear_history()
    emit('status', {'message': 'Conversation history cleared'})

def main():
    """Run the web server."""
    host = os.environ.get('TROOPER_WEB_HOST', '0.0.0.0')
    port = int(os.environ.get('TROOPER_WEB_PORT', 5000))
    
    print(f"\nStarting Trooper Web Chat Server on http://{host}:{port}")
    print("Press Ctrl+C to stop the server")
    
    socketio.run(app, host=host, port=port, allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    main() 