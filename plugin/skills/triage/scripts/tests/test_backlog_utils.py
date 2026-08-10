"""Tests for backlog_utils.py's fetching, filtering, and sorting."""

import json

import backlog_utils as bu

_LOGIN = "octocat"
_REPO = ("acme", "repo")
_PROJECT_NUM = 9


def _empty_deps_graphql() -> str:
    return json.dumps({"data": {"repository": {}}})


def test_fetch_backlog_issues_filters_by_type_status_and_assignee() -> None:
    """Only Todo Story/Task/Bug issues assigned to or unassigned for login survive."""
    project_items = json.dumps(
        {
            "items": [
                {
                    "status": "Todo",
                    "type": "Task",
                    "assignees": ["octocat"],
                    "priority": "Medium",
                    "content": {
                        "type": "Issue",
                        "number": 1,
                        "title": "Mine",
                        "url": "https://github.com/acme/repo/issues/1",
                    },
                },
                {
                    "status": "Todo",
                    "type": "Task",
                    "assignees": [],
                    "priority": "Medium",
                    "content": {
                        "type": "Issue",
                        "number": 2,
                        "title": "Free",
                        "url": "https://github.com/acme/repo/issues/2",
                    },
                },
                {
                    "status": "Todo",
                    "type": "Task",
                    "assignees": ["bob"],
                    "priority": "Medium",
                    "content": {
                        "type": "Issue",
                        "number": 3,
                        "title": "Bob's",
                        "url": "https://github.com/acme/repo/issues/3",
                    },
                },
                {
                    "status": "Todo",
                    "type": "Epic",
                    "assignees": [],
                    "priority": "Medium",
                    "content": {
                        "type": "Issue",
                        "number": 4,
                        "title": "Epic",
                        "url": "https://github.com/acme/repo/issues/4",
                    },
                },
                {
                    "status": "Done",
                    "type": "Task",
                    "assignees": [],
                    "priority": "Medium",
                    "content": {
                        "type": "Issue",
                        "number": 5,
                        "title": "Done",
                        "url": "https://github.com/acme/repo/issues/5",
                    },
                },
            ],
        },
    )

    def fake_run_cmd(args: list[str]) -> str:
        if args[:3] == ["gh", "project", "item-list"]:
            return project_items
        return _empty_deps_graphql()

    result = bu.fetch_backlog_issues(
        fake_run_cmd,
        _REPO,
        "acme",
        _PROJECT_NUM,
        _LOGIN,
    )

    issues = result["backlog_issues"]
    assert [issue["number"] for issue in issues] == [1, 2]
    assert issues[0]["assignee"] == "You"
    assert issues[1]["assignee"] == "Unassigned"
    assert result["assigned_to_others_count"] == 1
    assert result["fully_blocked_count"] == 0


def test_fetch_backlog_issues_batches_dependency_lookups_in_one_call() -> None:
    """All Todo candidates' dependencies are fetched in a single GraphQL request."""
    project_items = json.dumps(
        {
            "items": [
                {
                    "status": "Todo",
                    "type": "Task",
                    "assignees": ["octocat"],
                    "priority": "Low",
                    "content": {
                        "type": "Issue",
                        "number": 1,
                        "title": "Mine",
                        "url": "https://github.com/acme/repo/issues/1",
                    },
                },
                {
                    "status": "Todo",
                    "type": "Task",
                    "assignees": [],
                    "priority": "Low",
                    "content": {
                        "type": "Issue",
                        "number": 2,
                        "title": "Free",
                        "url": "https://github.com/acme/repo/issues/2",
                    },
                },
            ],
        },
    )
    combined_deps_graphql = json.dumps(
        {
            "data": {
                "repository": {
                    "i1": {
                        "blockedBy": {
                            "nodes": [
                                {
                                    "number": 10,
                                    "state": "OPEN",
                                    "url": "https://github.com/acme/repo/issues/10",
                                    "timelineItems": {"nodes": []},
                                },
                                {
                                    "number": 11,
                                    "state": "CLOSED",
                                    "url": "https://github.com/acme/repo/issues/11",
                                    "timelineItems": {"nodes": []},
                                },
                            ],
                        },
                        "blocking": {"nodes": []},
                    },
                    "i2": {"blockedBy": {"nodes": []}, "blocking": {"nodes": []}},
                },
            },
        },
    )
    calls: list[list[str]] = []

    def fake_run_cmd(args: list[str]) -> str:
        calls.append(args)
        if args[:3] == ["gh", "project", "item-list"]:
            return project_items
        return combined_deps_graphql

    result = bu.fetch_backlog_issues(
        fake_run_cmd,
        _REPO,
        "acme",
        _PROJECT_NUM,
        _LOGIN,
    )

    graphql_calls = [c for c in calls if c[:3] == ["gh", "api", "graphql"]]
    assert len(graphql_calls) == 1
    assert "i1: issue(number: 1)" in graphql_calls[0][4]
    assert "i2: issue(number: 2)" in graphql_calls[0][4]

    issues = result["backlog_issues"]
    assert sorted(issue["number"] for issue in issues) == [1, 2]
    assert result["fully_blocked_count"] == 1

    all_bucket_numbers = {
        issue["number"]
        for bucket in (
            "assigned_ready",
            "assigned_stackable",
            "available_ready",
            "available_stackable",
        )
        for issue in result[bucket]
    }
    assert 1 not in all_bucket_numbers


def test_fetch_backlog_issues_includes_issue_blocked_by_open_pr() -> None:
    """Multiple blocking issues with PRs format as PR [#n](url), [#m](url)."""

    def blocking_issue_node(num: int, pr_num: int) -> dict:
        return {
            "number": num,
            "state": "OPEN",
            "url": f"https://github.com/acme/repo/issues/{num}",
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

    pr_blocked_graphql = json.dumps(
        {
            "data": {
                "repository": {
                    "i1": {
                        "blockedBy": {
                            "nodes": [
                                blocking_issue_node(10, 25),
                                blocking_issue_node(11, 26),
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
        return pr_blocked_graphql

    result = bu.fetch_backlog_issues(fake_run_cmd, _REPO, "acme", _PROJECT_NUM, _LOGIN)
    issues = result["backlog_issues"]
    assert (
        issues[0]["blocked_by"]
        == "PR [#25](https://github.com/acme/repo/pull/25), [#26](https://github.com/acme/repo/pull/26)"
    )
    assert issues[0]["blocking"] == "0 issues"


def test_fetch_backlog_issues_fully_blocked_issue_keeps_all_blocked_by_items() -> None:
    """A fully-blocked issue keeps all its blockers intact.

    A mix of PR-backed and PR-less blockers stays in backlog_issues, but is
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

    issues = result["backlog_issues"]
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


def test_fetch_backlog_issues_renders_null_priority_as_unset() -> None:
    """A missing priority is rendered as Unset and sorts last."""
    project_items = json.dumps(
        {
            "items": [
                {
                    "status": "Todo",
                    "type": "Task",
                    "assignees": ["octocat"],
                    "priority": None,
                    "content": {
                        "type": "Issue",
                        "number": 1,
                        "title": "A",
                        "url": "https://github.com/acme/repo/issues/1",
                    },
                },
            ],
        },
    )

    def fake_run_cmd(args: list[str]) -> str:
        if args[:3] == ["gh", "project", "item-list"]:
            return project_items
        return _empty_deps_graphql()

    result = bu.fetch_backlog_issues(fake_run_cmd, _REPO, "acme", _PROJECT_NUM, _LOGIN)
    issues = result["backlog_issues"]
    assert issues[0]["priority"] == "Unset"
