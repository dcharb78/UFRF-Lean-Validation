#!/usr/bin/env python3
"""
Training-Spectral Alignment Test

Compares training network behavior with spectral operator behavior to validate
cross-domain alignment. This tests if the same structure "lights up" in both:
- Static operator (H_full eigenvectors)
- Dynamic network (training epochs, coherence patterns)

Author: Daniel Charboneau
Date: December 2025
"""

import numpy as np
from spectral_computation import *
from robustness_test import compute_many_zeros
from spectral_analysis import load_zeta_zeros
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class TrainingPattern:
    """Represents a training network pattern"""
    epoch: int
    position: int
    phase: str
    coherence: float
    activity: float  # Network activity/activation at this position

def simulate_training_patterns(positions: List[int], epochs: List[int]) -> List[TrainingPattern]:
    """
    Simulate training network patterns.
    
    In a real implementation, this would load actual training data.
    For now, we simulate patterns that should align with spectral structure:
    - Higher activity at UFRF-prime positions
    - Coherence spikes at nested manifold points (89, 233)
    - Phase-dependent patterns
    """
    patterns = []
    
    for epoch in epochs:
        for pos in positions:
            phase = phase_of(pos)
            
            # Simulate coherence (higher at special positions)
            coherence = 0.5 + 0.3 * np.random.random()
            if pos == 89 % 13 or pos == 233 % 13:
                coherence += 0.2  # Nested manifold resonance
            if is_uprime(SysNode(level=0, pos=pos)):
                coherence += 0.15  # UFRF-prime enhancement
            
            # Simulate activity (higher at active phases)
            activity = 0.3 + 0.4 * np.random.random()
            if phase == "rest":
                activity += 0.2
            if phase == "harmonize":
                activity += 0.15
            
            patterns.append(TrainingPattern(
                epoch=epoch,
                position=pos,
                phase=phase,
                coherence=coherence,
                activity=activity
            ))
    
    return patterns

def analyze_spectral_eigenvectors(basis: List, eigenvecs: np.ndarray, 
                                  eigenvals: np.ndarray, 
                                  riemann_zeros: List[complex]) -> Dict:
    """
    Analyze which positions/levels contribute most to eigenvectors
    associated with ζ-like zeros.
    """
    # Find eigenvectors corresponding to ζ-like zeros
    # For each zero, find closest eigenvalue
    zero_contributions = {}
    
    for zero in riemann_zeros[:20]:  # Analyze first 20 zeros
        # Find eigenvector with eigenvalue closest to zero
        target_imag = zero.imag
        closest_idx = np.argmin(np.abs(eigenvals - target_imag))
        
        eigenvec = eigenvecs[:, closest_idx]
        
        # Find positions with largest contributions
        contributions_by_pos = {}
        contributions_by_level = {}
        contributions_by_phase = {}
        
        for i, b in enumerate(basis):
            weight = abs(eigenvec[i])
            
            # By position
            pos = b.node.pos
            contributions_by_pos[pos] = contributions_by_pos.get(pos, 0) + weight
            
            # By level
            level = b.node.level
            contributions_by_level[level] = contributions_by_level.get(level, 0) + weight
            
            # By phase
            phase = phase_of(b.node.pos)
            contributions_by_phase[phase] = contributions_by_phase.get(phase, 0) + weight
        
        zero_contributions[target_imag] = {
            "by_position": contributions_by_pos,
            "by_level": contributions_by_level,
            "by_phase": contributions_by_phase,
            "top_positions": sorted(contributions_by_pos.items(), 
                                   key=lambda x: x[1], reverse=True)[:5],
        }
    
    return zero_contributions

