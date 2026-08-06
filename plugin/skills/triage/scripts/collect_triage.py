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

from backlog_utils import PRIORITY_RANK, fetch_backlog_issues
from review_state import fetch_review_state

TECHNICAL_BLOCKERS = {
    "BOTH": "Conflicting and failing checks",
    "CHECKS": "Failing checks",
    "CONFLICT": "Conflicting",
    "NONE": "None",
}

REVIEW_BLOCKERS = {
    "BOTH": "Unresolved threads and comments",
    "COMMENTS": "Unresolved comments",
    "THREADS": "Unresolved threads",
    "NONE": "None",
}

REVIEW_REQUEST_STATE = {
    True: "Requested",
    False: "Not requested",
}

AWAITING_REVIEW_LABEL = {
    True: "Awaiting your review",
    False: "Not awaiting your review",
}

TECH_BLOCKER_RANK = {
    TECHNICAL_BLOCKERS["NONE"]: 0,
    TECHNICAL_BLOCKERS["CONFLICT"]: 1,
    TECHNICAL_BLOCKERS["CHECKS"]: 2,
    TECHNICAL_BLOCKERS["BOTH"]: 3,
}

REV_BLOCKER_RANK = {
    REVIEW_BLOCKERS["NONE"]: 0,
    REVIEW_BLOCKERS["THREADS"]: 1,
    REVIEW_BLOCKERS["COMMENTS"]: 2,
    REVIEW_BLOCKERS["BOTH"]: 3,
}



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


def _fetch_default_branch(run_cmd: Callable[[list[str]], str]) -> str:
    try:
        output = run_cmd(["gh", "repo", "view", "--json", "defaultBranchRef"])
        data = json.loads(output)
        return data.get("defaultBranchRef", {}).get("name", "main")
    except Exception:
        return "main"


def _fetch_prs_to_review(
    run_cmd: Callable[[list[str]], str],
    login: str,
) -> list[dict[str, Any]]:
    output = run_cmd(
        [
            "gh",
            "pr",
            "list",
            "--search",
            "is:open -author:@me draft:false",
            "--json",
            "number,title,url,author,reviewRequests,reviewDecision",
        ],
    )
    prs = json.loads(output)

    items = []
    for pr in prs:
        author = pr.get("author") or {}
        if author.get("is_bot") or pr.get("reviewDecision") == "APPROVED":
            continue
        requested_logins = {
            (r.get("login") or (r.get("requestedReviewer") or {}).get("login"))
            for r in pr.get("reviewRequests", [])
        }
        is_awaiting = login in requested_logins
        items.append(
            {
                "number": pr["number"],
                "title": pr["title"],
                "url": pr["url"],
                "state": AWAITING_REVIEW_LABEL[is_awaiting],
                "review": REVIEW_REQUEST_STATE[is_awaiting],
                "priority": "Medium",
                "blocking": "0 PRs, 0 issues",
                "suggestion": f"Review the PR with `/commons:review --pr {pr['number']}`",
            },
        )

    items.sort(
        key=lambda x: (
            0 if x["review"] == REVIEW_REQUEST_STATE[True] else 1,
            PRIORITY_RANK.get(x["priority"], 3),
        ),
    )
    return items


def _compute_technical_blockers(conflicting: bool, checks: str) -> str:
    if conflicting and checks == "failing":
        return TECHNICAL_BLOCKERS["BOTH"]
    if checks == "failing":
        return TECHNICAL_BLOCKERS["CHECKS"]
    if conflicting:
        return TECHNICAL_BLOCKERS["CONFLICT"]
    return TECHNICAL_BLOCKERS["NONE"]


def _compute_review_blockers(threads: str, comments: str) -> str:
    if threads == "unresolved" and comments == "unresolved":
        return REVIEW_BLOCKERS["BOTH"]
    if comments == "unresolved":
        return REVIEW_BLOCKERS["COMMENTS"]
    if threads == "unresolved":
        return REVIEW_BLOCKERS["THREADS"]
    return REVIEW_BLOCKERS["NONE"]



def _linked_issue_for(pr: dict[str, Any]) -> dict[str, Any] | None:
    linked_issues = pr.get("closingIssuesReferences") or []
    return (
        {"number": linked_issues[0]["number"], "url": linked_issues[0]["url"]}
        if linked_issues
        else None
    )


