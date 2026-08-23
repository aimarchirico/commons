# Python

Shared Python tooling, distributed as installable packages rather than
copied config files.

## Install

Requires Python 3.13 and [Task](https://taskfile.dev).

There is no PyPI-compatible registry available, so packages here are not
published anywhere and Release Please is not involved. Consumers pin
directly to `main` as a git dependency, e.g.:

```sh
uv add "git+https://github.com/aimarchirico/commons@main#subdirectory=python/commons-python"
```

## Usage

Run from the repository root:

- `task python:check`: check all Python packages.
- `task python:fix`: auto-fix all Python packages.

## Development

### Tech Stack

Python 3.13 · uv (workspace: `pyproject.toml` here is a virtual root with
`[tool.uv.workspace]`, listing member packages) · ruff 0.14+ (lint + format)
· ty 0.0.60+ (type checking) · coverage 7.6+ (test coverage enforcement) ·
hatchling (build backend).

### Folder Structure

```text
python/
├── pyproject.toml      # virtual workspace root (no [project] table)
├── Taskfile.yaml       # single Taskfile for the whole workspace
└── commons-python/     # shared ruff/ty/coverage config + CLI
    ├── src/commons_python/
    │   ├── __init__.py
    │   ├── cli.py              # `commons-python` entry point, dispatches on first arg
    │   ├── comments.py         # comments check (part of `commons-python commons check`)
    │   ├── line_length.py      # line-length check (part of `commons-python commons check`)
    │   └── assets/
    │       ├── __init__.py
    │       ├── ruff.toml       # bundled ruff config
    │       ├── ty.toml         # bundled ty config
    │       └── coverage.toml   # bundled coverage config
    ├── tests/                  # commons-python's own test suite
    └── pyproject.toml
```

Only `commons-python` exists today; adding a package means adding it to
`pyproject.toml`'s `members` list, following the same pattern.

`assets/` is a regular subpackage (not just data files) so
`importlib.resources.files("commons_python.assets")` resolves reliably
whether the package is installed from a wheel, sdist, or editable install.

### Code Quality

- **Linting**: ruff with bundled `assets/ruff.toml` (`commons-python ruff`).
- **Types**: ty with bundled `assets/ty.toml` (`commons-python ty`).
- **Documentation & Comments**: Google-style docstrings for public
  declarations; line comments and comments on internal declarations
  disallowed (`commons-python commons check`).
- **File Length**: 300-line maximum per file (`commons-python commons check`).
- **Testing & Coverage**: pytest and pytest-cov enforcing an 80% coverage
  threshold (`commons-python pytest`).

## Contributing

See [CONTRIBUTING.md](../.github/CONTRIBUTING.md).

## License

[MIT](../LICENSE) © Aimár A. Chirico
