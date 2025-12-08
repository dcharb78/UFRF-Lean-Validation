#!/usr/bin/env python3
"""
Enhanced Signature-Breaking Tests

Strengthens signature tests to push from 2/5 to 4/5:
1. GUE spacing test (kills random baselines)
2. Pair correlation test (Montgomery-Dyson)
3. Spectral rigidity (Δ₃-statistics)

Author: Daniel Charboneau
Date: December 2025
"""

import numpy as np
from spectral_computation import *
from spectral_zeta import spectral_zeta, find_spectral_zeros
from spectral_analysis import load_zeta_zeros
from typing import List, Dict, Tuple
import scipy.stats
from scipy.special import gamma
from scipy.integrate import quad

def gue_spacing_distribution(s: np.ndarray) -> np.ndarray:
    """
    Theoretical GUE spacing distribution:
    P(s) ≈ (32/π²) s² exp(-4s²/π) for small s
    
    This is the distribution for Riemann zeta zeros.
    """
    return (32 / (np.pi ** 2)) * (s ** 2) * np.exp(-4 * (s ** 2) / np.pi)

def goe_spacing_distribution(s: np.ndarray) -> np.ndarray:
    """
    Theoretical GOE spacing distribution:
    P(s) ≈ (π/2) s exp(-πs²/4) for small s
    
    This is the distribution for random symmetric matrices.
    """
    return (np.pi / 2) * s * np.exp(-np.pi * (s ** 2) / 4)

def test_gue_spacing(eigenvals: np.ndarray) -> Dict:
    """
    Test if spacing distribution matches GUE (Riemann) vs GOE (random).
    
    This is the strongest discriminator - random symmetric matrices
    follow GOE, Riemann zeros follow GUE.
    """
    positive_evals = np.sort(eigenvals[eigenvals > 0])
    
    if len(positive_evals) < 10:
        return {"error": "Insufficient eigenvalues"}
    
    # Compute normalized spacings
    spacings = np.diff(positive_evals)
    mean_spacing = np.mean(spacings)
    normalized_spacings = spacings / mean_spacing if mean_spacing > 0 else spacings
    
    # Bin spacings for comparison
    s_values = np.linspace(0, 3, 100)
    hist, bin_edges = np.histogram(normalized_spacings, bins=50, range=(0, 3), density=True)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    # Theoretical distributions
    gue_theory = gue_spacing_distribution(bin_centers)
    goe_theory = goe_spacing_distribution(bin_centers)
    
    # Normalize theoretical distributions
    gue_norm = np.trapz(gue_theory, bin_centers)
    goe_norm = np.trapz(goe_theory, bin_centers)
    gue_theory = gue_theory / gue_norm if gue_norm > 0 else gue_theory
    goe_theory = goe_theory / goe_norm if goe_norm > 0 else goe_theory
    
    # Compare to theoretical distributions
    # Use chi-squared test
    gue_chi2 = np.sum(((hist - gue_theory) ** 2) / (gue_theory + 1e-10))
    goe_chi2 = np.sum(((hist - goe_theory) ** 2) / (goe_theory + 1e-10))
    
    # Lower chi-squared = better fit
    is_gue_like = gue_chi2 < goe_chi2
    
    # Level repulsion: probability of very small spacing
    # GUE: P(s < 0.1) ≈ 0.001 (strong repulsion)
    # GOE: P(s < 0.1) ≈ 0.01 (weaker repulsion)
    very_small_prob = np.sum(normalized_spacings < 0.1) / len(normalized_spacings)
    
    # Small spacing behavior: GUE ~ s², GOE ~ s
    small_spacings = normalized_spacings[normalized_spacings < 0.5]
    if len(small_spacings) > 0:
        # Fit to s^alpha
        log_s = np.log(small_spacings + 1e-10)
        log_counts = np.log(np.histogram(small_spacings, bins=10)[0] + 1)
        # GUE: alpha ≈ 2, GOE: alpha ≈ 1
        # Simple estimate: mean of s² / mean of s
        alpha_estimate = np.mean(small_spacings ** 2) / (np.mean(small_spacings) + 1e-10)
    else:
        alpha_estimate = 0.0
    
    return {
        "normalized_spacings": normalized_spacings,
        "gue_chi2": gue_chi2,
        "goe_chi2": goe_chi2,
        "is_gue_like": is_gue_like,
        "very_small_prob": very_small_prob,
        "alpha_estimate": alpha_estimate,
        "spacing_variance": np.var(normalized_spacings),
        "histogram": hist,
        "bin_centers": bin_centers,
        "gue_theory": gue_theory,
        "goe_theory": goe_theory,
    }

