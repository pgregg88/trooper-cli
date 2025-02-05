"""Audio effects processing for Stormtrooper voice."""

from pathlib import Path
from typing import Optional, Union, Tuple
from dataclasses import dataclass
import random
from loguru import logger
import numpy as np
from scipy import signal
import soundfile as sf

from src.quotes import UrgencyLevel, URGENCY_EFFECTS

@dataclass
class EffectParams:
    """Parameters for Stormtrooper voice effects."""
    
    # Audio Format
    sample_rate: int = 44100
    output_format: str = "WAV"
    
    # Filter Curve EQ - More "tinny" radio sound
    highpass_freq: float = 500.0    # Back to 500Hz to reduce bass
    lowpass_freq: float = 2500.0    # Narrower band for more radio-like sound
    mid_boost_db: float = 20.0      # Much stronger boost in the mids (increased from 15)
    filter_order: int = 6           # Steeper filter rolloff
    
    # Helmet Resonance
    resonance_freq1: float = 1000.0  # First resonant peak (Hz)
    resonance_freq2: float = 2000.0  # Second resonant peak (Hz)
    resonance_q: float = 5.0        # Q factor for resonance
    resonance_gain: float = 9.0     # Gain for resonant peaks (increased from 6)
    
    # Radio Modulation
    mod_freq: float = 55.0         # Modulation frequency (Hz)
    mod_depth: float = 0.15        # Modulation depth (0-1)
    
    # Output Gain
    output_gain_db: float = 6.0    # Additional output gain boost
    
    # Radio Effects - More aggressive static
    static_duration_min: float = 0.08  # Longer minimum duration
    static_duration_max: float = 0.2   # Longer maximum duration
    static_volume: float = 0.4        # Much louder static
    static_variation: float = 0.3     # Less variation to keep it consistently loud
    static_ramp_percent: float = 0.4  # Percentage of static duration for volume ramp
    
    # Mic Click - Much more prominent clicks
    click_duration: float = 0.04    # Longer duration for more impact
    click_volume: float = 0.8      # Very loud clicks
    click_freq: float = 2000.0     # Frequency of click sound (Hz)
    click_variation: float = 0.2   # Less variation to keep clicks consistently loud

