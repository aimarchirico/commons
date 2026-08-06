"""Tests for the shared fetch_issue_dependencies module."""

import json

from shared.blocking_prs import fetch_issue_dependencies


def test_fetch_issue_dependencies_parses_open_blockers_and_prs() -> None:
    """Extracts open blocking issues, open PR details, and open downstream items."""
    api_response = json.dumps({
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
                                            "subject": {
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
                                "timelineItems": {"nodes": []},
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
    })

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
