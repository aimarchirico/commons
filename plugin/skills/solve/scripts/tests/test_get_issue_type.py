"""Tests for get_issue_type.py, covering both the library call and the CLI."""

import json
import subprocess
import sys

import get_issue_type as git
import pytest

_REPO_OUTPUT = json.dumps({"owner": {"login": "acme"}, "name": "widgets"})


def _api_response(type_name: str | None) -> str:
    if type_name is None:
        return json.dumps({"data": {"repository": {"issue": {"projectItems": {
            "nodes": [],
        }}}}})
    return json.dumps({"data": {"repository": {"issue": {"projectItems": {
        "nodes": [{"fieldValueByName": {"name": type_name}}],
    }}}}})


def test_get_issue_type_returns_type_field_value() -> None:
    """Returns the Type field's name when a project item has one."""
    calls: list[list[str]] = []

    def fake_run_cmd(args: list[str]) -> str:
        calls.append(args)
        if args[:3] == ["gh", "repo", "view"]:
            return _REPO_OUTPUT
        return _api_response("Bug")

    result = git.get_issue_type(fake_run_cmd, "42")

    assert result == "Bug"
    assert calls[1][:3] == ["gh", "api", "graphql"]
    assert "-F" in calls[1]
    assert "number=42" in calls[1]


def test_get_issue_type_returns_none_when_no_type_field() -> None:
    """Returns None when the issue has no linked project item with a Type."""
    def fake_run_cmd(args: list[str]) -> str:
        if args[:3] == ["gh", "repo", "view"]:
            return _REPO_OUTPUT
        return _api_response(None)

    result = git.get_issue_type(fake_run_cmd, "42")

    assert result is None


def test_main_exits_when_issue_id_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """main() exits with an error when no issue ID is given."""
    monkeypatch.setattr(sys, "argv", ["get_issue_type"])

    with pytest.raises(SystemExit):
        git.main()


def test_main_exits_when_gh_is_not_installed(monkeypatch: pytest.MonkeyPatch) -> None:
    """main() fails fast when the gh CLI isn't on PATH."""
    monkeypatch.setattr(sys, "argv", ["get_issue_type", "42"])
    monkeypatch.setattr(git.shutil, "which", lambda _name: None)

    with pytest.raises(SystemExit):
        git.main()


def test_main_prints_type_to_stdout(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """main() prints the resolved Type to stdout on success."""
    monkeypatch.setattr(sys, "argv", ["get_issue_type", "42"])
    monkeypatch.setattr(git.shutil, "which", lambda _name: "/usr/bin/gh")

    def fake_run_cmd(args: list[str]) -> str:
        if args[:3] == ["gh", "repo", "view"]:
            return _REPO_OUTPUT
        return _api_response("Story")

    monkeypatch.setattr(git, "_run_cmd", fake_run_cmd)

    git.main()

    assert capsys.readouterr().out == "Story\n"


def test_main_warns_to_stderr_when_no_type_found(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """main() warns on stderr, without raising, when no Type field is found."""
    monkeypatch.setattr(sys, "argv", ["get_issue_type", "42"])
    monkeypatch.setattr(git.shutil, "which", lambda _name: "/usr/bin/gh")

    def fake_run_cmd(args: list[str]) -> str:
        if args[:3] == ["gh", "repo", "view"]:
            return _REPO_OUTPUT
        return _api_response(None)

    monkeypatch.setattr(git, "_run_cmd", fake_run_cmd)

    git.main()

    assert "no linked project item with a" in capsys.readouterr().err


def test_main_exits_when_gh_command_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    """main() exits cleanly when the underlying gh call fails."""
    monkeypatch.setattr(sys, "argv", ["get_issue_type", "42"])
    monkeypatch.setattr(git.shutil, "which", lambda _name: "/usr/bin/gh")

    def fake_run_cmd(args: list[str]) -> str:
        raise subprocess.CalledProcessError(1, args)

    monkeypatch.setattr(git, "_run_cmd", fake_run_cmd)

    with pytest.raises(SystemExit):
        git.main()
