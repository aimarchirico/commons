"""Check docstrings and comments enforcement in Python files.

Public declarations require docstrings (enforced by Ruff pydocstyle), while
docstrings on non-public declarations (prefixed with ``_``) and plain `#`
line/block comments are prohibited.
"""

import ast
import io
from pathlib import Path
import tokenize

EXCLUDED_DIRS = {".venv", "__pycache__", ".git", "build", "dist"}


def _is_excluded(path: Path) -> bool:
    return any(
        part in EXCLUDED_DIRS or part.endswith(".egg-info") for part in path.parts
    )


def _iter_python_files(root: Path):
    if root.is_file():
        if root.suffix == ".py" and not _is_excluded(root):
            yield root
        return
    for path in root.rglob("*.py"):
        if not _is_excluded(path):
            yield path


def check_comments(paths: list[str]) -> int:
    """Walk the given paths and verify comment/docstring rules.

    Returns a process exit code (0 for success, 1 for violations).
    """
    violations: list[str] = []

    for arg in paths:
        for file in _iter_python_files(Path(arg)):
            try:
                content_bytes = file.read_bytes()
            except OSError:
                continue

            try:
                tokens = tokenize.tokenize(io.BytesIO(content_bytes).readline)
                for tok in tokens:
                    if tok.type == tokenize.COMMENT:
                        if tok.start[0] == 1 and tok.string.startswith("#!"):
                            continue
                        violations.append(
                            f"{file}:{tok.start[0]}: Comments are prohibited."
                        )
            except tokenize.TokenError:
                pass

            try:
                source = content_bytes.decode("utf-8")
                tree = ast.parse(source, filename=str(file))
            except (SyntaxError, UnicodeDecodeError):
                continue

            for node in ast.walk(tree):
                if isinstance(
                    node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
                ):
                    if (
                        node.name.startswith("_")
                        and ast.get_docstring(node) is not None
                    ):
                        msg = (
                            f"{file}:{node.lineno}: Docstring on "
                            f"non-public declaration '{node.name}' "
                            "is prohibited."
                        )
                        violations.append(msg)

    if violations:
        for violation in violations:
            print(violation)
        return 1

    return 0
