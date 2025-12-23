"""
Local Test Script for ROEX-style Mixing
Test the mixing engine locally without Backblaze
"""

import os
import sys
import numpy as np
import soundfile as sf
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from audio_engine.mixer.stem_processor import StemProcessor
from audio_engine.analyzer.genre_detector import GenreDetector
from audio_engine.masterer.ozone_engine import OzoneStyleMasteringEngine


def detect_stem_role(filename: str) -> str:
    """Detect stem role from filename"""
    name = filename.lower()
    
    # Common stem naming patterns
    if any(x in name for x in ['kick', 'bd', 'kick_drum']):
        return 'kick'
    elif any(x in name for x in ['snare', 'sd', 'clap']):
        return 'snare'
    elif any(x in name for x in ['hihat', 'hh', 'hat', 'cymbal', 'ride']):
        return 'hihat'
    elif any(x in name for x in ['perc', 'shaker', 'tamb', 'conga', 'bongo']):
        return 'percussion'
    elif any(x in name for x in ['drum', 'drums', 'beat', 'loop']):
        return 'drums'
    elif any(x in name for x in ['bass', 'sub', '808']):
        return 'bass'
    elif any(x in name for x in ['vocal', 'vox', 'voice', 'lead_voc']):
        return 'vocal'
    elif any(x in name for x in ['backing', 'bv', 'choir', 'harmony']):
        return 'backing_vocal'
    elif any(x in name for x in ['synth', 'keys', 'pad', 'chord']):
        return 'synth'
    elif any(x in name for x in ['lead', 'arp', 'pluck', 'melody']):
        return 'lead'
    elif any(x in name for x in ['guitar', 'gtr']):
        return 'guitar'
    elif any(x in name for x in ['piano', 'rhodes', 'organ']):
        return 'piano'
    elif any(x in name for x in ['fx', 'sfx', 'riser', 'impact', 'noise']):
        return 'fx'
    elif any(x in name for x in ['string', 'violin', 'cello']):
        return 'strings'
    else:
        return 'other'


def panning_to_stereo(audio: np.ndarray, angle: float) -> np.ndarray:
    """Apply panning angle to audio (-60 to +60 degrees)"""
    if audio.ndim == 1:
        # Convert mono to stereo
        audio = np.stack([audio, audio], axis=0)
    
    # Normalize angle to -1 to 1 range
    pan = angle / 60.0
    pan = np.clip(pan, -1, 1)
    
    # Calculate left/right gains (constant power panning)
    left_gain = np.cos((pan + 1) * np.pi / 4)
    right_gain = np.sin((pan + 1) * np.pi / 4)
    
    audio[0] *= left_gain
    audio[1] *= right_gain
    
    return audio


