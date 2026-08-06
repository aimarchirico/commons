#!/usr/bin/env python3
"""Script for resolving issue target base branch from GitHub blockedBy."""

import importlib.util
import json
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Any

MIN_ARG_COUNT = 2


def _load_blocking_prs() -> ModuleType:
    shared_dir = Path(__file__).resolve().parent.parent.parent.parent / "shared"
    module_path = shared_dir / "blocking_prs.py"
    spec = importlib.util.spec_from_file_location("blocking_prs", module_path)
    if spec is None or spec.loader is None:
        msg = f"Cannot load blocking_prs from {module_path}"
        raise ImportError(msg)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_blocking_prs = _load_blocking_prs()
fetch_issue_dependencies = _blocking_prs.fetch_issue_dependencies


def _run_cmd(args: list[str]) -> str:
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return result.stdout.strip()


def _load_project_preflight() -> ModuleType:
    shared_dir = Path(__file__).resolve().parent.parent.parent.parent / "shared"
    module_path = shared_dir / "project_preflight.py"
    spec = importlib.util.spec_from_file_location("project_preflight", module_path)
    if spec is None or spec.loader is None:
        msg = f"Cannot load project_preflight from {module_path}"
        raise ImportError(msg)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_project_preflight = _load_project_preflight()
project_preflight = _project_preflight
check_cli_dependencies = _project_preflight.check_cli_dependencies


def get_issue_base_branch(
    run_cmd: Callable[[list[str]], str],
    issue_id: str,
) -> dict[str, Any]:
    """Determine base branch candidates for a given issue ID.

    Returns a dict containing:
    - default_branch: str
    - status: "default" | "single" | "multiple"
    - base_branch: str | None
    - candidates: list of candidate PR dicts
    """
    repo_output = run_cmd(
        ["gh", "repo", "view", "--json", "owner,name,defaultBranchRef"],
    )
    repo_data = json.loads(repo_output)
    owner = repo_data["owner"]["login"]
    repo_name = repo_data["name"]
    default_branch = repo_data.get("defaultBranchRef", {}).get("name") or "main"

    try:
        deps = fetch_issue_dependencies(run_cmd, owner, repo_name, int(issue_id))
    except (
        subprocess.CalledProcessError,
        json.JSONDecodeError,
        ValueError,
        KeyError,
        AttributeError,
    ):
        return {
            "default_branch": default_branch,
            "status": "default",
            "base_branch": default_branch,
            "candidates": [],
        }

    open_pr_candidates = []
    seen_branches = set()

    for item in deps.get("blocked_by", []):
        pr = item.get("open_pr")
        if pr and pr["branch_name"] not in seen_branches:
            seen_branches.add(pr["branch_name"])
            open_pr_candidates.append(
                {
                    "issue_number": item["number"],
                    "pr_number": pr["number"],
                    "pr_title": pr["title"],
                    "branch_name": pr["branch_name"],
                    "is_draft": pr["is_draft"],
                },
            )

    if not open_pr_candidates:
        return {
            "default_branch": default_branch,
            "status": "default",
            "base_branch": default_branch,
            "candidates": [],
        }
    if len(open_pr_candidates) == 1:
        return {
            "default_branch": default_branch,
            "status": "single",
            "base_branch": open_pr_candidates[0]["branch_name"],
            "candidates": open_pr_candidates,
        }

    return {
        "default_branch": default_branch,
        "status": "multiple",
        "base_branch": None,
        "candidates": open_pr_candidates,
    }


def main() -> None:
    """Main entry point for resolving an issue's base branch from the CLI."""
    if len(sys.argv) < MIN_ARG_COUNT:
        sys.stderr.write("Error: Issue ID not specified.\n")
        sys.stderr.write(f"Usage: {sys.argv[0]} <issue-id> [--json]\n")
        sys.exit(1)

    issue_id = sys.argv[1]
    output_json = "--json" in sys.argv

    check_cli_dependencies()

    try:
        res = get_issue_base_branch(_run_cmd, issue_id)
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
        sys.stderr.write(f"Error: Failed to fetch base branch info. {e}\n")
        sys.exit(1)

    if output_json or res["status"] == "multiple":
        sys.stdout.write(f"{json.dumps(res, indent=2)}\n")
    else:
        sys.stdout.write(f"{res['base_branch']}\n")


if __name__ == "__main__":
    main()
