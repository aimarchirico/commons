#!/usr/bin/env python3
"""Script for posting a merged review as PR review comments via the GitHub API."""

import contextlib
import json
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

MIN_ARG_COUNT = 3


def _run_cmd(args: list[str], input_text: str | None = None) -> str:
    result = subprocess.run(
        args, input=input_text, capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def _check_dependencies() -> None:
    if not shutil.which("gh"):
        sys.stderr.write(
            "Error: GitHub CLI (gh) is not installed or not in PATH.\n",
        )
        sys.exit(1)


def post_review(
    run_cmd: Callable[..., str],
    pr_number: str,
    body: str,
    comments: list[dict[str, Any]],
) -> None:
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


def main() -> None:
    """Main entry point for posting review findings from a JSON file."""
    if len(sys.argv) < MIN_ARG_COUNT:
        sys.stderr.write(
            "Error: PR number or JSON file path not specified.\n",
        )
        sys.stderr.write(
            f"Usage: {sys.argv[0]} <pr-number> <path-to-review.json>\n",
        )
        sys.exit(1)

    pr_number = sys.argv[1]
    json_file_path = Path(sys.argv[2])

    _check_dependencies()

    try:
        with json_file_path.open(encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        sys.stderr.write(
            f"Error: Failed to parse '{json_file_path}' as JSON. {e}\n",
        )
        sys.exit(1)

    try:
        post_review(
            _run_cmd, pr_number, data.get("body", ""), data.get("comments", []),
        )
        sys.stdout.write(f"Posted review to PR #{pr_number}.\n")
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
        sys.stderr.write(f"Error: Failed to post review. {e}\n")
        sys.exit(1)
    finally:
        with contextlib.suppress(OSError):
            json_file_path.unlink()


if __name__ == "__main__":
    main()
