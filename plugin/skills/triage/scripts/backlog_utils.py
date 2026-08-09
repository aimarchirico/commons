#!/usr/bin/env python3
"""Helper for fetching, filtering, and sorting backlog issues."""

import importlib.util
import json
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Any

SOLVABLE_ISSUE_TYPES = {"Story", "Task", "Bug"}
PRIORITY_RANK = {"High": 0, "Medium": 1, "Low": 2, "Unset": 3}
ASSIGNEE_YOU = "You"
ASSIGNEE_UNASSIGNED = "Unassigned"
NO_BLOCKERS = "None"
_EMPTY_DEPS = {"blocked_by": [], "blocking": []}


def _load_blocking_prs() -> ModuleType:
    shared_dir = Path(__file__).resolve().parent.parent.parent.parent / "shared"
    module_path = shared_dir / "blocking_prs.py"
    spec = importlib.util.spec_from_file_location("blocking_prs", module_path)
    if spec is None or spec.loader is None:
        msg = f"Cannot load blocking_prs from {module_path}"
        raise ImportError(msg)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_blocking_prs = _load_blocking_prs()
fetch_issues_dependencies = _blocking_prs.fetch_issues_dependencies


def _format_blocked_by(
    blocked_by_items: list[dict[str, Any]],
) -> str:
    if not blocked_by_items:
        return NO_BLOCKERS

    formatted = []
    for idx, b in enumerate(blocked_by_items):
        pr = b.get("open_pr")
        item = pr or b
        num = str(item["number"])
        url = item.get("url")
        link = f"[#{num}]({url})" if url else f"#{num}"
        prefix = "PR " if idx == 0 else ""
        formatted.append(f"{prefix}{link}")
    return ", ".join(formatted)


def _format_blocking_issues(count: int) -> str:
    suffix = "s" if count != 1 else ""
    return f"{count} issue{suffix}"


_BacklogCandidate = tuple[dict[str, Any], dict[str, Any], int, bool]


def _collect_backlog_candidates(
    items: list[dict[str, Any]],
    login: str,
) -> tuple[list[_BacklogCandidate], int]:
    candidates: list[_BacklogCandidate] = []
    assigned_to_others_count = 0

    for item in items:
        content = item.get("content") or {}
        if (
            item.get("status") != "Todo"
            or content.get("type") != "Issue"
            or item.get("type") not in SOLVABLE_ISSUE_TYPES
        ):
            continue

        number = content.get("number")
        if number is None:
            continue

        assignees = item.get("assignees") or []
        is_mine = login in assignees
        if not (is_mine or not assignees):
            assigned_to_others_count += 1
            continue

        candidates.append((item, content, number, is_mine))

    return candidates, assigned_to_others_count


def _build_backlog_entries(
    candidates: list[_BacklogCandidate],
    deps_by_number: dict[int, dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]], int]:
    entries: list[dict[str, Any]] = []
    buckets: dict[str, list[dict[str, Any]]] = {
        "assigned_ready": [],
        "assigned_stackable": [],
        "available_ready": [],
        "available_stackable": [],
    }
    fully_blocked_count = 0

    for item, content, number, is_mine in candidates:
        deps = deps_by_number.get(number, _EMPTY_DEPS)
        blocked_by_items = deps.get("blocked_by", [])
        blocking_items = deps.get("blocking", [])

        if any(b.get("open_pr") is None for b in blocked_by_items):
            fully_blocked_count += 1
            continue

        blocking_count = len(blocking_items)
        entry = {
            "number": number,
            "title": content.get("title"),
            "url": content.get("url"),
            "item": f"[#{number}]({content.get('url')}) {content.get('title')}",
            "assignee": ASSIGNEE_YOU if is_mine else ASSIGNEE_UNASSIGNED,
            "priority": item.get("priority") or "Unset",
            "blocked_by": _format_blocked_by(blocked_by_items),
            "blocking": _format_blocking_issues(blocking_count),
            "blocking_count": blocking_count,
            "_blocked_by_items": blocked_by_items,
            "_blocking_items": blocking_items,
            "suggestion": f"Solve issue with `/commons:solve --issue {number}`",
        }
        entries.append(entry)

        is_blocked = bool(blocked_by_items)
        if is_mine:
            buckets["assigned_stackable" if is_blocked else "assigned_ready"].append(
                entry,
            )
        else:
            buckets["available_stackable" if is_blocked else "available_ready"].append(
                entry,
            )

    return entries, buckets, fully_blocked_count


