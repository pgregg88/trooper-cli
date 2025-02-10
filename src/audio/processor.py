"""Text-to-speech processor with Stormtrooper voice effect and playback.

This module combines TTS generation, audio processing, and playback into a single pipeline.
It provides functionality to:
- Generate speech using Amazon Polly's neural voices
- Apply Stormtrooper voice effects
- Control playback volume and urgency
- Manage temporary audio files

Example:
    Basic usage:
    >>> from src.audio.processor import process_and_play_text
    >>> process_and_play_text("Stop right there!", urgency="high", context="combat")

    Generate without playing:
    >>> output_path = process_and_play_text(
    ...     "All clear",
    ...     play_immediately=False,
    ...     cleanup=False
    ... )
    >>> print(f"Audio saved to: {output_path}")
"""

import os
import signal
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, TypedDict, Union, cast

import numpy as np
import sounddevice as sd
import soundfile as sf
from dotenv import load_dotenv
from loguru import logger

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# Load audio-specific environment variables
audio_env_path = Path(__file__).parent / ".env"
if audio_env_path.exists():
    load_dotenv(audio_env_path)

from src.audio import AudioError, AudioPlayer
from src.audio.effects import StormtrooperEffect
from src.audio.paths import AudioPathManager
from src.audio.polly import PollyClient
from src.quotes.models import Quote, UrgencyLevel


# Add DeviceInfo type definition
class DeviceInfo(TypedDict, total=False):
    """Type definition for sounddevice device info."""
    name: str
    max_output_channels: int
    default_samplerate: float

class AudioCache:
    """Simple LRU cache for processed audio data."""
    
    def __init__(self, max_size: int = 10):
        """Initialize audio cache.
        
        Args:
            max_size: Maximum number of audio samples to cache
        """
        self._cache: Dict[str, np.ndarray] = {}
        self._max_size = max_size
        
    def get(self, key: str) -> Optional[np.ndarray]:
        """Get cached audio data.
        
        Args:
            key: Cache key (text + urgency + context)
            
        Returns:
            Cached audio data if available, else None
        """
        return self._cache.get(key)
        
    def set(self, key: str, audio: np.ndarray) -> None:
        """Cache audio data.
        
        Args:
            key: Cache key (text + urgency + context)
            audio: Audio data to cache
        """
        if len(self._cache) >= self._max_size:
            # Remove oldest entry
            self._cache.pop(next(iter(self._cache)))
        self._cache[key] = audio.copy()  # Store a copy to prevent modification

# Global audio cache instance
_audio_cache = AudioCache()

def process_and_play_text(
    text: str,
    urgency: str = "normal",
    context: str = "general",
    volume: Optional[float] = None,
    play_immediately: bool = True,
    cleanup: bool = True
) -> Optional[Path]:
    """Process text through TTS pipeline and play audio.
    
    Args:
        text: Text to process
        urgency: Voice urgency level
        context: Voice context
        volume: Optional volume level (1-11)
        play_immediately: Whether to play audio after processing
        cleanup: Whether to delete generated files
        
    Returns:
        Path to processed audio file if keep=True, else None
    """
    try:
        # Generate cache key
        cache_key = f"{text}_{urgency}_{context}"
        
        # Check cache first
        cached_audio = _audio_cache.get(cache_key)
        if cached_audio is not None:
            logger.debug("Using cached audio")
            processed_audio = cached_audio
            if volume is not None:
                processed_audio = processed_audio * (volume / 5.0)
        else:
            # Generate speech
            polly = PollyClient()
            pcm_data = polly.generate_speech(text, urgency, context)
            
            # Convert PCM bytes to float32 array
            if not isinstance(pcm_data, bytes):
                raise ValueError("Expected bytes from Polly TTS")
            audio_data = np.frombuffer(pcm_data, dtype=np.int16)
            audio_float = audio_data.astype(np.float32) / 32768.0
            
            # Apply effects
            effect = StormtrooperEffect()
            processed_audio = effect.process_audio_data(
                audio_float,
                16000,  # Sample rate
                UrgencyLevel(urgency)
            )
            
            # Cache the processed audio
            _audio_cache.set(cache_key, processed_audio)
            
            # Apply volume
            if volume is not None:
                processed_audio *= (volume / 5.0)
        
        # Initialize path manager
        path_manager = AudioPathManager()
        path_manager.ensure_directories()
        
        # Use temp file for processing
        temp_path = path_manager.temp_dir / f"temp_{int(time.time())}.wav"
        sf.write(str(temp_path), processed_audio, 16000)
        
        # Move to final location
        output_path = path_manager.processed_dir / f"processed_{int(time.time())}.wav"
        temp_path.rename(output_path)
        
        # Play if requested
        if play_immediately:
            play_audio_file(output_path)
            
        # Cleanup if requested
        if cleanup and output_path.exists():
            output_path.unlink()
            path_manager.cleanup_temp_files()
            return None
            
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to process audio: {e}")
        raise

