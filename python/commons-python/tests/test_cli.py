"""Tests for the dispatching CLI."""

import subprocess
import sys

import pytest

from commons_python import cli


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

    def fake_run(command: list[str], check: bool) -> _FakeCompletedProcess:
        captured["command"] = command
        return _FakeCompletedProcess(returncode=3)

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(sys, "argv", ["commons-python", tool, "check", "extra"])

    with pytest.raises(SystemExit) as exc_info:
        cli.main()

    assert exc_info.value.code == 3
    command = captured["command"]
    assert command[0] == binary
    assert command[1] == "check"
    assert command[2] == config_flag
    assert command[3].endswith(asset_name)
    assert command[4:] == ["extra"]


def test_dispatches_pytest(monkeypatch: pytest.MonkeyPatch) -> None:
    """``pytest`` tool forwards args and injects coverage.toml config."""
    captured: dict[str, list[str]] = {}

    def fake_run(command: list[str], check: bool) -> _FakeCompletedProcess:
        captured["command"] = command
        return _FakeCompletedProcess(returncode=0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(sys, "argv", ["commons-python", "pytest", "-v"])

    with pytest.raises(SystemExit) as exc_info:
        cli.main()

    assert exc_info.value.code == 0
    command = captured["command"]
    assert command[0] == "pytest"
    assert command[1] == "--cov"
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

    def fake_comments(paths: list[str]) -> int:
        calls["comments"] = paths
        return 1

    monkeypatch.setattr(
        "commons_python.line_length.check_line_length", fake_line_length
    )
    monkeypatch.setattr("commons_python.comments.check_comments", fake_comments)
    monkeypatch.setattr(sys, "argv", ["commons-python", "commons", "check", "src"])

    with pytest.raises(SystemExit) as exc_info:
        cli.main()

    assert exc_info.value.code == 1
    assert calls["line_length"] == ["src"]
    assert calls["comments"] == ["src"]


def test_commons_check_passes_when_both_succeed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``commons check`` exits 0 when both native checks succeed."""
    monkeypatch.setattr(
        "commons_python.line_length.check_line_length", lambda paths: 0
    )
    monkeypatch.setattr("commons_python.comments.check_comments", lambda paths: 0)
    monkeypatch.setattr(sys, "argv", ["commons-python", "commons", "check"])

    with pytest.raises(SystemExit) as exc_info:
        cli.main()

    assert exc_info.value.code == 0


def test_unknown_tool_prints_usage_and_exits_2(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    """An unrecognized first argument prints usage to stderr and exits 2."""
    monkeypatch.setattr(sys, "argv", ["commons-python", "bogus"])

    with pytest.raises(SystemExit) as exc_info:
        cli.main()

    assert exc_info.value.code == 2
    assert "usage" in capsys.readouterr().err
