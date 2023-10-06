
/* Analyseur syntaxique pour Arith */

%{
  open Ast
%}

%token <int> CST
%token <string> IDENT
%token SET, LET, IN, PRINT
%token EOF
%token LP RP
%token PLUS MINUS TIMES DIV
%token EQ

/* Définitions des priorités et associativités des tokens */

%nonassoc IN
%left PLUS MINUS
%left TIMES DIV
%nonassoc uminus

/* Point d'entrée de la grammaire */
%start prog

/* Type des valeurs retournées par l'analyseur syntaxique */
%type <Ast.program> prog

%%

prog:
| p = stmts EOF { List.rev p }
;

stmts:
| i = stmt           { [i] }
| l = stmts i = stmt { i :: l }
;

stmt:
| SET id = IDENT EQ e = expr { Set (id, e) }
| PRINT e = expr             { Print e }
;

expr:
| c = CST                        { Cst c }
| id = IDENT                     { Var id }
| e1 = expr o = op e2 = expr     { Binop (o, e1, e2) }
| MINUS e = expr %prec uminus    { Binop (Sub, Cst 0, e) }
| LET id = IDENT EQ e1 = expr IN e2 = expr
                                 { Letin (id, e1, e2) }
| LP e = expr RP                 { e }
;

%inline op:
| PLUS  { Add }
| MINUS { Sub }
| TIMES { Mul }
| DIV   { Div }
;



