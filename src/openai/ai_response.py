"""OpenAI integration for Stormtrooper responses."""

import json
import os
import threading
import time
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv

from ..realtime.client import RealtimeClient
from .config import config

# Load environment variables
load_dotenv()

# Constants for token limits
BASE_TOKEN_LIMIT = 75
CLIFF_MODE_TOKEN_LIMIT = 250

def get_stormtrooper_response(
    user_input: str, 
    cliff_clavin_mode: bool = False,
    previous_user_input: Optional[str] = None,
    previous_response: Optional[str] = None
) -> Tuple[str, str, str]:
    """Get a response from the Stormtrooper AI.
    
    Args:
        user_input: The current user's question/input
        cliff_clavin_mode: Whether to enable Cliff Clavin mode (increases token limit for detailed trivia)
        previous_user_input: The last user message (optional)
        previous_response: The last assistant response (optional)
        
    Returns:
        tuple: (response_text, user_input, response_text) - Current response and context for next call
    """
    # Create client
    client = RealtimeClient()
    
    try:
        # Connect with timeout
        client.connect(timeout=30)
        
        # Configure session
        client.send_event({
            "type": "session.update",
            "session": {
                "instructions": config.instructions,
                "modalities": ["text"]
            }
        })
        
        # Add previous context if available
        if previous_user_input and previous_response:
            client.send_event({
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [{
                        "type": "input_text",
                        "text": previous_user_input
                    }]
                }
            })
            client.send_event({
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
        
        # Add current user input
        current_input = user_input
        if cliff_clavin_mode:
            current_input += " (Cliff Clavin Mode is ON)"
            
        client.send_event({
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [{
                    "type": "input_text",
                    "text": current_input
                }]
            }
        })
        
        # Request response
        client.send_event({
            "type": "response.create",
            "response": {
                "modalities": ["text"]
            }
        })
        
        # Wait for session ready
        while not client.session_ready:
            time.sleep(0.1)
            
        # Wait for response with timeout
        start_time = time.time()
        while time.time() - start_time < 30:  # 30 second timeout
            if client.current_response_buffer:
                response_text = "".join(client.current_response_buffer)
                # Clean up response by removing any "Assistant: " prefix
                response_text = response_text.replace("Assistant: ", "").strip()
                return response_text, user_input, response_text
            time.sleep(0.1)
            
        raise TimeoutError("Response timed out")
        
    finally:
        client.close()

# Example usage
if __name__ == "__main__":
    # First message
    response1, prev_input, prev_response = get_stormtrooper_response(
        "What's your designation?", 
        cliff_clavin_mode=True
    )
    print("Response 1:", response1)
    
    # Second message with context
    response2, _, _ = get_stormtrooper_response(
        "And what's your current assignment?",
        cliff_clavin_mode=True,
        previous_user_input=prev_input,
        previous_response=prev_response
    )
    print("Response 2:", response2)