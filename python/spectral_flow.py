#!/usr/bin/env python3
"""
Spectral Flow Across Scales

Run ζ_H(s) for SL0, SL1, SL2, SL3 and track:
- Zero locations
- Spacing distributions
- How structure sharpens or washes out

We want to see a monotonic trend toward zeta behavior.

Author: Daniel Charboneau
Date: December 2025
"""

import numpy as np
from spectral_computation import *
from spectral_zeta import spectral_zeta, find_spectral_zeros, compute_many_zeros
from spectral_analysis import load_zeta_zeros
from enhanced_signature_tests import test_gue_spacing, test_pair_correlation, spectral_rigidity
from typing import Dict, List

def analyze_spectral_flow():
    """Analyze spectral flow across system levels"""
    print("=" * 60)
    print("SPECTRAL FLOW ACROSS SCALES")
    print("=" * 60)
    
    riemann_zeros = load_zeta_zeros(n_zeros=200)
    
    results = {}
    
    for max_level in [0, 1, 2, 3]:
        print(f"\n{'='*60}")
        print(f"System Level: SL0 to SL{max_level}")
        print(f"{'='*60}")
        
        # Build basis and matrix
        basis = enumerate_basis(max_level=max_level)
        H = build_matrix(basis)
        eigenvals, eigenvecs = compute_spectrum(H)
        
        print(f"Basis size: {len(basis)}")
        print(f"Matrix size: {H.shape}")
        print(f"Positive eigenvalues: {np.sum(eigenvals > 0)}")
        
        # Find zeros
        print("Computing zeros...")
        zeros = compute_many_zeros(eigenvals, imag_range=(0, 100), resolution=2000)
        print(f"Zeros found: {len(zeros)}")
        
        if len(zeros) == 0:
            continue
        
        # Analyze zero locations
        zero_imags = [z.imag for z in zeros]
        print(f"Zero imaginary parts range: [{np.min(zero_imags):.2f}, {np.max(zero_imags):.2f}]")
        print(f"Mean zero location: {np.mean(zero_imags):.2f}")
        
        # Compare to Riemann zeros
        if len(riemann_zeros) > 0:
            from robustness_test import compare_zeros_detailed
            comparison = compare_zeros_detailed(zeros, riemann_zeros)
            print(f"Correlation with ζ zeros: {comparison.get('correlation', 0):.6f}")
            print(f"MAD: {comparison.get('mad', 0):.6f}")
        
        # GUE spacing test
        print("\nGUE Spacing Test:")
        spacing_result = test_gue_spacing(eigenvals)
        if "error" not in spacing_result:
            print(f"  Is GUE-like: {spacing_result.get('is_gue_like', False)}")
            print(f"  Spacing variance: {spacing_result.get('spacing_variance', 0):.4f}")
            print(f"  Alpha estimate: {spacing_result.get('alpha_estimate', 0):.4f} (GUE≈2, GOE≈1)")
        
        # Pair correlation
        print("\nPair Correlation Test:")
        pair_result = test_pair_correlation(eigenvals, riemann_zeros)
        if "error" not in pair_result:
            if pair_result.get('empirical_riemann_correlation') is not None:
                print(f"  Empirical vs Riemann: {pair_result.get('empirical_riemann_correlation', 0):.4f}")
        
        # Spectral rigidity
        print("\nSpectral Rigidity:")
        rigidity_result = spectral_rigidity(eigenvals)
        if "error" not in rigidity_result:
            print(f"  Is GUE-like: {rigidity_result.get('is_gue_like', False)}")
            print(f"  Slope: {rigidity_result.get('slope', 0):.4f} (GUE≈0.101)")
        
        # Store results
        results[max_level] = {
            "basis_size": len(basis),
            "zeros_count": len(zeros),
            "zero_imags": zero_imags,
            "comparison": comparison if len(riemann_zeros) > 0 else {},
            "spacing": spacing_result,
            "pair_correlation": pair_result,
            "rigidity": rigidity_result,
        }
    
    # Analyze trends
    print("\n" + "=" * 60)
    print("SPECTRAL FLOW TRENDS")
    print("=" * 60)
    
    if len(results) > 1:
        print("\nCorrelation Trend:")
        for level in sorted(results.keys()):
            corr = results[level].get("comparison", {}).get("correlation", 0)
            print(f"  SL{level}: {corr:.6f}")
        
        # Check if monotonic improvement
        correlations = [results[l].get("comparison", {}).get("correlation", 0) 
                       for l in sorted(results.keys())]
        if len(correlations) > 1:
            is_monotonic = all(correlations[i] <= correlations[i+1] 
                             for i in range(len(correlations)-1))
            if is_monotonic:
                print("  ✓ Monotonic improvement toward zeta behavior")
            else:
                print("  ⚠ Not monotonic - may need refinement")
        
        print("\nGUE Spacing Trend:")
        for level in sorted(results.keys()):
            is_gue = results[level].get("spacing", {}).get("is_gue_like", False)
            print(f"  SL{level}: {'GUE-like' if is_gue else 'GOE-like'}")
        
        print("\nSpectral Rigidity Trend:")
        for level in sorted(results.keys()):
            is_gue = results[level].get("rigidity", {}).get("is_gue_like", False)
            slope = results[level].get("rigidity", {}).get("slope", 0)
            print(f"  SL{level}: {'GUE-like' if is_gue else 'GOE-like'} (slope={slope:.4f})")
    
    return results

def main():
    """Run spectral flow analysis"""
    results = analyze_spectral_flow()
    
    print("\n" + "=" * 60)
    print("Spectral Flow Analysis Complete")
    print("=" * 60)
    print("\nKey Question:")
    print("  Does structure sharpen (more zeta-like) or wash out")
    print("  as we increase system levels?")

if __name__ == "__main__":
    main()

