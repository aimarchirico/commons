"""Tests for pr_blocking.py's apply_pr_blocking."""

from pr_blocking import apply_pr_blocking


def test_apply_pr_blocking_credits_pr_closing_a_blocker_of_a_fully_blocked_issue() -> (
    None
):
    """A PR closing a blocker of a fully-blocked issue is credited.

    The PR must be credited with blocking that issue, even though the issue
    itself is excluded from the display buckets because another blocker
    still has no open PR (this reproduces the bios repo #159/#219-#225 bug).
    """
    backlog_issues = [
        {
            "number": 1,
            "_blocked_by_items": [
                {"number": 10, "open_pr": {"number": 25}},
                {"number": 11, "open_pr": None},
            ],
            "_blocking_items": [],
        },
    ]
    pr_entries = [
        {
            "number": 25,
            "_closing_issues": [{"number": 10}],
        },
    ]

    apply_pr_blocking(pr_entries, backlog_issues)

    assert pr_entries[0]["blocking"] == "1 issue"
