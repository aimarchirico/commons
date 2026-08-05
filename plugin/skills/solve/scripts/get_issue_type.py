#!/usr/bin/env python3
"""Script for fetching a GitHub issue's linked project Type field value."""

import json
import shutil
import subprocess
import sys
from collections.abc import Callable

MIN_ARG_COUNT = 2


def _run_cmd(args: list[str]) -> str:
    result = subprocess.run(
        args, capture_output=True, text=True, encoding="utf-8", check=True,
    )
    return result.stdout.strip()


def _check_dependencies() -> None:
    if not shutil.which("gh"):
        sys.stderr.write(
            "Error: GitHub CLI (gh) is not installed or not in PATH.\n",
        )
        sys.exit(1)


def get_issue_type(
    run_cmd: Callable[[list[str]], str], issue_id: str,
) -> str | None:
    """Fetch the Type field value of an issue's linked project item, if any."""
    repo_output = run_cmd(["gh", "repo", "view", "--json", "owner,name"])
    repo_data = json.loads(repo_output)
    owner = repo_data["owner"]["login"]
    repo_name = repo_data["name"]

    query = """
    query($owner: String!, $repo: String!, $number: Int!) {
      repository(owner: $owner, name: $repo) {
        issue(number: $number) {
          projectItems(first: 5) {
            nodes {
              fieldValueByName(name: "Type") {
                ... on ProjectV2ItemFieldSingleSelectValue { name }
              }
            }
          }
        }
      }
    }
    """
    api_output = run_cmd([
        "gh", "api", "graphql",
        "-f", f"query={query}",
        "-f", f"owner={owner}",
        "-f", f"repo={repo_name}",
        "-F", f"number={issue_id}",
    ])
    api_data = json.loads(api_output)
    issue = api_data.get("data", {}).get("repository", {}).get("issue") or {}
    nodes = issue.get("projectItems", {}).get("nodes", [])

    for node in nodes:
        field_value = node.get("fieldValueByName")
        if field_value and field_value.get("name"):
            return field_value["name"]

    return None


def main() -> None:
    """Main entry point for resolving an issue's Type field from the CLI."""
    if len(sys.argv) < MIN_ARG_COUNT:
        sys.stderr.write("Error: Issue ID not specified.\n")
        sys.stderr.write(f"Usage: {sys.argv[0]} <issue-id>\n")
        sys.exit(1)

    issue_id = sys.argv[1]

    _check_dependencies()

    try:
        issue_type = get_issue_type(_run_cmd, issue_id)
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
        sys.stderr.write(f"Error: Failed to fetch issue type. {e}\n")
        sys.exit(1)

    if issue_type:
        sys.stdout.write(f"{issue_type}\n")
    else:
        sys.stderr.write(
            f"Warning: Issue #{issue_id} has no linked project item with a "
            "Type field.\n",
        )


if __name__ == "__main__":
    main()
