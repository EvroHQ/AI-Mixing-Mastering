"""
Genre-Specific Mixing & Mastering Presets
Professional settings based on industry standards for each music genre
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class GenrePresets:
    """
    Professional mixing and mastering presets for each music genre.
    Based on industry research and professional engineer practices.
    """
    
    # ==========================================================================
    # MIXING PRESETS - Per-stem and bus processing settings
    # ==========================================================================
    
    MIXING_PRESETS = {
        'house': {
            'name': 'House / Afro House',
            'description': 'Groovy, warm bass, wide percussion, club-ready',
            
            'stem_settings': {
                'kick': {
                    'highpass_freq': 25,
                    'eq_bands': [
                        {'type': 'peak', 'frequency': 55, 'gain': 2.5, 'q': 2.0},   # Sub fundamental
                        {'type': 'peak', 'frequency': 100, 'gain': 1.5, 'q': 1.5},  # Body
                        {'type': 'peak', 'frequency': 3500, 'gain': 2.0, 'q': 2.0}, # Click
                    ],
                    'compression': {'threshold': -10, 'ratio': 3.5, 'attack': 5, 'release': 60},
                },
                'bass': {
                    'highpass_freq': 25,
                    'eq_bands': [
                        {'type': 'low_shelf', 'frequency': 80, 'gain': 2.0, 'q': 0.7},
                        {'type': 'peak', 'frequency': 150, 'gain': -1.0, 'q': 1.5},
                        {'type': 'peak', 'frequency': 800, 'gain': 1.5, 'q': 1.5},  # Growl
                    ],
                    'compression': {'threshold': -14, 'ratio': 3.0, 'attack': 10, 'release': 100},
                    'sidechain_from': 'kick',
                    'sidechain_amount': 0.25,  # Subtle sidechain for house
                    'saturation': {'drive': 0.2, 'type': 'tape'},
                },
                'percussion': {
                    'highpass_freq': 200,
                    'eq_bands': [
                        {'type': 'peak', 'frequency': 5000, 'gain': 2.0, 'q': 1.5},
                        {'type': 'high_shelf', 'frequency': 10000, 'gain': 2.5, 'q': 0.7},
                    ],
                    'stereo_width': 130,
                    'compression': {'threshold': -15, 'ratio': 2.5, 'attack': 8, 'release': 80},
                },
                'synth': {
                    'highpass_freq': 150,
                    'eq_bands': [
                        {'type': 'peak', 'frequency': 2500, 'gain': 1.5, 'q': 1.5},
                        {'type': 'high_shelf', 'frequency': 8000, 'gain': 2.0, 'q': 0.7},
                    ],
                    'stereo_width': 125,
                },
                'vocal': {
                    'highpass_freq': 100,
                    'eq_bands': [
                        {'type': 'peak', 'frequency': 200, 'gain': -1.5, 'q': 1.5},
                        {'type': 'peak', 'frequency': 3000, 'gain': 2.0, 'q': 1.5},
                        {'type': 'high_shelf', 'frequency': 10000, 'gain': 2.0, 'q': 0.7},
                    ],
                    'compression': {'threshold': -16, 'ratio': 3.0, 'attack': 8, 'release': 80},
                    'deesser': True,
                },
            },
            
            'bus_settings': {
                'drum_bus': {
                    'glue_compression': {'threshold': -12, 'ratio': 2.5, 'attack': 15, 'release': 80},
                    'parallel_mix': 0.25,
                    'eq_boost': [{'frequency': 100, 'gain': 1.0}, {'frequency': 8000, 'gain': 1.5}],
                },
                'music_bus': {
                    'stereo_width': 120,
                    'eq_cut': [{'frequency': 250, 'gain': -1.5}],
                },
                'master_bus': {
                    'compression': {'threshold': -10, 'ratio': 2.0, 'attack': 12, 'release': 100},
                },
            },
            
            'sidechain': {
                'enabled': True,
                'source': 'kick',
                'targets': ['bass'],
                'amount': 0.25,
                'attack_ms': 2,
                'release_ms': 80,
            },
        },
        
        'techno': {
            'name': 'Techno / Tech House',
            'description': 'Driving, hypnotic, powerful low-end',
            
            'stem_settings': {
                'kick': {
                    'highpass_freq': 25,
                    'eq_bands': [
                        {'type': 'peak', 'frequency': 50, 'gain': 3.0, 'q': 2.0},
                        {'type': 'peak', 'frequency': 4000, 'gain': 2.5, 'q': 2.0},
                    ],
                    'compression': {'threshold': -8, 'ratio': 4.0, 'attack': 3, 'release': 50},
                },
                'bass': {
                    'highpass_freq': 25,
                    'eq_bands': [
                        {'type': 'low_shelf', 'frequency': 80, 'gain': 2.5, 'q': 0.7},
                        {'type': 'peak', 'frequency': 200, 'gain': -2.0, 'q': 1.5},
                    ],
                    'compression': {'threshold': -12, 'ratio': 3.5, 'attack': 8, 'release': 80},
                    'sidechain_from': 'kick',
                    'sidechain_amount': 0.35,
                },
                'synth': {
                    'highpass_freq': 200,
                    'eq_bands': [
                        {'type': 'peak', 'frequency': 3000, 'gain': 2.0, 'q': 1.5},
                    ],
                    'stereo_width': 130,
                },
                'percussion': {
                    'highpass_freq': 300,
                    'stereo_width': 140,
                },
            },
            
            'bus_settings': {
                'drum_bus': {
                    'glue_compression': {'threshold': -10, 'ratio': 3.0, 'attack': 10, 'release': 70},
                    'parallel_mix': 0.30,
                },
                'master_bus': {
                    'compression': {'threshold': -8, 'ratio': 2.5, 'attack': 8, 'release': 60},
                },
            },
            
            'sidechain': {
                'enabled': True,
                'source': 'kick',
                'targets': ['bass', 'synth'],
                'amount': 0.35,
                'attack_ms': 1,
                'release_ms': 40,
            },
        },
        
        'edm': {
            'name': 'EDM / Electronic',
            'description': 'Loud, punchy, wide stereo with pumping dynamics',
            
            # Stem processing
            'stem_settings': {
                'kick': {
                    'highpass_freq': 30,
                    'eq_bands': [
                        {'type': 'peak', 'frequency': 60, 'gain': 2.0, 'q': 1.5},   # Sub punch
                        {'type': 'peak', 'frequency': 4000, 'gain': 2.5, 'q': 2.0}, # Click
                    ],
                    'compression': {'threshold': -12, 'ratio': 4.0, 'attack': 5, 'release': 50},
                },
                'bass': {
                    'highpass_freq': 25,
                    'eq_bands': [
                        {'type': 'low_shelf', 'frequency': 80, 'gain': 2.0, 'q': 0.7},
                        {'type': 'peak', 'frequency': 200, 'gain': -2.0, 'q': 1.5}, # Reduce mud
                    ],
                    'compression': {'threshold': -15, 'ratio': 3.0, 'attack': 10, 'release': 100},
                    'sidechain_from': 'kick',  # Sidechain ducking
                    'sidechain_amount': 0.4,
                },
                'synth': {
                    'highpass_freq': 100,
                    'eq_bands': [
                        {'type': 'peak', 'frequency': 3000, 'gain': 2.0, 'q': 1.5},
                        {'type': 'high_shelf', 'frequency': 10000, 'gain': 3.0, 'q': 0.7},
                    ],
                    'stereo_width': 140,
                },
                'drums': {
                    'highpass_freq': 40,
                    'compression': {'threshold': -10, 'ratio': 3.5, 'attack': 3, 'release': 80},
                    'parallel_compression': {'ratio': 8.0, 'mix': 0.35},
                },
            },
            
            # Bus processing
            'bus_settings': {
                'drum_bus': {
                    'glue_compression': {'threshold': -12, 'ratio': 3.0, 'attack': 20, 'release': 100},
                    'parallel_mix': 0.30,
                    'eq_boost': [{'frequency': 80, 'gain': 1.5}, {'frequency': 5000, 'gain': 2.0}],
                },
                'music_bus': {
                    'stereo_width': 130,
                    'eq_cut': [{'frequency': 300, 'gain': -2.0}],  # Reduce mud
                },
                'master_bus': {
                    'compression': {'threshold': -8, 'ratio': 2.0, 'attack': 10, 'release': 80},
                },
            },
            
            # Sidechain settings
            'sidechain': {
                'enabled': True,
                'source': 'kick',
                'targets': ['bass', 'synth'],
                'amount': 0.4,
                'attack_ms': 1,
                'release_ms': 50,
            },
        },
        
        'hiphop': {
            'name': 'Hip-Hop / Trap',
            'description': 'Heavy 808s, punchy drums, vocals in front',
            
            'stem_settings': {
                'kick': {
                    'highpass_freq': 25,
                    'eq_bands': [
                        {'type': 'peak', 'frequency': 55, 'gain': 3.0, 'q': 2.0},   # 808 fundamental
                        {'type': 'peak', 'frequency': 3500, 'gain': 2.0, 'q': 2.0}, # Attack
                    ],
                    'compression': {'threshold': -10, 'ratio': 4.0, 'attack': 3, 'release': 80},
                    'saturation': {'drive': 0.3, 'type': 'tape'},
                },
                'bass': {
                    'highpass_freq': 20,
                    'eq_bands': [
                        {'type': 'low_shelf', 'frequency': 60, 'gain': 3.0, 'q': 0.7},
                        {'type': 'peak', 'frequency': 150, 'gain': -1.5, 'q': 2.0},
                    ],
                    'compression': {'threshold': -12, 'ratio': 3.5, 'attack': 8, 'release': 120},
                    'saturation': {'drive': 0.4, 'type': 'tube'},
                },
                'vocal': {
                    'highpass_freq': 80,
                    'eq_bands': [
                        {'type': 'peak', 'frequency': 200, 'gain': -2.0, 'q': 1.5},  # Reduce mud
                        {'type': 'peak', 'frequency': 3000, 'gain': 3.0, 'q': 1.5},  # Presence
                        {'type': 'peak', 'frequency': 5000, 'gain': 2.0, 'q': 2.0},  # Clarity
                        {'type': 'high_shelf', 'frequency': 10000, 'gain': 2.5, 'q': 0.7}, # Air
                    ],
                    'compression': {'threshold': -18, 'ratio': 4.0, 'attack': 5, 'release': 60},
                    'deesser': True,
                },
                'hihat': {
                    'highpass_freq': 400,
                    'eq_bands': [
                        {'type': 'peak', 'frequency': 8000, 'gain': 2.0, 'q': 1.5},
                    ],
                    'stereo_width': 120,
                },
            },
            
            'bus_settings': {
                'drum_bus': {
                    'glue_compression': {'threshold': -10, 'ratio': 4.0, 'attack': 5, 'release': 60},
                    'parallel_mix': 0.40,
                    'saturation': {'drive': 0.25, 'type': 'tape'},
                },
                'vocal_bus': {
                    'compression': {'threshold': -15, 'ratio': 3.0, 'attack': 8, 'release': 80},
                    'parallel_mix': 0.25,
                    'eq_boost': [{'frequency': 3500, 'gain': 2.0}],
                },
            },
            
            'sidechain': {
                'enabled': True,
                'source': 'kick',
                'targets': ['bass'],
                'amount': 0.3,
            },
        },
        
        'pop': {
            'name': 'Pop',
            'description': 'Polished, vocals prominent, wide and bright',
            
            'stem_settings': {
                'vocal': {
                    'highpass_freq': 100,
                    'eq_bands': [
                        {'type': 'peak', 'frequency': 180, 'gain': -2.5, 'q': 1.5},
                        {'type': 'peak', 'frequency': 2500, 'gain': 2.5, 'q': 1.5},
                        {'type': 'peak', 'frequency': 5000, 'gain': 2.0, 'q': 2.0},
                        {'type': 'high_shelf', 'frequency': 12000, 'gain': 3.0, 'q': 0.7},
                    ],
                    'compression': {'threshold': -20, 'ratio': 3.5, 'attack': 8, 'release': 80},
                    'parallel_compression': {'ratio': 6.0, 'mix': 0.20},
                    'deesser': True,
                },
                'kick': {
                    'highpass_freq': 35,
                    'eq_bands': [
                        {'type': 'peak', 'frequency': 70, 'gain': 1.5, 'q': 1.5},
                        {'type': 'peak', 'frequency': 3000, 'gain': 2.0, 'q': 2.0},
                    ],
                    'compression': {'threshold': -12, 'ratio': 3.5, 'attack': 5, 'release': 60},
                },
                'synth': {
                    'highpass_freq': 150,
                    'eq_bands': [
                        {'type': 'high_shelf', 'frequency': 8000, 'gain': 2.5, 'q': 0.7},
                    ],
                    'stereo_width': 130,
                },
                'drums': {
                    'highpass_freq': 50,
                    'compression': {'threshold': -12, 'ratio': 3.0, 'attack': 5, 'release': 80},
                },
            },
            
            'bus_settings': {
                'vocal_bus': {
                    'compression': {'threshold': -14, 'ratio': 2.5, 'attack': 10, 'release': 100},
                    'eq_boost': [{'frequency': 3000, 'gain': 1.5}, {'frequency': 12000, 'gain': 2.0}],
                },
                'music_bus': {
                    'stereo_width': 120,
                    'eq_cut': [{'frequency': 250, 'gain': -1.5}],
                },
                'master_bus': {
                    'compression': {'threshold': -10, 'ratio': 1.8, 'attack': 15, 'release': 120},
                },
            },
        },
        
        'rock': {
            'name': 'Rock',
            'description': 'Dynamic, punchy, mid-focused guitars',
            
            'stem_settings': {
                'drums': {
                    'highpass_freq': 40,
                    'eq_bands': [
                        {'type': 'peak', 'frequency': 80, 'gain': 2.0, 'q': 1.5},
                        {'type': 'peak', 'frequency': 4000, 'gain': 2.5, 'q': 2.0},
                    ],
                    'compression': {'threshold': -14, 'ratio': 3.5, 'attack': 8, 'release': 100},
                    'parallel_compression': {'ratio': 8.0, 'mix': 0.30},
                },
                'guitar': {
                    'highpass_freq': 80,
                    'eq_bands': [
                        {'type': 'peak', 'frequency': 300, 'gain': -2.0, 'q': 1.5},
                        {'type': 'peak', 'frequency': 2500, 'gain': 2.0, 'q': 1.5},
                        {'type': 'peak', 'frequency': 5000, 'gain': 1.5, 'q': 2.0},
                    ],
                    'saturation': {'drive': 0.3, 'type': 'tube'},
                },
                'bass': {
                    'highpass_freq': 40,
                    'eq_bands': [
                        {'type': 'peak', 'frequency': 100, 'gain': 1.5, 'q': 1.5},
                        {'type': 'peak', 'frequency': 700, 'gain': 2.0, 'q': 1.5},  # Growl
                    ],
                    'compression': {'threshold': -16, 'ratio': 3.0, 'attack': 15, 'release': 120},
                    'saturation': {'drive': 0.25, 'type': 'tube'},
                },
                'vocal': {
                    'highpass_freq': 120,
                    'eq_bands': [
                        {'type': 'peak', 'frequency': 3500, 'gain': 2.5, 'q': 1.5},
                        {'type': 'peak', 'frequency': 6000, 'gain': 1.5, 'q': 2.0},
                    ],
                    'compression': {'threshold': -18, 'ratio': 4.0, 'attack': 5, 'release': 80},
                },
            },
            
            'bus_settings': {
                'drum_bus': {
                    'glue_compression': {'threshold': -14, 'ratio': 3.0, 'attack': 15, 'release': 120},
                    'parallel_mix': 0.35,
                    'saturation': {'drive': 0.20, 'type': 'tape'},
                },
                'master_bus': {
                    'compression': {'threshold': -12, 'ratio': 2.0, 'attack': 20, 'release': 150},
                    'saturation': {'drive': 0.15, 'type': 'tape'},
                },
            },
        },
        
        'rnb': {
            'name': 'R&B / Soul',
            'description': 'Warm, smooth, silky vocals',
            
            'stem_settings': {
                'vocal': {
                    'highpass_freq': 80,
                    'eq_bands': [
                        {'type': 'peak', 'frequency': 250, 'gain': -1.5, 'q': 1.5},
                        {'type': 'peak', 'frequency': 2000, 'gain': 2.0, 'q': 1.5},
                        {'type': 'high_shelf', 'frequency': 8000, 'gain': 2.0, 'q': 0.7},
                    ],
                    'compression': {'threshold': -20, 'ratio': 3.0, 'attack': 12, 'release': 100},
                    'saturation': {'drive': 0.15, 'type': 'tube'},
                    'deesser': True,
                },
                'bass': {
                    'highpass_freq': 30,
                    'eq_bands': [
                        {'type': 'low_shelf', 'frequency': 80, 'gain': 2.0, 'q': 0.7},
                        {'type': 'peak', 'frequency': 400, 'gain': 1.0, 'q': 1.5},
                    ],
                    'compression': {'threshold': -16, 'ratio': 2.5, 'attack': 15, 'release': 150},
                    'saturation': {'drive': 0.20, 'type': 'tube'},
                },
                'keys': {
                    'highpass_freq': 100,
                    'eq_bands': [
                        {'type': 'peak', 'frequency': 2500, 'gain': 1.5, 'q': 1.5},
                    ],
                    'stereo_width': 110,
                },
            },
            
            'bus_settings': {
                'vocal_bus': {
                    'compression': {'threshold': -16, 'ratio': 2.5, 'attack': 12, 'release': 120},
                    'saturation': {'drive': 0.10, 'type': 'tube'},
                },
                'music_bus': {
                    'eq_cut': [{'frequency': 300, 'gain': -1.5}],
                    'saturation': {'drive': 0.15, 'type': 'tape'},
                },
            },
        },
        
        'acoustic': {
            'name': 'Acoustic / Folk',
            'description': 'Natural dynamics, minimal processing',
            
            'stem_settings': {
                'guitar': {
                    'highpass_freq': 80,
                    'eq_bands': [
                        {'type': 'peak', 'frequency': 200, 'gain': -1.0, 'q': 1.5},
                        {'type': 'peak', 'frequency': 3000, 'gain': 1.5, 'q': 1.5},
                        {'type': 'high_shelf', 'frequency': 8000, 'gain': 1.5, 'q': 0.7},
                    ],
                    'compression': {'threshold': -22, 'ratio': 2.0, 'attack': 20, 'release': 150},
                },
                'vocal': {
                    'highpass_freq': 100,
                    'eq_bands': [
                        {'type': 'peak', 'frequency': 150, 'gain': -1.5, 'q': 1.5},
                        {'type': 'peak', 'frequency': 2500, 'gain': 1.5, 'q': 1.5},
                    ],
                    'compression': {'threshold': -22, 'ratio': 2.5, 'attack': 15, 'release': 120},
                    'deesser': True,
                },
                'drums': {
                    'highpass_freq': 50,
                    'compression': {'threshold': -18, 'ratio': 2.5, 'attack': 15, 'release': 120},
                },
            },
            
            'bus_settings': {
                'master_bus': {
                    'compression': {'threshold': -16, 'ratio': 1.5, 'attack': 25, 'release': 200},
                },
            },
        },
        
        'metal': {
            'name': 'Metal / Hard Rock',
            'description': 'Aggressive, heavy, wall of sound',
            
            'stem_settings': {
                'drums': {
                    'highpass_freq': 35,
                    'eq_bands': [
                        {'type': 'peak', 'frequency': 80, 'gain': 2.5, 'q': 1.5},
                        {'type': 'peak', 'frequency': 5000, 'gain': 3.0, 'q': 2.0},
                    ],
                    'compression': {'threshold': -10, 'ratio': 5.0, 'attack': 2, 'release': 50},
                    'parallel_compression': {'ratio': 10.0, 'mix': 0.40},
                },
                'guitar': {
                    'highpass_freq': 100,
                    'eq_bands': [
                        {'type': 'peak', 'frequency': 400, 'gain': -3.0, 'q': 1.5},
                        {'type': 'peak', 'frequency': 2000, 'gain': 2.0, 'q': 1.5},
                        {'type': 'peak', 'frequency': 4000, 'gain': 2.5, 'q': 2.0},
                    ],
                    'compression': {'threshold': -12, 'ratio': 4.0, 'attack': 5, 'release': 60},
                },
                'bass': {
                    'highpass_freq': 40,
                    'eq_bands': [
                        {'type': 'peak', 'frequency': 100, 'gain': 2.0, 'q': 1.5},
                        {'type': 'peak', 'frequency': 1000, 'gain': 2.5, 'q': 1.5},
                    ],
                    'compression': {'threshold': -12, 'ratio': 4.0, 'attack': 8, 'release': 80},
                    'saturation': {'drive': 0.4, 'type': 'tube'},
                },
                'vocal': {
                    'highpass_freq': 150,
                    'eq_bands': [
                        {'type': 'peak', 'frequency': 3000, 'gain': 3.0, 'q': 1.5},
                        {'type': 'peak', 'frequency': 5000, 'gain': 2.0, 'q': 2.0},
                    ],
                    'compression': {'threshold': -15, 'ratio': 5.0, 'attack': 3, 'release': 50},
                },
            },
            
            'bus_settings': {
                'drum_bus': {
                    'glue_compression': {'threshold': -8, 'ratio': 4.0, 'attack': 5, 'release': 50},
                    'parallel_mix': 0.45,
                },
                'master_bus': {
                    'compression': {'threshold': -8, 'ratio': 2.5, 'attack': 10, 'release': 80},
                },
            },
        },
    }
    
    # ==========================================================================
    # MASTERING PRESETS - Final stage processing
    # ==========================================================================
    
    MASTERING_PRESETS = {
        'house': {
            'target_lufs': -9.0,
            'ceiling_dbTP': -0.5,
            'eq': [
                {'type': 'low_shelf', 'frequency': 50, 'gain': 1.5, 'q': 0.7},
                {'type': 'peak', 'frequency': 200, 'gain': -1.0, 'q': 1.5},
                {'type': 'peak', 'frequency': 3500, 'gain': 1.5, 'q': 1.5},
                {'type': 'high_shelf', 'frequency': 10000, 'gain': 2.0, 'q': 0.7},
            ],
            'multiband': {
                'crossovers': [80, 400, 2500, 10000],
                'ratios': [2.5, 2.0, 2.0, 2.0, 1.5],
                'thresholds': [-12, -14, -14, -14, -16],
            },
            'saturation': {'tape': 0.20, 'tube': 0.15},
            'stereo_width': 120,
            'limiter': {'ceiling': -0.5, 'release': 80},
        },
        
        'techno': {
            'target_lufs': -8.0,
            'ceiling_dbTP': -0.3,
            'eq': [
                {'type': 'low_shelf', 'frequency': 50, 'gain': 2.0, 'q': 0.7},
                {'type': 'peak', 'frequency': 200, 'gain': -1.5, 'q': 1.5},
                {'type': 'peak', 'frequency': 4000, 'gain': 2.0, 'q': 1.5},
                {'type': 'high_shelf', 'frequency': 12000, 'gain': 2.0, 'q': 0.7},
            ],
            'multiband': {
                'crossovers': [80, 400, 2000, 8000],
                'ratios': [3.0, 2.5, 2.5, 2.0, 1.5],
                'thresholds': [-10, -12, -12, -14, -16],
            },
            'saturation': {'tape': 0.25, 'tube': 0.20},
            'stereo_width': 125,
            'limiter': {'ceiling': -0.3, 'release': 50},
        },
        
        'edm': {
            'target_lufs': -8.0,
            'ceiling_dbTP': -0.5,
            'eq': [
                {'type': 'low_shelf', 'frequency': 50, 'gain': 1.5, 'q': 0.7},
                {'type': 'peak', 'frequency': 200, 'gain': -1.5, 'q': 1.5},
                {'type': 'peak', 'frequency': 4000, 'gain': 2.0, 'q': 1.5},
                {'type': 'high_shelf', 'frequency': 12000, 'gain': 2.5, 'q': 0.7},
            ],
            'multiband': {
                'crossovers': [100, 500, 2000, 8000],
                'ratios': [3.0, 2.0, 2.5, 2.0, 1.5],
                'thresholds': [-12, -15, -14, -15, -18],
            },
            'saturation': {'tape': 0.25, 'tube': 0.15},
            'stereo_width': 130,
            'limiter': {'ceiling': -0.5, 'release': 50},
        },
        
        'hiphop': {
            'target_lufs': -10.0,
            'ceiling_dbTP': -0.5,
            'eq': [
                {'type': 'low_shelf', 'frequency': 60, 'gain': 2.5, 'q': 0.7},
                {'type': 'peak', 'frequency': 150, 'gain': -1.0, 'q': 1.5},
                {'type': 'peak', 'frequency': 3000, 'gain': 1.5, 'q': 1.5},
                {'type': 'high_shelf', 'frequency': 10000, 'gain': 2.0, 'q': 0.7},
            ],
            'multiband': {
                'crossovers': [80, 400, 2500, 10000],
                'ratios': [3.5, 2.5, 2.0, 2.0, 1.5],
                'thresholds': [-10, -14, -15, -14, -16],
            },
            'saturation': {'tape': 0.30, 'tube': 0.20},
            'stereo_width': 115,
            'limiter': {'ceiling': -0.5, 'release': 80},
        },
        
        'pop': {
            'target_lufs': -10.0,
            'ceiling_dbTP': -1.0,
            'eq': [
                {'type': 'low_shelf', 'frequency': 60, 'gain': 1.0, 'q': 0.7},
                {'type': 'peak', 'frequency': 250, 'gain': -1.0, 'q': 1.5},
                {'type': 'peak', 'frequency': 3500, 'gain': 1.5, 'q': 1.5},
                {'type': 'high_shelf', 'frequency': 12000, 'gain': 2.5, 'q': 0.7},
            ],
            'multiband': {
                'crossovers': [100, 500, 3000, 10000],
                'ratios': [2.5, 2.0, 2.0, 2.0, 1.5],
                'thresholds': [-14, -16, -15, -14, -16],
            },
            'saturation': {'tape': 0.15, 'tube': 0.10},
            'stereo_width': 120,
            'limiter': {'ceiling': -1.0, 'release': 100},
        },
        
        'rock': {
            'target_lufs': -12.0,
            'ceiling_dbTP': -1.0,
            'eq': [
                {'type': 'low_shelf', 'frequency': 80, 'gain': 1.0, 'q': 0.7},
                {'type': 'peak', 'frequency': 300, 'gain': -1.0, 'q': 1.5},
                {'type': 'peak', 'frequency': 3000, 'gain': 1.5, 'q': 1.5},
                {'type': 'high_shelf', 'frequency': 10000, 'gain': 1.5, 'q': 0.7},
            ],
            'multiband': {
                'crossovers': [100, 400, 2500, 8000],
                'ratios': [2.5, 2.0, 2.0, 2.0, 1.5],
                'thresholds': [-16, -18, -16, -16, -18],
            },
            'saturation': {'tape': 0.25, 'tube': 0.15},
            'stereo_width': 110,
            'limiter': {'ceiling': -1.0, 'release': 150},
        },
        
        'rnb': {
            'target_lufs': -12.0,
            'ceiling_dbTP': -1.0,
            'eq': [
                {'type': 'low_shelf', 'frequency': 80, 'gain': 1.5, 'q': 0.7},
                {'type': 'peak', 'frequency': 200, 'gain': -0.5, 'q': 1.5},
                {'type': 'peak', 'frequency': 2500, 'gain': 1.0, 'q': 1.5},
                {'type': 'high_shelf', 'frequency': 8000, 'gain': 1.5, 'q': 0.7},
            ],
            'multiband': {
                'crossovers': [100, 400, 2000, 8000],
                'ratios': [2.0, 2.0, 1.8, 1.8, 1.5],
                'thresholds': [-18, -18, -17, -18, -20],
            },
            'saturation': {'tape': 0.20, 'tube': 0.25},
            'stereo_width': 110,
            'limiter': {'ceiling': -1.0, 'release': 150},
        },
        
        'acoustic': {
            'target_lufs': -14.0,
            'ceiling_dbTP': -1.5,
            'eq': [
                {'type': 'low_shelf', 'frequency': 100, 'gain': 0.5, 'q': 0.7},
                {'type': 'peak', 'frequency': 250, 'gain': -0.5, 'q': 1.5},
                {'type': 'peak', 'frequency': 3000, 'gain': 1.0, 'q': 1.5},
                {'type': 'high_shelf', 'frequency': 10000, 'gain': 1.0, 'q': 0.7},
            ],
            'multiband': {
                'crossovers': [100, 500, 2500, 10000],
                'ratios': [1.8, 1.5, 1.5, 1.5, 1.3],
                'thresholds': [-20, -20, -18, -20, -22],
            },
            'saturation': {'tape': 0.10, 'tube': 0.05},
            'stereo_width': 105,
            'limiter': {'ceiling': -1.5, 'release': 200},
        },
        
        'metal': {
            'target_lufs': -8.0,
            'ceiling_dbTP': -0.3,
            'eq': [
                {'type': 'low_shelf', 'frequency': 60, 'gain': 2.0, 'q': 0.7},
                {'type': 'peak', 'frequency': 400, 'gain': -2.0, 'q': 1.5},
                {'type': 'peak', 'frequency': 3500, 'gain': 2.0, 'q': 1.5},
                {'type': 'high_shelf', 'frequency': 10000, 'gain': 2.0, 'q': 0.7},
            ],
            'multiband': {
                'crossovers': [80, 400, 2000, 8000],
                'ratios': [4.0, 3.0, 2.5, 2.5, 2.0],
                'thresholds': [-8, -12, -12, -12, -14],
            },
            'saturation': {'tape': 0.35, 'tube': 0.25},
            'stereo_width': 115,
            'limiter': {'ceiling': -0.3, 'release': 40},
        },
    }
    
    @classmethod
    def get_mixing_preset(cls, genre: str) -> Dict[str, Any]:
        """Get mixing preset for a genre."""
        preset = cls.MIXING_PRESETS.get(genre, cls.MIXING_PRESETS['pop'])
        logger.info(f"Using mixing preset: {preset['name']}")
        return preset
    
    @classmethod
    def get_mastering_preset(cls, genre: str) -> Dict[str, Any]:
        """Get mastering preset for a genre."""
        preset = cls.MASTERING_PRESETS.get(genre, cls.MASTERING_PRESETS['pop'])
        logger.info(f"Using mastering preset: {genre} (LUFS: {preset['target_lufs']})")
        return preset
    
    @classmethod
    def get_full_preset(cls, genre: str) -> Dict[str, Any]:
        """Get both mixing and mastering presets for a genre."""
        return {
            'genre': genre,
            'mixing': cls.get_mixing_preset(genre),
            'mastering': cls.get_mastering_preset(genre),
        }
    
    @classmethod
    def list_genres(cls) -> list:
        """List all available genres."""
        return list(cls.MIXING_PRESETS.keys())
