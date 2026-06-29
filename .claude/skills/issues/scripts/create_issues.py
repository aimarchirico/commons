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
        print("Error: GitHub CLI (gh) is not installed or not in PATH.", file=sys.stderr)
        sys.exit(1)

    # Check gh auth status
    try:
        subprocess.run(["gh", "auth", "status"], capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("Error: GitHub CLI is not authenticated. Please run 'gh auth login' first.", file=sys.stderr)
        sys.exit(1)

    # Check/install gh-sub-issue extension
    try:
        output = run_cmd(["gh", "extension", "list"])
        if "gh-sub-issue" not in output:
            print("Installing gh-sub-issue extension...")
            subprocess.run(["gh", "extension", "install", "yahsan2/gh-sub-issue"], check=True)
    except Exception as e:
        print(f"Warning: Error verifying or installing gh-sub-issue: {e}", file=sys.stderr)

def get_project_context():
    try:
        repo_output = run_cmd(["gh", "repo", "view", "--json", "owner,name"])
        repo_data = json.loads(repo_output)
        owner = repo_data["owner"]["login"]
        repo_name = repo_data["name"]
    except Exception as e:
        print(f"Error: Could not retrieve GitHub repository context. {e}", file=sys.stderr)
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
        linked_projects = api_data.get("data", {}).get("repository", {}).get("projectsV2", {}).get("nodes", [])
        
        # Filter for open projects
        open_projects = [p for p in linked_projects if not p.get("closed", False)]
        if open_projects:
            # Prefer the first open linked project
            proj = open_projects[0]
            project_number = proj["number"]
            project_id = proj["id"]
            print(f"Found active linked project: '{proj.get('title')}' (number: {project_number}, id: {project_id})")
            return owner, project_number, project_id
    except Exception as e:
        print(f"Warning: Error querying linked projects via GraphQL. {e}", file=sys.stderr)

    print("No active linked projects found. Skipping project field setup.")
    return owner, None, None

def get_project_fields(owner, project_number):
    type_field_id = None
    priority_field_id = None
    fields_data = {}

    if not project_number:
        return type_field_id, priority_field_id, fields_data

    try:
        fields_output = run_cmd(["gh", "project", "field-list", str(project_number), "--owner", owner, "--format", "json"])
        fields_data = json.loads(fields_output)
        for field in fields_data.get("fields", []):
            if field.get("name") == "Type":
                type_field_id = field["id"]
            elif field.get("name") == "Priority":
                priority_field_id = field["id"]
    except Exception as e:
        print(f"Warning: Could not retrieve project fields. {e}", file=sys.stderr)

    return type_field_id, priority_field_id, fields_data

def create_issue_recursive(item, parent_id, owner, project_number, project_id, type_field_id, priority_field_id, fields_data):
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
        args = ["gh", "sub-issue", "create", "--title", title, "--body", body, "--parent", str(parent_id)]
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
            item_output = run_cmd(["gh", "project", "item-add", str(project_number), "--owner", owner, "--url", issue_url, "--format", "json"])
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
                        run_cmd(["gh", "project", "item-edit", "--id", item_id, "--project-id", project_id, "--field-id", type_field_id, "--single-select-option-id", option_id])

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
                        run_cmd(["gh", "project", "item-edit", "--id", item_id, "--project-id", project_id, "--field-id", priority_field_id, "--single-select-option-id", option_id])
        except Exception as e:
            print(f"Warning: Failed to add/configure project fields for issue {issue_id}. {e}", file=sys.stderr)

    # Recurse for children
    for child in item.get("children", []):
        create_issue_recursive(child, issue_id, owner, project_number, project_id, type_field_id, priority_field_id, fields_data)

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
        owner, project_number, project_id = get_project_context()
        type_field_id, priority_field_id, fields_data = get_project_fields(owner, project_number)

        print("Processing and creating issues...")
        for item in data.get("items", []):
            create_issue_recursive(item, None, owner, project_number, project_id, type_field_id, priority_field_id, fields_data)

        print("Successfully created all issues.")
    finally:
        try:
            os.remove(json_file)
        except Exception:
            pass

if __name__ == "__main__":
    main()
