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
            "--json", "number,title,url,isDraft,closingIssuesReferences",
        ): your_prs,
        (
            "gh", "project", "item-list", "9", "--owner", "acme",
            "--format", "json", "--limit", "200",
        ): project_items,
    }


def _review_state_response(
    *,
    number: int,
    review_state: str | None = None,
    thread_resolutions: list[bool] | None = None,
    comment_bodies: list[str] | None = None,
) -> tuple[tuple[str, ...], str]:
    key = _normalize([
        "gh", "api", "graphql", "-f", "owner=acme", "-f", "repo=widgets",
        "-F", f"number={number}", "-f", "query=placeholder",
    ])
    body = json.dumps({
        "data": {"repository": {"pullRequest": {
            "latestReview": {
                "nodes": [] if review_state is None else [{"state": review_state}],
            },
            "allReviews": {"nodes": []},
            "reviewThreads": {
                "nodes": [{"isResolved": r} for r in (thread_resolutions or [])],
            },
            "comments": {
                "nodes": [
                    {"body": body_text, "createdAt": f"2024-01-01T00:00:{i:02d}Z"}
                    for i, body_text in enumerate(comment_bodies or [])
                ],
            },
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
    assert result["prs_to_review"][0]["state"] == "Awaiting your review"
    assert result["prs_to_review"][1]["state"] == "Not awaiting your review"


def test_main_classifies_your_prs_and_includes_linked_issue_for_drafts(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """Your PRs sort merge, resolve-then-merge, resolve, self-review, then draft."""
    your_prs = json.dumps([
        {
            "number": 1, "title": "Draft", "url": "u1", "isDraft": True,
            "closingIssuesReferences": [{"number": 42, "url": "issue-url"}],
        },
        {
            "number": 2, "title": "Approved clean", "url": "u2", "isDraft": False,
            "closingIssuesReferences": [],
        },
        {
            "number": 3, "title": "Approved unresolved", "url": "u3", "isDraft": False,
            "closingIssuesReferences": [],
        },
        {
            "number": 4, "title": "Changes requested", "url": "u4", "isDraft": False,
            "closingIssuesReferences": [],
        },
        {
            "number": 5, "title": "Untouched", "url": "u5", "isDraft": False,
            "closingIssuesReferences": [],
        },
    ])
    responses = _base_responses(your_prs=your_prs)
    key, body = _review_state_response(
        number=2, review_state="APPROVED", thread_resolutions=[True],
    )
    responses[key] = body
    key, body = _review_state_response(
        number=3, review_state="APPROVED", thread_resolutions=[False],
    )
    responses[key] = body
    key, body = _review_state_response(
        number=4, review_state="CHANGES_REQUESTED", thread_resolutions=[False],
    )
    responses[key] = body
    key, body = _review_state_response(number=5, review_state=None)
    responses[key] = body
    _install_gh(monkeypatch, responses)

    ct.main()

    result = json.loads(capsys.readouterr().out)
    yours = result["your_prs"]
    assert [pr["number"] for pr in yours] == [2, 3, 4, 5, 1]
    assert [pr["suggestion"] for pr in yours] == [
        "Merge the PR",
        (
            "Resolve the unresolved review with `/commons:resolve --pr 3`, "
            "then merge the PR"
        ),
        "Resolve the unresolved review with `/commons:resolve --pr 4`",
        "Self-review the PR with `/commons:review --pr 5`",
        None,
    ]
    assert [pr["state"] for pr in yours] == [
        "Approved", "Approved", "Changes requested", "None", "Not ready for review",
    ]
    assert yours[4]["linked_issue"] == {"number": 42, "url": "issue-url"}


def test_main_computes_real_review_state_for_approved_draft_prs(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """A draft PR is always not_ready regardless of any underlying review activity."""
    your_prs = json.dumps([
        {
            "number": 5, "title": "Approved draft", "url": "u5", "isDraft": True,
            "closingIssuesReferences": [],
        },
    ])
    _install_gh(monkeypatch, _base_responses(your_prs=your_prs))

    ct.main()

    result = json.loads(capsys.readouterr().out)
    yours = result["your_prs"]
    assert yours[0]["suggestion"] is None
    assert yours[0]["state"] == "Not ready for review"
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
