"""CLI for briefsmith-agent."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from .errors import BriefsmithAgentError, InputValidationError
from .formatter import format_markdown
from .models import Mode
from .parser import parse_notes
from .reader import read_input_text
from .writer import save_markdown


def build_parser() -> argparse.ArgumentParser:
    """Build command-line parser."""
    parser = argparse.ArgumentParser(
        prog="briefsmith-agent",
        description="Convert messy text notes into a structured consulting/PE work brief.",
        epilog=(
            "Examples:\n"
            "  briefsmith-agent notes.txt --mode internal\n"
            "  briefsmith-agent meeting_transcript.docx --mode client\n"
            "  briefsmith-agent .\\data\\deal_notes.txt --mode investment\n"
            "  briefsmith-agent client_call.txt --mode client --output-dir outputs"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input_path", type=Path, help="Path to input .txt or .docx notes file")
    parser.add_argument(
        "--mode",
        required=True,
        choices=[m.value for m in Mode],
        help="Output mode: internal, client, investment",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs"),
        help="Directory for generated markdown output (default: outputs)",
    )
    return parser


def validate_input_file(path: Path) -> None:
    """Validate user input file path."""
    if not path.exists():
        raise InputValidationError(f"Input file not found: {path}")
    if path.is_dir():
        raise InputValidationError(f"Expected a file path, got directory: {path}")
    if path.suffix.lower() not in {".txt", ".docx"}:
        raise InputValidationError(f"Expected a .txt or .docx file, got: {path}")


def main(argv: Sequence[str] | None = None) -> int:
    """Run application and return exit code."""
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)

    input_path: Path = args.input_path
    output_dir: Path = args.output_dir
    mode = Mode(args.mode)

    try:
        validate_input_file(input_path)
        raw_text = read_input_text(input_path)
        brief = parse_notes(raw_text, mode)
        markdown = format_markdown(brief, mode, input_path)
        output_path = save_markdown(markdown, mode, output_dir)
    except BriefsmithAgentError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Brief generated: {output_path.as_posix()}")
    return 0


def run() -> None:
    """Console script entrypoint."""
    raise SystemExit(main())


if __name__ == "__main__":
    run()
