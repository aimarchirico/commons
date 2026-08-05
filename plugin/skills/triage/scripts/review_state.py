"""Pull request review-state computation used by triage's collect_triage.py."""

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


def _first_substantive_line(body: str) -> str:
    for line in body.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped
    return ""


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
        else "resolved"
        if _first_substantive_line(all_comments[-1]["body"]).startswith("Resolved.")
        else "unresolved"
    )

    return {"state": state, "threads": threads, "comments": comments}
