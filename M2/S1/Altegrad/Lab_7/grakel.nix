{
  lib,
  python3,
  fetchFromGitHub,
}:

python3.pkgs.buildPythonApplication {
  pname = "grakel";
  version = "unstable-2025-07-26";
  pyproject = true;

  src = fetchFromGitHub {
    owner = "ysig";
    repo = "GraKeL";
    rev = "eac1e47f1a6e37eb3f6c5d9d63a0cbd3ff74efa4";
    hash = "sha256-pBJMNw3XVd8uw2itXUpOZwzmQE86OHZSKdQZ55ePkPQ=";
  };

  build-system = [
    python3.pkgs.cython
    python3.pkgs.numpy
    python3.pkgs.setuptools
  ];

  dependencies = with python3.pkgs; [
    cython
    future
    joblib
    numpy
    scikit-learn
    six
  ];

  optional-dependencies = with python3.pkgs; {
    dev = [
      cvxopt
      pytest
      pytest-coverage
      torch-geometric
    ];
    lovasz = [
      cvxopt
    ];
    test = [
      pytest
      pytest-coverage
      torch-geometric
    ];
    wheel = [
      pytest
      pytest-coverage
    ];
  };

  pythonImportsCheck = [
    "grakel"
  ];

  meta = {
    description = "A scikit-learn compatible library for graph kernels";
    homepage = "https://github.com/ysig/GraKeL";
    license = lib.licenses.bsd3;
    maintainers = [ "Pandada" ];
    mainProgram = "grakel";
  };
}
