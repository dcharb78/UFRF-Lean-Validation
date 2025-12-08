#!/usr/bin/env python3
"""
Fractal Self-Similarity Test

Tests whether H_L (restriction to level L) is self-similar to H_0.
This is a key property of UFRF: the pattern repeats at each system level.

Author: Daniel Charboneau
Date: December 2025
"""

import numpy as np
from spectral_computation import *
from typing import List, Dict, Tuple

def extract_level_matrix(basis: List, H: np.ndarray, level: int) -> Tuple[np.ndarray, List]:
    """
    Extract H_L: restriction of H to nodes at system level L.
    
    Returns:
        H_L: Submatrix of H for level L nodes
        basis_L: Subset of basis indices at level L
    """
    # Find all basis indices at level L
    level_indices = []
    for i, b in enumerate(basis):
        if b.node.level == level:
            level_indices.append(i)
    
    if len(level_indices) == 0:
        return np.array([]), []
    
    # Extract submatrix
    H_L = H[np.ix_(level_indices, level_indices)]
    basis_L = [basis[i] for i in level_indices]
    
    return H_L, basis_L

def normalize_matrix(H: np.ndarray) -> np.ndarray:
    """
    Normalize matrix by Frobenius norm.
    """
    if H.size == 0:
        return H
    
    norm = np.linalg.norm(H, 'fro')
    if norm > 0:
        return H / norm
    return H

def compare_adjacency_patterns(H0: np.ndarray, HL: np.ndarray) -> Dict:
    """
    Compare adjacency patterns between H_0 and H_L.
    
    Returns similarity metrics:
    - Structural similarity (sparsity pattern)
    - Coupling strength similarity
    - Pattern correlation
    """
    if H0.size == 0 or HL.size == 0:
        return {"error": "Empty matrices"}
    
    # Normalize both matrices
    H0_norm = normalize_matrix(H0)
    HL_norm = normalize_matrix(HL)
    
    # 1. Structural similarity (sparsity pattern)
    # Compare which elements are non-zero
    H0_sparse = (H0_norm != 0).astype(float)
    HL_sparse = (HL_norm != 0).astype(float)
    
    # Resize to same dimensions if needed
    min_size = min(H0_norm.shape[0], HL_norm.shape[0])
    H0_sparse_resized = H0_sparse[:min_size, :min_size]
    HL_sparse_resized = HL_sparse[:min_size, :min_size]
    
    structural_similarity = np.sum(H0_sparse_resized == HL_sparse_resized) / (min_size ** 2)
    
    # 2. Coupling strength similarity
    # Compare normalized coupling strengths
    H0_resized = H0_norm[:min_size, :min_size]
    HL_resized = HL_norm[:min_size, :min_size]
    
    # Correlation of non-zero elements
    mask = (H0_resized != 0) & (HL_resized != 0)
    if np.sum(mask) > 0:
        coupling_correlation = np.corrcoef(
            H0_resized[mask].flatten(),
            HL_resized[mask].flatten()
        )[0, 1] if len(H0_resized[mask].flatten()) > 1 else 0.0
    else:
        coupling_correlation = 0.0
    
    # 3. Pattern correlation (overall similarity)
    pattern_correlation = np.corrcoef(
        H0_resized.flatten(),
        HL_resized.flatten()
    )[0, 1] if len(H0_resized.flatten()) > 1 else 0.0
    
    return {
        "structural_similarity": structural_similarity,
        "coupling_correlation": coupling_correlation if not np.isnan(coupling_correlation) else 0.0,
        "pattern_correlation": pattern_correlation if not np.isnan(pattern_correlation) else 0.0,
    }