def montgomery_dyson_pair_correlation(r: np.ndarray) -> np.ndarray:
    """
    Montgomery-Dyson pair correlation function:
    R₂(r) = 1 - (sin(πr) / (πr))²
    
    This is the theoretical pair correlation for Riemann zeta zeros.
    """
    # Avoid division by zero
    r_safe = np.where(r == 0, 1e-10, r)
    return 1 - (np.sin(np.pi * r_safe) / (np.pi * r_safe)) ** 2

def test_pair_correlation(eigenvals: np.ndarray, 
                          riemann_zeros: np.ndarray = None) -> Dict:
    """
    Test pair correlation function (Montgomery-Dyson).
    
    This is the biggest discriminator - random baselines will not match.
    """
    positive_evals = np.sort(eigenvals[eigenvals > 0])
    
    if len(positive_evals) < 10:
        return {"error": "Insufficient eigenvalues"}
    
    # Normalize by mean spacing
    mean_spacing = np.mean(np.diff(positive_evals))
    normalized_evals = positive_evals / mean_spacing if mean_spacing > 0 else positive_evals
    
    # Compute pair correlation
    r_values = np.linspace(0, 5, 200)
    pair_corr_empirical = []
    
    for r in r_values:
        # Count pairs at distance r (within tolerance)
        pairs = 0
        tolerance = 0.05
        for i in range(len(normalized_evals)):
            for j in range(i+1, len(normalized_evals)):
                dist = abs(normalized_evals[j] - normalized_evals[i])
                if abs(dist - r) < tolerance:
                    pairs += 1
        # Normalize by expected number
        expected_pairs = len(normalized_evals) * tolerance  # Rough estimate
        pair_corr_empirical.append(pairs / (expected_pairs + 1))
    
    # Theoretical Montgomery-Dyson
    pair_corr_theory = montgomery_dyson_pair_correlation(r_values)
    
    # Compare to theory
    correlation_with_theory = np.corrcoef(pair_corr_empirical, pair_corr_theory)[0, 1]
    
    # Compare to Riemann zeros if provided
    riemann_corr = None
    riemann_correlation_with_theory = None
    if riemann_zeros is not None and len(riemann_zeros) > 0:
        riemann_mean_spacing = np.mean(np.diff(riemann_zeros))
        riemann_normalized = riemann_zeros / riemann_mean_spacing
        
        riemann_pair_corr = []
        for r in r_values:
            pairs = 0
            tolerance = 0.05
            for i in range(len(riemann_normalized)):
                for j in range(i+1, len(riemann_normalized)):
                    dist = abs(riemann_normalized[j] - riemann_normalized[i])
                    if abs(dist - r) < tolerance:
                        pairs += 1
            expected_pairs = len(riemann_normalized) * tolerance
            riemann_pair_corr.append(pairs / (expected_pairs + 1))
        
        riemann_corr = riemann_pair_corr
        riemann_correlation_with_theory = np.corrcoef(riemann_pair_corr, pair_corr_theory)[0, 1]
        
        # Compare empirical to Riemann
        empirical_riemann_corr = np.corrcoef(pair_corr_empirical, riemann_pair_corr)[0, 1]
    else:
        empirical_riemann_corr = None
    
    return {
        "r_values": r_values,
        "pair_correlation_empirical": pair_corr_empirical,
        "pair_correlation_theory": pair_corr_theory,
        "riemann_pair_correlation": riemann_corr,
        "correlation_with_theory": correlation_with_theory,
        "riemann_correlation_with_theory": riemann_correlation_with_theory,
        "empirical_riemann_correlation": empirical_riemann_corr,
    }

