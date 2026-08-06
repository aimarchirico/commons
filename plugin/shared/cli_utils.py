"""Shared CLI execution and dependency verification utilities for plugin skills."""

import shutil
import subprocess
import sys


def run_cmd(args: list[str], input_text: str | None = None) -> str:
    """Execute a shell command via subprocess and return stripped output."""
    result = subprocess.run(
        args,
        input=input_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return result.stdout.strip()


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
