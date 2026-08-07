#!/usr/bin/env python3
"""Helper for fetching, classifying, and sorting pull requests for triage."""

import json
import subprocess
from collections.abc import Callable
from typing import Any

from backlog_utils import PRIORITY_RANK
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


def fetch_default_branch(run_cmd: Callable[[list[str]], str]) -> str:
    """Query GitHub repository default branch name."""
    try:
        output = run_cmd(["gh", "repo", "view", "--json", "defaultBranchRef"])
        data = json.loads(output)
        return data.get("defaultBranchRef", {}).get("name", "main")
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError):
        return "main"


def fetch_prs_to_review(
    run_cmd: Callable[[list[str]], str],
    login: str,
) -> list[dict[str, Any]]:
    """Fetch open PRs authored by others waiting for review."""
    args = [
        "gh", "pr", "list", "--search", "is:open -author:@me draft:false",
        "--json", "number,title,url,author,reviewRequests,reviewDecision",
    ]
    prs = json.loads(run_cmd(args))

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
                "item": f"[#{pr['number']}]({pr['url']}) {pr['title']}",
                "state": AWAITING_REVIEW_LABEL[is_awaiting],
                "review": REVIEW_REQUEST_STATE[is_awaiting],
                "priority": "Medium",
                "blocking": "0 PRs, 0 issues",
                "suggestion": (
                    f"Review the PR with `/commons:review --pr {pr['number']}`"
                ),
            },
        )

    items.sort(
        key=lambda x: (
            0 if x["review"] == REVIEW_REQUEST_STATE[True] else 1,
            PRIORITY_RANK.get(x["priority"], 3),
        ),
    )
    return items


def compute_technical_blockers(*, conflicting: bool, checks: str) -> str:
    """Format technical blocker description from conflicting and checks states."""
    if conflicting and checks == "failing":
        return TECHNICAL_BLOCKERS["BOTH"]
    if checks == "failing":
        return TECHNICAL_BLOCKERS["CHECKS"]
    if conflicting:
        return TECHNICAL_BLOCKERS["CONFLICT"]
    return TECHNICAL_BLOCKERS["NONE"]


def compute_review_blockers(threads: str, comments: str) -> str:
    """Format review blocker description from threads and comments states."""
    if threads == "unresolved" and comments == "unresolved":
        return REVIEW_BLOCKERS["BOTH"]
    if comments == "unresolved":
        return REVIEW_BLOCKERS["COMMENTS"]
    if threads == "unresolved":
        return REVIEW_BLOCKERS["THREADS"]
    return REVIEW_BLOCKERS["NONE"]


def linked_issue_for(pr: dict[str, Any]) -> dict[str, Any] | None:
    """Extract first linked closing issue from PR payload."""
    linked_issues = pr.get("closingIssuesReferences") or []
    return (
        {"number": linked_issues[0]["number"], "url": linked_issues[0]["url"]}
        if linked_issues
        else None
    )


