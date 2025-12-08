#!/usr/bin/env python3
"""
Spectral Zeta Function ζ_H(s)

Computes the spectral zeta function ζ_H(s) = Σ λ⁻ˢ over positive eigenvalues
of H_full, for comparison with the Riemann zeta function.

Author: Daniel Charboneau
Date: December 2025
"""

import numpy as np
from spectral_computation import *
from spectral_analysis import load_zeta_zeros

def spectral_zeta(H_eigenvals: np.ndarray, s: complex) -> complex:
    """Compute spectral zeta ζ_H(s) = Σ λ⁻ˢ over positive eigenvalues
    
    Args:
        H_eigenvals: All eigenvalues of H_full
        s: Complex number (typically s = σ + it)
    
    Returns:
        ζ_H(s) = Σ_{λ > 0} λ⁻ˢ
    """
    positive_evals = H_eigenvals[H_eigenvals > 0]
    if len(positive_evals) == 0:
        return 0.0
    
    # ζ_H(s) = Σ λ⁻ˢ = Σ exp(-s * log(λ))
    # For numerical stability, use: λ⁻ˢ = exp(-s * log(λ))
    log_evals = np.log(positive_evals)
    zeta_sum = np.sum(np.exp(-s * log_evals))
    return zeta_sum

def spectral_zeta_derivative(H_eigenvals: np.ndarray, s: complex) -> complex:
    """Compute derivative d/ds ζ_H(s) = -Σ λ⁻ˢ log(λ)"""
    positive_evals = H_eigenvals[H_eigenvals > 0]
    if len(positive_evals) == 0:
        return 0.0
    
    log_evals = np.log(positive_evals)
    zeta_deriv = -np.sum(np.exp(-s * log_evals) * log_evals)
    return zeta_deriv

def find_spectral_zeros(H_eigenvals: np.ndarray, 
                       real_part: float = 0.5,
                       imag_range: tuple = (0, 50),
                       resolution: int = 1000) -> list:
    """Find zeros of ζ_H(s) on the critical line Re(s) = real_part
    
    Uses Newton's method to find zeros where ζ_H(real_part + it) = 0
    
    Args:
        H_eigenvals: All eigenvalues of H_full
        real_part: Real part of s (default 0.5 for critical line)
        imag_range: (min_imag, max_imag) range to search
        resolution: Number of points to check
    
    Returns:
        List of approximate zeros (complex numbers)
    """
    zeros = []
    t_values = np.linspace(imag_range[0], imag_range[1], resolution)
    
    prev_sign = None
    for i, t in enumerate(t_values):
        s = real_part + 1j * t
        zeta_val = spectral_zeta(H_eigenvals, s)
        
        # Check for sign change (indicates zero crossing)
        current_sign = np.sign(zeta_val.real) if abs(zeta_val.real) > abs(zeta_val.imag) else np.sign(zeta_val.imag)
        
        if prev_sign is not None and prev_sign != current_sign and prev_sign != 0:
            # Sign change detected, refine zero using Newton's method
            zero_approx = refine_zero(H_eigenvals, real_part + 1j * t_values[i-1], real_part + 1j * t)
            zeros.append(zero_approx)
        
        prev_sign = current_sign
    
    return zeros

def refine_zero(H_eigenvals: np.ndarray, s0: complex, s1: complex, 
                real_part: float = 0.5,
                tolerance: float = 1e-6, max_iter: int = 10) -> complex:
    """Refine zero location using Newton's method"""
    s = (s0 + s1) / 2  # Start at midpoint
    
    for _ in range(max_iter):
        zeta_val = spectral_zeta(H_eigenvals, s)
        zeta_deriv = spectral_zeta_derivative(H_eigenvals, s)
        
        if abs(zeta_deriv) < 1e-10:
            break
        
        s_new = s - zeta_val / zeta_deriv
        
        # Keep real part fixed, only adjust imaginary part
        s = real_part + 1j * s_new.imag
        
        if abs(zeta_val) < tolerance:
            break
    
    return s

