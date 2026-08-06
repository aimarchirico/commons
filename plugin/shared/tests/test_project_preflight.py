"""Tests for the shared project_preflight module."""

import json

import pytest

from shared import project_preflight as pf


def test_resolve_project_context_single_project() -> None:
    """Returns project details when a single active open project is returned."""
    repo_data = json.dumps({"owner": {"login": "acme"}, "name": "widgets"})
    api_data = json.dumps({
        "data": {
            "repository": {
                "projectsV2": {
                    "nodes": [
                        {
                            "id": "PROJ_1",
                            "number": 9,
                            "title": "Widgets Board",
                            "closed": False,
                            "owner": {"login": "acme"},
                        },
                    ],
                },
            },
        },
    })

    def mock_run_cmd(args: list[str]) -> str:
        if args[:4] == ["gh", "repo", "view", "--json"]:
            return repo_data
        return api_data

    ctx = pf.resolve_project_context(mock_run_cmd)
    owner, repo_name, num, project_id, project_owner = ctx
    assert owner == "acme"
    assert repo_name == "widgets"
    expected_num = 9
    assert num == expected_num
    assert project_id == "PROJ_1"
    assert project_owner == "acme"


def test_resolve_project_context_disambiguates_multiple_projects() -> None:
    """Selects matching title-cased project when multiple active projects exist."""
    repo_data = json.dumps({"owner": {"login": "acme"}, "name": "widgets"})
    api_data = json.dumps({
        "data": {
            "repository": {
                "projectsV2": {
                    "nodes": [
                        {
                            "id": "PROJ_1",
                            "number": 9,
                            "title": "Widgets",
                            "closed": False,
                            "owner": {"login": "acme"},
                        },
                        {
                            "id": "PROJ_2",
                            "number": 10,
                            "title": "Other",
                            "closed": False,
                            "owner": {"login": "acme"},
                        },
                    ],
                },
            },
        },
    })

    def mock_run_cmd(args: list[str]) -> str:
        if args[:4] == ["gh", "repo", "view", "--json"]:
            return repo_data
        return api_data

    ctx = pf.resolve_project_context(mock_run_cmd)
    num, project_id = ctx[2], ctx[3]
    expected_num = 9
    assert num == expected_num
    assert project_id == "PROJ_1"


def test_resolve_project_context_raises_when_no_projects_exist() -> None:
    """Raises ProjectPreflightError when no open active projects exist."""
    repo_data = json.dumps({"owner": {"login": "acme"}, "name": "widgets"})
    api_data = json.dumps({"data": {"repository": {"projectsV2": {"nodes": []}}}})

    def mock_run_cmd(args: list[str]) -> str:
        if args[:4] == ["gh", "repo", "view", "--json"]:
            return repo_data
        return api_data

    with pytest.raises(pf.ProjectPreflightError):
        pf.resolve_project_context(mock_run_cmd)


def test_run_project_preflight_exits_when_no_projects_exist(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exits with SystemExit when project preflight fails."""
    monkeypatch.setattr(
        pf.shutil, "which", lambda _name: "/usr/bin/gh",
    )
    repo_data = json.dumps({"owner": {"login": "acme"}, "name": "widgets"})
    api_data = json.dumps({"data": {"repository": {"projectsV2": {"nodes": []}}}})

    def mock_run_cmd(args: list[str]) -> str:
        if args[:4] == ["gh", "repo", "view"]:
            return repo_data
        return api_data

    with pytest.raises(SystemExit):
        pf.run_project_preflight(mock_run_cmd, require_fields=False)


def test_fetch_project_fields_extracts_type_and_priority() -> None:
    """Correctly parses Type and Priority field IDs."""
    fields_data = json.dumps({
        "fields": [
            {"id": "F_TYPE", "name": "Type"},
            {"id": "F_PRIO", "name": "Priority"},
        ],
    })

    def mock_run_cmd(_args: list[str]) -> str:
        return fields_data

    target_num = 9
    type_id, prio_id, _data, errors = pf.fetch_project_fields(
        mock_run_cmd, "acme", target_num,
    )
    assert type_id == "F_TYPE"
    assert prio_id == "F_PRIO"
    assert errors == []