def fetch_backlog_issues(
    run_cmd: Callable[[list[str]], str],
    repo: tuple[str, str],
    project_owner: str,
    project_number: int,
    login: str,
) -> dict[str, Any]:
    """Fetch Todo backlog issues assigned to or unassigned for `login`.

    Issues blocked by an open issue that lacks an open PR are excluded.
    Issues blocked only by open issues with attached open PRs are included.
    Returns a dict with `backlog_issues`, categorized sub-lists,
    `assigned_to_others_count`, and `fully_blocked_count`.
    """
    owner, repo_name = repo
    item_output = run_cmd(
        [
            "gh",
            "project",
            "item-list",
            str(project_number),
            "--owner",
            project_owner,
            "--format",
            "json",
            "--limit",
            "200",
            "--query",
            "status:Todo is:issue",
        ],
    )
    items = json.loads(item_output).get("items", [])
    candidates, assigned_to_others_count = _collect_backlog_candidates(items, login)

    deps_by_number = fetch_issues_dependencies(
        run_cmd,
        owner,
        repo_name,
        [c[2] for c in candidates],
    )
    entries, buckets, fully_blocked_count = _build_backlog_entries(
        candidates,
        deps_by_number,
    )

    def sort_key(issue: dict[str, Any]) -> tuple[int, int]:
        p_rank = PRIORITY_RANK.get(issue["priority"], 3)
        return (p_rank, -issue["blocking_count"])

    for bucket in buckets.values():
        bucket.sort(key=sort_key)

    all_backlog = sorted(
        entries,
        key=lambda i: (
            0 if i["assignee"] == ASSIGNEE_YOU else 1,
            PRIORITY_RANK.get(i["priority"], 3),
            -i["blocking_count"],
        ),
    )

    return {
        "backlog_issues": all_backlog,
        "assigned_ready": buckets["assigned_ready"],
        "assigned_stackable": buckets["assigned_stackable"],
        "available_ready": buckets["available_ready"],
        "available_stackable": buckets["available_stackable"],
        "assigned_to_others_count": assigned_to_others_count,
        "fully_blocked_count": fully_blocked_count,
    }


def fetch_in_progress_issues(
    run_cmd: Callable[[list[str]], str],
    repo: tuple[str, str],
    project_owner: str,
    project_number: int,
) -> list[dict[str, Any]]:
    """Fetch In Progress issues assigned to the caller, sorted by priority.

    Each entry's `blocking` count mirrors `fetch_backlog_issues`' format.
    Callers are responsible for excluding issues already covered by an open PR.
    """
    owner, repo_name = repo
    item_output = run_cmd(
        [
            "gh",
            "project",
            "item-list",
            str(project_number),
            "--owner",
            project_owner,
            "--format",
            "json",
            "--limit",
            "200",
            "--query",
            'status:"In Progress" is:issue assignee:@me',
        ],
    )
    items = json.loads(item_output).get("items", [])

    candidates: list[tuple[dict[str, Any], dict[str, Any], int]] = []
    for item in items:
        content = item.get("content") or {}
        if (
            content.get("type") != "Issue"
            or item.get("type") not in SOLVABLE_ISSUE_TYPES
        ):
            continue

        number = content.get("number")
        if number is None:
            continue

        candidates.append((item, content, number))

    deps_by_number = fetch_issues_dependencies(
        run_cmd,
        owner,
        repo_name,
        [c[2] for c in candidates],
    )

    entries: list[dict[str, Any]] = []
    for item, content, number in candidates:
        blocking_count = len(deps_by_number.get(number, _EMPTY_DEPS)["blocking"])

        entries.append(
            {
                "number": number,
                "title": content.get("title"),
                "url": content.get("url"),
                "item": f"[#{number}]({content.get('url')}) {content.get('title')}",
                "priority": item.get("priority") or "Unset",
                "blocking": _format_blocking_issues(blocking_count),
                "blocking_count": blocking_count,
                "suggestion": "Continue implementing or open PR",
            },
        )

    entries.sort(
        key=lambda i: (PRIORITY_RANK.get(i["priority"], 3), -i["blocking_count"]),
    )
    return entries
