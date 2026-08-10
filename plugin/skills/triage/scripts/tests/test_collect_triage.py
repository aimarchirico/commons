"""Tests for collect_triage.py, driven through its public main() entry point."""

import json

import collect_triage as ct
import pytest
from collect_triage_helpers import (
    _assert_empty_survey,
    _base_responses,
    _install_gh,
    _issues_deps_response,
    _make_pr,
    _review_states_response,
)


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


def test_main_classifies_your_prs_and_splits_out_drafts(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Non-draft PRs sort and categorize into merge_ready, merge_blockers, etc."""
    your_prs = json.dumps(
        [
            _make_pr(
                num=1,
                title="Draft",
                draft=True,
                refs=[{"number": 42, "url": "issue-url"}],
            ),
            _make_pr(num=2, title="Approved clean"),
            _make_pr(num=3, title="Approved unresolved"),
            _make_pr(num=4, title="Changes requested"),
            _make_pr(num=5, title="Untouched"),
            _make_pr(num=6, title="Approved but blocked"),
        ],
    )
    responses = _base_responses(your_prs=your_prs)
    specs = {
        2: {"review_state": "APPROVED", "thread_resolutions": [True]},
        3: {"review_state": "APPROVED", "thread_resolutions": [False]},
        4: {"review_state": "CHANGES_REQUESTED", "thread_resolutions": [False]},
        5: {},
        6: {
            "review_state": "APPROVED",
            "thread_resolutions": [True],
            "mergeable": "CONFLICTING",
            "checks_state": "FAILURE",
        },
    }
    k, b = _review_states_response(specs)
    responses[k] = b
    _install_gh(monkeypatch, responses)

    ct.main()

    result = json.loads(capsys.readouterr().out)
    cats = result["categories"]["actionable_items"]
    assert [pr["number"] for pr in cats["merge_ready"]] == [2]
    assert [pr["number"] for pr in cats["merge_blockers"]] == [3, 4, 6]

    assert [
        pr["number"] for pr in result["categories"]["pending_prs"]["pending_approval"]
    ] == [5]

    assert result["your_draft_prs"][0]["number"] == 1


def test_main_credits_a_pr_with_unblocking_via_the_closed_issues_own_blocking_edge(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A PR's blocking count is read from what the issue it closes directly blocks."""
    your_prs = json.dumps(
        [_make_pr(num=1, title="Closes 10", refs=[{"number": 10, "url": "issue-url"}])],
    )
    responses = _base_responses(your_prs=your_prs)
    k, b = _review_states_response({1: {}})
    responses[k] = b
    k, b = _issues_deps_response(
        {
            10: {
                "blocking_nodes": [
                    {
                        "number": 42,
                        "url": "https://github.com/acme/widgets/issues/42",
                        "state": "OPEN",
                        "title": "Downstream",
                    },
                ],
            },
        },
    )
    responses[k] = b
    _install_gh(monkeypatch, responses)

    ct.main()

    result = json.loads(capsys.readouterr().out)
    pending = result["categories"]["pending_prs"]["pending_approval"]
    assert [pr["number"] for pr in pending] == [1]
    assert pending[0]["blocking"] == "1 issue"


def test_main_draft_prs_without_linked_issue_report_null(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A draft with no closing issue reference reports linked_issue as null."""
    draft_pr_number = 5
    your_prs = json.dumps(
        [_make_pr(num=draft_pr_number, title="Untouched draft", draft=True)],
    )

    _install_gh(monkeypatch, _base_responses(your_prs=your_prs))

    ct.main()

    result = json.loads(capsys.readouterr().out)
    assert result["your_draft_prs"][0]["number"] == draft_pr_number
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
