#!/usr/bin/env python3
"""Helper utilities for fetching PR blocking problems (conflicts, checks, feedback)."""

import json
import subprocess
from collections.abc import Callable
from typing import Any


def fetch_conflicting(run_cmd: Callable[[list[str]], str], pr_number: str) -> bool:
    """Check if PR has merge conflicts with base branch."""
    output = run_cmd(["gh", "pr", "view", pr_number, "--json", "mergeable"])
    return bool(json.loads(output)["mergeable"] == "CONFLICTING")


def fetch_failing_checks(
    run_cmd: Callable[[list[str]], str],
    pr_number: str,
) -> list[dict[str, str]]:
    """Fetch list of failing status checks on PR."""
    try:
        output = run_cmd(
            [
                "gh",
                "pr",
                "checks",
                pr_number,
                "--json",
                "name,bucket,link",
            ],
        )
    except subprocess.CalledProcessError:
        return []
    checks = json.loads(output) if output else []
    return [
        {"name": c["name"], "link": c["link"]}
        for c in checks
        if c.get("bucket") == "fail"
    ]