def compare_eigenvalue_distributions(H0: np.ndarray, HL: np.ndarray) -> Dict:
    """
    Compare eigenvalue distributions between H_0 and H_L.
    
    Tests self-similarity in the spectrum.
    """
    if H0.size == 0 or HL.size == 0:
        return {"error": "Empty matrices"}
    
    # Compute eigenvalues
    eigenvals0 = np.linalg.eigvalsh(H0)
    eigenvalsL = np.linalg.eigvalsh(HL)
    
    # Normalize by mean
    mean0 = np.mean(eigenvals0) if len(eigenvals0) > 0 else 1.0
    meanL = np.mean(eigenvalsL) if len(eigenvalsL) > 0 else 1.0
    
    eigenvals0_norm = eigenvals0 / mean0 if mean0 > 0 else eigenvals0
    eigenvalsL_norm = eigenvalsL / meanL if meanL > 0 else eigenvalsL
    
    # Compare distributions
    # 1. Mean similarity
    mean_similarity = 1.0 - abs(mean0 - meanL) / (mean0 + meanL + 1e-10)
    
    # 2. Distribution shape similarity (using histogram)
    if len(eigenvals0_norm) > 0 and len(eigenvalsL_norm) > 0:
        hist0, bins = np.histogram(eigenvals0_norm, bins=20)
        histL, _ = np.histogram(eigenvalsL_norm, bins=bins)
        
        # Normalize histograms
        hist0_norm = hist0 / (np.sum(hist0) + 1e-10)
        histL_norm = histL / (np.sum(histL) + 1e-10)
        
        # Correlation of histograms
        distribution_correlation = np.corrcoef(hist0_norm, histL_norm)[0, 1] if len(hist0_norm) > 1 else 0.0
        distribution_correlation = distribution_correlation if not np.isnan(distribution_correlation) else 0.0
        
        # KL divergence (smaller is better)
        kl_div = np.sum(hist0_norm * np.log(hist0_norm / (histL_norm + 1e-10) + 1e-10))
    else:
        distribution_correlation = 0.0
        kl_div = float('inf')
    
    # 3. Spacing distribution similarity
    if len(eigenvals0_norm) > 1 and len(eigenvalsL_norm) > 1:
        spacings0 = np.diff(np.sort(eigenvals0_norm))
        spacingsL = np.diff(np.sort(eigenvalsL_norm))
        
        spacing_correlation = np.corrcoef(spacings0, spacingsL)[0, 1] if len(spacings0) > 1 else 0.0
        spacing_correlation = spacing_correlation if not np.isnan(spacing_correlation) else 0.0
    else:
        spacing_correlation = 0.0
    
    return {
        "mean_similarity": mean_similarity,
        "distribution_correlation": distribution_correlation,
        "spacing_correlation": spacing_correlation,
        "kl_divergence": kl_div,
    }

def test_fractal_self_similarity(max_level: int = 3) -> Dict:
    """
    Test fractal self-similarity across system levels.
    
    For each L in {0,1,2,3}:
    - Extract H_L (restriction to level L)
    - Normalize
    - Compare H_L vs H_0 by:
      - Adjacency pattern
      - Eigenvalue distribution
    
    Returns similarity scores for each level.
    """
    print("=" * 60)
    print("FRACTAL SELF-SIMILARITY TEST")
    print("=" * 60)
    
    # Build full operator
    basis = enumerate_basis(max_level=max_level)
    H_full = build_matrix(basis)
    
    # Extract H_0 (base level)
    H0, basis0 = extract_level_matrix(basis, H_full, level=0)
    
    if H0.size == 0:
        return {"error": "Could not extract H_0"}
    
    print(f"\nH_0 size: {H0.shape}")
    print(f"H_0 basis size: {len(basis0)}")
    
    results = {}
    
    for L in range(1, max_level + 1):
        print(f"\n{'='*60}")
        print(f"Testing Level L={L}")
        print(f"{'='*60}")
        
        # Extract H_L
        HL, basisL = extract_level_matrix(basis, H_full, level=L)
        
        if HL.size == 0:
            print(f"  No nodes at level {L}")
            results[L] = {"error": "No nodes at this level"}
            continue
        
        print(f"  H_L size: {HL.shape}")
        print(f"  H_L basis size: {len(basisL)}")
        
        # Compare adjacency patterns
        print("\n  Comparing adjacency patterns...")
        adj_comparison = compare_adjacency_patterns(H0, HL)
        if "error" not in adj_comparison:
            print(f"    Structural similarity: {adj_comparison['structural_similarity']:.4f}")
            print(f"    Coupling correlation: {adj_comparison['coupling_correlation']:.4f}")
            print(f"    Pattern correlation: {adj_comparison['pattern_correlation']:.4f}")
        
        # Compare eigenvalue distributions
        print("\n  Comparing eigenvalue distributions...")
        eigen_comparison = compare_eigenvalue_distributions(H0, HL)
        if "error" not in eigen_comparison:
            print(f"    Mean similarity: {eigen_comparison['mean_similarity']:.4f}")
            print(f"    Distribution correlation: {eigen_comparison['distribution_correlation']:.4f}")
            print(f"    Spacing correlation: {eigen_comparison['spacing_correlation']:.4f}")
            print(f"    KL divergence: {eigen_comparison['kl_divergence']:.4f}")
        
        # Combined similarity score
        if "error" not in adj_comparison and "error" not in eigen_comparison:
            # Weighted average of similarity metrics
            similarity_score = (
                0.3 * adj_comparison['structural_similarity'] +
                0.2 * adj_comparison['coupling_correlation'] +
                0.2 * adj_comparison['pattern_correlation'] +
                0.1 * eigen_comparison['mean_similarity'] +
                0.1 * eigen_comparison['distribution_correlation'] +
                0.1 * eigen_comparison['spacing_correlation']
            )
            print(f"\n  Combined similarity score: {similarity_score:.4f}")
            
            results[L] = {
                "adjacency": adj_comparison,
                "eigenvalue": eigen_comparison,
                "similarity_score": similarity_score,
            }
        else:
            results[L] = {
                "adjacency": adj_comparison,
                "eigenvalue": eigen_comparison,
            }
    
    # Overall fractal self-similarity score
    similarity_scores = [results[L].get("similarity_score", 0.0) 
                        for L in results.keys() 
                        if "similarity_score" in results[L]]
    
    if len(similarity_scores) > 0:
        overall_score = np.mean(similarity_scores)
        print(f"\n{'='*60}")
        print(f"OVERALL FRACTAL SELF-SIMILARITY SCORE: {overall_score:.4f}")
        print(f"{'='*60}")
        
        if overall_score > 0.8:
            print("STRONG: High fractal self-similarity (UFRF-like)")
        elif overall_score > 0.6:
            print("MODERATE: Some fractal self-similarity")
        elif overall_score > 0.4:
            print("WEAK: Low fractal self-similarity")
        else:
            print("NONE: No fractal self-similarity (random-like)")
        
        results["overall_score"] = overall_score
    else:
        results["overall_score"] = 0.0
    
    return results

