"""Tests for backlog_utils.py's fetching, filtering, and sorting."""

import json
from collections.abc import Callable

import backlog_utils as bu

_LOGIN = "octocat"


def _no_deps_response(number: int) -> tuple[tuple[str, ...], str]:
    key = ("gh", "issue", "view", str(number), "--json", "blockedBy,blocking")
    return key, json.dumps({
        "blockedBy": {"nodes": [], "totalCount": 0},
        "blocking": {"nodes": [], "totalCount": 0},
    })


def _run_cmd_from(
    responses: dict[tuple[str, ...], str],
) -> Callable[[list[str]], str]:
    def fake_run_cmd(args: list[str]) -> str:
        return responses[tuple(args)]
    return fake_run_cmd


def test_fetch_backlog_issues_filters_by_type_status_and_assignee() -> None:
    """Only Todo Story/Task/Bug issues assigned to or unassigned for login survive.

    A Story/Task/Bug decomposed from an Epic still has a parent, but that's
    expected: those are the actionable leaf items and belong in the backlog.
    """
    project_items = json.dumps({"items": [
        {
            "status": "Todo", "type": "Task", "assignees": ["octocat"],
            "priority": "Medium",
            "content": {"type": "Issue", "number": 1, "title": "Mine", "url": "u1"},
        },
        {
            "status": "Todo", "type": "Task", "assignees": [],
            "priority": "Medium",
            "content": {"type": "Issue", "number": 2, "title": "Free", "url": "u2"},
        },
        {
            "status": "Todo", "type": "Task", "assignees": ["bob"],
            "priority": "Medium",
            "content": {"type": "Issue", "number": 3, "title": "Bob's", "url": "u3"},
        },
        {
            "status": "Todo", "type": "Epic", "assignees": [],
            "priority": "Medium",
            "content": {"type": "Issue", "number": 4, "title": "Epic", "url": "u4"},
        },
        {
            "status": "Done", "type": "Task", "assignees": [],
            "priority": "Medium",
            "content": {"type": "Issue", "number": 5, "title": "Done", "url": "u5"},
        },
    ]})
    responses = {
        ("gh", "project", "item-list", "9", "--owner", "acme",
         "--format", "json", "--limit", "200"): project_items,
    }
    for number in (1, 2):
        key, body = _no_deps_response(number)
        responses[key] = body

    result = bu.fetch_backlog_issues(_run_cmd_from(responses), "acme", 9, _LOGIN)

    assert [issue["number"] for issue in result] == [1, 2]
    assert result[0]["assignee"] == "You"
    assert result[1]["assignee"] == "Unassigned"


def test_fetch_backlog_issues_excludes_issues_blocked_by_an_open_issue() -> None:
    """An issue with an open blocker is dropped entirely, not just demoted."""
    project_items = json.dumps({"items": [
        {
            "status": "Todo", "type": "Task", "assignees": ["octocat"],
            "priority": "Low",
            "content": {"type": "Issue", "number": 1, "title": "Mine", "url": "u1"},
        },
        {
            "status": "Todo", "type": "Task", "assignees": [],
            "priority": "Low",
            "content": {"type": "Issue", "number": 2, "title": "Free", "url": "u2"},
        },
    ]})
    responses = {
        ("gh", "project", "item-list", "9", "--owner", "acme",
         "--format", "json", "--limit", "200"): project_items,
        ("gh", "issue", "view", "1", "--json", "blockedBy,blocking"): json.dumps({
            "blockedBy": {
                "nodes": [
                    {"number": 10, "state": "OPEN"},
                    {"number": 11, "state": "CLOSED"},
                ],
                "totalCount": 2,
            },
            "blocking": {"nodes": [], "totalCount": 0},
        }),
    }
    key, body = _no_deps_response(2)
    responses[key] = body

    result = bu.fetch_backlog_issues(_run_cmd_from(responses), "acme", 9, _LOGIN)

    assert [issue["number"] for issue in result] == [2]


def test_fetch_backlog_issues_renders_null_priority_as_unset() -> None:
    """A missing priority is rendered as Unset and sorts last."""
    project_items = json.dumps({"items": [
        {
            "status": "Todo", "type": "Task", "assignees": ["octocat"],
            "priority": None,
            "content": {"type": "Issue", "number": 1, "title": "A", "url": "u1"},
        },
    ]})
    responses = {
        ("gh", "project", "item-list", "9", "--owner", "acme",
         "--format", "json", "--limit", "200"): project_items,
    }
    key, body = _no_deps_response(1)
    responses[key] = body

    result = bu.fetch_backlog_issues(_run_cmd_from(responses), "acme", 9, _LOGIN)

    assert result[0]["priority"] == "Unset"


def test_fetch_backlog_issues_sorts_by_assignee_priority_then_blocking_count() -> None:
    """Sort order: assigned before unassigned, then priority, then blocking count."""
    project_items = json.dumps({"items": [
        {
            "status": "Todo", "type": "Task", "assignees": [],
            "priority": "High",
            "content": {"type": "Issue", "number": 1, "title": "A", "url": "u1"},
        },
        {
            "status": "Todo", "type": "Task", "assignees": ["octocat"],
            "priority": "Low",
            "content": {"type": "Issue", "number": 2, "title": "B", "url": "u2"},
        },
        {
            "status": "Todo", "type": "Task", "assignees": ["octocat"],
            "priority": "Low",
            "content": {"type": "Issue", "number": 3, "title": "C", "url": "u3"},
        },
    ]})
    responses = {
        ("gh", "project", "item-list", "9", "--owner", "acme",
         "--format", "json", "--limit", "200"): project_items,
        ("gh", "issue", "view", "3", "--json", "blockedBy,blocking"): json.dumps({
            "blockedBy": {"nodes": [], "totalCount": 0},
            "blocking": {"nodes": [{"number": 99, "state": "OPEN"}], "totalCount": 1},
        }),
    }
    for number in (1, 2):
        key, body = _no_deps_response(number)
        responses[key] = body

    result = bu.fetch_backlog_issues(_run_cmd_from(responses), "acme", 9, _LOGIN)

    assert [issue["number"] for issue in result] == [3, 2, 1]
    assert result[0]["blocking"] == "#99"
    assert result[1]["blocking"] == "Not blocking"
    assert result[2]["priority"] == "High"
