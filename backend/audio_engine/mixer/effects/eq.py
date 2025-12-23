"""
Studio-Quality Equalizer
Professional EQ with linear-phase and dynamic options
"""

import numpy as np
from pedalboard import (
    HighpassFilter,
    LowpassFilter,
    PeakFilter,
    HighShelfFilter,
    LowShelfFilter
)
from scipy import signal
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class StudioEQ:
    """
    Professional-grade equalizer with multiple filter types
    """
    
    def __init__(self, sample_rate: int = 48000):
        """
        Initialize EQ
        
        Args:
            sample_rate: Audio sample rate
        """
        self.sample_rate = sample_rate
    
    def process(
        self,
        audio: np.ndarray,
        bands: List[Dict]
    ) -> np.ndarray:
        """
        Apply EQ with multiple bands
        
        Args:
            audio: Input audio
            bands: List of EQ band dictionaries with:
                - type: 'peak', 'low_shelf', 'high_shelf', 'highpass', 'lowpass'
                - frequency: Center/cutoff frequency in Hz
                - gain: Gain in dB (for peak/shelf)
                - q: Q factor (for peak)
                
        Returns:
            Equalized audio
        """
        # Ensure audio is 2D
        if audio.ndim == 1:
            audio = audio.reshape(1, -1)
            was_mono = True
        else:
            was_mono = False
        
        output = audio.copy()
        
        # Apply each band
        for band in bands:
            band_type = band.get('type', 'peak')
            frequency = band.get('frequency', 1000)
            gain = band.get('gain', 0.0)
            q = band.get('q', 1.0)
            
            # Skip if no gain
            if abs(gain) < 0.1 and band_type in ['peak', 'low_shelf', 'high_shelf']:
                continue
            
            # Process each channel
            for i in range(output.shape[0]):
                if band_type == 'peak':
                    filter_obj = PeakFilter(
                        cutoff_frequency_hz=frequency,
                        gain_db=gain,
                        q=q
                    )
                elif band_type == 'low_shelf':
                    filter_obj = LowShelfFilter(
                        cutoff_frequency_hz=frequency,
                        gain_db=gain,
                        q=q
                    )
                elif band_type == 'high_shelf':
                    filter_obj = HighShelfFilter(
                        cutoff_frequency_hz=frequency,
                        gain_db=gain,
                        q=q
                    )
                elif band_type == 'highpass':
                    filter_obj = HighpassFilter(
                        cutoff_frequency_hz=frequency
                    )
                elif band_type == 'lowpass':
                    filter_obj = LowpassFilter(
                        cutoff_frequency_hz=frequency
                    )
                else:
                    continue
                
                output[i] = filter_obj(
                    output[i].astype(np.float32),
                    self.sample_rate
                )
        
        # Return to original shape
        if was_mono:
            output = output.flatten()
        
        return output
    
    def linear_phase_eq(
        self,
        audio: np.ndarray,
        bands: List[Dict],
        fft_size: int = 8192
    ) -> np.ndarray:
        """
        Apply linear-phase EQ (zero phase distortion)
        
        Args:
            audio: Input audio
            bands: EQ bands
            fft_size: FFT size for processing
            
        Returns:
            Linear-phase equalized audio
        """
        # Ensure mono for processing
        if audio.ndim > 1:
            audio_mono = np.mean(audio, axis=0)
        else:
            audio_mono = audio
        
        # Create frequency response
        freqs = np.fft.rfftfreq(fft_size, 1/self.sample_rate)
        magnitude_response = np.ones(len(freqs))
        
        # Apply each band to frequency response
        for band in bands:
            band_type = band.get('type', 'peak')
            frequency = band.get('frequency', 1000)
            gain = band.get('gain', 0.0)
            q = band.get('q', 1.0)
            
            if band_type == 'peak':
                # Bell filter
                bandwidth = frequency / q
                for i, f in enumerate(freqs):
                    if f > 0:
                        # Gaussian-like response
                        response = gain * np.exp(
                            -((f - frequency) ** 2) / (2 * (bandwidth / 2) ** 2)
                        )
                        magnitude_response[i] *= 10 ** (response / 20)
            
            elif band_type == 'low_shelf':
                # Low shelf
                for i, f in enumerate(freqs):
                    if f < frequency:
                        magnitude_response[i] *= 10 ** (gain / 20)
                    else:
                        # Smooth transition
                        transition = np.exp(-(f - frequency) / (frequency / q))
                        magnitude_response[i] *= 10 ** (gain * transition / 20)
            
            elif band_type == 'high_shelf':
                # High shelf
                for i, f in enumerate(freqs):
                    if f > frequency:
                        magnitude_response[i] *= 10 ** (gain / 20)
                    else:
                        # Smooth transition
                        transition = np.exp(-(frequency - f) / (frequency / q))
                        magnitude_response[i] *= 10 ** (gain * transition / 20)
        
        # Apply via FFT convolution
        output = self._apply_frequency_response(
            audio_mono,
            magnitude_response,
            fft_size
        )
        
        # Match original shape
        if audio.ndim > 1:
            output = np.tile(output, (audio.shape[0], 1))
        
        return output
    
    def dynamic_eq(
        self,
        audio: np.ndarray,
        frequency: float,
        threshold_db: float = -20.0,
        max_gain_db: float = -6.0,
        q: float = 2.0,
        attack_ms: float = 10.0,
        release_ms: float = 100.0
    ) -> np.ndarray:
        """
        Apply dynamic EQ (frequency-specific compression)
        
        Args:
            audio: Input audio
            frequency: Target frequency
            threshold_db: Threshold for reduction
            max_gain_db: Maximum reduction
            q: Q factor
            attack_ms: Attack time
            release_ms: Release time
            
        Returns:
            Dynamic EQ processed audio
        """
        # Ensure mono
        if audio.ndim > 1:
            audio_mono = np.mean(audio, axis=0)
        else:
            audio_mono = audio
        
        # Extract target frequency band
        bandwidth = frequency / q
        sos = signal.butter(
            4,
            [frequency - bandwidth/2, frequency + bandwidth/2],
            'band',
            fs=self.sample_rate,
            output='sos'
        )
        band_signal = signal.sosfilt(sos, audio_mono)
        
        # Calculate envelope
        envelope = self._calculate_envelope(band_signal, attack_ms, release_ms)
        envelope_db = 20 * np.log10(np.abs(envelope) + 1e-10)
        
        # Calculate dynamic gain
        gain_db = np.zeros_like(envelope_db)
        mask = envelope_db > threshold_db
        
        # Linear reduction above threshold
        excess_db = envelope_db[mask] - threshold_db
        gain_db[mask] = np.clip(
            -excess_db * (max_gain_db / 20),  # Scale to max_gain
            max_gain_db,
            0
        )
        
        # Apply dynamic EQ
        dynamic_bands = [{
            'type': 'peak',
            'frequency': frequency,
            'gain': float(np.mean(gain_db)),  # Average gain
            'q': q
        }]
        
        output = self.process(audio, dynamic_bands)
        
        return output
    
    def masking_eq(
        self,
        audio: np.ndarray,
        masking_recommendations: List[Dict]
    ) -> np.ndarray:
        """
        Apply EQ based on masking analysis recommendations
        
        Args:
            audio: Input audio
            masking_recommendations: List of EQ recommendations from MaskingAnalyzer
            
        Returns:
            EQ'd audio
        """
        bands = []
        
        for rec in masking_recommendations:
            if 'eq' in rec:
                eq_rec = rec['eq']
                bands.append({
                    'type': 'peak',
                    'frequency': eq_rec['frequency'],
                    'gain': eq_rec['gain_db'],
                    'q': eq_rec['q']
                })
        
        if bands:
            return self.process(audio, bands)
        else:
            return audio
    
    def _apply_frequency_response(
        self,
        audio: np.ndarray,
        magnitude_response: np.ndarray,
        fft_size: int
    ) -> np.ndarray:
        """
        Apply frequency response via FFT
        
        Args:
            audio: Input audio
            magnitude_response: Magnitude response
            fft_size: FFT size
            
        Returns:
            Filtered audio
        """
        # Pad audio
        hop_size = fft_size // 2
        padded = np.pad(audio, (0, fft_size))
        
        # Process in chunks with overlap-add
        output = np.zeros_like(padded)
        
        for i in range(0, len(padded) - fft_size, hop_size):
            # Extract chunk
            chunk = padded[i:i + fft_size]
            
            # Window
            window = np.hanning(fft_size)
            windowed = chunk * window
            
            # FFT
            spectrum = np.fft.rfft(windowed)
            
            # Apply magnitude response (preserve phase)
            filtered_spectrum = spectrum * magnitude_response
            
            # IFFT
            filtered_chunk = np.fft.irfft(filtered_spectrum, n=fft_size)
            
            # Overlap-add
            output[i:i + fft_size] += filtered_chunk * window
        
        # Remove padding
        output = output[:len(audio)]
        
        return output
    
    def _calculate_envelope(
        self,
        audio: np.ndarray,
        attack_ms: float,
        release_ms: float
    ) -> np.ndarray:
        """Calculate envelope follower"""
        attack_samples = int(attack_ms * self.sample_rate / 1000)
        release_samples = int(release_ms * self.sample_rate / 1000)
        
        rectified = np.abs(audio)
        envelope = np.zeros_like(rectified)
        envelope[0] = rectified[0]
        
        for i in range(1, len(rectified)):
            if rectified[i] > envelope[i-1]:
                alpha = 1.0 - np.exp(-1.0 / attack_samples)
            else:
                alpha = 1.0 - np.exp(-1.0 / release_samples)
            
            envelope[i] = alpha * rectified[i] + (1 - alpha) * envelope[i-1]
        
        return envelope
    
    def intelligent_eq(
        self,
        audio: np.ndarray,
        target_curve: Optional[np.ndarray] = None,
        max_gain_db: float = 4.0
    ) -> np.ndarray:
        """
        Apply intelligent EQ matching to target curve
        
        Args:
            audio: Input audio
            target_curve: Target frequency response (optional)
            max_gain_db: Maximum gain per band
            
        Returns:
            Intelligently EQ'd audio
        """
        # Analyze current spectrum
        stft = np.abs(np.fft.rfft(audio))
        freqs = np.fft.rfftfreq(len(audio), 1/self.sample_rate)
        
        # Default target: flat with slight smile curve
        if target_curve is None:
            target_curve = np.ones_like(stft)
            # Boost lows and highs slightly
            for i, f in enumerate(freqs):
                if f < 100:
                    target_curve[i] = 1.2  # +1.5 dB
                elif f > 8000:
                    target_curve[i] = 1.15  # +1 dB
        
        # Calculate required EQ
        ratio = target_curve / (stft + 1e-10)
        gain_db = 20 * np.log10(ratio)
        
        # Limit gain
        gain_db = np.clip(gain_db, -max_gain_db, max_gain_db)
        
        # Smooth gain curve
        from scipy.ndimage import gaussian_filter1d
        gain_db_smooth = gaussian_filter1d(gain_db, sigma=10)
        
        # Create EQ bands at key frequencies
        key_freqs = [60, 120, 250, 500, 1000, 2000, 4000, 8000, 12000]
        bands = []
        
        for freq in key_freqs:
            # Find closest frequency bin
            idx = np.argmin(np.abs(freqs - freq))
            if idx < len(gain_db_smooth):
                gain = float(gain_db_smooth[idx])
                if abs(gain) > 0.5:  # Only apply if significant
                    bands.append({
                        'type': 'peak',
                        'frequency': freq,
                        'gain': gain,
                        'q': 1.5
                    })
        
        if bands:
            return self.process(audio, bands)
        else:
            return audio
