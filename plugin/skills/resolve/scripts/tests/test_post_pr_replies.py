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
        fake_run_cmd, "42",
        [{"comment_id": 1, "body": "fixed"}, {"comment_id": 2, "body": "done"}],
        "All resolved.",
    )

    thread_call_1, thread_call_2, conversation_call = calls[1], calls[2], calls[3]
    assert thread_call_1[0][2] == "repos/acme/widgets/pulls/42/comments/1/replies"
    assert json.loads(thread_call_1[1] or "") == {"body": "fixed"}
    assert thread_call_2[0][2] == "repos/acme/widgets/pulls/42/comments/2/replies"
    assert conversation_call[0][2] == "repos/acme/widgets/issues/42/comments"
    assert json.loads(conversation_call[1] or "") == {"body": "All resolved."}


def test_post_replies_skips_conversation_reply_when_empty() -> None:
    """No conversation-level call is made when conversation_reply is empty."""
    calls: list[list[str]] = []

    def fake_run_cmd(args: list[str], input_text: str | None = None) -> str:
        del input_text
        calls.append(args)
        return _REPO_OUTPUT if args[:3] == ["gh", "repo", "view"] else "{}"

    ppr.post_replies(fake_run_cmd, "42", [], "")

    assert len(calls) == 1


def test_main_exits_when_args_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """main() exits with an error when the PR number or file path is missing."""
    monkeypatch.setattr(sys, "argv", ["post_pr_replies", "42"])

    with pytest.raises(SystemExit):
        ppr.main()


def test_main_exits_when_gh_is_not_installed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    """main() fails fast when the gh CLI isn't on PATH."""
    replies_file = tmp_path / "replies.json"
    replies_file.write_text("{}")
    monkeypatch.setattr(sys, "argv", ["post_pr_replies", "42", str(replies_file)])
    monkeypatch.setattr(ppr.shutil, "which", lambda _name: None)

    with pytest.raises(SystemExit):
        ppr.main()


def test_main_exits_when_json_file_is_invalid(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    """main() exits cleanly when the replies file isn't valid JSON."""
    replies_file = tmp_path / "replies.json"
    replies_file.write_text("not json")
    monkeypatch.setattr(sys, "argv", ["post_pr_replies", "42", str(replies_file)])
    monkeypatch.setattr(ppr.shutil, "which", lambda _name: "/usr/bin/gh")

    with pytest.raises(SystemExit):
        ppr.main()


def test_main_posts_replies_and_deletes_the_file_on_success(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """main() posts replies, prints a confirmation, and cleans up the file."""
    replies_file = tmp_path / "replies.json"
    replies_file.write_text(json.dumps({
        "thread_replies": [], "conversation_reply": "",
    }))
    monkeypatch.setattr(sys, "argv", ["post_pr_replies", "42", str(replies_file)])
    monkeypatch.setattr(ppr.shutil, "which", lambda _name: "/usr/bin/gh")

    def fake_run_cmd(args: list[str], input_text: str | None = None) -> str:
        del input_text
        return _REPO_OUTPUT if args[:3] == ["gh", "repo", "view"] else "{}"

    monkeypatch.setattr(ppr, "_run_cmd", fake_run_cmd)

    ppr.main()

    assert "Successfully posted all replies." in capsys.readouterr().out
    assert not replies_file.exists()


def test_main_exits_and_cleans_up_when_gh_command_fails(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    """main() exits and still deletes the file when the gh call fails."""
    replies_file = tmp_path / "replies.json"
    replies_file.write_text(json.dumps({
        "thread_replies": [], "conversation_reply": "",
    }))
    monkeypatch.setattr(sys, "argv", ["post_pr_replies", "42", str(replies_file)])
    monkeypatch.setattr(ppr.shutil, "which", lambda _name: "/usr/bin/gh")

    def fake_run_cmd(args: list[str], input_text: str | None = None) -> str:
        del input_text, args
        raise subprocess.CalledProcessError(1, ["gh"])

    monkeypatch.setattr(ppr, "_run_cmd", fake_run_cmd)

    with pytest.raises(SystemExit):
        ppr.main()

    assert not replies_file.exists()
