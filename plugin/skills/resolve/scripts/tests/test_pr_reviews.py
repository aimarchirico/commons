"""Tests for pr_reviews.py in resolve skill."""

import json

import pr_reviews


def test_request_re_reviews_requests_reviewers_excluding_user() -> None:
    """Re-requests reviews from past reviewers excluding the current user."""
    reviews_data = json.dumps(
        {
            "reviews": [
                {"author": {"login": "alice"}},
                {"author": {"login": "bob"}},
                {"author": {"login": "me"}},
            ],
        },
    )

    calls = []

    def fake_run_cmd(args: list[str]) -> str:
        calls.append(args)
        if args[:4] == ["gh", "pr", "view", "123"]:
            return reviews_data
        if args[:3] == ["gh", "api", "user"]:
            return "me"
        return ""

    pr_reviews.request_re_reviews(fake_run_cmd, "123")
    assert ["gh", "pr", "edit", "123", "--add-reviewer", "alice"] in calls
    assert ["gh", "pr", "edit", "123", "--add-reviewer", "bob"] in calls
    assert ["gh", "pr", "edit", "123", "--add-reviewer", "me"] not in calls
