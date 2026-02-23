"""Input file readers for supported note formats."""

from __future__ import annotations

import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from .errors import FileReadError, InputValidationError

_WORD_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def read_input_text(path: Path) -> str:
    """Read text from .txt or .docx and validate non-empty content."""
    try:
        if path.suffix.lower() == ".txt":
            content = path.read_text(encoding="utf-8")
        elif path.suffix.lower() == ".docx":
            content = _read_docx_text(path)
        else:
            raise InputValidationError(f"Expected a .txt or .docx file, got: {path}")
    except InputValidationError:
        raise
    except OSError as exc:
        raise FileReadError(f"Failed to read input file: {path}") from exc
    except (zipfile.BadZipFile, ET.ParseError, KeyError) as exc:
        raise FileReadError(f"Failed to parse .docx file: {path}") from exc

    if not content.strip():
        raise InputValidationError(f"Input file is empty: {path}")
    return content


def _read_docx_text(path: Path) -> str:
    """Extract plain text from a Word .docx by reading document XML."""
    with zipfile.ZipFile(path) as archive:
        xml_bytes = archive.read("word/document.xml")

    root = ET.fromstring(xml_bytes)
    lines: list[str] = []
    for paragraph in root.findall(".//w:p", _WORD_NS):
        texts = [node.text for node in paragraph.findall(".//w:t", _WORD_NS) if node.text]
        line = "".join(texts).strip()
        if line:
            lines.append(line)
    return "\n".join(lines)
