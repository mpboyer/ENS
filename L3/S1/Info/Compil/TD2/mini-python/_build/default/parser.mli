
(* The type of tokens. *)

type token = 
  | TIMES
  | RSQ
  | RP
  | RETURN
  | PRINT
  | PLUS
  | OR
  | NOT
  | NEWLINE
  | MOD
  | MINUS
  | LSQ
  | LP
  | IN
  | IF
  | IDENT of (string)
  | FOR
  | EQUAL
  | EOF
  | END
  | ELSE
  | DIV
  | DEF
  | CST of (Ast.constant)
  | COMMA
  | COLON
  | CMP of (Ast.binop)
  | BEGIN
  | AND

(* This exception is raised by the monolithic API functions. *)

exception Error

(* The monolithic API. *)

val file: (Lexing.lexbuf -> token) -> Lexing.lexbuf -> (Ast.file)
