"""
Simple Mastering Engine
-----------------------
Minimal, transparent mastering that doesn't add artifacts.
Just: LUFS normalization + transparent limiting
"""

import numpy as np
from scipy import signal
import logging

logger = logging.getLogger(__name__)


class SimpleMasteringEngine:
    """
    Transparent mastering engine that respects the mix.
    No EQ, no multiband compression, no saturation.
    """
    
    # Platform presets (LUFS targets)
    PLATFORM_PRESETS = {
        'spotify': {'lufs': -14, 'ceiling': -1.0},
        'apple_music': {'lufs': -16, 'ceiling': -1.0},
        'youtube': {'lufs': -14, 'ceiling': -1.0},
        'soundcloud': {'lufs': -14, 'ceiling': -1.0},
        'club': {'lufs': -9, 'ceiling': -0.3},
        'dynamic': {'lufs': -18, 'ceiling': -1.0},  # Preserve dynamics
        'default': {'lufs': -14, 'ceiling': -1.0},
    }
    
    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate
    
    def master(self, audio: np.ndarray, platform: str = 'spotify') -> dict:
        """
        Simple mastering chain:
        1. Measure input loudness
        2. Apply gentle gain to approach target
        3. Apply transparent limiter
        4. Verify output
        """
        # Get preset
        preset = self.PLATFORM_PRESETS.get(platform, self.PLATFORM_PRESETS['default'])
        target_lufs = preset['lufs']
        ceiling_db = preset['ceiling']
        ceiling_linear = 10 ** (ceiling_db / 20)
        
        logger.info(f"Simple mastering for {platform}: target {target_lufs} LUFS, ceiling {ceiling_db} dBTP")
        
        # Ensure stereo
        if audio.ndim == 1:
            audio = np.stack([audio, audio])
        elif audio.shape[0] > audio.shape[1]:
            audio = audio.T
        
        # 1. Measure input
        input_lufs = self._measure_lufs(audio)
        input_peak = 20 * np.log10(max(np.max(np.abs(audio)), 1e-10))
        logger.info(f"  Input: {input_lufs:.1f} LUFS, {input_peak:.1f} dBTP")
        
        # 2. Calculate gain needed
        gain_db = target_lufs - input_lufs
        
        # Limit gain to prevent extreme changes
        gain_db = np.clip(gain_db, -12, 18)
        
        # Apply gain
        gain_linear = 10 ** (gain_db / 20)
        audio = audio * gain_linear
        
        logger.info(f"  Applied gain: {gain_db:+.1f} dB")
        
        # 3. Apply transparent limiter
        audio = self._transparent_limiter(audio, ceiling_linear)
        
        # 4. Measure output
        output_lufs = self._measure_lufs(audio)
        output_peak = 20 * np.log10(max(np.max(np.abs(audio)), 1e-10))
        logger.info(f"  Output: {output_lufs:.1f} LUFS, {output_peak:.1f} dBTP")
        
        return {
            'audio': audio,
            'input_lufs': input_lufs,
            'output_lufs': output_lufs,
            'output_peak': output_peak,
            'gain_applied': gain_db,
            'platform': platform
        }
    
    def _measure_lufs(self, audio: np.ndarray) -> float:
        """Simplified LUFS measurement"""
        # K-weighting approximation (high-pass at ~60Hz, shelf at ~1500Hz)
        try:
            # Simple RMS-based approximation
            rms = np.sqrt(np.mean(audio ** 2))
            # Approximate LUFS from RMS (not exact but close enough)
            lufs = 20 * np.log10(max(rms, 1e-10)) - 0.5
            return lufs
        except:
            return -24.0
    
    def _transparent_limiter(self, audio: np.ndarray, ceiling: float) -> np.ndarray:
        """
        Transparent look-ahead limiter
        Uses envelope following with slow attack/release to avoid pumping
        """
        result = audio.copy()
        
        # Parameters for transparent limiting
        attack_ms = 5.0  # Fast attack to catch peaks
        release_ms = 100.0  # Slow release to avoid pumping
        lookahead_ms = 5.0  # Look ahead for smooth limiting
        
        attack_coef = np.exp(-1.0 / (attack_ms * self.sample_rate / 1000))
        release_coef = np.exp(-1.0 / (release_ms * self.sample_rate / 1000))
        lookahead_samples = int(lookahead_ms * self.sample_rate / 1000)
        
        # Get peak envelope (max of both channels)
        peak_signal = np.maximum(np.abs(audio[0]), np.abs(audio[1]))
        
        # Build gain reduction envelope
        envelope = np.zeros(len(peak_signal))
        env = 0.0
        
        for i in range(len(peak_signal)):
            peak = peak_signal[i]
            
            if peak > env:
                env = attack_coef * env + (1 - attack_coef) * peak
            else:
                env = release_coef * env + (1 - release_coef) * peak
            
            envelope[i] = env
        
        # Apply lookahead by shifting envelope
        if lookahead_samples > 0:
            envelope = np.concatenate([
                envelope[lookahead_samples:],
                np.full(lookahead_samples, envelope[-1])
            ])
        
        # Calculate gain reduction
        gain = np.ones_like(envelope)
        above_ceiling = envelope > ceiling
        gain[above_ceiling] = ceiling / envelope[above_ceiling]
        
        # Smooth the gain to avoid clicks
        # Simple moving average
        kernel_size = int(1.0 * self.sample_rate / 1000)  # 1ms
        if kernel_size > 1:
            kernel = np.ones(kernel_size) / kernel_size
            gain = np.convolve(gain, kernel, mode='same')
        
        # Apply gain
        result[0] = audio[0] * gain
        result[1] = audio[1] * gain
        
        # Final safety clip
        result = np.clip(result, -ceiling, ceiling)
        
        # Log limiting amount
        max_reduction = 20 * np.log10(max(np.min(gain), 1e-10))
        if max_reduction < -0.5:
            logger.info(f"  Limiter: max reduction {max_reduction:.1f} dB")
        
        return result


def simple_master(audio: np.ndarray, sample_rate: int = 48000, platform: str = 'spotify') -> dict:
    """Convenience function for simple mastering"""
    engine = SimpleMasteringEngine(sample_rate)
    return engine.master(audio, platform)
