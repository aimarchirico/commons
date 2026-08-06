"""Shared GitHub Project preflight validation utility."""

import json
import shutil
import subprocess
import sys
from collections.abc import Callable
from typing import Any

SINGLE_MATCH = 1


class ProjectPreflightError(Exception):
    """Exception raised when project preflight validation fails."""


def _title_case_repo_name(repo_name: str) -> str:
    words = repo_name.replace("_", "-").split("-")
    return " ".join(word.capitalize() for word in words if word)


def check_cli_dependencies() -> None:
    """Verify gh CLI is installed and authenticated."""
    if not (gh_bin := shutil.which("gh")):
        sys.stderr.write("Error: GitHub CLI (gh) is not installed or not in PATH.\n")
        sys.exit(1)
    try:
        subprocess.run([gh_bin, "auth", "status"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, OSError):
        sys.stderr.write(
            "Error: GitHub CLI is not authenticated. "
            "Please run 'gh auth login' first.\n",
        )
        sys.exit(1)


def resolve_project_context(
    run_cmd: Callable[..., str],
) -> tuple[str, str, int, str, str]:
    """Fetch repo owner/name and resolve linked active GitHub Project (v2)."""
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
        msg = f"Could not retrieve GitHub repository context: {e}"
        raise ProjectPreflightError(msg) from e

    query = (
        "query($owner: String!, $name: String!) { repository(owner: $owner, name: "
        "$name) { projectsV2(first: 10) { nodes { id number title closed owner { "
        "... on User { login } ... on Organization { login } } } } } }"
    )

    try:
        api_output = run_cmd(
            [
                "gh",
                "api",
                "graphql",
                "-f",
                f"owner={owner}",
                "-f",
                f"name={repo_name}",
                "-f",
                f"query={query}",
            ],
        )
        api_data = json.loads(api_output)
        repository = api_data.get("data", {}).get("repository", {})
        nodes = repository.get("projectsV2", {}).get("nodes", [])
        open_projects = [p for p in nodes if not p.get("closed", False)]
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
        msg = f"Could not query linked GitHub Projects: {e}"
        raise ProjectPreflightError(msg) from e

    if not open_projects:
        msg = "No active project linked to this repository."
        raise ProjectPreflightError(msg)

    if len(open_projects) > SINGLE_MATCH:
        expected_title = _title_case_repo_name(repo_name)
        matches = [p for p in open_projects if p.get("title") == expected_title]
        if len(matches) == SINGLE_MATCH:
            proj = matches[0]
            project_owner = str(proj.get("owner", {}).get("login", owner))
            return (
                owner,
                repo_name,
                int(proj["number"]),
                str(proj.get("id", "")),
                project_owner,
            )

        project_list = "\n".join(
            f"  - {p.get('title')} (number: {p['number']})" for p in open_projects
        )
        msg = (
            f"Multiple active projects linked to '{owner}/{repo_name}', "
            f"and none (or more than one) is titled '{expected_title}' to "
            "disambiguate:\n"
            f"{project_list}"
        )
        raise ProjectPreflightError(msg)

    proj = open_projects[0]
    project_owner = str(proj.get("owner", {}).get("login", owner))
    return owner, repo_name, int(proj["number"]), str(proj.get("id", "")), project_owner


def fetch_project_fields(
    run_cmd: Callable[..., str],
    owner: str,
    project_number: int,
) -> tuple[str | None, str | None, dict[str, Any], list[str]]:
    """Retrieve Type and Priority field IDs and metadata for a project."""
    type_field_id = None
    priority_field_id = None
    fields_data = {}
    errors = []

    try:
        fields_output = run_cmd(
            [
                "gh",
                "project",
                "field-list",
                str(project_number),
                "--owner",
                owner,
                "--format",
                "json",
            ],
        )
        fields_data = json.loads(fields_output)
        type_opts = []
        priority_opts = []
        for field in fields_data.get("fields", []):
            if field.get("name") == "Type":
                type_field_id = field["id"]
                type_opts = field.get("options", [])
            elif field.get("name") == "Priority":
                priority_field_id = field["id"]
                priority_opts = field.get("options", [])
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
        errors.append(f"Could not retrieve project fields: {e}")

    if type_field_id is None:
        errors.append("Project is missing required 'Type' field.")
    elif not type_opts:
        errors.append("Project 'Type' field has no options configured.")

    if priority_field_id is None:
        errors.append("Project is missing required 'Priority' field.")
    elif not priority_opts:
        errors.append("Project 'Priority' field has no options configured.")

    return type_field_id, priority_field_id, fields_data, errors


ALLOWED_TOP_LEVEL_TYPES = {"Epic", "Story", "Task", "Bug"}
ALLOWED_CHILD_TYPES = {
    "Epic": {"Story", "Task", "Bug"},
    "Story": {"Subtask"},
    "Task": {"Subtask"},
    "Bug": {"Subtask"},
    "Subtask": set(),
}


def validate_issue_hierarchy(items: list[dict[str, Any]]) -> list[str]:
    """Validate issue type hierarchy against Jira/CONTRIBUTING.md rules."""
    errors: list[str] = []

    def validate_node(item: dict[str, Any], parent_type: str | None) -> None:
        title = item.get("title", "<untitled>")
        item_type = item.get("type")

        if parent_type is None:
            if item_type == "Subtask":
                msg = f"Subtask '{title}' cannot be a top-level issue without a parent."
                errors.append(msg)
            elif item_type and item_type not in ALLOWED_TOP_LEVEL_TYPES:
                msg = (
                    f"Issue type '{item_type}' for '{title}' is "
                    "not allowed at top level."
                )
                errors.append(msg)
        else:
            allowed = ALLOWED_CHILD_TYPES.get(parent_type, set())
            if item_type and item_type not in allowed:
                if parent_type == "Subtask":
                    msg = (
                        f"Subtask '{parent_type}' cannot contain "
                        f"child issues ('{title}')."
                    )
                    errors.append(msg)
                else:
                    arr_str = f"{sorted(allowed)}"
                    msg = (
                        f"Issue '{title}' of type '{item_type}' cannot "
                        f"be a child of '{parent_type}'. Allowed child "
                        f"types for '{parent_type}': {arr_str}."
                    )
                    errors.append(msg)

        children = item.get("children", [])
        for child in children:
            validate_node(child, item_type)

    for top_item in items:
        validate_node(top_item, None)

    return errors


def validate_item_options(
    items: list[dict[str, Any]],
    fields_data: dict[str, Any],
) -> list[str]:
    """Validate that issue type and priority values in items match project options."""
    errors: list[str] = validate_issue_hierarchy(items)
    types_used, priorities_used = set(), set()

    def walk(item_list: list[dict[str, Any]]) -> None:
        for item in item_list:
            if type_val := item.get("type"):
                types_used.add(type_val)
            if priority_val := item.get("priority"):
                priorities_used.add(priority_val)
            walk(item.get("children", []))

    walk(items)
    for f_name, vals in (("Type", types_used), ("Priority", priorities_used)):
        avail = {
            opt["name"]
            for f in fields_data.get("fields", [])
            if f.get("name") == f_name
            for opt in f.get("options", [])
        }
        errors.extend(
            f"{f_name} value '{v}' does not match any option in the project's "
            f"{f_name} field. Available: {sorted(avail)}."
            for v in sorted(vals)
            if v not in avail
        )
    return errors


def run_project_preflight(
    run_cmd: Callable[..., str],
    *,
    require_fields: bool = True,
) -> dict[str, Any]:
    """Run CLI, project resolution, and field preflight validation."""
    check_cli_dependencies()
    try:
        ctx = resolve_project_context(run_cmd)
    except ProjectPreflightError as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)

    owner, repo_name, project_number, project_id, project_owner = ctx
    t_id, p_id, fields_data = None, None, {}

    if require_fields:
        t_id, p_id, fields_data, field_errors = fetch_project_fields(
            run_cmd,
            project_owner,
            project_number,
        )
        if field_errors:
            err_msg = (
                "Error: GitHub project setup is incomplete. "
                f"Found {len(field_errors)} problem(s):\n"
                + "".join(f"  - {err}\n" for err in field_errors)
            )
            sys.stderr.write(err_msg)
            sys.exit(1)

    return {
        "owner": owner,
        "repo_name": repo_name,
        "project_number": project_number,
        "project_id": project_id,
        "project_owner": project_owner,
        "type_field_id": t_id,
        "priority_field_id": p_id,
        "fields_data": fields_data,
    }
