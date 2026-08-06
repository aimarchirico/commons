"""Tests for post_pr_replies.py, covering both the library call and the CLI."""

import json
import subprocess
import sys
from pathlib import Path

import post_pr_replies as ppr
import pytest

_REPO_OUTPUT = json.dumps({"owner": {"login": "acme"}, "name": "widgets"})


def test_post_replies_replies_to_each_thread_then_the_conversation() -> None:
    """Posts one reply per thread comment, then one conversation-level reply."""
    calls: list[tuple[list[str], str | None]] = []

    def fake_run_cmd(args: list[str], input_text: str | None = None) -> str:
        calls.append((args, input_text))
        return _REPO_OUTPUT if args[:3] == ["gh", "repo", "view"] else "{}"

    ppr.post_replies(
        fake_run_cmd,
        "42",
        [
            {"comment_id": 1, "thread_id": "T_1", "body": "fixed"},
            {"comment_id": 2, "thread_id": "T_2", "body": "done"},
        ],
        "Addressed the null-check feedback.",
    )

    thread_call_1, thread_call_2 = calls[1], calls[2]
    assert thread_call_1[0][2] == "repos/acme/widgets/pulls/42/comments/1/replies"
    assert json.loads(thread_call_1[1] or "") == {"body": "fixed"}
    assert thread_call_2[0][2] == "repos/acme/widgets/pulls/42/comments/2/replies"

    conversation_call = calls[-1]
    assert conversation_call[0][2] == "repos/acme/widgets/issues/42/comments"
    assert json.loads(conversation_call[1] or "") == {
        "body": (
            "## Resolution summary\n\nResolved. Addressed the null-check feedback."
        ),
    }


def test_post_replies_resolves_each_unique_thread_once() -> None:
    """Each distinct thread_id is resolved once, even with multiple replies."""
    calls: list[list[str]] = []

    def fake_run_cmd(args: list[str], input_text: str | None = None) -> str:
        del input_text
        calls.append(args)
        return _REPO_OUTPUT if args[:3] == ["gh", "repo", "view"] else "{}"

    ppr.post_replies(
        fake_run_cmd,
        "42",
        [
            {"comment_id": 1, "thread_id": "T_1", "body": "fixed"},
            {"comment_id": 2, "thread_id": "T_1", "body": "also fixed"},
            {"comment_id": 3, "thread_id": "T_2", "body": "done"},
        ],
        "",
    )

    resolve_calls = [c for c in calls if c[:3] == ["gh", "api", "graphql"]]
    resolved_thread_ids = {c[4].removeprefix("threadId=") for c in resolve_calls}
    assert resolved_thread_ids == {"T_1", "T_2"}


def test_render_conversation_reply_leads_with_header_then_verdict() -> None:
    """The header comes first, then the literal Resolved. verdict."""
    body = ppr.render_conversation_reply("Fixed the thing.")

    assert body == "## Resolution summary\n\nResolved. Fixed the thing."


def test_post_replies_skips_conversation_reply_when_empty() -> None:
    """No conversation-level call is made when conversation_summary is empty."""
    calls: list[list[str]] = []

    def fake_run_cmd(args: list[str], input_text: str | None = None) -> str:
        del input_text
        calls.append(args)
        return _REPO_OUTPUT if args[:3] == ["gh", "repo", "view"] else "{}"

    ppr.post_replies(fake_run_cmd, "42", [], "")

    assert len(calls) == 1


def test_request_re_reviews_requests_from_all_reviewers_except_the_user() -> None:
    """Re-review is requested from every unique prior reviewer except the user."""
    calls: list[list[str]] = []

    def fake_run_cmd(args: list[str], input_text: str | None = None) -> str:
        del input_text
        calls.append(args)
        if args[:3] == ["gh", "pr", "view"]:
            return json.dumps(
                {
                    "reviews": [
                        {"author": {"login": "alice"}},
                        {"author": {"login": "bob"}},
                        {"author": {"login": "alice"}},
                    ],
                },
            )
        return "bob"

    ppr.request_re_reviews(fake_run_cmd, "42")

    add_reviewer_calls = [c for c in calls if c[:3] == ["gh", "pr", "edit"]]
    assert add_reviewer_calls == [["gh", "pr", "edit", "42", "--add-reviewer", "alice"]]


