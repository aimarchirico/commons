# Python

Shared Python tooling, distributed as installable packages rather than copied
config files.

## Tech Stack

- **Python** 3.13
- **uv** (workspace: `pyproject.toml` here is a virtual root with
  `[tool.uv.workspace]`, listing member packages)
- **ruff** 0.14+ (lint + format)
- **ty** 0.0.60+ (type checking)
- **coverage** 7.6+ (test coverage enforcement)
- **hatchling** (build backend)

## Folder Structure

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

## Local Development

Requires Python 3.13 and [Task](https://taskfile.dev). Run from the
repository root:

- `task python:check`: check all Python packages.
- `task python:fix`: auto-fix all Python packages.

## Code Quality

- **Linting**: ruff with bundled `assets/ruff.toml`
  (`commons-python ruff <args>`), selecting rule groups `E`, `F`, and `D`.
- **Types**: ty with bundled `assets/ty.toml` (`commons-python ty <args>`).
- **Documentation**: every public module, function, class, and method needs a
  Google-style docstring, enforced via ruff's `D` (`pydocstyle`) rule group
  configured with `convention = "google"`. Non-public declarations (prefixed
  with `_`) do not carry docstrings.
- **Comments**: only docstrings documenting a public declaration are allowed
  (`commons-python commons check`), mirroring the owner-aware doc-comment
  enforcement across the repository: whatever is required to have a doc
  comment is also the only thing allowed to have one. Line comments (`# ...`),
  orphaned docstrings, and docstrings on non-public declarations are rejected,
  so explanation stays attached to what it describes.
- **Line length**: native Python check enforcing a 300-line-per-file maximum
  (`commons-python commons check`), skipping `.venv/`, `__pycache__/`, `.git/`,
  `build/`, `dist/`, and `*.egg-info/`.
- **Testing & Coverage** — pytest and pytest-cov with bundled `assets/coverage.toml`,
  enforcing an 80% minimum (`fail_under = 80`) with branch coverage on
  (`commons-python pytest <args>`).

## Deployment

Unlike `maven/` and `npm/`, GitHub Packages has no PyPI-compatible registry,
so packages here are not published anywhere and Release Please is not
involved. Consumers pin directly to `main` as a git dependency, e.g.:

```sh
uv add "git+https://github.com/aimarchirico/commons@main#subdirectory=python/commons-python"
```

`plugin/` in this repo is the reference consumer.
</content>
