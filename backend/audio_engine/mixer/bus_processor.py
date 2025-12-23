"""
Bus Processor - REACTIVATED
Processes groups of stems (drum bus, music bus, vocal bus)
"""

import numpy as np
from typing import Dict, List
import logging

from .effects import StudioCompressor, StudioEQ, StereoProcessor

logger = logging.getLogger(__name__)


class BusProcessor:
    """Processes audio buses (groups of stems)"""
    
    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate
        self.compressor = StudioCompressor(sample_rate)
        self.eq = StudioEQ(sample_rate)
        self.stereo = StereoProcessor(sample_rate)
    
    def process_drum_bus(self, stems: Dict[str, np.ndarray]) -> Dict:
        """Process drum bus with glue compression"""
        logger.info("Processing drum bus...")
        
        bus_audio = sum(stems.values())
        processing_log = []
        
        # Glue compression (gentle)
        bus_audio = self.compressor.process(
            bus_audio,
            threshold_db=-15.0,
            ratio=2.5,
            attack_ms=30.0,
            release_ms=150.0,
            makeup_gain_db=2.0
        )
        processing_log.append("Glue compression: 2.5:1")
        
        # Parallel compression for punch
        bus_audio = self.compressor.parallel_compress(
            bus_audio,
            threshold_db=-20.0,
            ratio=6.0,
            attack_ms=5.0,
            release_ms=80.0,
            mix=0.25
        )
        processing_log.append("Parallel compression: 25%")
        
        # Transient enhancement
        bus_audio = self.eq.process(bus_audio, [
            {'type': 'peak', 'frequency': 80, 'gain': 1.0, 'q': 1.5},
            {'type': 'peak', 'frequency': 3000, 'gain': 1.5, 'q': 2.0}
        ])
        processing_log.append("Transient EQ")
        
        # Stereo narrowing
        if bus_audio.ndim > 1:
            bus_audio = self.stereo.adjust_width(bus_audio, width_percent=90.0, safe_bass=True)
            processing_log.append("Stereo width: 90%")
        
        logger.info(f"Drum bus: {', '.join(processing_log)}")
        return {'audio': bus_audio, 'processing_log': processing_log}
    
    def process_music_bus(self, stems: Dict[str, np.ndarray]) -> Dict:
        """Process music bus"""
        logger.info("Processing music bus...")
        
        bus_audio = sum(stems.values())
        processing_log = []
        
        # Low-mid cleanup
        bus_audio = self.eq.process(bus_audio, [
            {'type': 'peak', 'frequency': 250, 'gain': -1.5, 'q': 2.0},
            {'type': 'peak', 'frequency': 350, 'gain': -1.0, 'q': 1.5}
        ])
        processing_log.append("Low-mid cleanup")
        
        # Air boost
        bus_audio = self.eq.process(bus_audio, [
            {'type': 'high_shelf', 'frequency': 10000, 'gain': 1.5, 'q': 0.7}
        ])
        processing_log.append("Air boost")
        
        # Gentle compression
        bus_audio = self.compressor.process(
            bus_audio,
            threshold_db=-18.0,
            ratio=2.0,
            attack_ms=20.0,
            release_ms=120.0,
            makeup_gain_db=1.5
        )
        processing_log.append("Gentle compression: 2:1")
        
        logger.info(f"Music bus: {', '.join(processing_log)}")
        return {'audio': bus_audio, 'processing_log': processing_log}
    
    def process_vocal_bus(self, stems: Dict[str, np.ndarray]) -> Dict:
        """Process vocal bus"""
        logger.info("Processing vocal bus...")
        
        bus_audio = sum(stems.values())
        processing_log = []
        
        # Presence boost
        bus_audio = self.eq.process(bus_audio, [
            {'type': 'peak', 'frequency': 3000, 'gain': 2.0, 'q': 2.0},
            {'type': 'high_shelf', 'frequency': 8000, 'gain': 1.5, 'q': 0.7}
        ])
        processing_log.append("Presence boost")
        
        # Parallel compression
        bus_audio = self.compressor.parallel_compress(
            bus_audio,
            threshold_db=-22.0,
            ratio=8.0,
            attack_ms=3.0,
            release_ms=60.0,
            mix=0.30
        )
        processing_log.append("Parallel compression: 30%")
        
        # Main compression
        bus_audio = self.compressor.process(
            bus_audio,
            threshold_db=-16.0,
            ratio=3.0,
            attack_ms=10.0,
            release_ms=100.0,
            makeup_gain_db=2.5
        )
        processing_log.append("Main compression: 3:1")
        
        logger.info(f"Vocal bus: {', '.join(processing_log)}")
        return {'audio': bus_audio, 'processing_log': processing_log}
    
    def process_master_bus(self, audio: np.ndarray, gentle: bool = True) -> Dict:
        """Process master bus"""
        logger.info("Processing master bus...")
        
        processing_log = []
        
        if gentle:
            processed = self.compressor.process(
                audio,
                threshold_db=-12.0,
                ratio=1.5,
                attack_ms=30.0,
                release_ms=200.0,
                makeup_gain_db=0.5
            )
            processing_log.append("Gentle glue: 1.5:1")
        else:
            processed = self.compressor.process(
                audio,
                threshold_db=-10.0,
                ratio=2.5,
                attack_ms=20.0,
                release_ms=150.0,
                makeup_gain_db=2.0
            )
            processing_log.append("Bus compression: 2.5:1")
        
        # Subtle high-end
        processed = self.eq.process(processed, [
            {'type': 'high_shelf', 'frequency': 12000, 'gain': 0.5, 'q': 0.7}
        ])
        processing_log.append("Subtle air")
        
        logger.info(f"Master bus: {', '.join(processing_log)}")
        return {'audio': processed, 'processing_log': processing_log}
    
    def create_buses(self, stems: Dict[str, np.ndarray], stem_roles: Dict[str, str]) -> Dict[str, Dict]:
        """Create and process buses"""
        logger.info("Creating and processing buses...")
        
        drum_stems = {}
        music_stems = {}
        vocal_stems = {}
        
        drum_roles = ['kick', 'snare', 'hihat', 'drums', 'percussion']
        vocal_roles = ['vocal', 'lead_vocal', 'backing_vocal', 'vox']
        
        for name, audio in stems.items():
            role = stem_roles.get(name, 'other')
            if role in drum_roles:
                drum_stems[name] = audio
            elif role in vocal_roles:
                vocal_stems[name] = audio
            else:
                music_stems[name] = audio
        
        buses = {}
        if drum_stems:
            buses['drums'] = self.process_drum_bus(drum_stems)
            logger.info(f"Drum bus: {len(drum_stems)} stems")
        if music_stems:
            buses['music'] = self.process_music_bus(music_stems)
            logger.info(f"Music bus: {len(music_stems)} stems")
        if vocal_stems:
            buses['vocals'] = self.process_vocal_bus(vocal_stems)
            logger.info(f"Vocal bus: {len(vocal_stems)} stems")
        
        return buses
