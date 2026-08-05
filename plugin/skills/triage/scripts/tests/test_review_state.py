"""Tests for the shared pull request review-state computation."""

from typing import Any

from review_state import fetch_review_state


def _response(
    *,
    review_state: str | None,
    thread_resolutions: list[bool],
    comment_bodies: list[str],
) -> dict[str, Any]:
    return {
        "data": {"repository": {"pullRequest": {
            "latestReview": {
                "nodes": [] if review_state is None else [{"state": review_state}],
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
        }}},
    }


def test_draft_short_circuits_without_querying() -> None:
    """A draft PR is always not_ready/none/none without calling graphql."""

    def _fail_graphql(*_args: object, **_kwargs: object) -> dict[str, Any]:
        raise AssertionError("graphql should not be called for drafts")

    result = fetch_review_state(_fail_graphql, "acme", "widgets", 1, is_draft=True)

    assert result == {"review": "not_ready", "threads": "none", "comments": "none"}


def test_maps_latest_review_state_and_resolves_threads() -> None:
    """The latest review's state and full thread resolution are reflected."""
    response = _response(
        review_state="APPROVED", thread_resolutions=[True, True], comment_bodies=[],
    )
    result = fetch_review_state(
        lambda *_a, **_kw: response, "acme", "widgets", 2, is_draft=False,
    )

    assert result == {"review": "approved", "threads": "resolved", "comments": "none"}


def test_any_unresolved_thread_marks_threads_unresolved() -> None:
    """A single unresolved thread among many resolved ones still counts."""
    response = _response(
        review_state="CHANGES_REQUESTED",
        thread_resolutions=[True, False],
        comment_bodies=[],
    )
    result = fetch_review_state(
        lambda *_a, **_kw: response, "acme", "widgets", 3, is_draft=False,
    )

    assert result["threads"] == "unresolved"
    assert result["review"] == "changes_requested"


def test_latest_comment_starting_with_resolved_marks_comments_resolved() -> None:
    """The most recent comment, by timestamp, decides the comments state."""
    response = _response(
        review_state=None,
        thread_resolutions=[],
        comment_bodies=["Please fix this.", "Resolved. Addressed in the last push."],
    )
    result = fetch_review_state(
        lambda *_a, **_kw: response, "acme", "widgets", 4, is_draft=False,
    )

    assert result == {"review": "none", "threads": "none", "comments": "resolved"}


def test_latest_comment_not_starting_with_resolved_marks_comments_unresolved() -> None:
    """Any other trailing comment leaves the comments state unresolved."""
    response = _response(
        review_state=None,
        thread_resolutions=[],
        comment_bodies=["Resolved. Done.", "Actually, one more thing."],
    )
    result = fetch_review_state(
        lambda *_a, **_kw: response, "acme", "widgets", 5, is_draft=False,
    )

    assert result["comments"] == "unresolved"
