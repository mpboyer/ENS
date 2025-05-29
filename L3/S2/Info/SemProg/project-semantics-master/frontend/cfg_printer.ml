(*
  Cours "Sémantique et Application à la Vérification de programmes"

  Ecole normale supérieure, Paris, France / CNRS / INRIA
*)

(*
   Pretty-printer for control-flow graphs.
 *)



open Lexing
open Abstract_syntax_tree
open Cfg



(* locations *)
(* ********* *)

let pp_pos fmt p =
  let file = p.pos_fname in
  let line = p.pos_lnum in
	Format.fprintf fmt "File \"%s\", line %d" file line

let string_of_position p =
  Format.sprintf "%s:%i:%i" p.pos_fname p.pos_lnum (p.pos_cnum - p.pos_bol)

let string_of_extent (p,q) =
  if p.pos_fname = q.pos_fname then
    if p.pos_lnum = q.pos_lnum then
      if p.pos_cnum = q.pos_cnum then
        Format.sprintf "%s:%i.%i" p.pos_fname p.pos_lnum (p.pos_cnum - p.pos_bol)
      else
        Format.sprintf "%s:%i.%i-%i" p.pos_fname p.pos_lnum (p.pos_cnum - p.pos_bol) (q.pos_cnum - q.pos_bol)
    else
      Format.sprintf "%s:%i.%i-%i.%i" p.pos_fname p.pos_lnum (p.pos_cnum - p.pos_bol) q.pos_lnum (q.pos_cnum - q.pos_bol)
  else
    Format.sprintf "%s:%i.%i-%s:%i.%i" p.pos_fname p.pos_lnum (p.pos_cnum - p.pos_bol) q.pos_fname q.pos_lnum (q.pos_cnum - q.pos_bol)



(* operators *)
(* ********* *)

let string_of_int_unary_op = function
  | AST_UNARY_PLUS -> "+"
  | AST_UNARY_MINUS -> "-"

let string_of_bool_unary_op = function
  | AST_NOT -> "!"

let string_of_int_binary_op = function
  | AST_MULTIPLY -> "*"
  | AST_DIVIDE -> "/"
  | AST_MODULO -> "%"
  | AST_PLUS -> "+"
  | AST_MINUS -> "-"

let string_of_compare_op = function
  | AST_EQUAL -> "=="
  | AST_NOT_EQUAL -> "!="
  | AST_LESS -> "<"
  | AST_LESS_EQUAL -> "<="
  | AST_GREATER -> ">"
  | AST_GREATER_EQUAL -> ">="

let string_of_bool_binary_op = function
  | AST_AND -> "&&"
  | AST_OR -> "||"



let int_expr_precedence = function
  | CFG_int_unary (_, _) -> 99
  | CFG_int_binary ((AST_MULTIPLY | AST_DIVIDE | AST_MODULO), _, _) -> 6
  | CFG_int_binary ((AST_PLUS | AST_MINUS), _, _) -> 5
  | _ -> 100

let bool_expr_precedence = function
  | CFG_compare (_,_,_) -> 3
  | CFG_bool_binary (AST_AND,_,_) -> 2
  | CFG_bool_binary (AST_OR,_,_) -> 1
  | _ -> 100


(* utility to print lists *)
let print_list f sep fmt l =
  let rec aux = function
    | [] -> ()
    | [a] -> f fmt a
    | a::b -> f fmt a; Format.fprintf fmt "%s" sep; aux b
  in
  aux l

(* utility to print options *)
let print_option f none fmt l =
  match l with
  | None -> Format.fprintf fmt "%s" none
  | Some v -> f fmt v



(* expressions *)
(* *********** *)


let print_var fmt v =
  Format.fprintf fmt "%s(%i)" v.var_name v.var_id


let string_of_type t =
  match t with
  | AST_TYP_INT -> "int"


let rec print_int_expr fmt e =
  match e with

  | CFG_int_unary (op,e1) ->
      Format.fprintf fmt "%s" (string_of_int_unary_op op);
      if int_expr_precedence e1 <= int_expr_precedence e
      then Format.fprintf fmt " (%a)" print_int_expr e1
      else Format.fprintf fmt " %a" print_int_expr e1

  | CFG_int_binary (op,e1,e2) ->
      if int_expr_precedence e1 < int_expr_precedence e
      then Format.fprintf fmt "(%a) " print_int_expr e1
      else Format.fprintf fmt "%a " print_int_expr e1;
      Format.fprintf fmt "%s" (string_of_int_binary_op op);
      if int_expr_precedence e2 <= int_expr_precedence e
      then Format.fprintf fmt " (%a)" print_int_expr e2
      else Format.fprintf fmt " %a" print_int_expr e2

  | CFG_int_const i -> Format.fprintf fmt "%s" (Z.to_string i)

  | CFG_int_rand (i1,i2) ->
      Format.fprintf fmt "rand(%s,%s)" (Z.to_string i1) (Z.to_string i2)

  | CFG_int_var v -> print_var fmt v


