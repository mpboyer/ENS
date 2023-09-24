type trie = {words : string list; branches : (int * trie) list}

let empty = {words = []; branches = []}

let rec find = function 
  | tr, [] -> tr.words
  | tr, h :: t -> find ((List.assoc h tr.branches), t)

let change_assoc a b l = 
  try
    List.assoc a l;
    let rec modif = function
      |[] -> [(a, b)]
      |h::t -> if fst h == a then (a, b)::t else h::(modif t)
    in 
    modif l
  with Not_found -> (a, b)::l

let rec add tr nlist s = 
  match nlist with
  | [] -> {words = s::tr.words; branches = tr.branches}
  | h::t -> let b = (add (List.assoc_opt h tr.branches |> Option.value ~default:empty) t s) in 
  {words = tr.words; branches = change_assoc h b tr.branches}


let key = function
  |'a'|'b'|'c' -> 2
  |'d'|'e'|'f' -> 3
  |'g'|'h'|'i' -> 4
  |'j'|'l'|'k' -> 5
  |'m'|'n'|'o' -> 6
  |'p'|'q'|'r'|'s' -> 7
  |'t'|'u'|'v' -> 8
  |'w'|'x'|'y'|'z' -> 9
  | _ -> assert false

let int_list_of_string s = String.fold_right (fun c acc -> (key c)::acc) s [] 


let add_word tr s = let nlist = int_list_of_string s in add tr nlist s


let dict = [
  "lex"; "key"; "void" ; "caml" ; "unix" ; "for" ; "while" ; "done" ;
  "let" ; "fold"; "val"; "exn" ; "rec" ; "else" ; "then" ; "type" ;
  "try" ; "with" ; "to"; "find" ; "do" ; "in" ; "if" ; "hd" ; "tl" ;
  "iter" ; "map" ; "get"; "copy" ; "and"; "as" ; "begin" ; "class" ;
  "downto" ; "end" ; "exception" ; "false" ; "fun" ; "function" ;
  "match" ; "mod" ; "mutable" ; "open" ; "or" ; "true" ; "when" ;
  "load" ; "mem" ; "length" ; "bash" ; "unit" ; "site"; "php"; "sql";
  "ssh"; "spam"; "su"; "qt"; "root"; "bsd"; "boot"; "bash";
  "ocaml"; "kde"; "gtk" ; "gcc"
]

let dictr = List.fold_left add_word empty dict


let branch i t =
  try List.assoc i t.branches with Not_found -> empty

let remove tr l s = 
  let rec remove trie = function
    | [] -> {trie with words = List.filter ((<>) s) trie.words}
    | h :: t -> let tro = branch h trie in
                let f = match remove tro t with
                |{words = []; branches = []} -> List.remove_assoc h
                |trop -> change_assoc h trop 
  in {trie with branches = f trie.branches}
in remove tr l

let remove_word tr s = remove tr (int_list_of_string s) s






