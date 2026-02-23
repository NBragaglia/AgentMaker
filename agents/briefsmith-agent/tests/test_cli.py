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


def test_cli_batch_mode_processes_directory(tmp_path: Path, capsys) -> None:
    batch_dir = tmp_path / "batch"
    batch_dir.mkdir()
    (batch_dir / "a.txt").write_text("Risk: timeline slip", encoding="utf-8")
    (batch_dir / "b.txt").write_text("Finding: margin improved", encoding="utf-8")
    output_dir = tmp_path / "outputs"

    exit_code = main(["--batch-dir", str(batch_dir), "--mode", "client", "--output-dir", str(output_dir)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Batch complete: 2 briefs generated." in captured.out
    assert len(list(output_dir.glob("brief_client_*.md"))) == 2


def test_cli_email_ready_flag_includes_email_section(tmp_path: Path, capsys) -> None:
    input_path = tmp_path / "notes.txt"
    input_path.write_text("Finding: margin improved\nRisk: timeline slip\n", encoding="utf-8")
    output_dir = tmp_path / "outputs"

    exit_code = main(
        [str(input_path), "--mode", "client", "--output-dir", str(output_dir), "--email-ready"]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Brief generated:" in captured.out
    output_file = list(output_dir.glob("brief_client_*.md"))[0]
    content = output_file.read_text(encoding="utf-8")
    assert "## Team Update Email Draft" in content


def test_cli_validates_mutually_exclusive_input_and_batch(tmp_path: Path, capsys) -> None:
    input_path = tmp_path / "notes.txt"
    input_path.write_text("Finding: margin improved", encoding="utf-8")
    batch_dir = tmp_path / "batch"
    batch_dir.mkdir()

    exit_code = main([str(input_path), "--batch-dir", str(batch_dir), "--mode", "internal"])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "either input_path or --batch-dir, not both" in captured.err.lower()


def test_cli_rejects_invalid_max_values(tmp_path: Path, capsys) -> None:
    input_path = tmp_path / "notes.txt"
    input_path.write_text("Finding: margin improved", encoding="utf-8")

    exit_code = main([str(input_path), "--mode", "internal", "--max-bullets", "0"])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "--max-bullets must be >= 1" in captured.err


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
