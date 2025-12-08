/-
  UFRF/Spectral.lean

  Spectral operator H_full defined on UFRF geometric basis.

  This module defines:
  - BasisIndex = SysNode × Trinity × Axis (the spectral basis)
  - Coupling functions: cycle, harmonic, trinity, axis
  - H_full operator kernel
  - Symmetry and basic properties

  The spectral operator H_full is the UFRF-native operator whose spectrum
  reflects the geometry. This is the foundation for connecting to zeta zeros
  and Moonshine patterns through computation, not assumption.

  Author: Daniel Charboneau
  Date: December 2025
-/

import UFRF.Foundation
import UFRF.RecursiveCycle
import UFRF.UPrime

namespace UFRF.Spectral

open UFRF RecursiveCycle Phase UPrime

/-!
## Spectral Basis Structure

The spectral operator acts on a basis indexed by:
- SysNode: recursive system level and position
- Trinity: minus, zero, plus (values -0.5, 0, +0.5)
- Axis: EW (east-west) or NS (north-south)

This creates a rich basis that captures:
- Recursive hierarchy (via SysNode)
- Balance structure (via Trinity)
- Duality (via Axis)
- Harmonic motion (via couplings)
-/

/-- Trinity labels for the spectral basis -/
inductive Trinity : Type
  | minus  -- -0.5
  | zero   -- 0
  | plus   -- +0.5
deriving DecidableEq, Repr

open Trinity

/-- Map Trinity label to its real value -/
def trinityValue (t : Trinity) : ℝ :=
  match t with
  | minus => trinityNeg
  | zero => trinityNeutral
  | plus => trinityPos

/-- Verification: trinityValue maps correctly -/
theorem trinityValue_correct :
    trinityValue minus = -0.5 ∧
    trinityValue zero = 0 ∧
    trinityValue plus = 0.5 := by
  constructor
  · unfold trinityValue trinityNeg; norm_num
  · constructor
    · unfold trinityValue trinityNeutral; norm_num
    · unfold trinityValue trinityPos; norm_num

/-- Axis labels: EW (east-west) and NS (north-south) -/
inductive Axis : Type
  | ew  -- East-West axis
  | ns  -- North-South axis
deriving DecidableEq, Repr

open Axis

/-- The spectral basis index: SysNode × Trinity × Axis -/
structure BasisIndex where
  node : SysNode
  trinity : Trinity
  axis : Axis
deriving DecidableEq, Repr

/-!
## Coupling Functions

The operator H_full is built from several coupling terms:
1. Cycle coupling: neighbors on the 13-cycle (±1 positions)
2. Harmonic coupling: fifthsStep and fourthsStep connections
3. Trinity coupling: transitions between trinity states
4. Axis coupling: EW ↔ NS transitions
5. Mass term: diagonal contribution

Each coupling respects the geometric structure.
-/

/-- Cycle coupling: connects neighboring positions on the 13-cycle.

    Two basis indices are cycle-coupled if:
    - Same system level
    - Same trinity
    - Same axis
    - Positions differ by ±1 mod 13
    
    Coupling strength is enhanced if either node is UFRF-prime.
-/
def cycleCoupling (x y : BasisIndex) : ℝ :=
  if x.node.level = y.node.level ∧
     x.trinity = y.trinity ∧
     x.axis = y.axis then
    -- Check if positions are neighbors (±1 mod 13)
    let xPos := x.node.pos.val
    let yPos := y.node.pos.val
    let diff := if xPos ≤ yPos then yPos - xPos else xPos - yPos
    let diffMod := diff % cycleLen
    if diffMod = 1 ∨ diffMod = cycleLen - 1 then
      -- Base coupling strength
      let baseStrength := 1.0
      -- Enhanced if UFRF-prime
      let enhancement := if isUPrime x.node ∨ isUPrime y.node then 0.5 else 0.0
      baseStrength + enhancement
    else
      0.0
  else
    0.0

/-- Harmonic coupling: connects via circle-of-fifths or circle-of-fourths.

    Two basis indices are harmonically coupled if:
    - Same system level
    - Same trinity
    - Same axis
    - Positions are related by fifthsStep or fourthsStep
    
    Coupling is stronger if both nodes are UFRF-prime (harmonic resonance).
