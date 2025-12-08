#!/usr/bin/env python3
"""
UFRF Spectral Operator - Computational Implementation

This module implements the spectral operator H_full for computational analysis.
It builds finite matrix approximations and computes eigenvalues for comparison
with Riemann zeta zeros and Moonshine patterns.

Author: Daniel Charboneau
Date: December 2025
"""

import numpy as np
from typing import List, Tuple, Dict
from dataclasses import dataclass
from enum import Enum

# ============================================================================
# Basis Structure
# ============================================================================

class Trinity(Enum):
    """Trinity labels: minus, zero, plus"""
    MINUS = "minus"
    ZERO = "zero"
    PLUS = "plus"

class Axis(Enum):
    """Axis labels: east-west, north-south"""
    EW = "ew"
    NS = "ns"

class TetraRole(Enum):
    """Tetrahedral role: UPPER, LOWER, INTERSECTION, CENTER"""
    UPPER = "upper"
    LOWER = "lower"
    INTERSECTION = "intersection"
    CENTER = "center"

@dataclass(frozen=True)
class SysNode:
    """System node: level and position in 13-cycle"""
    level: int
    pos: int  # 0-12
    
    def __post_init__(self):
        assert 0 <= self.pos < 13, f"Position must be 0-12, got {self.pos}"

@dataclass(frozen=True)
class BasisIndex:
    """Spectral basis index: SysNode × TetraRole × Trinity × Axis"""
    node: SysNode
    tetra_role: TetraRole
    trinity: Trinity
    axis: Axis
    
    def __hash__(self):
        return hash((self.node.level, self.node.pos, self.tetra_role.value, self.trinity.value, self.axis.value))

# ============================================================================
# Phase and UFRF-Primality
# ============================================================================

def phase_of(pos: int) -> str:
    """Get phase for position in 13-cycle"""
    if pos <= 2:
        return "seed"
    elif pos <= 5:
        return "amplify"
    elif pos <= 8:
        return "harmonize"
    elif pos == 9:
        return "rest"
    else:
        return "new"

def is_uprime(node: SysNode) -> bool:
    """Check if node is UFRF-prime"""
    # At SL0: positions 0 and 9 are UFRF-prime
    if node.level == 0:
        return node.pos == 0 or node.pos == 9
    # For higher levels, check conditions
    ph = phase_of(node.pos)
    is_seed_trinity = node.pos <= 2
    is_rest = node.pos == 9
    is_active_phase = ph in ["rest", "harmonize"]
    is_harmonically_aligned = node.pos % 3 == 0
    is_in_phase = node.level == 0 or node.pos % 2 == 0
    
    return (is_seed_trinity or is_rest) and is_active_phase and is_harmonically_aligned and is_in_phase

# ============================================================================
# Coupling Functions
# ============================================================================

def cycle_coupling(x: BasisIndex, y: BasisIndex) -> float:
    """Cycle coupling: neighbors on 13-cycle"""
    if (x.node.level == y.node.level and 
        x.trinity == y.trinity and 
        x.axis == y.axis):
        x_pos, y_pos = x.node.pos, y.node.pos
        diff = abs(x_pos - y_pos)
        diff_mod = min(diff, 13 - diff)  # Mod 13 distance
        if diff_mod == 1:
            base_strength = 1.0
            enhancement = 0.5 if (is_uprime(x.node) or is_uprime(y.node)) else 0.0
            return base_strength + enhancement
    return 0.0

def fifths_step(pos: int) -> int:
    """Circle-of-fifths step: +8 mod 13"""
    return (pos + 8) % 13

def fourths_step(pos: int) -> int:
    """Circle-of-fourths step: +5 mod 13"""
    return (pos + 5) % 13

# Golden ratio φ
PHI = (1 + np.sqrt(5)) / 2
INV_PHI = 1 / PHI

def directional_harmonic_kernel(x: BasisIndex, y: BasisIndex) -> float:
    """
    Directional harmonic kernel: root, 5th, 4th with φ and 1/φ weighting.
    
    Role-dependent emphasis:
    - UPPER: Emphasis on expansion (5th)
    - LOWER: Emphasis on return (4th)
    - INTERSECTION: Balanced
    - CENTER: Neutral
    """
    if (x.node.level == y.node.level and 
        x.trinity == y.trinity and 
        x.axis == y.axis):
        # 5th position (expansion) - weighted by φ
        if y.node.pos == fifths_step(x.node.pos):
            base_strength = 0.5 * PHI
            role_emphasis = {
                TetraRole.UPPER: 1.2,
                TetraRole.LOWER: 0.8,
                TetraRole.INTERSECTION: 1.0,
                TetraRole.CENTER: 1.0
            }[x.tetra_role]
            return base_strength * role_emphasis
        # 4th position (return) - weighted by 1/φ
        elif y.node.pos == fourths_step(x.node.pos):
            base_strength = 0.5 * INV_PHI
            role_emphasis = {
                TetraRole.UPPER: 0.8,
                TetraRole.LOWER: 1.2,
                TetraRole.INTERSECTION: 1.0,
                TetraRole.CENTER: 1.0
            }[x.tetra_role]
            return base_strength * role_emphasis
    return 0.0

