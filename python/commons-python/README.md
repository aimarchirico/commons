# commons-python

Shared ruff and ty configuration and Python conventions, installed as a
package so consumers get pinned config plus a CLI instead of copying files
around.

## Tech Stack

- **Python** 3.13
- **uv** (project/dependency management, workspace member of `python/`)
- **ruff** 0.14+ (lint + format)
- **ty** 0.0.60+ (type checking)
- **hatchling** (build backend)

## Folder Structure

```text
commons-python/
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

`assets/` is a regular subpackage (not just data files) so
`importlib.resources.files("commons_python.assets")` resolves reliably
whether the package is installed from a wheel, sdist, or editable install.

## Environment Variables

None.

## Local Development

Requires Python 3.13, [uv](https://docs.astral.sh/uv/), and
[Task](https://taskfile.dev). Run from the repository root:

- `task python:check` — lint, type-check, and check the line-length
  convention.
- `task python:fix` — auto-fix lint issues and format.

## Code Quality

`commons-python` is a single CLI with three subcommands, each a thin,
single-responsibility wrapper — composition (which checks to run, in what
order) is left to each consumer's own Taskfile/scripts, not baked into the
package:

- `commons-python ruff <args>` — forwards `<args>` to `ruff` with the bundled
  `assets/ruff.toml` injected via `--config`. All ruff subcommands/flags
  (`check`, `format`, `--fix`, paths) pass through untouched.
- `commons-python ty <args>` — forwards `<args>` to `ty` with the bundled
  `assets/ty.toml` injected via `--config-file`.
- `commons-python line-length <paths>` — ruff has no rule for a maximum
  *file* line count (only line-*width* rules), so this is a native Python
  check enforcing a 300-line-per-file maximum, skipping `.venv/`,
  `__pycache__/`, `.git/`, `build/`, `dist/`, and `*.egg-info/`.

## Deployment

Releases are driven by Release Please (`release-type: simple`), starting at
`1.0.0`. There is no PyPI-compatible registry on GitHub Packages, so this
package is not published anywhere — consumers add it as a git dependency
pinned to a release tag (e.g. via `uv add
"git+https://github.com/aimarchirico/commons@commons-python-v<version>#subdirectory=python/commons-python"`).
`plugin/` in this repo is the reference consumer.
