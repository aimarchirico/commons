# Python

Shared Python tooling, distributed as installable packages rather than copied
config files.

## Tech Stack

- **Python** 3.13
- **uv** (workspace: `pyproject.toml` here is a virtual root with
  `[tool.uv.workspace]`, listing member packages)
- **ruff** 0.14+ (lint + format)
- **ty** 0.0.60+ (type checking)
- **hatchling** (build backend)

## Folder Structure

```text
python/
├── pyproject.toml      # virtual workspace root (no [project] table)
├── Taskfile.yaml         # single Taskfile for the whole workspace
└── commons-python/     # shared ruff/ty config + CLI
    ├── src/commons_python/
    │   ├── __init__.py
    │   ├── cli.py                # `commons-python` entry point, dispatches on first arg
    │   ├── line_length.py         # line-length check, invoked via `commons-python line-length`
    │   └── assets/
    │       ├── __init__.py
    │       ├── ruff.toml           # bundled ruff config
    │       └── ty.toml             # bundled ty config
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

- `task python:check` — check all Python packages.
- `task python:fix` — auto-fix all Python packages.

## Code Quality

- **Linting** — ruff with bundled `assets/ruff.toml` (`commons-python ruff <args>`), selecting rule groups `E`, `F`, and `D`.
- **Types** — ty with bundled `assets/ty.toml` (`commons-python ty <args>`).
- **Documentation** — every public module, function, class, and method needs a
  Google-style docstring, enforced via ruff's `D` (`pydocstyle`) rule group
  configured with `convention = "google"`. Non-public declarations (prefixed
  with `_`) do not carry docstrings.
- **Comments** — only docstrings documenting a public declaration are allowed,
  mirroring the owner-aware doc-comment enforcement across the repository:
  whatever is required to have a doc comment is also the only thing allowed
  to have one. Line comments (`# ...`), orphaned docstrings, and docstrings on
  non-public declarations are rejected, so explanation stays attached to what
  it describes. Tooling directives such as `# noqa` or `# type: ignore` remain
  legal where required by tooling.
- **Line length** — native Python check enforcing a 300-line-per-file maximum
  (`commons-python line-length`), skipping `.venv/`, `__pycache__/`, `.git/`,
  `build/`, `dist/`, and `*.egg-info/`.

## Deployment

Unlike `maven/` and `npm/`, GitHub Packages has no PyPI-compatible registry,
so packages here are not published anywhere and Release Please is not
involved. Consumers pin directly to `main` as a git dependency, e.g.:

```sh
uv add "git+https://github.com/aimarchirico/commons@main#subdirectory=python/commons-python"
```

`plugin/` in this repo is the reference consumer.
</content>
