"""AWS Polly integration for text-to-speech."""

import os
from pathlib import Path
from typing import Optional
import boto3
from loguru import logger
from src.quotes import UrgencyLevel

class PollyClient:
    """AWS Polly client for text-to-speech synthesis."""
    
    # SSML templates for different urgency levels
    URGENCY_TEMPLATES = {
        'high': '<speak><amazon:effect name="drc"><prosody volume="x-loud" rate="medium"><s>{text}</s></prosody></amazon:effect></speak>',
        'medium': '<speak><amazon:effect name="drc"><prosody volume="x-loud" rate="medium"><s>{text}</s></prosody></amazon:effect></speak>',
        'low': '<speak><amazon:effect name="drc"><prosody volume="loud" rate="medium"><s>{text}</s></prosody></amazon:effect></speak>'
    }
    
    # SSML templates for different contexts
    CONTEXT_TEMPLATES = {
        'combat': '{text}<break time="350ms"/><prosody rate="x-fast" volume="x-loud">Over!</prosody>',
        'patrol': '{text}<break time="300ms"/><prosody rate="x-fast" volume="x-loud">Over.</prosody>',
        'alert': '<prosody rate="x-fast" volume="x-loud">Alert!</prosody><break time="200ms"/>{text}',
        'inspection': '{text}',
        'warning': '{text}',
        'casual': '{text}'
    }
    
    def __init__(self, profile_name: str = 'trooper', region_name: str = 'us-east-1'):
        """Initialize Polly client with AWS credentials."""
        try:
            self.polly = boto3.Session(
                profile_name=profile_name,
                region_name=region_name
            ).client('polly')
            self.voice_id = "Matthew"  # Default voice
            logger.info(f"Initialized Polly client with voice: {self.voice_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Polly client: {str(e)}")
            raise
    
    def apply_ssml_template(self, text: str, urgency: str = 'medium', context: str = 'patrol') -> str:
        """Apply SSML template based on urgency and context.
        
        Args:
            text: Raw text to enhance with SSML
            urgency: Urgency level (high, medium, low)
            context: Context for the quote
            
        Returns:
            SSML-enhanced text
        """
        # Clean up any existing XML tags
        text = text.replace('<', '&lt;').replace('>', '&gt;')
        
        # Add breaks between key phrases (after punctuation)
        text = text.replace('. ', '.<break time="250ms"/> ')
        text = text.replace('! ', '!<break time="200ms"/> ')
        text = text.replace('? ', '?<break time="250ms"/> ')
        text = text.replace(', ', ',<break time="150ms"/> ')
        
        # Make single words x-fast
        words = text.split()
        if len(words) == 1:
            text = f'<prosody rate="x-fast">{text}</prosody>'
        
        # Apply context-specific formatting first
        context_template = self.CONTEXT_TEMPLATES.get(context, self.CONTEXT_TEMPLATES['casual'])
        text = context_template.format(text=text)
        
        # Wrap everything in the urgency template
        urgency_template = self.URGENCY_TEMPLATES.get(urgency, self.URGENCY_TEMPLATES['medium'])
        
        return urgency_template.format(text=text)
    
    def generate_speech(self, text: str, output_path: Optional[str] = None, 
                       urgency: str = 'medium', context: str = 'patrol') -> bytes | str:
        """Generate speech from text using Polly.
        
        Args:
            text: The text to convert to speech
            output_path: Optional path to save the audio file
            urgency: Urgency level for SSML template
            context: Context for SSML template
            
        Returns:
            Raw PCM audio data if no output_path is provided,
            otherwise returns the path to the saved file as string
        """
        try:
            # Apply SSML templates
            ssml_text = self.apply_ssml_template(text, urgency, context)
            logger.debug(f"Generated SSML: {ssml_text}")
            
            response = self.polly.synthesize_speech(
                Text=ssml_text,
                TextType='ssml',
                OutputFormat='pcm',
                SampleRate='16000',
                VoiceId=self.voice_id,
                Engine='neural'
            )
            
            if "AudioStream" not in response:
                raise ValueError("No AudioStream in Polly response")
            
            audio_data = response['AudioStream'].read()
            
            if output_path:
                path = Path(output_path)
                path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(path, 'wb') as f:
                    f.write(audio_data)
                logger.info(f"Saved audio to: {path}")
                return str(path)
            
            return audio_data
            
        except Exception as e:
            logger.error(f"Failed to generate speech: {str(e)}")
            raise
    
    def set_voice(self, voice_id: str) -> None:
        """Change the Polly voice ID."""
        self.voice_id = voice_id
        logger.info(f"Changed voice to: {voice_id}")

def get_polly_ssml(text: str, urgency: UrgencyLevel) -> str:
    """Generate SSML text for AWS Polly with appropriate effects.
    
    Args:
        text: Text to convert to speech
        urgency: Urgency level for voice effects
        
    Returns:
        SSML formatted text
    """
    # Base templates for different urgency levels
    URGENCY_TEMPLATES = {
        UrgencyLevel.HIGH.value: '<speak><amazon:effect name="drc"><prosody volume="x-loud" rate="medium"><s>{text}</s></prosody></amazon:effect></speak>',
        UrgencyLevel.MEDIUM.value: '<speak><amazon:effect name="drc"><prosody volume="x-loud" rate="medium"><s>{text}</s></prosody></amazon:effect></speak>',
        UrgencyLevel.LOW.value: '<speak><amazon:effect name="drc"><prosody volume="loud" rate="medium"><s>{text}</s></prosody></amazon:effect></speak>'
    }
    
    # Get template for urgency level
    template = URGENCY_TEMPLATES[urgency.value]
    
    # Format template with text
    return template.format(text=text) 