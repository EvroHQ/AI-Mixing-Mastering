"""
Audio Analyzer - Spectral Analysis
Extracts spectral features using STFT, CQT, and MFCC
"""

import numpy as np
import librosa
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class SpectralAnalyzer:
    """Spectral analysis for audio signals"""
    
    def __init__(
        self,
        sample_rate: int = 48000,
        n_fft: int = 2048,
        hop_length: int = 512
    ):
        """
        Initialize spectral analyzer
        
        Args:
            sample_rate: Audio sample rate
            n_fft: FFT window size
            hop_length: Hop length for STFT
        """
        self.sample_rate = sample_rate
        self.n_fft = n_fft
        self.hop_length = hop_length
        
    def analyze(self, audio: np.ndarray) -> Dict:
        """
        Perform spectral analysis on audio
        
        Args:
            audio: Audio signal (mono)
            
        Returns:
            Dictionary with spectral features
        """
        logger.info("Performing spectral analysis...")
        
        features = {}
        
        # STFT - Short-Time Fourier Transform
        stft = librosa.stft(
            audio,
            n_fft=self.n_fft,
            hop_length=self.hop_length
        )
        magnitude = np.abs(stft)
        features['stft_magnitude'] = magnitude
        features['stft_phase'] = np.angle(stft)
        
        # Spectral centroid
        spectral_centroid = librosa.feature.spectral_centroid(
            y=audio,
            sr=self.sample_rate,
            n_fft=self.n_fft,
            hop_length=self.hop_length
        )
        features['spectral_centroid'] = np.mean(spectral_centroid)
        
        # Spectral rolloff
        spectral_rolloff = librosa.feature.spectral_rolloff(
            y=audio,
            sr=self.sample_rate,
            n_fft=self.n_fft,
            hop_length=self.hop_length
        )
        features['spectral_rolloff'] = np.mean(spectral_rolloff)
        
        # Spectral bandwidth
        spectral_bandwidth = librosa.feature.spectral_bandwidth(
            y=audio,
            sr=self.sample_rate,
            n_fft=self.n_fft,
            hop_length=self.hop_length
        )
        features['spectral_bandwidth'] = np.mean(spectral_bandwidth)
        
        # Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(
            audio,
            frame_length=self.n_fft,
            hop_length=self.hop_length
        )
        features['zero_crossing_rate'] = np.mean(zcr)
        
        # CQT - Constant-Q Transform
        cqt = np.abs(librosa.cqt(
            audio,
            sr=self.sample_rate,
            hop_length=self.hop_length
        ))
        features['cqt'] = cqt
        
        # MFCC - Mel-Frequency Cepstral Coefficients
        mfcc = librosa.feature.mfcc(
            y=audio,
            sr=self.sample_rate,
            n_mfcc=13,
            n_fft=self.n_fft,
            hop_length=self.hop_length
        )
        features['mfcc'] = mfcc
        features['mfcc_mean'] = np.mean(mfcc, axis=1)
        features['mfcc_std'] = np.std(mfcc, axis=1)
        
        # Chroma features
        chroma = librosa.feature.chroma_stft(
            y=audio,
            sr=self.sample_rate,
            n_fft=self.n_fft,
            hop_length=self.hop_length
        )
        features['chroma'] = chroma
        features['chroma_mean'] = np.mean(chroma, axis=1)
        
        # Spectral contrast
        contrast = librosa.feature.spectral_contrast(
            y=audio,
            sr=self.sample_rate,
            n_fft=self.n_fft,
            hop_length=self.hop_length
        )
        features['spectral_contrast'] = contrast
        features['spectral_contrast_mean'] = np.mean(contrast, axis=1)
        
        logger.info("Spectral analysis complete")
        return features
    
    def detect_peaks(
        self, 
        audio: np.ndarray,
        threshold: float = 0.5
    ) -> np.ndarray:
        """
        Detect spectral peaks
        
        Args:
            audio: Audio signal
            threshold: Peak detection threshold
            
        Returns:
            Array of peak frequencies
        """
        # Compute power spectrum
        stft = librosa.stft(audio, n_fft=self.n_fft)
        power = np.abs(stft) ** 2
        
        # Average over time
        avg_power = np.mean(power, axis=1)
        
        # Find peaks
        from scipy.signal import find_peaks
        peaks, _ = find_peaks(avg_power, height=threshold * np.max(avg_power))
        
        # Convert to frequencies
        freqs = librosa.fft_frequencies(sr=self.sample_rate, n_fft=self.n_fft)
        peak_freqs = freqs[peaks]
        
        return peak_freqs
    
    def analyze_frequency_bands(
        self, 
        audio: np.ndarray
    ) -> Dict[str, float]:
        """
        Analyze energy in different frequency bands
        
        Args:
            audio: Audio signal
            
        Returns:
            Dictionary with band energies
        """
        # Compute STFT
        stft = librosa.stft(audio, n_fft=self.n_fft)
        power = np.abs(stft) ** 2
        
        # Frequency bins
        freqs = librosa.fft_frequencies(sr=self.sample_rate, n_fft=self.n_fft)
        
        # Define bands
        bands = {
            'sub_bass': (20, 60),      # Sub bass
            'bass': (60, 250),         # Bass
            'low_mid': (250, 500),     # Low mids
            'mid': (500, 2000),        # Mids
            'high_mid': (2000, 4000),  # High mids
            'presence': (4000, 6000),  # Presence
            'brilliance': (6000, 20000) # Brilliance/Air
        }
        
        band_energies = {}
        for band_name, (low, high) in bands.items():
            # Find frequency bins in this band
            mask = (freqs >= low) & (freqs < high)
            
            # Sum energy in this band
            band_power = np.sum(power[mask, :])
            band_energies[band_name] = float(band_power)
        
        # Normalize by total energy
        total_energy = sum(band_energies.values())
        if total_energy > 0:
            band_energies = {
                k: v / total_energy 
                for k, v in band_energies.items()
            }
        
        return band_energies
