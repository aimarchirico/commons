#!/usr/bin/env python3
"""PR review utilities for requesting re-reviews on pull requests."""

import json
import sys
from collections.abc import Callable


def request_re_reviews(run_cmd: Callable[..., str], pr_number: str) -> None:
    """Request re-review from the PR's prior reviewers, excluding the user."""
    reviews_output = run_cmd(["gh", "pr", "view", pr_number, "--json", "reviews"])
    reviewers = {
        r["author"]["login"]
        for r in json.loads(reviews_output).get("reviews", [])
        if r.get("author", {}).get("login")
    }
    login = run_cmd(["gh", "api", "user", "--jq", ".login"])

    for reviewer in sorted(reviewers - {login}):
        sys.stdout.write(f"Requesting re-review from {reviewer}...\n")
        run_cmd(["gh", "pr", "edit", pr_number, "--add-reviewer", reviewer])
