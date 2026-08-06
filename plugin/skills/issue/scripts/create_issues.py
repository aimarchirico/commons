#!/usr/bin/env python3
"""Script for creating GitHub issues and linking them to GitHub Projects."""

import contextlib
import json
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from project_utils import (
    run_project_preflight,
    set_project_field,
    validate_item_options,
)

MIN_ARG_COUNT = 2


def run_cmd(args: list[str]) -> str:
    """Execute a shell command via subprocess and return stripped output."""
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return result.stdout.strip()


def check_sub_issue_extension() -> None:
    """Ensure gh-sub-issue extension is installed."""
    try:
        output = run_cmd(["gh", "extension", "list"])
        if "gh-sub-issue" not in output:
            sys.stdout.write("Installing gh-sub-issue extension...\n")
            gh_bin = shutil.which("gh") or "gh"
            subprocess.run(
                [gh_bin, "extension", "install", "yahsan2/gh-sub-issue"],
                check=True,
            )
    except (subprocess.CalledProcessError, OSError) as e:
        sys.stderr.write(
            f"Warning: Error verifying or installing gh-sub-issue: {e}\n",
        )


def fail_if_errors(errors: list[str]) -> None:
    """Print setup error messages to stderr and exit if any exist."""
    if errors:
        sys.stderr.write(
            "Error: GitHub project setup is incomplete. "
            f"Found {len(errors)} problem(s):\n",
        )
        for e in errors:
            sys.stderr.write(f"  - {e}\n")
        sys.exit(1)


DepState = tuple[dict[str, str], list[tuple[str, list[str]]]]


def record_dependency_state(
    item: dict[str, Any],
    issue_id: str,
    dep_state: DepState,
) -> None:
    """Record issue ID mappings and pending blocked-by dependencies."""
    id_map, pending_deps = dep_state
    if local_id := item.get("id"):
        id_map[local_id] = issue_id
    if blocked_by := item.get("blocked_by"):
        pending_deps.append((issue_id, blocked_by))


def create_issue_recursive(
    item: dict[str, Any],
    parent_id: str | None,
    owner: str,
    project_info: tuple[int | None, str | None, str | None, str | None, dict[str, Any]],
    dep_state: DepState | None = None,
) -> None:
    """Recursively create a GitHub issue and its children, linking to projects."""
    if dep_state is None:
        dep_state = ({}, [])
    project_number, project_id, type_field_id, priority_field_id, fields_data = (
        project_info
    )
    title = item.get("title")
    body = item.get("body", "")
    type_val = item.get("type")
    priority_val = item.get("priority")

    if not title:
        sys.stdout.write("Warning: Skipped creating issue due to missing title.\n")
        return

    if not parent_id:
        sys.stdout.write(f"Creating top-level issue: '{title}'...\n")
        args = ["gh", "issue", "create", "--title", title, "--body", body]
    else:
        sys.stdout.write(
            f"Creating child issue: '{title}' under parent {parent_id}...\n",
        )
        args = [
            "gh",
            "sub-issue",
            "create",
            "--title",
            title,
            "--body",
            body,
            "--parent",
            str(parent_id),
        ]

    issue_url_raw = run_cmd(args)
    issue_url = next(
        (w for w in issue_url_raw.split() if w.startswith(("http://", "https://"))),
        issue_url_raw,
    )
    issue_id = issue_url.split("/")[-1]
    level_str = "child" if parent_id else "top-level"
    sys.stdout.write(f"Created {level_str} issue: {issue_id}\n")

    record_dependency_state(item, issue_id, dep_state)

    if project_id and issue_url:
        try:
            sys.stdout.write(
                f"Adding issue {issue_id} to project #{project_number}...\n",
            )
            item_output = run_cmd(
                [
                    "gh",
                    "project",
                    "item-add",
                    str(project_number),
                    "--owner",
                    owner,
                    "--url",
                    issue_url,
                    "--format",
                    "json",
                ],
            )
            item_data = json.loads(item_output)
            if item_id := item_data.get("id"):
                set_project_field(
                    run_cmd,
                    item_id,
                    project_id,
                    ("Type", type_field_id, type_val),
                    fields_data,
                )
                set_project_field(
                    run_cmd,
                    item_id,
                    project_id,
                    ("Priority", priority_field_id, priority_val),
                    fields_data,
                )
        except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
            sys.stderr.write(
                "Warning: Failed to add/configure project fields for issue "
                f"{issue_id}. {e}\n",
            )

    for child in item.get("children", []):
        create_issue_recursive(
            child,
            issue_id,
            owner,
            project_info,
            dep_state,
        )


def wire_blocked_by(
    run_cmd: Callable[[list[str]], str],
    id_map: dict[str, str],
    pending_deps: list[tuple[str, list[str]]],
) -> None:
    """Edit created GitHub issues to add blocked-by relationships."""
    for issue_id, blocked_by in pending_deps:
        numbers = []
        for local_id in blocked_by:
            blocker_id = id_map.get(local_id)
            if blocker_id is None:
                sys.stderr.write(
                    f"Warning: blocked_by id '{local_id}' for issue {issue_id} does "
                    "not match any created issue; skipping.\n",
                )
                continue
            numbers.append(blocker_id)

        if not numbers:
            continue

        sys.stdout.write(
            f"Marking issue {issue_id} as blocked by {', '.join(numbers)}...\n",
        )
        try:
            run_cmd(
                [
                    "gh",
                    "issue",
                    "edit",
                    issue_id,
                    "--add-blocked-by",
                    ",".join(numbers),
                ],
            )
        except subprocess.CalledProcessError as e:
            msg = f"Warning: Failed to set blocked-by for issue {issue_id}. {e}\n"
            sys.stderr.write(msg)


def main() -> None:
    """Main entry point for parsing input JSON and creating issues."""
    if len(sys.argv) < MIN_ARG_COUNT:
        sys.stdout.write("Error: JSON file path not specified.\n")
        sys.stdout.write(f"Usage: {sys.argv[0]} <path-to-issues.json>\n")
        sys.exit(1)

    json_file_path = Path(sys.argv[1])
    if not json_file_path.is_file():
        sys.stderr.write(f"Error: File '{json_file_path}' not found.\n")
        sys.exit(1)

    try:
        with json_file_path.open(encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        sys.stderr.write(f"Error: Failed to parse '{json_file_path}' as JSON. {e}\n")
        with contextlib.suppress(OSError):
            json_file_path.unlink()
        sys.exit(1)

    try:
        pf = run_project_preflight(run_cmd, require_fields=True)
        check_sub_issue_extension()
        items = data.get("items", [])
        if item_errors := validate_item_options(items, pf["fields_data"]):
            fail_if_errors(item_errors)

        sys.stdout.write("Processing and creating issues...\n")
        project_info = (
            pf["project_number"],
            pf["project_id"],
            pf["type_field_id"],
            pf["priority_field_id"],
            pf["fields_data"],
        )
        owner = str(pf["owner"])
        id_map: dict[str, str] = {}
        pending_deps: list[tuple[str, list[str]]] = []
        dep_state: DepState = (id_map, pending_deps)
        for item in items:
            create_issue_recursive(item, None, owner, project_info, dep_state)

        if pending_deps:
            sys.stdout.write("Wiring blocked-by relationships...\n")
            wire_blocked_by(run_cmd, id_map, pending_deps)

        sys.stdout.write("Successfully created all issues.\n")
    finally:
        with contextlib.suppress(OSError):
            json_file_path.unlink()


if __name__ == "__main__":
    main()
