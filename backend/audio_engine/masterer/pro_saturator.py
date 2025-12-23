"""
Professional Saturation & Harmonic Enhancement
Studio-grade analog modeling and harmonic exciter
"""

import numpy as np
from scipy import signal
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ProSaturator:
    """
    Professional saturation processor with:
    - Analog tape saturation modeling
    - Tube saturation
    - Harmonic exciter
    - Multi-band saturation
    """
    
    def __init__(self, sample_rate: int = 48000):
        """
        Initialize pro saturator
        
        Args:
            sample_rate: Audio sample rate
        """
        self.sample_rate = sample_rate
    
    def tape_saturation(
        self,
        audio: np.ndarray,
        drive: float = 0.5,
        bias: float = 0.0,
        mix: float = 1.0
    ) -> np.ndarray:
        """
        Analog tape saturation modeling
        
        Args:
            audio: Input audio
            drive: Saturation drive (0-1)
            bias: Tape bias (-1 to 1)
            mix: Wet/dry mix (0-1)
            
        Returns:
            Saturated audio
        """
        logger.info(f"Tape saturation: drive={drive:.2f}, bias={bias:.2f}")
        
        # Apply drive
        driven = audio * (1 + drive * 3)
        
        # Add bias
        biased = driven + bias * 0.1
        
        # Tape saturation curve (soft clipping with asymmetry)
        saturated = np.tanh(biased * 1.5)
        
        # Add even harmonics (tape characteristic)
        saturated = saturated + 0.1 * drive * np.tanh(biased * 3) ** 2
        
        # Remove bias
        saturated = saturated - bias * 0.1
        
        # Normalize
        saturated = saturated / (1 + drive * 0.3)
        
        # Mix with dry
        output = (1 - mix) * audio + mix * saturated
        
        return output
    
    def tube_saturation(
        self,
        audio: np.ndarray,
        drive: float = 0.5,
        warmth: float = 0.5,
        mix: float = 1.0
    ) -> np.ndarray:
        """
        Tube/valve saturation modeling
        
        Args:
            audio: Input audio
            drive: Saturation drive (0-1)
            warmth: Warmth amount (0-1)
            mix: Wet/dry mix (0-1)
            
        Returns:
            Tube saturated audio
        """
        logger.info(f"Tube saturation: drive={drive:.2f}, warmth={warmth:.2f}")
        
        # Apply drive
        driven = audio * (1 + drive * 5)
        
        # Tube saturation curve (asymmetric soft clipping)
        # Positive side: softer clipping
        pos_mask = driven > 0
        neg_mask = driven <= 0
        
        saturated = np.zeros_like(driven)
        saturated[pos_mask] = np.tanh(driven[pos_mask] * 0.8)
        saturated[neg_mask] = np.tanh(driven[neg_mask] * 1.2)
        
        # Add odd harmonics (tube characteristic)
        saturated = saturated + 0.15 * drive * np.tanh(driven * 2) ** 3
        
        # Add warmth (low-frequency emphasis)
        if warmth > 0:
            # Low-pass filter for warmth
            sos = signal.butter(2, 500, fs=self.sample_rate, output='sos')
            warm_signal = signal.sosfilt(sos, saturated)
            saturated = saturated + warmth * 0.2 * warm_signal
        
        # Normalize
        saturated = saturated / (1 + drive * 0.4)
        
        # Mix with dry
        output = (1 - mix) * audio + mix * saturated
        
        return output
    
    def harmonic_exciter(
        self,
        audio: np.ndarray,
        frequency: float = 3000.0,
        amount: float = 0.3,
        harmonics: int = 3
    ) -> np.ndarray:
        """
        Harmonic exciter (adds brightness and presence)
        
        Args:
            audio: Input audio
            frequency: Crossover frequency
            amount: Exciter amount (0-1)
            harmonics: Number of harmonics to generate
            
        Returns:
            Excited audio
        """
        logger.info(f"Harmonic exciter: freq={frequency}Hz, amount={amount:.2f}")
        
        # Ensure mono for processing
        if audio.ndim > 1:
            audio_mono = np.mean(audio, axis=0)
        else:
            audio_mono = audio
        
        # Extract high frequencies
        sos = signal.butter(4, frequency, 'high', fs=self.sample_rate, output='sos')
        highs = signal.sosfilt(sos, audio_mono)
        
        # Generate harmonics
        excited = highs.copy()
        for h in range(2, harmonics + 1):
            # Create harmonic by waveshaping
            harmonic = np.tanh(highs * h) / h
            excited = excited + harmonic * (amount / h)
        
        # High-pass filter excited signal
        sos_hp = signal.butter(4, frequency * 1.5, 'high', fs=self.sample_rate, output='sos')
        excited = signal.sosfilt(sos_hp, excited)
        
        # Mix back
        if audio.ndim > 1:
            excited = np.tile(excited, (audio.shape[0], 1))
        
        output = audio + excited * amount
        
        return output
    
    def multiband_saturate(
        self,
        audio: np.ndarray,
        crossovers: list = [250, 2000, 6000],
        drives: list = [0.3, 0.5, 0.4, 0.6]
    ) -> np.ndarray:
        """
        Multi-band saturation for frequency-specific control
        
        Args:
            audio: Input audio
            crossovers: Crossover frequencies
            drives: Drive amount for each band
            
        Returns:
            Multi-band saturated audio
        """
        logger.info(f"Multi-band saturation: {len(drives)} bands")
        
        # Ensure mono for processing
        if audio.ndim > 1:
            audio_mono = np.mean(audio, axis=0)
        else:
            audio_mono = audio
        
        # Split into bands
        bands = self._split_bands(audio_mono, crossovers)
        
        # Saturate each band
        saturated_bands = []
        for i, (band, drive) in enumerate(zip(bands, drives)):
            # Use tube saturation for each band
            saturated = self.tube_saturation(band, drive=drive, warmth=0.3, mix=1.0)
            saturated_bands.append(saturated)
            logger.info(f"  Band {i+1}: drive={drive:.2f}")
        
        # Sum bands
        output = sum(saturated_bands)
        
        # Match original shape
        if audio.ndim > 1:
            output = np.tile(output, (audio.shape[0], 1))
        
        return output
    
    def _split_bands(
        self,
        audio: np.ndarray,
        crossovers: list
    ) -> list:
        """
        Split audio into frequency bands
        
        Args:
            audio: Input audio (mono)
            crossovers: Crossover frequencies
            
        Returns:
            List of band signals
        """
        bands = []
        
        # Low band
        sos = signal.butter(4, crossovers[0], 'low', fs=self.sample_rate, output='sos')
        low_band = signal.sosfilt(sos, audio)
        bands.append(low_band)
        
        # Mid bands
        for i in range(len(crossovers) - 1):
            sos = signal.butter(
                4,
                [crossovers[i], crossovers[i + 1]],
                'band',
                fs=self.sample_rate,
                output='sos'
            )
            mid_band = signal.sosfilt(sos, audio)
            bands.append(mid_band)
        
        # High band
        sos = signal.butter(4, crossovers[-1], 'high', fs=self.sample_rate, output='sos')
        high_band = signal.sosfilt(sos, audio)
        bands.append(high_band)
        
        return bands
    
    def studio_chain(
        self,
        audio: np.ndarray,
        preset: str = 'balanced'
    ) -> np.ndarray:
        """
        Complete studio saturation chain
        
        Args:
            audio: Input audio
            preset: Preset name ('balanced', 'warm', 'bright', 'aggressive')
            
        Returns:
            Processed audio
        """
        logger.info(f"Studio saturation chain: {preset}")
        
        presets = {
            'balanced': {
                'tape_drive': 0.4,
                'tape_mix': 0.6,
                'tube_drive': 0.3,
                'tube_warmth': 0.4,
                'exciter_amount': 0.25
            },
            'warm': {
                'tape_drive': 0.6,
                'tape_mix': 0.8,
                'tube_drive': 0.5,
                'tube_warmth': 0.7,
                'exciter_amount': 0.15
            },
            'bright': {
                'tape_drive': 0.3,
                'tape_mix': 0.5,
                'tube_drive': 0.2,
                'tube_warmth': 0.2,
                'exciter_amount': 0.5
            },
            'aggressive': {
                'tape_drive': 0.7,
                'tape_mix': 0.9,
                'tube_drive': 0.6,
                'tube_warmth': 0.3,
                'exciter_amount': 0.4
            }
        }
        
        params = presets.get(preset, presets['balanced'])
        
        # Stage 1: Tape saturation
        output = self.tape_saturation(
            audio,
            drive=params['tape_drive'],
            bias=0.0,
            mix=params['tape_mix']
        )
        
        # Stage 2: Tube saturation
        output = self.tube_saturation(
            output,
            drive=params['tube_drive'],
            warmth=params['tube_warmth'],
            mix=0.7
        )
        
        # Stage 3: Harmonic exciter
        output = self.harmonic_exciter(
            output,
            frequency=3000.0,
            amount=params['exciter_amount'],
            harmonics=3
        )
        
        return output
