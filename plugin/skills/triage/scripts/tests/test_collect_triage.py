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
    monkeypatch.setattr(
        ct.project_preflight.shutil, "which", lambda _name: "/usr/bin/gh",
    )


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
    mergeable: str = "MERGEABLE",
    checks_state: str | None = None,
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
            "comments": {"nodes": []},
            "mergeable": mergeable,
            "commits": {
                "nodes": [] if checks_state is None else [
                    {"commit": {"statusCheckRollup": {"state": checks_state}}},
                ],
            },
        }}},
    })
    return key, body


def test_main_prints_empty_survey_when_nothing_is_open(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """With nothing open anywhere, main() reports four empty lists."""
    _install_gh(monkeypatch, _base_responses())

    ct.main()

    result = json.loads(capsys.readouterr().out)
    assert result == {
        "prs_to_review": [], "your_open_prs": [], "your_draft_prs": [],
        "backlog_issues": [], "assigned_to_others_count": 0, "fully_blocked_count": 0,
    }


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


def test_main_classifies_your_prs_and_splits_out_drafts(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """Non-draft PRs sort merge, resolve-then-merge, resolve, self-review.

    Drafts land in your_draft_prs instead, with no review-state query made
    for them (not actionable until they're out of draft).
    """
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
        {
            "number": 6, "title": "Approved but blocked", "url": "u6",
            "isDraft": False, "closingIssuesReferences": [],
        },
    ])
    responses = _base_responses(your_prs=your_prs)
    for number, review_state, thread_resolutions, mergeable, checks_state in (
        (2, "APPROVED", [True], "MERGEABLE", None),
        (3, "APPROVED", [False], "MERGEABLE", None),
        (4, "CHANGES_REQUESTED", [False], "MERGEABLE", None),
        (5, None, None, "MERGEABLE", None),
        (6, "APPROVED", [True], "CONFLICTING", "FAILURE"),
    ):
        key, body = _review_state_response(
            number=number, review_state=review_state,
            thread_resolutions=thread_resolutions,
            mergeable=mergeable, checks_state=checks_state,
        )
        responses[key] = body
    _install_gh(monkeypatch, responses)

    ct.main()

    result = json.loads(capsys.readouterr().out)
    yours = result["your_open_prs"]
    assert [pr["number"] for pr in yours] == [2, 3, 6, 4, 5]
    assert [pr["suggestion"] for pr in yours] == [
        "Merge the PR",
        "Resolve problems with `/commons:resolve --pr 3`, then merge the PR",
        "Resolve problems with `/commons:resolve --pr 6`, then merge the PR",
        "Resolve problems with `/commons:resolve --pr 4`",
        "Self-review the PR with `/commons:review --pr 5`",
    ]
    assert [pr["state"] for pr in yours] == [
        "Approved", "Approved", "Approved", "Changes requested", "No reviews",
    ]
    assert (yours[2]["conflicting"], yours[2]["checks"]) == ("Yes", "Failing")

    drafts = result["your_draft_prs"]
    assert drafts == [{
        "number": 1, "title": "Draft", "url": "u1",
        "linked_issue": {"number": 42, "url": "issue-url"},
    }]


def test_main_draft_prs_without_linked_issue_report_null(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """A draft with no closing issue reference reports linked_issue as null."""
    your_prs = json.dumps([
        {
            "number": 5, "title": "Untouched draft", "url": "u5", "isDraft": True,
            "closingIssuesReferences": [],
        },
    ])
    _install_gh(monkeypatch, _base_responses(your_prs=your_prs))

    ct.main()

    result = json.loads(capsys.readouterr().out)
    assert result["your_draft_prs"] == [
        {"number": 5, "title": "Untouched draft", "url": "u5", "linked_issue": None},
    ]


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
    assert result == {
        "prs_to_review": [], "your_open_prs": [], "your_draft_prs": [],
        "backlog_issues": [], "assigned_to_others_count": 0, "fully_blocked_count": 0,
    }


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
