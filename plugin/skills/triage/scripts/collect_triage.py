#!/usr/bin/env python3
"""Script for surveying open PRs and backlog issues relevant to the user."""

import json
import shutil
import subprocess
import sys
from collections.abc import Callable
from typing import Any

from backlog_utils import fetch_backlog_issues

SINGLE_MATCH = 1


def _run_cmd(args: list[str]) -> str:
    result = subprocess.run(args, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def _check_dependencies() -> None:
    gh_bin = shutil.which("gh")
    if not gh_bin:
        sys.stderr.write(
            "Error: GitHub CLI (gh) is not installed or not in PATH.\n",
        )
        sys.exit(1)

    try:
        subprocess.run([gh_bin, "auth", "status"], capture_output=True, check=True)
    except subprocess.CalledProcessError:
        sys.stderr.write(
            "Error: GitHub CLI is not authenticated. "
            "Please run 'gh auth login' first.\n",
        )
        sys.exit(1)


def _graphql(
    run_cmd: Callable[[list[str]], str], query: str, **variables: str | int,
) -> dict[str, Any]:
    args = ["gh", "api", "graphql"]
    for key, value in variables.items():
        args += ["-F" if isinstance(value, int) else "-f", f"{key}={value}"]
    args += ["-f", f"query={query}"]
    return dict(json.loads(run_cmd(args)))


def _get_repo_context(run_cmd: Callable[[list[str]], str]) -> tuple[str, str]:
    repo_output = run_cmd(["gh", "repo", "view", "--json", "owner,name"])
    repo_data = json.loads(repo_output)
    return str(repo_data["owner"]["login"]), str(repo_data["name"])


def _title_case_repo_name(repo_name: str) -> str:
    words = repo_name.replace("_", "-").split("-")
    return " ".join(word.capitalize() for word in words if word)


def _get_linked_project(
    run_cmd: Callable[[list[str]], str], owner: str, repo_name: str,
) -> tuple[str, int]:
    query = (
        "query($owner: String!, $name: String!) {"
        " repository(owner: $owner, name: $name) { projectsV2(first: 10) {"
        " nodes { number title closed"
        " owner { ... on User { login } ... on Organization { login } } } } } }"
    )
    api_data = _graphql(run_cmd, query, owner=owner, name=repo_name)
    nodes = (
        api_data.get("data", {}).get("repository", {})
        .get("projectsV2", {}).get("nodes", [])
    )
    open_projects = [p for p in nodes if not p.get("closed", False)]

    if not open_projects:
        sys.stderr.write(
            f"Error: No open GitHub Project linked to '{owner}/{repo_name}'.\n",
        )
        sys.exit(1)
    if len(open_projects) > SINGLE_MATCH:
        expected_title = _title_case_repo_name(repo_name)
        matches = [p for p in open_projects if p.get("title") == expected_title]
        if len(matches) != SINGLE_MATCH:
            project_list = "\n".join(
                f"  - {p.get('title')} (number: {p['number']})"
                for p in open_projects
            )
            sys.stderr.write(
                f"Error: Multiple open GitHub Projects linked to "
                f"'{owner}/{repo_name}', and none (or more than one) is titled "
                f"'{expected_title}' to disambiguate:\n{project_list}\n",
            )
            sys.exit(1)
        open_projects = matches

    project = open_projects[0]
    project_owner = str(project["owner"]["login"])
    project_number = int(project["number"])
    return project_owner, project_number


def _resolve_login(run_cmd: Callable[[list[str]], str]) -> str:
    return run_cmd(["gh", "api", "user", "--jq", ".login"])


def _fetch_prs_to_review(
    run_cmd: Callable[[list[str]], str], login: str,
) -> list[dict[str, Any]]:
    output = run_cmd([
        "gh", "pr", "list",
        "--search", "is:open -author:@me draft:false",
        "--json", "number,title,url,author,reviewRequests",
    ])
    prs = json.loads(output)

    review_requested = []
    not_requested = []
    for pr in prs:
        author = pr.get("author") or {}
        if author.get("is_bot"):
            continue
        requested_logins = {
            (r.get("login") or (r.get("requestedReviewer") or {}).get("login"))
            for r in pr.get("reviewRequests", [])
        }
        entry = {
            "number": pr["number"],
            "title": pr["title"],
            "url": pr["url"],
            "author": author.get("login"),
        }
        if login in requested_logins:
            entry["bucket"] = "review_requested"
            review_requested.append(entry)
        else:
            entry["bucket"] = "not_requested"
            not_requested.append(entry)

    return review_requested + not_requested


def _fetch_unresolved_threads(
    run_cmd: Callable[[list[str]], str], owner: str, repo_name: str, number: int,
) -> bool:
    query = (
        "query($owner: String!, $repo: String!, $number: Int!) {"
        " repository(owner: $owner, name: $repo) { pullRequest(number: $number) {"
        " reviewThreads(first: 50) { nodes { isResolved } } } } }"
    )
    api_data = _graphql(run_cmd, query, owner=owner, repo=repo_name, number=number)
    pr = api_data.get("data", {}).get("repository", {}).get("pullRequest") or {}
    threads = pr.get("reviewThreads", {}).get("nodes", [])
    return any(not t.get("isResolved") for t in threads)


def _classify_your_pr(
    *, is_draft: bool, review_decision: str | None, has_unresolved_threads: bool,
) -> str:
    if is_draft:
        return "draft"
    if review_decision == "APPROVED" and not has_unresolved_threads:
        return "approved"
    if review_decision == "APPROVED" and has_unresolved_threads:
        return "unresolved_approved"
    if review_decision != "APPROVED" and has_unresolved_threads:
        return "unresolved"
    return "no_unresolved"


def _fetch_your_prs(
    run_cmd: Callable[[list[str]], str], owner: str, repo_name: str,
) -> list[dict[str, Any]]:
    output = run_cmd([
        "gh", "pr", "list",
        "--search", "is:open author:@me",
        "--json", "number,title,url,isDraft,reviewDecision,closingIssuesReferences",
    ])
    prs = json.loads(output)

    buckets: dict[str, list[dict[str, Any]]] = {
        "approved": [],
        "unresolved_approved": [],
        "unresolved": [],
        "no_unresolved": [],
        "draft": [],
    }

    for pr in prs:
        is_draft = bool(pr.get("isDraft"))
        has_unresolved_threads = False
        if not is_draft:
            has_unresolved_threads = _fetch_unresolved_threads(
                run_cmd, owner, repo_name, pr["number"],
            )
        bucket = _classify_your_pr(
            is_draft=is_draft,
            review_decision=pr.get("reviewDecision"),
            has_unresolved_threads=has_unresolved_threads,
        )

        entry: dict[str, Any] = {
            "number": pr["number"],
            "title": pr["title"],
            "url": pr["url"],
            "is_draft": is_draft,
            "bucket": bucket,
        }
        if bucket == "draft":
            linked_issues = pr.get("closingIssuesReferences") or []
            entry["linked_issue"] = (
                {"number": linked_issues[0]["number"], "url": linked_issues[0]["url"]}
                if linked_issues
                else None
            )
        buckets[bucket].append(entry)

    return (
        buckets["approved"]
        + buckets["unresolved_approved"]
        + buckets["unresolved"]
        + buckets["no_unresolved"]
        + buckets["draft"]
    )


def main() -> None:
    """Main entry point for printing the triage survey as JSON."""
    _check_dependencies()

    try:
        owner, repo_name = _get_repo_context(_run_cmd)
        project_owner, project_number = _get_linked_project(_run_cmd, owner, repo_name)
        login = _resolve_login(_run_cmd)

        result = {
            "prs_to_review": _fetch_prs_to_review(_run_cmd, login),
            "your_prs": _fetch_your_prs(_run_cmd, owner, repo_name),
            "backlog_issues": fetch_backlog_issues(
                _run_cmd, project_owner, project_number, login,
            ),
        }
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
        sys.stderr.write(f"Error: Failed to collect triage data. {e}\n")
        sys.exit(1)

    sys.stdout.write(f"{json.dumps(result, indent=2)}\n")


if __name__ == "__main__":
    main()
