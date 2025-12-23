import librosa
import numpy as np
from typing import Dict, Any


class AudioAnalyzer:
    """Simplified audio analyzer using librosa (without Essentia)"""
    
    def __init__(self):
        self.sample_rate = 44100
    
    def analyze(self, audio_file: str) -> Dict[str, Any]:
        """
        Analyze audio file and extract features
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Dictionary with audio features
        """
        # Load audio
        y, sr = librosa.load(audio_file, sr=self.sample_rate)
        
        # Extract features
        features = {}
        
        # Tempo detection
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        features['tempo'] = float(tempo)
        
        # Key detection (simplified)
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        key = int(np.argmax(np.sum(chroma, axis=1)))
        features['key'] = key
        
        # RMS energy
        rms = librosa.feature.rms(y=y)[0]
        features['rms_mean'] = float(np.mean(rms))
        features['rms_std'] = float(np.std(rms))
        
        # Spectral centroid
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        features['spectral_centroid_mean'] = float(np.mean(spectral_centroids))
        
        # Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        features['zcr_mean'] = float(np.mean(zcr))
        
        # Instrument type classification (simplified heuristic)
        features['instrument_type'] = self._classify_instrument(features)
        
        # Duration
        features['duration'] = float(librosa.get_duration(y=y, sr=sr))
        
        return features
    
    def _classify_instrument(self, features: Dict[str, Any]) -> str:
        """
        Simple heuristic-based instrument classification
        
        Args:
            features: Extracted audio features
            
        Returns:
            Instrument type string
        """
        # Simple classification based on spectral features
        centroid = features.get('spectral_centroid_mean', 0)
        zcr = features.get('zcr_mean', 0)
        
        # Drums: high ZCR, broad spectrum
        if zcr > 0.1:
            return 'drums'
        
        # Bass: low spectral centroid
        elif centroid < 500:
            return 'bass'
        
        # Vocals: mid-range spectral centroid
        elif 500 <= centroid < 2000:
            return 'vocals'
        
        # Synth/other: high spectral centroid
        else:
            return 'synth'
