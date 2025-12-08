# UFRF Spectral Operator - Python Implementation

## Overview

This directory contains Python implementations of the UFRF spectral operator `H_full` for computational analysis and comparison with Riemann zeta zeros and Moonshine patterns.

## Files

- **spectral_computation.py**: Core implementation of H_full operator
- **spectral_analysis.py**: Enhanced analysis with visualization and ζ comparison
- **README.md**: This file

## Requirements

```bash
pip install numpy matplotlib
```

## Usage

### Basic Computation

```python
from spectral_computation import *

# Enumerate basis (SL0 and SL1)
basis = enumerate_basis(max_level=1)

# Build H_full matrix
H = build_matrix(basis)

# Compute spectrum
eigenvals, eigenvecs = compute_spectrum(H)

# Analyze
analysis = analyze_spectrum(eigenvals)
```

### Run Analysis

```bash
python3 spectral_computation.py    # Basic computation
python3 spectral_analysis.py      # Enhanced analysis with visualization
```

## Structure

### BasisIndex

The spectral basis is `BasisIndex = SysNode × Trinity × Axis`:

- **SysNode**: `(level: int, pos: int)` where `pos ∈ {0, ..., 12}`
- **Trinity**: `MINUS`, `ZERO`, `PLUS` (values -0.5, 0, +0.5)
- **Axis**: `EW`, `NS` (east-west, north-south)

### H_full Operator

```python
H_full(x, y) = massTerm(x) * δ(x=y)
             + cycleCoupling(x, y)
             + harmonicCoupling(x, y)
             + trinityCoupling(x, y)
             + axisCoupling(x, y)
```

All couplings are enhanced for UFRF-prime nodes.

### UFRF-Primality

A node is UFRF-prime if it satisfies geometric conditions. At SL0, positions **0** and **9** are UFRF-prime.

## Output

The scripts output:
- Matrix properties (symmetry, diagonal non-negativity)
- Eigenvalue statistics
- Spacing distributions
- UFRF-prime analysis
- Comparison with ζ zeros (if available)
- Visualizations (if matplotlib available)

## Next Steps

1. **Larger basis**: Extend to SL2, SL3, ...
2. **Spectral zeta**: Compute ζ_H(s) = Σ λ⁻ˢ
3. **ζ zero comparison**: Load actual ζ zeros and compare spacing
4. **Moonshine patterns**: Analyze harmonic structure in spectrum
5. **Training coherence**: Map eigenvalues to breath cycles

## Notes

- Matrix is symmetric (verified)
- Diagonal elements are non-negative (verified)
- UFRF-primes enhance coupling strengths
- Spectrum shows interesting structure ready for analysis

---

**Status**: Core implementation complete, ready for analysis  
**Date**: December 2025

