#!/usr/bin/env python3
"""Pull request review-state computation used by triage's collect_triage.py."""

from collections.abc import Callable
from typing import Any

from plugin_shared.pr_feedback import comments_since_checkpoint, unresolved_threads

_REVIEW_STATE_QUERY = """
query($owner: String!, $repo: String!, $number: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $number) {
      latestReview: reviews(last: 1) { nodes { state } }
      allReviews: reviews(first: 100) { nodes { body createdAt } }
      reviewThreads(first: 100) { nodes { isResolved } }
      comments(first: 100) { nodes { body createdAt } }
    }
  }
}
"""

_REVIEW_STATE_MAP = {
    "APPROVED": "approved",
    "CHANGES_REQUESTED": "changes_requested",
    "COMMENTED": "commented",
}


def fetch_review_state(
    graphql: Callable[..., dict[str, Any]],
    owner: str,
    repo_name: str,
    number: int,
    *,
    is_draft: bool,
) -> dict[str, str]:
    """Compute a pull request's ``state``, ``threads``, and ``comments``.

    ``graphql`` must match ``graphql(query: str, **variables) -> dict``,
    returning the parsed GraphQL response, so callers can reuse their own
    ``gh api graphql`` wrapper.

    Drafts short-circuit to ``not_ready``/``none``/``none`` without querying,
    since a draft's review activity isn't actionable until it's marked ready.
    """
    if is_draft:
        return {"state": "not_ready", "threads": "none", "comments": "none"}

    api_data = graphql(_REVIEW_STATE_QUERY, owner=owner, repo=repo_name, number=number)
    pr = api_data.get("data", {}).get("repository", {}).get("pullRequest") or {}

    latest_review_nodes = pr.get("latestReview", {}).get("nodes", [])
    state = (
        "none" if not latest_review_nodes
        else _REVIEW_STATE_MAP.get(latest_review_nodes[0]["state"], "none")
    )

    thread_nodes = pr.get("reviewThreads", {}).get("nodes", [])
    threads = (
        "none" if not thread_nodes
        else "unresolved" if unresolved_threads(thread_nodes)
        else "resolved"
    )

    all_comments = [
        c for c in (
            pr.get("comments", {}).get("nodes", [])
            + pr.get("allReviews", {}).get("nodes", [])
        )
        if c.get("body")
    ]
    comments = (
        "none" if not all_comments
        else "unresolved" if comments_since_checkpoint(all_comments)
        else "resolved"
    )

    return {"state": state, "threads": threads, "comments": comments}