class TimingManager:
    """Manages timing and pauses between quotes in sequences."""
    
    @staticmethod
    def calculate_pause(current_quote: Quote, next_quote: Optional[Quote] = None) -> float:
        """Calculate appropriate pause between quotes.
        
        Args:
            current_quote: The quote that was just played
            next_quote: The next quote to be played (if any)
            
        Returns:
            Pause duration in seconds
        """
        # Base pause from quote settings
        base_pause = current_quote.max_pause
        
        # Adjust for urgency transitions
        if next_quote and next_quote.urgency != current_quote.urgency:
            if next_quote.urgency == UrgencyLevel.HIGH:
                # Shorter pause before high urgency
                base_pause *= 0.7
            elif current_quote.urgency == UrgencyLevel.HIGH:
                # Longer pause after high urgency
                base_pause *= 1.3
                
        # Ensure minimum pause
        return max(base_pause, 0.1)

    @staticmethod
    def handle_interrupt(sequence: List[Quote], current_index: int) -> None:
        """Handle sequence interruption.
        
        Args:
            sequence: The quote sequence being played
            current_index: Index of current quote in sequence
        """
        logger.info("\nSequence interrupted.")
        # Use AudioPathManager for cleanup
        path_manager = AudioPathManager()
        try:
            path_manager.cleanup_temp_files()
        except Exception as e:
            logger.error(f"Error during interrupt cleanup: {e}")

class SequenceController:
    """Controls sequence playback and state."""
    
    def __init__(self):
        """Initialize sequence controller."""
        self._is_playing = False
        self._current_sequence: Optional[List[Quote]] = None
        self._current_index = 0
        self._timing_manager = TimingManager()
    
    @property
    def is_playing(self) -> bool:
        """Check if a sequence is currently playing."""
        return self._is_playing
    
    def start_sequence(
        self,
        quotes: List[Quote],
        volume: Optional[float] = None,
        cleanup: bool = True
    ) -> None:
        """Start playing a sequence of quotes.
        
        Args:
            quotes: List of quotes to play
            volume: Optional volume level (1-11)
            cleanup: Whether to cleanup files after playback
        """
        if self._is_playing:
            logger.warning("Sequence already playing")
            return
            
        self._is_playing = True
        self._current_sequence = quotes
        self._current_index = 0
        
        try:
            process_and_play_sequence(quotes, volume=volume, cleanup=cleanup)
        finally:
            self._is_playing = False
            self._current_sequence = None
            self._current_index = 0
    
    def stop_sequence(self) -> None:
        """Stop the current sequence if playing."""
        if not self._is_playing:
            logger.warning("No sequence playing")
            return
            
        # Send interrupt signal to stop playback
        os.kill(os.getpid(), signal.SIGINT)

# Create global sequence controller instance
sequence_controller = SequenceController()

def process_and_play_sequence(
    quotes: List[Quote],
    volume: Optional[float] = None,
    play_immediately: bool = True,
    cleanup: bool = True
) -> List[Path]:
    """Process and play a sequence of quotes."""
    try:
        output_files = []
        timing_manager = TimingManager()
        path_manager = AudioPathManager()
        
        # Set up interrupt handler
        def handle_interrupt(signum, frame):
            timing_manager.handle_interrupt(quotes, len(output_files))
            sys.exit(0)
        
        signal.signal(signal.SIGINT, handle_interrupt)
        
        for i, quote in enumerate(quotes):
            if sequence_controller._current_sequence:
                sequence_controller._current_index = i
                
            # Check if processed file already exists
            base_name = path_manager.get_base_name(quote)
            processed_path = path_manager.processed_dir / f"{base_name}_processed.wav"
            
            if processed_path.exists():
                logger.debug(f"Using existing processed file: {processed_path}")
                output_files.append(processed_path)
            else:
                # Process quote only if needed
                output_path = process_and_play_text(
                    text=quote.text,
                    urgency=quote.urgency.value,
                    context=quote.context,
                    volume=volume,
                    play_immediately=False,
                    cleanup=False
                )
                if output_path:
                    output_files.append(output_path)
                
        # Play sequence if requested
        if play_immediately and output_files:
            for i, file_path in enumerate(output_files):
                logger.debug(f"Playing: {file_path}")
                play_audio_file(file_path)
                
                # Calculate and add pause between quotes
                if i < len(quotes) - 1:
                    next_quote = quotes[i + 1]
                    pause_duration = timing_manager.calculate_pause(quotes[i], next_quote)
                    if pause_duration > 0:
                        time.sleep(pause_duration)
        
        return output_files
        
    except Exception as e:
        logger.error(f"Failed to process sequence: {e}")
        raise

def play_audio_file(file_path: Union[str, Path]) -> None:
    """Play an audio file.
    
    Args:
        file_path: Path to audio file
        
    Raises:
        AudioError: If playback fails due to device or file issues
    """
    try:
        # Get configured device
        device = os.environ.get("TROOPER_AUDIO_DEVICE")
        device_id = int(device) if device else None
        
        # Verify device is available
        try:
            import sounddevice as sd
            if device_id is not None:
                devices = sd.query_devices()
                if device_id >= len(devices):
                    raise AudioError(f"Audio device {device_id} not found")
                device_info = devices[device_id]  # type: ignore[index]
                if device_info.get('max_output_channels', 0) <= 0:
                    raise AudioError(f"Device {device_id} is not an output device")
        except Exception as e:
            logger.warning(f"Audio device verification failed: {e}")
            device_id = None  # Fall back to default device
        
        # Load and verify audio file
        try:
            audio_data, sample_rate = sf.read(str(file_path))
        except Exception as e:
            raise AudioError(f"Failed to load audio file: {e}")
        
        # Check memory usage
        try:
            audio_size = audio_data.nbytes / (1024 * 1024)  # Size in MB
            if audio_size > 100:  # Arbitrary limit
                logger.warning(f"Large audio file: {audio_size:.1f}MB")
        except Exception:
            pass  # Memory check is optional
        
        # Play audio with error handling
        try:
            sd.play(audio_data, sample_rate, device=device_id)
            sd.wait()  # Wait for playback to finish
        except Exception as e:
            raise AudioError(f"Playback failed: {e}")
        
    except Exception as e:
        logger.error(f"Failed to play audio: {e}")
        raise 