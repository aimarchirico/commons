"""Dispatching CLI that wraps Astral's tools with the bundled Commons config."""

import importlib.resources
import subprocess
import sys


def _run_wrapped(
    binary: str, config_flag: str, asset_name: str, args: list[str]
) -> int:
    """Invoke ``binary <subcommand> config_flag config_path ...`` for the given args.

    ``config_flag`` names the flag used to pass the bundled ``asset_name``
    config; it's placed after the subcommand since ``ty`` only accepts it
    there (``ruff`` accepts it in either position).
    """
    asset = importlib.resources.files("commons_python.assets") / asset_name
    with importlib.resources.as_file(asset) as config_path:
        subcommand, *rest = args
        command = [binary, subcommand, config_flag, str(config_path), *rest]
        result = subprocess.run(command, check=False)
    return result.returncode


def main() -> None:
    """Dispatch to a wrapped tool based on the first argument.

    ``ruff`` and ``ty`` forward their remaining arguments untouched to the
    respective tool, with the bundled config injected. ``line-length`` runs
    the file-length check natively (no equivalent tool to wrap).
    """
    tool, *rest = sys.argv[1:] or [""]

    if tool == "line-length":
        from commons_python.line_length import check_line_length

        sys.exit(check_line_length(rest or ["."]))
    if tool == "ruff":
        sys.exit(_run_wrapped("ruff", "--config", "ruff.toml", rest))
    if tool == "ty":
        sys.exit(_run_wrapped("ty", "--config-file", "ty.toml", rest))

    print("usage: commons-python <ruff|ty|line-length> ...", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
