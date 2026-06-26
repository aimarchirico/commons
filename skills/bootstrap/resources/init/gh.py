import subprocess
import json
import shutil

def run_cmd(args):
    result = subprocess.run(args, capture_output=True, text=True, check=True)
    return result.stdout.strip()

def get_github_context():
    try:
        output = run_cmd(["gh", "repo", "view", "--json", "owner,name"])
        data = json.loads(output)
        owner = data.get("owner", {}).get("login")
        repo = data.get("name")
        return owner, repo
    except Exception as e:
        print(f"Warning: Could not determine GitHub repository context. Error: {e}")
        return None, None

def setup_github_project(project_title):
    if not shutil.which("gh"):
        print("Warning: GitHub CLI 'gh' is not installed or not in PATH. Skipping GitHub Project initialization.")
        return

    owner, repo = get_github_context()
    if not owner or not repo:
        print("Warning: Skipping GitHub Project initialization due to missing repo context.")
        return

    print(f"Initializing GitHub Project for owner: {owner}, repo: {repo}")

    try:
        print(f"Creating new GitHub Project: '{project_title}'...")
        output = run_cmd(["gh", "project", "create", "--owner", owner, "--title", project_title, "--format", "json"])
        proj_data = json.loads(output)
        project_number = proj_data.get("number")
        print(f"Successfully created GitHub Project #{project_number}")
    except Exception as e:
        print(f"Error: Failed to create GitHub Project. Error: {e}")
        return

    # Link the project to the repository
    try:
        print(f"Linking repository '{owner}/{repo}' to project #{project_number}...")
        run_cmd(["gh", "project", "link", str(project_number), "--owner", owner, "-R", f"{owner}/{repo}"])
        print("Successfully linked repository to project.")
    except Exception as e:
        print(f"Warning: Failed to link repository to project #{project_number}. Error: {e}")

    # Configure custom fields
    configure_fields(project_number, owner)

def configure_fields(project_number, owner):
    # Create 'Type' field
    try:
        print("Creating 'Type' custom field (Epic, Story, Task, Bug, Subtask)...")
        run_cmd([
            "gh", "project", "field-create", str(project_number),
            "--owner", owner,
            "--name", "Type",
            "--data-type", "SINGLE_SELECT",
            "--single-select-options", "Epic,Story,Task,Bug,Subtask"
        ])
        print("Successfully created 'Type' field.")
    except Exception as e:
        print(f"Warning: Failed to create 'Type' field. Error: {e}")

    # Create 'Priority' field
    try:
        print("Creating 'Priority' custom field (High, Medium, Low)...")
        run_cmd([
            "gh", "project", "field-create", str(project_number),
            "--owner", owner,
            "--name", "Priority",
            "--data-type", "SINGLE_SELECT",
            "--single-select-options", "High,Medium,Low"
        ])
        print("Successfully created 'Priority' field.")
    except Exception as e:
        print(f"Warning: Failed to create 'Priority' field. Error: {e}")

