"""
Professional Instrument Processing Presets
Based on ROEX TONN Audio Effects Guide and industry standards
"""

from typing import Dict, Any

# Panning angles: -60 (full left) to +60 (full right)
# Gain in dB, Q values: 0.1-10 (lower = wider curve)
# Compression: threshold, ratio, attack_ms, release_ms

INSTRUMENT_PRESETS: Dict[str, Dict[str, Any]] = {
    
    # ========== BASS INSTRUMENTS ==========
    'bass': {
        'name': 'Bass Guitar/Synth Bass',
        'description': 'Solid, consistent low end with clarity',
        'gainDb': -3,
        'panning_angle': 0,  # Always center
        'eq_settings': {
            'band_1': {'gain': 2, 'q': 0.7, 'centre_freq': 60},    # Sub boost
            'band_2': {'gain': -3, 'q': 0.5, 'centre_freq': 250},  # Cut mud
            'band_3': {'gain': 0, 'q': 0.8, 'centre_freq': 800},
            'band_4': {'gain': 1, 'q': 1.0, 'centre_freq': 2000},  # Add click
            'band_5': {'gain': -2, 'q': 0.5, 'centre_freq': 5000},
            'band_6': {'gain': -4, 'q': 0.3, 'centre_freq': 12000},  # Roll off highs
        },
        'compression_settings': {
            'threshold': -18,
            'ratio': 4,
            'attack_ms': 10,
            'release_ms': 80
        },
        'highpass_freq': 30,
    },
    
    # ========== DRUMS ==========
    'kick': {
        'name': 'Kick Drum',
        'description': 'Punchy low end with beater click definition',
        'gainDb': 0,
        'panning_angle': 0,  # Center
        'eq_settings': {
            'band_1': {'gain': 4, 'q': 1.0, 'centre_freq': 50},    # Sub punch
            'band_2': {'gain': -4, 'q': 0.8, 'centre_freq': 200},  # Box removal
            'band_3': {'gain': -2, 'q': 0.5, 'centre_freq': 500},  # Mud cut
            'band_4': {'gain': 3, 'q': 1.5, 'centre_freq': 3000},  # Beater click
            'band_5': {'gain': 0, 'q': 0.7, 'centre_freq': 6000},
            'band_6': {'gain': -6, 'q': 0.3, 'centre_freq': 12000},
        },
        'compression_settings': {
            'threshold': -12,
            'ratio': 6,
            'attack_ms': 3,
            'release_ms': 50
        },
        'highpass_freq': 25,
    },
    
    'snare': {
        'name': 'Snare Drum',
        'description': 'Punchy body with crisp snap',
        'gainDb': -2,
        'panning_angle': 0,  # Center or slight left (-5)
        'eq_settings': {
            'band_1': {'gain': -4, 'q': 0.6, 'centre_freq': 60},   # Cut sub
            'band_2': {'gain': 2, 'q': 0.8, 'centre_freq': 200},   # Body
            'band_3': {'gain': -2, 'q': 1.0, 'centre_freq': 500},  # Box cut
            'band_4': {'gain': 3, 'q': 1.2, 'centre_freq': 2500},  # Crack
            'band_5': {'gain': 2, 'q': 0.8, 'centre_freq': 5000},  # Snap
            'band_6': {'gain': 1, 'q': 0.5, 'centre_freq': 10000}, # Air
        },
        'compression_settings': {
            'threshold': -14,
            'ratio': 5,
            'attack_ms': 5,
            'release_ms': 40
        },
        'highpass_freq': 60,
    },
    
    'drums': {
        'name': 'Full Drum Kit / Drum Bus',
        'description': 'Balanced punch with room for all elements',
        'gainDb': 0,
        'panning_angle': 0,
        'eq_settings': {
            'band_1': {'gain': 2, 'q': 0.8, 'centre_freq': 60},
            'band_2': {'gain': -2, 'q': 0.6, 'centre_freq': 300},
            'band_3': {'gain': 0, 'q': 0.8, 'centre_freq': 800},
            'band_4': {'gain': 2, 'q': 1.0, 'centre_freq': 3000},
            'band_5': {'gain': 1, 'q': 0.7, 'centre_freq': 8000},
            'band_6': {'gain': 0, 'q': 0.5, 'centre_freq': 12000},
        },
        'compression_settings': {
            'threshold': -16,
            'ratio': 4,
            'attack_ms': 8,
            'release_ms': 60
        },
        'highpass_freq': 30,
    },
    
    'hihat': {
        'name': 'Hi-Hats / Cymbals',
        'description': 'Bright, crisp high-frequency elements with stereo width',
        'gainDb': -4,
        'panning_angle': 25,  # Slightly right (or -25 for left)
        'eq_settings': {
            'band_1': {'gain': -8, 'q': 0.5, 'centre_freq': 60},   # Kill sub
            'band_2': {'gain': -3, 'q': 0.7, 'centre_freq': 250},  # Cut low
            'band_3': {'gain': 1, 'q': 1.0, 'centre_freq': 1500},
            'band_4': {'gain': 3, 'q': 1.2, 'centre_freq': 4000},  # Presence
            'band_5': {'gain': 4, 'q': 0.8, 'centre_freq': 8000},  # Brightness
            'band_6': {'gain': 3, 'q': 0.5, 'centre_freq': 14000}, # Air/shimmer
        },
        'compression_settings': {
            'threshold': -15,
            'ratio': 4,
            'attack_ms': 5,
            'release_ms': 60
        },
        'highpass_freq': 300,
    },
    
    'percussion': {
        'name': 'Percussion / Shakers',
        'description': 'Rhythmic elements with width',
        'gainDb': -5,
        'panning_angle': -30,  # Opposite side from hihats
        'eq_settings': {
            'band_1': {'gain': -6, 'q': 0.5, 'centre_freq': 80},
            'band_2': {'gain': -2, 'q': 0.6, 'centre_freq': 200},
            'band_3': {'gain': 1, 'q': 0.8, 'centre_freq': 1000},
            'band_4': {'gain': 2, 'q': 1.0, 'centre_freq': 3500},
            'band_5': {'gain': 3, 'q': 0.8, 'centre_freq': 7000},
            'band_6': {'gain': 2, 'q': 0.6, 'centre_freq': 12000},
        },
        'compression_settings': {
            'threshold': -18,
            'ratio': 3,
            'attack_ms': 8,
            'release_ms': 70
        },
        'highpass_freq': 150,
    },
    
    # ========== SYNTHS ==========
    'synth': {
        'name': 'Synth Chords / Pads',
        'description': 'Warm, present mid-range with sparkle and width',
        'gainDb': -2,
        'panning_angle': 15,  # Slight right
        'eq_settings': {
            'band_1': {'gain': -6, 'q': 0.7, 'centre_freq': 80},   # Cut sub
            'band_2': {'gain': -2, 'q': 0.5, 'centre_freq': 200},  # Reduce mud
            'band_3': {'gain': 2, 'q': 1.2, 'centre_freq': 1000},  # Body
            'band_4': {'gain': 3, 'q': 1.5, 'centre_freq': 3000},  # Presence
            'band_5': {'gain': 2, 'q': 0.8, 'centre_freq': 8000},  # Sparkle
            'band_6': {'gain': 1, 'q': 0.5, 'centre_freq': 15000}, # Air
        },
        'compression_settings': {
            'threshold': -20,
            'ratio': 3,
            'attack_ms': 15,
            'release_ms': 100
        },
        'highpass_freq': 100,
        'stereo_width': 120,
    },
    
    'lead': {
        'name': 'Lead Synth / Lead Instrument',
        'description': 'Forward presence with harmonic enhancement',
        'gainDb': -5,
        'panning_angle': -15,  # Slight left (opposite from pads)
        'eq_settings': {
            'band_1': {'gain': -5, 'q': 0.7, 'centre_freq': 80},
            'band_2': {'gain': 1, 'q': 0.8, 'centre_freq': 400},
            'band_3': {'gain': 2, 'q': 1.0, 'centre_freq': 1200},
            'band_4': {'gain': 3, 'q': 1.2, 'centre_freq': 2500},  # Forward
            'band_5': {'gain': 4, 'q': 0.8, 'centre_freq': 6000},  # Clarity
            'band_6': {'gain': 2, 'q': 0.6, 'centre_freq': 12000}, # Shine
        },
        'compression_settings': {
            'threshold': -22,
            'ratio': 3,
            'attack_ms': 20,
            'release_ms': 150
        },
        'highpass_freq': 120,
    },
    
    'pad': {
        'name': 'Ambient Pads / Atmospheres',
        'description': 'Wide, lush background textures',
        'gainDb': -6,
        'panning_angle': 0,  # Center but with stereo width
        'eq_settings': {
            'band_1': {'gain': -8, 'q': 0.6, 'centre_freq': 100},  # Cut low
            'band_2': {'gain': -3, 'q': 0.5, 'centre_freq': 300},
            'band_3': {'gain': 1, 'q': 0.8, 'centre_freq': 800},
            'band_4': {'gain': 2, 'q': 1.0, 'centre_freq': 2500},
            'band_5': {'gain': 3, 'q': 0.6, 'centre_freq': 6000},
            'band_6': {'gain': 2, 'q': 0.4, 'centre_freq': 12000},
        },
        'compression_settings': {
            'threshold': -24,
            'ratio': 2,
            'attack_ms': 30,
            'release_ms': 200
        },
        'highpass_freq': 150,
        'stereo_width': 140,
    },
    
    # ========== VOCALS ==========
    'vocal': {
        'name': 'Lead Vocal',
        'description': 'Clear, present and intimate',
        'gainDb': 0,
        'panning_angle': 0,  # Always center
        'eq_settings': {
            'band_1': {'gain': -6, 'q': 0.7, 'centre_freq': 80},   # Rumble cut
            'band_2': {'gain': -2, 'q': 0.8, 'centre_freq': 250},  # Mud cut
            'band_3': {'gain': 1, 'q': 0.6, 'centre_freq': 800},   # Body
            'band_4': {'gain': 3, 'q': 1.0, 'centre_freq': 3000},  # Presence
            'band_5': {'gain': 2, 'q': 0.8, 'centre_freq': 5000},  # Clarity
            'band_6': {'gain': 1, 'q': 0.5, 'centre_freq': 12000}, # Air
        },
        'compression_settings': {
            'threshold': -16,
            'ratio': 4,
            'attack_ms': 10,
            'release_ms': 80
        },
        'highpass_freq': 80,
        'deess': True,
        'deess_freq': 6000,
    },
    
    'backing_vocal': {
        'name': 'Backing Vocals',
        'description': 'Support without competing with lead',
        'gainDb': -4,
        'panning_angle': 35,  # Wide panning (opposite sides: +35 and -35)
        'eq_settings': {
            'band_1': {'gain': -8, 'q': 0.6, 'centre_freq': 100},
            'band_2': {'gain': -3, 'q': 0.7, 'centre_freq': 300},
            'band_3': {'gain': 0, 'q': 0.8, 'centre_freq': 800},
            'band_4': {'gain': 2, 'q': 1.0, 'centre_freq': 2500},
            'band_5': {'gain': 1, 'q': 0.8, 'centre_freq': 5000},
            'band_6': {'gain': 0, 'q': 0.5, 'centre_freq': 10000},
        },
        'compression_settings': {
            'threshold': -18,
            'ratio': 3,
            'attack_ms': 15,
            'release_ms': 100
        },
        'highpass_freq': 120,
        'deess': True,
    },
    
    # ========== GUITARS ==========
    'guitar': {
        'name': 'Electric Guitar',
        'description': 'Full-range with bite',
        'gainDb': -3,
        'panning_angle': 20,  # Can be doubled on opposite sides
        'eq_settings': {
            'band_1': {'gain': -6, 'q': 0.6, 'centre_freq': 80},
            'band_2': {'gain': -1, 'q': 0.7, 'centre_freq': 250},
            'band_3': {'gain': 2, 'q': 1.0, 'centre_freq': 800},
            'band_4': {'gain': 3, 'q': 1.2, 'centre_freq': 2500},
            'band_5': {'gain': 2, 'q': 0.8, 'centre_freq': 5000},
            'band_6': {'gain': 0, 'q': 0.5, 'centre_freq': 10000},
        },
        'compression_settings': {
            'threshold': -18,
            'ratio': 3,
            'attack_ms': 15,
            'release_ms': 100
        },
        'highpass_freq': 80,
    },
    
    'acoustic_guitar': {
        'name': 'Acoustic Guitar',
        'description': 'Natural, open sound',
        'gainDb': -3,
        'panning_angle': -20,
        'eq_settings': {
            'band_1': {'gain': -4, 'q': 0.7, 'centre_freq': 100},
            'band_2': {'gain': -2, 'q': 0.6, 'centre_freq': 300},
            'band_3': {'gain': 1, 'q': 0.8, 'centre_freq': 800},
            'band_4': {'gain': 2, 'q': 1.0, 'centre_freq': 2000},
            'band_5': {'gain': 3, 'q': 0.7, 'centre_freq': 5000},
            'band_6': {'gain': 2, 'q': 0.5, 'centre_freq': 10000},
        },
        'compression_settings': {
            'threshold': -20,
            'ratio': 2.5,
            'attack_ms': 20,
            'release_ms': 120
        },
        'highpass_freq': 80,
    },
    
    # ========== KEYS & PIANO ==========
    'piano': {
        'name': 'Piano / Keys',
        'description': 'Full-range warmth with clarity',
        'gainDb': -2,
        'panning_angle': -10,
        'eq_settings': {
            'band_1': {'gain': -2, 'q': 0.7, 'centre_freq': 60},
            'band_2': {'gain': -1, 'q': 0.6, 'centre_freq': 250},
            'band_3': {'gain': 1, 'q': 0.8, 'centre_freq': 800},
            'band_4': {'gain': 2, 'q': 1.0, 'centre_freq': 2500},
            'band_5': {'gain': 2, 'q': 0.7, 'centre_freq': 6000},
            'band_6': {'gain': 1, 'q': 0.5, 'centre_freq': 12000},
        },
        'compression_settings': {
            'threshold': -22,
            'ratio': 2,
            'attack_ms': 25,
            'release_ms': 150
        },
        'highpass_freq': 40,
    },
    
    # ========== FX & OTHER ==========
    'fx': {
        'name': 'Sound Effects / FX',
        'description': 'Special effects with wide stereo placement',
        'gainDb': -6,
        'panning_angle': 45,  # Wide placement
        'eq_settings': {
            'band_1': {'gain': -4, 'q': 0.6, 'centre_freq': 100},
            'band_2': {'gain': -2, 'q': 0.5, 'centre_freq': 300},
            'band_3': {'gain': 1, 'q': 0.8, 'centre_freq': 1000},
            'band_4': {'gain': 2, 'q': 1.0, 'centre_freq': 3000},
            'band_5': {'gain': 3, 'q': 0.7, 'centre_freq': 7000},
            'band_6': {'gain': 2, 'q': 0.5, 'centre_freq': 14000},
        },
        'compression_settings': {
            'threshold': -20,
            'ratio': 2,
            'attack_ms': 15,
            'release_ms': 100
        },
        'highpass_freq': 100,
        'stereo_width': 150,
    },
    
    'strings': {
        'name': 'Strings / Orchestra',
        'description': 'Lush, wide string sections',
        'gainDb': -4,
        'panning_angle': 10,
        'eq_settings': {
            'band_1': {'gain': -4, 'q': 0.6, 'centre_freq': 80},
            'band_2': {'gain': -2, 'q': 0.5, 'centre_freq': 250},
            'band_3': {'gain': 1, 'q': 0.7, 'centre_freq': 700},
            'band_4': {'gain': 2, 'q': 0.9, 'centre_freq': 2000},
            'band_5': {'gain': 3, 'q': 0.7, 'centre_freq': 6000},
            'band_6': {'gain': 2, 'q': 0.5, 'centre_freq': 12000},
        },
        'compression_settings': {
            'threshold': -24,
            'ratio': 2,
            'attack_ms': 30,
            'release_ms': 200
        },
        'highpass_freq': 80,
        'stereo_width': 130,
    },
    
    'other': {
        'name': 'Other / Unknown',
        'description': 'Conservative processing for unknown sources',
        'gainDb': -4,
        'panning_angle': 0,
        'eq_settings': {
            'band_1': {'gain': -2, 'q': 0.7, 'centre_freq': 80},
            'band_2': {'gain': -1, 'q': 0.6, 'centre_freq': 300},
            'band_3': {'gain': 0, 'q': 0.8, 'centre_freq': 800},
            'band_4': {'gain': 1, 'q': 1.0, 'centre_freq': 2500},
            'band_5': {'gain': 1, 'q': 0.7, 'centre_freq': 6000},
            'band_6': {'gain': 0, 'q': 0.5, 'centre_freq': 12000},
        },
        'compression_settings': {
            'threshold': -20,
            'ratio': 2,
            'attack_ms': 20,
            'release_ms': 100
        },
        'highpass_freq': 60,
    },
}


