"""
Adaptive Audio Processor
Analyzes audio content and applies intelligent, adaptive processing
No fixed presets - all parameters calculated from audio analysis
"""

import numpy as np
import librosa
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class AdaptiveProcessor:
    """
    Intelligent processor that adapts to audio content
    """
    
    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate
    
    def analyze_and_process(
        self,
        audio: np.ndarray,
        stem_role: str
    ) -> Dict:
        """
        Analyze audio and determine optimal processing parameters
        
        Args:
            audio: Input audio
            stem_role: Detected role (kick, bass, vocal, etc.)
            
        Returns:
            Dictionary with processing parameters
        """
        logger.info(f"Analyzing {stem_role} for adaptive processing...")
        
        # Convert stereo to mono for analysis
        if audio.ndim > 1:
            audio_mono = np.mean(audio, axis=0)
        else:
            audio_mono = audio
        
        # 1. Spectral Analysis
        spectral_info = self._analyze_spectrum(audio_mono)
        
        # 2. Dynamic Range Analysis
        dynamics_info = self._analyze_dynamics(audio_mono)
        
        # 3. Calculate adaptive parameters
        params = self._calculate_adaptive_params(
            spectral_info,
            dynamics_info,
            stem_role
        )
        
        logger.info(f"Adaptive params for {stem_role}:")
        logger.info(f"  HPF: {params['highpass_freq']} Hz")
        logger.info(f"  Dominant freq: {spectral_info['dominant_freq']:.0f} Hz")
        logger.info(f"  Compression ratio: {params['compression']['ratio']:.1f}:1")
        logger.info(f"  Dynamic range: {dynamics_info['crest_factor_db']:.1f} dB")
        
        return params
    
    def _analyze_spectrum(self, audio: np.ndarray) -> Dict:
        """
        Analyze spectral content
        """
        # Compute FFT
        fft = np.fft.rfft(audio)
        magnitude = np.abs(fft)
        freqs = np.fft.rfftfreq(len(audio), 1/self.sample_rate)
        
        # Find dominant frequency
        dominant_idx = np.argmax(magnitude)
        dominant_freq = freqs[dominant_idx]
        
        # Calculate energy in frequency bands
        bands = {
            'sub_bass': (20, 60),
            'bass': (60, 250),
            'low_mids': (250, 500),
            'mids': (500, 2000),
            'high_mids': (2000, 6000),
            'highs': (6000, 20000)
        }
        
        band_energies = {}
        for band_name, (low, high) in bands.items():
            mask = (freqs >= low) & (freqs < high)
            band_energies[band_name] = np.sum(magnitude[mask])
        
        # Normalize energies
        total_energy = sum(band_energies.values())
        band_ratios = {k: v/total_energy for k, v in band_energies.items()}
        
        # Find spectral centroid
        spectral_centroid = np.sum(freqs * magnitude) / np.sum(magnitude)
        
        return {
            'dominant_freq': dominant_freq,
            'spectral_centroid': spectral_centroid,
            'band_energies': band_energies,
            'band_ratios': band_ratios
        }
    
    def _analyze_dynamics(self, audio: np.ndarray) -> Dict:
        """
        Analyze dynamic range
        """
        # RMS level
        rms = np.sqrt(np.mean(audio ** 2))
        rms_db = 20 * np.log10(rms + 1e-10)
        
        # Peak level
        peak = np.max(np.abs(audio))
        peak_db = 20 * np.log10(peak + 1e-10)
        
        # Crest factor (peak to RMS ratio)
        crest_factor_db = peak_db - rms_db
        
        # Estimate dynamic range using percentiles
        abs_audio = np.abs(audio)
        p95 = np.percentile(abs_audio, 95)
        p5 = np.percentile(abs_audio, 5)
        dynamic_range_db = 20 * np.log10((p95 / (p5 + 1e-10)) + 1e-10)
        
        return {
            'rms_db': rms_db,
            'peak_db': peak_db,
            'crest_factor_db': crest_factor_db,
            'dynamic_range_db': dynamic_range_db
        }
    
    def _calculate_adaptive_params(
        self,
        spectral: Dict,
        dynamics: Dict,
        role: str
    ) -> Dict:
        """
        Calculate processing parameters based on analysis
        """
        # Base highpass: remove only true rumble
        # Adaptive based on dominant frequency
        if spectral['dominant_freq'] < 100:
            # Low frequency content - be conservative
            highpass_freq = max(20, spectral['dominant_freq'] * 0.3)
        elif spectral['dominant_freq'] < 500:
            # Mid-low content
            highpass_freq = max(30, spectral['dominant_freq'] * 0.2)
        else:
            # Higher content - can cut more lows
            highpass_freq = min(80, spectral['dominant_freq'] * 0.1)
        
        # Adaptive compression based on dynamic range
        # More dynamic = less compression needed
        if dynamics['crest_factor_db'] > 12:
            # Very dynamic (e.g., drums)
            ratio = 2.0
            threshold = -15
            makeup_gain = 0.5
        elif dynamics['crest_factor_db'] > 8:
            # Moderately dynamic
            ratio = 2.5
            threshold = -18
            makeup_gain = 1.0
        else:
            # Already compressed
            ratio = 1.5
            threshold = -20
            makeup_gain = 0.0
        
        # Adaptive EQ based on spectral balance
        eq_bands = []
        
        # If too much bass energy, reduce it
        if spectral['band_ratios']['bass'] > 0.3:
            eq_bands.append({
                'type': 'peak',
                'frequency': 250,
                'gain': -1.0,
                'q': 1.5
            })
        
        # If lacking high-mids, boost presence
        if spectral['band_ratios']['high_mids'] < 0.15:
            eq_bands.append({
                'type': 'peak',
                'frequency': 3000,
                'gain': 0.5,
                'q': 2.0
            })
        
        # Adaptive stereo width
        # Narrower for low frequency content
        if spectral['spectral_centroid'] < 500:
            stereo_width = 70  # Narrow for bass
        elif spectral['spectral_centroid'] < 2000:
            stereo_width = 100  # Normal
        else:
            stereo_width = 120  # Wide for highs
        
        return {
            'highpass_freq': int(highpass_freq),
            'eq_bands': eq_bands,
            'compression': {
                'threshold': threshold,
                'ratio': ratio,
                'attack': 10,
                'release': 100,
                'makeup_gain': makeup_gain
            },
            'stereo_width': stereo_width,
            'reverb_send': None,  # No reverb
            'delay_send': None,   # No delay
            'deess': role in ['vocal', 'lead_vocal', 'backing_vocal']
        }
