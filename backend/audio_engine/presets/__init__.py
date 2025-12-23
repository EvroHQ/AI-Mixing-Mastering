"""
Audio Presets Module
Genre-specific and instrument-specific processing presets
"""

from .genre_presets import GenrePresets
from .instrument_presets import (
    INSTRUMENT_PRESETS,
    PANNING_STRATEGIES,
    FREQUENCY_RANGES,
    get_instrument_preset,
    get_panning_angle
)

__all__ = [
    'GenrePresets',
    'INSTRUMENT_PRESETS',
    'PANNING_STRATEGIES', 
    'FREQUENCY_RANGES',
    'get_instrument_preset',
    'get_panning_angle'
]