def test_main_exits_when_args_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """main() exits with an error when the PR number or file path is missing."""
    monkeypatch.setattr(sys, "argv", ["post_pr_replies", "42"])

    with pytest.raises(SystemExit):
        ppr.main()


def test_main_exits_when_gh_is_not_installed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """main() fails fast when the gh CLI isn't on PATH."""
    replies_file = tmp_path / "replies.json"
    replies_file.write_text("{}")
    monkeypatch.setattr(sys, "argv", ["post_pr_replies", "42", str(replies_file)])
    monkeypatch.setattr(ppr.project_preflight.shutil, "which", lambda _name: None)

    with pytest.raises(SystemExit):
        ppr.main()


def test_main_exits_when_json_file_is_invalid(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """main() exits cleanly when the replies file isn't valid JSON."""
    replies_file = tmp_path / "replies.json"
    replies_file.write_text("not json")
    monkeypatch.setattr(sys, "argv", ["post_pr_replies", "42", str(replies_file)])
    monkeypatch.setattr(
        ppr.project_preflight.shutil,
        "which",
        lambda _name: "/usr/bin/gh",
    )
    monkeypatch.setattr(
        ppr.project_preflight.subprocess,
        "run",
        lambda *_a, **_k: None,
    )

    with pytest.raises(SystemExit):
        ppr.main()


def test_main_posts_replies_and_deletes_the_file_on_success(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """main() posts replies, prints a confirmation, and cleans up the file."""
    replies_file = tmp_path / "replies.json"
    replies_file.write_text(
        json.dumps(
            {
                "thread_replies": [],
                "conversation_summary": "",
            },
        ),
    )
    monkeypatch.setattr(sys, "argv", ["post_pr_replies", "42", str(replies_file)])
    monkeypatch.setattr(
        ppr.project_preflight.shutil,
        "which",
        lambda _name: "/usr/bin/gh",
    )
    monkeypatch.setattr(
        ppr.project_preflight.subprocess,
        "run",
        lambda *_a, **_k: None,
    )

    def fake_run_cmd(args: list[str], input_text: str | None = None) -> str:
        del input_text
        return _REPO_OUTPUT if args[:3] == ["gh", "repo", "view"] else "{}"

    monkeypatch.setattr(ppr, "_run_cmd", fake_run_cmd)

    ppr.main()

    assert "Successfully posted all replies." in capsys.readouterr().out
    assert not replies_file.exists()


def test_main_exits_and_cleans_up_when_gh_command_fails(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """main() exits and still deletes the file when the gh call fails."""
    replies_file = tmp_path / "replies.json"
    replies_file.write_text(
        json.dumps(
            {
                "thread_replies": [],
                "conversation_summary": "",
            },
        ),
    )
    monkeypatch.setattr(sys, "argv", ["post_pr_replies", "42", str(replies_file)])
    monkeypatch.setattr(
        ppr.project_preflight.shutil,
        "which",
        lambda _name: "/usr/bin/gh",
    )
    monkeypatch.setattr(
        ppr.project_preflight.subprocess,
        "run",
        lambda *_a, **_k: None,
    )

    def fake_run_cmd(args: list[str], input_text: str | None = None) -> str:
        del input_text, args
        raise subprocess.CalledProcessError(1, ["gh"])

    monkeypatch.setattr(ppr, "_run_cmd", fake_run_cmd)

    with pytest.raises(SystemExit):
        ppr.main()

    assert not replies_file.exists()