def process_local_stems(input_folder: str, output_folder: str, genre: str = None):
    """
    Process stems from a local folder
    
    Args:
        input_folder: Path to folder containing stem audio files
        output_folder: Path to save processed files
        genre: Optional genre override (e.g., 'house', 'hiphop', 'rock')
    """
    
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all audio files
    audio_extensions = {'.wav', '.aiff', '.flac', '.mp3'}
    stem_files = [f for f in input_path.iterdir() 
                  if f.suffix.lower() in audio_extensions]
    
    if not stem_files:
        logger.error(f"No audio files found in {input_folder}")
        return
    
    logger.info(f"Found {len(stem_files)} stems to process")
    
    # Load first file to get sample rate
    first_audio, sample_rate = sf.read(str(stem_files[0]))
    logger.info(f"Sample rate: {sample_rate} Hz")
    
    # Initialize processors
    stem_processor = StemProcessor(sample_rate)
    genre_detector = GenreDetector(sample_rate)
    
    # Detect genre if not provided
    if not genre:
        logger.info("Detecting genre from stems...")
        result = genre_detector.detect_genre(str(stem_files[0]))
        genre = result['genre']
        logger.info(f"Detected genre: {genre} ({result['confidence']*100:.0f}% confidence)")
    
    # Detect tempo
    tempo = genre_detector._detect_tempo(first_audio)
    logger.info(f"Detected tempo: {tempo:.1f} BPM")
    
    # Process each stem
    processed_stems = []
    max_length = 0
    
    for i, stem_file in enumerate(stem_files):
        logger.info(f"\n{'='*50}")
        logger.info(f"Processing: {stem_file.name}")
        
        # Load audio
        audio, sr = sf.read(str(stem_file))
        
        # Convert to float and normalize
        if audio.dtype != np.float32 and audio.dtype != np.float64:
            audio = audio.astype(np.float32) / np.iinfo(audio.dtype).max
        
        # Ensure 2D array (channels, samples)
        if audio.ndim == 1:
            audio = np.stack([audio, audio], axis=0)
        elif audio.ndim == 2 and audio.shape[1] == 2:
            audio = audio.T  # Transpose to (channels, samples)
        
        max_length = max(max_length, audio.shape[1])
        
        # Detect stem role
        role = detect_stem_role(stem_file.name)
        logger.info(f"  Role detected: {role}")
        
        # Process the stem
        result = stem_processor.process(
            audio,
            stem_role=role,
            tempo_bpm=tempo,
            genre=genre,
            track_index=i
        )
        
        processed_audio = result['audio']
        panning_angle = result.get('panning_angle', 0)
        
        # Apply panning
        if panning_angle != 0:
            processed_audio = panning_to_stereo(processed_audio, panning_angle)
            logger.info(f"  Panning: {panning_angle}°")
        
        # Save processed stem
        processed_stem_path = output_path / f"processed_{stem_file.stem}.wav"
        sf.write(str(processed_stem_path), processed_audio.T, sample_rate)
        logger.info(f"  Saved: {processed_stem_path.name}")
        
        processed_stems.append({
            'audio': processed_audio,
            'role': role,
            'panning': panning_angle,
            'log': result['processing_log']
        })
    
    # Pad all stems to same length
    for stem in processed_stems:
        if stem['audio'].shape[1] < max_length:
            padding = max_length - stem['audio'].shape[1]
            stem['audio'] = np.pad(stem['audio'], ((0, 0), (0, padding)))
    
    # Mix all stems together
    logger.info(f"\n{'='*50}")
    logger.info("MIXING ALL STEMS...")
    
    mix = np.zeros((2, max_length), dtype=np.float64)
    for stem in processed_stems:
        mix += stem['audio']
    
    # Measure current level
    rms = np.sqrt(np.mean(mix ** 2))
    current_rms_db = 20 * np.log10(max(rms, 1e-10))
    peak = np.max(np.abs(mix))
    peak_db = 20 * np.log10(max(peak, 1e-10))
    logger.info(f"  Raw mix: Peak={peak_db:.1f}dB, RMS={current_rms_db:.1f}dB")
    
    # Only prevent hard clipping - normalize peak to -0.5dB if above 0
    if peak > 1.0:
        gain_linear = 0.89 / peak  # -1dB headroom
        mix = mix * gain_linear
        logger.info(f"  Prevented clipping (peak was {peak_db:.1f}dB)")
    
    # Final levels
    final_peak = np.max(np.abs(mix))
    final_rms = np.sqrt(np.mean(mix ** 2))
    logger.info(f"  Pre-master: Peak={20*np.log10(final_peak):.1f}dB, RMS={20*np.log10(final_rms):.1f}dB")
    
    # Save the mix
    mix_path = output_path / "mix_pre_master.wav"
    sf.write(str(mix_path), mix.T, sample_rate)
    logger.info(f"Saved pre-master mix: {mix_path}")
    
    # Master the mix
    logger.info(f"\n{'='*50}")
    logger.info("SIMPLE TRANSPARENT MASTERING...")
    
    try:
        from audio_engine.masterer.simple_master import SimpleMasteringEngine
        
        # Determine platform
        platform = genre if genre in ['spotify', 'apple_music', 'youtube', 'soundcloud', 'club'] else 'spotify'
        
        logger.info(f"Platform preset: {platform}")
        
        mastering_engine = SimpleMasteringEngine(sample_rate)
        mastered = mastering_engine.master(mix, platform=platform)
        
        master_path = output_path / "master_final.wav"
        sf.write(str(master_path), mastered['audio'].T, sample_rate)
        logger.info(f"Saved mastered file: {master_path}")
        
        logger.info(f"  Final LUFS: {mastered['output_lufs']:.1f}")
        logger.info(f"  True Peak: {mastered['output_peak']:.1f} dBTP")
        logger.info(f"  Gain applied: {mastered['gain_applied']:+.1f} dB")
            
    except Exception as e:
        logger.warning(f"Mastering failed: {e}")
        import traceback
        traceback.print_exc()
        logger.info("Saving mix without mastering...")
        master_path = output_path / "master_final.wav"
        sf.write(str(master_path), mix.T, sample_rate)
    
    logger.info(f"\n{'='*50}")
    logger.info("DONE!")
    logger.info(f"Output folder: {output_path}")
    logger.info(f"Files created:")
    for f in output_path.iterdir():
        logger.info(f"  - {f.name}")
    
    return output_path


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test ROEX-style mixing locally")
    parser.add_argument("--input", "-i", default="test_stems", help="Input folder with stems")
    parser.add_argument("--output", "-o", default="test_output", help="Output folder")
    parser.add_argument("--genre", "-g", default=None, help="Genre/platform (e.g., house, hiphop, spotify, apple_music, youtube, club)")
    parser.add_argument("--platform", "-p", default=None, 
                        choices=['spotify', 'apple_music', 'youtube', 'soundcloud', 'club'],
                        help="Streaming platform preset (overrides genre for mastering)")
    parser.add_argument("--safe", "-s", action="store_true",
                        help="Safe mode: disable saturation, use conservative settings (no distortion)")
    
    args = parser.parse_args()
    
    # Platform overrides genre for mastering
    mastering_target = args.platform if args.platform else args.genre
    
    # If safe mode, use conservative preset
    if args.safe:
        mastering_target = 'conservative'
    
    print("\n" + "="*60)
    print("  MixMaster Local Test - ROEX + Ozone Style Processing")
    print("="*60)
    print(f"  Input:  {args.input}")
    print(f"  Output: {args.output}")
    print(f"  Genre:  {args.genre or 'auto-detect'}")
    print(f"  Platform: {args.platform or 'N/A (using genre preset)'}")
    print(f"  Safe Mode: {'ON (no saturation)' if args.safe else 'OFF'}")
    print("="*60 + "\n")
    
    # Create test_stems folder if it doesn't exist
    input_folder = Path(args.input)
    if not input_folder.exists():
        input_folder.mkdir(parents=True)
        print(f"\nCreated folder: {input_folder}")
        print(f"Please add your stem files (.wav, .aiff, .flac, .mp3) to this folder")
        print(f"Then run this script again.\n")
        sys.exit(0)
    
    # Use platform if specified, otherwise use genre
    process_local_stems(args.input, args.output, mastering_target or args.genre)

