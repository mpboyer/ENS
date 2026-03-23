{
  sources ? import ./lon.nix,
  pkgs ? import sources.nixpkgs { overlays = [ (import (builtins.fetchTarball "https://github.com/oxalica/rust-overlay/archive/master.tar.gz")) ]; },
}:

let
  inherit (pkgs) lib;
in
{
  devShell = pkgs.mkShell rec {
    buildInputs = with pkgs; [
      libxkbcommon
      libGL
      rust-bin.beta.latest.complete

      # WINIT_UNIX_BACKEND=wayland
      wayland

      # WINIT_UNIX_BACKEND=x11
      xorg.libXcursor
      xorg.libXrandr
      xorg.libXi
      xorg.libX11
    ];
    LD_LIBRARY_PATH = "${lib.makeLibraryPath buildInputs}";
    WINIT_UNIX_BACKEND = "x11";
  };
}
