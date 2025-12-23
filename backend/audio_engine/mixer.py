import numpy as np
import soundfile as sf
from pedalboard import Pedalboard, Compressor, HighpassFilter, LowpassFilter, Gain, Reverb
from typing import List, Dict, Any, Callable, Optional
import librosa


class AudioMixer:
    """Intelligent audio mixing engine"""
    
    def __init__(self):
        self.sample_rate = 44100
    
    def mix(
        self,
        stem_files: List[str],
        stem_metadata: List[Dict[str, Any]],
        output_file: str,
        progress_callback: Optional[Callable[[float], None]] = None
    ):
        """
        Mix multiple stems with intelligent processing
        
        Args:
            stem_files: List of paths to stem files
            stem_metadata: List of metadata dicts from analyzer
            output_file: Path for output mixed file
            progress_callback: Optional callback for progress updates (0-100)
        """
        processed_stems = []
        
        # Process each stem
        for i, (stem_file, metadata) in enumerate(zip(stem_files, stem_metadata)):
            # Load audio
            audio, sr = sf.read(stem_file)
            
            # Resample if needed
            if sr != self.sample_rate:
                audio = librosa.resample(audio, orig_sr=sr, target_sr=self.sample_rate)
            
            # Convert to stereo if mono
            if len(audio.shape) == 1:
                audio = np.stack([audio, audio], axis=-1)
            
            # Apply processing chain based on instrument type
            processed = self._process_stem(audio, metadata)
            
            processed_stems.append(processed)
            
            if progress_callback:
                progress_callback((i + 1) / len(stem_files) * 100)
        
        # Ensure all stems have the same length
        max_length = max(len(stem) for stem in processed_stems)
        padded_stems = []
        
        for stem in processed_stems:
            if len(stem) < max_length:
                padding = np.zeros((max_length - len(stem), 2))
                stem = np.vstack([stem, padding])
            padded_stems.append(stem)
        
        # Sum all stems
        mixed = np.sum(padded_stems, axis=0)
        
        # Normalize to prevent clipping
        max_val = np.max(np.abs(mixed))
        if max_val > 0.9:
            mixed = mixed * (0.9 / max_val)
        
        # Save mixed file
        sf.write(output_file, mixed, self.sample_rate)
    
    def _process_stem(self, audio: np.ndarray, metadata: Dict[str, Any]) -> np.ndarray:
        """
        Apply processing chain to individual stem
        
        Args:
            audio: Audio data (stereo)
            metadata: Stem metadata from analyzer
            
        Returns:
            Processed audio
        """
        instrument_type = metadata['instrument_type']
        
        # Create processing chain based on instrument
        if instrument_type == 'drums':
            board = self._drums_chain(metadata)
        elif instrument_type == 'bass':
            board = self._bass_chain(metadata)
        elif instrument_type == 'vocals':
            board = self._vocals_chain(metadata)
        elif instrument_type == 'synth':
            board = self._synth_chain(metadata)
        else:
            board = self._default_chain(metadata)
        
        # Process audio
        processed = board(audio.T, sample_rate=self.sample_rate).T
        
        return processed
    
    def _drums_chain(self, metadata: Dict[str, Any]) -> Pedalboard:
        """Processing chain for drums"""
        return Pedalboard([
            HighpassFilter(cutoff_frequency_hz=30),
            Compressor(
                threshold_db=-15,
                ratio=4.0,
                attack_ms=3,
                release_ms=50
            ),
            Gain(gain_db=-3)
        ])
    
    def _bass_chain(self, metadata: Dict[str, Any]) -> Pedalboard:
        """Processing chain for bass"""
        return Pedalboard([
            HighpassFilter(cutoff_frequency_hz=40),
            LowpassFilter(cutoff_frequency_hz=300),
            Compressor(
                threshold_db=-18,
                ratio=5.0,
                attack_ms=10,
                release_ms=100
            ),
            Gain(gain_db=-2)
        ])
    
    def _vocals_chain(self, metadata: Dict[str, Any]) -> Pedalboard:
        """Processing chain for vocals"""
        return Pedalboard([
            HighpassFilter(cutoff_frequency_hz=80),
            Compressor(
                threshold_db=-20,
                ratio=4.0,
                attack_ms=5,
                release_ms=50
            ),
            Reverb(
                room_size=0.3,
                damping=0.5,
                wet_level=0.15,
                dry_level=0.85
            ),
            Gain(gain_db=-2)
        ])
    
    def _synth_chain(self, metadata: Dict[str, Any]) -> Pedalboard:
        """Processing chain for synths"""
        return Pedalboard([
            Compressor(
                threshold_db=-18,
                ratio=3.0,
                attack_ms=10,
                release_ms=100
            ),
            Reverb(
                room_size=0.4,
                damping=0.6,
                wet_level=0.2,
                dry_level=0.8
            ),
            Gain(gain_db=-3)
        ])
    
    def _default_chain(self, metadata: Dict[str, Any]) -> Pedalboard:
        """Default processing chain"""
        return Pedalboard([
            Compressor(
                threshold_db=-18,
                ratio=3.0,
                attack_ms=10,
                release_ms=80
            ),
            Gain(gain_db=-3)
        ])
