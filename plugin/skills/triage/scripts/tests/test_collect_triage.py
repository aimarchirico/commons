"""Tests for collect_triage.py, driven through its public main() entry point."""

import json
import subprocess

import collect_triage as ct
import pytest

_REPO_CONTEXT = json.dumps({"owner": {"login": "acme"}, "name": "widgets"})
_LOGIN = "octocat"


_PROJECT_QUERY_RESPONSE = json.dumps(
    {
        "data": {
            "repository": {
                "projectsV2": {
                    "nodes": [
                        {
                            "number": 9,
                            "title": "Widgets",
                            "closed": False,
                            "owner": {"login": "acme"},
                        },
                    ],
                },
            },
        },
    },
)


def _normalize(args: list[str]) -> tuple[str, ...]:
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
    q_args = [
        "gh",
        "api",
        "graphql",
        "-f",
        "owner=acme",
        "-f",
        "name=widgets",
        "-f",
        "query=placeholder",
    ]
    pr_rev_args = [
        "gh",
        "pr",
        "list",
        "--search",
        "is:open -author:@me draft:false",
        "--json",
        "number,title,url,author,reviewRequests,reviewDecision",
    ]
    pr_me_args = [
        "gh",
        "pr",
        "list",
        "--search",
        "is:open author:@me",
        "--json",
        "number,title,url,isDraft,closingIssuesReferences",
    ]
    item_args = [
        "gh",
        "project",
        "item-list",
        "9",
        "--owner",
        "acme",
        "--format",
        "json",
        "--limit",
        "200",
    ]
    return {
        ("gh", "repo", "view", "--json", "owner,name"): _REPO_CONTEXT,
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
        [
            "gh",
            "api",
            "graphql",
            "-f",
            "owner=acme",
            "-f",
            "repo=widgets",
            "-F",
            f"number={number}",
            "-f",
            "query=placeholder",
        ],
    )
    body = json.dumps(
        {
            "data": {
                "repository": {
                    "pullRequest": {
                        "latestReview": {
                            "nodes": []
                            if review_state is None
                            else [{"state": review_state}],
                        },
                        "allReviews": {"nodes": []},
                        "reviewThreads": {
                            "nodes": [
                                {"isResolved": r} for r in (thread_resolutions or [])
                            ],
                        },
                        "comments": {"nodes": []},
                        "mergeable": mergeable,
                        "commits": {
                            "nodes": []
                            if checks_state is None
                            else [
                                {
                                    "commit": {
                                        "statusCheckRollup": {"state": checks_state},
                                    },
                                },
                            ],
                        },
                    },
                },
            },
        },
    )
    return key, body


def test_main_prints_empty_survey_when_nothing_is_open(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """With nothing open anywhere, main() reports four empty lists."""
    _install_gh(monkeypatch, _base_responses())

    ct.main()

    result = json.loads(capsys.readouterr().out)
    assert result == {
        "prs_to_review": [],
        "your_open_prs": [],
        "your_draft_prs": [],
        "backlog_issues": [],
        "assigned_to_others_count": 0,
        "fully_blocked_count": 0,
    }


def test_main_drops_bot_and_approved_prs_from_review_list(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Bot and already-approved PRs are dropped; awaiting-review sorts first."""
    prs_to_review = json.dumps(
        [
            {
                "number": 1,
                "title": "Bot PR",
                "url": "u1",
                "author": {"login": "dependabot", "is_bot": True},
                "reviewRequests": [],
                "reviewDecision": "",
            },
            {
                "number": 2,
                "title": "Already approved",
                "url": "u2",
                "author": {"login": "bob", "is_bot": False},
                "reviewRequests": [{"login": "octocat"}],
                "reviewDecision": "APPROVED",
            },
            {
                "number": 3,
                "title": "Not requested",
                "url": "u3",
                "author": {"login": "bob", "is_bot": False},
                "reviewRequests": [],
                "reviewDecision": "",
            },
            {
                "number": 4,
                "title": "Requested",
                "url": "u4",
                "author": {"login": "carol", "is_bot": False},
                "reviewRequests": [{"login": "octocat"}],
                "reviewDecision": "",
            },
        ],
    )
    _install_gh(monkeypatch, _base_responses(prs_to_review=prs_to_review))

    ct.main()

    result = json.loads(capsys.readouterr().out)
    assert [pr["number"] for pr in result["prs_to_review"]] == [4, 3]
    assert result["prs_to_review"][0]["state"] == "Awaiting your review"
    assert result["prs_to_review"][1]["state"] == "Not awaiting your review"


def test_main_disambiguates_multiple_projects_by_repo_name(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """When several open Projects are linked, the one titled after the repo wins."""
    node2 = {"number": 10, "title": "Widgets Template", "closed": False}
    response = json.dumps(
        {
            "data": {
                "repository": {
                    "projectsV2": {
                        "nodes": [
                            {"number": 9, "title": "Widgets", "closed": False},
                            node2,
                        ],
                    },
                },
            },
        },
    )
    _install_gh(monkeypatch, _base_responses(project_query_response=response))

    ct.main()

    result = json.loads(capsys.readouterr().out)
    assert result["prs_to_review"] == []
    assert result["your_open_prs"] == []
    assert result["your_draft_prs"] == []
    assert result["backlog_issues"] == []
    assert (result["assigned_to_others_count"], result["fully_blocked_count"]) == (0, 0)


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
