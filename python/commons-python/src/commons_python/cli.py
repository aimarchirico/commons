"""Dispatching CLI that wraps Astral's tools with the bundled Commons config."""

import importlib.resources
import subprocess
import sys


def _run_wrapped(
    binary: str, config_flag: str, asset_name: str, args: list[str]
) -> int:
    asset = importlib.resources.files("commons_python.assets") / asset_name
    with importlib.resources.as_file(asset) as config_path:
        subcommand, *rest = args
        command = [binary, subcommand, config_flag, str(config_path), *rest]
        result = subprocess.run(command, check=False)
    return result.returncode


def main() -> None:
    """Dispatch to a wrapped tool based on the first argument.

    ``ruff``, ``ty``, ``pytest``, and ``coverage`` forward their remaining
    arguments untouched to the respective tool, with the bundled config
    injected. ``commons check`` runs the native Python checks (line length
    and comments).
    """
    tool, *rest = sys.argv[1:] or [""]

    if tool == "commons":
        subcommand = rest[0] if rest else ""
        paths = rest[1:] or ["."]
        if subcommand == "check":
            from commons_python.comments import check_comments
            from commons_python.line_length import check_line_length

            line_length_rc = check_line_length(paths)
            comments_rc = check_comments(paths)
            sys.exit(1 if (line_length_rc or comments_rc) else 0)
    if tool == "ruff":
        sys.exit(_run_wrapped("ruff", "--config", "ruff.toml", rest))
    if tool == "ty":
        sys.exit(_run_wrapped("ty", "--config-file", "ty.toml", rest))
    if tool == "pytest":
        asset = importlib.resources.files("commons_python.assets") / "coverage.toml"
        with importlib.resources.as_file(asset) as config_path:
            cov_args = [] if any(a.startswith("--cov") for a in rest) else ["--cov"]
            command = ["pytest", *cov_args, "--cov-config", str(config_path), *rest]
            result = subprocess.run(command, check=False)
        sys.exit(result.returncode)
    if tool == "coverage":
        sys.exit(_run_wrapped("coverage", "--rcfile", "coverage.toml", rest))

    print(
        "usage: commons-python <ruff|ty|pytest|coverage|commons> ...",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
