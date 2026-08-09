"""Shared gh-mocking fixtures for collect_triage.py tests."""

import json
import subprocess
from collections.abc import Sequence

import collect_triage as ct
import pytest

REPO_CONTEXT = json.dumps({"owner": {"login": "acme"}, "name": "widgets"})
LOGIN = "octocat"
node_def = {"number": 9, "title": "Widgets", "closed": False}
PROJECT_QUERY_RESPONSE = json.dumps(
    {"data": {"repository": {"projectsV2": {"nodes": [node_def]}}}},
)


def _normalize(args: Sequence[str]) -> tuple[str, ...]:
    return tuple("query=<Q>" if a.startswith("query=") else a for a in args)


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
    q_str = "gh|api|graphql|-f|owner=acme|-f|name=widgets|-f|query=placeholder"
    q_args = q_str.split("|")
    pr_rev_str = (
        "gh|pr|list|--search|is:open -author:@me draft:false|"
        "--json|number,title,url,author,reviewRequests,reviewDecision"
    )
    pr_rev_args = pr_rev_str.split("|")
    pr_me_str = (
        "gh|pr|list|--search|is:open author:@me|"
        "--json|number,title,url,isDraft,closingIssuesReferences,headRefName,baseRefName"
    )
    pr_me_args = pr_me_str.split("|")
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
        ("gh", "repo", "view", "--json", "owner,name"): REPO_CONTEXT,
        ("gh", "repo", "view", "--json", "defaultBranchRef"): json.dumps(
            {"defaultBranchRef": {"name": "main"}},
        ),
        _normalize(q_args): project_query_response,
        ("gh", "api", "user", "--jq", ".login"): LOGIN,
        tuple(pr_rev_args): prs_to_review,
        tuple(pr_me_args): your_prs,
        tuple(item_args): project_items,
        tuple(in_progress_args): in_progress_items,
    }


def _review_state_response(
    *,
    number: int,
    review_state: str | None = None,
    thread_resolutions: list[bool] | None = None,
    mergeable: str = "MERGEABLE",
    checks_state: str | None = None,
) -> tuple[tuple[str, ...], str]:
    key = _normalize(
        f"gh|api|graphql|-f|owner=acme|-f|repo=widgets|-F|number={number}|-f|query=placeholder".split(
            "|",
        ),
    )
    rev = [] if review_state is None else [{"state": review_state}]
    thr = [{"isResolved": r} for r in (thread_resolutions or [])]
    chk = (
        []
        if checks_state is None
        else [{"commit": {"statusCheckRollup": {"state": checks_state}}}]
    )
    pr_data = {
        "latestReview": {"nodes": rev},
        "allReviews": {"nodes": []},
        "reviewThreads": {"nodes": thr},
        "comments": {"nodes": []},
        "mergeable": mergeable,
        "commits": {"nodes": chk},
    }
    return key, json.dumps({"data": {"repository": {"pullRequest": pr_data}}})


def _assert_empty_survey(capsys: pytest.CaptureFixture[str]) -> None:
    res = json.loads(capsys.readouterr().out)
    assert not res["prs_to_review"]
    assert not res["your_open_prs"]
    assert not res["your_draft_prs"]
    assert not res["backlog_issues"]
    assert "categories" in res
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
    }
