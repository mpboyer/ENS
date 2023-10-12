
exception VarUndef of string
  (** exception levée pour signaler une variable non déclarée *)

val compile_program : Ast.program -> string -> unit
  (** [compile_program p f] compile le programme [p] et écrit le code X86-64
      correspondant dans le fichier [f] *)

