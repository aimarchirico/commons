#!/usr/bin/env python3
"""Script for fetching a pull request's open review feedback."""

import importlib.util
import json
import shutil
import subprocess
import sys
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

MIN_ARG_COUNT = 2


def _run_cmd(args: list[str]) -> str:
    result = subprocess.run(args, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def _check_dependencies() -> None:
    if not shutil.which("gh"):
        sys.stderr.write(
            "Error: GitHub CLI (gh) is not installed or not in PATH.\n",
        )
        sys.exit(1)


def fetch_review_feedback(
    run_cmd: Callable[[list[str]], str], pr_number: str,
) -> dict[str, Any]:
    """Fetch a PR's open feedback: unresolved threads and comments.

    "Open" means unresolved threads and comments since the last
    ``Resolved.`` checkpoint; see ``pr_feedback.py``.
    """
    repo_output = run_cmd(["gh", "repo", "view", "--json", "owner,name"])
    repo_data = json.loads(repo_output)
    owner = repo_data["owner"]["login"]
    repo_name = repo_data["name"]

    query = """
    query($owner: String!, $repo: String!, $number: Int!) {
      repository(owner: $owner, name: $repo) {
        pullRequest(number: $number) {
          comments(first: 100) {
            nodes { databaseId body author { login } createdAt }
          }
          reviews(first: 100) {
            nodes { databaseId body author { login } createdAt }
          }
          reviewThreads(first: 100) {
            nodes {
              id
              isResolved
              path
              line
              comments(first: 50) {
                nodes { databaseId body author { login } }
              }
            }
          }
        }
      }
    }
    """
    api_output = run_cmd([
        "gh", "api", "graphql",
        "-f", f"owner={owner}",
        "-f", f"repo={repo_name}",
        "-F", f"number={pr_number}",
        "-f", f"query={query}",
    ])
    api_data = json.loads(api_output)
    pr = api_data.get("data", {}).get("repository", {}).get("pullRequest") or {}

    all_comments = [
        {
            "id": node["databaseId"],
            "body": node["body"],
            "author": (node.get("author") or {}).get("login"),
            "createdAt": node["createdAt"],
        }
        for node in pr.get("comments", {}).get("nodes", [])
    ]
    all_comments.extend(
        {
            "id": node["databaseId"],
            "body": node["body"],
            "author": (node.get("author") or {}).get("login"),
            "createdAt": node["createdAt"],
        }
        for node in pr.get("reviews", {}).get("nodes", [])
        if node.get("body")
    )
    open_comments = [
        {"id": c["id"], "body": c["body"], "author": c["author"]}
        for c in comments_since_checkpoint(all_comments)
    ]

    open_threads = [
        {
            "thread_id": thread["id"],
            "path": thread.get("path"),
            "line": thread.get("line"),
            "comments": [
                {
                    "id": c["databaseId"],
                    "body": c["body"],
                    "author": (c.get("author") or {}).get("login"),
                }
                for c in thread.get("comments", {}).get("nodes", [])
            ],
        }
        for thread in unresolved_threads(pr.get("reviewThreads", {}).get("nodes", []))
    ]

    return {"threads": open_threads, "comments": open_comments}


def main() -> None:
    """Main entry point for printing a PR's open feedback as JSON."""
    if len(sys.argv) < MIN_ARG_COUNT:
        sys.stderr.write("Error: PR number not specified.\n")
        sys.stderr.write(f"Usage: {sys.argv[0]} <pr-number>\n")
        sys.exit(1)

    pr_number = sys.argv[1]

    _check_dependencies()

    try:
        feedback = fetch_review_feedback(_run_cmd, pr_number)
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
        sys.stderr.write(f"Error: Failed to fetch PR feedback. {e}\n")
        sys.exit(1)

    sys.stdout.write(f"{json.dumps(feedback, indent=2)}\n")


if __name__ == "__main__":
    main()
