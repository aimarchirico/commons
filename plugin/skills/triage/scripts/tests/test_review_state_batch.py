"""Tests for review_state.py's batched fetch_review_states."""

from typing import Any

from review_state import fetch_review_states
from review_state_fixtures import pr_state_fields


def test_fetch_review_states_batches_multiple_numbers_in_one_call() -> None:
    """Aliases each PR number in a single request and keys results by number."""
    response = {
        "data": {
            "repository": {
                "pr2": pr_state_fields(
                    review_state="APPROVED",
                    thread_resolutions=[True],
                    comment_bodies=[],
                ),
                "pr3": pr_state_fields(
                    review_state=None,
                    thread_resolutions=[],
                    comment_bodies=[],
                ),
            },
        },
    }
    calls: list[tuple[str, dict[str, Any]]] = []

    def fake_graphql(query: str, **variables: object) -> dict:
        calls.append((query, variables))
        return response

    result = fetch_review_states(fake_graphql, "acme", "widgets", [2, 3])

    assert len(calls) == 1
    query = calls[0][0]
    assert "pr2: pullRequest(number: 2)" in query
    assert "pr3: pullRequest(number: 3)" in query
    assert result[2]["state"] == "approved"
    assert result[3]["state"] == "no_reviews"


def test_fetch_review_states_returns_empty_dict_for_no_numbers() -> None:
    """Skips the API call entirely when there's nothing to fetch."""
    calls = []

    def fake_graphql(query: str, **variables: object) -> dict:
        calls.append((query, variables))
        return {}

    assert fetch_review_states(fake_graphql, "acme", "widgets", []) == {}
    assert calls == []
