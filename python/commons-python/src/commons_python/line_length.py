"""Check that Python files stay under a maximum line count.

Ruff has no rule expressing a maximum file length, so this script covers
that convention on top of the bundled ruff config.
"""

import sys
from pathlib import Path

from commons_python.files import iter_python_files

MAX_LINES = 300


def check_line_length(paths: list[str]) -> int:
    """Walk the given paths and flag files over ``MAX_LINES``.

    Returns a process exit code.
    """
    violations: list[str] = []

    for arg in paths:
        for file in iter_python_files(Path(arg)):
            line_count = sum(1 for _ in file.open(encoding="utf-8"))
            if line_count > MAX_LINES:
                violations.append(f"{file}: {line_count} lines (max {MAX_LINES})")

    if violations:
        for violation in violations:
            sys.stdout.write(f"{violation}\n")
        return 1

    return 0
