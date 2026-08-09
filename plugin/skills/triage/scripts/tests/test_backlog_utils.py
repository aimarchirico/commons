"""Tests for backlog_utils.py's fetching, filtering, and sorting."""

import json

import backlog_utils as bu

_LOGIN = "octocat"
_REPO = ("acme", "repo")
_PROJECT_NUM = 9


def _empty_deps_graphql() -> str:
    res = {
        "data": {
            "repository": {
                "issue": {"blockedBy": {"nodes": []}, "blocking": {"nodes": []}},
            },
        },
    }
    return json.dumps(res)


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


def test_fetch_backlog_issues_excludes_issues_with_open_blocker_without_pr() -> None:
    """An issue with an open blocker lacking an open PR is dropped entirely."""
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

    blocked_deps_graphql = json.dumps(
        {
            "data": {
                "repository": {
                    "issue": {
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
                },
            },
        },
    )

    def fake_run_cmd(args: list[str]) -> str:
        if args[:3] == ["gh", "project", "item-list"]:
            return project_items
        if "-F" in args and "number=1" in args:
            return blocked_deps_graphql
        return _empty_deps_graphql()

    result = bu.fetch_backlog_issues(
        fake_run_cmd,
        _REPO,
        "acme",
        _PROJECT_NUM,
        _LOGIN,
    )

    issues = result["backlog_issues"]
    assert [issue["number"] for issue in issues] == [2]
    assert result["fully_blocked_count"] == 1


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
                    "issue": {
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


def test_fetch_in_progress_issues_filters_by_type_and_sorts_by_priority() -> None:
    """Only Story/Task/Bug issues survive, sorted High before Low."""
    project_items = json.dumps(
        {
            "items": [
                {
                    "type": "Task",
                    "priority": "Low",
                    "content": {
                        "type": "Issue",
                        "number": 1,
                        "title": "Low prio",
                        "url": "https://github.com/acme/repo/issues/1",
                    },
                },
                {
                    "type": "Task",
                    "priority": "High",
                    "content": {
                        "type": "Issue",
                        "number": 2,
                        "title": "High prio",
                        "url": "https://github.com/acme/repo/issues/2",
                    },
                },
                {
                    "type": "Epic",
                    "priority": "High",
                    "content": {
                        "type": "Issue",
                        "number": 3,
                        "title": "Epic",
                        "url": "https://github.com/acme/repo/issues/3",
                    },
                },
            ],
        },
    )

    def fake_run_cmd(args: list[str]) -> str:
        if args[:3] == ["gh", "project", "item-list"]:
            return project_items
        return _empty_deps_graphql()

    result = bu.fetch_in_progress_issues(fake_run_cmd, _REPO, "acme", _PROJECT_NUM)

    assert [issue["number"] for issue in result] == [2, 1]
    assert result[0]["suggestion"] == "Continue implementing or open PR"


def test_fetch_in_progress_issues_queries_status_and_assignee_server_side() -> None:
    """The gh call filters to In Progress issues assigned to the caller."""
    captured: list[list[str]] = []

    def fake_run_cmd(args: list[str]) -> str:
        captured.append(args)
        if args[:3] == ["gh", "project", "item-list"]:
            return json.dumps({"items": []})
        return _empty_deps_graphql()

    bu.fetch_in_progress_issues(fake_run_cmd, _REPO, "acme", _PROJECT_NUM)

    assert captured[0][-2:] == ["--query", 'status:"In Progress" is:issue assignee:@me']

