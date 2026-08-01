#!/usr/bin/env python3
"""Script for posting a merged review as PR review comments via the GitHub API."""

import json
import os
import shutil
import subprocess
import sys


def _run_cmd(args, input_text=None):
    result = subprocess.run(
        args, input=input_text, capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def _check_dependencies():
    if not shutil.which("gh"):
        print(
            "Error: GitHub CLI (gh) is not installed or not in PATH.",
            file=sys.stderr,
        )
        sys.exit(1)


def post_review(run_cmd, pr_number, body, comments):
    """Post a single PR review with a summary body and per-line comments."""
    repo_output = run_cmd(["gh", "repo", "view", "--json", "owner,name"])
    repo_data = json.loads(repo_output)
    owner = repo_data["owner"]["login"]
    repo_name = repo_data["name"]

    payload = {"event": "COMMENT", "body": body, "comments": comments}
    run_cmd(
        [
            "gh", "api",
            f"repos/{owner}/{repo_name}/pulls/{pr_number}/reviews",
            "--input", "-",
        ],
        input_text=json.dumps(payload),
    )


def main():
    """Main entry point for posting review findings from a JSON file."""
    if len(sys.argv) < 3:
        print("Error: PR number or JSON file path not specified.", file=sys.stderr)
        print(
            f"Usage: {sys.argv[0]} <pr-number> <path-to-review.json>",
            file=sys.stderr,
        )
        sys.exit(1)

    pr_number = sys.argv[1]
    json_file = sys.argv[2]

    _check_dependencies()

    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error: Failed to parse '{json_file}' as JSON. {e}", file=sys.stderr)
        sys.exit(1)

    try:
        post_review(
            _run_cmd, pr_number, data.get("body", ""), data.get("comments", [])
        )
        print(f"Posted review to PR #{pr_number}.")
    except Exception as e:
        print(f"Error: Failed to post review. {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        try:
            os.remove(json_file)
        except Exception:
            pass


if __name__ == "__main__":
    main()
