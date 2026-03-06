{
  pkgs ? import <nixpkgs> { },
}:
with pkgs;

pkgs.mkShell {
  buildInputs = [
    (python3.withPackages (
      ps: with ps; [
        jupyter
        ipython
        numpy
        scipy
        matplotlib
        opencv4Full
        networkx
        imageio
      ]
    ))
    gtk4
    pkg-config
  ];

  shellHook = "jupyter notebook";
}
