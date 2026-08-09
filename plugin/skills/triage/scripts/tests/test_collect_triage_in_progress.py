"""Tests for collect_triage.py's In Progress category."""

import json

import collect_triage as ct
import pytest
from collect_triage_helpers import (
    _base_responses,
    _install_gh,
    _issues_deps_response,
    _make_pr,
    _review_states_response,
)


def _make_in_progress_item(
    *,
    number: int,
    priority: str = "Medium",
) -> dict[str, object]:
    return {
        "type": "Task",
        "priority": priority,
        "content": {
            "type": "Issue",
            "number": number,
            "title": f"In progress {number}",
            "url": f"https://github.com/acme/widgets/issues/{number}",
        },
    }


def test_main_lists_in_progress_issues_without_an_open_pr(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """In Progress issues assigned to you surface unless a PR already closes them."""
    in_progress_items = json.dumps(
        {
            "items": [
                _make_in_progress_item(number=7),
                _make_in_progress_item(number=8),
            ],
        },
    )
    your_prs = json.dumps(
        [_make_pr(num=1, title="Closes 7", refs=[{"number": 7, "url": "issue-url"}])],
    )
    responses = _base_responses(your_prs=your_prs, in_progress_items=in_progress_items)
    k, b = _review_states_response({1: {}})
    responses[k] = b
    k, b = _issues_deps_response({7: {}, 8: {}})
    responses[k] = b
    _install_gh(monkeypatch, responses)

    ct.main()

    result = json.loads(capsys.readouterr().out)
    in_progress = result["categories"]["actionable_items"]["in_progress"]
    assert [issue["number"] for issue in in_progress] == [8]
    assert in_progress[0]["suggestion"] == "Continue implementing or open PR"
