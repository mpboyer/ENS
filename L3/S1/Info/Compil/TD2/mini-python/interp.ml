
open Ast
open Format

(* Exception levée pour signaler une erreur pendant l'interprétation *)
exception Error of string
let error s = raise (Error s)

(* Les valeurs de Mini-Python

   - une différence notable avec Python : on
     utilise ici le type int alors que les entiers de Python sont de
     précision arbitraire ; on pourrait utiliser le module Big_int d'OCaml
     mais on choisit ici la facilité
   - ce que Python appelle une liste est en réalité un tableau
     redimensionnable ; dans le fragment considéré ici, il n'y a pas
     de possibilité d'en modifier la longueur, donc un simple tableau OCaml
     convient *)
type value =
  | Vnone
  | Vbool of bool
  | Vint of int
  | Vstring of string
  | Vlist of value array

(* Affichage d'une valeur sur la sortie standard *)
let rec print_value = function
  | Vnone -> printf "None"
  | Vbool true -> printf "True"
  | Vbool false -> printf "False"
  | Vint n -> printf "%d" n
  | Vstring s -> printf "%s" s
  | Vlist a ->
    let n = Array.length a in
    printf "[";
    for i = 0 to n-1 do print_value a.(i); if i < n-1 then printf ", " done;
    printf "]"

(* Interprétation booléenne d'une valeur

   En Python, toute valeur peut être utilisée comme un booléen : None,
   la liste vide, la chaîne vide et l'entier 0 sont considérés comme
   False et toute autre valeurs comme True *)

let is_false = function 
    | Vnone | Vbool false | Vstring "" |Vlist [||] -> true
    | Vint n -> n = 0
    | _ -> false

let is_true (v: value) = not (is_false v)

(* Les fonctions sont ici uniquement globales *)

let functions = (Hashtbl.create 16 : (string, ident list * stmt) Hashtbl.t)

(* L'instruction 'return' de Python est interprétée à l'aide d'une exception *)

exception Return of value

(* Les variables locales (paramètres de fonctions et variables introduites
   par des affectations) sont stockées dans une table de hachage passée en
   arguments aux fonctions suivantes sous le nom 'ctx' *)

type ctx = (string, value) Hashtbl.t

(* Interprétation d'une expression (renvoie une valeur) *)

let rec compare_list a1 n1 a2 n2 i =
  if i = n1 && i = n2 then 0
  else if i = n1 then -1
  else if i = n2 then 1
  else let c = compare_value a1.(i) a2.(i) in
       if c <> 0 then c else compare_list a1 n1 a2 n2 (i + 1)

and compare_value v1 v2 = match v1, v2 with
  | Vlist a1, Vlist a2 ->
    compare_list a1 (Array.length a1) a2 (Array.length a2) 0
  | Vbool b1, Vint _ -> compare_value (Vint (if b1 then 1 else 0)) v2
  | Vint _, Vbool b2 -> compare_value v1 (Vint (if b2 then 1 else 0))
  | _ -> compare v1 v2


let rec expr (ctx: ctx) = function
  | Ecst Cnone ->
      Vnone
  | Ecst (Cstring s) ->
      Vstring s
  (* arithmétique *)
  | Ecst (Cint n) ->
      Vint n
  | Ebinop (Badd | Bsub | Bmul | Bdiv | Bmod |
            Beq | Bneq | Blt | Ble | Bgt | Bge as op, e1, e2) ->
      let v1 = expr ctx e1 in
      let v2 = expr ctx e2 in
      begin match op, v1, v2 with
        | Badd, Vint n1, Vint n2 -> Vint (n1 + n2)
        | Bsub, Vint n1, Vint n2 -> Vint (n1 - n2)
        | Bmul, Vint n1, Vint n2 -> Vint (n1 * n2)
        | Bdiv, Vint n1, Vint n2 -> begin match n2 with
                | 0 -> error "division by zero"
                | _ -> Vint (n1/n2)
            end 
        | Bmod, Vint n1, Vint n2 -> 
            begin match n2 with
            | 0 -> error "division by zero"
            | _ -> Vint (n1 mod n2)
        end
        | Beq, _, _  -> Vbool (compare_value v1 v2 = 0)
        | Bneq, _, _ -> Vbool (compare_value v1 v2 <> 0)
        | Blt, _, _  -> Vbool (compare_value v1 v2 < 0)
        | Ble, _, _  -> Vbool (compare_value v1 v2 <= 0)
        | Bgt, _, _  -> Vbool (compare_value v1 v2 > 0)
        | Bge, _, _  -> Vbool (compare_value v1 v2 >= 0)
        | Badd, Vstring s1, Vstring s2 ->
            Vstring (s1 ^ s2)
        | Badd, Vlist l1, Vlist l2 ->
            assert false (* à compléter (question 5) *)
        | _ -> error "unsupported operand types"
      end
  | Eunop (Uneg, e1) ->
      begin match expr ctx e1 with 
        | Vint(n) -> Vint (-n)
        | _ -> error "unsupported operand types" 
  end
  (* booléens *)
  | Ecst (Cbool b) ->
      Vbool(b)
  | Ebinop (Band, e1, e2) ->
      let v1 = expr ctx e1 in
      if is_true v1 then expr ctx e2 else v1
  | Ebinop (Bor, e1, e2) ->
    let v1 = expr ctx e1 in
    if is_false v1 then expr ctx e2 else v1
  | Eunop (Unot, e1) ->
      Vbool (is_false (expr ctx e1))
  | Eident id ->
    if not (Hashtbl.mem ctx id) then error ("unbound variable " ^ id) ;
    Hashtbl.find ctx id
  (* appel de fonction *)
  | Ecall ("len", [e1]) ->
      begin match expr ctx e1 with
        |Vstring s -> Vint (String.length s)
        |Vlist l -> Vint (Array.length l)
        | _ -> error ("unsupported operand type")
  end
  | Ecall ("list", [Ecall ("range", [e1])]) ->
    begin match expr ctx e1 with
    | Vint n -> Vlist (Array.init (max 0 n) (fun i -> Vint i))
    | _ -> error "integer expected"
  end
  | Ecall (f, el) ->
      if not (Hashtbl.mem functions f) then error ("unbound function " ^ f);
      let args, body = Hashtbl.find functions f in
      if List.length args <> List.length el then error ("bar arity");
      let ctx_ = Hashtbl.create 16 in 
      List.iter2 (fun x e -> Hashtbl.add ctx_ x (expr ctx e)) args el;
      begin try stmt ctx_ body; Vnone with Return v -> v end
  | Elist el ->
      Vlist (Array.of_list (List.map (expr ctx) el))
  | Eget (e1, e2) ->
      begin match expr ctx e1 with
        | Vlist l -> 
            begin match expr ctx e2 with
                | Vint n -> (try l.(n) with Invalid_argument _ -> error "oob")
                | _ -> error "integer expected"
            end 
        | _ -> error "list expected"
        end

(* interprétation d'une instruction ; ne renvoie rien *)

and stmt (ctx: ctx) = function
  | Seval e ->
      ignore (expr ctx e)
  | Sprint e ->
      print_value (expr ctx e); printf "@."
  | Sblock bl ->
      block ctx bl
  | Sif (e, s1, s2) ->
      let v = expr ctx e in
      if is_true v then stmt ctx s1 else stmt ctx s2
  | Sassign (id, e1) ->
      Hashtbl.replace ctx id (expr ctx e1)
  | Sreturn e ->
      raise (Return (expr ctx e))
  | Sfor (x, e, s) ->
      begin match expr ctx e with 
        | Vlist l -> Array.iter (fun v -> Hashtbl.replace ctx x v; stmt ctx s) l
        | _ -> error "list expected"
  end
  | Sset (e1, e2, e3) ->
    begin match expr ctx e1 with
    | Vlist l -> begin match expr ctx e2 with
    | Vint n -> (try l.(n) <- expr ctx e3 with Invalid_argument _ -> error "oob")
    | _ -> error "integer expected"
end 
    | _ -> error "list expected" end

(* interprétation d'un bloc i.e. d'une séquence d'instructions *)

and block (ctx: ctx) = function
  | [] -> ()
  | s :: sl -> stmt ctx s; block ctx sl

(* interprétation d'un fichier
   - dl est une liste de définitions de fonction (cf Ast.def)
   - s est une instruction, qui représente les instructions globales
 *)

let file ((dl: def list), (s: stmt)) =
  List.iter (fun (f, args, body) -> Hashtbl.add functions f (args, body)) dl;
  stmt (Hashtbl.create 16) s




