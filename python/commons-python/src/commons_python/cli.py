"""Thin wrapper around ``ruff`` that injects the bundled Commons config."""

import importlib.resources
import subprocess
import sys


def main() -> None:
    """Run ``ruff`` with the bundled Commons config injected.

    All arguments are forwarded to ``ruff`` untouched (e.g. ``check``,
    ``format``, ``--fix``, path arguments); only ``--config`` is added.
    """
    assets = importlib.resources.files("commons_python.assets") / "ruff.toml"
    with importlib.resources.as_file(assets) as config_path:
        result = subprocess.run(
            ["ruff", "--config", str(config_path), *sys.argv[1:]],
            check=False,
        )
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
