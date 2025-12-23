"""
Audio Analyzer - Spectral Masking Detection
Detects frequency conflicts between stems for intelligent mixing
"""

import numpy as np
import librosa
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class MaskingAnalyzer:
    """
    Detects spectral masking between audio stems
    This allows stems to "communicate" and avoid frequency conflicts
    """
    
    def __init__(
        self,
        sample_rate: int = 48000,
        n_fft: int = 2048,
        hop_length: int = 512
    ):
        """
        Initialize masking analyzer
        
        Args:
            sample_rate: Audio sample rate
            n_fft: FFT window size
            hop_length: Hop length for STFT
        """
        self.sample_rate = sample_rate
        self.n_fft = n_fft
        self.hop_length = hop_length
        
        # Critical frequency bands for masking detection
        self.critical_bands = {
            'kick_fundamental': (40, 80),      # Kick fundamental
            'bass_fundamental': (80, 200),     # Bass fundamental
            'low_mids': (200, 500),            # Low mids (muddiness)
            'vocal_fundamental': (200, 800),   # Vocal fundamentals
            'presence': (2000, 5000),          # Vocal presence
            'sibilance': (5000, 10000),        # Sibilance
            'air': (10000, 20000)              # Air/brilliance
        }
    
    def analyze_masking_between_stems(
        self,
        stems: Dict[str, np.ndarray],
        stem_roles: Dict[str, str]
    ) -> Dict:
        """
        Analyze spectral masking between all stems
        
        Args:
            stems: Dictionary of {stem_name: audio_signal}
            stem_roles: Dictionary of {stem_name: role} 
                       (e.g., 'kick', 'bass', 'vocal', 'synth')
            
        Returns:
            Dictionary with masking analysis and recommendations
        """
        logger.info(f"Analyzing masking between {len(stems)} stems...")
        
        # Compute spectrograms for all stems
        spectrograms = {}
        for name, audio in stems.items():
            # Convert stereo to mono if needed
            if audio.ndim > 1:
                audio = np.mean(audio, axis=0)
            
            stft = librosa.stft(
                audio,
                n_fft=self.n_fft,
                hop_length=self.hop_length
            )
            spectrograms[name] = np.abs(stft)
        
        # Analyze conflicts
        conflicts = []
        recommendations = {}
        
        # Check specific stem pairs that commonly conflict
        conflict_pairs = [
            ('kick', 'bass', 'kick_fundamental'),
            ('kick', 'bass', 'bass_fundamental'),
            ('vocal', 'synth', 'vocal_fundamental'),
            ('vocal', 'synth', 'presence'),
            ('vocal', 'guitar', 'presence'),
            ('snare', 'vocal', 'presence')
        ]
        
        for stem1_role, stem2_role, band_name in conflict_pairs:
            # Find stems with these roles
            stem1_names = [n for n, r in stem_roles.items() if r == stem1_role]
            stem2_names = [n for n, r in stem_roles.items() if r == stem2_role]
            
            for s1 in stem1_names:
                for s2 in stem2_names:
                    if s1 in spectrograms and s2 in spectrograms:
                        conflict = self._detect_conflict(
                            spectrograms[s1],
                            spectrograms[s2],
                            self.critical_bands[band_name],
                            s1,
                            s2
                        )
                        
                        if conflict['severity'] > 0.3:  # Significant conflict
                            conflicts.append(conflict)
                            
                            # Generate recommendation
                            rec = self._generate_recommendation(
                                conflict,
                                stem1_role,
                                stem2_role,
                                band_name
                            )
                            
                            key = f"{s1}_vs_{s2}"
                            recommendations[key] = rec
        
        # Analyze overall spectral balance
        balance = self._analyze_spectral_balance(spectrograms, stem_roles)
        
        result = {
            'conflicts': conflicts,
            'recommendations': recommendations,
            'spectral_balance': balance,
            'conflict_count': len(conflicts)
        }
        
        logger.info(f"Found {len(conflicts)} spectral conflicts")
        
        return result
    
    def _detect_conflict(
        self,
        spec1: np.ndarray,
        spec2: np.ndarray,
        freq_range: Tuple[float, float],
        name1: str,
        name2: str
    ) -> Dict:
        """
        Detect conflict between two spectrograms in a frequency range
        
        Args:
            spec1: First spectrogram
            spec2: Second spectrogram
            freq_range: Frequency range to analyze (low, high)
            name1: Name of first stem
            name2: Name of second stem
            
        Returns:
            Dictionary with conflict information
        """
        # Get frequency bins
        freqs = librosa.fft_frequencies(sr=self.sample_rate, n_fft=self.n_fft)
        
        # Find bins in range
        low, high = freq_range
        mask = (freqs >= low) & (freqs < high)
        
        # Extract energy in this range
        energy1 = np.mean(spec1[mask, :], axis=0)
        energy2 = np.mean(spec2[mask, :], axis=0)
        
        # Calculate overlap (correlation)
        if len(energy1) > 0 and len(energy2) > 0:
            # Normalize
            energy1_norm = energy1 / (np.max(energy1) + 1e-10)
            energy2_norm = energy2 / (np.max(energy2) + 1e-10)
            
            # Correlation
            correlation = np.corrcoef(energy1_norm, energy2_norm)[0, 1]
            
            # Overlap (both high at same time)
            overlap = np.mean(np.minimum(energy1_norm, energy2_norm))
            
            # Severity combines correlation and overlap
            severity = (correlation + overlap) / 2
        else:
            correlation = 0.0
            overlap = 0.0
            severity = 0.0
        
        return {
            'stem1': name1,
            'stem2': name2,
            'freq_range': freq_range,
            'correlation': float(correlation),
            'overlap': float(overlap),
            'severity': float(max(0, severity))  # Ensure non-negative
        }
    
    def _generate_recommendation(
        self,
        conflict: Dict,
        role1: str,
        role2: str,
        band_name: str
    ) -> Dict:
        """
        Generate mixing recommendation based on conflict
        
        Args:
            conflict: Conflict information
            role1: Role of first stem
            role2: Role of second stem
            band_name: Name of frequency band
            
        Returns:
            Dictionary with mixing recommendations
        """
        low, high = conflict['freq_range']
        center_freq = (low + high) / 2
        
        recommendation = {
            'action': 'sidechain_eq',
            'severity': conflict['severity']
        }
        
        # Determine which stem should be reduced
        # Priority order: kick > bass > vocal > other
        priority = {
            'kick': 5,
            'bass': 4,
            'vocal': 3,
            'snare': 2,
            'other': 1
        }
        
        priority1 = priority.get(role1, 1)
        priority2 = priority.get(role2, 1)
        
        if priority1 > priority2:
            # Reduce stem2
            recommendation['reduce_stem'] = conflict['stem2']
            recommendation['preserve_stem'] = conflict['stem1']
        else:
            # Reduce stem1
            recommendation['reduce_stem'] = conflict['stem1']
            recommendation['preserve_stem'] = conflict['stem2']
        
        # EQ recommendation
        recommendation['eq'] = {
            'stem': recommendation['reduce_stem'],
            'type': 'cut',
            'frequency': center_freq,
            'gain_db': -2.0 * conflict['severity'],  # Up to -2dB cut
            'q': 2.0  # Moderate Q
        }
        
        # Sidechain recommendation for kick-bass
        if (role1 == 'kick' and role2 == 'bass') or \
           (role1 == 'bass' and role2 == 'kick'):
            recommendation['sidechain'] = {
                'source': conflict['stem1'] if role1 == 'kick' else conflict['stem2'],
                'target': conflict['stem2'] if role1 == 'kick' else conflict['stem1'],
                'frequency_range': conflict['freq_range'],
                'reduction_db': 3.0 * conflict['severity'],  # Up to -3dB
                'attack_ms': 5.0,
                'release_ms': 100.0
            }
        
        return recommendation
    
    def _analyze_spectral_balance(
        self,
        spectrograms: Dict[str, np.ndarray],
        stem_roles: Dict[str, str]
    ) -> Dict:
        """
        Analyze overall spectral balance of the mix
        
        Args:
            spectrograms: Dictionary of spectrograms
            stem_roles: Dictionary of stem roles
            
        Returns:
            Dictionary with balance analysis
        """
        # Sum all spectrograms
        total_spec = sum(spectrograms.values())
        
        # Analyze energy in different bands
        freqs = librosa.fft_frequencies(sr=self.sample_rate, n_fft=self.n_fft)
        
        bands = {
            'sub_bass': (20, 60),
            'bass': (60, 250),
            'low_mids': (250, 500),
            'mids': (500, 2000),
            'high_mids': (2000, 4000),
            'highs': (4000, 10000),
            'air': (10000, 20000)
        }
        
        balance = {}
        total_energy = np.sum(total_spec)
        
        for band_name, (low, high) in bands.items():
            mask = (freqs >= low) & (freqs < high)
            band_energy = np.sum(total_spec[mask, :])
            balance[band_name] = float(band_energy / (total_energy + 1e-10))
        
        # Detect imbalances
        warnings = []
        
        if balance['bass'] < 0.15:
            warnings.append("Bass energy low - mix may sound thin")
        elif balance['bass'] > 0.35:
            warnings.append("Bass energy high - mix may sound muddy")
        
        if balance['mids'] < 0.20:
            warnings.append("Mid energy low - mix may lack body")
        
        if balance['highs'] < 0.10:
            warnings.append("High energy low - mix may sound dull")
        elif balance['highs'] > 0.25:
            warnings.append("High energy high - mix may sound harsh")
        
        return {
            'band_energies': balance,
            'warnings': warnings,
            'is_balanced': len(warnings) == 0
        }
