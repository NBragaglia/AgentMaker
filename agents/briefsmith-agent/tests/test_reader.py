from pathlib import Path
import zipfile

import pytest

from briefsmith_agent.errors import FileReadError, InputValidationError
from briefsmith_agent.reader import read_input_text


def _write_minimal_docx(path: Path, paragraphs: list[str]) -> None:
    body = "".join(
        f"<w:p><w:r><w:t>{text}</w:t></w:r></w:p>" for text in paragraphs
    )
    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body>{body}</w:body></w:document>"
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        "</Types>"
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"></Relationships>'
    )
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", rels)
        archive.writestr("word/document.xml", document_xml)


def test_reader_reads_docx_text(tmp_path: Path) -> None:
    path = tmp_path / "sample.docx"
    _write_minimal_docx(path, ["Background: kickoff", "Risk: timeline slip"])
    text = read_input_text(path)

    assert "Background: kickoff" in text
    assert "Risk: timeline slip" in text


def test_reader_rejects_empty_docx(tmp_path: Path) -> None:
    path = tmp_path / "empty.docx"
    _write_minimal_docx(path, [])

    with pytest.raises(InputValidationError, match="Input file is empty"):
        read_input_text(path)


def test_reader_rejects_invalid_docx(tmp_path: Path) -> None:
    path = tmp_path / "broken.docx"
    path.write_bytes(b"not-a-zip")

    with pytest.raises(FileReadError, match="Failed to parse .docx file"):
        read_input_text(path)
