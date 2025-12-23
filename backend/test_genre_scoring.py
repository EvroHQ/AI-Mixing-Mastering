"""Quick test for genre detection"""
import sys
sys.path.insert(0, '.')

from audio_engine.analyzer.genre_detector import GenreDetector
import numpy as np

# Create detector
detector = GenreDetector(sample_rate=48000)

# Simulate what the detector MIGHT be seeing for stems
# These are the "problem" values that lead to Rock detection
problem_analysis = {
    'tempo': 123.0,  # Should be detected correctly
    'bass_ratio': 0.18,  # Lower bass
    'sub_bass_ratio': 0.03,  # Low sub (problem! Rock condition)
    'mid_ratio': 0.52,  # HIGH MIDS (problem! Rock condition)
    'high_ratio': 0.12,
    'brightness': 0.4,
    'presence_ratio': 0.08,
    'low_mid_ratio': 0.15,
    'crest_factor': 6.5,  # HIGH (problem! Rock condition)
    'dynamic_range_db': 16,  # HIGH (problem! Rock condition)
    'transient_density': 0.3,
    'four_on_floor_score': 0.2,  # Low (problem!)
}

print("=" * 60)
print("TESTING GENRE SCORING WITH PROBLEMATIC STEM ANALYSIS")
print("=" * 60)
print(f"\nTempo: {problem_analysis['tempo']} BPM")
print(f"Bass ratio: {problem_analysis['bass_ratio']}")
print(f"Mid ratio: {problem_analysis['mid_ratio']} << HIGH (Rock-like)")
print(f"Crest factor: {problem_analysis['crest_factor']} << HIGH (Rock-like)")
print(f"Dynamic range: {problem_analysis['dynamic_range_db']} dB << HIGH")
print(f"Sub-bass: {problem_analysis['sub_bass_ratio']} << LOW (Rock-like)")
print()

# Test the scoring
scores = detector._calculate_genre_scores(problem_analysis)

print("\n" + "=" * 60)
print("GENRE SCORES:")
print("=" * 60)
for genre, score in sorted(scores.items(), key=lambda x: -x[1]):
    bar = "█" * int(score * 40)
    print(f"  {genre:12}: {score:6.1%} {bar}")

print(f"\n🎯 Detected: {max(scores, key=scores.get).upper()}")
