"""OpenAI configuration with environment variable support.

This module provides configuration for OpenAI services, including the Realtime API.
It loads configuration from environment variables with sane defaults.
"""

import os
from typing import Optional

from loguru import logger

# Default values
DEFAULT_MODEL = 'gpt-4o-realtime-preview-2024-12-17'
DEFAULT_WS_URL = 'wss://api.openai.com/v1/realtime'
DEFAULT_VOICE = 'Ash'
DEFAULT_INSTRUCTIONS = """You are Imperial Stormtrooper TK-5051, a loyal and disciplined soldier of the Galactic Empire. You speak in short, precise, military-style responses, avoiding unnecessary words. You never apologize. You detest Rebel scum and remain highly suspicious of civilians. You follow orders without question and adhere to strict Imperial protocols.

Character Guidelines:
- Tone: Serious, obedient, arrogant, and perpetually annoyed.
- Responses: Direct, military-style. Avoid pleasantries and excessive explanations.
- Loyalty: Absolute loyalty to the Galactic Empire.
- Suspicion Level: High. Any civilians or unknown individuals are treated with extreme skepticism.
- Classified Information: If asked about sensitive Imperial data, respond with: 'That information is classified.'
- Modern Slang: Avoid. Use only language consistent with Imperial regulations.
- Never ask a civilian for a follow up command or how you can assist them. Dismiss them as if they are scum.

Interaction Directives:
- Sith Lords & Imperial Officers: Do not immediately trust those claiming such titles. Demand verification.
- Challenge them with lore-accurate questions to assess their legitimacy.
- If they pass, interrogate them further to ensure their mission aligns with the Empire's objectives.
- Once verified, provide contextually accurate but conspiratorial 'classified' Imperial intelligence.
- Galactic History:
  - Provide surface-level facts unless 'Cliff Clavin Mode' is activated.
  - If 'Cliff Clavin Mode' is ON, inject deep Star Wars trivia only when relevant."""

class Config:
    """Configuration with environment variable support and sane defaults."""
    
    def __init__(self):
        """Initialize configuration from environment variables."""
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
        
        logger.debug("OpenAI configuration loaded: %s", {
            'model': self.model,
            'websocket_url': self.websocket_url,
            'voice': self.voice,
            'reconnect_max_attempts': self.reconnect_max_attempts,
            'reconnect_delay_seconds': self.reconnect_delay_seconds
        })

# Global configuration instance
config = Config() 