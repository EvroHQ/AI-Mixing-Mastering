"""Mixer effects module"""

from .compressor import StudioCompressor
from .eq import StudioEQ
from .deesser import StudioDeesser
from .reverb import StudioReverb, StudioDelay
from .stereo import StereoProcessor

__all__ = [
    'StudioCompressor',
    'StudioEQ',
    'StudioDeesser',
    'StudioReverb',
    'StudioDelay',
    'StereoProcessor'
]
