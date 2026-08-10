"""Tests for pr_utils.py's PR fetching, classification, and sorting."""

import pr_utils as pu


def test_compute_technical_blockers() -> None:
    """Correctly formats technical blocker descriptions."""
    assert (
        pu.compute_technical_blockers(conflicting=True, checks="failing")
        == pu.TECHNICAL_BLOCKERS["BOTH"]
    )
    assert (
        pu.compute_technical_blockers(conflicting=False, checks="failing")
        == pu.TECHNICAL_BLOCKERS["CHECKS"]
    )
    assert (
        pu.compute_technical_blockers(conflicting=True, checks="passing")
        == pu.TECHNICAL_BLOCKERS["CONFLICT"]
    )
    assert (
        pu.compute_technical_blockers(conflicting=False, checks="passing")
        == pu.TECHNICAL_BLOCKERS["NONE"]
    )


def test_compute_review_blockers() -> None:
    """Correctly formats review blocker descriptions."""
    assert (
        pu.compute_review_blockers("unresolved", "unresolved")
        == pu.REVIEW_BLOCKERS["BOTH"]
    )
    assert (
        pu.compute_review_blockers("resolved", "unresolved")
        == pu.REVIEW_BLOCKERS["COMMENTS"]
    )
    assert (
        pu.compute_review_blockers("unresolved", "resolved")
        == pu.REVIEW_BLOCKERS["THREADS"]
    )
    assert (
        pu.compute_review_blockers("resolved", "resolved") == pu.REVIEW_BLOCKERS["NONE"]
    )


def test_linked_issues_for_returns_all_closing_issues() -> None:
    """Extracts every closing issue reference, or an empty list when there are none."""
    pr_with_links = {
        "closingIssuesReferences": [
            {"number": 10, "url": "issue-url-10"},
            {"number": 11, "url": "issue-url-11"},
        ],
    }
    assert pu.linked_issues_for(pr_with_links) == [
        {"number": 10, "url": "issue-url-10"},
        {"number": 11, "url": "issue-url-11"},
    ]
    assert pu.linked_issues_for({}) == []
