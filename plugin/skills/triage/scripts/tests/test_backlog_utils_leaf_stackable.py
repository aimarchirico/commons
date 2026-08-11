"""Tests for backlog_utils.py's leaf filtering and single-PR stackable rule."""

import json

import backlog_utils as bu

_LOGIN = "octocat"
_REPO = ("acme", "repo")
_PROJECT_NUM = 9


def _blocking_issue_node(num: int, pr_num: int) -> dict:
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


def _single_item_project(number: int) -> str:
    return json.dumps(
        {
            "items": [
                {
                    "status": "Todo",
                    "type": "Task",
                    "assignees": ["octocat"],
                    "priority": "High",
                    "content": {
                        "type": "Issue",
                        "number": number,
                        "title": "Mine",
                        "url": f"https://github.com/acme/repo/issues/{number}",
                    },
                },
            ],
        },
    )


def test_fetch_backlog_issues_stackable_when_blockers_share_one_open_pr() -> None:
    """Two blockers closed by the same PR are stackable on that one PR."""
    project_items = _single_item_project(1)
    pr_blocked_graphql = json.dumps(
        {
            "data": {
                "repository": {
                    "i1": {
                        "blockedBy": {
                            "nodes": [
                                _blocking_issue_node(10, 25),
                                _blocking_issue_node(11, 25),
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

    assert [i["number"] for i in result["assigned_stackable"]] == [1]
    entry = result["assigned_stackable"][0]
    assert entry["blocked_by"] == (
        "PR [#25](https://github.com/acme/repo/pull/25), "
        "PR [#25](https://github.com/acme/repo/pull/25)"
    )
    assert entry["blocking"] == "None"


def test_fetch_backlog_issues_hides_when_blockers_span_multiple_open_prs() -> None:
    """Blockers resolving to two different PRs have no single branch to stack on."""
    project_items = _single_item_project(1)
    pr_blocked_graphql = json.dumps(
        {
            "data": {
                "repository": {
                    "i1": {
                        "blockedBy": {
                            "nodes": [
                                _blocking_issue_node(10, 25),
                                _blocking_issue_node(11, 26),
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

    assert result["fully_blocked_count"] == 1
    for bucket in (
        "assigned_ready",
        "assigned_stackable",
        "available_ready",
        "available_stackable",
    ):
        assert result[bucket] == []


def test_fetch_backlog_issues_excludes_non_leaf_issues() -> None:
    """A Story with its own Subtasks isn't itself an actionable row."""
    project_items = _single_item_project(1)
    deps_graphql = json.dumps(
        {
            "data": {
                "repository": {
                    "i1": {
                        "blockedBy": {"nodes": []},
                        "blocking": {"nodes": []},
                        "subIssuesSummary": {"total": 2, "completed": 0},
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

    assert result["leaf_issues"] == []
    assert result["fully_blocked_count"] == 0


def test_fetch_backlog_issues_includes_parent_when_all_subissues_closed() -> None:
    """A Story whose Subtasks are all closed is treated as a leaf again."""
    project_items = _single_item_project(1)
    deps_graphql = json.dumps(
        {
            "data": {
                "repository": {
                    "i1": {
                        "blockedBy": {"nodes": []},
                        "blocking": {"nodes": []},
                        "subIssuesSummary": {"total": 2, "completed": 2},
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

    assert [i["number"] for i in result["leaf_issues"]] == [1]


def test_fetch_backlog_issues_annotates_blocker_inherited_via_parent() -> None:
    """A blocker on the leaf's own parent is shown with a via-parent note."""
    project_items = _single_item_project(1)
    deps_graphql = json.dumps(
        {
            "data": {
                "repository": {
                    "i1": {
                        "blockedBy": {"nodes": []},
                        "blocking": {"nodes": []},
                        "parent": {
                            "blockedBy": {"nodes": [_blocking_issue_node(10, 25)]},
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

    assert [i["number"] for i in result["assigned_stackable"]] == [1]
    assert result["assigned_stackable"][0]["blocked_by"] == (
        "PR [#25](https://github.com/acme/repo/pull/25) (via parent)"
    )
