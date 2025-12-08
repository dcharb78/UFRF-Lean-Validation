#!/usr/bin/env python3
"""
Comprehensive Visualization of UFRF Spectral Structure

Creates visualizations of:
- Eigenvalue distribution
- Spacing distributions
- UFRF-prime spectral activity
- Spectral zeta on critical line
- Comparison with ζ zeros

Author: Daniel Charboneau
Date: December 2025
"""

import numpy as np
import matplotlib.pyplot as plt
from spectral_computation import *
from spectral_zeta import spectral_zeta, find_spectral_zeros
from spectral_analysis import load_zeta_zeros

def create_comprehensive_visualization():
    """Create comprehensive visualization suite"""
    
    print("Creating comprehensive UFRF spectral visualizations...")
    
    # Build spectrum
    basis = enumerate_basis(max_level=1)
    H = build_matrix(basis)
    eigenvals, eigenvecs = compute_spectrum(H)
    positive_evals = eigenvals[eigenvals > 0]
    
    # Find UFRF-primes
    uprime_indices = [i for i, b in enumerate(basis) if is_uprime(b.node)]
    
    # Compute spectral zeta on critical line
    t_values = np.linspace(0, 50, 500)
    zeta_real = []
    zeta_imag = []
    for t in t_values:
        s = 0.5 + 1j * t
        zeta_val = spectral_zeta(eigenvals, s)
        zeta_real.append(zeta_val.real)
        zeta_imag.append(zeta_val.imag)
    
    # Find zeros
    zeros = find_spectral_zeros(eigenvals, real_part=0.5, imag_range=(0, 50))
    
    # Load ζ zeros for comparison
    try:
        riemann_zeros = load_zeta_zeros(n_zeros=min(100, len(positive_evals)))
    except:
        riemann_zeros = np.array([])
    
    # Create figure with subplots
    fig = plt.figure(figsize=(16, 12))
    
    # 1. Eigenvalue distribution
    ax1 = plt.subplot(3, 3, 1)
    ax1.hist(positive_evals, bins=50, edgecolor='black', alpha=0.7, color='blue')
    ax1.set_xlabel('Eigenvalue')
    ax1.set_ylabel('Frequency')
    ax1.set_title('H_full Eigenvalue Distribution')
    ax1.grid(True, alpha=0.3)
    
    # 2. Spacing distribution
    ax2 = plt.subplot(3, 3, 2)
    if len(positive_evals) > 1:
        spacings = np.diff(np.sort(positive_evals))
        mean_spacing = np.mean(spacings)
        normalized_spacings = spacings / mean_spacing if mean_spacing > 0 else spacings
        
        ax2.hist(normalized_spacings, bins=30, edgecolor='black', alpha=0.7, color='green')
        ax2.set_xlabel('Normalized Spacing')
        ax2.set_ylabel('Frequency')
        ax2.set_title('Eigenvalue Spacing Distribution')
        ax2.axvline(1.0, color='r', linestyle='--', label='Mean')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
    
    # 3. Eigenvalue sequence
    ax3 = plt.subplot(3, 3, 3)
    ax3.plot(positive_evals, 'o', markersize=2, alpha=0.6, color='purple')
    ax3.set_xlabel('Index')
    ax3.set_ylabel('Eigenvalue')
    ax3.set_title('Eigenvalue Sequence')
    ax3.grid(True, alpha=0.3)
    
    # 4. Spectral zeta real part on critical line
    ax4 = plt.subplot(3, 3, 4)
    ax4.plot(t_values, zeta_real, linewidth=1.5, color='red', label='Re(ζ_H)')
    ax4.axhline(0, color='black', linestyle='--', alpha=0.5)
    ax4.set_xlabel('Imaginary part t')
    ax4.set_ylabel('Real part')
    ax4.set_title('Re(ζ_H(0.5 + it)) on Critical Line')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # 5. Spectral zeta imaginary part
    ax5 = plt.subplot(3, 3, 5)
    ax5.plot(t_values, zeta_imag, linewidth=1.5, color='blue', label='Im(ζ_H)')
    ax5.axhline(0, color='black', linestyle='--', alpha=0.5)
    ax5.set_xlabel('Imaginary part t')
    ax5.set_ylabel('Imaginary part')
    ax5.set_title('Im(ζ_H(0.5 + it)) on Critical Line')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # 6. Zeros on critical line
    ax6 = plt.subplot(3, 3, 6)
    if len(zeros) > 0:
        zero_imags = [z.imag for z in zeros]
        ax6.scatter([0.5] * len(zero_imags), zero_imags, 
                   s=50, alpha=0.7, color='red', label='ζ_H zeros')
    if len(riemann_zeros) > 0:
        ax6.scatter([0.5] * len(riemann_zeros[:len(zeros)]), 
                   riemann_zeros[:len(zeros)], 
                   s=30, alpha=0.5, color='blue', marker='x', label='ζ zeros')
    ax6.set_xlabel('Real part')
    ax6.set_ylabel('Imaginary part')
    ax6.set_title('Zeros on Critical Line')
    ax6.set_xlim([0.4, 0.6])
    ax6.legend()
    ax6.grid(True, alpha=0.3)
    
    # 7. UFRF-prime spectral activity
    ax7 = plt.subplot(3, 3, 7)
    if len(uprime_indices) > 0:
        uprime_eigenvals = []
        for idx in uprime_indices:
            component = np.abs(eigenvecs[:, idx])
            significant_modes = eigenvals[component > 0.1]
            uprime_eigenvals.extend(significant_modes)
        
        if len(uprime_eigenvals) > 0:
            ax7.hist(uprime_eigenvals, bins=30, edgecolor='black', alpha=0.7, color='orange')
            ax7.set_xlabel('Eigenvalue')
            ax7.set_ylabel('Frequency')
            ax7.set_title(f'UFRF-Prime Spectral Activity\n({len(uprime_indices)} primes)')
            ax7.grid(True, alpha=0.3)
    
    # 8. Comparison: Spectral vs Riemann zeros
    ax8 = plt.subplot(3, 3, 8)
    if len(zeros) > 0 and len(riemann_zeros) > 0:
        spectral_imags = np.array([z.imag for z in zeros])
        riemann_imags = riemann_zeros[:len(spectral_imags)]
        
        # Normalize for comparison
        spectral_mean = np.mean(spectral_imags)
        riemann_mean = np.mean(riemann_imags)
        normalized_spectral = spectral_imags / spectral_mean if spectral_mean > 0 else spectral_imags
        normalized_riemann = riemann_imags / riemann_mean if riemann_mean > 0 else riemann_imags
        
        ax8.scatter(normalized_spectral, normalized_riemann, 
                   s=30, alpha=0.6, color='green')
        ax8.plot([0, max(normalized_spectral.max(), normalized_riemann.max())], 
                [0, max(normalized_spectral.max(), normalized_riemann.max())], 
                'r--', alpha=0.5, label='y=x')
        ax8.set_xlabel('Normalized Spectral Zeros')
        ax8.set_ylabel('Normalized Riemann Zeros')
        ax8.set_title('Zero Comparison')
        ax8.legend()
        ax8.grid(True, alpha=0.3)
    
    # 9. Matrix structure visualization
    ax9 = plt.subplot(3, 3, 9)
    # Show sparsity pattern
    H_sparse = (np.abs(H) > 1e-10).astype(int)
    ax9.spy(H_sparse, markersize=0.5, alpha=0.5)
    ax9.set_xlabel('Column index')
    ax9.set_ylabel('Row index')
    ax9.set_title('H_full Sparsity Pattern')
    
    plt.tight_layout()
    plt.savefig('comprehensive_spectral_analysis.png', dpi=150, bbox_inches='tight')
    print("Saved comprehensive visualization to comprehensive_spectral_analysis.png")
    
    # Print summary statistics
    print("\n" + "=" * 60)
    print("Visualization Summary")
    print("=" * 60)
    print(f"Total eigenvalues: {len(eigenvals)}")
    print(f"Positive eigenvalues: {len(positive_evals)}")
    print(f"Spectral zeta zeros found: {len(zeros)}")
    print(f"UFRF-prime nodes: {len(uprime_indices)}")
    if len(zeros) > 0 and len(riemann_zeros) > 0:
        correlation = np.corrcoef(
            [z.imag for z in zeros][:len(riemann_zeros)],
            riemann_zeros[:len(zeros)]
        )[0, 1]
        print(f"Correlation with ζ zeros: {correlation:.4f}")
    print("=" * 60)

if __name__ == "__main__":
    create_comprehensive_visualization()

