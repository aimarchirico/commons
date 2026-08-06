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
fetch_issue_dependencies = _blocking_prs.fetch_issue_dependencies


def _format_blocked_by(
    blocked_by_items: list[dict[str, Any]],
) -> str:
    if not blocked_by_items:
        return NO_BLOCKERS

    formatted = []
    for b in blocked_by_items:
        pr = b.get("open_pr")
        if pr:
            formatted.append(str(pr["number"]))
        else:
            formatted.append(str(b["number"]))
    return ", ".join(formatted)


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
        ],
    )
    items = json.loads(item_output).get("items", [])

    entries: list[dict[str, Any]] = []
    assigned_ready: list[dict[str, Any]] = []
    assigned_stackable: list[dict[str, Any]] = []
    available_ready: list[dict[str, Any]] = []
    available_stackable: list[dict[str, Any]] = []

    assigned_to_others_count = 0
    fully_blocked_count = 0

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

        deps = fetch_issue_dependencies(run_cmd, owner, repo_name, number)
        blocked_by_items = deps.get("blocked_by", [])
        blocking_items = deps.get("blocking", [])

        if any(b.get("open_pr") is None for b in blocked_by_items):
            fully_blocked_count += 1
            continue

        priority = item.get("priority") or "Unset"
        blocking_count = len(blocking_items)
        blocking_str = f"{blocking_count} issues"

        entry = {
            "number": number,
            "title": content.get("title"),
            "url": content.get("url"),
            "assignee": ASSIGNEE_YOU if is_mine else ASSIGNEE_UNASSIGNED,
            "priority": priority,
            "blocked_by": _format_blocked_by(blocked_by_items),
            "blocking": blocking_str,
            "blocking_count": blocking_count,
            "suggestion": f"Solve issue with `/commons:solve --issue {number}`",
        }
        entries.append(entry)

        is_blocked = bool(blocked_by_items)
        if is_mine:
            if is_blocked:
                assigned_stackable.append(entry)
            else:
                assigned_ready.append(entry)
        elif is_blocked:
            available_stackable.append(entry)
        else:
            available_ready.append(entry)

    def sort_key(issue: dict[str, Any]) -> tuple[int, int]:
        p_rank = PRIORITY_RANK.get(issue["priority"], 3)
        return (p_rank, -issue["blocking_count"])

    assigned_ready.sort(key=sort_key)
    assigned_stackable.sort(key=sort_key)
    available_ready.sort(key=sort_key)
    available_stackable.sort(key=sort_key)

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
        "assigned_ready": assigned_ready,
        "assigned_stackable": assigned_stackable,
        "available_ready": available_ready,
        "available_stackable": available_stackable,
        "assigned_to_others_count": assigned_to_others_count,
        "fully_blocked_count": fully_blocked_count,
    }
