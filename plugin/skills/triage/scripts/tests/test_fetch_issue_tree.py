"""Tests for fetch_issue_tree.py, covering both the library call and the CLI."""

import json
import subprocess
import sys

import fetch_issue_tree as fit
import pytest

_REPO_OUTPUT = json.dumps({"owner": {"login": "acme"}, "name": "widgets"})


def _type_field(type_name: str | None) -> dict:
    nodes = [{"fieldValueByName": {"name": type_name}}] if type_name else []
    return {"projectItems": {"nodes": nodes}}


def _api_response(number: int, title: str, body: str, type_name: str | None) -> str:
    issue = {
        "number": number,
        "title": title,
        "body": body,
        **_type_field(type_name),
        "subIssues": {"nodes": []},
    }
    return json.dumps({"data": {"repository": {"issue": issue}}})


def test_get_issue_tree_resolves_owner_and_repo_then_fetches_tree() -> None:
    """Resolves owner/repo via `gh repo view`, then fetches the issue tree."""
    calls: list[list[str]] = []

    def fake_run_cmd(args: list[str]) -> str:
        calls.append(args)
        if args[:3] == ["gh", "repo", "view"]:
            return _REPO_OUTPUT
        return _api_response(10, "Closing issue", "Some body", "Story")

    result = fit.get_issue_tree(fake_run_cmd, "10")

    assert result == {
        "number": 10,
        "title": "Closing issue",
        "body": "Some body",
        "type": "Story",
        "children": [],
    }
    assert calls[1][:3] == ["gh", "api", "graphql"]
    assert "number=10" in calls[1]


def test_main_exits_when_issue_id_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """main() exits with an error when no issue ID is given."""
    monkeypatch.setattr(sys, "argv", ["fetch_issue_tree"])

    with pytest.raises(SystemExit):
        fit.main()


def test_main_exits_when_gh_is_not_installed(monkeypatch: pytest.MonkeyPatch) -> None:
    """main() fails fast when the gh CLI isn't on PATH."""
    monkeypatch.setattr(sys, "argv", ["fetch_issue_tree", "10"])
    monkeypatch.setattr(fit.project_preflight.shutil, "which", lambda _name: None)

    with pytest.raises(SystemExit):
        fit.main()


def test_main_prints_tree_as_json_to_stdout(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """main() prints the fetched tree as indented JSON on success."""
    monkeypatch.setattr(sys, "argv", ["fetch_issue_tree", "10"])
    monkeypatch.setattr(fit, "check_cli_dependencies", lambda: None)

    def fake_run_cmd(args: list[str]) -> str:
        if args[:3] == ["gh", "repo", "view"]:
            return _REPO_OUTPUT
        return _api_response(10, "Closing issue", "Some body", "Story")

    monkeypatch.setattr(fit, "_run_cmd", fake_run_cmd)

    fit.main()

    printed = json.loads(capsys.readouterr().out)
    assert printed == {
        "number": 10,
        "title": "Closing issue",
        "body": "Some body",
        "type": "Story",
        "children": [],
    }


def test_main_exits_when_gh_command_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    """main() exits cleanly when the underlying gh call fails."""
    monkeypatch.setattr(sys, "argv", ["fetch_issue_tree", "10"])
    monkeypatch.setattr(fit, "check_cli_dependencies", lambda: None)

    def fake_run_cmd(args: list[str]) -> str:
        raise subprocess.CalledProcessError(1, args)

    monkeypatch.setattr(fit, "_run_cmd", fake_run_cmd)

    with pytest.raises(SystemExit):
        fit.main()
