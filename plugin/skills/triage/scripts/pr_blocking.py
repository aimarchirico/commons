#!/usr/bin/env python3
"""Helpers for computing PR blocking counts from closed-issue dependency data."""

from typing import Any


def _blocking_prs_for(
    pr_number: int,
    all_blocked: set[int],
    issue_to_closing_prs: dict[int, list[int]],
) -> set[int]:
    result: set[int] = set()
    for ds_num in all_blocked:
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
    closing_issue_deps: dict[int, dict[str, Any]],
) -> None:
    """Populate the 'blocking' field on each PR entry in-place.

    For a PR that closes issues C1, C2, ...:
    - all_blocked = union of each Ci's own direct `blocking` edges
    - blocking PRs = other open PRs that also close any all_blocked issue
    - issue count = all_blocked issues not already closed by a blocking PR

    Sets 'blocking' to "None" if both counts are zero.

    `closing_issue_deps` must be keyed by every issue number any pr_entries
    PR closes, fetched fresh regardless of whether that issue is itself a
    leaf, since a closed parent issue's own `blocking` edges count too.
    """
    issue_to_closing_prs: dict[int, list[int]] = {}
    for pr in pr_entries:
        for ci in pr.get("_closing_issues", []):
            issue_to_closing_prs.setdefault(ci["number"], []).append(pr["number"])

    for pr in pr_entries:
        closing_nums = {ci["number"] for ci in pr.get("_closing_issues", [])}
        if not closing_nums:
            pr["blocking"] = "None"
            continue

        all_blocked: set[int] = set()
        for cnum in closing_nums:
            deps = closing_issue_deps.get(cnum) or {}
            all_blocked.update(b["number"] for b in deps.get("blocking", []))

        blocking_pr_nums = _blocking_prs_for(
            pr["number"], all_blocked, issue_to_closing_prs,
        )
        covered = _covered_issue_nums(blocking_pr_nums, pr_entries)
        uncovered = sum(1 for n in all_blocked if n not in covered)
        pr["blocking"] = _format_blocking(len(blocking_pr_nums), uncovered)
