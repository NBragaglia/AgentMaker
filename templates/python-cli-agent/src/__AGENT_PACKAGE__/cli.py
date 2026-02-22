"""CLI for __AGENT_NAME__."""

from __future__ import annotations

import argparse
from typing import Sequence


def build_parser() -> argparse.ArgumentParser:
    """Build command-line parser."""
    parser = argparse.ArgumentParser(prog="__AGENT_NAME__", description="Starter Python CLI agent")
    parser.add_argument("--version", action="store_true", help="Show version")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run CLI and return exit code."""
    args = build_parser().parse_args(argv)
    if args.version:
        from . import __version__

        print(__version__)
        return 0

    print("__AGENT_NAME__ scaffold is ready.")
    return 0


def run() -> None:
    """Console script entrypoint."""
    raise SystemExit(main())


if __name__ == "__main__":
    run()
