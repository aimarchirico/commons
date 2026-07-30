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
└── commons-python/     # shared ruff/ty config + CLI (see its own README)
```

Only `commons-python` exists today; adding a package means adding it to
`pyproject.toml`'s `members` list, following the same pattern.

## Local Development

Requires Python 3.13 and [Task](https://taskfile.dev). Run from the
repository root:

- `task python:check` — check all Python packages.
- `task python:fix` — auto-fix all Python packages.

## Deployment

Unlike `maven/` and `npm/`, GitHub Packages has no PyPI-compatible registry,
so packages here are not published anywhere. Each is released by Release
Please and consumed as a git dependency pinned to the resulting tag. See
[`commons-python/README.md`](commons-python/README.md#deployment) for
details.
