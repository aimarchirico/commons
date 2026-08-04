"""Check docstrings and comments enforcement in Python files.

Public declarations require docstrings (enforced by Ruff pydocstyle), while
docstrings on non-public declarations (prefixed with ``_``), orphaned string
literals with no owning declaration, and plain `#` line/block comments are
prohibited.
"""

import ast
import io
import sys
import tokenize
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

DocstringOwner = ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef

DOCSTRING_OWNER_TYPES = (
    ast.Module,
    ast.ClassDef,
    ast.FunctionDef,
    ast.AsyncFunctionDef,
)


def _is_excluded(path: Path) -> bool:
    return any(
        part in EXCLUDED_DIRS or part.endswith(".egg-info") for part in path.parts
    )


def _iter_python_files(root: Path) -> Iterator[Path]:
    if root.is_file():
        if root.suffix == ".py" and not _is_excluded(root):
            yield root
        return
    for path in root.rglob("*.py"):
        if not _is_excluded(path):
            yield path


def _docstring_stmt(owner: DocstringOwner) -> ast.Expr | None:
    body = getattr(owner, "body", None)
    if not body:
        return None
    stmt = body[0]
    if (
        isinstance(stmt, ast.Expr)
        and isinstance(stmt.value, ast.Constant)
        and isinstance(stmt.value.value, str)
    ):
        return stmt
    return None


def _owner_label(owner: DocstringOwner, file: Path) -> str:
    if isinstance(owner, ast.Module):
        return f"module '{file.stem}'"
    return f"declaration '{owner.name}'"


def _is_public(owner: DocstringOwner, file: Path) -> bool:
    if isinstance(owner, ast.Module):
        return file.stem == "__init__" or not file.stem.startswith("_")
    return not owner.name.startswith("_")


def _check_tokenize_comments(file: Path, content_bytes: bytes) -> list[str]:
    violations: list[str] = []
    try:
        tokens = tokenize.tokenize(io.BytesIO(content_bytes).readline)
        for tok in tokens:
            if tok.type == tokenize.COMMENT:
                if tok.start[0] == 1 and tok.string.startswith("#!"):
                    continue
                violations.append(f"{file}:{tok.start[0]}: Comments are prohibited.")
    except tokenize.TokenError:
        pass
    return violations


def _check_ast_docstrings(file: Path, content_bytes: bytes) -> list[str]:
    violations: list[str] = []
    try:
        source = content_bytes.decode("utf-8")
        tree = ast.parse(source, filename=str(file))
    except (SyntaxError, UnicodeDecodeError):
        return violations

    owners: dict[int, DocstringOwner] = {
        id(stmt): node
        for node in ast.walk(tree)
        if isinstance(node, DOCSTRING_OWNER_TYPES)
        and (stmt := _docstring_stmt(node)) is not None
    }

    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            continue

        owner = owners.get(id(node))
        if owner is None:
            violations.append(
                f"{file}:{node.lineno}: Orphaned string literal "
                "treated as a comment is prohibited.",
            )
        elif not _is_public(owner, file):
            violations.append(
                f"{file}:{node.lineno}: Docstring on non-public "
                f"{_owner_label(owner, file)} is prohibited.",
            )

    return violations


def _check_file_comments(file: Path) -> list[str]:
    try:
        content_bytes = file.read_bytes()
    except OSError:
        return []

    violations = _check_tokenize_comments(file, content_bytes)
    violations.extend(_check_ast_docstrings(file, content_bytes))
    return violations


def check_comments(paths: list[str]) -> int:
    """Walk the given paths and verify comment/docstring rules.

    Returns a process exit code (0 for success, 1 for violations).
    """
    violations: list[str] = []

    for arg in paths:
        for file in _iter_python_files(Path(arg)):
            violations.extend(_check_file_comments(file))

    if violations:
        for violation in violations:
            sys.stdout.write(f"{violation}\n")
        return 1

    return 0
