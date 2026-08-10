"""Tests for backlog_utils.py's handling of transitive Subtask dependencies."""

import json

import backlog_utils as bu

_LOGIN = "octocat"
_REPO = ("acme", "repo")
_PROJECT_NUM = 9


def _project_item(number: int, *, is_mine: bool) -> dict:
    return {
        "status": "Todo",
        "type": "Task",
        "assignees": ["octocat"] if is_mine else [],
        "priority": "High",
        "content": {
            "type": "Issue",
            "number": number,
            "title": f"Issue {number}",
            "url": f"https://github.com/acme/repo/issues/{number}",
        },
    }


def _open_issue(number: int) -> dict:
    return {
        "number": number,
        "state": "OPEN",
        "url": f"https://github.com/acme/repo/issues/{number}",
        "title": f"Issue {number}",
        "timelineItems": {"nodes": []},
    }


def _open_issue_with_pr(number: int, pr_num: int) -> dict:
    return {
        "number": number,
        "state": "OPEN",
        "url": f"https://github.com/acme/repo/issues/{number}",
        "title": f"Issue {number}",
        "timelineItems": {
            "nodes": [
                {
                    "willCloseTarget": True,
                    "source": {
                        "number": pr_num,
                        "state": "OPEN",
                        "headRefName": f"pr-{pr_num}",
                        "url": f"https://github.com/acme/repo/pull/{pr_num}",
                    },
                },
            ],
        },
    }


def test_fetch_backlog_issues_hides_story_blocked_via_descendant_subtask() -> None:
    """A Story is fully-blocked via a Subtask blocked by another Story's Subtask.

    This holds even though the Story's own blockedBy is empty.
    """
    project_items = json.dumps({"items": [_project_item(1, is_mine=True)]})

    deps_graphql = json.dumps(
        {
            "data": {
                "repository": {
                    "i1": {
                        "blockedBy": {"nodes": []},
                        "blocking": {"nodes": []},
                        "subIssues": {
                            "nodes": [
                                {
                                    "blockedBy": {"nodes": [_open_issue(999)]},
                                    "blocking": {"nodes": []},
                                },
                            ],
                        },
                    },
                },
            },
        },
    )

    def fake_run_cmd(args: list[str]) -> str:
        if args[:3] == ["gh", "project", "item-list"]:
            return project_items
        return deps_graphql

    result = bu.fetch_backlog_issues(fake_run_cmd, _REPO, "acme", _PROJECT_NUM, _LOGIN)

    assert result["fully_blocked_count"] == 1
    assert {b["number"] for b in result["backlog_issues"][0]["_blocked_by_items"]} == {
        999,
    }
    for bucket in (
        "assigned_ready",
        "assigned_stackable",
        "available_ready",
        "available_stackable",
    ):
        assert result[bucket] == []


def test_fetch_backlog_issues_rolls_up_descendant_blocking_credit() -> None:
    """A Story's `blocking_count` includes edges owned by its descendant Subtasks."""
    project_items = json.dumps({"items": [_project_item(2, is_mine=False)]})

    deps_graphql = json.dumps(
        {
            "data": {
                "repository": {
                    "i2": {
                        "blockedBy": {"nodes": []},
                        "blocking": {"nodes": []},
                        "subIssues": {
                            "nodes": [
                                {
                                    "blockedBy": {"nodes": []},
                                    "blocking": {"nodes": [_open_issue(777)]},
                                },
                            ],
                        },
                    },
                },
            },
        },
    )

    def fake_run_cmd(args: list[str]) -> str:
        if args[:3] == ["gh", "project", "item-list"]:
            return project_items
        return deps_graphql

    result = bu.fetch_backlog_issues(fake_run_cmd, _REPO, "acme", _PROJECT_NUM, _LOGIN)

    entry = result["backlog_issues"][0]
    assert entry["blocking_count"] == 1
    assert entry["blocking"] == "1 issue"


def test_fetch_backlog_issues_stackable_when_descendant_blocker_has_open_pr() -> None:
    """A Story is stackable once a descendant Subtask's blocker gets an open PR.

    It must not stay counted as fully-blocked at that point.
    """
    project_items = json.dumps({"items": [_project_item(3, is_mine=True)]})

    deps_graphql = json.dumps(
        {
            "data": {
                "repository": {
                    "i3": {
                        "blockedBy": {"nodes": []},
                        "blocking": {"nodes": []},
                        "subIssues": {
                            "nodes": [
                                {
                                    "blockedBy": {
                                        "nodes": [_open_issue_with_pr(998, 42)],
                                    },
                                    "blocking": {"nodes": []},
                                },
                            ],
                        },
                    },
                },
            },
        },
    )

    def fake_run_cmd(args: list[str]) -> str:
        if args[:3] == ["gh", "project", "item-list"]:
            return project_items
        return deps_graphql

    result = bu.fetch_backlog_issues(fake_run_cmd, _REPO, "acme", _PROJECT_NUM, _LOGIN)

    assert result["fully_blocked_count"] == 0
    assert [i["number"] for i in result["assigned_stackable"]] == [3]
    assert result["assigned_stackable"][0]["blocked_by"] == (
        "PR [#42](https://github.com/acme/repo/pull/42)"
    )
