"""File writer for markdown output."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .errors import OutputWriteError
from .models import Mode


def save_markdown(markdown: str, mode: Mode, output_dir: Path) -> Path:
    """Write markdown file using timestamped naming and return output path."""
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"brief_{mode.value}_{timestamp}.md"
        output_path.write_text(markdown, encoding="utf-8")
    except OSError as exc:
        raise OutputWriteError(f"Failed to write output file in: {output_dir}") from exc
    return output_path
