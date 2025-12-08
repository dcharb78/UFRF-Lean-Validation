#!/usr/bin/env python3
"""
Unified Signature Score

Combines multiple metrics into a single score for:
"Does a given operator belong to the UFRF class?"

Metrics:
1. Global correlation
2. Spacing statistics (GUE vs GOE)
3. Harmonic invariants (fifths/fourths)
4. Symmetry-breaking (multi-scale resonance)
5. Spectral stability (across scales)
6. Manifold agreement alignment (89, 233)

Author: Daniel Charboneau
Date: December 2025
"""

import numpy as np
from spectral_computation import *
from spectral_zeta import find_spectral_zeros
from robustness_test import compute_many_zeros
from spectral_analysis import load_zeta_zeros
from symmetry_breaking_tests import *
from enhanced_signature_tests import test_gue_spacing, test_pair_correlation, spectral_rigidity
from real_5scale_test import run_real_5scale_test
from fractal_self_similarity import test_fractal_self_similarity
from typing import Dict

def compute_unified_signature_score(basis: List, H: np.ndarray, 
                                   eigenvals: np.ndarray, eigenvecs: np.ndarray,
                                   riemann_zeros: np.ndarray = None) -> Dict:
    """
    Compute unified signature score for UFRF operator.
    
    Returns score from 0-1 where:
    - 1.0 = Perfect UFRF signature
    - 0.0 = No UFRF signature
    """
    
    scores = {}
    weights = {}
    
    # 1. Global Correlation (0-1)
    print("1. Computing global correlation...")
    if riemann_zeros is not None and len(riemann_zeros) > 0:
        zeros = compute_many_zeros(eigenvals, imag_range=(0, 100), resolution=2000)
        if len(zeros) > 0:
            from robustness_test import compare_zeros_detailed
            comparison = compare_zeros_detailed(zeros, riemann_zeros)
            corr = comparison.get('correlation', 0)
            # Normalize: 0.99+ = 1.0, 0.95 = 0.5, 0.90 = 0.0
            global_score = max(0, min(1, (corr - 0.90) / 0.09))
            scores["global_correlation"] = global_score
            weights["global_correlation"] = 0.15  # Lower weight (rotation-invariant)
            print(f"   Correlation: {corr:.6f} → Score: {global_score:.4f}")
    else:
        scores["global_correlation"] = 0.0
        weights["global_correlation"] = 0.15
    
    # 2. Spacing Statistics (GUE vs GOE) (0-1)
    print("2. Computing spacing statistics...")
    spacing_result = test_gue_spacing(eigenvals)
    if "error" not in spacing_result:
        is_gue = spacing_result.get('is_gue_like', False)
        alpha = spacing_result.get('alpha_estimate', 0)
        # Score: GUE-like = 1.0, alpha close to 2 = bonus
        spacing_score = 1.0 if is_gue else 0.0
        if alpha > 1.5:  # Closer to GUE (α=2)
            spacing_score = min(1.0, spacing_score + 0.2)
        scores["spacing_statistics"] = spacing_score
        weights["spacing_statistics"] = 0.20
        print(f"   Is GUE-like: {is_gue}, Alpha: {alpha:.2f} → Score: {spacing_score:.4f}")
    else:
        scores["spacing_statistics"] = 0.0
        weights["spacing_statistics"] = 0.20
    
    # 3. Harmonic Invariants (0-1)
    print("3. Computing harmonic invariants...")
    invariants_result = fifths_fourths_walk_invariants(basis, eigenvecs, eigenvals)
    mean_pairs = invariants_result.get('mean_fifths_pairs', 0) + invariants_result.get('mean_fourths_pairs', 0)
    # Score: >7 pairs = 1.0, 5-7 = 0.7, 3-5 = 0.4, <3 = 0.0
    if mean_pairs > 7:
        harmonic_score = 1.0
    elif mean_pairs > 5:
        harmonic_score = 0.7
    elif mean_pairs > 3:
        harmonic_score = 0.4
    else:
        harmonic_score = 0.0
    scores["harmonic_invariants"] = harmonic_score
    weights["harmonic_invariants"] = 0.15
    print(f"   Mean pairs: {mean_pairs:.2f} → Score: {harmonic_score:.4f}")
    
    # 4. Multi-Scale Resonance (0-1)
    print("4. Computing multi-scale resonance...")
    resonance_result = multi_scale_resonance_test(basis)
    has_resonance = resonance_result.get('has_resonance', False)
    jump89 = resonance_result.get('expected_jump_89', 0)
    jump233 = resonance_result.get('expected_jump_233', 0)
    # Score: Both jumps >0.3 = 1.0, one jump >0.2 = 0.6, no jumps = 0.0
    if jump89 > 0.3 and jump233 > 0.3:
        resonance_score = 1.0
    elif jump89 > 0.2 or jump233 > 0.2:
        resonance_score = 0.6
    else:
        resonance_score = 0.0
    scores["multi_scale_resonance"] = resonance_score
    weights["multi_scale_resonance"] = 0.20
    print(f"   Jump 89: {jump89:.4f}, Jump 233: {jump233:.4f} → Score: {resonance_score:.4f}")
    
    # 5. Pair Correlation (Montgomery-Dyson) (0-1)
    print("5. Computing pair correlation...")
    if riemann_zeros is not None and len(riemann_zeros) > 0:
        pair_result = test_pair_correlation(eigenvals, riemann_zeros)
        if "error" not in pair_result:
            emp_riemann_corr = pair_result.get('empirical_riemann_correlation', 0)
            # Score: >0.8 = 1.0, 0.6-0.8 = 0.7, 0.4-0.6 = 0.4, <0.4 = 0.0
            if emp_riemann_corr > 0.8:
                pair_score = 1.0
            elif emp_riemann_corr > 0.6:
                pair_score = 0.7
            elif emp_riemann_corr > 0.4:
                pair_score = 0.4
            else:
                pair_score = 0.0
            scores["pair_correlation"] = pair_score
            weights["pair_correlation"] = 0.20
            print(f"   Empirical-Riemann correlation: {emp_riemann_corr:.4f} → Score: {pair_score:.4f}")
        else:
            scores["pair_correlation"] = 0.0
            weights["pair_correlation"] = 0.20
    else:
        scores["pair_correlation"] = 0.0
        weights["pair_correlation"] = 0.20
    
    # 6. Spectral Rigidity (0-1)
    print("6. Computing spectral rigidity...")
    rigidity_result = spectral_rigidity(eigenvals)
    if "error" not in rigidity_result:
        is_gue = rigidity_result.get('is_gue_like', False)
        slope = rigidity_result.get('slope', 0)
        # Score: GUE-like with slope ≈0.101 = 1.0
        if is_gue and abs(slope - 0.101) < 0.05:
            rigidity_score = 1.0
        elif is_gue:
            rigidity_score = 0.7
        else:
            rigidity_score = 0.0
        scores["spectral_rigidity"] = rigidity_score
        weights["spectral_rigidity"] = 0.10
        print(f"   Is GUE-like: {is_gue}, Slope: {slope:.4f} → Score: {rigidity_score:.4f}")
    else:
        scores["spectral_rigidity"] = 0.0
        weights["spectral_rigidity"] = 0.10
    
    # 7. Fractal Self-Similarity (0-1)
    print("7. Computing fractal self-similarity...")
    # Adjust weights to make room for new component
    # Reduce other weights slightly
    for key in weights:
        weights[key] = weights[key] * 0.93  # Make room for 0.15 weight
    
    fractal_result = test_fractal_self_similarity(max_level=min(3, max(b.node.level for b in basis)))
    fractal_score = fractal_result.get("overall_score", 0.0)
    scores["fractal_self_similarity"] = fractal_score
    weights["fractal_self_similarity"] = 0.15
    print(f"   Overall fractal score: {fractal_score:.4f} → Score: {fractal_score:.4f}")
    
    # Compute weighted total
    total_score = sum(scores[key] * weights[key] for key in scores.keys())
    total_weight = sum(weights.values())
    normalized_score = total_score / total_weight if total_weight > 0 else 0.0
    
    return {
        "scores": scores,
        "weights": weights,
        "total_score": normalized_score,
        "components": {
            "global_correlation": scores.get("global_correlation", 0),
            "spacing_statistics": scores.get("spacing_statistics", 0),
            "harmonic_invariants": scores.get("harmonic_invariants", 0),
            "multi_scale_resonance": scores.get("multi_scale_resonance", 0),
            "pair_correlation": scores.get("pair_correlation", 0),
            "spectral_rigidity": scores.get("spectral_rigidity", 0),
            "fractal_self_similarity": scores.get("fractal_self_similarity", 0),
        }
    }

