"""
Studio-Quality De-esser
Professional de-essing for vocal processing
"""

import numpy as np
from scipy import signal
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class StudioDeesser:
    """
    Professional de-esser for controlling sibilance in vocals
    """
    
    def __init__(self, sample_rate: int = 48000):
        """
        Initialize de-esser
        
        Args:
            sample_rate: Audio sample rate
        """
        self.sample_rate = sample_rate
    
    def process(
        self,
        audio: np.ndarray,
        frequency: float = 6000.0,
        threshold_db: float = -20.0,
        ratio: float = 4.0,
        bandwidth_hz: float = 2000.0,
        attack_ms: float = 1.0,
        release_ms: float = 50.0
    ) -> np.ndarray:
        """
        Apply de-essing to audio
        
        Args:
            audio: Input audio (typically vocal)
            frequency: Center frequency of sibilance (4-8 kHz typical)
            threshold_db: Threshold for de-essing
            ratio: Compression ratio for sibilance
            bandwidth_hz: Bandwidth of sibilance detection
            attack_ms: Attack time
            release_ms: Release time
            
        Returns:
            De-essed audio
        """
        logger.info(f"De-essing at {frequency} Hz...")
        
        # Ensure mono
        if audio.ndim > 1:
            audio_mono = np.mean(audio, axis=0)
        else:
            audio_mono = audio
        
        # Extract sibilance band
        sibilance_band = self._extract_band(
            audio_mono,
            frequency,
            bandwidth_hz
        )
        
        # Calculate sibilance envelope
        envelope = self._calculate_envelope(
            sibilance_band,
            attack_ms,
            release_ms
        )
        
        # Convert to dB
        envelope_db = 20 * np.log10(np.abs(envelope) + 1e-10)
        
        # Calculate gain reduction
        gain_reduction_db = np.zeros_like(envelope_db)
        mask = envelope_db > threshold_db
        
        # Apply ratio
        excess_db = envelope_db[mask] - threshold_db
        gain_reduction_db[mask] = excess_db * (1 - 1/ratio)
        
        # Smooth gain reduction
        gain_reduction_db = self._smooth_gain(gain_reduction_db)
        
        # Convert to linear
        gain_reduction_linear = 10 ** (-gain_reduction_db / 20)
        
        # Apply gain reduction only to sibilance band
        sibilance_reduced = sibilance_band * gain_reduction_linear
        
        # Subtract original sibilance and add reduced
        output = audio_mono - sibilance_band + sibilance_reduced
        
        # Match original shape
        if audio.ndim > 1:
            output = np.tile(output, (audio.shape[0], 1))
        
        logger.info(f"De-essing complete (avg reduction: {np.mean(gain_reduction_db):.1f} dB)")
        
        return output
    
    def multiband_deess(
        self,
        audio: np.ndarray,
        frequencies: list = [5000, 7000, 9000],
        thresholds_db: list = [-18, -20, -22],
        ratios: list = [4.0, 5.0, 6.0]
    ) -> np.ndarray:
        """
        Apply multi-band de-essing for more precise control
        
        Args:
            audio: Input audio
            frequencies: List of sibilance frequencies
            thresholds_db: Thresholds for each band
            ratios: Ratios for each band
            
        Returns:
            Multi-band de-essed audio
        """
        output = audio.copy()
        
        for freq, threshold, ratio in zip(frequencies, thresholds_db, ratios):
            output = self.process(
                output,
                frequency=freq,
                threshold_db=threshold,
                ratio=ratio
            )
        
        return output
    
    def adaptive_deess(
        self,
        audio: np.ndarray,
        auto_threshold: bool = True
    ) -> np.ndarray:
        """
        Apply adaptive de-essing with automatic parameter detection
        
        Args:
            audio: Input audio
            auto_threshold: Automatically detect threshold
            
        Returns:
            Adaptively de-essed audio
        """
        # Ensure mono
        if audio.ndim > 1:
            audio_mono = np.mean(audio, axis=0)
        else:
            audio_mono = audio
        
        # Detect sibilance frequency
        sibilance_freq = self._detect_sibilance_frequency(audio_mono)
        
        # Auto-detect threshold if requested
        if auto_threshold:
            threshold_db = self._auto_threshold(audio_mono, sibilance_freq)
        else:
            threshold_db = -20.0
        
        # Apply de-essing
        output = self.process(
            audio,
            frequency=sibilance_freq,
            threshold_db=threshold_db,
            ratio=4.0
        )
        
        return output
    
    def _extract_band(
        self,
        audio: np.ndarray,
        center_freq: float,
        bandwidth: float
    ) -> np.ndarray:
        """
        Extract frequency band
        
        Args:
            audio: Input audio
            center_freq: Center frequency
            bandwidth: Bandwidth
            
        Returns:
            Band-passed audio
        """
        low_freq = center_freq - bandwidth / 2
        high_freq = center_freq + bandwidth / 2
        
        # Design bandpass filter
        sos = signal.butter(
            4,
            [low_freq, high_freq],
            'band',
            fs=self.sample_rate,
            output='sos'
        )
        
        # Apply filter
        filtered = signal.sosfilt(sos, audio)
        
        return filtered
    
    def _calculate_envelope(
        self,
        audio: np.ndarray,
        attack_ms: float,
        release_ms: float
    ) -> np.ndarray:
        """
        Calculate envelope follower
        
        Args:
            audio: Input audio
            attack_ms: Attack time
            release_ms: Release time
            
        Returns:
            Envelope
        """
        attack_samples = int(attack_ms * self.sample_rate / 1000)
        release_samples = int(release_ms * self.sample_rate / 1000)
        
        # Rectify
        rectified = np.abs(audio)
        
        # Envelope follower
        envelope = np.zeros_like(rectified)
        envelope[0] = rectified[0]
        
        for i in range(1, len(rectified)):
            if rectified[i] > envelope[i-1]:
                alpha = 1.0 - np.exp(-1.0 / max(1, attack_samples))
            else:
                alpha = 1.0 - np.exp(-1.0 / max(1, release_samples))
            
            envelope[i] = alpha * rectified[i] + (1 - alpha) * envelope[i-1]
        
        return envelope
    
    def _smooth_gain(
        self,
        gain_db: np.ndarray,
        window_size: int = 100
    ) -> np.ndarray:
        """
        Smooth gain reduction curve
        
        Args:
            gain_db: Gain reduction in dB
            window_size: Smoothing window size
            
        Returns:
            Smoothed gain
        """
        from scipy.ndimage import gaussian_filter1d
        
        # Smooth with gaussian filter
        smoothed = gaussian_filter1d(
            gain_db,
            sigma=window_size / 4
        )
        
        return smoothed
    
    def _detect_sibilance_frequency(
        self,
        audio: np.ndarray
    ) -> float:
        """
        Detect dominant sibilance frequency
        
        Args:
            audio: Input audio
            
        Returns:
            Sibilance frequency in Hz
        """
        # Compute spectrum in sibilance range (4-10 kHz)
        stft = np.abs(np.fft.rfft(audio))
        freqs = np.fft.rfftfreq(len(audio), 1/self.sample_rate)
        
        # Focus on sibilance range
        mask = (freqs >= 4000) & (freqs <= 10000)
        sibilance_spectrum = stft[mask]
        sibilance_freqs = freqs[mask]
        
        # Find peak
        if len(sibilance_spectrum) > 0:
            peak_idx = np.argmax(sibilance_spectrum)
            sibilance_freq = sibilance_freqs[peak_idx]
        else:
            sibilance_freq = 6000.0  # Default
        
        logger.info(f"Detected sibilance frequency: {sibilance_freq:.0f} Hz")
        
        return float(sibilance_freq)
    
    def _auto_threshold(
        self,
        audio: np.ndarray,
        frequency: float
    ) -> float:
        """
        Automatically detect de-essing threshold
        
        Args:
            audio: Input audio
            frequency: Sibilance frequency
            
        Returns:
            Threshold in dB
        """
        # Extract sibilance band
        sibilance_band = self._extract_band(audio, frequency, 2000)
        
        # Calculate RMS
        rms = np.sqrt(np.mean(sibilance_band ** 2))
        rms_db = 20 * np.log10(rms + 1e-10)
        
        # Set threshold slightly below RMS
        threshold_db = rms_db - 6.0
        
        # Clamp to reasonable range
        threshold_db = np.clip(threshold_db, -30.0, -10.0)
        
        logger.info(f"Auto threshold: {threshold_db:.1f} dB")
        
        return float(threshold_db)
