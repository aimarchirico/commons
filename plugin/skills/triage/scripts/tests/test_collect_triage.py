"""Tests for collect_triage.py, driven through its public main() entry point."""

import json
import subprocess

import collect_triage as ct
import pytest

_REPO_CONTEXT = json.dumps({"owner": {"login": "acme"}, "name": "widgets"})
_LOGIN = "octocat"

_PROJECT_QUERY_RESPONSE = json.dumps({
    "data": {"repository": {"projectsV2": {"nodes": [
        {
            "number": 9, "title": "Widgets", "closed": False,
            "owner": {"login": "acme"},
        },
    ]}}},
})


def _normalize(args: list[str]) -> tuple[str, ...]:
    return tuple("query=<Q>" if a.startswith("query=") else a for a in args)


def _fake_completed(stdout: str) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=[], returncode=0, stdout=stdout)


def _install_gh(
    monkeypatch: pytest.MonkeyPatch, responses: dict[tuple[str, ...], str],
) -> None:
    def fake_run(
        args: list[str], **_kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        if args[-2:] == ["auth", "status"]:
            return _fake_completed("")
        return _fake_completed(responses[_normalize(args)])

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(ct.shutil, "which", lambda _name: "/usr/bin/gh")


def _base_responses(
    *, prs_to_review: str = "[]", your_prs: str = "[]",
    project_items: str = '{"items": []}',
    project_query_response: str = _PROJECT_QUERY_RESPONSE,
) -> dict[tuple[str, ...], str]:
    return {
        ("gh", "repo", "view", "--json", "owner,name"): _REPO_CONTEXT,
        _normalize([
            "gh", "api", "graphql", "-f", "owner=acme", "-f", "name=widgets",
            "-f", "query=placeholder",
        ]): project_query_response,
        ("gh", "api", "user", "--jq", ".login"): _LOGIN,
        (
            "gh", "pr", "list", "--search", "is:open -author:@me draft:false",
            "--json", "number,title,url,author,reviewRequests,reviewDecision",
        ): prs_to_review,
        (
            "gh", "pr", "list", "--search", "is:open author:@me",
            "--json", "number,title,url,isDraft,reviewDecision,closingIssuesReferences",
        ): your_prs,
        (
            "gh", "project", "item-list", "9", "--owner", "acme",
            "--format", "json", "--limit", "200",
        ): project_items,
    }


def _review_state_response(
    *, unresolved: bool, has_reviews: bool, number: int,
) -> tuple[tuple[str, ...], str]:
    key = _normalize([
        "gh", "api", "graphql", "-f", "owner=acme", "-f", "repo=widgets",
        "-F", f"number={number}", "-f", "query=placeholder",
    ])
    body = json.dumps({
        "data": {"repository": {"pullRequest": {
            "reviewThreads": {"nodes": [{"isResolved": not unresolved}]},
            "reviews": {"totalCount": 1 if has_reviews else 0},
        }}},
    })
    return key, body


def test_main_prints_empty_survey_when_nothing_is_open(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """With nothing open anywhere, main() reports three empty lists."""
    _install_gh(monkeypatch, _base_responses())

    ct.main()

    result = json.loads(capsys.readouterr().out)
    assert result == {"prs_to_review": [], "your_prs": [], "backlog_issues": []}


def test_main_drops_bot_and_approved_prs_from_review_list(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """Bot and already-approved PRs are dropped; awaiting-review sorts first."""
    prs_to_review = json.dumps([
        {
            "number": 1, "title": "Bot PR", "url": "u1",
            "author": {"login": "dependabot", "is_bot": True},
            "reviewRequests": [], "reviewDecision": "",
        },
        {
            "number": 2, "title": "Already approved", "url": "u2",
            "author": {"login": "bob", "is_bot": False},
            "reviewRequests": [{"login": "octocat"}], "reviewDecision": "APPROVED",
        },
        {
            "number": 3, "title": "Not requested", "url": "u3",
            "author": {"login": "bob", "is_bot": False},
            "reviewRequests": [], "reviewDecision": "",
        },
        {
            "number": 4, "title": "Requested", "url": "u4",
            "author": {"login": "carol", "is_bot": False},
            "reviewRequests": [{"login": "octocat"}], "reviewDecision": "",
        },
    ])
    _install_gh(monkeypatch, _base_responses(prs_to_review=prs_to_review))

    ct.main()

    result = json.loads(capsys.readouterr().out)
    assert [pr["number"] for pr in result["prs_to_review"]] == [4, 3]
    assert result["prs_to_review"][0]["reviews"] == "awaiting_your_review"
    assert result["prs_to_review"][1]["reviews"] == "not_awaiting_your_review"


def test_main_classifies_your_prs_and_includes_linked_issue_for_drafts(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """Your PRs sort approved, unresolved, not-reviewed, then draft."""
    your_prs = json.dumps([
        {
            "number": 1, "title": "Draft", "url": "u1", "isDraft": True,
            "reviewDecision": "", "closingIssuesReferences": [
                {"number": 42, "url": "issue-url"},
            ],
        },
        {
            "number": 2, "title": "Approved clean", "url": "u2", "isDraft": False,
            "reviewDecision": "APPROVED", "closingIssuesReferences": [],
        },
        {
            "number": 3, "title": "Needs review", "url": "u3", "isDraft": False,
            "reviewDecision": "", "closingIssuesReferences": [],
        },
        {
            "number": 4, "title": "Untouched", "url": "u4", "isDraft": False,
            "reviewDecision": "", "closingIssuesReferences": [],
        },
    ])
    responses = _base_responses(your_prs=your_prs)
    key, body = _review_state_response(unresolved=False, has_reviews=True, number=2)
    responses[key] = body
    key, body = _review_state_response(unresolved=True, has_reviews=True, number=3)
    responses[key] = body
    key, body = _review_state_response(unresolved=False, has_reviews=False, number=4)
    responses[key] = body
    _install_gh(monkeypatch, responses)

    ct.main()

    result = json.loads(capsys.readouterr().out)
    yours = result["your_prs"]
    assert [pr["number"] for pr in yours] == [2, 3, 4, 1]
    statuses = [(pr["status"], pr["reviews"]) for pr in yours]
    assert statuses == [
        ("approved", "no_unresolved_review"),
        ("not_approved", "unresolved_review"),
        ("not_approved", "not_reviewed"),
        ("not_approved", "not_ready"),
    ]
    assert yours[3]["linked_issue"] == {"number": 42, "url": "issue-url"}


def test_main_computes_real_status_for_approved_draft_prs(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """A draft PR that was approved while in draft still reports approved status."""
    your_prs = json.dumps([
        {
            "number": 5, "title": "Approved draft", "url": "u5", "isDraft": True,
            "reviewDecision": "APPROVED", "closingIssuesReferences": [],
        },
    ])
    _install_gh(monkeypatch, _base_responses(your_prs=your_prs))

    ct.main()

    result = json.loads(capsys.readouterr().out)
    yours = result["your_prs"]
    assert (yours[0]["status"], yours[0]["reviews"]) == ("approved", "not_ready")
    assert yours[0]["linked_issue"] is None


def test_main_disambiguates_multiple_projects_by_repo_name(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """When several open Projects are linked, the one titled after the repo wins."""
    response = json.dumps({
        "data": {"repository": {"projectsV2": {"nodes": [
            {
                "number": 9, "title": "Widgets", "closed": False,
                "owner": {"login": "acme"},
            },
            {
                "number": 10, "title": "Widgets Template", "closed": False,
                "owner": {"login": "acme"},
            },
        ]}}},
    })
    _install_gh(monkeypatch, _base_responses(project_query_response=response))

    ct.main()

    result = json.loads(capsys.readouterr().out)
    assert result == {"prs_to_review": [], "your_prs": [], "backlog_issues": []}


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
    monkeypatch.setattr(ct.shutil, "which", lambda _name: None)

    with pytest.raises(SystemExit):
        ct.main()
