"""Tests for backlog_utils.py's handling of fully-blocked issues."""

import json

import backlog_utils as bu

_LOGIN = "octocat"
_REPO = ("acme", "repo")
_PROJECT_NUM = 9


def test_fetch_backlog_issues_fully_blocked_issue_keeps_all_blocked_by_items() -> None:
    """A fully-blocked issue keeps all its blockers intact.

    A mix of PR-backed and PR-less blockers stays in leaf_issues, but is
    hidden from buckets.
    """

    def blocking_issue_node(num: int, pr_num: int | None) -> dict:
        timeline_nodes = (
            [
                {
                    "willCloseTarget": True,
                    "source": {
                        "number": pr_num,
                        "state": "OPEN",
                        "headRefName": f"pr-{pr_num}",
                        "url": f"https://github.com/acme/repo/pull/{pr_num}",
                    },
                },
            ]
            if pr_num is not None
            else []
        )
        return {
            "number": num,
            "state": "OPEN",
            "url": f"https://github.com/acme/repo/issues/{num}",
            "timelineItems": {"nodes": timeline_nodes},
        }

    project_items = json.dumps(
        {
            "items": [
                {
                    "status": "Todo",
                    "type": "Task",
                    "assignees": ["octocat"],
                    "priority": "High",
                    "content": {
                        "type": "Issue",
                        "number": 1,
                        "title": "Mine",
                        "url": "https://github.com/acme/repo/issues/1",
                    },
                },
            ],
        },
    )

    mixed_blocked_graphql = json.dumps(
        {
            "data": {
                "repository": {
                    "i1": {
                        "blockedBy": {
                            "nodes": [
                                blocking_issue_node(10, 25),
                                blocking_issue_node(11, None),
                            ],
                        },
                        "blocking": {"nodes": []},
                    },
                },
            },
        },
    )

    def fake_run_cmd(args: list[str]) -> str:
        if args[:3] == ["gh", "project", "item-list"]:
            return project_items
        return mixed_blocked_graphql

    result = bu.fetch_backlog_issues(fake_run_cmd, _REPO, "acme", _PROJECT_NUM, _LOGIN)

    issues = result["leaf_issues"]
    assert [issue["number"] for issue in issues] == [1]
    blocked_by_items = issues[0]["_blocked_by_items"]
    assert {b["number"] for b in blocked_by_items} == {10, 11}
    assert any(b.get("open_pr") is not None for b in blocked_by_items)
    assert any(b.get("open_pr") is None for b in blocked_by_items)

    for bucket in (
        "assigned_ready",
        "assigned_stackable",
        "available_ready",
        "available_stackable",
    ):
        assert result[bucket] == []

    assert result["fully_blocked_count"] == 1
