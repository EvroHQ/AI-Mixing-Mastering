"""
Studio-Quality Reverb & Delay
Professional spatial effects using Pedalboard
"""

import numpy as np
from pedalboard import Reverb, Delay as PedalboardDelay
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class StudioReverb:
    """
    Professional reverb processor
    """
    
    def __init__(self, sample_rate: int = 48000):
        """
        Initialize reverb
        
        Args:
            sample_rate: Audio sample rate
        """
        self.sample_rate = sample_rate
    
    def process(
        self,
        audio: np.ndarray,
        room_size: float = 0.5,
        damping: float = 0.5,
        wet_level: float = 0.15,  # Reduced from 0.3 for clarity
        dry_level: float = 0.85,  # Increased from 0.7
        width: float = 1.0,
        freeze_mode: float = 0.0
    ) -> np.ndarray:
        """
        Apply reverb to audio
        
        Args:
            audio: Input audio
            room_size: Room size (0-1)
            damping: High frequency damping (0-1)
            wet_level: Wet signal level (0-1)
            dry_level: Dry signal level (0-1)
            width: Stereo width (0-1)
            freeze_mode: Freeze mode (0-1)
            
        Returns:
            Reverb processed audio
        """
        # Ensure audio is 2D
        if audio.ndim == 1:
            audio = np.stack([audio, audio])
            was_mono = True
        else:
            was_mono = False
        
        # Create reverb
        reverb = Reverb(
            room_size=room_size,
            damping=damping,
            wet_level=wet_level,
            dry_level=dry_level,
            width=width,
            freeze_mode=freeze_mode
        )
        
        # Process
        output = reverb(audio.astype(np.float32), self.sample_rate)
        
        # Return to original shape
        if was_mono:
            output = np.mean(output, axis=0)
        
        return output
    
    def plate_reverb(
        self,
        audio: np.ndarray,
        decay_time: float = 2.0,
        pre_delay_ms: float = 20.0,
        mix: float = 0.15  # Reduced from 0.25
    ) -> np.ndarray:
        """
        Plate reverb simulation
        
        Args:
            audio: Input audio
            decay_time: Decay time in seconds
            pre_delay_ms: Pre-delay in milliseconds
            mix: Wet/dry mix (0-1)
            
        Returns:
            Plate reverb processed audio
        """
        # Map decay time to room size
        room_size = min(0.95, decay_time / 4.0)
        
        # Apply pre-delay
        if pre_delay_ms > 0:
            pre_delay_samples = int(pre_delay_ms * self.sample_rate / 1000)
            audio_delayed = np.pad(audio, ((0, 0), (pre_delay_samples, 0)))[:, :audio.shape[1]]
        else:
            audio_delayed = audio
        
        # Apply reverb
        output = self.process(
            audio_delayed,
            room_size=room_size,
            damping=0.3,  # Bright plate sound
            wet_level=mix,
            dry_level=1.0 - mix,
            width=0.9
        )
        
        return output
    
    def room_reverb(
        self,
        audio: np.ndarray,
        room_type: str = 'small',
        mix: float = 0.10  # Reduced from 0.15
    ) -> np.ndarray:
        """
        Room reverb simulation
        
        Args:
            audio: Input audio
            room_type: 'small', 'medium', 'large', 'hall'
            mix: Wet/dry mix
            
        Returns:
            Room reverb processed audio
        """
        # Room presets
        presets = {
            'small': {'room_size': 0.3, 'damping': 0.7, 'width': 0.5},
            'medium': {'room_size': 0.5, 'damping': 0.5, 'width': 0.7},
            'large': {'room_size': 0.7, 'damping': 0.4, 'width': 0.9},
            'hall': {'room_size': 0.9, 'damping': 0.3, 'width': 1.0}
        }
        
        preset = presets.get(room_type, presets['medium'])
        
        output = self.process(
            audio,
            room_size=preset['room_size'],
            damping=preset['damping'],
            wet_level=mix,
            dry_level=1.0 - mix,
            width=preset['width']
        )
        
        return output
    
    def send_reverb(
        self,
        audio: np.ndarray,
        send_level: float = 0.20,  # Reduced from 0.3
        reverb_type: str = 'plate'
    ) -> np.ndarray:
        """
        Apply reverb as a send effect
        
        Args:
            audio: Input audio
            send_level: Send amount (0-1)
            reverb_type: 'plate', 'room', 'hall'
            
        Returns:
            Audio with send reverb
        """
        if reverb_type == 'plate':
            wet = self.plate_reverb(audio, mix=1.0)
        elif reverb_type == 'hall':
            wet = self.room_reverb(audio, room_type='hall', mix=1.0)
        else:
            wet = self.room_reverb(audio, room_type='medium', mix=1.0)
        
        # Mix
        output = audio + wet * send_level
        
        return output


