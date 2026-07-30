#!/usr/bin/env python3
"""Script for creating GitHub issues and linking them to GitHub Projects."""

import json
import os
import shutil
import subprocess
import sys

from project_utils import (
    get_project_context,
    get_project_fields,
    set_project_field,
    validate_project_setup,
)


def _run_cmd(args):
    result = subprocess.run(args, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def _check_dependencies():
    if not shutil.which("gh"):
        print(
            "Error: GitHub CLI (gh) is not installed or not in PATH.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        subprocess.run(["gh", "auth", "status"], capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print(
            "Error: GitHub CLI is not authenticated. Please run 'gh auth login' first.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        output = _run_cmd(["gh", "extension", "list"])
        if "gh-sub-issue" not in output:
            print("Installing gh-sub-issue extension...")
            subprocess.run(
                ["gh", "extension", "install", "yahsan2/gh-sub-issue"],
                check=True,
            )
    except Exception as e:
        print(
            f"Warning: Error verifying or installing gh-sub-issue: {e}",
            file=sys.stderr,
        )


def _fail_if_errors(errors):
    if errors:
        print(
            "Error: GitHub project setup is incomplete. "
            f"Found {len(errors)} problem(s):",
            file=sys.stderr,
        )
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)


def _create_issue_recursive(
    item,
    parent_id,
    owner,
    project_number,
    project_id,
    type_field_id,
    priority_field_id,
    fields_data,
):
    title = item.get("title")
    body = item.get("body", "")
    type_val = item.get("type")
    priority_val = item.get("priority")

    if not title:
        print("Warning: Skipped creating issue due to missing title.")
        return

    if not parent_id:
        print(f"Creating top-level issue: '{title}'...")
        args = ["gh", "issue", "create", "--title", title, "--body", body]
    else:
        print(f"Creating child issue: '{title}' under parent {parent_id}...")
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
            if w.startswith("http://") or w.startswith("https://")
        ),
        issue_url_raw,
    )
    issue_id = issue_url.split("/")[-1]
    level_str = "child" if parent_id else "top-level"
    print(f"Created {level_str} issue: {issue_id}")

    if project_id and issue_url:
        try:
            print(f"Adding issue {issue_id} to project #{project_number}...")
            item_output = _run_cmd([
                "gh", "project", "item-add", str(project_number),
                "--owner", owner, "--url", issue_url, "--format", "json",
            ])
            item_data = json.loads(item_output)
            if item_id := item_data.get("id"):
                set_project_field(
                    _run_cmd, item_id, project_id, "Type",
                    type_field_id, type_val, fields_data,
                )
                set_project_field(
                    _run_cmd, item_id, project_id, "Priority",
                    priority_field_id, priority_val, fields_data,
                )
        except Exception as e:
            print(
                "Warning: Failed to add/configure project fields for issue "
                f"{issue_id}. {e}",
                file=sys.stderr,
            )

    for child in item.get("children", []):
        _create_issue_recursive(
            child,
            issue_id,
            owner,
            project_number,
            project_id,
            type_field_id,
            priority_field_id,
            fields_data,
        )


def main():
    """Main entry point for parsing input JSON and creating issues."""
    if len(sys.argv) < 2:
        print("Error: JSON file path not specified.")
        print(f"Usage: {sys.argv[0]} <path-to-issues.json>")
        sys.exit(1)

    json_file = sys.argv[1]
    if not os.path.isfile(json_file):
        print(f"Error: File '{json_file}' not found.", file=sys.stderr)
        sys.exit(1)

    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error: Failed to parse '{json_file}' as JSON. {e}", file=sys.stderr)
        try:
            os.remove(json_file)
        except Exception:
            pass
        sys.exit(1)

    try:
        _check_dependencies()
        owner, project_number, project_id, context_error = get_project_context(_run_cmd)
        type_field_id, priority_field_id, fields_data, fields_errors = (
            get_project_fields(_run_cmd, owner, project_number)
        )
        errors = validate_project_setup(
            data.get("items", []), project_number, project_id,
            type_field_id, priority_field_id, fields_data,
            context_error, fields_errors,
        )
        _fail_if_errors(errors)

        print("Processing and creating issues...")
        for item in data.get("items", []):
            _create_issue_recursive(
                item, None, owner, project_number, project_id,
                type_field_id, priority_field_id, fields_data,
            )

        print("Successfully created all issues.")
    finally:
        try:
            os.remove(json_file)
        except Exception:
            pass


if __name__ == "__main__":
    main()
