#!/usr/bin/env python3
"""
Robustness Tests for UFRF Spectral Operator

Tests whether the 99.5% correlation with ζ zeros is robust or a fluke.

Author: Daniel Charboneau
Date: December 2025
"""

import numpy as np
from spectral_computation import *
from spectral_zeta import spectral_zeta, find_spectral_zeros
from spectral_analysis import load_zeta_zeros
from typing import List, Tuple, Dict
import scipy.linalg

def compute_many_zeros(H_eigenvals: np.ndarray, 
                       real_part: float = 0.5,
                       imag_range: tuple = (0, 200),
                       resolution: int = 5000) -> List[complex]:
    """Find many zeros of ζ_H(s) on critical line with high resolution"""
    zeros = []
    t_values = np.linspace(imag_range[0], imag_range[1], resolution)
    
    prev_sign_real = None
    prev_sign_imag = None
    
    for i, t in enumerate(t_values):
        s = real_part + 1j * t
        zeta_val = spectral_zeta(H_eigenvals, s)
        
        # Check both real and imaginary parts for sign changes
        current_sign_real = np.sign(zeta_val.real) if abs(zeta_val.real) > 1e-10 else 0
        current_sign_imag = np.sign(zeta_val.imag) if abs(zeta_val.imag) > 1e-10 else 0
        
        # Zero crossing detected
        if prev_sign_real is not None:
            if (prev_sign_real != 0 and current_sign_real != 0 and 
                prev_sign_real != current_sign_real):
                # Refine zero
                zero_approx = refine_zero_simple(H_eigenvals, 
                                                 real_part + 1j * t_values[i-1],
                                                 real_part + 1j * t,
                                                 real_part)
                zeros.append(zero_approx)
            elif (prev_sign_imag != 0 and current_sign_imag != 0 and
                  prev_sign_imag != current_sign_imag):
                # Also check imaginary part
                zero_approx = refine_zero_simple(H_eigenvals,
                                                 real_part + 1j * t_values[i-1],
                                                 real_part + 1j * t,
                                                 real_part)
                zeros.append(zero_approx)
        
        prev_sign_real = current_sign_real
        prev_sign_imag = current_sign_imag
    
    return zeros

def refine_zero_simple(H_eigenvals: np.ndarray, s0: complex, s1: complex,
                      real_part: float, max_iter: int = 20) -> complex:
    """Simple zero refinement using bisection"""
    s = (s0 + s1) / 2
    
    for _ in range(max_iter):
        zeta_val = spectral_zeta(H_eigenvals, s)
        if abs(zeta_val) < 1e-6:
            break
        
        # Bisection: check which side has zero
        zeta_s0 = spectral_zeta(H_eigenvals, s0)
        zeta_s = spectral_zeta(H_eigenvals, s)
        
        if abs(zeta_s0) < abs(zeta_s):
            s1 = s
        else:
            s0 = s
        
        s = (s0 + s1) / 2
        # Keep real part fixed
        s = real_part + 1j * s.imag
    
    return s

def compare_zeros_detailed(spectral_zeros: List[complex], 
                          riemann_zeros: np.ndarray) -> Dict:
    """Detailed comparison of spectral and Riemann zeros"""
    if len(spectral_zeros) == 0 or len(riemann_zeros) == 0:
        return {"error": "Insufficient zeros"}
    
    spectral_imags = np.array([z.imag for z in spectral_zeros])
    riemann_imags = riemann_zeros[:len(spectral_imags)]
    
    # Normalize for comparison
    spectral_mean = np.mean(spectral_imags)
    riemann_mean = np.mean(riemann_imags)
    
    normalized_spectral = spectral_imags / spectral_mean if spectral_mean > 0 else spectral_imags
    normalized_riemann = riemann_imags / riemann_mean if riemann_mean > 0 else riemann_imags
    
    # Correlation
    min_len = min(len(normalized_spectral), len(normalized_riemann))
    correlation = np.corrcoef(normalized_spectral[:min_len], 
                             normalized_riemann[:min_len])[0, 1]
    
    # Mean Absolute Deviation (MAD)
    mad = np.mean(np.abs(normalized_spectral[:min_len] - normalized_riemann[:min_len]))
    
    # Scaled differences
    scaled_diffs = np.abs(normalized_spectral[:min_len] - normalized_riemann[:min_len]) / normalized_riemann[:min_len]
    mean_scaled_diff = np.mean(scaled_diffs)
    max_scaled_diff = np.max(scaled_diffs)
    
    return {
        "count": min_len,
        "correlation": correlation,
        "mad": mad,
        "mean_scaled_diff": mean_scaled_diff,
        "max_scaled_diff": max_scaled_diff,
        "spectral_mean": spectral_mean,
        "riemann_mean": riemann_mean,
    }

