"""
Intelligent Mix Balancer
AI-powered stem level balancing and gain staging
"""

import numpy as np
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class IntelligentMixBalancer:
    """
    Intelligent mix balancer that analyzes stems and calculates optimal levels
    """
    
    def __init__(self, sample_rate: int = 48000):
        """
        Initialize mix balancer
        
        Args:
            sample_rate: Audio sample rate
        """
        self.sample_rate = sample_rate
        
        # Reference levels for different stem roles (in dB relative to mix)
        self.reference_levels = {
            'kick': -6.0,          # Kick should be prominent
            'bass': -8.0,          # Bass slightly below kick
            'snare': -10.0,        # Snare punchy but not overpowering
            'drums': -8.0,         # Full drum bus
            'vocal': -8.0,         # Vocals prominent
            'lead_vocal': -7.0,    # Lead vocal most prominent
            'backing_vocal': -12.0, # Backing vocals supporting
            'synth': -12.0,        # Synths in background
            'pad': -14.0,          # Pads atmospheric
            'lead': -10.0,         # Lead instruments present
            'guitar': -11.0,       # Guitars supporting
            'piano': -11.0,        # Piano supporting
            'strings': -13.0,      # Strings atmospheric
            'fx': -16.0,           # Effects subtle
            'other': -12.0         # Default for unknown
        }
    
    def calculate_optimal_levels(
        self,
        stems: Dict[str, np.ndarray],
        stem_roles: Dict[str, str],
        target_lufs: float = -14.0
    ) -> Dict[str, float]:
        """
        Calculate optimal gain for each stem based on intelligent analysis
        
        Args:
            stems: Dictionary of {stem_name: audio}
            stem_roles: Dictionary of {stem_name: role}
            target_lufs: Target loudness for final mix
            
        Returns:
            Dictionary of {stem_name: gain_db}
        """
        logger.info("Calculating intelligent mix balance...")
        
        optimal_gains = {}
        
        # Step 1: Analyze each stem
        stem_analysis = {}
        for name, audio in stems.items():
            analysis = self._analyze_stem(audio)
            stem_analysis[name] = analysis
            logger.info(f"  {name}: RMS={analysis['rms_db']:.1f}dB, Peak={analysis['peak_db']:.1f}dB, Crest={analysis['crest_factor']:.1f}")
        
        # Step 2: Calculate reference mix level
        # Use the loudest stem as reference
        max_rms = max(a['rms_db'] for a in stem_analysis.values())
        
        # Step 3: Calculate gain for each stem
        for name, audio in stems.items():
            role = stem_roles.get(name, 'other')
            analysis = stem_analysis[name]
            
            # Get target level for this role
            target_level = self.reference_levels.get(role, -12.0)
            
            # Calculate gain needed
            # We want this stem at target_level dB relative to the loudest stem
            current_level = analysis['rms_db']
            desired_level = max_rms + target_level
            
            gain_db = desired_level - current_level
            
            # Apply intelligent limiting
            # Don't boost too much (max +12dB) or cut too much (max -24dB)
            gain_db = np.clip(gain_db, -24.0, 12.0)
            
            # Special handling for very quiet stems
            if analysis['rms_db'] < -60.0:
                logger.warning(f"  {name} is very quiet (RMS={analysis['rms_db']:.1f}dB), limiting boost")
                gain_db = min(gain_db, 6.0)
            
            # Special handling for very loud stems
            if analysis['peak_db'] > -3.0:
                logger.warning(f"  {name} is very loud (Peak={analysis['peak_db']:.1f}dB), applying cut")
                peak_reduction = analysis['peak_db'] - (-6.0)  # Target -6dB peak
                gain_db = min(gain_db, -peak_reduction)
            
            optimal_gains[name] = gain_db
            logger.info(f"  {name} ({role}): {gain_db:+.1f}dB")
        
        return optimal_gains
    
    def apply_intelligent_balance(
        self,
        stems: Dict[str, np.ndarray],
        stem_roles: Dict[str, str]
    ) -> Dict[str, np.ndarray]:
        """
        Apply intelligent balancing to all stems
        
        Args:
            stems: Dictionary of stems
            stem_roles: Dictionary of stem roles
            
        Returns:
            Dictionary of balanced stems
        """
        # Calculate optimal gains
        optimal_gains = self.calculate_optimal_levels(stems, stem_roles)
        
        # Apply gains
        balanced_stems = {}
        for name, audio in stems.items():
            gain_db = optimal_gains[name]
            gain_linear = 10 ** (gain_db / 20)
            balanced_stems[name] = audio * gain_linear
            
        logger.info("✓ Intelligent balance applied")
        return balanced_stems
    
    def _analyze_stem(self, audio: np.ndarray) -> Dict:
        """
        Analyze a single stem
        
        Args:
            audio: Audio signal
            
        Returns:
            Dictionary with analysis metrics
        """
        # Convert to mono for analysis
        if audio.ndim > 1:
            audio_mono = np.mean(audio, axis=0)
        else:
            audio_mono = audio
        
        # Calculate RMS (average loudness)
        rms = np.sqrt(np.mean(audio_mono ** 2))
        rms_db = 20 * np.log10(rms + 1e-10)
        
        # Calculate peak
        peak = np.max(np.abs(audio_mono))
        peak_db = 20 * np.log10(peak + 1e-10)
        
        # Calculate crest factor (peak/RMS ratio)
        crest_factor = peak / (rms + 1e-10)
        
        # Calculate dynamic range estimate
        # Use 95th percentile to avoid outliers
        sorted_abs = np.sort(np.abs(audio_mono))
        percentile_95 = sorted_abs[int(len(sorted_abs) * 0.95)]
        percentile_5 = sorted_abs[int(len(sorted_abs) * 0.05)]
        dynamic_range = 20 * np.log10((percentile_95 + 1e-10) / (percentile_5 + 1e-10))
        
        return {
            'rms': rms,
            'rms_db': rms_db,
            'peak': peak,
            'peak_db': peak_db,
            'crest_factor': crest_factor,
            'dynamic_range_db': dynamic_range
        }
    
    def calculate_bus_gains(
        self,
        buses: Dict[str, np.ndarray]
    ) -> Dict[str, float]:
        """
        Calculate optimal gains for buses
        
        Args:
            buses: Dictionary of bus audio
            
        Returns:
            Dictionary of bus gains in dB
        """
        bus_gains = {}
        
        # Analyze each bus
        for name, audio in buses.items():
            analysis = self._analyze_stem(audio)
            
            # Target: -12dB RMS for buses
            target_rms = -12.0
            gain_db = target_rms - analysis['rms_db']
            gain_db = np.clip(gain_db, -18.0, 6.0)
            
            bus_gains[name] = gain_db
            logger.info(f"Bus {name}: {gain_db:+.1f}dB")
        
        return bus_gains
