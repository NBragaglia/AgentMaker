"""CLI for briefsmith-agent."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import sys
from pathlib import Path
from typing import Sequence

from .errors import BriefsmithAgentError, InputValidationError
from .formatter import format_markdown
from .models import Mode
from .parser import parse_notes
from .reader import read_input_text
from .writer import save_markdown


@dataclass(slots=True)
class RunConfig:
    """Runtime configuration for brief generation."""

    mode: Mode
    output_dir: Path
    max_bullets: int | None
    max_ktas: int
    email_ready: bool


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
            "  briefsmith-agent client_call.txt --mode client --output-dir outputs --email-ready\n"
            "  briefsmith-agent --batch-dir .\\meeting_notes --mode investment --max-bullets 3"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "input_path",
        nargs="?",
        type=Path,
        help="Path to input .txt or .docx notes file (omit when using --batch-dir)",
    )
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
    parser.add_argument(
        "--batch-dir",
        type=Path,
        help="Directory to batch process all .txt and .docx files",
    )
    parser.add_argument(
        "--max-bullets",
        type=int,
        default=None,
        help="Maximum bullets per section (overrides mode defaults)",
    )
    parser.add_argument(
        "--max-ktas",
        type=int,
        default=4,
        help="Maximum number of key takeaways (default: 4)",
    )
    parser.add_argument(
        "--email-ready",
        action="store_true",
        help="Include a team update email draft section in output",
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


def validate_batch_dir(path: Path) -> None:
    """Validate batch input directory."""
    if not path.exists():
        raise InputValidationError(f"Batch directory not found: {path}")
    if not path.is_dir():
        raise InputValidationError(f"Expected a directory for --batch-dir, got: {path}")


def collect_batch_files(batch_dir: Path) -> list[Path]:
    """Collect supported note files from a batch directory."""
    files = sorted([*batch_dir.glob("*.txt"), *batch_dir.glob("*.docx")])
    if not files:
        raise InputValidationError(f"No .txt or .docx files found in batch directory: {batch_dir}")
    return files


def process_single_file(input_path: Path, config: RunConfig) -> Path:
    """Process one notes file and return output path."""
    validate_input_file(input_path)
    raw_text = read_input_text(input_path)
    brief = parse_notes(raw_text, config.mode, max_bullets=config.max_bullets)
    markdown = format_markdown(
        brief,
        config.mode,
        input_path,
        max_ktas=config.max_ktas,
        email_ready=config.email_ready,
    )
    return save_markdown(markdown, config.mode, config.output_dir)


def main(argv: Sequence[str] | None = None) -> int:
    """Run application and return exit code."""
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)

    input_path: Path | None = args.input_path
    output_dir: Path = args.output_dir
    mode = Mode(args.mode)
    batch_dir: Path | None = args.batch_dir
    max_bullets: int | None = args.max_bullets
    max_ktas: int = args.max_ktas
    email_ready: bool = bool(args.email_ready)

    if input_path is None and batch_dir is None:
        print("Provide either input_path or --batch-dir.", file=sys.stderr)
        return 2
    if input_path is not None and batch_dir is not None:
        print("Use either input_path or --batch-dir, not both.", file=sys.stderr)
        return 2
    if max_bullets is not None and max_bullets < 1:
        print("--max-bullets must be >= 1", file=sys.stderr)
        return 2
    if max_ktas < 1:
        print("--max-ktas must be >= 1", file=sys.stderr)
        return 2

    config = RunConfig(
        mode=mode,
        output_dir=output_dir,
        max_bullets=max_bullets,
        max_ktas=max_ktas,
        email_ready=email_ready,
    )

    try:
        if batch_dir is not None:
            validate_batch_dir(batch_dir)
            batch_files = collect_batch_files(batch_dir)
            outputs: list[Path] = []
            for file_path in batch_files:
                outputs.append(process_single_file(file_path, config))
            print(f"Batch complete: {len(outputs)} briefs generated.")
            for output_path in outputs:
                print(f"- {output_path.as_posix()}")
            return 0

        if input_path is None:
            raise InputValidationError("Input path is required when --batch-dir is not set.")
        output_path = process_single_file(input_path, config)
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