def test_varying_basis_size():
    """Test how zeros evolve with different basis sizes"""
    print("Testing Varying Basis Sizes")
    print("=" * 60)
    
    results = {}
    
    for max_level in [0, 1, 2]:
        print(f"\nMax Level: {max_level} (SL0 to SL{max_level})")
        basis = enumerate_basis(max_level=max_level)
        H = build_matrix(basis)
        eigenvals, eigenvecs = compute_spectrum(H)
        
        print(f"  Basis size: {len(basis)}")
        print(f"  Matrix size: {H.shape}")
        print(f"  Positive eigenvalues: {np.sum(eigenvals > 0)}")
        
        # Find zeros
        zeros = compute_many_zeros(eigenvals, imag_range=(0, 100), resolution=2000)
        print(f"  Zeros found: {len(zeros)}")
        
        if len(zeros) > 0:
            results[max_level] = {
                "basis_size": len(basis),
                "zeros": zeros,
                "eigenvals": eigenvals
            }
    
    # Compare zero locations across levels
    if len(results) > 1:
        print("\nZero Location Evolution:")
        for level in sorted(results.keys()):
            zeros = results[level]["zeros"]
            if len(zeros) > 0:
                imags = [z.imag for z in zeros[:10]]  # First 10
                print(f"  Level {level}: {[f'{im:.2f}' for im in imags]}")
    
    return results

def analyze_eigenvector_contributions(basis: List, eigenvecs: np.ndarray, 
                                     eigenvals: np.ndarray, 
                                     zero_index: int) -> Dict:
    """Analyze which phases/SysNodes contribute most to eigenvector"""
    # Find eigenvector corresponding to zero
    # (This is simplified - actual mapping requires more analysis)
    
    # Get eigenvector with largest component
    eigenvec = eigenvecs[:, zero_index]
    
    # Find top contributors
    top_indices = np.argsort(np.abs(eigenvec))[-10:][::-1]
    
    contributions = []
    for idx in top_indices:
        node = basis[idx]
        contribution = abs(eigenvec[idx])
        contributions.append({
            "node": node,
            "level": node.node.level,
            "pos": node.node.pos.val,
            "phase": phase_of(node.node.pos.val),
            "is_uprime": is_uprime(node.node),
            "contribution": contribution
        })
    
    return {
        "top_contributors": contributions,
        "uprime_count": sum(1 for c in contributions if c["is_uprime"]),
        "level_distribution": {}
    }

