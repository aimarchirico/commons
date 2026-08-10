"""Tests for the shared fetch_issue_tree module."""

import json

from shared.issue_tree import fetch_issue_tree, flatten_issue_numbers


def _type_field(type_name: str | None) -> dict:
    nodes = [{"fieldValueByName": {"name": type_name}}] if type_name else []
    return {"projectItems": {"nodes": nodes}}


def _issue(
    number: int,
    title: str,
    body: str | None = "",
    type_name: str | None = None,
    children: list[dict] | None = None,
) -> dict:
    node = {
        "number": number,
        "title": title,
        "body": body,
        **_type_field(type_name),
    }
    if children is not None:
        node["subIssues"] = {"nodes": children}
    return node


def test_fetch_issue_tree_parses_leaf_issue_with_no_children() -> None:
    """A leaf issue with no sub-issues returns an empty children list."""
    root = _issue(1, "Leaf issue", "Some body", "Subtask")
    api_response = json.dumps({"data": {"repository": {"issue": root}}})

    def mock_run_cmd(_args: list[str]) -> str:
        return api_response

    tree = fetch_issue_tree(mock_run_cmd, "owner", "repo", 1)

    assert tree == {
        "number": 1,
        "title": "Leaf issue",
        "body": "Some body",
        "type": "Subtask",
        "children": [],
    }


def test_fetch_issue_tree_recurses_one_level_of_children() -> None:
    """Direct sub-issues are parsed into the children list."""
    root = _issue(
        1,
        "Parent",
        "Parent body",
        "Task",
        children=[
            _issue(2, "Child A", "Body A", "Subtask", children=[]),
            _issue(3, "Child B", "Body B", "Subtask", children=[]),
        ],
    )
    api_response = json.dumps({"data": {"repository": {"issue": root}}})

    def mock_run_cmd(_args: list[str]) -> str:
        return api_response

    tree = fetch_issue_tree(mock_run_cmd, "owner", "repo", 1)

    assert [c["number"] for c in tree["children"]] == [2, 3]
    assert tree["children"][0]["title"] == "Child A"
    assert tree["children"][1]["body"] == "Body B"


def test_fetch_issue_tree_recurses_two_levels_hitting_the_depth_bound() -> None:
    """Grandchildren (Epic -> Story -> Subtask depth) are still captured."""
    root = _issue(
        1,
        "Epic",
        "Epic body",
        "Epic",
        children=[
            _issue(
                2,
                "Story",
                "Story body",
                "Story",
                children=[
                    _issue(3, "Subtask", "Subtask body", "Subtask", children=[]),
                ],
            ),
        ],
    )
    api_response = json.dumps({"data": {"repository": {"issue": root}}})

    def mock_run_cmd(_args: list[str]) -> str:
        return api_response

    tree = fetch_issue_tree(mock_run_cmd, "owner", "repo", 1)

    grandchild = tree["children"][0]["children"][0]
    assert grandchild["number"] == 3
    assert grandchild["title"] == "Subtask"


def test_fetch_issue_tree_handles_missing_type_field() -> None:
    """An issue with no linked project Type field parses type as None."""
    root = _issue(1, "No type", "Body")
    api_response = json.dumps({"data": {"repository": {"issue": root}}})

    def mock_run_cmd(_args: list[str]) -> str:
        return api_response

    tree = fetch_issue_tree(mock_run_cmd, "owner", "repo", 1)

    assert tree["type"] is None


def test_fetch_issue_tree_defaults_null_body_to_empty_string() -> None:
    """A null body (issue with no description) parses as an empty string."""
    root = _issue(1, "No body", body=None)
    api_response = json.dumps({"data": {"repository": {"issue": root}}})

    def mock_run_cmd(_args: list[str]) -> str:
        return api_response

    tree = fetch_issue_tree(mock_run_cmd, "owner", "repo", 1)

    assert tree["body"] == ""


def test_flatten_issue_numbers_returns_parent_then_descendants_depth_first() -> None:
    """flatten_issue_numbers walks the parent then every descendant, in order."""
    tree = {
        "number": 1,
        "children": [
            {
                "number": 2,
                "children": [{"number": 4, "children": []}],
            },
            {"number": 3, "children": []},
        ],
    }

    assert flatten_issue_numbers(tree) == [1, 2, 4, 3]


def test_flatten_issue_numbers_returns_single_number_for_leaf() -> None:
    """A leaf tree with no children flattens to just its own number."""
    tree = {"number": 5, "children": []}

    assert flatten_issue_numbers(tree) == [5]