def compare_to_riemann_zeta(spectral_zeros: list, riemann_zeros: np.ndarray) -> dict:
    """Compare spectral zeta zeros to Riemann zeta zeros
    
    Args:
        spectral_zeros: Zeros of ζ_H(s) on critical line
        riemann_zeros: Imaginary parts of known ζ zeros
    
    Returns:
        Comparison statistics
    """
    if len(spectral_zeros) == 0 or len(riemann_zeros) == 0:
        return {"error": "Insufficient zeros for comparison"}
    
    spectral_imag = np.array([z.imag for z in spectral_zeros])
    riemann_imag = riemann_zeros[:len(spectral_imag)]
    
    # Normalize to similar scale
    spectral_mean = np.mean(spectral_imag)
    riemann_mean = np.mean(riemann_imag)
    
    normalized_spectral = spectral_imag / spectral_mean if spectral_mean > 0 else spectral_imag
    normalized_riemann = riemann_imag / riemann_mean if riemann_mean > 0 else riemann_imag
    
    # Compute correlation
    min_len = min(len(normalized_spectral), len(normalized_riemann))
    correlation = np.corrcoef(normalized_spectral[:min_len], normalized_riemann[:min_len])[0, 1]
    
    return {
        "spectral_zero_count": len(spectral_zeros),
        "riemann_zero_count": len(riemann_zeros),
        "correlation": correlation,
        "spectral_mean_imag": spectral_mean,
        "riemann_mean_imag": riemann_mean,
    }

def main():
    """Main spectral zeta analysis"""
    print("Spectral Zeta Function Analysis")
    print("=" * 60)
    
    # Build H_full and compute spectrum
    print("\n1. Computing H_full spectrum...")
    basis = enumerate_basis(max_level=1)
    H = build_matrix(basis)
    eigenvals, eigenvecs = compute_spectrum(H)
    positive_evals = eigenvals[eigenvals > 0]
    
    print(f"   Positive eigenvalues: {len(positive_evals)}")
    print(f"   Range: [{np.min(positive_evals):.4f}, {np.max(positive_evals):.4f}]")
    
    # Compute spectral zeta at critical line points
    print("\n2. Computing ζ_H(s) on critical line...")
    critical_points = [0.5 + 1j * t for t in [14.13, 21.02, 25.01, 30.42, 32.93, 37.58]]
    
    print("   ζ_H(s) values:")
    for s in critical_points:
        zeta_val = spectral_zeta(eigenvals, s)
        print(f"     ζ_H({s.real:.1f} + {s.imag:.2f}i) = {zeta_val.real:.4f} + {zeta_val.imag:.4f}i")
    
    # Find zeros
    print("\n3. Finding zeros of ζ_H(s) on critical line...")
    zeros = find_spectral_zeros(eigenvals, real_part=0.5, imag_range=(0, 50))
    print(f"   Found {len(zeros)} zeros")
    if len(zeros) > 0:
        print("   First few zeros:")
        for z in zeros[:5]:
            print(f"     {z.real:.4f} + {z.imag:.4f}i")
    
    # Compare to Riemann zeta zeros
    print("\n4. Comparing to Riemann zeta zeros...")
    riemann_zeros = load_zeta_zeros(n_zeros=min(100, len(positive_evals)))
    comparison = compare_to_riemann_zeta(zeros, riemann_zeros)
    for key, value in comparison.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.4f}")
        else:
            print(f"   {key}: {value}")
    
    print("\n" + "=" * 60)
    print("Spectral zeta analysis complete!")
    print("\nKey insights:")
    print("  - ζ_H(s) computed on critical line")
    print("  - Zeros found (if any)")
    print("  - Comparison with ζ zeros available")
    print("  - Ready for deeper analysis")

if __name__ == "__main__":
    main()

