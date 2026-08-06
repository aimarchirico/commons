"""Tests for pr_utils.py's PR fetching, classification, and sorting."""

import json

import pr_utils as pu


def test_compute_technical_blockers() -> None:
    """Correctly formats technical blocker descriptions."""
    assert pu.compute_technical_blockers(True, "failing") == pu.TECHNICAL_BLOCKERS["BOTH"]
    assert pu.compute_technical_blockers(False, "failing") == pu.TECHNICAL_BLOCKERS["CHECKS"]
    assert pu.compute_technical_blockers(True, "passing") == pu.TECHNICAL_BLOCKERS["CONFLICT"]
    assert pu.compute_technical_blockers(False, "passing") == pu.TECHNICAL_BLOCKERS["NONE"]


def test_compute_review_blockers() -> None:
    """Correctly formats review blocker descriptions."""
    assert pu.compute_review_blockers("unresolved", "unresolved") == pu.REVIEW_BLOCKERS["BOTH"]
    assert pu.compute_review_blockers("resolved", "unresolved") == pu.REVIEW_BLOCKERS["COMMENTS"]
    assert pu.compute_review_blockers("unresolved", "resolved") == pu.REVIEW_BLOCKERS["THREADS"]
    assert pu.compute_review_blockers("resolved", "resolved") == pu.REVIEW_BLOCKERS["NONE"]


def test_linked_issue_for_returns_first_closing_issue() -> None:
    """Extracts first closing issue reference or None."""
    pr_with_link = {"closingIssuesReferences": [{"number": 10, "url": "issue-url"}]}
    assert pu.linked_issue_for(pr_with_link) == {"number": 10, "url": "issue-url"}
    assert pu.linked_issue_for({}) is None
