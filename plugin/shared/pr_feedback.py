"""Partition raw PR review-thread and comment nodes into open feedback.

Used by both the ``triage`` skill (to compute an aggregate state) and the
``resolve`` skill (to get the actual items to draft fixes for), so both
agree on what counts as "unresolved" instead of maintaining separate,
possibly diverging definitions. Dynamically loaded by path from each
consuming script rather than as an installed package, since skill
scripts run as plain ``python3 script.py`` with no venv/dependency setup.
"""

from typing import Any

RESOLVED_VERDICT_PREFIX = "Resolved."


def _first_substantive_line(body: str) -> str:
    for line in body.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped
    return ""


def unresolved_threads(threads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return the review threads whose ``isResolved`` field is falsy."""
    return [t for t in threads if not t.get("isResolved")]


def comments_since_checkpoint(comments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return comments after the last ``Resolved.`` checkpoint, sorted by time.

    A checkpoint is a comment whose first substantive line (ignoring
    leading blank/header lines) starts with the verdict ``Resolved.``. If no
    checkpoint exists, every comment is returned.
    """
    ordered = sorted(comments, key=lambda c: c["createdAt"])

    checkpoint_index = None
    for i, comment in enumerate(ordered):
        if _first_substantive_line(comment["body"]).startswith(RESOLVED_VERDICT_PREFIX):
            checkpoint_index = i

    if checkpoint_index is None:
        return ordered
    return ordered[checkpoint_index + 1 :]
