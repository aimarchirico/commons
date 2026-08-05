"""Tests for post_review_comments.py, covering both the library calls and CLI."""

import json
import subprocess
import sys
from pathlib import Path

import post_review_comments as prc
import pytest

_REPO_OUTPUT = json.dumps({"owner": {"login": "acme"}, "name": "widgets"})


def test_build_review_approves_when_there_are_no_findings() -> None:
    """An empty findings list renders the bare Approved. verdict."""
    review = prc.build_review([])

    assert review == {"body": "Approved.", "comments": []}


def test_build_review_renders_resolvable_findings_as_inline_comments() -> None:
    """Findings with a file/line become comments; the body counts them."""
    findings = [
        {
            "file": "a.py", "line": 3, "summary": "Off-by-one",
            "failure_scenario": "Loop runs one too many times.", "category": "logic",
        },
        {
            "file": "b.py", "line": 7, "summary": "Missing check",
            "failure_scenario": "Null dereference on empty input.",
            "category": "correctness",
        },
    ]

    review = prc.build_review(findings)

    assert review["comments"] == [
        {
            "path": "a.py", "line": 3,
            "body": "**Off-by-one**\n\nLoop runs one too many times.\n\n"
                    "_category: logic_",
        },
        {
            "path": "b.py", "line": 7,
            "body": "**Missing check**\n\nNull dereference on empty input.\n\n"
                    "_category: correctness_",
        },
    ]
    assert review["body"].startswith("## Review summary\n\nChanges requested.\n\n")
    assert "2 findings" in review["body"]
    assert "2 posted as inline comments" in review["body"]


def test_build_review_lists_unresolvable_findings_in_the_summary() -> None:
    """Findings without a resolvable file/line are listed, not posted inline."""
    findings = [
        {
            "file": "a.py", "line": 3, "summary": "Off-by-one",
            "failure_scenario": "Loop runs one too many times.", "category": "logic",
        },
        {
            "file": None, "line": None, "summary": "Design concern",
            "failure_scenario": "No single file to point at.",
            "category": "compliance",
        },
    ]

    review = prc.build_review(findings)

    assert len(review["comments"]) == 1
    assert "1 posted as inline comments" in review["body"]
    assert "no resolvable file/line" in review["body"]
    assert "**Design concern**: No single file to point at. " in review["body"]
    assert "(_category: compliance_)" in review["body"]


def test_post_review_sends_body_and_comments_to_the_reviews_endpoint() -> None:
    """Posts a single COMMENT-event review with the given body and comments."""
    calls: list[tuple[list[str], str | None]] = []

    def fake_run_cmd(args: list[str], input_text: str | None = None) -> str:
        calls.append((args, input_text))
        return _REPO_OUTPUT if args[:3] == ["gh", "repo", "view"] else "{}"

    comments = [{"path": "a.py", "line": 1, "body": "nit"}]
    prc.post_review(fake_run_cmd, "42", "Looks good", comments)

    endpoint_args, payload = calls[1]
    assert payload is not None
    assert endpoint_args[:2] == ["gh", "api"]
    assert endpoint_args[2] == "repos/acme/widgets/pulls/42/reviews"
    assert json.loads(payload) == {
        "event": "COMMENT", "body": "Looks good", "comments": comments,
    }


def test_main_exits_when_args_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """main() exits with an error when the PR number or file path is missing."""
    monkeypatch.setattr(sys, "argv", ["post_review_comments", "42"])

    with pytest.raises(SystemExit):
        prc.main()


def test_main_exits_when_gh_is_not_installed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    """main() fails fast when the gh CLI isn't on PATH."""
    findings_file = tmp_path / "findings.json"
    findings_file.write_text("[]")
    monkeypatch.setattr(
        sys, "argv", ["post_review_comments", "42", str(findings_file)],
    )
    monkeypatch.setattr(prc.shutil, "which", lambda _name: None)

    with pytest.raises(SystemExit):
        prc.main()


def test_main_exits_when_json_file_is_invalid(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    """main() exits cleanly when the findings file isn't valid JSON."""
    findings_file = tmp_path / "findings.json"
    findings_file.write_text("not json")
    monkeypatch.setattr(
        sys, "argv", ["post_review_comments", "42", str(findings_file)],
    )
    monkeypatch.setattr(prc.shutil, "which", lambda _name: "/usr/bin/gh")

    with pytest.raises(SystemExit):
        prc.main()


def test_main_posts_review_and_deletes_the_file_on_success(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """main() posts the review, prints a confirmation, and cleans up the file."""
    findings_file = tmp_path / "findings.json"
    findings_file.write_text("[]")
    monkeypatch.setattr(
        sys, "argv", ["post_review_comments", "42", str(findings_file)],
    )
    monkeypatch.setattr(prc.shutil, "which", lambda _name: "/usr/bin/gh")

    def fake_run_cmd(args: list[str], input_text: str | None = None) -> str:
        del input_text
        return _REPO_OUTPUT if args[:3] == ["gh", "repo", "view"] else "{}"

    monkeypatch.setattr(prc, "_run_cmd", fake_run_cmd)

    prc.main()

    assert "Posted review to PR #42." in capsys.readouterr().out
    assert not findings_file.exists()


def test_main_exits_and_cleans_up_when_gh_command_fails(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    """main() exits and still deletes the file when the gh call fails."""
    findings_file = tmp_path / "findings.json"
    findings_file.write_text("[]")
    monkeypatch.setattr(
        sys, "argv", ["post_review_comments", "42", str(findings_file)],
    )
    monkeypatch.setattr(prc.shutil, "which", lambda _name: "/usr/bin/gh")

    def fake_run_cmd(args: list[str], input_text: str | None = None) -> str:
        del input_text, args
        raise subprocess.CalledProcessError(1, ["gh"])

    monkeypatch.setattr(prc, "_run_cmd", fake_run_cmd)

    with pytest.raises(SystemExit):
        prc.main()

    assert not findings_file.exists()
