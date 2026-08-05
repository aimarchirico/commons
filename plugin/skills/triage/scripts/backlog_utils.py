#!/usr/bin/env python3
"""Helper for fetching, filtering, and sorting backlog issues."""

import json
from collections.abc import Callable
from typing import Any

SOLVABLE_ISSUE_TYPES = {"Story", "Task", "Bug"}
PRIORITY_RANK = {"High": 0, "Medium": 1, "Low": 2}


def _fetch_dependencies(
    run_cmd: Callable[[list[str]], str], number: int,
) -> tuple[list[int], list[int]]:
    output = run_cmd([
        "gh", "issue", "view", str(number), "--json", "blockedBy,blocking",
    ])
    data = json.loads(output)
    blocked_by = [
        n["number"] for n in data.get("blockedBy", {}).get("nodes", [])
        if n.get("state") == "OPEN"
    ]
    blocking = [
        n["number"] for n in data.get("blocking", {}).get("nodes", [])
        if n.get("state") == "OPEN"
    ]
    return blocked_by, blocking


def fetch_backlog_issues(
    run_cmd: Callable[[list[str]], str],
    project_owner: str,
    project_number: int,
    login: str,
) -> list[dict[str, Any]]:
    """Fetch Todo backlog issues assigned to or unassigned for `login`.

    Issues blocked by an open issue are excluded entirely: they aren't
    actionable yet regardless of assignment. Results are sorted assigned
    before unassigned, then by priority (High first), then by how many
    open issues each one is blocking (most first).
    """
    item_output = run_cmd([
        "gh", "project", "item-list", str(project_number),
        "--owner", project_owner, "--format", "json", "--limit", "200",
    ])
    items = json.loads(item_output).get("items", [])

    entries: list[dict[str, Any]] = []
    ranks: list[tuple[bool, int, int]] = []
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
            continue

        blocked_by, blocking = _fetch_dependencies(run_cmd, number)
        if blocked_by:
            continue

        priority = item.get("priority")
        entries.append({
            "number": number,
            "title": content.get("title"),
            "url": content.get("url"),
            "assignee": "You" if is_mine else "Unassigned",
            "priority": priority or "Unset",
            "blocking": (
                ", ".join(f"#{n}" for n in blocking) if blocking else "Not blocking"
            ),
        })
        ranks.append((
            not is_mine,
            PRIORITY_RANK.get(priority, len(PRIORITY_RANK)),
            -len(blocking),
        ))

    order = sorted(range(len(entries)), key=lambda i: ranks[i])
    return [entries[i] for i in order]
