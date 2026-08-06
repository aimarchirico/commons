#!/usr/bin/env python3
"""Script for surveying open PRs and backlog issues relevant to the user."""

import json
import shutil
import subprocess
import sys
from collections.abc import Callable
from typing import Any

from backlog_utils import fetch_backlog_issues
from review_state import fetch_review_state

SINGLE_MATCH = 1


def _run_cmd(args: list[str]) -> str:
    result = subprocess.run(
        args, capture_output=True, text=True, encoding="utf-8", check=True,
    )
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


_PRS_TO_REVIEW_LABELS = {
    True: "Awaiting your review",
    False: "Not awaiting your review",
}


def _fetch_prs_to_review(
    run_cmd: Callable[[list[str]], str], login: str,
) -> list[dict[str, Any]]:
    output = run_cmd([
        "gh", "pr", "list",
        "--search", "is:open -author:@me draft:false",
        "--json", "number,title,url,author,reviewRequests,reviewDecision",
    ])
    prs = json.loads(output)

    awaiting = []
    not_awaiting = []
    for pr in prs:
        author = pr.get("author") or {}
        if author.get("is_bot") or pr.get("reviewDecision") == "APPROVED":
            continue
        requested_logins = {
            (r.get("login") or (r.get("requestedReviewer") or {}).get("login"))
            for r in pr.get("reviewRequests", [])
        }
        is_awaiting = login in requested_logins
        entry = {
            "number": pr["number"],
            "title": pr["title"],
            "url": pr["url"],
            "state": _PRS_TO_REVIEW_LABELS[is_awaiting],
        }
        (awaiting if is_awaiting else not_awaiting).append(entry)

    return awaiting + not_awaiting


_YOUR_PR_BUCKET_ORDER = ["merge", "resolve_then_merge", "resolve", "self_review"]

_PR_STATE_LABELS = {
    "approved": "Approved",
    "changes_requested": "Changes requested",
    "commented": "Commented",
    "no_reviews": "No reviews",
}

_THREAD_STATE_LABELS = {
    "none": "None", "resolved": "Resolved", "unresolved": "Unresolved",
}

_CHECKS_STATE_LABELS = {
    "none": "None", "passing": "Passing", "pending": "Pending", "failing": "Failing",
}

_CONFLICTING_LABELS = {True: "Yes", False: "No"}


def _bucket_for(
    state: str, threads: str, comments: str, *, conflicting: bool, checks: str,
) -> str:
    needs_resolve = (
        threads == "unresolved" or comments == "unresolved"
        or conflicting or checks == "failing"
    )
    if needs_resolve:
        return "resolve_then_merge" if state == "approved" else "resolve"
    return "merge" if state == "approved" else "self_review"


def _suggestion_for(bucket: str, pr_number: int) -> str:
    if bucket == "merge":
        return "Merge the PR"
    if bucket == "resolve_then_merge":
        return (
            f"Resolve problems with `/commons:resolve --pr {pr_number}`,"
            " then merge the PR"
        )
    if bucket == "resolve":
        return f"Resolve problems with `/commons:resolve --pr {pr_number}`"
    return f"Self-review the PR with `/commons:review --pr {pr_number}`"


def _linked_issue_for(pr: dict[str, Any]) -> dict[str, Any] | None:
    linked_issues = pr.get("closingIssuesReferences") or []
    return (
        {"number": linked_issues[0]["number"], "url": linked_issues[0]["url"]}
        if linked_issues
        else None
    )


def _fetch_open_and_draft_prs(
    run_cmd: Callable[[list[str]], str], owner: str, repo_name: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    output = run_cmd([
        "gh", "pr", "list",
        "--search", "is:open author:@me",
        "--json", "number,title,url,isDraft,closingIssuesReferences",
    ])
    prs = json.loads(output)

    your_open_prs = []
    ranks = []
    your_draft_prs = []
    for pr in prs:
        if bool(pr.get("isDraft")):
            your_draft_prs.append({
                "number": pr["number"],
                "title": pr["title"],
                "url": pr["url"],
                "linked_issue": _linked_issue_for(pr),
            })
            continue

        review_state = fetch_review_state(
            lambda query, **variables: _graphql(run_cmd, query, **variables),
            owner, repo_name, pr["number"],
        )
        bucket = _bucket_for(
            review_state["state"], review_state["threads"], review_state["comments"],
            conflicting=review_state["conflicting"], checks=review_state["checks"],
        )

        your_open_prs.append({
            "number": pr["number"],
            "title": pr["title"],
            "url": pr["url"],
            "state": _PR_STATE_LABELS[review_state["state"]],
            "threads": _THREAD_STATE_LABELS[review_state["threads"]],
            "comments": _THREAD_STATE_LABELS[review_state["comments"]],
            "conflicting": _CONFLICTING_LABELS[review_state["conflicting"]],
            "checks": _CHECKS_STATE_LABELS[review_state["checks"]],
            "suggestion": _suggestion_for(bucket, pr["number"]),
        })
        ranks.append(_YOUR_PR_BUCKET_ORDER.index(bucket))

    order = sorted(range(len(your_open_prs)), key=lambda i: ranks[i])
    return [your_open_prs[i] for i in order], your_draft_prs


def main() -> None:
    """Main entry point for printing the triage survey as JSON."""
    _check_dependencies()

    try:
        owner, repo_name = _get_repo_context(_run_cmd)
        project_owner, project_number = _get_linked_project(_run_cmd, owner, repo_name)
        login = _resolve_login(_run_cmd)
        your_open_prs, your_draft_prs = _fetch_open_and_draft_prs(
            _run_cmd, owner, repo_name,
        )

        result = {
            "prs_to_review": _fetch_prs_to_review(_run_cmd, login),
            "your_open_prs": your_open_prs,
            "your_draft_prs": your_draft_prs,
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
