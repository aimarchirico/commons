"""Tests for the shared fetch_issue_dependencies module."""

import json
from typing import NamedTuple

from shared.blocking_prs import fetch_issue_dependencies, fetch_issues_dependencies


class _SubIssues(NamedTuple):
    open: int = 0
    closed: int = 0


def _timeline(pr_num: int | None, *, will_close: bool = True) -> dict:
    if pr_num is None:
        return {"nodes": []}
    return {
        "nodes": [
            {
                "willCloseTarget": will_close,
                "source": {
                    "number": pr_num,
                    "url": f"https://github.com/owner/repo/pull/{pr_num}",
                    "title": f"PR {pr_num}",
                    "headRefName": f"pr-{pr_num}",
                    "state": "OPEN",
                    "isDraft": False,
                },
            },
        ],
    }


def _blocker(number: int, *, state: str = "OPEN", pr_num: int | None = None) -> dict:
    return {
        "number": number,
        "url": f"https://github.com/owner/repo/issues/{number}",
        "state": state,
        "title": f"Issue {number}",
        "timelineItems": _timeline(pr_num),
    }


def _issue(
    number: int,
    *,
    blocked_by: list[dict] | None = None,
    blocking: list[dict] | None = None,
    parent: dict | None = None,
    sub_issues: _SubIssues | None = None,
) -> dict:
    sub_issues = sub_issues or _SubIssues()
    node = {
        "number": number,
        "subIssuesSummary": {
            "total": sub_issues.open + sub_issues.closed,
            "completed": sub_issues.closed,
        },
        "blockedBy": {"nodes": blocked_by or []},
        "blocking": {"nodes": blocking or []},
    }
    if parent is not None:
        node["parent"] = parent
    return node


def test_fetch_issue_dependencies_parses_open_blockers_and_prs() -> None:
    """Extracts open blocking issues, open PR details, and open downstream items."""
    root = _issue(
        11,
        blocked_by=[
            _blocker(10, pr_num=25),
            _blocker(13, pr_num=None),
            _blocker(5, state="CLOSED"),
        ],
        blocking=[_blocker(12)],
    )
    api_response = json.dumps({"data": {"repository": {"issue": root}}})

    def mock_run_cmd(_args: list[str]) -> str:
        return api_response

    res = fetch_issue_dependencies(mock_run_cmd, "owner", "repo", 11)

    assert [b["number"] for b in res["blocked_by"]] == [10, 13]
    assert res["blocked_by"][0]["via_parent"] is False
    assert res["blocked_by"][0]["open_pr"] == {
        "number": 25,
        "url": "https://github.com/owner/repo/pull/25",
        "title": "PR 25",
        "branch_name": "pr-25",
        "is_draft": False,
    }
    assert res["blocked_by"][1]["open_pr"] is None
    assert [b["number"] for b in res["blocking"]] == [12]
    assert res["has_open_children"] is False


def test_fetch_issue_dependencies_ignores_mentions_that_wont_close() -> None:
    """A cross-reference without the closing keyword doesn't count as an open PR."""
    root = _issue(11, blocked_by=[_blocker(10, pr_num=None)])
    root["blockedBy"]["nodes"][0]["timelineItems"] = _timeline(26, will_close=False)
    api_response = json.dumps({"data": {"repository": {"issue": root}}})

    def mock_run_cmd(_args: list[str]) -> str:
        return api_response

    res = fetch_issue_dependencies(mock_run_cmd, "owner", "repo", 11)

    assert res["blocked_by"][0]["open_pr"] is None


def test_fetch_issue_dependencies_reports_has_open_children() -> None:
    """A non-zero count of open sub-issues marks the issue as not a leaf."""
    root = _issue(100, sub_issues=_SubIssues(open=2))
    api_response = json.dumps({"data": {"repository": {"issue": root}}})

    def mock_run_cmd(_args: list[str]) -> str:
        return api_response

    res = fetch_issue_dependencies(mock_run_cmd, "owner", "repo", 100)

    assert res["has_open_children"] is True


def test_fetch_issue_dependencies_treats_all_closed_children_as_leaf() -> None:
    """An issue whose sub-issues are all closed is treated as a leaf."""
    root = _issue(101, sub_issues=_SubIssues(closed=2))
    api_response = json.dumps({"data": {"repository": {"issue": root}}})

    def mock_run_cmd(_args: list[str]) -> str:
        return api_response

    res = fetch_issue_dependencies(mock_run_cmd, "owner", "repo", 101)

    assert res["has_open_children"] is False


