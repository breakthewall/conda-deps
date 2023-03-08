# conda_deps
## Description
This module is a simple way to list dependencies for conda packages.

## Input

### Positional arguments
* **--packages**: (string)+ List of packages to list dependencies for.

### Optional arguments
* **--env**: (string) Name of the environment to use. If not provided, the current environment is used.
* **--recursive**: (flag) If set, dependencies of dependencies are also listed (default: false).
* **--outfile**: (string) Name of the output file (JSON). If not provided, the output is printed to stdout.
* **--deps-graphs**: (string)+ List of JSON files containing dependency graphs.


## Install
### From Conda
```sh
[sudo] conda install -c conda-forge conda_deps
```

## Use

### Function call from Python code
```python
from conda_deps.conda import conda_list_deps
from networkx import DiGraph

deps_graph = DiGraph()
for package in <packages>:
    deps_graph = conda_list_deps(package)
```

If parameters from CLI have to be parsed, the function `build_args_parser` is available:
```python
from rrparser import build_args_parser

parser = buildparser()
params = parser.parse_args()
```

### Run from CLI
```sh
python -m conda_deps \
  --packages <pkg1_name> [<pkg2_name>...] \
  [--env <env_name>] \
  [--recursive \
  [--outfile <filename>] \
  [--deps-graphs <json_file1> [<json_file2>...]]
```

## Tests
Test can be run with the following commands:

### Natively
```bash
python -m pytest -v
```

# CI/CD
For further tests and development tools, a CI toolkit is provided in `ci` folder (see [ci/README.md](ci/README.md)).

## Authors

* **Joan Hérisson**

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

