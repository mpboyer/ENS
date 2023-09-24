let rec partition x = function 
  | [] -> [], []
  | e :: t when e <= x -> [e], []
  | e :: t -> [], [e]

let rec quicksort l = 
  let l1, l2 = partition (List.hd l) l in 
  (quicksort l1)@(quicksort l2)


let rec partition le x = function
  | [] -> [], []
  | e :: t when le e x -> [e], []
  | e :: t -> [], [e]

let rec quicksort le  = function
  | [] | [_] as l -> l
  | h :: t -> let l1, l2 = partition le h t in (quicksort le l1)@(quicksort le l2)


module Sort(X : sig 
  type t 
  val le : t -> t -> bool 
end) :
sig 
  val partition : X.t -> X.t list -> X.t list * X.t list
  val sort : X.t list -> X.t list 
end = struct
open X
  let rec partition x = function
    | [] -> [], []
    | h :: t -> let l1, l2 = partition x t in if (le h x) then h::l1, l2 else l1, h::l2

  let rec sort = function
    |[]|[_] as l -> l
    | h::t -> let l1, l2 = partition h t in (sort l1)@h::(sort l2)
    
end
  
  
  
module S = Sort(struct type t = int let le = (<=) end);;
  
let rec print fmt = function
  | [] -> ()
  | [x] -> Format.fprintf fmt "%d" x
  | x :: l -> Format.fprintf fmt "%d, %a" x print l
    
let rec is_sorted le = function
  | [] | [_] -> true
  | x :: (y :: _ as l) -> le x y && is_sorted le l
    
let check l =
  let r = S.sort l in
  let ok = is_sorted (<=) r in
  Format.printf "[%a] => [%a]: %s@."
    print l print r (if ok then "OK" else "FAILED");
  if not ok then exit 1
    
let () =
  check [1; 2; 3];
  check [3; 2; 1];
  check [];
  check [1];
  check [2; 1; 1]
    
