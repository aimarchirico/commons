"""Tests for the line-length check."""

from pathlib import Path

from commons_python.line_length import MAX_LINES, check_line_length


def _write_lines(path: Path, count: int) -> None:
    path.write_text("\n".join(f"x = {i}" for i in range(count)) + "\n")


def test_file_under_limit_passes(tmp_path: Path) -> None:
    """A file with fewer than MAX_LINES lines produces no violation."""
    file = tmp_path / "short.py"
    _write_lines(file, MAX_LINES - 1)

    assert check_line_length([str(tmp_path)]) == 0


def test_file_over_limit_fails(tmp_path: Path, capsys) -> None:
    """A file with more than MAX_LINES lines is reported as a violation."""
    file = tmp_path / "long.py"
    _write_lines(file, MAX_LINES + 1)

    assert check_line_length([str(tmp_path)]) == 1
    assert str(file) in capsys.readouterr().out


def test_excluded_dir_is_skipped(tmp_path: Path) -> None:
    """Files under an excluded directory are not checked."""
    excluded = tmp_path / ".venv" / "pkg"
    excluded.mkdir(parents=True)
    _write_lines(excluded / "long.py", MAX_LINES + 1)

    assert check_line_length([str(tmp_path)]) == 0


def test_single_file_argument(tmp_path: Path) -> None:
    """Passing a single file path (not a directory) checks that file."""
    file = tmp_path / "long.py"
    _write_lines(file, MAX_LINES + 1)

    assert check_line_length([str(file)]) == 1
