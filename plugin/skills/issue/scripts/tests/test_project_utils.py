"""Tests for project_utils.py's GitHub Projects (v2) helpers."""

import json
import subprocess
from collections.abc import Callable

import project_utils as pu

_REPO_OUTPUT = json.dumps({"owner": {"login": "acme"}, "name": "widgets"})


def _projects_response(nodes: list[dict[str, object]]) -> str:
    return json.dumps({"data": {"repository": {"projectsV2": {"nodes": nodes}}}})


def test_get_project_context_returns_the_single_open_project() -> None:
    """With one open project linked, its owner/number/id are returned."""

    def fake_run_cmd(args: list[str]) -> str:
        if args[:3] == ["gh", "repo", "view"]:
            return _REPO_OUTPUT
        return _projects_response(
            [
                {"id": "PID", "number": 9, "title": "Widgets", "closed": False},
            ],
        )

    owner, number, project_id, error = pu.get_project_context(fake_run_cmd)

    assert (owner, number, project_id, error) == ("acme", 9, "PID", None)


def test_get_project_context_disambiguates_multiple_by_repo_name() -> None:
    """With several open projects, the one titled after the repo wins."""

    def fake_run_cmd(args: list[str]) -> str:
        if args[:3] == ["gh", "repo", "view"]:
            return _REPO_OUTPUT
        return _projects_response(
            [
                {"id": "PID", "number": 9, "title": "Widgets", "closed": False},
                {
                    "id": "PID2",
                    "number": 10,
                    "title": "Widgets Template",
                    "closed": False,
                },
            ],
        )

    owner, number, project_id, error = pu.get_project_context(fake_run_cmd)

    assert (owner, number, project_id, error) == ("acme", 9, "PID", None)


def test_get_project_context_errors_when_ambiguous() -> None:
    """With several open projects and no title matching the repo, it errors."""

    def fake_run_cmd(args: list[str]) -> str:
        if args[:3] == ["gh", "repo", "view"]:
            return _REPO_OUTPUT
        return _projects_response(
            [
                {"id": "PID", "number": 9, "title": "Foo", "closed": False},
                {"id": "PID2", "number": 10, "title": "Bar", "closed": False},
            ],
        )

    owner, number, project_id, error = pu.get_project_context(fake_run_cmd)

    assert (owner, number, project_id) == ("acme", None, None)
    assert error is not None
    assert "Multiple active projects" in error


def test_get_project_context_errors_when_no_open_project() -> None:
    """With no open projects linked, it reports that clearly."""

    def fake_run_cmd(args: list[str]) -> str:
        if args[:3] == ["gh", "repo", "view"]:
            return _REPO_OUTPUT
        return _projects_response([])

    owner, number, project_id, error = pu.get_project_context(fake_run_cmd)

    assert (owner, number, project_id) == ("acme", None, None)
    assert error == "No active project linked to this repository."


def test_get_project_context_errors_when_repo_view_fails() -> None:
    """When the repo context itself can't be fetched, that's reported too."""

    def fake_run_cmd(args: list[str]) -> str:
        raise subprocess.CalledProcessError(1, args)

    owner, number, project_id, error = pu.get_project_context(fake_run_cmd)

    assert (owner, number, project_id) == (None, None, None)
    assert error is not None
    assert "Could not retrieve" in error


def test_get_project_fields_extracts_type_and_priority_ids() -> None:
    """Type and Priority field IDs are pulled out of the field list."""

    def fake_run_cmd(_args: list[str]) -> str:
        return json.dumps(
            {
                "fields": [
                    {
                        "id": "TID",
                        "name": "Type",
                        "options": [{"id": "o1", "name": "Task"}],
                    },
                    {"id": "PRID", "name": "Priority", "options": []},
                    {"id": "OID", "name": "Other", "options": []},
                ],
            },
        )

    type_id, priority_id, fields_data, errors = pu.get_project_fields(
        fake_run_cmd,
        "acme",
        9,
    )

    assert (type_id, priority_id, errors) == ("TID", "PRID", [])
    assert fields_data["fields"][0]["name"] == "Type"


