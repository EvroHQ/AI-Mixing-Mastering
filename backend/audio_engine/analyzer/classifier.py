"""
Audio Analyzer - Source Classification
Automatically classifies stems (kick, bass, vocal, etc.)
"""

import numpy as np
import librosa
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class SourceClassifier:
    """
    Classifies audio stems based on spectral and temporal features
    """
    
    def __init__(self, sample_rate: int = 48000):
        """
        Initialize source classifier
        
        Args:
            sample_rate: Audio sample rate
        """
        self.sample_rate = sample_rate
        
        # Feature thresholds for classification
        self.thresholds = {
            'kick': {
                'low_energy_ratio': 0.4,      # >40% energy in sub/bass
                'transient_strength': 0.6,     # Strong transients
                'harmonic_ratio': 0.3,         # Low harmonics
                'spectral_centroid': 200       # Low centroid
            },
            'bass': {
                'low_energy_ratio': 0.5,       # >50% energy in bass
                'harmonic_ratio': 0.6,         # More harmonic
                'spectral_centroid': 300       # Low centroid
            },
            'snare': {
                'mid_energy_ratio': 0.3,       # Energy in mids
                'transient_strength': 0.7,     # Very strong transients
                'spectral_centroid': 2000      # Mid-high centroid
            },
            'hihat': {
                'high_energy_ratio': 0.6,      # >60% energy in highs
                'transient_strength': 0.5,     # Moderate transients
                'spectral_centroid': 8000      # High centroid
            },
            'vocal': {
                'mid_energy_ratio': 0.4,       # Energy in mids
                'harmonic_ratio': 0.7,         # Very harmonic
                'spectral_centroid': 1000,     # Mid centroid
                'formant_presence': 0.5        # Formant structure
            },
            'synth': {
                'harmonic_ratio': 0.6,         # Harmonic
                'spectral_centroid': 1500      # Variable centroid
            },
            'guitar': {
                'harmonic_ratio': 0.65,        # Harmonic
                'mid_energy_ratio': 0.35,      # Mid energy
                'spectral_centroid': 1200      # Mid centroid
            },
            'piano': {
                'harmonic_ratio': 0.75,        # Very harmonic
                'transient_strength': 0.4,     # Moderate transients
                'spectral_centroid': 800       # Mid-low centroid
            }
        }
    
    def classify(
        self,
        audio: np.ndarray,
        name: str = "unknown"
    ) -> Tuple[str, float]:
        """
        Classify audio stem
        
        Args:
            audio: Audio signal (mono or stereo)
            name: Stem name (for logging)
            
        Returns:
            Tuple of (classification, confidence)
        """
        logger.info(f"Classifying stem: {name}")
        
        # STEP 1: Try to classify by filename FIRST (most reliable!)
        filename_class = self._classify_by_filename(name)
        if filename_class:
            logger.info(f"Classified {name} as {filename_class} (from filename)")
            return filename_class, 1.0
        
        # STEP 2: Fall back to audio analysis
        # Convert stereo to mono if needed
        if audio.ndim > 1:
            audio = np.mean(audio, axis=0)
        
        # Extract features
        features = self._extract_features(audio)
        
        # Score each category
        scores = {}
        for category in self.thresholds.keys():
            score = self._score_category(features, category)
            scores[category] = score
        
        # Get best match
        best_category = max(scores, key=scores.get)
        confidence = scores[best_category]
        
        logger.info(f"Classified {name} as {best_category} (confidence: {confidence:.2f})")
        
        return best_category, confidence
    
    def _classify_by_filename(self, name: str) -> str:
        """
        Classify stem by filename keywords
        
        Args:
            name: Stem/file name
            
        Returns:
            Classification or None if no match
        """
        name_lower = name.lower()
        
        # Kick/drums patterns
        kick_patterns = ['kick', 'bd', 'bassdrum', '808', 'boom']
        for p in kick_patterns:
            if p in name_lower:
                return 'kick'
        
        # Bass patterns
        bass_patterns = ['bass', 'sub', 'low end', 'lowend']
        for p in bass_patterns:
            if p in name_lower:
                return 'bass'
        
        # Snare patterns
        snare_patterns = ['snare', 'sd', 'clap', 'rimshot', 'snr']
        for p in snare_patterns:
            if p in name_lower:
                return 'snare'
        
        # Hi-hat patterns
        hihat_patterns = ['hi-hat', 'hihat', 'hh', 'hat', 'shaker', 'cymbal', 'ride', 'crash']
        for p in hihat_patterns:
            if p in name_lower:
                return 'hihat'
        
        # Percussion patterns
        perc_patterns = ['perc', 'conga', 'bongo', 'tom', 'toms', 'tamb']
        for p in perc_patterns:
            if p in name_lower:
                return 'percussion'
        
        # Drums (general)
        drum_patterns = ['drum', 'drums', 'beat', 'loop']
        for p in drum_patterns:
            if p in name_lower:
                return 'drums'
        
        # Vocal patterns
        vocal_patterns = ['vocal', 'vox', 'voice', 'sing', 'adlib', 'hook', 'verse', 'chorus']
        for p in vocal_patterns:
            if p in name_lower:
                return 'vocal'
        
        # Synth patterns
        synth_patterns = ['synth', 'pad', 'lead', 'arp', 'pluck', 'stab', 'chord']
        for p in synth_patterns:
            if p in name_lower:
                return 'synth'
        
        # Piano/keys patterns
        piano_patterns = ['piano', 'keys', 'keyboard', 'organ', 'rhodes', 'wurli', 'ep']
        for p in piano_patterns:
            if p in name_lower:
                return 'piano'
        
        # Guitar patterns
        guitar_patterns = ['guitar', 'gtr', 'acoustic', 'electric', 'strum']
        for p in guitar_patterns:
            if p in name_lower:
                return 'guitar'
        
        # Strings patterns
        strings_patterns = ['string', 'violin', 'cello', 'orchestra']
        for p in strings_patterns:
            if p in name_lower:
                return 'synth'  # Treat strings as synth for processing
        
        # FX patterns
        fx_patterns = ['fx', 'effect', 'riser', 'impact', 'sweep', 'noise', 'atmos', 'ambient']
        for p in fx_patterns:
            if p in name_lower:
                return 'fx'
        
        # No match - return None to trigger audio analysis
        return None
    
    def _extract_features(self, audio: np.ndarray) -> Dict:
        """
        Extract classification features from audio
        
        Args:
            audio: Audio signal
            
        Returns:
            Dictionary of features
        """
        features = {}
        
        # Spectral features
        stft = librosa.stft(audio)
        magnitude = np.abs(stft)
        
        # Spectral centroid
        centroid = librosa.feature.spectral_centroid(
            y=audio,
            sr=self.sample_rate
        )
        features['spectral_centroid'] = np.mean(centroid)
        
        # Energy distribution by frequency bands
        freqs = librosa.fft_frequencies(sr=self.sample_rate)
        
        # Low energy (20-250 Hz)
        low_mask = (freqs >= 20) & (freqs < 250)
        low_energy = np.sum(magnitude[low_mask, :])
        
        # Mid energy (250-4000 Hz)
        mid_mask = (freqs >= 250) & (freqs < 4000)
        mid_energy = np.sum(magnitude[mid_mask, :])
        
        # High energy (4000-20000 Hz)
        high_mask = (freqs >= 4000) & (freqs < 20000)
        high_energy = np.sum(magnitude[high_mask, :])
        
        total_energy = low_energy + mid_energy + high_energy + 1e-10
        
        features['low_energy_ratio'] = low_energy / total_energy
        features['mid_energy_ratio'] = mid_energy / total_energy
        features['high_energy_ratio'] = high_energy / total_energy
        
        # Harmonic vs percussive
        harmonic, percussive = librosa.effects.hpss(audio)
        
        harmonic_energy = np.sum(harmonic ** 2)
        percussive_energy = np.sum(percussive ** 2)
        total_hp_energy = harmonic_energy + percussive_energy + 1e-10
        
        features['harmonic_ratio'] = harmonic_energy / total_hp_energy
        features['percussive_ratio'] = percussive_energy / total_hp_energy
        
        # Transient strength
        onset_env = librosa.onset.onset_strength(
            y=audio,
            sr=self.sample_rate
        )
        features['transient_strength'] = np.mean(onset_env) / (np.max(onset_env) + 1e-10)
        
        # Formant presence (for vocals)
        # Check for energy peaks in formant regions (500-3000 Hz)
        formant_mask = (freqs >= 500) & (freqs < 3000)
        formant_spectrum = np.mean(magnitude[formant_mask, :], axis=1)
        
        # Detect peaks in formant region
        from scipy.signal import find_peaks
        peaks, _ = find_peaks(formant_spectrum, height=np.mean(formant_spectrum))
        
        features['formant_presence'] = len(peaks) / 10.0  # Normalize
        
        # Zero crossing rate (for noise/hi-hats)
        zcr = librosa.feature.zero_crossing_rate(audio)
        features['zero_crossing_rate'] = np.mean(zcr)
        
        return features
    
    def _score_category(
        self,
        features: Dict,
        category: str
    ) -> float:
        """
        Score how well features match a category
        
        Args:
            features: Extracted features
            category: Category to score
            
        Returns:
            Score (0-1)
        """
        thresholds = self.thresholds[category]
        
        scores = []
        
        # Check each threshold
        for feature_name, threshold in thresholds.items():
            if feature_name not in features:
                continue
            
            feature_value = features[feature_name]
            
            # Different scoring based on feature type
            if 'ratio' in feature_name or 'presence' in feature_name:
                # For ratios, check if above threshold
                if feature_value >= threshold:
                    score = min(1.0, feature_value / threshold)
                else:
                    score = feature_value / threshold
            
            elif 'centroid' in feature_name or 'strength' in feature_name:
                # For centroids, check proximity
                if 'centroid' in feature_name:
                    # Closer to threshold is better
                    distance = abs(feature_value - threshold)
                    max_distance = threshold  # Normalize by threshold
                    score = max(0, 1.0 - (distance / max_distance))
                else:
                    # For strength, check if above threshold
                    if feature_value >= threshold:
                        score = min(1.0, feature_value / threshold)
                    else:
                        score = feature_value / threshold
            
            else:
                # Default: proximity scoring
                score = 1.0 / (1.0 + abs(feature_value - threshold))
            
            scores.append(score)
        
        # Average score
        if scores:
            return np.mean(scores)
        else:
            return 0.0
    
    def classify_multiple(
        self,
        stems: Dict[str, np.ndarray]
    ) -> Dict[str, Tuple[str, float]]:
        """
        Classify multiple stems
        
        Args:
            stems: Dictionary of {name: audio}
            
        Returns:
            Dictionary of {name: (classification, confidence)}
        """
        classifications = {}
        
        for name, audio in stems.items():
            classification, confidence = self.classify(audio, name)
            classifications[name] = (classification, confidence)
        
        return classifications
    
    def get_stem_roles(
        self,
        classifications: Dict[str, Tuple[str, float]]
    ) -> Dict[str, str]:
        """
        Convert classifications to simple role mapping
        
        Args:
            classifications: Dictionary of {name: (classification, confidence)}
            
        Returns:
            Dictionary of {name: role}
        """
        roles = {}
        
        for name, (classification, confidence) in classifications.items():
            # Use classification if confidence is high enough
            if confidence > 0.5:
                roles[name] = classification
            else:
                # Default to 'other' if uncertain
                roles[name] = 'other'
        
        return roles
