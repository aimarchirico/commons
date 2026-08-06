#!/usr/bin/env python3
"""Helper for fetching, filtering, and sorting backlog issues."""

import importlib.util
import json
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Any

SOLVABLE_ISSUE_TYPES = {"Story", "Task", "Bug"}
PRIORITY_RANK = {"High": 0, "Medium": 1, "Low": 2}


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
    owner: str,
    repo_name: str,
) -> str:
    if not blocked_by_items:
        return "None"
    formatted = []
    for b in blocked_by_items:
        num = b["number"]
        url = b.get("url", f"https://github.com/{owner}/{repo_name}/issues/{num}")
        pr = b.get("open_pr")
        if pr:
            pr_num = pr["number"]
            pr_url = pr.get(
                "url",
                f"https://github.com/{owner}/{repo_name}/pull/{pr_num}",
            )
            formatted.append(f"[#{num}]({url}) (PR [#{pr_num}]({pr_url}))")
        else:
            formatted.append(f"[#{num}]({url})")
    return ", ".join(formatted)


def _format_blocking(
    blocking_items: list[dict[str, Any]],
    owner: str,
    repo_name: str,
) -> str:
    if not blocking_items:
        return "None"
    formatted = []
    for b in blocking_items:
        num = b["number"]
        url = b.get("url", f"https://github.com/{owner}/{repo_name}/issues/{num}")
        formatted.append(f"[#{num}]({url})")
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
    Returns a dict with `backlog_issues`, `assigned_to_others_count`,
    and `fully_blocked_count`.
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
    ranks: list[tuple[bool, int, int]] = []
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

        priority = item.get("priority")
        entries.append(
            {
                "number": number,
                "title": content.get("title"),
                "url": content.get("url"),
                "assignee": "You" if is_mine else "Unassigned",
                "priority": priority or "Unset",
                "blocked_by": _format_blocked_by(blocked_by_items, owner, repo_name),
                "blocking": _format_blocking(blocking_items, owner, repo_name),
            },
        )
        ranks.append(
            (
                not is_mine,
                PRIORITY_RANK.get(priority, len(PRIORITY_RANK)),
                -len(blocking_items),
            ),
        )

    order = sorted(range(len(entries)), key=lambda i: ranks[i])
    return {
        "backlog_issues": [entries[i] for i in order],
        "assigned_to_others_count": assigned_to_others_count,
        "fully_blocked_count": fully_blocked_count,
    }