def compare_training_spectral(training_patterns: List[TrainingPattern],
                              spectral_contributions: Dict) -> Dict:
    """
    Compare training network patterns with spectral operator contributions.
    
    Returns alignment metrics:
    - Position alignment: Do same positions light up?
    - Phase alignment: Do same phases show activity?
    - Nested manifold alignment: Do 89/233 show resonance in both?
    - UPrime alignment: Do UFRF-primes show activity in both?
    """
    # Aggregate training patterns by position
    training_by_pos = {}
    training_by_phase = {}
    
    for pattern in training_patterns:
        pos = pattern.position
        phase = pattern.phase
        
        if pos not in training_by_pos:
            training_by_pos[pos] = []
        training_by_pos[pos].append(pattern.activity)
        
        if phase not in training_by_phase:
            training_by_phase[phase] = []
        training_by_phase[phase].append(pattern.coherence)
    
    # Average training activity by position
    training_activity = {pos: np.mean(activities) 
                        for pos, activities in training_by_pos.items()}
    
    # Average training coherence by phase
    training_coherence = {phase: np.mean(coherences)
                         for phase, coherences in training_by_phase.items()}
    
    # Aggregate spectral contributions
    spectral_by_pos = {}
    spectral_by_phase = {}
    
    for zero_data in spectral_contributions.values():
        for pos, weight in zero_data["by_position"].items():
            spectral_by_pos[pos] = spectral_by_pos.get(pos, 0) + weight
        
        for phase, weight in zero_data["by_phase"].items():
            spectral_by_phase[phase] = spectral_by_phase.get(phase, 0) + weight
    
    # Normalize spectral contributions
    max_spectral_pos = max(spectral_by_pos.values()) if spectral_by_pos else 1.0
    max_spectral_phase = max(spectral_by_phase.values()) if spectral_by_phase else 1.0
    
    spectral_by_pos_norm = {pos: w / max_spectral_pos 
                            for pos, w in spectral_by_pos.items()}
    spectral_by_phase_norm = {phase: w / max_spectral_phase
                              for phase, w in spectral_by_phase.items()}
    
    # Normalize training activity
    max_training_pos = max(training_activity.values()) if training_activity else 1.0
    training_activity_norm = {pos: a / max_training_pos 
                             for pos, a in training_activity.items()}
    
    # Compute alignment metrics
    # 1. Position alignment (correlation)
    common_positions = set(training_activity_norm.keys()) & set(spectral_by_pos_norm.keys())
    if len(common_positions) > 1:
        training_vals = [training_activity_norm[p] for p in common_positions]
        spectral_vals = [spectral_by_pos_norm[p] for p in common_positions]
        position_correlation = np.corrcoef(training_vals, spectral_vals)[0, 1]
    else:
        position_correlation = 0.0
    
    # 2. Phase alignment
    common_phases = set(training_coherence.keys()) & set(spectral_by_phase_norm.keys())
    if len(common_phases) > 1:
        training_phase_vals = [training_coherence[p] for p in common_phases]
        spectral_phase_vals = [spectral_by_phase_norm[p] for p in common_phases]
        phase_correlation = np.corrcoef(training_phase_vals, spectral_phase_vals)[0, 1]
    else:
        phase_correlation = 0.0
    
    # 3. Nested manifold alignment (89, 233)
    pos89 = 89 % 13
    pos233 = 233 % 13
    
    manifold_alignment = 0.0
    if pos89 in training_activity_norm and pos89 in spectral_by_pos_norm:
        # Both should show high activity
        training_89 = training_activity_norm[pos89]
        spectral_89 = spectral_by_pos_norm[pos89]
        manifold_alignment += (training_89 + spectral_89) / 2
    
    if pos233 in training_activity_norm and pos233 in spectral_by_pos_norm:
        training_233 = training_activity_norm[pos233]
        spectral_233 = spectral_by_pos_norm[pos233]
        manifold_alignment += (training_233 + spectral_233) / 2
    
    manifold_alignment = manifold_alignment / 2.0  # Average
    
    # 4. UPrime alignment
    uprime_positions = [pos for pos in range(13) 
                      if is_uprime(SysNode(level=0, pos=pos))]
    
    uprime_alignment = 0.0
    uprime_count = 0
    
    for pos in uprime_positions:
        if pos in training_activity_norm and pos in spectral_by_pos_norm:
            training_uprime = training_activity_norm[pos]
            spectral_uprime = spectral_by_pos_norm[pos]
            uprime_alignment += (training_uprime + spectral_uprime) / 2
            uprime_count += 1
    
    if uprime_count > 0:
        uprime_alignment = uprime_alignment / uprime_count
    
    return {
        "position_correlation": position_correlation if not np.isnan(position_correlation) else 0.0,
        "phase_correlation": phase_correlation if not np.isnan(phase_correlation) else 0.0,
        "manifold_alignment": manifold_alignment,
        "uprime_alignment": uprime_alignment,
        "training_activity": training_activity_norm,
        "spectral_contributions": spectral_by_pos_norm,
    }

