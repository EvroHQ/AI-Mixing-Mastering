"""
Professional Limiter - SIMPLE VERSION (No Oversampling)
Prevents vibrato artifacts
"""

import numpy as np
import logging

logger = logging.getLogger(__name__)


class ProLimiter:
    """Professional limiter WITHOUT oversampling to avoid vibrato"""
    
    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate
    
    def process(
        self,
        audio: np.ndarray,
        ceiling_db: float = -0.3,
        threshold_db: float = -2.0,
        release_ms: float = 150.0,  # Increased from 50ms to prevent pumping
        lookahead_ms: float = 5.0
    ) -> np.ndarray:
        """Apply brick-wall limiting WITHOUT oversampling"""
        
        logger.info(f"Pro Limiter (simple): ceiling={ceiling_db}dB")
        
        # Ensure stereo
        if audio.ndim == 1:
            audio = np.stack([audio, audio])
            was_mono = True
        else:
            was_mono = False
        
        # Convert dB to linear
        ceiling_linear = 10 ** (ceiling_db / 20)
        threshold_linear = 10 ** (threshold_db / 20)
        
        # Lookahead buffer
        lookahead_samples = int(lookahead_ms * self.sample_rate / 1000)
        buffered = np.pad(audio, ((0, 0), (lookahead_samples, 0)), mode='edge')
        
        # Calculate gain reduction
        gain_reduction = self._calculate_gain_reduction(
            buffered,
            threshold_linear,
            ceiling_linear,
            release_ms
        )
        
        # Apply gain reduction
        limited = buffered * gain_reduction
        
        # Remove lookahead buffer
        limited = limited[:, lookahead_samples:]
        
        # Final safety clipper
        output = np.clip(limited, -ceiling_linear, ceiling_linear)
        
        # Return to original shape
        if was_mono:
            output = np.mean(output, axis=0)
        
        gr_db = -20 * np.log10(np.min(gain_reduction) + 1e-10)
        logger.info(f"Pro Limiter: Max GR = {gr_db:.1f} dB")
        
        return output
    
    def _calculate_gain_reduction(
        self,
        audio: np.ndarray,
        threshold: float,
        ceiling: float,
        release_ms: float
    ) -> np.ndarray:
        """Calculate gain reduction envelope"""
        
        # Peak envelope (max of both channels)
        peak_envelope = np.max(np.abs(audio), axis=0)
        
        # Required gain reduction
        gain_reduction = np.ones_like(peak_envelope)
        mask = peak_envelope > threshold
        gain_reduction[mask] = ceiling / (peak_envelope[mask] + 1e-10)
        
        # Smooth release
        release_samples = int(release_ms * self.sample_rate / 1000)
        release_coef = np.exp(-1.0 / release_samples)
        
        # Instant attack, smooth release
        smoothed = np.zeros_like(gain_reduction)
        smoothed[0] = gain_reduction[0]
        
        for i in range(1, len(gain_reduction)):
            if gain_reduction[i] < smoothed[i-1]:
                smoothed[i] = gain_reduction[i]  # Attack
            else:
                smoothed[i] = release_coef * smoothed[i-1] + (1 - release_coef) * gain_reduction[i]  # Release
        
        # Broadcast to stereo
        smoothed = np.tile(smoothed, (audio.shape[0], 1))
        
        return smoothed
    
    def multi_stage_limit(
        self,
        audio: np.ndarray,
        ceiling_db: float = -0.3,
        stages: int = 3,
        release_ms: float = 150.0  # BPM-synced!
    ) -> np.ndarray:
        """Multi-stage limiting for transparency"""
        
        logger.info(f"Multi-stage limiting: {stages} stages")
        
        stage_ceilings = np.linspace(-6.0, ceiling_db, stages)
        output = audio.copy()
        
        for i, stage_ceiling in enumerate(stage_ceilings):
            threshold = stage_ceiling - 3.0
            
            output = self.process(
                output,
                ceiling_db=stage_ceiling,
                threshold_db=threshold,
                release_ms=release_ms / (i + 1),  # Use BPM-synced release
                lookahead_ms=5.0
            )
            
            logger.info(f"  Stage {i+1}/{stages}: ceiling={stage_ceiling:.1f}dB")
        
        return output
