(*
  Cours "Sémantique et Application à la Vérification de programmes"

  Ecole normale supérieure, Paris, France / CNRS / INRIA
*)

open Frontend
open Cfg

let iterate cfg =
  let _ = Random.self_init () in

  let iter_arc arc: unit =
    match arc.arc_inst with
    | _ -> failwith "TODO"
  in

  let iter_node node: unit =
    Format.printf "<%i>: ⊤@ " node.node_id
  in

  List.iter iter_arc cfg.cfg_arcs;
  Format.printf "Node Values:@   @[<v 0>";
  List.iter iter_node cfg.cfg_nodes;
  Format.printf "@]"
