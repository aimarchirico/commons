"""Tests for the comments/docstring check."""

from pathlib import Path

from commons_python.comments import check_comments


def test_public_docstring_passes(tmp_path: Path) -> None:
    """A docstring on a public function is allowed."""
    file = tmp_path / "mod.py"
    file.write_text(
        '"""Module docstring."""\n\n\ndef foo():\n    """Foo docstring."""\n'
    )

    assert check_comments([str(tmp_path)]) == 0


def test_non_public_docstring_fails(tmp_path: Path, capsys) -> None:
    """A docstring on a non-public function is rejected."""
    file = tmp_path / "mod.py"
    file.write_text(
        '"""Module docstring."""\n\n\ndef _foo():\n    """Not allowed."""\n'
    )

    assert check_comments([str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "non-public" in out


def test_orphaned_string_literal_fails(tmp_path: Path, capsys) -> None:
    """A bare string expression with no owning declaration is rejected."""
    file = tmp_path / "mod.py"
    file.write_text(
        '"""Module docstring."""\n\n\n'
        'def foo():\n    """Foo docstring."""\n    "orphaned"\n'
    )

    assert check_comments([str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "Orphaned string literal" in out


def test_hash_comment_fails(tmp_path: Path, capsys) -> None:
    """A plain ``#`` comment is rejected."""
    file = tmp_path / "mod.py"
    file.write_text('"""Module docstring."""\n\n# not allowed\nx = 1\n')

    assert check_comments([str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "Comments are prohibited" in out


def test_shebang_is_exempt(tmp_path: Path) -> None:
    """A shebang on line 1 is not treated as a prohibited comment."""
    file = tmp_path / "mod.py"
    file.write_text('#!/usr/bin/env python3\n"""Module docstring."""\n')

    assert check_comments([str(tmp_path)]) == 0


def test_syntax_error_file_is_skipped(tmp_path: Path) -> None:
    """A file with invalid syntax is skipped rather than raising."""
    file = tmp_path / "mod.py"
    file.write_text("def foo(:\n")

    assert check_comments([str(tmp_path)]) == 0


def test_unreadable_file_is_skipped(tmp_path: Path, monkeypatch) -> None:
    """A file that cannot be read (OSError) is skipped rather than raising."""
    file = tmp_path / "mod.py"
    file.write_text('"""Module docstring."""\n')

    original_read_bytes = Path.read_bytes

    def _boom(self: Path) -> bytes:
        if self == file:
            raise OSError("boom")
        return original_read_bytes(self)

    monkeypatch.setattr(Path, "read_bytes", _boom)

    assert check_comments([str(tmp_path)]) == 0
