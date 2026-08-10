#!/usr/bin/env python3
"""Script for fetching an issue's full recursive title/body/type tree."""

import importlib.util
import json
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Any

MIN_ARG_COUNT = 2


def _load_module(name: str) -> ModuleType:
    shared_dir = Path(__file__).resolve().parent.parent.parent.parent / "shared"
    module_path = shared_dir / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, module_path)
    if spec is None or spec.loader is None:
        msg = f"Cannot load {name} from {module_path}"
        raise ImportError(msg)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_issue_tree = _load_module("issue_tree")
_fetch_issue_tree = _issue_tree.fetch_issue_tree

project_preflight = _load_module("project_preflight")
check_cli_dependencies = project_preflight.check_cli_dependencies


def _run_cmd(args: list[str]) -> str:
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return result.stdout.strip()


def get_issue_tree(
    run_cmd: Callable[[list[str]], str],
    issue_id: str,
) -> dict[str, Any]:
    """Resolve owner/repo and fetch the full recursive issue tree."""
    repo_output = run_cmd(["gh", "repo", "view", "--json", "owner,name"])
    repo_data = json.loads(repo_output)
    owner = repo_data["owner"]["login"]
    repo_name = repo_data["name"]
    return _fetch_issue_tree(run_cmd, owner, repo_name, int(issue_id))


def main() -> None:
    """Main entry point for fetching an issue's recursive tree from the CLI."""
    if len(sys.argv) < MIN_ARG_COUNT:
        sys.stderr.write("Error: Issue ID not specified.\n")
        sys.stderr.write(f"Usage: {sys.argv[0]} <issue-id>\n")
        sys.exit(1)

    issue_id = sys.argv[1]

    check_cli_dependencies()

    try:
        tree = get_issue_tree(_run_cmd, issue_id)
    except (
        subprocess.CalledProcessError,
        json.JSONDecodeError,
        KeyError,
        ValueError,
    ) as e:
        sys.stderr.write(f"Error: Failed to fetch issue tree. {e}\n")
        sys.exit(1)

    sys.stdout.write(f"{json.dumps(tree, indent=2)}\n")


if __name__ == "__main__":
    main()
