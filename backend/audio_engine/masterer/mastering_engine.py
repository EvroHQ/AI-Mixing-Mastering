"""
Professional Mastering Engine - Genre-Aware Version
Grammy-level mastering chain with genre-specific processing
"""

import numpy as np
from typing import Dict, Optional, List, Any
import logging

from ..analyzer import LoudnessAnalyzer
from ..mixer.effects import StudioEQ, StereoProcessor
from .pro_limiter import ProLimiter
from .pro_saturator import ProSaturator
from .pro_multiband import ProMultibandCompressor

logger = logging.getLogger(__name__)


class MasteringEngine:
    """
    Professional mastering engine with genre-aware processing.
    Applies EQ, multiband compression, saturation, and limiting
    based on genre-specific presets.
    """
    
    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate
        self.eq = StudioEQ(sample_rate)
        self.multiband = ProMultibandCompressor(sample_rate)
        self.saturator = ProSaturator(sample_rate)
        self.limiter = ProLimiter(sample_rate)
        self.stereo = StereoProcessor(sample_rate)
        self.loudness_analyzer = LoudnessAnalyzer(sample_rate)
    
    def master(
        self,
        audio: np.ndarray,
        target_lufs: float = -14.0,
        ceiling_dbTP: float = -1.0,
        max_width_percent: int = 140,
        preset: str = 'balanced',
        tempo_bpm: Optional[float] = None,
        genre_preset: Optional[Dict[str, Any]] = None
    ) -> Dict:
        """
        Master audio with professional genre-aware chain.
        
        Args:
            audio: Input audio array
            target_lufs: Target loudness
            ceiling_dbTP: True peak ceiling
            max_width_percent: Maximum stereo width
            preset: Preset name (used if no genre_preset)
            tempo_bpm: Detected tempo for BPM-synced processing
            genre_preset: Genre-specific mastering settings
            
        Returns:
            Dict with mastered audio and processing report
        """
        logger.info(f"Starting mastering (target: {target_lufs} LUFS, preset: {preset})...")
        
        processing_log = []
        
        # Use genre preset if available, else use defaults
        if genre_preset:
            logger.info(f"Using genre-specific mastering preset")
            eq_bands = genre_preset.get('eq', [])
            multiband_settings = genre_preset.get('multiband', None)
            saturation_settings = genre_preset.get('saturation', {})
            stereo_width = genre_preset.get('stereo_width', max_width_percent)
            limiter_settings = genre_preset.get('limiter', {})
        else:
            # Default conservative settings
            eq_bands = [
                {'type': 'low_shelf', 'frequency': 60, 'gain': 0.5, 'q': 0.7},
                {'type': 'peak', 'frequency': 200, 'gain': -0.5, 'q': 1.5},
                {'type': 'peak', 'frequency': 3000, 'gain': 1.0, 'q': 1.5},
                {'type': 'high_shelf', 'frequency': 10000, 'gain': 1.0, 'q': 0.7}
            ]
            multiband_settings = None
            saturation_settings = {'tape': 0.15, 'tube': 0.10}
            stereo_width = max_width_percent
            limiter_settings = {'ceiling': ceiling_dbTP, 'release': 100}
        
        # Step 1: Linear-Phase EQ
        logger.info("Applying mastering EQ...")
        if eq_bands:
            audio = self.eq.linear_phase_eq(audio, eq_bands)
            processing_log.append(f"EQ: {len(eq_bands)} bands")
        
        # Step 2: Multiband Compression
        logger.info("Applying multiband compression...")
        if multiband_settings:
            try:
                result = self.multiband.process(
                    audio,
                    crossovers=multiband_settings.get('crossovers', [100, 500, 2000, 8000]),
                    thresholds=multiband_settings.get('thresholds', [-15, -15, -15, -15, -15]),
                    ratios=multiband_settings.get('ratios', [2.0, 2.0, 2.0, 2.0, 2.0]),
                    attacks=multiband_settings.get('attacks', [10, 10, 10, 10, 10]),
                    releases=multiband_settings.get('releases', [100, 100, 100, 100, 100]),
                    auto_makeup=True,
                    parallel_mix=0.3
                )
                audio = result['audio']
                processing_log.append(f"Multiband: {len(multiband_settings['crossovers'])+1} bands")
            except Exception as e:
                logger.warning(f"Multiband compression failed: {e}, skipping...")
        
        # Step 3: Saturation
        logger.info("Applying saturation...")
        if saturation_settings:
            tape_amount = saturation_settings.get('tape', 0.15)
            tube_amount = saturation_settings.get('tube', 0.10)
            
            if tape_amount > 0:
                audio = self.saturator.tape_saturation(audio, drive=tape_amount, mix=0.3)
                processing_log.append(f"Tape saturation: {tape_amount:.0%}")
            
            if tube_amount > 0:
                audio = self.saturator.tube_saturation(audio, drive=tube_amount, warmth=0.2, mix=0.25)
                processing_log.append(f"Tube saturation: {tube_amount:.0%}")
        
        # Step 4: Stereo Width
        logger.info("Adjusting stereo width...")
        if audio.ndim > 1 and stereo_width != 100:
            audio = self.stereo.adjust_width(audio, stereo_width, safe_bass=True)
            processing_log.append(f"Stereo width: {stereo_width}%")
        
        # Step 5: Loudness Normalization (pre-limiting)
        logger.info("Normalizing loudness...")
        audio = self.loudness_analyzer.normalize_to_lufs(audio, target_lufs + 2)  # Leave headroom for limiter
        
        # Step 6: True-Peak Limiting
        logger.info("Applying true-peak limiting...")
        limiter_ceiling = limiter_settings.get('ceiling', ceiling_dbTP)
        release_ms = limiter_settings.get('release', 100)
        
        # BPM-synced release if tempo available
        if tempo_bpm and tempo_bpm > 0:
            beat_duration_ms = (60.0 / tempo_bpm) * 1000
            release_ms = min(release_ms, beat_duration_ms / 2)
            logger.info(f"  BPM-synced limiter: {tempo_bpm} BPM = {release_ms:.0f}ms")
        
        audio = self.limiter.multi_stage_limit(
            audio,
            ceiling_db=limiter_ceiling,
            stages=3,
            release_ms=release_ms
        )
        processing_log.append(f"Limiter: {limiter_ceiling} dBTP")
        
        # Step 7: Final Loudness Match
        logger.info("Final loudness matching...")
        audio = self._final_loudness_match(audio, target_lufs, limiter_ceiling)
        
        # Final analysis
        final_metrics = self.loudness_analyzer.analyze(audio)
        
        logger.info(f"Mastering complete! LUFS={final_metrics['lufs_integrated']:.1f}, TP={final_metrics['true_peak_dbTP']:.1f} dBTP")
        
        return {
            'audio': audio,
            'report': {
                'processing_chain': processing_log,
                'final_metrics': {
                    'lufs': final_metrics['lufs_integrated'],
                    'lufs_target': target_lufs,
                    'lufs_delta': final_metrics['lufs_integrated'] - target_lufs,
                    'true_peak_dbTP': final_metrics['true_peak_dbTP'],
                    'lra': final_metrics['lra'],
                    'crest_factor': final_metrics['crest_factor'],
                    'dynamic_range_db': final_metrics.get('dynamic_range', 0.0)
                },
                'mono_compatibility': self._check_mono_compatibility(audio),
                'qc_results': self._auto_qc(final_metrics, target_lufs, limiter_ceiling),
                'warnings': self._generate_warnings(final_metrics, target_lufs)
            },
            'sample_rate': self.sample_rate
        }
    
    def _final_loudness_match(
        self,
        audio: np.ndarray,
        target_lufs: float,
        ceiling_dbTP: float
    ) -> np.ndarray:
        """Final loudness adjustment with iterative limiting."""
        
        max_iterations = 3
        
        for i in range(max_iterations):
            metrics = self.loudness_analyzer.analyze(audio)
            lufs_delta = target_lufs - metrics['lufs_integrated']
            
            if abs(lufs_delta) < 0.5:
                break
            
            # Apply gain adjustment
            gain_db = lufs_delta * 0.7  # Conservative adjustment
            gain_linear = 10 ** (gain_db / 20)
            audio = audio * gain_linear
            
            # Re-limit if needed
            if metrics['true_peak_dbTP'] > ceiling_dbTP:
                audio = self.limiter.process(audio, ceiling_db=ceiling_dbTP)
        
        return audio
    
    def _check_mono_compatibility(self, audio: np.ndarray) -> Dict:
        """Check mono compatibility of stereo audio."""
        
        if audio.ndim < 2:
            return {'mono_compatible': True, 'correlation': 1.0}
        
        left = audio[0]
        right = audio[1]
        
        # Calculate correlation
        correlation = np.corrcoef(left, right)[0, 1]
        
        # Check for phase issues
        mono = left + right
        mono_rms = np.sqrt(np.mean(mono ** 2))
        stereo_rms = np.sqrt(np.mean((left ** 2 + right ** 2)))
        
        ratio = mono_rms / (stereo_rms + 1e-10)
        
        return {
            'mono_compatible': correlation > 0.5 and ratio > 0.7,
            'correlation': float(correlation),
            'mono_stereo_ratio': float(ratio)
        }
    
    def _auto_qc(
        self,
        metrics: Dict,
        target_lufs: float,
        ceiling_dbTP: float
    ) -> Dict:
        """Automatic quality control checks."""
        
        lufs_ok = abs(metrics['lufs_integrated'] - target_lufs) < 1.0
        tp_ok = metrics['true_peak_dbTP'] <= ceiling_dbTP + 0.1
        crest_ok = metrics['crest_factor'] >= 3.0
        lra_ok = metrics['lra'] >= 3.0
        
        return {
            'lufs_safe': lufs_ok,
            'true_peak_safe': tp_ok,
            'crest_factor_safe': crest_ok,
            'lra_safe': lra_ok,
            'all_safe': lufs_ok and tp_ok and crest_ok and lra_ok
        }
    
    def _generate_warnings(
        self,
        metrics: Dict,
        target_lufs: float
    ) -> List[str]:
        """Generate warnings for potential issues."""
        
        warnings = []
        
        if metrics['crest_factor'] < 4.0:
            warnings.append("Low crest factor - may sound over-compressed")
        
        if metrics['lra'] < 4.0:
            warnings.append("Low loudness range - limited dynamics")
        
        if abs(metrics['lufs_integrated'] - target_lufs) > 1.0:
            warnings.append(f"LUFS deviation: {metrics['lufs_integrated']:.1f} vs target {target_lufs}")
        
        return warnings
