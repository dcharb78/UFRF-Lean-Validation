/-
  Unified UFRF Formal Proofs

  This Lean 4 project provides formal proofs that fundamental physical
  constants emerge from geometric relationships in the Unified Field
  Resonance Framework (UFRF).

  All proofs are unified through a single 13-cycle geometric foundation.
-/

import Lake
open Lake DSL

package «UFRFUnified» where

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "v4.26.0-rc2"

lean_lib «UFRFUnified» where
  roots := #[`UFRF.Foundation, `UFRF.Constants, `UFRF.Unity, `UFRF.CriticalLine, `UFRF.ZetaFunction, `UFRF.RiemannHypothesis, `UFRF.Results]

