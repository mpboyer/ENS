
(* Syntaxe abstraite pour le langage Arith *)

type program = stmt list

and stmt =
  | Set of string * expr
  | Print of expr

and expr =
  | Cst of int
  | Var of string
  | Binop of binop * expr * expr
  | Letin of string * expr * expr

and binop = Add | Sub | Mul | Div