# Panning strategies for stereo placement
PANNING_STRATEGIES = {
    'electronic': {
        # Electronic music - wide synths, centered bass/kick
        'bass': 0, 'kick': 0, 'sub': 0,
        'snare': 0, 'clap': 0,
        'hihat': 25, 'cymbal': -25,
        'percussion': -30,
        'synth': 15, 'pad': -15,
        'lead': 0, 'arp': 35,
        'vocal': 0, 'fx': 45,
    },
    'rock': {
        # Rock - rhythm guitars hard panned, drums natural
        'bass': 0, 'kick': 0,
        'snare': 0,
        'hihat': -15, 'overhead': 30,
        'guitar': 40, 'guitar_2': -40,  # Hard panned
        'acoustic': 20,
        'keys': -20, 'organ': 25,
        'vocal': 0, 'backing_vocal': 35,
    },
    'hiphop': {
        # Hip-hop - heavy center focus
        'bass': 0, '808': 0,
        'kick': 0, 'snare': 0,
        'hihat': 15, 'percussion': -20,
        'synth': 10, 'keys': -10,
        'vocal': 0, 'adlib': 30,
        'fx': 40,
    },
}


# Frequency ranges reference
FREQUENCY_RANGES = {
    'sub_bass': (20, 60),      # Fundamental low frequency energy
    'bass': (60, 250),          # Warmth and body
    'low_mids': (250, 800),     # Fullness and thickness
    'mids': (800, 2000),        # Presence and definition
    'upper_mids': (2000, 5000), # Clarity and articulation
    'highs': (5000, 20000),     # Brightness and air
}


