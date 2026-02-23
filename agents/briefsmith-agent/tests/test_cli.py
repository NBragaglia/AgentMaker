from pathlib import Path
import zipfile

from briefsmith_agent.cli import main


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


def test_cli_valid_run_writes_markdown(tmp_path: Path, capsys) -> None:
    input_path = tmp_path / "notes.txt"
    input_path.write_text("Risk: timeline slip\n", encoding="utf-8")
    output_dir = tmp_path / "outputs"

    exit_code = main([str(input_path), "--mode", "internal", "--output-dir", str(output_dir)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Brief generated:" in captured.out
    files = list(output_dir.glob("brief_internal_*.md"))
    assert len(files) == 1


def test_cli_accepts_docx_input(tmp_path: Path, capsys) -> None:
    input_path = tmp_path / "notes.docx"
    _write_minimal_docx(input_path, ["Risk: timeline slip", "Next step: assign owner"])
    output_dir = tmp_path / "outputs"

    exit_code = main([str(input_path), "--mode", "internal", "--output-dir", str(output_dir)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Brief generated:" in captured.out
    files = list(output_dir.glob("brief_internal_*.md"))
    assert len(files) == 1


def test_cli_rejects_missing_file(tmp_path: Path, capsys) -> None:
    missing = tmp_path / "missing.txt"
    exit_code = main([str(missing), "--mode", "client"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Input file not found" in captured.err


def test_cli_rejects_non_txt_file(tmp_path: Path, capsys) -> None:
    bad_file = tmp_path / "notes.md"
    bad_file.write_text("content", encoding="utf-8")

    exit_code = main([str(bad_file), "--mode", "investment"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Expected a .txt or .docx file" in captured.err


def test_cli_rejects_empty_file(tmp_path: Path, capsys) -> None:
    empty_file = tmp_path / "notes.txt"
    empty_file.write_text("   \n\n", encoding="utf-8")

    exit_code = main([str(empty_file), "--mode", "internal"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Input file is empty" in captured.err


def test_cli_invalid_mode_returns_parser_error(tmp_path: Path, capsys) -> None:
    input_path = tmp_path / "notes.txt"
    input_path.write_text("Something", encoding="utf-8")

    exit_code = main([str(input_path), "--mode", "badmode"])
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "invalid choice" in captured.err.lower()
