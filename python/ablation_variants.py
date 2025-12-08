#!/usr/bin/env python3
"""
Geometry Ablation Variants for H_full

Tests robustness by breaking geometric structure:
- Random permutation instead of rotate
- Different cycle lengths
- Collapsed trinity
- Single axis
- Flat recursion

Author: Daniel Charboneau
Date: December 2025
"""

import numpy as np
from spectral_computation import *
from spectral_zeta import spectral_zeta, find_spectral_zeros
from spectral_analysis import load_zeta_zeros
from typing import List, Dict
import random

def build_matrix_random_permutation(basis: List) -> np.ndarray:
    """Build H_full with random permutation instead of rotate"""
    n = len(basis)
    H = np.zeros((n, n))
    
    # Create random permutation of 13-cycle
    cycle_perm = list(range(13))
    random.shuffle(cycle_perm)
    
    def random_rotate(pos: int) -> int:
        """Random permutation instead of +8 mod 13"""
        return cycle_perm[pos % 13]
    
    # Rebuild couplings with random permutation
    for i, x in enumerate(basis):
        for j, y in enumerate(basis):
            # Mass term (unchanged)
            if x == y:
                H[i, j] = mass_term(x)
            
            # Cycle coupling with random permutation
            if (x.node.level == y.node.level and
                x.trinity == y.trinity and
                x.axis == y.axis):
                x_pos, y_pos = x.node.pos, y.node.pos
                # Use random permutation instead of ±1 mod 13
                perm_x = random_rotate(x_pos)
                perm_y = random_rotate(y_pos)
                diff = abs(perm_x - perm_y)
                diff_mod = min(diff, 13 - diff)
                if diff_mod == 1:
                    H[i, j] += 1.0
            
            # Other couplings unchanged for now
            H[i, j] += harmonic_coupling(x, y)
            H[i, j] += trinity_coupling(x, y)
            H[i, j] += axis_coupling(x, y)
    
    return H

def build_matrix_different_cycle_length(basis: List, cycle_len: int = 11) -> np.ndarray:
    """Build H_full with different cycle length (11 or 17 instead of 13)"""
    n = len(basis)
    H = np.zeros((n, n))
    
    def modified_rotate(pos: int, offset: int) -> int:
        """Rotate with different cycle length"""
        return (pos + offset) % cycle_len
    
    for i, x in enumerate(basis):
        for j, y in enumerate(basis):
            if x == y:
                H[i, j] = mass_term(x)
            
            # Cycle coupling with modified cycle length
            if (x.node.level == y.node.level and
                x.trinity == y.trinity and
                x.axis == y.axis):
                x_pos, y_pos = x.node.pos % cycle_len, y.node.pos % cycle_len
                diff = abs(x_pos - y_pos)
                diff_mod = min(diff, cycle_len - diff)
                if diff_mod == 1:
                    H[i, j] += 1.0
            
            H[i, j] += harmonic_coupling(x, y)
            H[i, j] += trinity_coupling(x, y)
            H[i, j] += axis_coupling(x, y)
    
    return H

def build_matrix_collapsed_trinity(basis: List) -> np.ndarray:
    """Build H_full with collapsed trinity (zero only)"""
    n = len(basis)
    H = np.zeros((n, n))
    
    # Filter to only zero trinity
    zero_basis = [b for b in basis if b.trinity.value == "zero"]
    zero_indices = {b: i for i, b in enumerate(zero_basis)}
    
    H_collapsed = np.zeros((len(zero_basis), len(zero_basis)))
    
    for i, x in enumerate(zero_basis):
        for j, y in enumerate(zero_basis):
            if x == y:
                H_collapsed[i, j] = mass_term(x)
            H_collapsed[i, j] += cycle_coupling(x, y)
            H_collapsed[i, j] += harmonic_coupling(x, y)
            # No trinity coupling (all same)
            H_collapsed[i, j] += axis_coupling(x, y)
    
    # Map back to full basis (zero elsewhere)
    H = np.zeros((n, n))
    for i, x in enumerate(zero_basis):
        orig_i = basis.index(x)
        for j, y in enumerate(zero_basis):
            orig_j = basis.index(y)
            H[orig_i, orig_j] = H_collapsed[i, j]
    
    return H

def build_matrix_single_axis(basis: List) -> np.ndarray:
    """Build H_full with single axis (EW only)"""
    n = len(basis)
    H = np.zeros((n, n))
    
    # Filter to only EW axis
    ew_basis = [b for b in basis if b.axis.value == "ew"]
    
    for i, x in enumerate(ew_basis):
        orig_i = basis.index(x)
        for j, y in enumerate(ew_basis):
            orig_j = basis.index(y)
            if x == y:
                H[orig_i, orig_j] = mass_term(x)
            H[orig_i, orig_j] += cycle_coupling(x, y)
            H[orig_i, orig_j] += harmonic_coupling(x, y)
            H[orig_i, orig_j] += trinity_coupling(x, y)
            # No axis coupling (all same)
    
    return H

