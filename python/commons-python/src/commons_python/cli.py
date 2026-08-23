"""Dispatching CLI that wraps Astral's tools with the bundled Commons config."""

import importlib.resources
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path
from typing import Any

import tomli_w

from commons_python import line_length


def _run_wrapped(
    binary: str,
    config_flag: str,
    asset_name: str,
    args: list[str],
) -> int:
    asset = importlib.resources.files("commons_python.assets") / asset_name
    with importlib.resources.as_file(asset) as config_path:
        subcommand, *rest = args
        command = [binary, subcommand, config_flag, str(config_path), *rest]
        result = subprocess.run(command, check=False)
    return result.returncode


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        base_value = merged.get(key)
        if isinstance(value, dict) and isinstance(base_value, dict):
            merged[key] = _deep_merge(base_value, value)
        elif isinstance(value, list) and isinstance(base_value, list):
            merged[key] = base_value + [v for v in value if v not in base_value]
        else:
            merged[key] = value
    return merged


def _resolve_ruff_config(bundled_path: Path, tmp_dir: str) -> Path:
    local_config = Path.cwd() / "ruff.toml"
    if not local_config.exists():
        return bundled_path

    base_config = tomllib.loads(bundled_path.read_text())
    local_overrides = tomllib.loads(local_config.read_text())
    merged_path = Path(tmp_dir) / "ruff.toml"
    merged_path.write_text(tomli_w.dumps(_deep_merge(base_config, local_overrides)))
    return merged_path


def _run_ruff(args: list[str]) -> int:
    asset = importlib.resources.files("commons_python.assets") / "ruff.toml"
    with (
        importlib.resources.as_file(asset) as bundled_path,
        tempfile.TemporaryDirectory() as tmp_dir,
    ):
        config_path = _resolve_ruff_config(bundled_path, tmp_dir)
        subcommand, *rest = args
        command = ["ruff", subcommand, "--config", str(config_path), *rest]
        result = subprocess.run(command, check=False)
    return result.returncode


def main() -> None:
    """Dispatch to a wrapped tool based on the first argument.

    ``ruff``, ``ty``, ``pytest``, and ``coverage`` forward their remaining
    arguments untouched to the respective tool, with the bundled config
    injected. ``ruff`` additionally layers a ``ruff.toml`` from the current
    directory on top of the bundled config, if one exists. ``commons check``
    runs the native line-length check.
    """
    tool, *rest = sys.argv[1:] or [""]

    if tool == "commons":
        subcommand = rest[0] if rest else ""
        paths = rest[1:] or ["."]
        if subcommand == "check":
            sys.exit(line_length.check_line_length(paths))
    if tool == "ruff":
        sys.exit(_run_ruff(rest))
    if tool == "ty":
        sys.exit(_run_wrapped("ty", "--config-file", "ty.toml", rest))
    if tool == "pytest":
        asset = importlib.resources.files("commons_python.assets") / "coverage.toml"
        with importlib.resources.as_file(asset) as config_path:
            cov_args = [] if any(a.startswith("--cov") for a in rest) else ["--cov=."]
            command = ["pytest", *cov_args, "--cov-config", str(config_path), *rest]
            result = subprocess.run(command, check=False)
        sys.exit(result.returncode)
    if tool == "coverage":
        sys.exit(_run_wrapped("coverage", "--rcfile", "coverage.toml", rest))

    sys.stderr.write(
        "usage: commons-python <ruff|ty|pytest|coverage|commons> ...\n",
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
