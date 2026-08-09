#!/usr/bin/env python3
"""Script for surveying open PRs and backlog issues relevant to the user."""

import importlib.util
import json
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Any

from backlog_utils import fetch_backlog_issues, fetch_in_progress_issues
from pr_blocking import apply_pr_blocking
from pr_utils import (
    fetch_all_open_prs,
    fetch_open_and_draft_prs,
    fetch_prs_to_review,
)


def _load_project_preflight() -> ModuleType:
    shared_dir = Path(__file__).resolve().parent.parent.parent.parent / "shared"
    module_path = shared_dir / "project_preflight.py"
    spec = importlib.util.spec_from_file_location("project_preflight", module_path)
    if spec is None or spec.loader is None:
        msg = f"Cannot load project_preflight from {module_path}"
        raise ImportError(msg)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


project_preflight = _load_project_preflight()
run_project_preflight = project_preflight.run_project_preflight


def _run_cmd(args: list[str]) -> str:
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return result.stdout.strip()


def _graphql(
    run_cmd: Callable[[list[str]], str],
    query: str,
    **variables: str | int,
) -> dict[str, Any]:
    args = ["gh", "api", "graphql"]
    for key, value in variables.items():
        args += ["-F" if isinstance(value, int) else "-f", f"{key}={value}"]
    args += ["-f", f"query={query}"]
    return dict(json.loads(run_cmd(args)))


def _resolve_login(run_cmd: Callable[[list[str]], str]) -> str:
    return run_cmd(["gh", "api", "user", "--jq", ".login"])


def main() -> None:
    """Main entry point for printing the triage survey as JSON."""
    preflight = run_project_preflight(_run_cmd, require_fields=False)
    owner = preflight["owner"]
    repo_name = preflight["repo_name"]
    project_number = preflight["project_number"]
    project_owner = preflight["project_owner"]
    default_branch = preflight["default_branch"]

    try:
        login = _resolve_login(_run_cmd)
        all_open_prs = fetch_all_open_prs(_run_cmd)

        pr_data = fetch_open_and_draft_prs(
            all_open_prs,
            lambda query, **variables: _graphql(_run_cmd, query, **variables),
            (owner, repo_name),
            default_branch,
            login,
        )
        backlog_data = fetch_backlog_issues(
            _run_cmd,
            (owner, repo_name),
            project_owner,
            project_number,
            login,
        )
        prs_to_review = fetch_prs_to_review(all_open_prs, login)

        all_your_prs = pr_data["your_open_prs"] + pr_data["your_draft_prs"]
        apply_pr_blocking(all_your_prs, backlog_data["backlog_issues"])

        linked_issue_numbers = {
            closing["number"]
            for pr in all_your_prs
            for closing in pr.get("_closing_issues", [])
        }
        in_progress_issues = [
            issue
            for issue in fetch_in_progress_issues(
                _run_cmd,
                (owner, repo_name),
                project_owner,
                project_number,
            )
            if issue["number"] not in linked_issue_numbers
        ]

        categories = {
            "actionable_items": {
                "review_requests": prs_to_review,
                "merge_ready": pr_data["merge_ready"],
                "merge_blockers": pr_data["merge_blockers"],
                "draft_prs": pr_data["draft_prs"],
                "in_progress": in_progress_issues,
                "assigned_ready": backlog_data["assigned_ready"],
                "assigned_stackable": backlog_data["assigned_stackable"],
            },
            "pending_prs": {
                "pending_approval": pr_data["pending_approval"],
                "stacked_queue": pr_data["stacked_queue"],
            },
            "unassigned_issues": {
                "available_ready": backlog_data["available_ready"],
                "available_stackable": backlog_data["available_stackable"],
            },
        }

        active_count = sum(
            len(items) for category in categories.values() for items in category.values()
        )

        result = {
            "active_count": active_count,
            "categories": categories,
            "prs_to_review": prs_to_review,
            "your_open_prs": pr_data["your_open_prs"],
            "your_draft_prs": pr_data["your_draft_prs"],
            "backlog_issues": backlog_data["backlog_issues"],
            "assigned_to_others_count": backlog_data["assigned_to_others_count"],
            "fully_blocked_count": backlog_data["fully_blocked_count"],
        }
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
        sys.stderr.write(f"Error: Failed to collect triage data. {e}\n")
        sys.exit(1)

    sys.stdout.write(f"{json.dumps(result, indent=2)}\n")


if __name__ == "__main__":
    main()
