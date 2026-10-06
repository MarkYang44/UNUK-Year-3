/-
Lecture 3 : Propositional Logic

-/

variable {P Q R : Prop}


theorem C : (P → Q) → ((Q → R) → (P → R)) := by
  intro pq
  intro qr
  intro p
  apply qr
  apply pq
  assumption


theorem swap : (P → Q → R) → (Q → P → R) := by
  intro pqr q p
  apply pqr
  · assumption
  · assumption


-- ∧ (conjunction)

example : P → Q → P ∧ Q := by
  intro p q
  constructor
  · assumption
  · assumption

example : P ∧ Q → P := by
  intro pq
  cases pq with
  | intro p q => assumption


theorem curry: (P → Q → R) ↔ (P ∧ Q → R) := by
  constructor
  · intro pqr pq
    cases pq with
    | intro p q =>
      exact pqr p q
  · intro pqr p q
    exact pqr ⟨p, q⟩

    /-
    apply pqr
    · cases pq with
      | intro p q =>
        assumption
    · cases pq with
      | intro p q =>
        assumption
     -/


theorem curry2 : (P → Q → R) ↔ (P ∧ Q → R) := by
  constructor
  · intro pqr pq
    cases pq with
    | intro p q =>
      apply pqr
      assumption
      assumption
  · intro pqr p q
    apply pqr
    constructor
    · assumption
    · assumption


example : P → P ∨ Q := by
  intro p
  left
  assumption


example : (P → R) → (Q → R) → (P ∨ Q → R) := by
  intro pr qr pq
  cases pq with
  | inl p =>
      apply pr
      assumption
  | inr q =>
      apply qr
      assumption


example : (P → R) ∧ (Q → R) ↔ P ∨ Q → R := by
  constructor
  · intro prqr pq
    cases prqr with
    | intro pr qr =>
      cases pq with
      | inl p =>
        apply pr
        assumption
      | inr q =>
        apply qr
        assumption
  · intro pqr
    constructor
    · intro p
      apply pqr
      left
      assumption
    · intro q
      apply pqr
      right
      assumption


example : (P ∧ (Q ∨ R)) ↔ (P ∧ Q) ∨ (P ∧ R) := by
  constructor
  · intro pqr
    cases pqr with
    | intro p qr =>
      cases qr with
      | inl q =>
        left
        constructor
        · assumption
        · assumption
      | inr r =>
        right
        constructor
        · assumption
        · assumption
  · intro pqpr
    cases pqpr with
    | inl pq =>
      cases pq with
      | intro p q =>
        constructor
        · assumption
        · left
          assumption
    | inr pr =>
      cases pr with
      | intro p r =>
        constructor
        · assumption
        · right
          assumption


example : True :=by
  constructor

-- ex falso quod libet
-- from false everything follows
example : False → P := by
  intro f
  cases f
