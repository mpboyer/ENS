theory tpsel4b
imports AutoCorres.AutoCorres "~~/src/HOL/Number_Theory/Number_Theory"
begin

(* Parse the C file into SIMPL. *)
install_C_file "tpsel4a.c"

(* Note: The autocorres tool is not applied.
         Here we reason on the SIMPL model directly *)

context tpsel4a begin

thm is_prime_impl       (* The specification \<Gamma> maps names to program terms. *)
thm is_prime_body_def   (* This is the SIMPL model of the imported C function. *)

term "unat"
(* with associated tactic: apply unat_arith *)

(* Loop invariant for "is_prime". *)
definition
  is_prime_inv :: "word32 \<Rightarrow> word32 \<Rightarrow> word32 \<Rightarrow> bool"
where
  "is_prime_inv i init_n curr_n \<equiv> True" (*** TODO ***)

(* Measure function for "is_prime". Must be strictly decreasing
 * for each loop iteration. *)
definition
  is_prime_measure :: "word32 \<Rightarrow> word32 \<Rightarrow> word32 \<Rightarrow> nat"
where
  "is_prime_measure i init_n curr_n \<equiv> 0" (*** TODO ***)

(* The loop invariant holds coming into the loop. *)
lemma is_prime_precond_implies_inv:
  "True"
  sorry (*** TODO ***)

(* The loop invariant holds for each loop iteration. *)
lemma is_prime_body_obeys_inv:
  "True"
  sorry (*** TODO ***)

(* The loop measure decrements each loop iteration. *)
lemma is_prime_body_obeys_measure:
  "\<lbrakk> is_prime_inv i init_n curr_n; curr_n mod i \<noteq> 0 \<rbrakk>
      \<Longrightarrow> is_prime_measure i init_n curr_n > is_prime_measure (i + 1) init_n curr_n"
  sorry (*** TODO ***)

(* The loop invariant implies the post-condition. *)
lemma is_prime_inv_implies_postcondition:
  "True"
  sorry (*** TODO ***)

(*
 * Show that "is_prime' n" is correct.
 *
 * Note that there are two ways of writing variables: \<acute>n and
 * (n_' s). The first fetches the value "n" from an implicitly
 * specified state, while the second fetches the value "n" from state
 * "s". While less pretty, it is generally easier to use the latter.
 *)
lemma is_prime_correct:
   "\<Gamma> \<turnstile>\<^sub>t {s. n_' s = n }
          \<acute>ret__unsigned :== PROC is_prime(n)
        {t. ret__unsigned_' t = (if prime (unat n) then 1 else 0) }"
  (* Unfold the program's body. *)
  apply (hoare_rule HoareTotal.ProcNoRec1)
  apply (unfold creturn_def)

  (* Annotate the loop with an invariant and measure. *)
  apply (subst whileAnno_def)
  apply (subst whileAnno_def [symmetric, where
       I="{s. is_prime_inv (i_' s) n (n_' s) }" and
       V="measure (\<lambda>s. is_prime_measure (i_' s) n (n_' s))"])

  (*
   * Run the VCG.
   *
   * You will need to prove (i) the function's precondition implies your
   * loop's invariant; (ii) the loop invariant holds each time the loop
   * executes; (iii) the measure decreases each time the loop exceutes;
   * and (iv) when the loop has finished, the loop invariant implies the
   * functions post-condition.
   *
   * Spend some time looking at the vcg's output to make sure you know
   * what the goals it is leaving you correspond to.
   *)
  apply vcg

  (* Finish the proof. *)
  sorry (*** TODO ***)

end

end

