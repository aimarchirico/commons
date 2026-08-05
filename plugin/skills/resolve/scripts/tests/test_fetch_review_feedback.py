"""Tests for fetch_review_feedback.py, covering both the library call and CLI."""

import json
import subprocess
import sys

import fetch_review_feedback as frf
import pytest

_REPO_OUTPUT = json.dumps({"owner": {"login": "acme"}, "name": "widgets"})
_MERGEABLE_OUTPUT = json.dumps({"mergeable": "MERGEABLE"})
_CHECKS_OUTPUT = json.dumps([])


def _pr_response(
    *, comments: list[dict[str, object]], reviews: list[dict[str, object]],
    threads: list[dict[str, object]],
) -> str:
    return json.dumps({"data": {"repository": {"pullRequest": {
        "comments": {"nodes": comments},
        "reviews": {"nodes": reviews},
        "reviewThreads": {"nodes": threads},
    }}}})


def _dispatch(
    args: list[str], graphql_response: str,
    *, mergeable: str = _MERGEABLE_OUTPUT, checks: str = _CHECKS_OUTPUT,
) -> str:
    if args[:3] == ["gh", "repo", "view"]:
        return _REPO_OUTPUT
    if args[:3] == ["gh", "pr", "view"]:
        return mergeable
    if args[:3] == ["gh", "pr", "checks"]:
        return checks
    return graphql_response


def test_fetch_review_feedback_collects_comments_and_bodied_reviews() -> None:
    """Comments include issue comments and reviews with a body, since createdAt."""
    def fake_run_cmd(args: list[str]) -> str:
        return _dispatch(args, _pr_response(
            comments=[
                {
                    "databaseId": 1, "body": "hi", "author": {"login": "bob"},
                    "createdAt": "2024-01-01T00:00:00Z",
                },
            ],
            reviews=[
                {
                    "databaseId": 2, "body": "LGTM", "author": {"login": "carol"},
                    "createdAt": "2024-01-02T00:00:00Z",
                },
                {
                    "databaseId": 3, "body": "", "author": {"login": "dave"},
                    "createdAt": "2024-01-03T00:00:00Z",
                },
            ],
            threads=[],
        ))

    result = frf.fetch_review_feedback(fake_run_cmd, "42")

    assert result["comments"] == [
        {"id": 1, "body": "hi", "author": "bob"},
        {"id": 2, "body": "LGTM", "author": "carol"},
    ]


def test_fetch_review_feedback_drops_comments_before_the_checkpoint() -> None:
    """Only comments after the last Resolved. checkpoint are returned."""
    def fake_run_cmd(args: list[str]) -> str:
        return _dispatch(args, _pr_response(
            comments=[
                {
                    "databaseId": 1, "body": "Please fix this.",
                    "author": {"login": "bob"}, "createdAt": "2024-01-01T00:00:00Z",
                },
                {
                    "databaseId": 2, "body": "Resolved. Fixed it.",
                    "author": {"login": "carol"}, "createdAt": "2024-01-02T00:00:00Z",
                },
                {
                    "databaseId": 3, "body": "One more thing.",
                    "author": {"login": "bob"}, "createdAt": "2024-01-03T00:00:00Z",
                },
            ],
            reviews=[],
            threads=[],
        ))

    result = frf.fetch_review_feedback(fake_run_cmd, "42")

    assert result["comments"] == [
        {"id": 3, "body": "One more thing.", "author": "bob"},
    ]


def test_fetch_review_feedback_drops_resolved_threads() -> None:
    """Only unresolved review threads are included, with their comments."""
    def fake_run_cmd(args: list[str]) -> str:
        return _dispatch(args, _pr_response(
            comments=[], reviews=[],
            threads=[
                {
                    "id": "t1", "isResolved": True, "path": "a.py", "line": 1,
                    "comments": {"nodes": []},
                },
                {
                    "id": "t2", "isResolved": False, "path": "b.py", "line": 2,
                    "comments": {"nodes": [
                        {"databaseId": 9, "body": "fix this", "author": None},
                    ]},
                },
            ],
        ))

    result = frf.fetch_review_feedback(fake_run_cmd, "42")

    assert result["threads"] == [{
        "thread_id": "t2", "path": "b.py", "line": 2,
        "comments": [{"id": 9, "body": "fix this", "author": None}],
    }]


def test_fetch_review_feedback_reports_conflicting_and_failing_checks() -> None:
    """Conflicting mergeable state and failing checks are surfaced."""
    def fake_run_cmd(args: list[str]) -> str:
        return _dispatch(
            args, _pr_response(comments=[], reviews=[], threads=[]),
            mergeable=json.dumps({"mergeable": "CONFLICTING"}),
            checks=json.dumps([
                {"name": "lint", "bucket": "fail", "link": "https://x/lint"},
                {"name": "tests", "bucket": "pass", "link": "https://x/tests"},
            ]),
        )

    result = frf.fetch_review_feedback(fake_run_cmd, "42")

    assert result["conflicting"] is True
    assert result["failing_checks"] == [{"name": "lint", "link": "https://x/lint"}]


def test_fetch_review_feedback_treats_missing_checks_as_none_failing() -> None:
    """If `gh pr checks` errors (e.g. no checks configured), default to none."""
    def fake_run_cmd(args: list[str]) -> str:
        if args[:3] == ["gh", "pr", "checks"]:
            raise subprocess.CalledProcessError(1, args)
        return _dispatch(args, _pr_response(comments=[], reviews=[], threads=[]))

    result = frf.fetch_review_feedback(fake_run_cmd, "42")

    assert result["failing_checks"] == []


def test_main_exits_when_pr_number_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """main() exits with an error when no PR number is given."""
    monkeypatch.setattr(sys, "argv", ["fetch_review_feedback"])

    with pytest.raises(SystemExit):
        frf.main()


def test_main_exits_when_gh_is_not_installed(monkeypatch: pytest.MonkeyPatch) -> None:
    """main() fails fast when the gh CLI isn't on PATH."""
    monkeypatch.setattr(sys, "argv", ["fetch_review_feedback", "42"])
    monkeypatch.setattr(frf.shutil, "which", lambda _name: None)

    with pytest.raises(SystemExit):
        frf.main()


def test_main_prints_feedback_as_json(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """main() prints the collected feedback as indented JSON."""
    monkeypatch.setattr(sys, "argv", ["fetch_review_feedback", "42"])
    monkeypatch.setattr(frf.shutil, "which", lambda _name: "/usr/bin/gh")

    def fake_run_cmd(args: list[str]) -> str:
        return _dispatch(args, _pr_response(comments=[], reviews=[], threads=[]))

    monkeypatch.setattr(frf, "_run_cmd", fake_run_cmd)

    frf.main()

    printed = json.loads(capsys.readouterr().out)
    assert printed == {
        "threads": [], "comments": [], "conflicting": False, "failing_checks": [],
    }


def test_main_exits_when_gh_command_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    """main() exits cleanly when the underlying gh call fails."""
    monkeypatch.setattr(sys, "argv", ["fetch_review_feedback", "42"])
    monkeypatch.setattr(frf.shutil, "which", lambda _name: "/usr/bin/gh")

    def fake_run_cmd(args: list[str]) -> str:
        raise subprocess.CalledProcessError(1, args)

    monkeypatch.setattr(frf, "_run_cmd", fake_run_cmd)

    with pytest.raises(SystemExit):
        frf.main()
