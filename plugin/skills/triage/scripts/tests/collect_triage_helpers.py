"""Shared gh-mocking fixtures for collect_triage.py tests."""

import json
import re
import subprocess
from collections.abc import Sequence
from typing import Any

import collect_triage as ct
import pytest

REPO_CONTEXT = json.dumps(
    {
        "owner": {"login": "acme"},
        "name": "widgets",
        "defaultBranchRef": {"name": "main"},
    },
)
LOGIN = "octocat"
node_def = {"number": 9, "title": "Widgets", "closed": False}
PROJECT_QUERY_RESPONSE = json.dumps(
    {"data": {"repository": {"projectsV2": {"nodes": [node_def]}}}},
)
PR_LIST_FIELDS = (
    "number,title,url,author,reviewRequests,reviewDecision,isDraft,"
    "closingIssuesReferences,headRefName,baseRefName"
)

_ALIAS_RE = re.compile(r"\b((?:i|pr)\d+):")


def _normalize(args: Sequence[str]) -> tuple[str, ...]:
    def norm(a: str) -> str:
        if not a.startswith("query="):
            return a
        aliases = sorted(set(_ALIAS_RE.findall(a)))
        return f"query=<{','.join(aliases)}>" if aliases else "query=<Q>"

    return tuple(norm(a) for a in args)


def _fake_completed(stdout: str) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=[], returncode=0, stdout=stdout)


def _install_gh(
    monkeypatch: pytest.MonkeyPatch,
    responses: dict[tuple[str, ...], str],
) -> None:
    def fake_run(
        args: list[str],
        **_kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        if args[-2:] == ["auth", "status"]:
            return _fake_completed("")
        return _fake_completed(responses[_normalize(args)])

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(
        ct.project_preflight.shutil,
        "which",
        lambda _name: "/usr/bin/gh",
    )


def _base_responses(
    *,
    prs_to_review: str = "[]",
    your_prs: str = "[]",
    project_items: str = '{"items": []}',
    in_progress_items: str = '{"items": []}',
    project_query_response: str = PROJECT_QUERY_RESPONSE,
) -> dict[tuple[str, ...], str]:
    q_args = "gh|api|graphql|-f|owner=acme|-f|name=widgets|-f|query=placeholder"
    q_args = q_args.split("|")
    pr_list_args = ["gh", "pr", "list", "--search", "is:open", "--json", PR_LIST_FIELDS]
    combined_prs = json.loads(your_prs) + json.loads(prs_to_review)
    item_str = (
        "gh|project|item-list|9|--owner|acme|--format|json|--limit|200|"
        "--query|status:Todo is:issue"
    )
    item_args = item_str.split("|")
    in_progress_str = (
        "gh|project|item-list|9|--owner|acme|--format|json|--limit|200|"
        '--query|status:"In Progress" is:issue assignee:@me'
    )
    in_progress_args = in_progress_str.split("|")
    return {
        ("gh", "repo", "view", "--json", "owner,name,defaultBranchRef"): REPO_CONTEXT,
        _normalize(q_args): project_query_response,
        ("gh", "api", "user", "--jq", ".login"): LOGIN,
        tuple(pr_list_args): json.dumps(combined_prs),
        tuple(item_args): project_items,
        tuple(in_progress_args): in_progress_items,
    }


def _review_states_response(
    specs: dict[int, dict[str, Any]],
) -> tuple[tuple[str, ...], str]:
    aliases_text = " ".join(f"pr{n}:" for n in specs)
    key = _normalize(
        (
            "gh", "api", "graphql", "-f", "owner=acme", "-f", "repo=widgets",
            "-f", f"query={aliases_text}",
        ),
    )
    repo_data = {}
    for n, spec in specs.items():
        review_state = spec.get("review_state")
        thread_resolutions = spec.get("thread_resolutions") or []
        mergeable = spec.get("mergeable", "MERGEABLE")
        checks_state = spec.get("checks_state")
        rev = [] if review_state is None else [{"state": review_state}]
        thr = [{"isResolved": r} for r in thread_resolutions]
        chk = (
            []
            if checks_state is None
            else [{"commit": {"statusCheckRollup": {"state": checks_state}}}]
        )
        repo_data[f"pr{n}"] = {
            "latestReview": {"nodes": rev},
            "allReviews": {"nodes": []},
            "reviewThreads": {"nodes": thr},
            "comments": {"nodes": []},
            "mergeable": mergeable,
            "commits": {"nodes": chk},
        }
    return key, json.dumps({"data": {"repository": repo_data}})


def _issues_deps_response(
    deps_by_number: dict[int, dict[str, Any]],
) -> tuple[tuple[str, ...], str]:
    aliases_text = " ".join(f"i{n}:" for n in deps_by_number)
    key = _normalize(
        (
            "gh", "api", "graphql", "-f", f"query={aliases_text}",
            "-f", "owner=acme", "-f", "repo=widgets",
        ),
    )
    repo_data = {
        f"i{n}": {
            "blockedBy": {"nodes": deps.get("blocked_by_nodes", [])},
            "blocking": {"nodes": deps.get("blocking_nodes", [])},
        }
        for n, deps in deps_by_number.items()
    }
    return key, json.dumps({"data": {"repository": repo_data}})


def _assert_empty_survey(capsys: pytest.CaptureFixture[str]) -> None:
    res = json.loads(capsys.readouterr().out)
    assert not res["prs_to_review"]
    assert not res["your_open_prs"]
    assert not res["your_draft_prs"]
    assert not res["leaf_issues"]
    assert "categories" in res
    assert res["active_count"] == 0
    assert (res["assigned_to_others_count"], res["fully_blocked_count"]) == (0, 0)


def _make_pr(
    *,
    num: int,
    title: str,
    draft: bool = False,
    refs: list[object] | None = None,
    branch_info: tuple[str, str] = ("feature/branch", "main"),
) -> dict[str, object]:
    head, base = branch_info
    ref_list = refs or []
    return {
        "number": num,
        "title": title,
        "url": f"u{num}",
        "isDraft": draft,
        "closingIssuesReferences": ref_list,
        "headRefName": head,
        "baseRefName": base,
        "author": {"login": LOGIN, "is_bot": False},
        "reviewRequests": [],
        "reviewDecision": "",
    }
