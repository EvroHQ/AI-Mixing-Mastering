"""
Mix Engine
Orchestrates the complete mixing process with intelligent stem communication
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

from ..analyzer import (
    SpectralAnalyzer,
    LoudnessAnalyzer,
    MusicalAnalyzer,
    MaskingAnalyzer,
    SourceClassifier
)
from .stem_processor import StemProcessor
from .bus_processor import BusProcessor
from .sidechain_matrix import SidechainMatrix
from .intelligent_balancer import IntelligentMixBalancer

logger = logging.getLogger(__name__)


class MixEngine:
    """
    Professional mixing engine with intelligent stem communication
    """
    
    def __init__(self, sample_rate: int = 48000):
        """
        Initialize mix engine
        
        Args:
            sample_rate: Audio sample rate
        """
        self.sample_rate = sample_rate
        
        # Initialize analyzers
        self.spectral_analyzer = SpectralAnalyzer(sample_rate)
        self.loudness_analyzer = LoudnessAnalyzer(sample_rate)
        self.musical_analyzer = MusicalAnalyzer(sample_rate)
        self.masking_analyzer = MaskingAnalyzer(sample_rate)
        self.classifier = SourceClassifier(sample_rate)
        
        # Initialize processors
        self.stem_processor = StemProcessor(sample_rate)
        self.bus_processor = BusProcessor(sample_rate)
        self.sidechain_matrix = SidechainMatrix(sample_rate)
        self.intelligent_balancer = IntelligentMixBalancer(sample_rate)
    
    def mix(
        self,
        stems: Dict[str, np.ndarray],
        stem_roles: Optional[Dict[str, str]] = None,
        target_lufs: float = -14.0,
        preset: Optional[str] = None,
        genre_preset: Optional[Dict] = None
    ) -> Dict:
        """
        Mix stems with intelligent processing
        
        Args:
            stems: Dictionary of {stem_name: audio}
            stem_roles: Optional dictionary of {stem_name: role}
                       If None, will auto-classify
            target_lufs: Target loudness for mix
            preset: Optional preset name
            genre_preset: Genre-specific mixing settings
            
        Returns:
            Dictionary with mixed audio and detailed report
        """
        logger.info(f"Starting mix process with {len(stems)} stems...")
        
        # Ensure all stems are same length
        stems = self._align_stems(stems)
        
        # Step 1: Classify stems if not provided
        if stem_roles is None:
            logger.info("Auto-classifying stems...")
            classifications = self.classifier.classify_multiple(stems)
            stem_roles = self.classifier.get_stem_roles(classifications)
            logger.info(f"Classifications: {stem_roles}")
        
        # Step 2: Analyze all stems
        logger.info("Analyzing stems...")
        analysis = self._analyze_stems(stems, stem_roles)
        
        # Step 3: Detect masking (stems communicate!)
        logger.info("Analyzing spectral masking (stem communication)...")
        masking_analysis = self.masking_analyzer.analyze_masking_between_stems(
            stems,
            stem_roles
        )
        
        logger.info(f"Found {masking_analysis['conflict_count']} spectral conflicts")
        logger.info(f"Generated {len(masking_analysis['recommendations'])} recommendations")
        
        # Step 3.5: INTELLIGENT BALANCE - Calculate optimal levels BEFORE processing
        logger.info("Applying intelligent mix balance...")
        balanced_stems = self.intelligent_balancer.apply_intelligent_balance(
            stems,
            stem_roles
        )
        
        # Step 4: Process individual stems
        logger.info("Processing individual stems...")
        processed_stems = {}
        stem_processing_logs = {}
        
        for name, audio in balanced_stems.items():
            role = stem_roles.get(name, 'other')
            
            # Get masking recommendations for this stem
            stem_recs = [
                rec for rec in masking_analysis['recommendations'].values()
                if name in str(rec)
            ]
            
            # Process stem
            result = self.stem_processor.process(
                audio,
                stem_role=role,
                masking_recommendations=stem_recs,
                tempo_bpm=analysis['tempo']
            )
            
            processed_stems[name] = result['audio']
            stem_processing_logs[name] = result['processing_log']
        
        # Step 5: Apply sidechain matrix (stems communicate more!)
        logger.info("Applying sidechain matrix...")
        sidechained_stems = self.sidechain_matrix.apply_sidechains(
            processed_stems,
            stem_roles,
            list(masking_analysis['recommendations'].values())
        )
        
        # Step 6: Create and process buses
        logger.info("Creating and processing buses...")
        buses = self.bus_processor.create_buses(
            sidechained_stems,
            stem_roles
        )
        
        # Step 7: Sum buses to create mix
        logger.info("Summing buses...")
        mix_audio = self._sum_buses(buses)
        
        # Step 8: Master bus processing
        logger.info("Processing master bus...")
        master_result = self.bus_processor.process_master_bus(
            mix_audio,
            gentle=True  # Gentle for mastering chain
        )
        mix_audio = master_result['audio']
        
        # Step 9: Normalize to target LUFS
        logger.info(f"Normalizing to {target_lufs} LUFS...")
        mix_audio = self.loudness_analyzer.normalize_to_lufs(
            mix_audio,
            target_lufs
        )
        
        # Step 10: Final analysis
        logger.info("Performing final analysis...")
        final_metrics = self.loudness_analyzer.analyze(mix_audio)
        
        # Check mono compatibility
        if mix_audio.ndim > 1:
            from .effects import StereoProcessor
            stereo_proc = StereoProcessor(self.sample_rate)
            mono_compat = stereo_proc.check_mono_compatibility(mix_audio)
        else:
            mono_compat = {'mono_compatible': True, 'correlation': 1.0}
        
        # Create comprehensive report
        report = {
            'stem_count': len(stems),
            'stem_roles': stem_roles,
            'tempo_bpm': analysis['tempo'],
            'key': analysis['key'],
            'masking_analysis': {
                'conflicts_found': masking_analysis['conflict_count'],
                'recommendations_applied': len(masking_analysis['recommendations']),
                'spectral_balance': masking_analysis['spectral_balance']
            },
            'processing': {
                'stem_logs': stem_processing_logs,
                'buses_created': list(buses.keys()),
                'bus_logs': {
                    name: bus['processing_log']
                    for name, bus in buses.items()
                },
                'master_bus_log': master_result['processing_log']
            },
            'final_metrics': {
                'lufs_integrated': final_metrics['lufs_integrated'],
                'lufs_target': target_lufs,
                'lra': final_metrics['lra'],
                'true_peak_dbTP': final_metrics['true_peak_dbTP'],
                'crest_factor': final_metrics['crest_factor'],
                'dynamic_range_db': final_metrics['dynamic_range_db']
            },
            'mono_compatibility': mono_compat,
            'quality_checks': self._quality_checks(final_metrics, mono_compat)
        }
        
        logger.info("Mix complete!")
        logger.info(f"Final LUFS: {final_metrics['lufs_integrated']:.1f}")
        logger.info(f"True Peak: {final_metrics['true_peak_dbTP']:.1f} dBTP")
        logger.info(f"Mono compatible: {mono_compat['mono_compatible']}")
        
        return {
            'audio': mix_audio,
            'report': report,
            'sample_rate': self.sample_rate
        }
    
    def _analyze_stems(
        self,
        stems: Dict[str, np.ndarray],
        stem_roles: Dict[str, str]
    ) -> Dict:
        """
        Analyze all stems
        
        Args:
            stems: Dictionary of stems
            stem_roles: Dictionary of stem roles
            
        Returns:
            Dictionary with analysis results
        """
        # Analyze first stem for tempo/key (assume all stems are same song)
        first_stem = next(iter(stems.values()))
        
        # Ensure mono for analysis
        if first_stem.ndim > 1:
            first_stem_mono = np.mean(first_stem, axis=0)
        else:
            first_stem_mono = first_stem
        
        # Musical analysis
        musical_features = self.musical_analyzer.analyze(first_stem_mono)
        
        return {
            'tempo': musical_features['tempo'],
            'key': musical_features['key'],
            'beat_count': musical_features['beat_count']
        }
    
    def _align_stems(
        self,
        stems: Dict[str, np.ndarray]
    ) -> Dict[str, np.ndarray]:
        """
        Align all stems to same length
        
        Args:
            stems: Dictionary of stems
            
        Returns:
            Dictionary of aligned stems
        """
        # Find maximum length
        max_length = max(
            audio.shape[-1] if audio.ndim > 1 else len(audio)
            for audio in stems.values()
        )
        
        # Pad all stems to max length
        aligned = {}
        for name, audio in stems.items():
            if audio.ndim == 1:
                # Mono
                if len(audio) < max_length:
                    audio = np.pad(audio, (0, max_length - len(audio)))
            else:
                # Stereo
                if audio.shape[1] < max_length:
                    pad_width = ((0, 0), (0, max_length - audio.shape[1]))
                    audio = np.pad(audio, pad_width)
            
            aligned[name] = audio
        
        return aligned
    
    def _sum_buses(
        self,
        buses: Dict[str, Dict]
    ) -> np.ndarray:
        """
        Sum all buses to create final mix
        
        Args:
            buses: Dictionary of processed buses
            
        Returns:
            Summed audio
        """
        bus_audios = [bus['audio'] for bus in buses.values()]
        
        if not bus_audios:
            raise ValueError("No buses to sum")
        
        # Ensure all same shape
        max_length = max(
            audio.shape[-1] if audio.ndim > 1 else len(audio)
            for audio in bus_audios
        )
        
        # Align and sum
        total = None
        for audio in bus_audios:
            # Pad if needed
            if audio.ndim == 1:
                if len(audio) < max_length:
                    audio = np.pad(audio, (0, max_length - len(audio)))
                if total is None:
                    total = audio
                else:
                    total = total + audio
            else:
                if audio.shape[1] < max_length:
                    pad_width = ((0, 0), (0, max_length - audio.shape[1]))
                    audio = np.pad(audio, pad_width)
                if total is None:
                    total = audio
                else:
                    total = total + audio
        
        return total
    
    def _quality_checks(
        self,
        metrics: Dict,
        mono_compat: Dict
    ) -> Dict:
        """
        Perform quality checks on mix
        
        Args:
            metrics: Loudness metrics
            mono_compat: Mono compatibility metrics
            
        Returns:
            Dictionary of quality check results
        """
        checks = {}
        
        # True peak check
        checks['true_peak_safe'] = metrics['true_peak_dbTP'] <= -1.0
        
        # Crest factor check (avoid over-compression)
        checks['crest_factor_safe'] = metrics['crest_factor'] >= 3.0
        
        # Mono compatibility
        checks['mono_compatible'] = mono_compat['mono_compatible']
        
        # Dynamic range
        checks['dynamic_range_adequate'] = metrics['dynamic_range_db'] >= 6.0
        
        # Overall
        checks['all_checks_passed'] = all(checks.values())
        
        return checks
