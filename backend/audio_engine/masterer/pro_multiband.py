"""
Professional Multi-Band Compressor
Studio-grade frequency-specific dynamics control
"""

import numpy as np
from scipy import signal
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ProMultibandCompressor:
    """
    Professional multi-band compressor with:
    - Linear-phase crossovers
    - Independent band processing
    - Automatic makeup gain
    - Parallel compression per band
    """
    
    def __init__(self, sample_rate: int = 48000):
        """
        Initialize multi-band compressor
        
        Args:
            sample_rate: Audio sample rate
        """
        self.sample_rate = sample_rate
    
    def process(
        self,
        audio: np.ndarray,
        crossovers: List[float] = [250, 2000, 6000],
        thresholds: List[float] = [-20, -18, -16, -14],
        ratios: List[float] = [4.0, 3.5, 3.0, 2.5],
        attacks: List[float] = [15, 10, 5, 3],
        releases: List[float] = [120, 100, 80, 60],
        auto_makeup: bool = True,
        parallel_mix: float = 0.0
    ) -> Dict:
        """
        Apply multi-band compression
        
        Args:
            audio: Input audio
            crossovers: Crossover frequencies
            thresholds: Threshold for each band (dB)
            ratios: Compression ratio for each band
            attacks: Attack time for each band (ms)
            releases: Release time for each band (ms)
            auto_makeup: Enable automatic makeup gain
            parallel_mix: Parallel compression mix (0-1)
            
        Returns:
            Dictionary with processed audio and metrics
        """
        logger.info(f"Multi-band compression: {len(crossovers)+1} bands")
        
        # Ensure mono for processing
        if audio.ndim > 1:
            audio_mono = np.mean(audio, axis=0)
            is_stereo = True
        else:
            audio_mono = audio
            is_stereo = False
        
        # Split into bands
        bands = self._split_bands_linear_phase(audio_mono, crossovers)
        
        # Process each band
        compressed_bands = []
        band_metrics = []
        
        for i, band in enumerate(bands):
            # Compress band
            compressed, metrics = self._compress_band(
                band,
                threshold_db=thresholds[i],
                ratio=ratios[i],
                attack_ms=attacks[i],
                release_ms=releases[i],
                auto_makeup=auto_makeup
            )
            
            compressed_bands.append(compressed)
            band_metrics.append(metrics)
            
            logger.info(f"  Band {i+1}: GR={metrics['max_gr_db']:.1f}dB, "
                       f"makeup={metrics['makeup_gain_db']:.1f}dB")
        
        # Sum bands
        output = sum(compressed_bands)
        
        # Parallel compression
        if parallel_mix > 0:
            output = (1 - parallel_mix) * audio_mono + parallel_mix * output
            logger.info(f"  Parallel mix: {parallel_mix*100:.0f}%")
        
        # Match original shape
        if is_stereo:
            output = np.tile(output, (audio.shape[0], 1))
        
        return {
            'audio': output,
            'band_metrics': band_metrics,
            'total_gr_db': max(m['max_gr_db'] for m in band_metrics)
        }
    
    def _split_bands_linear_phase(
        self,
        audio: np.ndarray,
        crossovers: List[float]
    ) -> List[np.ndarray]:
        """
        Split audio into bands using linear-phase filters
        
        Args:
            audio: Input audio (mono)
            crossovers: Crossover frequencies
            
        Returns:
            List of band signals
        """
        bands = []
        
        # Use FIR filters for linear phase
        fir_length = 1025  # Must be odd for high-pass filters
        
        # Low band
        low_fir = signal.firwin(fir_length, crossovers[0], fs=self.sample_rate)
        low_band = signal.filtfilt(low_fir, 1.0, audio)
        bands.append(low_band)
        
        # Mid bands
        for i in range(len(crossovers) - 1):
            band_fir = signal.firwin(
                fir_length,
                [crossovers[i], crossovers[i + 1]],
                pass_zero=False,
                fs=self.sample_rate
            )
            mid_band = signal.filtfilt(band_fir, 1.0, audio)
            bands.append(mid_band)
        
        # High band
        high_fir = signal.firwin(
            fir_length,
            crossovers[-1],
            pass_zero=False,
            fs=self.sample_rate
        )
        high_band = signal.filtfilt(high_fir, 1.0, audio)
        bands.append(high_band)
        
        return bands
    
    def _compress_band(
        self,
        audio: np.ndarray,
        threshold_db: float,
        ratio: float,
        attack_ms: float,
        release_ms: float,
        auto_makeup: bool
    ) -> tuple:
        """
        Compress a single frequency band
        
        Args:
            audio: Band audio
            threshold_db: Threshold in dB
            ratio: Compression ratio
            attack_ms: Attack time
            release_ms: Release time
            auto_makeup: Enable auto makeup gain
            
        Returns:
            Tuple of (compressed audio, metrics)
        """
        # Convert threshold to linear
        threshold_linear = 10 ** (threshold_db / 20)
        
        # Calculate envelope
        envelope = self._calculate_envelope(audio, attack_ms, release_ms)
        
        # Calculate gain reduction
        gain_reduction = np.ones_like(envelope)
        mask = envelope > threshold_linear
        
        # Apply compression curve
        excess = envelope[mask] / threshold_linear
        gain_reduction[mask] = 1.0 / (1.0 + (excess - 1.0) * (1.0 - 1.0/ratio))
        
        # Apply gain reduction
        compressed = audio * gain_reduction
        
        # Calculate metrics
        max_gr_db = -20 * np.log10(np.min(gain_reduction) + 1e-10)
        
        # Auto makeup gain
        makeup_gain_db = 0.0
        if auto_makeup:
            # Calculate makeup based on average gain reduction
            avg_gr = np.mean(gain_reduction)
            makeup_gain_db = -20 * np.log10(avg_gr + 1e-10) * 0.7  # 70% compensation
            makeup_linear = 10 ** (makeup_gain_db / 20)
            compressed = compressed * makeup_linear
        
        metrics = {
            'max_gr_db': max_gr_db,
            'makeup_gain_db': makeup_gain_db,
            'avg_gr_db': -20 * np.log10(np.mean(gain_reduction) + 1e-10)
        }
        
        return compressed, metrics
    
    def _calculate_envelope(
        self,
        audio: np.ndarray,
        attack_ms: float,
        release_ms: float
    ) -> np.ndarray:
        """
        Calculate RMS envelope with attack/release
        
        Args:
            audio: Input audio
            attack_ms: Attack time
            release_ms: Release time
            
        Returns:
            Envelope
        """
        # RMS calculation
        window_size = int(10 * self.sample_rate / 1000)  # 10ms window
        rms = np.sqrt(np.convolve(audio**2, np.ones(window_size)/window_size, mode='same'))
        
        # Attack/release smoothing
        attack_samples = int(attack_ms * self.sample_rate / 1000)
        release_samples = int(release_ms * self.sample_rate / 1000)
        
        envelope = np.zeros_like(rms)
        envelope[0] = rms[0]
        
        for i in range(1, len(rms)):
            if rms[i] > envelope[i-1]:
                # Attack
                alpha = 1.0 - np.exp(-1.0 / max(attack_samples, 1))
            else:
                # Release
                alpha = 1.0 - np.exp(-1.0 / max(release_samples, 1))
            
            envelope[i] = alpha * rms[i] + (1 - alpha) * envelope[i-1]
        
        return envelope
    
    def studio_presets(self, preset: str) -> Dict:
        """
        Get studio-grade preset parameters
        
        Args:
            preset: Preset name
            
        Returns:
            Dictionary of parameters
        """
        presets = {
            'mastering_gentle': {
                'crossovers': [250, 2000, 6000],
                'thresholds': [-18, -16, -14, -12],
                'ratios': [2.5, 2.0, 2.0, 1.8],
                'attacks': [20, 15, 10, 5],
                'releases': [150, 120, 100, 80],
                'parallel_mix': 0.0
            },
            'mastering_balanced': {
                'crossovers': [250, 2000, 6000],
                'thresholds': [-16, -14, -12, -10],
                'ratios': [3.0, 2.5, 2.5, 2.0],
                'attacks': [15, 10, 8, 5],
                'releases': [120, 100, 80, 60],
                'parallel_mix': 0.0
            },
            'mastering_aggressive': {
                'crossovers': [300, 2500, 5000],
                'thresholds': [-14, -12, -10, -8],
                'ratios': [4.0, 3.5, 3.0, 2.5],
                'attacks': [10, 8, 5, 3],
                'releases': [100, 80, 60, 50],
                'parallel_mix': 0.15
            },
            'mix_glue': {
                'crossovers': [200, 2000, 8000],
                'thresholds': [-20, -18, -16, -14],
                'ratios': [3.0, 2.5, 2.5, 2.0],
                'attacks': [25, 20, 15, 10],
                'releases': [200, 150, 120, 100],
                'parallel_mix': 0.3
            },
            'punchy': {
                'crossovers': [150, 1500, 5000],
                'thresholds': [-18, -16, -14, -12],
                'ratios': [4.0, 3.0, 2.5, 2.0],
                'attacks': [30, 15, 8, 5],
                'releases': [100, 80, 60, 50],
                'parallel_mix': 0.2
            }
        }
        
        return presets.get(preset, presets['mastering_balanced'])
