"""OpenAI Realtime API WebSocket client.

A self-contained implementation of the OpenAI Realtime API client.
Handles configuration, WebSocket connection, and message handling.
"""
import json
import logging
import os
import threading
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from websocket import WebSocket
from websocket._app import WebSocketApp

# Try to load .env files in order of priority first
try:
    # First try src/realtime/.env
    local_env_path = Path(__file__).parent / '.env'
    if local_env_path.exists():
        load_dotenv(local_env_path)
        print(f"Loaded .env from {local_env_path}")
    
    # Then try root .env as fallback
    root_env_path = Path(__file__).parent.parent.parent / '.env'
    if root_env_path.exists():
        load_dotenv(root_env_path, override=False)  # Don't override existing vars
        print(f"Loaded .env from {root_env_path}")
except Exception as e:
    pass  # Fail silently if .env files don't exist or can't be loaded

# Now configure logging with the loaded environment variables
logger = logging.getLogger("realtime_client")
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))

# Get absolute paths for log files
workspace_root = Path(__file__).parent.parent.parent
log_file = workspace_root / os.getenv("LOG_FILE", "logs/realtime.log")
transcript_file = workspace_root / os.getenv("TRANSCRIPT_FILE", "logs/transcript.log")

# Ensure log directories exist
for log_path in [log_file, transcript_file]:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Created log directory: {log_path.parent}")

# File handler for operational logs
file_handler = RotatingFileHandler(
    str(log_file),
    maxBytes=10_000_000,  # 10MB
    backupCount=5,
    delay=True  # Don't create file until first write
)
file_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)
logger.addHandler(file_handler)

# File handler for transcript logs
transcript_logger = logging.getLogger("realtime_transcript")
transcript_logger.setLevel(logging.INFO)
transcript_handler = RotatingFileHandler(
    str(transcript_file),
    maxBytes=10_000_000,  # 10MB
    backupCount=5,
    delay=True  # Don't create file until first write
)
transcript_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(message)s')
)
transcript_logger.addHandler(transcript_handler)

# Console handler for operational logs only
console_handler = logging.StreamHandler()
console_handler.setFormatter(
    logging.Formatter('%(message)s')  # Simplified for console
)
logger.addHandler(console_handler)

# Test log file creation
logger.info("Logging initialized")
transcript_logger.info("Transcript logging initialized")

# Configuration with defaults
DEFAULT_MODEL = 'gpt-4o-realtime-preview-2024-12-17'
DEFAULT_WS_URL = 'wss://api.openai.com/v1/realtime'
DEFAULT_VOICE = 'Ash'
DEFAULT_INSTRUCTIONS = (
    "You are a stormtrooper in the Imperial Army. "
    "You are gruff and all business. "
    "Keep your responses concise and militaristic."
)

# Load configuration with fallbacks
class Config:
    """Configuration with environment variable support and sane defaults."""
    
    def __init__(self):
        # Required configuration
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY must be set in environment variables or .env file"
            )
            
        # Optional configuration with defaults
        self.model = os.getenv('REALTIME_MODEL', DEFAULT_MODEL)
        self.websocket_url = os.getenv('REALTIME_WEBSOCKET_URL', DEFAULT_WS_URL)
        self.voice = os.getenv('AI_VOICE', DEFAULT_VOICE)
        self.instructions = os.getenv('SYSTEM_INSTRUCTIONS', DEFAULT_INSTRUCTIONS)
        self.reconnect_max_attempts = int(os.getenv('RECONNECT_MAX_ATTEMPTS', '3'))
        self.reconnect_delay_seconds = int(os.getenv('RECONNECT_DELAY_SECONDS', '2'))
        
        logger.debug("Configuration loaded: %s", {
            'model': self.model,
            'websocket_url': self.websocket_url,
            'voice': self.voice,
            'reconnect_max_attempts': self.reconnect_max_attempts,
            'reconnect_delay_seconds': self.reconnect_delay_seconds
        })


