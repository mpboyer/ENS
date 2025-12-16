{
  pkgs ? import <nixpkgs> { },
}:

let
  # Import pyproject-nix
  pyproject-nix =
    import
      (pkgs.fetchFromGitHub {
        owner = "pyproject-nix";
        repo = "pyproject.nix";
        rev = "master"; # or pin to a specific commit
        sha256 = "sha256-Z+R2lveIp6Skn1VPH3taQIuMhABg1IizJd8oVdmdHsQ="; # update with actual hash
      })
      {
        lib = pkgs.lib;
      };

  # Load/parse requirements.txt
  project = pyproject-nix.lib.project.loadRequirementsTxt { projectRoot = ./.; };

  python = pkgs.python3;

  pythonEnv =
    # Assert that versions from nixpkgs matches what's described in requirements.txt
    # In projects that are overly strict about pinning it might be best to remove this assertion entirely.
    # Render requirements.txt into a Python withPackages environment
    pkgs.python3.withPackages (project.renderers.withPackages { inherit python; });

in
pkgs.mkShell {
  packages = [
    pythonEnv
    (pkgs.callPackage ./grakel.nix { })
  ];
}
