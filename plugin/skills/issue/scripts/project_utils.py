#!/usr/bin/env python3
"""Helper utilities for querying and validating GitHub Projects (v2)."""

import importlib.util
import json
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Any

MAX_PROJECTS = 10
SINGLE_MATCH = 1


def _load_project_preflight() -> ModuleType:
    shared_dir = Path(__file__).resolve().parent.parent.parent.parent / "shared"
    module_path = shared_dir / "project_preflight.py"
    spec = importlib.util.spec_from_file_location("project_preflight", module_path)
    if spec is None or spec.loader is None:
        msg = f"Cannot load project_preflight from {module_path}"
        raise ImportError(msg)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_project_preflight = _load_project_preflight()
_resolve_project_context = _project_preflight.resolve_project_context
_fetch_project_fields = _project_preflight.fetch_project_fields
ProjectPreflightError = _project_preflight.ProjectPreflightError


def _title_case_repo_name(repo_name: str) -> str:
    words = repo_name.replace("_", "-").split("-")
    return " ".join(word.capitalize() for word in words if word)


def get_project_context(
    run_cmd: Callable[..., str],
) -> tuple[str | None, int | None, str | None, str | None]:
    """Fetch repository context and query linked active GitHub Projects."""
    try:
        repo_output = run_cmd(["gh", "repo", "view", "--json", "owner,name"])
        repo_data = json.loads(repo_output)
        owner = str(repo_data["owner"]["login"])
    except (
        subprocess.CalledProcessError,
        json.JSONDecodeError,
        KeyError,
        TypeError,
    ) as e:
        return None, None, None, f"Could not retrieve GitHub repository context: {e}"

    try:
        ctx = _resolve_project_context(run_cmd)
    except ProjectPreflightError as e:
        return owner, None, None, str(e)
    else:
        return ctx[0], ctx[2], ctx[3], None


def get_project_fields(
    run_cmd: Callable[..., str],
    owner: str,
    project_number: int | None,
) -> tuple[str | None, str | None, dict[str, Any], list[str]]:
    """Retrieve Type and Priority field IDs and metadata for a project."""
    if not project_number:
        return None, None, {}, []
    return _fetch_project_fields(run_cmd, owner, project_number)


validate_item_options = _project_preflight.validate_item_options


def validate_project_setup(
    items: list[dict[str, Any]],
    field_ids: tuple[int | None, str | None, str | None, str | None],
    fields_data: dict[str, Any],
    error_info: tuple[str | None, list[str]],
) -> list[str]:
    """Validate project setup and ensure issue type/priority options exist."""
    project_number, _project_id, type_field_id, priority_field_id = field_ids
    context_error, fields_errors = error_info
    errors: list[str] = []

    if context_error is not None:
        errors.append(context_error)

    if project_number is not None:
        errors.extend(fields_errors)

    if type_field_id is not None or priority_field_id is not None:
        errors.extend(validate_item_options(items, fields_data))

    return errors


def set_project_field(
    run_cmd: Callable[..., str],
    item_id: str,
    project_id: str,
    field_target: tuple[str, str | None, str | None],
    fields_data: dict[str, Any],
) -> None:
    """Set a single-select custom field option on a project item."""
    field_name, field_id, val = field_target
    if not (val and field_id):
        return

    option_id = None
    for field in fields_data.get("fields", []):
        if field.get("name") == field_name:
            for opt in field.get("options", []):
                if opt.get("name") == val:
                    option_id = opt["id"]
                    break

    if option_id:
        sys.stdout.write(f"Setting project item {field_name} to '{val}'...\n")
        run_cmd(
            [
                "gh",
                "project",
                "item-edit",
                "--id",
                item_id,
                "--project-id",
                project_id,
                "--field-id",
                field_id,
                "--single-select-option-id",
                option_id,
            ],
        )
