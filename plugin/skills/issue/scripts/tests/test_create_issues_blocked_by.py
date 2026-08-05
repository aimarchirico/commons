"""Tests for the id/blocked_by dependency wiring in create_issues.py."""

import json
import subprocess
import sys
from pathlib import Path

import create_issues as ci
import pytest
from test_create_issues import _NO_PROJECT_INFO, _install_gh


def test_create_issue_recursive_records_id_and_pending_deps(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An item's "id" is mapped to its issue number; blocked_by is queued."""
    def fake_run_cmd(_args: list[str]) -> str:
        return "https://github.com/acme/widgets/issues/101"

    monkeypatch.setattr(ci, "_run_cmd", fake_run_cmd)
    id_map: dict[str, str] = {}
    pending_deps: list[tuple[str, list[str]]] = []

    ci._create_issue_recursive(
        {"title": "Fix bug", "id": "fix", "blocked_by": ["migration"]},
        None, "acme", _NO_PROJECT_INFO, (id_map, pending_deps),
    )

    assert id_map == {"fix": "101"}
    assert pending_deps == [("101", ["migration"])]


def test_wire_blocked_by_resolves_ids_and_edits_the_issue() -> None:
    """Resolved blocked_by ids are joined into a single --add-blocked-by edit."""
    calls: list[list[str]] = []

    def fake_run_cmd(args: list[str]) -> str:
        calls.append(args)
        return ""

    id_map = {"migration": "100", "schema": "99"}
    pending_deps = [("101", ["migration", "schema"])]

    ci._wire_blocked_by(fake_run_cmd, id_map, pending_deps)

    assert calls == [[
        "gh", "issue", "edit", "101", "--add-blocked-by", "100,99",
    ]]


def test_wire_blocked_by_warns_and_skips_unresolved_ids(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """An id with no matching created issue is skipped with a warning."""
    calls: list[list[str]] = []

    def fake_run_cmd(args: list[str]) -> str:
        calls.append(args)
        return ""

    ci._wire_blocked_by(fake_run_cmd, {}, [("101", ["missing"])])

    assert calls == []
    assert "does not match any created issue" in capsys.readouterr().err


def test_wire_blocked_by_warns_when_gh_edit_fails(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A failed gh issue edit is reported as a warning, not an exception."""
    def fake_run_cmd(_args: list[str]) -> str:
        raise subprocess.CalledProcessError(1, ["gh"])

    ci._wire_blocked_by(fake_run_cmd, {"a": "100"}, [("101", ["a"])])

    assert "Warning: Failed to set blocked-by" in capsys.readouterr().err


def test_main_wires_blocked_by_across_sibling_issues(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """main() resolves blocked_by ids to real issue numbers after creation."""
    issues_file = tmp_path / "issues.json"
    issues_file.write_text(json.dumps({"items": [
        {"title": "Migration", "id": "migration", "type": "Task", "priority": "P1"},
        {
            "title": "Endpoint", "id": "endpoint", "type": "Task", "priority": "P1",
            "blocked_by": ["migration"],
        },
    ]}))
    monkeypatch.setattr(sys, "argv", ["create_issues", str(issues_file)])

    _install_gh(monkeypatch, {})
    urls = iter([
        "https://github.com/acme/widgets/issues/101",
        "https://github.com/acme/widgets/issues/102",
    ])
    calls: list[list[str]] = []
    base_run_cmd = ci._run_cmd

    def fake_run_cmd(args: list[str]) -> str:
        calls.append(args)
        if args[:3] == ["gh", "issue", "create"]:
            return next(urls)
        return base_run_cmd(args)

    monkeypatch.setattr(ci, "_run_cmd", fake_run_cmd)

    ci.main()

    edit_call = next(c for c in calls if c[:3] == ["gh", "issue", "edit"])
    assert edit_call == ["gh", "issue", "edit", "102", "--add-blocked-by", "101"]
    assert "Successfully created all issues." in capsys.readouterr().out
