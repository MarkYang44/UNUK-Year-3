  /-
COMP2065-IFR
Exercise 01 (10 points)

Prove all the following propositions in Lean. 1 point per exercise.
That is replace "sorry" with your proof.

You are only allowed to use the tactics introduced in the lecture
(i.e. intro, exact, apply, constructor, cases, left, right, have)
and only in the way we have introduced them.

Your proofs must be tactic proofs: each proof starts with "by",
followed by a sequence of the tactics above. Do not write proof
terms by hand, e.g. no "fun p => ...", no anonymous constructors
"⟨p, q⟩", no "And.intro", "Or.inl", "h.1", "h.mp" etc., and no
"match". The argument of "exact" (and "apply") should just be the
name of a hypothesis or lemma, possibly applied to other hypotheses
(e.g. "exact p" or "exact pq p"). Proofs that do not follow these
rules will not get any marks.

You can use auxilliary theorems (lemmas) which you need to prove
as well. Indeed this is good practice where appropriate.

Please submit your solution on moodle before the deadline. There will also be an inclass quiz in the lab related to the exercise which counts for 30% of the marks.

-/
namespace proofs

variable (P Q R : Prop)

/- --- Do not add/change anything above this line --- -/

theorem q01 : (P → P → Q) → (P → Q) := by
  sorry

theorem q02 : (P → Q) → (P → P → Q) := by
  sorry

theorem q03 : (P → P → Q) ↔ (P → Q) := by
  sorry

theorem q04 : P ∧ True ↔ P := by
  sorry

theorem q05 : (P ∧ Q) ∧ R ↔ P ∧ (Q ∧ R) := by
  sorry

theorem q06 : P ∨ False ↔ P := by
  sorry

theorem q07 : (P ∨ Q) ∨ R ↔ P ∨ (Q ∨ R) := by
  sorry

theorem q08 : (P ↔ Q) ↔ (Q ↔ P) := by
  sorry

theorem q09 : (P ↔ Q) → ((P → R) ↔ (Q → R)) := by
  sorry

theorem q10 : (P ∨ Q ↔ P ∧ Q) ↔ (P ↔ Q) := by
  sorry

/- --- Do not add/change anything below this line --- -/
end proofs