def harmonic_coupling(x: BasisIndex, y: BasisIndex) -> float:
    """
    Harmonic coupling: uses directional kernel with φ weighting.
    Enhanced by UFRF-primality and nesting.
    """
    directional_kernel = directional_harmonic_kernel(x, y)
    if directional_kernel > 0:
        prime_resonance = 0.3 if (is_uprime(x.node) and is_uprime(y.node)) else 0.0
        nesting_resonance = 0.4 if (x.node.pos in [89 % 13, 233 % 13] and 
                                   y.node.pos in [89 % 13, 233 % 13]) else 0.0
        level_resonance = x.node.level * 0.15
        return directional_kernel + prime_resonance + nesting_resonance + level_resonance
    return 0.0

def cross_level_coupling(x: BasisIndex, y: BasisIndex) -> float:
    """
    Cross-level coupling: mirrors wrapUp pattern where sub_nodes feed into parents.
    
    A node at level L+1 couples to nodes at level L that it "wraps".
    Only couples if levels differ by exactly 1 (wrapUp pattern).
    """
    # Only couple if levels differ by exactly 1
    level_diff = abs(x.node.level - y.node.level)
    if (level_diff == 1 and
        x.node.pos == y.node.pos and  # Same position in wrapped cycle
        x.trinity == y.trinity and
        x.axis == y.axis):
        base_strength = 0.3
        # Enhanced if roles align
        role_alignment = 0.2 if x.tetra_role == y.tetra_role else 0.0
        # Enhanced if UFRF-prime
        prime_enhancement = 0.2 if (is_uprime(x.node) or is_uprime(y.node)) else 0.0
        return base_strength + role_alignment + prime_enhancement
    return 0.0

def trinity_coupling(x: BasisIndex, y: BasisIndex) -> float:
    """Trinity coupling: trinity state transitions"""
    if (x.node.level == y.node.level and 
        x.node.pos == y.node.pos and 
        x.axis == y.axis and 
        x.trinity != y.trinity):
        # Strong coupling: minus ↔ zero, zero ↔ plus
        strong_pairs = [
            (Trinity.MINUS, Trinity.ZERO),
            (Trinity.ZERO, Trinity.MINUS),
            (Trinity.ZERO, Trinity.PLUS),
            (Trinity.PLUS, Trinity.ZERO)
        ]
        if (x.trinity, y.trinity) in strong_pairs:
            return 0.3
        else:
            return 0.1  # minus ↔ plus (weaker)
    return 0.0

def axis_coupling(x: BasisIndex, y: BasisIndex) -> float:
    """Axis coupling: EW ↔ NS"""
    if (x.node.level == y.node.level and 
        x.node.pos == y.node.pos and 
        x.trinity == y.trinity and 
        x.axis != y.axis):
        return 0.2
    return 0.0

def mass_term(x: BasisIndex) -> float:
    """Mass term: diagonal contribution"""
    level_mass = x.node.level * 0.1
    ph = phase_of(x.node.pos)
    phase_mass = {
        "rest": 1.0,
        "harmonize": 0.5,
        "seed": 0.3,
        "amplify": 0.4,
        "new": 0.2
    }[ph]
    trinity_mass = 0.5 if x.trinity == Trinity.ZERO else 0.3
    prime_mass = 0.5 if is_uprime(x.node) else 0.0
    return level_mass + phase_mass + trinity_mass + prime_mass

# ============================================================================
# Spectral Operator H_full
# ============================================================================

def H_full(x: BasisIndex, y: BasisIndex) -> float:
    """
    Full spectral operator H_full
    
    Combines:
    - Diagonal mass term
    - Cycle coupling (neighbors on 13-cycle)
    - Harmonic coupling (directional fifths/fourths with φ weighting)
    - Cross-level coupling (wrapUp pattern: sub_nodes → parents)
    - Trinity coupling (trinity state transitions)
    - Axis coupling (EW ↔ NS)
    """
    diagonal = mass_term(x) if x == y else 0.0
    return (diagonal + 
            cycle_coupling(x, y) + 
            harmonic_coupling(x, y) + 
            cross_level_coupling(x, y) +
            trinity_coupling(x, y) + 
            axis_coupling(x, y))

