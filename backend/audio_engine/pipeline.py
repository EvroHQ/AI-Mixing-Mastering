"""
Audio Pipeline - Genre-Aware Version
Complete end-to-end audio processing pipeline with automatic genre detection
Orchestrates: Genre Detection → Analysis → Mixing → Mastering
"""

import numpy as np
import soundfile as sf
from typing import Dict, List, Optional, Callable
from pathlib import Path
import logging
import time

from .mixer import MixEngine
from .masterer.simple_master import SimpleMasteringEngine
from .analyzer import LoudnessAnalyzer
from .presets import GenrePresets

# Try to use AI genre detector, fallback to analysis-based
try:
    from .analyzer.genre_detector_ai import AIGenreDetector as GenreDetector
    _using_ai_detector = True
except ImportError:
    from .analyzer.genre_detector import GenreDetector
    _using_ai_detector = False

logger = logging.getLogger(__name__)


class AudioPipeline:
    """
    Complete audio processing pipeline with genre detection
    Target: ≤120 seconds for 4-minute track with 12 stems
    """
    
    def __init__(self, sample_rate: int = 48000):
        """Initialize audio pipeline with all engines."""
        self.sample_rate = sample_rate
        
        # Initialize engines
        self.mix_engine = MixEngine(sample_rate)
        self.mastering_engine = SimpleMasteringEngine(sample_rate)
        self.loudness_analyzer = LoudnessAnalyzer(sample_rate)
        self.genre_detector = GenreDetector(sample_rate)
        
        if _using_ai_detector:
            logger.info("Using AI-powered genre detector (Essentia TensorFlow)")
        else:
            logger.info("Using analysis-based genre detector (fallback)")
    
    def process(
        self,
        stem_files: List[str],
        output_mix_path: str,
        output_master_path: str,
        target_lufs: float = -14.0,
        ceiling_dbTP: float = -1.0,
        max_width_percent: int = 140,
        preset: str = 'balanced',
        genre_override: Optional[str] = None,  # User can override detected genre
        progress_callback: Optional[Callable] = None
    ) -> Dict:
        """
        Process stems through complete pipeline with genre-aware processing.
        
        Args:
            stem_files: List of stem file paths
            output_mix_path: Output path for mix
            output_master_path: Output path for master
            target_lufs: Target loudness (can be overridden by genre preset)
            ceiling_dbTP: True peak ceiling
            max_width_percent: Maximum stereo width
            preset: Mastering preset (overridden by genre if detected)
            genre_override: Manually specify genre instead of auto-detect
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary with complete processing report including genre info
        """
        start_time = time.time()
        
        logger.info("="*60)
        logger.info("MIXMASTER PRO - GENRE-AWARE AUDIO PIPELINE")
        logger.info("="*60)
        logger.info(f"Stems: {len(stem_files)}")
        logger.info("="*60)
        
        # Stage 1: Load stems
        if progress_callback:
            progress_callback(0, "Loading stems...")
        
        logger.info("\n[STAGE 1/5] Loading stems...")
        stage1_start = time.time()
        
        stems = self._load_stems(stem_files)
        
        stage1_time = time.time() - stage1_start
        logger.info(f"✓ Loaded {len(stems)} stems in {stage1_time:.1f}s")
        
        # Stage 2: Rough mix + Genre detection
        if progress_callback:
            progress_callback(10, "Analyzing genre...")
        
        logger.info("\n[STAGE 2/5] Genre Detection...")
        stage2_start = time.time()
        
        # Create rough mix for genre detection
        rough_mix = self._create_rough_mix(stems)
        
        # Detect genre or use override
        if genre_override and genre_override in GenrePresets.list_genres():
            detected_genre = genre_override
            genre_confidence = 1.0
            logger.info(f"Using user-specified genre: {genre_override}")
            genre_result = {
                'detected_genre': detected_genre,
                'genre_name': GenrePresets.get_mixing_preset(detected_genre)['name'],
                'confidence': 1.0,
                'description': GenrePresets.get_mixing_preset(detected_genre)['description'],
                'all_scores': {},
                'analysis': {}
            }
        else:
            genre_result = self.genre_detector.detect_genre(rough_mix)
            detected_genre = genre_result['detected_genre']
            genre_confidence = genre_result['confidence']
        
        # Get genre-specific presets
        mixing_preset = GenrePresets.get_mixing_preset(detected_genre)
        mastering_preset = GenrePresets.get_mastering_preset(detected_genre)
        
        # Use genre-specific target LUFS
        genre_target_lufs = mastering_preset['target_lufs']
        genre_ceiling = mastering_preset.get('ceiling_dbTP', ceiling_dbTP)
        
        stage2_time = time.time() - stage2_start
        logger.info(f"✓ Genre detected: {genre_result['genre_name']} ({genre_confidence:.0%})")
        logger.info(f"  Target LUFS: {genre_target_lufs} dB")
        logger.info(f"  Description: {genre_result['description']}")
        
        # Stage 3: Mixing with genre presets
        if progress_callback:
            progress_callback(25, f"Mixing ({genre_result['genre_name']})...")
        
        logger.info("\n[STAGE 3/5] Mixing with genre presets...")
        stage3_start = time.time()
        
        mix_result = self.mix_engine.mix(
            stems=stems,
            target_lufs=genre_target_lufs,
            preset=detected_genre,
            genre_preset=mixing_preset
        )
        
        stage3_time = time.time() - stage3_start
        logger.info(f"✓ Mix complete in {stage3_time:.1f}s")
        logger.info(f"  LUFS: {mix_result['report']['final_metrics']['lufs_integrated']:.1f}")
        
        # Stage 4: Mastering with genre presets
        if progress_callback:
            progress_callback(60, f"Mastering ({genre_result['genre_name']})...")
        
        logger.info("\n[STAGE 4/5] Simple transparent mastering...")
        stage4_start = time.time()
        
        # Use simple mastering with platform preset
        # Map genre to platform if applicable, otherwise use spotify as default
        platform = 'spotify'
        if genre_target_lufs <= -16:
            platform = 'apple_music'
        elif genre_target_lufs >= -10:
            platform = 'club'
        
        master_result = self.mastering_engine.master(
            audio=mix_result['audio'],
            platform=platform
        )
        
        stage4_time = time.time() - stage4_start
        logger.info(f"✓ Master complete in {stage4_time:.1f}s")
        logger.info(f"  LUFS: {master_result['output_lufs']:.1f}")
        logger.info(f"  True Peak: {master_result['output_peak']:.1f} dBTP")
        
        # Stage 5: Export
        if progress_callback:
            progress_callback(90, "Exporting files...")
        
        logger.info("\n[STAGE 5/5] Exporting...")
        stage5_start = time.time()
        
        # Export mix
        self._export_audio(
            mix_result['audio'],
            output_mix_path,
            self.sample_rate
        )
        logger.info(f"✓ Mix exported: {output_mix_path}")
        
        # Export master
        self._export_audio(
            master_result['audio'],
            output_master_path,
            self.sample_rate
        )
        logger.info(f"✓ Master exported: {output_master_path}")
        
        stage5_time = time.time() - stage5_start
        
        # Calculate total time
        total_time = time.time() - start_time
        
        if progress_callback:
            progress_callback(100, "Complete!")
        
        logger.info("\n" + "="*60)
        logger.info("PIPELINE COMPLETE")
        logger.info("="*60)
        logger.info(f"Genre: {genre_result['genre_name']} ({genre_confidence:.0%})")
        logger.info(f"Total time: {total_time:.1f}s")
        logger.info(f"  Load: {stage1_time:.1f}s")
        logger.info(f"  Genre detect: {stage2_time:.1f}s")
        logger.info(f"  Mix: {stage3_time:.1f}s")
        logger.info(f"  Master: {stage4_time:.1f}s")
        logger.info(f"  Export: {stage5_time:.1f}s")
        logger.info("="*60)
        
        return {
            'success': True,
            'genre': {
                'detected': detected_genre,
                'name': genre_result['genre_name'],
                'confidence': genre_confidence,
                'description': genre_result['description'],
                'all_scores': genre_result.get('all_scores', {})
            },
            'presets_used': {
                'mixing': mixing_preset['name'],
                'mastering_lufs': genre_target_lufs,
                'mastering_ceiling': genre_ceiling
            },
            'mix_report': mix_result['report'],
            'master_report': {
                'output_lufs': master_result['output_lufs'],
                'output_peak': master_result['output_peak'],
                'gain_applied': master_result['gain_applied'],
                'platform': master_result['platform']
            },
            'timing': {
                'total_seconds': total_time,
                'load': stage1_time,
                'genre_detection': stage2_time,
                'mixing': stage3_time,
                'mastering': stage4_time,
                'export': stage5_time
            },
            'output_files': {
                'mix': str(output_mix_path),
                'master': str(output_master_path)
            }
        }
    
    def analyze_genre_only(
        self,
        stem_files: List[str]
    ) -> Dict:
        """
        Quick genre detection without full processing.
        Used for frontend preview before processing.
        
        Args:
            stem_files: List of stem file paths
            
        Returns:
            Genre detection result with recommended settings
        """
        logger.info("Quick genre analysis...")
        
        # Load stems
        stems = self._load_stems(stem_files)
        
        # Create rough mix
        rough_mix = self._create_rough_mix(stems)
        
        # Detect genre
        genre_result = self.genre_detector.detect_genre(rough_mix)
        
        # Get presets
        mixing_preset = GenrePresets.get_mixing_preset(genre_result['detected_genre'])
        mastering_preset = GenrePresets.get_mastering_preset(genre_result['detected_genre'])
        
        return {
            'genre': genre_result['detected_genre'],
            'genre_name': genre_result['genre_name'],
            'confidence': genre_result['confidence'],
            'description': genre_result['description'],
            'all_scores': genre_result['all_scores'],
            'recommended_settings': {
                'target_lufs': mastering_preset['target_lufs'],
                'ceiling_dbTP': mastering_preset.get('ceiling_dbTP', -1.0),
                'stereo_width': mastering_preset.get('stereo_width', 120)
            },
            'analysis': genre_result.get('analysis', {}),
            'available_genres': GenrePresets.list_genres()
        }
    
    def _create_rough_mix(self, stems: Dict[str, np.ndarray]) -> np.ndarray:
        """Create a basic rough mix for genre detection."""
        
        if not stems:
            return np.zeros(1)
        
        # Find maximum length
        max_length = max(s.shape[-1] for s in stems.values())
        
        # Sum all stems (basic rough mix)
        rough_mix = None
        
        for name, audio in stems.items():
            # Pad to same length
            if audio.ndim == 1:
                audio = np.stack([audio, audio])
            
            if audio.shape[-1] < max_length:
                pad = max_length - audio.shape[-1]
                audio = np.pad(audio, ((0, 0), (0, pad)))
            
            # Normalize each stem
            peak = np.max(np.abs(audio)) + 1e-10
            audio = audio / peak * 0.5
            
            if rough_mix is None:
                rough_mix = audio
            else:
                rough_mix = rough_mix + audio
        
        # Normalize rough mix
        peak = np.max(np.abs(rough_mix)) + 1e-10
        rough_mix = rough_mix / peak * 0.8
        
        return rough_mix
    
    def _load_stems(self, stem_files: List[str]) -> Dict[str, np.ndarray]:
        """Load stem files into memory."""
        
        stems = {}
        detected_sr = None
        
        for file_path in stem_files:
            try:
                audio, sr = sf.read(file_path, always_2d=False)
                
                if detected_sr is None:
                    detected_sr = sr
                    if sr != self.sample_rate:
                        logger.info(f"Using native sample rate: {sr} Hz")
                        self.sample_rate = sr
                        self.mix_engine.sample_rate = sr
                        self.mastering_engine.sample_rate = sr
                        self.loudness_analyzer.sample_rate = sr
                        self.genre_detector.sample_rate = sr
                
                if sr != detected_sr:
                    logger.warning(f"Sample rate mismatch: {Path(file_path).name}")
                    import resampy
                    audio = resampy.resample(audio, sr, detected_sr, filter='kaiser_best')
                
                audio = audio.astype(np.float32)
                
                if audio.ndim == 2:
                    audio = audio.T
                
                stem_name = Path(file_path).stem
                stems[stem_name] = audio
                
                logger.info(f"  Loaded: {stem_name} ({audio.shape})")
                
            except Exception as e:
                logger.error(f"  Failed to load {file_path}: {e}")
                raise
        
        return stems
    
    def _export_audio(
        self,
        audio: np.ndarray,
        output_path: str,
        sample_rate: int
    ) -> None:
        """Export audio to file."""
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        if audio.ndim > 1:
            audio = audio.T
        
        sf.write(output_path, audio, sample_rate, subtype='PCM_24')
    
    @staticmethod
    def get_available_genres() -> List[Dict]:
        """Get list of available genres with descriptions."""
        genres = []
        for genre_id in GenrePresets.list_genres():
            preset = GenrePresets.get_mixing_preset(genre_id)
            mastering = GenrePresets.get_mastering_preset(genre_id)
            genres.append({
                'id': genre_id,
                'name': preset['name'],
                'description': preset['description'],
                'target_lufs': mastering['target_lufs']
            })
        return genres
