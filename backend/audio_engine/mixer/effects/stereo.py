"""
Studio-Quality Stereo Width Processor
Professional stereo imaging and width control
"""

import numpy as np
from typing import Optional, Tuple, Dict
import logging

logger = logging.getLogger(__name__)


class StereoProcessor:
    """
    Professional stereo width and imaging processor
    """
    
    def __init__(self, sample_rate: int = 48000):
        """
        Initialize stereo processor
        
        Args:
            sample_rate: Audio sample rate
        """
        self.sample_rate = sample_rate
    
    def adjust_width(
        self,
        audio: np.ndarray,
        width_percent: float = 100.0,
        safe_bass: bool = True,
        bass_mono_freq: float = 120.0
    ) -> np.ndarray:
        """
        Adjust stereo width
        
        Args:
            audio: Input audio (stereo)
            width_percent: Width percentage (0-200%)
                          0% = mono, 100% = original, 200% = extra wide
            safe_bass: Keep bass frequencies mono for compatibility
            bass_mono_freq: Frequency below which to keep mono
            
        Returns:
            Width-adjusted audio
        """
        # Ensure stereo
        if audio.ndim == 1:
            logger.warning("Input is mono, returning unchanged")
            return audio
        
        # Convert to M/S
        mid, side = self._to_mid_side(audio)
        
        # Adjust width
        width_factor = width_percent / 100.0
        side_adjusted = side * width_factor
        
        # Keep bass mono if requested
        if safe_bass:
            side_adjusted = self._mono_bass(
                side_adjusted,
                bass_mono_freq
            )
        
        # Convert back to L/R
        output = self._to_left_right(mid, side_adjusted)
        
        # Safety check: prevent excessive width
        if width_percent > 140:
            logger.warning(f"Width {width_percent}% exceeds safe limit (140%)")
        
        return output
    
    def haas_effect(
        self,
        audio: np.ndarray,
        delay_ms: float = 20.0,
        mix: float = 0.5
    ) -> np.ndarray:
        """
        Apply Haas effect for stereo widening
        
        Args:
            audio: Input audio
            delay_ms: Delay time in milliseconds (10-40ms typical)
            mix: Effect mix (0-1)
            
        Returns:
            Haas-widened audio
        """
        # Ensure stereo
        if audio.ndim == 1:
            audio = np.stack([audio, audio])
        
        # Calculate delay in samples
        delay_samples = int(delay_ms * self.sample_rate / 1000)
        
        # Create delayed version
        left = audio[0]
        right = np.pad(audio[1], (delay_samples, 0))[:len(audio[1])]
        
        # Mix with original
        output = np.stack([
            (1 - mix) * audio[0] + mix * left,
            (1 - mix) * audio[1] + mix * right
        ])
        
        return output
    
    def stereo_enhance(
        self,
        audio: np.ndarray,
        amount: float = 0.3,
        frequency_dependent: bool = True
    ) -> np.ndarray:
        """
        Enhance stereo image
        
        Args:
            audio: Input audio (stereo)
            amount: Enhancement amount (0-1)
            frequency_dependent: Apply more enhancement to highs
            
        Returns:
            Enhanced stereo audio
        """
        if audio.ndim == 1:
            return audio
        
        # Convert to M/S
        mid, side = self._to_mid_side(audio)
        
        if frequency_dependent:
            # Enhance highs more than lows
            from scipy import signal
            
            # Split into bands
            crossover = 2000  # Hz
            
            # Low band
            sos_low = signal.butter(
                4, crossover, 'low',
                fs=self.sample_rate, output='sos'
            )
            side_low = signal.sosfilt(sos_low, side)
            
            # High band
            sos_high = signal.butter(
                4, crossover, 'high',
                fs=self.sample_rate, output='sos'
            )
            side_high = signal.sosfilt(sos_high, side)
            
            # Enhance highs more
            side_enhanced = (
                side_low * (1 + amount * 0.5) +
                side_high * (1 + amount * 1.5)
            )
        else:
            # Uniform enhancement
            side_enhanced = side * (1 + amount)
        
        # Convert back
        output = self._to_left_right(mid, side_enhanced)
        
        return output
    
    def pseudo_stereo(
        self,
        audio: np.ndarray,
        width: float = 0.5,
        decorrelation: float = 0.3
    ) -> np.ndarray:
        """
        Create pseudo-stereo from mono
        
        Args:
            audio: Input audio (mono)
            width: Stereo width (0-1)
            decorrelation: Amount of decorrelation (0-1)
            
        Returns:
            Pseudo-stereo audio
        """
        # Ensure mono
        if audio.ndim > 1:
            audio = np.mean(audio, axis=0)
        
        # Create decorrelated version
        from scipy import signal
        
        # All-pass filter for decorrelation
        b, a = signal.iirfilter(
            4, 0.5, btype='highpass',
            ftype='butter', fs=self.sample_rate
        )
        decorrelated = signal.filtfilt(b, a, audio)
        
        # Mix decorrelated with original
        left = audio + decorrelated * decorrelation * width
        right = audio - decorrelated * decorrelation * width
        
        # Normalize
        max_val = max(np.max(np.abs(left)), np.max(np.abs(right)))
        if max_val > 1.0:
            left = left / max_val
            right = right / max_val
        
        output = np.stack([left, right])
        
        return output
    
    def check_mono_compatibility(
        self,
        audio: np.ndarray
    ) -> Dict:
        """
        Check mono compatibility of stereo signal
        
        Args:
            audio: Input audio (stereo)
            
        Returns:
            Dictionary with compatibility metrics
        """
        if audio.ndim == 1:
            return {
                'correlation': 1.0,
                'phase_issues': False,
                'mono_compatible': True
            }
        
        left, right = audio[0], audio[1]
        
        # Calculate correlation
        correlation = np.corrcoef(left, right)[0, 1]
        
        # Check for phase issues (negative correlation)
        phase_issues = correlation < 0.1
        
        # Mono sum
        mono = (left + right) / 2
        
        # Check for cancellation
        mono_level = np.sqrt(np.mean(mono ** 2))
        stereo_level = np.sqrt(np.mean((left ** 2 + right ** 2) / 2))
        
        cancellation_db = 20 * np.log10((mono_level / (stereo_level + 1e-10)) + 1e-10)
        
        # Mono compatible if correlation > 0.1 and cancellation < 6dB
        mono_compatible = correlation >= 0.1 and cancellation_db > -6.0
        
        return {
            'correlation': float(correlation),
            'phase_issues': bool(phase_issues),
            'mono_compatible': bool(mono_compatible),
            'cancellation_db': float(cancellation_db)
        }
    
    def fix_phase_issues(
        self,
        audio: np.ndarray
    ) -> np.ndarray:
        """
        Fix phase issues in stereo signal
        
        Args:
            audio: Input audio (stereo)
            
        Returns:
            Phase-corrected audio
        """
        if audio.ndim == 1:
            return audio
        
        # Check compatibility
        compat = self.check_mono_compatibility(audio)
        
        if compat['phase_issues']:
            logger.warning("Phase issues detected, inverting right channel")
            
            # Invert right channel
            output = audio.copy()
            output[1] = -output[1]
            
            # Check if it improved
            new_compat = self.check_mono_compatibility(output)
            
            if new_compat['correlation'] > compat['correlation']:
                return output
            else:
                logger.warning("Inversion didn't help, returning original")
                return audio
        
        return audio
    
    def _to_mid_side(
        self,
        audio: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert L/R to M/S
        
        Args:
            audio: Stereo audio (2, samples)
            
        Returns:
            Tuple of (mid, side)
        """
        left, right = audio[0], audio[1]
        
        mid = (left + right) / 2
        side = (left - right) / 2
        
        return mid, side
    
    def _to_left_right(
        self,
        mid: np.ndarray,
        side: np.ndarray
    ) -> np.ndarray:
        """
        Convert M/S to L/R
        
        Args:
            mid: Mid signal
            side: Side signal
            
        Returns:
            Stereo audio (2, samples)
        """
        left = mid + side
        right = mid - side
        
        return np.stack([left, right])
    
    def _mono_bass(
        self,
        side: np.ndarray,
        cutoff_freq: float
    ) -> np.ndarray:
        """
        Make bass frequencies mono in side signal
        
        Args:
            side: Side signal
            cutoff_freq: Frequency below which to remove side
            
        Returns:
            Bass-mono side signal
        """
        from scipy import signal
        
        # High-pass filter the side signal
        sos = signal.butter(
            4, cutoff_freq, 'high',
            fs=self.sample_rate, output='sos'
        )
        
        side_filtered = signal.sosfilt(sos, side)
        
        return side_filtered
