#!/usr/bin/env python3
"""Helpers for computing PR blocking counts from backlog dependency data."""

from typing import Any


def _downstream_issues(
    closing_nums: set[int],
    issue_to_downstream: dict[int, list[dict[str, Any]]],
) -> dict[int, dict[str, Any]]:
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
    covered: set[int] = set()
    for bpr_num in blocking_pr_nums:
        for bpr in pr_entries:
            if bpr["number"] == bpr_num:
                for ci in bpr.get("_closing_issues", []):
                    covered.add(ci["number"])
    return covered


def _format_blocking(pr_count: int, issue_count: int) -> str:
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
    - blocked_backlog = backlog issues that list this PR in their blocked_by items
    - all_blocked = downstream U blocked_backlog
    - blocking PRs = other open PRs that close any all_blocked issue
    - issue count  = all_blocked issues not already closed by a blocking PR

    Sets 'blocking' to "None" if both counts are zero.

    `backlog_issues` may include fully-blocked entries that are hidden from
    the display buckets but still carry `_blocked_by_items`/`_blocking_items`
    needed here.
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

    pr_to_blocked_backlog: dict[int, set[int]] = {}
    for issue in backlog_issues:
        for blocker in issue.get("_blocked_by_items", []):
            open_pr = blocker.get("open_pr")
            if open_pr is not None:
                pr_num = open_pr.get("number")
                if pr_num is not None:
                    pr_to_blocked_backlog.setdefault(pr_num, set()).add(issue["number"])

    for pr in pr_entries:
        closing_nums = {ci["number"] for ci in pr.get("_closing_issues", [])}
        if not closing_nums:
            pr["blocking"] = "None"
            continue

        downstream = _downstream_issues(closing_nums, issue_to_downstream)
        blocked_backlog = pr_to_blocked_backlog.get(pr["number"], set())
        all_blocked = set(downstream.keys()) | blocked_backlog
        blocking_pr_nums = _blocking_prs_for(
            pr["number"], {n: {} for n in all_blocked}, issue_to_closing_prs,
        )
        covered = _covered_issue_nums(blocking_pr_nums, pr_entries)
        uncovered = sum(1 for n in all_blocked if n not in covered)
        pr["blocking"] = _format_blocking(len(blocking_pr_nums), uncovered)
