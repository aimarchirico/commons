"""Shared utility for fetching issue dependencies and attached open PRs."""

import json
from collections.abc import Callable
from typing import Any

_EMPTY_DEPS = {"blocked_by": [], "blocking": [], "has_children": False}

_BLOCKED_BY_FIELD = """
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
"""

_BLOCKING_FIELD = """
      blocking(first: 10) {
        nodes {
          number
          url
          state
          title
        }
      }
"""

_ANCESTOR_MAX_DEPTH = 2


def _ancestor_fields(depth: int) -> str:
    if depth <= 0:
        return ""
    return f"""
      parent {{
        number
        {_BLOCKED_BY_FIELD}
        {_ancestor_fields(depth - 1)}
      }}
"""


_ISSUE_FIELDS = f"""
      number
      subIssuesSummary {{
        total
      }}
      {_BLOCKED_BY_FIELD}
      {_BLOCKING_FIELD}
      {_ancestor_fields(_ANCESTOR_MAX_DEPTH)}
"""

BLOCKING_PRS_QUERY = f"""
query($owner: String!, $repo: String!, $number: Int!) {{
  repository(owner: $owner, name: $repo) {{
    issue(number: $number) {{
      {_ISSUE_FIELDS}
    }}
  }}
}}
"""


def _parse_blocked_by_nodes(
    nodes: list[dict[str, Any]],
    *,
    via_parent: bool,
) -> list[dict[str, Any]]:
    result = []
    for node in nodes:
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

        result.append(
            {
                "number": node.get("number"),
                "url": node.get("url"),
                "title": node.get("title"),
                "open_pr": open_pr,
                "via_parent": via_parent,
            },
        )
    return result


def _parse_blocking_nodes(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "number": node.get("number"),
            "url": node.get("url"),
            "title": node.get("title"),
        }
        for node in nodes
        if node.get("state") == "OPEN"
    ]


def _dedupe_by_number(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[int] = set()
    deduped = []
    for item in items:
        number = item["number"]
        if number in seen:
            continue
        seen.add(number)
        deduped.append(item)
    return deduped


def _effective_blocked_by(issue_data: dict[str, Any]) -> list[dict[str, Any]]:
    own_nodes = issue_data.get("blockedBy", {}).get("nodes", [])
    result = _parse_blocked_by_nodes(own_nodes, via_parent=False)

    node = issue_data
    while True:
        parent = node.get("parent")
        if not parent:
            break
        parent_nodes = parent.get("blockedBy", {}).get("nodes", [])
        result.extend(_parse_blocked_by_nodes(parent_nodes, via_parent=True))
        node = parent

    return _dedupe_by_number(result)


def _parse_issue_dependencies(issue_data: dict[str, Any]) -> dict[str, Any]:
    return {
        "blocked_by": _effective_blocked_by(issue_data),
        "blocking": _parse_blocking_nodes(
            issue_data.get("blocking", {}).get("nodes", []),
        ),
        "has_children": bool(
            (issue_data.get("subIssuesSummary") or {}).get("total"),
        ),
    }


def fetch_issue_dependencies(
    run_cmd: Callable[[list[str]], str],
    owner: str,
    repo_name: str,
    number: int,
) -> dict[str, Any]:
    """Fetch an issue's dependencies plus attached open PR details.

    `blocked_by` includes the issue's own blockers and, separately flagged
    via `via_parent`, every ancestor's own direct blockers (a block on a
    containing Story or Epic blocks everything beneath it). Edges between
    siblings are not folded away: they're real, direct blockers on whichever
    sibling they name.

    `blocking` is the issue's own direct outbound edges only, since a block
    on an ancestor already covers its descendants via `via_parent` above -
    no traversal needed from this side.

    Returns a dict containing:
    - blocked_by: list of open blocking issues:
        [
            {
                "number": int,
                "url": str,
                "title": str,
                "via_parent": bool,
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
    - has_children: bool, whether this issue has any open or closed sub-issues
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
        return dict(_EMPTY_DEPS)

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
        f"i{n}: issue(number: {n}) {{ {_ISSUE_FIELDS} }}" for n in numbers
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
        return {n: dict(_EMPTY_DEPS) for n in numbers}

    return {
        n: _parse_issue_dependencies(repo_data.get(f"i{n}") or {}) for n in numbers
    }
