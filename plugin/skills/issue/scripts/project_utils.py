#!/usr/bin/env python3
"""Helper utilities for querying and validating GitHub Projects (v2)."""

import json
import subprocess
import sys
from collections.abc import Callable
from typing import Any

MAX_PROJECTS = 10
SINGLE_MATCH = 1


def _title_case_repo_name(repo_name: str) -> str:
    words = repo_name.replace("_", "-").split("-")
    return " ".join(word.capitalize() for word in words if word)


def get_project_context(
    run_cmd: Callable[..., str],
) -> tuple[str | None, int | None, str | None, str | None]:
    """Fetch repository context and query linked active GitHub Projects."""
    try:
        repo_output = run_cmd(["gh", "repo", "view", "--json", "owner,name"])
        repo_data = json.loads(repo_output)
        owner = str(repo_data["owner"]["login"])
        repo_name = str(repo_data["name"])
    except (
        subprocess.CalledProcessError,
        json.JSONDecodeError,
        KeyError,
        TypeError,
    ) as e:
        return None, None, None, f"Could not retrieve GitHub repository context: {e}"

    sys.stdout.write(
        f"Checking for projects linked to repository '{owner}/{repo_name}'...\n",
    )
    try:
        query = """
        query($owner: String!, $name: String!) {
          repository(owner: $owner, name: $name) {
            projectsV2(first: 10) {
              nodes {
                id
                number
                title
                closed
              }
            }
          }
        }
        """
        api_output = run_cmd([
            "gh", "api", "graphql",
            "-f", f"owner={owner}",
            "-f", f"name={repo_name}",
            "-f", f"query={query}",
        ])
        api_data = json.loads(api_output)
        repository = api_data.get("data", {}).get("repository", {})
        linked_projects = repository.get("projectsV2", {}).get("nodes", [])
        open_projects = [p for p in linked_projects if not p.get("closed", False)]

        if len(open_projects) > SINGLE_MATCH:
            expected_title = _title_case_repo_name(repo_name)
            matches = [p for p in open_projects if p.get("title") == expected_title]

            if len(matches) == SINGLE_MATCH:
                proj = matches[0]
                project_number = int(proj["number"])
                project_id = str(proj["id"])
                sys.stdout.write(
                    "Multiple active projects linked; auto-selected "
                    f"'{proj.get('title')}' matching the repository name "
                    f"(number: {project_number}, id: {project_id})\n",
                )
                return owner, project_number, project_id, None

            project_list = "\n".join(
                f"  - {p.get('title')} (number: {p['number']})"
                for p in open_projects
            )
            return owner, None, None, (
                f"Multiple active projects linked to '{owner}/{repo_name}', and none "
                f"(or more than one) is titled '{expected_title}' to disambiguate:\n"
                f"{project_list}\n"
                f"Rename the intended project to '{expected_title}', or close/unlink "
                "the extras."
            )

        if open_projects:
            proj = open_projects[0]
            project_number = int(proj["number"])
            project_id = str(proj["id"])
            sys.stdout.write(
                f"Found active linked project: '{proj.get('title')}' "
                f"(number: {project_number}, id: {project_id})\n",
            )
            return owner, project_number, project_id, None
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
        return owner, None, None, f"Error querying linked projects: {e}"

    return owner, None, None, "No active project linked to this repository."


def get_project_fields(
    run_cmd: Callable[..., str], owner: str, project_number: int | None,
) -> tuple[str | None, str | None, dict[str, Any], list[str]]:
    """Retrieve Type and Priority field IDs and metadata for a project."""
    type_field_id: str | None = None
    priority_field_id: str | None = None
    fields_data: dict[str, Any] = {}
    errors: list[str] = []

    if not project_number:
        return type_field_id, priority_field_id, fields_data, errors

    try:
        fields_output = run_cmd([
            "gh", "project", "field-list", str(project_number),
            "--owner", owner, "--format", "json",
        ])
        fields_data = json.loads(fields_output)
        for field in fields_data.get("fields", []):
            if field.get("name") == "Type":
                type_field_id = field["id"]
            elif field.get("name") == "Priority":
                priority_field_id = field["id"]
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
        errors.append(f"Could not retrieve project fields: {e}")

    if type_field_id is None:
        errors.append("Project is missing required 'Type' field.")
    if priority_field_id is None:
        errors.append("Project is missing required 'Priority' field.")

    return type_field_id, priority_field_id, fields_data, errors


def _collect_issue_type_priority_values(
    items: list[dict[str, Any]],
) -> tuple[set[str], set[str]]:
    types_used: set[str] = set()
    priorities_used: set[str] = set()

    def walk(item_list: list[dict[str, Any]]) -> None:
        for item in item_list:
            if type_val := item.get("type"):
                types_used.add(type_val)
            if priority_val := item.get("priority"):
                priorities_used.add(priority_val)
            walk(item.get("children", []))

    walk(items)
    return types_used, priorities_used


def validate_project_setup(
    items: list[dict[str, Any]],
    field_ids: tuple[int | None, str | None, str | None, str | None],
    fields_data: dict[str, Any],
    error_info: tuple[str | None, list[str]],
) -> list[str]:
    """Validate project setup and ensure issue type/priority options exist."""
    project_number, _project_id, type_field_id, priority_field_id = field_ids
    context_error, fields_errors = error_info
    errors: list[str] = []

    if context_error is not None:
        errors.append(context_error)

    if project_number is not None:
        errors.extend(fields_errors)

    types_used, priorities_used = _collect_issue_type_priority_values(items)

    def check_options(
        field_name: str, field_id: str | None, values: set[str],
    ) -> None:
        if field_id is None:
            return
        available = {
            opt["name"]
            for field in fields_data.get("fields", [])
            if field.get("name") == field_name
            for opt in field.get("options", [])
        }
        errors.extend(
            f"{field_name} value '{val}' does not match any option in the "
            f"project's {field_name} field. Available: {sorted(available)}."
            for val in values
            if val not in available
        )

    check_options("Type", type_field_id, types_used)
    check_options("Priority", priority_field_id, priorities_used)

    return errors


def set_project_field(
    run_cmd: Callable[..., str],
    item_id: str,
    project_id: str,
    field_target: tuple[str, str | None, str | None],
    fields_data: dict[str, Any],
) -> None:
    """Set a single-select custom field option on a project item."""
    field_name, field_id, val = field_target
    if not (val and field_id):
        return

    option_id = None
    for field in fields_data.get("fields", []):
        if field.get("name") == field_name:
            for opt in field.get("options", []):
                if opt.get("name") == val:
                    option_id = opt["id"]
                    break

    if option_id:
        sys.stdout.write(f"Setting project item {field_name} to '{val}'...\n")
        run_cmd([
            "gh", "project", "item-edit",
            "--id", item_id,
            "--project-id", project_id,
            "--field-id", field_id,
            "--single-select-option-id", option_id,
        ])
