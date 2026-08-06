"""Tests for get_issue_base_branch.py."""

import json
import sys

import get_issue_base_branch as gibb
import pytest

_REPO_OUTPUT = json.dumps({
    "owner": {"login": "acme"},
    "name": "widgets",
    "defaultBranchRef": {"name": "main"},
})

_EXPECTED_CANDIDATES_SINGLE = 1
_EXPECTED_CANDIDATES_MULTIPLE = 2
_EXPECTED_PR_NUMBER = 15


def _api_response(nodes: list[dict]) -> str:
    return json.dumps({
        "data": {
            "repository": {
                "issue": {
                    "blockedBy": {
                        "nodes": nodes,
                    },
                },
            },
        },
    })


def test_get_issue_base_branch_default() -> None:
    """Returns default branch when there are no blocking issues with open PRs."""
    def fake_run_cmd(args: list[str]) -> str:
        if args[:3] == ["gh", "repo", "view"]:
            return _REPO_OUTPUT
        return _api_response([])

    res = gibb.get_issue_base_branch(fake_run_cmd, "42")
    assert res["status"] == "default"
    assert res["base_branch"] == "main"
    assert res["candidates"] == []


def test_get_issue_base_branch_single_pr() -> None:
    """Returns single candidate branch when issue is blocked by 1 open PR."""
    blocking_nodes = [
        {
            "number": 10,
            "state": "OPEN",
            "title": "Blocker",
            "timelineItems": {
                "nodes": [
                    {
                        "subject": {
                            "number": _EXPECTED_PR_NUMBER,
                            "title": "Fix blocker",
                            "headRefName": "feature/blocker-fix",
                            "state": "OPEN",
                            "isDraft": False,
                        },
                    },
                ],
            },
        },
    ]

    def fake_run_cmd(args: list[str]) -> str:
        if args[:3] == ["gh", "repo", "view"]:
            return _REPO_OUTPUT
        return _api_response(blocking_nodes)

    res = gibb.get_issue_base_branch(fake_run_cmd, "42")
    assert res["status"] == "single"
    assert res["base_branch"] == "feature/blocker-fix"
    assert len(res["candidates"]) == _EXPECTED_CANDIDATES_SINGLE
    assert res["candidates"][0]["pr_number"] == _EXPECTED_PR_NUMBER


def test_get_issue_base_branch_multiple_prs() -> None:
    """Returns status='multiple' when issue is blocked by multiple open PRs."""
    blocking_nodes = [
        {
            "number": 10,
            "state": "OPEN",
            "title": "Blocker 1",
            "timelineItems": {
                "nodes": [
                    {
                        "subject": {
                            "number": 15,
                            "title": "Fix blocker 1",
                            "headRefName": "feature/blocker-1",
                            "state": "OPEN",
                            "isDraft": False,
                        },
                    },
                ],
            },
        },
        {
            "number": 11,
            "state": "OPEN",
            "title": "Blocker 2",
            "timelineItems": {
                "nodes": [
                    {
                        "subject": {
                            "number": 16,
                            "title": "Fix blocker 2",
                            "headRefName": "feature/blocker-2",
                            "state": "OPEN",
                            "isDraft": False,
                        },
                    },
                ],
            },
        },
    ]

    def fake_run_cmd(args: list[str]) -> str:
        if args[:3] == ["gh", "repo", "view"]:
            return _REPO_OUTPUT
        return _api_response(blocking_nodes)

    res = gibb.get_issue_base_branch(fake_run_cmd, "42")
    assert res["status"] == "multiple"
    assert res["base_branch"] is None
    assert len(res["candidates"]) == _EXPECTED_CANDIDATES_MULTIPLE


def test_main_exits_when_issue_id_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """main() exits with an error when no issue ID is given."""
    monkeypatch.setattr(sys, "argv", ["get_issue_base_branch"])

    with pytest.raises(SystemExit):
        gibb.main()


def test_main_prints_base_branch_single(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """main() prints base branch to stdout when single or default."""
    monkeypatch.setattr(sys, "argv", ["get_issue_base_branch", "42"])
    monkeypatch.setattr(gibb.shutil, "which", lambda _name: "/usr/bin/gh")

    def fake_run_cmd(args: list[str]) -> str:
        if args[:3] == ["gh", "repo", "view"]:
            return _REPO_OUTPUT
        return _api_response([])

    monkeypatch.setattr(gibb, "_run_cmd", fake_run_cmd)

    gibb.main()
    assert capsys.readouterr().out == "main\n"
