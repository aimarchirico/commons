"""Shared utility for fetching issue dependencies and attached open PRs."""

import json
from collections.abc import Callable
from typing import Any

BLOCKING_PRS_QUERY = """
query($owner: String!, $repo: String!, $number: Int!) {
  repository(owner: $owner, name: $repo) {
    issue(number: $number) {
      blockedBy(first: 10) {
        nodes {
          number
          url
          state
          title
          timelineItems(
            first: 20
            itemTypes: [CONNECTED_EVENT]
          ) {
            nodes {
              ... on ConnectedEvent {
                subject {
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
    }
  }
}
"""


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

    blocked_by_nodes = issue_data.get("blockedBy", {}).get("nodes", [])
    blocking_nodes = issue_data.get("blocking", {}).get("nodes", [])

    blocked_by_list = []
    for node in blocked_by_nodes:
        if node.get("state") != "OPEN":
            continue

        open_pr = None
        timeline = node.get("timelineItems", {}).get("nodes", [])
        for item in timeline:
            pr = item.get("subject")
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
