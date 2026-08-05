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

        entries.append({
            "number": number,
            "title": content.get("title"),
            "url": content.get("url"),
            "assignee": "you" if is_mine else "unassigned",
            "priority": item.get("priority"),
            "blocking": blocking,
        })

    entries.sort(
        key=lambda e: (
            e["assignee"] != "you",
            PRIORITY_RANK.get(e["priority"], len(PRIORITY_RANK)),
            -len(e["blocking"]),
        ),
    )
    return entries