and print_bool_expr fmt e =
  match e with

  | CFG_bool_unary (op,e1) ->
      Format.fprintf fmt "%s" (string_of_bool_unary_op op);
      if bool_expr_precedence e1 <= bool_expr_precedence e
      then Format.fprintf fmt " (%a)" print_bool_expr e1
      else Format.fprintf fmt " %a" print_bool_expr e1

  | CFG_bool_binary (op,e1,e2) ->
      if bool_expr_precedence e1 < bool_expr_precedence e
      then Format.fprintf fmt "(%a) " print_bool_expr e1
      else Format.fprintf fmt "%a " print_bool_expr e1;
      Format.fprintf fmt "%s" (string_of_bool_binary_op op);
      if bool_expr_precedence e2 <= bool_expr_precedence e
      then Format.fprintf fmt " (%a)" print_bool_expr e2
      else Format.fprintf fmt " %a" print_bool_expr e2

  | CFG_compare (op,e1,e2) ->
      if int_expr_precedence e1 < bool_expr_precedence e
      then Format.fprintf fmt "(%a) " print_int_expr e1
      else Format.fprintf fmt "%a " print_int_expr e1;
      Format.fprintf fmt "%s" (string_of_compare_op op);
      if int_expr_precedence e2 <= bool_expr_precedence e
      then Format.fprintf fmt " (%a)" print_int_expr e2
      else Format.fprintf fmt " %a" print_int_expr e2

  | CFG_bool_const i -> Format.fprintf fmt "%B" i

  | CFG_bool_rand -> Format.fprintf fmt "brand"



(* instructions *)
(* ************ *)


let print_inst fmt i =
  match i with
  | CFG_skip msg -> Format.fprintf fmt "%s" msg
  | CFG_assign (v,e) -> Format.fprintf fmt "%a = %a" print_var v print_int_expr e
  | CFG_guard b -> Format.fprintf fmt "%a ?" print_bool_expr b
  | CFG_assert (b, _) -> Format.fprintf fmt "assert %a" print_bool_expr b
  | CFG_call f -> Format.fprintf fmt "call %s" f.func_name



(* programs *)
(* ******** *)

(* raw dump of the graph *)
let print_cfg fmt p =
  let pp_var fmt v =
    Format.fprintf fmt "%s(%i):%s"
      v.var_name v.var_id (string_of_type v.var_type)
  in
  Format.fprintf fmt "List of variables:\n";
  List.iter
    (fun v ->
      Format.fprintf fmt "  %a at %s\n"
        pp_var v (string_of_extent v.var_pos)
    ) p.cfg_vars;
  Format.fprintf fmt "\n";
  Format.fprintf fmt "List of functions:\n";
  List.iter
    (fun f ->
      Format.fprintf fmt "  %i: %s(%a) -> %a at %s, entry: %i, exit: %i, calls:"
        f.func_id f.func_name
        (print_list pp_var ",") f.func_args
        (print_option pp_var "void") f.func_ret
        (string_of_extent f.func_pos)
        f.func_entry.node_id f.func_exit.node_id;
      List.iter
        (fun a ->
          Format.fprintf fmt " %i->%i" a.arc_src.node_id a.arc_dst.node_id
        ) f.func_calls;
      Format.fprintf fmt "\n";
    ) p.cfg_funcs;
  Format.fprintf fmt "\n";
  Format.fprintf fmt "List of nodes:\n";
  List.iter
    (fun n ->
      Format.fprintf fmt "  %i: at %s, in: "
        n.node_id  (string_of_position n.node_pos);
      List.iter (fun a -> Format.fprintf fmt "%i " a.arc_src.node_id) n.node_in;
      Format.fprintf fmt "out:";
      List.iter (fun a -> Format.fprintf fmt "%i " a.arc_dst.node_id) n.node_out;
      Format.fprintf fmt "\n";
    ) p.cfg_nodes;
  Format.fprintf fmt "\n";
  Format.fprintf fmt "List of arcs:\n";
  List.iter
    (fun a ->
      Format.fprintf fmt "  %i -> %i: %a\n"
        a.arc_src.node_id a.arc_dst.node_id print_inst a.arc_inst
    ) p.cfg_arcs;
  Format.fprintf fmt "\n"


(* dump to a DOT file, viewable with Graphviz *)
let output_dot name p =
  let ch = open_out name in
  let fmt = Format.formatter_of_out_channel ch in
  Format.fprintf fmt "digraph CFG {\n";
  (* nodes and instructions *)
  List.iter
    (fun a ->
      Format.fprintf fmt " %i -> %i [label=\"%a\"];\n"
        a.arc_src.node_id a.arc_dst.node_id print_inst a.arc_inst
    ) p.cfg_arcs;
  let isguard arc =
    match arc.arc_inst with CFG_guard _ -> true | _ -> false in
  List.iter
    (fun n -> if n.node_out <> [] && List.for_all isguard n.node_out then
      Format.fprintf fmt "  %i [shape=diamond];" n.node_id)
    p.cfg_nodes;
  (* function entry and exit *)
  List.iter
    (fun f ->
      Format.fprintf fmt "  entry_%s [shape=box,label=\"%s(%a) -> %a\"];\n"
        f.func_name f.func_name
        (print_list print_var ",") f.func_args
        (print_option print_var "void") f.func_ret;
      Format.fprintf fmt "  exit_%s [shape=box,label=\"exit %s\"];\n"
        f.func_name f.func_name;
      Format.fprintf fmt "  entry_%s -> %i;\n" f.func_name f.func_entry.node_id;
      Format.fprintf fmt "  %i -> exit_%s;\n" f.func_exit.node_id f.func_name
    ) p.cfg_funcs;
  (* init code entry and exit *)
  Format.fprintf fmt "  init_entry [shape=box];\n";
  Format.fprintf fmt "  init_exit [shape=box];\n";
  Format.fprintf fmt "  init_entry -> %i;\n" p.cfg_init_entry.node_id;
  Format.fprintf fmt "  %i -> init_exit;\n" p.cfg_init_exit.node_id;
  Format.fprintf fmt "}\n";
  flush ch;
  close_out ch