# ============================================================================
# Matrix Construction
# ============================================================================

def enumerate_basis(max_level: int = 1) -> List[BasisIndex]:
    """
    Enumerate basis indices up to max_level.
    
    BasisIndex = SysNode × TetraRole × Trinity × Axis
    """
    basis = []
    for level in range(max_level + 1):
        for pos in range(13):
            node = SysNode(level=level, pos=pos)
            for tetra_role in TetraRole:
                for trinity in Trinity:
                    for axis in Axis:
                        basis.append(BasisIndex(
                            node=node,
                            tetra_role=tetra_role,
                            trinity=trinity,
                            axis=axis
                        ))
    return basis

def build_matrix(basis: List[BasisIndex]) -> np.ndarray:
    """Build H_full as a finite matrix"""
    n = len(basis)
    H = np.zeros((n, n))
    for i, x in enumerate(basis):
        for j, y in enumerate(basis):
            H[i, j] = H_full(x, y)
    return H

# ============================================================================
# Spectral Analysis
# ============================================================================

def compute_spectrum(H: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Compute eigenvalues and eigenvectors of H"""
    eigenvals, eigenvecs = np.linalg.eigh(H)  # eigh for symmetric matrices
    return eigenvals, eigenvecs

def analyze_spectrum(eigenvals: np.ndarray) -> Dict:
    """Analyze spectral properties"""
    # Filter positive eigenvalues (for spectral zeta)
    positive_evals = eigenvals[eigenvals > 0]
    
    # Compute spacing distribution
    sorted_evals = np.sort(positive_evals)
    if len(sorted_evals) > 1:
        spacings = np.diff(sorted_evals)
        mean_spacing = np.mean(spacings)
        normalized_spacings = spacings / mean_spacing if mean_spacing > 0 else spacings
    else:
        normalized_spacings = np.array([])
    
    return {
        "total_eigenvalues": len(eigenvals),
        "positive_eigenvalues": len(positive_evals),
        "min_eigenvalue": np.min(eigenvals),
        "max_eigenvalue": np.max(eigenvals),
        "mean_spacing": np.mean(normalized_spacings) if len(normalized_spacings) > 0 else 0.0,
        "spacing_std": np.std(normalized_spacings) if len(normalized_spacings) > 0 else 0.0,
    }

# ============================================================================
# Main Analysis
# ============================================================================

def main():
    """Main computational analysis"""
    print("UFRF Spectral Operator - Computational Analysis")
    print("=" * 60)
    
    # Enumerate basis (start with SL0 and SL1)
    print("\n1. Enumerating basis...")
    basis = enumerate_basis(max_level=1)
    print(f"   Basis size: {len(basis)} indices")
    print(f"   (SL0: {13 * 3 * 2} = 78, SL1: {13 * 3 * 2} = 78, Total: 156)")
    
    # Build matrix
    print("\n2. Building H_full matrix...")
    H = build_matrix(basis)
    print(f"   Matrix shape: {H.shape}")
    print(f"   Matrix is symmetric: {np.allclose(H, H.T)}")
    print(f"   Diagonal elements non-negative: {np.all(H.diagonal() >= 0)}")
    
    # Compute spectrum
    print("\n3. Computing spectrum...")
    eigenvals, eigenvecs = compute_spectrum(H)
    print(f"   Computed {len(eigenvals)} eigenvalues")
    
    # Analyze spectrum
    print("\n4. Analyzing spectrum...")
    analysis = analyze_spectrum(eigenvals)
    for key, value in analysis.items():
        print(f"   {key}: {value}")
    
    # Check for UFRF-prime nodes
    print("\n5. UFRF-prime analysis...")
    uprime_nodes = [b for b in basis if is_uprime(b.node)]
    print(f"   UFRF-prime nodes: {len(uprime_nodes)}")
    for node in uprime_nodes[:10]:  # Show first 10
        print(f"     Level {node.node.level}, Pos {node.node.pos}, "
              f"Trinity {node.trinity.value}, Axis {node.axis.value}")
    
    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("\nNext steps:")
    print("  - Compare eigenvalues to ζ zeros")
    print("  - Analyze spacing distribution (GUE-like?)")
    print("  - Compute spectral zeta ζ_H(s)")
    print("  - Visualize spectrum and couplings")

if __name__ == "__main__":
    main()

