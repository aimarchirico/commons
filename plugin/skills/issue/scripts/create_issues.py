#!/usr/bin/env python3
import sys
import os
import json
import subprocess
import shutil

def run_cmd(args):
    result = subprocess.run(args, capture_output=True, text=True, check=True)
    return result.stdout.strip()

def check_dependencies():
    if not shutil.which("gh"):
        print(
            "Error: GitHub CLI (gh) is not installed or not in PATH.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Check gh auth status
    try:
        subprocess.run(["gh", "auth", "status"], capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print(
            "Error: GitHub CLI is not authenticated. Please run 'gh auth login' first.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Check/install gh-sub-issue extension
    try:
        output = run_cmd(["gh", "extension", "list"])
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

def get_project_context():
    try:
        repo_output = run_cmd(["gh", "repo", "view", "--json", "owner,name"])
        repo_data = json.loads(repo_output)
        owner = repo_data["owner"]["login"]
        repo_name = repo_data["name"]
    except Exception as e:
        print(
            f"Error: Could not retrieve GitHub repository context. {e}",
            file=sys.stderr,
        )
        sys.exit(1)

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
            "-f", f"query={query}"
        ])
        api_data = json.loads(api_output)
        repository = api_data.get("data", {}).get("repository", {})
        linked_projects = repository.get("projectsV2", {}).get("nodes", [])

        # Filter for open projects
        open_projects = [p for p in linked_projects if not p.get("closed", False)]
        if open_projects:
            # Prefer the first open linked project
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

def get_project_fields(owner, project_number):
    type_field_id = None
    priority_field_id = None
    fields_data = {}
    errors = []

    if not project_number:
        return type_field_id, priority_field_id, fields_data, errors

    try:
        fields_output = run_cmd([
            "gh", "project", "field-list", str(project_number),
            "--owner", owner, "--format", "json"
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

def collect_issue_type_priority_values(items):
    types_used = set()
    priorities_used = set()

    def walk(item_list):
        for item in item_list:
            type_val = item.get("type")
            priority_val = item.get("priority")
            if type_val:
                types_used.add(type_val)
            if priority_val:
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
    errors = []

    if context_error is not None:
        errors.append(context_error)

    if project_number is not None:
        errors.extend(fields_errors)

    types_used, priorities_used = collect_issue_type_priority_values(items)

    if type_field_id is not None:
        available = {
            opt["name"]
            for field in fields_data.get("fields", [])
            if field.get("name") == "Type"
            for opt in field.get("options", [])
        }
        for t in types_used:
            if t not in available:
                errors.append(
                    f"Type value '{t}' does not match any option in the "
                    f"project's Type field. Available: {sorted(available)}."
                )

    if priority_field_id is not None:
        available = {
            opt["name"]
            for field in fields_data.get("fields", [])
            if field.get("name") == "Priority"
            for opt in field.get("options", [])
        }
        for p in priorities_used:
            if p not in available:
                errors.append(
                    f"Priority value '{p}' does not match any option in the "
                    f"project's Priority field. Available: {sorted(available)}."
                )

    return errors

def fail_if_errors(errors):
    if errors:
        print(
            f"Error: GitHub project setup is incomplete. Found {len(errors)} "
            "problem(s):",
            file=sys.stderr,
        )
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

def create_issue_recursive(
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

    # Create issue
    if not parent_id:
        print(f"Creating top-level issue: '{title}'...")
        args = ["gh", "issue", "create", "--title", title, "--body", body]
        issue_url_raw = run_cmd(args)
    else:
        print(f"Creating child issue: '{title}' under parent {parent_id}...")
        args = [
            "gh", "sub-issue", "create",
            "--title", title,
            "--body", body,
            "--parent", str(parent_id)
        ]
        issue_url_raw = run_cmd(args)

    issue_url = None
    for word in issue_url_raw.split():
        if word.startswith("http://") or word.startswith("https://"):
            issue_url = word
            break
    if not issue_url:
        issue_url = issue_url_raw

    issue_id = issue_url.split("/")[-1]
    if not parent_id:
        print(f"Created top-level issue: {issue_id}")
    else:
        print(f"Created child issue: {issue_id}")

    # Add to project and configure fields
    if project_id and issue_url:
        try:
            print(f"Adding issue {issue_id} to project #{project_number}...")
            item_output = run_cmd([
                "gh", "project", "item-add", str(project_number),
                "--owner", owner, "--url", issue_url, "--format", "json"
            ])
            item_data = json.loads(item_output)
            item_id = item_data.get("id")

            if item_id:
                # Set Type field if defined
                if type_val and type_field_id:
                    option_id = None
                    for field in fields_data.get("fields", []):
                        if field.get("name") == "Type":
                            for opt in field.get("options", []):
                                if opt.get("name") == type_val:
                                    option_id = opt["id"]
                                    break
                    if option_id:
                        print(f"Setting project item Type to '{type_val}'...")
                        run_cmd([
                            "gh", "project", "item-edit",
                            "--id", item_id,
                            "--project-id", project_id,
                            "--field-id", type_field_id,
                            "--single-select-option-id", option_id
                        ])

                # Set Priority field if defined
                if priority_val and priority_field_id:
                    option_id = None
                    for field in fields_data.get("fields", []):
                        if field.get("name") == "Priority":
                            for opt in field.get("options", []):
                                if opt.get("name") == priority_val:
                                    option_id = opt["id"]
                                    break
                    if option_id:
                        print(f"Setting project item Priority to '{priority_val}'...")
                        run_cmd([
                            "gh", "project", "item-edit",
                            "--id", item_id,
                            "--project-id", project_id,
                            "--field-id", priority_field_id,
                            "--single-select-option-id", option_id
                        ])
        except Exception as e:
            print(
                "Warning: Failed to add/configure project fields for "
                f"issue {issue_id}. {e}",
                file=sys.stderr,
            )

    # Recurse for children
    for child in item.get("children", []):
        create_issue_recursive(
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
        # Delete temporary file before exiting
        try:
            os.remove(json_file)
        except Exception:
            pass
        sys.exit(1)

    # Ensure the temporary file is deleted on script exit
    try:
        check_dependencies()
        owner, project_number, project_id, context_error = get_project_context()
        type_field_id, priority_field_id, fields_data, fields_errors = (
            get_project_fields(owner, project_number)
        )
        errors = validate_project_setup(
            data.get("items", []), project_number, project_id,
            type_field_id, priority_field_id, fields_data,
            context_error, fields_errors,
        )
        fail_if_errors(errors)

        print("Processing and creating issues...")
        for item in data.get("items", []):
            create_issue_recursive(
                item,
                None,
                owner,
                project_number,
                project_id,
                type_field_id,
                priority_field_id,
                fields_data,
            )

        print("Successfully created all issues.")
    finally:
        try:
            os.remove(json_file)
        except Exception:
            pass

if __name__ == "__main__":
    main()
