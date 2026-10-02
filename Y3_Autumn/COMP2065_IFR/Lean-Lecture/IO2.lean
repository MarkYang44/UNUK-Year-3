/-

Lean: interative proof system

Lecture 2: Propositional Logic in Lean

Proposition: intuitionistic, a statement for which we can have evidence

-/

variable {P Q R : Prop}
-- P = the sun shines
-- Q = we got to the zoo
-- R = the children are happy

-- connectives: and, or, implies, not, iff

-- primitive connectives
#check P ∧ Q -- \and
#check P → Q -- \to
#check P ∨ Q -- \or
#check True  -- \true
#check False -- \false

-- defined connectives
#check ¬ P   -- \neg
#check P ↔ Q -- \iff (P → Q) ∧ (Q → P)

-- precidence (see the tree)
#check P ∧ Q → P ∨ R -- \and has higher precedence than \or and \to
#check P ∧ Q ∨ R     -- \and has higher precedence than \or

-- what is evidence: proofs

-- tautology: a proposition which holds for all
-- assignments of propositions to the atoms (P,Q,R)

-- if the sun shines, the sun shines
theorem I : P → P := by -- (:= by): start proof
  intro x
  -- exact x
  assumption

/-
If (if the sun shines we go to the zoo)
then if (if we go to the zoo then the children are happy)
     then if the sun shines then the children are happy
-/

theorem C : (P → Q) → ((Q → R) → (P → R)) := by
  intro h1 h2 h3
  apply h2
  apply h1
  exact h3

theorem D :(P → Q) → ((Q → R) → (P → R)) := by
  intro pq
  intro qr
  intro p
  apply qr
  apply pq
  assumption

#print I
#print C
#print D

-- proofs are functional programs
