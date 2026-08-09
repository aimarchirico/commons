"""Tests for backlog_utils.py's fetch_in_progress_issues."""

import json

import backlog_utils as bu

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
