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

    result = bu.fetch_backlog_issues(fake_run_cmd, _REPO, "acme", _PROJECT_NUM, _LOGIN)

    graphql_calls = [c for c in calls if c[:3] == ["gh", "api", "graphql"]]
    assert len(graphql_calls) == 1
    assert "i1: issue(number: 1)" in graphql_calls[0][4]
    assert "i2: issue(number: 2)" in graphql_calls[0][4]

    issues = result["backlog_issues"]
    assert sorted(issue["number"] for issue in issues) == [1, 2]
    assert result["fully_blocked_count"] == 1
    for bucket in (
        "assigned_ready",
        "assigned_stackable",
        "available_ready",
        "available_stackable",
    ):
        assert 1 not in {i["number"] for i in result[bucket]}


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