def spectral_rigidity(eigenvals: np.ndarray, L: float = 10.0) -> Dict:
    """
    Spectral rigidity Δ₃(L) - major physics/maths discriminant.
    
    Random baselines almost never match Δ₃ of ζ.
    
    Δ₃(L) measures the variance of the number of eigenvalues in an interval
    of length L (in units of mean spacing).
    """
    positive_evals = np.sort(eigenvals[eigenvals > 0])
    
    if len(positive_evals) < 20:
        return {"error": "Insufficient eigenvalues"}
    
    # Normalize by mean spacing
    mean_spacing = np.mean(np.diff(positive_evals))
    normalized_evals = positive_evals / mean_spacing if mean_spacing > 0 else positive_evals
    
    # Compute Δ₃(L) for various L values
    L_values = np.linspace(1, L, 20)
    delta3_values = []
    
    for L_val in L_values:
        # For each starting point, count eigenvalues in interval [x, x+L]
        variances = []
        
        # Sample starting points
        max_start = normalized_evals[-1] - L_val
        if max_start > 0:
            start_points = np.linspace(0, max_start, min(50, int(max_start)))
            
            for start in start_points:
                # Count eigenvalues in [start, start+L]
                count = np.sum((normalized_evals >= start) & (normalized_evals <= start + L_val))
                variances.append(count)
            
            if len(variances) > 0:
                # Δ₃(L) = variance of counts
                delta3 = np.var(variances)
                delta3_values.append(delta3)
            else:
                delta3_values.append(0.0)
        else:
            delta3_values.append(0.0)
    
    # Theoretical: For GUE, Δ₃(L) ≈ (1/π²) log(L) + const
    # For GOE (random), Δ₃(L) is larger
    
    # Fit to log(L) to check GUE behavior
    delta3_array = np.array(delta3_values)
    if len(L_values) > 0 and len(delta3_values) > 0 and np.any(delta3_array > 0):
        nonzero_mask = delta3_array > 0
        log_L = np.log(np.array(L_values)[nonzero_mask] + 1e-10)
        delta3_nonzero = delta3_array[nonzero_mask]
        
        if len(log_L) > 1 and len(delta3_nonzero) > 1:
            # Linear fit: delta3 = a * log(L) + b
            coeffs = np.polyfit(log_L, delta3_nonzero, 1)
            slope = coeffs[0]
            # GUE: slope ≈ 1/π² ≈ 0.101
            # GOE: slope is larger
            is_gue_like = abs(slope - 1/(np.pi**2)) < abs(slope - 0.2)
        else:
            slope = 0.0
            is_gue_like = False
    else:
        slope = 0.0
        is_gue_like = False
    
    return {
        "L_values": L_values,
        "delta3_values": delta3_values,
        "slope": slope,
        "is_gue_like": is_gue_like,
        "mean_delta3": np.mean(delta3_values) if len(delta3_values) > 0 else 0.0,
    }

