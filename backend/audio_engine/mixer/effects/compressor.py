"""
Studio-Quality Compressor
Uses Pedalboard for professional audio compression
"""

import numpy as np
from pedalboard import Compressor as PedalboardCompressor
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class StudioCompressor:
    """
    Professional-grade compressor with advanced features
    """
    
    def __init__(
        self,
        sample_rate: int = 48000
    ):
        """
        Initialize compressor
        
        Args:
            sample_rate: Audio sample rate
        """
        self.sample_rate = sample_rate
    
    def process(
        self,
        audio: np.ndarray,
        threshold_db: float = -20.0,
        ratio: float = 4.0,
        attack_ms: float = 5.0,
        release_ms: float = 100.0,
        knee_db: float = 6.0,
        makeup_gain_db: float = 0.0
    ) -> np.ndarray:
        """
        Apply compression to audio
        
        Args:
            audio: Input audio (mono or stereo)
            threshold_db: Compression threshold in dB
            ratio: Compression ratio (e.g., 4:1)
            attack_ms: Attack time in milliseconds
            release_ms: Release time in milliseconds
            knee_db: Knee width in dB (soft knee)
            makeup_gain_db: Makeup gain in dB
            
        Returns:
            Compressed audio
        """
        # Ensure audio is 2D
        if audio.ndim == 1:
            audio = audio.reshape(1, -1)
            was_mono = True
        else:
            was_mono = False
        
        # Create compressor
        compressor = PedalboardCompressor(
            threshold_db=threshold_db,
            ratio=ratio,
            attack_ms=attack_ms,
            release_ms=release_ms
        )
        
        # Process each channel
        compressed = np.zeros_like(audio)
        for i in range(audio.shape[0]):
            compressed[i] = compressor(
                audio[i].astype(np.float32),
                self.sample_rate
            )
        
        # Apply makeup gain
        if makeup_gain_db != 0:
            gain_linear = 10 ** (makeup_gain_db / 20)
            compressed = compressed * gain_linear
        
        # Return to original shape
        if was_mono:
            compressed = compressed.flatten()
        
        return compressed
    
    def parallel_compress(
        self,
        audio: np.ndarray,
        threshold_db: float = -25.0,
        ratio: float = 6.0,
        attack_ms: float = 1.0,
        release_ms: float = 50.0,
        mix: float = 0.3
    ) -> np.ndarray:
        """
        Apply parallel compression (New York compression)
        
        Args:
            audio: Input audio
            threshold_db: Compression threshold
            ratio: Compression ratio
            attack_ms: Attack time
            release_ms: Release time
            mix: Wet/dry mix (0-1)
            
        Returns:
            Parallel compressed audio
        """
        # Compress heavily
        compressed = self.process(
            audio,
            threshold_db=threshold_db,
            ratio=ratio,
            attack_ms=attack_ms,
            release_ms=release_ms,
            makeup_gain_db=10.0  # Heavy makeup gain
        )
        
        # Mix with dry signal
        output = (1 - mix) * audio + mix * compressed
        
        return output
    
    def multiband_compress(
        self,
        audio: np.ndarray,
        crossover_freqs: list = [250, 2000, 6000],
        thresholds: list = [-20, -18, -15, -12],
        ratios: list = [3.0, 4.0, 3.0, 2.0],
        attack_ms: list = [10, 5, 2, 1],
        release_ms: list = [100, 80, 60, 40]
    ) -> np.ndarray:
        """
        Apply multiband compression
        
        Args:
            audio: Input audio
            crossover_freqs: Crossover frequencies for bands
            thresholds: Threshold for each band
            ratios: Ratio for each band
            attack_ms: Attack time for each band
            release_ms: Release time for each band
            
        Returns:
            Multiband compressed audio
        """
        from scipy import signal
        
        # Ensure audio is mono for processing
        if audio.ndim > 1:
            audio_mono = np.mean(audio, axis=0)
        else:
            audio_mono = audio
        
        # Split into bands
        bands = self._split_bands(audio_mono, crossover_freqs)
        
        # Compress each band
        compressed_bands = []
        for i, band in enumerate(bands):
            compressed_band = self.process(
                band,
                threshold_db=thresholds[i],
                ratio=ratios[i],
                attack_ms=attack_ms[i],
                release_ms=release_ms[i]
            )
            compressed_bands.append(compressed_band)
        
        # Sum bands
        output = sum(compressed_bands)
        
        # Match original shape
        if audio.ndim > 1:
            output = np.tile(output, (audio.shape[0], 1))
        
        return output
    
    def _split_bands(
        self,
        audio: np.ndarray,
        crossover_freqs: list
    ) -> list:
        """
        Split audio into frequency bands
        
        Args:
            audio: Input audio (mono)
            crossover_freqs: Crossover frequencies
            
        Returns:
            List of band signals
        """
        from scipy import signal
        
        bands = []
        
        # Low band (below first crossover)
        sos = signal.butter(
            4,
            crossover_freqs[0],
            'low',
            fs=self.sample_rate,
            output='sos'
        )
        low_band = signal.sosfilt(sos, audio)
        bands.append(low_band)
        
        # Mid bands
        for i in range(len(crossover_freqs) - 1):
            sos = signal.butter(
                4,
                [crossover_freqs[i], crossover_freqs[i + 1]],
                'band',
                fs=self.sample_rate,
                output='sos'
            )
            mid_band = signal.sosfilt(sos, audio)
            bands.append(mid_band)
        
        # High band (above last crossover)
        sos = signal.butter(
            4,
            crossover_freqs[-1],
            'high',
            fs=self.sample_rate,
            output='sos'
        )
        high_band = signal.sosfilt(sos, audio)
        bands.append(high_band)
        
        return bands
    
    def sidechain_compress(
        self,
        audio: np.ndarray,
        sidechain: np.ndarray,
        threshold_db: float = -20.0,
        ratio: float = 10.0,
        attack_ms: float = 5.0,
        release_ms: float = 100.0,
        freq_range: Optional[tuple] = None
    ) -> np.ndarray:
        """
        Apply sidechain compression
        
        Args:
            audio: Audio to compress
            sidechain: Sidechain signal (e.g., kick for bass ducking)
            threshold_db: Threshold
            ratio: Ratio
            attack_ms: Attack time
            release_ms: Release time
            freq_range: Optional frequency range to filter sidechain (low, high)
            
        Returns:
            Sidechain compressed audio
        """
        # Filter sidechain if freq_range specified
        if freq_range is not None:
            from scipy import signal
            low, high = freq_range
            sos = signal.butter(
                4,
                [low, high],
                'band',
                fs=self.sample_rate,
                output='sos'
            )
            sidechain_filtered = signal.sosfilt(sos, sidechain)
        else:
            sidechain_filtered = sidechain
        
        # Calculate envelope of sidechain
        envelope = self._calculate_envelope(sidechain_filtered, attack_ms, release_ms)
        
        # Calculate gain reduction
        envelope_db = 20 * np.log10(np.abs(envelope) + 1e-10)
        
        # Apply threshold and ratio
        gain_reduction_db = np.zeros_like(envelope_db)
        mask = envelope_db > threshold_db
        gain_reduction_db[mask] = (envelope_db[mask] - threshold_db) * (1 - 1/ratio)
        
        # Convert to linear
        gain_reduction_linear = 10 ** (-gain_reduction_db / 20)
        
        # Apply to audio
        if audio.ndim == 1:
            output = audio * gain_reduction_linear
        else:
            output = audio * gain_reduction_linear.reshape(1, -1)
        
        return output
    
    def _calculate_envelope(
        self,
        audio: np.ndarray,
        attack_ms: float,
        release_ms: float
    ) -> np.ndarray:
        """
        Calculate envelope with attack/release
        
        Args:
            audio: Input audio
            attack_ms: Attack time
            release_ms: Release time
            
        Returns:
            Envelope
        """
        # Convert to samples
        attack_samples = int(attack_ms * self.sample_rate / 1000)
        release_samples = int(release_ms * self.sample_rate / 1000)
        
        # Rectify
        rectified = np.abs(audio)
        
        # Envelope follower
        envelope = np.zeros_like(rectified)
        envelope[0] = rectified[0]
        
        for i in range(1, len(rectified)):
            if rectified[i] > envelope[i-1]:
                # Attack
                alpha = 1.0 - np.exp(-1.0 / attack_samples)
            else:
                # Release
                alpha = 1.0 - np.exp(-1.0 / release_samples)
            
            envelope[i] = alpha * rectified[i] + (1 - alpha) * envelope[i-1]
        
        return envelope
