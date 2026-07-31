#!/usr/bin/env python3
"""Helper utilities for querying and validating GitHub Projects (v2)."""

import json


def _title_case_repo_name(repo_name):
    """Convert a hyphen/underscore repo name to Title Case ('my-repo' -> 'My Repo')."""
    words = repo_name.replace("_", "-").split("-")
    return " ".join(word.capitalize() for word in words if word)


def get_project_context(run_cmd):
    """Fetch repository context and query linked active GitHub Projects."""
    try:
        repo_output = run_cmd(["gh", "repo", "view", "--json", "owner,name"])
        repo_data = json.loads(repo_output)
        owner = repo_data["owner"]["login"]
        repo_name = repo_data["name"]
    except Exception as e:
        return None, None, None, f"Could not retrieve GitHub repository context: {e}"

    print(f"Checking for projects linked to repository '{owner}/{repo_name}'...")
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

        if len(open_projects) > 1:
            expected_title = _title_case_repo_name(repo_name)
            matches = [p for p in open_projects if p.get("title") == expected_title]

            if len(matches) == 1:
                proj = matches[0]
                project_number = proj["number"]
                project_id = proj["id"]
                print(
                    "Multiple active projects linked; auto-selected "
                    f"'{proj.get('title')}' matching the repository name "
                    f"(number: {project_number}, id: {project_id})"
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
            project_number = proj["number"]
            project_id = proj["id"]
            print(
                f"Found active linked project: '{proj.get('title')}' "
                f"(number: {project_number}, id: {project_id})"
            )
            return owner, project_number, project_id, None
    except Exception as e:
        return owner, None, None, f"Error querying linked projects: {e}"

    return owner, None, None, "No active project linked to this repository."


def get_project_fields(run_cmd, owner, project_number):
    """Retrieve Type and Priority field IDs and metadata for a project."""
    type_field_id = None
    priority_field_id = None
    fields_data = {}
    errors = []

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
    except Exception as e:
        errors.append(f"Could not retrieve project fields: {e}")

    if type_field_id is None:
        errors.append("Project is missing required 'Type' field.")
    if priority_field_id is None:
        errors.append("Project is missing required 'Priority' field.")

    return type_field_id, priority_field_id, fields_data, errors


def _collect_issue_type_priority_values(items):
    types_used = set()
    priorities_used = set()

    def walk(item_list):
        for item in item_list:
            if type_val := item.get("type"):
                types_used.add(type_val)
            if priority_val := item.get("priority"):
                priorities_used.add(priority_val)
            walk(item.get("children", []))

    walk(items)
    return types_used, priorities_used


def validate_project_setup(
    items,
    project_number,
    project_id,
    type_field_id,
    priority_field_id,
    fields_data,
    context_error,
    fields_errors,
):
    """Validate project setup and ensure issue type/priority options exist."""
    errors = []

    if context_error is not None:
        errors.append(context_error)

    if project_number is not None:
        errors.extend(fields_errors)

    types_used, priorities_used = _collect_issue_type_priority_values(items)

    def check_options(field_name, field_id, values):
        if field_id is None:
            return
        available = {
            opt["name"]
            for field in fields_data.get("fields", [])
            if field.get("name") == field_name
            for opt in field.get("options", [])
        }
        for val in values:
            if val not in available:
                errors.append(
                    f"{field_name} value '{val}' does not match any option in the "
                    f"project's {field_name} field. Available: {sorted(available)}."
                )

    check_options("Type", type_field_id, types_used)
    check_options("Priority", priority_field_id, priorities_used)

    return errors


def set_project_field(
    run_cmd, item_id, project_id, field_name, field_id, val, fields_data
):
    """Set a single-select custom field option on a project item."""
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
        print(f"Setting project item {field_name} to '{val}'...")
        run_cmd([
            "gh", "project", "item-edit",
            "--id", item_id,
            "--project-id", project_id,
            "--field-id", field_id,
            "--single-select-option-id", option_id,
        ])
