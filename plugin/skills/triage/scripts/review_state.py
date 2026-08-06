#!/usr/bin/env python3
"""Pull request review-state computation used by triage's collect_triage.py."""

import importlib.util
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Any


def _load_pr_feedback() -> ModuleType:
    shared_dir = Path(__file__).resolve().parent.parent.parent.parent / "shared"
    module_path = shared_dir / "pr_feedback.py"
    spec = importlib.util.spec_from_file_location("pr_feedback", module_path)
    if spec is None or spec.loader is None:
        msg = f"Cannot load pr_feedback from {module_path}"
        raise ImportError(msg)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_pr_feedback = _load_pr_feedback()
comments_since_checkpoint = _pr_feedback.comments_since_checkpoint
unresolved_threads = _pr_feedback.unresolved_threads

_REVIEW_STATE_QUERY = """
query($owner: String!, $repo: String!, $number: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $number) {
      latestReview: reviews(last: 1) { nodes { state } }
      allReviews: reviews(first: 100) { nodes { body createdAt } }
      reviewThreads(first: 100) { nodes { isResolved } }
      comments(first: 100) { nodes { body createdAt } }
      mergeable
      commits(last: 1) {
        nodes { commit { statusCheckRollup { state } } }
      }
    }
  }
}
"""

NO_REVIEWS = "no_reviews"
STATE_NONE = "none"
STATE_UNRESOLVED = "unresolved"
STATE_RESOLVED = "resolved"

_REVIEW_STATE_MAP = {
    "APPROVED": "approved",
    "CHANGES_REQUESTED": "changes_requested",
    "COMMENTED": "commented",
}

_CHECKS_STATE_MAP = {
    "SUCCESS": "passing",
    "FAILURE": "failing",
    "ERROR": "failing",
    "PENDING": "pending",
    "EXPECTED": "pending",
}



def fetch_review_state(
    graphql: Callable[..., dict[str, Any]],
    owner: str,
    repo_name: str,
    number: int,
) -> dict[str, Any]:
    """Compute a pull request's real review and merge state.

    ``graphql`` must match ``graphql(query: str, **variables) -> dict``,
    returning the parsed GraphQL response, so callers can reuse their own
    ``gh api graphql`` wrapper.

    Draft PRs can still carry comments, threads, conflicts, and failing
    checks (GitHub allows commenting/reviewing drafts), so nothing here is
    special-cased for drafts; callers decide what's actionable from
    ``isDraft`` separately.
    """
    api_data = graphql(_REVIEW_STATE_QUERY, owner=owner, repo=repo_name, number=number)
    pr = api_data.get("data", {}).get("repository", {}).get("pullRequest") or {}

    latest_review_nodes = pr.get("latestReview", {}).get("nodes", [])
    state = (
        NO_REVIEWS
        if not latest_review_nodes
        else _REVIEW_STATE_MAP.get(latest_review_nodes[0]["state"], NO_REVIEWS)
    )

    thread_nodes = pr.get("reviewThreads", {}).get("nodes", [])
    threads = (
        STATE_NONE
        if not thread_nodes
        else STATE_UNRESOLVED
        if unresolved_threads(thread_nodes)
        else STATE_RESOLVED
    )

    all_comments = [
        c
        for c in (
            pr.get("comments", {}).get("nodes", [])
            + pr.get("allReviews", {}).get("nodes", [])
        )
        if c.get("body")
    ]
    comments = (
        STATE_NONE
        if not all_comments
        else STATE_UNRESOLVED
        if comments_since_checkpoint(all_comments)
        else STATE_RESOLVED
    )

    conflicting = pr.get("mergeable") == "CONFLICTING"

    commit_nodes = pr.get("commits", {}).get("nodes", [])
    rollup = (
        (commit_nodes[0]["commit"].get("statusCheckRollup") or {}).get("state")
        if commit_nodes
        else None
    )
    checks = STATE_NONE if rollup is None else _CHECKS_STATE_MAP.get(rollup, STATE_NONE)


    return {
        "state": state,
        "threads": threads,
        "comments": comments,
        "conflicting": conflicting,
        "checks": checks,
    }
