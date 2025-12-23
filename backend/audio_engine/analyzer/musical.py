"""
Audio Analyzer - Musical Features
Detects tempo, key, beat grid, and harmonic content
"""

import numpy as np
import librosa
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class MusicalAnalyzer:
    """Musical feature extraction"""
    
    def __init__(self, sample_rate: int = 48000):
        """
        Initialize musical analyzer
        
        Args:
            sample_rate: Audio sample rate
        """
        self.sample_rate = sample_rate
        
    def analyze(self, audio: np.ndarray) -> Dict:
        """
        Perform musical analysis on audio
        
        Args:
            audio: Audio signal (mono)
            
        Returns:
            Dictionary with musical features
        """
        logger.info("Performing musical analysis...")
        
        features = {}
        
        # Tempo and beat detection
        tempo, beats = librosa.beat.beat_track(
            y=audio,
            sr=self.sample_rate,
            units='time'
        )
        features['tempo'] = float(tempo)
        features['beats'] = beats
        features['beat_count'] = len(beats)
        
        # Onset detection (transients)
        onset_env = librosa.onset.onset_strength(
            y=audio,
            sr=self.sample_rate
        )
        onsets = librosa.onset.onset_detect(
            onset_envelope=onset_env,
            sr=self.sample_rate,
            units='time'
        )
        features['onsets'] = onsets
        features['onset_count'] = len(onsets)
        
        # Key detection
        chroma = librosa.feature.chroma_cqt(
            y=audio,
            sr=self.sample_rate
        )
        
        # Estimate key from chroma
        key_name, key_confidence = self._estimate_key(chroma)
        features['key'] = key_name
        features['key_confidence'] = float(key_confidence)
        
        # Harmonic-percussive separation
        harmonic, percussive = librosa.effects.hpss(audio)
        
        # Measure harmonic vs percussive ratio
        harmonic_energy = np.sum(harmonic ** 2)
        percussive_energy = np.sum(percussive ** 2)
        total_energy = harmonic_energy + percussive_energy
        
        if total_energy > 0:
            features['harmonic_ratio'] = float(harmonic_energy / total_energy)
            features['percussive_ratio'] = float(percussive_energy / total_energy)
        else:
            features['harmonic_ratio'] = 0.5
            features['percussive_ratio'] = 0.5
        
        # Rhythm patterns
        tempogram = librosa.feature.tempogram(
            y=audio,
            sr=self.sample_rate
        )
        features['rhythm_strength'] = float(np.mean(np.abs(tempogram)))
        
        logger.info(f"Musical analysis complete: Tempo={tempo:.1f} BPM, Key={key_name}")
        
        return features
    
    def _estimate_key(
        self, 
        chroma: np.ndarray
    ) -> Tuple[str, float]:
        """
        Estimate musical key from chroma features
        
        Args:
            chroma: Chroma features
            
        Returns:
            Tuple of (key_name, confidence)
        """
        # Average chroma over time
        chroma_mean = np.mean(chroma, axis=1)
        
        # Normalize
        chroma_mean = chroma_mean / (np.sum(chroma_mean) + 1e-10)
        
        # Key profiles (Krumhansl-Schmuckler)
        major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 
                                 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53,
                                 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
        
        # Normalize profiles
        major_profile = major_profile / np.sum(major_profile)
        minor_profile = minor_profile / np.sum(minor_profile)
        
        # Note names
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 
                'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        # Try all rotations for major and minor
        max_corr = -1
        best_key = 'C major'
        
        for i in range(12):
            # Rotate chroma
            rotated = np.roll(chroma_mean, i)
            
            # Correlate with major
            corr_major = np.corrcoef(rotated, major_profile)[0, 1]
            if corr_major > max_corr:
                max_corr = corr_major
                best_key = f"{notes[i]} major"
            
            # Correlate with minor
            corr_minor = np.corrcoef(rotated, minor_profile)[0, 1]
            if corr_minor > max_corr:
                max_corr = corr_minor
                best_key = f"{notes[i]} minor"
        
        confidence = max(0.0, min(1.0, max_corr))
        
        return best_key, confidence
    
    def detect_transients(
        self, 
        audio: np.ndarray,
        threshold: float = 0.5
    ) -> np.ndarray:
        """
        Detect transient positions
        
        Args:
            audio: Audio signal
            threshold: Detection threshold
            
        Returns:
            Array of transient times in seconds
        """
        # Onset strength
        onset_env = librosa.onset.onset_strength(
            y=audio,
            sr=self.sample_rate
        )
        
        # Detect onsets
        onsets = librosa.onset.onset_detect(
            onset_envelope=onset_env,
            sr=self.sample_rate,
            units='time',
            backtrack=True
        )
        
        return onsets
    
    def analyze_groove(
        self, 
        audio: np.ndarray
    ) -> Dict:
        """
        Analyze rhythmic groove and timing
        
        Args:
            audio: Audio signal
            
        Returns:
            Dictionary with groove features
        """
        # Tempo and beats
        tempo, beat_frames = librosa.beat.beat_track(
            y=audio,
            sr=self.sample_rate
        )
        
        # Convert to times
        beat_times = librosa.frames_to_time(
            beat_frames,
            sr=self.sample_rate
        )
        
        # Calculate inter-beat intervals
        if len(beat_times) > 1:
            intervals = np.diff(beat_times)
            
            # Groove consistency (lower std = more consistent)
            groove_consistency = 1.0 - min(1.0, np.std(intervals) / np.mean(intervals))
            
            # Swing ratio (if applicable)
            if len(intervals) >= 4:
                # Compare even vs odd intervals
                even_intervals = intervals[::2]
                odd_intervals = intervals[1::2]
                
                min_len = min(len(even_intervals), len(odd_intervals))
                if min_len > 0:
                    swing_ratio = np.mean(even_intervals[:min_len]) / (
                        np.mean(odd_intervals[:min_len]) + 1e-10
                    )
                else:
                    swing_ratio = 1.0
            else:
                swing_ratio = 1.0
        else:
            groove_consistency = 0.0
            swing_ratio = 1.0
        
        return {
            'tempo': float(tempo),
            'beat_times': beat_times,
            'groove_consistency': float(groove_consistency),
            'swing_ratio': float(swing_ratio)
        }
    
    def detect_sections(
        self, 
        audio: np.ndarray,
        min_section_length: float = 8.0
    ) -> np.ndarray:
        """
        Detect structural sections (intro, verse, chorus, etc.)
        
        Args:
            audio: Audio signal
            min_section_length: Minimum section length in seconds
            
        Returns:
            Array of section boundary times
        """
        # Compute chroma features
        chroma = librosa.feature.chroma_cqt(
            y=audio,
            sr=self.sample_rate
        )
        
        # Compute self-similarity matrix
        similarity = librosa.segment.recurrence_matrix(
            chroma,
            mode='affinity'
        )
        
        # Detect boundaries
        boundaries = librosa.segment.agglomerative(
            similarity,
            k=None  # Auto-detect number of segments
        )
        
        # Convert to times
        boundary_times = librosa.frames_to_time(
            boundaries,
            sr=self.sample_rate
        )
        
        # Filter out sections that are too short
        if len(boundary_times) > 1:
            filtered_boundaries = [boundary_times[0]]
            for i in range(1, len(boundary_times)):
                if boundary_times[i] - filtered_boundaries[-1] >= min_section_length:
                    filtered_boundaries.append(boundary_times[i])
            boundary_times = np.array(filtered_boundaries)
        
        return boundary_times
