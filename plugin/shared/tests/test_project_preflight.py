"""Tests for the shared project_preflight module."""

import json
import subprocess

import pytest

from shared import project_preflight as pf


def test_check_cli_dependencies_exits_when_gh_not_in_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exits with SystemExit when gh executable is missing."""
    monkeypatch.setattr(pf.shutil, "which", lambda _name: None)
    with pytest.raises(SystemExit):
        pf.check_cli_dependencies()


def test_check_cli_dependencies_exits_when_auth_status_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exits with SystemExit when gh auth status fails."""
    monkeypatch.setattr(pf.shutil, "which", lambda _name: "/usr/bin/gh")

    def mock_run(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        raise subprocess.CalledProcessError(1, ["gh", "auth", "status"])

    monkeypatch.setattr(subprocess, "run", mock_run)
    with pytest.raises(SystemExit):
        pf.check_cli_dependencies()


def test_check_cli_dependencies_succeeds_when_authenticated(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Succeeds without error when gh CLI is installed and authenticated."""
    monkeypatch.setattr(pf.shutil, "which", lambda _name: "/usr/bin/gh")
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *_a, **_k: subprocess.CompletedProcess(["gh", "auth", "status"], 0),
    )
    pf.check_cli_dependencies()


def test_resolve_project_context_single_project() -> None:
    """Returns project details when a single active open project is returned."""
    repo_data = json.dumps({"owner": {"login": "acme"}, "name": "widgets"})
    node = {"id": "P1", "number": 9, "title": "Widgets Board", "closed": False}
    api_data = json.dumps({"data": {"repository": {"projectsV2": {"nodes": [node]}}}})

    def mock_run_cmd(args: list[str]) -> str:
        return repo_data if args[:4] == ["gh", "repo", "view", "--json"] else api_data

    ctx = pf.resolve_project_context(mock_run_cmd)
    assert ctx == ("acme", "widgets", 9, "P1", "acme")


def test_resolve_project_context_disambiguates_multiple_projects() -> None:
    """Selects matching title-cased project when multiple active projects exist."""
    repo_data = json.dumps({"owner": {"login": "acme"}, "name": "widgets"})
    nodes = [
        {"id": "P1", "number": 9, "title": "Widgets", "closed": False},
        {"id": "P2", "number": 10, "title": "Other", "closed": False},
    ]
    api_data = json.dumps({"data": {"repository": {"projectsV2": {"nodes": nodes}}}})

    def mock_run_cmd(args: list[str]) -> str:
        return repo_data if args[:4] == ["gh", "repo", "view", "--json"] else api_data

    ctx = pf.resolve_project_context(mock_run_cmd)
    assert (ctx[2], ctx[3]) == (9, "P1")


def test_resolve_project_context_raises_when_no_projects_exist() -> None:
    """Raises ProjectPreflightError when no open active projects exist."""
    repo_data = json.dumps({"owner": {"login": "acme"}, "name": "widgets"})
    api_data = json.dumps({"data": {"repository": {"projectsV2": {"nodes": []}}}})

    def mock_run_cmd(args: list[str]) -> str:
        return repo_data if args[:4] == ["gh", "repo", "view", "--json"] else api_data

    with pytest.raises(pf.ProjectPreflightError):
        pf.resolve_project_context(mock_run_cmd)


def test_resolve_project_context_raises_when_repo_view_fails() -> None:
    """Raises ProjectPreflightError when gh repo view command fails."""

    def mock_run_cmd(args: list[str]) -> str:
        raise subprocess.CalledProcessError(1, args)

    with pytest.raises(pf.ProjectPreflightError):
        pf.resolve_project_context(mock_run_cmd)


def test_resolve_project_context_raises_when_graphql_fails() -> None:
    """Raises ProjectPreflightError when GraphQL query fails."""
    repo_data = json.dumps({"owner": {"login": "acme"}, "name": "widgets"})

    def mock_run_cmd(args: list[str]) -> str:
        if args[:4] == ["gh", "repo", "view", "--json"]:
            return repo_data
        raise subprocess.CalledProcessError(1, args)

    with pytest.raises(pf.ProjectPreflightError):
        pf.resolve_project_context(mock_run_cmd)


def test_resolve_project_context_raises_when_multiple_ambiguous_projects() -> None:
    """Raises ProjectPreflightError when multiple open projects match no title."""
    repo_data = json.dumps({"owner": {"login": "acme"}, "name": "widgets"})
    nodes = [
        {"id": "P1", "number": 1, "title": "Board A", "closed": False},
        {"id": "P2", "number": 2, "title": "Board B", "closed": False},
    ]
    api_data = json.dumps({"data": {"repository": {"projectsV2": {"nodes": nodes}}}})

    def mock_run_cmd(args: list[str]) -> str:
        return repo_data if args[:4] == ["gh", "repo", "view", "--json"] else api_data

    with pytest.raises(pf.ProjectPreflightError):
        pf.resolve_project_context(mock_run_cmd)


def test_run_project_preflight_exits_when_no_projects_exist(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exits with SystemExit when project preflight fails."""
    monkeypatch.setattr(pf.shutil, "which", lambda _name: "/usr/bin/gh")
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *_a, **_k: subprocess.CompletedProcess([], 0, "", ""),
    )
    repo_data = json.dumps({"owner": {"login": "acme"}, "name": "widgets"})
    api_data = json.dumps({"data": {"repository": {"projectsV2": {"nodes": []}}}})

    def mock_run_cmd(args: list[str]) -> str:
        return repo_data if args[:3] == ["gh", "repo", "view"] else api_data

    with pytest.raises(SystemExit):
        pf.run_project_preflight(mock_run_cmd, require_fields=False)


def test_fetch_project_fields_extracts_type_and_priority() -> None:
    """Correctly parses Type and Priority field IDs."""
    opts = [{"id": "t1", "name": "Task"}]
    fields_data = json.dumps(
        {
            "fields": [
                {"id": "F_TYPE", "name": "Type", "options": opts},
                {"id": "F_PRIO", "name": "Priority", "options": opts},
            ],
        },
    )

    def mock_run_cmd(_args: list[str]) -> str:
        return fields_data

    type_id, prio_id, _data, errors = pf.fetch_project_fields(mock_run_cmd, "acme", 9)
    assert (type_id, prio_id, errors) == ("F_TYPE", "F_PRIO", [])


def test_fetch_project_fields_flags_empty_options() -> None:
    """Reports error when Type or Priority field has no options configured."""
    fields_data = json.dumps(
        {
            "fields": [
                {"id": "F_TYPE", "name": "Type", "options": []},
                {"id": "F_PRIO", "name": "Priority", "options": []},
            ],
        },
    )

    def mock_run_cmd(_args: list[str]) -> str:
        return fields_data

    _t_id, _p_id, _data, errors = pf.fetch_project_fields(mock_run_cmd, "acme", 9)
    expected_errors = 2
    assert len(errors) == expected_errors
    assert "no options configured" in errors[0]


def test_validate_item_options_checks_used_values() -> None:
    """Returns errors when items specify unknown Type or Priority options."""
    fields_data = {
        "fields": [
            {"name": "Type", "options": [{"name": "Task"}, {"name": "Bug"}]},
            {"name": "Priority", "options": [{"name": "P1"}]},
        ],
    }
    items = [
        {
            "title": "A",
            "type": "Task",
            "priority": "P1",
            "children": [{"title": "B", "type": "UnknownType", "priority": "P2"}],
        },
    ]
    errors = pf.validate_item_options(items, fields_data)
    expected_errors = 2
    assert len(errors) == expected_errors
    assert "Type value 'UnknownType'" in errors[0]
    assert "Priority value 'P2'" in errors[1]


def test_fetch_project_fields_returns_errors_on_command_failure() -> None:
    """Returns errors list when field lookup command fails."""

    def mock_run_cmd(args: list[str]) -> str:
        raise subprocess.CalledProcessError(1, args)

    _type_id, _prio_id, _data, errors = pf.fetch_project_fields(mock_run_cmd, "acme", 9)
    assert len(errors) >= 1
    assert "Could not retrieve project fields" in errors[0]


def test_run_project_preflight_exits_when_fields_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exits with SystemExit when required fields are missing on project."""
    monkeypatch.setattr(pf.shutil, "which", lambda _name: "/usr/bin/gh")
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *_a, **_k: subprocess.CompletedProcess([], 0, "", ""),
    )
    repo_data = json.dumps({"owner": {"login": "acme"}, "name": "widgets"})
    node = {"id": "P1", "number": 9, "title": "Widgets", "closed": False}
    api_data = json.dumps({"data": {"repository": {"projectsV2": {"nodes": [node]}}}})
    empty_fields = json.dumps({"fields": []})

    def mock_run_cmd(args: list[str]) -> str:
        if args[:3] == ["gh", "repo", "view"]:
            return repo_data
        if args[:3] == ["gh", "project", "field-list"]:
            return empty_fields
        return api_data

    with pytest.raises(SystemExit):
        pf.run_project_preflight(mock_run_cmd, require_fields=True)


def test_run_project_preflight_succeeds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Returns preflight dictionary when project context and fields are valid."""
    monkeypatch.setattr(pf.shutil, "which", lambda _name: "/usr/bin/gh")
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *_a, **_k: subprocess.CompletedProcess([], 0, "", ""),
    )
    repo_data = json.dumps({"owner": {"login": "acme"}, "name": "widgets"})
    node = {"id": "P1", "number": 9, "title": "Widgets", "closed": False}
    api_data = json.dumps({"data": {"repository": {"projectsV2": {"nodes": [node]}}}})
    opts = [{"id": "t1", "name": "Task"}]
    fields_data = json.dumps(
        {
            "fields": [
                {"id": "F_TYPE", "name": "Type", "options": opts},
                {"id": "F_PRIO", "name": "Priority", "options": opts},
            ],
        },
    )

    def mock_run_cmd(args: list[str]) -> str:
        if args[:3] == ["gh", "repo", "view"]:
            return repo_data
        if args[:3] == ["gh", "project", "field-list"]:
            return fields_data
        return api_data

    res = pf.run_project_preflight(mock_run_cmd, require_fields=True)
    assert res["owner"] == "acme"
    assert res["type_field_id"] == "F_TYPE"
    assert res["priority_field_id"] == "F_PRIO"
