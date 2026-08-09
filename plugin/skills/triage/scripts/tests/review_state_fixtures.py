"""Shared PR review-state field builder for review_state.py tests."""

from typing import Any


def pr_state_fields(
    *,
    review_state: str | None,
    thread_resolutions: list[bool],
    comment_bodies: list[str],
    mergeable: str = "MERGEABLE",
    checks_state: str | None = None,
) -> dict[str, Any]:
    """Build the inner PR fields dict shared by single and batched responses."""
    return {
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
        "mergeable": mergeable,
        "commits": {
            "nodes": []
            if checks_state is None
            else [{"commit": {"statusCheckRollup": {"state": checks_state}}}],
        },
    }
