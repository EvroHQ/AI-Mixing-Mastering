"""
Audio Analyzer - Loudness Analysis
Measures LUFS, LRA, True Peak, and Crest Factor
"""

import numpy as np
import pyloudnorm as pyln
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class LoudnessAnalyzer:
    """Loudness analysis for audio signals"""
    
    def __init__(self, sample_rate: int = 48000):
        """
        Initialize loudness analyzer
        
        Args:
            sample_rate: Audio sample rate
        """
        self.sample_rate = sample_rate
        self.meter = pyln.Meter(sample_rate)
        
    def analyze(self, audio: np.ndarray) -> Dict:
        """
        Perform loudness analysis on audio
        
        Args:
            audio: Audio signal (mono or stereo)
            
        Returns:
            Dictionary with loudness metrics
        """
        logger.info("Performing loudness analysis...")
        
        # Ensure audio is 2D (channels x samples)
        if audio.ndim == 1:
            audio = audio.reshape(1, -1)
        
        # Transpose to (samples x channels) for pyloudnorm
        audio_t = audio.T
        
        metrics = {}
        
        # Integrated loudness (LUFS)
        try:
            loudness = self.meter.integrated_loudness(audio_t)
            metrics['lufs_integrated'] = float(loudness)
        except Exception as e:
            logger.warning(f"Could not measure LUFS: {e}")
            metrics['lufs_integrated'] = -70.0  # Very quiet
        
        # Loudness range (LRA)
        try:
            lra = self._calculate_lra(audio_t)
            metrics['lra'] = float(lra)
        except Exception as e:
            logger.warning(f"Could not measure LRA: {e}")
            metrics['lra'] = 0.0
        
        # True peak
        true_peak = self._calculate_true_peak(audio)
        metrics['true_peak_dbTP'] = float(true_peak)
        
        # Peak level
        peak = np.max(np.abs(audio))
        metrics['peak_dbFS'] = float(20 * np.log10(peak + 1e-10))
        
        # RMS level
        rms = np.sqrt(np.mean(audio ** 2))
        metrics['rms_dbFS'] = float(20 * np.log10(rms + 1e-10))
        
        # Crest factor
        crest_factor = peak / (rms + 1e-10)
        metrics['crest_factor'] = float(crest_factor)
        metrics['crest_factor_db'] = float(20 * np.log10(crest_factor + 1e-10))
        
        # Dynamic range (difference between peak and RMS)
        metrics['dynamic_range_db'] = metrics['peak_dbFS'] - metrics['rms_dbFS']
        
        logger.info(f"Loudness analysis complete: LUFS={metrics['lufs_integrated']:.1f}, "
                   f"TP={metrics['true_peak_dbTP']:.1f} dBTP")
        
        return metrics
    
    def _calculate_lra(self, audio: np.ndarray) -> float:
        """
        Calculate Loudness Range (LRA)
        
        Args:
            audio: Audio signal (samples x channels)
            
        Returns:
            LRA in LU
        """
        # Use 3-second blocks
        block_size = int(3.0 * self.sample_rate)
        hop_size = int(0.1 * self.sample_rate)  # 100ms hop
        
        loudness_blocks = []
        
        for i in range(0, len(audio) - block_size, hop_size):
            block = audio[i:i + block_size]
            try:
                block_loudness = self.meter.integrated_loudness(block)
                if block_loudness > -70:  # Ignore very quiet blocks
                    loudness_blocks.append(block_loudness)
            except:
                pass
        
        if len(loudness_blocks) < 2:
            return 0.0
        
        # LRA is difference between 95th and 10th percentile
        loudness_blocks = np.array(loudness_blocks)
        lra = np.percentile(loudness_blocks, 95) - np.percentile(loudness_blocks, 10)
        
        return max(0.0, lra)
    
    def _calculate_true_peak(self, audio: np.ndarray) -> float:
        """
        Calculate True Peak level
        
        Args:
            audio: Audio signal
            
        Returns:
            True peak in dBTP
        """
        # Oversample by 4x for true peak detection
        from scipy import signal
        
        if audio.ndim == 1:
            audio = audio.reshape(1, -1)
        
        max_peak = 0.0
        
        for channel in audio:
            # Upsample
            upsampled = signal.resample(channel, len(channel) * 4)
            
            # Find peak
            peak = np.max(np.abs(upsampled))
            max_peak = max(max_peak, peak)
        
        # Convert to dBTP
        true_peak_dbTP = 20 * np.log10(max_peak + 1e-10)
        
        return true_peak_dbTP
    
    def normalize_to_lufs(
        self, 
        audio: np.ndarray, 
        target_lufs: float
    ) -> np.ndarray:
        """
        Normalize audio to target LUFS
        
        Args:
            audio: Audio signal
            target_lufs: Target LUFS level
            
        Returns:
            Normalized audio
        """
        # Measure current loudness
        if audio.ndim == 1:
            audio_t = audio.reshape(-1, 1)
        else:
            audio_t = audio.T
        
        try:
            current_lufs = self.meter.integrated_loudness(audio_t)
        except:
            logger.warning("Could not measure LUFS for normalization")
            return audio
        
        # Calculate gain needed
        gain_db = target_lufs - current_lufs
        gain_linear = 10 ** (gain_db / 20)
        
        # Apply gain
        normalized = audio * gain_linear
        
        # Check for clipping
        peak = np.max(np.abs(normalized))
        if peak > 0.99:
            # Reduce gain to avoid clipping
            safety_gain = 0.99 / peak
            normalized = normalized * safety_gain
            logger.warning(f"Reduced gain to avoid clipping (peak={peak:.2f})")
        
        logger.info(f"Normalized from {current_lufs:.1f} to {target_lufs:.1f} LUFS "
                   f"(gain={gain_db:.1f} dB)")
        
        return normalized
    
    def check_safety_limits(
        self, 
        metrics: Dict,
        max_true_peak: float = -1.0,
        min_crest_factor: float = 3.0
    ) -> Dict[str, bool]:
        """
        Check if audio meets safety limits
        
        Args:
            metrics: Loudness metrics dictionary
            max_true_peak: Maximum allowed true peak (dBTP)
            min_crest_factor: Minimum crest factor
            
        Returns:
            Dictionary of safety check results
        """
        checks = {}
        
        # True peak check
        checks['true_peak_safe'] = metrics['true_peak_dbTP'] <= max_true_peak
        
        # Crest factor check (avoid over-compression)
        checks['crest_factor_safe'] = metrics['crest_factor'] >= min_crest_factor
        
        # Overall safety
        checks['all_safe'] = all(checks.values())
        
        if not checks['all_safe']:
            logger.warning(f"Safety check failed: {checks}")
        
        return checks
