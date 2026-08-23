"""Check that inline suppressions state why they are there.

Ruff enforces that ``noqa`` and ``type: ignore`` name specific codes (PGH003,
PGH004) but not that they justify themselves.
"""

import re
import sys
import tokenize
from pathlib import Path

from commons_python.files import iter_python_files

SUPPRESSION = re.compile(
    r"#\s*(?:noqa:\s*[A-Z]+[0-9]+(?:\s*,\s*[A-Z]+[0-9]+)*"
    r"|type:\s*ignore\[[^\]]+\])(?P<reason>.*)$",
)

REASON_SEPARATORS = " \t-:#,"


def _violations_in(file: Path) -> list[str]:
    try:
        with file.open("rb") as handle:
            tokens = list(tokenize.tokenize(handle.readline))
    except (tokenize.TokenError, SyntaxError, OSError):
        return []

    violations: list[str] = []
    for token in tokens:
        if token.type != tokenize.COMMENT:
            continue
        match = SUPPRESSION.search(token.string)
        if match and not match.group("reason").strip(REASON_SEPARATORS):
            violations.append(
                f"{file}:{token.start[0]}: Suppression must state a reason "
                "after its codes.",
            )
    return violations


def check_suppressions(paths: list[str]) -> int:
    """Walk the given paths and flag suppressions carrying no reason.

    Returns a process exit code.
    """
    violations: list[str] = []

    for arg in paths:
        for file in iter_python_files(Path(arg)):
            violations.extend(_violations_in(file))

    if violations:
        for violation in violations:
            sys.stdout.write(f"{violation}\n")
        return 1

    return 0