def get_instrument_preset(stem_role: str) -> Dict[str, Any]:
    """Get processing preset for an instrument type"""
    # Normalize the role name
    role = stem_role.lower().replace(' ', '_').replace('-', '_')
    
    # Check for aliases
    aliases = {
        'lead_vocal': 'vocal',
        'main_vocal': 'vocal',
        'vox': 'vocal',
        'sub': 'bass',
        '808': 'bass',
        'synth_bass': 'bass',
        'kick_drum': 'kick',
        'hat': 'hihat',
        'hi_hat': 'hihat',
        'hats': 'hihat',
        'cymbal': 'hihat',
        'perc': 'percussion',
        'shaker': 'percussion',
        'tambourine': 'percussion',
        'chords': 'synth',
        'keys': 'piano',
        'keyboard': 'piano',
        'rhodes': 'piano',
        'organ': 'piano',
        'pluck': 'lead',
        'arp': 'lead',
        'sfx': 'fx',
        'riser': 'fx',
        'impact': 'fx',
        'ambient': 'pad',
        'atmosphere': 'pad',
        'texture': 'pad',
    }
    
    if role in aliases:
        role = aliases[role]
    
    return INSTRUMENT_PRESETS.get(role, INSTRUMENT_PRESETS['other'])


def get_panning_angle(stem_role: str, genre: str = 'electronic', track_index: int = 0) -> float:
    """Get panning angle for a stem based on genre and role"""
    strategy = PANNING_STRATEGIES.get(genre, PANNING_STRATEGIES['electronic'])
    role = stem_role.lower()
    
    # Get base panning from strategy
    base_panning = strategy.get(role, 0)
    
    # For duplicate instruments, alternate sides
    if track_index % 2 == 1 and base_panning != 0:
        base_panning = -base_panning
    
    return base_panning
