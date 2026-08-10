"""Tests for pr_blocking.py's apply_pr_blocking."""

from pr_blocking import apply_pr_blocking


def test_apply_pr_blocking_credits_pr_via_closed_issues_own_blocking_edge() -> None:
    """A PR is credited with unblocking whatever the issue it closes blocks.

    This is read directly from the closed issue's own `blocking` edge,
    fetched regardless of whether that issue is itself a leaf.
    """
    closing_issue_deps = {
        10: {"blocking": [{"number": 1}]},
    }
    pr_entries = [
        {
            "number": 25,
            "_closing_issues": [{"number": 10}],
        },
    ]

    apply_pr_blocking(pr_entries, closing_issue_deps)

    assert pr_entries[0]["blocking"] == "1 issue"


def test_apply_pr_blocking_credits_another_pr_instead_of_double_counting() -> None:
    """When another open PR also closes the blocked issue, credit that PR."""
    closing_issue_deps = {
        10: {"blocking": [{"number": 1}]},
    }
    pr_entries = [
        {"number": 25, "_closing_issues": [{"number": 10}]},
        {"number": 26, "_closing_issues": [{"number": 1}]},
    ]

    apply_pr_blocking(pr_entries, closing_issue_deps)

    assert pr_entries[0]["blocking"] == "1 PR"
