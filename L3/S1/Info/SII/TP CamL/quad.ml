
(**************************************)
(* Déclarations des types de l'énoncé *)
(**************************************)

type color = White | Black

type tree =
  | Leaf of color
  | Node of tree * tree * tree * tree

type image = color array array

(* Ouvrir la fenêtre graphique *)

let _ = Graphics.open_graph " 1024x1024"

(**************)
(* Question 1 *)
(**************)

let rec count_leaves = function
  |Leaf(_) -> 1
  |Node(t1, t2, t3, t4) -> count_leaves t1 + count_leaves t2 + count_leaves t3 + count_leaves t4

let rec do_draw i j k = function
  |Leaf Black -> Graphics.fill_rect i j k k
  |Leaf White -> ()
  |Node(t1, t2, t3, t4) -> let k2 = k/2 in
    do_draw i (j+k2) k2 t1;
    do_draw (i+k2) (j+k2) k2 t2;
    do_draw i j k2 t3;
    do_draw (i+k2) j k2 t4

let draw_tree k a = do_draw 0 0 k a


let rec do_to_tree img x y k =
    if k <= 1 then
      Leaf img.(x).(y)
    else
      let k2 = k/2 in
      let t1 = do_to_tree img x (y+k2) k2 in
      let t2 = do_to_tree img (x + k2) (y+k2) k2 in
      let t3 = do_to_tree img x y k2 in
      let t4 = do_to_tree img (x + k2) y k2 in
      match t1, t2, t3, t4 with
      | Leaf n1, Leaf n2, Leaf n3, Leaf n4 when n1 = n2 && n2 = n3 && n3 = n4 -> t1
      | _ -> Node(t1, t2, t3, t4)


let image_to_tree k img = do_to_tree img 0 0 k

(* Test de image_to_tree *)
let img =
[|
  [| Black ;Black ;Black ;Black ;Black ;Black ;Black ;Black ;
     Black ;Black ;Black ;Black ;White ;White ;White ;White ; |] ;
  [| Black ;Black ;Black ;Black ;Black ;Black ;Black ;Black ;
     Black ;Black ;Black ;Black ;White ;White ;White ;White ; |] ;
  [| Black ;Black ;Black ;Black ;Black ;Black ;Black ;Black ;
     Black ;Black ;Black ;Black; White ;White ;White ;White ; |] ;
  [| Black ;Black ;Black ;Black ;Black ;Black ;Black ;Black ;
     Black ;Black ;Black ;Black;White ;White ;White ;White ; |] ;
  [| Black ;Black ;Black ;Black ;Black ;Black ;Black ;Black ;
     White ;White ;White ;White ;White ;White ;White ;White ; |] ;
  [| Black ;Black ;Black ;Black ;Black ;Black ;Black ;Black ;
     White ;White ;White ;White ;White ;White ;White ;White ; |] ;
  [| Black ;Black ;Black ;Black ;Black ;Black ;Black ;Black ;
     White ;White ;White ;White ;White ;White ;White ;White ; |] ;
  [| Black ;Black ;Black ;Black ;Black ;Black ;Black ;Black ;
     White ;White ;White ;White ;White ;White ;White ;White ; |] ;
  [| Black ;Black ;Black ;Black ;Black ;Black ;Black ;Black ;
     Black ;Black ;Black ;Black ;Black ;Black ;Black ;Black ; |] ;
  [| Black ;Black ;Black ;Black ;Black ;Black ;Black ;Black ;
     Black ;Black ;Black ;Black ;Black ;Black ;Black ;Black ; |] ;
  [| Black ;Black ;Black ;Black ;Black ;Black ;Black ;Black ;
     Black ;Black ;Black ;Black ;Black ;Black ;Black ;Black ; |] ;
  [| Black ;Black ;Black ;Black ;Black ;Black ;Black ;Black ;
     Black ;Black ;Black ;Black ;Black ;Black ;Black ;Black ; |] ;
  [| Black ;Black ;Black ;Black ;Black ;Black ;Black ;Black ;
     Black ;Black ;Black ;Black ;Black ;Black ;Black ;Black ; |] ;
  [| Black ;Black ;Black ;Black ;Black ;Black ;Black ;Black ;
     Black ;Black ;Black ;Black ;Black ;Black ;Black ;Black ; |] ;
  [| Black ;Black ;Black ;Black ;Black ;Black ;Black ;Black ;
     Black ;Black ;Black ;Black ;Black ;Black ;Black ;Black ; |] ;
  [| Black ;Black ;Black ;Black ;Black ;Black ;Black ;Black ;
     Black ;Black ;Black ;Black ;Black ;Black ;Black ;Black ; |] ;
  |]
[@@ocamlformat "disable"]

(**************)
(* Question 3 *)
(**************)

(* TROIS FONCTIONS A COMPLETER *)
let rec inverse = function
  | Leaf White ->
      Leaf Black
  | Leaf Black ->
      Leaf White
  | Node (t1, t2, t3, t4) ->
      Node (inverse t1, inverse t2, inverse t3, inverse t4)

let rec rotate = function
  | Leaf _ as a -> a
  | Node (c1, c2, c3, c4) -> Node (rotate c2, rotate c4, rotate c1, rotate c3)

let rec antirotate = function
  | Leaf _ as a -> a
  | Node (c1, c2, c3, c4) -> Node (rotate c3, rotate c1, rotate c4, rotate c2)

(* Test des rotations *)

(**************)
(* Question 4 *)
(**************)

let rec fractal n =
  if n <= 0 then Leaf Black
  else let nan = fractal (n-1) in
    let t1 = Node(nan, nan, nan, Leaf White) in
    let t3 = rotate t1 in
    let t4 = rotate t3 in
    let t2 = rotate t4 in 
    Node(t1, t2, t3, t4)


(**************)
(* Question 5 *)
(**************)

type bit = Zero | One

let rec do_be_do_to_list a k = match a with
  | Leaf White ->
      Zero :: Zero :: k
  | Leaf Black  ->
      Zero :: One :: k
  | Node (a1, a2, a3, a4) ->
      One :: do_be_do_to_list a1
        (do_be_do_to_list a2
           (do_be_do_to_list a3
              (do_be_do_to_list a4 k)))

let tree_to_list a = do_be_do_to_list a []

let rec do_be_do_to_tree = function
    | Zero :: Zero :: k -> Leaf White, k 
    | Zero :: One :: k -> Leaf Black, k
    | One :: k ->
      let a1, k = do_be_do_to_tree k in
      let a2, k = do_be_do_to_tree k in
      let a3, k = do_be_do_to_tree k in
      let a4, k = do_be_do_to_tree k in
      Node(a1, a2, a3, a4), k
    | _ -> assert false

let list_to_tree bits = let a,_ = do_be_do_to_tree bits in a 

let rec bit_to_int = function
  | Zero -> 0
  | One -> 1

let get_bit = function
  | [] -> Zero, []
  | h :: t -> h, t

let rec get_bits n l = 
  if n <= 0 then 0, l
  else let h, t = get_bit l in
  let r, t = get_bits (n-1) t in
  2 * r + bit_to_int h, t

let rec output_list file = function 
  | [] -> ()
  | l -> let v, t = get_bits 8 l in output_char file (Char.chr v);
  output_list file t

let write_tree name a = let f = open_out_bin name in output_list f (tree_to_list a); close_out f

let rec get_n_bits digits n = 
  if digits <= 0 then []
  else let b = match n mod 2 with
  |0 -> Zero
  |1 -> One
  |_ -> assert false
  in b::get_n_bits (digits - 1)(n/2)

let read_byte f = 
  try let c = input_char f in Some (Char.code c) with End_of_file -> None


let rec input_list f = match read_byte f with
  |None -> []
  |Some n -> get_n_bits 8 n @ input_list f


let read_tree name = let f = open_in_bin name in let a = list_to_tree (input_list f) in close_in f; a

let () =
  let arbuste = read_tree "a.quad" in
  let rec q3 a =
    Graphics.clear_graph ();
    draw_tree 1024 a;
    let rec do_rec () =
      let c = Graphics.read_key () in
      if c = 'n' then q3 (rotate a)
      else if c = 'p' then q3 (antirotate a)
      else if c = 'i' then q3 (inverse a)
      else if c = 'q' then ()
      else do_rec ()
    in
    do_rec ()
  in q3 arbuste