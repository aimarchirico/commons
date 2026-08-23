#!/usr/bin/env python3
"""Helper for fetching, classifying, and sorting pull requests for triage."""

import json
from collections.abc import Callable
from typing import Any

from backlog_utils import PRIORITY_RANK
from review_state import fetch_review_states

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


def fetch_all_open_prs(run_cmd: Callable[[list[str]], str]) -> list[dict[str, Any]]:
    """Fetch every open PR in the repository, returning raw PR dictionaries."""
    fields = (
        "number,title,url,author,reviewRequests,reviewDecision,isDraft,"
        "closingIssuesReferences,headRefName,baseRefName"
    )
    args = ["gh", "pr", "list", "--search", "is:open", "--json", fields]
    return list(json.loads(run_cmd(args)))


def fetch_prs_to_review(
    prs: list[dict[str, Any]],
    login: str,
) -> list[dict[str, Any]]:
    """Filter open PRs authored by others, excluding drafts, waiting for review."""
    items = []
    for pr in prs:
        author = pr.get("author") or {}
        if (
            author.get("login") == login
            or bool(pr.get("isDraft"))
            or author.get("is_bot")
            or pr.get("reviewDecision") == "APPROVED"
        ):
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


def linked_issues_for(pr: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract all linked closing issues from PR payload."""
    return [
        {"number": issue["number"], "url": issue["url"]}
        for issue in pr.get("closingIssuesReferences") or []
    ]


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


def _sort_blockers(item: dict[str, Any]) -> tuple[int, int, int]:
    t_rank = TECH_BLOCKER_RANK.get(item["technical_blockers"], 3)
    r_rank = REV_BLOCKER_RANK.get(item["review_blockers"], 3)
    p_rank = PRIORITY_RANK.get(item["priority"], 3)
    return (t_rank, r_rank, p_rank)

def _sort_std(item: dict[str, Any]) -> int:
    return PRIORITY_RANK.get(item["priority"], 3)


def fetch_open_and_draft_prs(
    prs: list[dict[str, Any]],
    graphql_fn: Callable[..., dict[str, Any]],
    repo: tuple[str, str],
    default_branch: str,
    login: str,
) -> dict[str, Any]:
    """Classify and sort the caller's own open and draft PRs."""
    owner, repo_name = repo
    your_prs = [pr for pr in prs if (pr.get("author") or {}).get("login") == login]

    head_to_pr_info = {
        pr["headRefName"]: {"number": pr["number"], "url": pr.get("url")}
        for pr in your_prs
        if "headRefName" in pr
    }

    non_draft_numbers = [
        pr["number"] for pr in your_prs if not bool(pr.get("isDraft"))
    ]
    review_states = fetch_review_states(graphql_fn, owner, repo_name, non_draft_numbers)

    your_open_prs = []
    your_draft_prs = []
    sub_cats: dict[str, list[dict[str, Any]]] = {
        "merge_ready": [],
        "merge_blockers": [],
        "draft_prs": [],
        "pending_approval": [],
        "stacked_queue": [],
    }

    for pr in your_prs:
        pr_number = pr["number"]

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
                "linked_issues": linked_issues_for(pr),
                "_closing_issues": closing,
            }
            your_draft_prs.append(draft_entry)
            sub_cats["draft_prs"].append(draft_entry)
            continue
        review_state = review_states[pr_number]
        cat_key, entry = _classify_open_pr(
            pr,
            review_state,
            default_branch,
            head_to_pr_info,
        )
        entry["_closing_issues"] = [
            {"number": r["number"], "url": r.get("url", "")}
            for r in pr.get("closingIssuesReferences") or []
        ]
        sub_cats[cat_key].append(entry)
        your_open_prs.append(entry)
    for cat in ("merge_ready", "draft_prs", "pending_approval", "stacked_queue"):
        sub_cats[cat].sort(key=_sort_std)
    sub_cats["merge_blockers"].sort(key=_sort_blockers)
    return {
        "your_open_prs": your_open_prs,
        "your_draft_prs": your_draft_prs,
        **{k: sub_cats[k] for k in sub_cats},
    }
