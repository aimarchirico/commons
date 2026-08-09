"""Shared utility for fetching issue dependencies and attached open PRs."""

import json
from collections.abc import Callable
from typing import Any

_ISSUE_DEPENDENCY_FIELDS = """
      blockedBy(first: 10) {
        nodes {
          number
          url
          state
          title
          timelineItems(
            first: 20
            itemTypes: [CROSS_REFERENCED_EVENT]
          ) {
            nodes {
              ... on CrossReferencedEvent {
                willCloseTarget
                source {
                  ... on PullRequest {
                    number
                    url
                    title
                    headRefName
                    state
                    isDraft
                  }
                }
              }
            }
          }
        }
      }
      blocking(first: 10) {
        nodes {
          number
          url
          state
          title
        }
      }
"""

BLOCKING_PRS_QUERY = f"""
query($owner: String!, $repo: String!, $number: Int!) {{
  repository(owner: $owner, name: $repo) {{
    issue(number: $number) {{
      {_ISSUE_DEPENDENCY_FIELDS}
    }}
  }}
}}
"""


def _parse_issue_dependencies(issue_data: dict[str, Any]) -> dict[str, Any]:
    blocked_by_nodes = issue_data.get("blockedBy", {}).get("nodes", [])
    blocking_nodes = issue_data.get("blocking", {}).get("nodes", [])

    blocked_by_list = []
    for node in blocked_by_nodes:
        if node.get("state") != "OPEN":
            continue

        open_pr = None
        timeline = node.get("timelineItems", {}).get("nodes", [])
        for item in timeline:
            if not item.get("willCloseTarget"):
                continue
            pr = item.get("source")
            if isinstance(pr, dict) and pr.get("state") == "OPEN":
                head_ref = pr.get("headRefName")
                if head_ref:
                    open_pr = {
                        "number": pr.get("number"),
                        "url": pr.get("url"),
                        "title": pr.get("title"),
                        "branch_name": head_ref,
                        "is_draft": bool(pr.get("isDraft", False)),
                    }
                    break

        blocked_by_list.append(
            {
                "number": node.get("number"),
                "url": node.get("url"),
                "title": node.get("title"),
                "open_pr": open_pr,
            },
        )

    blocking_list = [
        {
            "number": node.get("number"),
            "url": node.get("url"),
            "title": node.get("title"),
        }
        for node in blocking_nodes
        if node.get("state") == "OPEN"
    ]

    return {
        "blocked_by": blocked_by_list,
        "blocking": blocking_list,
    }


def fetch_issue_dependencies(
    run_cmd: Callable[[list[str]], str],
    owner: str,
    repo_name: str,
    number: int,
) -> dict[str, Any]:
    """Fetch issue blockedBy and blocking relationships with attached open PR details.

    Returns a dict containing:
    - blocked_by: list of open blocking issues:
        [
            {
                "number": int,
                "url": str,
                "title": str,
                "open_pr": {
                    "number": int,
                    "url": str,
                    "title": str,
                    "branch_name": str,
                    "is_draft": bool,
                } | None
            }
        ]
    - blocking: list of open downstream issues:
        [
            {
                "number": int,
                "url": str,
                "title": str,
            }
        ]
    """
    args = [
        "gh",
        "api",
        "graphql",
        "-f",
        f"query={BLOCKING_PRS_QUERY}",
        "-f",
        f"owner={owner}",
        "-f",
        f"repo={repo_name}",
        "-F",
        f"number={number}",
    ]
    try:
        output = run_cmd(args)
        data = json.loads(output)
        issue_data = data.get("data", {}).get("repository", {}).get("issue") or {}
    except (json.JSONDecodeError, KeyError, AttributeError):
        return {"blocked_by": [], "blocking": []}

    return _parse_issue_dependencies(issue_data)


def fetch_issues_dependencies(
    run_cmd: Callable[[list[str]], str],
    owner: str,
    repo_name: str,
    numbers: list[int],
) -> dict[int, dict[str, Any]]:
    """Batch-fetch dependencies for multiple issues in a single GraphQL request.

    Uses one aliased field per issue number so N issues cost one round-trip
    instead of N. Returns a dict keyed by issue number, each value shaped like
    `fetch_issue_dependencies`'s return value.
    """
    if not numbers:
        return {}

    aliased_fields = "\n".join(
        f"i{n}: issue(number: {n}) {{ {_ISSUE_DEPENDENCY_FIELDS} }}" for n in numbers
    )
    query = f"""
query($owner: String!, $repo: String!) {{
  repository(owner: $owner, name: $repo) {{
    {aliased_fields}
  }}
}}
"""
    args = [
        "gh",
        "api",
        "graphql",
        "-f",
        f"query={query}",
        "-f",
        f"owner={owner}",
        "-f",
        f"repo={repo_name}",
    ]
    try:
        output = run_cmd(args)
        data = json.loads(output)
        repo_data = data.get("data", {}).get("repository") or {}
    except (json.JSONDecodeError, KeyError, AttributeError):
        return {n: {"blocked_by": [], "blocking": []} for n in numbers}

    return {
        n: _parse_issue_dependencies(repo_data.get(f"i{n}") or {}) for n in numbers
    }