def build_matrix_flat_recursion(basis: List) -> np.ndarray:
    """Build H_full with flat recursion (all SL0 only)"""
    n = len(basis)
    H = np.zeros((n, n))
    
    # Filter to only level 0
    sl0_basis = [b for b in basis if b.node.level == 0]
    
    for i, x in enumerate(sl0_basis):
        orig_i = basis.index(x)
        for j, y in enumerate(sl0_basis):
            orig_j = basis.index(y)
            if x == y:
                H[orig_i, orig_j] = mass_term(x)
            H[orig_i, orig_j] += cycle_coupling(x, y)
            H[orig_i, orig_j] += harmonic_coupling(x, y)
            H[orig_i, orig_j] += trinity_coupling(x, y)
            H[orig_i, orig_j] += axis_coupling(x, y)
    
    return H

def test_ablation_variant(name: str, build_func, basis: List, 
                          riemann_zeros: np.ndarray) -> Dict:
    """Test an ablation variant and compare to ζ zeros"""
    print(f"\nTesting: {name}")
    print("-" * 60)
    
    try:
        H = build_func(basis)
        eigenvals, eigenvecs = compute_spectrum(H)
        positive_evals = eigenvals[eigenvals > 0]
        
        print(f"  Matrix size: {H.shape}")
        print(f"  Positive eigenvalues: {len(positive_evals)}")
        
        # Find zeros
        zeros = find_spectral_zeros(eigenvals, imag_range=(0, 50), resolution=1000)
        print(f"  Zeros found: {len(zeros)}")
        
        if len(zeros) > 0:
            from robustness_test import compare_zeros_detailed
            comparison = compare_zeros_detailed(zeros, riemann_zeros)
            corr = comparison.get('correlation', 0)
            print(f"  Correlation with ζ zeros: {corr:.4f}")
            return {
                "name": name,
                "correlation": corr,
                "zeros_count": len(zeros),
                "comparison": comparison
            }
        else:
            print("  No zeros found")
            return {"name": name, "correlation": 0.0, "zeros_count": 0}
    except Exception as e:
        print(f"  Error: {e}")
        return {"name": name, "correlation": 0.0, "error": str(e)}

def main():
    """Run all ablation tests"""
    print("Geometry Ablation Tests")
    print("=" * 60)
    
    # Build baseline
    basis = enumerate_basis(max_level=1)
    H_baseline = build_matrix(basis)
    eigenvals_baseline, _ = compute_spectrum(H_baseline)
    zeros_baseline = find_spectral_zeros(eigenvals_baseline, imag_range=(0, 50), resolution=1000)
    
    riemann_zeros = load_zeta_zeros(n_zeros=min(100, len(zeros_baseline)))
    
    from robustness_test import compare_zeros_detailed
    baseline_comparison = compare_zeros_detailed(zeros_baseline, riemann_zeros)
    baseline_corr = baseline_comparison.get('correlation', 0)
    
    print(f"\nBaseline (Original H_full):")
    print(f"  Correlation: {baseline_corr:.4f}")
    
    results = []
    
    # Test variants
    variants = [
        ("Random Permutation", lambda b: build_matrix_random_permutation(b)),
        ("Cycle Length 11", lambda b: build_matrix_different_cycle_length(b, 11)),
        ("Cycle Length 17", lambda b: build_matrix_different_cycle_length(b, 17)),
        ("Collapsed Trinity", lambda b: build_matrix_collapsed_trinity(b)),
        ("Single Axis (EW)", lambda b: build_matrix_single_axis(b)),
        ("Flat Recursion (SL0)", lambda b: build_matrix_flat_recursion(b)),
    ]
    
    for name, build_func in variants:
        result = test_ablation_variant(name, build_func, basis, riemann_zeros)
        results.append(result)
    
    # Summary
    print("\n" + "=" * 60)
    print("Ablation Test Summary")
    print("=" * 60)
    print(f"Baseline correlation: {baseline_corr:.4f}")
    print("\nAblation variants:")
    for r in results:
        corr = r.get('correlation', 0)
        drop = baseline_corr - corr
        print(f"  {r['name']:25s}: {corr:.4f} (drop: {drop:.4f})")
        if drop > 0.1:
            print("    ✓ Significant drop (geometry matters)")
        elif drop < 0.05:
            print("    ⚠ Small drop (geometry may not be critical)")
    
    return results

if __name__ == "__main__":
    main()

