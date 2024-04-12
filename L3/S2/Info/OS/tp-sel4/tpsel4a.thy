theory tpsel4a
imports AutoCorres.AutoCorres "~~/src/HOL/Number_Theory/Number_Theory"
begin

(* Parse the C file into the SIMPL language. *)
install_C_file "tpsel4a.c"

context tpsel4a begin

thm is_prime_impl       (* The specification \<Gamma> maps names to program terms. *)
thm is_prime_body_def   (* This is the SIMPL model of the imported C function. *)

end

(* Abstract the SIMPL model into a monadic model. *)
autocorres[ts_rules = nondet, unsigned_word_abs = is_prime is_prime] "tpsel4a.c"
print_theorems

context tpsel4a begin

thm is_prime'_def       (* This is the monadic model of the C function. *)
thm is_prime'_ac_corres (* This lemma relates monadic and SIMP models. *)

(* Loop invariant for "is_prime". *)
definition
  is_prime_inv :: "nat \<Rightarrow> nat \<Rightarrow> bool"
where
 "\<forall>j < i, \<lbrakk>j \<ge> 2\<rbrakk> \<Longrightarrow> n mod j \<noteq> 0"

(* The loop invariant holds coming into the loop. *)
lemma is_prime_precond_implies_inv:
  "\<lbrakk> 2 \<le> n; n \<le> UINT_MAX \<rbrakk> \<Longrightarrow> is_prime_inv 2 n"
  sorry (*** Q2. TODO ***)

(* The loop invariant holds for each loop iteration. *)
lemma is_prime_body_obeys_inv:
  "\<lbrakk> is_prime_inv i n; n mod i \<noteq> 0 \<rbrakk> \<Longrightarrow> is_prime_inv (i + 1) n"
  sorry (*** Q3. TODO ***)

find_theorems "prime (_::nat) = _"
thm prime_nat_iff'

find_theorems "_ dvd _" "_ mod _"
thm dvd_eq_mod_eq_0[symmetric]

(* Q4. The loop invariant implies the post-condition. *)
lemma is_prime_inv_implies_postcondition:
  "\<lbrakk> is_prime_inv i n; n mod i = 0 \<rbrakk> \<Longrightarrow> (i = n) \<longleftrightarrow> prime n"
  sorry (*** TODO ***)

(* Measure function for "is_prime". Must be strictly decreasing
 * for each loop iteration. *)
definition
  is_prime_measure :: "nat \<Rightarrow> nat \<Rightarrow> nat"
where
  "is_prime_measure i n \<equiv> 0" (*** Q5. TODO ***)

(* The loop measure decrements each loop iteration. *)
lemma is_prime_body_obeys_measure:
  "\<lbrakk> is_prime_inv i n; n mod i \<noteq> 0 \<rbrakk>
      \<Longrightarrow> is_prime_measure i n > is_prime_measure (i + 1) n"
  sorry (*** Q6. TODO ***)

(*
 * Show that "is_prime' n" is correct.
 *
 * AutoCorres has applied "word abstraction" to this function,
 * meaning that you are able to reason using "nats" instead of
 * "word32" data types, at the price of having to reason that
 * your values do not overflow UINT_MAX.
 *)
lemma is_prime_correct:
  "\<lbrace>\<lambda>s. n \<le> UINT_MAX \<rbrace> is_prime'is_prime' n \<lbrace>\<lambda>r s. r = (if prime n then 1 else 0) \<rbrace>!"
  (* Move the precondition into the assumptions. *)
  apply (rule validNF_assume_pre)
  (* Unfold the program body. *)
  apply (unfold is_prime'_def)

  (* Annotate the loop with an invariant and measure. *)
  apply (subst whileLoop_add_inv [
      where I="\<lambda>r s. is_prime_inv r n"
      and M="(\<lambda>(r, s). Suc n - r)"])

  (*
   * Run "wp" to generate verification conditions.
   *
   * The resulting subgoals are:
   *    1. The loop body obeys the invariant;
   *    2. The loop body causes the measure to decrease;
   *    3. The loop counter never exceeds UINT_MAX.
   *    4. The invariant is equivalent to the post-condition of the function; and
   *    5. Exiting early (when n < 2) implies the post-condition.
   *)
  apply (wp, intro conjI)
  sorry (*** Q7. TODO ***)

end

end
