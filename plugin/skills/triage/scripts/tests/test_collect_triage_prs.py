"""Tests for PR classification in collect_triage.py."""

import json

import collect_triage as ct
import pytest
from test_collect_triage import _base_responses, _install_gh, _review_state_response


def test_main_classifies_your_prs_and_splits_out_drafts(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Non-draft PRs sort merge, resolve-then-merge, resolve, self-review.

    Drafts land in your_draft_prs instead, with no review-state query made for them.
    """
    your_prs = json.dumps(
        [
            {
                "number": 1,
                "title": "Draft",
                "url": "u1",
                "isDraft": True,
                "closingIssuesReferences": [{"number": 42, "url": "issue-url"}],
            },
            {
                "number": 2,
                "title": "Approved clean",
                "url": "u2",
                "isDraft": False,
                "closingIssuesReferences": [],
            },
            {
                "number": 3,
                "title": "Approved unresolved",
                "url": "u3",
                "isDraft": False,
                "closingIssuesReferences": [],
            },
            {
                "number": 4,
                "title": "Changes requested",
                "url": "u4",
                "isDraft": False,
                "closingIssuesReferences": [],
            },
            {
                "number": 5,
                "title": "Untouched",
                "url": "u5",
                "isDraft": False,
                "closingIssuesReferences": [],
            },
            {
                "number": 6,
                "title": "Approved but blocked",
                "url": "u6",
                "isDraft": False,
                "closingIssuesReferences": [],
            },
        ],
    )
    responses = _base_responses(your_prs=your_prs)
    for number, review_state, thread_resolutions, mergeable, checks_state in (
        (2, "APPROVED", [True], "MERGEABLE", None),
        (3, "APPROVED", [False], "MERGEABLE", None),
        (4, "CHANGES_REQUESTED", [False], "MERGEABLE", None),
        (5, None, None, "MERGEABLE", None),
        (6, "APPROVED", [True], "CONFLICTING", "FAILURE"),
    ):
        key, body = _review_state_response(
            number=number,
            review_state=review_state,
            thread_resolutions=thread_resolutions,
            mergeable=mergeable,
            checks_state=checks_state,
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
        "Approved",
        "Approved",
        "Approved",
        "Changes requested",
        "No reviews",
    ]
    assert (yours[2]["conflicting"], yours[2]["checks"]) == ("Yes", "Failing")

    drafts = result["your_draft_prs"]
    assert drafts == [
        {
            "number": 1,
            "title": "Draft",
            "url": "u1",
            "linked_issue": {"number": 42, "url": "issue-url"},
        },
    ]


def test_main_draft_prs_without_linked_issue_report_null(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A draft with no closing issue reference reports linked_issue as null."""
    your_prs = json.dumps(
        [
            {
                "number": 5,
                "title": "Untouched draft",
                "url": "u5",
                "isDraft": True,
                "closingIssuesReferences": [],
            },
        ],
    )
    _install_gh(monkeypatch, _base_responses(your_prs=your_prs))

    ct.main()

    result = json.loads(capsys.readouterr().out)
    assert result["your_draft_prs"] == [
        {"number": 5, "title": "Untouched draft", "url": "u5", "linked_issue": None},
    ]
