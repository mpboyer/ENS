let rec insert e = function
  | [] -> [e]
  | h :: t -> if e <= h then e :: h :: t else h::(insert e t)

let rec insertion_sort l1 = function
  | [] -> l1
  | h :: t -> insertion_sort (insert h l1) t


