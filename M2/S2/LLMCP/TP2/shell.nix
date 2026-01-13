{
  pkgs ? import <nixpkgs> { },
}:
let
  pythonEnv = pkgs.python3.withPackages (ps: [
    ps.torch
    ps.transformers
    ps.accelerate
    ps.datasets
    ps.chess
    ps.huggingface-hub
    ps.hf-xet
    ps.tqdm
    ps.numpy
    ps.wandb
  ]);
in
pkgs.mkShell {
  packages = [ pythonEnv ];
}
