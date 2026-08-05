"""Shared pull request review-state computation for skills that need it.

Both the ``triage`` and ``resolve`` skills need to answer the same question —
what state is a pull request's review, threads, and comments in — so the
GraphQL query and its interpretation live here once instead of being
duplicated per skill.
"""

from collections.abc import Callable
from typing import Any

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
    """Compute a pull request's ``review``, ``threads``, and ``comments`` state.

    ``graphql`` must match ``graphql(query: str, **variables) -> dict``,
    returning the parsed GraphQL response, so callers can reuse their own
    ``gh api graphql`` wrapper.

    Drafts short-circuit to ``not_ready``/``none``/``none`` without querying,
    since a draft's review activity isn't actionable until it's marked ready.
    """
    if is_draft:
        return {"review": "not_ready", "threads": "none", "comments": "none"}

    api_data = graphql(_REVIEW_STATE_QUERY, owner=owner, repo=repo_name, number=number)
    pr = api_data.get("data", {}).get("repository", {}).get("pullRequest") or {}

    latest_review_nodes = pr.get("latestReview", {}).get("nodes", [])
    review = (
        "none" if not latest_review_nodes
        else _REVIEW_STATE_MAP.get(latest_review_nodes[0]["state"], "none")
    )

    thread_nodes = pr.get("reviewThreads", {}).get("nodes", [])
    threads = (
        "none" if not thread_nodes
        else "resolved" if all(t["isResolved"] for t in thread_nodes)
        else "unresolved"
    )

    all_comments = [
        c for c in (
            pr.get("comments", {}).get("nodes", [])
            + pr.get("allReviews", {}).get("nodes", [])
        )
        if c.get("body")
    ]
    all_comments.sort(key=lambda c: c["createdAt"])
    comments = (
        "none" if not all_comments
        else "resolved" if all_comments[-1]["body"].startswith("Resolved.")
        else "unresolved"
    )

    return {"review": review, "threads": threads, "comments": comments}
