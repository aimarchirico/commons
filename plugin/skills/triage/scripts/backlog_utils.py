#!/usr/bin/env python3
"""Helper for fetching and bucketing backlog issues, including blockers."""

import json
from collections.abc import Callable
from typing import Any

SOLVABLE_ISSUE_TYPES = {"Story", "Task", "Bug"}


def _fetch_open_blockers(
    run_cmd: Callable[[list[str]], str], number: int,
) -> list[int]:
    output = run_cmd(["gh", "issue", "view", str(number), "--json", "blockedBy"])
    data = json.loads(output)
    nodes = data.get("blockedBy", {}).get("nodes", [])
    return [n["number"] for n in nodes if n.get("state") == "OPEN"]


def fetch_backlog_issues(
    run_cmd: Callable[[list[str]], str],
    project_owner: str,
    project_number: int,
    login: str,
) -> list[dict[str, Any]]:
    """Fetch Todo backlog issues assigned to or unassigned for `login`.

    Issues blocked by an open issue are bucketed separately, since they
    aren't actionable yet regardless of assignment.
    """
    item_output = run_cmd([
        "gh", "project", "item-list", str(project_number),
        "--owner", project_owner, "--format", "json", "--limit", "200",
    ])
    items = json.loads(item_output).get("items", [])

    assigned = []
    unassigned = []
    blocked = []
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

        entry = {
            "number": number,
            "title": content.get("title"),
            "url": content.get("url"),
        }
        blockers = _fetch_open_blockers(run_cmd, number)
        if blockers:
            entry["bucket"] = "blocked"
            entry["blocked_by"] = blockers
            blocked.append(entry)
        elif is_mine:
            entry["bucket"] = "assigned"
            assigned.append(entry)
        else:
            entry["bucket"] = "unassigned"
            unassigned.append(entry)

    return assigned + unassigned + blocked
