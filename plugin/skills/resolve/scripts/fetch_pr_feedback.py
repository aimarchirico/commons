#!/usr/bin/env python3
"""Script for fetching a pull request's conversation and review-thread feedback."""

import json
import shutil
import subprocess
import sys


def _run_cmd(args):
    result = subprocess.run(args, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def _check_dependencies():
    if not shutil.which("gh"):
        print(
            "Error: GitHub CLI (gh) is not installed or not in PATH.",
            file=sys.stderr,
        )
        sys.exit(1)


def fetch_pr_feedback(run_cmd, pr_number):
    """Fetch a PR's conversation comments and its unresolved review threads."""
    repo_output = run_cmd(["gh", "repo", "view", "--json", "owner,name"])
    repo_data = json.loads(repo_output)
    owner = repo_data["owner"]["login"]
    repo_name = repo_data["name"]

    query = """
    query($owner: String!, $repo: String!, $number: Int!) {
      repository(owner: $owner, name: $repo) {
        pullRequest(number: $number) {
          comments(first: 100) {
            nodes { databaseId body author { login } }
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

    conversation_comments = [
        {
            "id": node["databaseId"],
            "body": node["body"],
            "author": (node.get("author") or {}).get("login"),
        }
        for node in pr.get("comments", {}).get("nodes", [])
    ]

    review_threads = []
    for thread in pr.get("reviewThreads", {}).get("nodes", []):
        if thread.get("isResolved"):
            continue
        review_threads.append({
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
        })

    return {
        "conversation_comments": conversation_comments,
        "review_threads": review_threads,
    }


def main():
    """Main entry point for printing a PR's feedback as JSON."""
    if len(sys.argv) < 2:
        print("Error: PR number not specified.", file=sys.stderr)
        print(f"Usage: {sys.argv[0]} <pr-number>", file=sys.stderr)
        sys.exit(1)

    pr_number = sys.argv[1]

    _check_dependencies()

    try:
        feedback = fetch_pr_feedback(_run_cmd, pr_number)
    except Exception as e:
        print(f"Error: Failed to fetch PR feedback. {e}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(feedback, indent=2))


if __name__ == "__main__":
    main()
