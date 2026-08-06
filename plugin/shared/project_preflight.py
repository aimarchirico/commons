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
    gh_bin = shutil.which("gh")
    if not gh_bin:
        sys.stderr.write(
            "Error: GitHub CLI (gh) is not installed or not in PATH.\n",
        )
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

    query = """
    query($owner: String!, $name: String!) {
      repository(owner: $owner, name: $name) {
        projectsV2(first: 10) {
          nodes {
            id
            number
            title
            closed
            owner { ... on User { login } ... on Organization { login } }
          }
        }
      }
    }
    """
    try:
        api_output = run_cmd([
            "gh", "api", "graphql",
            "-f", f"owner={owner}",
            "-f", f"name={repo_name}",
            "-f", f"query={query}",
        ])
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
                owner, repo_name, int(proj["number"]),
                str(proj.get("id", "")), project_owner,
            )

        project_list = "\n".join(
            f"  - {p.get('title')} (number: {p['number']})"
            for p in open_projects
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
    return (
        owner, repo_name, int(proj["number"]),
        str(proj.get("id", "")), project_owner,
    )


def fetch_project_fields(
    run_cmd: Callable[..., str], owner: str, project_number: int,
) -> tuple[str | None, str | None, dict[str, Any], list[str]]:
    """Retrieve Type and Priority field IDs and metadata for a project."""
    type_field_id = None
    priority_field_id = None
    fields_data = {}
    errors = []

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


def run_project_preflight(
    run_cmd: Callable[..., str],
    *,
    require_fields: bool = True,
) -> dict[str, Any]:
    """Run CLI, project resolution, and field preflight validation.

    If any validation check fails, prints structured diagnostic messages to stderr
    and exits immediately with status code 1.
    """
    check_cli_dependencies()
    try:
        ctx = resolve_project_context(run_cmd)
    except ProjectPreflightError as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)

    owner, repo_name, project_number, project_id, project_owner = ctx

    type_field_id = None
    priority_field_id = None
    fields_data = {}

    if require_fields:
        type_field_id, priority_field_id, fields_data, field_errors = (
            fetch_project_fields(run_cmd, project_owner, project_number)
        )
        if field_errors:
            sys.stderr.write(
                "Error: GitHub project setup is incomplete. "
                f"Found {len(field_errors)} problem(s):\n",
            )
            for err in field_errors:
                sys.stderr.write(f"  - {err}\n")
            sys.exit(1)

    return {
        "owner": owner,
        "repo_name": repo_name,
        "project_number": project_number,
        "project_id": project_id,
        "project_owner": project_owner,
        "type_field_id": type_field_id,
        "priority_field_id": priority_field_id,
        "fields_data": fields_data,
    }