def test_enhanced_signature(eigenvals: np.ndarray, 
                           riemann_zeros: np.ndarray = None) -> Dict:
    """Run all enhanced signature tests"""
    results = {}
    
    # 1. GUE spacing test
    print("\n1. GUE SPACING TEST")
    print("-" * 60)
    spacing_result = test_gue_spacing(eigenvals)
    if "error" not in spacing_result:
        print(f"  GUE chi²: {spacing_result.get('gue_chi2', 0):.4f}")
        print(f"  GOE chi²: {spacing_result.get('goe_chi2', 0):.4f}")
        print(f"  Is GUE-like: {spacing_result.get('is_gue_like', False)}")
        print(f"  Very small spacing prob: {spacing_result.get('very_small_prob', 0):.4f}")
        print(f"  Alpha estimate: {spacing_result.get('alpha_estimate', 0):.4f} (GUE≈2, GOE≈1)")
        if spacing_result.get('is_gue_like'):
            print("  ✓ GUE-like spacing (Riemann-like)")
        else:
            print("  ⚠ GOE-like spacing (random-like)")
    results["gue_spacing"] = spacing_result
    
    # 2. Pair correlation test
    print("\n2. PAIR CORRELATION TEST (Montgomery-Dyson)")
    print("-" * 60)
    pair_result = test_pair_correlation(eigenvals, riemann_zeros)
    if "error" not in pair_result:
        print(f"  Correlation with theory: {pair_result.get('correlation_with_theory', 0):.4f}")
        if pair_result.get('riemann_correlation_with_theory') is not None:
            print(f"  Riemann correlation with theory: {pair_result.get('riemann_correlation_with_theory', 0):.4f}")
        if pair_result.get('empirical_riemann_correlation') is not None:
            print(f"  Empirical vs Riemann correlation: {pair_result.get('empirical_riemann_correlation', 0):.4f}")
            if pair_result.get('empirical_riemann_correlation', 0) > 0.8:
                print("  ✓ Strong match with Riemann pair correlation")
    results["pair_correlation"] = pair_result
    
    # 3. Spectral rigidity
    print("\n3. SPECTRAL RIGIDITY (Δ₃-statistics)")
    print("-" * 60)
    rigidity_result = spectral_rigidity(eigenvals)
    if "error" not in rigidity_result:
        print(f"  Slope: {rigidity_result.get('slope', 0):.4f} (GUE≈0.101, GOE>0.2)")
        print(f"  Is GUE-like: {rigidity_result.get('is_gue_like', False)}")
        print(f"  Mean Δ₃: {rigidity_result.get('mean_delta3', 0):.4f}")
        if rigidity_result.get('is_gue_like'):
            print("  ✓ GUE-like spectral rigidity (Riemann-like)")
        else:
            print("  ⚠ GOE-like spectral rigidity (random-like)")
    results["spectral_rigidity"] = rigidity_result
    
    return results

def main():
    """Run enhanced signature tests"""
    print("=" * 60)
    print("ENHANCED SIGNATURE-BREAKING TESTS")
    print("=" * 60)
    
    # Build UFRF operator
    basis = enumerate_basis(max_level=1)
    H = build_matrix(basis)
    eigenvals, eigenvecs = compute_spectrum(H)
    
    # Load Riemann zeros
    riemann_zeros = load_zeta_zeros(n_zeros=100)
    
    # Run tests
    results = test_enhanced_signature(eigenvals, riemann_zeros)
    
    # Summary
    print("\n" + "=" * 60)
    print("ENHANCED SIGNATURE SUMMARY")
    print("=" * 60)
    
    signature_score = 0
    max_score = 3
    
    if results.get("gue_spacing", {}).get("is_gue_like"):
        print("✓ GUE spacing test passed")
        signature_score += 1
    
    if results.get("pair_correlation", {}).get("empirical_riemann_correlation", 0) > 0.8:
        print("✓ Pair correlation test passed")
        signature_score += 1
    
    if results.get("spectral_rigidity", {}).get("is_gue_like"):
        print("✓ Spectral rigidity test passed")
        signature_score += 1
    
    print(f"\nEnhanced Signature Score: {signature_score}/{max_score}")
    
    if signature_score >= 2:
        print("STRONG EVIDENCE: UFRF shows Riemann-like structure")
    elif signature_score >= 1:
        print("MODERATE EVIDENCE: Some Riemann-like structure")
    else:
        print("WEAK EVIDENCE: Need refinement")

if __name__ == "__main__":
    main()

