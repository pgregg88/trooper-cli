"""Audio processing and effects."""

from .effects import StormtrooperEffect, EffectParams
from .polly import PollyClient
from .utils import generate_filename
from .player import AudioPlayer

class AudioError(Exception):
    """Base exception for audio processing errors."""

__all__ = [
    'StormtrooperEffect',
    'EffectParams',
    'PollyClient',
    'generate_filename',
    'AudioError',
    'AudioPlayer',
] 