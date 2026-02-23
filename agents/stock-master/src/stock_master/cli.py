"""CLI for stock-master."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .prompt_assets import (
    CONSTRAINTS_QUESTIONNAIRE_TEMPLATE,
    IMPLEMENTATION_BRIEF_TEMPLATE,
    SYSTEM_PROMPT,
    write_text_file,
)

DEFAULT_BRIEF_PATH = Path("stock_master_implementation_brief.md")
DEFAULT_CONSTRAINTS_PATH = Path("stock_master_constraints.json")
DEFAULT_PROMPT_PATH = Path("AGENT_PROMPT.md")


def build_parser() -> argparse.ArgumentParser:
    """Build command-line parser."""
    parser = argparse.ArgumentParser(
        prog="stock-master",
        description="Stock Master scaffold: prompt pack + implementation brief generator",
    )
    parser.add_argument("--version", action="store_true", help="Show version")

    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("show-prompt", help="Print the Stock Master system prompt")

    init_brief_parser = subparsers.add_parser(
        "init-brief",
        help="Create a practical implementation brief markdown template",
    )
    init_brief_parser.add_argument("--output", type=Path, default=DEFAULT_BRIEF_PATH)
    init_brief_parser.add_argument("--force", action="store_true")

    bootstrap_parser = subparsers.add_parser(
        "bootstrap",
        help="Initialize all planning assets in one command",
    )
    bootstrap_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("."),
        help="Directory where prompt/brief/constraints files are created",
    )
    bootstrap_parser.add_argument("--force", action="store_true", help="Overwrite existing files")

    return parser


def _handle_init_brief(output_path: Path, force: bool) -> int:
    """Write the implementation brief template to disk."""
    try:
        write_text_file(output_path, IMPLEMENTATION_BRIEF_TEMPLATE, force=force)
    except FileExistsError as exc:
        print(f"Error: {exc}")
        return 2

    print(f"Wrote implementation brief template to: {output_path}")
    return 0


def _write_bootstrap_assets(output_dir: Path, force: bool) -> int:
    """Create prompt, brief, and constraints questionnaire in the output directory."""
    targets = {
        output_dir / DEFAULT_PROMPT_PATH: SYSTEM_PROMPT,
        output_dir / DEFAULT_BRIEF_PATH: IMPLEMENTATION_BRIEF_TEMPLATE,
        output_dir / DEFAULT_CONSTRAINTS_PATH: CONSTRAINTS_QUESTIONNAIRE_TEMPLATE,
    }

    try:
        for path, content in targets.items():
            write_text_file(path, content, force=force)
    except FileExistsError as exc:
        print(f"Error: {exc}")
        return 2

    print("Bootstrap complete. Created:")
    for path in targets:
        print(f"- {path}")
    print("Next step: fill stock_master_constraints.json, then refine the implementation brief.")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Run CLI and return exit code."""
    args = build_parser().parse_args(argv)

    if args.version:
        from . import __version__

        print(__version__)
        return 0

    if args.command == "show-prompt":
        print(SYSTEM_PROMPT)
        return 0

    if args.command == "init-brief":
        return _handle_init_brief(output_path=args.output, force=args.force)

    if args.command == "bootstrap":
        return _write_bootstrap_assets(output_dir=args.output_dir, force=args.force)

    print("stock-master scaffold is ready.")
    print("Use `stock-master show-prompt` to view the full system prompt blueprint.")
    print("Use `stock-master init-brief` to generate a runnable implementation brief.")
    print("Use `stock-master bootstrap` to generate prompt + brief + constraints in one shot.")
    return 0


def run() -> None:
    """Console script entrypoint."""
    raise SystemExit(main())


if __name__ == "__main__":
    run()
