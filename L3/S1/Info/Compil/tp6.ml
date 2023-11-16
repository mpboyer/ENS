type typ = Tint | Tarrow of typ * typ | Tproduct of typ * typ | Tvar of tvar
and tvar = { id : int; mutable def : typ option }

let rec pp_typ fmt = function
  | Tproduct (t1, t2) -> Format.fprintf fmt "%a *@ %a" pp_atom t1 pp_atom t2
  | Tarrow (t1, t2) -> Format.fprintf fmt "%a ->@ %a" pp_atom t1 pp_typ t2
  | (Tint | Tvar _) as t -> pp_atom fmt t

and pp_atom fmt = function
  | Tint -> Format.fprintf fmt "int"
  | Tvar v -> pp_tvar fmt v
  | (Tarrow _ | Tproduct _) as t -> Format.fprintf fmt "@[<1>(%a)@]" pp_typ t

and pp_tvar fmt = function
  | { def = None; id } -> Format.fprintf fmt "'%d" id
  | { def = Some t; id } -> Format.fprintf fmt "@[<1>('%d := %a)@]" id pp_typ t

module V = struct
  type t = tvar

  let compare v1 v2 = Stdlib.compare v1.id v2.id
  let equal v1 v2 = v1.id = v2.id

  let create =
    let r = ref 0 in
    fun () ->
      incr r;
      { id = !r; def = None }
end

let rec head = function Tvar { def = Some t } -> head t | t -> t

let rec canon t =
  match head t with
  | (Tvar _ | Tint) as t -> t
  | Tproduct (t1, t2) -> Tproduct (canon t1, canon t2)
  | Tarrow (t1, t2) -> Tarrow (canon t1, canon t2)

exception UnificationFailure of typ * typ

let unification_error t1 t2 = raise (UnificationFailure (canon t1, canon t2))

let rec occur v t =
  match head t with
  | Tvar w -> V.equal v w
  | Tarrow (t1, t2) | Tproduct (t1, t2) -> occur v t1 || occur v t2
  | Tint -> false

let rec unify t1 t2 =
  match (head t1, head t2) with
  | Tint, Tint -> ()
  | Tvar v1, Tvar v2 when V.equal v1 v2 -> ()
  | (Tvar v1 as t1), t2 ->
      if occur v1 t2 then unification_error t1 t2;
      assert (v1.def = None);
      v1.def <- Some t2
  | t1, Tvar v2 -> unify t2 t1
  | Tarrow (t11, t12), Tarrow (t21, t22)
  | Tproduct (t11, t12), Tproduct (t21, t22) ->
      unify t11 t21;
      unify t12 t22
  | t1, t2 -> unification_error t1 t2

module Vset = Set.Make (V)

let rec fvars t =
  match head t with
  | Tint -> Vset.empty
  | Tvar a -> Vset.singleton a
  | Tarrow (t1, t2) | Tproduct (t1, t2) -> Vset.union (fvars t1) (fvars t2)

type schema = { vars : Vset.t; typ : typ }

module Smap = Map.Make (String)

type env = { bindings : schema Smap.t; fvars : Vset.t }

let empty = { bindings = Smap.empty; fvars = Vset.empty }

let norm_varset s =
  Vset.fold (fun v s -> Vset.union (fvars (Tvar v)) s) s Vset.empty

let add gen x t env =
  let vt = fvars t in
  let s, fvars =
    if gen then
      let env_fvars = norm_varset env.fvars in
      ({ vars = Vset.diff vt env_fvars; typ = t }, env.fvars)
    else ({ vars = Vset.empty; typ = t }, Vset.union env.fvars vt)
  in
  { bindings = Smap.add x s env.bindings; fvars }

module Vmap = Map.Make (V)

let find x env =
  let tx = Smap.find x env.bindings in
  let s =
    Vset.fold (fun v s -> Vmap.add v (Tvar (V.create ())) s) tx.vars Vmap.empty
  in
  let rec subst t =
    match head t with
    | Tvar x as t -> ( try Vmap.find x s with Not_found -> t)
    | Tint -> Tint
    | Tarrow (t1, t2) -> Tarrow (subst t1, subst t2)
    | Tproduct (t1, t2) -> Tproduct (subst t1, subst t2)
  in
  subst tx.typ

type expression =
  | Var of string
  | Const of int
  | Op of string
  | Fun of string * expression
  | App of expression * expression
  | Pair of expression * expression
  | Let of string * expression * expression