def test_get_project_fields_returns_empty_without_a_project_number() -> None:
    """With no project linked, field lookup is a no-op."""
    result = pu.get_project_fields(lambda _args: "{}", "acme", None)

    assert result == (None, None, {}, [])


def test_get_project_fields_reports_missing_required_fields() -> None:
    """Missing Type/Priority fields on the project surface as errors."""
    type_id, priority_id, _fields_data, errors = pu.get_project_fields(
        lambda _args: json.dumps({"fields": []}),
        "acme",
        9,
    )

    assert (type_id, priority_id) == (None, None)
    assert "Type" in errors[0]
    assert "Priority" in errors[1]


def test_validate_project_setup_collects_context_and_field_errors() -> None:
    """Context errors and (when a project is linked) field errors both surface."""
    errors = pu.validate_project_setup(
        items=[],
        field_ids=(9, "PID", None, None),
        fields_data={},
        error_info=("context broke", ["missing Type"]),
    )

    assert errors == ["context broke", "missing Type"]


def test_validate_project_setup_skips_field_errors_without_a_project() -> None:
    """Field errors are irrelevant noise when no project is linked at all."""
    errors = pu.validate_project_setup(
        items=[],
        field_ids=(None, None, None, None),
        fields_data={},
        error_info=(None, ["missing Type"]),
    )

    assert errors == []


def test_validate_project_setup_flags_type_and_priority_values_not_in_options() -> None:
    """Type/Priority values used in items must match an existing project option."""
    fields_data = {
        "fields": [
            {"name": "Type", "options": [{"name": "Task"}]},
            {"name": "Priority", "options": [{"name": "P1"}]},
        ],
    }
    items = [
        {
            "type": "Epic",
            "priority": "P9",
            "children": [{"type": "Task", "priority": "P1"}],
        },
    ]

    errors = pu.validate_project_setup(
        items=items,
        field_ids=(9, "PID", "TID", "PRID"),
        fields_data=fields_data,
        error_info=(None, []),
    )

    expected_error_count = 2
    assert len(errors) == expected_error_count
    assert any("Epic" in e and "Type" in e for e in errors)
    assert any("P9" in e and "Priority" in e for e in errors)


def _recording_run_cmd(calls: list[list[str]]) -> Callable[[list[str]], str]:
    def run_cmd(args: list[str]) -> str:
        calls.append(args)
        return ""

    return run_cmd


def test_set_project_field_sets_the_matching_option() -> None:
    """Sets the single-select option whose name matches the target value."""
    calls: list[list[str]] = []
    fields_data = {
        "fields": [
            {"name": "Type", "options": [{"id": "opt1", "name": "Task"}]},
        ],
    }

    pu.set_project_field(
        _recording_run_cmd(calls),
        "item1",
        "PID",
        ("Type", "TID", "Task"),
        fields_data,
    )

    assert calls == [
        [
            "gh",
            "project",
            "item-edit",
            "--id",
            "item1",
            "--project-id",
            "PID",
            "--field-id",
            "TID",
            "--single-select-option-id",
            "opt1",
        ],
    ]


def test_set_project_field_is_a_noop_without_a_value_or_field_id() -> None:
    """Nothing is run when there's no value to set or no field ID to set it on."""
    calls: list[list[str]] = []
    run_cmd = _recording_run_cmd(calls)

    pu.set_project_field(run_cmd, "item1", "PID", ("Type", "TID", None), {})
    pu.set_project_field(run_cmd, "item1", "PID", ("Type", None, "Task"), {})

    assert calls == []


def test_set_project_field_is_a_noop_when_no_option_matches() -> None:
    """Nothing is run when the value doesn't match any known option."""
    calls: list[list[str]] = []
    fields_data = {
        "fields": [
            {"name": "Type", "options": [{"id": "o1", "name": "Bug"}]},
        ],
    }

    pu.set_project_field(
        _recording_run_cmd(calls),
        "item1",
        "PID",
        ("Type", "TID", "Task"),
        fields_data,
    )

    assert calls == []