def test_training_spectral_alignment():
    """Run training-spectral alignment test"""
    print("=" * 60)
    print("TRAINING-SPECTRAL ALIGNMENT TEST")
    print("=" * 60)
    
    # Build spectral operator
    basis = enumerate_basis(max_level=1)
    H = build_matrix(basis)
    eigenvals, eigenvecs = compute_spectrum(H)
    
    # Find zeros
    riemann_zeros = load_zeta_zeros(n_zeros=50)
    zeros = compute_many_zeros(eigenvals, imag_range=(0, 50), resolution=1000)
    
    print(f"\nBasis size: {len(basis)}")
    print(f"Zeros found: {len(zeros)}")
    
    # Analyze spectral eigenvectors
    print("\nAnalyzing spectral eigenvectors...")
    spectral_contributions = analyze_spectral_eigenvectors(
        basis, eigenvecs, eigenvals, zeros
    )
    
    # Simulate training patterns
    print("\nSimulating training patterns...")
    positions = list(range(13))
    epochs = list(range(0, 100, 10))  # Sample epochs
    training_patterns = simulate_training_patterns(positions, epochs)
    
    print(f"Training patterns: {len(training_patterns)}")
    
    # Compare
    print("\nComparing training and spectral patterns...")
    alignment = compare_training_spectral(training_patterns, spectral_contributions)
    
    # Display results
    print("\n" + "=" * 60)
    print("ALIGNMENT RESULTS")
    print("=" * 60)
    
    print(f"\nPosition Correlation: {alignment['position_correlation']:.4f}")
    if alignment['position_correlation'] > 0.7:
        print("  ✓ Strong position alignment")
    elif alignment['position_correlation'] > 0.4:
        print("  ⚠ Moderate position alignment")
    else:
        print("  ✗ Weak position alignment")
    
    print(f"\nPhase Correlation: {alignment['phase_correlation']:.4f}")
    if alignment['phase_correlation'] > 0.7:
        print("  ✓ Strong phase alignment")
    elif alignment['phase_correlation'] > 0.4:
        print("  ⚠ Moderate phase alignment")
    else:
        print("  ✗ Weak phase alignment")
    
    print(f"\nManifold Alignment (89, 233): {alignment['manifold_alignment']:.4f}")
    if alignment['manifold_alignment'] > 0.6:
        print("  ✓ Strong nested manifold alignment")
    else:
        print("  ⚠ Weak nested manifold alignment")
    
    print(f"\nUPrime Alignment: {alignment['uprime_alignment']:.4f}")
    if alignment['uprime_alignment'] > 0.6:
        print("  ✓ Strong UPrime alignment")
    else:
        print("  ⚠ Weak UPrime alignment")
    
    # Overall alignment score
    overall_score = (
        0.3 * alignment['position_correlation'] +
        0.3 * alignment['phase_correlation'] +
        0.2 * alignment['manifold_alignment'] +
        0.2 * alignment['uprime_alignment']
    )
    
    print(f"\n{'='*60}")
    print(f"OVERALL ALIGNMENT SCORE: {overall_score:.4f}")
    print(f"{'='*60}")
    
    if overall_score > 0.7:
        print("STRONG: Training and spectral patterns align well")
    elif overall_score > 0.5:
        print("MODERATE: Some alignment between training and spectral")
    else:
        print("WEAK: Limited alignment - may need refinement")
    
    return alignment

def main():
    """Run training-spectral alignment test"""
    alignment = test_training_spectral_alignment()
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)
    print("\nKey Question:")
    print("  Do the same structures light up in both:")
    print("  - Static operator (H_full eigenvectors)?")
    print("  - Dynamic network (training epochs)?")

if __name__ == "__main__":
    main()