def test_geometry_ablation():
    """Test H_full variants with broken geometry"""
    print("\nGeometry Ablation Tests")
    print("=" * 60)
    
    results = {}
    
    # Original H_full
    print("\n1. Original H_full (baseline):")
    basis = enumerate_basis(max_level=1)
    H_original = build_matrix(basis)
    eigenvals_orig, _ = compute_spectrum(H_original)
    zeros_orig = compute_many_zeros(eigenvals_orig, imag_range=(0, 50), resolution=1000)
    
    if len(zeros_orig) > 0:
        riemann_zeros = load_zeta_zeros(n_zeros=min(100, len(zeros_orig)))
        comparison_orig = compare_zeros_detailed(zeros_orig, riemann_zeros)
        print(f"  Correlation: {comparison_orig.get('correlation', 0):.4f}")
        results["original"] = comparison_orig
    
    # TODO: Implement actual ablation variants
    # - Random permutation instead of rotate
    # - Different cycle length
    # - Collapsed trinity
    # - Single axis
    # - Flat recursion
    
    print("\nNote: Ablation variants need implementation")
    print("  - Random permutation")
    print("  - Different cycle length")
    print("  - Collapsed trinity")
    print("  - Single axis")
    print("  - Flat recursion")
    
    return results

def test_random_baselines():
    """Test random symmetric matrices as baseline"""
    print("\nRandom Baseline Tests")
    print("=" * 60)
    
    basis = enumerate_basis(max_level=1)
    n = len(basis)
    
    correlations = []
    
    for trial in range(10):
        # Generate random symmetric matrix
        A = np.random.randn(n, n)
        H_random = (A + A.T) / 2  # Symmetrize
        
        # Make diagonal positive
        np.fill_diagonal(H_random, np.abs(np.diagonal(H_random)) + 0.1)
        
        eigenvals_rand, _ = compute_spectrum(H_random)
        zeros_rand = compute_many_zeros(eigenvals_rand, imag_range=(0, 50), resolution=1000)
        
        if len(zeros_rand) > 0:
            riemann_zeros = load_zeta_zeros(n_zeros=min(100, len(zeros_rand)))
            comparison = compare_zeros_detailed(zeros_rand, riemann_zeros)
            corr = comparison.get('correlation', 0)
            correlations.append(corr)
            print(f"  Trial {trial+1}: correlation = {corr:.4f}")
    
    if len(correlations) > 0:
        print(f"\nRandom baseline statistics:")
        print(f"  Mean correlation: {np.mean(correlations):.4f}")
        print(f"  Std correlation: {np.std(correlations):.4f}")
        print(f"  Min correlation: {np.min(correlations):.4f}")
        print(f"  Max correlation: {np.max(correlations):.4f}")
    
    return correlations

def main():
    """Run all robustness tests"""
    print("UFRF Spectral Operator - Robustness Tests")
    print("=" * 60)
    
    # 1. Scale up comparison
    print("\n1. SCALED UP COMPARISON")
    print("-" * 60)
    basis = enumerate_basis(max_level=1)
    H = build_matrix(basis)
    eigenvals, eigenvecs = compute_spectrum(H)
    
    print(f"Computing many zeros (0-200 range)...")
    zeros = compute_many_zeros(eigenvals, imag_range=(0, 200), resolution=5000)
    print(f"Found {len(zeros)} zeros")
    
    if len(zeros) > 0:
        riemann_zeros = load_zeta_zeros(n_zeros=min(200, len(zeros)))
        comparison = compare_zeros_detailed(zeros, riemann_zeros)
        
        print(f"\nDetailed Comparison:")
        for key, value in comparison.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.6f}")
            else:
                print(f"  {key}: {value}")
    
    # 2. Varying basis size
    print("\n2. VARYING BASIS SIZE")
    print("-" * 60)
    varying_results = test_varying_basis_size()
    
    # 3. Geometry ablation
    print("\n3. GEOMETRY ABLATION")
    print("-" * 60)
    ablation_results = test_geometry_ablation()
    
    # 4. Random baselines
    print("\n4. RANDOM BASELINES")
    print("-" * 60)
    random_correlations = test_random_baselines()
    
    print("\n" + "=" * 60)
    print("Robustness Tests Complete")
    print("\nKey Questions:")
    print("  1. Does correlation hold at larger sample sizes?")
    print("  2. Do zeros converge or drift with basis size?")
    print("  3. Does breaking geometry reduce correlation?")
    print("  4. Are random matrices significantly worse?")

if __name__ == "__main__":
    main()