class StudioDelay:
    """
    Professional delay processor
    """
    
    def __init__(self, sample_rate: int = 48000):
        """
        Initialize delay
        
        Args:
            sample_rate: Audio sample rate
        """
        self.sample_rate = sample_rate
    
    def process(
        self,
        audio: np.ndarray,
        delay_seconds: float = 0.5,
        feedback: float = 0.3,
        mix: float = 0.3
    ) -> np.ndarray:
        """
        Apply delay to audio
        
        Args:
            audio: Input audio
            delay_seconds: Delay time in seconds
            feedback: Feedback amount (0-1)
            mix: Wet/dry mix (0-1)
            
        Returns:
            Delayed audio
        """
        # Ensure audio is 2D
        if audio.ndim == 1:
            audio = np.stack([audio, audio])
            was_mono = True
        else:
            was_mono = False
        
        # Create delay
        delay = PedalboardDelay(
            delay_seconds=delay_seconds,
            feedback=feedback,
            mix=mix
        )
        
        # Process
        output = delay(audio.astype(np.float32), self.sample_rate)
        
        # Return to original shape
        if was_mono:
            output = np.mean(output, axis=0)
        
        return output
    
    def tempo_sync_delay(
        self,
        audio: np.ndarray,
        tempo_bpm: float,
        note_value: str = '1/4',
        feedback: float = 0.4,
        mix: float = 0.25
    ) -> np.ndarray:
        """
        Apply tempo-synced delay
        
        Args:
            audio: Input audio
            tempo_bpm: Tempo in BPM
            note_value: Note value ('1/4', '1/8', '1/16', '1/2', 'dotted_1/8')
            feedback: Feedback amount
            mix: Wet/dry mix
            
        Returns:
            Tempo-synced delayed audio
        """
        # Calculate delay time from tempo
        beat_duration = 60.0 / tempo_bpm
        
        note_multipliers = {
            '1/2': 2.0,
            '1/4': 1.0,
            'dotted_1/4': 1.5,
            '1/8': 0.5,
            'dotted_1/8': 0.75,
            '1/16': 0.25,
            '1/32': 0.125
        }
        
        multiplier = note_multipliers.get(note_value, 1.0)
        delay_seconds = beat_duration * multiplier
        
        return self.process(audio, delay_seconds, feedback, mix)
    
    def ping_pong_delay(
        self,
        audio: np.ndarray,
        delay_seconds: float = 0.375,
        feedback: float = 0.5,
        mix: float = 0.3
    ) -> np.ndarray:
        """
        Apply ping-pong delay (stereo)
        
        Args:
            audio: Input audio
            delay_seconds: Delay time
            feedback: Feedback amount
            mix: Wet/dry mix
            
        Returns:
            Ping-pong delayed audio
        """
        # Ensure stereo
        if audio.ndim == 1:
            audio = np.stack([audio, audio])
        
        # Create ping-pong effect manually
        delay_samples = int(delay_seconds * self.sample_rate)
        
        # Initialize output
        output = np.zeros((2, audio.shape[1] + delay_samples * 4))
        output[:, :audio.shape[1]] = audio
        
        # Ping-pong between channels
        for i in range(4):  # 4 repeats
            delay_offset = delay_samples * (i + 1)
            channel = i % 2  # Alternate channels
            
            # Add delayed signal
            if delay_offset < output.shape[1]:
                delayed_signal = audio[1 - channel] * (feedback ** (i + 1))
                end_idx = min(audio.shape[1] + delay_offset, output.shape[1])
                output[channel, delay_offset:end_idx] += delayed_signal[:end_idx - delay_offset]
        
        # Trim to original length
        output = output[:, :audio.shape[1]]
        
        # Mix
        output = (1 - mix) * audio + mix * output
        
        return output
    
    def slapback_delay(
        self,
        audio: np.ndarray,
        delay_ms: float = 100.0,
        mix: float = 0.4
    ) -> np.ndarray:
        """
        Apply slapback delay (short single repeat)
        
        Args:
            audio: Input audio
            delay_ms: Delay time in milliseconds
            mix: Wet/dry mix
            
        Returns:
            Slapback delayed audio
        """
        return self.process(
            audio,
            delay_seconds=delay_ms / 1000.0,
            feedback=0.0,  # No feedback for slapback
            mix=mix
        )
