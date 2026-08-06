"""Tests for the shared pull request review-state computation."""

from typing import Any

from review_state import fetch_review_state


def _response(
    *,
    review_state: str | None,
    thread_resolutions: list[bool],
    comment_bodies: list[str],
    mergeable: str = "MERGEABLE",
    checks_state: str | None = None,
) -> dict[str, Any]:
    return {
        "data": {
            "repository": {
                "pullRequest": {
                    "latestReview": {
                        "nodes": []
                        if review_state is None
                        else [{"state": review_state}],
                    },
                    "allReviews": {"nodes": []},
                    "reviewThreads": {
                        "nodes": [{"isResolved": r} for r in thread_resolutions],
                    },
                    "comments": {
                        "nodes": [
                            {"body": body, "createdAt": f"2024-01-01T00:00:{i:02d}Z"}
                            for i, body in enumerate(comment_bodies)
                        ],
                    },
                    "mergeable": mergeable,
                    "commits": {
                        "nodes": []
                        if checks_state is None
                        else [
                            {"commit": {"statusCheckRollup": {"state": checks_state}}},
                        ],
                    },
                },
            },
        },
    }


def test_maps_latest_review_state_and_resolves_threads() -> None:
    """The latest review's state and full thread resolution are reflected."""
    response = _response(
        review_state="APPROVED",
        thread_resolutions=[True, True],
        comment_bodies=[],
    )
    result = fetch_review_state(lambda *_a, **_kw: response, "acme", "widgets", 2)

    assert result == {
        "state": "approved",
        "threads": "resolved",
        "comments": "none",
        "conflicting": False,
        "checks": "none",
    }


def test_any_unresolved_thread_marks_threads_unresolved() -> None:
    """A single unresolved thread among many resolved ones still counts."""
    response = _response(
        review_state="CHANGES_REQUESTED",
        thread_resolutions=[True, False],
        comment_bodies=[],
    )
    result = fetch_review_state(lambda *_a, **_kw: response, "acme", "widgets", 3)

    assert result["threads"] == "unresolved"
    assert result["state"] == "changes_requested"


def test_latest_comment_starting_with_resolved_marks_comments_resolved() -> None:
    """The most recent comment, by timestamp, decides the comments state."""
    response = _response(
        review_state=None,
        thread_resolutions=[],
        comment_bodies=["Please fix this.", "Resolved. Addressed in the last push."],
    )
    result = fetch_review_state(lambda *_a, **_kw: response, "acme", "widgets", 4)

    assert result == {
        "state": "no_reviews",
        "threads": "none",
        "comments": "resolved",
        "conflicting": False,
        "checks": "none",
    }


def test_latest_comment_not_starting_with_resolved_marks_comments_unresolved() -> None:
    """Any other trailing comment leaves the comments state unresolved."""
    response = _response(
        review_state=None,
        thread_resolutions=[],
        comment_bodies=["Resolved. Done.", "Actually, one more thing."],
    )
    result = fetch_review_state(lambda *_a, **_kw: response, "acme", "widgets", 5)

    assert result["comments"] == "unresolved"


def test_verdict_after_a_leading_header_is_still_recognized() -> None:
    """A markdown header before the verdict line doesn't hide the verdict."""
    response = _response(
        review_state=None,
        thread_resolutions=[],
        comment_bodies=["## Resolution summary\n\nResolved. Addressed above."],
    )
    result = fetch_review_state(lambda *_a, **_kw: response, "acme", "widgets", 6)

    assert result["comments"] == "resolved"


def test_conflicting_mergeable_state_is_reported() -> None:
    """A CONFLICTING mergeable state sets conflicting to True."""
    response = _response(
        review_state=None,
        thread_resolutions=[],
        comment_bodies=[],
        mergeable="CONFLICTING",
    )
    result = fetch_review_state(lambda *_a, **_kw: response, "acme", "widgets", 7)

    assert result["conflicting"] is True


def test_failing_check_rollup_is_reported() -> None:
    """A FAILURE status check rollup maps to a failing checks state."""
    response = _response(
        review_state=None,
        thread_resolutions=[],
        comment_bodies=[],
        checks_state="FAILURE",
    )
    result = fetch_review_state(lambda *_a, **_kw: response, "acme", "widgets", 8)

    assert result["checks"] == "failing"


def test_no_commits_reports_no_checks() -> None:
    """No commit rollup (e.g. checks not yet configured) reports none."""
    response = _response(review_state=None, thread_resolutions=[], comment_bodies=[])
    result = fetch_review_state(lambda *_a, **_kw: response, "acme", "widgets", 9)

    assert result["checks"] == "none"


def test_draft_review_activity_and_merge_state_are_still_computed_for_real() -> None:
    """A draft's comments/threads/conflicting/checks are real, not forced to none.

    Drafts can carry all the same activity; only the bucket/suggestion a
    caller derives from `isDraft` treats them specially, not this data.
    """
    response = _response(
        review_state="COMMENTED",
        thread_resolutions=[False],
        comment_bodies=["wip"],
        mergeable="CONFLICTING",
        checks_state="FAILURE",
    )
    result = fetch_review_state(lambda *_a, **_kw: response, "acme", "widgets", 10)

    assert result == {
        "state": "commented",
        "threads": "unresolved",
        "comments": "unresolved",
        "conflicting": True,
        "checks": "failing",
    }
