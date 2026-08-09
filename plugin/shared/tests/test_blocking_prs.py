"""Tests for the shared fetch_issue_dependencies module."""

import json

from shared.blocking_prs import fetch_issue_dependencies, fetch_issues_dependencies


def test_fetch_issue_dependencies_parses_open_blockers_and_prs() -> None:
    """Extracts open blocking issues, open PR details, and open downstream items."""
    api_response = json.dumps(
        {
            "data": {
                "repository": {
                    "issue": {
                        "blockedBy": {
                            "nodes": [
                                {
                                    "number": 10,
                                    "url": "https://github.com/owner/repo/issues/10",
                                    "state": "OPEN",
                                    "title": "Setup auth API",
                                    "timelineItems": {
                                        "nodes": [
                                            {
                                                "willCloseTarget": True,
                                                "source": {
                                                    "number": 25,
                                                    "url": "https://github.com/owner/repo/pull/25",
                                                    "title": "Add auth API endpoint",
                                                    "headRefName": "feature/auth-api",
                                                    "state": "OPEN",
                                                    "isDraft": False,
                                                },
                                            },
                                        ],
                                    },
                                },
                                {
                                    "number": 13,
                                    "url": "https://github.com/owner/repo/issues/13",
                                    "state": "OPEN",
                                    "title": "Setup database",
                                    "timelineItems": {
                                        "nodes": [
                                            {
                                                "willCloseTarget": False,
                                                "source": {
                                                    "number": 26,
                                                    "url": "https://github.com/owner/repo/pull/26",
                                                    "title": "Just a mention",
                                                    "headRefName": "feature/mention",
                                                    "state": "OPEN",
                                                    "isDraft": False,
                                                },
                                            },
                                        ],
                                    },
                                },
                                {
                                    "number": 5,
                                    "url": "https://github.com/owner/repo/issues/5",
                                    "state": "CLOSED",
                                    "title": "Old task",
                                    "timelineItems": {"nodes": []},
                                },
                            ],
                        },
                        "blocking": {
                            "nodes": [
                                {
                                    "number": 12,
                                    "url": "https://github.com/owner/repo/issues/12",
                                    "state": "OPEN",
                                    "title": "Auth UI",
                                },
                            ],
                        },
                    },
                },
            },
        },
    )

    def mock_run_cmd(_args: list[str]) -> str:
        return api_response

    res = fetch_issue_dependencies(mock_run_cmd, "owner", "repo", 11)
    expected_blocked_by_count = 2
    expected_blocker_1 = 10
    expected_blocker_2 = 13
    expected_blocking_1 = 12
    assert len(res["blocked_by"]) == expected_blocked_by_count
    assert res["blocked_by"][0]["number"] == expected_blocker_1
    assert res["blocked_by"][0]["open_pr"] == {
        "number": 25,
        "url": "https://github.com/owner/repo/pull/25",
        "title": "Add auth API endpoint",
        "branch_name": "feature/auth-api",
        "is_draft": False,
    }
    assert res["blocked_by"][1]["number"] == expected_blocker_2
    assert res["blocked_by"][1]["open_pr"] is None

    assert len(res["blocking"]) == 1
    assert res["blocking"][0]["number"] == expected_blocking_1


def test_fetch_issues_dependencies_batches_multiple_numbers_in_one_call() -> None:
    """Aliases each issue number in a single request and keys results by number."""
    api_response = json.dumps(
        {
            "data": {
                "repository": {
                    "i7": {
                        "blockedBy": {"nodes": []},
                        "blocking": {
                            "nodes": [
                                {
                                    "number": 12,
                                    "url": "u12",
                                    "state": "OPEN",
                                    "title": "Downstream",
                                },
                            ],
                        },
                    },
                    "i8": {"blockedBy": {"nodes": []}, "blocking": {"nodes": []}},
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
    assert res[8] == {"blocked_by": [], "blocking": []}


def test_fetch_issues_dependencies_returns_empty_dict_for_no_numbers() -> None:
    """Skips the API call entirely when there's nothing to fetch."""
    calls: list[list[str]] = []

    def mock_run_cmd(args: list[str]) -> str:
        calls.append(args)
        return "{}"

    assert fetch_issues_dependencies(mock_run_cmd, "owner", "repo", []) == {}
    assert calls == []
