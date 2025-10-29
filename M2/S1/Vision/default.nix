{
  sources ? import ./lon.nix,
  pkgs' ? import sources.nixpkgs { },
}:
let
  pkgs = import (pkgs'.applyPatches {
    src = pkgs'.path;
    patches = [
      (pkgs'.fetchpatch {
        url = "http://github.com/NixOS/nixpkgs/pull/455181.patch";
        hash = "sha256-/kwcAB+gz2FwQaXp4PlZ6vFevnFG4MUP7arQN5bJ2kg=";
      })
    ];
  }) { };

in
{
  devShell = pkgs.mkShell {
    packages = with pkgs; [
      cmake
      gnumake
      gcc
      qt6.qtbase
      libGL
    ];

    env.Imagine_DIR = pkgs.imaginepp;
	env.QT_PLUGIN_PATH = "/nowhere";
  };
}
