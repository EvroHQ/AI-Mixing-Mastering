"""
Professional Audio Quality Test
Demonstrates the upgraded mastering engine
"""

import numpy as np
import soundfile as sf
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from audio_engine.masterer import MasteringEngine
from audio_engine.analyzer import LoudnessAnalyzer

def generate_test_signal(duration_sec: float = 10.0, sample_rate: int = 48000):
    """
    Generate a complex test signal with multiple frequencies
    
    Args:
        duration_sec: Duration in seconds
        sample_rate: Sample rate
        
    Returns:
        Stereo test signal
    """
    print("Generating test signal...")
    
    samples = int(duration_sec * sample_rate)
    t = np.linspace(0, duration_sec, samples)
    
    # Create rich harmonic content
    signal = np.zeros(samples)
    
    # Bass (60Hz fundamental + harmonics)
    signal += 0.3 * np.sin(2 * np.pi * 60 * t)
    signal += 0.15 * np.sin(2 * np.pi * 120 * t)
    signal += 0.08 * np.sin(2 * np.pi * 180 * t)
    
    # Mids (440Hz A note + harmonics)
    signal += 0.25 * np.sin(2 * np.pi * 440 * t)
    signal += 0.12 * np.sin(2 * np.pi * 880 * t)
    signal += 0.06 * np.sin(2 * np.pi * 1320 * t)
    
    # Highs (2kHz + harmonics)
    signal += 0.15 * np.sin(2 * np.pi * 2000 * t)
    signal += 0.08 * np.sin(2 * np.pi * 4000 * t)
    signal += 0.04 * np.sin(2 * np.pi * 8000 * t)
    
    # Add some noise for realism
    signal += 0.02 * np.random.randn(samples)
    
    # Create stereo with slight difference
    left = signal
    right = signal * 0.95 + 0.05 * np.random.randn(samples)
    
    stereo = np.stack([left, right])
    
    # Normalize to -18 LUFS (typical pre-master level)
    stereo = stereo * 0.15
    
    print(f"✓ Generated {duration_sec}s test signal")
    return stereo

def test_mastering_quality():
    """
    Test the professional mastering engine
    """
    print("=" * 70)
    print("PROFESSIONAL MASTERING ENGINE - QUALITY TEST")
    print("=" * 70)
    
    sample_rate = 48000
    
    # Generate test signal
    audio = generate_test_signal(duration_sec=10.0, sample_rate=sample_rate)
    
    # Initialize engines
    print("\nInitializing professional mastering engine...")
    mastering_engine = MasteringEngine(sample_rate)
    loudness_analyzer = LoudnessAnalyzer(sample_rate)
    
    # Analyze input
    print("\n" + "-" * 70)
    print("INPUT ANALYSIS")
    print("-" * 70)
    input_metrics = loudness_analyzer.analyze(audio)
    print(f"LUFS:        {input_metrics['lufs_integrated']:.1f}")
    print(f"True Peak:   {input_metrics['true_peak_dbTP']:.1f} dBTP")
    print(f"LRA:         {input_metrics['lra']:.1f} LU")
    print(f"Crest Factor: {input_metrics['crest_factor']:.1f}")
    
    # Test different presets
    presets = ['balanced', 'dynamic', 'loud']
    
    for preset in presets:
        print("\n" + "=" * 70)
        print(f"TESTING PRESET: {preset.upper()}")
        print("=" * 70)
        
        # Master audio
        result = mastering_engine.master(
            audio=audio.copy(),
            target_lufs=-14.0,
            ceiling_dbTP=-0.3,
            max_width_percent=140,
            preset=preset
        )
        
        # Display results
        print("\n" + "-" * 70)
        print("PROCESSING CHAIN")
        print("-" * 70)
        for step in result['report']['processing_chain']:
            print(f"  • {step}")
        
        print("\n" + "-" * 70)
        print("OUTPUT METRICS")
        print("-" * 70)
        final = result['report']['final_metrics']
        print(f"LUFS:         {final['lufs']:.1f} (target: {final['lufs_target']:.1f}, Δ{final['lufs_delta']:.1f})")
        print(f"True Peak:    {final['true_peak_dbTP']:.1f} dBTP")
        print(f"LRA:          {final['lra']:.1f} LU")
        print(f"Crest Factor: {final['crest_factor']:.1f}")
        print(f"Dynamic Range: {final['dynamic_range_db']:.1f} dB")
        
        print("\n" + "-" * 70)
        print("QUALITY CHECKS")
        print("-" * 70)
        mono = result['report']['mono_compatibility']
        print(f"Mono Compatible: {mono['mono_compatible']}")
        print(f"Correlation:     {mono.get('correlation', 1.0):.3f}")
        
        qc = result['report']['qc_results']
        print(f"QC Iterations:   {qc['iterations']}")
        print(f"All Safe:        {qc['final_checks'].get('all_safe', False)}")
        
        if result['report']['warnings']:
            print("\n" + "-" * 70)
            print("WARNINGS")
            print("-" * 70)
            for warning in result['report']['warnings']:
                print(f"  ⚠ {warning}")
        
        # Save output
        output_dir = Path(__file__).parent / "test_outputs"
        output_dir.mkdir(exist_ok=True)
        
        output_path = output_dir / f"mastered_{preset}.wav"
        
        # Transpose for soundfile (samples first)
        output_audio = result['audio'].T
        
        sf.write(
            output_path,
            output_audio,
            sample_rate,
            subtype='PCM_24'
        )
        
        print(f"\n✓ Saved: {output_path}")
    
    # Save input for comparison
    input_path = output_dir / "input.wav"
    sf.write(
        input_path,
        audio.T,
        sample_rate,
        subtype='PCM_24'
    )
    print(f"\n✓ Saved input: {input_path}")
    
    print("\n" + "=" * 70)
    print("QUALITY TEST COMPLETE!")
    print("=" * 70)
    print(f"\nTest files saved to: {output_dir}")
    print("\nCompare the files to hear the difference:")
    print("  • input.wav - Original signal")
    print("  • mastered_balanced.wav - Balanced preset")
    print("  • mastered_dynamic.wav - Dynamic preset")
    print("  • mastered_loud.wav - Loud preset")
    print("\n" + "=" * 70)

if __name__ == "__main__":
    try:
        test_mastering_quality()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
