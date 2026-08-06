"""Tests for backlog_utils.py's fetching, filtering, and sorting."""

import json

import backlog_utils as bu

_LOGIN = "octocat"
_REPO = ("acme", "repo")
_PROJECT_NUM = 9


def _empty_deps_graphql() -> str:
    return json.dumps({
        "data": {
            "repository": {
                "issue": {
                    "blockedBy": {"nodes": []},
                    "blocking": {"nodes": []},
                },
            },
        },
    })


def test_fetch_backlog_issues_filters_by_type_status_and_assignee() -> None:
    """Only Todo Story/Task/Bug issues assigned to or unassigned for login survive."""
    project_items = json.dumps({"items": [
        {
            "status": "Todo", "type": "Task", "assignees": ["octocat"],
            "priority": "Medium",
            "content": {
                "type": "Issue", "number": 1, "title": "Mine",
                "url": "https://github.com/acme/repo/issues/1",
            },
        },
        {
            "status": "Todo", "type": "Task", "assignees": [],
            "priority": "Medium",
            "content": {
                "type": "Issue", "number": 2, "title": "Free",
                "url": "https://github.com/acme/repo/issues/2",
            },
        },
        {
            "status": "Todo", "type": "Task", "assignees": ["bob"],
            "priority": "Medium",
            "content": {
                "type": "Issue", "number": 3, "title": "Bob's",
                "url": "https://github.com/acme/repo/issues/3",
            },
        },
        {
            "status": "Todo", "type": "Epic", "assignees": [],
            "priority": "Medium",
            "content": {
                "type": "Issue", "number": 4, "title": "Epic",
                "url": "https://github.com/acme/repo/issues/4",
            },
        },
        {
            "status": "Done", "type": "Task", "assignees": [],
            "priority": "Medium",
            "content": {
                "type": "Issue", "number": 5, "title": "Done",
                "url": "https://github.com/acme/repo/issues/5",
            },
        },
    ]})

    def fake_run_cmd(args: list[str]) -> str:
        if args[:3] == ["gh", "project", "item-list"]:
            return project_items
        return _empty_deps_graphql()

    result = bu.fetch_backlog_issues(
        fake_run_cmd, _REPO, "acme", _PROJECT_NUM, _LOGIN,
    )

    issues = result["backlog_issues"]
    assert [issue["number"] for issue in issues] == [1, 2]
    assert issues[0]["assignee"] == "You"
    assert issues[1]["assignee"] == "Unassigned"
    assert result["assigned_to_others_count"] == 1
    assert result["fully_blocked_count"] == 0


def test_fetch_backlog_issues_excludes_issues_with_open_blocker_without_pr() -> None:
    """An issue with an open blocker lacking an open PR is dropped entirely."""
    project_items = json.dumps({"items": [
        {
            "status": "Todo", "type": "Task", "assignees": ["octocat"],
            "priority": "Low",
            "content": {
                "type": "Issue", "number": 1, "title": "Mine",
                "url": "https://github.com/acme/repo/issues/1",
            },
        },
        {
            "status": "Todo", "type": "Task", "assignees": [],
            "priority": "Low",
            "content": {
                "type": "Issue", "number": 2, "title": "Free",
                "url": "https://github.com/acme/repo/issues/2",
            },
        },
    ]})

    blocked_deps_graphql = json.dumps({
        "data": {
            "repository": {
                "issue": {
                    "blockedBy": {
                        "nodes": [
                            {
                                "number": 10, "state": "OPEN",
                                "url": "https://github.com/acme/repo/issues/10",
                                "timelineItems": {"nodes": []},
                            },
                            {
                                "number": 11, "state": "CLOSED",
                                "url": "https://github.com/acme/repo/issues/11",
                                "timelineItems": {"nodes": []},
                            },
                        ],
                    },
                    "blocking": {"nodes": []},
                },
            },
        },
    })

    def fake_run_cmd(args: list[str]) -> str:
        if args[:3] == ["gh", "project", "item-list"]:
            return project_items
        if "-F" in args and "number=1" in args:
            return blocked_deps_graphql
        return _empty_deps_graphql()

    result = bu.fetch_backlog_issues(
        fake_run_cmd, _REPO, "acme", _PROJECT_NUM, _LOGIN,
    )

    issues = result["backlog_issues"]
    assert [issue["number"] for issue in issues] == [2]
    assert result["fully_blocked_count"] == 1


def test_fetch_backlog_issues_includes_issue_blocked_by_open_pr() -> None:
    """An issue blocked by an open issue that has an open PR is included."""
    project_items = json.dumps({"items": [
        {
            "status": "Todo", "type": "Task", "assignees": ["octocat"],
            "priority": "High",
            "content": {
                "type": "Issue", "number": 1, "title": "Mine",
                "url": "https://github.com/acme/repo/issues/1",
            },
        },
    ]})

    pr_blocked_graphql = json.dumps({
        "data": {
            "repository": {
                "issue": {
                    "blockedBy": {
                        "nodes": [
                            {
                                "number": 10,
                                "state": "OPEN",
                                "url": "https://github.com/acme/repo/issues/10",
                                "timelineItems": {
                                    "nodes": [
                                        {
                                            "subject": {
                                                "number": 25,
                                                "state": "OPEN",
                                                "headRefName": "feature/auth-api",
                                                "url": "https://github.com/acme/repo/pull/25",
                                            },
                                        },
                                    ],
                                },
                            },
                        ],
                    },
                    "blocking": {"nodes": []},
                },
            },
        },
    })

    def fake_run_cmd(args: list[str]) -> str:
        if args[:3] == ["gh", "project", "item-list"]:
            return project_items
        return pr_blocked_graphql

    result = bu.fetch_backlog_issues(
        fake_run_cmd, _REPO, "acme", _PROJECT_NUM, _LOGIN,
    )

    issues = result["backlog_issues"]
    assert len(issues) == 1
    expected_blocked_by = (
        "[#10](https://github.com/acme/repo/issues/10) "
        "(PR [#25](https://github.com/acme/repo/pull/25))"
    )
    assert issues[0]["blocked_by"] == expected_blocked_by
    assert issues[0]["blocking"] == "None"


def test_fetch_backlog_issues_renders_null_priority_as_unset() -> None:
    """A missing priority is rendered as Unset and sorts last."""
    project_items = json.dumps({"items": [
        {
            "status": "Todo", "type": "Task", "assignees": ["octocat"],
            "priority": None,
            "content": {
                "type": "Issue", "number": 1, "title": "A",
                "url": "https://github.com/acme/repo/issues/1",
            },
        },
    ]})

    def fake_run_cmd(args: list[str]) -> str:
        if args[:3] == ["gh", "project", "item-list"]:
            return project_items
        return _empty_deps_graphql()

    result = bu.fetch_backlog_issues(
        fake_run_cmd, _REPO, "acme", _PROJECT_NUM, _LOGIN,
    )

    issues = result["backlog_issues"]
    assert issues[0]["priority"] == "Unset"
