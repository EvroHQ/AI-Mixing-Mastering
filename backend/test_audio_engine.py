"""
Test Script for MixMaster Pro Audio Engine
Simple test to validate the complete pipeline
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from audio_engine.pipeline import AudioPipeline
import numpy as np
import soundfile as sf


def create_test_stems(output_dir='./test_stems', duration=10.0, sample_rate=48000):
    """
    Create simple test stems for validation
    
    Args:
        output_dir: Directory to save test stems
        duration: Duration in seconds
        sample_rate: Sample rate
    """
    os.makedirs(output_dir, exist_ok=True)
    
    num_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, num_samples)
    
    # Create test stems with different frequencies
    stems = {
        'kick': np.sin(2 * np.pi * 60 * t) * 0.8,  # 60 Hz
        'bass': np.sin(2 * np.pi * 100 * t) * 0.6,  # 100 Hz
        'synth': np.sin(2 * np.pi * 440 * t) * 0.5,  # 440 Hz (A4)
        'vocal': np.sin(2 * np.pi * 880 * t) * 0.4,  # 880 Hz (A5)
    }
    
    stem_files = []
    for name, audio in stems.items():
        file_path = os.path.join(output_dir, f'{name}.wav')
        sf.write(file_path, audio, sample_rate, subtype='PCM_24')
        stem_files.append(file_path)
        print(f"✓ Created test stem: {file_path}")
    
    return stem_files


def test_audio_pipeline():
    """Test the complete audio pipeline"""
    
    print("="*60)
    print("MIXMASTER PRO - AUDIO ENGINE TEST")
    print("="*60)
    
    # Create test stems
    print("\n[1/3] Creating test stems...")
    stem_files = create_test_stems()
    
    # Initialize pipeline
    print("\n[2/3] Initializing AudioPipeline...")
    pipeline = AudioPipeline(sample_rate=48000)
    
    # Process
    print("\n[3/3] Processing audio...")
    print("-"*60)
    
    try:
        report = pipeline.process(
            stem_files=stem_files,
            output_mix_path='./test_output/mix.wav',
            output_master_path='./test_output/master.wav',
            target_lufs=-14.0,
            ceiling_dbTP=-1.0,
            max_width_percent=140,
            preset='balanced'
        )
        
        print("\n" + "="*60)
        print("✓ TEST PASSED!")
        print("="*60)
        
        print("\nResults:")
        print(f"  Processing time: {report['processing_time']['total_seconds']:.1f}s")
        print(f"  Final LUFS: {report['final_quality']['lufs']:.1f}")
        print(f"  True Peak: {report['final_quality']['true_peak_dbTP']:.1f} dBTP")
        print(f"  Mono compatible: {report['final_quality']['mono_compatible']}")
        print(f"  QC passed: {report['final_quality']['all_qc_passed']}")
        
        print("\nOutput files:")
        print(f"  Mix: {report['output']['mix_file']}")
        print(f"  Master: {report['output']['master_file']}")
        
        if report['warnings']:
            print("\nWarnings:")
            for warning in report['warnings']:
                print(f"  ⚠ {warning}")
        
        return True
        
    except Exception as e:
        print("\n" + "="*60)
        print("✗ TEST FAILED!")
        print("="*60)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_audio_pipeline()
    sys.exit(0 if success else 1)
