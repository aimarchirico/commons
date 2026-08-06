#!/usr/bin/env python3
"""Script for resolving issue target base branch from GitHub blockedBy."""

import json
import shutil
import subprocess
import sys
from collections.abc import Callable
from typing import Any

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


def get_issue_base_branch(
    run_cmd: Callable[[list[str]], str], issue_id: str,
) -> dict[str, Any]:
    """Determine base branch candidates for a given issue ID.

    Returns a dict containing:
    - default_branch: str
    - status: "default" | "single" | "multiple"
    - base_branch: str | None
    - candidates: list of candidate PR dicts
    """
    repo_output = run_cmd(
        ["gh", "repo", "view", "--json", "owner,name,defaultBranchRef"],
    )
    repo_data = json.loads(repo_output)
    owner = repo_data["owner"]["login"]
    repo_name = repo_data["name"]
    default_branch = (
        repo_data.get("defaultBranchRef", {}).get("name") or "main"
    )

    query = """
    query($owner: String!, $repo: String!, $number: Int!) {
      repository(owner: $owner, name: $repo) {
        issue(number: $number) {
          blockedBy(first: 10) {
            nodes {
              number
              state
              title
              timelineItems(
                first: 20
                itemTypes: [CONNECTED_EVENT, CROSS_REFERENCED_EVENT]
              ) {
                nodes {
                  ... on ConnectedEvent {
                    subject {
                      ... on PullRequest {
                        number
                        title
                        headRefName
                        state
                        isDraft
                      }
                    }
                  }
                  ... on CrossReferencedEvent {
                    source {
                      ... on PullRequest {
                        number
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
        }
      }
    }
    """

    try:
        api_output = run_cmd([
            "gh", "api", "graphql",
            "-f", f"query={query}",
            "-f", f"owner={owner}",
            "-f", f"repo={repo_name}",
            "-F", f"number={issue_id}",
        ])
        api_data = json.loads(api_output)
        issue_data = (
            api_data.get("data", {}).get("repository", {}).get("issue") or {}
        )
        blocked_by_nodes = issue_data.get("blockedBy", {}).get("nodes", [])
    except (
        subprocess.CalledProcessError,
        json.JSONDecodeError,
        KeyError,
        AttributeError,
    ):
        return {
            "default_branch": default_branch,
            "status": "default",
            "base_branch": default_branch,
            "candidates": [],
        }

    open_pr_candidates = []
    seen_branches = set()

    for blocking_node in blocked_by_nodes:
        blocking_number = blocking_node.get("number")
        timeline = blocking_node.get("timelineItems", {}).get("nodes", [])

        for item in timeline:
            pr = item.get("subject") or item.get("source")
            if not isinstance(pr, dict):
                continue

            pr_state = pr.get("state")
            branch_name = pr.get("headRefName")

            if pr_state == "OPEN" and branch_name and branch_name not in seen_branches:
                seen_branches.add(branch_name)
                open_pr_candidates.append({
                    "issue_number": blocking_number,
                    "pr_number": pr.get("number"),
                    "pr_title": pr.get("title"),
                    "branch_name": branch_name,
                    "is_draft": pr.get("isDraft", False),
                })

    if not open_pr_candidates:
        return {
            "default_branch": default_branch,
            "status": "default",
            "base_branch": default_branch,
            "candidates": [],
        }
    if len(open_pr_candidates) == 1:
        return {
            "default_branch": default_branch,
            "status": "single",
            "base_branch": open_pr_candidates[0]["branch_name"],
            "candidates": open_pr_candidates,
        }

    return {
        "default_branch": default_branch,
        "status": "multiple",
        "base_branch": None,
        "candidates": open_pr_candidates,
    }


def main() -> None:
    """Main entry point for resolving an issue's base branch from the CLI."""
    if len(sys.argv) < MIN_ARG_COUNT:
        sys.stderr.write("Error: Issue ID not specified.\n")
        sys.stderr.write(f"Usage: {sys.argv[0]} <issue-id> [--json]\n")
        sys.exit(1)

    issue_id = sys.argv[1]
    output_json = "--json" in sys.argv

    _check_dependencies()

    try:
        res = get_issue_base_branch(_run_cmd, issue_id)
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
        sys.stderr.write(f"Error: Failed to fetch base branch info. {e}\n")
        sys.exit(1)

    if output_json or res["status"] == "multiple":
        sys.stdout.write(f"{json.dumps(res, indent=2)}\n")
    else:
        sys.stdout.write(f"{res['base_branch']}\n")


if __name__ == "__main__":
    main()
