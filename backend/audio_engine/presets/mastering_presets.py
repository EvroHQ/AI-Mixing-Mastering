"""
Professional Mastering Presets
Based on industry standards and ROEX recommendations
"""

from typing import Dict, Any

# Mastering presets by genre and loudness target
MASTERING_PRESETS: Dict[str, Dict[str, Any]] = {
    
    # ========== ELECTRONIC / HOUSE / EDM ==========
    'electronic': {
        'name': 'Electronic / House / EDM',
        'description': 'Punchy, loud, club-ready masters',
        'target_lufs': -9,  # Loud for clubs
        'ceiling_dbtp': -0.3,
        'eq': [
            {'type': 'high_pass', 'frequency': 25, 'q': 0.7},  # Remove sub-rumble
            {'type': 'low_shelf', 'frequency': 60, 'gain': 1.5, 'q': 0.6},  # Sub boost
            {'type': 'peaking', 'frequency': 100, 'gain': 0.5, 'q': 1.0},  # Kick punch
            {'type': 'peaking', 'frequency': 250, 'gain': -1.0, 'q': 1.0},  # Cut mud
            {'type': 'peaking', 'frequency': 3500, 'gain': 1.0, 'q': 1.0},  # Presence
            {'type': 'high_shelf', 'frequency': 10000, 'gain': 1.5, 'q': 0.7},  # Air
        ],
        'multiband': {
            'crossovers': [80, 250, 2500, 8000],
            'thresholds': [-18, -16, -14, -14, -16],
            'ratios': [3.0, 2.5, 2.0, 2.0, 2.5],
            'attacks': [20, 15, 10, 8, 5],
            'releases': [150, 120, 80, 60, 50],
            'parallel_mix': 0.4,
        },
        'saturation': {
            'tape': 0.2,
            'tube': 0.15,
        },
        'stereo_width': 115,
        'limiter': {
            'ceiling': -0.3,
            'release': 80,
            'stages': 3,
        }
    },
    
    'house': {
        'name': 'House / Afro House',
        'description': 'Warm, punchy house masters',
        'target_lufs': -10,
        'ceiling_dbtp': -0.5,
        'eq': [
            {'type': 'high_pass', 'frequency': 28, 'q': 0.7},
            {'type': 'low_shelf', 'frequency': 55, 'gain': 2.0, 'q': 0.6},  # Strong sub
            {'type': 'peaking', 'frequency': 120, 'gain': 1.0, 'q': 0.8},  # Kick body
            {'type': 'peaking', 'frequency': 300, 'gain': -1.5, 'q': 1.2},  # Clear mud
            {'type': 'peaking', 'frequency': 4000, 'gain': 0.5, 'q': 1.0},  # Clarity
            {'type': 'high_shelf', 'frequency': 12000, 'gain': 1.0, 'q': 0.7},
        ],
        'multiband': {
            'crossovers': [80, 300, 3000, 8000],
            'thresholds': [-16, -15, -14, -14, -15],
            'ratios': [2.5, 2.0, 1.8, 1.8, 2.0],
            'attacks': [25, 15, 10, 8, 5],
            'releases': [180, 150, 100, 80, 60],
            'parallel_mix': 0.35,
        },
        'saturation': {
            'tape': 0.18,
            'tube': 0.12,
        },
        'stereo_width': 110,
        'limiter': {
            'ceiling': -0.5,
            'release': 100,
            'stages': 3,
        }
    },
    
    # ========== HIP-HOP / RAP ==========
    'hiphop': {
        'name': 'Hip-Hop / Rap',
        'description': 'Heavy low-end, crisp highs',
        'target_lufs': -10,
        'ceiling_dbtp': -0.3,
        'eq': [
            {'type': 'high_pass', 'frequency': 30, 'q': 0.7},
            {'type': 'low_shelf', 'frequency': 50, 'gain': 2.5, 'q': 0.5},  # 808 emphasis
            {'type': 'peaking', 'frequency': 100, 'gain': 1.0, 'q': 0.8},
            {'type': 'peaking', 'frequency': 400, 'gain': -1.0, 'q': 1.0},
            {'type': 'peaking', 'frequency': 3000, 'gain': 1.5, 'q': 1.2},  # Vocal presence
            {'type': 'high_shelf', 'frequency': 10000, 'gain': 2.0, 'q': 0.7},  # Crisp
        ],
        'multiband': {
            'crossovers': [60, 200, 2000, 6000],
            'thresholds': [-15, -14, -13, -14, -15],
            'ratios': [3.5, 2.5, 2.0, 2.0, 2.5],
            'attacks': [30, 20, 12, 8, 5],
            'releases': [200, 150, 100, 80, 50],
            'parallel_mix': 0.4,
        },
        'saturation': {
            'tape': 0.15,
            'tube': 0.1,
        },
        'stereo_width': 105,
        'limiter': {
            'ceiling': -0.3,
            'release': 60,
            'stages': 3,
        }
    },
    
    # ========== POP ==========
    'pop': {
        'name': 'Pop / Commercial',
        'description': 'Balanced, radio-ready masters',
        'target_lufs': -11,
        'ceiling_dbtp': -1.0,
        'eq': [
            {'type': 'high_pass', 'frequency': 35, 'q': 0.7},
            {'type': 'low_shelf', 'frequency': 80, 'gain': 1.0, 'q': 0.6},
            {'type': 'peaking', 'frequency': 250, 'gain': -0.5, 'q': 1.0},
            {'type': 'peaking', 'frequency': 2500, 'gain': 1.0, 'q': 1.5},  # Presence
            {'type': 'high_shelf', 'frequency': 8000, 'gain': 1.5, 'q': 0.7},  # Sparkle
        ],
        'multiband': {
            'crossovers': [100, 400, 2500, 8000],
            'thresholds': [-16, -15, -14, -15, -16],
            'ratios': [2.0, 1.8, 1.5, 1.5, 1.8],
            'attacks': [20, 15, 10, 8, 5],
            'releases': [150, 120, 100, 80, 60],
            'parallel_mix': 0.3,
        },
        'saturation': {
            'tape': 0.1,
            'tube': 0.08,
        },
        'stereo_width': 108,
        'limiter': {
            'ceiling': -1.0,
            'release': 120,
            'stages': 2,
        }
    },
    
    # ========== ROCK / INDIE ==========
    'rock': {
        'name': 'Rock / Indie',
        'description': 'Punchy, aggressive masters',
        'target_lufs': -11,
        'ceiling_dbtp': -0.5,
        'eq': [
            {'type': 'high_pass', 'frequency': 35, 'q': 0.7},
            {'type': 'low_shelf', 'frequency': 100, 'gain': 1.0, 'q': 0.6},
            {'type': 'peaking', 'frequency': 250, 'gain': -1.0, 'q': 1.2},
            {'type': 'peaking', 'frequency': 700, 'gain': 0.5, 'q': 1.0},  # Guitar body
            {'type': 'peaking', 'frequency': 3500, 'gain': 1.5, 'q': 1.2},  # Attack
            {'type': 'high_shelf', 'frequency': 10000, 'gain': 0.5, 'q': 0.7},
        ],
        'multiband': {
            'crossovers': [100, 500, 2500, 8000],
            'thresholds': [-15, -14, -13, -14, -15],
            'ratios': [2.5, 2.0, 2.0, 2.0, 2.0],
            'attacks': [15, 12, 8, 6, 4],
            'releases': [120, 100, 80, 60, 40],
            'parallel_mix': 0.35,
        },
        'saturation': {
            'tape': 0.25,  # More tape saturation for rock
            'tube': 0.15,
        },
        'stereo_width': 112,
        'limiter': {
            'ceiling': -0.5,
            'release': 80,
            'stages': 3,
        }
    },
    
    # ========== R&B / SOUL ==========
    'rnb': {
        'name': 'R&B / Soul',
        'description': 'Warm, smooth masters',
        'target_lufs': -12,
        'ceiling_dbtp': -1.0,
        'eq': [
            {'type': 'high_pass', 'frequency': 30, 'q': 0.7},
            {'type': 'low_shelf', 'frequency': 80, 'gain': 1.5, 'q': 0.6},  # Warm bass
            {'type': 'peaking', 'frequency': 300, 'gain': -0.5, 'q': 1.0},
            {'type': 'peaking', 'frequency': 2000, 'gain': 0.5, 'q': 1.5},  # Vocal clarity
            {'type': 'high_shelf', 'frequency': 8000, 'gain': 1.0, 'q': 0.7},
        ],
        'multiband': {
            'crossovers': [80, 300, 2500, 8000],
            'thresholds': [-18, -16, -15, -16, -17],
            'ratios': [2.0, 1.8, 1.5, 1.5, 1.8],
            'attacks': [25, 20, 15, 10, 8],
            'releases': [180, 150, 120, 100, 80],
            'parallel_mix': 0.25,
        },
        'saturation': {
            'tape': 0.12,
            'tube': 0.15,  # More tube for warmth
        },
        'stereo_width': 105,
        'limiter': {
            'ceiling': -1.0,
            'release': 150,
            'stages': 2,
        }
    },
    
    # ========== ACOUSTIC / FOLK ==========
    'acoustic': {
        'name': 'Acoustic / Folk',
        'description': 'Natural, dynamic masters',
        'target_lufs': -14,
        'ceiling_dbtp': -1.0,
        'eq': [
            {'type': 'high_pass', 'frequency': 40, 'q': 0.7},
            {'type': 'low_shelf', 'frequency': 100, 'gain': 0.5, 'q': 0.6},
            {'type': 'peaking', 'frequency': 250, 'gain': -0.5, 'q': 1.0},
            {'type': 'peaking', 'frequency': 3000, 'gain': 0.5, 'q': 1.0},
            {'type': 'high_shelf', 'frequency': 10000, 'gain': 1.0, 'q': 0.7},
        ],
        'multiband': None,  # Skip multiband for natural sound
        'saturation': {
            'tape': 0.05,  # Very subtle
            'tube': 0.05,
        },
        'stereo_width': 100,  # Natural width
        'limiter': {
            'ceiling': -1.0,
            'release': 200,
            'stages': 2,
        }
    },
    
    # ========== STREAMING OPTIMIZED ==========
    'streaming': {
        'name': 'Streaming Optimized',
        'description': 'Optimized for Spotify, Apple Music, YouTube',
        'target_lufs': -14,  # Spotify target
        'ceiling_dbtp': -1.0,
        'eq': [
            {'type': 'high_pass', 'frequency': 30, 'q': 0.7},
            {'type': 'peaking', 'frequency': 200, 'gain': -0.5, 'q': 1.0},
            {'type': 'peaking', 'frequency': 3000, 'gain': 0.5, 'q': 1.0},
            {'type': 'high_shelf', 'frequency': 10000, 'gain': 0.5, 'q': 0.7},
        ],
        'multiband': {
            'crossovers': [100, 400, 2500, 8000],
            'thresholds': [-18, -17, -16, -17, -18],
            'ratios': [1.8, 1.5, 1.3, 1.3, 1.5],
            'attacks': [25, 20, 15, 10, 8],
            'releases': [180, 150, 120, 100, 80],
            'parallel_mix': 0.2,
        },
        'saturation': {
            'tape': 0.08,
            'tube': 0.05,
        },
        'stereo_width': 105,
        'limiter': {
            'ceiling': -1.0,
            'release': 150,
            'stages': 2,
        }
    },
    
    # ========== CONSERVATIVE / SAFE ==========
    'conservative': {
        'name': 'Conservative / Safe',
        'description': 'Minimal processing, preserves dynamics',
        'target_lufs': -14,
        'ceiling_dbtp': -1.0,
        'eq': [
            {'type': 'high_pass', 'frequency': 25, 'q': 0.7},
        ],
        'multiband': None,
        'saturation': None,
        'stereo_width': 100,
        'limiter': {
            'ceiling': -1.0,
            'release': 200,
            'stages': 1,
        }
    },
    
    # ========== STREAMING PLATFORMS ==========
    'spotify': {
        'name': 'Spotify',
        'description': 'Optimized for Spotify (-14 LUFS normalization)',
        'target_lufs': -14,
        'ceiling_dbtp': -1.0,
        'eq': [
            {'type': 'high_pass', 'frequency': 30, 'q': 0.7},
            {'type': 'peaking', 'frequency': 200, 'gain': -0.5, 'q': 1.0},
            {'type': 'peaking', 'frequency': 3000, 'gain': 0.5, 'q': 1.0},
            {'type': 'high_shelf', 'frequency': 10000, 'gain': 0.5, 'q': 0.7},
        ],
        'multiband': {
            'crossovers': [100, 400, 2500, 8000],
            'thresholds': [-18, -17, -16, -17, -18],
            'ratios': [1.8, 1.5, 1.3, 1.3, 1.5],
            'attacks': [25, 20, 15, 10, 8],
            'releases': [180, 150, 120, 100, 80],
            'parallel_mix': 0.2,
        },
        'saturation': {
            'tape': 0.08,
            'tube': 0.05,
        },
        'stereo_width': 105,
        'limiter': {
            'ceiling': -1.0,
            'release': 150,
            'stages': 2,
        }
    },
    
    'apple_music': {
        'name': 'Apple Music',
        'description': 'Optimized for Apple Music (-16 LUFS normalization)',
        'target_lufs': -16,
        'ceiling_dbtp': -1.0,
        'eq': [
            {'type': 'high_pass', 'frequency': 30, 'q': 0.7},
            {'type': 'peaking', 'frequency': 250, 'gain': -0.5, 'q': 1.0},
            {'type': 'peaking', 'frequency': 3000, 'gain': 0.5, 'q': 1.0},
            {'type': 'high_shelf', 'frequency': 10000, 'gain': 0.5, 'q': 0.7},
        ],
        'multiband': {
            'crossovers': [100, 400, 2500, 8000],
            'thresholds': [-20, -18, -17, -18, -20],
            'ratios': [1.5, 1.3, 1.2, 1.2, 1.3],
            'attacks': [30, 25, 20, 15, 10],
            'releases': [200, 180, 150, 120, 100],
            'parallel_mix': 0.15,
        },
        'saturation': {
            'tape': 0.05,
            'tube': 0.03,
        },
        'stereo_width': 102,
        'limiter': {
            'ceiling': -1.0,
            'release': 180,
            'stages': 2,
        }
    },
    
    'youtube': {
        'name': 'YouTube',
        'description': 'Optimized for YouTube (-14 LUFS normalization)',
        'target_lufs': -14,
        'ceiling_dbtp': -1.0,
        'eq': [
            {'type': 'high_pass', 'frequency': 35, 'q': 0.7},
            {'type': 'peaking', 'frequency': 200, 'gain': -0.5, 'q': 1.0},
            {'type': 'peaking', 'frequency': 2500, 'gain': 0.5, 'q': 1.0},
            {'type': 'high_shelf', 'frequency': 8000, 'gain': 0.5, 'q': 0.7},
        ],
        'multiband': {
            'crossovers': [100, 400, 2500, 8000],
            'thresholds': [-18, -17, -16, -17, -18],
            'ratios': [1.8, 1.5, 1.3, 1.3, 1.5],
            'attacks': [25, 20, 15, 10, 8],
            'releases': [180, 150, 120, 100, 80],
            'parallel_mix': 0.2,
        },
        'saturation': {
            'tape': 0.08,
            'tube': 0.05,
        },
        'stereo_width': 105,
        'limiter': {
            'ceiling': -1.0,
            'release': 150,
            'stages': 2,
        }
    },
    
    'soundcloud': {
        'name': 'SoundCloud',
        'description': 'Optimized for SoundCloud (louder, -10 to -12 LUFS)',
        'target_lufs': -11,
        'ceiling_dbtp': -0.5,
        'eq': [
            {'type': 'high_pass', 'frequency': 30, 'q': 0.7},
            {'type': 'low_shelf', 'frequency': 80, 'gain': 1.0, 'q': 0.6},
            {'type': 'peaking', 'frequency': 250, 'gain': -0.5, 'q': 1.0},
            {'type': 'peaking', 'frequency': 3000, 'gain': 1.0, 'q': 1.0},
            {'type': 'high_shelf', 'frequency': 10000, 'gain': 1.0, 'q': 0.7},
        ],
        'multiband': {
            'crossovers': [100, 400, 2500, 8000],
            'thresholds': [-16, -15, -14, -15, -16],
            'ratios': [2.0, 1.8, 1.5, 1.5, 1.8],
            'attacks': [20, 15, 10, 8, 5],
            'releases': [150, 120, 100, 80, 60],
            'parallel_mix': 0.3,
        },
        'saturation': {
            'tape': 0.12,
            'tube': 0.08,
        },
        'stereo_width': 108,
        'limiter': {
            'ceiling': -0.5,
            'release': 100,
            'stages': 2,
        }
    },
    
    'club': {
        'name': 'Club / DJ',
        'description': 'Loud, punchy for club playback (-8 to -10 LUFS)',
        'target_lufs': -9,
        'ceiling_dbtp': -0.3,
        'eq': [
            {'type': 'high_pass', 'frequency': 25, 'q': 0.7},
            {'type': 'low_shelf', 'frequency': 60, 'gain': 2.0, 'q': 0.6},
            {'type': 'peaking', 'frequency': 100, 'gain': 0.5, 'q': 0.8},
            {'type': 'peaking', 'frequency': 300, 'gain': -1.0, 'q': 1.0},
            {'type': 'peaking', 'frequency': 4000, 'gain': 1.0, 'q': 1.0},
            {'type': 'high_shelf', 'frequency': 12000, 'gain': 1.5, 'q': 0.7},
        ],
        'multiband': {
            'crossovers': [80, 250, 2500, 8000],
            'thresholds': [-15, -14, -12, -12, -14],
            'ratios': [3.0, 2.5, 2.0, 2.0, 2.5],
            'attacks': [15, 10, 8, 6, 4],
            'releases': [120, 100, 80, 60, 40],
            'parallel_mix': 0.4,
        },
        'saturation': {
            'tape': 0.2,
            'tube': 0.15,
        },
        'stereo_width': 115,
        'limiter': {
            'ceiling': -0.3,
            'release': 60,
            'stages': 3,
        }
    },
}


def get_mastering_preset(genre: str) -> Dict[str, Any]:
    """Get mastering preset for a genre"""
    genre_lower = genre.lower().replace(' ', '_').replace('-', '_')
    
    # Aliases
    aliases = {
        'afro_house': 'house',
        'deep_house': 'house',
        'tech_house': 'house',
        'techno': 'electronic',
        'edm': 'electronic',
        'trance': 'electronic',
        'dubstep': 'electronic',
        'drum_and_bass': 'electronic',
        'dnb': 'electronic',
        'hip_hop': 'hiphop',
        'rap': 'hiphop',
        'trap': 'hiphop',
        'rnb': 'rnb',
        'r_b': 'rnb',
        'soul': 'rnb',
        'indie': 'rock',
        'alternative': 'rock',
        'metal': 'rock',
        'folk': 'acoustic',
        'classical': 'acoustic',
        'jazz': 'acoustic',
    }
    
    if genre_lower in aliases:
        genre_lower = aliases[genre_lower]
    
    return MASTERING_PRESETS.get(genre_lower, MASTERING_PRESETS['streaming'])
