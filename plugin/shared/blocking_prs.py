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

# A Story/Task/Bug's own subIssues are always Subtasks (the hierarchy's
# fixed 3 tiers per CONTRIBUTING.md), which never have children of their
# own, so two levels of nesting (Epic -> Story/Task/Bug -> Subtask) is
# always enough to cover the whole subtree.
_MAX_SUBTREE_DEPTH = 2


def _dependency_tree_fields(depth: int) -> str:
    """Build a GraphQL field selection nesting `subIssues` `depth` levels deep.

    Each level requests `number` plus the issue's own blockedBy/blocking
    edges, so the response carries enough data to fold descendant edges
    into the root while still being able to tell which edges point back
    within the same subtree.
    """
    fields = f"""
      number
      {_ISSUE_DEPENDENCY_FIELDS}
"""
    if depth > 0:
        fields += f"""
      subIssues(first: 50) {{
        nodes {{
          {_dependency_tree_fields(depth - 1)}
        }}
      }}
"""
    return fields


_ISSUE_DEPENDENCY_TREE_FIELDS = _dependency_tree_fields(_MAX_SUBTREE_DEPTH)

BLOCKING_PRS_QUERY = f"""
query($owner: String!, $repo: String!, $number: Int!) {{
  repository(owner: $owner, name: $repo) {{
    issue(number: $number) {{
      {_ISSUE_DEPENDENCY_TREE_FIELDS}
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


def _collect_subtree_numbers(issue_data: dict[str, Any]) -> set[int]:
    """Collect an issue's own number plus every descendant Subtask's number."""
    numbers = set()
    number = issue_data.get("number")
    if number is not None:
        numbers.add(number)
    for child in issue_data.get("subIssues", {}).get("nodes", []) or []:
        numbers |= _collect_subtree_numbers(child)
    return numbers


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


def _fold_issue_dependencies(issue_data: dict[str, Any]) -> dict[str, Any]:
    """Merge blocked_by/blocking across an issue and its whole subIssues tree.

    A PR is scoped to a whole Story/Task/Bug including all its Subtasks, so
    the issue is genuinely blocked/blocking whenever any descendant Subtask
    is. Edges that point at another issue within the same subtree (e.g. one
    sibling Subtask ordered before another) are purely internal
    implementation-order notes for that single PR's scope, not real external
    blockers, and are excluded from the result.
    """
    subtree_numbers = _collect_subtree_numbers(issue_data)

    def walk(node: dict[str, Any]) -> dict[str, Any]:
        parsed = _parse_issue_dependencies(node)
        blocked_by = [
            b for b in parsed["blocked_by"] if b["number"] not in subtree_numbers
        ]
        blocking = [
            b for b in parsed["blocking"] if b["number"] not in subtree_numbers
        ]
        for child in node.get("subIssues", {}).get("nodes", []) or []:
            child_result = walk(child)
            blocked_by.extend(child_result["blocked_by"])
            blocking.extend(child_result["blocking"])
        return {"blocked_by": blocked_by, "blocking": blocking}

    result = walk(issue_data)
    return {
        "blocked_by": _dedupe_by_number(result["blocked_by"]),
        "blocking": _dedupe_by_number(result["blocking"]),
    }


def fetch_issue_dependencies(
    run_cmd: Callable[[list[str]], str],
    owner: str,
    repo_name: str,
    number: int,
) -> dict[str, Any]:
    """Fetch issue blockedBy and blocking relationships with attached open PR details.

    Blocked/blocking checks are transitive across the issue's whole subtree
    of Subtasks (and, for Epics, their Story/Task/Bug children in turn): a
    blocker on any descendant Subtask surfaces here as if it blocked the
    root issue directly, since a PR is scoped to the whole subtree. Edges
    between two descendants of the same subtree are internal implementation
    ordering and are not included.

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

    return _fold_issue_dependencies(issue_data)


def fetch_issues_dependencies(
    run_cmd: Callable[[list[str]], str],
    owner: str,
    repo_name: str,
    numbers: list[int],
) -> dict[int, dict[str, Any]]:
    """Batch-fetch dependencies for multiple issues in a single GraphQL request.

    Uses one aliased field per issue number so N issues cost one round-trip
    instead of N. Returns a dict keyed by issue number, each value shaped like
    `fetch_issue_dependencies`'s return value (transitive across each
    issue's subtree of Subtasks).
    """
    if not numbers:
        return {}

    aliased_fields = "\n".join(
        f"i{n}: issue(number: {n}) {{ {_ISSUE_DEPENDENCY_TREE_FIELDS} }}"
        for n in numbers
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
        n: _fold_issue_dependencies(repo_data.get(f"i{n}") or {}) for n in numbers
    }
