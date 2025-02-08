"""Audio processing and effects."""

from .effects import EffectParams, StormtrooperEffect
from .errors import AudioError
from .player import AudioPlayer
from .polly import PollyClient
from .utils import generate_filename

__all__ = [
    'StormtrooperEffect',
    'EffectParams',
    'PollyClient',
    'generate_filename',
    'AudioError',
    'AudioPlayer',
] 