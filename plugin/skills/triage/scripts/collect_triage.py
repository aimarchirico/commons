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

from backlog_utils import fetch_backlog_issues
from pr_utils import fetch_default_branch, fetch_open_and_draft_prs, fetch_prs_to_review


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


def _format_blocking(pr_count: int, issue_count: int) -> str:
    """Format a 'blocking' string, omitting zero parts; 'None' if both zero."""
    parts = []
    if pr_count:
        parts.append(f"{pr_count} PR{'s' if pr_count != 1 else ''}")
    if issue_count:
        parts.append(f"{issue_count} issue{'s' if issue_count != 1 else ''}")
    return ", ".join(parts) if parts else "None"


def _compute_pr_blocking(
    pr_entries: list[dict[str, Any]],
    backlog_issues: list[dict[str, Any]],
) -> None:
    """Populate the 'blocking' field on each PR entry in-place.

    For a PR that closes issues C1, C2, ...:
    - downstream_issues = union of open issues blocked by any Ci
    - blocking_prs      = other open PRs (from pr_entries) that close any
                          issue in downstream_issues
    - final issue count = downstream_issues NOT already closed by a blocking PR

    Sets blocking to "None" if both counts are zero.
    """
    # issue_number -> list of downstream blocking issue dicts
    issue_to_downstream: dict[int, list[dict[str, Any]]] = {}
    for issue in backlog_issues:
        num = issue.get("number")
        if num is not None:
            issue_to_downstream[num] = issue.get("_blocking_items", [])

    # issue_number -> list of PR numbers (from your open PRs) that close it
    issue_to_closing_prs: dict[int, list[int]] = {}
    for pr in pr_entries:
        for ci in pr.get("_closing_issues", []):
            ci_num = ci["number"]
            issue_to_closing_prs.setdefault(ci_num, []).append(pr["number"])

    for pr in pr_entries:
        closing_nums = {ci["number"] for ci in pr.get("_closing_issues", [])}
        if not closing_nums:
            pr["blocking"] = "None"
            continue

        # All downstream issues blocked by any of this PR's closing issues
        downstream: dict[int, dict[str, Any]] = {}
        for cnum in closing_nums:
            for ds in issue_to_downstream.get(cnum, []):
                ds_num = ds.get("number")
                if ds_num is not None:
                    downstream[ds_num] = ds

        # Other PRs that close any downstream issue
        blocking_pr_nums: set[int] = set()
        for ds_num in downstream:
            for other_pr in issue_to_closing_prs.get(ds_num, []):
                if other_pr != pr["number"]:
                    blocking_pr_nums.add(other_pr)

        # Issues already covered by a blocking PR don't count toward issue total
        covered_by_pr: set[int] = set()
        for bpr_num in blocking_pr_nums:
            for bpr in pr_entries:
                if bpr["number"] == bpr_num:
                    for ci in bpr.get("_closing_issues", []):
                        covered_by_pr.add(ci["number"])

        uncovered_issues = sum(
            1 for ds_num in downstream if ds_num not in covered_by_pr
        )

        pr["blocking"] = _format_blocking(len(blocking_pr_nums), uncovered_issues)


def main() -> None:
    """Main entry point for printing the triage survey as JSON."""
    preflight = run_project_preflight(_run_cmd, require_fields=False)
    owner = preflight["owner"]
    repo_name = preflight["repo_name"]
    project_number = preflight["project_number"]
    project_owner = preflight["project_owner"]

    try:
        login = _resolve_login(_run_cmd)
        default_branch = fetch_default_branch(_run_cmd)

        pr_data = fetch_open_and_draft_prs(
            _run_cmd,
            lambda query, **variables: _graphql(_run_cmd, query, **variables),
            owner,
            repo_name,
            default_branch,
        )
        backlog_data = fetch_backlog_issues(
            _run_cmd,
            (owner, repo_name),
            project_owner,
            project_number,
            login,
        )
        prs_to_review = fetch_prs_to_review(_run_cmd, login)

        # Compute accurate blocking counts for all your PRs using backlog deps
        all_your_prs = pr_data["your_open_prs"] + pr_data["your_draft_prs"]
        _compute_pr_blocking(all_your_prs, backlog_data["backlog_issues"])

        categories = {
            "action_required": {
                "review_requests": prs_to_review,
                "merge_ready": pr_data["merge_ready"],
                "merge_blockers": pr_data["merge_blockers"],
                "draft_prs": pr_data["draft_prs"],
                "assigned_ready": backlog_data["assigned_ready"],
                "assigned_stackable": backlog_data["assigned_stackable"],
            },
            "waiting": {
                "pending_approval": pr_data["pending_approval"],
                "stacked_queue": pr_data["stacked_queue"],
            },
            "unassigned": {
                "available_ready": backlog_data["available_ready"],
                "available_stackable": backlog_data["available_stackable"],
            },
        }

        result = {
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