let rec w env = function
  | Var x -> find x env
  | Const _ -> Tint
  | Op "+" -> Tarrow (Tproduct (Tint, Tint), Tint)
  | Op op -> failwith ("pas d'opérateur " ^ op)
  | Pair (e1, e2) ->
      let t1 = w env e1 in
      let t2 = w env e2 in
      Tproduct (t1, t2)
  | Fun (x, e1) ->
      let v = Tvar (V.create ()) in
      let env = add false x v env in
      let t1 = w env e1 in
      Tarrow (v, t1)
  | App (e1, e2) ->
      let t1 = w env e1 in
      let t2 = w env e2 in
      let v = Tvar (V.create ()) in
      unify t1 (Tarrow (t2, v));
      v
  | Let (x, e1, e2) ->
      let t1 = w env e1 in
      let env = add true x t1 env in
      w env e2

let typeof e = canon (w empty e)
let () = Printexc.record_backtrace true

(* 1 : int *)
let () = assert (typeof (Const 1) = Tint)

(* fun x -> x : 'a -> 'a *)
let () =
  assert (
    match typeof (Fun ("x", Var "x")) with
    | Tarrow (Tvar v1, Tvar v2) -> V.equal v1 v2
    | _ -> false)

(* fun x -> x+1 : int -> int *)
let () =
  assert (
    typeof (Fun ("x", App (Op "+", Pair (Var "x", Const 1))))
    = Tarrow (Tint, Tint))

(* fun x -> x+x : int -> int *)
let () =
  assert (
    typeof (Fun ("x", App (Op "+", Pair (Var "x", Var "x"))))
    = Tarrow (Tint, Tint))

(* let x = 1 in x+x : int *)
let () =
  assert (
    typeof (Let ("x", Const 1, App (Op "+", Pair (Var "x", Var "x")))) = Tint)

(* let id = fun x -> x in id 1 *)
let () =
  assert (
    typeof (Let ("id", Fun ("x", Var "x"), App (Var "id", Const 1))) = Tint)

(* let id = fun x -> x in id id 1 *)
let () =
  assert (
    typeof
      (Let ("id", Fun ("x", Var "x"), App (App (Var "id", Var "id"), Const 1)))
    = Tint)

(* let id = fun x -> x in (id 1, id (1,2)) : int * (int * int) *)
let () =
  assert (
    typeof
      (Let
         ( "id",
           Fun ("x", Var "x"),
           Pair
             (App (Var "id", Const 1), App (Var "id", Pair (Const 1, Const 2)))
         ))
    = Tproduct (Tint, Tproduct (Tint, Tint)))

(* app = fun f x -> let y = f x in y : ('a -> 'b) -> 'a -> 'b *)
let () =
  let ty =
    typeof (Fun ("f", Fun ("x", Let ("y", App (Var "f", Var "x"), Var "y"))))
  in
  assert (
    match ty with
    | Tarrow (Tarrow (Tvar v1, Tvar v2), Tarrow (Tvar v3, Tvar v4)) ->
        V.equal v1 v3 && V.equal v2 v4
    | _ -> false)

let cant_type e =
  try
    let _ = typeof e in
    false
  with UnificationFailure _ -> true

(* 1 2 *)
let () = assert (cant_type (App (Const 1, Const 2)))

(* fun x -> x x *)
let () = assert (cant_type (Fun ("x", App (Var "x", Var "x"))))

(* (fun f -> +(f 1)) (fun x -> x) *)
let () =
  assert (
    cant_type
      (App (Fun ("f", App (Op "+", App (Var "f", Const 1))), Fun ("x", Var "x"))))

(* fun x -> (x 1, x (1,2)) *)
let () =
  assert (
    cant_type
      (Fun
         ( "x",
           Pair (App (Var "x", Const 1), App (Var "x", Pair (Const 1, Const 2)))
         )))

(* fun x -> let z = x in (z 1, z (1,2)) *)
let () =
  assert (
    cant_type
      (Fun
         ( "x",
           Let
             ( "z",
               Var "x",
               Pair
                 (App (Var "z", Const 1), App (Var "z", Pair (Const 1, Const 2)))
             ) )))

(* let distr_pair = fun f -> (f 1, f (1,2)) in distr_pair (fun x -> x) *)
let () =
  assert (
    cant_type
      (Let
         ( "distr_pair",
           Fun
             ( "f",
               Pair
                 (App (Var "f", Const 1), App (Var "f", Pair (Const 1, Const 2)))
             ),
           App (Var "distr_pair", Fun ("x", Var "x")) )))
