{
  description = "Notice To Air Missions Parser Written in Python";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.05";
  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.poetry2nix = {
    url = "github:nix-community/poetry2nix";
    inputs.nixpkgs.follows = "nixpkgs";
    inputs.flake-utils.follows = "flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix, ... }: {
    overlays.default = nixpkgs.lib.composeManyExtensions [
      poetry2nix.overlay
      (final: prev: let python = final.python3; in {
        pynotam = prev.poetry2nix.mkPoetryApplication {
          inherit python;
          projectDir = prev.poetry2nix.cleanPythonSources { src = ./.; };
          pythonImportCheck = [ "pynotam" ];
          overrides = prev.poetry2nix.overrides.withDefaults (final: prev: {
            timeutils = prev.timeutils.overridePythonAttrs (old: {
              buildInputs = (old.buildInputs or [ ]) ++ [ prev.setuptools ];
            });
          });
        };
        pynotam-dev = prev.poetry2nix.mkPoetryEnv {
          inherit python;
          projectDir = ./.;
          editablePackageSources = {
            pynotam = ./pynotam;
          };
          overrides = prev.poetry2nix.overrides.withDefaults (final: prev: {
            timeutils = prev.timeutils.overridePythonAttrs (old: {
              buildInputs = (old.buildInputs or [ ]) ++ [ prev.setuptools ];
            });
          });
        };
      })
    ];
  } // (flake-utils.lib.eachDefaultSystem (system:
    let
      pkgs = import nixpkgs {
        inherit system;
        overlays = [ self.overlays.default ];
      };
    in
    {
      packages = {
        default = pkgs.pynotam;
      };

      devShells.default = pkgs.pynotam-dev.env.overrideAttrs (oldAttrs: {
        buildInputs = with pkgs; [
          poetry
          nodejs
          curl
        ];
        shellHook = ''
          export POETRY_HOME=${pkgs.poetry}
          export POETRY_BINARY=${pkgs.poetry}/bin/poetry
          export POETRY_VIRTUALENVS_IN_PROJECT=true
          unset SOURCE_DATE_EPOCH
        '';
      });

      apps = {
        lint = {
          type = "app";
          program = toString (pkgs.writeScript "lint" ''
            export PATH="${pkgs.lib.makeBinPath [
                pkgs.pynotam-dev
                pkgs.git
            ]}"
            echo "[nix][lint] Run pynotam PEP 8 checks."
            flake8 --select=E,W,I --ignore W503 --max-line-length 88 --import-order-style pep8 --statistics --count pynotam
            echo "[nix][lint] Run pynotam PEP 257 checks."
            flake8 --select=D --ignore D301,D100 --statistics --count pynotam
            echo "[nix][lint] Run pynotam pyflakes checks."
            flake8 --select=F --statistics --count pynotam
            echo "[nix][lint] Run pynotam code complexity checks."
            flake8 --select=C901 --statistics --count pynotam
            echo "[nix][lint] Run pynotam open TODO checks."
            flake8 --select=T --statistics --count pynotam tests
            echo "[nix][lint] Run pynotam black checks."
            black --check pynotam
          '');
        };
        mypy = {
          type = "app";
          program = toString (pkgs.writeScript "mypy" ''
            export PATH="${pkgs.lib.makeBinPath [
                pkgs.pynotam-dev
                pkgs.git
            ]}"
            echo "[nix][mypy] Run pynotam mypy checks."
            mypy pynotam
          '');
        };
      };
    }
  ));
}
