"""Tests for the dispatching CLI."""

import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any

import pytest
from commons_python import cli

EXPECTED_EXIT_CODE_EXTRA = 3
EXPECTED_EXIT_CODE_USAGE = 2


class _FakeCompletedProcess:
    def __init__(self, returncode: int) -> None:
        self.returncode = returncode


@pytest.mark.parametrize(
    ("tool", "binary", "config_flag", "asset_name"),
    [
        ("ruff", "ruff", "--config", "ruff.toml"),
        ("ty", "ty", "--config-file", "ty.toml"),
        ("coverage", "coverage", "--rcfile", "coverage.toml"),
    ],
)
def test_dispatches_wrapped_tool(
    monkeypatch: pytest.MonkeyPatch,
    tool: str,
    binary: str,
    config_flag: str,
    asset_name: str,
) -> None:
    """Each wrapped tool builds the expected command and forwards args/rc."""
    captured: dict[str, list[str]] = {}

    def fake_run(command: list[str], *, check: bool = False) -> _FakeCompletedProcess:
        _ = check
        captured["command"] = command
        return _FakeCompletedProcess(returncode=EXPECTED_EXIT_CODE_EXTRA)

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(sys, "argv", ["commons-python", tool, "check", "extra"])

    with pytest.raises(SystemExit) as exc_info:
        cli.main()

    assert exc_info.value.code == EXPECTED_EXIT_CODE_EXTRA
    command = captured["command"]
    assert command[0] == binary
    assert command[1] == "check"
    assert command[2] == config_flag
    assert command[3].endswith(asset_name)
    assert command[4:] == ["extra"]


def test_ruff_merges_a_consumer_local_config_onto_the_bundled_one(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A local ``ruff.toml``'s per-file-ignores are merged, not substituted.

    Ruff's own ``extend`` replaces whole tables like ``per-file-ignores``
    rather than merging them key-by-key, which would silently drop every
    ignore the bundled config declares (e.g. ``S101`` for tests) the
    moment a consumer added its own. The merge must keep both.
    """
    captured: dict[str, list[str]] = {}
    merged_config: dict[str, Any] = {}

    def fake_run(command: list[str], *, check: bool = False) -> _FakeCompletedProcess:
        _ = check
        captured["command"] = command
        merged_config.update(tomllib.loads(Path(command[3]).read_text()))
        return _FakeCompletedProcess(returncode=0)

    local_config = tmp_path / "ruff.toml"
    local_config.write_text('[lint.per-file-ignores]\n"*_bootstrap.py" = ["E402"]\n')

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(sys, "argv", ["commons-python", "ruff", "check"])
    monkeypatch.chdir(tmp_path)

    with pytest.raises(SystemExit) as exc_info:
        cli.main()

    assert exc_info.value.code == 0
    command = captured["command"]
    assert command[:3] == ["ruff", "check", "--config"]
    assert Path(command[3]) != local_config
    per_file_ignores = merged_config["lint"]["per-file-ignores"]
    assert per_file_ignores["*_bootstrap.py"] == ["E402"]
    assert "S101" in per_file_ignores["*tests*"]


def test_ruff_uses_bundled_config_without_a_local_one(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """With no local ``ruff.toml``, the bundled config is used directly."""
    captured: dict[str, list[str]] = {}

    def fake_run(command: list[str], *, check: bool = False) -> _FakeCompletedProcess:
        _ = check
        captured["command"] = command
        return _FakeCompletedProcess(returncode=0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(sys, "argv", ["commons-python", "ruff", "check"])
    monkeypatch.chdir(tmp_path)

    with pytest.raises(SystemExit):
        cli.main()

    assert captured["command"][3].endswith("ruff.toml")
    assert "commons_python" in captured["command"][3]


def test_dispatches_pytest(monkeypatch: pytest.MonkeyPatch) -> None:
    """``pytest`` tool forwards args and injects coverage.toml config."""
    captured: dict[str, list[str]] = {}

    def fake_run(command: list[str], *, check: bool = False) -> _FakeCompletedProcess:
        _ = check
        captured["command"] = command
        return _FakeCompletedProcess(returncode=0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(sys, "argv", ["commons-python", "pytest", "-v"])

    with pytest.raises(SystemExit) as exc_info:
        cli.main()

    assert exc_info.value.code == 0
    command = captured["command"]
    assert command[0] == "pytest"
    assert command[1] == "--cov=."
    assert command[2] == "--cov-config"
    assert command[3].endswith("coverage.toml")
    assert command[4:] == ["-v"]


def test_commons_check_dispatches_to_native_checks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``commons check`` runs both checks, exiting non-zero if either fails."""
    calls: dict[str, list[str]] = {}

    def fake_line_length(paths: list[str]) -> int:
        calls["line_length"] = paths
        return 0

    def fake_suppressions(paths: list[str]) -> int:
        calls["suppressions"] = paths
        return 1

    monkeypatch.setattr(
        "commons_python.line_length.check_line_length",
        fake_line_length,
    )
    monkeypatch.setattr(
        "commons_python.suppressions.check_suppressions",
        fake_suppressions,
    )
    monkeypatch.setattr(sys, "argv", ["commons-python", "commons", "check", "src"])

    with pytest.raises(SystemExit) as exc_info:
        cli.main()

    assert exc_info.value.code == 1
    assert calls["line_length"] == ["src"]
    assert calls["suppressions"] == ["src"]


def test_commons_check_passes_when_both_succeed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``commons check`` exits 0 when both native checks succeed."""
    monkeypatch.setattr(
        "commons_python.line_length.check_line_length",
        lambda _paths: 0,
    )
    monkeypatch.setattr(
        "commons_python.suppressions.check_suppressions",
        lambda _paths: 0,
    )
    monkeypatch.setattr(sys, "argv", ["commons-python", "commons", "check"])

    with pytest.raises(SystemExit) as exc_info:
        cli.main()

    assert exc_info.value.code == 0


def test_unknown_tool_prints_usage_and_exits_2(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """An unrecognized first argument prints usage to stderr and exits 2."""
    monkeypatch.setattr(sys, "argv", ["commons-python", "bogus"])

    with pytest.raises(SystemExit) as exc_info:
        cli.main()

    assert exc_info.value.code == EXPECTED_EXIT_CODE_USAGE
    assert "usage" in capsys.readouterr().err
