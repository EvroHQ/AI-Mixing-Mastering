"""
Stem Processor - Professional Version with ROEX-style Processing
Based on industry-standard audio effects processing
"""

import numpy as np
from typing import Dict, List, Optional
import logging

from .effects import (
    StudioCompressor,
    StudioEQ,
    StudioDeesser,
    StereoProcessor
)
from .adaptive_processor import AdaptiveProcessor
from ..presets.instrument_presets import get_instrument_preset, get_panning_angle

logger = logging.getLogger(__name__)


class StemProcessor:
    """Processes individual stems with intelligent effect chains based on ROEX standards"""
    
    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate
        self.compressor = StudioCompressor(sample_rate)
        self.eq = StudioEQ(sample_rate)
        self.deesser = StudioDeesser(sample_rate)
        self.stereo = StereoProcessor(sample_rate)
        self.adaptive = AdaptiveProcessor(sample_rate)
    
    def convert_roex_eq_to_bands(self, eq_settings: Dict) -> List[Dict]:
        """Convert ROEX 6-band EQ format to our internal format"""
        bands = []
        for band_key in ['band_1', 'band_2', 'band_3', 'band_4', 'band_5', 'band_6']:
            if band_key in eq_settings:
                band = eq_settings[band_key]
                bands.append({
                    'type': 'peaking',
                    'frequency': band['centre_freq'],
                    'gain': band['gain'],
                    'q': band['q']
                })
        return bands
    
    def process(
        self,
        audio: np.ndarray,
        stem_role: str,
        masking_recommendations: Optional[List[Dict]] = None,
        tempo_bpm: Optional[float] = None,
        mix_settings: Optional[Dict] = None,
        genre: str = 'electronic',
        track_index: int = 0
    ) -> Dict:
        """Process stem with professional ROEX-style effect chain"""
        
        logger.info(f"Processing {stem_role} stem with ROEX-style processing...")
        
        # Get professional instrument preset (ROEX-based)
        preset = get_instrument_preset(stem_role)
        logger.info(f"  Using preset: {preset['name']}")
        
        # Merge with adaptive analysis
        adaptive_settings = self.adaptive.analyze_and_process(audio, stem_role)
        
        # Override with custom mix settings if provided
        if mix_settings:
            preset.update(mix_settings)
        
        processed = audio.copy()
        processing_log = []
        
        # 1. Apply gain adjustment
        gain_db = preset.get('gainDb', 0)
        if gain_db != 0:
            gain_linear = 10 ** (gain_db / 20)
            processed = processed * gain_linear
            processing_log.append(f"Gain: {gain_db:+.1f}dB")
        
        # 2. High-pass filter (remove rumble)
        highpass_freq = preset.get('highpass_freq', adaptive_settings.get('highpass_freq'))
        if highpass_freq and highpass_freq > 0:
            processed = self.eq.process(processed, [{
                'type': 'highpass',
                'frequency': highpass_freq
            }])
            processing_log.append(f"HPF: {highpass_freq}Hz")
        
        # 3. De-esser for vocals
        if stem_role in ['vocal', 'lead_vocal', 'backing_vocal', 'vox']:
            if preset.get('deess', True):
                processed = self.deesser.adaptive_deess(processed)
                processing_log.append("De-esser")
        
        # 4. 6-Band Parametric EQ (ROEX-style)
        if preset.get('eq_settings'):
            eq_bands = self.convert_roex_eq_to_bands(preset['eq_settings'])
            
            # Apply conservative gain scaling to prevent over-processing
            for band in eq_bands:
                band['gain'] = band['gain'] * 0.6  # 60% of prescribed gain
            
            processed = self.eq.process(processed, eq_bands)
            processing_log.append(f"EQ: 6-band parametric")
        
        # 5. Compression with ROEX-style settings
        if preset.get('compression_settings'):
            comp = preset['compression_settings']
            
            # Calculate BPM-synced release if tempo available
            if tempo_bpm and tempo_bpm > 0:
                beat_duration_ms = (60.0 / tempo_bpm) * 1000
                # Use preset release as base, blend with beat-synced value
                base_release = comp.get('release_ms', 100)
                synced_release = beat_duration_ms
                release_ms = (base_release * 0.6) + (synced_release * 0.4)
                logger.info(f"  BPM-synced release: {release_ms:.0f}ms (tempo={tempo_bpm})")
            else:
                release_ms = comp.get('release_ms', 100)
            
            processed = self.compressor.process(
                processed,
                threshold_db=comp.get('threshold', -20),
                ratio=comp.get('ratio', 3),
                attack_ms=comp.get('attack_ms', 15),
                release_ms=release_ms,
                makeup_gain_db=0
            )
            processing_log.append(f"Comp: {comp.get('ratio')}:1")
        
        # 6. Stereo Width
        if audio.ndim > 1:
            stereo_width = preset.get('stereo_width', 100)
            if stereo_width != 100:
                # Clamp to safe range (80-150%)
                stereo_width = max(80, min(stereo_width, 150))
                processed = self.stereo.adjust_width(
                    processed,
                    width_percent=stereo_width,
                    safe_bass=True,
                    bass_mono_freq=150.0
                )
                processing_log.append(f"Width: {stereo_width}%")
        
        # 7. Panning (just return the angle, applied during mixing)
        panning_angle = preset.get('panning_angle', 0)
        if panning_angle == 0 and genre:
            panning_angle = get_panning_angle(stem_role, genre, track_index)
        
        logger.info(f"{stem_role}: {', '.join(processing_log)}")
        
        return {
            'audio': processed,
            'processing_log': processing_log,
            'settings_used': preset,
            'panning_angle': panning_angle,
            'gain_db': gain_db
        }
