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
  intro ppq p
  exact ppq p p

theorem q02 : (P → Q) → (P → P → Q) := by
  intro pq p p2
  exact pq p

theorem q03 : (P → P → Q) ↔ (P → Q) := by
  constructor
  · exact q01 P Q
  · exact q02 P Q

theorem q04 : P ∧ True ↔ P := by
  constructor
  · intro pt
    cases pt with
    | intro p t =>
      exact p
  · intro p
    constructor
    · exact p
    · constructor

theorem q05 : (P ∧ Q) ∧ R ↔ P ∧ (Q ∧ R) := by
  constructor
  · intro pqr
    cases pqr with
    | intro pq r =>
      cases pq with
      | intro p q =>
        constructor
        · exact p
        · constructor
          · exact q
          · exact r
  · intro pqr
    cases pqr with
    | intro p qr =>
      cases qr with
      | intro q r =>
        constructor
        · constructor
          · exact p
          · exact q
        · exact r

theorem q06 : P ∨ False ↔ P := by
  constructor
  · intro pf
    cases pf with
    | inl p =>
      exact p
    | inr f =>
      cases f
  · intro p
    left
    exact p

theorem q07 : (P ∨ Q) ∨ R ↔ P ∨ (Q ∨ R) := by
  constructor
  · intro pqr
    cases pqr with
    | inl pq =>
      cases pq with
      | inl p =>
        left
        exact p
      | inr q =>
        right
        left
        exact q
    | inr r =>
      right
      right
      exact r
  · intro pqr
    cases pqr with
    | inl p =>
      left
      left
      exact p
    | inr qr =>
      cases qr with
      | inl q =>
        left
        right
        exact q
      | inr r =>
        right
        exact r

theorem q08 : (P ↔ Q) ↔ (Q ↔ P) := by
  constructor
  · intro pq
    cases pq with
    | intro pq qp =>
      constructor
      · exact qp
      · exact pq
  · intro qp
    cases qp with
    | intro qp pq =>
      constructor
      · exact pq
      · exact qp

theorem q09 : (P ↔ Q) → ((P → R) ↔ (Q → R)) := by
  intro pq
  cases pq with
  | intro pq qp =>
    constructor
    · intro pr q
      apply pr
      exact qp q
    · intro qr p
      apply qr
      exact pq p

theorem q10 : (P ∨ Q ↔ P ∧ Q) ↔ (P ↔ Q) := by
  constructor
  · intro h
    cases h with
    | intro forward backward =>
      constructor
      · intro p
        have pq : P ∧ Q := by
          apply forward
          left
          exact p
        cases pq with
        | intro p q =>
          exact q
      · intro q
        have pq : P ∧ Q := by
          apply forward
          right
          exact q
        cases pq with
        | intro p q =>
          exact p
  · intro h
    cases h with
    | intro pq qp =>
      constructor
      · intro porq
        cases porq with
        | inl p =>
          constructor
          · exact p
          · exact pq p
        | inr q =>
          constructor
          · exact qp q
          · exact q
      · intro pandq
        cases pandq with
        | intro p q =>
          left
          exact p

/- --- Do not add/change anything below this line --- -/
end proofs
