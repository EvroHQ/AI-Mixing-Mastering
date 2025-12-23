"""
Genre Detector - Improved AI-powered music genre detection
Analyzes audio characteristics to determine optimal mixing/mastering approach
Now with better support for House/Electronic genres
"""

import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class GenreDetector:
    """
    Detects music genre from audio analysis for adaptive mixing/mastering.
    Improved version with better support for House, Afro House, and electronic genres.
    """
    
    # Genre characteristics based on professional mixing research
    GENRE_PROFILES = {
        'house': {
            'name': 'House / Afro House',
            'tempo_range': (118, 130),
            'bass_energy_high': True,
            'four_on_floor': True,
            'description': 'House music with 4/4 kick, groovy bass, and melodic elements'
        },
        'edm': {
            'name': 'EDM / Electronic',
            'tempo_range': (125, 160),
            'bass_energy_high': True,
            'crest_factor_low': True,
            'stereo_width_high': True,
            'description': 'Electronic dance music with heavy bass, pumping dynamics'
        },
        'hiphop': {
            'name': 'Hip-Hop / Trap',
            'tempo_range': (70, 100),
            'bass_energy_high': True,
            'sub_bass_dominant': True,
            'vocal_prominent': True,
            'description': 'Hip-hop with 808s, punchy drums, prominent vocals'
        },
        'pop': {
            'name': 'Pop',
            'tempo_range': (100, 130),
            'balanced_spectrum': True,
            'vocal_prominent': True,
            'bright_highs': True,
            'description': 'Commercial pop with clear vocals, polished sound'
        },
        'rock': {
            'name': 'Rock',
            'tempo_range': (100, 145),
            'mid_focus': True,
            'dynamic_range_high': True,
            'guitar_presence': True,
            'description': 'Rock with live energy, guitars, dynamic drums'
        },
        'rnb': {
            'name': 'R&B / Soul',
            'tempo_range': (60, 100),
            'warm_lows': True,
            'smooth_highs': True,
            'vocal_prominent': True,
            'description': 'Smooth R&B with warm bass, silky vocals'
        },
        'acoustic': {
            'name': 'Acoustic / Folk',
            'tempo_range': (80, 140),
            'dynamic_range_high': True,
            'natural_sound': True,
            'minimal_processing': True,
            'description': 'Acoustic music with natural dynamics, minimal processing'
        },
        'techno': {
            'name': 'Techno / Tech House',
            'tempo_range': (125, 145),
            'bass_energy_high': True,
            'minimal_vocals': True,
            'four_on_floor': True,
            'description': 'Techno with driving beats, hypnotic rhythms'
        }
    }
    
    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate
    
    def detect_genre(self, audio: np.ndarray) -> Dict:
        """
        Analyze audio and detect genre with confidence scores.
        
        Args:
            audio: Audio array (stereo or mono)
            
        Returns:
            Dict with detected genre, confidence, and all scores
        """
        logger.info("Starting genre detection analysis...")
        
        # Convert to mono for analysis
        if audio.ndim > 1:
            mono = np.mean(audio, axis=0) if audio.shape[0] == 2 else audio[0]
        else:
            mono = audio
        
        # Analyze audio characteristics
        analysis = self._analyze_audio(mono)
        
        # Log analysis results for debugging
        logger.info(f"  Analysis results:")
        logger.info(f"    Tempo: {analysis['tempo']:.1f} BPM")
        logger.info(f"    Bass ratio: {analysis['bass_ratio']:.3f}")
        logger.info(f"    Sub-bass ratio: {analysis['sub_bass_ratio']:.3f}")
        logger.info(f"    Mid ratio: {analysis['mid_ratio']:.3f}")
        logger.info(f"    Crest factor: {analysis['crest_factor']:.2f}")
        logger.info(f"    Transient density: {analysis['transient_density']:.2f}")
        logger.info(f"    Four-on-floor score: {analysis.get('four_on_floor_score', 0):.2f}")
        
        # Score each genre
        genre_scores = self._calculate_genre_scores(analysis)
        
        # Log scores for debugging
        logger.info(f"  Genre scores:")
        for genre, score in sorted(genre_scores.items(), key=lambda x: -x[1]):
            logger.info(f"    {genre}: {score:.1%}")
        
        # Get best match
        best_genre = max(genre_scores, key=genre_scores.get)
        confidence = genre_scores[best_genre]
        
        # =====================================================================
        # TEMPO-BASED OVERRIDE FOR ELECTRONIC MUSIC
        # If tempo is in house/techno range and confidence is low, override
        # =====================================================================
        tempo = analysis['tempo']
        
        # House override (118-130 BPM is VERY likely house/afro house)
        if 118 <= tempo <= 130 and best_genre not in ['house', 'techno', 'edm']:
            if confidence < 0.40:  # Low confidence in current detection
                logger.info(f"  ⚠️ Tempo {tempo:.0f} BPM is house range - overriding {best_genre} -> house")
                best_genre = 'house'
                confidence = 0.45  # Give it decent confidence
                genre_scores['house'] = confidence
        
        # Techno/EDM override (128-145 BPM)
        elif 128 <= tempo <= 145 and best_genre not in ['house', 'techno', 'edm']:
            if confidence < 0.40:
                logger.info(f"  ⚠️ Tempo {tempo:.0f} BPM is techno range - overriding {best_genre} -> techno")
                best_genre = 'techno'
                confidence = 0.40
                genre_scores['techno'] = confidence
        
        logger.info(f"Genre detected: {self.GENRE_PROFILES[best_genre]['name']} ({confidence:.1%})")
        
        return {
            'detected_genre': best_genre,
            'genre_name': self.GENRE_PROFILES[best_genre]['name'],
            'confidence': confidence,
            'description': self.GENRE_PROFILES[best_genre]['description'],
            'all_scores': genre_scores,
            'analysis': analysis
        }
    
    def _analyze_audio(self, audio: np.ndarray) -> Dict:
        """Perform comprehensive audio analysis."""
        
        analysis = {}
        
        # 1. Tempo detection
        analysis['tempo'] = self._detect_tempo(audio)
        
        # 2. Four-on-floor detection (for house/techno)
        analysis['four_on_floor_score'] = self._detect_four_on_floor(audio, analysis['tempo'])
        
        # 3. Spectral balance
        spectral = self._analyze_spectrum(audio)
        analysis.update(spectral)
        
        # 4. Dynamic range
        dynamics = self._analyze_dynamics(audio)
        analysis.update(dynamics)
        
        # 5. Transient density
        analysis['transient_density'] = self._detect_transients(audio)
        
        # 6. Energy
        analysis['estimated_energy'] = float(np.mean(np.abs(audio)))
        
        return analysis
    
    def _detect_tempo(self, audio: np.ndarray) -> float:
        """Detect tempo using onset detection and autocorrelation."""
        
        hop = 512
        window = 1024
        
        # Calculate onset envelope
        onset_env = []
        for i in range(0, len(audio) - window, hop):
            frame = audio[i:i+window]
            energy = np.sum(frame ** 2)
            onset_env.append(energy)
        
        onset_env = np.array(onset_env)
        
        if np.max(onset_env) > 0:
            onset_env = onset_env / np.max(onset_env)
        
        # Autocorrelation for tempo
        if len(onset_env) > 100:
            corr = np.correlate(onset_env, onset_env, mode='full')
            corr = corr[len(corr)//2:]
            
            # Find peaks in BPM range (60-200 BPM)
            min_lag = int(60 * self.sample_rate / hop / 200)  # 200 BPM
            max_lag = int(60 * self.sample_rate / hop / 60)   # 60 BPM
            
            if max_lag < len(corr):
                search_region = corr[min_lag:max_lag]
                if len(search_region) > 0:
                    peak_idx = np.argmax(search_region) + min_lag
                    if peak_idx > 0:
                        tempo = 60 * self.sample_rate / hop / peak_idx
                        return float(np.clip(tempo, 60, 200))
        
        return 120.0  # Default
    
    def _detect_four_on_floor(self, audio: np.ndarray, tempo: float) -> float:
        """
        Detect if the track has a four-on-the-floor kick pattern.
        This is characteristic of house, techno, and similar genres.
        """
        if tempo < 100 or tempo > 150:
            return 0.0
        
        # Calculate beat duration in samples
        beat_samples = int(self.sample_rate * 60 / tempo)
        
        # Low-pass filter to isolate kick
        try:
            nyq = self.sample_rate / 2
            low = 100 / nyq
            b, a = signal.butter(4, low, btype='low')
            low_audio = signal.filtfilt(b, a, audio[:min(len(audio), self.sample_rate * 30)])
        except:
            return 0.0
        
        # Get envelope
        envelope = np.abs(low_audio)
        
        # Check for regular beats
        beat_count = 0
        total_beats = 0
        
        for i in range(0, len(envelope) - beat_samples, beat_samples):
            segment = envelope[i:i + beat_samples]
            peak_pos = np.argmax(segment)
            
            # Check if peak is near the start of the beat (kick on downbeat)
            if peak_pos < beat_samples * 0.2:  # Within first 20% of beat
                beat_count += 1
            total_beats += 1
        
        if total_beats > 0:
            return float(beat_count / total_beats)
        return 0.0
    
    def _analyze_spectrum(self, audio: np.ndarray) -> Dict:
        """Analyze frequency spectrum distribution."""
        
        segment_length = min(len(audio), self.sample_rate * 30)
        segment = audio[:segment_length]
        
        n_fft = 4096
        freqs = fftfreq(n_fft, 1/self.sample_rate)[:n_fft//2]
        
        hop = n_fft // 2
        spectra = []
        
        for i in range(0, len(segment) - n_fft, hop):
            chunk = segment[i:i+n_fft]
            spec = np.abs(fft(chunk * np.hanning(n_fft)))[:n_fft//2]
            spectra.append(spec)
        
        if not spectra:
            return {
                'sub_bass_ratio': 0.0,
                'bass_ratio': 0.0,
                'mid_ratio': 0.0,
                'high_ratio': 0.0,
                'brightness': 0.0,
                'low_mid_ratio': 0.0,
                'presence_ratio': 0.0
            }
        
        avg_spectrum = np.mean(spectra, axis=0)
        total_energy = np.sum(avg_spectrum) + 1e-10
        
        # Frequency bands
        sub_bass = np.sum(avg_spectrum[(freqs >= 20) & (freqs < 60)])
        bass = np.sum(avg_spectrum[(freqs >= 60) & (freqs < 250)])
        low_mid = np.sum(avg_spectrum[(freqs >= 250) & (freqs < 500)])
        mid = np.sum(avg_spectrum[(freqs >= 500) & (freqs < 2000)])
        high_mid = np.sum(avg_spectrum[(freqs >= 2000) & (freqs < 6000)])
        high = np.sum(avg_spectrum[(freqs >= 6000) & (freqs < 20000)])
        
        return {
            'sub_bass_ratio': float(sub_bass / total_energy),
            'bass_ratio': float((sub_bass + bass) / total_energy),
            'mid_ratio': float((low_mid + mid) / total_energy),
            'high_ratio': float((high_mid + high) / total_energy),
            'brightness': float(high / (bass + 1e-10)),
            'low_mid_ratio': float(low_mid / total_energy),
            'presence_ratio': float(high_mid / total_energy)
        }
    
    def _analyze_dynamics(self, audio: np.ndarray) -> Dict:
        """Analyze dynamic characteristics."""
        
        rms = np.sqrt(np.mean(audio ** 2))
        rms_db = 20 * np.log10(rms + 1e-10)
        
        peak = np.max(np.abs(audio))
        peak_db = 20 * np.log10(peak + 1e-10)
        
        crest_factor = peak / (rms + 1e-10)
        crest_factor_db = peak_db - rms_db
        
        abs_audio = np.abs(audio)
        loud_threshold = np.percentile(abs_audio, 95)
        quiet_threshold = np.percentile(abs_audio[abs_audio > 0], 10)
        dynamic_range = 20 * np.log10(loud_threshold / (quiet_threshold + 1e-10))
        
        return {
            'rms_db': float(rms_db),
            'peak_db': float(peak_db),
            'crest_factor': float(crest_factor),
            'crest_factor_db': float(crest_factor_db),
            'dynamic_range_db': float(np.clip(dynamic_range, 0, 40))
        }
    
    def _detect_transients(self, audio: np.ndarray) -> float:
        """Detect transient density (percussiveness)."""
        
        hop = 512
        envelope = []
        
        for i in range(1, len(audio) // hop - 1):
            curr = np.sum(np.abs(audio[i*hop:(i+1)*hop]))
            prev = np.sum(np.abs(audio[(i-1)*hop:i*hop]))
            diff = max(0, curr - prev)
            envelope.append(diff)
        
        if not envelope:
            return 0.5
        
        envelope = np.array(envelope)
        threshold = np.mean(envelope) + np.std(envelope)
        transients = np.sum(envelope > threshold)
        
        duration_seconds = len(audio) / self.sample_rate
        transients_per_second = transients / duration_seconds
        
        return float(np.clip(transients_per_second / 10, 0, 1))
    
    def _calculate_genre_scores(self, analysis: Dict) -> Dict[str, float]:
        """Calculate genre probability scores based on analysis."""
        
        tempo = analysis['tempo']
        scores = {}
        
        logger.info(f"  Scoring with tempo={tempo:.1f}, bass={analysis['bass_ratio']:.2f}, mid={analysis['mid_ratio']:.2f}")
        
        # =====================================================================
        # HOUSE / AFRO HOUSE (118-130 BPM) - TEMPO IS KING
        # =====================================================================
        house_score = 0.0
        
        # Tempo is VERY important for house - 50% weight
        if 120 <= tempo <= 128:
            house_score += 0.50  # Perfect house tempo
        elif 118 <= tempo <= 130:
            house_score += 0.40  # Good house tempo
        elif 115 <= tempo <= 133:
            house_score += 0.25  # Acceptable
        
        # Bass presence (house has groovy bass)
        if analysis['bass_ratio'] > 0.15:
            house_score += 0.20
        
        # Not too mid-heavy (unlike rock)
        if analysis['mid_ratio'] < 0.45:
            house_score += 0.15
        
        # Percussive
        if analysis['transient_density'] > 0.25:
            house_score += 0.10
        
        # Bonus for four-on-floor if detected
        if analysis.get('four_on_floor_score', 0) > 0.4:
            house_score += 0.15
        
        scores['house'] = house_score
        
        # =====================================================================
        # TECHNO / TECH HOUSE (125-145 BPM)
        # =====================================================================
        techno_score = 0.0
        
        if 128 <= tempo <= 140:
            techno_score += 0.45
        elif 125 <= tempo <= 145:
            techno_score += 0.35
        
        if analysis['bass_ratio'] > 0.18:
            techno_score += 0.20
        
        if analysis['mid_ratio'] < 0.40:
            techno_score += 0.15
        
        if analysis.get('four_on_floor_score', 0) > 0.4:
            techno_score += 0.15
        
        scores['techno'] = techno_score
        
        # =====================================================================
        # EDM / ELECTRONIC (128-160 BPM, high energy)
        # =====================================================================
        edm_score = 0.0
        
        if 128 <= tempo <= 150:
            edm_score += 0.40
        elif 125 <= tempo <= 160:
            edm_score += 0.30
        
        if analysis['bass_ratio'] > 0.20:
            edm_score += 0.20
        
        # EDM often compressed
        if analysis['crest_factor'] < 6:
            edm_score += 0.15
        
        if analysis['high_ratio'] > 0.10:
            edm_score += 0.15
        
        scores['edm'] = edm_score
        
        # =====================================================================
        # HIP-HOP (70-100 BPM, heavy sub-bass)
        # =====================================================================
        hiphop_score = 0.0
        
        if 75 <= tempo <= 95:
            hiphop_score += 0.45
        elif 70 <= tempo <= 100:
            hiphop_score += 0.35
        elif 65 <= tempo <= 110:
            hiphop_score += 0.15
        
        # Heavy sub-bass
        if analysis['sub_bass_ratio'] > 0.06:
            hiphop_score += 0.25
        
        if analysis['bass_ratio'] > 0.25:
            hiphop_score += 0.15
        
        scores['hiphop'] = hiphop_score
        
        # =====================================================================
        # POP (100-125 BPM, balanced)
        # =====================================================================
        pop_score = 0.0
        
        if 100 <= tempo <= 125:
            pop_score += 0.30
        
        # Balanced spectrum
        if 0.12 < analysis['bass_ratio'] < 0.28:
            pop_score += 0.20
        
        if 0.25 < analysis['mid_ratio'] < 0.45:
            pop_score += 0.15
        
        if analysis['brightness'] > 0.4:
            pop_score += 0.15
        
        # Vocal presence
        if analysis['presence_ratio'] > 0.08:
            pop_score += 0.15
        
        scores['pop'] = pop_score
        
        # =====================================================================
        # ROCK (100-145 BPM, mid-heavy, VERY dynamic)
        # =====================================================================
        rock_score = 0.0
        
        # Tempo contributes less for rock
        if 100 <= tempo <= 145:
            rock_score += 0.10
        
        # Rock is MID-HEAVY (guitars) - key differentiator
        if analysis['mid_ratio'] > 0.50:
            rock_score += 0.30
        elif analysis['mid_ratio'] > 0.45:
            rock_score += 0.15
        
        # Rock is VERY dynamic (crest factor > 6)
        if analysis['crest_factor'] > 7:
            rock_score += 0.25
        elif analysis['crest_factor'] > 5:
            rock_score += 0.10
        
        # High dynamic range
        if analysis['dynamic_range_db'] > 18:
            rock_score += 0.20
        elif analysis['dynamic_range_db'] > 14:
            rock_score += 0.10
        
        # Low sub-bass (acoustic instruments)
        if analysis['sub_bass_ratio'] < 0.04:
            rock_score += 0.15
        
        scores['rock'] = rock_score
        
        # =====================================================================
        # R&B / SOUL (60-95 BPM, warm, smooth)
        # =====================================================================
        rnb_score = 0.0
        
        if 65 <= tempo <= 95:
            rnb_score += 0.40
        elif 60 <= tempo <= 100:
            rnb_score += 0.25
        
        if 0.15 < analysis['bass_ratio'] < 0.28:
            rnb_score += 0.20
        
        if analysis['brightness'] < 0.6:
            rnb_score += 0.15
        
        if analysis['presence_ratio'] > 0.08:
            rnb_score += 0.15
        
        scores['rnb'] = rnb_score
        
        # =====================================================================
        # ACOUSTIC (natural dynamics, mid-focused)
        # =====================================================================
        acoustic_score = 0.0
        
        # Very high dynamic range
        if analysis['dynamic_range_db'] > 20:
            acoustic_score += 0.35
        elif analysis['dynamic_range_db'] > 16:
            acoustic_score += 0.20
        
        # Very high crest factor
        if analysis['crest_factor'] > 8:
            acoustic_score += 0.30
        elif analysis['crest_factor'] > 6:
            acoustic_score += 0.15
        
        # Low bass
        if analysis['sub_bass_ratio'] < 0.03:
            acoustic_score += 0.20
        
        # Low transients (less percussive)
        if analysis['transient_density'] < 0.25:
            acoustic_score += 0.15
        
        scores['acoustic'] = acoustic_score
        
        # =====================================================================
        # Log all scores before normalization
        # =====================================================================
        logger.info(f"  Raw scores: {scores}")
        
        # =====================================================================
        # Normalize scores
        # =====================================================================
        total = sum(scores.values())
        if total > 0:
            scores = {k: v / total for k, v in scores.items()}
        
        return scores


def create_genre_detector(sample_rate: int = 48000) -> GenreDetector:
    """Factory function for GenreDetector."""
    return GenreDetector(sample_rate)
