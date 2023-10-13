
(* Production de code pour le langage Arith *)

open Format
open X86_64
open Ast

(* Exception à lever quand une variable (locale ou globale) est mal utilisée *)
exception VarUndef of string

(* Taille de la frame, en octets (chaque variable locale occupe 8 octets) *)
let frame_size = ref 0

(* Les variables globales sont stockées dans une table de hachage *)
let (genv : (string, unit) Hashtbl.t) = Hashtbl.create 17

(* On utilise une table d'association dont les clés sont les variables locales
   (des chaînes de caractères) et où la valeur associée est la position
   par rapport à %rbp (en octets) *)
module StrMap = Map.Make(String)

(* Compilation d'une expression *)
let compile_expr =
  (* Fonction récursive locale à compile_expr utilisée pour générer le code
     machine de l'arbre de syntaxe abstraite associé à une valeur de type
     Ast.expr ; à l'issue de l'exécution de ce code, la valeur doit se trouver
     en sommet de pile *)
  let rec comprec env next = function
    | Cst i ->
        movq (imm i) !%rax ++
        pushq !%rax
    | Var x ->
        begin
          try 
            let ofs = - (StrMap.find x env) in
              movq (ind ~ofs rbp) !%rax ++
              pushq !%rax
          with Not_found -> 
            if not (Hashtbl.mem genv x) then raise (VarUndef x);
            movq (lab x) !%rax ++
            pushq !%rax
        end
    | Binop (op, e1, e2)->
        comprec env next e1 ++
        comprec enx next e2 ++
        popq !%rbx ++
        popq !%rax ++
        op !%rbx !%rax ++
        pushq !%rax

    
    | Letin (x, e1, e2) ->
        if !frame_size = next then frame_size := 8 + !frame_size;
        nop (* À COMPLÉTER *)
  in
  comprec StrMap.empty 0

(* Compilation d'une instruction *)
let compile_instr = function
  | Set (x, e) ->
      nop (* À COMPLÉTER *)
  | Print e ->
      nop (* À COMPLÉTER *)


(* Compile le programme p et enregistre le code dans le fichier ofile *)
let compile_program p ofile =
  let code = List.map compile_instr p in
  let code = List.fold_right (++) code nop in
  if !frame_size mod 16 = 8 then frame_size := 8 + !frame_size;
  let p =
    { text =
        globl "main" ++ label "main" ++
        nop (* À COMPLÉTER *) ++
        code ++
        nop (* À COMPLÉTER *) ++
        label "print_int" ++
        pushq !%rbp ++ (* assure notamment l'alignement *)
        movq !%rdi !%rsi ++
        leaq (lab ".Sprint_int") rdi ++
        movq (imm 0) !%rax ++
        call "printf" ++
        popq rbp ++
        ret;
      data =
        Hashtbl.fold (fun x _ l -> label x ++ dquad [1] ++ l) genv
          (label ".Sprint_int" ++ string "%d\n")
    }
  in
  let f = open_out ofile in
  let fmt = formatter_of_out_channel f in
  X86_64.print_program fmt p;
  (* on "flush" le buffer afin de s'assurer que tout y a été écrit
     avant de le fermer *)
  fprintf fmt "@?";
  close_out f
