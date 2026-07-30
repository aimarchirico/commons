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

    ``ruff`` and ``ty`` forward their remaining arguments untouched to the
    respective tool, with the bundled config injected. ``line-length`` and
    ``comments`` run native Python checks.
    """
    tool, *rest = sys.argv[1:] or [""]

    if tool == "comments":
        from commons_python.comments import check_comments

        sys.exit(check_comments(rest or ["."]))
    if tool == "line-length":
        from commons_python.line_length import check_line_length

        sys.exit(check_line_length(rest or ["."]))
    if tool == "ruff":
        sys.exit(_run_wrapped("ruff", "--config", "ruff.toml", rest))
    if tool == "ty":
        sys.exit(_run_wrapped("ty", "--config-file", "ty.toml", rest))

    print(
        "usage: commons-python <ruff|ty|line-length|comments> ...",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
