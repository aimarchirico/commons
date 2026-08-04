#!/usr/bin/env python3
"""Script for creating GitHub issues and linking them to GitHub Projects."""

import contextlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from project_utils import (
    get_project_context,
    get_project_fields,
    set_project_field,
    validate_project_setup,
)

MIN_ARG_COUNT = 2


def _run_cmd(args: list[str]) -> str:
    result = subprocess.run(args, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def _check_dependencies() -> None:
    gh_bin = shutil.which("gh")
    if not gh_bin:
        sys.stderr.write(
            "Error: GitHub CLI (gh) is not installed or not in PATH.\n",
        )
        sys.exit(1)

    try:
        subprocess.run([gh_bin, "auth", "status"], capture_output=True, check=True)
    except subprocess.CalledProcessError:
        sys.stderr.write(
            "Error: GitHub CLI is not authenticated. "
            "Please run 'gh auth login' first.\n",
        )
        sys.exit(1)

    try:
        output = _run_cmd(["gh", "extension", "list"])
        if "gh-sub-issue" not in output:
            sys.stdout.write("Installing gh-sub-issue extension...\n")
            subprocess.run(
                [gh_bin, "extension", "install", "yahsan2/gh-sub-issue"],
                check=True,
            )
    except (subprocess.CalledProcessError, OSError) as e:
        sys.stderr.write(
            f"Warning: Error verifying or installing gh-sub-issue: {e}\n",
        )


def _fail_if_errors(errors: list[str]) -> None:
    if errors:
        sys.stderr.write(
            "Error: GitHub project setup is incomplete. "
            f"Found {len(errors)} problem(s):\n",
        )
        for e in errors:
            sys.stderr.write(f"  - {e}\n")
        sys.exit(1)


def _create_issue_recursive(
    item: dict[str, Any],
    parent_id: str | None,
    owner: str,
    project_info: tuple[int | None, str | None, str | None, str | None, dict[str, Any]],
) -> None:
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
            "gh", "sub-issue", "create",
            "--title", title,
            "--body", body,
            "--parent", str(parent_id),
        ]

    issue_url_raw = _run_cmd(args)
    issue_url = next(
        (
            w for w in issue_url_raw.split()
            if w.startswith(("http://", "https://"))
        ),
        issue_url_raw,
    )
    issue_id = issue_url.split("/")[-1]
    level_str = "child" if parent_id else "top-level"
    sys.stdout.write(f"Created {level_str} issue: {issue_id}\n")

    if project_id and issue_url:
        try:
            sys.stdout.write(
                f"Adding issue {issue_id} to project #{project_number}...\n",
            )
            item_output = _run_cmd([
                "gh", "project", "item-add", str(project_number),
                "--owner", owner, "--url", issue_url, "--format", "json",
            ])
            item_data = json.loads(item_output)
            if item_id := item_data.get("id"):
                set_project_field(
                    _run_cmd, item_id, project_id,
                    ("Type", type_field_id, type_val), fields_data,
                )
                set_project_field(
                    _run_cmd, item_id, project_id,
                    ("Priority", priority_field_id, priority_val), fields_data,
                )
        except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
            sys.stderr.write(
                "Warning: Failed to add/configure project fields for issue "
                f"{issue_id}. {e}\n",
            )

    for child in item.get("children", []):
        _create_issue_recursive(
            child,
            issue_id,
            owner,
            project_info,
        )


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
        _check_dependencies()
        owner, project_number, project_id, context_error = get_project_context(_run_cmd)
        type_field_id, priority_field_id, fields_data, fields_errors = (
            get_project_fields(_run_cmd, owner or "", project_number)
        )
        field_ids = (project_number, project_id, type_field_id, priority_field_id)
        error_info = (context_error, fields_errors)
        errors = validate_project_setup(
            data.get("items", []), field_ids, fields_data, error_info,
        )
        _fail_if_errors(errors)

        sys.stdout.write("Processing and creating issues...\n")
        project_info = (
            project_number, project_id, type_field_id, priority_field_id, fields_data,
        )
        for item in data.get("items", []):
            _create_issue_recursive(
                item, None, owner or "", project_info,
            )

        sys.stdout.write("Successfully created all issues.\n")
    finally:
        with contextlib.suppress(OSError):
            json_file_path.unlink()


if __name__ == "__main__":
    main()