def main():
    """Compute unified signature score for UFRF operator"""
    print("=" * 60)
    print("UNIFIED SIGNATURE SCORE")
    print("=" * 60)
    
    # Build UFRF operator
    basis = enumerate_basis(max_level=1)
    H = build_matrix(basis)
    eigenvals, eigenvecs = compute_spectrum(H)
    
    # Load Riemann zeros
    riemann_zeros = load_zeta_zeros(n_zeros=200)
    
    # Compute score
    result = compute_unified_signature_score(basis, H, eigenvals, eigenvecs, riemann_zeros)
    
    # Display results
    print("\n" + "=" * 60)
    print("UNIFIED SIGNATURE SCORE RESULTS")
    print("=" * 60)
    
    print("\nComponent Scores:")
    for component, score in result["components"].items():
        weight = result["weights"].get(component, 0)
        print(f"  {component:25s}: {score:.4f} (weight: {weight:.2f})")
    
    print(f"\n{'='*60}")
    print(f"TOTAL SIGNATURE SCORE: {result['total_score']:.4f} / 1.0")
    print(f"{'='*60}")
    
    if result['total_score'] >= 0.8:
        print("STRONG UFRF SIGNATURE: Operator belongs to UFRF class")
    elif result['total_score'] >= 0.6:
        print("MODERATE UFRF SIGNATURE: Some UFRF characteristics")
    elif result['total_score'] >= 0.4:
        print("WEAK UFRF SIGNATURE: Few UFRF characteristics")
    else:
        print("NO UFRF SIGNATURE: Operator does not belong to UFRF class")
    
    return result

if __name__ == "__main__":
    main()

