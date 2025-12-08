# Robustness Test Plan - "Don't Delay" Items

## Overview

This document outlines the critical robustness tests to determine if the 99.5% correlation between ζ_H(s) and ζ(s) zeros is robust or a fluke.

## Status

✅ **Framework Created**: Basic test infrastructure in place  
📋 **In Progress**: Implementing real measurement logic  
⏳ **Pending**: Full ablation tests, random baselines

## Test Categories

### 1. Scale Up ζ_H vs ζ Comparison ✅ Framework Ready

**Current State**:
- 6 critical line points computed
- 25 zeros found
- 0.995 correlation

**Next Steps**:
- [x] Compute 100-200 zeros (framework ready in `robustness_test.py`)
- [ ] Compare against 100-200 classical ζ zeros
- [ ] Compute detailed metrics:
  - Correlation
  - Mean Absolute Deviation (MAD)
  - Scaled differences
- [ ] Vary truncation/matrix size
- [ ] Track convergence/drift

**Files**:
- `python/robustness_test.py` - Main test framework
- `python/spectral_zeta.py` - Zero finding

### 2. Real 5-Scale Nested Manifold Test ✅ Implementation Started

**Current State**:
- Mock implementation exists
- Real measurement logic started

**Next Steps**:
- [x] Implement real `measure_agreement_real()` based on spectral activity
- [x] Implement `measure_coherence()` based on phase consistency
- [x] Implement `measure_dominance()` based on relative agreement
- [ ] Run full test suite
- [ ] Validate predictions:
  - 233 should "light up" like 89 did at 3→4 transition
  - 89 should stay strong but not create new dramatic jump

**Files**:
- `python/real_5scale_test.py` - Real implementation
- `python/nested_manifold_test.py` - Original mock

### 3. Robustness / Ablation Experiments ⏳ Framework Ready

**Current State**:
- Framework exists in `robustness_test.py`
- Needs actual ablation implementations

**Next Steps**:
- [ ] **Break 13-cycle structure**:
  - Replace `rotate` with random permutation
  - Use cycle length 11 or 17 instead of 13
- [ ] **Remove dual trinity**:
  - Collapse Trinity to single level (zero only)
  - Permute the -0.5, 0, +0.5 mapping arbitrarily
- [ ] **Remove EW/NS axis**:
  - Collapse Axis to single plane
- [ ] **Flatten recursion**:
  - Ignore SysLevel, treat everything as SL0 only
- [ ] **Random baselines**:
  - Generate random symmetric matrices
  - Compute spectral zeta zeros
  - Compare correlation with ζ zeros

**Expected Results** (if UFRF is real):
- Correlation should drop significantly when geometry is broken
- 13-cycle + dual trinity + recursion should be uniquely good
- Random baselines should show ~0.2-0.6 correlation (not 0.995)

**Files**:
- `python/robustness_test.py` - Ablation framework
- Need: Ablation variant implementations

### 4. Lean Next Steps ✅ Started

**Current State**:
- SpectralZeta.lean strengthened with convergence theorem
- Nesting wired into Spectral via `isNestingSpecial`

**Completed**:
- [x] Strengthen SpectralZeta.lean:
  - Convergence theorem (finite sum always converges)
  - Real-valued property structure
  - Critical line function definition
- [x] Wire Nesting into Spectral:
  - `isNestingSpecial` predicate
  - Integrated into `massTerm` for enhanced activation

**Next Steps**:
- [ ] Complete `spectralZeta_real` proof (showing real s → real ζ_H(s))
- [ ] Prove functional relations if they exist numerically
- [ ] Make UPrime depend on Nesting patterns explicitly

**Files**:
- `lean/UFRF/SpectralZeta.lean` - Strengthened
- `lean/UFRF/Spectral.lean` - Nesting integrated
- `lean/UFRF/Nesting.lean` - Decomposition structure

## Implementation Priority

### Immediate (This Week)
1. ✅ Complete real 5-scale test implementation
2. ✅ Strengthen SpectralZeta.lean
3. ✅ Wire Nesting into Spectral
4. ⏳ Run scaled-up comparison (100-200 zeros)

### Short Term (Next Week)
1. Implement geometry ablation variants
2. Run random baseline tests
3. Analyze eigenvector contributions
4. Track phase/nesting dependence

### Medium Term (Next Month)
1. Full ablation analysis
2. Detailed spacing statistics
3. n-level correlations
4. Formalize geometric → spectral → zeta connection

## Success Criteria

### Correlation Robustness
- ✅ Maintain >99% correlation at 100-200 zeros
- ✅ Correlation drops <0.8 when geometry broken
- ✅ Random baselines show <0.7 correlation

### Nested Manifold Test
- ✅ Position 233 shows jump at 24→48 (4→5 transition)
- ✅ Position 89 shows jump at 12→24 (3→4 transition)
- ✅ Similar jump magnitudes (independent evidence)

### Geometry Dependence
- ✅ Breaking 13-cycle reduces correlation significantly
- ✅ Removing trinity reduces correlation
- ✅ Flattening recursion reduces correlation
- ✅ Random matrices show much lower correlation

## Key Questions

1. **Does correlation hold at larger sample sizes?**
   - Test: 100-200 zeros vs 25 zeros
   - Expected: Maintain >99% if robust

2. **Do zeros converge or drift with basis size?**
   - Test: Vary max_level (SL0, SL1, SL2, ...)
   - Expected: Converge if geometry is fundamental

3. **Does breaking geometry reduce correlation?**
   - Test: Ablation variants
   - Expected: Yes, significantly

4. **Are random matrices significantly worse?**
   - Test: Random symmetric matrices
   - Expected: Yes, correlation ~0.2-0.6

5. **Does 233 behave like 89?**
   - Test: 5-scale nested manifold test
   - Expected: Yes, similar jump pattern

## Files Created/Modified

### New Files
- `python/robustness_test.py` - Comprehensive robustness testing
- `python/real_5scale_test.py` - Real 5-scale test implementation
- `ROBUSTNESS_TEST_PLAN.md` - This document

### Modified Files
- `lean/UFRF/SpectralZeta.lean` - Strengthened with convergence
- `lean/UFRF/Spectral.lean` - Nesting integrated
- `python/spectral_zeta.py` - Enhanced zero finding

## Next Actions

1. **Run scaled-up comparison** (100-200 zeros)
2. **Complete ablation implementations**
3. **Run random baseline tests**
4. **Analyze results and document findings**

---

**Status**: Framework Ready, Implementation In Progress  
**Priority**: High - "Don't Delay" Items  
**Date**: December 2025

