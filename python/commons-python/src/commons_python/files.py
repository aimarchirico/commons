"""Walk Python files for the native checks, skipping generated directories."""

from collections.abc import Iterator
from pathlib import Path

EXCLUDED_DIRS = {
    ".venv",
    "__pycache__",
    ".git",
    "build",
    "dist",
    "node_modules",
    ".pnpm",
    ".task",
    ".ruff_cache",
}


def is_excluded(path: Path) -> bool:
    """Report whether a path sits in a generated or vendored directory."""
    return any(
        part in EXCLUDED_DIRS or part.endswith(".egg-info") for part in path.parts
    )


def iter_python_files(root: Path) -> Iterator[Path]:
    """Yield every Python file under a root, or the root itself if it is one."""
    if root.is_file():
        if root.suffix == ".py" and not is_excluded(root):
            yield root
        return
    for path in root.rglob("*.py"):
        if not is_excluded(path):
            yield path
