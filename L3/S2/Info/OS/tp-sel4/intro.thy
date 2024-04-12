theory intro
imports AutoCorres.AutoCorres
begin

(***
  Equivalents to some of the terms from Xavier Rival's lecture on Coq: slides 6--7.
  http://www.di.ens.fr/~rival/semverif-2018/sem-04-coq.pdf
 ***)

term "0"
term "1"
term "True"
typ nat
typ bool
term "\<lambda>(n::nat). n + 1"
value "(\<lambda>(n::nat). n + 1) 8"
term "\<exists>p::nat. 8 = 2 * p"
term "\<And>a b. a \<and> b \<Longrightarrow> a"
term "\<forall>a b. a \<and> b \<longrightarrow> a"

definition myzero :: nat
where
 "myzero \<equiv> 0"

definition myone :: nat
where
 "myone \<equiv> Suc 0"

fun myincr :: "nat \<Rightarrow> nat"
where
  "myincr n = n + 1"
print_theorems
thm myincr.simps (* automatically generated rewrite rules *)

(***
  Some simple proofs
 ***)

(* To type "\<and>", type "/" and then "\". *)
(* Similarly, "-->" gives "\<longrightarrow>", and "==>" gives "\<Longrightarrow>". *)
(* Alternatively, type (part of) the name in latex (<backslash> Longrightarrow...). *) 
lemma "(a \<and> b) \<longrightarrow> (b \<and> a)"
  find_theorems intro
  apply (rule impI)
  find_theorems elim
  apply (erule conjE)
  apply (rule conjI)
   apply assumption
  apply assumption
  done

(* You can Ctrl-click on rules and symbols to jump to their definitions. *)
(* Pressing Ctrl-` jumps back to the previous file. *)

lemma "(a \<and> b) \<longrightarrow> (a \<and> b)"
  apply simp (* Apply rewriting rules: LHS = RHS. *)
  done

lemma "(a \<and> b) \<longrightarrow> (a \<and> b)"
  apply clarsimp (* Safely apply rewriting rules and intro/elim/dest rules. *)
  done

lemma "(a \<and> b) \<longrightarrow> (a \<and> b)"
  apply auto (* Try lots of stuff... sometimes gives a mess. *)
  done

lemma "(a \<and> b) \<longrightarrow> (b \<and> a)"
  sledgehammer
  oops (* give up on proof *)

(* Type "[" then "|" for "\<lbrakk>". *)
lemma "\<lbrakk> a; b \<rbrakk> \<Longrightarrow> b \<and> a"
  sorry (* cheat *)

lemma "myincr myzero = myone"
  apply clarsimp (* apply myincr.simps *)
  unfolding myzero_def myone_def
  apply (rule refl)
  done

(***
  Equivalents to some of the Hoare rules in Jérôme Feret's lecture on 
  Axiomatic semantics: slides 13--23
  http://www.di.ens.fr/~rival/semverif-2018/sem-07-axiomatic.pdf
 ***)

find_theorems "\<lbrace>_\<rbrace> _ \<lbrace>_\<rbrace>!"
thm skip_nf            (* axiom for skip *)
thm validNF_return     (* like rule of assignment *)
thm validNF_weaken_pre (* like rule of consequence *)
thm validNF_if_split   (* Tests *)
thm validNF_bind       (* Sequences *)
thm validNF_whileLoop  (* loops *)

lemma "\<lbrace>\<lambda>s. True\<rbrace> do i \<leftarrow> return 2; return (i + 3) od \<lbrace>\<lambda>r s. r = 5 \<rbrace>!"
  apply (rule validNF_bind)
   apply (rule validNF_return)
  apply (rule validNF_weaken_pre)
  apply (rule validNF_return)
  apply simp
  done
(* try: apply wp
   to activate the Verification Condition Generator / Weakest Precondition Calculator *)

end

