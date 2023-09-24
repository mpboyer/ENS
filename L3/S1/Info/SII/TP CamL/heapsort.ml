type heap = Null | Fork of int * heap * heap

let rec merge = function
  | Null, a | a, Null -> a
  | Fork(e1, hl1, hr1), (Fork(e2, hl2, hr2) as b) when e1 < e2 -> Fork(e1, merge (hr1, b), hl1)
  | (Fork(e1, hl1, hr1) as a), Fork(e2, hl2, hr2) -> Fork(e2, merge (hr2, a), hl2)

let add n h = 
    merge (h, Fork(n, Null, Null))


exception Empty_heap

let extract_min = function  
  | Null -> raise Empty_heap
  | Fork(e, hl, hr) -> e, merge (hl, hr)

let rec heap_of_list = function
  | [] -> Null
  | h :: t -> add h (heap_of_list t)

let rec list_of_heap = function
  | Null -> []
  | h -> let e, h1  = extract_min h in e::(list_of_heap h1)

let heapsort l = list_of_heap (heap_of_list l)

