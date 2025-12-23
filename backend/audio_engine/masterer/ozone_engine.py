"""
Professional Mastering Engine - iZotope Ozone Style
Complete mastering suite with: EQ, Dynamics, Imager, Exciter, Maximizer
"""

import numpy as np
from typing import Dict, Optional, List, Any
from scipy import signal
import logging

logger = logging.getLogger(__name__)


class OzoneStyleMasteringEngine:
    """
    All-in-One Mastering Engine inspired by iZotope Ozone
    
    Chain: EQ → Dynamics → Exciter → Imager → Maximizer
    """
    
    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate
        self.nyquist = sample_rate / 2
    
    # ========== EQ MODULE ==========
    def apply_eq(self, audio: np.ndarray, bands: List[Dict]) -> np.ndarray:
        """
        Mastering EQ - subtle adjustments for tonal balance
        Band types: high_pass, low_pass, low_shelf, high_shelf, peaking
        """
        result = audio.copy()
        
        for band in bands:
            band_type = band.get('type', 'peaking')
            freq = band.get('frequency', 1000)
            gain = band.get('gain', 0)
            q = band.get('q', 0.707)
            
            # Normalize frequency
            w0 = min(freq / self.nyquist, 0.99)
            
            try:
                if band_type == 'high_pass':
                    b, a = signal.butter(2, w0, btype='high')
                elif band_type == 'low_pass':
                    b, a = signal.butter(2, w0, btype='low')
                elif band_type == 'low_shelf':
                    b, a = self._design_shelf(w0, gain, q, shelf_type='low')
                elif band_type == 'high_shelf':
                    b, a = self._design_shelf(w0, gain, q, shelf_type='high')
                else:  # peaking
                    b, a = self._design_peak(w0, gain, q)
                
                # Apply filter to each channel
                for ch in range(result.shape[0]):
                    result[ch] = signal.filtfilt(b, a, result[ch])
                    
            except Exception as e:
                logger.warning(f"EQ band failed: {e}")
        
        return result
    
    def _design_shelf(self, w0: float, gain_db: float, q: float, shelf_type: str):
        """Design shelf filter"""
        A = 10 ** (gain_db / 40)
        omega = w0 * np.pi
        alpha = np.sin(omega) / (2 * q)
        cos_omega = np.cos(omega)
        
        if shelf_type == 'low':
            b0 = A * ((A + 1) - (A - 1) * cos_omega + 2 * np.sqrt(A) * alpha)
            b1 = 2 * A * ((A - 1) - (A + 1) * cos_omega)
            b2 = A * ((A + 1) - (A - 1) * cos_omega - 2 * np.sqrt(A) * alpha)
            a0 = (A + 1) + (A - 1) * cos_omega + 2 * np.sqrt(A) * alpha
            a1 = -2 * ((A - 1) + (A + 1) * cos_omega)
            a2 = (A + 1) + (A - 1) * cos_omega - 2 * np.sqrt(A) * alpha
        else:  # high
            b0 = A * ((A + 1) + (A - 1) * cos_omega + 2 * np.sqrt(A) * alpha)
            b1 = -2 * A * ((A - 1) + (A + 1) * cos_omega)
            b2 = A * ((A + 1) + (A - 1) * cos_omega - 2 * np.sqrt(A) * alpha)
            a0 = (A + 1) - (A - 1) * cos_omega + 2 * np.sqrt(A) * alpha
            a1 = 2 * ((A - 1) - (A + 1) * cos_omega)
            a2 = (A + 1) - (A - 1) * cos_omega - 2 * np.sqrt(A) * alpha
        
        return np.array([b0, b1, b2]) / a0, np.array([a0, a1, a2]) / a0
    
    def _design_peak(self, w0: float, gain_db: float, q: float):
        """Design peaking EQ filter"""
        A = 10 ** (gain_db / 40)
        omega = w0 * np.pi
        alpha = np.sin(omega) / (2 * q)
        cos_omega = np.cos(omega)
        
        b0 = 1 + alpha * A
        b1 = -2 * cos_omega
        b2 = 1 - alpha * A
        a0 = 1 + alpha / A
        a1 = -2 * cos_omega
        a2 = 1 - alpha / A
        
        return np.array([b0, b1, b2]) / a0, np.array([a0, a1, a2]) / a0
    
    # ========== DYNAMICS MODULE (Multiband Compressor) ==========
    def apply_dynamics(self, audio: np.ndarray, settings: Dict) -> np.ndarray:
        """
        Multiband dynamics processing
        Glues the mix together with subtle compression
        """
        if not settings:
            return audio
        
        crossovers = settings.get('crossovers', [100, 500, 2000, 8000])
        thresholds = settings.get('thresholds', [-18, -16, -14, -14, -16])
        ratios = settings.get('ratios', [2.0, 2.0, 2.0, 2.0, 2.0])
        attacks = settings.get('attacks', [20, 15, 10, 8, 5])
        releases = settings.get('releases', [150, 120, 80, 60, 50])
        parallel_mix = settings.get('parallel_mix', 0.3)
        
        # Split into bands
        bands = self._split_bands(audio, crossovers)
        
        # Compress each band
        compressed_bands = []
        for i, band in enumerate(bands):
            threshold = thresholds[i] if i < len(thresholds) else -16
            ratio = ratios[i] if i < len(ratios) else 2.0
            attack = attacks[i] if i < len(attacks) else 10
            release = releases[i] if i < len(releases) else 100
            
            compressed = self._compress_band(band, threshold, ratio, attack, release)
            compressed_bands.append(compressed)
        
        # Sum bands
        processed = np.sum(compressed_bands, axis=0)
        
        # Parallel compression mix
        result = audio * (1 - parallel_mix) + processed * parallel_mix
        
        return result
    
    def _split_bands(self, audio: np.ndarray, crossovers: List[float]) -> List[np.ndarray]:
        """Split audio into frequency bands"""
        bands = []
        remaining = audio.copy()
        
        for freq in crossovers:
            w0 = min(freq / self.nyquist, 0.99)
            try:
                b_low, a_low = signal.butter(4, w0, btype='low')
                b_high, a_high = signal.butter(4, w0, btype='high')
                
                low_band = np.zeros_like(remaining)
                high_band = np.zeros_like(remaining)
                
                for ch in range(remaining.shape[0]):
                    low_band[ch] = signal.filtfilt(b_low, a_low, remaining[ch])
                    high_band[ch] = signal.filtfilt(b_high, a_high, remaining[ch])
                
                bands.append(low_band)
                remaining = high_band
            except:
                pass
        
        bands.append(remaining)  # Highest band
        return bands
    
    def _compress_band(self, audio: np.ndarray, threshold_db: float, ratio: float,
                       attack_ms: float, release_ms: float) -> np.ndarray:
        """Apply compression to a single band"""
        threshold = 10 ** (threshold_db / 20)
        attack_samples = int(attack_ms * self.sample_rate / 1000)
        release_samples = int(release_ms * self.sample_rate / 1000)
        
        attack_coef = np.exp(-1.0 / max(attack_samples, 1))
        release_coef = np.exp(-1.0 / max(release_samples, 1))
        
        result = np.zeros_like(audio)
        
        for ch in range(audio.shape[0]):
            envelope = 0.0
            for i in range(len(audio[ch])):
                level = abs(audio[ch, i])
                
                if level > envelope:
                    envelope = attack_coef * envelope + (1 - attack_coef) * level
                else:
                    envelope = release_coef * envelope + (1 - release_coef) * level
                
                if envelope > threshold:
                    gain_reduction = threshold / envelope
                    gain = gain_reduction ** (1 - 1/ratio)
                else:
                    gain = 1.0
                
                result[ch, i] = audio[ch, i] * gain
        
        return result
    
    # ========== EXCITER MODULE ==========
    def apply_exciter(self, audio: np.ndarray, settings: Dict) -> np.ndarray:
        """
        Harmonic Exciter - adds warmth, brightness, and punch
        Modes: tape, tube, warm, bright
        """
        if not settings:
            return audio
        
        mode = settings.get('mode', 'tape')
        amount = settings.get('amount', 0.15)
        mix = settings.get('mix', 0.3)
        
        # Split into frequency bands for multiband excitation
        freq_split = settings.get('frequency', 3000)
        
        w0 = min(freq_split / self.nyquist, 0.99)
        b_low, a_low = signal.butter(2, w0, btype='low')
        b_high, a_high = signal.butter(2, w0, btype='high')
        
        low_band = np.zeros_like(audio)
        high_band = np.zeros_like(audio)
        
        for ch in range(audio.shape[0]):
            low_band[ch] = signal.filtfilt(b_low, a_low, audio[ch])
            high_band[ch] = signal.filtfilt(b_high, a_high, audio[ch])
        
        # Apply saturation based on mode
        if mode == 'tape':
            excited = self._tape_saturation(high_band, amount)
        elif mode == 'tube':
            excited = self._tube_saturation(high_band, amount)
        elif mode == 'warm':
            excited = self._tube_saturation(low_band, amount * 0.5)
            low_band = low_band * (1 - mix) + excited * mix
            excited = high_band  # Don't process highs for warm
        else:  # bright
            excited = self._tape_saturation(high_band, amount * 1.5)
        
        if mode != 'warm':
            high_band = high_band * (1 - mix) + excited * mix
        
        return low_band + high_band
    
    def _tape_saturation(self, audio: np.ndarray, drive: float) -> np.ndarray:
        """Tape-style saturation with soft clipping"""
        x = audio * (1 + drive * 3)
        return np.tanh(x) * 0.9
    
    def _tube_saturation(self, audio: np.ndarray, drive: float) -> np.ndarray:
        """Tube-style saturation with even harmonics"""
        x = audio * (1 + drive * 2)
        # Asymmetric soft clipping for tube character
        positive = np.tanh(x * 1.2) * 0.85
        negative = np.tanh(x * 0.8) * 0.95
        return np.where(x >= 0, positive, negative)
    
    # ========== IMAGER MODULE ==========
    def apply_imager(self, audio: np.ndarray, settings: Dict) -> np.ndarray:
        """
        Stereo Imager - controls stereo width per frequency band
        - Keep low frequencies mono/centered
        - Widen mids and highs for depth
        """
        if audio.ndim == 1:
            return audio
        
        low_width = settings.get('low_width', 80)      # Tighter bass
        mid_width = settings.get('mid_width', 100)     # Natural mids
        high_width = settings.get('high_width', 120)   # Wider highs
        low_freq = settings.get('low_crossover', 200)
        high_freq = settings.get('high_crossover', 4000)
        
        # Convert to Mid/Side
        mid = (audio[0] + audio[1]) / 2
        side = (audio[0] - audio[1]) / 2
        
        # Split into bands
        w_low = min(low_freq / self.nyquist, 0.99)
        w_high = min(high_freq / self.nyquist, 0.99)
        
        b_low, a_low = signal.butter(2, w_low, btype='low')
        b_band, a_band = signal.butter(2, [w_low, w_high], btype='band')
        b_high, a_high = signal.butter(2, w_high, btype='high')
        
        # Apply width per band
        side_low = signal.filtfilt(b_low, a_low, side) * (low_width / 100)
        side_mid = signal.filtfilt(b_band, a_band, side) * (mid_width / 100)
        side_high = signal.filtfilt(b_high, a_high, side) * (high_width / 100)
        
        side_processed = side_low + side_mid + side_high
        
        # Convert back to L/R
        left = mid + side_processed
        right = mid - side_processed
        
        return np.stack([left, right])
    
    # ========== MASTER BUS COMPRESSOR ==========
    def _master_bus_compress(self, audio: np.ndarray) -> np.ndarray:
        """
        Gentle master bus compression to reduce crest factor
        This makes the limiter work less hard
        """
        # Measure current crest factor
        peak = np.max(np.abs(audio))
        rms = np.sqrt(np.mean(audio ** 2))
        crest_factor_db = 20 * np.log10(max(peak / max(rms, 1e-10), 1e-10))
        
        logger.info(f"  Master bus crest factor: {crest_factor_db:.1f} dB")
        
        # If crest factor is high (>18dB), apply compression
        if crest_factor_db > 18:
            # Gentle compression settings
            threshold_db = -18
            ratio = 2.0  # Gentle ratio
            attack_ms = 30  # Slow attack to preserve transients
            release_ms = 250  # Slow release
            
            threshold = 10 ** (threshold_db / 20)
            attack_coef = np.exp(-1.0 / max(int(attack_ms * self.sample_rate / 1000), 1))
            release_coef = np.exp(-1.0 / max(int(release_ms * self.sample_rate / 1000), 1))
            
            result = np.zeros_like(audio)
            envelope = 0.0
            
            # Process both channels together (linked)
            peaks = np.maximum(np.abs(audio[0]), np.abs(audio[1]))
            
            for i in range(len(peaks)):
                peak_sample = peaks[i]
                
                if peak_sample > envelope:
                    envelope = attack_coef * envelope + (1 - attack_coef) * peak_sample
                else:
                    envelope = release_coef * envelope + (1 - release_coef) * peak_sample
                
                if envelope > threshold:
                    gain_reduction = (threshold / envelope) ** (1 - 1/ratio)
                else:
                    gain_reduction = 1.0
                
                result[0, i] = audio[0, i] * gain_reduction
                result[1, i] = audio[1, i] * gain_reduction
            
            # Measure new crest factor
            new_peak = np.max(np.abs(result))
            new_rms = np.sqrt(np.mean(result ** 2))
            new_crest = 20 * np.log10(max(new_peak / max(new_rms, 1e-10), 1e-10))
            
            logger.info(f"  After bus compression: {new_crest:.1f} dB crest (reduced {crest_factor_db - new_crest:.1f} dB)")
            
            return result
        else:
            logger.info("  Crest factor OK, skipping bus compression")
            return audio
    
    # ========== MAXIMIZER MODULE ==========
    def apply_maximizer(self, audio: np.ndarray, settings: Dict) -> np.ndarray:
        """
        Maximizer (Limiter) - final stage for loudness
        True-peak limiting with multiple stages
        """
        ceiling_db = settings.get('ceiling', -0.3)
        character = settings.get('character', 5)  # 1-10, affects release
        gain_db = settings.get('gain', 0)
        stages = settings.get('stages', 2)
        
        ceiling = 10 ** (ceiling_db / 20)
        
        # Apply input gain
        if gain_db > 0:
            audio = audio * (10 ** (gain_db / 20))
        
        # Check input level first
        input_peak = np.max(np.abs(audio))
        logger.info(f"    Maximizer input peak: {20 * np.log10(max(input_peak, 1e-10)):.1f} dB")
        
        # Multi-stage limiting for transparency
        for stage in range(stages):
            stage_ceiling = ceiling * (1.0 + 0.02 * (stages - 1 - stage))  # Higher ceiling first
            audio = self._limit(audio, stage_ceiling, character)
        
        # Final true-peak limiting with hard clip guarantee
        audio = self._true_peak_limit(audio, ceiling)
        
        # FINAL SAFETY: Hard clip to guarantee ceiling (belt and suspenders)
        audio = np.clip(audio, -ceiling, ceiling)
        
        output_peak = np.max(np.abs(audio))
        logger.info(f"    Maximizer output peak: {20 * np.log10(max(output_peak, 1e-10)):.1f} dB")
        
        return audio
    
    def _limit(self, audio: np.ndarray, ceiling: float, character: int) -> np.ndarray:
        """Soft-knee limiter with character control"""
        # Character affects release time (1=fast, 10=slow)
        release_ms = 20 + character * 15
        attack_ms = 0.1 + character * 0.1  # Faster attack for limiting
        
        attack_samples = max(int(attack_ms * self.sample_rate / 1000), 1)
        release_samples = max(int(release_ms * self.sample_rate / 1000), 1)
        
        attack_coef = np.exp(-1.0 / attack_samples)
        release_coef = np.exp(-1.0 / release_samples)
        
        result = np.zeros_like(audio)
        envelope = 0.0
        
        # Peak detection across both channels
        peaks = np.maximum(np.abs(audio[0]), np.abs(audio[1]))
        
        for i in range(len(peaks)):
            peak = peaks[i]
            
            if peak > envelope:
                envelope = attack_coef * envelope + (1 - attack_coef) * peak
            else:
                envelope = release_coef * envelope + (1 - release_coef) * peak
            
            if envelope > ceiling:
                gain = ceiling / envelope
            else:
                gain = 1.0
            
            result[0, i] = audio[0, i] * gain
            result[1, i] = audio[1, i] * gain
        
        return result
    
    def _true_peak_limit(self, audio: np.ndarray, ceiling: float) -> np.ndarray:
        """Simple brick-wall limiter without resampling artifacts"""
        result = audio.copy()
        
        # Use soft clipping (tanh) to avoid harsh digital clipping
        # Scale so that tanh approaches ceiling asymptotically
        scale = 1.5  # Soft knee amount
        
        for ch in range(result.shape[0]):
            # Find peaks above threshold
            threshold = ceiling * 0.9  # Start limiting 10% before ceiling
            
            for i in range(len(result[ch])):
                sample = result[ch, i]
                abs_sample = abs(sample)
                
                if abs_sample > threshold:
                    # Soft clip using tanh
                    sign = 1 if sample >= 0 else -1
                    # Map to 0-1 range above threshold
                    excess = (abs_sample - threshold) / (1.0 - threshold + 0.01)
                    # Apply soft knee
                    soft_gain = threshold + (ceiling - threshold) * np.tanh(excess * scale) / np.tanh(scale)
                    result[ch, i] = sign * min(soft_gain, ceiling)
        
        # Final hard clip as absolute safety
        result = np.clip(result, -ceiling, ceiling)
        
        return result
    
    # ========== LOUDNESS MEASUREMENT ==========
    def measure_loudness(self, audio: np.ndarray) -> Dict:
        """Measure integrated LUFS and peak (simplified, no resampling)"""
        # Ensure audio is 2D
        if audio.ndim == 1:
            audio = np.stack([audio, audio])
        
        # Simple peak measurement (no oversampling to avoid artifacts)
        peak_linear = np.max(np.abs(audio))
        peak_db = 20 * np.log10(max(peak_linear, 1e-10))
        
        # Simplified LUFS measurement with K-weighting approximation
        # High-shelf +4dB at 1500Hz
        w0 = min(1500 / self.nyquist, 0.99)
        try:
            b, a = signal.butter(1, w0, btype='high')
            weighted = np.zeros_like(audio)
            for ch in range(audio.shape[0]):
                weighted[ch] = signal.lfilter(b, a, audio[ch])
        except:
            weighted = audio
        
        # RMS calculation
        rms = np.sqrt(np.mean(weighted ** 2))
        lufs = 20 * np.log10(max(rms, 1e-10)) - 0.691
        
        return {
            'integrated_lufs': lufs,
            'true_peak_dbtp': peak_db
        }
    
    def normalize_to_lufs(self, audio: np.ndarray, target_lufs: float, max_gain_db: float = 24.0) -> np.ndarray:
        """Normalize audio to target LUFS with maximum gain limit"""
        current = self.measure_loudness(audio)
        current_lufs = current['integrated_lufs']
        
        gain_db = target_lufs - current_lufs
        
        # Limit maximum gain to prevent extreme over-amplification
        if gain_db > max_gain_db:
            logger.warning(f"    Limiting gain from {gain_db:.1f}dB to {max_gain_db:.1f}dB")
            gain_db = max_gain_db
        
        gain_db = np.clip(gain_db, -20, max_gain_db)
        
        logger.info(f"    Normalization: {current_lufs:.1f} → {current_lufs + gain_db:.1f} LUFS (gain: {gain_db:+.1f}dB)")
        
        gain = 10 ** (gain_db / 20)
        return audio * gain
    
    def ensure_true_peak_ceiling(self, audio: np.ndarray, ceiling: float, max_iterations: int = 3) -> np.ndarray:
        """Ensure peak is below ceiling with simple iterative gain reduction"""
        result = audio.copy()
        ceiling_db = 20 * np.log10(ceiling)
        
        for iteration in range(max_iterations):
            # Simple peak measurement (no resampling to avoid artifacts)
            peak_linear = np.max(np.abs(result))
            peak_db = 20 * np.log10(max(peak_linear, 1e-10))
            
            if peak_db <= ceiling_db + 0.1:  # Within tolerance
                logger.info(f"    Peak: {peak_db:.1f} dB (target: {ceiling_db:.1f} dB) - OK")
                break
            
            # Reduce gain to bring peak under ceiling
            reduction_db = peak_db - ceiling_db + 0.3  # Extra margin
            reduction_linear = 10 ** (-reduction_db / 20)
            result = result * reduction_linear
            logger.info(f"    Iteration {iteration + 1}: Peak={peak_db:.1f}dB, reducing by {reduction_db:.1f}dB")
        
        # Final hard clip as absolute safety
        result = np.clip(result, -ceiling, ceiling)
        
        return result
    
    # ========== MAIN MASTERING CHAIN ==========
    def master(
        self,
        audio: np.ndarray,
        target_lufs: float = -14.0,
        preset: Optional[Dict] = None
    ) -> Dict:
        """
        Complete iZotope-style mastering chain
        
        Chain order: EQ → Dynamics → Exciter → Imager → Loudness Norm → Maximizer
        """
        logger.info(f"Starting Ozone-style mastering (target: {target_lufs} LUFS)...")
        
        # Default preset if none provided
        if not preset:
            preset = {
                'eq': [
                    {'type': 'high_pass', 'frequency': 30, 'q': 0.7},
                    {'type': 'low_shelf', 'frequency': 80, 'gain': 0.5, 'q': 0.6},
                    {'type': 'peaking', 'frequency': 250, 'gain': -0.5, 'q': 1.0},
                    {'type': 'peaking', 'frequency': 3000, 'gain': 0.5, 'q': 1.0},
                    {'type': 'high_shelf', 'frequency': 10000, 'gain': 0.5, 'q': 0.7},
                ],
                'dynamics': {
                    'crossovers': [100, 500, 2000, 8000],
                    'thresholds': [-18, -16, -14, -14, -16],
                    'ratios': [2.0, 1.8, 1.5, 1.5, 1.8],
                    'attacks': [20, 15, 10, 8, 5],
                    'releases': [150, 120, 100, 80, 60],
                    'parallel_mix': 0.25,
                },
                'exciter': {
                    'mode': 'tape',
                    'amount': 0.1,
                    'mix': 0.2,
                    'frequency': 3000,
                },
                'imager': {
                    'low_width': 80,
                    'mid_width': 100,
                    'high_width': 115,
                    'low_crossover': 200,
                    'high_crossover': 4000,
                },
                'maximizer': {
                    'ceiling': -0.3,
                    'character': 5,
                    'gain': 0,
                    'stages': 2,
                },
            }
        
        processing_log = []
        
        # Ensure stereo
        if audio.ndim == 1:
            audio = np.stack([audio, audio])
        elif audio.shape[0] > audio.shape[1]:
            audio = audio.T
        
        # Measure input
        input_loudness = self.measure_loudness(audio)
        logger.info(f"  Input: {input_loudness['integrated_lufs']:.1f} LUFS, {input_loudness['true_peak_dbtp']:.1f} dBTP")
        
        # 1. EQ
        if preset.get('eq'):
            audio = self.apply_eq(audio, preset['eq'])
            processing_log.append(f"EQ: {len(preset['eq'])} bands")
            logger.info(f"  Applied EQ: {len(preset['eq'])} bands")
        
        # 2. Dynamics (Multiband Compression)
        if preset.get('dynamics'):
            audio = self.apply_dynamics(audio, preset['dynamics'])
            processing_log.append("Dynamics: multiband")
            logger.info("  Applied multiband dynamics")
        
        # 3. Exciter
        if preset.get('exciter'):
            audio = self.apply_exciter(audio, preset['exciter'])
            mode = preset['exciter'].get('mode', 'tape')
            processing_log.append(f"Exciter: {mode}")
            logger.info(f"  Applied {mode} exciter")
        
        # 4. Imager
        if preset.get('imager'):
            audio = self.apply_imager(audio, preset['imager'])
            processing_log.append("Imager: multiband")
            logger.info("  Applied stereo imaging")
        
        # 4.5 Master Bus Compression (reduce crest factor before normalization)
        audio = self._master_bus_compress(audio)
        processing_log.append("Bus Comp")
        
        # 5. Loudness Normalization (pre-limiter)
        audio = self.normalize_to_lufs(audio, target_lufs + 1)
        
        # 6. Maximizer
        ceiling_db = -1.0  # Default
        if preset.get('maximizer'):
            ceiling_db = preset['maximizer'].get('ceiling', -0.3)
            audio = self.apply_maximizer(audio, preset['maximizer'])
            processing_log.append(f"Maximizer: {ceiling_db} dBTP")
            logger.info(f"  Applied maximizer ({ceiling_db} dBTP ceiling)")
        
        # 7. Ensure True Peak is below ceiling (iterative)
        ceiling_linear = 10 ** (ceiling_db / 20)
        audio = self.ensure_true_peak_ceiling(audio, ceiling_linear)
        processing_log.append("TP Check")
        
        # Final loudness measurement
        output_loudness = self.measure_loudness(audio)
        logger.info(f"  Output: {output_loudness['integrated_lufs']:.1f} LUFS, {output_loudness['true_peak_dbtp']:.1f} dBTP")
        
        return {
            'audio': audio,
            'processing_log': processing_log,
            'input_lufs': input_loudness['integrated_lufs'],
            'input_peak_dbtp': input_loudness['true_peak_dbtp'],
            'final_lufs': output_loudness['integrated_lufs'],
            'true_peak_dbtp': output_loudness['true_peak_dbtp'],
        }