class StormtrooperEffect:
    """Audio effects processor for Stormtrooper voice."""
    
    def __init__(self, params: Optional[EffectParams] = None):
        """Initialize the effects processor.
        
        Args:
            params: Optional effect parameters
        """
        self.params = params or EffectParams()
        self.sample_rate = self.params.sample_rate
        self.current_urgency = UrgencyLevel.MEDIUM  # Default urgency
        logger.info("Initialized Stormtrooper effects processor")
        
    def set_urgency(self, urgency: Union[UrgencyLevel, str]) -> None:
        """Set the urgency level for effect parameters.
        
        Args:
            urgency: Urgency level to use for effects
        """
        if isinstance(urgency, str):
            urgency = UrgencyLevel(urgency)
        self.current_urgency = urgency
        logger.debug(f"Set effect urgency to: {urgency.value}")
        
    def _get_urgency_params(self) -> dict:
        """Get effect parameters for current urgency level.
        
        Returns:
            Dictionary of effect parameters
        """
        return URGENCY_EFFECTS[self.current_urgency.value]
        
    def process_file(self, input_path: Union[str, Path], output_path: Optional[Union[str, Path]] = None, urgency: Optional[Union[UrgencyLevel, str]] = None) -> str:
        """Process an audio file with Stormtrooper effects.
        
        Args:
            input_path: Path to input audio file (MP3 or WAV)
            output_path: Optional path for output file. If not provided,
                        will append '_processed' to input filename
            urgency: Optional urgency level for effects
            
        Returns:
            Path to processed audio file
        """
        if urgency:
            self.set_urgency(urgency)
            
        try:
            # Convert paths to Path objects
            input_path = Path(input_path)
            
            # Read audio file
            data, sample_rate = sf.read(str(input_path))
            self.sample_rate = sample_rate
            
            # Convert to mono if stereo
            if len(data.shape) > 1:
                data = np.mean(data, axis=1)
            
            # Process audio
            processed = self._process_audio(data)
            
            # Generate output path if not provided
            if output_path is None:
                output_path = input_path.parent / f"{input_path.stem}_processed.wav"
            else:
                output_path = Path(output_path)
                if output_path.suffix.lower() not in ['.wav', '.mp3']:
                    output_path = output_path.with_suffix('.wav')
            
            # Save processed audio
            sf.write(str(output_path), processed, sample_rate, format='WAV', subtype='PCM_16')
            logger.info(f"Saved processed audio to: {output_path}")
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Failed to process audio file: {str(e)}")
            raise
            
    def _process_audio(self, data: np.ndarray) -> np.ndarray:
        """Apply Stormtrooper effects to audio data.
        
        Args:
            data: Input audio data
            
        Returns:
            Processed audio data
        """
        # Normalize input
        data = data / np.max(np.abs(data))
        
        # Apply Filter Curve EQ
        data = self._apply_filter_curve_eq(data)
        
        # Apply helmet resonance
        data = self._apply_helmet_resonance(data)
        
        # Apply radio modulation
        data = self._apply_radio_modulation(data)
        
        # Add radio effects
        data = self._add_radio_effects(data)
        
        # Apply final output gain boost
        output_gain = 10 ** (self.params.output_gain_db / 20)  # Convert dB to linear gain
        data = data * output_gain
        
        # Final normalization and clipping
        data = data / np.max(np.abs(data))
        data = np.clip(data, -1.0, 1.0)
        
        return data
        
    def _apply_filter_curve_eq(self, data: np.ndarray) -> np.ndarray:
        """Apply Filter Curve EQ with mid-frequency boost.
        
        Args:
            data: Input audio data
            
        Returns:
            Filtered audio data with mid boost
        """
        nyquist = self.sample_rate / 2
        
        # Design bandpass filter
        low = self.params.highpass_freq / nyquist
        high = self.params.lowpass_freq / nyquist
        b, a = signal.butter(self.params.filter_order, [low, high], btype='band')
        
        # Apply bandpass filter
        filtered = signal.filtfilt(b, a, data)
        
        # Apply mid-frequency boost
        boost_factor = 10 ** (self.params.mid_boost_db / 20)  # Convert dB to linear gain
        filtered *= boost_factor
        
        return filtered
        
    def _apply_helmet_resonance(self, data: np.ndarray) -> np.ndarray:
        """Apply helmet resonance using two resonant peaks.
        
        Args:
            data: Input audio data
            
        Returns:
            Audio data with helmet resonance
        """
        nyquist = self.sample_rate / 2
        result = data.copy()  # Ensure we start with an ndarray
        
        # Create resonant filters
        for freq in [self.params.resonance_freq1, self.params.resonance_freq2]:
            w0 = freq / nyquist
            Q = self.params.resonance_q
            gain = 10 ** (self.params.resonance_gain / 20)
            
            # Create resonant bandpass filter
            b, a = signal.iirpeak(w0, Q)
            filtered = signal.lfilter(b, a, result)
            result = np.array(filtered) * gain  # Ensure ndarray type
            
        return result
        
    def _apply_radio_modulation(self, data: np.ndarray) -> np.ndarray:
        """Apply amplitude modulation for radio effect.
        
        Args:
            data: Input audio data
            
        Returns:
            Modulated audio data
        """
        # Create modulation signal
        t = np.arange(len(data)) / self.sample_rate
        mod = 1.0 + self.params.mod_depth * np.sin(2 * np.pi * self.params.mod_freq * t)
        
        # Apply modulation
        return data * mod
        
    def _add_radio_effects(self, data: np.ndarray) -> np.ndarray:
        """Add radio static and mic click effects at start and end.
        
        Args:
            data: Input audio data
            
        Returns:
            Audio data with radio effects
        """
        # Get urgency-based parameters
        urgency_params = self._get_urgency_params()
        
        # Calculate random static duration and samples for effects
        static_duration = random.uniform(
            self.params.static_duration_min,
            self.params.static_duration_max
        )
        static_samples = int(static_duration * self.sample_rate)
        click_samples = int(self.params.click_duration * self.sample_rate)
        
        # Generate start mic click with urgency-based volume - ensure minimum volume
        start_click_volume = max(
            self.params.click_volume * 0.8,  # Minimum 80% of base volume
            self.params.click_volume * (
                1 + random.uniform(
                    -self.params.click_variation,
                    self.params.click_variation
                )
            )
        )
        start_click_freq = self.params.click_freq * (1 + random.uniform(-self.params.click_variation, self.params.click_variation))
        t = np.linspace(0, self.params.click_duration, click_samples)
        # Sharper attack, slower decay for more prominent click
        envelope = np.exp(-t / (self.params.click_duration * 0.3))  # Slower decay
        start_click = start_click_volume * np.sin(2 * np.pi * start_click_freq * t) * envelope
        
        # Generate end mic click with different variation but same loud characteristics
        end_click_volume = max(
            self.params.click_volume * 0.8,  # Minimum 80% of base volume
            self.params.click_volume * (
                1 + random.uniform(
                    -self.params.click_variation,
                    self.params.click_variation
                )
            )
        )
        end_click_freq = self.params.click_freq * (1 + random.uniform(-self.params.click_variation, self.params.click_variation))
        end_click = end_click_volume * np.sin(2 * np.pi * end_click_freq * t) * envelope
        
        # Generate aggressive static with volume ramp
        static_volume = self.params.static_volume * (
            1 + random.uniform(
                -self.params.static_variation,
                self.params.static_variation
            )
        )
        
        # Create base static
        static = np.random.normal(0, 1.0, static_samples)
        
        # Apply bandpass filter to make static more harsh
        nyquist = self.sample_rate / 2
        static_low = 1000 / nyquist  # 1000 Hz highpass
        static_high = 4000 / nyquist # 4000 Hz lowpass
        b, a = signal.butter(2, [static_low, static_high], btype='band')
        static = signal.filtfilt(b, a, static)
        
        # Create volume ramp
        ramp_samples = int(static_samples * self.params.static_ramp_percent)
        ramp = np.linspace(0.3, 1.0, ramp_samples)  # Start at 30% volume
        
        # Apply ramp to latter portion of static
        static_with_ramp = static * static_volume
        static_with_ramp[-ramp_samples:] *= ramp
        
        # Create output buffer with space for effects
        total_length = click_samples + len(data) + click_samples + static_samples
        result = np.zeros(total_length)
        
        # Add effects in sequence
        result[:click_samples] = start_click                          # Start click
        result[click_samples:click_samples + len(data)] = data       # Main audio
        pos = click_samples + len(data)
        result[pos:pos + click_samples] = end_click                  # End click
        result[pos + click_samples:] = static_with_ramp             # Ramped static at the end
        
        return result 