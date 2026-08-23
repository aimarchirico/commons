"""Tests for the suppression-reason check."""

from pathlib import Path

import pytest
from commons_python import suppressions


def _write(tmp_path: Path, source: str) -> Path:
    file = tmp_path / "sample.py"
    file.write_text(source, encoding="utf-8")
    return file


def test_noqa_without_a_reason_is_flagged(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A coded noqa carrying no justification fails."""
    _write(tmp_path, 'value = eval("1")  # noqa: S307\n')

    assert suppressions.check_suppressions([str(tmp_path)]) == 1
    assert "must state a reason" in capsys.readouterr().out


def test_noqa_with_a_reason_passes(tmp_path: Path) -> None:
    """A coded noqa followed by prose passes."""
    _write(tmp_path, 'value = eval("1")  # noqa: S307 - input is a literal\n')

    assert suppressions.check_suppressions([str(tmp_path)]) == 0


def test_multiple_codes_still_require_a_reason(tmp_path: Path) -> None:
    """A comma-separated code list is matched as one suppression."""
    _write(tmp_path, "value = 1  # noqa: S307, D103\n")

    assert suppressions.check_suppressions([str(tmp_path)]) == 1


def test_type_ignore_without_a_reason_is_flagged(tmp_path: Path) -> None:
    """A coded type ignore carrying no justification fails."""
    _write(tmp_path, 'value: int = "s"  # type: ignore[assignment]\n')

    assert suppressions.check_suppressions([str(tmp_path)]) == 1


def test_type_ignore_with_a_reason_passes(tmp_path: Path) -> None:
    """A coded type ignore followed by prose passes."""
    _write(tmp_path, 'value: int = "s"  # type: ignore[assignment] - stub is wrong\n')

    assert suppressions.check_suppressions([str(tmp_path)]) == 0


def test_ordinary_comments_are_left_alone(tmp_path: Path) -> None:
    """Comments that suppress nothing are none of this check's business."""
    _write(tmp_path, "# Guards against a firmware bug.\nvalue = 1\n")

    assert suppressions.check_suppressions([str(tmp_path)]) == 0


def test_uncoded_suppressions_are_left_to_ruff(tmp_path: Path) -> None:
    """Bare noqa and type ignore are PGH004/PGH003's job, not this check's."""
    _write(tmp_path, "import os  # noqa\nvalue = 1  # type: ignore\n")

    assert suppressions.check_suppressions([str(tmp_path)]) == 0


def test_unreadable_source_is_skipped(tmp_path: Path) -> None:
    """A file that cannot be tokenized yields no violations."""
    _write(tmp_path, 'value = "unterminated\n')

    assert suppressions.check_suppressions([str(tmp_path)]) == 0
