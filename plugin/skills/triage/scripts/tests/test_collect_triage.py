"""Tests for collect_triage.py, driven through its public main() entry point."""

import json
import subprocess
from collections.abc import Sequence

import collect_triage as ct
import pytest

_REPO_CONTEXT = json.dumps({"owner": {"login": "acme"}, "name": "widgets"})
_LOGIN = "octocat"
node_def = {"number": 9, "title": "Widgets", "closed": False}
_PROJECT_QUERY_RESPONSE = json.dumps(
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
    project_query_response: str = _PROJECT_QUERY_RESPONSE,
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
    item_str = "gh|project|item-list|9|--owner|acme|--format|json|--limit|200"
    item_args = item_str.split("|")
    return {
        ("gh", "repo", "view", "--json", "owner,name"): _REPO_CONTEXT,
        ("gh", "repo", "view", "--json", "defaultBranchRef"): json.dumps({"defaultBranchRef": {"name": "main"}}),
        _normalize(q_args): project_query_response,
        ("gh", "api", "user", "--jq", ".login"): _LOGIN,
        tuple(pr_rev_args): prs_to_review,
        tuple(pr_me_args): your_prs,
        tuple(item_args): project_items,
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


def test_main_prints_empty_survey_when_nothing_is_open(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """With nothing open anywhere, main() reports empty survey categories."""
    _install_gh(monkeypatch, _base_responses())
    ct.main()
    _assert_empty_survey(capsys)


def _make_review_pr(
    *,
    num: int,
    bot: bool = False,
    app: bool = False,
    req: bool = False,
) -> dict[str, object]:
    login = "dependabot" if bot else ("bob" if not req else "carol")
    author = {"login": login, "is_bot": bot}
    reqs = [{"login": "octocat"}] if (app or req) else []
    dec = "APPROVED" if app else ""
    return {
        "number": num,
        "title": f"P{num}",
        "url": f"u{num}",
        "author": author,
        "reviewRequests": reqs,
        "reviewDecision": dec,
    }


def test_main_drops_bot_and_approved_prs_from_review_list(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Bot and already-approved PRs are dropped; awaiting-review sorts first."""
    prs_to_review = json.dumps(
        [
            _make_review_pr(num=1, bot=True),
            _make_review_pr(num=2, app=True, req=True),
            _make_review_pr(num=3),
            _make_review_pr(num=4, req=True),
        ],
    )
    _install_gh(monkeypatch, _base_responses(prs_to_review=prs_to_review))

    ct.main()

    result = json.loads(capsys.readouterr().out)
    assert [pr["number"] for pr in result["prs_to_review"]] == [4, 3]
    assert result["prs_to_review"][0]["review"] == "Requested"
    assert result["prs_to_review"][1]["review"] == "Not requested"


def _make_pr(
    num: int,
    title: str,
    *,
    draft: bool = False,
    refs: list[object] | None = None,
    head: str = "feature/branch",
    base: str = "main",
) -> dict[str, object]:
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


def test_main_classifies_your_prs_and_splits_out_drafts(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Non-draft PRs sort and categorize into merge_ready, merge_blockers, etc."""
    your_prs = json.dumps(
        [
            _make_pr(1, "Draft", draft=True, refs=[{"number": 42, "url": "issue-url"}]),
            _make_pr(2, "Approved clean"),
            _make_pr(3, "Approved unresolved"),
            _make_pr(4, "Changes requested"),
            _make_pr(5, "Untouched"),
            _make_pr(6, "Approved but blocked"),
        ],
    )
    responses = _base_responses(your_prs=your_prs)
    states = (
        (2, "APPROVED", [True], "MERGEABLE", None),
        (3, "APPROVED", [False], "MERGEABLE", None),
        (4, "CHANGES_REQUESTED", [False], "MERGEABLE", None),
        (5, None, None, "MERGEABLE", None),
        (6, "APPROVED", [True], "CONFLICTING", "FAILURE"),
    )
    for num, state, threads, mergeable, checks in states:
        k, b = _review_state_response(
            number=num,
            review_state=state,
            thread_resolutions=threads,
            mergeable=mergeable,
            checks_state=checks,
        )
        responses[k] = b
    _install_gh(monkeypatch, responses)

    ct.main()

    result = json.loads(capsys.readouterr().out)
    cats = result["categories"]["action_required"]
    assert [pr["number"] for pr in cats["merge_ready"]] == [2]
    assert [pr["number"] for pr in cats["merge_blockers"]] == [3, 4, 6]

    assert [pr["number"] for pr in result["categories"]["waiting"]["pending_approval"]] == [5]

    assert result["your_draft_prs"][0]["number"] == 1



def test_main_draft_prs_without_linked_issue_report_null(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A draft with no closing issue reference reports linked_issue as null."""
    your_prs = json.dumps([_make_pr(5, "Untouched draft", draft=True)])
    _install_gh(monkeypatch, _base_responses(your_prs=your_prs))

    ct.main()

    result = json.loads(capsys.readouterr().out)
    assert result["your_draft_prs"][0]["number"] == 5
    assert result["your_draft_prs"][0]["linked_issue"] is None



def test_main_disambiguates_multiple_projects_by_repo_name(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """When several open Projects are linked, the one titled after the repo wins."""
    nodes = [
        {"number": 9, "title": "Widgets", "closed": False},
        {"number": 10, "title": "Widgets Template", "closed": False},
    ]
    response = json.dumps({"data": {"repository": {"projectsV2": {"nodes": nodes}}}})
    _install_gh(monkeypatch, _base_responses(project_query_response=response))
    ct.main()
    _assert_empty_survey(capsys)


def test_main_exits_when_no_open_project_is_linked(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """With no open Project linked, main() fails fast instead of guessing."""
    response = json.dumps({"data": {"repository": {"projectsV2": {"nodes": []}}}})
    _install_gh(monkeypatch, _base_responses(project_query_response=response))

    with pytest.raises(SystemExit):
        ct.main()


def test_main_exits_when_gh_is_not_installed(monkeypatch: pytest.MonkeyPatch) -> None:
    """main() fails fast when the gh CLI isn't on PATH."""
    monkeypatch.setattr(ct.project_preflight.shutil, "which", lambda _name: None)

    with pytest.raises(SystemExit):
        ct.main()
