"""Tests for the shared unresolved-threads/comments-since-checkpoint logic."""

from plugin_shared.pr_feedback import comments_since_checkpoint, unresolved_threads


def test_unresolved_threads_drops_resolved_ones() -> None:
    """Only threads with a falsy isResolved survive."""
    threads = [
        {"id": "T_1", "isResolved": True},
        {"id": "T_2", "isResolved": False},
        {"id": "T_3"},
    ]

    result = unresolved_threads(threads)

    assert [t["id"] for t in result] == ["T_2", "T_3"]


def test_comments_since_checkpoint_returns_all_when_no_checkpoint_exists() -> None:
    """With no Resolved. checkpoint, every comment is returned, sorted by time."""
    comments = [
        {"body": "Second.", "createdAt": "2024-01-02T00:00:00Z"},
        {"body": "First.", "createdAt": "2024-01-01T00:00:00Z"},
    ]

    result = comments_since_checkpoint(comments)

    assert [c["body"] for c in result] == ["First.", "Second."]


def test_comments_since_checkpoint_drops_everything_up_to_the_last_one() -> None:
    """Only comments after the most recent Resolved. checkpoint are returned."""
    comments = [
        {"body": "Please fix this.", "createdAt": "2024-01-01T00:00:00Z"},
        {"body": "Resolved. Fixed it.", "createdAt": "2024-01-02T00:00:00Z"},
        {"body": "One more thing.", "createdAt": "2024-01-03T00:00:00Z"},
    ]

    result = comments_since_checkpoint(comments)

    assert [c["body"] for c in result] == ["One more thing."]


def test_comments_since_checkpoint_returns_empty_when_checkpoint_is_latest() -> None:
    """If the last comment is itself the checkpoint, nothing is outstanding."""
    comments = [
        {"body": "Please fix this.", "createdAt": "2024-01-01T00:00:00Z"},
        {"body": "Resolved. Fixed it.", "createdAt": "2024-01-02T00:00:00Z"},
    ]

    result = comments_since_checkpoint(comments)

    assert result == []


def test_comments_since_checkpoint_recognizes_checkpoint_after_a_header() -> None:
    """A markdown header before the verdict line doesn't hide the checkpoint."""
    comments = [
        {"body": "Please fix this.", "createdAt": "2024-01-01T00:00:00Z"},
        {
            "body": "## Resolution summary\n\nResolved. Fixed it.",
            "createdAt": "2024-01-02T00:00:00Z",
        },
    ]

    result = comments_since_checkpoint(comments)

    assert result == []