class RealtimeClient:
    """Client for interacting with OpenAI's Realtime API via WebSocket."""
    
    def __init__(self):
        """Initialize the client with configuration."""
        self.config = Config()
        self.ws: Optional[WebSocketApp] = None
        self.ws_thread: Optional[threading.Thread] = None
        self.connected = threading.Event()
        self.session_ready = False
        self.reconnect_attempts = 0
        self.current_response_buffer = []  # Buffer for accumulating response text
        logger.info("Realtime client initialized")
        
    def connect(self, timeout: int = 30) -> None:
        """Establish WebSocket connection with OpenAI realtime API."""
        while self.reconnect_attempts < self.config.reconnect_max_attempts:
            try:
                self._connect(timeout)
                self.reconnect_attempts = 0  # Reset on successful connection
                return
            except Exception as e:
                self.reconnect_attempts += 1
                if self.reconnect_attempts >= self.config.reconnect_max_attempts:
                    logger.error(
                        "Failed to connect after %d attempts: %s",
                        self.config.reconnect_max_attempts,
                        str(e)
                    )
                    raise RuntimeError(
                        f"Failed to connect after {self.config.reconnect_max_attempts} "
                        f"attempts: {e}"
                    )
                logger.warning(
                    "Connection attempt %d failed, retrying in %ds...",
                    self.reconnect_attempts,
                    self.config.reconnect_delay_seconds
                )
                time.sleep(self.config.reconnect_delay_seconds)
                
    def _connect(self, timeout: int) -> None:
        """Internal connection method."""
        url = f"{self.config.websocket_url}?model={self.config.model}"
        headers = [
            f"Authorization: Bearer {self.config.api_key}",
            "OpenAI-Beta: realtime=v1"
        ]
        
        logger.debug("Connecting to %s", url)
        self.ws = WebSocketApp(
            url,
            header=headers,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )
        
        # Run WebSocket connection in background thread
        self.ws_thread = threading.Thread(
            target=self.ws.run_forever,
            daemon=True
        )
        self.ws_thread.start()
        
        # Wait for connection
        if not self.connected.wait(timeout):
            logger.error("Connection timeout after %ds", timeout)
            raise RuntimeError("Connection timeout")
            
    def send_event(self, event: Dict[str, Any]) -> None:
        """Send an event to the server."""
        if not self.ws or not self.connected.is_set():
            raise RuntimeError("WebSocket not connected")
            
        try:
            logger.debug("Sending event: %s", event)
            self.ws.send(json.dumps(event))
        except Exception as e:
            logger.error("Error sending event: %s", str(e))
            self._handle_send_error()
            raise
            
    def _handle_send_error(self) -> None:
        """Handle send errors by attempting reconnection."""
        logger.warning("Handling send error, attempting reconnection")
        self.connected.clear()
        self.session_ready = False
        try:
            self.connect()  # Attempt reconnection
        except Exception as e:
            logger.error("Failed to reconnect: %s", str(e))
            
    def close(self) -> None:
        """Clean up and close the WebSocket connection."""
        if self.ws:
            try:
                logger.info("Closing WebSocket connection")
                self.ws.close()
            finally:
                self.ws = None
                self.ws_thread = None
                self.session_ready = False
                self.connected.clear()
                self.reconnect_attempts = 0
            
    def _on_open(self, ws: WebSocket) -> None:
        """Handle WebSocket connection open."""
        logger.info("Connected to OpenAI Realtime API")
        self.connected.set()
        
        # Configure session with instructions
        session_config = {
            "type": "session.update",
            "session": {
                "instructions": self.config.instructions,
                "modalities": ["text"]
            }
        }
        logger.debug("Configuring session: %s", session_config)
        self.send_event(session_config)
        
    def _on_message(self, ws: WebSocket, message: Any) -> None:
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(message)
            logger.debug("Received message: %s", data)
            
            # Handle different event types
            if data.get("type") == "session.created":
                logger.info("Session created")
                
            elif data.get("type") == "session.updated":
                self.session_ready = True
                logger.info("Session configuration updated")
                
            elif data.get("type") == "response.created":
                # Clear the buffer for new response
                self.current_response_buffer = []
                print("\nAssistant: ", end="", flush=True)
                
            elif data.get("type") == "response.text.delta":
                # Accumulate text in buffer
                text = data.get("delta", "")
                if text:
                    self.current_response_buffer.append(text)
                    print(text, end="", flush=True)
                    
            elif data.get("type") == "response.text.done":
                # Log the complete response to transcript
                complete_response = "".join(self.current_response_buffer)
                transcript_logger.info("Assistant: %s", complete_response)
                self.current_response_buffer = []
                
            elif data.get("type") == "response.done":
                print("\nYou: ", end="", flush=True)
                
            elif data.get("type") == "error":
                error_msg = data.get("message", "Unknown error")
                logger.error("Server error: %s", error_msg)
                if "session expired" in error_msg.lower():
                    self._handle_session_expiry()
                print("\nError: ", error_msg)
                print("You: ", end="", flush=True)
        
        except json.JSONDecodeError as e:
            logger.error("Error parsing message: %s", str(e))
            
    def _handle_session_expiry(self) -> None:
        """Handle session expiry by reconnecting."""
        logger.warning("Session expired, attempting reconnection")
        self.session_ready = False
        try:
            self.connect()  # Attempt reconnection
        except Exception as e:
            logger.error("Failed to reconnect after session expiry: %s", str(e))
            
    def _on_error(self, ws: WebSocket, error: Any) -> None:
        """Handle WebSocket errors."""
        logger.error("WebSocket error: %s", str(error))
        self.connected.clear()
        
    def _on_close(self, ws: WebSocket, close_status_code: Any, close_msg: Any) -> None:
        """Handle WebSocket connection close."""
        logger.info("Connection closed: %s (%s)", close_msg, close_status_code)
        self.session_ready = False
        self.connected.clear()


def main() -> None:
    """Run an interactive chat session with the Realtime API."""
    try:
        # Create and connect client
        client = RealtimeClient()
        
        logger.info("Initializing Stormtrooper Realtime Chat")
        print("\nInitializing Stormtrooper Realtime Chat...")
        print("Type 'exit' to quit\n")
        
        client.connect()
        
        # Wait for session to be ready
        while not client.session_ready:
            time.sleep(0.1)
            
        print("You: ", end="", flush=True)
        
        while True:
            try:
                user_input = input().strip()
                
                if not user_input:
                    print("You: ", end="", flush=True)
                    continue
                    
                if user_input.lower() == 'exit':
                    break
                
                # Log user input
                transcript_logger.info("User: %s", user_input)
                
                # Send message and wait for response
                message = {
                    "type": "conversation.item.create",
                    "item": {
                        "type": "message",
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": user_input
                            }
                        ]
                    }
                }
                client.send_event(message)
                
                # Request response
                response_request = {
                    "type": "response.create",
                    "response": {
                        "modalities": ["text"]
                    }
                }
                client.send_event(response_request)
                
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt, exiting")
                break
                
            except Exception as e:
                logger.error("Error in main loop: %s", str(e), exc_info=True)
                print(f"\nError: {e}")
                print("Type 'exit' to quit or try again")
                print("You: ", end="", flush=True)
    
    except Exception as e:
        logger.error("Fatal error: %s", str(e), exc_info=True)
        print(f"\nFatal error: {e}")
        raise
        
    finally:
        if 'client' in locals():
            client.close()
            

if __name__ == '__main__':
    main() 