def test_random_baseline_comparison(max_level: int = 3):
    """
    Compare UFRF fractal self-similarity to random baseline.
    
    Random baselines should NOT have this property.
    """
    print("\n" + "=" * 60)
    print("RANDOM BASELINE COMPARISON")
    print("=" * 60)
    
    # Build UFRF operator
    basis = enumerate_basis(max_level=max_level)
    H_ufrf = build_matrix(basis)
    
    # Build random baseline
    n = len(basis)
    A = np.random.randn(n, n)
    H_random = (A + A.T) / 2
    np.fill_diagonal(H_random, np.abs(np.diagonal(H_random)) + 0.1)
    
    # Test UFRF
    print("\nTesting UFRF operator...")
    ufrf_results = test_fractal_self_similarity(max_level)
    ufrf_score = ufrf_results.get("overall_score", 0.0)
    
    # Test random (synthetic levels - just split matrix)
    print("\nTesting random baseline (synthetic levels)...")
    # For random, we'll just split the matrix arbitrarily
    # This won't have true self-similarity
    H0_random = H_random[:n//4, :n//4]
    HL_random = H_random[n//4:n//2, n//4:n//2]
    
    random_comparison = compare_adjacency_patterns(H0_random, HL_random)
    random_eigen = compare_eigenvalue_distributions(H0_random, HL_random)
    
    if "error" not in random_comparison and "error" not in random_eigen:
        random_score = (
            0.3 * random_comparison['structural_similarity'] +
            0.2 * random_comparison['coupling_correlation'] +
            0.2 * random_comparison['pattern_correlation'] +
            0.1 * random_eigen['mean_similarity'] +
            0.1 * random_eigen['distribution_correlation'] +
            0.1 * random_eigen['spacing_correlation']
        )
    else:
        random_score = 0.0
    
    print(f"\n{'='*60}")
    print("COMPARISON")
    print(f"{'='*60}")
    print(f"UFRF fractal self-similarity: {ufrf_score:.4f}")
    print(f"Random baseline: {random_score:.4f}")
    print(f"Difference: {ufrf_score - random_score:.4f}")
    
    if ufrf_score > random_score + 0.2:
        print("✓ UFRF shows significantly more fractal self-similarity")
    else:
        print("⚠ Need refinement or larger matrices")

def main():
    """Run fractal self-similarity tests"""
    results = test_fractal_self_similarity(max_level=3)
    
    # Compare to random baseline
    test_random_baseline_comparison(max_level=3)
    
    return results

if __name__ == "__main__":
    main()

