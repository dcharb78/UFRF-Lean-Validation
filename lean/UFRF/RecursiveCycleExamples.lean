/-
  UFRF/RecursiveCycleExamples.lean

  Examples demonstrating the recursive cycle structure and circle-of-fifths walk.

  This file shows how to use RecursiveCycle.lean in practice.
-/

import UFRF.RecursiveCycle

namespace UFRF.Examples

open UFRF RecursiveCycle

/-!
## Example: System Level Hierarchy

Demonstrating the recursive structure SL0 → SL1 → SL2 → ...
-/

/-- Example: Root node at SL0, position 0 (SEED phase) -/
def example_root : SysNode := rootNode

/-- Example: Node at SL1, position 5 (AMPLIFY phase) -/
def example_sl1 : SysNode := { level := 1, pos := ⟨5, by decide⟩ }

/-- Example: Wrapping up from SL0 to SL1 -/
def example_wrap : SysNode := wrapUp rootNode

/-- Verification: Wrapping preserves phase -/
example : nodePhase (wrapUp rootNode) = nodePhase rootNode := by
  exact wrapUp_preserves_phase rootNode

/-!
## Example: Circle of Fifths Walk

Demonstrating the harmonic motion through the 13-cycle.
-/

/-- Example: Starting at position 0, take 1 step in circle-of-fifths -/
def example_fifths_step1 : SysNode := fifthsWalk ⟨0, by decide⟩ 1

/-- Verification: Position 0 → position 8 (first step of circle-of-fifths) -/
example : (fifthsWalk ⟨0, by decide⟩ 1).pos = ⟨8, by decide⟩ := by
  unfold fifthsWalk fifthsStep rotate fifthsOffset cycleLen
  simp
  norm_num

/-- Example: Starting at position 0, take 2 steps in circle-of-fifths -/
def example_fifths_step2 : SysNode := fifthsWalk ⟨0, by decide⟩ 2

/-- Verification: Position 0 → 8 → 3 (second step) -/
example : (fifthsWalk ⟨0, by decide⟩ 2).pos = ⟨3, by decide⟩ := by
  unfold fifthsWalk fifthsStep rotate fifthsOffset cycleLen
  simp
  norm_num

/-- Example: Circle-of-fourths pulls back -/
def example_fourths_step1 : SysNode := fourthsWalk ⟨8, by decide⟩ 1

/-- Verification: Fourth step from 8 returns to 0 -/
example : (fourthsWalk ⟨8, by decide⟩ 1).pos = ⟨0, by decide⟩ := by
  unfold fourthsWalk fourthsStep rotate fourthsOffset cycleLen
  simp
  norm_num

/-!
## Example: Phase Preservation

Showing that phases are consistent across system levels.
-/

/-- Example: Root node is in SEED phase -/
example : nodePhase rootNode = Phase.seed := by
  unfold rootNode nodePhase
  rfl

/-- Example: SL1 node at position 5 is in AMPLIFY phase -/
example : nodePhase example_sl1 = Phase.amplify := by
  unfold example_sl1 nodePhase
  rfl

/-!
## Example: Complete Circle-of-Fifths Sequence

The sequence: 0 → 8 → 3 → 11 → 6 → 1 → 9 → 4 → 12 → 7 → 2 → 10 → 5 → 0
-/

/-- First few steps of the circle-of-fifths -/
example : (fifthsWalk ⟨0, by decide⟩ 0).pos.val = 0 := by rfl
example : (fifthsWalk ⟨0, by decide⟩ 1).pos.val = 8 := by norm_num
example : (fifthsWalk ⟨0, by decide⟩ 2).pos.val = 3 := by norm_num
example : (fifthsWalk ⟨0, by decide⟩ 3).pos.val = 11 := by norm_num
example : (fifthsWalk ⟨0, by decide⟩ 4).pos.val = 6 := by norm_num

end UFRF.Examples

