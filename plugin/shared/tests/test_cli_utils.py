"""Tests for shared cli_utils module."""

import subprocess

import pytest

from shared import cli_utils


def test_run_cmd_returns_stripped_output(monkeypatch: pytest.MonkeyPatch) -> None:
    """Returns stripped stdout when command succeeds."""
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *_a, **_k: subprocess.CompletedProcess([], 0, "  hello world\n ", ""),
    )
    assert cli_utils.run_cmd(["echo", "hello"]) == "hello world"


def test_check_cli_dependencies_exits_when_gh_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exits with SystemExit when gh executable is missing."""
    monkeypatch.setattr(cli_utils.shutil, "which", lambda _name: None)
    with pytest.raises(SystemExit):
        cli_utils.check_cli_dependencies()
