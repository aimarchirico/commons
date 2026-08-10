"""Tests for get_issue_base_branch.py."""

import json
import sys
from collections.abc import Callable
from typing import Any

import get_issue_base_branch as gibb
import pytest

_REPO_OUTPUT = json.dumps(
    {
        "owner": {"login": "acme"},
        "name": "widgets",
        "defaultBranchRef": {"name": "main"},
    },
)

_EXPECTED_CANDIDATES_SINGLE = 1
_EXPECTED_CANDIDATES_MULTIPLE = 2
_EXPECTED_PR_NUMBER = 15
_EXPECTED_BLOCKER_ISSUE_NUMBER = 10


def _tree_response(number: int, children: list[dict] | None = None) -> str:
    node: dict[str, Any] = {
        "number": number,
        "title": f"Issue {number}",
        "body": "Body",
        "projectItems": {"nodes": []},
        "subIssues": {"nodes": children or []},
    }
    return json.dumps({"data": {"repository": {"issue": node}}})


def _deps_response(entries: dict[int, dict[str, Any]]) -> str:
    repo: dict[str, Any] = {}
    for number, issue_data in entries.items():
        repo[f"i{number}"] = {
            "number": number,
            "blockedBy": {"nodes": issue_data.get("blocked_by_nodes", [])},
            "blocking": {"nodes": []},
            "subIssuesSummary": {"total": len(issue_data.get("children", []))},
            **({"parent": issue_data["parent"]} if "parent" in issue_data else {}),
        }
    return json.dumps({"data": {"repository": repo}})


def _blocker_node(*, issue_number: int, pr_number: int, branch: str) -> dict:
    return {
        "number": issue_number,
        "state": "OPEN",
        "title": "Blocker",
        "timelineItems": {
            "nodes": [
                {
                    "willCloseTarget": True,
                    "source": {
                        "number": pr_number,
                        "title": "Fix blocker",
                        "headRefName": branch,
                        "state": "OPEN",
                        "isDraft": False,
                    },
                },
            ],
        },
    }


def _leaf_child(number: int) -> dict:
    return {
        "number": number,
        "title": f"Issue {number}",
        "body": "",
        "projectItems": {"nodes": []},
        "subIssues": {"nodes": []},
    }


def _sequenced_run_cmd(*responses: str) -> Callable[[list[str]], str]:
    calls = iter(responses)

    def _run(_args: list[str]) -> str:
        return next(calls)

    return _run


def test_get_issue_base_branch_default() -> None:
    """Returns default branch when there are no blocking issues with open PRs."""
    run_cmd = _sequenced_run_cmd(
        _REPO_OUTPUT,
        _tree_response(42),
        _deps_response({42: {}}),
    )

    res = gibb.get_issue_base_branch(run_cmd, "42")
    assert res["status"] == "default"
    assert res["base_branch"] == "main"
    assert res["candidates"] == []


def test_get_issue_base_branch_single_pr() -> None:
    """Returns single candidate branch when issue is blocked by 1 open PR."""
    blocking_nodes = [
        _blocker_node(
            issue_number=10,
            pr_number=_EXPECTED_PR_NUMBER,
            branch="feature/blocker-fix",
        ),
    ]
    run_cmd = _sequenced_run_cmd(
        _REPO_OUTPUT,
        _tree_response(42),
        _deps_response({42: {"blocked_by_nodes": blocking_nodes}}),
    )

    res = gibb.get_issue_base_branch(run_cmd, "42")
    assert res["status"] == "single"
    assert res["base_branch"] == "feature/blocker-fix"
    assert len(res["candidates"]) == _EXPECTED_CANDIDATES_SINGLE
    assert res["candidates"][0]["pr_number"] == _EXPECTED_PR_NUMBER


def test_get_issue_base_branch_blocker_on_parent() -> None:
    """Uses a blocking PR's branch when the dependency is on the parent Story.

    A block directly on the parent reaches the Subtask being solved too.
    """
    parent_blocked_by = _blocker_node(
        issue_number=10,
        pr_number=_EXPECTED_PR_NUMBER,
        branch="feature/blocker-fix",
    )
    run_cmd = _sequenced_run_cmd(
        _REPO_OUTPUT,
        _tree_response(43),
        _deps_response(
            {
                43: {
                    "parent": {
                        "number": 42,
                        "blockedBy": {"nodes": [parent_blocked_by]},
                    },
                },
            },
        ),
    )

    res = gibb.get_issue_base_branch(run_cmd, "43")
    assert res["status"] == "single"
    assert res["base_branch"] == "feature/blocker-fix"
    assert res["candidates"][0]["issue_number"] == _EXPECTED_BLOCKER_ISSUE_NUMBER


def test_get_issue_base_branch_blocker_on_child() -> None:
    """Uses a blocking PR's branch when only a descendant sub-issue is blocked.

    Solving a parent issue means solving its whole tree, so a blocker on a
    child alone must still surface here even though the parent itself is
    unblocked.
    """
    child_blocked_by = _blocker_node(
        issue_number=10,
        pr_number=_EXPECTED_PR_NUMBER,
        branch="feature/blocker-fix",
    )
    run_cmd = _sequenced_run_cmd(
        _REPO_OUTPUT,
        _tree_response(42, children=[_leaf_child(44)]),
        _deps_response(
            {
                42: {},
                44: {"blocked_by_nodes": [child_blocked_by]},
            },
        ),
    )

    res = gibb.get_issue_base_branch(run_cmd, "42")
    assert res["status"] == "single"
    assert res["base_branch"] == "feature/blocker-fix"
    assert res["candidates"][0]["issue_number"] == _EXPECTED_BLOCKER_ISSUE_NUMBER


def test_get_issue_base_branch_multiple_prs() -> None:
    """Returns status='multiple' when issue is blocked by multiple open PRs."""
    blocking_nodes = [
        _blocker_node(issue_number=10, pr_number=15, branch="feature/blocker-1"),
        _blocker_node(issue_number=11, pr_number=16, branch="feature/blocker-2"),
    ]
    run_cmd = _sequenced_run_cmd(
        _REPO_OUTPUT,
        _tree_response(42),
        _deps_response({42: {"blocked_by_nodes": blocking_nodes}}),
    )

    res = gibb.get_issue_base_branch(run_cmd, "42")
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
    monkeypatch.setattr(
        gibb.project_preflight.shutil,
        "which",
        lambda _name: "/usr/bin/gh",
    )
    monkeypatch.setattr(
        gibb.project_preflight.subprocess,
        "run",
        lambda *_a, **_k: None,
    )

    run_cmd = _sequenced_run_cmd(
        _REPO_OUTPUT,
        _tree_response(42),
        _deps_response({42: {}}),
    )
    monkeypatch.setattr(gibb, "_run_cmd", run_cmd)

    gibb.main()
    assert capsys.readouterr().out == "main\n"
