#!/usr/bin/env python3
"""Script for posting resolving replies to a pull request's feedback."""

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


def post_replies(run_cmd, pr_number, thread_replies, conversation_reply):
    """Post a reply to each review-thread comment, then one conversation reply."""
    repo_output = run_cmd(["gh", "repo", "view", "--json", "owner,name"])
    repo_data = json.loads(repo_output)
    owner = repo_data["owner"]["login"]
    repo_name = repo_data["name"]

    for reply in thread_replies:
        comment_id = reply["comment_id"]
        print(f"Replying to review comment {comment_id}...")
        run_cmd(
            [
                "gh", "api",
                f"repos/{owner}/{repo_name}/pulls/{pr_number}/comments/"
                f"{comment_id}/replies",
                "--input", "-",
            ],
            input_text=json.dumps({"body": reply["body"]}),
        )

    if conversation_reply:
        print(f"Posting conversation reply on PR #{pr_number}...")
        run_cmd(
            [
                "gh", "api",
                f"repos/{owner}/{repo_name}/issues/{pr_number}/comments",
                "--input", "-",
            ],
            input_text=json.dumps({"body": conversation_reply}),
        )


def main():
    """Main entry point for posting resolving replies from a JSON file."""
    if len(sys.argv) < 3:
        print("Error: PR number or JSON file path not specified.", file=sys.stderr)
        print(
            f"Usage: {sys.argv[0]} <pr-number> <path-to-replies.json>",
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
        post_replies(
            _run_cmd,
            pr_number,
            data.get("thread_replies", []),
            data.get("conversation_reply", ""),
        )
        print("Successfully posted all replies.")
    except Exception as e:
        print(f"Error: Failed to post replies. {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        try:
            os.remove(json_file)
        except Exception:
            pass


if __name__ == "__main__":
    main()
