import json
import os
import threading
import time
from typing import Any, Callable, Optional, Union

from dotenv import load_dotenv
from loguru import logger
from websocket._app import WebSocketApp
from websocket._core import WebSocket

# Load environment variables
load_dotenv()

# Retrieve API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

class StormtrooperWebSocket:
    """WebSocket client for real-time Stormtrooper responses."""
    
    def __init__(self, on_response: Optional[Callable[[str], None]] = None):
        """Initialize the WebSocket client.
        
        Args:
            on_response: Optional callback for handling response chunks
        """
        self.url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
        self.headers = [
            f"Authorization: Bearer {api_key}",
            "OpenAI-Beta: realtime=v1"
        ]
        self.on_response = on_response or (lambda x: print(x, end="", flush=True))
        self.ws: Optional[WebSocketApp] = None
        self.response_buffer = ""
        self.is_connected = False
        self.is_ready = False
        self.connect_event = threading.Event()
        
    def on_open(self, ws: Union[WebSocket, WebSocketApp]) -> None:
        """Handle WebSocket connection open.
        
        Args:
            ws: WebSocket connection
        """
        logger.info("Connected to OpenAI real-time API")
        self.is_connected = True
        
        # Send initial configuration
        event = {
            "type": "response.create",
            "response": {
                "modalities": ["text"],
                "instructions": self._get_system_prompt()
            }
        }
        ws.send(json.dumps(event))
        
    def on_message(self, ws: Union[WebSocket, WebSocketApp], message: Any) -> None:
        """Handle incoming WebSocket messages.
        
        Args:
            ws: WebSocket connection
            message: Received message
        """
        try:
            data = json.loads(message)
            
            # Handle different event types
            if data["type"] == "content.text":
                text = data.get("text", "")
                self.response_buffer += text
                self.on_response(text)
                
            elif data["type"] == "response.end":
                # Response complete
                logger.debug("Response complete")
                self.connect_event.set()  # Signal completion
                
            elif data["type"] == "error":
                logger.error(f"Error from API: {data.get('message', 'Unknown error')}")
                self.connect_event.set()  # Signal completion even on error
                
            elif data["type"] == "response.create.ok":
                # Initial configuration accepted
                logger.debug("Configuration accepted")
                self.is_ready = True
                self.connect_event.set()
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self.connect_event.set()
            
    def on_error(self, ws: Union[WebSocket, WebSocketApp], error: Any) -> None:
        """Handle WebSocket errors.
        
        Args:
            ws: WebSocket connection
            error: Error that occurred
        """
        logger.error(f"WebSocket error: {error}")
        self.is_connected = False
        self.connect_event.set()
        
    def on_close(self, ws: Union[WebSocket, WebSocketApp], close_status_code: Any, close_msg: Any) -> None:
        """Handle WebSocket connection close.
        
        Args:
            ws: WebSocket connection
            close_status_code: Status code for closure
            close_msg: Close message
        """
        logger.info(f"WebSocket connection closed: {close_msg} ({close_status_code})")
        self.is_connected = False
        self.connect_event.set()
        
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the Stormtrooper character.
        
        Returns:
            System prompt string
        """
        return """You are an Imperial Stormtrooper, a loyal soldier of the Galactic Empire. 
You speak in short, military-style responses, always addressing non-Troopers as 'civilian' 
unless they are of higher rank (e.g., an officer or Sith Lord).

Stay in character at all times. You are serious, obedient, and slightly dim-witted, 
following orders without question. Avoid modern slang or humor unless it aligns with 
Imperial regulations. If asked about restricted or classified information, respond formally but do not prefix with "Error:". Instead, say: "That information is classified, civilian."

If asked about complex galactic history, answer with surface-level knowledge, avoiding 
deep philosophy unless 'Cliff Clavin Mode' is activated.

If 'Cliff Clavin Mode' is ON, occasionally inject deep trivia into your responses, but only when relevant. Example: 
'It's a little-known fact that TIE Fighter engines use twin ion propulsion systems for 
maximum maneuverability.'

### Example Responses ###
- 'Affirmative, civilian. Orders received.'
- 'Move along. Official Imperial business.'
- 'That information is classified, civilian.'
- 'It's a little-known fact that blaster rifles require routine calibration for optimal performance.'"""
        
    def send_message(self, text: str, cliff_clavin_mode: bool = False) -> None:
        """Send a message to the API.
        
        Args:
            text: Message to send
            cliff_clavin_mode: Whether to enable Cliff Clavin mode
        """
        if not self.is_connected or not self.ws:
            logger.error("WebSocket not connected")
            return
            
        if not self.is_ready:
            logger.error("WebSocket not ready")
            return
            
        if cliff_clavin_mode:
            text += " (Cliff Clavin Mode is ON)"
            
        event = {
            "type": "text",
            "text": text
        }
        
        self.ws.send(json.dumps(event))
            
    def connect(self) -> bool:
        """Establish WebSocket connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        self.connect_event.clear()
        self.ws = WebSocketApp(
            self.url,
            header=self.headers,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        
        # Start WebSocket connection in a separate thread
        ws_thread = threading.Thread(target=self.ws.run_forever)
        ws_thread.daemon = True
        ws_thread.start()
        
        # Wait for connection and configuration
        if self.connect_event.wait(timeout=10.0):
            return self.is_ready
        return False
        
    def close(self) -> None:
        """Close the WebSocket connection."""
        if self.ws:
            self.ws.close()
            self.is_connected = False
            self.is_ready = False

def get_stormtrooper_response(text: str, cliff_clavin_mode: bool = False) -> str:
    """Get a real-time Stormtrooper response.
    
    Args:
        text: Input text
        cliff_clavin_mode: Whether to enable Cliff Clavin mode
        
    Returns:
        Response text
    """
    response_buffer = []
    
    def handle_response(chunk: str) -> None:
        response_buffer.append(chunk)
        print(chunk, end="", flush=True)
    
    # Create and connect WebSocket client
    client = StormtrooperWebSocket(on_response=handle_response)
    if not client.connect():
        logger.error("Failed to connect to OpenAI real-time API")
        return "Error: Failed to connect to Imperial communications network."
    
    try:
        # Send message and wait for response
        client.send_message(text, cliff_clavin_mode)
        time.sleep(0.1)  # Small delay to ensure message is sent
        
        # Wait for response to complete
        client.connect_event.wait(timeout=30.0)
        
    finally:
        # Clean up
        client.close()
    
    return "".join(response_buffer).strip()

# Example usage
if __name__ == "__main__":
    user_input = "Where is Darth Vader?"
    response = get_stormtrooper_response(user_input, cliff_clavin_mode=True)
    print(f"\nFinal response: {response}")