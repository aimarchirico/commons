#!/usr/bin/env python3
"""Script for posting resolving replies to a pull request's feedback."""

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


def post_replies(
    run_cmd: Callable[..., str],
    pr_number: str,
    thread_replies: list[dict[str, Any]],
    conversation_reply: str,
) -> None:
    """Post a reply to each review-thread comment, then one conversation reply."""
    repo_output = run_cmd(["gh", "repo", "view", "--json", "owner,name"])
    repo_data = json.loads(repo_output)
    owner = repo_data["owner"]["login"]
    repo_name = repo_data["name"]

    for reply in thread_replies:
        comment_id = reply["comment_id"]
        sys.stdout.write(f"Replying to review comment {comment_id}...\n")
        endpoint = (
            f"repos/{owner}/{repo_name}/pulls/{pr_number}/comments/"
            f"{comment_id}/replies"
        )
        run_cmd(
            ["gh", "api", endpoint, "--input", "-"],
            input_text=json.dumps({"body": reply["body"]}),
        )

    if conversation_reply:
        sys.stdout.write(f"Posting conversation reply on PR #{pr_number}...\n")
        endpoint = f"repos/{owner}/{repo_name}/issues/{pr_number}/comments"
        run_cmd(
            ["gh", "api", endpoint, "--input", "-"],
            input_text=json.dumps({"body": conversation_reply}),
        )


def main() -> None:
    """Main entry point for posting resolving replies from a JSON file."""
    if len(sys.argv) < MIN_ARG_COUNT:
        sys.stderr.write(
            "Error: PR number or JSON file path not specified.\n",
        )
        sys.stderr.write(
            f"Usage: {sys.argv[0]} <pr-number> <path-to-replies.json>\n",
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
        post_replies(
            _run_cmd,
            pr_number,
            data.get("thread_replies", []),
            data.get("conversation_reply", ""),
        )
        sys.stdout.write("Successfully posted all replies.\n")
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
        sys.stderr.write(f"Error: Failed to post replies. {e}\n")
        sys.exit(1)
    finally:
        with contextlib.suppress(OSError):
            json_file_path.unlink()


if __name__ == "__main__":
    main()
