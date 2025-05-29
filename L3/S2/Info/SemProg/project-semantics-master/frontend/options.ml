(*
  Cours "Sémantique et Application à la Vérification de programmes"

  Ecole normale supérieure, Paris, France / CNRS / INRIA
*)


(*
  Command line parsing utility
*)

module IMap = Map.Make(String)

open Arg

(* Flags *)
let verbose  = ref false

(* string arguments *)
let file = ref ""
let cfg_out = ref "cfg.dot"
let domain  = ref ""

let args = [
  "-v", Set verbose,
    " Execute the analyzer in verbose/debug mode";
  "--dot-out", Set_string cfg_out,
    " Print the cfg in this file (default is cfg.dot)";
  "--domain", Set_string domain,
    " Select the abstract domain (constants/interval)";
] |> align

let usage = "usage: ./analyzer.exe [options] filename.c"

let init () =
  let _ = parse args ( (:=) file) usage in
  let _ = if Filename.extension !file <> ".c" then begin
    Format.eprintf "file should have extension .c file: \"%s\"\n" !file;
    Arg.usage args usage;
    exit 1
  end
  in
  let _ = if Filename.extension !cfg_out <> ".dot" then begin
    Format.eprintf "CFG output file should have extension .dot (%s)\n" !cfg_out;
    Arg.usage args usage;
    exit 1
  end
  in ()