def _classify_open_pr(
    pr: dict[str, Any],
    review_state: dict[str, Any],
    default_branch: str,
    head_to_pr_info: dict[str, dict[str, Any]],
) -> tuple[str, dict[str, Any]]:
    pr_number = pr["number"]

    tech_blockers = compute_technical_blockers(
        conflicting=review_state["conflicting"],
        checks=review_state["checks"],
    )
    rev_blockers = compute_review_blockers(
        review_state["threads"],
        review_state["comments"],
    )

    base_branch = pr.get("baseRefName", default_branch)
    is_default_target = base_branch == default_branch
    stacked_on_pr = head_to_pr_info.get(base_branch)

    has_blockers = (tech_blockers != TECHNICAL_BLOCKERS["NONE"]) or (
        rev_blockers != REVIEW_BLOCKERS["NONE"]
    )
    is_approved = review_state["state"] == "approved"

    base_entry = {
        "number": pr_number,
        "title": pr["title"],
        "url": pr["url"],
        "item": f"[#{pr_number}]({pr['url']}) {pr['title']}",
        "priority": "Medium",
        "blocking": "None",
        "technical_blockers": tech_blockers,
        "review_blockers": rev_blockers,
        "state": review_state["state"].capitalize(),
        "threads": review_state["threads"].capitalize(),
        "comments": review_state["comments"].capitalize(),
        "conflicting": "Yes" if review_state["conflicting"] else "No",
        "checks": review_state["checks"].capitalize(),
    }

    if has_blockers:
        base_entry["suggestion"] = (
            f"Resolve problems with `/commons:resolve --pr {pr_number}`"
        )
        return "merge_blockers", base_entry
    if is_default_target:
        if is_approved:
            base_entry["suggestion"] = "Merge the PR"
            return "merge_ready", base_entry
        base_entry["suggestion"] = (
            f"Self-review the PR with `/commons:review --pr {pr_number}`"
        )
        return "pending_approval", base_entry

    if stacked_on_pr:
        num = stacked_on_pr["number"]
        url = stacked_on_pr.get("url")
        link = f"[#{num}]({url})" if url else f"#{num}"
        stacked_on_str = f"PR {link}"
    else:
        stacked_on_str = base_branch

    base_entry["stacked_on"] = stacked_on_str
    base_entry["suggestion"] = (
        f"Self-review the PR with `/commons:review --pr {pr_number}`"
    )
    return "stacked_queue", base_entry


def fetch_open_and_draft_prs(
    run_cmd: Callable[[list[str]], str],
    graphql_fn: Callable[..., dict[str, Any]],
    owner: str,
    repo_name: str,
    default_branch: str,
) -> dict[str, Any]:
    """Fetch, classify, and sort user's open and draft PRs."""
    fields = "number,title,url,isDraft,closingIssuesReferences,headRefName,baseRefName"
    args = [
        "gh", "pr", "list", "--search", "is:open author:@me",
        "--json", fields,
    ]
    prs = json.loads(run_cmd(args))

    head_to_pr_info = {
        pr["headRefName"]: {"number": pr["number"], "url": pr.get("url")}
        for pr in prs
        if "headRefName" in pr
    }

    your_open_prs = []
    your_draft_prs = []

    sub_cats: dict[str, list[dict[str, Any]]] = {
        "merge_ready": [],
        "merge_blockers": [],
        "draft_prs": [],
        "pending_approval": [],
        "stacked_queue": [],
    }

    for pr in prs:
        pr_number = pr["number"]
        linked = linked_issue_for(pr)

        if bool(pr.get("isDraft")):
            closing = [
                {"number": r["number"], "url": r.get("url", "")}
                for r in pr.get("closingIssuesReferences") or []
            ]
            draft_entry = {
                "number": pr_number,
                "title": pr["title"],
                "url": pr["url"],
                "item": f"[#{pr_number}]({pr['url']}) {pr['title']}",
                "priority": "Medium",
                "blocking": "None",
                "linked_issue": linked,
                "_closing_issues": closing,
            }
            your_draft_prs.append(draft_entry)
            sub_cats["draft_prs"].append(draft_entry)
            continue

        review_state = fetch_review_state(
            graphql_fn,
            owner,
            repo_name,
            pr_number,
        )
        cat_key, entry = _classify_open_pr(
            pr,
            review_state,
            default_branch,
            head_to_pr_info,
        )
        # Attach closing issues for post-processing in collect_triage.py
        entry["_closing_issues"] = [
            {"number": r["number"], "url": r.get("url", "")}
            for r in pr.get("closingIssuesReferences") or []
        ]
        sub_cats[cat_key].append(entry)
        your_open_prs.append(entry)

    def sort_blockers(item: dict[str, Any]) -> tuple[int, int, int]:
        t_rank = TECH_BLOCKER_RANK.get(item["technical_blockers"], 3)
        r_rank = REV_BLOCKER_RANK.get(item["review_blockers"], 3)
        p_rank = PRIORITY_RANK.get(item["priority"], 3)
        return (t_rank, r_rank, p_rank)

    def sort_std(item: dict[str, Any]) -> int:
        return PRIORITY_RANK.get(item["priority"], 3)

    sub_cats["merge_ready"].sort(key=sort_std)
    sub_cats["merge_blockers"].sort(key=sort_blockers)
    sub_cats["draft_prs"].sort(key=sort_std)
    sub_cats["pending_approval"].sort(key=sort_std)
    sub_cats["stacked_queue"].sort(key=sort_std)

    return {
        "your_open_prs": your_open_prs,
        "your_draft_prs": your_draft_prs,
        "merge_ready": sub_cats["merge_ready"],
        "merge_blockers": sub_cats["merge_blockers"],
        "draft_prs": sub_cats["draft_prs"],
        "pending_approval": sub_cats["pending_approval"],
        "stacked_queue": sub_cats["stacked_queue"],
    }


