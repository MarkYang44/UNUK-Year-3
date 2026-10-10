/-

Lecture 04: Propositional Logic

-/

variable (P Q R : Prop)

theorem distr : P ∧ (Q ∨ R) ↔ P ∧ Q ∨ P ∧ R := by
  constructor
  · intro p_qr
    cases p_qr with
    | intro p qr =>
      cases qr with
      | inl q =>
        left
        constructor
        · exact p
        · exact q
      | inr r =>
        right
        constructor
        · exact p
        · exact r
  · intro pq_pr
    cases pq_pr with
    | inl pq =>
        cases pq with
        | intro p q =>
          constructor
          · exact p
          · left
            exact q
    | inr pr =>
        cases pr with
        | intro p r =>
          constructor
          · exact p
          · right
            exact r


-- ex falso quod libet（爆炸原理）
-- from false follows anything
theorem efq : False → P := by
  intro pcf
  cases pcf


theorem rain : True := by
  constructor


theorem aux : Q ∨ Q → Q := by
  intro q
  cases q with
  | inl q1 => exact q1
  | inr q2 => exact q2


example : (P → Q ∨ Q) → (P → Q) := by
  intro p_qq p
  apply aux
  apply p_qq
  assumption


-- we inroduce a new lemma (aux)
-- alternative is o use have
example : (P → Q ∨ Q) → (P → Q) := by
  intro p_qq p
  have qq : Q ∨ Q := by
    apply p_qq
    exact p
  cases qq with
  | inl q1 => exact q1
  | inr q2 => exact q2


-- a cut

-- de Morgan
-- npq : (P ∨ Q) → False
theorem dm1 : ¬ (P ∨ Q) ↔ ¬ P ∧ ¬ Q := by
  constructor
  · intro npq
    constructor
    · intro p
      apply npq
      left
      exact p
    · intro q
      apply npq
      right
      exact q
  · intro np_nq
    cases np_nq with
    |intro np nq =>
      intro pq
      cases pq with
      |inl p =>
        apply np
        exact p
      |inr q =>
        apply nq
        exact q

theorem dm2 : ¬ (P ∧ Q) ↔ ¬ P ∨ ¬ Q := by
  constructor
  · intro npq
    by_cases p : P
    · right
      intro q
      apply npq
      constructor
      · exact p
      · exact q
    · left
      exact p
  · intro np_nq
    cases np_nq with
    | inl np =>
      intro pq
      cases pq with
      | intro p q =>
        apply np
        exact p
    | inr nq =>
      intro pq
      cases pq with
      | intro p q =>
        apply nq
        exact q
