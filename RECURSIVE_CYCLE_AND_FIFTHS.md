# Recursive Cycle and Circle-of-Fifths

## Overview

The `RecursiveCycle.lean` module formalizes three key structures that are **first-class citizens** in the UFRF model:

1. **Local phases** (SEED/AMPLIFY/HARMONIZE/REST/NEW)
2. **Harmonic motion** (circle of fifths & fourths)
3. **Recursive system levels** (SL0, SL1, SL2, ...)

These are not separate concepts—they are unified in a single mathematical structure.

## The Trinity

### 1. Local Phases

At every system level, the same phase pattern applies:

- **SEED** (positions 0,1,2): Initial/seeding phase
- **AMPLIFY** (positions 3,4,5): Growth/amplification phase
- **HARMONIZE** (positions 6,7,8): Balancing/interference phase
- **REST** (position 9): Distinguished equilibrium phase
- **NEW** (positions 10,11,12): Completion/transition phase

### 2. Harmonic Motion

The **circle-of-fifths** provides harmonic motion through the 13-cycle:

**Sequence (1-based):** 1 → 9 → 4 → 12 → 7 → 2 → 10 → 5 → 13 → 8 → 3 → 11 → 6 → 1

**Sequence (0-based):** 0 → 8 → 3 → 11 → 6 → 1 → 9 → 4 → 12 → 7 → 2 → 10 → 5 → 0

Each step adds **+8 modulo 13**, visiting all 13 positions exactly once before returning.

The **circle-of-fourths** is the inverse motion (adds +5 modulo 13), providing the "pull back to source" harmonic motion.

### 3. Recursive System Levels

The recursive structure:

- **SL0**: Base 13-position cycle with phases
- **SL1**: 13 nodes, each node wraps a complete SL0 system
- **SL2**: 13 nodes, each node wraps a complete SL1 system
- **SL3, SL4, ...**: Infinite recursion

The key insight: **The same phase pattern applies at every level**. This is not "one thing over another"—it's the **same pattern repeated recursively**.

## Mathematical Structure

### System Nodes

```lean
structure SysNode where
  level : SysLevel  -- 0, 1, 2, ...
  pos   : Fin 13    -- Position in the 13-cycle
```

### Phase Assignment

```lean
def nodePhase (n : SysNode) : Phase := phaseOf n.pos
```

The phase depends only on the position, not the level. This ensures consistency across all system levels.

### Wrap-Up Operation

```lean
def wrapUp (n : SysNode) : SysNode :=
  { level := n.level + 1, pos := n.pos }
```

Wrapping a node to the next system level preserves its position (and thus its phase).

### Circle-of-Fifths

```lean
def fifthsStep (i : Fin 13) : Fin 13 := rotate ⟨8, by decide⟩ i
```

Each step moves forward by 8 positions modulo 13.

### Circle-of-Fourths

```lean
def fourthsStep (i : Fin 13) : Fin 13 := rotate ⟨5, by decide⟩ i
```

Each step moves forward by 5 positions modulo 13 (inverse of fifths).

## Key Properties

### 1. Phase Preservation

```lean
theorem wrapUp_preserves_phase (n : SysNode) :
    nodePhase (wrapUp n) = nodePhase n
```

Wrapping up to the next system level preserves the phase label.

### 2. Inverse Relationship

```lean
theorem fourths_inverse_fifths (i : Fin 13) :
    fourthsStep (fifthsStep i) = i

theorem fifths_inverse_fourths (i : Fin 13) :
    fifthsStep (fourthsStep i) = i
```

The circle-of-fourths is the inverse of the circle-of-fifths.

### 3. Periodicity

```lean
theorem fifthsWalk_periodic (pos₀ : Fin 13) :
    fifthsWalk pos₀ 13 = fifthsWalk pos₀ 0
```

After 13 steps of the circle-of-fifths, we return to the starting position.

## Usage Examples

See `RecursiveCycleExamples.lean` for concrete examples:

- Creating system nodes at different levels
- Walking the circle-of-fifths
- Verifying phase assignments
- Demonstrating the complete circle-of-fifths sequence

## Integration Points

This structure can be integrated with:

1. **Spectral Operators**: Use `fifthsStep` and `fourthsStep` to define harmonic neighbors in operator connectivity patterns.

2. **Training Schedules**: Map breath cycles and positions to `fifthsWalk` (growth) and `fourthsWalk` (pull-backs/resets).

3. **Monster Moonshine**: Use `fifthsStep` as the canonical permutation of 13 "notes"/states, with `nodePhase` marking segments that map to algebraic structures.

4. **Riemann Hypothesis**: The recursive structure provides the foundation for the trinity balance → critical line mapping.

## Key Insight

The recursion across system levels and the circle-of-fifths walk are **not separate concepts**—they are unified in a single mathematical structure where:

- The same phase pattern applies at every level
- Harmonic motion respects the phase boundaries
- Recursive wrapping preserves structure

This unified structure demonstrates that **local phases, harmonic motion, and recursive levels are all manifestations of the same underlying 13-cycle geometry**.

---

**File:** `lean/UFRF/RecursiveCycle.lean`  
**Examples:** `lean/UFRF/RecursiveCycleExamples.lean`  
**Status:** ✅ Lean-ready, no sorries in core definitions

