type terminal = string

type non_terminal = string

type symbol =
  | Terminal of terminal
  | NonTerminal of non_terminal

type production = symbol list

type rule = non_terminal * production

type grammar = {
  start : non_terminal;
  rules : rule list;
}

let g_arith =
  { start = "S'";
    rules = [ "S'", [ NonTerminal "E"; Terminal "#" ];
              "E",  [ NonTerminal "T"; NonTerminal "E'"; ];
              "E'", [ Terminal "+"; NonTerminal "T"; NonTerminal "E'"; ];
              "E'", [ ];
              "T",  [ NonTerminal "F"; NonTerminal "T'"; ];
              "T'", [ Terminal "*"; NonTerminal "F"; NonTerminal "T'"; ];
              "T'", [ ];
              "F",  [ Terminal "("; NonTerminal "E"; Terminal ")"; ];
              "F",  [ Terminal "int" ]; ] }


let rec fixpoint f a = 
  let (b, isnew) = f a in
  if isnew then fixpoint f b else b



module Ntset = Set.Make(String)
type nulls = Ntset.t


let is_null_production nulls p =
  let is_null_symbol = function
    | Terminal(_) -> false
    | NonTerminal(nt) -> Ntset.mem nt nulls
  in 
  List.for_all is_null_symbol p

let null g = 
  let step nulls =
    List.fold_left (fun ((n, _) as nb) (nt, p) -> if (not (Ntset.mem nt n)) && is_null_production n p then (Ntset.add nt n, true) else nb) (nulls, false) g.rules
  in 
  fixpoint step Ntset.empty

let pp_non_terminal fmt s = Format.fprintf fmt "%s" s

let pp_iter iter pp_elt fmt =
  let first = ref true in
  iter (fun elt ->
      if not !first then Format.fprintf fmt ",@ " else first := false;
      pp_elt fmt elt)
  
let pp_nulls fmt =
  Format.fprintf fmt "@[%a@]" (pp_iter Ntset.iter pp_non_terminal) 

module Ntmap = Map.Make(String)
module Tset = Set.Make(String)

type firsts = Tset.t Ntmap.t

let empty_map g = List.fold_left (fun f (s, _) -> Ntmap.add s Tset.empty f) Ntmap.empty g.rules

let first_production_step nulls firsts p = 
  let rec fold_prod = function 
    | [] -> Tset.empty
    | Terminal c::_ -> Tset.add c Tset.empty
    | NonTerminal nt::p -> if Ntset.mem nt nulls then 
        Tset.union (Ntmap.find nt firsts) (fold_prod p)
      else Ntmap.find nt firsts
  in fold_prod p


let first g nulls = 
  let step firsts = 
    List.fold_left (fun (f, _ as fb) (nt, p) -> 
        let fnt = Ntmap.find nt f in 
        let fp = first_production_step nulls f p in 
        if Tset.subset fp fnt then fb
        else (Ntmap.add nt (Tset.union fnt fp) f, true)          
      ) (firsts, false) g.rules
    in 
  fixpoint step (empty_map g)

let pp_iter_bindings iter pp_binding fmt =
  let first = ref true in
  iter (fun key elt ->
      if not !first then Format.fprintf fmt "@\n" else first := false;
      pp_binding fmt key elt)

let pp_terminal fmt s = Format.fprintf fmt "%s" s

let pp_firsts fmt =
  Format.fprintf fmt "@[%a@]"
  @@ pp_iter_bindings Ntmap.iter (fun fmt nt ts ->
          Format.fprintf fmt "@[%a -> {%a}@]" pp_non_terminal nt
            (pp_iter Tset.iter pp_terminal)
            ts)

type follows = Tset.t Ntmap.t

let follow g nulls firsts =
  let update (follows,b) nt follow_nt =
    let ntn = Ntmap.find nt follows in 
    if Tset.subset follow_nt ntn then
      (follows, b)
    else 
      (Ntmap.add nt (Tset.union follow_nt ntn) follows, true)     
  in
  let rec update_prod ((follows,b) as acc) nty = function
    | [] -> acc
    | NonTerminal ntx::beta -> 
      let acc_ = update acc ntx (first_production_step nulls firsts beta) in
      let acc__ = if is_null_production nulls beta then
        update acc_ ntx (Ntmap.find nty follows)
        else acc_
      in 
      update_prod acc__ nty beta
    |Terminal _::beta -> 
      update_prod acc nty beta     
  in
  let step follows =
    List.fold_left
      (fun acc (nt,p) -> update_prod acc nt p)
      (follows,false) g.rules
  in
  fixpoint step (empty_map g)


let pp_follows = pp_firsts

let () =
  let nulls_arith = null g_arith in
  let firsts_arith = first g_arith nulls_arith in
  let follows_arith = follow g_arith nulls_arith firsts_arith in
  Format.printf "follow: %a@." pp_follows follows_arith


module Tmap = Map.Make(String)
module Pset = Set.Make(struct type t = production let compare = compare end)

type expansion_table = Pset.t Tmap.t Ntmap.t

let add_entry table nt t p = 
  let line = try Ntmap.find nt table with Not_found -> Tmap.empty in
  let s = try Tmap.find t line with Not_found -> Pset.empty in
  Ntmap.add nt (Tmap.add t (Pset.add p s) line) table

let expansions g = 
  let nulls = null g in
  let firsts = first g nulls in
  let follows = follow g nulls firsts in 
  List.fold_left (fun table (nt, p) -> 
    let ts = first_production_step nulls firsts p in 
    let ts_ = if is_null_production nulls p then Tset.union ts (Ntmap.find nt follows) else ts in
    Tset.fold (fun t table -> add_entry table nt t p) ts_ table ) Ntmap.empty g.rules

  