-/
def harmonicCoupling (x y : BasisIndex) : ℝ :=
  if x.node.level = y.node.level ∧
     x.trinity = y.trinity ∧
     x.axis = y.axis then
    -- Check if y.pos = fifthsStep x.pos or y.pos = fourthsStep x.pos
    if y.node.pos = fifthsStep x.node.pos ∨ y.node.pos = fourthsStep x.node.pos then
      -- Base harmonic coupling strength
      let baseStrength := 0.5
      -- Enhanced if both are UFRF-prime (harmonic resonance)
      let resonance := if isUPrime x.node ∧ isUPrime y.node then 0.3 else 0.0
      baseStrength + resonance
    else
      0.0
  else
    0.0

/-- Trinity coupling: connects different trinity states.

    Two basis indices are trinity-coupled if:
    - Same system level
    - Same position
    - Same axis
    - Different trinity (allows transitions: minus ↔ zero ↔ plus)
-/
def trinityCoupling (x y : BasisIndex) : ℝ :=
  if x.node.level = y.node.level ∧
     x.node.pos = y.node.pos ∧
     x.axis = y.axis ∧
     x.trinity ≠ y.trinity then
    -- Coupling strength depends on trinity transition
    -- minus ↔ zero and zero ↔ plus have stronger coupling
    if (x.trinity = minus ∧ y.trinity = zero) ∨
       (x.trinity = zero ∧ y.trinity = minus) ∨
       (x.trinity = zero ∧ y.trinity = plus) ∨
       (x.trinity = plus ∧ y.trinity = zero) then
      0.3
    else
      0.1  -- minus ↔ plus (weaker, goes through zero)
  else
    0.0

/-- Axis coupling: connects EW ↔ NS.

    Two basis indices are axis-coupled if:
    - Same system level
    - Same position
    - Same trinity
    - Different axis (EW ↔ NS)
-/
def axisCoupling (x y : BasisIndex) : ℝ :=
  if x.node.level = y.node.level ∧
     x.node.pos = y.node.pos ∧
     x.trinity = y.trinity ∧
     x.axis ≠ y.axis then
    0.2  -- Axis coupling strength
  else
    0.0

/-- Mass term: diagonal contribution based on node properties.

    The mass term depends on:
    - System level (higher levels have larger mass)
    - Phase (REST phase has special mass)
    - Trinity (zero/balance has different mass)
    - UFRF-primality (primes have enhanced mass - "spectral activation")
-/
def massTerm (x : BasisIndex) : ℝ :=
  let levelMass := (x.node.level : ℝ) * 0.1
  let phaseMass :=
    match nodePhase x.node with
    | Phase.rest => 1.0
    | Phase.harmonize => 0.5
    | Phase.seed => 0.3
    | Phase.amplify => 0.4
    | Phase.new => 0.2
  let trinityMass :=
    match x.trinity with
    | Trinity.zero => 0.5  -- Balance point has special mass
    | _ => 0.3
  let primeMass := if isUPrime x.node then 0.5 else 0.0  -- UFRF-primes have enhanced mass
  levelMass + phaseMass + trinityMass + primeMass

/-!
## Spectral Operator H_full

The full spectral operator combines all coupling terms:

H_full x y = massTerm(x) * δ(x=y) + cycleCoupling(x,y) + harmonicCoupling(x,y) 
            + trinityCoupling(x,y) + axisCoupling(x,y)

This operator is symmetric and reflects the UFRF geometric structure.
-/

/-- The full spectral operator H_full.

    H_full x y gives the matrix element between basis states x and y.
    It combines:
    - Diagonal mass term (when x = y)
    - Cycle coupling (neighbors on 13-cycle)
    - Harmonic coupling (fifths/fourths connections)
    - Trinity coupling (trinity state transitions)
    - Axis coupling (EW ↔ NS transitions)
-/
def H_full (x y : BasisIndex) : ℝ :=
  (if x = y then massTerm x else 0.0) +
  cycleCoupling x y +
  harmonicCoupling x y +
  trinityCoupling x y +
  axisCoupling x y

/-!
## Basic Properties

We prove that H_full is symmetric and has other basic properties needed
for spectral analysis.
-/

/-- H_full is symmetric: H_full x y = H_full y x.

    This follows because:
    - Mass term is diagonal (symmetric)
    - All coupling functions are symmetric by construction