def test_fetch_issue_dependencies_includes_ancestors_own_blockers() -> None:
    """A block directly on a parent surfaces on the leaf, tagged via_parent."""
    root = _issue(
        102,
        blocked_by=[_blocker(999)],
        parent=_issue(101, blocked_by=[_blocker(1)]),
    )
    api_response = json.dumps({"data": {"repository": {"issue": root}}})

    def mock_run_cmd(_args: list[str]) -> str:
        return api_response

    res = fetch_issue_dependencies(mock_run_cmd, "owner", "repo", 102)

    by_number = {b["number"]: b for b in res["blocked_by"]}
    assert by_number.keys() == {999, 1}
    assert by_number[999]["via_parent"] is False
    assert by_number[1]["via_parent"] is True


def test_fetch_issue_dependencies_includes_grandparent_blockers() -> None:
    """A block on a grandparent (e.g. an Epic) still reaches the leaf."""
    root = _issue(
        103,
        parent=_issue(
            102,
            parent=_issue(101, blocked_by=[_blocker(1)]),
        ),
    )
    api_response = json.dumps({"data": {"repository": {"issue": root}}})

    def mock_run_cmd(_args: list[str]) -> str:
        return api_response

    res = fetch_issue_dependencies(mock_run_cmd, "owner", "repo", 103)

    assert [b["number"] for b in res["blocked_by"]] == [1]
    assert res["blocked_by"][0]["via_parent"] is True


def test_fetch_issue_dependencies_deduplicates_same_blocker_at_multiple_levels() -> (
    None
):
    """An issue blocking both a leaf and its parent only appears once."""
    root = _issue(
        202,
        blocked_by=[_blocker(999)],
        parent=_issue(201, blocked_by=[_blocker(999)]),
    )
    api_response = json.dumps({"data": {"repository": {"issue": root}}})

    def mock_run_cmd(_args: list[str]) -> str:
        return api_response

    res = fetch_issue_dependencies(mock_run_cmd, "owner", "repo", 202)

    assert [b["number"] for b in res["blocked_by"]] == [999]
    assert res["blocked_by"][0]["via_parent"] is False


def test_fetch_issue_dependencies_does_not_fold_blocking_across_ancestors() -> None:
    """Outbound `blocking` is the issue's own direct edges only, no traversal."""
    root = _issue(
        300,
        blocking=[_blocker(888)],
        parent=_issue(299, blocking=[_blocker(777)]),
    )
    api_response = json.dumps({"data": {"repository": {"issue": root}}})

    def mock_run_cmd(_args: list[str]) -> str:
        return api_response

    res = fetch_issue_dependencies(mock_run_cmd, "owner", "repo", 300)

    assert [b["number"] for b in res["blocking"]] == [888]


def test_fetch_issues_dependencies_batches_multiple_numbers_in_one_call() -> None:
    """Aliases each issue number in a single request and keys results by number."""
    api_response = json.dumps(
        {
            "data": {
                "repository": {
                    "i7": _issue(7, blocking=[_blocker(12)]),
                    "i8": _issue(8),
                },
            },
        },
    )
    calls: list[list[str]] = []

    def mock_run_cmd(args: list[str]) -> str:
        calls.append(args)
        return api_response

    res = fetch_issues_dependencies(mock_run_cmd, "owner", "repo", [7, 8])

    assert len(calls) == 1
    assert "i7: issue(number: 7)" in calls[0][4]
    assert "i8: issue(number: 8)" in calls[0][4]
    assert [b["number"] for b in res[7]["blocking"]] == [12]
    assert res[8] == {"blocked_by": [], "blocking": [], "has_open_children": False}


def test_fetch_issues_dependencies_returns_empty_dict_for_no_numbers() -> None:
    """Skips the API call entirely when there's nothing to fetch."""
    calls: list[list[str]] = []

    def mock_run_cmd(args: list[str]) -> str:
        calls.append(args)
        return "{}"

    assert fetch_issues_dependencies(mock_run_cmd, "owner", "repo", []) == {}
    assert calls == []
