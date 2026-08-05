"""Tests for create_issues.py, covering the recursive creator and the CLI."""

import json
import subprocess
import sys
from pathlib import Path

import create_issues as ci
import pytest

_REPO_OUTPUT = json.dumps({"owner": {"login": "acme"}, "name": "widgets"})
_PROJECTS_RESPONSE = json.dumps({"data": {"repository": {"projectsV2": {"nodes": [
    {"id": "PID", "number": 9, "title": "Widgets", "closed": False},
]}}}})
_FIELDS_RESPONSE = json.dumps({"fields": [
    {"id": "TID", "name": "Type", "options": [{"id": "t1", "name": "Task"}]},
    {"id": "PRID", "name": "Priority", "options": [{"id": "p1", "name": "P1"}]},
]})

_NO_PROJECT_INFO = (None, None, None, None, {})


def _project_info(project_id: str | None = "PID") -> tuple[
    int | None, str | None, str | None, str | None, dict[str, object],
]:
    return (9, project_id, "TID", "PRID", json.loads(_FIELDS_RESPONSE))


def test_create_issue_recursive_skips_items_without_a_title(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """No gh call is made for an item missing a title."""
    calls: list[list[str]] = []

    def fake_run_cmd(args: list[str]) -> str:
        calls.append(args)
        return ""

    monkeypatch.setattr(ci, "run_cmd", fake_run_cmd)

    ci.create_issue_recursive({}, None, "acme", _NO_PROJECT_INFO)

    assert calls == []


def test_create_issue_recursive_creates_a_top_level_issue(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A top-level item creates a plain issue, with no project linked."""
    calls: list[list[str]] = []

    def fake_run_cmd(args: list[str]) -> str:
        calls.append(args)
        return "https://github.com/acme/widgets/issues/101"

    monkeypatch.setattr(ci, "run_cmd", fake_run_cmd)

    ci.create_issue_recursive(
        {"title": "Fix bug", "body": "desc"}, None, "acme", _NO_PROJECT_INFO,
    )

    assert calls == [["gh", "issue", "create", "--title", "Fix bug", "--body", "desc"]]


def test_create_issue_recursive_creates_a_child_issue_with_parent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A nested item creates a sub-issue linked to the given parent ID."""
    calls: list[list[str]] = []

    def fake_run_cmd(args: list[str]) -> str:
        calls.append(args)
        return "https://github.com/acme/widgets/issues/102"

    monkeypatch.setattr(ci, "run_cmd", fake_run_cmd)

    ci.create_issue_recursive(
        {"title": "Child"}, "101", "acme", _NO_PROJECT_INFO,
    )

    assert calls == [[
        "gh", "sub-issue", "create",
        "--title", "Child", "--body", "", "--parent", "101",
    ]]


def test_create_issue_recursive_links_to_project_and_sets_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When a project is linked, the new issue is added and Type/Priority set."""
    calls: list[list[str]] = []

    def fake_run_cmd(args: list[str]) -> str:
        calls.append(args)
        if args[:3] == ["gh", "issue", "create"]:
            return "https://github.com/acme/widgets/issues/101"
        if args[:3] == ["gh", "project", "item-add"]:
            return json.dumps({"id": "ITEM1"})
        return ""

    monkeypatch.setattr(ci, "run_cmd", fake_run_cmd)

    ci.create_issue_recursive(
        {"title": "Fix bug", "type": "Task", "priority": "P1"},
        None, "acme", _project_info(),
    )

    item_add_call = next(c for c in calls if c[:3] == ["gh", "project", "item-add"])
    assert item_add_call == [
        "gh", "project", "item-add", "9",
        "--owner", "acme", "--url", "https://github.com/acme/widgets/issues/101",
        "--format", "json",
    ]
    edit_calls = [c for c in calls if c[:3] == ["gh", "project", "item-edit"]]
    expected_edit_count = 2
    assert len(edit_calls) == expected_edit_count
    assert edit_calls[0][-1] == "t1"
    assert edit_calls[1][-1] == "p1"


def test_create_issue_recursive_warns_when_project_add_fails(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A failed project item-add is reported as a warning, not an exception."""
    def fake_run_cmd(args: list[str]) -> str:
        if args[:3] == ["gh", "issue", "create"]:
            return "https://github.com/acme/widgets/issues/101"
        return "not json"

    monkeypatch.setattr(ci, "run_cmd", fake_run_cmd)

    ci.create_issue_recursive({"title": "Fix bug"}, None, "acme", _project_info())

    assert "Warning: Failed to add/configure project fields" in capsys.readouterr().err


def test_create_issue_recursive_recurses_into_children(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Children are created after the parent, passing the parent's issue ID."""
    calls: list[list[str]] = []

    def fake_run_cmd(args: list[str]) -> str:
        calls.append(args)
        if args[1] == "issue":
            return "https://github.com/acme/widgets/issues/101"
        return "https://github.com/acme/widgets/issues/102"

    monkeypatch.setattr(ci, "run_cmd", fake_run_cmd)

    ci.create_issue_recursive(
        {"title": "Parent", "children": [{"title": "Child"}]},
        None, "acme", _NO_PROJECT_INFO,
    )

    child_call = next(c for c in calls if c[0:2] == ["gh", "sub-issue"])
    assert "--parent" in child_call
    assert child_call[child_call.index("--parent") + 1] == "101"


def test_main_exits_when_json_path_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """main() exits with an error when no JSON path is given."""
    monkeypatch.setattr(sys, "argv", ["create_issues"])

    with pytest.raises(SystemExit):
        ci.main()


def test_main_exits_when_file_does_not_exist(monkeypatch: pytest.MonkeyPatch) -> None:
    """main() exits when the given JSON path doesn't exist."""
    monkeypatch.setattr(sys, "argv", ["create_issues", "/no/such/file.json"])

    with pytest.raises(SystemExit):
        ci.main()


def test_main_exits_and_cleans_up_when_json_is_invalid(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    """main() exits and deletes the file when it isn't valid JSON."""
    issues_file = tmp_path / "issues.json"
    issues_file.write_text("not json")
    monkeypatch.setattr(sys, "argv", ["create_issues", str(issues_file)])

    with pytest.raises(SystemExit):
        ci.main()

    assert not issues_file.exists()


def _install_gh(monkeypatch: pytest.MonkeyPatch, responses: dict[str, str]) -> None:
    fixed_responses: dict[tuple[str, ...], str] = {
        ("gh", "extension", "list"): "gh-sub-issue",
        ("gh", "repo", "view"): responses.get("repo_view", _REPO_OUTPUT),
        ("gh", "api", "graphql"): responses.get("graphql", _PROJECTS_RESPONSE),
        ("gh", "project", "field-list"): responses.get("fields", _FIELDS_RESPONSE),
        ("gh", "issue", "create"): "https://github.com/acme/widgets/issues/101",
        ("gh", "project", "item-add"): json.dumps({"id": "ITEM1"}),
    }

    def fake_run_cmd(args: list[str]) -> str:
        return fixed_responses.get(tuple(args[:3]), "")

    def fake_subprocess_run(
        _args: list[str], **_kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args=[], returncode=0)

    monkeypatch.setattr(ci.shutil, "which", lambda _name: "/usr/bin/gh")
    monkeypatch.setattr(ci.subprocess, "run", fake_subprocess_run)
    monkeypatch.setattr(ci, "run_cmd", fake_run_cmd)


def test_main_exits_when_project_setup_is_invalid(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    """main() exits before creating anything when project validation fails."""
    issues_file = tmp_path / "issues.json"
    issues_file.write_text(json.dumps({"items": [
        {"title": "Fix bug", "type": "NotAType", "body": ""},
    ]}))
    monkeypatch.setattr(sys, "argv", ["create_issues", str(issues_file)])
    _install_gh(monkeypatch, {})

    with pytest.raises(SystemExit):
        ci.main()


def test_main_creates_issues_and_cleans_up_on_success(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """main() creates every item, reports success, and deletes the input file."""
    issues_file = tmp_path / "issues.json"
    issues_file.write_text(json.dumps({"items": [
        {"title": "Fix bug", "type": "Task", "priority": "P1", "body": ""},
    ]}))
    monkeypatch.setattr(sys, "argv", ["create_issues", str(issues_file)])
    _install_gh(monkeypatch, {})

    ci.main()

    assert "Successfully created all issues." in capsys.readouterr().out
    assert not issues_file.exists()
