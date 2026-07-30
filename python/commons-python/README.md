# commons-python

Shared ruff configuration and Python conventions, installed as a package so
consumers get a pinned config plus a CLI instead of copying files around.

## Tech Stack

- **Python** 3.13
- **uv** (project/dependency management)
- **ruff** 0.14+ (lint + format)
- **hatchling** (build backend)

## Folder Structure

```text
commons-python/
├── src/commons_python/
│   ├── __init__.py
│   ├── cli.py              # `commons-python` entry point (ruff wrapper)
│   ├── line_length.py       # `commons-python-line-length` entry point
│   └── assets/
│       ├── __init__.py
│       └── ruff.toml         # bundled ruff config
├── pyproject.toml
└── Taskfile.yaml
```

`assets/` is a regular subpackage (not just data files) so
`importlib.resources.files("commons_python.assets")` resolves reliably
whether the package is installed from a wheel, sdist, or editable install.

## Environment Variables

None.

## Local Development

Requires Python 3.13, [uv](https://docs.astral.sh/uv/), and
[Task](https://taskfile.dev). Run from the repository root:

- `task python:check` — lint with the bundled config, check the line-length
  convention, and type-check.
- `task python:fix` — auto-fix lint issues and format.

## Code Quality

- **Linting/formatting** — `commons-python` is a thin wrapper around `ruff`
  that injects the bundled `assets/ruff.toml` via `--config`, so consumers
  run `commons-python check` / `commons-python check --fix` instead of
  managing their own ruff config file. All other arguments (paths, flags)
  pass through untouched.
- **Line length** — ruff has no rule for a maximum *file* line count (only
  line-*width* rules), so `commons-python-line-length` is a small standalone
  script enforcing a 300-line-per-file maximum, skipping `.venv/`,
  `__pycache__/`, `.git/`, `build/`, `dist/`, and `*.egg-info/`.
- **Types** — `ty check`.

## Deployment

Releases are driven by Release Please (`release-type: simple`), starting at
`1.0.0`. There is no PyPI-compatible registry on GitHub Packages, so this
package is not published anywhere — consumers add it as a git dependency
pinned to a release tag (e.g. via `uv add
"git+https://github.com/aimarchirico/commons@<tag>#subdirectory=python/commons-python"`).
Resolving distribution more thoroughly (e.g. a private index) is tracked
separately.
