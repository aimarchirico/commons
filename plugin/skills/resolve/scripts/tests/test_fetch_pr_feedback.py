"""Tests for fetch_pr_feedback.py, covering both the library call and the CLI."""

import json
import subprocess
import sys

import fetch_pr_feedback as fpf
import pytest

_REPO_OUTPUT = json.dumps({"owner": {"login": "acme"}, "name": "widgets"})


def _pr_response(
    *, comments: list[dict[str, object]], reviews: list[dict[str, object]],
    threads: list[dict[str, object]],
) -> str:
    return json.dumps({"data": {"repository": {"pullRequest": {
        "comments": {"nodes": comments},
        "reviews": {"nodes": reviews},
        "reviewThreads": {"nodes": threads},
    }}}})


def test_fetch_pr_feedback_collects_comments_and_bodied_reviews() -> None:
    """Conversation comments include issue comments and reviews with a body."""
    def fake_run_cmd(args: list[str]) -> str:
        if args[:3] == ["gh", "repo", "view"]:
            return _REPO_OUTPUT
        return _pr_response(
            comments=[
                {"databaseId": 1, "body": "hi", "author": {"login": "bob"}},
            ],
            reviews=[
                {"databaseId": 2, "body": "LGTM", "author": {"login": "carol"}},
                {"databaseId": 3, "body": "", "author": {"login": "dave"}},
            ],
            threads=[],
        )

    result = fpf.fetch_pr_feedback(fake_run_cmd, "42")

    assert result["conversation_comments"] == [
        {"id": 1, "body": "hi", "author": "bob"},
        {"id": 2, "body": "LGTM", "author": "carol"},
    ]


def test_fetch_pr_feedback_drops_resolved_threads() -> None:
    """Only unresolved review threads are included, with their comments."""
    def fake_run_cmd(args: list[str]) -> str:
        if args[:3] == ["gh", "repo", "view"]:
            return _REPO_OUTPUT
        return _pr_response(
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
        )

    result = fpf.fetch_pr_feedback(fake_run_cmd, "42")

    assert result["review_threads"] == [{
        "thread_id": "t2", "path": "b.py", "line": 2,
        "comments": [{"id": 9, "body": "fix this", "author": None}],
    }]


def test_main_exits_when_pr_number_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """main() exits with an error when no PR number is given."""
    monkeypatch.setattr(sys, "argv", ["fetch_pr_feedback"])

    with pytest.raises(SystemExit):
        fpf.main()


def test_main_exits_when_gh_is_not_installed(monkeypatch: pytest.MonkeyPatch) -> None:
    """main() fails fast when the gh CLI isn't on PATH."""
    monkeypatch.setattr(sys, "argv", ["fetch_pr_feedback", "42"])
    monkeypatch.setattr(fpf.shutil, "which", lambda _name: None)

    with pytest.raises(SystemExit):
        fpf.main()


def test_main_prints_feedback_as_json(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """main() prints the collected feedback as indented JSON."""
    monkeypatch.setattr(sys, "argv", ["fetch_pr_feedback", "42"])
    monkeypatch.setattr(fpf.shutil, "which", lambda _name: "/usr/bin/gh")

    def fake_run_cmd(args: list[str]) -> str:
        if args[:3] == ["gh", "repo", "view"]:
            return _REPO_OUTPUT
        return _pr_response(comments=[], reviews=[], threads=[])

    monkeypatch.setattr(fpf, "_run_cmd", fake_run_cmd)

    fpf.main()

    printed = json.loads(capsys.readouterr().out)
    assert printed == {"conversation_comments": [], "review_threads": []}


def test_main_exits_when_gh_command_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    """main() exits cleanly when the underlying gh call fails."""
    monkeypatch.setattr(sys, "argv", ["fetch_pr_feedback", "42"])
    monkeypatch.setattr(fpf.shutil, "which", lambda _name: "/usr/bin/gh")

    def fake_run_cmd(args: list[str]) -> str:
        raise subprocess.CalledProcessError(1, args)

    monkeypatch.setattr(fpf, "_run_cmd", fake_run_cmd)

    with pytest.raises(SystemExit):
        fpf.main()
