import numpy as np
import soundfile as sf
from matchering import process, Result
from matchering.results import pcm16, pcm24
from pedalboard import Pedalboard, Limiter, Gain
from typing import Optional, Callable
from config import settings


class AudioMasterer:
    """Audio mastering engine using Matchering"""
    
    def __init__(self):
        self.sample_rate = 44100
        self.target_lufs = settings.TARGET_LUFS
        self.true_peak_limit = settings.TRUE_PEAK_LIMIT
    
    def master(
        self,
        input_file: str,
        output_file: str,
        reference_file: Optional[str] = None,
        progress_callback: Optional[Callable[[float], None]] = None
    ):
        """
        Master audio file
        
        Args:
            input_file: Path to input mixed file
            output_file: Path for output master
            reference_file: Optional reference track for matching
            progress_callback: Optional callback for progress updates (0-100)
        """
        if progress_callback:
            progress_callback(10)
        
        if reference_file:
            # Use Matchering for reference-based mastering
            self._master_with_reference(input_file, output_file, reference_file)
        else:
            # Use custom mastering chain
            self._master_standalone(input_file, output_file)
        
        if progress_callback:
            progress_callback(100)
    
    def _master_with_reference(self, input_file: str, output_file: str, reference_file: str):
        """
        Master using Matchering with reference track
        
        Args:
            input_file: Path to input file
            output_file: Path to output file
            reference_file: Path to reference track
        """
        # Use Matchering for reference-based mastering
        process(
            target=input_file,
            reference=reference_file,
            results=[
                pcm24(output_file)
            ]
        )
    
    def _master_standalone(self, input_file: str, output_file: str):
        """
        Master without reference using custom chain
        
        Args:
            input_file: Path to input file
            output_file: Path to output file
        """
        # Load audio
        audio, sr = sf.read(input_file)
        
        # Calculate current loudness
        current_lufs = self._calculate_lufs(audio)
        
        # Calculate gain adjustment to reach target LUFS
        gain_adjustment = self.target_lufs - current_lufs
        
        # Create mastering chain
        mastering_chain = Pedalboard([
            # Gain adjustment for loudness
            Gain(gain_db=gain_adjustment),
            
            # Final limiter for true-peak control
            Limiter(
                threshold_db=self.true_peak_limit,
                release_ms=50
            )
        ])
        
        # Process audio
        if len(audio.shape) == 1:
            # Mono
            mastered = mastering_chain(audio, sample_rate=sr)
        else:
            # Stereo
            mastered = mastering_chain(audio.T, sample_rate=sr).T
        
        # Save mastered file
        sf.write(output_file, mastered, sr, subtype='PCM_24')
    
    def _calculate_lufs(self, audio: np.ndarray) -> float:
        """
        Calculate integrated loudness (LUFS)
        
        Args:
            audio: Audio data
            
        Returns:
            Loudness in LUFS
        """
        # Simple RMS-based loudness estimation
        # (In production, use pyloudnorm for accurate LUFS)
        rms = np.sqrt(np.mean(audio ** 2))
        lufs = 20 * np.log10(rms) - 0.691
        return float(lufs)
