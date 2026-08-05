#!/usr/bin/env python3
"""Script for rendering merged findings into a PR review and posting it."""

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


def _render_comment_body(finding: dict[str, Any]) -> str:
    return (
        f"**{finding['summary']}**\n\n"
        f"{finding['failure_scenario']}\n\n"
        f"_category: {finding['category']}_"
    )


def _render_unresolvable_line(finding: dict[str, Any]) -> str:
    return (
        f"- **{finding['summary']}**: {finding['failure_scenario']} "
        f"(_category: {finding['category']}_)"
    )


def build_review(findings: list[dict[str, Any]]) -> dict[str, Any]:
    """Render merged findings into a PR review body and inline comments array.

    Findings with a resolvable ``file``/``line`` become inline comments; the
    rest are listed in the summary body. If there are any findings, the
    body leads with a ``## Review summary`` header, then the explicit
    verdict as its own line, verbatim: ``Approved.`` if ``findings`` is
    empty (with no header, since there's nothing to summarize), otherwise
    ``Requesting changes.`` (if the repo has the self-review-signal GitHub
    Action configured, it skips leading blank/header lines to find this
    verdict, then may submit a real review on the user's behalf, since the
    user can't approve or request changes on their own PR).
    """
    def _is_resolvable(finding: dict[str, Any]) -> bool:
        return bool(finding.get("file")) and finding.get("line") is not None

    resolvable = [f for f in findings if _is_resolvable(f)]
    unresolvable = [f for f in findings if not _is_resolvable(f)]

    comments = [
        {
            "path": finding["file"],
            "line": finding["line"],
            "body": _render_comment_body(finding),
        }
        for finding in resolvable
    ]

    total = len(findings)
    posted = len(comments)

    if total == 0:
        return {"body": "Approved.", "comments": []}

    summary_lines = [
        "## Review summary",
        "",
        "Requesting changes.",
        "",
        (
            f"{total} findings across logic, compliance, performance, and "
            f"security; {posted} posted as inline comments on the diff."
        ),
    ]
    if total > posted:
        summary_lines += [
            "",
            "The remainder, listed below, have no resolvable file/line:",
            "",
            *[_render_unresolvable_line(f) for f in unresolvable],
        ]

    return {"body": "\n".join(summary_lines), "comments": comments}


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
            f"Usage: {sys.argv[0]} <pr-number> <path-to-findings.json>\n",
        )
        sys.exit(1)

    pr_number = sys.argv[1]
    json_file_path = Path(sys.argv[2])

    _check_dependencies()

    try:
        with json_file_path.open(encoding="utf-8") as f:
            findings = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        sys.stderr.write(
            f"Error: Failed to parse '{json_file_path}' as JSON. {e}\n",
        )
        sys.exit(1)

    try:
        review = build_review(findings)
        post_review(_run_cmd, pr_number, review["body"], review["comments"])
        sys.stdout.write(f"Posted review to PR #{pr_number}.\n")
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
        sys.stderr.write(f"Error: Failed to post review. {e}\n")
        sys.exit(1)
    finally:
        with contextlib.suppress(OSError):
            json_file_path.unlink()


if __name__ == "__main__":
    main()
