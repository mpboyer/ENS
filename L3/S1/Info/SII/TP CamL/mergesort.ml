let rec split = function
  |[] -> [], []
  |h :: t -> let l1, l2 = split t in h::l2, l1

let rec merge = function
  | [], l -> l | l, [] -> l
  | h1::t1, (h2::_ as l2) when h1 <= h2 -> h1 :: (merge (t1, l2))
  | l1, h2::t2 -> h2::(merge (t2, l1))

let rec mergesort = function
  |[] | [_]as l -> l
  |l -> let l1, l2 = split l in merge((mergesort l1),(mergesort l2))