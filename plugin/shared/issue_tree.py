"""Shared utility for recursively fetching an issue's title/body/type tree."""

import importlib.util
import json
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Any


def _load_blocking_prs() -> ModuleType:
    module_path = Path(__file__).resolve().parent / "blocking_prs.py"
    spec = importlib.util.spec_from_file_location("blocking_prs", module_path)
    if spec is None or spec.loader is None:
        msg = f"Cannot load blocking_prs from {module_path}"
        raise ImportError(msg)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_blocking_prs = _load_blocking_prs()
_ANCESTOR_MAX_DEPTH = _blocking_prs.ANCESTOR_MAX_DEPTH

_TYPE_FIELD = """
      projectItems(first: 5) {
        nodes {
          fieldValueByName(name: "Type") {
            ... on ProjectV2ItemFieldSingleSelectValue { name }
          }
        }
      }
"""


def _descendant_fields(depth: int) -> str:
    if depth <= 0:
        return ""
    return f"""
      subIssues(first: 50) {{
        nodes {{
          number
          title
          body
          {_TYPE_FIELD}
          {_descendant_fields(depth - 1)}
        }}
      }}
"""


_ISSUE_FIELDS = f"""
      number
      title
      body
      {_TYPE_FIELD}
      {_descendant_fields(_ANCESTOR_MAX_DEPTH)}
"""

ISSUE_TREE_QUERY = f"""
query($owner: String!, $repo: String!, $number: Int!) {{
  repository(owner: $owner, name: $repo) {{
    issue(number: $number) {{
      {_ISSUE_FIELDS}
    }}
  }}
}}
"""


def _extract_type(node: dict[str, Any]) -> str | None:
    nodes = node.get("projectItems", {}).get("nodes", [])
    for item in nodes:
        field_value = item.get("fieldValueByName")
        if field_value and field_value.get("name"):
            return str(field_value["name"])
    return None


def _parse_node(node: dict[str, Any]) -> dict[str, Any]:
    child_nodes = node.get("subIssues", {}).get("nodes", [])
    return {
        "number": node["number"],
        "title": node["title"],
        "body": node.get("body") or "",
        "type": _extract_type(node),
        "children": [_parse_node(child) for child in child_nodes],
    }


def fetch_issue_tree(
    run_cmd: Callable[[list[str]], str],
    owner: str,
    repo_name: str,
    number: int,
) -> dict[str, Any]:
    """Recursively fetch title/body/type for an issue and its sub-issue tree.

    Recurses into GitHub's native sub-issues, up to the same maximum nesting
    depth as the project's allowed issue type hierarchy (Epic -> Story/Task/
    Bug -> Subtask). Returns `{number, title, body, type, children: [...]}`,
    where `type` is the linked project item's Type field value (or None if
    unset), and `children` holds the same shape recursively for every direct
    sub-issue.

    Unlike `blocking_prs.fetch_issue_dependencies`, this lets exceptions
    (malformed API responses, missing fields) propagate rather than falling
    back to an empty result: a missing title or body is essential input for
    planning and assignment, so callers should fail loudly instead of
    silently planning against incomplete data.
    """
    args = [
        "gh",
        "api",
        "graphql",
        "-f",
        f"query={ISSUE_TREE_QUERY}",
        "-f",
        f"owner={owner}",
        "-f",
        f"repo={repo_name}",
        "-F",
        f"number={number}",
    ]
    output = run_cmd(args)
    data = json.loads(output)
    issue = data["data"]["repository"]["issue"]
    return _parse_node(issue)


def flatten_issue_numbers(tree: dict[str, Any]) -> list[int]:
    """Return the parent's number, then every descendant's, depth-first."""
    numbers = [tree["number"]]
    for child in tree.get("children", []):
        numbers.extend(flatten_issue_numbers(child))
    return numbers