def _fetch_open_and_draft_prs(
    run_cmd: Callable[[list[str]], str],
    owner: str,
    repo_name: str,
    default_branch: str,
) -> dict[str, Any]:
    output = run_cmd(
        [
            "gh",
            "pr",
            "list",
            "--search",
            "is:open author:@me",
            "--json",
            "number,title,url,isDraft,closingIssuesReferences,headRefName,baseRefName",
        ],
    )
    prs = json.loads(output)

    head_to_pr_num = {pr["headRefName"]: pr["number"] for pr in prs if "headRefName" in pr}

    your_open_prs = []
    your_draft_prs = []

    merge_ready = []
    merge_blockers = []
    stacked_blockers = []
    draft_prs = []
    pending_approval = []
    stacked_queue = []

    for pr in prs:
        pr_number = pr["number"]
        linked = _linked_issue_for(pr)

        if bool(pr.get("isDraft")):
            draft_entry = {
                "number": pr_number,
                "title": pr["title"],
                "url": pr["url"],
                "priority": "Medium",
                "blocking": "0 PRs, 0 issues",
                "linked_issue": linked,
            }
            your_draft_prs.append(draft_entry)
            draft_prs.append(draft_entry)
            continue

        review_state = fetch_review_state(
            lambda query, **variables: _graphql(run_cmd, query, **variables),
            owner,
            repo_name,
            pr_number,
        )

        tech_blockers = _compute_technical_blockers(
            review_state["conflicting"],
            review_state["checks"],
        )
        rev_blockers = _compute_review_blockers(
            review_state["threads"],
            review_state["comments"],
        )

        base_branch = pr.get("baseRefName", default_branch)
        is_default_target = base_branch == default_branch
        stacked_on_num = head_to_pr_num.get(base_branch)

        has_blockers = (tech_blockers != "None") or (rev_blockers != "None")
        is_approved = review_state["state"] == "approved"

        priority = "Medium"
        blocking = "0 PRs, 0 issues"

        base_entry = {
            "number": pr_number,
            "title": pr["title"],
            "url": pr["url"],
            "priority": priority,
            "blocking": blocking,
            "technical_blockers": tech_blockers,
            "review_blockers": rev_blockers,
            "state": review_state["state"].capitalize(),
            "threads": review_state["threads"].capitalize(),
            "comments": review_state["comments"].capitalize(),
            "conflicting": "Yes" if review_state["conflicting"] else "No",
            "checks": review_state["checks"].capitalize(),
        }

        if has_blockers:
            base_entry["suggestion"] = f"Resolve problems with `/commons:resolve --pr {pr_number}`"
            merge_blockers.append(base_entry)
        elif is_default_target:
            if is_approved:
                base_entry["suggestion"] = "Merge the PR"
                merge_ready.append(base_entry)
            else:
                base_entry["suggestion"] = f"Self-review the PR with `/commons:review --pr {pr_number}`"
                pending_approval.append(base_entry)
        else:
            base_entry["stacked_on"] = f"PR #{stacked_on_num}" if stacked_on_num else base_branch
            base_entry["suggestion"] = f"Self-review the PR with `/commons:review --pr {pr_number}`"
            stacked_queue.append(base_entry)

        your_open_prs.append(base_entry)

    def sort_blockers(item: dict[str, Any]) -> tuple[int, int, int]:
        t_rank = TECH_BLOCKER_RANK.get(item["technical_blockers"], 3)
        r_rank = REV_BLOCKER_RANK.get(item["review_blockers"], 3)
        p_rank = PRIORITY_RANK.get(item["priority"], 3)
        return (t_rank, r_rank, p_rank)

    def sort_std(item: dict[str, Any]) -> int:
        return PRIORITY_RANK.get(item["priority"], 3)

    merge_ready.sort(key=sort_std)
    merge_blockers.sort(key=sort_blockers)
    draft_prs.sort(key=sort_std)
    pending_approval.sort(key=sort_std)
    stacked_queue.sort(key=sort_std)

    return {
        "your_open_prs": your_open_prs,
        "your_draft_prs": your_draft_prs,
        "merge_ready": merge_ready,
        "merge_blockers": merge_blockers,
        "draft_prs": draft_prs,
        "pending_approval": pending_approval,
        "stacked_queue": stacked_queue,
    }


def main() -> None:
    """Main entry point for printing the triage survey as JSON."""
    preflight = run_project_preflight(_run_cmd, require_fields=False)
    owner = preflight["owner"]
    repo_name = preflight["repo_name"]
    project_number = preflight["project_number"]
    project_owner = preflight["project_owner"]

    try:
        login = _resolve_login(_run_cmd)
        default_branch = _fetch_default_branch(_run_cmd)

        pr_data = _fetch_open_and_draft_prs(
            _run_cmd,
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
        prs_to_review = _fetch_prs_to_review(_run_cmd, login)

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

