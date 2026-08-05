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
    *, others_prs: str = "[]", own_prs: str = "[]",
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
            "--json", "number,title,url,author,reviewRequests",
        ): others_prs,
        (
            "gh", "pr", "list", "--search", "is:open author:@me",
            "--json", "number,title,url,isDraft,reviewDecision,closingIssuesReferences",
        ): own_prs,
        (
            "gh", "project", "item-list", "9", "--owner", "acme",
            "--format", "json", "--limit", "200",
        ): project_items,
    }


def _threads_response(*, unresolved: bool, number: int) -> tuple[tuple[str, ...], str]:
    key = _normalize([
        "gh", "api", "graphql", "-f", "owner=acme", "-f", "repo=widgets",
        "-F", f"number={number}", "-f", "query=placeholder",
    ])
    body = json.dumps({
        "data": {"repository": {"pullRequest": {"reviewThreads": {"nodes": [
            {"isResolved": not unresolved},
        ]}}}},
    })
    return key, body


def test_main_prints_empty_survey_when_nothing_is_open(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """With nothing open anywhere, main() reports three empty lists."""
    _install_gh(monkeypatch, _base_responses())

    ct.main()

    result = json.loads(capsys.readouterr().out)
    assert result == {"others_prs": [], "own_prs": [], "backlog_issues": []}


def test_main_drops_bot_prs_and_orders_review_requested_first(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """Bot PRs are dropped; review-requested PRs sort before not-requested ones."""
    others_prs = json.dumps([
        {
            "number": 1, "title": "Bot PR", "url": "u1",
            "author": {"login": "dependabot", "is_bot": True},
            "reviewRequests": [],
        },
        {
            "number": 2, "title": "Not requested", "url": "u2",
            "author": {"login": "bob", "is_bot": False},
            "reviewRequests": [],
        },
        {
            "number": 3, "title": "Requested", "url": "u3",
            "author": {"login": "carol", "is_bot": False},
            "reviewRequests": [{"login": "octocat"}],
        },
    ])
    _install_gh(monkeypatch, _base_responses(others_prs=others_prs))

    ct.main()

    result = json.loads(capsys.readouterr().out)
    assert [pr["number"] for pr in result["others_prs"]] == [3, 2]
    assert result["others_prs"][0]["bucket"] == "review_requested"
    assert result["others_prs"][1]["bucket"] == "not_requested"


def test_main_classifies_own_prs_and_includes_linked_issue_for_drafts(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """Own PRs sort ready_to_merge, resolve, then draft; drafts carry linked_issue."""
    own_prs = json.dumps([
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
    ])
    responses = _base_responses(own_prs=own_prs)
    key, body = _threads_response(unresolved=False, number=2)
    responses[key] = body
    key, body = _threads_response(unresolved=True, number=3)
    responses[key] = body
    _install_gh(monkeypatch, responses)

    ct.main()

    result = json.loads(capsys.readouterr().out)
    own = result["own_prs"]
    assert [pr["number"] for pr in own] == [2, 3, 1]
    assert own[0]["bucket"] == "ready_to_merge"
    assert own[1]["bucket"] == "resolve"
    assert own[2]["bucket"] == "draft"
    assert own[2]["linked_issue"] == {"number": 42, "url": "issue-url"}


def test_main_filters_backlog_issues_by_type_and_assignee(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """Only Story/Task/Bug issues survive, assigned first, then unassigned.

    A Story/Task/Bug decomposed from an Epic still has a parent, but that's
    expected: those are the actionable leaf items and belong in the backlog.
    """
    project_items = json.dumps({"items": [
        {
            "status": "Todo", "type": "Task", "assignees": ["octocat"],
            "content": {"type": "Issue", "number": 1, "title": "Mine", "url": "u1"},
        },
        {
            "status": "Todo", "type": "Task", "assignees": [],
            "content": {"type": "Issue", "number": 2, "title": "Free", "url": "u2"},
        },
        {
            "status": "Todo", "type": "Task", "assignees": ["bob"],
            "content": {"type": "Issue", "number": 3, "title": "Bob's", "url": "u3"},
        },
        {
            "status": "Todo", "type": "Epic", "assignees": [],
            "content": {"type": "Issue", "number": 4, "title": "Epic", "url": "u4"},
        },
        {
            "status": "Done", "type": "Task", "assignees": [],
            "content": {"type": "Issue", "number": 5, "title": "Done", "url": "u5"},
        },
    ]})
    _install_gh(monkeypatch, _base_responses(project_items=project_items))

    ct.main()

    result = json.loads(capsys.readouterr().out)
    backlog = result["backlog_issues"]
    assert [issue["number"] for issue in backlog] == [1, 2]
    assert backlog[0]["bucket"] == "assigned"
    assert backlog[1]["bucket"] == "unassigned"


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
    assert result == {"others_prs": [], "own_prs": [], "backlog_issues": []}


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