-/
theorem H_full_symmetric (x y : BasisIndex) :
    H_full x y = H_full y x := by
  unfold H_full
  -- Mass term: symmetric (diagonal)
  by_cases h : x = y
  · simp [h]
  · simp [h, ne_comm.mp h]
  -- Cycle coupling: symmetric
  unfold cycleCoupling
  by_cases h1 : x.node.level = y.node.level ∧ x.trinity = y.trinity ∧ x.axis = y.axis
  · -- If conditions hold for x,y, they hold for y,x
    have h1' : y.node.level = x.node.level ∧ y.trinity = x.trinity ∧ y.axis = x.axis := by
      constructor <;> [exact h1.1.symm; exact h1.2.1.symm; exact h1.2.2.symm]
    -- Position difference is symmetric up to sign
    -- If |x.pos - y.pos| mod 13 = 1 or 12, then |y.pos - x.pos| mod 13 = 12 or 1
    -- Both are neighbors, so coupling is symmetric
    -- Key: diffMod = 1 or diffMod = 12 both indicate neighbors
    -- For x,y: diffMod = |xPos - yPos| mod 13
    -- For y,x: diffMod = |yPos - xPos| mod 13 = |xPos - yPos| mod 13 (same)
    -- So the neighbor check is symmetric
    -- Also, isUPrime x.node ∨ isUPrime y.node = isUPrime y.node ∨ isUPrime x.node (symmetric)
    -- Therefore cycleCoupling x y = cycleCoupling y x
    simp [h1, h1']
    -- The diffMod calculation is symmetric because |a - b| = |b - a|
    -- And the UFRF-prime check is symmetric (disjunction is commutative)
    congr 1
    -- Need to show: diffMod calculation gives same result for (x,y) and (y,x)
    -- This follows from |a - b| = |b - a|
    sorry -- Requires showing absolute difference is symmetric mod 13
  · simp [h1]
    -- If conditions don't hold for x,y, they don't hold for y,x
    have h1' : ¬(y.node.level = x.node.level ∧ y.trinity = x.trinity ∧ y.axis = x.axis) := by
      intro h'
      exact h1 ⟨h'.1.symm, h'.2.1.symm, h'.2.2.symm⟩
    simp [h1']
  -- Harmonic coupling: symmetric (fifthsStep and fourthsStep are inverses)
  unfold harmonicCoupling
  -- Similar structure to cycle coupling
  by_cases h_harmonic : x.node.level = y.node.level ∧ x.trinity = y.trinity ∧ x.axis = y.axis
  · -- If conditions hold for x,y, they hold for y,x
    have h_harmonic' : y.node.level = x.node.level ∧ y.trinity = x.trinity ∧ y.axis = x.axis := by
      constructor <;> [exact h_harmonic.1.symm; exact h_harmonic.2.1.symm; exact h_harmonic.2.2.symm]
    -- Check harmonic relation: y.pos = fifthsStep x.pos ↔ x.pos = fourthsStep y.pos
    -- Because fourthsStep is inverse of fifthsStep
    -- Similarly: y.pos = fourthsStep x.pos ↔ x.pos = fifthsStep y.pos
    -- So the harmonic relation is symmetric
    -- Also, isUPrime x.node ∧ isUPrime y.node = isUPrime y.node ∧ isUPrime x.node (symmetric)
    simp [h_harmonic, h_harmonic']
    -- Need to show: (y.pos = fifthsStep x.pos ∨ y.pos = fourthsStep x.pos) ↔
    --               (x.pos = fifthsStep y.pos ∨ x.pos = fourthsStep y.pos)
    -- This follows from fourths_inverse_fifths and fifths_inverse_fourths
    sorry -- Requires using inverse relationship from RecursiveCycle
  · -- If conditions don't hold, coupling is 0 for both
    have h_harmonic' : ¬(y.node.level = x.node.level ∧ y.trinity = x.trinity ∧ y.axis = x.axis) := by
      intro h'
      exact h_harmonic ⟨h'.1.symm, h'.2.1.symm, h'.2.2.symm⟩
    simp [h_harmonic, h_harmonic']
  -- Trinity coupling: symmetric by construction
  unfold trinityCoupling
  -- The conditions are symmetric: x.node.level = y.node.level ↔ y.node.level = x.node.level, etc.
  -- Coupling values are symmetric: if (x.trinity, y.trinity) = (minus, zero), then (y.trinity, x.trinity) = (zero, minus) with same value
  by_cases h_trinity : x.node.level = y.node.level ∧ x.node.pos = y.node.pos ∧ x.axis = y.axis ∧ x.trinity ≠ y.trinity
  · -- If conditions hold for x,y, they hold for y,x (symmetric)
    have h_trinity' : y.node.level = x.node.level ∧ y.node.pos = x.node.pos ∧ y.axis = x.axis ∧ y.trinity ≠ x.trinity := by
      constructor <;> [exact h_trinity.1.symm; exact h_trinity.2.1.symm; exact h_trinity.2.2.1.symm; exact h_trinity.2.2.2.symm]
    -- Now check coupling values are symmetric
    -- All trinity transitions have symmetric values by construction
    -- (minus, zero) = 0.3, (zero, minus) = 0.3
    -- (zero, plus) = 0.3, (plus, zero) = 0.3
    -- (minus, plus) = 0.1, (plus, minus) = 0.1
    simp [h_trinity, h_trinity']
    -- The coupling value depends only on the pair (x.trinity, y.trinity)
    -- and all pairs have symmetric values
    sorry -- Requires checking all 6 trinity transition cases explicitly
  · -- If conditions don't hold for x,y, they don't hold for y,x
    have h_trinity' : ¬(y.node.level = x.node.level ∧ y.node.pos = x.node.pos ∧ y.axis = x.axis ∧ y.trinity ≠ x.trinity) := by
      intro h'
      exact h_trinity ⟨h'.1.symm, h'.2.1.symm, h'.2.2.1.symm, h'.2.2.2.symm⟩
    simp [h_trinity, h_trinity']
  -- Axis coupling: symmetric by construction
  unfold axisCoupling
  -- Conditions are symmetric: same level, pos, trinity, different axis
  by_cases h_axis : x.node.level = y.node.level ∧ x.node.pos = y.node.pos ∧ x.trinity = y.trinity ∧ x.axis ≠ y.axis
  · -- If conditions hold for x,y, they hold for y,x
    have h_axis' : y.node.level = x.node.level ∧ y.node.pos = x.node.pos ∧ y.trinity = x.trinity ∧ y.axis ≠ x.axis := by
      constructor <;> [exact h_axis.1.symm; exact h_axis.2.1.symm; exact h_axis.2.2.1.symm; exact h_axis.2.2.2.symm]
    simp [h_axis, h_axis']
    -- Coupling value is 0.2 for both (symmetric)
    rfl
  · -- If conditions don't hold for x,y, they don't hold for y,x
    have h_axis' : ¬(y.node.level = x.node.level ∧ y.node.pos = x.node.pos ∧ y.trinity = x.trinity ∧ y.axis ≠ x.axis) := by
      intro h'
      exact h_axis ⟨h'.1.symm, h'.2.1.symm, h'.2.2.1.symm, h'.2.2.2.symm⟩
    simp [h_axis, h_axis']

/-- H_full has non-negative diagonal elements.

    This follows because massTerm is always positive.
-/
theorem H_full_diagonal_nonneg (x : BasisIndex) :
    0 ≤ H_full x x := by
  unfold H_full
  simp
  -- H_full x x = massTerm x + cycleCoupling x x + ...
  -- cycleCoupling x x = 0 (not neighbors with itself)
  -- harmonicCoupling x x = 0 (not related by fifths/fourths to itself)
  -- trinityCoupling x x = 0 (same trinity)
  -- axisCoupling x x = 0 (same axis)
  -- So H_full x x = massTerm x
  -- And massTerm x > 0 by construction
  have h_mass : 0 < massTerm x := by
    unfold massTerm
    -- levelMass ≥ 0 (level is natural number)
    have h_level : 0 ≤ (x.node.level : ℝ) * 0.1 := by
      apply mul_nonneg
      · simp [x.node.level]
      · norm_num
    -- phaseMass > 0 (all phase masses are positive)
    have h_phase : 0 < match nodePhase x.node with
      | Phase.rest => 1.0
      | Phase.harmonize => 0.5
      | Phase.seed => 0.3
      | Phase.amplify => 0.4
      | Phase.new => 0.2 := by
      cases nodePhase x.node <;> norm_num
    -- trinityMass > 0 (both cases are positive)
    have h_trinity : 0 < match x.trinity with
      | Trinity.zero => 0.5
      | _ => 0.3 := by
      cases x.trinity <;> norm_num
    -- primeMass ≥ 0 (either 0.5 or 0.0)
    have h_prime : 0 ≤ if isUPrime x.node then 0.5 else 0.0 := by
      by_cases h : isUPrime x.node
      · simp [h]; norm_num
      · simp [h]
    -- Sum is positive
    linarith [h_level, h_phase, h_trinity, h_prime]
  linarith [h_mass]

end UFRF.Spectral

