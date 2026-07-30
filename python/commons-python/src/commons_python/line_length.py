"""Check that Python files stay under a maximum line count.

Ruff has no rule expressing a maximum file length, so this script covers
that convention on top of the bundled ruff config.
"""

import sys
from pathlib import Path

MAX_LINES = 300

EXCLUDED_DIRS = {".venv", "__pycache__", ".git", "build", "dist"}


def _is_excluded(path: Path) -> bool:
    return any(part in EXCLUDED_DIRS or part.endswith(".egg-info") for part in path.parts)


def _iter_python_files(root: Path):
    if root.is_file():
        if root.suffix == ".py" and not _is_excluded(root):
            yield root
        return
    for path in root.rglob("*.py"):
        if not _is_excluded(path):
            yield path


def main() -> None:
    """Walk the given paths (default ``.``) and flag files over ``MAX_LINES``."""
    args = sys.argv[1:] or ["."]
    violations: list[str] = []

    for arg in args:
        for file in _iter_python_files(Path(arg)):
            line_count = sum(1 for _ in file.open(encoding="utf-8"))
            if line_count > MAX_LINES:
                violations.append(f"{file}: {line_count} lines (max {MAX_LINES})")

    if violations:
        for violation in violations:
            print(violation)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
