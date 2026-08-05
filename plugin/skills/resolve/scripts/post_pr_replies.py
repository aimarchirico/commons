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
        args,
        input=input_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return result.stdout.strip()


def _check_dependencies() -> None:
    if not shutil.which("gh"):
        sys.stderr.write(
            "Error: GitHub CLI (gh) is not installed or not in PATH.\n",
        )
        sys.exit(1)


_RESOLVE_THREAD_MUTATION = """
mutation($threadId: ID!) {
  resolveReviewThread(input: {threadId: $threadId}) { thread { id } }
}
"""


def _resolve_review_threads(run_cmd: Callable[..., str], thread_ids: set[str]) -> None:
    for thread_id in sorted(thread_ids):
        sys.stdout.write(f"Resolving review thread {thread_id}...\n")
        run_cmd([
            "gh", "api", "graphql",
            "-f", f"threadId={thread_id}",
            "-f", f"query={_RESOLVE_THREAD_MUTATION}",
        ])


def render_conversation_reply(summary: str) -> str:
    """Format a conversation-level reply with resolution summary header and verdict."""
    return f"## Resolution summary\n\nResolved. {summary}"


def post_replies(
    run_cmd: Callable[..., str],
    pr_number: str,
    thread_replies: list[dict[str, Any]],
    conversation_summary: str,
) -> None:
    """Reply to each review-thread comment, resolve its thread, post the rest.

    Posts one conversation-level reply last, built from ``conversation_summary``
    via ``render_conversation_reply`` (a ``## Resolution summary`` header
    followed by the verdict ``Resolved.``; `/commons:triage` detects this by
    skipping leading blank/header lines and checking that the first
    substantive line starts with ``Resolved.``).
    """
    repo_output = run_cmd(["gh", "repo", "view", "--json", "owner,name"])
    repo_data = json.loads(repo_output)
    owner = repo_data["owner"]["login"]
    repo_name = repo_data["name"]

    thread_ids: set[str] = set()
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
        thread_ids.add(reply["thread_id"])

    _resolve_review_threads(run_cmd, thread_ids)

    if conversation_summary:
        sys.stdout.write(f"Posting conversation reply on PR #{pr_number}...\n")
        endpoint = f"repos/{owner}/{repo_name}/issues/{pr_number}/comments"
        run_cmd(
            ["gh", "api", endpoint, "--input", "-"],
            input_text=json.dumps(
                {"body": render_conversation_reply(conversation_summary)},
            ),
        )


def request_re_reviews(run_cmd: Callable[..., str], pr_number: str) -> None:
    """Request re-review from the PR's prior reviewers, excluding the user."""
    reviews_output = run_cmd(["gh", "pr", "view", pr_number, "--json", "reviews"])
    reviewers = {
        r["author"]["login"]
        for r in json.loads(reviews_output).get("reviews", [])
        if r.get("author", {}).get("login")
    }
    login = run_cmd(["gh", "api", "user", "--jq", ".login"])

    for reviewer in sorted(reviewers - {login}):
        sys.stdout.write(f"Requesting re-review from {reviewer}...\n")
        run_cmd(["gh", "pr", "edit", pr_number, "--add-reviewer", reviewer])


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
            data.get("conversation_summary", ""),
        )
        request_re_reviews(_run_cmd, pr_number)
        sys.stdout.write("Successfully posted all replies.\n")
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
        sys.stderr.write(f"Error: Failed to post replies. {e}\n")
        sys.exit(1)
    finally:
        with contextlib.suppress(OSError):
            json_file_path.unlink()


if __name__ == "__main__":
    main()
