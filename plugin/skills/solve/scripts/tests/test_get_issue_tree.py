"""Tests for get_issue_tree.py, covering both the library call and the CLI."""

import json
import subprocess
import sys

import get_issue_tree as git
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
        return _api_response(42, "Parent", "Parent body", "Task")

    result = git.get_issue_tree(fake_run_cmd, "42")

    assert result == {
        "number": 42,
        "title": "Parent",
        "body": "Parent body",
        "type": "Task",
        "children": [],
    }
    assert calls[1][:3] == ["gh", "api", "graphql"]
    assert "number=42" in calls[1]


def test_main_exits_when_issue_id_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """main() exits with an error when no issue ID is given."""
    monkeypatch.setattr(sys, "argv", ["get_issue_tree"])

    with pytest.raises(SystemExit):
        git.main()


def test_main_exits_when_gh_is_not_installed(monkeypatch: pytest.MonkeyPatch) -> None:
    """main() fails fast when the gh CLI isn't on PATH."""
    monkeypatch.setattr(sys, "argv", ["get_issue_tree", "42"])
    monkeypatch.setattr(git.project_preflight.shutil, "which", lambda _name: None)

    with pytest.raises(SystemExit):
        git.main()


_PROJECTS_RESPONSE = json.dumps(
    {
        "data": {
            "repository": {
                "projectsV2": {
                    "nodes": [
                        {
                            "id": "PROJ_1",
                            "number": 9,
                            "title": "Widgets",
                            "closed": False,
                        },
                    ],
                },
            },
        },
    },
)

_OPTS = [{"id": "t1", "name": "Story"}]
_FIELDS_RESPONSE = json.dumps(
    {
        "fields": [
            {"id": "F_TYPE", "name": "Type", "options": _OPTS},
            {"id": "F_PRIO", "name": "Priority", "options": _OPTS},
        ],
    },
)


def _mock_cmd_handler(args: list[str]) -> str:
    if args[:3] == ["gh", "repo", "view"]:
        return _REPO_OUTPUT
    if args[:3] == ["gh", "project", "field-list"]:
        return _FIELDS_RESPONSE
    if "projectsV2" in "".join(args):
        return _PROJECTS_RESPONSE
    return _api_response(42, "Parent", "Parent body", "Task")


def test_main_prints_tree_as_json_to_stdout(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """main() prints the fetched tree as indented JSON on success."""
    monkeypatch.setattr(sys, "argv", ["get_issue_tree", "42"])
    monkeypatch.setattr(git.project_preflight, "check_cli_dependencies", lambda: None)

    monkeypatch.setattr(git, "_run_cmd", _mock_cmd_handler)

    git.main()

    printed = json.loads(capsys.readouterr().out)
    assert printed == {
        "number": 42,
        "title": "Parent",
        "body": "Parent body",
        "type": "Task",
        "children": [],
    }


def test_main_exits_when_gh_command_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    """main() exits cleanly when the underlying gh call fails."""
    monkeypatch.setattr(sys, "argv", ["get_issue_tree", "42"])
    monkeypatch.setattr(
        git.project_preflight.shutil,
        "which",
        lambda _name: "/usr/bin/gh",
    )

    def fake_run_cmd(args: list[str]) -> str:
        raise subprocess.CalledProcessError(1, args)

    monkeypatch.setattr(git, "_run_cmd", fake_run_cmd)

    with pytest.raises(SystemExit):
        git.main()