def _downstream_issues(
    closing_nums: set[int],
    issue_to_downstream: dict[int, list[dict[str, Any]]],
) -> dict[int, dict[str, Any]]:
    """Collect all open issues downstream of a PR's closing issues."""
    result: dict[int, dict[str, Any]] = {}
    for cnum in closing_nums:
        for ds in issue_to_downstream.get(cnum, []):
            ds_num = ds.get("number")
            if ds_num is not None:
                result[ds_num] = ds
    return result


def _blocking_prs_for(
    pr_number: int,
    downstream: dict[int, dict[str, Any]],
    issue_to_closing_prs: dict[int, list[int]],
) -> set[int]:
    """Find other open PRs that close any issue downstream of this PR."""
    result: set[int] = set()
    for ds_num in downstream:
        for other_pr in issue_to_closing_prs.get(ds_num, []):
            if other_pr != pr_number:
                result.add(other_pr)
    return result


def _covered_issue_nums(
    blocking_pr_nums: set[int],
    pr_entries: list[dict[str, Any]],
) -> set[int]:
    """Collect issues already covered by a set of blocking PRs."""
    covered: set[int] = set()
    for bpr_num in blocking_pr_nums:
        for bpr in pr_entries:
            if bpr["number"] == bpr_num:
                for ci in bpr.get("_closing_issues", []):
                    covered.add(ci["number"])
    return covered


def _format_blocking(pr_count: int, issue_count: int) -> str:
    """Format a 'blocking' string, omitting zero parts; 'None' if both zero."""
    parts = []
    if pr_count:
        parts.append(f"{pr_count} PR{'s' if pr_count != 1 else ''}")
    if issue_count:
        parts.append(f"{issue_count} issue{'s' if issue_count != 1 else ''}")
    return ", ".join(parts) if parts else "None"


def apply_pr_blocking(
    pr_entries: list[dict[str, Any]],
    backlog_issues: list[dict[str, Any]],
) -> None:
    """Populate the 'blocking' field on each PR entry in-place.

    For a PR that closes issues C1, C2, ...:
    - downstream  = union of open issues blocked by any Ci (from backlog data)
    - blocking PRs = other open PRs that close any downstream issue
    - issue count  = downstream issues not already closed by a blocking PR

    Sets 'blocking' to "None" if both counts are zero.
    """
    issue_to_downstream: dict[int, list[dict[str, Any]]] = {
        issue["number"]: issue.get("_blocking_items", [])
        for issue in backlog_issues
        if issue.get("number") is not None
    }

    issue_to_closing_prs: dict[int, list[int]] = {}
    for pr in pr_entries:
        for ci in pr.get("_closing_issues", []):
            issue_to_closing_prs.setdefault(ci["number"], []).append(pr["number"])

    for pr in pr_entries:
        closing_nums = {ci["number"] for ci in pr.get("_closing_issues", [])}
        if not closing_nums:
            pr["blocking"] = "None"
            continue

        downstream = _downstream_issues(closing_nums, issue_to_downstream)
        blocking_pr_nums = _blocking_prs_for(
            pr["number"], downstream, issue_to_closing_prs,
        )
        covered = _covered_issue_nums(blocking_pr_nums, pr_entries)
        uncovered = sum(1 for n in downstream if n not in covered)
        pr["blocking"] = _format_blocking(len(blocking_pr_nums), uncovered)
